"""Wave-13: regulation layer wired to the trainable net (real differentiable torch hooks).

The regulation modules (`hive/regulation/`) are deterministic-symbolic. These are the trainable
counterparts that actually modulate the network:

  - NeuralImmuneGate         detect anomalous activations (z-score vs running stats) and ATTENUATE
                             them before they propagate (a learned immune response). Differentiable.
  - consequence_weighted_loss weight per-sample loss by the consequence severity of getting it wrong
                             (high-consequence mistakes cost more) - canon Consequence memory.
  - SelectiveDecayRegularizer intentional forgetting on WEIGHTS: low-salience parameters decay faster
                             (canon Selective Memory Decay applied to the network itself).
"""
from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn


class NeuralImmuneGate(nn.Module):
    """Suppress pathological activations: outliers (|z| > threshold vs running stats) are clamped
    back toward the running mean. The gate uses detached statistics, so gradients still flow through
    accepted activations while anomalies are attenuated."""

    def __init__(self, dim: int, *, threshold: float = 4.0, momentum: float = 0.99) -> None:
        super().__init__()
        self.threshold = threshold
        self.momentum = momentum
        self.register_buffer("running_mean", torch.zeros(dim))
        self.register_buffer("running_var", torch.ones(dim))
        self.register_buffer("initialized", torch.tensor(0.0))

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, float]:
        flat = x.reshape(-1, x.shape[-1])
        if self.training:
            with torch.no_grad():
                bmean = flat.mean(dim=0)
                bvar = flat.var(dim=0, unbiased=False)
                if float(self.initialized) == 0.0:
                    self.running_mean.copy_(bmean)
                    self.running_var.copy_(bvar)
                    self.initialized.fill_(1.0)
                else:
                    self.running_mean.mul_(self.momentum).add_(bmean, alpha=1 - self.momentum)
                    self.running_var.mul_(self.momentum).add_(bvar, alpha=1 - self.momentum)
        std = (self.running_var + 1e-6).sqrt()
        z = (x - self.running_mean) / std
        mag = z.abs().detach()
        gate = torch.where(mag > self.threshold, self.threshold / mag.clamp(min=1e-6),
                           torch.ones_like(mag))                    # soft-clamp anomaly magnitude
        gated = self.running_mean + (x - self.running_mean) * gate
        anomaly_rate = float((mag > self.threshold).float().mean())
        return gated, anomaly_rate


def consequence_weighted_loss(per_sample_loss: torch.Tensor, consequence: torch.Tensor) -> torch.Tensor:
    """Weight each sample's loss by its consequence severity (>=0). High-consequence errors dominate."""
    w = consequence.clamp(min=0).to(per_sample_loss.dtype)
    if float(w.sum()) <= 0:
        return per_sample_loss.mean()
    return (w * per_sample_loss).sum() / w.sum()


class SelectiveDecayRegularizer:
    """Intentional forgetting on weights: parameter groups decay in proportion to (1 - salience),
    so rarely-useful weights are pruned toward zero over time while salient ones are preserved."""

    def __init__(self, base_decay: float = 1e-2) -> None:
        self.base_decay = base_decay

    @torch.no_grad()
    def apply(self, named_parameters, salience: dict[str, float]) -> dict[str, Any]:
        total_decay = 0.0
        touched = 0
        for name, p in named_parameters:
            s = max(0.0, min(1.0, salience.get(name, 1.0)))
            decay = self.base_decay * (1.0 - s)                    # low salience -> more decay
            if decay > 0:
                p.mul_(1.0 - decay)
                total_decay += decay
                touched += 1
        return {"total_decay": total_decay, "params_decayed": touched}
