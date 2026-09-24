# Observation contract

Status: proposed Cohervia contract version 0.1; pending Phase 1 review. No implementation exists.
Source mappings: [migration inventory](../provenance/MIGRATION_INVENTORY.md), INV-01 through INV-04.
This adapts EFGM semantics; it does not require binary compatibility with its model or inherit its default confidence or normalized value domain.

## O1 — Versioned record

All fields below are required keys. Nullable means explicit JSON null, never omitted.
Strings used as identifiers must be nonempty and have no leading/trailing whitespace.
Unknown fields are rejected in version 0.1. New incompatible fields require a new schema version.
Nested structures use the same required-key convention.

| Field | Logical type | Requirement and meaning | Origin |
| --- | --- | --- | --- |
| schema_version | string | Exactly observation/0.1 | Cohervia versioning |
| observation_id | string | Unique within run; immutable after acceptance | Cohervia identity |
| run_id, trajectory_id, subject_id | strings | Must match ingestion context | Adapt temporal identity |
| sequence | integer | Nonnegative, unique observation position within trajectory, excluding booleans | Cohervia ordering |
| event_time | timestamp | UTC ISO 8601 with six fractional digits and Z | Acquisition context |
| available_at | timestamp | Same format; time evidence became available to observer; not before event_time | Cohervia causality |
| phase | string | One of pre_action, post_action, pre_intervention, post_intervention, follow_up | Adapt EFGM temporal phases |
| metric_id, metric_version | strings | Resolve to frozen metric definition | Cohervia semantics |
| value_type | string | number, boolean, or string; must match definition | Cohervia typed values |
| value | declared type or null | See O2; number excludes booleans and is finite | Adapt MetricObservation |
| units | string or null | Exact metric-definition unit; use 1 for dimensionless numeric data, null for nonnumeric | Cohervia units |
| status | enum | observed, inferred, unknown, not_applicable | Adopt EFGM states |
| rationale | string | Nonblank basis; explains missingness/applicability when value is null | Adapt EFGM rationale |
| uncertainty | object or null | If known: kind=confidence, value finite in [0,1], basis nonblank; no default | Cohervia bounded representation |
| evidence_refs | array of artifact refs | See O3; empty allowed only for unknown/not_applicable | Adapt EFGM provenance |
| input_observation_ids | array of strings | Required nonempty for inferred; empty for other statuses | Cohervia derivation |
| derivation | object or null | For inferred: id, version; otherwise null | Cohervia derivation |
| source | object | id, version | Source identity |
| collector | object | id, version | Acquisition identity |
| scorer | object or null | If assessed: id, version, type (human/model/automated/hybrid) | Adapt EFGM scorer |
| config | object | id, sha256 (64 lowercase hex characters) | Adapt configuration provenance |
| acquisition_context | object | adapter_id and adapter_version; no raw sensitive payload | Cohervia acquisition |

Metric definitions supplied locally to validation include id, version, value_type, units,
numeric minimum/maximum where applicable, allowed strings where applicable, scale description,
and risk_orientation (higher_risk/lower_risk/nonmonotonic/not_defined).
Definitions and configuration are immutable within a run and their manifest is hashed.
No value is assumed to be in [0,1] unless its definition says so.

## O2 — Value and uncertainty invariants

Observed and inferred require a non-null value matching the definition.
Unknown and not_applicable require explicit null, a rationale, and null uncertainty.
Unknown means insufficient evidence; not_applicable means the metric does not apply.
Zero is a measured value, never a missingness code.
Reject nonfinite numbers, booleans supplied as numbers, incompatible units and domain violations.
Inferred values require derivation and accepted same-trajectory input references.
Those inputs must be available no later than this record's available_at.
Uncertainty may be null for a known value; this means unquantified, not zero or perfect confidence.
An inferred record needs a scorer; an automated source measurement may have scorer=null.

## O3 — Evidence and provenance

