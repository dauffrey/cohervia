"""Offline adversarial tests for read-only replay; mocked TSA is not proof."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cohervia_pilot.protocol import catalog
from persistent_custody import digest
from witnessed_replay import verify_rfc3161_pilot_evidence

class ReplayAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "evidence.json"
        self.tasks = catalog()
        self.bundle = {"run_id": "trial-1", "sha256": "bundle-digest",
                       "inputs": {"configuration": {"requested_model": "fixture"}}}
        self.commitments = {}
        self.attestations = {}
        for index, task in enumerate(self.tasks, 1):
            key = task["id"]
            commitment = {"trial_id": "trial-1:" + key, "prediction_digest": digest({"id":key}),
                          "previous_digest": "0" * 64, "sequence": index, "receipt": digest({"receipt":key})}
            self.commitments[key] = commitment
            self.attestations[key] = {"commitment_sha256": digest(commitment), "signature": "fixture"}
        self.evidence = {"schema_version": "witness-evidence/0.1", "run_id": "trial-1",
                         "witness_id": "rfc3161-tsa", "commitments": self.commitments,
                         "attestations": self.attestations}

    def tearDown(self):
        self.temp.cleanup()

    def verify(self, evidence=None, *, witness_ok=True):
        self.path.write_text(json.dumps(self.evidence if evidence is None else evidence), encoding="utf-8")
        def fake_verify(_, commitment):
            if not witness_ok:
                raise ValueError("invalid signature")
            return True
        with patch("witnessed_replay.replay_bundle", return_value=True), \
             patch("witnessed_replay.RFC3161Witness") as witness:
            witness.return_value.witness_id = "rfc3161-tsa"
            witness.return_value.verify.side_effect = fake_verify
            return verify_rfc3161_pilot_evidence(self.bundle, self.path, "https://example.invalid/tsr", self.path)

    def test_valid_fixture_replays(self):
        result = self.verify()
        self.assertTrue(result["independent_timestamp_verified"])
        self.assertFalse(result["provider_execution_time_independently_proven"])
        self.assertEqual(result["task_count"], len(self.tasks))

    def test_missing_sidecar(self):
        with patch("witnessed_replay.replay_bundle", return_value=True):
            with self.assertRaises(FileNotFoundError):
                verify_rfc3161_pilot_evidence(self.bundle, self.path, "https://example.invalid/tsr", self.path)

    def test_wrong_run(self):
        changed = copy.deepcopy(self.evidence)
        changed["run_id"] = "other"
        with self.assertRaises(ValueError):
            self.verify(changed)

    def test_missing_attestation(self):
        changed = copy.deepcopy(self.evidence)
        changed["attestations"].pop(self.tasks[0]["id"])
        with self.assertRaises(ValueError):
            self.verify(changed)

    def test_extra_attestation(self):
        changed = copy.deepcopy(self.evidence)
        changed["attestations"]["unknown"] = {"signature":"fixture"}
        with self.assertRaises(ValueError):
            self.verify(changed)

    def test_swapped_task(self):
        changed = copy.deepcopy(self.evidence)
        a, b = self.tasks[0]["id"], self.tasks[1]["id"]
        changed["commitments"][a], changed["commitments"][b] = changed["commitments"][b], changed["commitments"][a]
        with self.assertRaises(ValueError):
            self.verify(changed)

    def test_duplicate_custody_sequence(self):
        changed = copy.deepcopy(self.evidence)
        a, b = self.tasks[0]["id"], self.tasks[1]["id"]
        changed["commitments"][b]["sequence"] = changed["commitments"][a]["sequence"]
        with self.assertRaises(ValueError):
            self.verify(changed)

    def test_altered_commitment_rejected_by_signature(self):
        changed = copy.deepcopy(self.evidence)
        changed["commitments"][self.tasks[0]["id"]]["sequence"] = 900
        with self.assertRaises(ValueError):
            self.verify(changed, witness_ok=False)

    def test_invalid_signature(self):
        with self.assertRaises(ValueError):
            self.verify(witness_ok=False)

    def test_wrong_witness_id(self):
        changed = copy.deepcopy(self.evidence)
        changed["witness_id"] = "untrusted"
        with self.assertRaises(ValueError):
            self.verify(changed)

    def test_malformed_sidecar(self):
        self.path.write_text("{", encoding="utf-8")
        with patch("witnessed_replay.replay_bundle", return_value=True):
            with self.assertRaises(json.JSONDecodeError):
                verify_rfc3161_pilot_evidence(self.bundle, self.path, "https://example.invalid/tsr", self.path)

    def test_extra_schema_field(self):
        changed = copy.deepcopy(self.evidence)
        changed["unexpected"] = True
        with self.assertRaises(ValueError):
            self.verify(changed)

if __name__ == "__main__":
    unittest.main()
