"""Fabricated records only. These are infrastructure checks, not qualification."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch

from cohervia import AuditStore, Context, FrozenInputs, ReplayError, replay, validate_observation
from cohervia.canonical import bytes_sha256, canonical_bytes, parse_json, record_sha256
from cohervia.observations import ObservationState

TIME = "2026-09-18T12:00:01.000000Z"
CONTEXT = Context("fictional-run", "fictional-trajectory", "fictional-subject")
ARTIFACT = b"fabricated retry count: 2\n"
HASH = bytes_sha256(ARTIFACT)
PRODUCER = {"id": "fictional-recorder", "version": "1"}


def inputs(**changes):
    args = dict(definitions=[{"id": "retry_count", "version": "1", "value_type": "number",
                "units": "1", "minimum": 0, "maximum": 10, "allowed_strings": None,
                "scale": "fictional retry count", "risk_orientation": "not_defined"}],
                config_id="fictional-config", configuration={"fixture": True},
                evidence_manifest={"fictional-artifact": HASH}, artifacts={"fictional-artifact": ARTIFACT})
    args.update(changes)
    return FrozenInputs(**args)


def observation(**changes):
    o = dict(schema_version="observation/0.1", observation_id="obs-0", **CONTEXT.as_dict(),
             sequence=0, event_time="2026-09-18T12:00:00.000000Z", available_at=TIME,
             phase="post_action", metric_id="retry_count", metric_version="1", value_type="number",
             value=2, units="1", status="observed", rationale="Count in a fabricated fixture.",
             uncertainty=None, evidence_refs=[{"id": "fictional-artifact", "sha256": HASH}],
             input_observation_ids=[], derivation=None, source={"id": "fictional-source", "version": "1"},
             collector={"id": "fictional-collector", "version": "1"}, scorer=None, config=inputs().config,
             acquisition_context={"adapter_id": "fictional-adapter", "adapter_version": "1"})
    o.update(changes)
    return o


def inferred(**changes):
    args = dict(observation_id="obs-1", sequence=1, status="inferred", input_observation_ids=["obs-0"],
                derivation={"id": "fictional-identity", "version": "1"},
                scorer={"id": "fictional-scorer", "version": "1", "type": "automated"})
    args.update(changes)
    return observation(**args)


def resign(event):
    event["sha256"] = record_sha256({k: v for k, v in event.items() if k != "sha256"})


class CanonicalTests(unittest.TestCase):
    def test_rfc_number_and_string_vector(self):
        # RFC 8785 section 3.2.2 sample, expressed without depending on sorted JSON.
        value = parse_json(b'{"numbers":[333333333.33333329,1E30,4.50,2e-3,0.000000000000000000000000001],"string":"\\u20ac$\\u000f\\nA\'B\\\"\\\\\\\\/","literals":[null,true,false]}')
        expected = b'{"literals":[null,true,false],"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27],"string":"\xe2\x82\xac$\\u000f\\nA\'B\\\"\\\\\\\\/"}'
        self.assertEqual(canonical_bytes(value), expected)

    def test_utf16_property_order_vector(self):
        # RFC 8785 section 3.2.3: supplementary character sorts before U+FB33.
        names = ["\u20ac", "\r", "\ufb33", "1", "\U0001f600", "\u0080", "\u00f6"]
        self.assertEqual(list(parse_json(canonical_bytes(dict.fromkeys(names, 0)))),
                         ["\r", "1", "\u0080", "\u00f6", "\u20ac", "\U0001f600", "\ufb33"])

    def test_number_boundaries_and_negative_zero(self):
        self.assertEqual(canonical_bytes([-0.0, 1e-6, 1e-7, 1e20, 1e21]), b'[0,0.000001,1e-7,100000000000000000000,1e+21]')
        self.assertEqual(parse_json(canonical_bytes(9007199254740991)), 9007199254740991)

    def test_strict_json_rejections(self):
        bad = [b'{"a":1,"a":2}', b'{"a":{"x":1,"x":2}}', b'NaN', b'Infinity', b'1e999',
               b'9007199254740992', b'-9007199254740992', b'"\\ud800"', b'"\xff"', b'{', b'{} {}']
        for raw in bad:
            with self.subTest(raw=raw), self.assertRaises((ValueError, UnicodeError)):
                parse_json(raw)

    def test_no_coercion_and_hash_scope(self):
        self.assertEqual(canonical_bytes({"b": 1, "a": 2}), canonical_bytes({"a": 2, "b": 1}))
        self.assertNotEqual(record_sha256([1, 2]), record_sha256([2, 1]))
        self.assertNotEqual(record_sha256(" x "), record_sha256("x"))
        with self.assertRaises(ValueError):
            canonical_bytes({1: "x"})
        with self.assertRaises(ValueError):
            canonical_bytes((1, 2))
        self.assertEqual(bytes_sha256(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.inputs = inputs()
        self.state = ObservationState()

    def check(self, o, disposition, codes, *, frozen=None):
        before = self.state.snapshot()
        r = validate_observation(json.dumps(o).encode(), CONTEXT, frozen or self.inputs, self.state)
        self.assertEqual((r.disposition, r.reason_codes), (disposition, tuple(codes)))
        self.assertEqual(self.state.snapshot(), before)
        return r

    def test_observed_and_zero_are_valid_without_default_confidence(self):
        for value in (0, 2, 10, 2.5):
            result = self.check(observation(value=value), "accept", ["valid"])
            self.assertIsNone(result.observation["uncertainty"])

    def test_explicit_missingness(self):
        for status in ("unknown", "not_applicable"):
            r = self.check(observation(status=status, value=None, evidence_refs=[], rationale="Fictional fixture unavailable / inapplicable."), "accept", ["valid"])
            self.assertEqual(r.observation["status"], status)
            for update in (dict(value=0), dict(uncertainty={"kind": "confidence", "value": 0, "basis": "fixture"}), dict(rationale=" ")):
                self.check(observation(**dict(dict(status=status, value=None), **update)), "reject", ["invalid_record"])
        self.check(observation(value=None), "reject", ["invalid_record"])

    def test_every_required_field_and_unknown_keys(self):
        for key in observation():
            o = observation()
            del o[key]
            self.check(o, "reject", ["invalid_record"])
        self.check(observation(extra=None), "reject", ["invalid_record"])
        for field in ("source", "collector", "config", "acquisition_context"):
            o = observation()
            o[field]["extra"] = None
            self.check(o, "reject", ["invalid_record"])

    def test_bad_types_versions_units_and_domain(self):
        mutations = [dict(sequence=True), dict(sequence=-1), dict(sequence=0.0), dict(value=True), dict(value="2"),
                     dict(value=-1), dict(value=11), dict(units="seconds"), dict(units=None),
                     dict(value_type="boolean", value=True, units=None), dict(schema_version="observation/2"),
                     dict(phase="other"), dict(status="missing"), dict(observation_id=" obs"),
                     dict(rationale=None), dict(source={"id": "x", "version": ""}),
                     dict(scorer={"id": "x", "version": "1", "type": "unknown"})]
        for update in mutations:
            with self.subTest(update=update):
                self.check(observation(**update), "reject", ["invalid_record"])

    def test_nonnumeric_definitions(self):
        for kind, value, allowed in (("boolean", False, None), ("string", "low", ["low", "high"])):
            d = self.inputs.document["definitions"][0]
            d.update(value_type=kind, units=None, minimum=None, maximum=None, allowed_strings=allowed)
            frozen = inputs(definitions=[d])
            self.check(observation(value_type=kind, value=value, units=None), "accept", ["valid"], frozen=frozen)
            if kind == "string":
                self.check(observation(value_type=kind, value="other", units=None), "reject", ["invalid_record"], frozen=frozen)

    def test_timestamp_format_and_causality(self):
        for value in ("2026-09-18T12:00:01Z", "2026-09-18T12:00:01.000000+00:00", "2026-02-30T12:00:01.000000Z", "2026-09-18T12:00:60.000000Z"):
            self.check(observation(available_at=value), "reject", ["invalid_record"])
        self.check(observation(event_time="2026-09-18T12:00:02.000000Z"), "reject", ["invalid_record"])

    def test_identity_before_duplicate_and_all_reasons(self):
        self.state.add(observation())
        self.check(observation(subject_id="other"), "reject", ["identity_mismatch"])
        self.check(observation(subject_id="other", sequence=True), "reject", ["identity_mismatch", "invalid_record"])

    def test_duplicate_and_conflicting_payload_before_ordering(self):
        self.state.add(observation())
        self.check(observation(), "accept", ["duplicate_noop"])
        self.check(observation(value=3, sequence=100), "reject", ["conflicting_id"])
        self.check(observation(observation_id="different"), "reject", ["sequence_reuse"])

    def test_gap_regression_and_late_event(self):
        self.check(observation(sequence=2), "quarantine", ["sequence_gap"])
        self.state.add(observation())
        self.check(observation(observation_id="obs-1", sequence=1, event_time="2026-09-17T12:00:00.000000Z"), "accept", ["valid"])
        self.check(observation(observation_id="obs-2", sequence=2, available_at="2026-09-18T12:00:00.000000Z"), "quarantine", ["availability_regression", "sequence_gap"])

    def test_missing_artifacts_and_digest_mismatch(self):
        self.check(observation(), "quarantine", ["unresolved_reference"], frozen=inputs(artifacts={}))
        self.check(observation(evidence_refs=[{"id": "unknown", "sha256": HASH}]), "quarantine", ["unresolved_reference"])
        self.check(observation(), "reject", ["invalid_provenance"], frozen=inputs(artifacts={"fictional-artifact": b"changed"}))
        self.check(observation(evidence_refs=[{"id": "fictional-artifact", "sha256": "0" * 64}]), "reject", ["invalid_provenance"])
        self.check(observation(evidence_refs=[]), "reject", ["invalid_record"])
        for refs in ([{"id": " ", "sha256": HASH}], [{"id": "fictional-artifact", "sha256": HASH.upper()}], observation()["evidence_refs"] * 2):
            self.check(observation(evidence_refs=refs), "reject", ["invalid_record"])

    def test_config_binding_and_reject_priority(self):
        self.check(observation(config={"id": "other", "sha256": "0" * 64}, sequence=3, metric_id="absent"), "reject", ["invalid_provenance", "sequence_gap", "unresolved_reference"])

    def test_inferred_inputs_and_future_provenance(self):
        self.check(inferred(sequence=0), "quarantine", ["unresolved_reference"])
        self.state.add(observation())
        self.check(inferred(), "accept", ["valid"])
        self.check(inferred(available_at="2026-09-18T12:00:00.000000Z"), "reject", ["availability_regression", "invalid_provenance"])
        for update in (dict(scorer=None), dict(derivation=None), dict(input_observation_ids=[]), dict(input_observation_ids=["obs-0", "obs-0"])):
            self.check(inferred(**update), "reject", ["invalid_record"])
        other = observation(subject_id="other")
        self.state.accepted["obs-0"] = other
        self.check(inferred(), "quarantine", ["unresolved_reference"])

    def test_uncertainty_is_explicit_and_bounded(self):
        for value in (0, 0.5, 1):
            self.check(observation(uncertainty={"kind": "confidence", "value": value, "basis": "fabricated basis"}), "accept", ["valid"])
        for value in (True, -0.01, 1.01, "1"):
            self.check(observation(uncertainty={"kind": "confidence", "value": value, "basis": "fabricated basis"}), "reject", ["invalid_record"])

    def test_raw_json_invalid_is_a_disposition(self):
        for raw in (b'NaN', b'null', b'[]', b'{}', b'{"x":1,"x":2}', b'"\\ud800"', b'{'):
            r = validate_observation(raw, CONTEXT, self.inputs, self.state)
            self.assertEqual((r.disposition, r.reason_codes), ("reject", ("invalid_record",)))

    def test_inputs_are_frozen_copies_and_hashed(self):
        frozen = self.inputs
        before = frozen.sha256
        frozen.document["configuration"]["fixture"] = False
        frozen.definitions[("retry_count", "1")]["maximum"] = 0
        frozen.manifest.clear()
        frozen.artifacts.clear()
        self.assertEqual(before, frozen.sha256)
        self.check(observation(), "accept", ["valid"])
        self.assertNotEqual(inputs(configuration={"fixture": False}).sha256, before)

    def test_invalid_frozen_inputs_fail_before_ingestion(self):
        definition = self.inputs.document["definitions"][0]
        for changes in ({"maximum": -1}, {"minimum": True}, {"units": None}, {"risk_orientation": "unknown"}, {"extra": 1}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                inputs(definitions=[dict(definition, **changes)])
        with self.assertRaises(ValueError):
            inputs(definitions=[definition, definition])
        with self.assertRaises(ValueError):
            inputs(artifacts={"fictional-artifact": Path("sealed-holdout")})


class StorageReplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "audit.sqlite"
        self.store = AuditStore(self.path)
        self.inputs = inputs()
        self.counter = 0

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def append(self, o, **changes):
        self.counter += 1
        args = dict(event_id=f"event-{self.counter}", recorded_at=TIME, producer=PRODUCER)
        args.update(changes)
        return self.store.append_submission(o if type(o) is bytes else canonical_bytes(o), CONTEXT, self.inputs, **args)

    def export(self):
        return self.store.export(CONTEXT, self.inputs)

    def test_dispositions_roundtrip_and_no_automatic_quarantine_release(self):
        gap = observation(observation_id="obs-1", sequence=1)
        e0 = self.append(gap)
        self.assertEqual(e0["payload"]["disposition"], "quarantine")
        self.append(observation())
        events, records = self.export()
        self.assertEqual(replay(events, records, CONTEXT, self.inputs).next_sequence, 1)
        self.append(gap)
        self.append(observation())
        self.append(observation(value=3))
        self.append(b'{"malformed":')
        events, records = self.export()
        self.assertEqual([e["sequence"] for e in events], list(range(6)))
        self.assertEqual([e["payload"]["reason_codes"] for e in events], [["sequence_gap"], ["valid"], ["valid"], ["duplicate_noop"], ["conflicting_id"], ["invalid_record"]])
        state = replay(events, records, CONTEXT, self.inputs)
        self.assertEqual(state.next_sequence, 2)
        self.assertEqual(len(records), 2)
        self.assertEqual(events[-1]["payload"]["submission_sha256"], bytes_sha256(b'{"malformed":'))
        self.assertNotIn("malformed", canonical_bytes(events[-1]).decode())
        self.assertEqual(state.snapshot(), replay(deepcopy(events), deepcopy(records), CONTEXT, self.inputs).snapshot())

    def test_artifact_availability_requires_explicit_resubmission(self):
        unavailable = inputs(artifacts={})
        raw = canonical_bytes(observation())
        event = self.store.append_submission(raw, CONTEXT, unavailable, event_id="missing", recorded_at=TIME, producer=PRODUCER)
        self.assertEqual(event["payload"]["disposition"], "quarantine")
        self.assertEqual(self.store.export(CONTEXT, self.inputs)[1], {})
        self.append(observation())
        self.assertEqual(len(self.export()[1]), 1)
        with self.assertRaises(ReplayError):
            self.store.export(CONTEXT, unavailable)

    def test_replay_rejects_invalid_collection_types(self):
        for events, records in ((None, {}), ([], []), ((), {})):
            with self.assertRaises(ReplayError):
                replay(events, records, CONTEXT, self.inputs)

    def test_missingness_and_inferred_provenance_survive_replay(self):
        self.append(observation(value=0))
        self.append(inferred())
        self.append(observation(observation_id="obs-2", sequence=2, status="unknown", value=None,
                                evidence_refs=[], rationale="Fictional collector unavailable."))
        self.append(observation(observation_id="obs-3", sequence=3, status="not_applicable", value=None,
                                evidence_refs=[], rationale="Fictional metric does not apply."))
        events, records = self.export()
        state = replay(events, records, CONTEXT, self.inputs)
        self.assertEqual(state.accepted["obs-0"]["value"], 0)
        self.assertEqual(state.accepted["obs-1"]["input_observation_ids"], ["obs-0"])
        for key, status in (("obs-2", "unknown"), ("obs-3", "not_applicable")):
            self.assertEqual(state.accepted[key]["status"], status)
            self.assertIsNone(state.accepted[key]["value"])
            self.assertIsNone(state.accepted[key]["uncertainty"])

    def test_storage_corruption_prevents_another_append(self):
        self.append(observation())
        self.store.connection.execute("UPDATE events SET sequence=8")
        with self.assertRaises(ReplayError):
            self.append(inferred())
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM observations").fetchone()[0], 1)

    def test_unreferenced_storage_record_is_not_silently_skipped(self):
        self.append(observation())
        self.store.connection.execute("INSERT INTO observations VALUES (?, ?, ?, ?)",
                                      (CONTEXT.run_id, "orphan", CONTEXT.trajectory_id,
                                       canonical_bytes(observation(observation_id="orphan", sequence=1))))
        with self.assertRaises(ReplayError):
            self.export()

    def test_replay_event_schema_payload_invariants(self):
        self.append(observation())
        events, records = self.export()
        for field, value in (("reason_codes", ["valid", "valid"]), ("disposition", "allow"),
                             ("accepted_observation_ref", None), ("submission_sha256", "bad")):
            bad = deepcopy(events)
            bad[0]["payload"][field] = value
            resign(bad[0])
            with self.subTest(field=field), self.assertRaises(ReplayError):
                replay(bad, records, CONTEXT, self.inputs)
        bad = deepcopy(events)
        bad[0]["related_ids"]["decision_id"] = "permission"
        resign(bad[0])
        with self.assertRaises(ReplayError):
            replay(bad, records, CONTEXT, self.inputs)

    def test_empty_stream_and_wrong_input_manifest(self):
        checkpoint = {"event_count": 0, "last_sha256": None, "inputs_sha256": self.inputs.sha256}
        self.assertEqual(replay([], {}, CONTEXT, self.inputs, checkpoint=checkpoint).next_sequence, 0)
        with self.assertRaises(ReplayError):
            replay([], {}, CONTEXT, self.inputs, checkpoint=dict(checkpoint, event_count=False))
        self.append(observation())
        events, records = self.export()
        with self.assertRaises(ReplayError):
            replay(events, records, CONTEXT, inputs(configuration={"fixture": False}))

    def test_raw_hash_is_not_canonical_hash(self):
        raw = json.dumps(observation(), indent=2).encode()
        event = self.append(raw)
        self.assertEqual(event["payload"]["submission_sha256"], bytes_sha256(raw))
        self.assertNotEqual(event["payload"]["submission_sha256"], event["payload"]["accepted_observation_ref"]["sha256"])
        duplicate = self.append(canonical_bytes(observation()))
        self.assertEqual(duplicate["payload"]["reason_codes"], ["duplicate_noop"])

    def test_atomic_rollback_when_audit_insert_fails(self):
        self.store.connection.execute("CREATE TRIGGER fail_event BEFORE INSERT ON events BEGIN SELECT RAISE(ABORT, 'injected failure'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.append(observation())
        for table in ("observations", "events", "runs", "streams"):
            self.assertEqual(self.store.connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0], 0)
        self.store.connection.execute("DROP TRIGGER fail_event")
        self.assertEqual(self.append(observation())["sequence"], 0)

    def test_atomic_rollback_when_observation_insert_fails(self):
        self.store.connection.execute("CREATE TRIGGER fail_observation BEFORE INSERT ON observations BEGIN SELECT RAISE(ABORT, 'injected failure'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.append(observation())
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM events").fetchone()[0], 0)

    def test_duplicate_event_id_rolls_back_second_observation(self):
        self.append(observation(), event_id="same")
        with self.assertRaises(sqlite3.IntegrityError):
            self.append(inferred(), event_id="same")
        events, records = self.export()
        self.assertEqual((len(events), len(records)), (1, 1))

    def test_persistence_and_frozen_run_binding(self):
        self.append(observation())
        self.store.close()
        self.store = AuditStore(self.path)
        events, records = self.export()
        self.assertEqual(replay(events, records, CONTEXT, self.inputs).next_sequence, 1)
        with self.assertRaises(ReplayError):
            self.store.append_submission(canonical_bytes(inferred()), CONTEXT, inputs(configuration={"fixture": False}), event_id="other", recorded_at=TIME, producer=PRODUCER)
        wrong = Context(CONTEXT.run_id, CONTEXT.trajectory_id, "other")
        with self.assertRaises(ReplayError):
            self.store.export(wrong, self.inputs)

    def test_run_wide_id_conflict_across_trajectories(self):
        self.append(observation())
        context = Context(CONTEXT.run_id, "another-trajectory", CONTEXT.subject_id)
        o = observation(trajectory_id=context.trajectory_id, sequence=99)
        e = self.store.append_submission(canonical_bytes(o), context, self.inputs, event_id="another", recorded_at=TIME, producer=PRODUCER)
        self.assertEqual(e["payload"]["reason_codes"], ["conflicting_id"])
        events, records = self.store.export(context, self.inputs)
        self.assertEqual(replay(events, records, context, self.inputs).next_sequence, 0)

    def test_cross_trajectory_derivation_inputs_are_unresolved(self):
        self.append(observation())
        context = Context(CONTEXT.run_id, "another-trajectory", CONTEXT.subject_id)
        o = inferred(observation_id="other-obs", sequence=0, trajectory_id=context.trajectory_id)
        e = self.store.append_submission(canonical_bytes(o), context, self.inputs, event_id="another", recorded_at=TIME, producer=PRODUCER)
        self.assertEqual(e["payload"]["reason_codes"], ["unresolved_reference"])
        self.assertEqual(e["payload"]["disposition"], "quarantine")

    def test_concurrent_connections_serialize_duplicate(self):
        barrier = threading.Barrier(2)
        errors, events = [], []
        def worker(i):
            try:
                with AuditStore(self.path) as store:
                    barrier.wait(timeout=5)
                    events.append(store.append_submission(canonical_bytes(observation()), CONTEXT, self.inputs, event_id=f"thread-{i}", recorded_at=TIME, producer=PRODUCER))
            except BaseException as exc:
                errors.append(exc)
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertFalse(errors, errors)
        self.assertEqual(sorted(e["payload"]["reason_codes"][0] for e in events), ["duplicate_noop", "valid"])
        self.assertEqual(len(self.export()[1]), 1)

    def test_tampered_and_missing_observations_fail(self):
        self.append(observation())
        events, records = self.export()
        for bad in ({}, {"obs-0": observation(value=3)}):
            with self.assertRaises(ReplayError):
                replay(events, bad, CONTEXT, self.inputs)

    def test_audit_tampering_fails_even_if_rehashed(self):
        self.append(observation())
        self.append(observation())
        events, records = self.export()
        changes = [dict(schema_version="audit/2"), dict(sequence=1), dict(previous_sha256="0" * 64),
                   dict(subject_id="other"), dict(event_type="enforcement"), dict(extra=None),
                   dict(recorded_at="today"), dict(sequence=True)]
        for update in changes:
            bad = deepcopy(events)
            bad[0].update(update)
            resign(bad[0])
            with self.subTest(update=update), self.assertRaises(ReplayError):
                replay(bad[:1], records, CONTEXT, self.inputs)
        bad = deepcopy(events)
        bad[0]["producer"]["version"] = "2"
        with self.assertRaises(ReplayError):
            replay(bad, records, CONTEXT, self.inputs)
        bad = deepcopy(events)
        bad[1]["event_id"] = bad[0]["event_id"]
        resign(bad[1])
        with self.assertRaises(ReplayError):
            replay(bad, records, CONTEXT, self.inputs)

    def test_forged_accepted_semantics_fail_even_with_valid_hashes(self):
        self.append(observation())
        events, records = self.export()
        for value in (None, 99):
            bad = deepcopy(events)
            o = observation(value=value)
            bad[0]["payload"]["accepted_observation_ref"]["sha256"] = record_sha256(o)
            resign(bad[0])
            with self.assertRaises(ReplayError):
                replay(bad, {"obs-0": o}, CONTEXT, self.inputs)
        bad = deepcopy(events)
        bad[0]["payload"]["reason_codes"] = ["duplicate_noop"]
        resign(bad[0])
        with self.assertRaises(ReplayError):
            replay(bad, records, CONTEXT, self.inputs)

    def test_checkpoint_detects_tail_removal_and_input_substitution(self):
        self.append(observation())
        self.append(observation())
        events, records = self.export()
        checkpoint = {"event_count": len(events), "last_sha256": events[-1]["sha256"], "inputs_sha256": self.inputs.sha256}
        replay(events, records, CONTEXT, self.inputs, checkpoint=checkpoint)
        with self.assertRaises(ReplayError):
            replay(events[:1], records, CONTEXT, self.inputs, checkpoint=checkpoint)
        with self.assertRaises(ReplayError):
            replay(events, records, CONTEXT, self.inputs, checkpoint=dict(checkpoint, inputs_sha256="0" * 64))

    def test_external_io_is_absent_in_validation_and_replay(self):
        self.append(observation())
        events, records = self.export()
        with patch("socket.socket", side_effect=AssertionError("network prohibited")), patch("builtins.open", side_effect=AssertionError("file acquisition prohibited")):
            validate_observation(canonical_bytes(observation()), CONTEXT, self.inputs, ObservationState())
            replay(events, records, CONTEXT, self.inputs)

    def test_invalid_recorder_is_not_an_observation_disposition(self):
        for changes in (dict(event_id=" "), dict(recorded_at="now"), dict(producer={"id": "x"})):
            with self.assertRaises(ValueError):
                self.append(observation(), **changes)
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM events").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
