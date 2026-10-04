"""Fixed public tasks and deterministic success criteria; no file/task discovery."""
import re
from cohervia.canonical import canonical_bytes, parse_json
from cohervia_harness.tasks import development_tasks

VERSION = "public-pilot/0.1"
MAX_CALLS = 3
MAX_OUTPUT_TOKENS = 256
MAX_TEXT_BYTES = 16384
TIMEOUT_SECONDS = 20.0
INSTRUCTIONS = ('Solve only the supplied public task. Return exactly one JSON object with the '
                'single key "answer" and its answer value. No markdown, prose, tools or actions.')
MODEL = re.compile(r"[A-Za-z0-9._:/-]{1,128}\Z")


def model_id(value):
    return type(value) is str and MODEL.fullmatch(value) is not None


def catalog():
    rows = [{"id": t.task_id, "family": t.task_family_id, "prompt": t.prompt,
             "expected": t.expected} for t in development_tasks()]
    rows.append({"id": "DEV-TEXT-001", "family": "string_verifiable",
                 "prompt": "Return the integer count of the letter a in banana.", "expected": 3})
    if len(rows) != MAX_CALLS:
        raise ValueError("public fixture catalog changed; review/version the pilot")
    return rows


def assess(text):
    try:
        result = parse_json(text.encode("utf-8"))
        if type(result) is not dict or set(result) != {"answer"}:
            return False, None
        return True, result["answer"]
    except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError):
        return False, None


def _same_shape_and_types(answer, expected):
    """Check types before JCS can erase integer/float distinctions."""
    if type(answer) is not type(expected):
        return False
    if type(expected) is list:
        return len(answer) == len(expected) and all(
            _same_shape_and_types(a, e) for a, e in zip(answer, expected))
    if type(expected) is dict:
        return set(answer) == set(expected) and all(
            _same_shape_and_types(answer[k], expected[k]) for k in expected)
    return True


def outcomes(receipt, task):
    usable = receipt["status"] == "completed"
    valid, answer = assess(receipt["text"]) if usable else (None, None)
    # Integer criteria reject floats (including rounded decimal tokens) and booleans.
    success = (valid and _same_shape_and_types(answer, task["expected"])
               and canonical_bytes(answer) == canonical_bytes(task["expected"])) if usable else None
    return {"response_received": usable, "answer_valid_json": valid, "task_success": success}


def definitions():
    return [{"id": metric, "version": "1", "value_type": "boolean", "units": None,
             "minimum": None, "maximum": None, "allowed_strings": None,
             "scale": description, "risk_orientation": "not_defined"}
            for metric, description in (("response_received", "Completed usable provider text received"),
                                        ("answer_valid_json", "Exactly one strict JSON answer object"),
                                        ("task_success", "Exact match to this public task's fixed expected answer"))]
