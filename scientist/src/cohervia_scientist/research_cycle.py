from __future__ import annotations

from dataclasses import dataclass

from .models import ResearchPhase


class ResearchGateError(RuntimeError):
    pass


_ALLOWED: dict[ResearchPhase, set[ResearchPhase]] = {
    ResearchPhase.QUESTION: {ResearchPhase.HYPOTHESIS},
    ResearchPhase.HYPOTHESIS: {ResearchPhase.CRITIQUE, ResearchPhase.QUESTION},
    ResearchPhase.CRITIQUE: {ResearchPhase.HYPOTHESIS, ResearchPhase.EXPLORATION},
    ResearchPhase.EXPLORATION: {
        ResearchPhase.HYPOTHESIS,
        ResearchPhase.CRITIQUE,
        ResearchPhase.PREREGISTRATION,
    },
    ResearchPhase.PREREGISTRATION: {
        ResearchPhase.EXPLORATION,
        ResearchPhase.FROZEN,
    },
    ResearchPhase.FROZEN: {ResearchPhase.CONFIRMATORY_PENDING},
    ResearchPhase.CONFIRMATORY_PENDING: {ResearchPhase.RESULT_RECORDED},
    ResearchPhase.RESULT_RECORDED: {ResearchPhase.THEORY_REVISION},
    ResearchPhase.THEORY_REVISION: {
        ResearchPhase.QUESTION,
        ResearchPhase.PROMOTION_PROPOSED,
    },
    ResearchPhase.PROMOTION_PROPOSED: {ResearchPhase.QUESTION},
}


@dataclass
class ResearchCycle:
    phase: ResearchPhase = ResearchPhase.QUESTION
    preregistration_hash: str | None = None
    frozen_manifest_hash: str | None = None
    evaluator_id: str | None = None

    def transition(self, target: ResearchPhase) -> None:
        allowed = _ALLOWED[self.phase]
        if target not in allowed:
            raise ResearchGateError(
                f"illegal research transition: {self.phase.value} -> {target.value}"
            )

        if target is ResearchPhase.FROZEN and not self.preregistration_hash:
            raise ResearchGateError(
                "cannot freeze without a preregistration hash"
            )

        if target is ResearchPhase.CONFIRMATORY_PENDING:
            if not self.frozen_manifest_hash:
                raise ResearchGateError(
                    "cannot enter confirmatory pending without a frozen manifest"
                )
            if not self.evaluator_id:
                raise ResearchGateError(
                    "cannot enter confirmatory pending without an independent evaluator id"
                )

        self.phase = target

    def register_preregistration(self, artifact_hash: str) -> None:
        if self.phase is not ResearchPhase.PREREGISTRATION:
            raise ResearchGateError(
                "preregistration hash may only be registered in preregistration phase"
            )
        if not artifact_hash.strip():
            raise ValueError("artifact hash must not be empty")
        self.preregistration_hash = artifact_hash

    def register_freeze(self, manifest_hash: str, evaluator_id: str) -> None:
        if self.phase is not ResearchPhase.FROZEN:
            raise ResearchGateError(
                "freeze manifest may only be registered after entering frozen phase"
            )
        if not manifest_hash.strip() or not evaluator_id.strip():
            raise ValueError("manifest hash and evaluator id are required")
        self.frozen_manifest_hash = manifest_hash
        self.evaluator_id = evaluator_id
