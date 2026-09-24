from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ContextConfig:
    approved_paths: list[str]
    max_total: int = 60000
    max_per_document: int = 14000

    @classmethod
    def load(cls, scientist_root: Path) -> "ContextConfig":
        raw = json.loads(
            (scientist_root / "config" / "reasoning.json").read_text(
                encoding="utf-8"
            )
        )
        return cls(
            approved_paths=list(raw["approved_context_paths"]),
            max_total=int(raw.get("max_context_characters", 60000)),
            max_per_document=int(
                raw.get("max_characters_per_document", 14000)
            ),
        )


class RepositoryContext:
    def __init__(self, repo_root: Path, scientist_root: Path):
        self.repo_root = Path(repo_root).resolve()
        self.scientist_root = Path(scientist_root).resolve()
        self.config = ContextConfig.load(self.scientist_root)

    def build(self) -> str:
        chunks: list[str] = []
        used = 0

        for relative in self.config.approved_paths:
            path = (self.repo_root / relative).resolve()
            try:
                path.relative_to(self.repo_root)
            except ValueError as exc:
                raise ValueError(
                    f"approved context path escapes repository: {relative}"
                ) from exc

            if not path.exists() or not path.is_file():
                continue

            text = path.read_text(encoding="utf-8")
            text = text[: self.config.max_per_document]
            block = f"\n===== {relative} =====\n{text}\n"
            remaining = self.config.max_total - used
            if remaining <= 0:
                break
            block = block[:remaining]
            chunks.append(block)
            used += len(block)

        return "".join(chunks)
