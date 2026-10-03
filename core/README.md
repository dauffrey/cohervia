# Minimal observation and audit core v0.1.0

This separate package implements [O1–O4](../docs/contracts/OBSERVATION_CONTRACT.md)
and [A3–A5](../docs/contracts/AUTHORITY_AUDIT_CONTRACT.md) for caller-supplied local
records. It validates observation types, explicit missingness, uncertainty, identity,
ordering and provenance; hashes with pinned RFC 8785 JCS; atomically appends to SQLite;
and reconstructs accepted state through deterministic replay.

This is infrastructure tested with fabricated records. It supplies no scientific
evidence, estimator, qualification, independent evaluator, model call, governor,
permission or holdout access. Scientist and harness records require a separately
reviewed adapter before ingestion; neither package imports this core.

## Install and verify

From the repository root, using Python 3.11–3.13:

```sh
python -m pip install -e ./core
python -m unittest discover -s core/tests -v
```

The only runtime dependency is `rfc8785==0.1.4` (Apache-2.0), used directly rather
than a copied encoder or sorted-key JSON substitute. Tests include RFC 8785 numeric,
string and UTF-16 property ordering vectors. Cohervia's own license remains an owner
decision before distribution; no predecessor implementation was imported.

## Interfaces and caller obligations

- `Context(run_id, trajectory_id, subject_id)` fixes identity for an audit stream.
- `FrozenInputs(definitions, config_id, configuration, evidence_manifest, artifacts)`
  snapshots JSON definitions/configuration and expected raw artifact digests.
  Artifacts are explicitly supplied byte strings, never paths or URLs.
- `validate_observation(raw_bytes, context, inputs, state)` is pure and returns
  `ValidationResult(disposition, reason_codes, observation)`. Only accepts carry an
  observation. The caller must supply an accurate accepted state; the store rebuilds
  and verifies it instead of trusting a caller-maintained index.
- `AuditStore(path).append_submission(raw_bytes, context, inputs, event_id=...,
  recorded_at=..., producer={id, version})` returns the committed audit event.
  Recorder IDs and UTC timestamps are explicit; no clock or random ID is generated.
- `store.export(context, inputs)` returns a consistent verified pair of events and
  accepted observation records, as detached dictionaries.
- `replay(events, observations, context, inputs, checkpoint=None)` returns an
  `ObservationState` with accepted index, next sequence and last availability.
  `state.snapshot()` produces a detached JSON-compatible representation.

Each metric definition has exactly `id`, `version`, `value_type`, `units`, `minimum`,
`maximum`, `allowed_strings`, `scale`, and `risk_orientation`. Unused bounds/domain
are explicit null. Numeric units are nonblank (`"1"` for dimensionless values).
Nonnumeric units/bounds are null; booleans have null `allowed_strings`; strings may
supply a nonempty unique string domain. No universal normalized range is imposed.
Metric definitions, configuration and expected evidence manifest are frozen per run.
`inputs.sha256` hashes the complete `validation-inputs/0.1` document, including the
configuration. Availability of artifact bytes is separate from the expected manifest:
missing bytes quarantine a submission; supplying them later under the same manifest
requires an explicit resubmission. Replay requires bytes for all accepted evidence.

Observation and audit sequences are separate. An observation ID is unique across all
trajectories within a stored run. Exact duplicates get a new audit event without a new
observation. Rejects/quarantines retain only the raw submission digest, diagnostic codes
and a valid submitted observation ID; raw rejected content is not persisted.
Reason codes are sorted; rejection outranks quarantine. Shape/identity failures stop
before duplicate/ordering interpretation. Once those pass, semantic/provenance/ordering
checks collect applicable codes. Missingness rationale is required, but software cannot
verify the truth or adequacy of its explanation.

`BEGIN IMMEDIATE` serializes writers across independent SQLite connections; each
connection is thread-confined. The accepted observation, audit event and new input/stream
bindings commit together or roll back together. SQLite uses `synchronous=FULL`;
filesystem and hardware durability remain external assumptions. Export uses a read
transaction. Reopening an existing run verifies its input binding and stream identity.
Append verifies the entire existing stream before writing, intentionally O(n) in this
minimal implementation. No pruning, repair or automatic quarantine release is provided.

## Integrity limits and review gates

Replay verifies strict event schema, identity, contiguous sequence, links, event hashes,
accepted record hashes and reconstructed validation outcomes. Orphan accepted records
also fail. Rejected raw submissions are absent by design: replay checks their disposition
schema and hash chain, and cannot independently recompute the diagnostics or raw digest.
Integrity does not authenticate the recorder, validate a measurement's truth, establish
historical custody, or prevent an attacker who controls the database from rewriting it.

An optional independently trusted checkpoint has exactly `event_count`, `last_sha256`
(null for an empty stream), and `inputs_sha256`. It detects a changed tail or validation
input binding relative to that checkpoint. Checkpoint creation, external durable custody,
signatures, retention/redaction policy and operational access controls are deferred.
Without a trusted checkpoint, a valid truncated prefix or replacement stream can pass.

Only a caller-designated SQLite database is written. No evidence path resolver, network
resolver, daemon, CLI executor or Scientist-state writer exists. Deployment owners must
review ingestion/adapters, confidentiality, retention, source authentication, licensing,
resource limits and external custody before using live data. These are deployment gates,
not scientific findings or permission to open confirmatory holdouts.
