"""Offline custody-gate tests. No provider calls or independent time claims."""
import unittest
from dataclasses import replace
from evidence_custody import CustodyLedger

def prediction(trial="t", probability=0.7):
    return {"trial_id": trial, "task_hash": "a" * 64, "model": "test", "probability": probability}

class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.ledger = CustodyLedger()
        self.prediction = prediction()
        self.receipt = self.ledger.commit(**self.prediction)

    def test_commit_before_attempt(self):
        self.assertTrue(self.ledger.authorize_attempt(self.prediction, self.receipt))
        self.assertEqual(self.ledger.audit(), 1)

    def test_no_receipt(self):
        with self.assertRaises(ValueError):
            self.ledger.authorize_attempt(self.prediction, None)

    def test_tampered_prediction(self):
        with self.assertRaises(ValueError):
            self.ledger.authorize_attempt(prediction(probability=0.8), self.receipt)

    def test_reused_receipt(self):
        self.ledger.authorize_attempt(self.prediction, self.receipt)
        with self.assertRaises(ValueError):
            self.ledger.authorize_attempt(self.prediction, self.receipt)

    def test_duplicate_commit(self):
        with self.assertRaises(ValueError):
            self.ledger.commit(**self.prediction)

    def test_forged_receipt(self):
        with self.assertRaises(ValueError):
            self.ledger.authorize_attempt(self.prediction, replace(self.receipt, digest="f" * 64))

    def test_reordered_receipts_detected(self):
        self.ledger.commit(**prediction("other"))
        self.ledger._receipts.reverse()
        with self.assertRaises(ValueError):
            self.ledger.audit()

    def test_invalid_probabilities(self):
        for value in (True, -0.1, 1.1, float("nan")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                CustodyLedger().commit(**prediction(probability=value))

if __name__ == "__main__":
    unittest.main()
