"""Read-only independent verification of a witnessed pilot sidecar and bundle.

The verifier uses a pinned TSA trust root; it never requires the coordinator HMAC
secret. It does not establish trustworthy provider execution time on its own.
"""
import json
import math
from pathlib import Path
from cohervia_pilot.protocol import catalog
from cohervia_pilot.runner import replay_bundle
from persistent_custody import digest
from rfc3161_witness import RFC3161Witness

def verify_rfc3161_pilot_evidence(bundle, sidecar_path, tsa_url, pinned_ca_file):
    """Reject missing, swapped, altered, or nonmatching external evidence."""
    replay_bundle(bundle)
    path = Path(sidecar_path)
    evidence = json.loads(path.read_text(encoding="utf-8"))
    if type(evidence) is not dict or set(evidence) != {
        "schema_version", "run_id", "witness_id", "commitments", "predictions", "attestations"
    }:
        raise ValueError("invalid witness evidence schema")
    if evidence["schema_version"] != "witness-evidence/0.2" or evidence["run_id"] != bundle["run_id"]:
        raise ValueError("witness evidence run mismatch")
    witness = RFC3161Witness(tsa_url, pinned_ca_file)
    if evidence["witness_id"] != witness.witness_id:
        raise ValueError("witness identity mismatch")
    tasks = catalog()
    expected = {task["id"] for task in tasks}
    commitments, attestations, predictions = evidence["commitments"], evidence["attestations"], evidence["predictions"]
    if type(commitments) is not dict or type(attestations) is not dict or type(predictions) is not dict or set(commitments) != expected or set(attestations) != expected or set(predictions) != expected:
        raise ValueError("incomplete witness evidence")
    seen_sequences = set()
    for task in tasks:
        task_id = task["id"]
        commitment = commitments[task_id]
        prediction = predictions[task_id]
        if type(commitment) is not dict or set(commitment) != {"trial_id", "prediction_digest", "previous_digest", "sequence", "receipt"}:
            raise ValueError("invalid commitment schema")
        if type(prediction) is not dict or set(prediction) != {"trial_id", "task_hash", "model", "probability"}:
            raise ValueError("invalid prospective prediction schema")
        if (prediction["trial_id"] != bundle["run_id"] + ":" + task_id
                or prediction["task_hash"] != digest(task)
                or prediction["model"] != bundle["inputs"]["configuration"]["requested_model"]
                or type(prediction["probability"]) not in (int, float)
                or not math.isfinite(prediction["probability"])
                or not 0 <= prediction["probability"] <= 1):
            raise ValueError("prospective prediction mismatch")
        if digest(prediction) != commitment["prediction_digest"]:
            raise ValueError("prediction content does not match witnessed commitment")
        if type(commitment) is not dict or set(commitment) != {
            "trial_id", "prediction_digest", "previous_digest", "sequence", "receipt"
        }:
            raise ValueError("invalid commitment schema")
        if commitment["trial_id"] != bundle["run_id"] + ":" + task_id:
            raise ValueError("swapped task commitment")
        if type(commitment["prediction_digest"]) is not str or len(commitment["prediction_digest"]) != 64:
            raise ValueError("invalid prediction digest")
        sequence = commitment["sequence"]
        if type(sequence) is not int or sequence < 1 or sequence in seen_sequences:
            raise ValueError("duplicate or invalid custody sequence")
        seen_sequences.add(sequence)
        if type(commitment["receipt"]) is not str or len(commitment["receipt"]) != 64:
            raise ValueError("invalid custody receipt shape")
        if not witness.verify(attestations[task_id], commitment):
            raise ValueError("unverified external witness")
    return {
        "pilot_bundle_sha256": bundle["sha256"],
        "run_id": bundle["run_id"],
        "independent_timestamp_verified": True,
        "task_count": len(tasks),
        "provider_execution_time_independently_proven": False,
        "prediction_contents_authenticated": True,
    }
