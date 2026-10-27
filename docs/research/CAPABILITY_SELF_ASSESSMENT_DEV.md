# Capability self-assessment — bounded development proposal

**Status:** proposal only; not preregistered, not executed, not scientific evidence.  
**Scope:** public development pilot extension. This does not alter COH-EXP-0001, Scientist authority, governor enforcement, or any sealed holdout.

## Research question
Can a model's explicit pre-task estimate of success become better calibrated after feedback from independently scored, unfamiliar public development tasks? Does calibration improvement correspond to any measurable task-performance improvement, or only improved self-report?

## Separations
1. **Prediction:** record a bounded, structured probability of success before the task answer is generated. Preserve prompt, model ID, sampling settings, timestamps, response IDs, and hashes.
2. **Attempt:** use an independent model request without access to the prediction rationale, answer key, evaluator, or prior hidden outcomes. For feedback conditions, supply only the preregistered permitted public feedback.
3. **Verification:** deterministic task-specific checker, separately versioned and frozen before attempts. A failed/incomplete response is distinguished from an incorrect complete answer.
4. **Analysis:** compare predicted probability to observed correctness, and performance against matched controls; preserve all failures and missingness.

## Minimum development design
- First run existing offline pilot self-test and replay, and verify archive consistency. Its scripted results are **instrumentation**, never model performance.
- Next, with separate user authorization for any paid API calls, run the existing three-task public live pilot unchanged as a smoke test. Its tasks are too easy and public to establish generalization.
- Add a *separate* development task catalog of safe, automatically verifiable tasks of graded difficulty, with public answer keys stored outside model prompts. No confirmatory holdout reuse.
- Randomize task order and assign matched conditions: no feedback, outcome-only feedback, and explanation feedback. Keep token/time budget and model settings comparable.
- Measure calibration with Brier score and calibration curves, plus task accuracy, abstention/missingness, latency, and token usage. Report uncertainty intervals and per-task-family results. Explicitly test whether improvement is calibration-only.
- Include sham or irrelevant feedback controls where ethically and methodologically appropriate, and check prompt/answer contamination.
- Use externally held-out evaluation only after a separately approved preregistration and freeze. No claim of emergent capability from development scores.

## Governance and stop conditions
- Text-only, fixed low-risk tasks; no credentials in prompts, no network/tool access for the acting model, no physical actions, no production infrastructure.
- Independent controller owns task selection, answer keys, scoring, stop rules, and cost ceilings.
- Fail closed on missing provenance, unauthorized execution, budget exceedance, evaluator mismatch, or unexpected model/tool behavior.
- Preserve EFGM/CGS/Cohervia scientific lineages and existing frozen baselines; any EFGM metric is diagnostic rather than ground truth.
- Do not let Scientist propose, execute, score, and promote the same confirmatory result.

## Implementation checkpoints
1. **Instrumentation verified:** existing offline tests and replay pass in an execution environment; capture commit SHA and logs.
2. **Schema reviewed:** prediction/attempt/verdict link through immutable IDs; missing and incomplete observations explicit.
3. **Local fabricated test suite:** prove mismatched IDs, altered hashes, leaked answer keys, and missing predictions fail validation.
4. **Public development live run:** only after model/credential/cost authorization, with independently replayable report.
5. **Scientific design review:** independent evaluation, comparator selection, freeze and holdout custody before any COH-EXP-0001 modification or confirmatory experiment.

## Non-claims
This proposal does not establish model introspection, consciousness, weight updates, spontaneous curiosity, emergent capabilities, improved governance, or successful experimental execution.
