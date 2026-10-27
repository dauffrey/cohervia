"""Offline checks for custodian acceptance binding; signature test uses a mock."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from evidence_archive import export_evidence
from custodian_receipt import verify_custodian_receipt

class CustodianReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bundle = self.root / "bundle-source.json"
        self.witness = self.root / "witness-source.json"
        self.bundle.write_text('{"run_id":"synthetic"}')
        self.witness.write_text('{"schema_version":"witness-evidence/0.2"}')
        self.archive = self.root / "archive"
        export_evidence(self.bundle, self.witness, self.archive)
        self.receipt = self.root / "receipt.json"
        self.signature = self.root / "receipt.sig"
        self.key = self.root / "custodian.pub"
        self.signature.write_bytes(b"fixture")
        self.key.write_text("fixture")
        self.statement = {
            "schema_version": "custodian-intake/0.1",
            "archive_manifest_sha256": hashlib.sha256((self.archive / "manifest.json").read_bytes()).hexdigest(),
            "custodian_id": "independent-fixture", "storage_reference": "fixture-001",
            "accepted_at": "2026-10-27T00:00:00Z", "retain_until": "2036-10-27T00:00:00Z"
        }

    def tearDown(self):
        self.tmp.cleanup()

    def verify(self):
        self.receipt.write_text(json.dumps(self.statement))
        with patch("custodian_receipt.subprocess.run") as process:
            process.return_value.returncode = 0
            result = verify_custodian_receipt(self.archive, self.receipt, self.signature, self.key)
            process.assert_called_once()
        return result

    def test_signed_intake_fixture(self):
        self.assertEqual(self.verify()["storage_reference"], "fixture-001")

    def test_wrong_manifest_rejected(self):
        self.statement["archive_manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "different archive"):
            self.verify()

    def test_missing_custodian_rejected(self):
        self.statement.pop("custodian_id")
        with self.assertRaisesRegex(ValueError, "schema"):
            self.verify()

    def test_invalid_signature_rejected(self):
        self.receipt.write_text(json.dumps(self.statement))
        with patch("custodian_receipt.subprocess.run") as process:
            process.return_value.returncode = 1
            with self.assertRaisesRegex(ValueError, "signature"):
                verify_custodian_receipt(self.archive, self.receipt, self.signature, self.key)

if __name__ == "__main__":
    unittest.main()
