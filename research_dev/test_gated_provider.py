"""Offline proof that the gate consumes custody before the underlying provider call."""
import os
import tempfile
import unittest
from unittest.mock import Mock
from cohervia_pilot.protocol import catalog
from gated_provider import CustodyGatedProvider
from persistent_custody import PersistentCustody, digest

SECRET = b"test-secret-for-coordinator-only-00000000"

class GatedProviderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "custody.db")
        self.provider = Mock()
        self.provider.model = "scripted-fixture"
        self.provider.kind = "scripted_instrumentation"
        self.tasks = catalog()
        self.probabilities = {t["id"]: 0.5 for t in self.tasks}
        with PersistentCustody(self.path, SECRET) as ledger:
            self.receipts = {t["id"]: ledger.commit({
                "trial_id": "run:" + t["id"], "task_hash": digest(t),
                "model": self.provider.model, "probability": 0.5}) for t in self.tasks}

    def tearDown(self):
        self.tmp.cleanup()

    def wrapper(self, receipts=None):
        return CustodyGatedProvider(self.provider, self.path, SECRET, "run",
                                    self.receipts if receipts is None else receipts, self.probabilities)

    def test_consumed_before_call(self):
        wrapper = self.wrapper()
        task = self.tasks[0]
        def check(**_):
            with PersistentCustody(self.path, SECRET) as ledger:
                row = ledger.db.execute("SELECT attempted FROM commitments WHERE trial=?", ("run:" + task["id"],)).fetchone()
                self.assertEqual(row, (1,))
        self.provider.complete.side_effect = check
        wrapper.complete(instructions="test", prompt=task["prompt"])
        self.provider.complete.assert_called_once()

    def test_missing_receipt_prevents_call(self):
        receipts = dict(self.receipts)
        receipts[self.tasks[0]["id"]] = None
        with self.assertRaises(ValueError):
            self.wrapper(receipts).complete(instructions="test", prompt=self.tasks[0]["prompt"])
        self.provider.complete.assert_not_called()

    def test_out_of_order_prevents_call(self):
        with self.assertRaises(ValueError):
            self.wrapper().complete(instructions="test", prompt=self.tasks[1]["prompt"])
        self.provider.complete.assert_not_called()

    def test_retry_prevented_after_failure(self):
        wrapper = self.wrapper()
        self.provider.complete.side_effect = RuntimeError("provider failed")
        with self.assertRaises(RuntimeError):
            wrapper.complete(instructions="test", prompt=self.tasks[0]["prompt"])
        with self.assertRaises(ValueError):
            self.wrapper().complete(instructions="test", prompt=self.tasks[0]["prompt"])
        self.assertEqual(self.provider.complete.call_count, 1)

if __name__ == "__main__":
    unittest.main()
