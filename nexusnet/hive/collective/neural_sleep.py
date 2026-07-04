"""Neural sleep / consolidation (canon Neural Sleep; hippocampal replay, target 117).

Wake = capture traces; sleep = replay important events (prioritized by salience), strengthen useful
patterns via a running EMA, and promote stable patterns into durable abstractions.

    replay distribution: p_i = softmax(salience)        (sums to 1)
    consolidation:       strength_i <- (1 - d) * strength_i + d * activation_i      (EMA)
    promotion:           abstraction if strength_i >= promote_threshold

Invariant: the replay distribution sums to 1. Pure-Python, deterministic, shadow-only - promotions
are proposals that still pass the downstream gates.
"""
from __future__ import annotations

from typing import Any

from ..kernel import tensor_ops as ops

Vector = list[float]


def prioritized_replay(*, saliences: list[float], replay_count: int) -> dict[str, Any]:
    """Replay distribution over traces (sums to 1) + the top-salience indices to replay."""
    if not saliences:
        raise ValueError("need at least one trace")
    distribution = ops.softmax(saliences)
    order = sorted(range(len(saliences)), key=lambda i: saliences[i], reverse=True)
    replayed = order[: max(0, min(replay_count, len(saliences)))]
    return {
        "distribution": distribution,
        "replayed_indices": replayed,
        "distribution_sums_to_one": abs(sum(distribution) - 1.0) < 1e-9,
    }


def consolidate(
    *,
    strengths: Vector,
    activations: Vector,
    decay: float = 0.2,
    promote_threshold: float = 0.7,
) -> dict[str, Any]:
    """EMA-strengthen patterns from this sleep cycle's activations; promote stable ones."""
    if len(strengths) != len(activations):
        raise ValueError("strengths and activations must align")
    if not 0.0 < decay <= 1.0:
        raise ValueError("decay must be in (0, 1]")
    updated = [
        (1.0 - decay) * s + decay * a for s, a in zip(strengths, activations)
    ]
    promoted = [i for i, s in enumerate(updated) if s >= promote_threshold]
    return {
        "updated_strengths": updated,
        "promoted_abstractions": promoted,
        "promote_threshold": promote_threshold,
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
