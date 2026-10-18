# v0.2 implementation review

Base inspected: merged v0.1 at `69dc8701fb9af534c84b1bdd623e5ab31f8f1452` (PR #5).
Existing v0.2 work continued: PR #6 at `737a4cfb2517b409f01081173947e036e11e6034`.

## Findings corrected

| Finding | Correction and regression evidence |
| --- | --- |
| Rejected/revision-needed hypotheses could advance | Deterministic eligibility gate, abstention, blocked packet; tests verify no experiment-design call |
| Negative memory limit selected nearly the whole ledger | CLI and API bounds, record/ledger caps; invalid and oversized cases tested |
| Second-resolution names overwrote packets | Unique IDs, exclusive create, concurrent collision test |
| Arbitrary output paths could overwrite controls | `runs/`-only writer with pinned directories and no overwrite |
| Context configuration could admit holdouts or unrelated files | Reviewed allowlist, mandatory full policies, no traversal/symlink/hard-link reads |
| Later roles lacked source context and policies | One context snapshot shared across all calls, full policies in every role's instructions |
| Integrity findings did not alter packet status | Binding rejected/revision-required dispositions |
| Incomplete/ambiguous model output was accepted | Exact fields, required plan arrays, strict JSON parsing, complete critique coverage |
| Packet lacked source/model provenance | Source, configuration, memory, implementation, and request/response hashes; explicit unknown commit |
| Role separation implied evaluator independence | Corrected documentation and machine-readable limitation |
| Existing v0.2 changed authority configuration | Restored exact merged v0.1 configuration; no runtime permission grants |
| Provider assumed a model name and unbounded defaults | Explicit account API identifier, fixed endpoint, no tools, timeout/output/request caps |

## Validation scope

The regression suite exercises successful and blocked orchestration, hostile inputs, file boundaries, bounded retrieval, schema violations, mocked provider errors, provenance, and concurrent writes. Existing v0.1 ledger and research-cycle tests remain included. CI runs the offline core and repository/CLI smoke checks on Python 3.11–3.13 with a read-only token and no persisted checkout credential.

This is implementation/instrumentation validation only. No model-quality evaluation, confirmatory holdout access, experiment execution, or Cohervia scientific result is claimed. See REASONING_ENGINE.md for residual limitations and deployment assumptions. This review was performed in the implementation session, not by an independent scientific evaluator.
