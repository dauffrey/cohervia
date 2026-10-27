"""Independent-witness protocol boundary for prospective public development runs.

Witness is supplied by an independently operated service, not the model or
coordinator. This module deliberately does not provide a self-attesting witness.
A verified receipt is required before the first pilot task is executed.
"""
from datetime import datetime, timezone
from persistent_custody import digest

def verify_witness(receipt, commitment, verifier, *, expected_witness_id):
    """Verify identity, binding, and externally authenticated attestation.

    verifier(receipt) must validate an independently pinned public key and
    trustworthy receipt provenance. A callback returning True alone is NOT
    evidence of independence; production deployment must audit its implementation.
    """
    if type(receipt) is not dict or set(receipt) != {
        "version", "witness_id", "commitment_sha256", "observed_at", "signature"
    }:
        raise ValueError("invalid witness receipt")
    if receipt["version"] != "witness/0.1" or receipt["witness_id"] != expected_witness_id:
        raise ValueError("wrong witness identity or protocol")
    if receipt["commitment_sha256"] != digest(commitment):
        raise ValueError("witness commitment mismatch")
    timestamp = receipt["observed_at"]
    if type(timestamp) is not str or not timestamp.endswith("Z"):
        raise ValueError("invalid witness timestamp")
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid witness timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("witness timestamp must be UTC")
    if type(receipt["signature"]) is not str or not receipt["signature"]:
        raise ValueError("missing witness signature")
    if verifier is None or verifier(receipt) is not True:
        raise ValueError("witness authentication failed")
    return True

def witnessed_commitments(receipts, witness_receipts, verifier, witness_id):
    """Fail closed unless every prospective commitment has an external receipt."""
    if type(receipts) is not dict or type(witness_receipts) is not dict or set(receipts) != set(witness_receipts):
        raise ValueError("every commitment requires an external witness")
    for task_id, commitment in receipts.items():
        verify_witness(witness_receipts[task_id], commitment, verifier, expected_witness_id=witness_id)
    return True
