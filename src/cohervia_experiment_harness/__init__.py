"""Instrumentation-only runtime for COH-EXP-0001.

This package deliberately refuses confirmatory partitions by default.
"""

from .models import EvidenceQuality, Partition, TrialConfig, TrialResult

__all__ = ["EvidenceQuality", "Partition", "TrialConfig", "TrialResult"]
