"""B1 - The Capsule Neuron (canon C12M0048/0064; source: Capsule Networks 1710.09829).

The fundamental building block of NexusNet: a self-contained unit with input -> hidden -> output
layers that emits a POSE VECTOR. The vector's LENGTH is the probability the capsule's entity is
present (its routing confidence / inverse uncertainty for the Neural Bus tuple); its ORIENTATION
encodes instantiation parameters (the summary embedding). Pure-Python, deterministic, no numpy,
no production mutation - shadow-only evidence.

Composes the shipped tensor_ops primitives (rms_norm + swiglu) for the feed-forward, and the
capsule squash nonlinearity for the pose output.
"""
from __future__ import annotations

import math
from typing import Any

from . import tensor_ops as ops

Vector = list[float]


def squash(s: Vector, eps: float = 1e-12) -> Vector:
    """Capsule squash: squash(s) = (||s||^2 / (1 + ||s||^2)) * (s / ||s||).

    Shrinks the vector length into [0, 1) as a presence probability while preserving direction.
    Short vectors shrink toward 0; long vectors saturate just below 1.
    """
    sq = sum(x * x for x in s)
    length = math.sqrt(sq)
    scale = (sq / (1.0 + sq)) / (length + eps)
    return [x * scale for x in s]


def _weight_row(out_index: int, in_dim: int, *, salt: int) -> Vector:
    """Deterministic unit-norm weight row on the golden-angle phi-phase basis.

    No randomness: the same (out_index, in_dim, salt) always produces the same row, so a
    CapsuleNeuron is fully reproducible (shadow evidence must be replayable).
    """
    row = [
        math.cos((out_index + 1) * ops.GOLDEN_ANGLE_RADIANS * (i + 1) + salt * ops.PHI)
        for i in range(in_dim)
    ]
    return ops.l2_normalize(row)


def _project(matrix_rows: list[Vector], x: Vector) -> Vector:
    return [ops.dot(row, x) for row in matrix_rows]


class CapsuleNeuron:
    """A domain-specialized capsule: input -> hidden (SwiGLU) -> output -> squashed pose vector."""

    def __init__(self, *, domain_index: int, d_in: int, d_hidden: int, d_out: int) -> None:
        if min(d_in, d_hidden, d_out) <= 0:
            raise ValueError("capsule dimensions must be positive")
        self.domain_index = domain_index
        self.d_in = d_in
        self.d_hidden = d_hidden
        self.d_out = d_out
        # Deterministic weights. Distinct salts keep gate/value/output projections independent;
        # domain_index shifts the whole capsule so different experts occupy different phi phases.
        base = (domain_index + 1) * 7
        self._w_gate = [_weight_row(h, d_in, salt=base + 1) for h in range(d_hidden)]
        self._w_value = [_weight_row(h, d_in, salt=base + 2) for h in range(d_hidden)]
        self._w_out = [_weight_row(o, d_hidden, salt=base + 3) for o in range(d_out)]

    def forward(self, input_vec: Vector) -> dict[str, Any]:
        if len(input_vec) != self.d_in:
            raise ValueError(f"expected input dim {self.d_in}, got {len(input_vec)}")
        # 1. Pre-norm the input (RMSNorm) for stable activation magnitude.
        normed = ops.rms_norm(input_vec)
        # 2. SwiGLU feed-forward into the hidden layer.
        gate = _project(self._w_gate, normed)
        value = _project(self._w_value, normed)
        hidden = ops.swiglu(gate, value)
        # 3. Project hidden -> output pose, then squash into a presence-probability pose vector.
        pre_pose = _project(self._w_out, hidden)
        pose = squash(pre_pose)
        length = ops.norm(pose)
        return {
            "domain_index": self.domain_index,
            "pose": pose,
            "pose_length": length,          # presence probability in [0, 1)
            "uncertainty": 1.0 - length,    # Neural-Bus inverse of squash length
            "hidden_norm": round(ops.norm(hidden), 8),
            "production_mutation_allowed": False,
            "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
        }
