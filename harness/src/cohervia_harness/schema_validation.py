from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from .canonical import canonical_json
from .selectors import recompute_emergence_gate, recompute_transfer_gate, validate_estimate_statistics

from jsonschema import Draft202012Validator


def load_schema(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_instance(instance: dict[str, Any], schema_path: str | Path) -> None:
    canonical_json(instance)  # Reject NaN/Infinity anywhere in an artifact.
    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: str(list(e.path)))
    if errors:
        joined = "; ".join(error.message for error in errors)
        raise ValueError(joined)
    stage = instance.get("record_type")
    if stage in ("configuration_emergence_assessment", "configuration_transfer_assessment"):
        transfer = stage == "configuration_transfer_assessment"
        label_key = "transfer_classification" if transfer else "emergence_classification"
        statistics = validate_estimate_statistics(instance, transfer=transfer,
                                                 allow_missing=instance[label_key] == "invalid")
        if not statistics.passed:
            raise ValueError("; ".join(statistics.reasons))
    if stage == "configuration_emergence_assessment" and instance.get("emergence_classification") == "positive":
        gate = recompute_emergence_gate(instance)
        if not gate.passed:
            raise ValueError("; ".join(gate.reasons))
    if stage == "configuration_transfer_assessment" and instance.get("transfer_classification") == "confirmed":
        gate = recompute_transfer_gate(instance)
        if not gate.passed:
            raise ValueError("; ".join(gate.reasons))
