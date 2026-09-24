from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Protocol


class ReasoningProvider(Protocol):
    def complete(self, *, instructions: str, prompt: str) -> str:
        """Return model text for one bounded reasoning role."""


@dataclass
class OpenAIProvider:
    model: str
    reasoning_effort: str = "high"
    api_key: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if not self.model.strip():
            raise ValueError("an explicit API model identifier is required")
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - packaging failure
            raise RuntimeError(
                "OpenAI provider requires the 'openai' package"
            ) from exc
        self._client = OpenAI(api_key=self.api_key, base_url="https://api.openai.com/v1",
                              timeout=60.0, max_retries=0)

    def complete(self, *, instructions: str, prompt: str) -> str:
        response = self._client.responses.create(
            model=self.model,
            instructions=instructions,
            input=prompt,
            reasoning={"effort": self.reasoning_effort},
            tools=[],
            store=False,
            max_output_tokens=8000,
        )
        if getattr(response, "status", None) != "completed":
            raise RuntimeError("reasoning provider response did not complete")
        if any(getattr(item, "type", "") not in {"message", "reasoning"}
               for item in getattr(response, "output", [])):
            raise RuntimeError("reasoning provider returned an unexpected tool output")
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
