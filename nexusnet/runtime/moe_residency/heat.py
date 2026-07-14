from __future__ import annotations

from dataclasses import dataclass


@dataclass
class _HeatState:
    heat: int = 0
    last_used_sequence: int = 0


class ExpertHeatPolicy:
    """Frequency-first, recency-tie-breaking expert pinning with hysteresis."""

    def __init__(self, *, slot_count: int, hysteresis: float = 0.25) -> None:
        if slot_count < 0:
            raise ValueError("slot_count must be non-negative")
        if hysteresis < 0:
            raise ValueError("hysteresis must be non-negative")
        self.slot_count = slot_count
        self.hysteresis = hysteresis
        self._sequence = 0
        self._states: dict[str, _HeatState] = {}
        self._pinned: tuple[str, ...] = ()

    def touch(self, expert_ref: str, *, count: int = 1) -> None:
        if not expert_ref:
            raise ValueError("expert_ref is required")
        if count <= 0:
            raise ValueError("count must be positive")
        self._sequence += 1
        state = self._states.setdefault(expert_ref, _HeatState())
        state.heat += count
        state.last_used_sequence = self._sequence

    def heat(self, expert_ref: str) -> int:
        return self._states.get(expert_ref, _HeatState()).heat

    def score(self, expert_ref: str) -> int:
        state = self._states[expert_ref]
        return (state.heat << 8) + state.last_used_sequence

    def decay(self) -> None:
        for state in self._states.values():
            state.heat //= 2

    def repin(self) -> tuple[str, ...]:
        if self.slot_count == 0 or not self._states:
            self._pinned = ()
            return self._pinned

        ordered = sorted(self._states, key=self.score, reverse=True)
        pinned = [ref for ref in self._pinned if ref in self._states][: self.slot_count]
        for candidate in ordered:
            if candidate in pinned:
                continue
            if len(pinned) < self.slot_count:
                pinned.append(candidate)
                continue
            weakest = min(pinned, key=self.score)
            required = self.score(weakest) * (1.0 + self.hysteresis)
            if self.score(candidate) > required:
                pinned[pinned.index(weakest)] = candidate
        pinned.sort(key=self.score, reverse=True)
        self._pinned = tuple(pinned)
        return self._pinned
    @property
    def pinned(self) -> tuple[str, ...]:
        return self._pinned
