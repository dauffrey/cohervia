"""Offline coordinator preflight tests: never call an API."""
import os
import tempfile
import unittest
from unittest.mock import Mock, patch
from cohervia_pilot.protocol import catalog
from custodied_pilot import run_custodied_pilot
from persistent_custody import PersistentCustody

SECRET = b"offline-test-secret-for-coordinator-123456789"

class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.temp.name, "custody.sqlite")
        self.provider = Mock()
        self.provider.model = "fixture"
        self.provider.kind = "scripted_instrumentation"
        self.probabilities = {task["id"]: 0.5 for task in catalog()}

    def tearDown(self):
        self.temp.cleanup()

    def test_predictions_committed_before_runner(self):
        def verify(gated, output_dir, run_id):
            with PersistentCustody(self.db, SECRET) as ledger:
                self.assertEqual(ledger.db.execute("SELECT COUNT(*) FROM commitments").fetchone()[0], len(catalog()))
            self.assertEqual(gated.index, 0)
            return {"fixture": True}, "offline"
        with patch("custodied_pilot.run", side_effect=verify) as runner:
            result = run_custodied_pilot(self.provider, "unused", "run", self.probabilities, self.db, SECRET)
            self.assertEqual(result[0], {"fixture": True})
            runner.assert_called_once()
        self.provider.complete.assert_not_called()

    def test_missing_prediction_blocks_runner(self):
        incomplete = dict(self.probabilities)
        incomplete.pop(next(iter(incomplete)))
        with patch("custodied_pilot.run") as runner:
            with self.assertRaises(ValueError):
                run_custodied_pilot(self.provider, "unused", "run", incomplete, self.db, SECRET)
            runner.assert_not_called()
        self.provider.complete.assert_not_called()

if __name__ == "__main__":
    unittest.main()
