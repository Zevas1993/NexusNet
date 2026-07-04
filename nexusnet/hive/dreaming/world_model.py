"""Recursive Neural Dreaming v2 - JEPA world-model sidecar + SIGReg isotropy (canon addendum C).

Predict in LATENT space (JEPA): a deterministic latent predictor estimates the next latent from the
current one; `pred_err` is the prediction error. SIGReg (Sketched Isotropic Gaussian Regularization)
measures how far a batch of latents is from an isotropic Gaussian ~N(0, I): `gauss_dev`. A healthy
world-model dreams in a well-shaped latent space (low gauss_dev) and predicts well (low pred_err).
Deterministic, shadow-only.

Invariants: a batch drawn close to N(0,I) has low gauss_dev; a shifted/scaled batch has higher
gauss_dev. pred_err == 0 iff prediction equals target.
"""
from __future__ import annotations

import math
from typing import Any

from ..kernel import tensor_ops as ops

Vector = list[float]


def latent_predict(current: Vector, *, drift: float = 0.0) -> Vector:
    """Deterministic JEPA-style latent predictor: a norm-preserving golden-angle rotation."""
    out = list(current)
    for k in range(len(current) // 2):
        out[2 * k], out[2 * k + 1] = ops.rotary_pair(
            current[2 * k], current[2 * k + 1], position=1, k=k
        )
    return [x + drift for x in out]


def prediction_error(predicted: Vector, target: Vector) -> float:
    return ops.mse(predicted, target)


def sigreg_gauss_dev(latents: list[Vector]) -> float:
    """Deviation of a latent batch from N(0, I): ||mean||^2 + sum_d (var_d - 1)^2.

    Zero only when the batch has zero mean and unit per-dimension variance.
    """
    if not latents:
        raise ValueError("need at least one latent")
    n = len(latents)
    dim = len(latents[0])
    mean = [sum(v[d] for v in latents) / n for d in range(dim)]
    var = [sum((v[d] - mean[d]) ** 2 for v in latents) / n for d in range(dim)]
    mean_term = sum(m * m for m in mean)
    var_term = sum((vd - 1.0) ** 2 for vd in var)
    return mean_term + var_term


def world_model_signals(
    *, current_latents: list[Vector], next_latents: list[Vector], drift: float = 0.0
) -> dict[str, Any]:
    """JEPA pred_err over a batch + SIGReg gauss_dev on the predicted latents."""
    if len(current_latents) != len(next_latents):
        raise ValueError("current and next batches must align")
    preds = [latent_predict(c, drift=drift) for c in current_latents]
    errs = [prediction_error(p, t) for p, t in zip(preds, next_latents)]
    pred_err = sum(errs) / len(errs)
    gauss_dev = sigreg_gauss_dev(preds)
    return {
        "pred_err": pred_err,
        "gauss_dev": gauss_dev,
        "predicted_latents": preds,
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
