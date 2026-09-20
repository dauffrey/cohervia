from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


FREEZE_FIELD_MAP: dict[str, str] = {
    "model_identity": "model_identity",
    "orchestrator_identity": "orchestrator_identity",
    "orchestrator_version": "orchestrator_version",
    "tool_versions": "tool_versions_hash",
    "task_generation_procedure": "task_generation_procedure_hash",
    "development_manifest": "development_manifest_hash",
    "capability_holdout_a_manifest": "capability_holdout_a_manifest_hash",
    "transfer_holdout_b_manifest": "transfer_holdout_b_manifest_hash",
    "governance_holdout_c_manifest": "governance_holdout_c_manifest_hash",
    "baseline_estimator": "baseline_estimator_hash",
    "transfer_estimator": "transfer_estimator_hash",
    "sample_size_plan": "sample_size_plan_hash",
    "run_order_plan": "run_order_plan_hash",
    "retry_policy": "retry_policy_hash",
    "exclusion_rule": "exclusion_rule_hash",
    "missing_data_policy": "missing_data_policy_hash",
    "compute_time_limits": "compute_time_limits_hash",
    "primary_endpoint_definitions": "primary_endpoint_definitions_hash",
    "secondary_endpoint_definitions": "secondary_endpoint_definitions_hash",
    "delta_min": "delta_min_value",
    "transfer_delta_min": "transfer_delta_min_value",
    "uncertainty_procedure": "uncertainty_procedure_hash",
    "multiplicity_rule": "multiplicity_rule_hash",
    "success_threshold": "success_threshold_spec_hash",
    "comparator_definition": "comparator_definition_hash",
    "governance_control_definition": "governance_control_definition_hash",
    "holdout_selection_rule": "holdout_selection_rule_hash",
    "observer": "observer_hash",
    "observer_features": "observer_feature_spec_hash",
    "observer_feature_mask": "observer_feature_mask_hash",
    "observer_normalization_policy": "observer_normalization_policy_hash",
    "observer_thresholds": "observer_threshold_hash",
    "capability_evaluator": "capability_evaluator_hash",
    "transfer_evaluator": "transfer_evaluator_hash",
    "governance_evaluator": "governance_evaluator_hash",
    "verifier_identity": "verifier_hash",
    "configuration_hashes": "configuration_hash",
    "environment_image": "environment_image_hash",
    "channel_inventory": "channel_inventory_hash",
    "stop_conditions": "stop_conditions_hash",
    "stop_controller": "stop_controller_hash",
    "audit_immutability_configuration": "audit_immutability_config_hash",
}


@dataclass(frozen=True, slots=True)
class FrozenArtifact:
    name: str
    sha256: str


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def freeze_inventory(paths: dict[str, str | Path]) -> tuple[FrozenArtifact, ...]:
    return tuple(
        FrozenArtifact(name=name, sha256=sha256_file(path))
        for name, path in sorted(paths.items())
    )


def matrix_freeze_requirements(matrix_path: str | Path) -> tuple[str, ...]:
    with Path(matrix_path).open("r", encoding="utf-8") as handle:
        matrix = yaml.safe_load(handle)
    values = matrix.get("freeze_required_before_confirmatory_execution", [])
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise ValueError("matrix freeze requirements must be a list of strings")
    return tuple(values)


def verify_required_fields(
    manifest_path: str | Path,
    required_fields: Iterable[str],
) -> tuple[str, ...]:
    with Path(manifest_path).open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    return tuple(field for field in required_fields if field not in manifest)


def verify_freeze_contract(
    *,
    matrix_path: str | Path,
    manifest_path: str | Path,
) -> tuple[str, ...]:
    requirements = matrix_freeze_requirements(matrix_path)
    unknown_requirements = tuple(
        requirement for requirement in requirements if requirement not in FREEZE_FIELD_MAP
    )
    if unknown_requirements:
        return tuple(f"unmapped requirement: {name}" for name in unknown_requirements)

    manifest_fields = tuple(FREEZE_FIELD_MAP[name] for name in requirements)
    missing = verify_required_fields(manifest_path, manifest_fields)
    return tuple(f"missing manifest field: {field}" for field in missing)
