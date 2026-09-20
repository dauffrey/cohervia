from __future__ import annotations

from dataclasses import asdict, dataclass

from .canonical import hash_object
from .events import Event


@dataclass(frozen=True, slots=True)
class AuditRecord:
    sequence: int
    event: Event
    previous_hash: str
    record_hash: str


class AppendOnlyAuditLog:
    """Append-only, hash-chained audit log.

    Historical records are exposed as an immutable tuple and there is no
    mutation or deletion API.
    """

    GENESIS = "0" * 64

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    @property
    def records(self) -> tuple[AuditRecord, ...]:
        return tuple(self._records)

    @property
    def root_hash(self) -> str:
        return self._records[-1].record_hash if self._records else self.GENESIS

    def append(self, event: Event) -> AuditRecord:
        previous_hash = self.root_hash
        sequence = len(self._records)
        record_hash = hash_object(
            {
                "sequence": sequence,
                "event": asdict(event),
                "previous_hash": previous_hash,
            }
        )
        record = AuditRecord(
            sequence=sequence,
            event=event,
            previous_hash=previous_hash,
            record_hash=record_hash,
        )
        self._records.append(record)
        return record

    def verify(self) -> bool:
        previous = self.GENESIS
        for expected_sequence, record in enumerate(self._records):
            if record.sequence != expected_sequence:
                return False
            if record.previous_hash != previous:
                return False
            expected_hash = hash_object(
                {
                    "sequence": record.sequence,
                    "event": asdict(record.event),
                    "previous_hash": record.previous_hash,
                }
            )
            if expected_hash != record.record_hash:
                return False
            previous = record.record_hash
        return True
