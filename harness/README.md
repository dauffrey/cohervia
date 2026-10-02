# COH-EXP-0001 development apparatus

Reworked from PR #4 on Scientist v0.2.1 main. This independent package tests apparatus only. It has no Scientist tool/CLI connection, holdout reader, execution unlock, live provider, or evidence-ledger writer.

From the repository root:

```sh
python -m pip install -e ./harness
python -m unittest discover -s harness/tests -v
cohervia-harness --self-test
```

Tests and `--self-test` use two public deterministic scripted fixtures. Even a DEVELOPMENT trial is labeled instrumentation, `scientific_evidence=false`, `execution_authorized=false`. JSON self-test output preserves exact fixture prompts/expected/actual answers, trial configuration and audit-event snapshots. CI retains this output together with commit and source-file hashes.

Assessment schemas and numeric selectors are diagnostic prototypes exercised with fabricated records, not independent evaluators or experimental results. Template freeze checks verify field coverage only; the checked-in manifest is null and not ready for execution.

The runner accepts only the reviewed scripted fixture classes and public task records and rejects all confirmatory partitions before invoking them. Python type checks are not adversarial process containment. Stop/authority classes simulate interfaces; principal strings do not authenticate an owner. Resource-limit fields are design metadata, not enforced CPU/time budgets.

Defensive snapshots protect in-memory audit and memory interfaces from caller alias mutation. Memory writes commit state after successful audit append and record trial persistence scope. Memory is not wired into the scripted agent; no memory-factor effect is tested. The log is not persistent/WORM, does not meet the proposed JCS observation/audit contract, and cannot prove complete historical custody. Do not use this package as a live-agent sandbox.

See [Scientist boundary](../docs/research/SCIENTIST_CAPABILITY_BOUNDARY.md), [reconciliation audit](../docs/implementation/RECONCILIATION.md), and [proposed experiment](../experiments/COH-EXP-0001/README.md). Human review, exact scientific design, independent containment/evaluation and external authority remain mandatory before any future experiment.
