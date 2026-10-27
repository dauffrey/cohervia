"""Development-only prediction/attempt/verdict contract. No model calls or authority."""
import hashlib
import json
import math

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()

def validate(record):
    if not isinstance(record, dict) or set(record) != {"prediction", "attempt", "verdict"}:
        raise ValueError("three required stages")
    p, a, v = (record[k] for k in ("prediction", "attempt", "verdict"))
    if not all(isinstance(x, dict) for x in (p, a, v)):
        raise ValueError("invalid stage")
    if set(p) != {"trial_id", "task_hash", "model", "probability"}:
        raise ValueError("invalid prediction fields")
    if set(a) != {"trial_id", "task_hash", "response", "status", "prediction_hash"}:
        raise ValueError("invalid attempt fields")
    if set(v) != {"trial_id", "attempt_hash", "outcome", "verifier"}:
        raise ValueError("invalid verdict fields")
    if not isinstance(p["trial_id"], str) or not p["trial_id"] or not isinstance(p["model"], str) or not p["model"]:
        raise ValueError("missing identity")
    if not isinstance(p["task_hash"], str) or len(p["task_hash"]) != 64:
        raise ValueError("task digest required")
    if any(x != p["trial_id"] for x in (a["trial_id"], v["trial_id"])) or a["task_hash"] != p["task_hash"]:
        raise ValueError("trial or task mismatch")
    if a["prediction_hash"] != digest(p) or v["attempt_hash"] != digest(a):
        raise ValueError("stage hash mismatch")
    probability = p["probability"]
    if isinstance(probability, bool) or not isinstance(probability, (int, float)) or not math.isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError("invalid probability")
    if a["status"] not in ("completed", "incomplete", "error") or not isinstance(a["response"], (str, type(None))):
        raise ValueError("invalid attempt")
    if a["status"] == "completed" and not isinstance(a["response"], str):
        raise ValueError("completed attempt requires recorded text")
    if a["status"] != "completed" and a["response"] is not None:
        raise ValueError("non-completed response")
    if not isinstance(v["verifier"], str) or not v["verifier"]:
        raise ValueError("verifier identity required")
    if v["outcome"] is not None and type(v["outcome"]) is not bool:
        raise ValueError("invalid outcome")
    if a["status"] != "completed" and v["outcome"] is not None:
        raise ValueError("missing outcome must remain unknown")
    if a["status"] == "completed" and v["outcome"] is None:
        raise ValueError("completed attempt must be scored")
    return {"trial_id": p["trial_id"], "brier": None if v["outcome"] is None else (float(probability) - int(v["outcome"])) ** 2, "outcome": v["outcome"], "scientific_evidence": False, "execution_authorized": False}

def make_record(trial_id, task, model, probability, response, outcome, verifier="public-exact-v1"):
    """Fabricated/test helper; caller must supply independently established outcome."""
    p = {"trial_id": trial_id, "task_hash": digest(task), "model": model, "probability": probability}
    a = {"trial_id": trial_id, "task_hash": p["task_hash"], "response": response, "status": "completed" if response is not None else "incomplete", "prediction_hash": digest(p)}
    v = {"trial_id": trial_id, "attempt_hash": digest(a), "outcome": outcome, "verifier": verifier}
    record = {"prediction": p, "attempt": a, "verdict": v}
    validate(record)
    return record
