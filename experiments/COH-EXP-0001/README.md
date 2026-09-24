# COH-EXP-0001 — System-Level Capability Emergence

## Status

**Preregistration proposed; not executed.**

This directory does not contain confirmatory results and does not establish Cohervia performance.

## Objective

Evaluate, in a low-risk isolated environment, whether combinations of model instances, deterministic tools, structured persistent state, and independent verification produce reproducible capability gains above a preregistered component-based baseline, whether those gains transfer to a separate unseen task partition, and whether Cohervia can detect associated trajectory changes on a third independent partition.

## Confirmatory structure

The proposed design uses one development partition and three disjoint confirmatory holdouts:

```text
Development
   -> freeze
Capability Holdout A
   -> initial configuration-level emergence classification
Transfer Holdout B
   -> independent capability-transfer confirmation
Governance Holdout C
   -> independent Cohervia warning evaluation
```

Holdout A identifies candidate emergence. Holdout B must independently confirm that the capability gain transfers under the same frozen task-family/comparator design. Only configurations that pass both A and B may enter the primary governance analysis on Holdout C.

The entire factorial matrix runs under **Yellow-tier isolated-agent-sandbox controls**, including configurations where structured memory is disabled, so containment and audit controls remain constant across cells.

No real credentials, public network access, physical actuation, real offensive-security targets, financial execution, biological experimentation, chemical experimentation, or critical infrastructure are permitted.

## Files

- [PREREGISTRATION.md](PREREGISTRATION.md) — proposed confirmatory design
- [config/MATRIX.yaml](config/MATRIX.yaml) — candidate factorial, partition, and freeze structure
- [ARTIFACT_MANIFEST.template.json](ARTIFACT_MANIFEST.template.json) — complete freeze/provenance manifest template
- [../../schemas/capability-emergence-observation.schema.json](../../schemas/capability-emergence-observation.schema.json) — trial-level evidence schema
- [../../schemas/capability-emergence-assessment.schema.json](../../schemas/capability-emergence-assessment.schema.json) — Holdout A configuration-level emergence schema
- [../../schemas/capability-transfer-assessment.schema.json](../../schemas/capability-transfer-assessment.schema.json) — Holdout B capability-transfer schema

## Execution gate

Execution is prohibited until:

1. the preregistration is merged;
2. implementation and all three evaluators are reviewed;
3. development, Holdout A, Holdout B, and Holdout C task sets are mutually disjoint;
4. all confirmatory holdout inputs and outcomes are inaccessible to development/tuning processes;
5. all freeze items in the artifact manifest are populated and hashed;
6. the capability evaluator, transfer evaluator, governance evaluator, verifier, baseline estimator, transfer estimator, emergence criterion, transfer criterion, observer, thresholds, comparator definitions, sham-control definition, A-to-B rule, and B-to-C rule are frozen;
7. compute/time limits and every primary and secondary endpoint definition are frozen and hashed;
8. immutable or cryptographically append-only audit storage is configured;
9. stopping conditions are wired to an external controller;
10. the exact configuration and channel-inventory manifests are committed.

Any material change after Holdout A is opened invalidates the confirmatory sequence and requires new eligible Holdouts A, B, and C.
