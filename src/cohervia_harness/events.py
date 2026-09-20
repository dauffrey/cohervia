from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .canonical import hash_object


@dataclass(frozen=True, slots=True)
class Event:
    event_id: str
    trial_id: str
    actor: str
    kind: str
    payload: dict[str, Any]
    timestamp: str

    @classmethod
    def create(
        cls,
        *,
        trial_id: str,
        actor: str,
        kind: str,
        payload: dict[str, Any] | None = None,
        sequence: int,
    ) -> "Event":
        body = {
            "trial_id": trial_id,
            "actor": actor,
            "kind": kind,
            "payload": payload or {},
            "sequence": sequence,
        }
        return cls(
            event_id=hash_object(body),
            trial_id=trial_id,
            actor=actor,
            kind=kind,
            payload=payload or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
