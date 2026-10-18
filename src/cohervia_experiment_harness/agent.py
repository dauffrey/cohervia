from __future__ import annotations

from typing import Protocol

from .tasks import DevelopmentTask


class Agent(Protocol):
    identity: str

    def solve(self, task: DevelopmentTask) -> object:
        ...


class ScriptedDevelopmentAgent:
    """Deterministic stand-in used to exercise the harness plumbing."""

    identity = "scripted-development-agent-v1"

    def solve(self, task: DevelopmentTask) -> object:
        if task.task_id == "DEV-ALG-001":
            return [1, 2, 3]
        if task.task_id == "DEV-MATH-001":
            return 56
        raise KeyError(task.task_id)
