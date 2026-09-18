# Authority and audit contract

This document defines the Phase 1 boundary between trajectory-state estimation and authority governance. The purpose is to separate the governor signal from the authority boundary, while preserving a complete audit record for any final decision.

## Source lineage

The authority/audit contract is derived from the CGS architecture specification and the Cohervia foundation constraints:

- CGS repository: `https://github.com/dauffrey/CGS`
- commit: `96c15ce00221879ae613ec907e69206a5037d915`
- relevant specification: `docs/specs/CG-0.2.md`

The design also respects the evidential caution in the Cohervia foundation materials: a governance signal is not equivalent to a validated safety guarantee.

## Architectural boundary

The acting agent must not control:

- governor code or model weights;
- decision thresholds;
- telemetry collection;
- authorization enforcement;
- audit-log integrity;
- fallback execution;
- experiment labels.

This separation is a design invariant. A governor that is not independent from the acting agent is not a valid governance instrument under this specification.

## Authorization semantics

Cohervia preserves the distinction between:

- state viability: how healthy the current trajectory remains;
- action authorization: whether the next action is sufficiently assured under consequences and constraints;
- observed failure: a realized event;
- predicted future failure: a forecast probabilistic quantity.

The decision function is therefore specified as:

```text
D_t = G(
  H_t,
  M_state_t,
  dM_state_t,
  M_action_t(a_t),
  r(a_t),
  Gamma,
  monitor_integrity
)
```

with output space:

```text
PERMIT | VERIFY | RESTRICT | REPLAN | REVERT | HALT
```

A hard-invariant violation bypasses probabilistic reasoning and triggers a deterministic denial and the configured containment response.

## Immutable task contract

The authority layer operates against the immutable task contract:

```text
Gamma = (G0, K0, P0, R0)
```

where:

- `G0` is the authorized objective;
- `K0` is the explicit constraints;
- `P0` is the granted permissions;
- `R0` is the accepted risk envelope.

A strategy may change without changing `Gamma`. A material change to objective, permissions, or risk envelope requires an external authorization event that is separately logged.

## Required audit record

Any decision record must preserve the full chain from signal to consequence. The minimal record is:

```text
AuthorityAuditRecord
  event_id: string
  task_id: string
  time_index: integer
  gamma_hash: string
  telemetry_hash: string
  config_hash: string
  z_t: object
  H_t: float | null
  M_state_t: float | null
  dM_state_t: float | null
  M_action_t: float | null
  r_a_t: float | null
  decision: enum
  decision_reason: string
  monitor_integrity: boolean
  fallback_action: string | null
  evidence_refs: list[string]
  authorization_source: string
  recorded_at: datetime
```

At minimum, the audit record must capture:

- the underlying state estimate and decision inputs;
- the deterministic permission boundary in force;
- whether the final action came from a privileged or fallback path;
- the evidence references that support the decision;
- a record of any invariant violation.

## Decision provenance requirements

Every decision must be explainable in terms of:

- the current state estimate;
- the current action under review;
- the immutably defined task contract;
- the monitor integrity condition;
- the final governance output and fallback path.

A governance decision is not valid simply because a model produced a score. The decision must preserve both the signal and the authority boundary that determined the eventual result.

## Reaction-time and fallback boundary

For the Phase 1 contract, the reaction-time condition is documented but not treated as a validated deployment guarantee:

```text
T_reaction = T_detection + T_decision + T_revocation + T_fallback
```

with a safety allowance `T_safety`.

A predictive reversion condition may be considered:

```text
T_boundary_linear <= T_reaction + T_safety
```

This remains a design heuristic for later evaluation. It is not proof that a deployment threshold is safe.

## Hard-invariant principle

Deterministic permission boundaries and control-plane protections outrank any probabilistic governor estimate. If a hard invariant is violated, the system must:

1. deny or restrict the action deterministically;
2. trigger the configured containment or fallback response;
3. record the violation in the audit trail with the applicable evidence path.

## Phase 1 contract boundary

This document intentionally does not specify:

- a final production authorization policy;
- threshold values for allowed action classes;
- a universal safety guarantee;
- a required deployed governance mechanism.

It defines the accountability and audit obligations required before any shadow-mode or intervention implementation can be meaningfully evaluated.
