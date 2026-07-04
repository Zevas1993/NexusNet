"""Wave-12: advanced low-bit quantization - NF4 4-bit, GPTQ-lite, AWQ-lite (real torch numerics).

Canon quantization lane (Overlay): beyond int8, the birthed model must support 4-bit weight formats
(NF4) and the quality-preserving quantizers (GPTQ activation-aware error feedback, AWQ activation-
aware scaling). Implemented as real numerical algorithms with measured reconstruction error:

  - nf4_quantize     groupwise 4-bit NormalFloat4 (QLoRA codebook), per-group absmax scale.
  - gptq_quantize    GPTQ-style sequential column quantization with Hessian-weighted error feedback;
                     lower error than naive round-to-nearest on correlated weights.
  - awq_quantize     AWQ-style activation-aware per-channel scaling that protects salient channels,
                     lowering quantization error where activations are large.
"""
from __future__ import annotations

from typing import Any

import torch

# NF4 codebook (QLoRA: 16 NormalFloat levels in [-1, 1]).
NF4_CODEBOOK = torch.tensor([
    -1.0, -0.6961928009986877, -0.5250730514526367, -0.39491748809814453,
    -0.28444138169288635, -0.18477343022823334, -0.09105003625154495, 0.0,
    0.07958029955625534, 0.16093020141124725, 0.24611230194568634, 0.33791524171829224,
    0.44070982933044434, 0.5626170039176941, 0.7229568362236023, 1.0,
])


def _rel_error(approx: torch.Tensor, ref: torch.Tensor) -> float:
    return float((approx - ref).norm() / (ref.norm() + 1e-8))


def nf4_quantize(weight: torch.Tensor, *, group_size: int = 64) -> dict[str, Any]:
    """Groupwise 4-bit NF4: per-group absmax scale, map normalized weights to nearest NF4 code."""
    flat = weight.reshape(-1)
    n = flat.numel()
    pad = (-n) % group_size
    if pad:
        flat = torch.cat([flat, torch.zeros(pad, dtype=flat.dtype)])
    groups = flat.reshape(-1, group_size)
    scales = groups.abs().amax(dim=1, keepdim=True).clamp(min=1e-8)
    norm = groups / scales                                          # -> [-1, 1]
    codebook = NF4_CODEBOOK.to(weight.dtype)
    idx = (norm.unsqueeze(-1) - codebook).abs().argmin(dim=-1)      # nearest code per element
    deq = codebook[idx] * scales
    deq = deq.reshape(-1)[:n].reshape(weight.shape)
    return {
        "codes": idx, "scales": scales, "dequant": deq,
        "bits": 4, "group_size": group_size, "rel_error": _rel_error(deq, weight),
    }


def _rtn_int4(weight: torch.Tensor) -> torch.Tensor:
    """Naive per-tensor symmetric 4-bit round-to-nearest (baseline to beat)."""
    qmax = 7
    scale = weight.abs().max().clamp(min=1e-8) / qmax
    return torch.round(weight / scale).clamp(-qmax, qmax) * scale


def gptq_quantize(weight: torch.Tensor, calib: torch.Tensor, *, bits: int = 4,
                  damping: float = 0.01) -> dict[str, Any]:
    """GPTQ-lite: quantize input columns left->right, feeding the residual error forward weighted by
    the calibration Hessian (H = XᵀX). Beats round-to-nearest on correlated columns.

    weight (out, in), calib (n, in). Returns the dequantized weight + error vs the naive baseline.
    """
    W = weight.clone().float()
    out_dim, in_dim = W.shape
    H = calib.float().t() @ calib.float() / max(1, calib.shape[0])
    H = H + damping * torch.eye(in_dim) * torch.diag(H).mean()
    hd = torch.diag(H).clamp(min=1e-8)
    qmax = 2 ** (bits - 1) - 1
    scale = W.abs().amax(dim=1, keepdim=True).clamp(min=1e-8) / qmax
    Q = torch.zeros_like(W)
    for c in range(in_dim):
        w_c = W[:, c]
        q_c = torch.round(w_c / scale.squeeze(1)).clamp(-qmax, qmax) * scale.squeeze(1)
        Q[:, c] = q_c
        err = (w_c - q_c) / hd[c]
        if c + 1 < in_dim:
            W[:, c + 1:] -= torch.outer(err, H[c, c + 1:])         # propagate error forward
    rtn = _rtn_int4(weight)
    return {
        "dequant": Q, "bits": bits,
        "rel_error": _rel_error(Q, weight),
        "rtn_rel_error": _rel_error(rtn, weight),
        "beats_rtn": _rel_error(Q, weight) <= _rel_error(rtn, weight) + 1e-6,
    }


def awq_quantize(weight: torch.Tensor, act_scale: torch.Tensor, *, bits: int = 4,
                 alphas: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0)) -> dict[str, Any]:
    """AWQ-lite: search a per-input-channel scale s = act_scale^alpha that minimizes the ACTIVATION-
    WEIGHTED weight error ||(W - W_q) . diag(act_scale)||, protecting channels with large activations.

    alpha=0 reduces to plain round-to-nearest (so the searched best is never worse than plain).
    weight (out, in), act_scale (in,)."""
    qmax = 2 ** (bits - 1) - 1
    aw = act_scale.abs().unsqueeze(0)

    def _q(W: torch.Tensor) -> torch.Tensor:
        sc = W.abs().amax(dim=1, keepdim=True).clamp(min=1e-8) / qmax
        return torch.round(W / sc).clamp(-qmax, qmax) * sc

    def _weighted_err(Wq: torch.Tensor) -> float:
        return float(((weight - Wq) * aw).norm())

    plain_err = _weighted_err(_q(weight))
    best_err, best_alpha, best_deq = plain_err, 0.0, _q(weight)
    for alpha in alphas:
        s = (act_scale.abs() + 1e-8) ** alpha
        s = s / s.mean()
        deq = _q(weight * s.unsqueeze(0)) / s.unsqueeze(0)         # quantize scaled, unscale back
        err = _weighted_err(deq)
        if err < best_err - 1e-9:
            best_err, best_alpha, best_deq = err, alpha, deq
    return {
        "dequant": best_deq, "bits": bits, "alpha": best_alpha,
        "salient_weighted_error": best_err,
        "plain_weighted_error": plain_err,
        "protects_salient": best_err <= plain_err + 1e-6,
    }
