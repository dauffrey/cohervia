"""Offline persistent custody adversarial and restart tests."""
import copy
import os
import sqlite3
import tempfile
import unittest
from persistent_custody import PersistentCustody

SECRET = b"local-test-only-not-for-real-experiments!" * 2
def prediction(trial="t", probability=0.7):
    return {"trial_id": trial, "task_hash": "a" * 64, "model": "fixture", "probability": probability}

class PersistentCustodyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "custody.sqlite")

    def tearDown(self):
        self.tmp.cleanup()

    def test_restart_and_single_use(self):
        p = prediction()
        with PersistentCustody(self.path, SECRET) as ledger:
            receipt = ledger.commit(p)
        with PersistentCustody(self.path, SECRET) as ledger:
            self.assertTrue(ledger.authorize(p, receipt))
        with PersistentCustody(self.path, SECRET) as ledger:
            with self.assertRaises(ValueError):
                ledger.authorize(p, receipt)

    def test_missing_or_forged_receipt(self):
        p = prediction()
        with PersistentCustody(self.path, SECRET) as ledger:
            receipt = ledger.commit(p)
            for forged in (None, dict(receipt, receipt="f" * 64), dict(receipt, sequence=2)):
                with self.subTest(forged=forged), self.assertRaises(ValueError):
                    ledger.authorize(p, forged)

    def test_changed_prediction(self):
        p = prediction()
        with PersistentCustody(self.path, SECRET) as ledger:
            receipt = ledger.commit(p)
            with self.assertRaises(ValueError):
                ledger.authorize(prediction(probability=0.8), receipt)

    def test_duplicate_commit(self):
        p = prediction()
        with PersistentCustody(self.path, SECRET) as ledger:
            ledger.commit(p)
            with self.assertRaises(sqlite3.IntegrityError):
                ledger.commit(p)

    def test_database_rewrite_detected(self):
        with PersistentCustody(self.path, SECRET) as ledger:
            ledger.commit(prediction())
            ledger.db.execute("UPDATE commitments SET prediction=? WHERE trial='t'", ("f" * 64,))
            with self.assertRaises(ValueError):
                ledger.audit()

    def test_wrong_secret_detected(self):
        with PersistentCustody(self.path, SECRET) as ledger:
            ledger.commit(prediction())
        with PersistentCustody(self.path, b"x" * 32) as ledger:
            with self.assertRaises(ValueError):
                ledger.audit()

    def test_consumption_state_cannot_be_reset(self):
        p = prediction()
        with PersistentCustody(self.path, SECRET) as ledger:
            receipt = ledger.commit(p)
            ledger.authorize(p, receipt)
            ledger.db.execute("UPDATE commitments SET attempted=0 WHERE trial='t'")
            with self.assertRaises(ValueError):
                ledger.audit()
            with self.assertRaises(ValueError):
                ledger.authorize(p, receipt)

    def test_consumption_cannot_be_fabricated(self):
        with PersistentCustody(self.path, SECRET) as ledger:
            ledger.commit(prediction())
            ledger.db.execute("UPDATE commitments SET attempted=1 WHERE trial='t'")
            with self.assertRaises(ValueError):
                ledger.audit()

    def test_unicode_identity_round_trip(self):
        p = prediction("run-é:task")
        with PersistentCustody(self.path, SECRET) as ledger:
            receipt = ledger.commit(p)
            self.assertTrue(ledger.authorize(p, receipt))

    def test_no_secret_rejected(self):
        with self.assertRaises(ValueError):
            PersistentCustody(self.path, b"short")

if __name__ == "__main__":
    unittest.main()
