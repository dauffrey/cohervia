"""Explicitly opt-in guarded provider adapter for the existing qualification harness.

This module does not enable live execution in GitHub Actions. Pricing must be
reviewed and provided by the operator; unknown prices fail closed.
"""
from __future__ import annotations

from decimal import Decimal

from budget_guard import BudgetDenied, Pricing, ReservationBudget

MAX_OUTPUT_TOKENS = 8000


class GuardedOpenAIProvider:
    """Reserve worst-case request cost before invoking the existing provider."""

    def __init__(self, underlying, budget: ReservationBudget):
        if underlying.model != budget.pricing.model:
            raise BudgetDenied("Underlying provider model mismatch")
        self.underlying = underlying
        self.budget = budget
        self.model = underlying.model
        self.reasoning_effort = underlying.reasoning_effort

    def complete(self, *, instructions: str, prompt: str) -> str:
        if not isinstance(instructions, str) or not isinstance(prompt, str):
            raise BudgetDenied("Prompt must be text")
        # Conservative estimate for ordinary byte-encoded tokenizers; it must
        # be validated against the selected model's tokenizer and API accounting
        # before production use. Hidden/provider overhead is not established.
        prompt_bytes = len(instructions.encode("utf-8")) + len(prompt.encode("utf-8"))
        if prompt_bytes == 0:
            raise BudgetDenied("Empty prompt")
        self.budget.reserve(model=self.model, maximum_input_tokens=prompt_bytes,
                            maximum_output_tokens=MAX_OUTPUT_TOKENS)
        return self.underlying.complete(instructions=instructions, prompt=prompt)


def make_guarded_provider(underlying, *, model: str, input_rate: str, output_rate: str,
                          budget: ReservationBudget | None = None):
    pricing = Pricing(model, Decimal(input_rate), Decimal(output_rate))
    active_budget = budget if budget is not None else ReservationBudget(pricing)
    if active_budget.pricing != pricing:
        raise BudgetDenied("Budget pricing mismatch")
    return GuardedOpenAIProvider(underlying, active_budget)
