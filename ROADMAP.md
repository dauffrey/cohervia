# Roadmap

The roadmap below is intentionally staged and does not imply completed evidence. Each phase has explicit exit criteria.

## Phase 0: canonical foundation and provenance

Purpose: establish the project identity, lineage record, and scientific guardrails.

Exit criteria:

- canonical project identity and scope are documented;
- predecessor repositories are explicitly cited with pinned commits;
- scientific status warning and evidence policy are recorded;
- no unsupported production or safety claims are made.

## Phase 1: migration inventory and interface contracts

Purpose: inventory candidate constructs and establish migration boundaries without moving implementation code.

Exit criteria:

- each candidate construct is mapped to a predecessor source and evidence status;
- interfaces and observability contracts are recorded;
- migration boundaries are explicit about what is not automatically transferred.

## Phase 2: minimal observation and audit core

Purpose: define the minimal measurement, provenance, and audit layer required for disciplined evidence capture.

Exit criteria:

- explicit observation states are available and documented;
- provenance and artifact hashing are part of the core record;
- audit trails exist for telemetry, configuration, and decisions; 
- missing evidence is retained as missing rather than silently converted.

## Phase 3: shadow-mode governor and baseline evaluation

Purpose: evaluate a governor in shadow mode before any authority intervention.

Exit criteria:

- governance decisions are observable but not controlling;
- baseline false-alarm and warning behavior is evaluated under explicit budgets;
- no authority decisions are made without deterministic safety enforcement outside the governor.

## Phase 4: independently preregistered Cohervia experiment

Purpose: generate new evidence under the `COH-EXP-NNNN` namespace.

Exit criteria:

- a merged preregistration exists before execution;
- frozen implementation, data, and configuration are recorded;
- confirmatory holdouts remained inaccessible during development and tuning and were accessed only by the frozen evaluator after preregistration and implementation freeze;
- results are recorded under the Cohervia lineage, not by renaming predecessor evidence.

## Phase 5: controlled real-agent trials

Purpose: gather evidence for behavior in real autonomous-agent settings, if any such trials are authorized.

Exit criteria:

- evidence is scoped to the tested agents and conditions;
- results do not claim generalization beyond the trial design;
- real-agent findings remain distinguishable from synthetic evidence.

## Phase 6: authority intervention research

Purpose: evaluate graduated intervention logic under controlled, evidence-based conditions.

Exit criteria:

- intervention policy remains separately evaluated from deterministic enforcement;
- graduated outcomes are recorded as research products, not validated safe thresholds;
- the results remain bounded by their preregistered scope and evidence.
