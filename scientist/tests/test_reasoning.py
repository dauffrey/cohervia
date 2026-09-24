import json
import tempfile
import unittest
from pathlib import Path

from cohervia_scientist.json_utils import parse_json_object
from cohervia_scientist.memory import ScientificMemory
from cohervia_scientist.provider import ScriptedProvider
from cohervia_scientist.reasoning import ScientificReasoner
from cohervia_scientist.schemas import ExperimentPlan


QUESTION = {
    "question": "Does margin slope add warning value beyond margin level?",
    "importance": "It tests whether trajectory adds information.",
    "why_now": "Trajectory is currently a candidate construct.",
    "theory_targets": ["margin->trajectory"],
    "prior_evidence": ["synthetic margin evidence is bounded"],
    "unknowns": ["incremental warning value"],
}

HYPOTHESES = {
    "hypotheses": [
        {
            "id": f"H{i}",
            "statement": f"statement {i}",
            "mechanism": f"mechanism {i}",
            "prediction": f"prediction {i}",
            "falsification_condition": f"falsifier {i}",
            "novelty_rationale": f"novelty {i}",
            "theory_targets": ["margin->trajectory"],
            "prior_failures_considered": [],
        }
        for i in range(1, 5)
    ]
}

CRITIQUES = {
    "critiques": [
        {
            "hypothesis_id": f"H{i}",
            "recommendation": "advance_exploratory" if i == 1 else "revise",
            "fatal_flaws": [],
            "confounds": ["possible lag"],
            "leakage_risks": [],
            "alternative_explanations": ["measurement noise"],
            "required_revisions": [],
        }
        for i in range(1, 5)
    ]
}

SELECTION = {
    "hypothesis_id": "H1",
    "rationale": "Most discriminating.",
    "revisions_applied": [],
    "residual_uncertainties": ["noise sensitivity"],
}

EXPERIMENT = {
    "title": "Exploratory margin-slope comparison",
    "hypothesis_id": "H1",
    "purpose": "Test incremental warning value.",
    "environment": "bounded synthetic environment",
    "independent_variables": ["disturbance profile"],
    "dependent_variables": ["warning lead time"],
    "controls": ["fixed margin observer"],
    "baselines": ["margin level only"],
    "procedure": ["generate bounded trajectories", "compare observers"],
    "analysis_plan": ["match false-alarm budgets"],
    "failure_criteria": ["no incremental lead time"],
    "stopping_conditions": ["planned sweep complete"],
    "provenance_requirements": ["record code and config hashes"],
    "evidence_class": "exploratory",
    "requires_holdout": False,
    "authority_effect": "none",
}

REVIEW = {
    "disposition": "acceptable_exploratory",
    "unsupported_claims": [],
    "evidence_boundary_issues": [],
    "unresolved_concerns": ["synthetic scope"],
    "required_changes": [],
}


class JsonTests(unittest.TestCase):
    def test_parse_fenced_object(self):
        parsed = parse_json_object("```json\n{\"x\": 1}\n```")
        self.assertEqual(parsed["x"], 1)


class MemoryTests(unittest.TestCase):
    def test_retrieves_relevant_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "state").mkdir()
            (root / "state" / "failures.jsonl").write_text(
                json.dumps({
                    "id": "fail-1",
                    "hypothesis": "margin slope predicts failure",
                    "lesson": "slope alone was noisy",
                }) + "\n",
                encoding="utf-8",
            )
            (root / "state" / "anomalies.jsonl").write_text("", encoding="utf-8")
            memory = ScientificMemory(root)
            rows = memory.relevant("margin slope trajectory")
            self.assertEqual(rows[0]["id"], "fail-1")


class SchemaGuardTests(unittest.TestCase):
    def test_rejects_confirmatory_plan(self):
        bad = dict(EXPERIMENT)
        bad["evidence_class"] = "confirmatory"
        with self.assertRaises(ValueError):
            ExperimentPlan.from_dict(bad)


class ReasonerTests(unittest.TestCase):
    def _repo(self, tmp: str):
        repo = Path(tmp)
        scientist = repo / "scientist"
        (scientist / "config").mkdir(parents=True)
        (scientist / "state").mkdir(parents=True)
        (repo / "README.md").write_text("Cohervia test context", encoding="utf-8")
        (scientist / "SCIENTIFIC_CONSTITUTION.md").write_text(
            "constitution", encoding="utf-8"
        )
        (scientist / "config" / "reasoning.json").write_text(
            json.dumps({
                "approved_context_paths": [
                    "README.md",
                    "scientist/SCIENTIFIC_CONSTITUTION.md"
                ],
                "max_context_characters": 10000,
                "max_characters_per_document": 5000,
            }),
            encoding="utf-8",
        )
        (scientist / "state" / "failures.jsonl").write_text("", encoding="utf-8")
        (scientist / "state" / "anomalies.jsonl").write_text("", encoding="utf-8")
        return repo, scientist

    def test_full_reasoning_pipeline(self):
        responses = [
            json.dumps(QUESTION),
            json.dumps(HYPOTHESES),
            json.dumps(CRITIQUES),
            json.dumps(SELECTION),
            json.dumps(EXPERIMENT),
            json.dumps(REVIEW),
        ]
        provider = ScriptedProvider(responses)

        with tempfile.TemporaryDirectory() as tmp:
            repo, scientist = self._repo(tmp)
            reasoner = ScientificReasoner(
                provider=provider,
                repo_root=repo,
                scientist_root=scientist,
                hypothesis_count=4,
            )
            packet = reasoner.run()
            self.assertEqual(packet.status, "candidate_reasoning")
            self.assertEqual(packet.selection.hypothesis_id, "H1")
            self.assertEqual(
                packet.experiment.evidence_class,
                "exploratory",
            )
            self.assertEqual(len(provider.calls), 6)
            self.assertEqual(
                packet.integrity_review.disposition,
                "acceptable_exploratory",
            )


if __name__ == "__main__":
    unittest.main()
