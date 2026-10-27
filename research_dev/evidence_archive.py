"""Offline, self-contained evidence export; NOT independent off-site custody.

Export the completed pilot bundle and witnessed sidecar as immutable-by-convention
copies with a canonical SHA-256 manifest. Store the resulting directory with an
independent custodian; the manifest alone cannot defeat coordinated replacement.
"""
import hashlib
import json
import os
from pathlib import Path
from persistent_custody import canonical

FILES = {"bundle.json", "witness.json"}

def _sha256(raw):
    return hashlib.sha256(raw).hexdigest()

def _durable_exclusive(path, raw):
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())

def export_evidence(bundle_path, witness_path, destination):
    """Create an exclusive archival package; never overwrite prior evidence."""
    bundle = Path(bundle_path).read_bytes()
    witness = Path(witness_path).read_bytes()
    for raw in (bundle, witness):
        if type(json.loads(raw)) is not dict:
            raise ValueError("evidence must be JSON objects")
    destination = Path(destination)
    destination.mkdir(parents=False, exist_ok=False)
    parent_fd = os.open(destination.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)
    try:
        _durable_exclusive(destination / "bundle.json", bundle)
        _durable_exclusive(destination / "witness.json", witness)
        manifest = {"schema_version": "evidence-archive/0.1",
                    "files": {"bundle.json": _sha256(bundle), "witness.json": _sha256(witness)}}
        _durable_exclusive(destination / "manifest.json", canonical(manifest))
        fd = os.open(destination, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        return manifest
    except BaseException:
        # Retain partial evidence for inspection; do not silently erase it.
        raise

def verify_archive(destination):
    """Verify byte-level integrity; separately run RFC3161 replay for authenticity."""
    destination = Path(destination)
    if {p.name for p in destination.iterdir()} != FILES | {"manifest.json"}:
        raise ValueError("archive contains missing or unexpected files")
    manifest = json.loads((destination / "manifest.json").read_bytes())
    if (type(manifest) is not dict or set(manifest) != {"schema_version", "files"}
            or manifest["schema_version"] != "evidence-archive/0.1"
            or type(manifest["files"]) is not dict or set(manifest["files"]) != FILES):
        raise ValueError("invalid archive manifest")
    for name in FILES:
        if not (destination / name).is_file() or _sha256((destination / name).read_bytes()) != manifest["files"][name]:
            raise ValueError("archive digest mismatch: " + name)
    return manifest

def verify_archived_pilot(destination, tsa_url, pinned_ca_file):
    """Verify archive digests AND independently verify RFC3161 pilot evidence."""
    from witnessed_replay import verify_rfc3161_pilot_evidence
    destination = Path(destination)
    verify_archive(destination)
    bundle = json.loads((destination / "bundle.json").read_bytes())
    return verify_rfc3161_pilot_evidence(
        bundle, destination / "witness.json", tsa_url, pinned_ca_file
    )
