from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .agent import ScriptedDevelopmentAgent
from .archive import verify_trial_archive
from .canonical import hash_object
from .models import Partition, TrialConfig
from .observer import InstrumentationObserver, ObserverConfig
from .orchestrator import InstrumentationRunner
from .stop_controller import ExternalStopController
from .tasks import development_tasks
from .verifier import ExactMatchVerifier


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run COH-EXP-0001 instrumentation-only self-test"
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if not args.self_test:
        parser.print_help()
        return 0

    observer = InstrumentationObserver(
        ObserverConfig(
            allowed_event_kinds=frozenset({"agent_answer", "verifier_result"}),
            warning_event_count=2,
        )
    )
    runner = InstrumentationRunner(
        verifier=ExactMatchVerifier(),
        observer=observer,
        stop_controller=ExternalStopController(),
    )
    agent = ScriptedDevelopmentAgent()

    for index, task in enumerate(development_tasks(), start=1):
        config = TrialConfig(
            experiment_id="COH-EXP-0001",
            trial_id=f"INSTRUMENTATION-{index:03d}",
            task_family_id=task.task_family_id,
            partition=Partition.INSTRUMENTATION,
            system_configuration_hash=hash_object({"mode": "instrumentation"}),
            model_identity=agent.identity,
        )
        result = runner.run(config=config, task=task, agent=agent)
        archive = asdict(result)
        verify_trial_archive(archive)
        print(json.dumps(archive, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
