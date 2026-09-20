import copy
import unittest
from pathlib import Path

from cohervia_harness.schema_validation import validate_instance


ROOT = Path(__file__).resolve().parents[1]
EMERGENCE_SCHEMA = ROOT / "schemas" / "capability-emergence-assessment.schema.json"
TRANSFER_SCHEMA = ROOT / "schemas" / "capability-transfer-assessment.schema.json"


def emergence_record():
    return {
        "record_type": "configuration_emergence_assessment",
        "assessment_id": "ea-1",
        "experiment_id": "COH-EXP-0001",
        "configuration_id": "cfg-1",
        "timestamp": "2026-09-20T22:00:00+00:00",
        "system_configuration_hash": "cfg-hash",
        "capability_holdout_manifest_hash": "a-manifest",
        "capability_evaluator_hash": "eval",
        "baseline_estimator_hash": "baseline",
        "comparator_definition_hash": "comparator",
        "task_family_id": "algorithmic_verifiable",
        "capability_endpoint_id": "score",
        "n_target_trials": 10,
        "n_comparator_trials": 10,
        "baseline_prediction": 0.4,
        "mean_observed_value": 0.7,
        "delta_emergent": 0.3,
        "delta_min": 0.1,
        "lower_confidence_bound": 0.2,
        "uncertainty_procedure_hash": "uncertainty",
        "multiplicity_rule_hash": "multiplicity",
        "multiplicity_result": "pass",
        "verifier_result": "pass",
        "protocol_valid": True,
        "emergence_classification": "positive",
        "supporting_trial_observation_ids": ["t1"],
        "supporting_comparator_observation_ids": ["c1"],
        "provenance_hash": "prov",
    }


def transfer_record():
    return {
        "record_type": "configuration_transfer_assessment",
        "assessment_id": "ta-1",
        "experiment_id": "COH-EXP-0001",
        "configuration_id": "cfg-1",
        "timestamp": "2026-09-20T22:00:00+00:00",
        "system_configuration_hash": "cfg-hash",
        "transfer_holdout_manifest_hash": "b-manifest",
        "transfer_evaluator_hash": "eval",
        "transfer_estimator_hash": "transfer-estimator",
        "comparator_definition_hash": "comparator",
        "task_family_id": "algorithmic_verifiable",
        "capability_endpoint_id": "score",
        "n_target_trials": 10,
        "n_comparator_trials": 10,
        "baseline_prediction": 0.4,
        "mean_observed_value": 0.7,
        "delta_transfer": 0.3,
        "transfer_delta_min": 0.1,
        "lower_confidence_bound": 0.2,
        "uncertainty_procedure_hash": "uncertainty",
        "multiplicity_rule_hash": "multiplicity",
        "multiplicity_result": "pass",
        "verifier_result": "pass",
        "protocol_valid": True,
        "transfer_classification": "confirmed",
        "supporting_trial_observation_ids": ["t1"],
        "supporting_comparator_observation_ids": ["c1"],
        "provenance_hash": "prov",
    }


class ClassificationGateSchemaTests(unittest.TestCase):
    def test_valid_positive_emergence_record(self):
        validate_instance(emergence_record(), EMERGENCE_SCHEMA)

    def test_positive_emergence_rejects_invalid_protocol(self):
        record = copy.deepcopy(emergence_record())
        record["protocol_valid"] = False
        with self.assertRaises(ValueError):
            validate_instance(record, EMERGENCE_SCHEMA)

    def test_positive_emergence_rejects_failed_verifier(self):
        record = copy.deepcopy(emergence_record())
        record["verifier_result"] = "fail"
        with self.assertRaises(ValueError):
            validate_instance(record, EMERGENCE_SCHEMA)

    def test_invalid_emergence_requires_invalid_protocol(self):
        record = copy.deepcopy(emergence_record())
        record["emergence_classification"] = "invalid"
        with self.assertRaises(ValueError):
            validate_instance(record, EMERGENCE_SCHEMA)

    def test_valid_confirmed_transfer_record(self):
        validate_instance(transfer_record(), TRANSFER_SCHEMA)

    def test_confirmed_transfer_rejects_failed_multiplicity(self):
        record = copy.deepcopy(transfer_record())
        record["multiplicity_result"] = "fail"
        with self.assertRaises(ValueError):
            validate_instance(record, TRANSFER_SCHEMA)

    def test_confirmed_transfer_rejects_invalid_protocol(self):
        record = copy.deepcopy(transfer_record())
        record["protocol_valid"] = False
        with self.assertRaises(ValueError):
            validate_instance(record, TRANSFER_SCHEMA)


if __name__ == "__main__":
    unittest.main()
