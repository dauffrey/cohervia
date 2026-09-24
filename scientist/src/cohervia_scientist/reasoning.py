from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .context import RepositoryContext
from .json_utils import parse_json_object
from .memory import ScientificMemory
from .prompts import (
    CRITIC_INSTRUCTIONS,
    EXPERIMENT_INSTRUCTIONS,
    HYPOTHESIS_INSTRUCTIONS,
    INTEGRITY_INSTRUCTIONS,
    QUESTION_INSTRUCTIONS,
    SELECTION_INSTRUCTIONS,
)
from .provider import ReasoningProvider
from .schemas import (
    CandidateSelection,
    Critique,
    ExperimentPlan,
    Hypothesis,
    IntegrityReview,
    ResearchQuestion,
)


@dataclass(frozen=True)
class ResearchPacket:
    status: str
    created_at: str
    question: ResearchQuestion
    relevant_memory: list[dict[str, Any]]
    hypotheses: list[Hypothesis]
    critiques: list[Critique]
    selection: CandidateSelection
    experiment: ExperimentPlan
    integrity_review: IntegrityReview

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "created_at": self.created_at,
            "question": self.question.to_dict(),
            "relevant_memory": self.relevant_memory,
            "hypotheses": [item.to_dict() for item in self.hypotheses],
            "critiques": [item.to_dict() for item in self.critiques],
            "selection": self.selection.to_dict(),
            "experiment": self.experiment.to_dict(),
            "integrity_review": self.integrity_review.to_dict(),
        }


