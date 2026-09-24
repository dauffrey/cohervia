from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .ledger import AppendOnlyLedger


_TOKEN = re.compile(r"[a-zA-Z0-9_]+")


def _tokens(value: str) -> set[str]:
    return {token.lower() for token in _TOKEN.findall(value) if len(token) > 2}


def _flatten(record: dict[str, Any]) -> str:
    parts: list[str] = []
    for value in record.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
    return " ".join(parts)


class ScientificMemory:
    def __init__(self, scientist_root: Path):
        state = Path(scientist_root) / "state"
        self.failures = AppendOnlyLedger(state / "failures.jsonl")
        self.anomalies = AppendOnlyLedger(state / "anomalies.jsonl")

    def relevant(self, query: str, limit: int = 6) -> list[dict[str, Any]]:
        query_tokens = _tokens(query)
        candidates: list[tuple[int, str, dict[str, Any]]] = []

        for kind, ledger in (
            ("failure", self.failures),
            ("anomaly", self.anomalies),
        ):
            for record in ledger.read_all():
                record_tokens = _tokens(_flatten(record))
                score = len(query_tokens & record_tokens)
                if score:
                    candidates.append((score, kind, record))

        candidates.sort(key=lambda item: item[0], reverse=True)
        return [
            {"memory_type": kind, "relevance": score, **record}
            for score, kind, record in candidates[:limit]
        ]
