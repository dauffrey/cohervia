import unittest

from cohervia_harness.audit import AppendOnlyAuditLog
from cohervia_harness.events import Event


class AuditTests(unittest.TestCase):
    def test_hash_chain_verifies(self):
        audit = AppendOnlyAuditLog()
        first = Event.create(
            trial_id="T1", actor="agent", kind="trial_started", payload={}, sequence=0
        )
        second = Event.create(
            trial_id="T1", actor="agent", kind="agent_answer", payload={}, sequence=1
        )
        audit.append(first)
        audit.append(second)
        self.assertTrue(audit.verify())
        self.assertEqual(len(audit.records), 2)
        self.assertNotEqual(audit.root_hash, AppendOnlyAuditLog.GENESIS)

    def test_records_are_exposed_as_immutable_tuple(self):
        audit = AppendOnlyAuditLog()
        self.assertIsInstance(audit.records, tuple)


if __name__ == "__main__":
    unittest.main()
