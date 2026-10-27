"""Offline adapter tests: no API key or network requests."""
import sys
import unittest
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "qualification"))
from budget_guard import BudgetDenied, Pricing, ReservationBudget
from guarded_provider import GuardedOpenAIProvider


class FakeProvider:
    model = "test-model"
    reasoning_effort = "high"

    def __init__(self):
        self.calls = 0

    def complete(self, *, instructions, prompt):
        self.calls += 1
        return "{}"


class GuardedProviderTests(unittest.TestCase):
    def test_denied_call_never_reaches_provider(self):
        fake = FakeProvider()
        budget = ReservationBudget(Pricing("test-model", Decimal("100"), Decimal("100")),
                                   ceiling_usd=Decimal("0.01"))
        guarded = GuardedOpenAIProvider(fake, budget)
        with self.assertRaises(BudgetDenied):
            guarded.complete(instructions="instructions", prompt="prompt")
        self.assertEqual(fake.calls, 0)

    def test_allowed_call_is_reserved_before_provider(self):
        fake = FakeProvider()
        budget = ReservationBudget(Pricing("test-model", Decimal("0"), Decimal("1")))
        guarded = GuardedOpenAIProvider(fake, budget)
        self.assertEqual(guarded.complete(instructions="a", prompt="b"), "{}")
        self.assertEqual(fake.calls, 1)
        self.assertEqual(budget.calls, 1)
        self.assertEqual(budget.reserved, Decimal("0.008"))

    def test_model_mismatch_denied(self):
        with self.assertRaises(BudgetDenied):
            GuardedOpenAIProvider(FakeProvider(), ReservationBudget(
                Pricing("different-model", Decimal("1"), Decimal("1"))))


if __name__ == "__main__":
    unittest.main()
