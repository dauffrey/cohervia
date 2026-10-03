"""Pure apparatus diagnostics. No holdout reader or execution authorization."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True, slots=True)
class GateResult:
    passed: bool
    reasons: tuple[str, ...]


def _finite(value: object) -> bool:
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def validate_estimate_statistics(record: Mapping[str, Any], *, transfer: bool, allow_missing: bool = False) -> GateResult:
    """Check arithmetic regardless of the scientific classification label."""
    reasons: list[str] = []
    delta_key = "delta_transfer" if transfer else "delta_emergent"
    minimum_key = "transfer_delta_min" if transfer else "delta_min"
    delta, minimum, lower = (record.get(k) for k in (delta_key, minimum_key, "lower_confidence_bound"))
    mean, baseline = (record.get(k) for k in ("mean_observed_value", "baseline_prediction"))
    numeric = {delta_key: delta, minimum_key: minimum, "lower_confidence_bound": lower,
               "mean_observed_value": mean, "baseline_prediction": baseline}
    for key, value in numeric.items():
        if allow_missing and value is None and key != minimum_key:
            continue
        if not _finite(value):
            reasons.append("invalid_numeric:" + key)
        elif not (-1 <= value <= 1 if key in (delta_key, "lower_confidence_bound") else 0 <= value <= 1):
            reasons.append("out_of_range:" + key)
    if all(_finite(x) for x in (delta, mean, baseline)):
        # Frozen draft serialization tolerance; does not estimate uncertainty.
        if not math.isclose(delta, mean - baseline, rel_tol=0, abs_tol=1e-12):
            reasons.append("residual_component_mismatch")
    if _finite(lower) and _finite(delta) and lower > delta:
        reasons.append("lower_bound_above_estimate")
    return GateResult(not reasons, tuple(reasons))


def _gate(record: Mapping[str, Any], *, transfer: bool) -> GateResult:
    reasons: list[str] = []
    delta_key = "delta_transfer" if transfer else "delta_emergent"
    minimum_key = "transfer_delta_min" if transfer else "delta_min"
    label_key = "transfer_classification" if transfer else "emergence_classification"
    label = "confirmed" if transfer else "positive"
    if record.get("protocol_valid") is not True:
        reasons.append("protocol_invalid")
    if record.get("verifier_result") != "pass":
        reasons.append("verifier_not_pass")
    if record.get("multiplicity_result") not in ("pass", "not_applicable"):
        reasons.append("multiplicity_not_satisfied")
    for key in ("experiment_id", "configuration_id", "system_configuration_hash",
                "task_family_id", "comparator_definition_hash", "capability_endpoint_id"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            reasons.append("missing_identity:" + key)
    for key in ("n_target_trials", "n_comparator_trials"):
        if type(record.get(key)) is not int or record[key] < 1:
            reasons.append("invalid_trial_count:" + key)
    for key in ("supporting_trial_observation_ids", "supporting_comparator_observation_ids"):
        refs = record.get(key)
        if (not isinstance(refs, list) or not refs
                or not all(isinstance(x, str) and x for x in refs)
                or len(refs) != len(set(refs))):
            reasons.append("invalid_supporting_refs:" + key)
    reasons.extend(validate_estimate_statistics(record, transfer=transfer).reasons)
    delta, minimum, lower = (record.get(k) for k in (delta_key, minimum_key, "lower_confidence_bound"))
    if _finite(delta) and _finite(minimum) and delta < minimum:
        reasons.append("delta_below_minimum")
    if _finite(lower) and _finite(minimum) and lower < minimum:
        reasons.append("lower_bound_below_minimum")
    if record.get(label_key) != label:
        reasons.append("classification_not_" + label)
    return GateResult(not reasons, tuple(reasons))


def recompute_emergence_gate(record: Mapping[str, Any]) -> GateResult:
    return _gate(record, transfer=False)


def recompute_transfer_gate(record: Mapping[str, Any]) -> GateResult:
    return _gate(record, transfer=True)


def cross_family_eligible_configurations(
    emergence_records: Iterable[Mapping[str, Any]],
    transfer_records: Iterable[Mapping[str, Any]],
    *, minimum_families: int = 2,
) -> frozenset[str]:
    """Diagnostic only; never opens a holdout or accepts a scientific result.

    Reject ambiguous configuration identities across both stages. Match A/B on
    experiment, configuration/hash, family, comparator and endpoint. Conflicting
    duplicate assessments cannot become eligible through a favorable row.
    """
    if type(minimum_families) is not int or minimum_families < 2:
        raise ValueError("system-level cross-family gate must require at least 2 families")
    a_rows, b_rows = list(emergence_records), list(transfer_records)
    identities: dict[tuple[str, str], set[str]] = {}
    for r in a_rows + b_rows:
        cid, eid, digest = (r.get(k) for k in ("configuration_id", "experiment_id", "system_configuration_hash"))
        if all(isinstance(x, str) and x for x in (cid, eid)):
            identities.setdefault((eid, cid), set()).add(digest if isinstance(digest, str) else "")
    ambiguous = {key for key, hashes in identities.items() if len(hashes) != 1 or "" in hashes}

    def key(r):
        values = tuple(r.get(k) for k in ("experiment_id", "configuration_id", "system_configuration_hash",
                       "task_family_id", "comparator_definition_hash", "capability_endpoint_id"))
        return values if all(isinstance(x, str) and x for x in values) else None

    def stage(rows, gate):
        groups = {}
        for r in rows:
            k = key(r)
            if k is not None:
                groups.setdefault(k, []).append(r)
        return {k for k, group in groups.items()
                if all(gate(r).passed for r in group) and all(r == group[0] for r in group)}

    common = stage(a_rows, recompute_emergence_gate) & stage(b_rows, recompute_transfer_gate)
    families = {}
    for eid, cid, digest, family, comparator, endpoint in common:
        if (eid, cid) not in ambiguous:
            families.setdefault((eid, cid, digest, comparator, endpoint), set()).add(family)
    return frozenset(k[1] for k, fs in families.items() if len(fs) >= minimum_families)
