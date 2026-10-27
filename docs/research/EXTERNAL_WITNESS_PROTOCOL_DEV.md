# Independent witness integration boundary — development only

The strict coordinator `run_witnessed_pilot` requires a separate witness receipt for **every** prospective prediction commitment, verifies all receipts, and only then invokes the bounded public pilot. A missing, mismatched, malformed, or unauthenticated receipt blocks acquisition. The existing ungated pilot and local-only coordinator remain available for non-evidentiary instrumentation; **do not claim** they are externally witnessed.

## Trust and deployment requirements

1. Select a witness operated under independent credentials and storage, with a pinned verification public key, immutable/append-only retention, and externally auditable timestamps. The coordinator must not control the witness key or rewrite its records.
2. Implement `witness_submit(commitment)` as an authenticated submission returning a receipt with `version`, `witness_id`, `commitment_sha256`, UTC `observed_at`, and `signature`. The digest binds the complete local commitment receipt, including the prediction digest and chain predecessor.
3. Implement `witness_verify(receipt)` to **cryptographically verify** the witness signature using the pinned key and independently validate its receipt format and trusted timestamp. A callback returning `True` without real verification is insecure and is used only in offline mock tests.
4. Persist the witness receipts with the run evidence and independently cross-check the witnessed commitments, consumption records, and pilot bundle. The current strict coordinator **returns** witness receipts but does not yet archive them with the bundle.
5. Record witness clock accuracy, service identity, signing-key rotation, retention policy, outage handling, and a maximum permissible age. A signed timestamp from a self-controlled service is not proof of independent pre-commitment.
6. Require explicit authorization before any live provider invocation. No paid calls or confirmatory holdouts are enabled here.

## Limits

The interface and six offline adversarial tests are **protocol readiness**, not deployed external custody. A caller-supplied verifier can lie; this repository cannot assert independent verification until a concrete external witness and audit trail are deployed and reviewed. Witness receipt time must be proven earlier than provider attempt time by an independent mechanism, not merely compared against coordinator-generated timestamps.
