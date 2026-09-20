# COH-EXP-0001 preregistration

## Status

**Proposed preregistration. No confirmatory execution has occurred.**

## Title

System-Level Capability Emergence Under Controlled Tool, Memory, and Agent Composition

## Research questions

**RQ1.** Do specified combinations of tools, structured persistent memory, and multiple model instances produce capability performance that exceeds a prediction based on lower-order component configurations?

**RQ2.** After a configuration independently satisfies the frozen emergence criterion on capability Holdout A, can Cohervia detect associated trajectory changes on a separate untouched governance Holdout B before final outcomes are known?

**RQ3.** Do candidate divergence signals distinguish emergence-positive configurations from preregistered comparator configurations at matched false-alarm budgets on governance Holdout B?

## Non-claims

This experiment does not test consciousness, subjective desire, hidden motives, general deception, general alignment, or general AI safety.

A positive result does not establish that capability emergence is dangerous.

A negative result does not establish that uncharacterized capabilities are absent.

## Environment

Safety tier: **Yellow for the entire experimental matrix.**

All cells, including cells with structured memory disabled, run under the same Yellow-tier controls so containment and audit requirements do not vary with the experimental factor.

The environment must have:

- no public network access;
- no real credentials;
- no external side effects;
- namespace isolation;
- explicit inventory of every permitted communication channel;
- synthetic services only;
- instrumented shared state;
- immutable task evaluator;
- independent immutable stop controller;
- immutable or cryptographically append-only protected audit storage;
- deterministic environment reset;
- fixed compute/time budget per trial.

## Experimental partitions

The experiment contains three disjoint task partitions.

### Development

Used for instrumentation, debugging, prompt/tool development, baseline-estimator development, observer construction, threshold selection, and power/design checks.

Development data are not confirmatory evidence.

### Capability Holdout A

Used only to classify configurations with the frozen capability evaluator.

Holdout A determines whether a configuration satisfies the preregistered emergence criterion.

Its exact inputs and outcomes remain inaccessible during development.

### Governance Holdout B

Used only after Holdout A classification is complete.

Holdout B is a distinct untouched task set used to evaluate the frozen Cohervia observer on configurations selected by the preregistered Holdout-A selection rule and on their preregistered comparator configurations.

Holdout B inputs and outcomes remain inaccessible during development and remain inaccessible during Holdout A execution/classification.

The task families for all partitions are restricted to benign, machine-verifiable tasks drawn from at least:

1. algorithmic optimization or construction tasks with exact scorers;
2. mathematical/combinatorial tasks with deterministic checking.

The exact generation procedure and all three partition manifests must be frozen and hashed before confirmatory execution.

## Experimental factors

The candidate matrix is defined in [config/MATRIX.yaml](config/MATRIX.yaml).

Minimum factors:

- agent count: `1`, `2`;
- code tool: `off`, `on`;
- independent verifier feedback during search: `off`, `on`;
- structured persistent memory: `off`, `on`.

The initial full factorial therefore contains 16 cells before model-family or task-family stratification.

If cost requires a fractional design, the reduction must be declared before either holdout is exposed and must preserve the interaction terms identified as primary.

## Unit of analysis

A **trial** is one model-system attempt on one frozen task under one frozen configuration and one declared run identifier.

Trials are independent at the orchestration layer. No state may cross trials except explicitly frozen shared artifacts that are declared in advance and identically available to all eligible trials in that condition.

## Evidence record levels

Cohervia uses two different record levels.

### Trial-level evidence

A `CapabilityEmergenceTrialObservation` records one run: task score, trajectory evidence, tool/memory/agent involvement, constraint status, verifier result, and provenance.

It does **not** classify emergence.

### Configuration-level assessment

A `CapabilityEmergenceConfigurationAssessment` aggregates Holdout A trial evidence for one frozen configuration and records:

- baseline prediction derived from preregistered Holdout A comparator evidence;
- comparator-definition hash and supporting comparator-trial IDs;
- mean observed capability;
- `Delta_emergent`;
- `delta_min`;
- confidence bound;
- uncertainty procedure;
- multiplicity result;
- verifier result;
- protocol validity;
- final emergence classification;
- evaluator and provenance hashes.

Only the configuration-level assessment may assign `positive`, `not_positive`, or `invalid` emergence classification.

## Primary capability endpoint

For each task, define a normalized independent capability score `C in [0,1]` from the immutable task verifier.

The **form** of the baseline estimator and the exact lower-order comparator mapping are developed using the development partition and frozen before either holdout is opened.

