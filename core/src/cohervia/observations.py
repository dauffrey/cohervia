"""Pure validation: explicit missingness, provenance and ordering dispositions."""
from dataclasses import dataclass, field

from .canonical import bytes_sha256, canonical_bytes, parse_canonical, parse_json
from .inputs import identifier, keys, ref, timestamp, versioned

FIELDS = "schema_version observation_id run_id trajectory_id subject_id sequence event_time available_at phase metric_id metric_version value_type value units status rationale uncertainty evidence_refs input_observation_ids derivation source collector scorer config acquisition_context"
REJECT = {"invalid_record", "identity_mismatch", "conflicting_id", "sequence_reuse", "invalid_provenance"}


@dataclass
class ObservationState:
    accepted: dict = field(default_factory=dict)
    next_sequence: int = 0
    available_at: str | None = None

    def add(self, observation):
        observation = parse_canonical(canonical_bytes(observation))
        self.accepted[observation["observation_id"]] = observation
        self.next_sequence += 1
        self.available_at = observation["available_at"]

    def snapshot(self):
        return {"accepted": parse_canonical(canonical_bytes(self.accepted)), "next_sequence": self.next_sequence,
                "available_at": self.available_at}


@dataclass(frozen=True)
class ValidationResult:
    disposition: str
    reason_codes: tuple[str, ...]
    observation: dict | None = None


def _shape(o):
    if not keys(o, FIELDS):
        return False
    ids = "observation_id run_id trajectory_id subject_id metric_id metric_version".split()
    if not all(identifier(o[k]) for k in ids):
        return False
    if o["schema_version"] != "observation/0.1" or type(o["sequence"]) is not int or o["sequence"] < 0:
        return False
    if not all(timestamp(o[k]) for k in ("event_time", "available_at")) or o["available_at"] < o["event_time"]:
        return False
    if o["phase"] not in ("pre_action", "post_action", "pre_intervention", "post_intervention", "follow_up"):
        return False
    if o["value_type"] not in ("number", "boolean", "string") or o["status"] not in ("observed", "inferred", "unknown", "not_applicable"):
        return False
    if type(o["rationale"]) is not str or not o["rationale"].strip():
        return False
    if o["value_type"] == "number":
        if not identifier(o["units"]):
            return False
    elif o["units"] is not None:
        return False
    missing = o["status"] in ("unknown", "not_applicable")
    if missing:
        if o["value"] is not None or o["uncertainty"] is not None:
            return False
    else:
        expected = {"number": (int, float), "boolean": (bool,), "string": (str,)}[o["value_type"]]
        if type(o["value"]) not in expected:
            return False
    u = o["uncertainty"]
    if u is not None and not (keys(u, "kind value basis") and u["kind"] == "confidence" and type(u["value"]) in (int, float) and 0 <= u["value"] <= 1 and type(u["basis"]) is str and u["basis"].strip()):
        return False
    refs = o["evidence_refs"]
    if type(refs) is not list or any(not ref(r) for r in refs) or len({r["id"] for r in refs}) != len(refs) or (not missing and not refs):
        return False
    inputs = o["input_observation_ids"]
    if type(inputs) is not list or any(not identifier(i) for i in inputs) or len(set(inputs)) != len(inputs):
        return False
    inferred = o["status"] == "inferred"
    if inferred:
        if not inputs or not versioned(o["derivation"]) or o["scorer"] is None:
            return False
    elif inputs or o["derivation"] is not None:
        return False
    scorer = o["scorer"]
    if scorer is not None and not (keys(scorer, "id version type") and versioned({"id": scorer["id"], "version": scorer["version"]}) and scorer["type"] in ("human", "model", "automated", "hybrid")):
        return False
    return (versioned(o["source"]) and versioned(o["collector"]) and ref(o["config"])
            and keys(o["acquisition_context"], "adapter_id adapter_version")
            and all(identifier(v) for v in o["acquisition_context"].values()))


def validate_observation(raw, context, inputs, state, *, reserved_ids=()):
    """No mutations or IO. Rejections take priority; all applicable codes are sorted."""
    try:
        o = parse_json(raw)
    except (ValueError, UnicodeError, OverflowError, RecursionError):
        return ValidationResult("reject", ("invalid_record",))
    reasons = set()
    shape = _shape(o)
    if not shape:
        reasons.add("invalid_record")
    if type(o) is dict and any(k in o and o[k] != v for k, v in context.as_dict().items()):
        reasons.add("identity_mismatch")
    if reasons:
        return ValidationResult("reject", tuple(sorted(reasons)))
    previous = state.accepted.get(o["observation_id"])
    if previous is not None:
        if canonical_bytes(previous) == canonical_bytes(o):
            return ValidationResult("accept", ("duplicate_noop",), o)
        return ValidationResult("reject", ("conflicting_id",))
    if o["observation_id"] in reserved_ids:
        return ValidationResult("reject", ("conflicting_id",))
    definition = inputs.definitions.get((o["metric_id"], o["metric_version"]))
    if definition is None:
        reasons.add("unresolved_reference")
    else:
        if o["value_type"] != definition["value_type"] or o["units"] != definition["units"]:
            reasons.add("invalid_record")
        value = o["value"]
        if value is not None and o["value_type"] == definition["value_type"]:
            if o["value_type"] == "number":
                if (definition["minimum"] is not None and value < definition["minimum"]) or (definition["maximum"] is not None and value > definition["maximum"]):
                    reasons.add("invalid_record")
            if o["value_type"] == "string" and definition["allowed_strings"] is not None and value not in definition["allowed_strings"]:
                reasons.add("invalid_record")
    if o["config"] != inputs.config:
        reasons.add("invalid_provenance")
    manifest, artifacts = inputs.manifest, inputs.artifacts
    for r in o["evidence_refs"]:
        expected = manifest.get(r["id"])
        artifact = artifacts.get(r["id"])
        if expected is None or artifact is None:
            reasons.add("unresolved_reference")
        if (expected is not None and r["sha256"] != expected) or (artifact is not None and bytes_sha256(artifact) != r["sha256"]):
            reasons.add("invalid_provenance")
    for i in o["input_observation_ids"]:
        prior = state.accepted.get(i)
        if prior is None or any(prior[k] != v for k, v in context.as_dict().items()):
            reasons.add("unresolved_reference")
        elif prior["available_at"] > o["available_at"]:
            reasons.add("invalid_provenance")
    if o["sequence"] < state.next_sequence:
        reasons.add("sequence_reuse")
    elif o["sequence"] > state.next_sequence:
        reasons.add("sequence_gap")
    if state.available_at is not None and o["available_at"] < state.available_at:
        reasons.add("availability_regression")
    if reasons:
        return ValidationResult("reject" if reasons & REJECT else "quarantine", tuple(sorted(reasons)))
    return ValidationResult("accept", ("valid",), o)
