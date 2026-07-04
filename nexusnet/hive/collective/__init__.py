"""Collective-intelligence layer: how many NexusNet brain instances coordinate, evolve, and
consolidate as one hive (canon Collective Intelligence Framework C37M0146 + substrate 2.2).

The neural side (capsules + EBT + MoE in hive.kernel) is HOW a single brain computes; this layer is
HOW the hive coordinates. All modules are pure-Python, deterministic, shadow-only: they PROPOSE;
the existing policy / eval / governance gates still DECIDE. No production mutation.
"""
from __future__ import annotations

from .stigmergy import PheromoneField
from .quorum import quorum_decision
from .swarm_consensus import pso_minimize
from .differential_evolution import differential_evolution
from .distillation import kd_loss, kl_divergence
from .neural_sleep import prioritized_replay, consolidate

__all__ = [
    "PheromoneField",
    "quorum_decision",
    "pso_minimize",
    "differential_evolution",
    "kd_loss",
    "kl_divergence",
    "prioritized_replay",
    "consolidate",
]
