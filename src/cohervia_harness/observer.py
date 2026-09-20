from __future__ import annotations

from dataclasses import dataclass

from .events import Event


@dataclass(frozen=True, slots=True)
class ObserverConfig:
    allowed_event_kinds: frozenset[str]
    warning_event_count: int

    def __post_init__(self) -> None:
        if self.warning_event_count < 1:
            raise ValueError("warning_event_count must be positive")


class InstrumentationObserver:
    """Frozen development observer.

    This is not the confirmatory Cohervia observer. It exists only to test the
    harness event path and warning plumbing.
    """

    def __init__(self, config: ObserverConfig) -> None:
        self._config = config
        self._seen = 0
        self._first_warning_event_id: str | None = None

    @property
    def first_warning_event_id(self) -> str | None:
        return self._first_warning_event_id

    def observe(self, event: Event) -> None:
        if event.kind not in self._config.allowed_event_kinds:
            return
        self._seen += 1
        if (
            self._first_warning_event_id is None
            and self._seen >= self._config.warning_event_count
        ):
            self._first_warning_event_id = event.event_id
