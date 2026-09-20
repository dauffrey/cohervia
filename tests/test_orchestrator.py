import unittest

from cohervia_harness.agent import ScriptedDevelopmentAgent
from cohervia_harness.canonical import hash_object
from cohervia_harness.models import Partition, TrialConfig
from cohervia_harness.observer import InstrumentationObserver, ObserverConfig
from cohervia_harness.orchestrator import InstrumentationRunner
from cohervia_harness.stop_controller import ExternalStopController
from cohervia_harness.tasks import development_tasks
from cohervia_harness.verifier import ExactMatchVerifier


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.observer = InstrumentationObserver(
            ObserverConfig(
                allowed_event_kinds=frozenset({"agent_answer", "verifier_result"}),
                warning_event_count=2,
            )
        )
        self.runner = InstrumentationRunner(
            verifier=ExactMatchVerifier(),
            observer=self.observer,
            stop_controller=ExternalStopController(),
        )
        self.agent = ScriptedDevelopmentAgent()

    def test_development_trial_completes_with_valid_audit_chain(self):
        task = development_tasks()[0]
        config = TrialConfig(
            experiment_id="COH-EXP-0001",
            trial_id="DEV-1",
            task_family_id=task.task_family_id,
            partition=Partition.DEVELOPMENT,
            system_configuration_hash=hash_object({"mode": "development"}),
            model_identity=self.agent.identity,
        )
        result = self.runner.run(config=config, task=task, agent=self.agent)
        self.assertTrue(result.completed)
        self.assertFalse(result.paused)
        self.assertEqual(result.score, 1.0)
        self.assertTrue(result.metadata["audit_chain_valid"])
        self.assertEqual(result.metadata["evidence_quality"], "exploratory")

    def test_observer_state_resets_between_trials(self):
        first_task, second_task = development_tasks()
        first = TrialConfig(
            experiment_id="COH-EXP-0001",
            trial_id="DEV-1",
            task_family_id=first_task.task_family_id,
            partition=Partition.DEVELOPMENT,
            system_configuration_hash="a",
            model_identity=self.agent.identity,
        )
        second = TrialConfig(
            experiment_id="COH-EXP-0001",
            trial_id="DEV-2",
            task_family_id=second_task.task_family_id,
            partition=Partition.DEVELOPMENT,
            system_configuration_hash="b",
            model_identity=self.agent.identity,
        )
        r1 = self.runner.run(config=first, task=first_task, agent=self.agent)
        r2 = self.runner.run(config=second, task=second_task, agent=self.agent)
        self.assertIsNotNone(r1.first_divergence_event_id)
        self.assertIsNotNone(r2.first_divergence_event_id)
        self.assertNotEqual(r1.first_divergence_event_id, r2.first_divergence_event_id)


if __name__ == "__main__":
    unittest.main()
