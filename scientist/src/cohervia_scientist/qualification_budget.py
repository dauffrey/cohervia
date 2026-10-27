"""Fail-closed conservative cost reservation for a future live qualification runner.

Not wired to the provider: no paid execution is enabled by this module.
Rates must be explicitly reviewed and passed in USD per million tokens.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from threading import Lock


class BudgetDenied(RuntimeError):
    pass


@dataclass(frozen=True)
class Pricing:
    model: str
    input_usd_per_million: Decimal
    output_usd_per_million: Decimal

    def __post_init__(self):
        if not self.model or not self.model.strip():
            raise BudgetDenied("Model must be pinned")
        for rate in (self.input_usd_per_million, self.output_usd_per_million):
            if not isinstance(rate, Decimal) or not rate.is_finite() or rate < 0:
                raise BudgetDenied("Unknown or invalid model pricing")


class ReservationBudget:
    def __init__(self, pricing: Pricing, ceiling_usd=Decimal("5"), max_calls=42):
        if not isinstance(ceiling_usd, Decimal) or not ceiling_usd.is_finite() or ceiling_usd <= 0:
            raise BudgetDenied("Invalid spending ceiling")
        if not isinstance(max_calls, int) or not 1 <= max_calls <= 42:
            raise BudgetDenied("Invalid call limit")
        self.pricing = pricing
        self.ceiling = ceiling_usd
        self.max_calls = max_calls
        self.reserved = Decimal(0)
        self.calls = 0
        self._lock = Lock()

    def reserve(self, *, model: str, maximum_input_tokens: int, maximum_output_tokens: int):
        if model != self.pricing.model:
            raise BudgetDenied("Unapproved model")
        for value in (maximum_input_tokens, maximum_output_tokens):
            if type(value) is not int or value <= 0:
                raise BudgetDenied("Token bounds must be positive integers")
        cost = ((Decimal(maximum_input_tokens) * self.pricing.input_usd_per_million)
                + (Decimal(maximum_output_tokens) * self.pricing.output_usd_per_million)) / Decimal(1_000_000)
        with self._lock:
            if self.calls >= self.max_calls or self.reserved + cost > self.ceiling:
                raise BudgetDenied("Call or worst-case cost ceiling reached")
            self.reserved += cost
            self.calls += 1
            return cost
