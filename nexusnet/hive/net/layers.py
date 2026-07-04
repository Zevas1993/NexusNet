"""Trainable canon-design layers for the NexusNet neural network (PyTorch).

Each is a real learnable module implementing a required canon component:
  - RMSNorm                  pre-norm normalization (1910.07467; canon Decision RMSNorm pre-norm)
  - RoPE + harmonic basis    rotary positions with a golden-angle/harmonic phase option (canon math)
  - GQAttention              grouped-query attention (canon Decision 003: GQA-first)
  - SwiGLUExpert / MoE...     in model.py (sparse experts + DeepSeek loss-free balancing)
  - EBTRefinement            energy-based deliberation: minimize a LEARNED energy by gradient descent
                             (2507.02092; canon EBT routing/selection)
  - RecurrentDepth           Ouro LoopLM latent recurrence: Prelude -> looped Block -> Coda with a
                             learned hazard/halt (ACT) exit gate (canon recurrent-depth + hazard exit)
  - MultiPlaneMemory         multi-plane MemoryNode cross-plane attention (canon C04 11-plane memory)
  - CortexPool               Cortex / Meta-Reasoner attention-pool aggregation over the sequence
All trainable end-to-end; gradients flow through every one.
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

PHI = 1.61803398875
GOLDEN_ANGLE = math.radians(360 * (1 - 1 / PHI))


class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        rms = torch.rsqrt(x.pow(2).mean(dim=-1, keepdim=True) + self.eps)
        return x * rms * self.weight


def build_rope(seq_len: int, head_dim: int, *, base: float = 10000.0, harmonic: bool = True,
               device=None) -> tuple[torch.Tensor, torch.Tensor]:
    """Rotary position embeddings. With `harmonic`, blend in a golden-angle phase (canon basis)."""
    half = head_dim // 2
    idx = torch.arange(half, dtype=torch.float32, device=device)
    inv_freq = base ** (-2.0 * idx / head_dim)
    pos = torch.arange(seq_len, dtype=torch.float32, device=device)
    angles = torch.outer(pos, inv_freq)                          # (T, half)
    if harmonic:
        angles = angles + torch.outer(pos, (GOLDEN_ANGLE * (PHI ** -idx)))
    cos = torch.cos(angles).repeat_interleave(2, dim=-1)         # (T, head_dim)
    sin = torch.sin(angles).repeat_interleave(2, dim=-1)
    return cos, sin


def apply_rope(x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
    """x: (B, H, T, D). Rotate even/odd pairs."""
    x1, x2 = x[..., 0::2], x[..., 1::2]
    rot = torch.stack((-x2, x1), dim=-1).flatten(-2)
    return x * cos + rot * sin


class GQAttention(nn.Module):
    """Grouped-query attention (canon Decision 003 GQA-first). Bidirectional (encoder) by default."""

    def __init__(self, d_model: int, n_heads: int, n_kv_heads: int, *, causal: bool = False) -> None:
        super().__init__()
        if d_model % n_heads != 0 or n_heads % n_kv_heads != 0:
            raise ValueError("require d_model % n_heads == 0 and n_heads % n_kv_heads == 0")
        self.causal = causal
        self.n_heads = n_heads
        self.n_kv_heads = n_kv_heads
        self.head_dim = d_model // n_heads
        self.q_proj = nn.Linear(d_model, n_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(d_model, n_kv_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(d_model, n_kv_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor,
                *, cache=None, start_pos: int = 0) -> torch.Tensor:
        """With `cache` (a LayerKVCache) the new K/V are appended to the cached past and the causal
        mask uses absolute positions (start_pos..start_pos+T-1) - real incremental KV-cache decode.
        With cache=None / start_pos=0 the behavior is identical to plain full attention."""
        B, T, _ = x.shape
        q = self.q_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, T, self.n_kv_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, T, self.n_kv_heads, self.head_dim).transpose(1, 2)
        q = apply_rope(q, cos, sin)
        k = apply_rope(k, cos, sin)
        if cache is not None:
            k, v = cache.append(k, v)                            # concat past (pre-repeat) K/V
        rep = self.n_heads // self.n_kv_heads
        kk = k.repeat_interleave(rep, dim=1)                     # GQA: share KV across query groups
        vv = v.repeat_interleave(rep, dim=1)
        scores = (q @ kk.transpose(-2, -1)) / math.sqrt(self.head_dim)
        if self.causal:
            t_k = kk.shape[2]
            j = torch.arange(t_k, device=x.device)
            i = torch.arange(T, device=x.device) + start_pos
            mask = j.unsqueeze(0) > i.unsqueeze(1)               # (T, t_k) absolute-position causal
            scores = scores.masked_fill(mask, float("-inf"))     # no attending to the future
        attn = torch.softmax(scores, dim=-1)
        out = (attn @ vv).transpose(1, 2).reshape(B, T, -1)
        return self.o_proj(out)


class EBTRefinement(nn.Module):
    """Energy-Based deliberation: minimize a LEARNED scalar energy E_theta(h) by gradient descent.

    Prediction = refine the latent by stepping down the energy gradient (System-2 "thinking"); the
    step count is the deliberation budget. The energy gradient is taken via autograd (create_graph in
    training so the whole unrolled descent is differentiable end-to-end).
    """

    def __init__(self, d_model: int, hidden: int | None = None, steps: int = 2, lr: float = 0.5) -> None:
        super().__init__()
        hidden = hidden or d_model
        self.energy_net = nn.Sequential(
            nn.Linear(d_model, hidden), nn.SiLU(), nn.Linear(hidden, 1)
        )
        self.steps = steps
        self.lr = lr

    def energy(self, h: torch.Tensor) -> torch.Tensor:
        return self.energy_net(h).squeeze(-1)                    # (B, T)

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        # Enable grad even under inference (no_grad): EBT descent needs the energy gradient.
        with torch.enable_grad():
            for _ in range(self.steps):
                h = h.requires_grad_(True)
                e = self.energy(h).sum()
                (grad,) = torch.autograd.grad(e, h, create_graph=self.training)
                h = h - self.lr * grad
        return h


class RecurrentDepth(nn.Module):
    """Ouro LoopLM latent recurrence with an ACT-style learned hazard/halt gate.

    Applies a parameter-shared recurrent block repeatedly; at each step a learned halt probability
    accumulates (ponder), and the output is the halt-weighted mean of the per-step states. Embodies
    "recurrent deliberation + exit gates" (canon) - more loops = more depth, gated by hazard.
    """

    def __init__(self, block: nn.Module, d_model: int, max_steps: int = 3, halt_eps: float = 0.01) -> None:
        super().__init__()
        self.block = block
        self.halt = nn.Linear(d_model, 1)
        self.max_steps = max_steps
        self.halt_eps = halt_eps

    def forward(self, h: torch.Tensor, *args) -> torch.Tensor:
        """Per-token halting distribution: weight_step = p_step * prod_{j<step}(1 - p_j); the final
        step is forced to halt (p=1) so the per-token weights sum to exactly 1 (a proper ponder mean).
        Also exposes the expected number of steps (ponder cost) via `self.last_ponder`."""
        B, T, D = h.shape
        still = torch.ones(B, T, 1, device=h.device)             # prob still running before this step
        output = torch.zeros_like(h)
        ponder = torch.zeros(B, T, 1, device=h.device)
        for step in range(self.max_steps):
            h = self.block(h, *args)
            if step < self.max_steps - 1:
                p = torch.sigmoid(self.halt(h))                  # halt prob this step
            else:
                p = torch.ones(B, T, 1, device=h.device)        # force halt on the last step
            weight = p * still                                   # mass that halts at this step
            output = output + weight * h
            ponder = ponder + (step + 1) * weight
            still = still * (1.0 - p)
        self.last_ponder = ponder.detach().mean()
        return output


class MultiPlaneMemory(nn.Module):
    """Multi-plane MemoryNode: project the latent into K planes, attend across planes, recombine.

    Realizes the canon multi-plane memory + cross-plane attention as a trainable module.
    """

    def __init__(self, d_model: int, num_planes: int = 11) -> None:
        super().__init__()
        self.num_planes = num_planes
        self.to_planes = nn.Linear(d_model, num_planes * d_model)
        self.cross = nn.MultiheadAttention(d_model, num_heads=1, batch_first=True)
        self.from_planes = nn.Linear(num_planes * d_model, d_model)
        self.d_model = d_model

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        B, T, D = h.shape
        planes = self.to_planes(h).view(B * T, self.num_planes, D)   # tokens as batch, planes as seq
        attended, _ = self.cross(planes, planes, planes)             # cross-plane attention
        recombined = self.from_planes(attended.reshape(B, T, self.num_planes * D))
        return recombined


class CortexPool(nn.Module):
    """Cortex / Meta-Reasoner aggregation: attention-pool the sequence into one decision vector."""

    def __init__(self, d_model: int) -> None:
        super().__init__()
        self.query = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)
        self.attn = nn.MultiheadAttention(d_model, num_heads=1, batch_first=True)

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        B = h.shape[0]
        q = self.query.expand(B, 1, -1)
        pooled, _ = self.attn(q, h, h)
        return pooled.squeeze(1)                                     # (B, d_model)
