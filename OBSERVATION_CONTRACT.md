# Observation contract

This contract defines the minimum semantics for Cohervia observations during the Phase 1 design work. The goal is not to implement a runtime system here; it is to specify the measurement contract that any future minimal observation layer must satisfy.

## Scope

Cohervia adopts the explicit observation model established by the EFGM lineage, rooted at:

- EFGM repository: `https://github.com/dauffrey/efgm`
- commit: `37b2ff2d2b577c9f383dd0d7c3083597627150ea`
- relevant source: `efgm/schemas_v2.py`

The canonical semantics are intentionally conservative: a missing observation is not a zero, and an inapplicable observation is not a measured value.

## Normative observation model

An observation is a `MetricObservation`-like record with the following required semantics.

```text
MetricObservation
  value: float | null
  status: observed | inferred | unknown | not_applicable
  rationale: string
  evidence_refs: list[string]
  scorer_id: string | null
  scorer_type: human | model | automated | hybrid | null
  confidence: float in [0, 1]
  recorded_at: datetime | null
```

### Required rules

1. `value` may be present only when `status` is `observed` or `inferred`.
2. `value` must be absent when `status` is `unknown` or `not_applicable`.
3. A `value` of zero is a valid measured value, not an absence of evidence.
4. `unknown` and `not_applicable` are distinct states and must not be silently collapsed into zero or a default score.
5. `evidence_refs` must never contain blank entries.
6. `scorer_id` must not be blank when supplied.
7. `confidence` must remain in the inclusive range `[0, 1]`.
8. `rationale` must explain the observation basis and any applicable provenance caveats.

A future implementation must preserve these semantics exactly; permissive coercion such as "missing value implies zero" is forbidden.

## Source-grounded semantics

The EFGM model includes an explicit validator pattern that treats `unknown` and `not_applicable` as distinct from a numeric measurement. This distinction is required to prevent the governance layer from interpreting missing or inapplicable evidence as favorable evidence.

Cohervia Phase 1 therefore requires the following contract properties:

- observations are auditable units of measurement, not just raw floats;
- measurement semantics are preserved with provenance and scorer identity;
- the distinction between `unknown`, `not_applicable`, and a numeric `0` is retained in storage and reporting;
- evidence references remain explicit and reviewable;
- any adaptation in later phases must keep the contract backward-compatible with the original semantics.

## Required data model obligations

Any Cohervia observation record must preserve all of the following:

- stable identity of what was observed;
- measurement status (`observed`, `inferred`, `unknown`, `not_applicable`);
- the numeric value when one exists;
- the rationale for the value or the missing value;
- evidence references that link the observation to its source material;
- scorer identity and scorer type when a human or model makes the assessment;
- timestamp and confidence.

## Example valid record

```json
{
  "value": 0.81,
  "status": "inferred",
  "rationale": "Derived from the same policy-held telemetry stream and a frozen evaluator summary.",
  "evidence_refs": [
    "telemetry:run-0012:metric:goal_divergence",
    "evaluators:baseline-2024-04:summary"
  ],
  "scorer_id": "operator-07",
  "scorer_type": "human",
  "confidence": 0.72,
  "recorded_at": "2025-01-04T12:00:00Z"
}
```

## Example invalid records

These are not valid under the contract:

```json
{
  "value": null,
  "status": "observed",
  "rationale": "No observation"
}
```

```json
{
  "value": 0,
  "status": "unknown",
  "rationale": "The metric is missing"
}
```

```json
{
  "value": 0.5,
  "status": "inferred",
  "evidence_refs": ["", "valid-ref"],
  "rationale": "Bad evidence refs"
}
```

## Measurement accountabilities

The observation contract is not just a schema. It establishes responsibilities:

- data producers must attach provenance and rationale;
- data validators must reject blank evidence references and invalid status-value combinations;
- the governance layer must treat missing observations as missing evidence, not as a silent favorable default;
- audit logs must preserve the original observation and its validation outcome.

## Non-goals for Phase 1

This contract does not define:

- a production metric taxonomy;
- a policy threshold for action authorization;
- a learning algorithm for calibrating confidence;
- a generator for synthetic observations.

The contract specifies the semantics required for a disciplined observation layer, while leaving later phases to decide how those observations are produced and used.
