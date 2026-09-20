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

    def test_cross_trial_state_is_rejected(self):
        memory = GovernedMemory(audit=AppendOnlyAuditLog())
        memory.begin_trial("T1")
        with self.assertRaises(PermissionError):
            memory.read(trial_id="T2", key="anything")


if __name__ == "__main__":
    unittest.main()
