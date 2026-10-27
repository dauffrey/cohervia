"""Development-only coordinator entry point for custody-gated pilot execution.

Caller supplies genuine prospective probabilities; this module never invents
model predictions. All commitments are durable before pilot acquisition starts.
No live provider is constructed here and no external time claims are made.
"""
from cohervia_pilot.protocol import catalog
from cohervia_pilot.runner import run
from gated_provider import CustodyGatedProvider
from external_witness import witnessed_commitments
from persistent_custody import PersistentCustody, digest

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
    with PersistentCustody(custody_path, secret) as custody:
        for task in tasks:
            prediction = {"trial_id": run_id + ":" + task["id"], "task_hash": digest(task),
                          "model": provider.model, "probability": probabilities[task["id"]]}
            receipts[task["id"]] = custody.commit(prediction)
    witnessed = {task["id"]: witness_submit(receipts[task["id"]]) for task in tasks}
    witnessed_commitments(receipts, witnessed, witness_verify, witness_id)
    bundle, report = run(CustodyGatedProvider(provider, custody_path, secret, run_id, receipts, probabilities), output_dir, run_id)
    return bundle, report, receipts, witnessed
