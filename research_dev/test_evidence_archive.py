"""Offline archive integrity tests; no third-party storage is implied."""
import json
import tempfile
import unittest
from pathlib import Path
from evidence_archive import export_evidence, verify_archive

class EvidenceArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bundle = self.root / "source-bundle.json"
        self.witness = self.root / "source-witness.json"
        self.bundle.write_text('{"run_id":"synthetic"}')
        self.witness.write_text('{"schema_version":"witness-evidence/0.2"}')
        self.archive = self.root / "archive"

    def tearDown(self):
        self.tmp.cleanup()

    def test_round_trip(self):
        manifest = export_evidence(self.bundle, self.witness, self.archive)
        self.assertEqual(verify_archive(self.archive), manifest)

    def test_tampered_witness_rejected(self):
        export_evidence(self.bundle, self.witness, self.archive)
        (self.archive / "witness.json").write_text('{"tampered":true}')
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            verify_archive(self.archive)

    def test_tampered_bundle_rejected(self):
        export_evidence(self.bundle, self.witness, self.archive)
        (self.archive / "bundle.json").write_text('{"tampered":true}')
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            verify_archive(self.archive)

    def test_existing_archive_not_replaced(self):
        export_evidence(self.bundle, self.witness, self.archive)
        with self.assertRaises(FileExistsError):
            export_evidence(self.bundle, self.witness, self.archive)
        verify_archive(self.archive)

    def test_missing_evidence_rejected(self):
        export_evidence(self.bundle, self.witness, self.archive)
        (self.archive / "witness.json").unlink()
        with self.assertRaises(ValueError):
            verify_archive(self.archive)

    def test_extra_file_rejected(self):
        export_evidence(self.bundle, self.witness, self.archive)
        (self.archive / "unexpected").write_text("x")
        with self.assertRaises(ValueError):
            verify_archive(self.archive)

if __name__ == "__main__":
    unittest.main()
