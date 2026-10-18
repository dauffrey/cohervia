import copy
import math
import unittest

from cohervia_experiment_harness.selectors import (
    cross_family_eligible_configurations,
    recompute_emergence_gate,
    recompute_transfer_gate,
)


def emergence_record(family="algorithmic_verifiable"):
    return {
        "configuration_id": "cfg-1",
        "system_configuration_hash": "sha-frozen-cfg-1",
        "task_family_id": family,
        "delta_emergent": 0.3,
        "baseline_prediction": 0.2,
        "mean_observed_value": 0.5,
        "delta_min": 0.1,
        "lower_confidence_bound": 0.2,
        "multiplicity_result": "pass",
        "verifier_result": "pass",
        "protocol_valid": True,
        "emergence_classification": "positive",
    }


def transfer_record(family="algorithmic_verifiable"):
    return {
        "configuration_id": "cfg-1",
        "system_configuration_hash": "sha-frozen-cfg-1",
        "task_family_id": family,
        "delta_transfer": 0.3,
        "baseline_prediction": 0.2,
        "mean_observed_value": 0.5,
        "transfer_delta_min": 0.1,
        "lower_confidence_bound": 0.2,
        "multiplicity_result": "pass",
        "verifier_result": "pass",
        "protocol_valid": True,
        "transfer_classification": "confirmed",
    }


class SelectorTests(unittest.TestCase):
    def test_emergence_gate_recomputes_numeric_thresholds(self):
        self.assertTrue(recompute_emergence_gate(emergence_record()).passed)
        record = copy.deepcopy(emergence_record())
        record["lower_confidence_bound"] = 0.05
        result = recompute_emergence_gate(record)
        self.assertFalse(result.passed)
        self.assertIn("lower_bound_below_minimum", result.reasons)

    def test_transfer_gate_recomputes_numeric_thresholds(self):
        self.assertTrue(recompute_transfer_gate(transfer_record()).passed)
        record = copy.deepcopy(transfer_record())
        record["delta_transfer"] = 0.05
        result = recompute_transfer_gate(record)
        self.assertFalse(result.passed)
        self.assertIn("delta_below_minimum", result.reasons)

    def test_cross_family_gate_requires_same_config_pass_a_and_b_in_two_families(self):
        emergence = [
            emergence_record("algorithmic_verifiable"),
            emergence_record("mathematical_verifiable"),
        ]
        transfer = [
            transfer_record("algorithmic_verifiable"),
            transfer_record("mathematical_verifiable"),
        ]
        self.assertEqual(
            cross_family_eligible_configurations(emergence, transfer),
            frozenset({"cfg-1"}),
        )

    def test_transfer_without_matching_emergence_does_not_count(self):
        emergence = [emergence_record("algorithmic_verifiable")]
        transfer = [
            transfer_record("algorithmic_verifiable"),
            transfer_record("mathematical_verifiable"),
        ]
        self.assertEqual(
            cross_family_eligible_configurations(emergence, transfer),
            frozenset(),
        )

    def test_single_family_candidate_is_not_system_level_eligible(self):
        self.assertEqual(
            cross_family_eligible_configurations(
                [emergence_record("algorithmic_verifiable")],
                [transfer_record("algorithmic_verifiable")],
            ),
            frozenset(),
        )

    def test_nonfinite_or_boolean_numeric_fields_fail_closed(self):
        for factory, gate, delta_field, minimum_field in (
            (emergence_record, recompute_emergence_gate, "delta_emergent", "delta_min"),
            (transfer_record, recompute_transfer_gate, "delta_transfer", "transfer_delta_min"),
        ):
            for field in (delta_field, minimum_field, "lower_confidence_bound"):
                for bad in (math.nan, math.inf, -math.inf, True, False):
                    with self.subTest(field=field, bad=repr(bad)):
                        record = factory()
                        record[field] = bad
                        self.assertFalse(gate(record).passed)

    def test_residual_is_recomputed_not_trusted(self):
        for factory, gate in ((emergence_record, recompute_emergence_gate),
                              (transfer_record, recompute_transfer_gate)):
            example = factory()
            example["mean_observed_value"] = 0.1
            example["baseline_prediction"] = 0.8
            self.assertIn("residual_components_disagree", gate(example).reasons)
            example["mean_observed_value"] = None
            self.assertIn("missing_or_invalid_residual_components", gate(example).reasons)

    def test_cross_family_hash_mismatch_never_conflates_systems(self):
        families = ("algorithmic_verifiable", "mathematical_verifiable")
        emergence = [emergence_record(f) for f in families]
        transfer = [transfer_record(f) for f in families]
        transfer[1]["system_configuration_hash"] = "other-frozen-system"
        self.assertEqual(cross_family_eligible_configurations(emergence, transfer), frozenset())

    def test_duplicate_family_does_not_count_twice(self):
        emergence = [
            emergence_record("algorithmic_verifiable"),
            emergence_record("algorithmic_verifiable"),
        ]
        transfer = [
            transfer_record("algorithmic_verifiable"),
            transfer_record("algorithmic_verifiable"),
        ]
        self.assertEqual(
            cross_family_eligible_configurations(emergence, transfer),
            frozenset(),
        )

    def test_failed_transfer_does_not_count_toward_cross_family_gate(self):
        failed = transfer_record("mathematical_verifiable")
        failed["lower_confidence_bound"] = 0.01
        emergence = [
            emergence_record("algorithmic_verifiable"),
            emergence_record("mathematical_verifiable"),
        ]
        transfer = [transfer_record("algorithmic_verifiable"), failed]
        self.assertEqual(
            cross_family_eligible_configurations(emergence, transfer),
            frozenset(),
        )


if __name__ == "__main__":
    unittest.main()
