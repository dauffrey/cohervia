import unittest

from cohervia_experiment_harness.audit import AppendOnlyAuditLog
from cohervia_experiment_harness.events import Event


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

    def test_payload_cannot_be_mutated_through_caller_or_record_view(self):
        audit = AppendOnlyAuditLog()
        input_payload = {"nested": {"value": 1}}
        event = Event.create(
            trial_id="T1", actor="agent", kind="trial_started",
            payload=input_payload, sequence=0,
        )
        audit.append(event)
        root = audit.root_hash
        input_payload["nested"]["value"] = 2
        event.payload["nested"]["value"] = 3
        visible = audit.records
        visible[0].event.payload["nested"]["value"] = 4
        self.assertEqual(audit.records[0].event.payload["nested"]["value"], 1)
        self.assertEqual(audit.root_hash, root)
        self.assertTrue(audit.verify())

    def test_records_are_exposed_as_immutable_tuple(self):
        audit = AppendOnlyAuditLog()
        self.assertIsInstance(audit.records, tuple)


if __name__ == "__main__":
    unittest.main()
