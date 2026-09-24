from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Protocol


class ReasoningProvider(Protocol):
    def complete(self, *, instructions: str, prompt: str) -> str:
        """Return model text for one bounded reasoning role."""


@dataclass
class OpenAIProvider:
    model: str = "gpt-5.6-sol"
    reasoning_effort: str = "high"
    api_key: str | None = None

    def __post_init__(self) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - packaging failure
            raise RuntimeError(
                "OpenAI provider requires the 'openai' package"
            ) from exc
        self._client = OpenAI(api_key=self.api_key)

    def complete(self, *, instructions: str, prompt: str) -> str:
        response = self._client.responses.create(
            model=self.model,
            instructions=instructions,
            input=prompt,
            reasoning={"effort": self.reasoning_effort},
        )
        text = getattr(response, "output_text", None)
        if not text:
            raise RuntimeError("reasoning provider returned no text output")
        return str(text)


class ScriptedProvider:
    """Deterministic provider for tests and offline pipeline validation."""

    def __init__(self, responses: list[str]):
        self._responses = deque(responses)
        self.calls: list[dict[str, str]] = []

    def complete(self, *, instructions: str, prompt: str) -> str:
        self.calls.append({"instructions": instructions, "prompt": prompt})
        if not self._responses:
            raise RuntimeError("scripted provider has no remaining responses")
        return self._responses.popleft()