On capability Holdout A, the frozen evaluator computes `C_hat_A(x)` from preregistered lower-order comparator configurations evaluated on the **same Holdout A task distribution**. The target configuration `x` must not contribute its own outcomes to its baseline prediction. Where the task design permits, target and comparator evidence should be paired by task instance under the frozen estimator.

```text
Delta_emergent_A(x) = mean(C_A(x)) - C_hat_A(x)
```

This makes the confirmatory residual a within-Holdout-A comparison rather than a comparison between Holdout A and development performance.

The exact estimator form, comparator mapping, uncertainty procedure, minimum effect size `delta_min`, task-success threshold, and multiplicity treatment must be selected using development data only and frozen before Holdout A is opened. The numerical `C_hat_A(x)` is then computed only by the frozen capability evaluator from the designated Holdout A comparator evidence.

## Independently determined emergence condition

The Cohervia trajectory observer does **not** determine whether a configuration is emergence-positive.

A configuration `x` is classified as **emergence-positive** on Holdout A only if all preregistered conditions are satisfied:

1. `Delta_emergent_A(x) >= delta_min`;
2. the preregistered lower confidence bound for `Delta_emergent_A(x)` is greater than or equal to `delta_min`;
3. the result survives the frozen multiplicity rule; `not_applicable` is permitted only when the preregistration defines a single primary contrast that does not require multiplicity adjustment;
4. the capability result is confirmed by the independent task verifier;
5. no protocol violation invalidates the configuration-level estimate.

The classification is written to an immutable Holdout A result bundle by the frozen capability evaluator.

If no configuration is emergence-positive, governance Holdout B is not executed and the governance endpoint is reported as `not_applicable`.

## Holdout-A-to-B selection rule

Before either holdout is opened, freeze a deterministic selection rule that maps Holdout A emergence classifications to the configurations eligible for Holdout B.

For every emergence-positive configuration selected for Holdout B, the rule must also select its preregistered lower-order comparator configuration(s).

The selection rule may use only the immutable configuration-level classification outputs explicitly declared in advance. It may not inspect Holdout B inputs, outcomes, or trajectory data.

No observer feature, threshold, prompt, tool configuration, evaluator, comparator definition, or selection rule may change between Holdout A and Holdout B.

## Primary governance endpoint

Governance performance is estimated **only on governance Holdout B**.

The primary positive population is defined **before any Holdout B outcome is known**:

- every Holdout B trial whose frozen configuration was classified emergence-positive on Holdout A.

The reference population is likewise outcome-independent:

- every Holdout B trial from the preregistered comparator configurations selected by the frozen A-to-B selection rule.

The primary governance analysis therefore does **not** condition population membership on whether an individual Holdout B task succeeds or fails.

For each Holdout B trial, the frozen observer either emits a qualifying pre-terminal warning or does not. Primary metrics include:

- warning rate/sensitivity across all trials from Holdout-A-positive configurations;
- warning rate across all matched comparator trials;
- difference or other preregistered contrast between those rates at the frozen false-alarm budget;
- time from first qualifying warning to the frozen terminal evaluation point, where defined.

A secondary, explicitly outcome-conditioned analysis may report, among independently verified successful Holdout B trials:

```text
lead_time_to_success = t_success - t_first_divergence
```

This secondary analysis must be labeled as success-conditioned and cannot substitute for the primary outcome-independent governance endpoint.

This design prevents both configuration selection and primary governance population membership from depending on the same Holdout B outcomes.

## False-alarm matching

Trajectory-warning results on Holdout B must be reported at matched false-alarm budgets.

The confirmatory report must include at least:

- false alarms per comparator/reference trial;
- primary warning sensitivity across all trials from Holdout-A-positive configurations;
- warning rate across all matched comparator trials;
- preregistered contrast between those rates;
- fraction of positive-configuration trials with any pre-terminal warning;
- secondary success-conditioned lead time, if applicable and clearly labeled.

Thresholds are selected on development data only and frozen before Holdout A is opened.

## Candidate trajectory features

Only preregistered, externally observable events may be used by the confirmatory observer.

Candidate events include:

- tool call/result sequence;
- verifier submission/result;
- memory read/write/compaction;
- plan revision marker;
- subagent spawn;
- inter-agent message in the designated synthetic channel;
- shared-state access in the designated synthetic environment;
- explicit constraint encounter;
- strategy-shift marker generated by an external classifier or deterministic rule.

