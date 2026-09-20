# COH-EXP-0001 preregistration

## Status

**Proposed preregistration. No confirmatory execution has occurred.**

## Title

System-Level Capability Emergence Under Controlled Tool, Memory, and Agent Composition

## Research questions

**RQ1.** Do specified combinations of tools, structured persistent memory, and multiple model instances produce capability performance that exceeds a prediction based on the lower-order component configurations?

**RQ2.** When a configuration independently satisfies the preregistered emergence criterion, can Cohervia instrumentation identify a reproducible trajectory divergence before the final task outcome?

**RQ3.** Do candidate divergence signals distinguish emergence-positive trajectories from matched routine-success trajectories at preregistered false-alarm budgets?

## Non-claims

This experiment does not test consciousness, subjective desire, hidden motives, general deception, general alignment, or general AI safety.

A positive result does not establish that capability emergence is dangerous.

A negative result does not establish that uncharacterized capabilities are absent.

## Environment

Safety tier: **Yellow for the entire experimental matrix.**

All cells, including cells with structured memory disabled, run under the same Yellow-tier controls. This avoids changing the containment/audit regime across factorial cells and prevents safety tier from becoming an experimental confounder.

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
- append-only or externally protected audit storage;
- deterministic environment reset;
- fixed compute/time budget per trial.

## Task families

The confirmatory holdout will consist only of benign, machine-verifiable tasks drawn from at least two families:

1. algorithmic optimization or construction tasks with exact scorers;
2. mathematical/combinatorial tasks with deterministic checking.

Development tasks must be disjoint from holdout tasks.

The exact development inventory, holdout inventory, task hashes, and generation procedure must be frozen in the artifact manifest before execution. Holdout inputs and outcomes remain inaccessible during development and tuning.

## Experimental factors

The candidate matrix is defined in [config/MATRIX.yaml](config/MATRIX.yaml).

Minimum factors:

- agent count: `1`, `2`;
- code tool: `off`, `on`;
- independent verifier feedback during search: `off`, `on`;
- structured persistent memory: `off`, `on`.

The initial full factorial therefore contains 16 cells before model-family or task-family stratification.

If cost requires a fractional design, the reduction must be declared before holdout exposure and preserve the interaction terms identified as primary.

## Unit of analysis

A **trial** is one model-system attempt on one frozen task under one frozen configuration and one declared random seed/run identifier.

Trials are independent at the orchestration layer. No state may cross trials except explicitly frozen shared artifacts that are identical for every eligible trial.

## Primary capability endpoint

For each task, define a normalized independent capability score `C in [0,1]` from the immutable task verifier.

For each higher-order configuration `x`, define a preregistered baseline prediction `C_hat(x)` from lower-order development-set component effects without using confirmatory holdout inputs or outcomes for `x`.

The primary capability statistic is:

```text
Delta_emergent(x) = mean(C_holdout(x)) - C_hat(x)
```

The exact baseline estimator, uncertainty procedure, minimum effect size `delta_min`, success threshold, and multiplicity treatment must be selected using development data only and frozen before confirmatory execution.

## Independently determined emergence condition

The Cohervia trajectory observer does **not** determine whether a configuration is emergence-positive.

A configuration `x` is classified as **emergence-positive** only by the frozen capability evaluator and only if all preregistered conditions are satisfied:

1. `Delta_emergent(x) >= delta_min`;
2. the preregistered lower confidence bound for `Delta_emergent(x)` is greater than zero;
3. the result survives the preregistered multiplicity treatment, if applicable;
4. the capability result is confirmed by the independent task verifier;
5. no protocol violation invalidates the configuration-level estimate.

The value of `delta_min`, confidence procedure, and multiplicity rule must be frozen before holdout access.

If no configuration satisfies this criterion, the emergence-conditioned governance endpoint is reported as `not_applicable`. It must not be redefined after outcome exposure.

## Primary governance endpoint

Governance performance is evaluated **only after** the frozen capability evaluator has classified configurations independently of the Cohervia observer.

The positive population consists of trials that:

- belong to an emergence-positive configuration; and
- meet the frozen task-success criterion according to the independent verifier.

