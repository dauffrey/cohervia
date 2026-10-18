import json
import tempfile
import unittest
from pathlib import Path

from cohervia_scientist.ledger import AppendOnlyLedger
from cohervia_scientist.models import Prediction, ResearchPhase
from cohervia_scientist.research_cycle import ResearchCycle, ResearchGateError
from cohervia_scientist.theory import TheoryGraph


class LedgerTests(unittest.TestCase):
    def test_append_only_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "predictions.jsonl"
            ledger = AppendOnlyLedger(path)
            prediction = Prediction(
                claim="margin slope predicts boundary approach",
                theory_version="test",
                confidence=0.6,
            )
            ledger.append(prediction.to_dict())
            rows = ledger.read_all()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["claim"], prediction.claim)

    def test_prediction_rejects_invalid_confidence(self):
        prediction = Prediction(
            claim="x",
            theory_version="test",
            confidence=1.1,
        )
        with self.assertRaises(ValueError):
            prediction.to_dict()


class ResearchGateTests(unittest.TestCase):
    def test_cannot_skip_to_confirmation(self):
        cycle = ResearchCycle()
        with self.assertRaises(ResearchGateError):
            cycle.transition(ResearchPhase.CONFIRMATORY_PENDING)

    def test_freeze_requires_preregistration(self):
        cycle = ResearchCycle(phase=ResearchPhase.PREREGISTRATION)
        with self.assertRaises(ResearchGateError):
            cycle.transition(ResearchPhase.FROZEN)

    def test_confirmation_requires_manifest_and_evaluator(self):
        cycle = ResearchCycle(
            phase=ResearchPhase.PREREGISTRATION,
            preregistration_hash="abc",
        )
        cycle.transition(ResearchPhase.FROZEN)
        with self.assertRaises(ResearchGateError):
            cycle.transition(ResearchPhase.CONFIRMATORY_PENDING)
        cycle.register_freeze("manifest", "independent-evaluator")
        cycle.transition(ResearchPhase.CONFIRMATORY_PENDING)
        self.assertEqual(cycle.phase, ResearchPhase.CONFIRMATORY_PENDING)


class TheoryTests(unittest.TestCase):
    def test_theory_summary_and_weak_edges(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "theory.json"
            path.write_text(
                json.dumps({
                    "schema_version": 1,
                    "theory_version": "x",
                    "nodes": [{"id": "a"}, {"id": "b"}],
                    "edges": [{"from": "a", "to": "b", "status": "unknown"}],
                }),
                encoding="utf-8",
            )
            graph = TheoryGraph.load(path)
            self.assertEqual(graph.summary()["weak_edges"], 1)


if __name__ == "__main__":
    unittest.main()
