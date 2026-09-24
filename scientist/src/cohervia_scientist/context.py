from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .safe_io import read_local

POLICY_PATHS = (
    "scientist/SCIENTIFIC_CONSTITUTION.md",
    "docs/research/EVIDENCE_POLICY.md",
)
# Configuration may select a subset, never expand this reviewed boundary.
APPROVED_PATHS = frozenset((*POLICY_PATHS,
    "README.md", "ROADMAP.md", "CONTRIBUTING.md",
    "docs/architecture/OVERVIEW.md", "docs/provenance/CONSTRUCT_STATUS.md",
    "docs/provenance/LINEAGE.md", "experiments/README.md",
    "scientist/docs/CONTINUAL_LEARNING.md", "scientist/state/theory_graph.json",
))


@dataclass(frozen=True)
class ContextConfig:
    approved_paths: tuple[str, ...]
    max_total: int = 60000
    max_per_document: int = 14000
    sha256: str = ""

    @classmethod
    def load(cls, scientist_root: Path) -> "ContextConfig":
        data = read_local(scientist_root, "config/reasoning.json", max_bytes=16000)
        raw = json.loads(data)
        paths = raw["approved_context_paths"]
        if (not isinstance(paths, list) or not all(isinstance(x, str) for x in paths)
                or len(paths) != len(set(paths)) or not set(paths) <= APPROVED_PATHS):
            raise ValueError("context paths must be unique reviewed paths")
        total = raw.get("max_context_characters", 60000)
        per_doc = raw.get("max_characters_per_document", 14000)
        for value, maximum in ((total, 60000), (per_doc, 14000)):
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError("invalid context character budget")
        return cls(tuple(paths), total, per_doc, hashlib.sha256(data).hexdigest())


@dataclass(frozen=True)
class ContextSnapshot:
    text: str
    policies: str
    sources: tuple[dict, ...]
    config_sha256: str


class RepositoryContext:
    def __init__(self, repo_root: Path, scientist_root: Path):
        self.repo_root = Path(repo_root).absolute()
        self.scientist_root = Path(scientist_root).absolute()
        if self.scientist_root != self.repo_root / "scientist":
            raise ValueError("scientist root must be repository/scientist")
        self.config = ContextConfig.load(self.scientist_root)

    def snapshot(self) -> ContextSnapshot:
        self.config = ContextConfig.load(self.scientist_root)
        chunks, policies, sources = [], [], []
        used = 0
        paths = (*POLICY_PATHS, *(x for x in self.config.approved_paths if x not in POLICY_PATHS))
        for relative in paths:
            data = read_local(self.repo_root, relative, max_bytes=256000)
            text = data.decode("utf-8")
            required = relative in POLICY_PATHS
            if required and not text.strip():
                raise ValueError("governing policies must not be empty")
            included = text if required else text[:self.config.max_per_document]
            prefix = f"\n===== {relative} =====\n"
            remaining = self.config.max_total - used - len(prefix) - 1
            if required and len(included) > remaining:
                raise ValueError("context budget cannot fit complete governing policies")
            included = included[:max(0, remaining)]
            block = prefix + included + "\n" if remaining > 0 else ""
            chunks.append(block)
            used += len(block)
            if required:
                policies.append(block)
            sources.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest(),
                            "included_characters": len(included), "truncated": included != text})
        return ContextSnapshot("".join(chunks), "".join(policies), tuple(sources),
                               self.config.sha256)

    def build(self) -> str:
        return self.snapshot().text
