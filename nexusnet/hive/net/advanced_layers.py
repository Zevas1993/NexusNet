"""Wave-1 canon core-compute layers (real, trainable PyTorch).

Adds the canon-required compute primitives the base stack was missing:

  - SelectiveSSM      Mamba2-style selective state-space mixer (linear-time sequence mixing,
                      input-dependent dt/B/C selectivity, diagonal state). Canon C05M0156 hybrid
                      processing core (Mamba2 + attention fusion); C34 LFM2-style efficiency.
  - MLAttention       Multi-head Latent Attention (DeepSeek-V2): compress K/V into a low-rank latent
                      then reconstruct per head, so the cached state is the small latent. Canon
                      C08M0176 (MLA as a runtime/model feature; compressed KV latent).
  - build_rope_yarn   YaRN long-context RoPE scaling (NTK-by-parts ramp + attention temperature)
                      so the same weights extend to a longer effective context. Canon Aspect 4 /
                      C01 (1M effective context; RoPE + YaRN, not just accept tokens but use them).
  - HybridSSMAttentionBlock   fuses SSM (local/linear mixing) + attention (global) + MoE FFN, the
                      canon "hybrid processing core".

All modules are differentiable end-to-end (real backprop); device-agnostic.
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from .layers import RMSNorm, GQAttention, apply_rope, PHI, GOLDEN_ANGLE
from .model import MoECapsuleLayer


class SelectiveSSM(nn.Module):
    """Mamba2-style selective state-space mixer (diagonal, input-dependent).

    Linear-time sequence model: per channel a diagonal state recurrence
        h_t = exp(dt_t * A) . h_{t-1} + (dt_t * B_t) . x_t ;   y_t = C_t . h_t + D . x_t
    where A is a learned (negative) diagonal, and dt/B/C are *input-dependent* (the selectivity that
    makes Mamba content-aware). Implemented as a sequential scan (exact, differentiable); fine for the
    sequence lengths used here and on GPU. A gated SiLU branch (z) follows Mamba's block design.
    """

    def __init__(self, d_model: int, d_state: int = 16, expand: int = 2) -> None:
        super().__init__()
        d_inner = expand * d_model
        self.d_model = d_model
        self.d_inner = d_inner
        self.d_state = d_state
        self.in_proj = nn.Linear(d_model, 2 * d_inner, bias=False)   # -> (x, gate z)
        self.dt_proj = nn.Linear(d_inner, d_inner, bias=True)
        self.x_proj = nn.Linear(d_inner, 2 * d_state, bias=False)    # -> (B, C) selective
        # A as -exp(A_log); init to a stable diagonal range (1..d_state) per inner channel.
        a_init = torch.arange(1, d_state + 1, dtype=torch.float32).repeat(d_inner, 1)
        self.A_log = nn.Parameter(torch.log(a_init))
        self.D = nn.Parameter(torch.ones(d_inner))
        self.out_proj = nn.Linear(d_inner, d_model, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, _ = x.shape
        xz = self.in_proj(x)
        xi, z = xz.chunk(2, dim=-1)                                  # (B,T,d_inner)
        xi = F.silu(xi)
        dt = F.softplus(self.dt_proj(xi))                           # (B,T,d_inner) > 0
        bc = self.x_proj(xi)
        b_mat, c_mat = bc.split(self.d_state, dim=-1)                # (B,T,d_state)
        a = -torch.exp(self.A_log)                                   # (d_inner, d_state)
        h = torch.zeros(B, self.d_inner, self.d_state, device=x.device, dtype=x.dtype)
        ys = []
        for t in range(T):
            dt_t = dt[:, t].unsqueeze(-1)                            # (B,d_inner,1)
            d_a = torch.exp(dt_t * a)                                # (B,d_inner,d_state)
            d_bx = dt_t * b_mat[:, t].unsqueeze(1) * xi[:, t].unsqueeze(-1)  # (B,d_inner,d_state)
            h = d_a * h + d_bx
            y_t = (h * c_mat[:, t].unsqueeze(1)).sum(dim=-1)         # (B,d_inner)
            ys.append(y_t)
        y = torch.stack(ys, dim=1)                                   # (B,T,d_inner)
        y = y + xi * self.D
        y = y * F.silu(z)                                            # gated output (Mamba block)
        return self.out_proj(y)


class MLAttention(nn.Module):
    """Multi-head Latent Attention (DeepSeek-V2 style).

    Down-projects the token to a small KV *latent* c_kv (dim `kv_latent_dim` << n_heads*head_dim);
    that latent is the cacheable state (compressed KV). Per step it is up-projected to per-head K,V.
    RoPE is applied to q and k. This is the canon MLA option beside GQA: less KV memory for long
    context. Returns (output, kv_latent) so a cache/runtime can store the small latent.
    """

    def __init__(self, d_model: int, n_heads: int, kv_latent_dim: int, *, causal: bool = False) -> None:
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError("require d_model % n_heads == 0")
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.causal = causal
        self.kv_latent_dim = kv_latent_dim
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.kv_down = nn.Linear(d_model, kv_latent_dim, bias=False)     # compress -> latent (cached)
        self.kv_up = nn.Linear(kv_latent_dim, 2 * d_model, bias=False)   # reconstruct K, V
        self.o_proj = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor,
                *, return_latent: bool = False):
        B, T, _ = x.shape
        q = self.q_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        c_kv = self.kv_down(x)                                       # (B,T,kv_latent_dim) <- cacheable
        kv = self.kv_up(c_kv)                                        # (B,T,2*d_model)
        k, v = kv.chunk(2, dim=-1)
        k = k.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        q = apply_rope(q, cos, sin)
        k = apply_rope(k, cos, sin)
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        if self.causal:
            mask = torch.triu(torch.ones(T, T, device=x.device, dtype=torch.bool), diagonal=1)
            scores = scores.masked_fill(mask, float("-inf"))
        attn = torch.softmax(scores, dim=-1)
        out = (attn @ v).transpose(1, 2).reshape(B, T, -1)
        out = self.o_proj(out)
        if return_latent:
            return out, c_kv
        return out

    def kv_cache_ratio(self) -> float:
        """Compression: cached latent floats per token / full-KV floats per token (< 1 is a saving)."""
        full = 2 * self.n_heads * self.head_dim
        return self.kv_latent_dim / full


def _yarn_correction_dim(num_rotations: float, dim: int, base: float, max_pos: int) -> float:
    """The rotary index whose wavelength completes `num_rotations` turns over `max_pos` positions."""
    return (dim * math.log(max_pos / (num_rotations * 2 * math.pi))) / (2 * math.log(base))


def _yarn_ramp(low: float, high: float, size: int, device=None) -> torch.Tensor:
    """Linear ramp in [0,1] over rotary indices, clamped; selects extrapolate vs interpolate per freq."""
    if low == high:
        high += 0.001
    idx = torch.arange(size, dtype=torch.float32, device=device)
    ramp = (idx - low) / (high - low)
    return torch.clamp(ramp, 0.0, 1.0)


def build_rope_yarn(
    seq_len: int,
    head_dim: int,
    *,
    base: float = 10000.0,
    original_max_pos: int = 256,
    scale: float = 1.0,
    beta_fast: float = 32.0,
    beta_slow: float = 1.0,
    harmonic: bool = True,
    device=None,
) -> tuple[torch.Tensor, torch.Tensor, float]:
    """YaRN-scaled RoPE: extend the effective context by `scale` via NTK-by-parts interpolation.

    High-frequency rotary dims keep extrapolating (preserve local detail); low-frequency dims are
    interpolated by `scale` (so positions beyond the original window stay in-distribution). Returns
    (cos, sin, mscale) where `mscale` is the attention-temperature factor YaRN applies to logits.
    With scale == 1.0 this reduces to ordinary RoPE (plus the harmonic golden-angle phase).
    """
    half = head_dim // 2
    idx = torch.arange(half, dtype=torch.float32, device=device)
    pos_freqs = base ** (2.0 * idx / head_dim)
    inv_freq_extrap = 1.0 / pos_freqs                               # no scaling (extrapolate)
    inv_freq_interp = 1.0 / (scale * pos_freqs)                     # full scaling (interpolate)

    low = math.floor(_yarn_correction_dim(beta_fast, head_dim, base, original_max_pos))
    high = math.ceil(_yarn_correction_dim(beta_slow, head_dim, base, original_max_pos))
    low = max(low, 0)
    high = min(high, half - 1)
    # ramp==1 -> keep extrapolation (high freq); ramp==0 -> full interpolation (low freq)
    inv_freq_mask = 1.0 - _yarn_ramp(low, high, half, device=device)
    inv_freq = inv_freq_interp * (1.0 - inv_freq_mask) + inv_freq_extrap * inv_freq_mask

    pos = torch.arange(seq_len, dtype=torch.float32, device=device)
    angles = torch.outer(pos, inv_freq)                            # (T, half)
    if harmonic:
        angles = angles + torch.outer(pos, (GOLDEN_ANGLE * (PHI ** -idx)))
    cos = torch.cos(angles).repeat_interleave(2, dim=-1)
    sin = torch.sin(angles).repeat_interleave(2, dim=-1)
    mscale = 1.0 if scale <= 1.0 else (0.1 * math.log(scale) + 1.0)
    return cos, sin, mscale


class HybridSSMAttentionBlock(nn.Module):
    """Canon hybrid processing core: SSM (linear/local mixing) + attention (global) + MoE FFN.

    RMSNorm -> SelectiveSSM -> residual
    RMSNorm -> (GQA or MLA) attention -> residual
    RMSNorm -> sparse MoE capsule experts -> residual
    Signature matches TransformerBlock (h, cos, sin) so it drops into RecurrentDepth.
    """

    def __init__(self, d_model: int, n_heads: int, n_kv_heads: int, num_experts: int, top_k: int,
                 d_hidden: int, *, d_state: int = 16, attn_kind: str = "gqa",
                 kv_latent_dim: int | None = None, expert_kind: str = "swiglu") -> None:
        super().__init__()
        self.ssm_norm = RMSNorm(d_model)
        self.ssm = SelectiveSSM(d_model, d_state=d_state)
        self.attn_norm = RMSNorm(d_model)
        self.attn_kind = attn_kind
        if attn_kind == "mla":
            self.attn = MLAttention(d_model, n_heads, kv_latent_dim or max(8, d_model // 4))
        else:
            self.attn = GQAttention(d_model, n_heads, n_kv_heads)
        self.ffn_norm = RMSNorm(d_model)
        self.moe = MoECapsuleLayer(d_model, d_hidden, num_experts, top_k, expert_kind=expert_kind)

    def forward(self, h: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
        h = h + self.ssm(self.ssm_norm(h))                          # linear-time local mixing
        h = h + self.attn(self.attn_norm(h), cos, sin)              # global attention
        h = h + self.moe(self.ffn_norm(h))                          # sparse experts
        return h
