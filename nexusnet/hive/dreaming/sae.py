"""Sparse-circuit introspection via a Sparse Autoencoder (canon addendum C v2 dreaming).

Train-free deterministic SAE for SHADOW introspection: encode a capsule activation into sparse
features (ReLU then keep top-k), record which circuits fired, reconstruct, and compute a
`circuits_risk_score` from a per-circuit risk profile. Over time the system learns which circuits
produce high-value vs risky dreams. Deterministic, shadow-only.

Invariants: at most k features are active (sparsity); risk score in [0, 1]; an all-zero activation
fires no circuits and has zero risk.
"""
from __future__ import annotations

import math
from typing import Any

from ..kernel import tensor_ops as ops

Vector = list[float]


def _feature_row(f: int, dim: int) -> Vector:
    row = [math.cos((f + 1) * ops.GOLDEN_ANGLE_RADIANS * (i + 1)) for i in range(dim)]
    return ops.l2_normalize(row)


def encode_sparse(activation: Vector, *, num_features: int, top_k: int) -> dict[str, Any]:
    """Encode -> ReLU -> keep top-k features (sparse). Returns active features + codes."""
    raw = [max(0.0, ops.dot(_feature_row(f, len(activation)), activation)) for f in range(num_features)]
    ranked = sorted(range(num_features), key=lambda f: raw[f], reverse=True)
    active = [f for f in ranked[:top_k] if raw[f] > 0.0]
    codes = {f: raw[f] for f in active}
    return {"active_features": sorted(active), "codes": codes, "num_features": num_features}


def reconstruct(codes: dict[int, float], *, dim: int) -> Vector:
    out = [0.0] * dim
    for f, value in codes.items():
        row = _feature_row(f, dim)
        for i in range(dim):
            out[i] += value * row[i]
    return out


def circuits_risk_score(active_features: list[int], *, risk_profile: dict[int, float]) -> float:
    """Mean risk of the fired circuits (0 if none fired). Clamped to [0, 1]."""
    if not active_features:
        return 0.0
    total = sum(min(1.0, max(0.0, risk_profile.get(f, 0.0))) for f in active_features)
    return total / len(active_features)


def introspect(
    *, activation: Vector, num_features: int = 16, top_k: int = 3, risk_profile: dict[int, float] | None = None
) -> dict[str, Any]:
    enc = encode_sparse(activation, num_features=num_features, top_k=top_k)
    risk = circuits_risk_score(enc["active_features"], risk_profile=risk_profile or {})
    recon = reconstruct(enc["codes"], dim=len(activation))
    return {
        "circuits_used": enc["active_features"],
        "circuits_risk_score": risk,
        "reconstruction_error": ops.mse(recon, activation),
        "sparsity": len(enc["active_features"]),
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
