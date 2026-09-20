from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Any


@dataclass(frozen=True, slots=True)
class GateResult:
    passed: bool
    reasons: tuple[str, ...]


def _multiplicity_ok(value: object) -> bool:
    return value in {"pass", "not_applicable"}


def recompute_emergence_gate(record: Mapping[str, Any]) -> GateResult:
    reasons: list[str] = []

    if record.get("protocol_valid") is not True:
        reasons.append("protocol_invalid")
    if record.get("verifier_result") != "pass":
        reasons.append("verifier_not_pass")
    if not _multiplicity_ok(record.get("multiplicity_result")):
        reasons.append("multiplicity_not_satisfied")

    delta = record.get("delta_emergent")
    delta_min = record.get("delta_min")
    lower = record.get("lower_confidence_bound")

    if not isinstance(delta, (int, float)) or not isinstance(delta_min, (int, float)):
        reasons.append("invalid_delta_fields")
    elif delta < delta_min:
        reasons.append("delta_below_minimum")

    if not isinstance(lower, (int, float)) or not isinstance(delta_min, (int, float)):
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

    delta = record.get("delta_transfer")
    delta_min = record.get("transfer_delta_min")
    lower = record.get("lower_confidence_bound")

    if not isinstance(delta, (int, float)) or not isinstance(delta_min, (int, float)):
        reasons.append("invalid_delta_fields")
    elif delta < delta_min:
        reasons.append("delta_below_minimum")

    if not isinstance(lower, (int, float)) or not isinstance(delta_min, (int, float)):
        reasons.append("invalid_confidence_fields")
    elif lower < delta_min:
        reasons.append("lower_bound_below_minimum")

    if record.get("transfer_classification") != "confirmed":
        reasons.append("classification_not_confirmed")

    return GateResult(not reasons, tuple(reasons))


def cross_family_eligible_configurations(
    records: Iterable[Mapping[str, Any]],
    *,
    minimum_families: int = 2,
) -> frozenset[str]:
    if minimum_families < 2:
        raise ValueError("system-level cross-family gate must require at least 2 families")

    families_by_config: dict[str, set[str]] = {}
    for record in records:
        if not recompute_transfer_gate(record).passed:
            continue
        config_id = record.get("configuration_id")
        family_id = record.get("task_family_id")
        if not isinstance(config_id, str) or not config_id:
            continue
        if not isinstance(family_id, str) or not family_id:
            continue
        families_by_config.setdefault(config_id, set()).add(family_id)

    return frozenset(
        config_id
        for config_id, families in families_by_config.items()
        if len(families) >= minimum_families
    )