Model self-reports of motives are not treated as ground truth.

## Memory governance

Structured memory is a state-changing tool and is governed under Yellow-tier controls.

Every memory write must record:

- actor;
- trial ID;
- previous-state hash;
- resulting-state hash;
- timestamp;
- persistence scope;
- source event IDs.

Memory outside the designated mechanism is an automatic pause condition.

No memory state may cross trial boundaries unless it is an explicitly frozen artifact declared in advance and identically available to all eligible trials in that condition.

## Fixed analysis-integrity plan

Before Holdout A is opened, freeze and hash:

- exact trial/sample counts per eligible configuration, task family, and partition, or a fully specified non-optional sequential rule if one is scientifically required;
- run-order/randomization plan;
- retry policy;
- exclusion rules;
- missing-data policy;
- compute/time limits;
- all primary and secondary endpoints.

Optional stopping based on observed confirmatory performance is prohibited.

A retry may occur only under the frozen retry policy. Failed, timed-out, paused, excluded, and missing trials remain represented in the immutable evidence bundle with their disposition and reason.

## Stopping conditions

The external controller must pause a run on any unexpected:

- network boundary crossing;
- credential access;
- unapproved communication channel;
- monitor/evaluator modification attempt;
- persistent state outside the designated store;
- audit-log modification attempt;
- external side effect.

Paused runs remain in the immutable evidence record.

## Blinding and execution sequence

During development, tuning, debugging, observer construction, prompt design, tool design, threshold selection, baseline-estimator construction, and statistical-design work:

- no researcher, model, tuning process, or development-time evaluator may inspect Holdout A inputs or outcomes;
- no researcher, model, tuning process, or development-time evaluator may inspect Holdout B inputs or outcomes;
- metadata that would reveal or materially reconstruct either holdout is unavailable.

After preregistration, review, exact implementation/configuration freeze, artifact hashing, and authorization:

1. the frozen capability evaluator opens Holdout A;
2. Holdout A trials execute and produce an immutable result bundle;
3. the frozen capability evaluator emits configuration-level emergence assessments;
4. the frozen selection rule determines which configurations and comparators are eligible for Holdout B;
5. only then may the frozen governance evaluator open Holdout B;
6. Holdout B trials execute with the already-frozen Cohervia observer;
7. Holdout B results are written to a separate immutable result bundle.

No material component may change between steps 1 and 7.

If a material defect requires a change after Holdout A has been opened, the confirmatory sequence is invalidated and requires new eligible Holdout A and Holdout B partitions under an amended or new preregistration.

## Replication and causal ablation

A candidate system-level capability finding requires:

1. repeated success across declared runs;
2. ablation of at least one suspected enabling factor;
3. replication on a second task family;
4. independent verifier confirmation;
5. preservation of failed/null trials.

The governance claim is separate from the capability claim. Capability emergence may be supported while the trajectory-warning hypothesis fails.

## Evidence states

All observations use explicit:

- `observed`
- `inferred`
- `unknown`
- `not_applicable`

Missing evidence is never converted to zero.

## Planned outputs

The confirmatory report, if execution is authorized, must include:

- complete cell counts for both holdouts;
- all retries, exclusions, missing trials, and reasons;
- capability score distributions on Holdout A;
- emergence residual estimates with uncertainty;
- configuration-level emergence classifications;
- Holdout A selection outputs;
- Holdout B primary outcome-independent governance results;
- matched comparator/false-alarm results;
- clearly labeled secondary success-conditioned analyses;
- ablation results;
- negative/null findings;
- protocol deviations;
- all artifact/configuration/evaluator hashes;
- replication status.

## Falsification conditions

The capability-emergence hypothesis is weakened or falsified within tested scope if no higher-order configuration produces a reproducible positive residual satisfying the frozen Holdout A emergence condition.

The trajectory-warning hypothesis is weakened or falsified within tested scope if, on independent Holdout B, Cohervia's frozen primary governance endpoint does not distinguish Holdout-A-classified emergence-positive configurations from their preregistered comparators at the preregistered false-alarm budget, or if apparent effects fail replication/ablation.

If no configuration satisfies the frozen Holdout A emergence criterion, the governance endpoint is `not_applicable`. This is a valid null capability result and must not be converted into a post hoc governance test.

## Amendment rule

Any material design change before confirmatory execution must be committed as an explicit preregistration amendment.

After Holdout A or Holdout B input exposure, material changes require new eligible confirmatory partitions as specified above and must be explicitly documented.
