# From verified mechanisms to governance: prospective incremental-value protocol

**Status:** research proposal only. No mechanistic signals ingested, no governor built or enabled, no oversight effectiveness demonstrated. Builds on [scalable oversight and interpretability](SCALABLE_OVERSIGHT_AND_INTERPRETABILITY_PROGRAM.md).

## Source and scientific boundary

Nick Cammarata's 2026 working hypothesis, *Neural Networks Are Already Clean* (https://already-clean.goodfire.com/), motivates directly inspecting neurons and circuits, including their downstream effects, rather than treating plausible descriptions or reconstructed features as direct proof. The essay does **not** show that interpretable neurons suffice for governance or safety; the governance hypotheses below are **our own**, to be tested.

EFGM's proposed [native mechanism research](https://github.com/dauffrey/efgm/blob/research/causal-explanation-evidence-gate-20261012/research/NATIVE_MECHANISM_PREDICTION_PROTOCOL.md) asks whether a *causally validated* mechanism and a separately measured EFGM score can predict specified intervention outcomes on unseen inputs. Cohervia must not import either claim as true merely because it exists in EFGM or contains impressive metrics.

## Three independently gated comparisons

**A — Evidence admission (no monitoring claims).** On offline, non-sensitive, permitted public data, obtain records from a trusted independent evaluator/custodian. Verify source authenticity, model/protocol/dataset identifiers, evidence byte digests, pre-outcome prediction commitments, outcome timestamps and declared missingness. Do not convert self-reported statuses such as `observed` into authenticated results. Reproducible core acceptance means integrity of records, not truth.

**B — Shadow warning incremental value.** For a preregistered, bounded test environment, compare independent warning methods at matched alert budgets:

- simple deterministic invariant checklist and behavioral-only warnings;
- frozen native mechanistic evidence without EFGM metrics;
- frozen EFGM-only observations without mechanistic features;
- native + EFGM together;
- randomized/permuted information controls.

Use prospective `available_at` values: no post-action outputs, future interventions, sealed labels or final outcomes available to the predictor. Measure miss rate, false-positive rate, lead time, alert calibration, distribution shift, cost and abstention with missing evidence. Predeclare failure and confidence bounds. Require *incremental* gain over best simple baseline, not just superior training fit.

**C — Authority isolation (separate from prediction).** Only in an explicitly approved isolated sandbox, test that an external deterministic permission layer respects a frozen action policy regardless of what the agent, mechanistic monitor or model-generated explanation asserts. Verify unauthorized actions are rejected even when warnings are absent or deceptive and when evidence is unavailable. Fallback and allowed operations must be specified independently of model scores. Do **not** let predicted safety become authorization.

## Threat models / failure cases

- Accurate semantic labeling but wrong causal intervention effect.
- Causal effect observed only on development inputs or off-distribution activation perturbations.
- Compensating pathways, sign-dependent gates, important attention pathways not captured by neuron-level maps.
- Shared-failure or collusion between acting model and explanation/monitoring models.
- False `observed` claims, copied evaluator identities, forged hashes, untrusted acquisition adapters.
- Late arrival of evidence, quarantine, partial streams, rate limits, missing internals, changed checkpoints, unavailable networks.
- Apparent gains from target leakage, prompt-template overlap, repeated trajectories or calibration on held-out outcomes.
- High overall predictive performance with rare catastrophic governance failures.

**Critical negative-result criterion:** if mechanism-informed warnings cannot beat checklist/behavior-only baselines on held-out scenarios at equal false-positive rates, the governance increment is **not supported**, even if mechanistic explanations appear coherent.

## Contracts and review gates

The existing Cohervia `core` retains its exact observation schema, frozen inputs, explicit missingness and deterministic replay; the current `shadow_evidence` diagnostic only parses **untrusted** summary claims and does not ingest them. A future EFGM adapter must separately implement authenticity verification and record custody **before** mapping evidence into typed, versioned observations. Every derived signal must include code/protocol identity, source observation references and time-valid availability.

The Scientist remains proposal-only, without experiment execution, holdout, code promotion or permission-changing authority. New experiments require precommitted baselines, independent approval and staged results. No direct model modification, automated governor activation or production permission grant is part of this proposal.

## Stage-exit criteria

1. **Design gate:** independent reviewers accept EFGM estimands, holdout separation and EFGM/Cohervia observation semantics.
2. **Causal gate:** frozen independent intervention outcomes support a model- and task-scoped explanatory claim and report counterexamples.
3. **Predictive gate:** mechanisms plus EFGM metrics beat preregistered baseline warnings in a shadow-only, non-authoritative evaluation.
4. **Control gate:** independently evaluated deterministic external enforcement satisfies explicitly bounded policy properties in an isolated environment.
5. **External replication:** independent teams reproduce a narrowly stated result; nothing above establishes general AI safety.

All stage exits can return FAIL or INCONCLUSIVE and must preserve the negative evidence. `100% solved`, universal model understanding and guaranteed governance are not valid statuses.
