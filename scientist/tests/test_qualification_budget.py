"""Offline-only tests for conservative budget reservation."""
import unittest
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'qualification'))
from budget_guard import BudgetDenied, Pricing, ReservationBudget


class ReservationBudgetTests(unittest.TestCase):
    def pricing(self):
        return Pricing("reviewed-model", Decimal("1"), Decimal("10"))

    def test_exact_ceiling_allowed_next_call_denied(self):
        budget = ReservationBudget(self.pricing(), ceiling_usd=Decimal("0.011"))
        self.assertEqual(budget.reserve(model="reviewed-model", maximum_input_tokens=1000, maximum_output_tokens=1000), Decimal("0.011"))
        with self.assertRaises(BudgetDenied):
            budget.reserve(model="reviewed-model", maximum_input_tokens=1000, maximum_output_tokens=1000)

    def test_unknown_or_invalid_pricing_denied(self):
        for rate in (Decimal("NaN"), Decimal("-1"), Decimal("Infinity")):
            with self.assertRaises(BudgetDenied):
                Pricing("reviewed-model", rate, Decimal("1"))

    def test_model_mismatch_denied(self):
        with self.assertRaises(BudgetDenied):
            ReservationBudget(self.pricing()).reserve(model="other", maximum_input_tokens=1, maximum_output_tokens=1)

    def test_bad_token_bounds_denied(self):
        for value in (0, -1, 1.0, True):
            with self.assertRaises(BudgetDenied):
                ReservationBudget(self.pricing()).reserve(model="reviewed-model", maximum_input_tokens=value, maximum_output_tokens=1)

    def test_call_cap(self):
        budget = ReservationBudget(self.pricing(), max_calls=1)
        budget.reserve(model="reviewed-model", maximum_input_tokens=1, maximum_output_tokens=1)
        with self.assertRaises(BudgetDenied):
            budget.reserve(model="reviewed-model", maximum_input_tokens=1, maximum_output_tokens=1)

    def test_concurrent_reservations_cannot_exceed_cap(self):
        budget = ReservationBudget(self.pricing(), ceiling_usd=Decimal("0.011"), max_calls=42)
        def attempt(_):
            try:
                budget.reserve(model="reviewed-model", maximum_input_tokens=1000, maximum_output_tokens=1000)
                return True
            except BudgetDenied:
                return False
        with ThreadPoolExecutor(max_workers=16) as pool:
            outcomes = list(pool.map(attempt, range(50)))
        self.assertEqual(sum(outcomes), 1)
        self.assertEqual(budget.reserved, Decimal("0.011"))


if __name__ == "__main__":
    unittest.main()
