"""Bounded acquisition, local observation ingestion, and exact archive replay."""
from datetime import datetime, timezone
from importlib import import_module, metadata
from pathlib import Path
import os
import platform
import rfc8785

from cohervia import AuditStore, Context, FrozenInputs, replay
from cohervia.canonical import bytes_sha256, canonical_bytes, json_bytes, parse_canonical, record_sha256
from cohervia.inputs import identifier, keys, timestamp

from .protocol import (VERSION, INSTRUCTIONS, MAX_CALLS, MAX_OUTPUT_TOKENS, MAX_TEXT_BYTES,
                       TIMEOUT_SECONDS, catalog, definitions, model_id, outcomes)
from .provider import normalize

SOURCES = ("cohervia", "cohervia_harness", "cohervia_pilot", "cohervia.canonical", "cohervia.inputs", "cohervia.observations", "cohervia.audit",
           "cohervia.replay", "cohervia_harness.tasks", "cohervia_pilot.protocol",
           "cohervia_pilot.provider", "cohervia_pilot.runner", "cohervia_pilot.cli")


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _write(path, raw):
    """Atomic replacement within the fresh owned run directory."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def _sources():
    return {"source:" + name: Path(import_module(name).__file__).read_bytes() for name in SOURCES}


def _plan(model, kind, sources):
    if not model_id(model) or kind not in ("openai_responses", "scripted_instrumentation"):
        raise ValueError("explicit supported provider/model required")
    if rfc8785.__version__ != "0.1.4":
        raise ValueError("pilot requires the pinned JCS dependency")
    try:
        sdk_version = metadata.version("openai") if kind == "openai_responses" else None
    except metadata.PackageNotFoundError:
        sdk_version = None
    return {"schema_version": VERSION, "mode": "live_development" if kind == "openai_responses" else "scripted_instrumentation",
            "provider": kind, "requested_model": model, "sdk_version": sdk_version, "jcs_version": rfc8785.__version__, "python_version": platform.python_version(),
            "max_calls": MAX_CALLS, "max_output_tokens": MAX_OUTPUT_TOKENS,
            "max_text_bytes": MAX_TEXT_BYTES, "timeout_seconds": TIMEOUT_SECONDS, "retries": 0,
            "tools": [], "instructions": INSTRUCTIONS, "catalog_sha256": record_sha256(catalog()),
            "source_hashes": {k: bytes_sha256(v) for k, v in sources.items()},
            "confirmatory": False, "holdout_access": False}


def _records(task, receipt, context, config):
    values = outcomes(receipt["provider_result"], task)
    observations = []
    for sequence, (metric, value) in enumerate(values.items()):
        inferred = sequence > 0 and value is not None
        status = "unknown" if value is None else "inferred" if inferred else "observed"
        observations.append({"schema_version": "observation/0.1", "observation_id": task["id"] + ":" + metric,
            **context.as_dict(), "sequence": sequence, "event_time": receipt["started_at"],
            "available_at": receipt["finished_at"], "phase": "post_action", "metric_id": metric,
            "metric_version": "1", "value_type": "boolean", "value": value, "units": None,
            "status": status, "rationale": ("No completed usable response; task correctness is unknown."
                if value is None else "Fixed public development criterion, computed from the recorded provider receipt."),
            "uncertainty": None, "evidence_refs": [{"id": "public-catalog", "sha256": record_sha256(catalog())},
                {"id": "receipt:" + task["id"], "sha256": record_sha256(receipt)}],
            "input_observation_ids": [o["observation_id"] for o in observations] if inferred else [],
            "derivation": {"id": "public-json-exact-match", "version": "1"} if inferred else None,
            "source": {"id": config["provider"], "version": "1"},
            "collector": {"id": "public-pilot-recorder", "version": "1"},
            "scorer": {"id": "public-json-exact-match", "version": "1", "type": "automated"} if sequence > 0 else None,
            "config": {"id": "public-pilot-plan", "sha256": record_sha256(config)},
            "acquisition_context": {"adapter_id": "public-pilot", "adapter_version": "0.1.0"}})
    return observations


def run(provider, output_dir, run_id, *, clock=utc_now):
    if not identifier(run_id):
        raise ValueError("nonblank run ID required")
    # No caller-supplied prompts, task catalogs, artifact paths or verifier policies.
    sources = _sources()
    plan = _plan(provider.model, provider.kind, sources)
    target = Path(output_dir).resolve()
    repository = Path(__file__).resolve().parents[3]
    if (repository / "docs/implementation/RECONCILIATION_BASELINE.json").exists():
        if target.is_relative_to(repository) and not target.is_relative_to(repository / "pilot/runs"):
            raise ValueError("repository output must be inside pilot/runs; protected tracks cannot be written")
    target.mkdir(parents=True, exist_ok=False)
    _write(target / "plan.json", canonical_bytes(plan))  # Written before any provider call.
    artifacts = dict(sources, **{"public-catalog": canonical_bytes(catalog())})
    receipts = []
    stopped = False
    previous_finished = None
    try:
        for task in catalog():
            started = clock()
            if not timestamp(started) or (previous_finished is not None and started < previous_finished):
                raise ValueError("invalid acquisition timestamp")
            if stopped:
                result = {"status": "not_attempted", "text": None, "response_id": None, "actual_model": None, "usage": None}
            else:
                try:
                    result = normalize(provider.complete(instructions=INSTRUCTIONS, prompt=task["prompt"]))
                except Exception:
                    result = {"status": "provider_error", "text": None, "response_id": None, "actual_model": None, "usage": None}
            finished = clock()
            if not timestamp(finished) or finished < started:
                raise ValueError("acquisition clock regressed")
            previous_finished = finished
            receipt = {"schema_version": "pilot-receipt/0.1", "task_id": task["id"],
                       "attempted": not stopped, "started_at": started, "finished_at": finished,
                       "provider_result": result}
            stopped = stopped or result["status"] == "authentication_error"
            receipts.append(receipt)
            raw = canonical_bytes(receipt)
            artifacts["receipt:" + task["id"]] = raw
            _write(target / (task["id"] + ".receipt.json"), raw)
    finally:
        provider.close()
    # Detect source edits during acquisition before claiming source identity.
    if _sources() != sources:
        raise ValueError("pilot source changed during acquisition; raw receipts retained, no verified report")
    frozen = FrozenInputs(definitions(), "public-pilot-plan", plan,
                          {k: bytes_sha256(v) for k, v in artifacts.items()}, artifacts)
    streams = []
    with AuditStore(target / "observations.sqlite") as store:
        for task, receipt in zip(catalog(), receipts):
            context = Context(run_id, task["id"], "model:" + provider.model)
            for observation in _records(task, receipt, context, plan):
                event = store.append_submission(json_bytes(observation), context, frozen,
                    event_id=observation["observation_id"] + ":validation", recorded_at=receipt["finished_at"],
                    producer={"id": "public-pilot-recorder", "version": "1"})
                if event["payload"]["reason_codes"] != ["valid"]:
                    raise ValueError("pilot mapping failed core validation; no verified report")
            events, observations = store.export(context, frozen)
            streams.append({"context": context.as_dict(), "events": events, "observations": observations,
                            "checkpoint": {"event_count": len(events), "last_sha256": events[-1]["sha256"],
                                           "inputs_sha256": frozen.sha256}})
    bundle = {"schema_version": "pilot-bundle/0.1", "run_id": run_id, "inputs": frozen.document,
              "artifacts": {k: v.decode("utf-8") for k, v in artifacts.items()}, "streams": streams}
    bundle["sha256"] = record_sha256(bundle)
    report = replay_bundle(bundle)
    _write(target / "bundle.json", canonical_bytes(bundle))
    _write(target / "report.md", report.encode("utf-8"))
    return bundle, report


def replay_bundle(bundle, *, expected_sha256=None):
    """Recompute the report solely from captured local records; never execute source bytes."""
    if not keys(bundle, "schema_version run_id inputs artifacts streams sha256") or bundle["schema_version"] != "pilot-bundle/0.1":
        raise ValueError("unsupported pilot bundle")
    if record_sha256({k: v for k, v in bundle.items() if k != "sha256"}) != bundle["sha256"]:
        raise ValueError("bundle digest mismatch")
    if expected_sha256 is not None and expected_sha256 != bundle["sha256"]:
        raise ValueError("external bundle checkpoint mismatch")
    if not identifier(bundle["run_id"]):
        raise ValueError("invalid run identity")
    document = bundle["inputs"]
    if not keys(document, "schema_version definitions config configuration evidence_manifest") or document["schema_version"] != "validation-inputs/0.1":
        raise ValueError("invalid frozen inputs")
    if type(bundle["artifacts"]) is not dict or any(type(v) is not str for v in bundle["artifacts"].values()):
        raise ValueError("artifacts must be supplied UTF-8 bytes, never paths")
    artifacts = {k: v.encode("utf-8") for k, v in bundle["artifacts"].items()}
    frozen = FrozenInputs(document["definitions"], "public-pilot-plan", document["configuration"], document["evidence_manifest"], artifacts)
    if frozen.document != document or document["definitions"] != definitions():
        raise ValueError("metric/configuration binding mismatch")
    plan = document["configuration"]
    if not keys(plan, "schema_version mode provider requested_model sdk_version jcs_version python_version max_calls max_output_tokens max_text_bytes timeout_seconds retries tools instructions catalog_sha256 source_hashes confirmatory holdout_access"):
        raise ValueError("invalid pilot plan")
    expected_mode = {"openai_responses": "live_development", "scripted_instrumentation": "scripted_instrumentation"}.get(plan["provider"])
    if (plan["schema_version"] != VERSION or expected_mode is None or plan["mode"] != expected_mode or not model_id(plan["requested_model"])
        or plan["jcs_version"] != "0.1.4" or plan["max_calls"] != MAX_CALLS or type(plan["max_calls"]) is not int or plan["max_output_tokens"] != MAX_OUTPUT_TOKENS
        or type(plan["max_output_tokens"]) is not int or plan["max_text_bytes"] != MAX_TEXT_BYTES or plan["timeout_seconds"] != TIMEOUT_SECONDS
        or plan["retries"] != 0 or type(plan["retries"]) is not int or plan["tools"] != [] or plan["instructions"] != INSTRUCTIONS
        or plan["confirmatory"] is not False or plan["holdout_access"] is not False or plan["catalog_sha256"] != record_sha256(catalog())):
        raise ValueError("pilot protocol or authority boundary mismatch")
    expected_artifacts = {"public-catalog"} | {"receipt:" + task["id"] for task in catalog()} | {"source:" + name for name in SOURCES}
    if set(artifacts) != expected_artifacts or set(frozen.manifest) != expected_artifacts or plan["source_hashes"] != {k: bytes_sha256(artifacts[k]) for k in expected_artifacts if k.startswith("source:")}:
        raise ValueError("source/evidence inventory mismatch")
    if artifacts["public-catalog"] != canonical_bytes(catalog()):
        raise ValueError("public task catalog changed")
    if any(bytes_sha256(v) != frozen.manifest[k] for k, v in artifacts.items()):
        raise ValueError("artifact bytes mismatch")
    if type(bundle["streams"]) is not list or len(bundle["streams"]) != MAX_CALLS:
        raise ValueError("wrong stream count")
    rows = []
    stopped = False
    previous_finished = None
    for task, stream in zip(catalog(), bundle["streams"]):
        if not keys(stream, "context events observations checkpoint"):
            raise ValueError("invalid stream")
        context = Context(bundle["run_id"], task["id"], "model:" + plan["requested_model"])
        if stream["context"] != context.as_dict():
            raise ValueError("task/run/model identity mismatch")
        receipt = parse_canonical(artifacts["receipt:" + task["id"]])
        if not keys(receipt, "schema_version task_id attempted started_at finished_at provider_result") or receipt["schema_version"] != "pilot-receipt/0.1" or receipt["task_id"] != task["id"]:
            raise ValueError("invalid receipt")
        if not timestamp(receipt["started_at"]) or not timestamp(receipt["finished_at"]) or receipt["finished_at"] < receipt["started_at"] or receipt["attempted"] is not (not stopped) or (previous_finished is not None and receipt["started_at"] < previous_finished):
            raise ValueError("invalid receipt acquisition/attempt order")
        previous_finished = receipt["finished_at"]
        result = receipt["provider_result"]
        unattempted = {"status": "not_attempted", "text": None, "response_id": None, "actual_model": None, "usage": None}
        if (stopped and result != unattempted) or (not stopped and normalize(result) != result):
            raise ValueError("invalid bounded provider result")
        stopped = stopped or result["status"] == "authentication_error"
        state = replay(stream["events"], stream["observations"], context, frozen, checkpoint=stream["checkpoint"])
        expected = {o["observation_id"]: o for o in _records(task, receipt, context, plan)}
        if canonical_bytes(state.accepted) != canonical_bytes(expected) or len(stream["events"]) != 3:
            raise ValueError("captured observations do not match public verifier outcomes")
        success = outcomes(result, task)["task_success"]
        rows.append((task["id"], result["status"], "unknown" if success is None else "pass" if success else "fail", result["actual_model"] or "unknown"))
    label = "LIVE PUBLIC DEVELOPMENT ATTEMPTS" if plan["mode"] == "live_development" else "SCRIPTED INSTRUMENTATION — NOT A LIVE MODEL RUN"
    report = ["# Bounded public pilot", "", label, "", "Requested model: `" + plan["requested_model"] + "`", "",
              "| Public task | Provider status | Fixed criterion | Returned model |", "| --- | --- | --- | --- |"]
    report += [f"| {task} | {status} | {success} | {actual_model} |" for task, status, success, actual_model in rows]
    report += ["", "Counts: " + ", ".join(f"{label}={sum(row[2] == label for row in rows)}" for label in ("pass", "fail", "unknown")) + ".",
               "", "Verified replay: 3 task streams, 9 accepted observations, complete local evidence hashes.",
               "", "Bundle SHA-256: `" + bundle["sha256"] + "`", "",
               "This public development pilot is not a benchmark, confirmatory experiment, Scientist qualification,",
               "capability-emergence result or governor evaluation. Known public answers may be in model training data.",
               "No model tools, permissions or holdout access were provided. No result is promoted into Scientist.",
               "Replay is deterministic; model outputs are not. Bundle/checkpoints are locally recorded integrity",
               "values, not authenticated external custody or proof of provider identity. No scientific promotion follows.", ""]
    return "\n".join(report)
