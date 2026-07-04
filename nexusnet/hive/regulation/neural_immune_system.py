"""Neural Immune System (canon C35 6.8): anomaly detection + quarantine stop-signal.

Scores a candidate against a baseline distribution (mean/std per feature) and flags out-of-
distribution candidates for quarantine - the immune veto that raises the hive's stop-signal (pairs
with quorum.quorum_decision). Deterministic, shadow-only: it raises a signal; the governance gate
still decides.

Invariant: an in-distribution candidate is not quarantined; a far out-of-distribution candidate is.
"""
from __future__ import annotations

import math
from typing import Any

Vector = list[float]


def anomaly_score(*, candidate: Vector, baseline_mean: Vector, baseline_std: Vector) -> float:
    """Mean absolute z-score across features (robust, scale-free)."""
    if not (len(candidate) == len(baseline_mean) == len(baseline_std)):
        raise ValueError("candidate, mean, std must align")
    zs = [
        abs(candidate[i] - baseline_mean[i]) / (baseline_std[i] + 1e-9)
        for i in range(len(candidate))
    ]
    return sum(zs) / len(zs)


def screen(
    *,
    candidate: Vector,
    baseline_mean: Vector,
    baseline_std: Vector,
    z_threshold: float = 3.0,
) -> dict[str, Any]:
    score = anomaly_score(
        candidate=candidate, baseline_mean=baseline_mean, baseline_std=baseline_std
    )
    quarantine = score > z_threshold
    return {
        "anomaly_score": score,
        "z_threshold": z_threshold,
        "quarantine": quarantine,
        "stop_signal": quarantine,          # feeds quorum.quorum_decision(stop_signal=...)
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
