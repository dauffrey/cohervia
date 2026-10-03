from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from copy import deepcopy

from .audit import AppendOnlyAuditLog
from .canonical import hash_object
from .events import Event


@dataclass(frozen=True, slots=True)
class MemoryWrite:
    actor: str
    trial_id: str
    key: str
    previous_state_hash: str
    resulting_state_hash: str
    source_event_ids: tuple[str, ...]
    persistence_scope: str = "trial"


class GovernedMemory:
    """Trial-scoped persistent state with hash-bound writes.

    State is cleared when a new trial begins. Cross-trial state must therefore
    be supplied as an explicitly frozen artifact outside this class.
    """

    def __init__(self, *, audit: AppendOnlyAuditLog) -> None:
        self._audit = audit
        self._trial_id: str | None = None
        self._state: dict[str, Any] = {}
        self._used_trial_ids: set[str] = set()

    @property
    def trial_id(self) -> str | None:
        return self._trial_id

    @property
    def state_hash(self) -> str:
        return hash_object(self._state)

    def begin_trial(self, trial_id: str) -> None:
        if not isinstance(trial_id, str) or not trial_id.strip():
            raise ValueError("trial ID must be nonblank")
        if trial_id in self._used_trial_ids:
            raise PermissionError("a memory trial ID cannot be reused")
        event = Event.create(
            trial_id=trial_id, actor="apparatus", kind="memory_trial_started",
            payload={"previous_trial_id": self._trial_id,
                     "previous_state_hash": self.state_hash,
                     "resulting_state_hash": hash_object({}),
                     "persistence_scope": "trial"},
            sequence=len(self._audit.records),
        )
        self._audit.append(event)
        self._trial_id = trial_id
        self._state = {}
        self._used_trial_ids.add(trial_id)

    def read(self, *, trial_id: str, key: str) -> Any:
        self._require_trial(trial_id)
        return deepcopy(self._state.get(key))

    def write(
        self,
        *,
        actor: str,
        trial_id: str,
        key: str,
        value: Any,
        source_event_ids: tuple[str, ...] = (),
    ) -> MemoryWrite:
        self._require_trial(trial_id)
        previous_hash = self.state_hash
        candidate = deepcopy(self._state)
        candidate[key] = deepcopy(value)
        resulting_hash = hash_object(candidate)
        write = MemoryWrite(
            actor=actor,
            trial_id=trial_id,
            key=key,
            previous_state_hash=previous_hash,
            resulting_state_hash=resulting_hash,
            source_event_ids=source_event_ids,
        )
        event = Event.create(
            trial_id=trial_id,
            actor=actor,
            kind="memory_write",
            payload={
                "key": key,
                "previous_state_hash": previous_hash,
                "resulting_state_hash": resulting_hash,
                "source_event_ids": list(source_event_ids),
                "persistence_scope": "trial",
            },
            sequence=len(self._audit.records),
        )
        self._audit.append(event)
        self._state = candidate
        return write

    def _require_trial(self, trial_id: str) -> None:
        if self._trial_id != trial_id:
            raise PermissionError("memory state cannot cross trial boundaries")
