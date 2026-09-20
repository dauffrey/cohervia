# COH-EXP-0001 — System-Level Capability Emergence

## Status

**Preregistration proposed; not executed.**

This directory does not contain confirmatory results and does not establish Cohervia performance.

## Objective

Evaluate, in a low-risk isolated environment, whether combinations of model instances, deterministic tools, structured persistent state, and independent verification produce reproducible capability gains above a preregistered component-based baseline, and whether Cohervia can detect associated trajectory changes on independent evidence.

## Confirmatory structure

The proposed design uses three disjoint partitions:

```text
Development
   -> freeze
Capability Holdout A
   -> configuration-level emergence classification
Frozen A-to-B selection rule
   -> Governance Holdout B
   -> independent Cohervia warning evaluation
```

Holdout A establishes the capability phenomenon. Holdout B evaluates governance. They are not interchangeable.

The entire factorial matrix runs under **Yellow-tier isolated-agent-sandbox controls**, including configurations where structured memory is disabled, so containment and audit controls remain constant across cells.

No real credentials, public network access, physical actuation, real offensive-security targets, financial execution, biological experimentation, chemical experimentation, or critical infrastructure are permitted.

## Files

- [PREREGISTRATION.md](PREREGISTRATION.md) — proposed confirmatory design
- [config/MATRIX.yaml](config/MATRIX.yaml) — candidate factorial and partition structure
- [ARTIFACT_MANIFEST.template.json](ARTIFACT_MANIFEST.template.json) — complete freeze/provenance manifest template
- [../../schemas/capability-emergence-observation.schema.json](../../schemas/capability-emergence-observation.schema.json) — trial-level evidence schema
- [../../schemas/capability-emergence-assessment.schema.json](../../schemas/capability-emergence-assessment.schema.json) — configuration-level emergence schema

## Execution gate

Execution is prohibited until:

1. the preregistration is merged;
2. implementation and both evaluators are reviewed;
3. development, Holdout A, and Holdout B task sets are disjoint;
4. both holdout inputs and outcomes are inaccessible to development/tuning processes;
5. all freeze items in the artifact manifest are populated and hashed;
6. the capability evaluator, governance evaluator, verifier, baseline estimator, emergence criterion, observer, thresholds, comparator definition, and A-to-B selection rule are frozen;
7. immutable or cryptographically append-only audit storage is configured;
8. stopping conditions are wired to an external controller;
9. the exact configuration and channel-inventory manifests are committed.

Any material change after Holdout A is opened invalidates the confirmatory sequence and requires new eligible Holdout A and Holdout B partitions.
