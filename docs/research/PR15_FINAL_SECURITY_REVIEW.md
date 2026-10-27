# PR 15 — final security and evidence review (2026-10-27)

**Disposition: HOLD IN DRAFT.** This is a development prototype, not yet a scientific evidence system. Six CI workflows, including the real synthetic FreeTSA RFC 3161 smoke test, passed at commit `549d41af78b9ae314bcd6bf68bef645d1ad417af`. The timestamp evidence artifact was retained by GitHub Actions. This proves a successful test receipt, not prospective custody for a model trial.

## Findings and acceptance criteria

**P1 — External witness binding to execution remains unproven.** The `run_witnessed_pilot` entry point accepts arbitrary `witness_submit` and `witness_verify` callbacks; a verifier that always returns true passes the offline tests. The RFC 3161-specific path is stronger but still requires a genuine trust anchor and full integration tests. Require a tested cryptographic verifier, no bypass to generic callbacks in evidence-producing runs, and signed receipts for every committed task.

**P1 — Replay does not authenticate the witness sidecar.** `assess_custodied_pilot_bundle` checks local HMAC consumption and replays the bundle, but always reports `independent_timestamp_verified=False`; it does not ingest the sidecar or verify the signed TSA responses. Add a read-only witnessed replay verifier that validates each signed response, commitment digest, exact task identity, and bundle run identity; reject missing, duplicate, swapped, or altered evidence.

**P1 — Timestamp chronology is not end-to-end established.** The coordinator verifies all witness receipts before calling the runner, but the persisted evidence does not independently establish provider attempt time. Require a verifiable ordering record or trusted acquisition log, plus clock/ordering threat-model review. Do not equate timestamp authenticity with independent proof of task outcome.

**P2 — Durable evidence lifecycle.** The sidecar is fsynced before execution and created with exclusive mode, but its parent directory is not fsynced, and there is no atomic publication or bundle-sidecar manifest binding. Handle interrupted writes, stale sidecars, cleanup, recovery, and audit chain reconciliation. Never overwrite existing evidence silently.

**P2 — Witness freshness, identity, and certificate lifecycle.** The adapter validates the signed response against the submitted data and a pinned CA file. Review nonce matching, timestamp freshness, certificate policy/EKU, revocation handling, TSA key rotation, certificate expiry, and FreeTSA's service terms before production. Do not accept a CA fingerprint from an unverified source as an independent trust decision.

**P2 — External CI endpoint safety.** A pull-request-triggered network workflow can be abused or can overuse a free TSA. The smoke workflow was changed to manual dispatch only; verify no automatic external requests remain. Keep synthetic-only payloads and bounded timeout, with explicit service approval.

**P2 — Failure-path tests.** Add tests for TSA outage, invalid response content type, invalid/expired certificates, invalid signature, mismatched imprint, malformed DER, stale timestamps, swapped receipts, duplicate commitments, partial sidecar writes, and interruption between witness submission and execution. Ensure zero provider calls on all failures.

## Release gate

Do not merge PR 15 or label its output scientifically validated until P1 items are resolved, P2 threat model and negative tests are addressed, all workflows are green on the final commit, and the replayable external evidence can be independently verified without coordinator secrets. No live paid model calls or frozen holdout access are authorized by this review.