An artifact ref has exactly id and sha256. IDs resolve through a supplied local manifest;
no network resolution occurs. Observed/inferred records require at least one ref, with a
verified digest and locally available artifact. Blank or duplicate refs are rejected.
Unavailable artifacts are quarantined; mismatched digests are rejected.
A digest verifies bytes against an expected digest, not the truth of the measurement,
authenticated producer identity, or scientific reliability. Phase 2 does not implement
source authentication. Trusted acquisition remains an external assumption.
Do not copy secrets or raw personal data into records; use redacted artifact references.

## O4 — Ordering and dispositions

Validation receives a run/trajectory/subject context, frozen definitions, local evidence
manifest, accepted-ID index and ordering state. No hidden clock determines validation.
Ingestion follows increasing sequence, starting at 0; available_at is nondecreasing.
Event time may be earlier than the previous event time for late evidence, but never later
than its own available_at. Late evidence cannot rewrite a historical prediction.

| Condition | Disposition / reason | State effect |
| --- | --- | --- |
| Valid next record | accept / valid | Append; advance sequence |
| Same observation ID and same canonical payload | accept / duplicate_noop | No second observation; no sequence advance |
| Same ID with different payload | reject / conflicting_id | No accepted-state change |
| Missing keys, bad types, unsupported schema, nonfinite values or units | reject / invalid_record | No accepted-state change |
| Identity differs from context | reject / identity_mismatch | No accepted-state change |
| Sequence below next expected with a different ID | reject / sequence_reuse | No accepted-state change |
| Sequence above next expected | quarantine / sequence_gap | Explicit resubmission needed after gap filled |
| available_at decreases | quarantine / availability_regression | Never insert into past accepted history |
| Unknown metric definition or unresolved input/evidence reference | quarantine / unresolved_reference | Not exposed to consumers |
| Digest mismatch or future derivation input | reject / invalid_provenance | No accepted-state change |
| Uncertainty null, otherwise valid | accept / valid | Retain null |

Check identity/schema before duplicate handling; compare canonical payloads before ordering.
Reject takes precedence over quarantine if multiple errors exist. Return all reason codes
in lexical order. Quarantine never automatically mutates or releases a record.
Each submission produces an audit disposition; rejected content is referenced by digest,
not necessarily copied into the audit log.

## O5 — Examples

Fictional record; the repeated-zero digest is a placeholder, not evidence. This is valid
only with matching context, metric definition, local artifact and manifest.

```json
{
  "schema_version": "observation/0.1",
  "observation_id": "obs-0",
  "run_id": "demo-run",
  "trajectory_id": "demo-trajectory",
  "subject_id": "demo-agent",
  "sequence": 0,
  "event_time": "2026-09-18T12:00:00.000000Z",
  "available_at": "2026-09-18T12:00:01.000000Z",
  "phase": "post_action",
  "metric_id": "retry_count",
  "metric_version": "1",
  "value_type": "number",
  "value": 2,
  "units": "1",
  "status": "observed",
  "rationale": "Count in the fictional collector artifact.",
  "uncertainty": null,
  "evidence_refs": [{"id": "demo-artifact", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"}],
  "input_observation_ids": [],
  "derivation": null,
  "source": {"id": "demo-source", "version": "1"},
  "collector": {"id": "demo-collector", "version": "1"},
  "scorer": null,
  "config": {"id": "demo-config", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"},
  "acquisition_context": {"adapter_id": "demo-adapter", "adapter_version": "1"}
}
```

Valid inferred variant: assign the next sequence/ID, status=inferred, a non-null scorer,
derivation={id: retry-identity, version: 1}, input_observation_ids=[obs-0], and an
available_at no earlier than obs-0. Retain evidence refs and use a definition accepting the result.
These are illustrative instructions, not a dataset or confirmatory observation.

Invalid mutations of the complete example:

| Mutation | Expected result |
| --- | --- |
| status=unknown while value=2 | reject / invalid_record |
| status=observed with value=null | reject / invalid_record |
| metric_id missing | reject / invalid_record |
| status=inferred without derivation or inputs | reject / invalid_record |
| evidence_refs containing a blank ID | reject / invalid_record |
| units=seconds for retry_count | reject / invalid_record |

Serialization and replay use [A4](AUTHORITY_AUDIT_CONTRACT.md).
