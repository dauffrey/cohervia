from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True, slots=True)
class FrozenArtifact:
    name: str
    sha256: str


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def freeze_inventory(paths: dict[str, str | Path]) -> tuple[FrozenArtifact, ...]:
    return tuple(
        FrozenArtifact(name=name, sha256=sha256_file(path))
        for name, path in sorted(paths.items())
    )


def verify_required_fields(
    manifest_path: str | Path,
    required_fields: Iterable[str],
) -> tuple[str, ...]:
    with Path(manifest_path).open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    return tuple(field for field in required_fields if field not in manifest)
