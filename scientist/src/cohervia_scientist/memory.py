from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .json_utils import parse_json_object
from .safe_io import read_local

_TOKEN = re.compile(r"[a-zA-Z0-9_]+")
MAX_MEMORY_RESULTS = 20
MAX_RECORD_BYTES = 16000


def validate_memory_limit(limit: int) -> int:
    if type(limit) is not int or not 1 <= limit <= MAX_MEMORY_RESULTS:
        raise ValueError(f"memory limit must be between 1 and {MAX_MEMORY_RESULTS}")
    return limit


def _tokens(value: str) -> set[str]:
    return {token.lower() for token in _TOKEN.findall(value) if len(token) > 2}


class ScientificMemory:
    """Read only development memory. The operator must never import sealed outcomes here."""
    def __init__(self, scientist_root: Path):
        self.root = Path(scientist_root).absolute()
        self.sources: list[dict[str, str]] = []

    def relevant(self, query: str, limit: int = 6) -> list[dict[str, Any]]:
        validate_memory_limit(limit)
        query_tokens = _tokens(query)
        candidates = []
        self.sources = []
        for kind in ("failure", "anomaly"):
            relative = "state/" + ("failures.jsonl" if kind == "failure" else "anomalies.jsonl")
            data = read_local(self.root, relative, max_bytes=2_000_000)
            self.sources.append({"path": "scientist/" + relative,
                                 "sha256": hashlib.sha256(data).hexdigest()})
            for line_number, line in enumerate(data.splitlines(), 1):
                if not line.strip():
                    continue
                if len(line) > MAX_RECORD_BYTES:
                    raise ValueError("memory record exceeds byte budget")
                record = parse_json_object(line.decode("utf-8"))
                # Fail closed on explicitly segregated evidence. No dereferencing of links.
                if record.get("evidence_class", "exploratory") not in {"exploratory", "instrumentation"}:
                    raise ValueError("memory may contain only development records")
                score = len(query_tokens & _tokens(json.dumps(record, sort_keys=True)))
                if score:
                    candidates.append((score, kind, relative, line_number, line, record))
        candidates.sort(key=lambda item: item[0], reverse=True)
        return [{**record, "memory_type": kind, "relevance": score,
                 "source_path": "scientist/" + relative, "source_line": number,
                 "record_sha256": hashlib.sha256(line).hexdigest()}
                for score, kind, relative, number, line, record in candidates[:limit]]
