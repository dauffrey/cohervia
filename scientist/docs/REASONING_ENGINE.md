# Scientific reasoning engine

## Purpose

v0.2 gives Cohervia Scientist a bounded reasoning engine inspired by autonomous scientific-research systems while preserving Cohervia's stricter evidence boundaries.

The engine does not attempt to make a single model call behave like a complete scientist. It decomposes the research process into distinct roles with explicit structured outputs.

## Pipeline

```text
approved repository context
          |
          v
principal scientist
(question selection/framing)
          |
          v
mistake-aware memory retrieval
          |
          v
hypothesis scientist
(falsifiable candidates)
          |
          v
scientific critic
(adversarial review)
          |
          v
principal scientist
(candidate selection)
          |
          v
experiment designer
(exploratory plan only)
          |
          v
integrity reviewer
          |
          v
structured research packet
```

## Roles

### Principal scientist

Chooses one scientifically important unresolved question or rigorously frames a user-supplied question.

It must prefer questions that can change the theory rather than merely produce another metric.

### Hypothesis scientist

Generates candidate mechanisms that are:

- falsifiable;
- distinguishable from alternatives;
- linked to explicit theory constructs;
- bounded by current evidence;
- informed by prior failures and anomalies.

### Scientific critic

Attempts to reject or force revision of candidate hypotheses.

It looks specifically for:

- leakage;
- circular endpoints;
- unfair baselines;
- hidden post-outcome tuning;
- confounding;
- synthetic-to-real overgeneralization;
- unnecessary complexity;
- structural similarity to previously falsified ideas.

### Experiment designer

Creates an **exploratory** experiment plan only.

The plan is not a preregistration and cannot access a confirmatory holdout.

### Integrity reviewer

Performs a final review of the proposed packet and identifies unsupported claims, evidence-boundary violations, or unresolved concerns.

## Mistake-aware retrieval

The engine retrieves prior failure and anomaly records using a simple lexical relevance layer in v0.2.

This is intentionally transparent and auditable. Later versions may add semantic retrieval, but the retrieval method itself must remain provenance-visible.

Relevant mistakes are inserted into the hypothesis and criticism context so the engine cannot silently ignore previous failures.

## Provider boundary

The reasoning provider is behind a small protocol.

v0.2 includes:

- `OpenAIProvider` for a configured OpenAI API key;
- `ScriptedProvider` for deterministic unit tests.

The provider receives only the context assembled by the repository context loader.

## Output status

Every generated research packet is:

`candidate_reasoning`

It is not experimental evidence.

The packet may propose exploratory work, but evidence status can change only through the repository's existing experimental process.

## Security

The reasoning engine has no arbitrary code-execution interface.

It cannot:

- invoke a shell;
- install packages;
- modify the repository;
- open or merge pull requests;
- read a confirmatory holdout;
- alter authority configuration;
- alter the Scientific Constitution.

Those capabilities require later, separately reviewed interfaces.
