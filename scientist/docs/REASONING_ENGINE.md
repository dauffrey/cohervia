# Scientific reasoning engine

v0.2 produces candidate research packets. It does not execute experiments, create evidence, or promote theory. The Scientific Constitution, evidence policy, and v0.1 authority configuration remain unchanged.

## Orchestration

1. Snapshot reviewed repository documents and full governing policies.
2. Principal Scientist frames an unresolved question.
3. Retrieve development failures and anomalies by lexical token overlap.
4. Hypothesis Scientist proposes 2–8 distinct, falsifiable competing explanations (default 4), including null/no-effect and simpler alternatives in its instructions.
5. Scientific Critic evaluates every candidate for falsifiers, confounds, circular endpoints, leakage, unfair baselines, prior mistakes, and overgeneralization.
6. Principal Scientist selects an eligible candidate or abstains.
7. Experiment Designer proposes an exploratory plan with nonempty controls, baselines, procedure, analysis, failure criteria, stopping conditions, and provenance requirements.
8. Integrity Reviewer checks claims and evidence boundaries.
9. Emit the packet for human review.

At most six provider calls occur. If every candidate is blocked, the pipeline ends after criticism and still returns a packet. Revised hypotheses require a new cycle and new criticism; a selector cannot override the critic by asserting that it applied revisions.

## Hard gates and data boundaries

- Only `advance_exploratory` candidates without fatal flaws, leakage risks, or required revisions are eligible. Rejected or revision-needed candidates never reach experiment design.
- Integrity rejection, revision requests, unsupported claims, and evidence-boundary issues change the packet disposition. They cannot be hidden behind an acceptable label.
- JSON parsing rejects duplicate keys, non-finite values, surrounding prose, and oversized output. Typed records require exactly their declared fields, complete critique coverage, distinct hypothesis IDs/statements, and matching selection/plan IDs.
- Plan fields require `evidence_class=exploratory`, literal `requires_holdout=false`, and `authority_effect=none`. These declarations do not prove that prose is scientifically sound; human review remains required.
- Configuration may choose from a fixed reviewed context allowlist, never arbitrary paths. The Constitution and evidence policy are mandatory, complete, and supplied to every role. Missing documents or insufficient policy budgets fail closed. Optional-document truncation is recorded.
- Context is a single in-memory snapshot for the run. Repository text, memory, user questions, and previous outputs are treated as untrusted reference data, not permission instructions.
- Memory reads only `scientist/state/failures.jsonl` and `anomalies.jsonl`. Reads and individual records have byte caps; retrieval returns 1–20 records. Explicit non-development evidence classifications fail closed. Source links in memory are never followed.
- Reads reject traversal, symlinks, hard links, and non-regular files. POSIX directory descriptors pin path components against symlink replacement races.
- Packet writes are restricted to direct JSON children of `scientist/runs/`, use unique run IDs, and exclusively create new files. They cannot overwrite governance files, ledgers, source, or earlier packets. A failed disk write may leave an incomplete file; it is never silently reused.
- The reasoning engine exposes no shell, code-execution, GitHub-write, merge, holdout, permission-change, or evidence-promotion tool. It never calls the v0.1 ledger mutation CLI or research-cycle confirmation gates.

## Packet contract

Every packet declares `evidence_status=not_evidence`, `epistemic_state=inferred`, and `execution_authorized=false`. Status is one of:

| Status | Meaning |
| --- | --- |
| `candidate_reasoning` | Logical integrity review permits human consideration of an exploratory proposal |
| `blocked_by_critic` | No candidate advanced; experiment and integrity review are null |
| `revision_required` | Final review requires changes; no execution is authorized |
| `rejected_by_integrity` | Final review rejects the proposal |

The packet preserves the question, memory, hypotheses, criticisms, selection, proposed experiment if present, and integrity review if reached. Provenance records source and configuration SHA-256 hashes, truncation, memory source/line/record hashes, retrieval query/method/limit, implementation-module hashes, provider/model/effort, and request/instruction/response hashes. Source commit is explicitly `unknown`; the engine does not spawn Git or pretend a working tree is a clean commit. Archive the checkout and packet together when reviewing a run. Hashes identify bytes, not truth or authenticity.

Empty memory retrieval means no lexical matches, not proof that no relevant mistakes exist. Lexical retrieval can miss structural synonyms. Model-generated claims of having considered failures are not mechanically verified, and semantic distinctness/falsifiability still need critical human assessment. No learning effectiveness claim is made.

## Provider boundary

`ReasoningProvider` defines a text-only completion interface. `ScriptedProvider` supports deterministic offline tests. The optional `OpenAIProvider` uses an explicitly supplied API model identifier, the fixed OpenAI endpoint, no tools, no stored response request, no automatic retries, a 60-second timeout, and an 8,000-token output limit. Incomplete responses, missing text, and unexpected tool outputs fail closed. JSON responses are capped at 100,000 characters and complete requests at 400,000 characters.

Each role is a separate stateless call. The default adapter uses the same configured model across roles: this is logical separation, **not an independent evaluator** or proof of independence. Tests use scripted responses and a mocked SDK; no live provider quality or account compatibility is claimed.

## Deployment assumptions and limits

The operator invokes this CLI explicitly and supplies the provider credential externally. This does not grant the Scientist any autonomous capability in `authority.json`. Do not provision GitHub credentials, executable tools, or confirmatory data to the process. Use a read-only checkout and development-memory mount, with only `scientist/runs/` writable, and restrict network egress to the configured provider. Dependencies and custom Python provider implementations are trusted operator code, not model-generated extensions.

These Python interfaces are not an OS sandbox. They cannot detect a human copying sealed outcomes into an approved document or falsely labeling a memory record. Development memory must be curated outside the Scientist, and holdouts must remain separately controlled and unmounted. Provider failure or malformed output raises an error and does not produce a completed packet; partial-call recovery is not implemented. No live experiment, independent confirmation, autonomous merge, or self-modification exists in this release.
