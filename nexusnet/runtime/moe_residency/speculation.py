from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from time import perf_counter
from typing import Any, Callable, Mapping, TypeVar


T = TypeVar("T")


def _outputs_equivalent(target: object, candidate: object) -> bool:
    if isinstance(target, Mapping) and isinstance(candidate, Mapping):
        return target.keys() == candidate.keys() and all(
            _outputs_equivalent(target[key], candidate[key]) for key in target
        )
    if isinstance(target, (list, tuple)) and isinstance(candidate, type(target)):
        return len(target) == len(candidate) and all(
            _outputs_equivalent(left, right) for left, right in zip(target, candidate)
        )
    try:
        comparison = target == candidate
    except Exception:
        return False
    if isinstance(comparison, bool):
        return comparison
    try:
        return bool(comparison.all().item())
    except (AttributeError, RuntimeError, TypeError, ValueError):
        return False


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

    def __init__(
        self,
        *,
        min_trials: int = 3,
        min_speedup: float = 1.02,
        clock: Callable[[], float] = perf_counter,
    ) -> None:
        if min_trials <= 0:
            raise ValueError("min_trials must be positive")
        if min_speedup <= 0:
            raise ValueError("min_speedup must be positive")
        self.min_trials = min_trials
        self.min_speedup = min_speedup
        self._clock = clock
        self._profiles: dict[str, _Accumulator] = {}
        self._lock = RLock()

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
        with self._lock:
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
        with self._lock:
            return self._profiles.get(profile_ref, _Accumulator()).enabled

    def state(self, profile_ref: str) -> SpeculationProfileState:
        with self._lock:
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

    def run(
        self,
        profile_ref: str,
        *,
        target_only: Callable[..., T],
        speculative: Callable[..., T],
        equivalent: Callable[[T, T], bool] | None = None,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
    ) -> T:
        """Calibrate a speculative path against target output and wall-clock latency."""
        call_kwargs = dict(kwargs or {})
        if not self.enabled(profile_ref):
            return target_only(*args, **call_kwargs)

        baseline_start = self._clock()
        baseline = target_only(*args, **call_kwargs)
        baseline_seconds = max(self._clock() - baseline_start, 1e-12)
        candidate_start = self._clock()
        try:
            candidate = speculative(*args, **call_kwargs)
        except Exception:
            with self._lock:
                profile = self._profiles.setdefault(profile_ref, _Accumulator())
                profile.enabled = False
                profile.reason = "candidate_execution_failed"
            return baseline
        candidate_seconds = max(self._clock() - candidate_start, 1e-12)

        verifier = equivalent or _outputs_equivalent
        try:
            equivalent_output = verifier(baseline, candidate)
        except Exception:
            self._disable(profile_ref, "target_verification_failed")
            return baseline
        if not equivalent_output:
            self._disable(profile_ref, "target_verification_mismatch")
            return baseline

        try:
            accepted, proposed = self._candidate_counts(candidate)
            state = self.observe(
                profile_ref,
                baseline_seconds=baseline_seconds,
                candidate_seconds=candidate_seconds,
                accepted=accepted,
                proposed=proposed,
            )
        except (TypeError, ValueError):
            self._disable(profile_ref, "candidate_accounting_invalid")
            return baseline
        return candidate if state.enabled else baseline

    def _disable(self, profile_ref: str, reason: str) -> None:
        with self._lock:
            profile = self._profiles.setdefault(profile_ref, _Accumulator())
            profile.enabled = False
            profile.reason = reason

    @staticmethod
    def _candidate_counts(candidate: object) -> tuple[int, int]:
        if not isinstance(candidate, Mapping):
            return (0, 0)
        accepted = candidate.get("accepted", 0)
        proposed = candidate.get("proposed", 0)
        if (
            isinstance(accepted, bool)
            or isinstance(proposed, bool)
            or not isinstance(accepted, int)
            or not isinstance(proposed, int)
        ):
            raise TypeError("candidate accepted/proposed counts must be integers")
        return accepted, proposed

    def decode(
        self,
        profile_ref: str,
        *,
        target_only: Callable[..., T],
        speculative: Callable[..., T],
        equivalent: Callable[[T, T], bool] | None = None,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
    ) -> T:
        return self.run(
            profile_ref,
            target_only=target_only,
            speculative=speculative,
            equivalent=equivalent,
            args=args,
            kwargs=kwargs,
        )
