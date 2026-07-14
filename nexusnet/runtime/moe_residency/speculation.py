from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class SpeculationProfileState:
    profile_ref: str
    enabled: bool
    reason: str
    trials: int
    baseline_seconds: float
    candidate_seconds: float
    accepted: int
    proposed: int
    acceptance_rate: float
    speedup: float


@dataclass
class _Accumulator:
    trials: int = 0
    baseline_seconds: float = 0.0
    candidate_seconds: float = 0.0
    accepted: int = 0
    proposed: int = 0
    enabled: bool = True
    reason: str = "warming"


class AdaptiveSpeculationController:
    """Profile-scoped speculation gate driven by measured end-to-end benefit."""

    def __init__(self, *, min_trials: int = 3, min_speedup: float = 1.02) -> None:
        if min_trials <= 0:
            raise ValueError("min_trials must be positive")
        if min_speedup <= 0:
            raise ValueError("min_speedup must be positive")
        self.min_trials = min_trials
        self.min_speedup = min_speedup
        self._profiles: dict[str, _Accumulator] = {}

    def observe(
        self,
        profile_ref: str,
        *,
        baseline_seconds: float,
        candidate_seconds: float,
        accepted: int,
        proposed: int,
    ) -> SpeculationProfileState:
        if not profile_ref:
            raise ValueError("profile_ref is required")
        if baseline_seconds <= 0 or candidate_seconds <= 0:
            raise ValueError("timings must be positive")
        if proposed < 0 or accepted < 0 or accepted > proposed:
            raise ValueError("accepted/proposed counts are invalid")
        profile = self._profiles.setdefault(profile_ref, _Accumulator())
        profile.trials += 1
        profile.baseline_seconds += baseline_seconds
        profile.candidate_seconds += candidate_seconds
        profile.accepted += accepted
        profile.proposed += proposed
        speedup = profile.baseline_seconds / profile.candidate_seconds
        if profile.enabled and profile.trials >= self.min_trials:
            if speedup < self.min_speedup:
                profile.enabled = False
                profile.reason = "non_positive_end_to_end_benefit"
            else:
                profile.reason = "measured_positive_benefit"
        return self.state(profile_ref)

    def enabled(self, profile_ref: str) -> bool:
        return self._profiles.get(profile_ref, _Accumulator()).enabled

    def state(self, profile_ref: str) -> SpeculationProfileState:
        profile = self._profiles.get(profile_ref, _Accumulator())
        acceptance_rate = profile.accepted / profile.proposed if profile.proposed else 0.0
        speedup = (
            profile.baseline_seconds / profile.candidate_seconds
            if profile.candidate_seconds
            else 0.0
        )
        return SpeculationProfileState(
            profile_ref=profile_ref,
            enabled=profile.enabled,
            reason=profile.reason,
            trials=profile.trials,
            baseline_seconds=profile.baseline_seconds,
            candidate_seconds=profile.candidate_seconds,
            accepted=profile.accepted,
            proposed=profile.proposed,
            acceptance_rate=acceptance_rate,
            speedup=speedup,
        )

    def decode(
        self,
        profile_ref: str,
        *,
        target_only: Callable[..., T],
        speculative: Callable[..., T],
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
    ) -> T:
        decoder = speculative if self.enabled(profile_ref) else target_only
        return decoder(*args, **dict(kwargs or {}))
