"""Offline adversarial witness boundary tests. Mock attestations are NOT evidence."""
import os
import json
import tempfile
import unittest
from unittest.mock import Mock, patch
from cohervia_pilot.protocol import catalog
from custodied_pilot import run_witnessed_pilot
from external_witness import verify_witness
from persistent_custody import digest

class WitnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.provider = Mock()
        self.provider.model = "fixture"
        self.provider.kind = "scripted_instrumentation"
        self.predictions = {task["id"]: 0.5 for task in catalog()}
        self.path = os.path.join(self.tmp.name, "custody.sqlite")
        self.secret = b"witness-offline-test-secret-000000000000"
    def tearDown(self):
        self.tmp.cleanup()
    def receipt(self, commitment):
        return {"version": "witness/0.1", "witness_id": "independent-fixture",
                "commitment_sha256": digest(commitment), "observed_at": "2026-10-27T04:00:00Z",
                "signature": "offline-fixture-not-real-signature"}
    def invoke(self, submit, verify):
        return run_witnessed_pilot(self.provider, os.path.join(self.tmp.name, "pilot-run"), "run", self.predictions,
                                   self.path, self.secret, submit, verify, "independent-fixture")
    def test_valid_mock_witness_before_runner(self):
        with patch("custodied_pilot.run", return_value=({}, "offline")) as runner:
            self.invoke(self.receipt, lambda _: True)
            runner.assert_called_once()
            sidecar = os.path.join(self.tmp.name, "pilot-run.witness.json")
            with open(sidecar, encoding="utf-8") as stream:
                evidence = json.load(stream)
            self.assertEqual(set(evidence["attestations"]), set(self.predictions))
        self.provider.complete.assert_not_called()
    def test_missing_witness_blocks_execution(self):
        with patch("custodied_pilot.run") as runner:
            with self.assertRaises(ValueError):
                self.invoke(lambda _: None, lambda _: True)
            runner.assert_not_called()
        self.provider.complete.assert_not_called()
    def test_forged_binding_blocks_execution(self):
        def bad(commitment):
            value = self.receipt(commitment)
            value["commitment_sha256"] = "0" * 64
            return value
        with patch("custodied_pilot.run") as runner:
            with self.assertRaises(ValueError):
                self.invoke(bad, lambda _: True)
            runner.assert_not_called()
    def test_invalid_signature_blocks_execution(self):
        with patch("custodied_pilot.run") as runner:
            with self.assertRaises(ValueError):
                self.invoke(self.receipt, lambda _: False)
            runner.assert_not_called()
    def test_wrong_witness_identity(self):
        commitment = {"test": 1}
        receipt = self.receipt(commitment)
        receipt["witness_id"] = "other"
        with self.assertRaises(ValueError):
            verify_witness(receipt, commitment, lambda _: True, expected_witness_id="independent-fixture")
    def test_malformed_timestamp(self):
        commitment = {"test": 1}
        receipt = self.receipt(commitment)
        receipt["observed_at"] = "not-a-time"
        with self.assertRaises(ValueError):
            verify_witness(receipt, commitment, lambda _: True, expected_witness_id="independent-fixture")

if __name__ == "__main__":
    unittest.main()
