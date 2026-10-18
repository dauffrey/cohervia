# Phase 2 plan — minimal observation and audit core

Status: implemented for review in the separate [core v0.1.0 package](../../core/README.md), from merged PR #8 main. Fabricated acceptance regressions validate infrastructure only. Scientist qualification and COH-EXP-0001 statistical design remain separate workstreams; confirmatory holdouts remain sealed.
Goal: validate versioned observations, preserve identity/provenance, append audit dispositions,
and replay deterministically. Contract conformance is distinct from measurement truth, predictive validity or scientific evidence.

## P1 — Bounded implementation

Fresh implementation (no predecessor code copied):

| Module | Public interface | Responsibility |
| --- | --- | --- |
| core/src/cohervia/observations.py | validate_observation(raw, context, inputs, state) -> ValidationResult | O1–O4; accept/reject/quarantine and reason codes |
| core/src/cohervia/canonical.py | canonical_bytes(record), record_sha256(record) | A4; pinned JCS-compatible encoding |
| core/src/cohervia/audit.py | AuditStore(path).append_submission(raw, context, inputs, recorder fields), export(context, inputs) | A3–A4; atomic local persistence |
| core/src/cohervia/replay.py | replay(events, observations, context, inputs, checkpoint=None) -> ObservationState | A5; deterministic reconstruction |

Uses a local transactional SQLite store with explicit caller-supplied path and
serialized writes. No daemon, cloud service or network evidence resolver.
The JCS implementation is pinned to `rfc8785==0.1.4`, with numeric/string/UTF-16 conformance vectors. `FrozenInputs` binds the canonical definitions, configuration and expected evidence manifest per run; artifacts are supplied bytes, never paths.
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

Observation validation, canonical encoding, atomic audit append and replay are implemented in separate modules.
Exit requires all matrix tests passing, documentation matching behavior, reproducible local
installation/test instructions, and review of the exact implementation commit.
The dedicated observation-core CI runs its contract acceptance gate on Python 3.11–3.13, plus preserved mainline boundaries. Existing Scientist and apparatus suites remain independent gates. See the package README for installation, input schema, checkpoint semantics and replay limitations.
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
