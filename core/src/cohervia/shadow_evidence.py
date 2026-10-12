"""Read-only research intake for untrusted EFGM evidence summaries.

Never an authorizer, scientific evaluator, trusted provenance validator,
or model-interpreter. No implicit ingestion into Cohervia's audit store.
"""
from dataclasses import dataclass

from .inputs import digest, identifier

_FIELDS = {
    "schema_version", "source_repository", "claim_id", "model_sha256",
    "evidence_manifest_sha256", "efgm_disposition", "efgm_reasons",
    "provenance_status", "independent_evidence_status",
}
_STATES = {"observed", "inferred", "unknown", "not_applicable"}
_DISPOSITIONS = {"INVALID", "INSUFFICIENT_EVIDENCE", "READY_FOR_EXTERNAL_AUDIT"}


@dataclass(frozen=True)
class ShadowEvidenceSignal:
    status: str
    reasons: tuple[str, ...]
    evidence_independently_verified: bool = False
    grants_permission: bool = False
    governor_intervened: bool = False


def assess_shadow_evidence(summary: object) -> ShadowEvidenceSignal:
    """Categorize the *reported* readiness of evidence for external review.

    Not a cross-project trust boundary: all fields can be forged by a caller.
    Even 'UNVERIFIED_REVIEW_CANDIDATE' cannot promote scientific claims,
    alter the agent's permissions, or be used as authorization.
    """
    if type(summary) is not dict or set(summary) != _FIELDS:
        return ShadowEvidenceSignal("INVALID", ("invalid_shape",))
    if summary["schema_version"] != "efgm-evidence-summary/0.1":
        return ShadowEvidenceSignal("INVALID", ("unsupported_schema",))
    if summary["source_repository"] != "dauffrey/efgm" or not identifier(summary["claim_id"]):
        return ShadowEvidenceSignal("INVALID", ("invalid_source_or_claim",))
    if not digest(summary["model_sha256"]) or not digest(summary["evidence_manifest_sha256"]):
        return ShadowEvidenceSignal("INVALID", ("invalid_hash_identity",))
    if summary["efgm_disposition"] not in _DISPOSITIONS or type(summary["efgm_disposition"]) is not str:
        return ShadowEvidenceSignal("INVALID", ("invalid_disposition",))
    reasons = summary["efgm_reasons"]
    if (type(reasons) is not list
            or any(not identifier(v) for v in reasons)
            or reasons != sorted(set(reasons))
            or any(type(summary[key]) is not str or summary[key] not in _STATES
                   for key in ("provenance_status", "independent_evidence_status"))):
        return ShadowEvidenceSignal("INVALID", ("invalid_evidence_states",))

    blockers = []
    if summary["efgm_disposition"] != "READY_FOR_EXTERNAL_AUDIT":
        blockers.append("efgm_claim_not_review_ready")
    if reasons:
        blockers.append("reported_claim_has_issues")
    if summary["provenance_status"] != "observed":
        blockers.append("provenance_not_observed")
    if summary["independent_evidence_status"] != "observed":
        blockers.append("independent_evidence_not_observed")
    if blockers:
        return ShadowEvidenceSignal("INSUFFICIENT_EVIDENCE", tuple(sorted(blockers)))
    return ShadowEvidenceSignal("UNVERIFIED_REVIEW_CANDIDATE", ())


__all__ = ["ShadowEvidenceSignal", "assess_shadow_evidence"]