class ScientificReasoner:
    def __init__(
        self,
        *,
        provider: ReasoningProvider,
        repo_root: Path,
        scientist_root: Path,
        hypothesis_count: int = 4,
        memory_limit: int = 6,
    ):
        self.provider = provider
        self.repo_root = Path(repo_root).resolve()
        self.scientist_root = Path(scientist_root).resolve()
        self.hypothesis_count = hypothesis_count
        self.memory_limit = memory_limit
        self.context = RepositoryContext(self.repo_root, self.scientist_root)
        self.memory = ScientificMemory(self.scientist_root)

    def _call_json(self, instructions: str, prompt: str) -> dict[str, Any]:
        text = self.provider.complete(
            instructions=instructions,
            prompt=prompt,
        )
        return parse_json_object(text)

    def frame_question(self, override: str | None = None) -> ResearchQuestion:
        context = self.context.build()
        override_text = override.strip() if override else "NONE"
        prompt = f"""APPROVED REPOSITORY CONTEXT:
{context}

USER-SUPPLIED QUESTION OVERRIDE:
{override_text}

Return:
{{
  "question": "one falsifiable or discriminating research question",
  "importance": "why it matters scientifically",
  "why_now": "why current evidence makes it timely",
  "theory_targets": ["node or edge"],
  "prior_evidence": ["bounded evidence only"],
  "unknowns": ["important unknown"]
}}

If an override is supplied, preserve its scientific intent while making it
precise enough to guide hypothesis generation.
"""
        return ResearchQuestion.from_dict(
            self._call_json(QUESTION_INSTRUCTIONS, prompt)
        )

    def generate_hypotheses(
        self,
        question: ResearchQuestion,
        relevant_memory: list[dict[str, Any]],
    ) -> list[Hypothesis]:
        prompt = f"""RESEARCH QUESTION:
{json.dumps(question.to_dict(), indent=2)}

RELEVANT PRIOR FAILURES/ANOMALIES:
{json.dumps(relevant_memory, indent=2)}

Generate exactly {self.hypothesis_count} competing candidate hypotheses.

Return:
{{
  "hypotheses": [
    {{
      "id": "H1",
      "statement": "...",
      "mechanism": "...",
      "prediction": "...",
      "falsification_condition": "...",
      "novelty_rationale": "...",
      "theory_targets": ["..."],
      "prior_failures_considered": ["failure/anomaly id or lesson"]
    }}
  ]
}}
"""
        raw = self._call_json(HYPOTHESIS_INSTRUCTIONS, prompt)
        values = raw.get("hypotheses")
        if not isinstance(values, list):
            raise ValueError("hypothesis response must contain hypotheses list")
        hypotheses = [
            Hypothesis.from_dict(item)
            for item in values
            if isinstance(item, dict)
        ]
        if len(hypotheses) != self.hypothesis_count:
            raise ValueError(
                f"expected {self.hypothesis_count} hypotheses, got {len(hypotheses)}"
            )
        ids = [item.id for item in hypotheses]
        if len(set(ids)) != len(ids):
            raise ValueError("hypothesis ids must be unique")
        return hypotheses

    def critique(
        self,
        question: ResearchQuestion,
        hypotheses: list[Hypothesis],
        relevant_memory: list[dict[str, Any]],
    ) -> list[Critique]:
        prompt = f"""RESEARCH QUESTION:
{json.dumps(question.to_dict(), indent=2)}

HYPOTHESES:
{json.dumps([x.to_dict() for x in hypotheses], indent=2)}

PRIOR FAILURES/ANOMALIES:
{json.dumps(relevant_memory, indent=2)}

Return one critique per hypothesis:
{{
  "critiques": [
    {{
      "hypothesis_id": "H1",
      "recommendation": "reject|revise|advance_exploratory",
      "fatal_flaws": [],
      "confounds": [],
      "leakage_risks": [],
      "alternative_explanations": [],
      "required_revisions": []
    }}
  ]
}}
"""
        raw = self._call_json(CRITIC_INSTRUCTIONS, prompt)
        values = raw.get("critiques")
        if not isinstance(values, list):
            raise ValueError("critic response must contain critiques list")
        critiques = [
            Critique.from_dict(item)
            for item in values
            if isinstance(item, dict)
        ]
        expected = {x.id for x in hypotheses}
        actual = {x.hypothesis_id for x in critiques}
        if actual != expected or len(critiques) != len(hypotheses):
            raise ValueError("critic must return exactly one critique per hypothesis")
        return critiques

    def select(
        self,
        question: ResearchQuestion,
        hypotheses: list[Hypothesis],
        critiques: list[Critique],
    ) -> CandidateSelection:
        prompt = f"""RESEARCH QUESTION:
{json.dumps(question.to_dict(), indent=2)}

HYPOTHESES:
{json.dumps([x.to_dict() for x in hypotheses], indent=2)}

CRITIQUES:
{json.dumps([x.to_dict() for x in critiques], indent=2)}

Return:
{{
  "hypothesis_id": "one existing id",
  "rationale": "why this candidate is most informative to explore",
  "revisions_applied": ["critic revision carried forward"],
  "residual_uncertainties": ["..."]
}}
"""
        selection = CandidateSelection.from_dict(
            self._call_json(SELECTION_INSTRUCTIONS, prompt)
        )
        valid_ids = {x.id for x in hypotheses}
        if selection.hypothesis_id not in valid_ids:
            raise ValueError("selection references unknown hypothesis")
        return selection

    def design_experiment(
        self,
        question: ResearchQuestion,
        hypotheses: list[Hypothesis],
        critiques: list[Critique],
        selection: CandidateSelection,
    ) -> ExperimentPlan:
        chosen = next(x for x in hypotheses if x.id == selection.hypothesis_id)
        critique = next(
            x for x in critiques if x.hypothesis_id == selection.hypothesis_id
        )
        prompt = f"""RESEARCH QUESTION:
{json.dumps(question.to_dict(), indent=2)}

SELECTED HYPOTHESIS:
{json.dumps(chosen.to_dict(), indent=2)}

CRITIQUE:
{json.dumps(critique.to_dict(), indent=2)}

SELECTION AND REQUIRED REVISIONS:
{json.dumps(selection.to_dict(), indent=2)}

Return:
{{
  "title": "...",
  "hypothesis_id": "{selection.hypothesis_id}",
  "purpose": "...",
  "environment": "bounded synthetic or analytical environment",
  "independent_variables": ["..."],
  "dependent_variables": ["..."],
  "controls": ["..."],
  "baselines": ["..."],
  "procedure": ["..."],
  "analysis_plan": ["..."],
  "failure_criteria": ["..."],
  "stopping_conditions": ["..."],
  "provenance_requirements": ["..."],
  "evidence_class": "exploratory",
  "requires_holdout": false,
  "authority_effect": "none"
}}
"""
        plan = ExperimentPlan.from_dict(
            self._call_json(EXPERIMENT_INSTRUCTIONS, prompt)
        )
        if plan.hypothesis_id != selection.hypothesis_id:
            raise ValueError("experiment plan references wrong hypothesis")
        return plan

    def integrity_review(
        self,
        *,
        question: ResearchQuestion,
        hypotheses: list[Hypothesis],
        critiques: list[Critique],
        selection: CandidateSelection,
        experiment: ExperimentPlan,
    ) -> IntegrityReview:
        packet = {
            "question": question.to_dict(),
            "hypotheses": [x.to_dict() for x in hypotheses],
            "critiques": [x.to_dict() for x in critiques],
            "selection": selection.to_dict(),
            "experiment": experiment.to_dict(),
        }
        prompt = f"""CANDIDATE RESEARCH PACKET:
{json.dumps(packet, indent=2)}

Return:
{{
  "disposition": "acceptable_exploratory|revise|reject",
  "unsupported_claims": [],
  "evidence_boundary_issues": [],
  "unresolved_concerns": [],
  "required_changes": []
}}
"""
        return IntegrityReview.from_dict(
            self._call_json(INTEGRITY_INSTRUCTIONS, prompt)
        )

    def run(self, question_override: str | None = None) -> ResearchPacket:
        question = self.frame_question(question_override)
        query = " ".join(
            [question.question, *question.theory_targets, *question.unknowns]
        )
        relevant_memory = self.memory.relevant(
            query,
            limit=self.memory_limit,
        )
        hypotheses = self.generate_hypotheses(question, relevant_memory)
        critiques = self.critique(question, hypotheses, relevant_memory)
        selection = self.select(question, hypotheses, critiques)
        experiment = self.design_experiment(
            question,
            hypotheses,
            critiques,
            selection,
        )
        review = self.integrity_review(
            question=question,
            hypotheses=hypotheses,
            critiques=critiques,
            selection=selection,
            experiment=experiment,
        )
        return ResearchPacket(
            status="candidate_reasoning",
            created_at=datetime.now(timezone.utc).isoformat(),
            question=question,
            relevant_memory=relevant_memory,
            hypotheses=hypotheses,
            critiques=critiques,
            selection=selection,
            experiment=experiment,
            integrity_review=review,
        )


def write_packet(packet: ResearchPacket, output: Path) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(packet.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output
