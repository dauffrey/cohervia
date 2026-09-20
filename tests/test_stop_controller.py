import unittest

from cohervia_harness.events import Event
from cohervia_harness.stop_controller import ExternalStopController


class StopControllerTests(unittest.TestCase):
    def test_forbidden_event_pauses_run(self):
        controller = ExternalStopController()
        controller.begin_trial()
        event = Event.create(
            trial_id="T1",
            actor="agent",
            kind="holdout_access_attempt",
            payload={},
            sequence=0,
        )
        decision = controller.observe(event)
        self.assertTrue(decision.paused)
        self.assertEqual(decision.reason, "holdout_access_attempt")

    def test_safe_event_does_not_pause(self):
        controller = ExternalStopController()
        controller.begin_trial()
        event = Event.create(
            trial_id="T1",
            actor="agent",
            kind="agent_answer",
            payload={},
            sequence=0,
        )
        self.assertFalse(controller.observe(event).paused)


if __name__ == "__main__":
    unittest.main()
