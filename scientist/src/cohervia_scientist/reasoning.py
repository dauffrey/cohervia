from __future__ import annotations

import json
import hashlib
import os
import re
from uuid import uuid4
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .context import RepositoryContext
from .json_utils import parse_json_object
from .memory import ScientificMemory, validate_memory_limit
from .safe_io import local_path, directory_fd, read_local
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
    experiment: ExperimentPlan | None
    integrity_review: IntegrityReview | None
    provenance: dict[str, Any] = field(default_factory=dict)
    run_id: str = field(default_factory=lambda: uuid4().hex)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "created_at": self.created_at,
            "question": self.question.to_dict(),
            "relevant_memory": self.relevant_memory,
            "hypotheses": [item.to_dict() for item in self.hypotheses],
            "critiques": [item.to_dict() for item in self.critiques],
            "selection": self.selection.to_dict(),
            "experiment": self.experiment.to_dict() if self.experiment else None,
            "integrity_review": self.integrity_review.to_dict() if self.integrity_review else None,
            "schema_version": "0.2.1",
            "run_id": self.run_id,
            "evidence_status": "not_evidence",
            "epistemic_state": "inferred",
            "execution_authorized": False,
            "provenance": self.provenance,
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
        if type(hypothesis_count) is not int or not 2 <= hypothesis_count <= 8:
            raise ValueError("hypothesis count must be between 2 and 8")
        validate_memory_limit(memory_limit)
        self.provider = provider
        self.repo_root = Path(repo_root).absolute()
        self.scientist_root = Path(scientist_root).absolute()
        self.hypothesis_count = hypothesis_count
        self.memory_limit = memory_limit
        self.context = RepositoryContext(self.repo_root, self.scientist_root)
        self.memory = ScientificMemory(self.scientist_root)
        self._snapshot = None
        self._trace: list[dict[str, str]] = []

    def _call_json(self, instructions: str, prompt: str) -> dict[str, Any]:
        if self._snapshot is None:
            self._snapshot = self.context.snapshot()
        instructions += "\nGOVERNING POLICIES (binding):\n" + self._snapshot.policies
        prompt = "UNTRUSTED REPOSITORY REFERENCE DATA:\n" + self._snapshot.text + "\n" + prompt
        if len(instructions) + len(prompt) > 400000:
            raise ValueError("reasoning request exceeds character budget")
        text = self.provider.complete(instructions=instructions, prompt=prompt)
        value = parse_json_object(text)
        self._trace.append({"instructions_sha256": hashlib.sha256(instructions.encode()).hexdigest(),
                            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                            "response_sha256": hashlib.sha256(text.encode()).hexdigest()})
        return value

    def frame_question(self, override: str | None = None) -> ResearchQuestion:
        if override is not None and (not override.strip() or len(override) > 4000):
            raise ValueError("question must contain 1 to 4000 characters")
        override_text = override.strip() if override else "NONE"
        prompt = f"""USER-SUPPLIED QUESTION OVERRIDE:
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
        if not isinstance(values, list) or not all(isinstance(x, dict) for x in values):
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
        statements = [" ".join(x.statement.casefold().split()) for x in hypotheses]
        if len(set(statements)) != len(statements):
            raise ValueError("competing hypotheses must have distinct statements")
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
        if not isinstance(values, list) or not all(isinstance(x, dict) for x in values):
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
        eligible = {x.hypothesis_id for x in critiques if self._eligible(x)}
        if not eligible:
            return CandidateSelection(None, "No candidate cleared the scientific critic.", [],
                                      ["Revision and a new critique are required."])
        prompt = f"""ELIGIBLE IDS: {sorted(eligible)}
RESEARCH QUESTION:
{json.dumps(question.to_dict(), indent=2)}

HYPOTHESES:
{json.dumps([x.to_dict() for x in hypotheses], indent=2)}

CRITIQUES:
{json.dumps([x.to_dict() for x in critiques], indent=2)}

