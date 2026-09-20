# COH-EXP-0001 — System-Level Capability Emergence

## Status

**Preregistration proposed; not executed.**

This directory does not contain confirmatory results and does not establish Cohervia performance.

## Objective

Evaluate, in a low-risk offline environment, whether combinations of model instances, deterministic tools, structured persistent state, and independent verification produce reproducible capability gains that exceed a preregistered component-based baseline, and whether Cohervia instrumentation can locate trajectory changes associated with those gains.

## Scope

Initial task families are restricted to machine-verifiable mathematics, algorithmic search, and synthetic computational tasks.

No real credentials, public network access, physical actuation, real offensive-security targets, financial execution, biological experimentation, chemical experimentation, or critical infrastructure are permitted.

## Files

- [PREREGISTRATION.md](PREREGISTRATION.md) — proposed confirmatory design
- [config/MATRIX.yaml](config/MATRIX.yaml) — candidate frozen factorial structure
- [ARTIFACT_MANIFEST.template.json](ARTIFACT_MANIFEST.template.json) — provenance manifest template

## Execution gate

Execution is prohibited until:

1. the preregistration is merged;
2. implementation and evaluator are reviewed;
3. development and holdout task sets are separated;
4. model/tool/environment identities are frozen and hashed;
5. the independent verifier is frozen;
6. stopping conditions are wired to an external controller;
7. the exact configuration manifest is committed.

Any change after freeze requires an amendment before confirmatory execution.
