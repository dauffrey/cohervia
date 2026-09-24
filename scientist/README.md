# Cohervia Scientist

Cohervia Scientist is an experimental autonomous-research scaffold for Cohervia.

Its purpose is not to prove Cohervia correct. Its purpose is to identify important open questions, generate falsifiable hypotheses, design and execute bounded exploratory work, preserve mistakes and negative results, and propose evidence-backed revisions to Cohervia's scientific core.

> Scientific status: foundation only. This scaffold is not an autonomous validated scientist, does not establish Cohervia performance, and does not authorize confirmatory evidence production by itself.

## Design principle

The scientist may challenge and revise Cohervia's scientific theory, constructs, models, simulations, and candidate mechanisms.

The scientist may not rewrite the rules that determine whether its research is trustworthy.

## v0.1 scope

This initial version establishes:

- a scientific constitution;
- explicit research phases and promotion gates;
- durable ledgers for predictions, anomalies, and failures;
- a versioned theory graph;
- a research-cycle state machine;
- a CLI for recording and inspecting scientific memory;
- tests for the key invariants.

It intentionally does **not** yet include:

- an LLM/model provider;
- arbitrary network access;
- unrestricted code execution;
- autonomous GitHub merge authority;
- confirmatory holdout access;
- permission to rewrite its own constitution.

## Local use

```bash
cd scientist
python -m pip install -e .
cohervia-scientist status
```

Run tests:

```bash
cd scientist
python -m unittest discover -s tests -v
```

## Planned progression

1. Foundation and invariants.
2. Repository-aware research memory.
3. Model-provider abstraction.
4. Hypothesis generation and scientific criticism.
5. Sandboxed exploratory experiment execution.
6. Preregistration and freeze artifacts.
7. Independent confirmatory evaluator.
8. Theory-promotion proposals and regression suites.
9. Continuous research orchestration.

No later phase may bypass the scientific constitution or Cohervia's existing evidence policy.
