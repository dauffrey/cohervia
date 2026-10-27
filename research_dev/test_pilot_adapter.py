"""Offline adapter contract tests; fabricated pilot records, no scientific evidence."""
import unittest
from unittest.mock import patch
from capability_assessment import digest
from pilot_adapter import assess_pilot_bundle

TASK = {"id": "DEV-MATH-001", "family": "math", "prompt": "7*8", "expected": 56}
RECEIPT = '{"provider_result":{"status":"completed","text":"{\\"answer\\":56}"}}'
BUNDLE = {"sha256": "synthetic", "run_id": "dev", "inputs": {"configuration": {
    "mode": "scripted_instrumentation", "requested_model": "scripted"}},
    "artifacts": {"receipt:DEV-MATH-001": RECEIPT}}

class AdapterTests(unittest.TestCase):
    @patch("pilot_adapter.replay_bundle", return_value="verified")
    @patch("pilot_adapter.catalog", return_value=[TASK])
    def test_scored_scripted_record(self, _catalog, _replay):
        report = assess_pilot_bundle(BUNDLE, {"DEV-MATH-001": {"probability": 0.75, "checkpoint": "external:demo"}})
        self.assertAlmostEqual(report["mean_brier_observed"], 0.0625)
        self.assertFalse(report["scientific_evidence"])
        self.assertFalse(report["execution_authorized"])

    @patch("pilot_adapter.replay_bundle", return_value="verified")
    @patch("pilot_adapter.catalog", return_value=[TASK])
    def test_missing_prediction_rejected(self, _catalog, _replay):
        with self.assertRaises(ValueError):
            assess_pilot_bundle(BUNDLE, {})

    @patch("pilot_adapter.replay_bundle", side_effect=ValueError("invalid bundle"))
    def test_replay_failure_rejected(self, _replay):
        with self.assertRaises(ValueError):
            assess_pilot_bundle(BUNDLE, {})

    @patch("pilot_adapter.replay_bundle", return_value="verified")
    @patch("pilot_adapter.catalog", return_value=[TASK])
    def test_missing_checkpoint_rejected(self, _catalog, _replay):
        with self.assertRaises(ValueError):
            assess_pilot_bundle(BUNDLE, {"DEV-MATH-001": {"probability": 0.5, "checkpoint": ""}})

if __name__ == "__main__":
    unittest.main()
