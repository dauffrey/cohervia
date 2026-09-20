import copy
import unittest
from pathlib import Path

from cohervia_harness.schema_validation import validate_instance


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "capability-emergence-observation.schema.json"


def base_record():
    return {
        "record_type": "trial_evidence",
        "observation_id": "obs-1",
        "experiment_id": "COH-EXP-0001",
        "trial_id": "trial-1",
        "evaluation_partition": "development",
        "timestamp": "2026-09-20T22:00:00+00:00",
        "system_configuration_hash": "cfg",
        "model_identity": "scripted-agent",
        "task_family_id": "algorithmic_verifiable",
        "capability_endpoint_id": "exact-match",
        "task_score": 1.0,
        "first_divergence_event_id": None,
        "tools_involved": [],
        "memory_involved": False,
        "agents_involved": ["scripted-agent"],
        "environmental_affordance": None,
        "constraint_status": "satisfied",
        "verifier_result": "pass",
        "applicability": "observed",
        "evidence_quality": "exploratory",
        "provenance_hash": "prov",
    }


class SchemaValidationTests(unittest.TestCase):
    def test_valid_development_record(self):
        validate_instance(base_record(), SCHEMA)

    def test_development_cannot_be_confirmatory(self):
        record = copy.deepcopy(base_record())
        record["evidence_quality"] = "confirmatory"
        with self.assertRaises(ValueError):
            validate_instance(record, SCHEMA)

    def test_score_above_one_is_rejected(self):
        record = copy.deepcopy(base_record())
        record["task_score"] = 1.01
        with self.assertRaises(ValueError):
            validate_instance(record, SCHEMA)

    def test_holdout_record_must_be_confirmatory(self):
        record = copy.deepcopy(base_record())
        record["evaluation_partition"] = "capability_holdout_a"
        record["evidence_quality"] = "exploratory"
        with self.assertRaises(ValueError):
            validate_instance(record, SCHEMA)


if __name__ == "__main__":
    unittest.main()
