# PR 15 — Independent evidence custody handoff and release gate

Status: **NOT COMPLETE**. This document specifies a verifiable handoff; it does not assert that an external custodian has accepted any evidence.

## Custodian requirements

Select a legal and operational entity independent of the experiment coordinator and model provider. Before any transfer, record its identity, retention term, immutable/versioned storage controls, access and deletion policy, legal jurisdiction, incident response process, and a named contact. Require a retention commitment that outlives temporary CI artifacts. Record fees and secure explicit cost authorization before provisioning paid storage.

## Handoff procedure

1. Finish the run, export the bundle and witnessed sidecar with `export_evidence`, and independently verify with `verify_archived_pilot` using an authenticated pinned TSA trust anchor.
2. Transfer the **entire archive directory**, including `manifest.json`, over an authenticated channel to the custodian. Do not upload secrets, HMAC keys, model credentials, or frozen holdout materials.
3. Have the custodian independently compute the SHA-256 of every file and the archive manifest, and acknowledge the exact manifest digest, run ID, custody intake timestamp, retention deadline, storage identity, and custodian signature. Preserve this acknowledgment separately from the experiment operator's storage.
4. Retrieve a fresh copy through the custodian's read interface and verify archive hashes and RFC 3161 evidence again, without access to coordinator secrets. Test retention and access controls. Reject mismatches and preserve both copies for incident review.
5. Publish a non-sensitive verification record identifying the custodian, manifest digest, cryptographic verification outcome, and known limitations. No claim of independent custody is allowed before steps 2–4 succeed.

## Execution chronology

RFC 3161 receipts prove that commitments existed by the TSA's signed generation time, subject to TSA trust. They do **not** prove when a provider executed, what the provider actually saw, or whether a response came from the stated model. A trusted external acquisition service must independently attest request digest, response digest, provider identity, attempt start and completion ordering, and the exact witnessed commitments. Validate the attestation against a separate trust anchor and independently retained logs. Coordinator-generated timestamps and self-signed receipts are insufficient.

## Release gate

Keep PR #15 in draft until: all CI checks pass on final HEAD; an independent custodian has accepted and returned verifiable evidence; execution attestation is independently verifiable; TSA trust-anchor provenance, nonce/freshness policy, certificate validity and revocation handling are reviewed; negative tests cover outage, malformed responses, swaps, interruption and recovery; and an independent reviewer signs off on scientific claims. No model capability, provider provenance, or chronology claim follows merely from a green test suite.

No live provider calls, external TSA requests, holdout access, or paid services are required to implement this handoff specification.
