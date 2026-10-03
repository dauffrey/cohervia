from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Partition(StrEnum):
    INSTRUMENTATION = "instrumentation"
    DEVELOPMENT = "development"
    CAPABILITY_HOLDOUT_A = "capability_holdout_a"
    TRANSFER_HOLDOUT_B = "transfer_holdout_b"
    GOVERNANCE_HOLDOUT_C = "governance_holdout_c"

    @property
    def is_confirmatory(self) -> bool:
        return self in {
            Partition.CAPABILITY_HOLDOUT_A,
            Partition.TRANSFER_HOLDOUT_B,
            Partition.GOVERNANCE_HOLDOUT_C,
        }


class EvidenceQuality(StrEnum):
    INSTRUMENTATION = "instrumentation"
    EXPLORATORY = "exploratory"
    CONFIRMATORY = "confirmatory"


@dataclass(frozen=True, slots=True)
class TrialConfig:
    experiment_id: str
    trial_id: str
    task_family_id: str
    partition: Partition
    system_configuration_hash: str
    model_identity: str
    compute_step_limit: int = 100

    def validate_for_harness(self) -> None:
        if not isinstance(self.partition, Partition):
            raise ValueError("partition must be an explicit Partition enum")
        if not self.experiment_id.startswith("COH-EXP-"):
            raise ValueError("experiment_id must use the COH-EXP namespace")
        if type(self.compute_step_limit) is not int or self.compute_step_limit < 1:
            raise ValueError("compute_step_limit must be positive")
        if self.partition.is_confirmatory:
            raise PermissionError(
                "confirmatory partitions are disabled in the instrumentation harness"
            )
        if self.experiment_id != "COH-EXP-0001":
            raise ValueError("this fixture harness only supports COH-EXP-0001")


@dataclass(frozen=True, slots=True)
class TrialResult:
    trial_id: str
    partition: Partition
    completed: bool
    paused: bool
    score: float | None
    verifier_result: str
    first_divergence_event_id: str | None
    audit_root_hash: str
    event_count: int
    metadata: dict[str, Any] = field(default_factory=dict)
