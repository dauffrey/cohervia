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


def parse_json(raw):
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

    value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
    canonical_bytes(value)
    return value
