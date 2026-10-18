from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TheoryGraph:
    document: dict[str, Any]

    @classmethod
    def load(cls, path: Path) -> "TheoryGraph":
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError("theory graph must be a JSON object")
        required = {"schema_version", "theory_version", "nodes", "edges"}
        missing = sorted(required - document.keys())
        if missing:
            raise ValueError(f"theory graph missing required fields: {missing}")
        return cls(document=document)

    @property
    def version(self) -> str:
        return str(self.document["theory_version"])

    def weak_edges(self) -> list[dict[str, Any]]:
        weak = {"unknown", "candidate_relation", "weakened", "falsified"}
        return [
            edge for edge in self.document.get("edges", [])
            if edge.get("status") in weak
        ]

    def summary(self) -> dict[str, Any]:
        nodes = self.document.get("nodes", [])
        edges = self.document.get("edges", [])
        return {
            "theory_version": self.version,
            "nodes": len(nodes),
            "edges": len(edges),
            "weak_edges": len(self.weak_edges()),
            "status": self.document.get("status", "unknown"),
        }
