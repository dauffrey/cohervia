"""Read-only adapter: pair externally supplied pre-task predictions with an existing pilot bundle.

No model calls, no task generation, no authority, and no experiment execution.
Predictions are external and must have been committed before pilot acquisition.
"""
from cohervia.canonical import parse_canonical
from cohervia_pilot.runner import replay_bundle
from cohervia_pilot.protocol import catalog, outcomes
from capability_assessment import make_record, validate

def assess_pilot_bundle(bundle, predictions):
    """Return development-only calibration rows after independently replaying pilot evidence.

    predictions: mapping task_id -> {"probability": number, "checkpoint": string}.
    Checkpoint is a nonempty external commitment reference; its existence/time is
    NOT authenticated here. Never treat this as prospective evidence without custody.
    """
    replay_bundle(bundle)
    tasks = catalog()
    if type(predictions) is not dict or set(predictions) != {t["id"] for t in tasks}:
        raise ValueError("predictions must cover the exact fixed catalog")
    plan = bundle["inputs"]["configuration"]
    if plan["mode"] not in ("live_development", "scripted_instrumentation"):
        raise ValueError("not a development pilot")
    rows = []
    for task in tasks:
        prediction = predictions[task["id"]]
        if type(prediction) is not dict or set(prediction) != {"probability", "checkpoint"}:
            raise ValueError("invalid prediction")
        if type(prediction["checkpoint"]) is not str or not prediction["checkpoint"].strip():
            raise ValueError("external prediction checkpoint required")
        receipt = parse_canonical(bundle["artifacts"]["receipt:" + task["id"]].encode("utf-8"))
        result = receipt["provider_result"]
        outcome = outcomes(result, task)["task_success"]
        response = result["text"] if result["status"] == "completed" else None
        record = make_record(bundle["run_id"] + ":" + task["id"], task, plan["requested_model"],
                             prediction["probability"], response, outcome)
        scored = validate(record)
        rows.append({"task_id": task["id"], "prediction_checkpoint": prediction["checkpoint"],
                     "outcome": scored["outcome"], "brier": scored["brier"],
                     "scientific_evidence": False, "execution_authorized": False})
    return {"pilot_bundle_sha256": bundle["sha256"], "mode": plan["mode"], "rows": rows,
            "mean_brier_observed": (sum(r["brier"] for r in rows if r["brier"] is not None) /
                sum(r["brier"] is not None for r in rows)) if any(r["brier"] is not None for r in rows) else None,
            "scientific_evidence": False, "execution_authorized": False}
