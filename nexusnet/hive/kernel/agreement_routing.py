"""B2 - Routing-by-agreement (canon: the principled router; source: Capsule Networks 1710.09829).

Lower capsules send their pose vectors to higher capsules via deterministic prediction transforms.
Coupling coefficients are refined iteratively so that a lower capsule routes mass to the higher
capsule whose prediction AGREES with the higher capsule's emergent pose (high dot product). This is
the principled version of the canon "reference-frame consensus router" (assimilation target 123):
consensus by agreement, not just a one-shot top-k softmax.

    c_ij = softmax_j(b_ij)                          (coupling sums to 1 over higher capsules)
    s_j  = sum_i c_ij * u_hat_{j|i}                 (higher capsule input)
    v_j  = squash(s_j)                              (higher capsule pose)
    b_ij += u_hat_{j|i} . v_j                       (agreement update)

Pure-Python, deterministic, shadow-only.
"""
from __future__ import annotations

from typing import Any

from . import tensor_ops as ops
from .capsule import _weight_row, squash, Vector


def _prediction_transform(i: int, j: int, d_lower: int, d_higher: int) -> list[Vector]:
    """Deterministic W_{j|i}: maps a lower pose (d_lower) into higher capsule j's space (d_higher)."""
    salt = (i + 1) * 31 + (j + 1) * 17
    return [_weight_row(o, d_lower, salt=salt + o) for o in range(d_higher)]


def route_by_agreement(
    lower_poses: list[Vector],
    *,
    num_higher: int,
    d_higher: int,
    iterations: int = 3,
) -> dict[str, Any]:
    if not lower_poses:
        raise ValueError("need at least one lower capsule pose")
    if num_higher <= 0 or d_higher <= 0:
        raise ValueError("num_higher and d_higher must be positive")
    n_lower = len(lower_poses)
    d_lower = len(lower_poses[0])

    # Per-(i,j) predictions u_hat_{j|i}.
    u_hat = [
        [
            [ops.dot(row, lower_poses[i]) for row in _prediction_transform(i, j, d_lower, d_higher)]
            for j in range(num_higher)
        ]
        for i in range(n_lower)
    ]

    logits = [[0.0] * num_higher for _ in range(n_lower)]  # b_ij
    coupling: list[Vector] = [[0.0] * num_higher for _ in range(n_lower)]
    higher_poses: list[Vector] = [[0.0] * d_higher for _ in range(num_higher)]
    mean_agreement_per_iter: list[float] = []

    for _ in range(max(1, iterations)):
        # Coupling: softmax over higher capsules, per lower capsule.
        coupling = [ops.softmax(logits[i]) for i in range(n_lower)]
        # Higher capsule inputs and squashed poses.
        for j in range(num_higher):
            s_j = [0.0] * d_higher
            for i in range(n_lower):
                c = coupling[i][j]
                for d in range(d_higher):
                    s_j[d] += c * u_hat[i][j][d]
            higher_poses[j] = squash(s_j)
        # Agreement update and bookkeeping.
        agreements: list[float] = []
        for i in range(n_lower):
            for j in range(num_higher):
                agree = ops.dot(u_hat[i][j], higher_poses[j])
                logits[i][j] += agree
                agreements.append(agree)
        mean_agreement_per_iter.append(sum(agreements) / len(agreements))

    return {
        "coupling": coupling,                       # n_lower x num_higher, each row sums to 1
        "higher_poses": higher_poses,               # num_higher squashed pose vectors
        "higher_pose_lengths": [ops.norm(p) for p in higher_poses],
        "mean_agreement_per_iter": mean_agreement_per_iter,
        "iterations": max(1, iterations),
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
