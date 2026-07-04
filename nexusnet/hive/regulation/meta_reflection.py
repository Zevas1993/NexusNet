"""Meta-Reflection (canon C35 6.11): metacognitive self-monitoring.

Summarizes recent decision confidences and outcome errors into a self-assessment and a recommended
extra deliberation budget (more EBT steps when calibration is poor / error is high). Deterministic,
shadow-only. Pairs with the EBT deliberation budget (hive.kernel.ebt).

Invariant: higher mean error => greater-or-equal suggested extra deliberation (monotone).
"""
from __future__ import annotations

from typing import Any

Vector = list[float]


def reflect(*, confidences: Vector, errors: Vector, max_extra_steps: int = 8) -> dict[str, Any]:
    if len(confidences) != len(errors):
        raise ValueError("confidences and errors must align")
    if not confidences:
        raise ValueError("need at least one observation")
    mean_conf = sum(confidences) / len(confidences)
    mean_err = sum(errors) / len(errors)
    # Calibration gap: confident AND wrong is the dangerous quadrant.
    calibration_gap = max(0.0, mean_conf - (1.0 - mean_err))
    # More error -> more deliberation (clamped, monotone in mean_err).
    suggested_extra = round(min(1.0, mean_err) * max_extra_steps)
    return {
        "mean_confidence": mean_conf,
        "mean_error": mean_err,
        "calibration_gap": calibration_gap,
        "overconfident": calibration_gap > 0.1,
        "suggested_extra_deliberation": suggested_extra,
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