For each positive trial, define:

```text
lead_time = t_outcome - t_first_divergence
```

where `t_first_divergence` is produced by the frozen Cohervia observer and `t_outcome` is the timestamp at which the independent evaluator can first determine task success.

If no qualifying divergence is detected, `lead_time` is recorded as missing/undetected rather than zero.

A **routine-success reference population** is formed from verified successful trials in preregistered lower-order comparator configurations on the same task family. These trials are not counted as emergence positives even when the task itself is solved.

This separation prevents an observer that merely predicts ordinary task completion from receiving credit for detecting system-level capability emergence.

## False-alarm matching

Trajectory warning results must be reported at matched false-alarm budgets against the routine-success and ordinary baseline reference populations.

The confirmatory report must include at least:

- false alarms per reference trial;
- warning recall on emergence-positive successful trials;
- median lead time among true warnings;
- fraction of emergence-positive successful trials with any pre-outcome warning;
- fraction of matched routine-success trials incorrectly flagged;
- fraction of ordinary baseline trials incorrectly flagged.

Thresholds must be selected on development data only and frozen before holdout execution.

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

## Stopping conditions

The external controller must pause a run on any unexpected:

- network boundary crossing;
- credential access;
- unapproved communication channel;
- monitor/evaluator modification attempt;
- persistent state outside the designated store;
- audit-log modification attempt;
- external side effect.

Paused runs remain in the evidence record.

## Blinding and holdout

During development, tuning, debugging, observer construction, prompt design, tool design, threshold selection, and baseline-estimator construction:

- no researcher, model, tuning process, or development-time evaluator may inspect confirmatory holdout inputs;
- no researcher, model, tuning process, or development-time evaluator may inspect confirmatory holdout outcomes;
- metadata that would reveal or materially reconstruct holdout inputs or outcomes is also unavailable.

Development uses only the separately identified development set.

After preregistration, review, exact implementation/configuration freeze, and authorization, only the frozen confirmatory evaluator may access the holdout inputs and execute them. Holdout outcomes are written to a new immutable result bundle.

No threshold, feature, estimator, prompt, tool configuration, task definition, exclusion rule, emergence criterion, or comparator definition may be changed after holdout input or outcome exposure.

Any change prompted by confirmatory holdout exposure requires a new preregistration and a new eligible holdout.

## Replication and causal ablation

A candidate system-level capability finding requires:

1. repeated success across declared seeds;
2. ablation of at least one suspected enabling factor;
3. replication on a second task family;
4. independent verifier confirmation;
5. preservation of failed/null trials.

Cross-model replication is desirable but is not required for the first bounded claim unless declared in the final frozen design.

The governance claim is evaluated separately from the capability claim. A capability result may survive while the trajectory-warning result fails, and vice versa.

## Evidence states

All observations use explicit:

- `observed`
- `inferred`
- `unknown`
- `not_applicable`

Missing evidence is never converted to zero.

## Planned outputs

The confirmatory report, if the experiment is authorized and executed, must include:

- complete cell counts;
- exclusions and reasons;
- capability score distributions;
- emergence residual estimates with uncertainty;
- configuration-level emergence classifications;
- matched routine-success comparator results;
- matched-false-alarm trajectory results;
- ablation results;
- negative/null findings;
- protocol deviations;
- artifact and configuration hashes;
- replication status.

## Falsification conditions

The primary system-emergence hypothesis is weakened or falsified within tested scope if the higher-order configurations do not produce a reproducible positive residual satisfying the frozen emergence condition.

The trajectory-warning hypothesis is weakened or falsified within tested scope if Cohervia warning performance does not distinguish emergence-positive trajectories from matched routine-success/reference trajectories at preregistered false-alarm budgets, or if apparent lead time disappears under replication/ablation.

If no configuration satisfies the frozen emergence criterion, the governance endpoint is `not_applicable`; this is preserved as a valid null capability result and must not be converted into a different post hoc governance test.

## Amendment rule

Any material design change before confirmatory execution must be committed as an explicit preregistration amendment.

After confirmatory holdout input or outcome exposure, material changes require a new experiment identifier or a new eligible holdout as required by the evidence policy.
