"""Offline AWS S3 Object Lock custody deployment contract.

No boto3 dependency, credentials, cloud calls, or resource provisioning.
An independent custodian must own the destination account and attest intake.
"""
from datetime import datetime, timezone

def validate_s3_custody_plan(plan):
    required = {"bucket", "region", "custodian_id", "retention_days",
                "object_lock_mode", "independent_account", "expected_monthly_cost_usd"}
    if type(plan) is not dict or set(plan) != required:
        raise ValueError("invalid custody plan schema")
    for key in ("bucket", "region", "custodian_id"):
        if type(plan[key]) is not str or not plan[key].strip():
            raise ValueError("invalid custody plan field: " + key)
    if plan["object_lock_mode"] != "COMPLIANCE":
        raise ValueError("compliance-mode object lock required")
    if plan["independent_account"] is not True:
        raise ValueError("independent account required")
    if type(plan["retention_days"]) is not int or plan["retention_days"] < 1:
        raise ValueError("positive retention period required")
    cost = plan["expected_monthly_cost_usd"]
    if type(cost) not in (int, float) or not 0 <= cost < float("inf"):
        raise ValueError("finite nonnegative cost estimate required")
    return dict(plan)

def validate_s3_retention_evidence(evidence, plan):
    """Validate provider-returned retention metadata; not proof of provider origin."""
    validate_s3_custody_plan(plan)
    if type(evidence) is not dict or set(evidence) != {"bucket", "version_id", "mode", "retain_until"}:
        raise ValueError("invalid retention evidence")
    if evidence["bucket"] != plan["bucket"] or evidence["mode"] != "COMPLIANCE":
        raise ValueError("incorrect custody destination or lock mode")
    if type(evidence["version_id"]) is not str or not evidence["version_id"].strip():
        raise ValueError("versioned object required")
    if type(evidence["retain_until"]) is not str:
        raise ValueError("retention deadline required")
    try:
        deadline = datetime.fromisoformat(evidence["retain_until"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid retention deadline") from exc
    if deadline.tzinfo is None or deadline <= datetime.now(timezone.utc):
        raise ValueError("retention deadline must be in the future")
    return True
