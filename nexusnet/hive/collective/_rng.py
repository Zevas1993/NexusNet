"""Deterministic, dependency-free PRNG (LCG) so swarm/DE runs are exactly reproducible.

Numerical Recipes LCG constants. Not for cryptography - only for replayable shadow-mode search.
"""
from __future__ import annotations


class DeterministicRNG:
    _A = 1664525
    _C = 1013904223
    _M = 2 ** 32

    def __init__(self, seed: int = 0) -> None:
        self._state = seed % self._M

    def random(self) -> float:
        """Uniform float in [0, 1)."""
        self._state = (self._A * self._state + self._C) % self._M
        return self._state / self._M

    def uniform(self, low: float, high: float) -> float:
        return low + (high - low) * self.random()

    def randint(self, low: int, high_inclusive: int) -> int:
        span = high_inclusive - low + 1
        return low + int(self.random() * span) % span
