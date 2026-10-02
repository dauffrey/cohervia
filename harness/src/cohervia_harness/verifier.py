from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class VerificationResult:
    score: float | None
    status: str


class Verifier(Protocol):
    def verify(self, *, expected: object, actual: object) -> VerificationResult:
        ...


class ExactMatchVerifier:
    """Deterministic verifier for benign development tasks."""

    def verify(self, *, expected: object, actual: object) -> VerificationResult:
        return VerificationResult(
            score=1.0 if actual == expected else 0.0,
            status="pass" if actual == expected else "fail",
        )
