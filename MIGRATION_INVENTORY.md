# Migration inventory and adoption boundaries

This document is a source-grounded migration inventory for Cohervia Phase 1. It is intentionally limited to specification work: no implementation code, no runtime migration, no dependency scaffolding, and no production claim.

## Scope and governing rule

Cohervia may adopt, adapt, defer, or exclude predecessor constructs only when the choice is traceable to the pinned predecessor snapshots recorded in [docs/provenance/LINEAGE.md](docs/provenance/LINEAGE.md).

The migration posture is conservative:

- adopt only where the evidence and semantics are clear and in scope;
- adapt only when the predecessor idea is relevant but must be renamed or constrained for Cohervia;
- defer when the idea is useful but not yet implementable under the Phase 1 specification boundary;
- exclude when the predecessor claim is unsupported, mis-scoped, or not compatible with Cohervia's research posture.

The project is still a foundation-only research effort. Nothing in this inventory is evidence that a construct is validated for production use or general-agent safety.

## Source anchors

### EFGM

Repository: `https://github.com/dauffrey/efgm`
Commit: `37b2ff2d2b577c9f383dd0d7c3083597627150ea`
Relevant source: `efgm/schemas_v2.py`

This lineage contributes the observation semantics that Cohervia must preserve as a measurement contract:

- `MetricObservation` as the normalized unit of auditable measurement;
- `ObservationStatus` values: `observed`, `inferred`, `unknown`, `not_applicable`;
- explicit separation of `unknown` and `not_applicable` from a measured value of zero;
- provenance-bearing fields such as `rationale`, `evidence_refs`, `scorer_id`, `scorer_type`, and `confidence`;
- enforcement that missing or inapplicable values are not silently coerced to favorable values.

### EFGM Artificial Homeostasis

Repository: `https://github.com/dauffrey/EFGM-artificial-homeostasis`
Commit: `7d67c01647a2a5305d5bf651ff2eacc8c2834d40`
Relevant source: `README.md` and experiment records

This lineage contributes the strongest bounded synthetic evidence for the mechanism family of:

- disturbance pressure, remaining reserve, and recovery dynamics;
- viability margin as a state-level quantity;
- counterfactual abstention as a response to uncertainty;
- explicit negative results that narrowed the mechanism rather than validating a universal law.

The strongest supported result is also the most constrained one: coupling current disturbance pressure to remaining operational reserve can be useful under controlled synthetic disturbance, but the broader claim of uniform superiority is not valid and intervention governance failed under some conditions.

### Coherence Governor System (CGS)

Repository: `https://github.com/dauffrey/CGS`
Commit: `96c15ce00221879ae613ec907e69206a5037d915`
Relevant source: `docs/specs/CG-0.2.md`

This lineage contributes the architecture and mathematical boundaries for the independent governor:

- the acting agent must not control the governor or its audit plane;
- `Gamma = (G0, K0, P0, R0)` is the immutable task contract;
- `z_t = [G_t, P_t, B_t, R_t, X_t, U_t, I_t]` is the observable sensor vector;
- hazard is accumulated evidence, not a free-floating score;
- `H_t`, `M_state_t`, and `dM_state_t` are not interchangeable with action authorization;
- the evaluation endpoint must be independently defined and not derived from the governor sensor set itself;
- `M_action_t(a_t)` is a separate authorization-margin quantity.

## Inventory table

