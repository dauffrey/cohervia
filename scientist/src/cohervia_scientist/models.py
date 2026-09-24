from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class EpistemicState(StrEnum):
    OBSERVED = "observed"
    INFERRED = "inferred"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class FailureClass(StrEnum):
    THEORY = "theory_failure"
    CONSTRUCT = "construct_failure"
    PREDICTION = "prediction_failure"
    GENERALIZATION = "generalization_failure"
    MEASUREMENT = "measurement_failure"
    CALIBRATION = "calibration_failure"
    INTERVENTION = "intervention_failure"
    EXPERIMENTAL = "experimental_failure"
    STATISTICAL = "statistical_failure"
    PROVENANCE = "provenance_failure"
    IMPLEMENTATION = "implementation_failure"
    UNKNOWN = "unknown"


class ResearchPhase(StrEnum):
    QUESTION = "question"
    HYPOTHESIS = "hypothesis"
    CRITIQUE = "critique"
    EXPLORATION = "exploration"
    PREREGISTRATION = "preregistration"
    FROZEN = "frozen"
    CONFIRMATORY_PENDING = "confirmatory_pending"
    RESULT_RECORDED = "result_recorded"
    THEORY_REVISION = "theory_revision"
    PROMOTION_PROPOSED = "promotion_proposed"


@dataclass(frozen=True)
class Prediction:
    claim: str
    theory_version: str
    confidence: float | None = None
    falsifies: list[str] = field(default_factory=list)
    experiment_id: str | None = None
    id: str = field(default_factory=lambda: f"pred-{uuid4().hex[:12]}")
    created_at: str = field(default_factory=utc_now)

    def validate(self) -> None:
        if not self.claim.strip():
            raise ValueError("prediction claim must not be empty")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


@dataclass(frozen=True)
class Anomaly:
    observed: str
    expected: str
    theory_version: str
    explanation_state: EpistemicState = EpistemicState.UNKNOWN
    competing_hypotheses: list[str] = field(default_factory=list)
    priority: str = "medium"
    id: str = field(default_factory=lambda: f"anom-{uuid4().hex[:12]}")
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        if not self.observed.strip():
            raise ValueError("observed must not be empty")
        return asdict(self)


@dataclass(frozen=True)
class FailurePostmortem:
    hypothesis: str
    observed: str
    failure_class: FailureClass
    lesson: str
    theory_version: str
    cause: str | None = None
    affected_constructs: list[str] = field(default_factory=list)
    theory_change: str | None = None
    unresolved: list[str] = field(default_factory=list)
    follow_up: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: f"fail-{uuid4().hex[:12]}")
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        if not self.hypothesis.strip():
            raise ValueError("hypothesis must not be empty")
        if not self.observed.strip():
            raise ValueError("observed must not be empty")
        if not self.lesson.strip():
            raise ValueError("lesson must not be empty")
        return asdict(self)
