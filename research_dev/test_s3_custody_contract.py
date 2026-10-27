"""No-cloud-call contract tests for proposed independent S3 custody."""
import unittest
from datetime import datetime, timedelta, timezone
from s3_custody_contract import validate_s3_custody_plan, validate_s3_retention_evidence

class S3CustodyContractTests(unittest.TestCase):
    def setUp(self):
        self.plan = {"bucket": "independent-evidence", "region": "ca-central-1",
                     "custodian_id": "fixture-custodian", "retention_days": 365,
                     "object_lock_mode": "COMPLIANCE", "independent_account": True,
                     "expected_monthly_cost_usd": 0.0}

    def test_valid_plan(self):
        self.assertEqual(validate_s3_custody_plan(self.plan), self.plan)

    def test_reject_governance_mode(self):
        self.plan["object_lock_mode"] = "GOVERNANCE"
        with self.assertRaises(ValueError):
            validate_s3_custody_plan(self.plan)

    def test_reject_same_account(self):
        self.plan["independent_account"] = False
        with self.assertRaises(ValueError):
            validate_s3_custody_plan(self.plan)

    def test_reject_nonfinite_cost(self):
        self.plan["expected_monthly_cost_usd"] = float("nan")
        with self.assertRaises(ValueError):
            validate_s3_custody_plan(self.plan)

    def test_valid_retention_metadata(self):
        evidence = {"bucket": self.plan["bucket"], "version_id": "v1",
                    "mode": "COMPLIANCE",
                    "retain_until": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()}
        self.assertTrue(validate_s3_retention_evidence(evidence, self.plan))

    def test_reject_unlocked_object(self):
        evidence = {"bucket": self.plan["bucket"], "version_id": "v1",
                    "mode": "GOVERNANCE", "retain_until": "2030-01-01T00:00:00Z"}
        with self.assertRaises(ValueError):
            validate_s3_retention_evidence(evidence, self.plan)

if __name__ == "__main__":
    unittest.main()
