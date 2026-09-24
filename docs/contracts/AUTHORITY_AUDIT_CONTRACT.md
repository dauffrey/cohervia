# Authority and audit contract

Status: proposed Cohervia contracts, pending review. Phase 2 implements only audit
records and observation validation dispositions. Recommendations and enforcement are future interfaces.
See inventory INV-12 and INV-13 for CGS architectural lineage.

## A1 — GovernorRecommendation

Required future keys:

| Field | Type and obligation |
| --- | --- |
| schema_version, recommendation_id | authority-recommendation/0.1; unique ID |
| run_id, trajectory_id, subject_id | Same identity as input snapshot |
| action_ref | {id, sha256} for action-specific recommendations; null for trajectory-wide advice |
| snapshot_id | Immutable input snapshot reference |
| policy | {id, version, config_sha256} |
| recommendation | ALLOW, CHALLENGE, LIMIT, HOLD, DENY, FALLBACK |
| reason_codes, evidence_limitations | Arrays; reasons nonempty |
| mode | shadow or intervention |
| created_at, expires_at | UTC timestamps; expiry strictly after creation |
| producer | {id, version}; governor identity |

ALLOW recommends continuing within existing permissions; CHALLENGE requests verification;
LIMIT proposes narrower scope; HOLD requests a pause; DENY rejects the proposed action;
FALLBACK requests the externally configured alternative.
These outcomes are not an ordinal numeric scale.
This vocabulary is Cohervia's proposal, not a verbatim CGS enum.
If an action margin or consequence estimate is attached in a future schema, it must use
the same immutable action_ref; a task/time index alone is insufficient.

## A2 — EnforcementDecision

Required future keys: schema_version=enforcement/0.1, decision_id, run_id, trajectory_id,
subject_id, action_ref (non-null id and sha256), recommendation_id (nullable),
authority_id/version, deterministic_policy_id/version/hash, actual_disposition
(allow/deny/hold), permitted_scope (resources and limits), reason_codes, created_at,
expires_at, and audit_event_id.
FALLBACK requires separate authorization of the fallback action; it is not a blanket permission.
Task authorization is a versioned reference with immutable objective, constraints, permissions,
and risk envelope for that version; external reauthorization creates a new logged version.

Invariants:

- Recommendations cannot create permissions or override hard denials.
- Relaxation stays within independently authorized bounds.
- Shadow mode has no authority-changing side effects and emits no executable permission.
- Malformed, expired, identity-mismatched or unavailable recommendations never silently mean ALLOW.
- The authority owner must configure the unavailable-recommendation response; absent configuration
  prevents enabling intervention mode. No universal fallback is asserted safe for every domain.
- A proposed action's bytes must match action_ref when enforced.
- The acting agent cannot modify governor policies, thresholds, enforcement or authoritative logs.
- Permission decisions remain distinct from viability and from recommendation generation.

## A3 — AuditEvent

Required keys:

| Field | Type / validation |
| --- | --- |
| schema_version | audit/0.1 |
| event_id, run_id, trajectory_id, subject_id | Nonblank IDs; immutable |
| sequence | Nonnegative integer per audit stream; contiguous starting at 0 |
| recorded_at | O1 UTC format; supplied by trusted recorder |
| producer | id, version |
| event_type | observation_validation in Phase 2; future types require schema extension |
| related_ids | object: observation_id, snapshot_id, recommendation_id, decision_id; nullable values |
| payload_version | observation-validation/0.1 in Phase 2 |
| payload | submission_sha256, disposition, reason_codes, accepted_observation_ref (nullable) |
| previous_sha256 | null for stream genesis, otherwise previous event digest |
| sha256 | Current event digest |

An audit stream is scoped to run/trajectory/subject. Accepted observation references are
{id, sha256} objects into a separate immutable local observation store.
Rejected or quarantined payloads need not be stored in full; preserve their submission digest
and diagnostic codes, avoiding sensitive values. Duplicate submissions also get audit events,
but accepted observation state is not advanced.

## A4 — Canonical encoding and integrity

Proposed Phase 2 convention: [RFC 8785 JSON Canonicalization Scheme (JCS)](https://www.rfc-editor.org/rfc/rfc8785), UTF-8, SHA-256,
lowercase hexadecimal digest. Use the same convention for observations, definitions and
configuration; artifact refs instead hash the artifact's exact raw bytes.

Only JCS-compatible JSON is accepted: reject duplicate object keys, nonfinite numbers,
invalid Unicode and integers outside the interoperable safe range [-9007199254740991,
9007199254740991]. Booleans are not numbers in validation. No implicit string trimming,
timestamp conversion, array sorting or data coercion occurs during hashing.
Object property order is canonicalized by JCS; array order is preserved.
Pin the implementation/version and validate it against canonicalization vectors before use;
ordinary sorted-key JSON is not asserted equivalent to JCS.

Hash a complete audit event with only its top-level sha256 key excluded. Include
previous_sha256, identity, timestamps, payload and all other declared fields.
Observation hashes cover every observation field. A raw submission digest covers original
input bytes, permitting malformed JSON to be recorded without interpreting it.

The append operation commits the accepted observation and its disposition audit atomically
to a caller-supplied local transactional store. Failure rolls back both; no orphan accepted
record. Audit stream sequence and observation sequence are different counters.
Concurrent appends require serialization; an append-only application interface is not
filesystem tamper resistance.

Hash chaining detects alterations relative to a trusted checkpoint. It cannot alone detect
replacement of the whole log, removal of its tail, or forgery of producer identity.
Authenticity, durable external checkpoints and operational access controls are deferred;
never claim immutability or non-repudiation from hashes alone.

## A5 — Replay

Replay validates schema, digests, contiguous audit sequence, previous links, identity and
referenced accepted observation hashes. It reconstructs the accepted-ID index and ordering
state from accepted events; duplicate_noop has no state effect.
Missing referenced accepted observations, malformed events, or broken links stop replay with
an error; no silent skipping. Quarantine requires a later explicit submission.
No current clock, network lookup, random ID generation or estimator runs occur during replay.
Given identical records, definitions and manifests, reconstructed state is identical.
Tail completeness requires an external trusted checkpoint and is not promised by Phase 2.

## A6 — Examples and privacy

Shadow example: snapshot s1 -> recommendation r1 (LIMIT, mode=shadow) -> advisory audit.
Existing external permission controls remain unchanged; no enforcement token is emitted.

Hard-denial example: action a1/hash h1 violates deterministic policy p1 despite recommendation
r2=ALLOW. Enforcement d1 references a1/h1, r2 and p1, sets deny, and records a separate audit event.
No action executes because of the recommendation.

These future event sequences are illustrative, not Phase 2 functionality or evidence.
Do not include raw prompts, secrets, credentials or personal data in routine audit payloads.
A deployment owner must define retention, redaction and evidence access before live ingestion.
Phase 2 fixtures use fictional non-sensitive records only.
