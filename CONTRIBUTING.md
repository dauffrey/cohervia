# Contributing

Cohervia is a research project, not a production assurance product. Contributions must preserve scientific discipline, provenance, and conservative interpretation.

## Scientific standards

- Preserve immutable experiment history. Predecessor experiment identifiers and outcomes remain part of the historical record and must not be overwritten or renamed.
- Review before execution. Evidence-producing experiments must be reviewed before they run.
- Maintain exact provenance. Every claim must identify the relevant predecessor lineage or new Cohervia evidence source.
- Preserve negative, null, and falsified results. These are part of the evidence record.
- Use conservative claims. If the evidence does not support a stronger statement, state the limitation explicitly.
- Distinguish synthetic evidence from real-agent evidence.

## Implementation expectations

- Changes to implementations, configurations, evaluators, or data pipelines must include tests or documentation validation, as appropriate.
- Keep development artifacts separated from holdout inputs and outcomes until preregistration, freeze, and evaluator authorization; after authorization, only the frozen evaluator may access the holdout for confirmatory execution.
- Do not silently convert missing evidence into zero or default values.
- Do not hide uncertainty and evidence quality behind a single score.

## Pull requests

Each pull request should state:

- what is being proposed;
- what evidence it depends on;
- what remains uncertain or unvalidated; and
- how the change preserves scientific provenance and research discipline.

Conservative, traceable contributions are preferred over broad claims or premature validation statements.
