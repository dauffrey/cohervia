"""Read-only research-signal regressions; fictional inputs only."""
import unittest

from cohervia.shadow_evidence import assess_shadow_evidence


def packet():
    return {
        "schema_version": "efgm-evidence-summary/0.1",
        "source_repository": "dauffrey/efgm",
        "claim_id": "fabricated-claim",
        "model_sha256": "a" * 64,
        "evidence_manifest_sha256": "b" * 64,
        "efgm_disposition": "READY_FOR_EXTERNAL_AUDIT",
        "efgm_reasons": [],
        "provenance_status": "observed",
        "independent_evidence_status": "observed",
    }


class ShadowEvidenceTests(unittest.TestCase):
    def test_complete_fictional_summary_is_still_untrusted(self):
        result = assess_shadow_evidence(packet())
        self.assertEqual(result.status, "UNVERIFIED_REVIEW_CANDIDATE")
        self.assertFalse(result.evidence_independently_verified)
        self.assertFalse(result.grants_permission)
        self.assertFalse(result.governor_intervened)

    def test_explicit_missingness_blocks_review(self):
        for field in ("provenance_status", "independent_evidence_status"):
            for value in ("unknown", "inferred", "not_applicable"):
                with self.subTest(field=field, value=value):
                    sample = packet()
                    sample[field] = value
                    result = assess_shadow_evidence(sample)
                    self.assertEqual(result.status, "INSUFFICIENT_EVIDENCE")
                    self.assertIn(field.removesuffix("_status") + "_not_observed", result.reasons)
                    self.assertFalse(result.grants_permission)

    def test_prior_efgm_issue_cannot_be_laundered(self):
        sample = packet()
        sample.update(efgm_disposition="INSUFFICIENT_EVIDENCE",
                      efgm_reasons=["heldout_evaluation_not_observed"])
        result = assess_shadow_evidence(sample)
        self.assertEqual(result.status, "INSUFFICIENT_EVIDENCE")
        self.assertIn("reported_claim_has_issues", result.reasons)

    def test_malformed_or_forged_shape_rejected(self):
        self.assertEqual(assess_shadow_evidence({}).status, "INVALID")
        self.assertEqual(assess_shadow_evidence(None).status, "INVALID")
        for field, value in (
            ("source_repository", "unknown/efgm"),
            ("model_sha256", "INVALID"),
            ("efgm_disposition", "SCIENTIFICALLY_PROVEN"),
            ("provenance_status", True),
            ("efgm_reasons", ["duplicate", "duplicate"]),
            ("efgm_reasons", ["z", "a"]),
        ):
            sample = packet()
            sample[field] = value
            self.assertEqual(assess_shadow_evidence(sample).status, "INVALID")
        sample = packet()
        sample["allows_action"] = True
        self.assertEqual(assess_shadow_evidence(sample).status, "INVALID")

    def test_no_record_can_grant_permissions_or_establish_causal_truth(self):
        cases = [packet(), None, {}, dict(packet(), provenance_status="unknown")]
        for candidate in cases:
            outcome = assess_shadow_evidence(candidate)
            self.assertFalse(outcome.grants_permission)
            self.assertFalse(outcome.evidence_independently_verified)
            self.assertFalse(outcome.governor_intervened)


if __name__ == "__main__":
    unittest.main()
