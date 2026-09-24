from __future__ import annotations

import json
from typing import Any


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError(f"non-finite JSON value: {value}")


def parse_json_object(text: str) -> dict[str, Any]:
    """Accept one object or a complete JSON fence; never salvage surrounding prose."""
    if not isinstance(text, str) or len(text) > 100000:
        raise ValueError("model response exceeds character budget or is not text")
    value = text.strip()
    if value.startswith("```"):
        lines = value.splitlines()
        if len(lines) < 3 or lines[0] not in {"```", "```json"} or lines[-1] != "```":
            raise ValueError("invalid JSON fence")
        value = "\n".join(lines[1:-1])
    try:
        parsed = json.loads(value, object_pairs_hook=_unique, parse_constant=_invalid_constant)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("model response contained invalid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("model response must be a JSON object")
    return parsed