| Candidate construct | Source | Decision | Evidence posture | Cohervia interpretation |
| --- | --- | --- | --- | --- |
| `MetricObservation` semantics | EFGM `efgm/schemas_v2.py` | Adopt | Explicit and source-grounded | This is the basis for the Cohervia observation contract. |
| Observation statuses (`observed`, `inferred`, `unknown`, `not_applicable`) | EFGM `efgm/schemas_v2.py` | Adopt | Explicit and source-grounded | Missing evidence must remain missing, not be converted to zero. |
| explicit provenance fields (`evidence_refs`, `rationale`, `confidence`, `scorer_id`) | EFGM `efgm/schemas_v2.py` | Adopt | Explicit and source-grounded | Required for any Cohervia measurement record and audit trail. |
| state viability vs action authorization separation | CGS `docs/specs/CG-0.2.md` | Adopt | Architecture-level and source-grounded | This is a core design invariant. |
| `Gamma` and external authorization boundary | CGS `docs/specs/CG-0.2.md` | Adopt | Architecture-level and source-grounded | Cohervia must document task contract and authorization semantics separately from viability prediction. |
| `H_t` accumulation and `C_index_t` as presentation-only transform | CGS `docs/specs/CG-0.2.md` | Adopt | Architecture-level and source-grounded | `C_t` is not an independent evidence stream and must not be counted as extra evidence. |
| state viability margin `M_state_t` | CGS `docs/specs/CG-0.2.md` | Adopt | Architecture-level and source-grounded | Core trajectory-state quantity. |
| state-margin velocity `dM_state_t` | CGS `docs/specs/CG-0.2.md` | Adopt | Architecture-level and source-grounded | Used only for state deterioration velocity, not action authorization. |
| action authorization margin `M_action_t(a_t)` | CGS `docs/specs/CG-0.2.md` | Adopt | Architecture-level and source-grounded | Used only to assess proposed action, not as a state metric. |
| coupled disturbance-to-reserve mechanism | EFGM-AH `README.md` and experiment records | Adapt | Strong bounded synthetic evidence but not universal | Use as a design motif for trajectory-state estimation under uncertainty, not as a universal rule. |
| counterfactual abstention | EFGM-AH `README.md` | Adapt | Synthetic evidence survives holdout under bounded conditions | A useful abstention policy pattern for uncertainty-heavy decisions. |
| broad “uniform superiority” claim | EFGM-AH experiment records | Exclude | Falsified or partially falsified | Must not be inherited as a general performance claim. |
| simplistic over-regulation detectors | EFGM-AH experiment records | Exclude | Falsified | Preserved as failure modes and cautionary examples. |
| real-agent deployment claims | All predecessor sources | Exclude | Not supported by the recorded evidence | Cohervia must not claim production safety or real-agent generalization. |
| threshold tuning as a substitute for evidence | All predecessor sources | Exclude | Not valid under evidence-policy rules | Thresholds remain part of implementation, not proof. |

## Migration decisions by category

### Adopt

These constructs are retained as first-class Cohervia specification concepts because they are explicit, auditable, and logically central to the architecture.

- explicit observation states and value semantics;
- provenance-bearing metric records;
- separation between viability estimates and authority decisions;
- independent governance architecture;
- hazard accumulation and state/action margin separation;
- requirement that failure endpoints be defined independently of the governor signal.

### Adapt

These constructs require reinterpretation to fit Cohervia's conservative evidence posture.

- coupled-margin regulation: useful as a bounded mechanism family but not a validated production control law;
- counterfactual abstention: acceptable as a design principle for uncertainty-aware governance, not as a universal guarantee;
- trajectory-pressure constructs: should be documented as evidence-bearing signals under a bounded research question, not as solved operational quantities.

### Defer

These ideas are relevant but outside the Phase 1 specification boundary.

- full implementation of viability estimation models;
- the first shadow-mode governance harness;
- parameter learning and optimization against real agentic trajectories;
- real and semi-real deployment trials.

### Exclude

These are explicitly not inherited.

- any broad claim that a predecessor signal or regulator is validated by virtue of the lineage alone;
- uniform superiority claims unsupported by the recorded negative results;
- direct operational assumptions, thresholds, or policy defaults from synthetic experiments;
- any unqualified transfer of results from synthetic benchmarks to real systems.

## Compatibility risks

The main incompatibilities are not about syntax; they are about interpretation.

1. EFGM's observation semantics are explicit and evidence-aware, but CGS designs still require a separate authority layer. Cohervia must not collapse these concepts.
2. EFGM-AH's strongest mechanism is bounded and synthetic; it cannot become a general safety rule simply because it survives one holdout.
3. CGS's `M_state_t` and `M_action_t(a_t)` are conceptually distinct. A migration that treats them as the same quantity would invalidate the architecture.
4. Predecessor results were recorded under separate experiment IDs. Cohervia must not rename those records or pretend the evidence is directly Cohervia evidence.

## Phase 1 decision record

This Phase 1 inventory intentionally documents the migration boundary without moving implementation code. The target is a disciplined interface contract and a traceable migration map, not a runtime assembly of controls.

The expected future Phase 2 work will then translate these contracts into the minimal observation-and-audit core, while preserving all of the evidence and provenance constraints already specified in the foundation documentation.
