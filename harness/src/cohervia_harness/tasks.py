from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DevelopmentTask:
    task_id: str
    task_family_id: str
    prompt: str
    expected: object


def development_tasks() -> tuple[DevelopmentTask, ...]:
    """Benign deterministic tasks used only to test instrumentation."""
    return (
        DevelopmentTask(
            task_id="DEV-ALG-001",
            task_family_id="algorithmic_verifiable",
            prompt="Return the sorted form of [3, 1, 2].",
            expected=[1, 2, 3],
        ),
        DevelopmentTask(
            task_id="DEV-MATH-001",
            task_family_id="mathematical_verifiable",
            prompt="Return the integer value of 7 * 8.",
            expected=56,
        ),
    )