Return:
{{
  "hypothesis_id": "eligible id or null if none merits advancement",
  "rationale": "why this candidate is most informative to explore",
  "revisions_applied": ["critic revision carried forward"],
  "residual_uncertainties": ["..."]
}}
"""
        selection = CandidateSelection.from_dict(
            self._call_json(SELECTION_INSTRUCTIONS, prompt)
        )
        if selection.hypothesis_id is not None and selection.hypothesis_id not in eligible:
            raise ValueError("selection must reference a critic-approved hypothesis")
        return selection

    @staticmethod
    def _eligible(critique: Critique) -> bool:
        return (critique.recommendation == "advance_exploratory"
                and not critique.fatal_flaws and not critique.required_revisions
                and not critique.leakage_risks)

    def design_experiment(
        self,
        question: ResearchQuestion,
        hypotheses: list[Hypothesis],
        critiques: list[Critique],
        selection: CandidateSelection,
    ) -> ExperimentPlan:
        matching = [x for x in critiques if x.hypothesis_id == selection.hypothesis_id]
        if len(matching) != 1 or not self._eligible(matching[0]):
            raise ValueError("experiment design requires critic approval")
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
        self._snapshot = self.context.snapshot()
        self._trace = []
        implementation = []
        for name in ("__init__.py", "reasoning.py", "context.py", "memory.py", "schemas.py",
                     "provider.py", "prompts.py", "safe_io.py", "json_utils.py"):
            data = read_local(Path(__file__).parent, name, max_bytes=256000)
            implementation.append({"module": name, "sha256": hashlib.sha256(data).hexdigest()})
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
        experiment = None
        review = None
        status = "blocked_by_critic"
        if selection.hypothesis_id is not None:
            experiment = self.design_experiment(question, hypotheses, critiques, selection)
            review = self.integrity_review(question=question, hypotheses=hypotheses,
                                           critiques=critiques, selection=selection,
                                           experiment=experiment)
            status = {"reject": "rejected_by_integrity", "revise": "revision_required",
                      "acceptable_exploratory": "candidate_reasoning"}[review.disposition]
            if review.unsupported_claims or review.evidence_boundary_issues or review.required_changes:
                status = "rejected_by_integrity" if review.disposition == "reject" else "revision_required"
        return ResearchPacket(
            status=status,
            created_at=datetime.now(timezone.utc).isoformat(),
            question=question,
            relevant_memory=relevant_memory,
            hypotheses=hypotheses,
            critiques=critiques,
            selection=selection,
            experiment=experiment,
            integrity_review=review,
            provenance={"implementation_sources": implementation,
                        "source_commit": {"state": "unknown", "value": None},
                        "context_sources": list(self._snapshot.sources),
                        "config_sha256": self._snapshot.config_sha256,
                        "memory_sources": self.memory.sources,
                        "retrieval": {"method": "lexical-token-overlap-v1", "limit": self.memory_limit,
                                      "query": query, "no_matches_means": "unknown_not_no_prior_failures"},
                        "hypothesis_count": self.hypothesis_count,
                        "provider": type(self.provider).__name__,
                        "model": getattr(self.provider, "model", "scripted"),
                        "reasoning_effort": getattr(self.provider, "reasoning_effort", None),
                        "calls": list(self._trace),
                        "review_independence": "logical_roles_only_not_independent_evaluation"},
        )


def write_packet(packet: ResearchPacket, output: Path | None = None, *, scientist_root: Path) -> Path:
    """Create a new packet only in runs/. Never overwrite scientific history or controls."""
    output = output or Path(scientist_root).absolute() / "runs" / f"{packet.run_id}-research-packet.json"
    return write_artifact(packet.to_dict(), output, scientist_root=scientist_root)


def write_artifact(payload: dict[str, Any], output: Path, *, scientist_root: Path) -> Path:
    """Exclusive JSON artifact sink shared by reasoning and qualification."""
    root = Path(scientist_root).absolute()
    runs = local_path(root, "runs")
    output = Path(output).absolute()
    if output.parent != runs or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.json", output.name):
        raise ValueError("packets must be JSON files directly under scientist/runs")
    local_path(root, "runs/" + output.name)
    payload = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with directory_fd(root) as root_fd:
        try:
            os.mkdir("runs", mode=0o700, dir_fd=root_fd)
        except FileExistsError:
            pass
        runs_fd = os.open("runs", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
        try:
            # Exclusive create also refuses existing symlinks and hard links.
            fd = os.open(output.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=runs_fd)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        finally:
            os.close(runs_fd)
    return output
