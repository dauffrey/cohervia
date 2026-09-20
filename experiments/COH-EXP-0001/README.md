# COH-EXP-0001 — System-Level Capability Emergence

## Status

**Preregistration proposed; not executed.**

This directory does not contain confirmatory results and does not establish Cohervia performance.

## Objective

Evaluate, in a low-risk isolated environment, whether combinations of model instances, deterministic tools, structured persistent state, and independent verification produce reproducible capability gains that exceed a preregistered component-based baseline, and whether Cohervia instrumentation can locate trajectory changes associated with those gains.

## Scope

Initial task families are restricted to machine-verifiable mathematics, algorithmic search, and synthetic computational tasks.

The entire factorial matrix runs under **Yellow-tier isolated-agent-sandbox controls**, including configurations where structured memory is disabled, so containment and audit controls remain constant across cells.

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
4. confirmatory holdout inputs and outcomes are inaccessible to development/tuning processes;
5. model/tool/environment identities are frozen and hashed;
6. the independent verifier, baseline estimator, emergence criterion, observer, and thresholds are frozen;
7. stopping conditions are wired to an external controller;
8. the exact configuration and channel-inventory manifests are committed.

Any change after freeze requires an amendment before confirmatory execution. Any material change prompted by confirmatory holdout exposure requires a new eligible holdout or experiment as required by the evidence policy.
