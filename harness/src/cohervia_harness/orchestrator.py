from __future__ import annotations
from dataclasses import asdict

from .agent import Agent, ScriptedDevelopmentAgent
from .audit import AppendOnlyAuditLog
from .canonical import hash_object
from .events import Event
from .memory import GovernedMemory
from .models import EvidenceQuality, Partition, TrialConfig, TrialResult
from .observer import InstrumentationObserver
from .stop_controller import ExternalStopController
from .tasks import DevelopmentTask, development_tasks
from .verifier import Verifier, ExactMatchVerifier


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
        config.validate_for_harness()
        # This is a local apparatus self-test, not a sandbox for arbitrary code.
        # Reject before accessing agent, task, observer or stop-controller methods.
        if (type(agent) is not ScriptedDevelopmentAgent
                or type(task) is not DevelopmentTask
                or type(self._verifier) is not ExactMatchVerifier
                or type(self._observer) is not InstrumentationObserver
                or type(self._stop) is not ExternalStopController):
            raise PermissionError("only reviewed scripted apparatus fixtures are enabled")
        if task not in development_tasks():
            raise PermissionError("only public development task fixtures are enabled")
        if config.model_identity != ScriptedDevelopmentAgent.identity:
            raise ValueError("model identity must identify the scripted fixture")
        if config.task_family_id != task.task_family_id:
            raise ValueError("trial config task_family_id does not match task")
        self._observer.begin_trial()
        self._stop.begin_trial()
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

        emit("trial_started", {"task_id": task.task_id,
                               "task_sha256": hash_object(asdict(task)),
                               "trial_config_sha256": hash_object(asdict(config))})
        if self._stop.decision.paused:
            return self._paused_result(config, audit)

        answer = agent.solve(task)
        emit("agent_answer", {"task_id": task.task_id, "answer_sha256": hash_object(answer)})

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
                ),
                "audit_chain_valid": audit.verify(),
                "scientific_evidence": False,
                "execution_authorized": False,
                "apparatus_mode": "scripted_fixture_instrumentation",
                "trial_config": asdict(config),
                "task": asdict(task),
                "actual_answer": answer,
                "audit_records": [asdict(r) for r in audit.records],
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
                "evidence_quality": EvidenceQuality.INSTRUMENTATION.value,
                "scientific_evidence": False,
                "execution_authorized": False,
            },
        )
