# Trajectory state contract

This document defines the Cohervia Phase 1 contract for trajectory-state estimation. It is a specification document only; it does not implement an executable governor.

## Scope and source lineage

The trajectory-state contract is informed by the CGS research specification and framed by the conservative evidence posture of the Cohervia foundation. The canonical reference is:

- CGS repository: `https://github.com/dauffrey/CGS`
- commit: `96c15ce00221879ae613ec907e69206a5037d915`
- relevant specification: `docs/specs/CG-0.2.md`

In addition, the coupled disturbance/reserve mechanism from the EFGM Artificial Homeostasis lineage is treated as a bounded design motif, not a universal law.

## Core design principle

Trajectory state must remain a description of viability dynamics, not an implicit authorization decision.

The same system may exhibit:

- low viability;
- high urgency;
- low action authorization margin; or
- a strong future warning signal,

without implying that any specific authority action is justified by the state estimate alone.

## Operational definitions

### Task contract

The immutable task contract is:

```text
Gamma = (G0, K0, P0, R0)
```

where:

- `G0` is the authorized objective;
- `K0` is the explicit constraints set;
- `P0` is the granted permissions;
- `R0` is the accepted risk envelope.

Any material change to objective, permissions, or risk envelope requires an external authorization event that is separately logged.

### Sensor vector

The observable sensor vector for trajectory-state estimation is:

```text
z_t = [G_t, P_t, B_t, R_t, X_t, U_t, I_t]
```

where:

- `G_t`: goal-action divergence;
- `P_t`: persistence despite low progress;
- `B_t`: boundary pressure;
- `R_t`: reward/proxy divergence;
- `X_t`: unauthorized coordination;
- `U_t`: observable uncertainty mismatch;
- `I_t`: optional internal or process anomaly.

`U_t` must not require privileged hidden reasoning. A valid estimator may use monitor disagreement, instability, evidence insufficiency, calibration error, or any externally measurable mismatch between expressed confidence and outcome quality.

### Hazard accumulation

The hazard signal is accumulated degradation evidence:

```text
H_t = max(0, H_(t-1) + ell_t)
```

in likelihood mode, or

```text
H_t = max(0, H_(t-1) + S_t - kappa)
```

in score mode.

Important rules:

- likelihood mode and score mode must remain distinguishable in code and reporting;
- `C_index_t = exp(-H_t / lambda_H)` is only a presentation transform and not an independent evidence source;
- the hazard signal is not itself an authorization decision.

## State viability

State viability is defined as the remaining reserve in the current trajectory relative to a frozen reference definition.

```text
V_L(T_t, a_t, pi) = P^pi[z_(t+tau) in K_Gamma for every tau = 1..L | T_t, a_t]
```

A lower confidence bound may be used:

```text
V_lower = LCB_(1-alpha)[V_L]
```

The resulting state viability margin is:

```text
M_state_t = V_lower_L(T_t, pi_ref) - theta_0
```

where:

- `pi_ref` is a frozen reference continuation policy;
- `theta_0` is the reference requirement threshold;
- the choice of reference policy and evaluation routine must be fixed before confirmatory evaluation.

The critical design distinction is that state viability answers a question about the current trajectory reserve, not about whether a given action should be authorized.

## State-margin velocity

The state-margin velocity is computed only from the state viability margin:

```text
dM_state_t = (M_state_t - M_state_(t-k)) / Delta t
```

Rules:

- a negative velocity means the viability reserve is declining under the frozen reference definition;
- a negative velocity is not created solely by assigning a higher consequence classification to the current action;
- state margin velocity is not an authorization metric.

## Action authorization margin

Action authorization is separate from state viability:

```text
M_action_t(a_t) = V_lower_L(T_t, a_t, pi_follow) - theta(r(a_t))
```

This quantity answers the question: "is this particular action sufficiently assured under its consequence envelope to be authorized?"

It is therefore a governance input, not a trajectory-state metric.

## Boundary estimate

A local linear boundary estimate may be used as a diagnostic only if the required conditions hold:

```text
T_boundary_linear = M_state_t / max(epsilon, -dM_state_t)
```

only when:

```text
M_state_t > 0 and dM_state_t < 0
```

Additional rules:

- if `M_state_t <= 0`, boundary time is `0`;
- if `dM_state_t >= 0`, the linear estimate is infinite;
- this is not a physical law and must not be treated as a guarantee.

## Required state record

A Cohervia trajectory-state record should include at least the following fields:

```text
TrajectoryState
  task_id: string
  time_index: integer
  gamma_hash: string
  z_t: object
  H_t: float | null
  M_state_t: float | null
  dM_state_t: float | null
  M_action_t: float | null
  V_lower: float | null
  theta_0: float | null
  T_boundary_linear: float | null
  evidence_refs: list[string]
  notes: list[string]
```

The record must also preserve which estimator mode was used:

- likelihood mode;
- score mode; or
- a future explicitly documented alternative.

## Required invariants

The following invariants are mandatory for the Phase 1 specification.

1. The acting agent does not control the source of the state estimate.
2. `M_state_t` and `M_action_t(a_t)` are represented as distinct quantities.
3. `dM_state_t` is derived from `M_state_t` only.
4. `C_index_t` is not counted as a separate feature in any comparison.
5. The evaluation endpoint is independent of the governor signal.
6. Observed anomalies may precede an endpoint but may not define the endpoint label.

## Non-goals for Phase 1

This contract does not define:

- a deployed governor implementation;
- specific threshold values for authorization;
- a validation claim about general safety;
- a universal law of agent stability;
- real-agent deployment or intervention policies.

The contract is simply the minimum specification necessary to reason clearly about trajectory viability and action authorization without conflating them.
