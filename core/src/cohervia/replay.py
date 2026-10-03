"""Deterministic integrity replay. No clocks, filesystem lookups or estimators."""
from .canonical import canonical_bytes, parse_json, record_sha256
from .inputs import digest, identifier, keys, ref, timestamp, versioned
from .observations import ObservationState, REJECT, _shape, validate_observation

EVENT_FIELDS = "schema_version event_id run_id trajectory_id subject_id sequence recorded_at producer event_type related_ids payload_version payload previous_sha256 sha256"
CODES = REJECT | {"sequence_gap", "availability_regression", "unresolved_reference", "valid", "duplicate_noop"}


class ReplayError(ValueError):
    pass


def _event_shape(e):
    if not keys(e, EVENT_FIELDS):
        return False
    if e["schema_version"] != "audit/0.1" or e["payload_version"] != "observation-validation/0.1" or e["event_type"] != "observation_validation":
        return False
    if not all(identifier(e[k]) for k in ("event_id", "run_id", "trajectory_id", "subject_id")):
        return False
    if type(e["sequence"]) is not int or e["sequence"] < 0 or not timestamp(e["recorded_at"]) or not versioned(e["producer"]):
        return False
    if not digest(e["sha256"]) or (e["previous_sha256"] is not None and not digest(e["previous_sha256"])):
        return False
    related = e["related_ids"]
    if not keys(related, "observation_id snapshot_id recommendation_id decision_id") or any(v is not None and not identifier(v) for v in related.values()):
        return False
    if any(related[k] is not None for k in ("snapshot_id", "recommendation_id", "decision_id")):
        return False
    p = e["payload"]
    if not keys(p, "submission_sha256 disposition reason_codes accepted_observation_ref") or not digest(p["submission_sha256"]):
        return False
    codes = p["reason_codes"]
    if type(codes) is not list or not codes or any(type(c) is not str or c not in CODES for c in codes) or codes != sorted(set(codes)):
        return False
    if p["disposition"] == "accept":
        return codes in (["valid"], ["duplicate_noop"]) and ref(p["accepted_observation_ref"]) and related["observation_id"] == p["accepted_observation_ref"]["id"]
    if p["disposition"] not in ("reject", "quarantine") or p["accepted_observation_ref"] is not None or set(codes) & {"valid", "duplicate_noop"}:
        return False
    return p["disposition"] == ("reject" if set(codes) & REJECT else "quarantine")


def replay(events, observations, context, inputs, *, checkpoint=None):
    """Return reconstructed state or fail closed.

    Optional trusted checkpoint is {event_count, last_sha256, inputs_sha256}.
    Without one, a valid truncated prefix or rewritten whole stream is undetectable.
    Rejected raw submissions are deliberately absent: replay checks their disposition
    schema and chain, not the truth of diagnostic claims or recorder authenticity.
    """
    state = ObservationState()
    previous = None
    event_ids = set()
    count = 0
    try:
        for count, raw_event in enumerate(events, start=1):
            if not _event_shape(raw_event):
                raise ReplayError("invalid audit schema")
            e = parse_json(canonical_bytes(raw_event))
            if not _event_shape(e):
                raise ReplayError("invalid audit schema")
            if e["sequence"] != count - 1 or e["previous_sha256"] != previous:
                raise ReplayError("broken audit sequence/link")
            if any(e[k] != v for k, v in context.as_dict().items()) or e["event_id"] in event_ids:
                raise ReplayError("audit identity/event-id mismatch")
            unsigned = {k: v for k, v in e.items() if k != "sha256"}
            if record_sha256(unsigned) != e["sha256"]:
                raise ReplayError("audit digest mismatch")
            p = e["payload"]
            if p["disposition"] == "accept":
                r = p["accepted_observation_ref"]
                o = observations.get(r["id"])
                if o is None or not _shape(o) or record_sha256(o) != r["sha256"] or o.get("observation_id") != r["id"]:
                    raise ReplayError("missing or corrupt accepted observation")
                result = validate_observation(canonical_bytes(o), context, inputs, state)
                if result.disposition != "accept" or list(result.reason_codes) != p["reason_codes"]:
                    raise ReplayError("accepted disposition cannot be reconstructed")
                if result.reason_codes == ("valid",):
                    state.add(o)
            event_ids.add(e["event_id"])
            previous = e["sha256"]
        if set(observations) != set(state.accepted):
            raise ReplayError("unreferenced accepted observation")
        if checkpoint is not None:
            if not keys(checkpoint, "event_count last_sha256 inputs_sha256") or type(checkpoint["event_count"]) is not int or checkpoint["event_count"] < 0 or not digest(checkpoint["inputs_sha256"]) or (checkpoint["last_sha256"] is not None and not digest(checkpoint["last_sha256"])):
                raise ReplayError("invalid trusted checkpoint")
            expected = {"event_count": count, "last_sha256": previous, "inputs_sha256": inputs.sha256}
            if checkpoint != expected:
                raise ReplayError("trusted checkpoint mismatch")
    except (ValueError, TypeError, UnicodeError, KeyError, OverflowError, RecursionError) as exc:
        if isinstance(exc, ReplayError):
            raise
        raise ReplayError("malformed replay input") from exc
    return state
