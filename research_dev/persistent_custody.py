"""Persistent development custody: SQLite transaction gate with HMAC receipt authentication.

A secret held by the coordinator (not the model) authenticates local receipts.
This is NOT third-party timestamping or proof of independent external custody.
"""
import hashlib
import hmac
import json
import math
import sqlite3
from pathlib import Path

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()

def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

class PersistentCustody:
    def __init__(self, path, secret):
        if type(secret) is not bytes or len(secret) < 32:
            raise ValueError("coordinator secret must contain at least 32 bytes")
        self.secret = secret
        self.db = sqlite3.connect(str(Path(path)), isolation_level=None, timeout=10)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS commitments (
            seq INTEGER PRIMARY KEY AUTOINCREMENT, trial TEXT NOT NULL UNIQUE,
            prediction TEXT NOT NULL, previous TEXT NOT NULL, receipt TEXT NOT NULL,
            attempted INTEGER NOT NULL DEFAULT 0 CHECK(attempted IN (0,1)),
            consumption_mac TEXT)""")

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _mac(self, payload):
        return hmac.new(self.secret, canonical(payload), hashlib.sha256).hexdigest()

    def _audit(self):
        previous = "0" * 64
        rows = self.db.execute("SELECT seq,trial,prediction,previous,receipt,attempted,consumption_mac FROM commitments ORDER BY seq").fetchall()
        for index, (seq, trial, prediction, prev, receipt, attempted, consumption_mac) in enumerate(rows, 1):
            payload = {"sequence": seq, "trial_id": trial, "prediction_digest": prediction, "previous_digest": prev}
            if seq != index or prev != previous or not hmac.compare_digest(receipt, self._mac(payload)) or attempted not in (0, 1):
                raise ValueError("custody integrity failure")
            expected_consumption = self._mac({"consumed_receipt": receipt, "trial_id": trial, "sequence": seq})
            if (attempted == 0 and consumption_mac is not None) or (attempted == 1 and (type(consumption_mac) is not str or not hmac.compare_digest(consumption_mac, expected_consumption))):
                raise ValueError("custody consumption integrity failure")
            previous = receipt
        return previous

    def commit(self, prediction):
        if type(prediction) is not dict or set(prediction) != {"trial_id", "task_hash", "model", "probability"}:
            raise ValueError("invalid prediction")
        trial, task, model, probability = (prediction[k] for k in ("trial_id", "task_hash", "model", "probability"))
        if not all(type(x) is str and x for x in (trial, task, model)) or len(task) != 64 or any(c not in "0123456789abcdef" for c in task):
            raise ValueError("invalid prediction identity")
        if type(probability) not in (int, float) or not math.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError("invalid probability")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            previous = self._audit()
            seq = self.db.execute("SELECT COUNT(*) FROM commitments").fetchone()[0] + 1
            payload = {"sequence": seq, "trial_id": trial, "prediction_digest": digest(prediction), "previous_digest": previous}
            receipt = self._mac(payload)
            self.db.execute("INSERT INTO commitments(seq,trial,prediction,previous,receipt) VALUES (?,?,?,?,?)",
                            (seq, trial, payload["prediction_digest"], previous, receipt))
            self.db.execute("COMMIT")
            return dict(payload, receipt=receipt)
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def authorize(self, prediction, receipt):
        if type(receipt) is not dict or set(receipt) != {"sequence", "trial_id", "prediction_digest", "previous_digest", "receipt"}:
            raise ValueError("invalid receipt")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self._audit()
            if type(prediction) is not dict or digest(prediction) != receipt["prediction_digest"]:
                raise ValueError("prediction does not match receipt")
            row = self.db.execute("SELECT seq,prediction,previous,receipt,attempted FROM commitments WHERE trial=?",
                                  (receipt["trial_id"],)).fetchone()
            if row is None or row != (receipt["sequence"], receipt["prediction_digest"],
                                      receipt["previous_digest"], receipt["receipt"], 0):
                raise ValueError("missing, altered or consumed commitment")
            if not hmac.compare_digest(receipt["receipt"], self._mac({k: receipt[k] for k in ("sequence", "trial_id", "prediction_digest", "previous_digest")})):
                raise ValueError("invalid receipt signature")
            consumption_mac = self._mac({"consumed_receipt": receipt["receipt"], "trial_id": receipt["trial_id"], "sequence": receipt["sequence"]})
            self.db.execute("UPDATE commitments SET attempted=1, consumption_mac=? WHERE trial=?", (consumption_mac, receipt["trial_id"]))
            self.db.execute("COMMIT")
            return True
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def audit(self):
        return self._audit()
