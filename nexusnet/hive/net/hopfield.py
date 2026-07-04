"""Wave-8: differentiable modern Hopfield associative memory (real torch).

Canon MemoryNode + Hopfield (C04; modern Hopfield is mathematically equivalent to transformer
attention - Ramsauer et al. 2020). Retrieval is a softmax over stored-pattern similarities:

    retrieve(R) = softmax(beta * R @ Xi^T) @ Xi

One update is one attention step; iterating converges to a stored pattern (high beta) or a metastable
mixture (low beta). This is the associative recall the kernel models deterministically, now as a
trainable, content-addressable module: give it a NOISY cue, it returns the clean stored pattern.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


def hopfield_retrieve(query: torch.Tensor, patterns: torch.Tensor, *, beta: float = 1.0,
                      steps: int = 1) -> torch.Tensor:
    """Modern Hopfield update(s). query (B, d), patterns (M, d) -> retrieved (B, d)."""
    r = query
    for _ in range(steps):
        attn = torch.softmax(beta * (r @ patterns.t()), dim=-1)   # (B, M)
        r = attn @ patterns                                       # (B, d)
    return r


class ModernHopfield(nn.Module):
    """Stateless modern Hopfield retrieval (attention-equivalent associative memory)."""

    def __init__(self, beta: float = 1.0, steps: int = 1) -> None:
        super().__init__()
        self.beta = beta
        self.steps = steps

    def forward(self, query: torch.Tensor, patterns: torch.Tensor, *, steps: int | None = None
                ) -> torch.Tensor:
        return hopfield_retrieve(query, patterns, beta=self.beta, steps=steps or self.steps)

    def retrieval_weights(self, query: torch.Tensor, patterns: torch.Tensor) -> torch.Tensor:
        return torch.softmax(self.beta * (query @ patterns.t()), dim=-1)


class HopfieldAssociativeStore(nn.Module):
    """Content-addressable store: write patterns, recall the clean pattern from a noisy cue."""

    def __init__(self, dim: int, *, beta: float = 8.0, steps: int = 3) -> None:
        super().__init__()
        self.dim = dim
        self.hopfield = ModernHopfield(beta=beta, steps=steps)
        self.register_buffer("patterns", torch.empty(0, dim))

    def write(self, patterns: torch.Tensor) -> None:
        self.patterns = torch.cat([self.patterns, patterns.detach()], dim=0)

    def recall(self, cue: torch.Tensor, *, steps: int | None = None) -> torch.Tensor:
        if self.patterns.numel() == 0:
            return cue
        return self.hopfield(cue, self.patterns, steps=steps)


class HopfieldLayer(nn.Module):
    """Trainable Hopfield layer: project state to a query, retrieve over learned/stored keys-values.

    A drop-in associative-memory block: RMSNorm-free linear projections (q,k,v), Hopfield retrieval
    over a set of stored value patterns, output projection. Differentiable end-to-end.
    """

    def __init__(self, d_model: int, *, beta: float = 1.0, steps: int = 1) -> None:
        super().__init__()
        self.q = nn.Linear(d_model, d_model, bias=False)
        self.k = nn.Linear(d_model, d_model, bias=False)
        self.v = nn.Linear(d_model, d_model, bias=False)
        self.o = nn.Linear(d_model, d_model, bias=False)
        self.beta = beta
        self.steps = steps

    def forward(self, state: torch.Tensor, memory: torch.Tensor) -> torch.Tensor:
        """state (B, d) cue; memory (M, d) stored items -> retrieved & projected (B, d)."""
        q = self.q(state)
        keys = self.k(memory)
        vals = self.v(memory)
        r = q
        for _ in range(self.steps):
            attn = torch.softmax(self.beta * (r @ keys.t()), dim=-1)
            r = attn @ keys
        attn = torch.softmax(self.beta * (r @ keys.t()), dim=-1)
        return self.o(attn @ vals)
