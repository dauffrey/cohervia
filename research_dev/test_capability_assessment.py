"""Offline contract regressions: fabricated fixtures, never scientific evidence."""
import copy
import unittest
from capability_assessment import digest, make_record, validate

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.record = make_record("dev-001", {"prompt": "7*8", "expected": 56}, "scripted-fixture", 0.75, '{"answer":56}', True)

    def test_brier_and_non_evidence(self):
        result = validate(self.record)
        self.assertAlmostEqual(result["brier"], 0.0625)
        self.assertFalse(result["scientific_evidence"])
        self.assertFalse(result["execution_authorized"])

    def test_unknown_is_not_failure(self):
        record = make_record("dev-002", "public-task", "scripted-fixture", 0.2, None, None)
        self.assertIsNone(validate(record)["brier"])

    def test_tampered_prediction(self):
        record = copy.deepcopy(self.record)
        record["prediction"]["probability"] = 0.1
        with self.assertRaises(ValueError):
            validate(record)

    def test_tampered_attempt(self):
        record = copy.deepcopy(self.record)
        record["attempt"]["response"] = "changed"
        with self.assertRaises(ValueError):
            validate(record)

    def test_trial_mismatch(self):
        record = copy.deepcopy(self.record)
        record["verdict"]["trial_id"] = "other"
        with self.assertRaises(ValueError):
            validate(record)

    def test_invalid_probability(self):
        for value in (float("nan"), float("inf"), -0.1, 1.1, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                make_record("x", "task", "model", value, "response", True)

    def test_incomplete_cannot_be_scored(self):
        with self.assertRaises(ValueError):
            make_record("x", "task", "model", 0.5, None, False)

    def test_completed_without_response_rejected_even_with_valid_hashes(self):
        record = copy.deepcopy(self.record)
        record["attempt"]["response"] = None
        record["verdict"]["attempt_hash"] = digest(record["attempt"])
        with self.assertRaises(ValueError):
            validate(record)

    def test_numeric_verdict_lookalikes_rejected(self):
        for value in (0, 1, 0.0, 1.0):
            with self.subTest(value=value):
                record = copy.deepcopy(self.record)
                record["verdict"]["outcome"] = value
                with self.assertRaises(ValueError):
                    validate(record)
                with self.assertRaises(ValueError):
                    make_record("x", "task", "model", 0.5, "response", value)

    def test_unexpected_fields(self):
        record = copy.deepcopy(self.record)
        record["prediction"]["answer_key"] = "leak"
        with self.assertRaises(ValueError):
            validate(record)

if __name__ == "__main__":
    unittest.main()
