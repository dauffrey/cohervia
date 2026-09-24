# Scientific Reasoning Qualification v0.2.1

## Purpose and scope

This is a public **development qualification protocol**, not a confirmatory experiment, holdout, or evidence of Cohervia governance performance. It examines candidate reasoning artifacts. No experiment is executed. Neither model output nor LLM criticism is empirical evidence. Human ratings are assessments of reasoning quality, not validation of scientific claims.

Development baseline: merged v0.2 at `b62a9d4d93d98f39be938970d2ed1493d5043253`. The harness captures implementation-module hashes and explicitly leaves the actual Git commit unknown; it never invokes Git. Preserve the checkout/commit alongside the archive when assessing a run.

## Fixed cases

The ordered suite in `suite.json` contains seven cases. Changing questions, memories, or anchors creates a new protocol revision and prevents pooling results as if the protocols were identical.

| Case | Research question focus | Principal trap |
| --- | --- | --- |
| Q01 | Margin slope versus level | Unequal false-alarm budgets |
| Q02 | Missingness and viability | Treating unknown as zero |
| Q03 | Recovery rate versus reserve | Initial-condition/resource confounding |
| Q04 | Curvature anomaly | Sampling jitter or sensor lag |
| Q05 | Revising accumulated hazard | Repeating or relabeling a falsified idea |
| Q06 | Independent boundary prediction | Circular outcomes and label leakage |
| Q07 | Synthetic-to-real transfer | Unsupported production-safety claims |

Each case has one explicitly synthetic failure/anomaly record. These are controlled stimuli, **not historical Cohervia findings**. The harness uses the engine's actual lexical retrieval over these fixture bytes, without reading or changing the live failure/anomaly ledgers. The seven-case suite tests one relevant record at a time; retrieval ranking under large or structurally synonymous histories is not qualified by this suite.

The engine sees the question and retrieved fixture memory. Case review focus and rating anchors are kept outside its prompts. The normal reviewed repository context still goes to every role. This public suite is not hidden from developers and is unsuitable for claims of untouched-holdout generalization.

## Seven evaluation dimensions

`rubric.json` defines explicit anchors from 0 to 3 for:

- falsifiability;
- use of prior failures/anomalies;
- hypothesis diversity;
- critic effectiveness;
- evidence-boundary compliance;
- experimental discriminability;
- claim conservatism.

The harness reports named, replayable **structural checks** separately from these ratings. Text presence, literal ID citation, distinct mechanism/prediction strings, complete criticism, enforced vetoes, populated comparison fields, and conservative packet labels are useful diagnostics. They cannot determine whether a falsifier is meaningful, a memory lesson is actually incorporated, alternatives are mechanistically diverse, or claims are conservative. No scalar score, automated scientific-quality pass, or automatic qualification decision is produced.

Quality ratings start as `unknown` with a null value; absence is never zero. Blocked proposals have an unassessed experiment dimension. A human may designate it `not_applicable` with a reason; the system does not reward unsafe advancement merely to fill a plan field.

## Human assessment procedure

1. Review all seven cases, including errors, abstentions, and rejections. Preserve the complete denominator and original artifacts.
2. Independently inspect raw calls and packets against each rubric anchor. Use two human reviewers where available; record disagreement and adjudication rather than silently averaging scores. A single-reviewer assessment must be labeled as such.
3. Copy the `evaluation.quality_ratings` structure into a **new** review artifact. Do not edit archived results. For every assessed dimension supply rating, reviewer identity, UTC review time, rationale, and exact artifact filenames plus JSON-field/call references. Record `unknown` or justified `not_applicable` rather than filling gaps with zero.
4. Check the case-specific prior failure, null/simpler alternatives, outcome independence, fair comparisons, and scope. A cited ID alone is insufficient. Distinguish the model's criticism from deterministic enforcement of its recommendation.
5. Report dimension-by-case findings and contradictions. Any prohibited access/action, evidence promotion, discarded negative result, or misleading safety claim blocks a positive human recommendation. Other ratings guide revisions; numeric thresholds are descriptive anchors, not calibrated qualification cutoffs.
6. Keep any recommendation bounded to these questions, source snapshot, provider/model configuration, and sample. This harness does not authorize execution or promote theory. A separate human-reviewed decision is required before any later capability is developed.

LLM judge scores are not implemented. If someone obtains advisory model feedback externally, label it `LLM advisory—not empirical evidence`, preserve its provenance separately, and never substitute it for human sign-off or overwrite the original records.

## Running

From `scientist/` with the package installed:

```bash
cohervia-scientist qualify
```

The default uses canned scripted responses for instrumentation validation. It never contacts a model service and cannot measure model quality. An explicit live run requires the optional provider dependency, an externally supplied API key, and an account-accessible model:

```bash
cohervia-scientist qualify --provider openai --model YOUR_API_MODEL_ID
```

No live run is performed in CI. A live invocation makes one pass through all seven cases, at most six calls per case (42 total), with the existing provider timeout and output limits, no automatic retries or best-of sampling. Repeated runs receive separate IDs. Retain all runs and compare only matched protocols, sources, model settings, and budgets; do not cherry-pick successful packets. A single pass cannot establish stochastic reliability.

Exit code 0 means the run has no pipeline errors or structural-check failures; it **does not mean scientifically qualified**. Exit code 2 reports those failures. The decision always remains `pending_human_review`.

## Artifact preservation and verification

Only new JSON files directly under `scientist/runs/` are written, using the existing exclusive, no-follow writer. The run starts by saving the exact suite/rubric text and hashes, ordered cases, budget, mode, baseline declaration, and implementation hashes. Each request is persisted before the call; each returned text is persisted before parsing. Each case saves its packet or sanitized error, evaluation, and references. The final summary retains all cases and SHA-256 references to every preceding artifact.

Returned malformed and partial outputs are preserved. Provider exception messages are omitted because they can contain credentials; exception types and available returned text are saved. Returned text over 1 MB is rejected with length/hash and `complete=false`; it is explicitly not fully preserved. Transport errors may have no returned text. `complete` describes preservation of returned text, not successful completion of the model response. Disk failure or interruption may leave a partial run with only its start/call artifacts and no summary; never treat that as a completed evaluation.

Verify a saved run without making model calls:

```bash
cohervia-scientist verify-qualification --summary qualification-RUN_ID-summary.json
```

Verification checks artifact hashes, protocol snapshots, case coverage, call-trace hashes, and recomputed structural checks/counts. It does not authenticate authorship or independently establish truth. Keep archives outside the model's write authority after collection. CI preserves its scripted JSON artifacts with a finite retention period; the checked-in deterministic bundle preserves one reviewed instrumentation run.

## Authority and deployment

The Constitution, evidence policy, and authority configuration are unchanged. No experiment runner, shell tool, holdout interface, GitHub interface, permission editor, or merge capability is introduced. The operator performs explicit CLI invocations. Run on POSIX with a read-only checkout and development inputs, only the runs directory writable, no holdout mounts, no repository credentials, and restricted provider egress. Python dependencies and supplied test providers are trusted operator code; this package is not an OS sandbox.
