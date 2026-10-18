import json
import unittest

from cohervia_experiment_harness.audit import AppendOnlyAuditLog
from cohervia_experiment_harness.events import Event

from cohervia_experiment_harness.agent import ScriptedDevelopmentAgent
from cohervia_experiment_harness.canonical import hash_object
from cohervia_experiment_harness.models import Partition, TrialConfig
from cohervia_experiment_harness.observer import InstrumentationObserver, ObserverConfig
from cohervia_experiment_harness.orchestrator import InstrumentationRunner
from cohervia_experiment_harness.stop_controller import ExternalStopController
from cohervia_experiment_harness.tasks import development_tasks
from cohervia_experiment_harness.verifier import ExactMatchVerifier


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

    def test_audit_export_preserves_config_and_independent_verifier(self):
        task = development_tasks()[0]
        config = TrialConfig(
            experiment_id="COH-EXP-0001",
            trial_id="AUDIT-TEST-1",
            task_family_id=task.task_family_id,
            partition=Partition.DEVELOPMENT,
            system_configuration_hash="frozen-configuration-identity",
            model_identity=self.agent.identity,
        )
        result = self.runner.run(config=config, task=task, agent=self.agent)
        records = json.loads(self.runner.export_audit(config.trial_id))
        self.assertEqual(result.event_count, len(records))
        start = records[0]["event"]["payload"]
        self.assertEqual(start["system_configuration_hash"], config.system_configuration_hash)
        self.assertEqual(start["model_identity"], config.model_identity)
        self.assertEqual(start["experiment_id"], config.experiment_id)
        self.assertEqual(start["partition"], config.partition.value)
        verifier_event = next(r["event"] for r in records if r["event"]["kind"] == "verifier_result")
        self.assertNotEqual(verifier_event["actor"], self.agent.identity)
        self.assertIn("ExactMatchVerifier", verifier_event["actor"])
        self.assertEqual(records[-1]["record_hash"], result.audit_root_hash)
        with self.assertRaises(ValueError):
            self.runner.run(config=config, task=task, agent=self.agent)

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
