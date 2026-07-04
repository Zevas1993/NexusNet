"""CritiqueAO veto over risky dreams (canon addendum C/E: CritiqueAO is the dreaming governor).

Consumes the optional v2 signals (pred_err, gauss_dev, circuits_risk_score) and vetoes a dream if
any exceeds its threshold. The veto is a STOP-signal into the gated promotion pipeline - CritiqueAO
proposes the veto; governance still decides. Deterministic, shadow-only.

Invariant: a dream within all thresholds is not vetoed; a dream breaching any threshold is vetoed.
"""
from __future__ import annotations

from typing import Any


def critique_veto(
    *,
    pred_err: float,
    gauss_dev: float,
    circuits_risk_score: float,
    pred_err_max: float = 1.0,
    gauss_dev_max: float = 2.0,
    risk_max: float = 0.6,
) -> dict[str, Any]:
    reasons = []
    if pred_err > pred_err_max:
        reasons.append("pred_err_exceeded")
    if gauss_dev > gauss_dev_max:
        reasons.append("gauss_dev_exceeded")
    if circuits_risk_score > risk_max:
        reasons.append("circuit_risk_exceeded")
    vetoed = bool(reasons)
    return {
        "vetoed": vetoed,
        "stop_signal": vetoed,
        "reasons": reasons,
        "signals": {
            "pred_err": pred_err,
            "gauss_dev": gauss_dev,
            "circuits_risk_score": circuits_risk_score,
        },
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
