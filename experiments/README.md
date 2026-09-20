# Experiments

Cohervia reserves a new experimental namespace:

`COH-EXP-NNNN`

## Namespace rules

- Predecessor experiment IDs remain unchanged and must never be renamed as Cohervia experiments.
- Cohervia begins a new experimental lineage separate from `EFGM-EXP`, `AH-EXP`, and `CG-EXP` identifiers.
- Known predecessor data cannot become new confirmatory evidence merely by being copied into the Cohervia repository.
- Every Cohervia confirmatory experiment begins with a merged preregistration.
- A `COH-EXP-NNNN` directory may contain a proposed preregistration before execution, but its status must explicitly state that no confirmatory execution has occurred.
- `AH-EXP-0012` remains a predecessor experiment and must not be duplicated, renamed, or contaminated.

## Current Cohervia namespace

- [COH-EXP-0001](COH-EXP-0001/README.md) — **proposed / not executed**; system-level capability emergence under controlled tool, memory, verifier, and agent composition.

## Execution rule

Creating an experiment directory does not authorize execution.

Confirmatory execution requires:

- merged preregistration;
- frozen implementation/configuration/evaluator;
- separated development and holdout data;
- committed artifact/configuration hashes;
- applicable safety controls and stop conditions;
- explicit authorization under the evidence policy.

## Research posture

The project does not treat predecessor experiments as direct evidence of Cohervia performance. Instead, they serve as lineage, methodology, and bounded prior context. New Cohervia evidence must be collected under new preregistration, frozen implementation, and traceable artifact records.
