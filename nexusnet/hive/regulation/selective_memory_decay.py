"""Selective Memory Decay (canon C35 6.9): memory hygiene.

Memory strengths decay over time unless reinforced by access; strengths that fall below a floor are
pruned. Salient/accessed memories are refreshed, low-value ones fade - keeping the store bounded
without losing important knowledge. Deterministic, shadow-only.

Invariant: an unaccessed memory's strength is strictly non-increasing each step; an accessed memory
is refreshed (does not decay below its reinforcement).
"""
from __future__ import annotations

from typing import Any


def decay_step(
    *,
    strengths: dict[str, float],
    accessed: dict[str, float] | None = None,
    decay_rate: float = 0.1,
    prune_floor: float = 0.05,
) -> dict[str, Any]:
    if not 0.0 < decay_rate < 1.0:
        raise ValueError("decay_rate must be in (0, 1)")
    accessed = accessed or {}
    updated: dict[str, float] = {}
    pruned: list[str] = []
    for key, strength in strengths.items():
        decayed = strength * (1.0 - decay_rate)
        if key in accessed:
            # Reinforcement refreshes the trace: take the stronger of decayed vs reinforcement.
            decayed = max(decayed, accessed[key])
        if decayed < prune_floor:
            pruned.append(key)
        else:
            updated[key] = decayed
    return {
        "strengths": updated,
        "pruned": pruned,
        "prune_floor": prune_floor,
        "production_mutation_allowed": False,
    }
