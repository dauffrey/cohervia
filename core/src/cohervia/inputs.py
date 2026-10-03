"""Caller-supplied context and immutable, locally available validation inputs."""
from dataclasses import dataclass
from datetime import datetime
import re

from .canonical import canonical_bytes, parse_json, record_sha256

HEX = re.compile(r"[0-9a-f]{64}\Z")
TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z\Z")


def identifier(value):
    return type(value) is str and bool(value) and value == value.strip()


def digest(value):
    return type(value) is str and HEX.fullmatch(value) is not None


def timestamp(value):
    if type(value) is not str or TIME.fullmatch(value) is None:
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        return True
    except ValueError:
        return False


def keys(value, expected):
    return type(value) is dict and set(value) == set(expected.split())


def versioned(value):
    return keys(value, "id version") and all(identifier(v) for v in value.values())


def ref(value):
    return keys(value, "id sha256") and identifier(value["id"]) and digest(value["sha256"])


@dataclass(frozen=True)
class Context:
    run_id: str
    trajectory_id: str
    subject_id: str

    def __post_init__(self):
        if not all(identifier(v) for v in self.as_dict().values()):
            raise ValueError("invalid context identity")

    def as_dict(self):
        return dict(run_id=self.run_id, trajectory_id=self.trajectory_id, subject_id=self.subject_id)


@dataclass(frozen=True, init=False)
class FrozenInputs:
    """Canonical snapshots; properties return copies. Artifacts are bytes, never paths.

    Definition fields are explicit, including nullable minimum, maximum and
    allowed_strings. The manifest binds config, definitions and expected artifact
    digests; availability is a separate local snapshot and cannot alter that binding.
    """
    _document: bytes
    _artifacts: tuple

    def __init__(self, definitions, config_id, configuration, evidence_manifest, artifacts):
        if not identifier(config_id):
            raise ValueError("invalid config id")
        definitions = parse_json(canonical_bytes(definitions))
        if type(definitions) is not list:
            raise ValueError("definitions must be a list")
        seen = set()
        for d in definitions:
            if not keys(d, "id version value_type units minimum maximum allowed_strings scale risk_orientation"):
                raise ValueError("invalid metric definition keys")
            if not versioned({"id": d["id"], "version": d["version"]}) or not identifier(d["scale"]):
                raise ValueError("invalid metric definition identity/scale")
            pair = (d["id"], d["version"])
            if pair in seen:
                raise ValueError("duplicate metric definition")
            seen.add(pair)
            if d["value_type"] not in ("number", "boolean", "string") or d["risk_orientation"] not in ("higher_risk", "lower_risk", "nonmonotonic", "not_defined"):
                raise ValueError("invalid metric semantics")
            if d["value_type"] == "number":
                if not identifier(d["units"]) or d["allowed_strings"] is not None:
                    raise ValueError("invalid numeric definition")
                for bound in (d["minimum"], d["maximum"]):
                    if bound is not None and type(bound) not in (int, float):
                        raise ValueError("invalid numeric bounds")
                if d["minimum"] is not None and d["maximum"] is not None and d["minimum"] > d["maximum"]:
                    raise ValueError("inverted bounds")
            else:
                if any(d[k] is not None for k in ("units", "minimum", "maximum")):
                    raise ValueError("invalid nonnumeric definition")
                allowed = d["allowed_strings"]
                if d["value_type"] == "boolean" and allowed is not None:
                    raise ValueError("invalid boolean definition")
                if allowed is not None and (type(allowed) is not list or not allowed or any(type(v) is not str for v in allowed) or len(set(allowed)) != len(allowed)):
                    raise ValueError("invalid string domain")
        if type(evidence_manifest) is not dict or any(not identifier(k) or not digest(v) for k, v in evidence_manifest.items()):
            raise ValueError("invalid evidence manifest")
        if type(artifacts) is not dict or any(k not in evidence_manifest or type(v) is not bytes for k, v in artifacts.items()):
            raise ValueError("artifacts must be manifested byte strings")
        document = {"schema_version": "validation-inputs/0.1", "definitions": definitions,
                    "config": {"id": config_id, "sha256": record_sha256(configuration)},
                    "configuration": configuration, "evidence_manifest": evidence_manifest}
        object.__setattr__(self, "_document", canonical_bytes(document))
        object.__setattr__(self, "_artifacts", tuple(sorted(artifacts.items())))

    @property
    def document(self):
        return parse_json(self._document)

    @property
    def sha256(self):
        return record_sha256(self.document)

    @property
    def definitions(self):
        return {(d["id"], d["version"]): d for d in self.document["definitions"]}

    @property
    def config(self):
        return self.document["config"]

    @property
    def manifest(self):
        return self.document["evidence_manifest"]

    @property
    def artifacts(self):
        return dict(self._artifacts)
