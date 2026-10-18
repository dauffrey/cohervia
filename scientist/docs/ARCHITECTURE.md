# Architecture

## Overview

Cohervia Scientist is designed as a bounded autonomous research programme rather than a single unconstrained agent.

```text
Research question
      |
      v
Principal Scientist
      |
      +--> Literature/lineage review
      +--> Theory analysis
      +--> Hypothesis generation
      +--> Scientific critic
      |
      v
Experiment manager
      |
      v
Sandboxed exploratory execution
      |
      v
Analysis + failure postmortem
      |
      v
Preregistration proposal
      |
      v
Freeze boundary
      |
      v
Independent confirmatory evaluator
      |
      v
Evidence record
      |
      v
Theory revision proposal
      |
      v
Human/independent promotion review
```

## Roles

The eventual system may use one or more models, but logical roles remain separated.

### Principal Scientist
Selects important unresolved questions and synthesizes the research programme.

### Literature and lineage reviewer
Checks Cohervia, predecessor evidence, and later approved external literature. It prevents novelty claims from being based on ignorance of prior work.

### Theory Scientist
Maintains the versioned theory graph and identifies weak, contradictory, or unsupported edges.

### Hypothesis Scientist
Generates falsifiable candidate hypotheses.

### Scientific Critic
Attempts to invalidate assumptions, detect leakage, identify unfair baselines, and expose alternative explanations.

### Experiment Manager
Creates bounded exploratory plans and tracks provenance.

### Experimental Engineer
Produces experiment code within a sandbox. It has no production authority.

### Statistician
Evaluates whether claims follow from results and records uncertainty.

### Evidence Archivist
Maintains immutable ledgers for predictions, failures, anomalies, and theory revisions.

## Trust boundaries

The autonomous research system is not trusted with:

- repository protection;
- canonical merges;
- confirmatory holdout policy;
- constitution changes;
- credential management;
- production systems.

## Confirmatory boundary

The independent evaluator must not be the same mutable process used for development and tuning.

A frozen manifest should eventually contain hashes for:

- preregistration;
- code;
- configuration;
- simulator/environment;
- dataset/holdout;
- evaluator;
- analysis rules.

Any mismatch invalidates the confirmatory execution unless explicitly re-preregistered.
