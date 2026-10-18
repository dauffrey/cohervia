"""Strict JSON intake and pinned RFC 8785 encoding, without coercion."""
import hashlib
import json

import rfc8785

MAX_INTEGER = 9007199254740991


def _check(value):
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > MAX_INTEGER:
            raise ValueError("integer outside interoperable safe range")
    elif type(value) is float:
        import math
        if not math.isfinite(value):
            raise ValueError("nonfinite number")
    elif type(value) is str:
        value.encode("utf-8", errors="strict")
    elif type(value) is list:
        for item in value:
            _check(item)
    elif type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("JSON object keys must be strings")
            _check(key)
            _check(item)
    else:
        raise ValueError("not a JSON value")


def canonical_bytes(value):
    _check(value)
    return rfc8785.dumps(value)


def record_sha256(value):
    return bytes_sha256(canonical_bytes(value))


def bytes_sha256(raw):
    if type(raw) is not bytes:
        raise TypeError("raw input must be bytes")
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value):
    """JSON for validation/replay, preserving numeric types rather than JCS spelling.

    Not a hash dialect. In particular 1e20 remains a floating-point token instead
    of the integer token emitted by JCS; unsafe Python integers remain rejected.
    """
    _check(value)
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")


def _decode_json(raw, *, parse_int=int):
    if type(raw) is not bytes:
        raise TypeError("raw input must be bytes")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def constant(_):
        raise ValueError("nonfinite number")

    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=constant, parse_int=parse_int)


def parse_json(raw):
    """Strict submission intake: integer tokens outside the safe range fail."""
    value = _decode_json(raw)
    canonical_bytes(value)
    return value


def parse_canonical(raw):
    """Read exact JCS bytes, preserving the pinned encoder's binary64 semantics.

    JCS emits large integral floats in decimal integer spelling below 1e21.
    Recover those as floats only if the complete input reproduces byte-for-byte
    under JCS. This reader is separate from strict raw submission intake.
    """
    def canonical_integer(token):
        value = int(token)
        return value if abs(value) <= MAX_INTEGER else float(token)

    value = _decode_json(raw, parse_int=canonical_integer)
    if canonical_bytes(value) != raw:
        raise ValueError("input is not exact canonical JSON")
    return value
