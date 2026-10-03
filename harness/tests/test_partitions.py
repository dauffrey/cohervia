import unittest

from cohervia_harness.models import Partition, TrialConfig


class PartitionTests(unittest.TestCase):
    def _config(self, partition):
        return TrialConfig(
            experiment_id="COH-EXP-0001",
            trial_id="T1",
            task_family_id="algorithmic_verifiable",
            partition=partition,
            system_configuration_hash="abc",
            model_identity="test-agent",
        )

    def test_development_partitions_are_allowed(self):
        self._config(Partition.INSTRUMENTATION).validate_for_harness()
        self._config(Partition.DEVELOPMENT).validate_for_harness()

    def test_confirmatory_partitions_are_disabled(self):
        for partition in (
            Partition.CAPABILITY_HOLDOUT_A,
            Partition.TRANSFER_HOLDOUT_B,
            Partition.GOVERNANCE_HOLDOUT_C,
        ):
            with self.assertRaises(PermissionError):
                self._config(partition).validate_for_harness()


if __name__ == "__main__":
    unittest.main()
