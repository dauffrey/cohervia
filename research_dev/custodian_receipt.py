"""Custodian intake receipts: validate independently signed acceptance of an archive.

This module does not transfer evidence or create a trusted custodian. An
independent custodian must sign the exact intake statement with its private key.
"""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from evidence_archive import verify_archive
from persistent_custody import canonical

REQUIRED = {"schema_version", "archive_manifest_sha256", "custodian_id",
            "storage_reference", "accepted_at", "retain_until"}

def verify_custodian_receipt(archive_dir, receipt_path, signature_path, public_key_path):
    """Verify archive, exact intake statement, and detached Ed25519 signature."""
    archive_dir = Path(archive_dir)
    verify_archive(archive_dir)
    statement = json.loads(Path(receipt_path).read_bytes())
    if type(statement) is not dict or set(statement) != REQUIRED:
        raise ValueError("invalid custodian receipt schema")
    if statement["schema_version"] != "custodian-intake/0.1":
        raise ValueError("unsupported custodian receipt")
    for name in REQUIRED - {"schema_version", "archive_manifest_sha256"}:
        if type(statement[name]) is not str or not statement[name].strip():
            raise ValueError("invalid custodian receipt field: " + name)
    expected = hashlib.sha256((archive_dir / "manifest.json").read_bytes()).hexdigest()
    if statement["archive_manifest_sha256"] != expected:
        raise ValueError("custodian receipt references different archive")
    with tempfile.TemporaryDirectory() as directory:
        payload = Path(directory) / "statement.json"
        payload.write_bytes(canonical(statement))
        result = subprocess.run(
            ["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(public_key_path),
             "-rawin", "-in", str(payload), "-sigfile", str(signature_path)],
            capture_output=True, check=False, timeout=30)
        if result.returncode:
            raise ValueError("invalid custodian signature")
    return statement
