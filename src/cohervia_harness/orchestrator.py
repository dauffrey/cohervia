from __future__ import annotations

from .agent import Agent
from .audit import AppendOnlyAuditLog
from .events import Event
from .memory import GovernedMemory
from .models import EvidenceQuality, Partition, TrialConfig, TrialResult
from .observer import InstrumentationObserver
from .stop_controller import ExternalStopController
from .tasks import DevelopmentTask
from .verifier import Verifier


class InstrumentationRunner:
    """Development-only runner for testing the experimental apparatus."""

    def __init__(
        self,
        *,
        verifier: Verifier,
        observer: InstrumentationObserver,
        stop_controller: ExternalStopController,
    ) -> None:
        self._verifier = verifier
        self._observer = observer
        self._stop = stop_controller

    def run(
        self,
        *,
        config: TrialConfig,
        task: DevelopmentTask,
        agent: Agent,
    ) -> TrialResult:
        config.validate_for_harness(allow_confirmatory=False)
        if config.partition not in {
            Partition.INSTRUMENTATION,
            Partition.DEVELOPMENT,
        }:
            raise PermissionError("only development/instrumentation runs are enabled")

        audit = AppendOnlyAuditLog()
        memory = GovernedMemory(audit=audit)
        memory.begin_trial(config.trial_id)

        def emit(kind: str, payload: dict[str, object] | None = None) -> Event:
            event = Event.create(
                trial_id=config.trial_id,
                actor=agent.identity,
                kind=kind,
                payload=payload,
                sequence=len(audit.records),
            )
            audit.append(event)
            self._observer.observe(event)
            self._stop.observe(event)
            return event

        emit("trial_started", {"task_id": task.task_id})
        if self._stop.decision.paused:
            return self._paused_result(config, audit)

        answer = agent.solve(task)
        emit("agent_answer", {"task_id": task.task_id})

        result = self._verifier.verify(expected=task.expected, actual=answer)
        emit("verifier_result", {"status": result.status, "score": result.score})

        completed = not self._stop.decision.paused
        return TrialResult(
            trial_id=config.trial_id,
            partition=config.partition,
            completed=completed,
            paused=self._stop.decision.paused,
            score=result.score,
            verifier_result=result.status,
            first_divergence_event_id=self._observer.first_warning_event_id,
            audit_root_hash=audit.root_hash,
            event_count=len(audit.records),
            metadata={
                "task_id": task.task_id,
                "task_family_id": task.task_family_id,
                "evidence_quality": (
                    EvidenceQuality.INSTRUMENTATION.value
                    if config.partition == Partition.INSTRUMENTATION
                    else EvidenceQuality.EXPLORATORY.value
                ),
                "audit_chain_valid": audit.verify(),
            },
        )

    def _paused_result(
        self,
        config: TrialConfig,
        audit: AppendOnlyAuditLog,
    ) -> TrialResult:
        return TrialResult(
            trial_id=config.trial_id,
            partition=config.partition,
            completed=False,
            paused=True,
            score=None,
            verifier_result="not_applicable",
            first_divergence_event_id=self._observer.first_warning_event_id,
            audit_root_hash=audit.root_hash,
            event_count=len(audit.records),
            metadata={
                "pause_reason": self._stop.decision.reason,
                "audit_chain_valid": audit.verify(),
            },
        )
