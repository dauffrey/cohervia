from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


def _require_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _strings(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ValueError(f"{key} must be a list of strings")
    return [x.strip() for x in value if x.strip()]


@dataclass(frozen=True)
class ResearchQuestion:
    question: str
    importance: str
    why_now: str
    theory_targets: list[str] = field(default_factory=list)
    prior_evidence: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchQuestion":
        return cls(
            question=_require_text(data, "question"),
            importance=_require_text(data, "importance"),
            why_now=_require_text(data, "why_now"),
            theory_targets=_strings(data, "theory_targets"),
            prior_evidence=_strings(data, "prior_evidence"),
            unknowns=_strings(data, "unknowns"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Hypothesis:
    id: str
    statement: str
    mechanism: str
    prediction: str
    falsification_condition: str
    novelty_rationale: str
    theory_targets: list[str] = field(default_factory=list)
    prior_failures_considered: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Hypothesis":
        return cls(
            id=_require_text(data, "id"),
            statement=_require_text(data, "statement"),
            mechanism=_require_text(data, "mechanism"),
            prediction=_require_text(data, "prediction"),
            falsification_condition=_require_text(data, "falsification_condition"),
            novelty_rationale=_require_text(data, "novelty_rationale"),
            theory_targets=_strings(data, "theory_targets"),
            prior_failures_considered=_strings(data, "prior_failures_considered"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Critique:
    hypothesis_id: str
    recommendation: str
    fatal_flaws: list[str] = field(default_factory=list)
    confounds: list[str] = field(default_factory=list)
    leakage_risks: list[str] = field(default_factory=list)
    alternative_explanations: list[str] = field(default_factory=list)
    required_revisions: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Critique":
        recommendation = _require_text(data, "recommendation")
        allowed = {"reject", "revise", "advance_exploratory"}
        if recommendation not in allowed:
            raise ValueError(
                f"recommendation must be one of {sorted(allowed)}"
            )
        return cls(
            hypothesis_id=_require_text(data, "hypothesis_id"),
            recommendation=recommendation,
            fatal_flaws=_strings(data, "fatal_flaws"),
            confounds=_strings(data, "confounds"),
            leakage_risks=_strings(data, "leakage_risks"),
            alternative_explanations=_strings(data, "alternative_explanations"),
            required_revisions=_strings(data, "required_revisions"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateSelection:
    hypothesis_id: str
    rationale: str
    revisions_applied: list[str]
    residual_uncertainties: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CandidateSelection":
        return cls(
            hypothesis_id=_require_text(data, "hypothesis_id"),
            rationale=_require_text(data, "rationale"),
            revisions_applied=_strings(data, "revisions_applied"),
            residual_uncertainties=_strings(data, "residual_uncertainties"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExperimentPlan:
    title: str
    hypothesis_id: str
    purpose: str
    environment: str
    independent_variables: list[str]
    dependent_variables: list[str]
    controls: list[str]
    baselines: list[str]
    procedure: list[str]
    analysis_plan: list[str]
    failure_criteria: list[str]
    stopping_conditions: list[str]
    provenance_requirements: list[str]
    evidence_class: str
    requires_holdout: bool
    authority_effect: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExperimentPlan":
        evidence_class = _require_text(data, "evidence_class")
        if evidence_class != "exploratory":
            raise ValueError("v0.2 experiment plans must be exploratory")
        requires_holdout = data.get("requires_holdout")
        if requires_holdout is not False:
            raise ValueError("v0.2 experiment plans may not require a holdout")
        authority_effect = _require_text(data, "authority_effect")
        if authority_effect != "none":
            raise ValueError("v0.2 experiment plans may not affect authority")
        return cls(
            title=_require_text(data, "title"),
            hypothesis_id=_require_text(data, "hypothesis_id"),
            purpose=_require_text(data, "purpose"),
            environment=_require_text(data, "environment"),
            independent_variables=_strings(data, "independent_variables"),
            dependent_variables=_strings(data, "dependent_variables"),
            controls=_strings(data, "controls"),
            baselines=_strings(data, "baselines"),
            procedure=_strings(data, "procedure"),
            analysis_plan=_strings(data, "analysis_plan"),
            failure_criteria=_strings(data, "failure_criteria"),
            stopping_conditions=_strings(data, "stopping_conditions"),
            provenance_requirements=_strings(data, "provenance_requirements"),
            evidence_class=evidence_class,
            requires_holdout=requires_holdout,
            authority_effect=authority_effect,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IntegrityReview:
    disposition: str
    unsupported_claims: list[str]
    evidence_boundary_issues: list[str]
    unresolved_concerns: list[str]
    required_changes: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IntegrityReview":
        disposition = _require_text(data, "disposition")
        allowed = {"acceptable_exploratory", "revise", "reject"}
        if disposition not in allowed:
            raise ValueError(f"disposition must be one of {sorted(allowed)}")
        return cls(
            disposition=disposition,
            unsupported_claims=_strings(data, "unsupported_claims"),
            evidence_boundary_issues=_strings(data, "evidence_boundary_issues"),
            unresolved_concerns=_strings(data, "unresolved_concerns"),
            required_changes=_strings(data, "required_changes"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
