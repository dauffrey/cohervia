# Bounded public development pilot v0.1.0

A separate text-only model driver connects three fixed public tasks to the merged
observation/audit core. It is outside Scientist and has no experiment, governor,
permission-enforcement or confirmatory-holdout interface.

**Status: runner and offline instrumentation implemented; a real model run requires
an explicit accessible API model and a configured provider credential. No live run
is claimed by this PR.** The checked-in tests and CI use fabricated/mock responses.

## Three public tasks and fixed criteria

| Task | Prompt | Exact expected JSON answer |
| --- | --- | --- |
| DEV-ALG-001 | Return the sorted form of [3, 1, 2]. | `{"answer":[1,2,3]}` |
| DEV-MATH-001 | Return the integer value of 7 * 8. | `{"answer":56}` |
| DEV-TEXT-001 | Return the integer count of the letter a in banana. | `{"answer":3}` |

The first two reuse the harness's public task definitions. No caller-supplied tasks,
file inputs, hidden verifiers or recursive discovery exist. Only the fixed instruction
and each prompt are sent to the model, in independent requests without conversation
history. Answer keys are public but are not inserted into the request. These trivial
known tasks can be in training data: they exercise behavior capture, not generalization.

## Installation and execution

From the repository root, Python 3.11–3.13:

```sh
python -m pip install -e ./core -e ./harness -e './pilot[openai]'
python -m unittest discover -s pilot/tests -v
```

Configure `OPENAI_API_KEY` in the execution environment. Choose an explicitly accessible
Responses-compatible model; there is no implicit default or model substitution. A live
run can make billable requests; the user authorizes the fixed development scope, not
confirmatory execution. Maximum three calls per invocation, 256 output tokens per call,
20-second SDK timeout, no retries, no background execution, no streaming, `tools=[]`,
`tool_choice="none"`, `store=False`. Output limits include reasoning tokens, so an
incomplete response remains unknown. API model compatibility, account access and price
are not assumed. API provider retention is not negated by the local `store=False` setting.

```sh
cohervia-pilot live --model "$OPENAI_MODEL" --run-id public-dev-001 --output pilot/runs/public-dev-001
cohervia-pilot replay --directory pilot/runs/public-dev-001
```

The endpoint is fixed to `https://api.openai.com/v1`; a custom endpoint environment
variable does not redirect acquisition. Missing key/SDK blocks before a run directory
or model-result archive is created. Authentication failure stops further calls and marks
remaining tasks unattempted/unknown. Other task-level errors are retained without retry.
Exception text, headers, credentials and private system context are not archived.
API references: [Responses create](https://developers.openai.com/api/reference/python/resources/responses/methods/create)
and [data controls](https://developers.openai.com/api/docs/guides/your-data).

## Offline self-test and replay

```sh
cohervia-pilot self-test --run-id offline-001 --output pilot/runs/offline-001
cohervia-pilot replay --directory pilot/runs/offline-001
```

This deliberately fabricates one pass, one wrong answer and one timeout. Its report
says **SCRIPTED INSTRUMENTATION — NOT A LIVE MODEL RUN**. The counts are pass=1,
fail=1, unknown=1; they are not measured model performance. CI exports these labelled
instrumentation artifacts separately from scientific evidence.

## Observation and report semantics

Each task has its own trajectory with three accepted observations:

- `response_received`: observed boolean, meaning completed nonblank bounded provider text.
- `answer_valid_json`: inferred strict answer-object check when usable text exists;
  unknown/null when it does not.
- `task_success`: inferred exact match to this public expected answer, with accepted
  same-trajectory input IDs; unknown/null when no usable completed response exists.

Completed text that fails JSON/answer criteria is a failure. Incomplete, missing,
oversized, invalid-provider or unexpected-tool outputs do not become false measured
answers: success remains unknown. A wrong completed answer is explicitly false, never
missing. Python booleans do not count as integer answers. No confidence default or
scientific-reliability score is assigned.

Before acquisition the driver writes its fixed plan, hashes the public catalog and
captures exact source bytes for the pilot/core/public-task modules. After each
attempt it saves the bounded returned text and selected API metadata (ID, returned
model, token usage) in a receipt. These are SDK-level acquisition records, not full HTTP
wire captures or authenticated producer attestations. Python/SDK and pinned JCS versions are recorded;
source changes during acquisition invalidate report generation. No source archive is
executed during replay. Expected evidence digests are frozen after collection; measurement
configuration and scoring rules are fixed beforehand. This is not a preregistration.

The resulting fresh owned directory contains the plan, per-task receipts, SQLite
observations/audits, a complete `bundle.json` and regenerated `report.md`. Existing
output directories are refused. Within a source checkout, outputs must be under
`pilot/runs/`; protected repository tracks cannot be output targets. Runtime exports
are ignored by Git. Partial acquisition failures retain receipts without a verified
report; they never silently look like complete model runs.

Bundle replay verifies the public catalog, source/evidence inventory and raw hashes,
frozen configuration, all three streams/checkpoints, core replay and independent
recomputation of the fixed public criteria. It regenerates identical report text with
no network, current clock, source execution or file acquisition. The CLI reads only the
explicit run's bundle. Replaying never calls the model again.

A locally bundled checksum/checkpoint detects accidental corruption, not replacement
of the entire bundle by someone controlling storage. An independently retained bundle
hash can be supplied with `replay --expected-sha256 HASH`. Authentication, external custody,
retention/redaction and production resource controls remain deployment gates.

No results are ingested into Scientist, no qualification rating is assigned, and no
COH-EXP identifier is created. A/B/C inputs/outcomes and reconstructive metadata remain
sealed. This is public exploratory development, not a benchmark, capability-emergence
finding, safety finding or evidence that a governor predicts failure or safely adjusts
authority. Statistical design and independent evaluator infrastructure remain separate.
