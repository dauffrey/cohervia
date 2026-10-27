# Capability prediction evidence custody — development plan

Status: **proposal only**. No confirmatory study or model execution authorized.

## Objective
Ensure a capability-success prediction is recorded and independently committed **before** the corresponding task attempt. A hash alone proves consistency, not when a record existed.

## Proposed protocol
1. Freeze a public development task identifier, task specification digest, model identifier, prediction probability, and protocol version.
2. Write a canonical prediction record and compute its digest.
3. Obtain an independently retained, time-ordered commitment receipt before any task attempt. The receipt must bind the prediction digest, run ID, and a monotonic sequence or externally auditable timestamp.
4. Only after receipt acceptance, permit the bounded existing public pilot attempt.
5. Bind the attempt receipt and independent verifier outcome to the prior commitment; reject missing, late, conflicting, or reused commitments.
6. Replay and audit the complete chain, including failures and unknown outcomes.

## Non-goals and safeguards
- No trusted timestamps are asserted by the current prototype.
- Git commit timestamps, self-reported clocks, and locally computed hashes alone are insufficient independent proof.
- Keep public development tasks separate from the frozen COH-EXP-0001 holdouts.
- No live provider calls, paid usage, or automatic promotion of scientific claims.
- Require offline adversarial tests for replay, tampering, reordering, duplicate commitment, and absent receipt.
- Review threat model and custody provider before implementation or confirmatory use.
