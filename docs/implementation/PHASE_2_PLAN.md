# Phase 2 plan — minimal observation and audit core

Status: proposed plan; implementation has not begun. Phase 1 remains pending review.
Goal: validate versioned observations, preserve identity/provenance, append audit dispositions,
and replay deterministically. Contracts are proposed requirements, not validated mechanisms.

## P1 — Bounded implementation

Proposed fresh implementation (no files created by this PR):

| Module | Public interface | Responsibility |
| --- | --- | --- |
| src/cohervia/observations.py | validate_observation(raw, context, definitions, manifest, state) -> ValidationResult | O1–O4; accept/reject/quarantine and reason codes |
| src/cohervia/canonical.py | canonical_bytes(record), record_sha256(record) | A4; pinned JCS-compatible encoding |
| src/cohervia/audit.py | append_submission(store, raw, context), verify_stream(events, store) | A3–A4; atomic local persistence |
| src/cohervia/replay.py | replay(events, observations, definitions, manifest) -> ReplayState | A5; deterministic reconstruction |

Use a local transactional store (proposed SQLite) with explicit caller-supplied path and
serialized writes. No daemon, cloud service or network evidence resolver.
The first implementation PR must choose and pin a JCS implementation or demonstrate conformance
of a fresh encoder before claiming stable hashes. This dependency is an implementation gate.
Tests use fabricated local artifacts and deterministic IDs/timestamps supplied by fixtures.
Runtime package/dependency/license choices remain subject to owner review before distribution.

## P2 — Explicit exclusions

No composite scores, hazard, viability or velocity estimation; no boundary diagnostics;
no authority or intervention controller; no permission enforcement; no shadow-mode benchmark;
no model/API calls, autonomous tools, real-agent trials, or confirmatory experiment.
No COH-EXP identifier is created. No predecessor holdout is accessed or executed.
Record validation does not prove data truth, predictive value, security or safety.

## P3 — Acceptance matrix

| Test | Contract | Expected result |
| --- | --- | --- |
| Observed and inferred valid records | O1–O3 | Accept; inferred retains derivation, inputs and scorer |
| Unknown and not_applicable | O2 | Null preserved; status distinctions survive replay |
| Nonfinite, boolean-as-number, invalid units/domain | O2 | Reject; no accepted-state mutation |
| Run/trajectory/subject mismatch | O4 | Reject identity_mismatch |
| Identical duplicate and conflicting ID | O4 | duplicate_noop vs rejection; audit both submissions |
| Late event, sequence gap and decreasing availability | O4, T3 | Late evidence accepted only at current availability; gap/regression quarantined |
| Missing/unresolved refs and digest mismatch | O3–O4 | Missing required ref rejected; unresolved quarantine; mismatch reject |
| Null uncertainty | O2 | Retained without confidence default |
| Canonicalization vectors, reordered keys, array changes | A4 | Same digest for equivalent JCS objects; changed ordered arrays differ |
| Atomic append failure | A4 | Both audit and observation rolled back |
| Audit round-trip and replay | A3–A5 | Identical accepted index/order; duplicate does not advance |
| Corruption, missing referenced record, broken chain | A5 | Stop with explicit error; no silent skip |
| Unsupported schema version | O1, A3 | Reject before interpreting fields |
| External behavior boundary | P2, A5 | Tests deny network access and spy on side-effect boundaries; only designated local store writes |
| Privacy fixtures | A6 | No real prompts, secrets, personal data or holdout artifacts |

Do not test predecessor experiments. This matrix tests new interface behavior with fictional fixtures.
Later predictor tests and authority tests belong to separate phases.

## P4 — Sequence and exit

Implement observation validation, then canonical encoding, then atomic audit append and replay.
Exit requires all matrix tests passing, documentation matching behavior, reproducible local
installation/test instructions, and review of the exact implementation commit.
A later PR can introduce an appropriate CI gate; none is introduced here.
No claim of production hardening or tamper-proof storage follows from passing these tests.

## P5 — Decisions and reuse blockers

Fresh implementation can satisfy these contracts without importing predecessor code.
EFGM has Apache-2.0 and CGS has MIT notices; any later copying requires applicable notices
and a compatibility review. Artificial Homeostasis has no root license or declared project
license in the inspected snapshot, so no code reuse is assumed authorized.
Cohervia licensing is unresolved and must be decided before code distribution.

Domain metric definitions, calibrated state estimators, authenticated collectors,
retention policy and trusted external checkpoints remain deferred. They do not prevent
a local fixture-based observation core, but they block claims of deployment readiness.
