from __future__ import annotations

from dataclasses import asdict

from .canonical import canonical_json

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
        self._audit_logs: dict[str, AppendOnlyAuditLog] = {}

    def export_audit(self, trial_id: str) -> str:
        """Return canonical, recomputable JSON for a completed or paused development trial."""
        return canonical_json([asdict(record) for record in self._audit_logs[trial_id].records])

    def run(
        self,
        *,
        config: TrialConfig,
        task: DevelopmentTask,
        agent: Agent,
    ) -> TrialResult:
        config.validate_for_harness()
        if config.task_family_id != task.task_family_id:
            raise ValueError("trial config task_family_id does not match task")
        self._observer.begin_trial()
        self._stop.begin_trial()
        if config.partition not in {
            Partition.INSTRUMENTATION,
            Partition.DEVELOPMENT,
        }:
            raise PermissionError("only development/instrumentation runs are enabled")

        if config.trial_id in self._audit_logs:
            raise ValueError("trial_id already recorded; refusing to overwrite audit evidence")
        audit = AppendOnlyAuditLog()
        self._audit_logs[config.trial_id] = audit
        memory = GovernedMemory(audit=audit)
        memory.begin_trial(config.trial_id)

        def emit(kind: str, payload: dict[str, object] | None = None, *, actor: str | None = None) -> Event:
            event = Event.create(
                trial_id=config.trial_id,
                actor=agent.identity if actor is None else actor,
                kind=kind,
                payload=payload,
                sequence=len(audit.records),
            )
            audit.append(event)
            self._observer.observe(event)
            self._stop.observe(event)
            return event

        emit("trial_started", {
            "task_id": task.task_id,
            "task_family_id": config.task_family_id,
            "experiment_id": config.experiment_id,
            "partition": config.partition.value,
            "system_configuration_hash": config.system_configuration_hash,
            "model_identity": config.model_identity,
        })
        if self._stop.decision.paused:
            return self._paused_result(config, audit)

        answer = agent.solve(task)
        emit("agent_answer", {"task_id": task.task_id})

        result = self._verifier.verify(expected=task.expected, actual=answer)
        verifier_id = type(self._verifier).__module__ + "." + type(self._verifier).__qualname__
        emit("verifier_result", {"status": result.status, "score": result.score}, actor=verifier_id)

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
