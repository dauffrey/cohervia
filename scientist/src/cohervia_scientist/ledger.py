from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


class AppendOnlyLedger:
    """Simple append-only JSONL ledger.

    v0.1 deliberately provides no update/delete operation. Historical correction
    should be represented by a new record that references the prior record.
    """

    def __init__(self, path: Path):
        self.path = Path(path)

    def append(self, record: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")))
            handle.write("\n")

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"invalid JSONL at {self.path}:{line_number}"
                    ) from exc
                if not isinstance(value, dict):
                    raise ValueError(
                        f"ledger record at {self.path}:{line_number} must be an object"
                    )
                rows.append(value)
        return rows

    def __iter__(self) -> Iterable[dict[str, Any]]:
        return iter(self.read_all())
