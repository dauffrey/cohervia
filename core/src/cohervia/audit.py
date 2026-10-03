"""Serialized, transactional SQLite append; no enforcement or external IO."""
import sqlite3

from .canonical import bytes_sha256, canonical_bytes, parse_json, record_sha256
from .inputs import identifier, timestamp, versioned
from .observations import validate_observation
from .replay import ReplayError, replay


class AuditStore:
    """Caller owns path, recorder identity/time and operational access controls.

    Each connection is thread-confined; BEGIN IMMEDIATE serializes independent
    connections/processes. A run freezes inputs and an observation ID is unique
    across trajectories in that run. Existing state is verified before append.
    """
    def __init__(self, path):
        self.connection = sqlite3.connect(path, isolation_level=None, timeout=30)
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.execute("PRAGMA synchronous=FULL")
        self.connection.executescript('''
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY, inputs_sha256 TEXT NOT NULL, inputs_json BLOB NOT NULL);
            CREATE TABLE IF NOT EXISTS streams (
                run_id TEXT NOT NULL, trajectory_id TEXT NOT NULL, subject_id TEXT NOT NULL,
                PRIMARY KEY (run_id, trajectory_id), FOREIGN KEY (run_id) REFERENCES runs(run_id));
            CREATE TABLE IF NOT EXISTS observations (
                run_id TEXT NOT NULL, observation_id TEXT NOT NULL, trajectory_id TEXT NOT NULL,
                record BLOB NOT NULL, PRIMARY KEY (run_id, observation_id),
                FOREIGN KEY (run_id, trajectory_id) REFERENCES streams(run_id, trajectory_id));
            CREATE TABLE IF NOT EXISTS events (
                run_id TEXT NOT NULL, trajectory_id TEXT NOT NULL, sequence INTEGER NOT NULL,
                event_id TEXT NOT NULL, record BLOB NOT NULL,
                PRIMARY KEY (run_id, trajectory_id, sequence), UNIQUE (run_id, trajectory_id, event_id),
                FOREIGN KEY (run_id, trajectory_id) REFERENCES streams(run_id, trajectory_id));
        ''')

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _bind(self, context, inputs, create):
        db = self.connection
        row = db.execute("SELECT inputs_sha256, inputs_json FROM runs WHERE run_id=?", (context.run_id,)).fetchone()
        if row is None:
            if not create:
                raise ReplayError("unknown run")
            db.execute("INSERT INTO runs VALUES (?, ?, ?)", (context.run_id, inputs.sha256, canonical_bytes(inputs.document)))
        elif row != (inputs.sha256, canonical_bytes(inputs.document)):
            raise ReplayError("frozen run inputs mismatch")
        row = db.execute("SELECT subject_id FROM streams WHERE run_id=? AND trajectory_id=?", (context.run_id, context.trajectory_id)).fetchone()
        if row is None:
            if not create:
                raise ReplayError("unknown stream")
            db.execute("INSERT INTO streams VALUES (?, ?, ?)", tuple(context.as_dict().values()))
        elif row[0] != context.subject_id:
            raise ReplayError("stream subject mismatch")

    def _export(self, context):
        args = (context.run_id, context.trajectory_id)
        events = []
        for sequence, event_id, raw in self.connection.execute("SELECT sequence, event_id, record FROM events WHERE run_id=? AND trajectory_id=? ORDER BY sequence", args):
            event = parse_json(raw)
            if type(event) is not dict or event.get("sequence") != sequence or event.get("event_id") != event_id:
                raise ReplayError("event storage index mismatch")
            events.append(event)
        observations = {r[0]: parse_json(r[1]) for r in self.connection.execute("SELECT observation_id, record FROM observations WHERE run_id=? AND trajectory_id=?", args)}
        return events, observations

    def export(self, context, inputs):
        """Consistent, verified snapshot; returned dictionaries cannot mutate storage."""
        self.connection.execute("BEGIN")
        try:
            self._bind(context, inputs, False)
            events, observations = self._export(context)
            replay(events, observations, context, inputs)
            self.connection.execute("COMMIT")
            return events, observations
        except BaseException:
            self.connection.execute("ROLLBACK")
            raise

    def append_submission(self, raw, context, inputs, *, event_id, recorded_at, producer):
        """Every bytes submission gets a disposition. Recorder errors fail transaction."""
        submission_sha256 = bytes_sha256(raw)
        if not identifier(event_id) or not timestamp(recorded_at) or not versioned(producer):
            raise ValueError("invalid trusted recorder fields")
        producer = parse_json(canonical_bytes(producer))
        db = self.connection
        db.execute("BEGIN IMMEDIATE")
        try:
            self._bind(context, inputs, True)
            events, observations = self._export(context)
            state = replay(events, observations, context, inputs)
            # Duplicate handling precedes ordering, with an index scoped to the
            # whole run. Cross-trajectory inputs still fail the validator's identity check.
            for observation_id, stored in db.execute("SELECT observation_id, record FROM observations WHERE run_id=? AND trajectory_id<>?", (context.run_id, context.trajectory_id)):
                state.accepted[observation_id] = parse_json(stored)
            result = validate_observation(raw, context, inputs, state)
            o = result.observation
            accepted_ref = None
            if result.disposition == "accept":
                accepted_ref = {"id": o["observation_id"], "sha256": record_sha256(o)}
                if result.reason_codes == ("valid",):
                    db.execute("INSERT INTO observations VALUES (?, ?, ?, ?)", (context.run_id, o["observation_id"], context.trajectory_id, canonical_bytes(o)))
            related_id = None
            try:
                submitted = parse_json(raw)
                if type(submitted) is dict and identifier(submitted.get("observation_id")):
                    related_id = submitted["observation_id"]
            except (ValueError, UnicodeError, OverflowError, RecursionError):
                pass
            event = {"schema_version": "audit/0.1", "event_id": event_id, **context.as_dict(),
                     "sequence": len(events), "recorded_at": recorded_at, "producer": producer,
                     "event_type": "observation_validation", "related_ids": {"observation_id": related_id,
                     "snapshot_id": None, "recommendation_id": None, "decision_id": None},
                     "payload_version": "observation-validation/0.1", "payload": {
                     "submission_sha256": submission_sha256, "disposition": result.disposition,
                     "reason_codes": list(result.reason_codes), "accepted_observation_ref": accepted_ref},
                     "previous_sha256": events[-1]["sha256"] if events else None}
            event["sha256"] = record_sha256(event)
            db.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?)", (context.run_id, context.trajectory_id, len(events), event_id, canonical_bytes(event)))
            db.execute("COMMIT")
            return event
        except BaseException:
            db.execute("ROLLBACK")
            raise
