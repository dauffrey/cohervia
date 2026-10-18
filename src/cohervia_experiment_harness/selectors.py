from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite
from typing import Any, Iterable, Mapping


@dataclass(frozen=True, slots=True)
class GateResult:
    passed: bool
    reasons: tuple[str, ...]


def _multiplicity_ok(value: object) -> bool:
    return type(value) is str and value in {"pass", "not_applicable"}


def _finite_number(value: object) -> bool:
    return type(value) in (int, float) and isfinite(value)


def recompute_emergence_gate(record: Mapping[str, Any]) -> GateResult:
    reasons: list[str] = []

    if record.get("protocol_valid") is not True:
        reasons.append("protocol_invalid")
    if record.get("verifier_result") != "pass":
        reasons.append("verifier_not_pass")
    if not _multiplicity_ok(record.get("multiplicity_result")):
        reasons.append("multiplicity_not_satisfied")

    observed = record.get("mean_observed_value")
    baseline = record.get("baseline_prediction")
    delta = record.get("delta_emergent")
    if not _finite_number(observed) or not _finite_number(baseline):
        reasons.append("missing_or_invalid_residual_components")
    elif not _finite_number(delta) or not isclose(delta, observed - baseline, rel_tol=0, abs_tol=1e-9):
        reasons.append("residual_components_disagree")
    delta_min = record.get("delta_min")
    lower = record.get("lower_confidence_bound")

    if not _finite_number(delta) or not _finite_number(delta_min):
        reasons.append("invalid_delta_fields")
    elif delta < delta_min:
        reasons.append("delta_below_minimum")

    if not _finite_number(lower) or not _finite_number(delta_min):
        reasons.append("invalid_confidence_fields")
    elif lower < delta_min:
        reasons.append("lower_bound_below_minimum")

    if record.get("emergence_classification") != "positive":
        reasons.append("classification_not_positive")

    return GateResult(not reasons, tuple(reasons))


def recompute_transfer_gate(record: Mapping[str, Any]) -> GateResult:
    reasons: list[str] = []

    if record.get("protocol_valid") is not True:
        reasons.append("protocol_invalid")
    if record.get("verifier_result") != "pass":
        reasons.append("verifier_not_pass")
    if not _multiplicity_ok(record.get("multiplicity_result")):
        reasons.append("multiplicity_not_satisfied")

    observed = record.get("mean_observed_value")
    baseline = record.get("baseline_prediction")
    delta = record.get("delta_transfer")
    if not _finite_number(observed) or not _finite_number(baseline):
        reasons.append("missing_or_invalid_residual_components")
    elif not _finite_number(delta) or not isclose(delta, observed - baseline, rel_tol=0, abs_tol=1e-9):
        reasons.append("residual_components_disagree")
    delta_min = record.get("transfer_delta_min")
    lower = record.get("lower_confidence_bound")

    if not _finite_number(delta) or not _finite_number(delta_min):
        reasons.append("invalid_delta_fields")
    elif delta < delta_min:
        reasons.append("delta_below_minimum")

    if not _finite_number(lower) or not _finite_number(delta_min):
        reasons.append("invalid_confidence_fields")
    elif lower < delta_min:
        reasons.append("lower_bound_below_minimum")

    if record.get("transfer_classification") != "confirmed":
        reasons.append("classification_not_confirmed")

    return GateResult(not reasons, tuple(reasons))


def cross_family_eligible_configurations(
    emergence_records: Iterable[Mapping[str, Any]],
    transfer_records: Iterable[Mapping[str, Any]],
    *,
    minimum_families: int = 2,
) -> frozenset[str]:
    """Return configs that independently pass A and B in enough task families."""
    if minimum_families < 2:
        raise ValueError("system-level cross-family gate must require at least 2 families")

    a_positive: set[tuple[str, str, str]] = set()
    for record in emergence_records:
        if not recompute_emergence_gate(record).passed:
            continue
        config_id = record.get("configuration_id")
        family_id = record.get("task_family_id")
        digest = record.get("system_configuration_hash")
        if all(type(x) is str and x for x in (config_id, family_id, digest)):
            a_positive.add((config_id, family_id, digest))

    families_by_config: dict[tuple[str, str], set[str]] = {}
    hashes_by_id: dict[str, set[str]] = {}
    for record in transfer_records:
        if not recompute_transfer_gate(record).passed:
            continue
        config_id = record.get("configuration_id")
        family_id = record.get("task_family_id")
        digest = record.get("system_configuration_hash")
        if not all(type(x) is str and x for x in (config_id, family_id, digest)):
            continue
        hashes_by_id.setdefault(config_id, set()).add(digest)
        if (config_id, family_id, digest) not in a_positive:
            continue
        families_by_config.setdefault((config_id, digest), set()).add(family_id)

    return frozenset(
        config_id
        for (config_id, digest), families in families_by_config.items()
        if len(families) >= minimum_families and len(hashes_by_id[config_id]) == 1
    )
