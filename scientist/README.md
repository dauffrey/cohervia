# Cohervia Scientist

Cohervia Scientist is an experimental autonomous-research system for Cohervia.

Its purpose is not to prove Cohervia correct. Its purpose is to identify important open questions, generate falsifiable hypotheses, challenge them, design bounded exploratory experiments, preserve mistakes and negative results, and propose evidence-backed revisions to Cohervia's scientific core.

> Scientific status: research scaffold. v0.2 adds an LLM-backed scientific reasoning engine, but it is not a validated autonomous scientist, does not establish Cohervia performance, and does not authorize confirmatory evidence production by itself.

## Design principle

The scientist may challenge and revise Cohervia's scientific theory, constructs, models, simulations, and candidate mechanisms.

The scientist may not rewrite the rules that determine whether its research is trustworthy.

## Current capability — v0.2

v0.2 adds a bounded scientific reasoning loop:

1. ingest approved Cohervia repository context;
2. identify or frame one important unresolved research question;
3. retrieve relevant prior failures and anomalies;
4. generate falsifiable hypotheses;
5. subject all hypotheses to an adversarial critic role;
6. select a candidate for exploratory work;
7. design an explicitly exploratory experiment;
8. run a final scientific-integrity review;
9. emit a structured research packet for human review.

The engine deliberately does **not** execute experiment code or access confirmatory holdouts.

## Local use

```bash
cd scientist
python -m pip install -e .
cohervia-scientist status
```

To run the reasoning engine with an OpenAI API key:

```bash
python -m pip install -e ".[openai]"
export OPENAI_API_KEY="..."
cohervia-scientist reason --provider openai --model YOUR_API_MODEL_ID
```

Or supply a specific research question:

```bash
cohervia-scientist reason \
  --provider openai --model YOUR_API_MODEL_ID \
  --question "Does trajectory curvature add useful pre-boundary warning beyond margin slope?"
```

Run on Linux/POSIX with Python 3.11 or newer. Supply an API model identifier available to your account; the package does not infer one from a ChatGPT model name.

Packets are created exclusively under `scientist/runs/`, with unique IDs and no overwrite. An explicit `--output` must also name a new JSON file directly in that directory. Blocked or rejected reasoning is preserved with its disposition; the CLI exits 2 when it does not produce an acceptable candidate. No disposition authorizes execution.

`--memory-limit` accepts 1–20 records and `--hypothesis-count` accepts 2–8. The default counts are 6 and 4. Provider requests have no tools, a 60-second timeout, zero automatic retries, and an 8,000-token output cap. A run makes at most six calls. No API calls occur in the tests.

See [the reasoning engine contract](docs/REASONING_ENGINE.md) for enforced boundaries, provenance, and deployment assumptions.

## Safety and evidence posture

v0.2 has:

- no main-branch write authority;
- no merge authority;
- no arbitrary shell/code execution;
- no confirmatory holdout access;
- no experiment execution;
- no ability to alter its constitution or authority configuration;
- no automatic claim promotion.

Model output is treated as **candidate reasoning**, not evidence.

## Planned progression

1. Foundation and invariants. **Complete in v0.1.**
2. Scientific reasoning engine. **Implemented in v0.2.**
3. Repository-aware research branch/PR workflow.
4. Sandboxed exploratory experiment execution.
5. Preregistration and freeze artifacts.
6. Independent confirmatory evaluator.
7. Theory-promotion proposals and regression suites.
8. Continuous research orchestration.

No later phase may bypass the Scientific Constitution or Cohervia's existing evidence policy.
