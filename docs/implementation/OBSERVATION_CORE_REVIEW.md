# Observation core review — PR #9

Reviewed baseline: `6fb23a18a395901efdaaf1fefad2c0ac4317583c`, on the fresh branch
from merged PR #8. This is an implementation review by the implementing assistant,
not an independent scientific evaluator's approval. Fabricated fixtures only;
Scientist qualification and COH-EXP-0001 statistical design remain separate.

| Finding | Failure before correction | Correction and regression |
| --- | --- | --- |
| Canonical numeric round-trip | A valid observation with `value=1e20` was accepted and committed, then export failed because JCS encoded it as an unsafe integer token. Large floating-point definitions/configuration also broke frozen snapshots. | Separate strict raw intake from exact-JCS storage decoding. Require byte-identical re-encoding; preserve float tokens during replay validation. Test numeric boundaries, hashes, snapshots, reopen, duplicates, inference and continued rejection of unsafe raw integers. |
| Trajectory isolation | Run-wide duplicate checks loaded foreign records into the local accepted index. A foreign row with corrupted identity could supply a local derivation input, commit an accept and leave the new stream unreplayable. | Reserve foreign IDs without loading their payloads into derivation state. Test index/payload identity disagreement, quarantine, replay and ID conflict priority. |
| Transaction failure paths | SQLite-initiated rollback was followed by another rollback, masking the original integrity error. A trigger silently suppressing an observation insert could leave a committed audit referencing a missing record, or a reported disposition with no saved audit. | Roll back only active transactions; replay persisted rows before commit. Test automatic rollback error identity, silent suppression, complete rollback and normalized corruption errors. |
| Invalid identifier Unicode | Surrogate IDs could pass context/recorder validation and fail only later during encoding or SQLite binding. | Reject invalid UTF-8 identifiers before beginning a run; test context and recorder fields. |

The updated suite has 54 core tests. Existing mainline boundary regressions protect
Scientist/evidence-policy bytes, authority restrictions and the unfrozen experiment
manifest. Dedicated CI also runs Scientist and apparatus suites on Python 3.11–3.13.
Exact-head CI outcomes are recorded in the PR description after validation.

No statistical plan, evaluator, estimator, governor, permission interface or automatic
ingestion adapter was added. Confirmatory holdouts were not accessed or executed.
No empirical scientific evidence or deployment readiness is claimed.

Remaining human decisions are unchanged: API/metric semantics, dependency/license
approval, authentication and independently trusted checkpoint custody, live-data
retention/redaction, resource limits and operational access controls. Raw submission
byte strings are not retained; their digests cannot be recomputed without external
copies. Hash chains cannot authenticate a producer or establish complete historical
custody on their own.
