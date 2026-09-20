# COH-EXP-0001 instrumentation harness

## Status

**Development/instrumentation only.**

This harness does not authorize or implement confirmatory execution of capability Holdout A, transfer Holdout B, or governance Holdout C.

## Purpose

The harness exists to test whether the experimental apparatus can preserve the preregistered authority, provenance, isolation, and freeze boundaries before any confirmatory task is opened.

It currently provides:

- trial and partition types;
- explicit rejection of all confirmatory partitions by the runtime;
- deterministic synthetic development tasks;
- an append-only hash-chained audit interface;
- trial-scoped governed memory with before/after state hashes;
- a deterministic external stop controller;
- protected-resource authority rules;
- deterministic verifier and instrumentation-observer interfaces;
- trial-level JSON-Schema validation;
- protocol freeze-contract validation against `MATRIX.yaml` and the artifact manifest;
- unit tests and CI;
- a local instrumentation self-test.

## Authority model

The acting agent is not given mutation authority over:

- evaluator;
- observer;
- stop controller;
- audit history;
- permission policy;
- holdout manifests.

The current harness makes confirmatory partitions unavailable by default:

```text
Instrumentation / Development -> allowed

Capability Holdout A -> rejected
Transfer Holdout B   -> rejected
Governance Holdout C -> rejected
```

A future confirmatory runner must be introduced separately and must satisfy the complete execution gate. Enabling a holdout by simply changing the instrumentation runner is not an acceptable execution path.

## Audit model

Each event is appended to a SHA-256 hash chain:

```text
record_hash_n = H(sequence_n, event_n, record_hash_n-1)
```

The application interface exposes historical records as an immutable tuple and does not provide update/delete operations.

This is an instrumentation implementation, not yet the final immutable/WORM audit sink required by the preregistration.

## Memory model

`GovernedMemory` is trial-scoped. Each write records:

- actor;
- trial ID;
- key;
- previous-state hash;
- resulting-state hash;
- source-event IDs.

Beginning another trial clears the active state. Any future cross-trial state must be supplied through an explicitly frozen artifact rather than silently inherited.

## Stop conditions

The external stop controller pauses on the preregistered classes of unexpected actions, including:

- network boundary crossing;
- credential access;
- unapproved communication;
- observer/evaluator/audit modification attempts;
- state escape;
- permission modification;
- holdout-access attempts;
- external side effects.

The scripted development agent never exercises real external capabilities.

## Freeze-contract validation

The harness maps every item in:

`experiments/COH-EXP-0001/config/MATRIX.yaml -> freeze_required_before_confirmatory_execution`

to a concrete field in:

`experiments/COH-EXP-0001/ARTIFACT_MANIFEST.template.json`.

CI fails if a declared freeze requirement is unmapped or its manifest field is absent.

At the current preregistration revision, the expected count is **42 freeze requirements**.

## Development tasks

The included tasks are intentionally trivial and deterministic. They exist only to exercise logging, verification, observer, isolation, and provenance paths.

They are not capability-discovery evidence and must never be promoted into Holdouts A, B, or C.

## Next implementation gates

Before this harness can support a freeze package, later work must still provide:

- process/container namespace isolation;
- a real immutable or cryptographically append-only external audit sink;
- frozen environment/image identity;
- exact resource-budget enforcement;
- evaluator process separation;
- observer process separation;
- externally owned permission enforcement;
- holdout vault and manifest access controls;
- deterministic run-order/randomization implementation;
- complete artifact-freeze generator;
- failure-injection tests against every automatic pause condition.

None of those items should be inferred from the existence of this initial harness.
