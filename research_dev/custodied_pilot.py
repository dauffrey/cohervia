"""Development-only coordinator entry point for custody-gated pilot execution.

Caller supplies genuine prospective probabilities; this module never invents
model predictions. All commitments are durable before pilot acquisition starts.
No live provider is constructed here and no external time claims are made.
"""
import os
import tempfile
from pathlib import Path
from cohervia_pilot.protocol import catalog
from cohervia_pilot.runner import run
from gated_provider import CustodyGatedProvider
from external_witness import witnessed_commitments
from persistent_custody import PersistentCustody, digest, canonical

def run_custodied_pilot(provider, output_dir, run_id, probabilities, custody_path, secret):
    tasks = catalog()
    expected = {task["id"] for task in tasks}
    if type(probabilities) is not dict or set(probabilities) != expected:
        raise ValueError("complete prospective predictions required")
    receipts = {}
    # Commit all predictions before invoking runner; no fallback to ungated run.
    with PersistentCustody(custody_path, secret) as custody:
        for task in tasks:
            prediction = {"trial_id": run_id + ":" + task["id"], "task_hash": digest(task),
                          "model": provider.model, "probability": probabilities[task["id"]]}
            receipts[task["id"]] = custody.commit(prediction)
    gated = CustodyGatedProvider(provider, custody_path, secret, run_id, receipts, probabilities)
    bundle, report = run(gated, output_dir, run_id)
    return bundle, report, receipts

def run_witnessed_pilot(provider, output_dir, run_id, probabilities, custody_path, secret, witness_submit, witness_verify, witness_id):
    """Fail closed unless every commitment is witnessed before acquisition."""
    tasks = catalog()
    if type(probabilities) is not dict or set(probabilities) != {task["id"] for task in tasks}:
        raise ValueError("complete predictions required")
    if not callable(witness_submit) or not callable(witness_verify) or not witness_id:
        raise ValueError("external witness required")
    receipts = {}
    predictions = {}
    with PersistentCustody(custody_path, secret) as custody:
        for task in tasks:
            prediction = {"trial_id": run_id + ":" + task["id"], "task_hash": digest(task),
                          "model": provider.model, "probability": probabilities[task["id"]]}
            predictions[task["id"]] = prediction
            receipts[task["id"]] = custody.commit(prediction)
    witnessed = {task["id"]: witness_submit(receipts[task["id"]]) for task in tasks}
    witnessed_commitments(receipts, witnessed, witness_verify, witness_id)
    # Retain an independently verifiable sidecar before any acquisition.
    # The pilot runner owns its output directory, so sidecar lives alongside it.
    sidecar = Path(str(output_dir) + ".witness.json")
    record = {"schema_version": "witness-evidence/0.2", "run_id": run_id,
              "witness_id": witness_id, "commitments": receipts, "predictions": predictions, "attestations": witnessed}
    raw = canonical(record)
    # Exclusive final publication: an interrupted temporary write never appears
    # as a valid sidecar. Never replace evidence from an earlier run.
    parent = sidecar.parent
    if sidecar.exists():
        raise FileExistsError("witness evidence already exists")
    fd, temporary = tempfile.mkstemp(prefix="." + sidecar.name + ".", suffix=".pending", dir=parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        # Hard-link is atomic and fails if the final evidence already exists.
        os.link(temporary, sidecar)
        directory_fd = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        os.unlink(temporary)
    bundle, report = run(CustodyGatedProvider(provider, custody_path, secret, run_id, receipts, probabilities), output_dir, run_id)
    return bundle, report, receipts, witnessed

def run_rfc3161_pilot(provider, output_dir, run_id, probabilities, custody_path,
                      secret, tsa_url, pinned_ca_file):
    """Production-shaped strict path; real TSA network use requires authorization.

    Verification binds each response to the exact committed receipt.
    """
    from rfc3161_witness import RFC3161Witness
    witness = RFC3161Witness(tsa_url, pinned_ca_file)
    def submit(commitment):
        return witness.submit(commitment)
    # Store expected commitment per signed response for verifier callback.
    submitted = {}
    def tracked_submit(commitment):
        receipt = submit(commitment)
        submitted[receipt["signature"]] = commitment
        return receipt
    def verify(receipt):
        commitment = submitted.get(receipt["signature"])
        if commitment is None:
            return False
        return witness.verify(receipt, commitment)
    return run_witnessed_pilot(provider, output_dir, run_id, probabilities, custody_path,
                               secret, tracked_submit, verify, witness.witness_id)
