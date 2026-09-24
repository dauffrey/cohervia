# Trajectory-state contract

Status: proposed interface, pending review. Phase 2 does not compute state estimates.
See inventory INV-09 through INV-14 for CGS lineage.
The following is a Cohervia interface, not a claim of validated estimators.

## T1 — Candidate components and meanings

| Component | Meaning | Required interpretation |
| --- | --- | --- |
| H_t | Accumulated trajectory hazard | Not automatically a calibrated failure probability |
| M_state_t | State viability margin | Foundation M_t shorthand; not action authorization |
| dM_state/dt | State-margin velocity | Derived only from compatible state margins |
| U_t | Uncertainty/evidence-quality information | May be structured; not CGS's uncertainty_mismatch sensor |

CGS's observable U_t and Cohervia's proposed U_t have different meanings.
An adapter must use explicit names such as cgs.uncertainty_mismatch.
No implicit conversion between them is allowed.
No component is assumed to be scalar, normalized to [0,1], or independent of other components.
High viability does not establish safety, alignment, or permission.

## T2 — Versioned snapshot

Required fields: schema_version=trajectory/0.1, snapshot_id, run_id, trajectory_id,
subject_id, sequence, event_cutoff, availability_cutoff, created_at, config reference
(id and sha256), and components. Identity and timestamp conventions follow O1.

Components contains all four named entries, even when unavailable.
Each entry has definition_id/version, estimator_id/version, estimator_mode, value_type,
value, status, reason, units, scale, risk_orientation, uncertainty,
input_observation_ids and config reference. Status is estimated, unknown, or not_applicable;
unavailable entries have value=null and a reason. Uncertainty can be null but not silently defaulted.
Structured values require a named versioned definition.
Estimator_mode must explicitly distinguish score from likelihood if either is used for H_t;
not_applicable is permitted for other components. It must never be inferred from a numeric value.

A component cannot be published without a definition, estimator identity, and traceable
accepted inputs. Missing evidence must not create a healthy default.

## T3 — Causal boundary

Only observations with event_time <= event_cutoff and available_at <= availability_cutoff
are eligible. Both cutoffs must be <= created_at. A late observation can affect a new
snapshot but cannot retroactively improve an earlier warning.
Future disturbance, future observations, final class, tau_escape, and outcome labels
must not enter online inputs or hidden derived features.
Record the entire input-ID set and derivation version; truncated provenance is invalid.
Combining correlated sensors requires a declared dependence treatment; a normalized
hazard presentation index must not be counted as independent evidence.

## T4 — Velocity and deferred mathematics

Velocity requires two available margins from the same identity, definition, estimator,
configuration, units and scale. Declare both snapshot IDs, interval value, and interval
unit (seconds or steps). Interval must be positive and finite.
Insufficient history or incompatible margins yields unknown/null with a reason.
Changing an estimator or configuration starts a new compatible history segment.

CGS functions likelihood_hazard, score_hazard, state_margin, action_margin and
linear_time_to_boundary are predecessor research examples, not selected Cohervia formulas.
Their implementation is deferred. In particular, this contract requires no boundary-time
diagnostic, so the previous conflicting zero/infinity rules are removed rather than
turned into a new Cohervia policy. Any future diagnostic needs its own versioned definition
with mutually exclusive edge cases and an explicit representation of unbounded time.

Action margin, if studied later, belongs to an action-bound recommendation and is not
a fifth state component. No permission follows directly from a snapshot.

## T5 — Offline outcomes

Outcome records live in a separate evaluator namespace/store inaccessible to online estimators.
Required future fields: outcome_schema_version, outcome_id, run_id, trajectory_id,
subject_id, endpoint_definition_id/version, occurred, event_time (null if censored),
censoring_reason, evidence_refs and evaluator_id/version.
Outcome definitions must be prespecified and externally auditable, independent of predictor
scores or alerts. The definition cannot be changed by an intervention; an intervention may
causally affect the realized outcome in a later intervention experiment.

After execution, an evaluator joins immutable snapshots and outcomes by run/trajectory/subject
under a frozen evaluation plan. It never feeds joined labels back into the online record store.
Development data stay development data; known predecessor outcomes are not fresh holdouts.
Phase 2 implements neither outcome evaluation nor this estimator interface.
