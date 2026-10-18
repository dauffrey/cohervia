import unittest

from cohervia_harness.audit import AppendOnlyAuditLog
from cohervia_harness.memory import GovernedMemory


class MemoryTests(unittest.TestCase):
    def test_write_changes_hash_and_is_audited(self):
        audit = AppendOnlyAuditLog()
        memory = GovernedMemory(audit=audit)
        memory.begin_trial("T1")
        before = memory.state_hash
        write = memory.write(
            actor="agent",
            trial_id="T1",
            key="plan",
            value={"step": 1},
            source_event_ids=("source-1",),
        )
        self.assertNotEqual(before, memory.state_hash)
        self.assertEqual(write.resulting_state_hash, memory.state_hash)
        self.assertEqual(audit.records[-1].event.kind, "memory_write")
        self.assertTrue(audit.verify())
        self.assertEqual(write.persistence_scope, "trial")
        self.assertEqual(audit.records[-1].event.payload["persistence_scope"], "trial")

    def test_caller_mutation_cannot_modify_stored_memory_without_audit(self):
        audit = AppendOnlyAuditLog()
        memory = GovernedMemory(audit=audit)
        memory.begin_trial("T1")
        original = {"nested": [1]}
        memory.write(actor="agent", trial_id="T1", key="plan", value=original)
        captured_hash = memory.state_hash
        root = audit.root_hash
        original["nested"].append(2)
        read = memory.read(trial_id="T1", key="plan")
        read["nested"].append(3)
        self.assertEqual(memory.read(trial_id="T1", key="plan"), {"nested": [1]})
        self.assertEqual(memory.state_hash, captured_hash)
        self.assertEqual(audit.root_hash, root)
        self.assertTrue(audit.verify())

    def test_cross_trial_state_is_rejected(self):
        memory = GovernedMemory(audit=AppendOnlyAuditLog())
        memory.begin_trial("T1")
        with self.assertRaises(PermissionError):
            memory.read(trial_id="T2", key="anything")


if __name__ == "__main__":
    unittest.main()
