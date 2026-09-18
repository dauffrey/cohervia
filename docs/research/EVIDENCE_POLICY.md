# Evidence policy

Cohervia is a falsification-driven research project. The policy below defines the minimum standards for evidence, preregistration, and conservative interpretation.

## Core rules

1. Preregister before confirmatory execution.
   - A study must have a merged preregistration before confirmatory execution begins.
   - The preregistration must define the measurement, evaluation plan, holdouts, and stopping conditions in advance.

2. Freeze the implementation, configurations, thresholds, inputs, and evaluator identity.
   - The implementation, parameters, and test harness must be fixed before confirmatory evaluation starts.
   - Any later change to data, evaluator, or configuration must be treated as a new study unless explicitly re-preregistered.

3. Keep development data separate from holdout data during development and tuning.
   - Development or tuning data must not be mixed with holdout inputs or outcomes.
   - Holdout inputs and outcomes remain inaccessible during observer construction, implementation development, training, threshold selection, tuning, debugging, and structural validation.
   - After preregistration, review, exact implementation/configuration freeze, and authorization, only the frozen evaluator may access the holdout for confirmatory execution.
   - Holdout outcomes may not be used for post-outcome retuning.
   - Changes prompted by confirmatory outcomes require a new preregistration and a new eligible holdout.

4. Preserve negative, null, weakening, and falsified results.
   - Weak or failed results are part of the evidence record and cannot be discarded simply because they are inconvenient.
   - Falsification is a valid scientific result, not a failure of method.

5. Define endpoints independently of candidate sensors.
   - Evaluation endpoints are defined before confirmatory evaluation begins.
   - Endpoints must be externally auditable and based on the task contract, environment state, or another independent outcome source.
   - Endpoints must not depend on candidate sensor values, candidate alerts or predictions, warning thresholds, governor decisions, or interventions.
   - Endpoints must not be altered after outcome exposure.
   - This is a requirement of independence from the candidate predictor, not a prohibition against using independently defined operational measurements in the outcome definition.

6. Compare at matched false-alarm budgets when evaluating early warning.
   - Early-warning evaluation must be matched to false-alarm budgets to avoid over-optimistic interpretation.

7. Prohibit label leakage and post-outcome retuning.
   - No labels, thresholds, or evaluation rules may be altered based on the outcome of confirmatory testing.

8. Distinguish instrumentation tests from evidentiary experiments.
   - Instrumentation evidence establishes that a pipeline, control, detector, evaluator, or recording mechanism operates as intended; it does not establish predictive or governance value.
   - Exploratory evidence may provide bounded, hypothesis-generating evidence but must be labeled exploratory and cannot be presented as confirmatory support.
   - Confirmatory evidence requires preregistration, frozen implementation and evaluation rules, untouched holdout outcomes during development, and execution by the frozen evaluator; it may support only the claims defined in the preregistration.

9. Record commit hashes, configuration hashes, data hashes, and artifact hashes.
   - Every experimental record must capture the implementation version and relevant artifacts used for the evaluation.

10. Use explicit `observed`, `inferred`, `unknown`, and `not_applicable` states.
    - Missing or partially observed data must remain explicit and not be normalized into a misleading zero or default value.

11. Never silently convert missing evidence to zero.
    - Missing evidence is not the same as evidence of no effect.

12. Do not generalize synthetic results to real autonomous agents without new evidence.
    - Synthetic success is a bounded result, not a statement about real-world autonomous behavior.

## Measurement and provenance rules

- Each observation must carry provenance and applicability state.
- Each inference must be traceable to a measurement basis and assumptions.
- State values must remain explicit about uncertainty and the scope of evidence.
- Missing evidence must be documented as missing, not imputed silently.

## Consequence

A result only becomes a basis for a stronger claim once it is associated with the correct evidence record, frozen implementation, and preregistration. Until then, it remains a candidate finding, not an established scientific conclusion.
