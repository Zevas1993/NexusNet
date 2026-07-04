"""Wave-7: trainable JEPA world-model + SIGReg (real torch; the learnable dreaming counterpart).

`dreaming/world_model.py` measures JEPA latent-prediction error + Gaussian isotropy deterministically.
This is the TRAINABLE version: a Joint-Embedding Predictive Architecture that learns to predict the
representation of a masked/future part of a sequence FROM its context, entirely in latent space.

  - context encoder (trained) + target encoder (EMA copy, no gradient) -> predictor.
  - prediction loss is in latent space (JEPA): the predictor matches the EMA target's representation.
  - SIGReg (variance + covariance regularization, VICReg-style) keeps the latent space isotropic and
    prevents representation collapse; `gauss_dev` measures deviation from isotropic N(0, I).
  - the EMA target encoder is what stops collapse-to-constant without negatives.

Self-supervised: no labels - the model dreams (predicts its own future latents) and improves.
"""
from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F


class _Encoder(nn.Module):
    def __init__(self, d_model: int, hidden: int) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d_model, hidden), nn.GELU(), nn.Linear(hidden, d_model))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def sigreg(latents: torch.Tensor, *, eps: float = 1e-4) -> dict[str, torch.Tensor]:
    """Sketched Isotropic Gaussian Regularization (VICReg-style).

    variance term -> hinge that keeps per-dim std near 1 (anti-collapse);
    covariance term -> pushes off-diagonal covariance to 0 (decorrelate dims);
    gauss_dev -> scalar deviation from isotropic N(0, I) (mean^2 + (std-1)^2 + off-diag energy).
    """
    z = latents.reshape(-1, latents.shape[-1])
    n, d = z.shape
    mean = z.mean(dim=0)
    std = z.std(dim=0) + eps
    var_term = torch.relu(1.0 - std).mean()                       # want std >= 1
    zc = z - mean
    cov = (zc.T @ zc) / max(1, n - 1)
    off_diag = cov - torch.diag(torch.diag(cov))
    cov_term = off_diag.pow(2).sum() / d
    gauss_dev = mean.pow(2).mean() + (std - 1.0).pow(2).mean() + cov_term.detach()
    return {"var_term": var_term, "cov_term": cov_term, "gauss_dev": gauss_dev}


class JEPAWorldModel(nn.Module):
    """Predict the EMA-target representation of the target span from the context span (latent space)."""

    def __init__(self, d_model: int, hidden: int | None = None, *, ema: float = 0.99) -> None:
        super().__init__()
        hidden = hidden or 2 * d_model
        self.ema = ema
        self.context_encoder = _Encoder(d_model, hidden)
        self.target_encoder = _Encoder(d_model, hidden)
        self.predictor = nn.Sequential(nn.Linear(d_model, hidden), nn.GELU(), nn.Linear(hidden, d_model))
        # target encoder starts as a copy of the context encoder and is updated by EMA only.
        self.target_encoder.load_state_dict(self.context_encoder.state_dict())
        for p in self.target_encoder.parameters():
            p.requires_grad_(False)

    @torch.no_grad()
    def update_target(self) -> None:
        for tp, cp in zip(self.target_encoder.parameters(), self.context_encoder.parameters()):
            tp.mul_(self.ema).add_(cp, alpha=1.0 - self.ema)

    def forward(self, context: torch.Tensor, target: torch.Tensor) -> dict[str, torch.Tensor]:
        # pool spans -> context summary predicts target summary (both (B, d_model))
        ctx_sum = self.context_encoder(context).mean(dim=1)
        pred = self.predictor(ctx_sum)
        with torch.no_grad():
            tgt = self.target_encoder(target).mean(dim=1)
        pred_err = F.smooth_l1_loss(pred, tgt)
        return {"pred": pred, "target": tgt, "pred_err": pred_err}


def dream_step(
    jepa: JEPAWorldModel,
    sequence: torch.Tensor,
    optimizer: torch.optim.Optimizer,
    *,
    sigreg_weight: float = 0.04,
) -> dict[str, float]:
    """One self-supervised dream step: split (context | target), predict target latent, regularize, EMA."""
    B, T, D = sequence.shape
    split = max(1, T // 2)
    context, target = sequence[:, :split], sequence[:, split:]
    optimizer.zero_grad()
    out = jepa(context, target)
    reg = sigreg(jepa.context_encoder(context))
    loss = out["pred_err"] + sigreg_weight * (reg["var_term"] + reg["cov_term"])
    loss.backward()
    optimizer.step()
    jepa.update_target()
    return {
        "loss": float(loss.detach()),
        "pred_err": float(out["pred_err"].detach()),
        "gauss_dev": float(reg["gauss_dev"].detach()),
        "var_term": float(reg["var_term"].detach()),
    }


def train_world_model(
    jepa: JEPAWorldModel,
    sequences: torch.Tensor,
    *,
    steps: int = 80,
    lr: float = 3e-3,
    sigreg_weight: float = 0.04,
) -> dict[str, Any]:
    """Train the JEPA world-model on a batch of latent sequences. pred_err should fall as it learns."""
    optimizer = torch.optim.Adam((p for p in jepa.parameters() if p.requires_grad), lr=lr)
    hist: list[float] = []
    last: dict[str, float] = {}
    for _ in range(steps):
        last = dream_step(jepa, sequences, optimizer, sigreg_weight=sigreg_weight)
        hist.append(last["pred_err"])
    return {
        "pred_err_history": hist,
        "initial_pred_err": hist[0],
        "final_pred_err": hist[-1],
        "world_model_learned": hist[-1] < hist[0],
        "final_gauss_dev": last["gauss_dev"],
    }
