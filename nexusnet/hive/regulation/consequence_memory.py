"""Consequence Memory - the negative-experience bank (canon C39M0046 D; Aspect-7 consequence loop).

A pulsing feedback signal from outcomes back into routing/weights (RL-like credit assignment). The
bank records penalties against context signatures; on a new decision it returns an avoidance penalty
for the matching signature so the router can steer away from previously-bad routes. Penalties decay
over time so old mistakes fade (auditable, never a permanent silent bias). Shadow-only; deterministic.

Invariants: penalty >= 0; an unseen signature has 0 penalty; recording a penalty raises that
signature's penalty; decay lowers all penalties monotonically.
"""
from __future__ import annotations

from typing import Any


class ConsequenceMemory:
    def __init__(self, *, decay_rate: float = 0.05) -> None:
        if not 0.0 <= decay_rate < 1.0:
            raise ValueError("decay_rate must be in [0, 1)")
        self.decay_rate = decay_rate
        self._penalties: dict[str, float] = {}

    def record(self, *, signature: str, penalty: float) -> None:
        if penalty < 0.0:
            raise ValueError("penalty must be non-negative")
        self._penalties[signature] = self._penalties.get(signature, 0.0) + penalty

    def penalty_for(self, signature: str) -> float:
        return self._penalties.get(signature, 0.0)

    def avoidance_signal(self, signature: str, *, scale: float = 1.0) -> dict[str, Any]:
        """Routing penalty (>=0) to subtract from a candidate route's score."""
        penalty = self.penalty_for(signature) * scale
        return {
            "signature": signature,
            "penalty": penalty,
            "avoid": penalty > 0.0,
            "production_mutation_allowed": False,
        }

    def decay(self) -> None:
        """Fade every stored penalty; drop ones that round to ~0."""
        self._penalties = {
            sig: p * (1.0 - self.decay_rate)
            for sig, p in self._penalties.items()
            if p * (1.0 - self.decay_rate) > 1e-9
        }

    def snapshot(self) -> dict[str, float]:
        return dict(self._penalties)
