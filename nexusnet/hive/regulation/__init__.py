"""Homeostatic self-regulation layer (canon C35 6.8/6.9/6.11 + C39 Consequence Memory).

Keeps the hive stable and self-correcting: consequence feedback, memory hygiene, immune anomaly
veto, and metacognitive reflection. All deterministic, shadow-only - they raise signals and propose
adjustments; the existing governance gates still decide.
"""
from __future__ import annotations

from .consequence_memory import ConsequenceMemory
from .selective_memory_decay import decay_step
from .neural_immune_system import anomaly_score, screen
from .meta_reflection import reflect

__all__ = [
    "ConsequenceMemory",
    "decay_step",
    "anomaly_score",
    "screen",
    "reflect",
]
