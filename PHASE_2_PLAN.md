# Phase 2 plan: minimal observation and audit core

This document records the implementation plan for the next Cohervia milestone after the Phase 1 specification layer. It is a planning document only and does not introduce runtime code or operational claims.

## Goal

The Phase 2 objective is to build the minimal observation-and-audit core required for disciplined evidence capture in a future governance path. This is the first implementation-oriented milestone, but it remains deliberately narrow and evidence-first.

## Scope boundary

Phase 2 will not:

- implement a production governor;
- claim validated safety or general agent performance;
- grant authority to an autonomous system on the basis of the new core alone;
- merge predecessor evidence into Cohervia as if it were new Cohervia evidence;
- replace the architecture's strict separation between state estimation, governance, and enforcement.

## Workstreams

### 1. Observation layer

Purpose: preserve explicit measurement semantics.

Planned work:

- implement a canonical observation record compatible with the EFGM `MetricObservation` semantics;
- preserve `observed`, `inferred`, `unknown`, and `not_applicable` as distinct states;
- require `rationale`, `evidence_refs`, and confidence on each record where applicable;
- reject blank evidence references and invalid status-value pairs;
- store source provenance for each measurement source.

Exit condition:

- the observation layer can preserve missing evidence as missing and can reject invalid coercions.

### 2. Telemetry provenance and hashing

Purpose: make source quality and artifact integrity explicit.

Planned work:

- record telemetry provenance, configuration provenance, and evaluator metadata;
- attach a hash for relevant configuration or artifact snapshots when available;
- preserve the original dataset and measurement provenance chain;
- distinguish between instrumentation evidence, exploratory evidence, and confirmatory evidence.

Exit condition:

- an observation can be traced back to a source artifact and its configuration context.

### 3. Trajectory-state estimation layer

Purpose: compute viability and action authorization as separate concepts.

Planned work:

- formalize `Gamma`, `z_t`, `H_t`, `M_state_t`, `dM_state_t`, and `M_action_t(a_t)` as first-class state objects;
- maintain a frozen reference policy and a deterministic rule for state viability computations;
- preserve likelihood-mode and score-mode hazard calculation distinctions;
- provide a boundary-time diagnostic only as a local estimate and not as a guarantee.

Exit condition:

- the state layer cleanly distinguishes trajectory viability from action authorization and does not claim a safety decision from a state estimate alone.

### 4. Authority and audit layer

Purpose: enforce the governance boundary without collapsing signal and authority.

Planned work:

- retain an independent authority boundary and a separate audit record;
- log final decisions, fallback actions, and invariant violations;
- separate the decision function from the deterministic permission boundary;
- preserve the explicit difference between advisory warning and final authority action.

Exit condition:

- any decision record can explain how the final authority action was reached, what the evidence path was, and whether a hard invariant intervened.

### 5. Shadow-mode evaluation scaffold

Purpose: evaluate without granting operational authority.

Planned work:

- support shadow-mode observation and logging;
- record baseline false-alarm budgets and warning lead times;
- separate evaluation and intervention logic from enforcement logic;
- maintain a clean barrier between model development and confirmatory holdout data.

Exit condition:

- the system can produce audit-grade shadow-mode evaluations without acting as an operational authority.

## Phase 2 implementation ordering

The implementation should proceed in this order:

1. observation semantics and provenance;
2. telemetry and configuration hashing;
3. trajectory-state objects and invariants;
4. authority decision record and enforcement boundary;
5. shadow-mode evaluation harness.

This order preserves the evidence-first architecture and reduces the risk of misinterpreting trajectory signals as authority decisions before the necessary audit structure exists.

## Evidence gates

Phase 2 should not move past a workstream until the workstream satisfies its evidence gate:

- source-grounded specification is recorded;
- the record is reviewable and reproducible;
- the design boundary is explicit about what is not yet validated;
- no code path silently converts missing evidence into a value;
- no decision path bypasses the authority audit boundary.

## Exit criteria for Phase 2

Phase 2 is complete only when all of the following are true:

- explicit observation states exist and are enforced;
- provenance and artifact hashing are part of the core record;
- trajectory viability and action authorization are documented as separate quantities;
- authority decisions and fallback records are independently auditable;
- the system remains shadow-mode-first and does not claim general safety or production readiness.

Phase 2 is therefore a disciplined prerequisite for later experimentation and any future controlled authority intervention work.
