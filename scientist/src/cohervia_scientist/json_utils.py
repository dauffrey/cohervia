from __future__ import annotations

import json
from typing import Any


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse one JSON object from model output.

    The parser accepts a plain object or a fenced JSON block, but never evaluates
    code and never attempts permissive Python-literal parsing.
    """
    value = text.strip()
    if value.startswith("```"):
        lines = value.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        value = "\n".join(lines).strip()
        if value.lower().startswith("json\n"):
            value = value[5:].lstrip()

    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        start = value.find("{")
        end = value.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("model response did not contain a JSON object")
        try:
            parsed = json.loads(value[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError("model response contained invalid JSON") from exc

    if not isinstance(parsed, dict):
        raise ValueError("model response must be a JSON object")
    return parsed
