"""Development-only prospective custody gate; local order, NOT independent timestamp proof.

The coordinator must store the receipt outside model control before invoking the pilot.
A local hash chain cannot establish external custody or defend against rewriting all files.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
import math

def _digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class Receipt:
    sequence: int
    trial_id: str
    prediction_digest: str
    previous_digest: str
    digest: str

class CustodyLedger:
    """In-memory test coordinator: one commitment per trial; no external authority."""
    def __init__(self):
        self._receipts = []
        self._seen = set()
        self._attempted = set()

    def commit(self, trial_id, task_hash, model, probability):
        if not all(type(v) is str and v for v in (trial_id, task_hash, model)):
            raise ValueError("invalid commitment identity")
        if type(probability) not in (int, float) or not math.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError("invalid probability")
        if trial_id in self._seen or trial_id in self._attempted:
            raise ValueError("duplicate or late commitment")
        prediction = {"trial_id": trial_id, "task_hash": task_hash, "model": model, "probability": probability}
        previous = self._receipts[-1].digest if self._receipts else "0" * 64
        payload = {"sequence": len(self._receipts) + 1, "trial_id": trial_id,
                   "prediction_digest": _digest(prediction), "previous_digest": previous}
        receipt = Receipt(**payload, digest=_digest(payload))
        self._receipts.append(receipt)
        self._seen.add(trial_id)
        return receipt

    def authorize_attempt(self, prediction, receipt):
        if type(prediction) is not dict or type(receipt) is not Receipt:
            raise ValueError("invalid attempt gate")
        if receipt not in self._receipts or receipt.trial_id != prediction.get("trial_id"):
            raise ValueError("missing custody receipt")
        if _digest(prediction) != receipt.prediction_digest:
            raise ValueError("prediction changed after commitment")
        if receipt.trial_id in self._attempted:
            raise ValueError("attempt already authorized")
        self._attempted.add(receipt.trial_id)
        return True

    def audit(self):
        previous = "0" * 64
        for index, receipt in enumerate(self._receipts, 1):
            payload = {"sequence": receipt.sequence, "trial_id": receipt.trial_id,
                       "prediction_digest": receipt.prediction_digest, "previous_digest": receipt.previous_digest}
            if receipt.sequence != index or receipt.previous_digest != previous or receipt.digest != _digest(payload):
                raise ValueError("custody chain invalid")
            previous = receipt.digest
        return len(self._receipts)
