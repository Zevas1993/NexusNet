"""NexusNetTransformer - the full canon architecture as ONE trainable neural network.

Integrates the required canon designs end-to-end (all learnable, all differentiable):
  token embedding
   -> RoPE + harmonic positional basis
   -> Ouro recurrent-depth loop over a parameter-shared Transformer block, each block:
         RMSNorm -> GQA attention (Decision 003) -> residual
         RMSNorm -> sparse MoE capsule experts (SwiGLU + DeepSeek loss-free balancing) -> residual
      with a learned hazard/halt (ACT) exit gate
   -> EBT energy-minimization deliberation (refine latent by descending a learned energy)
   -> multi-plane MemoryNode cross-plane attention
   -> Cortex / Meta-Reasoner attention-pool aggregation
   -> output head

Trains by real backprop; `.to("cuda")` for the RTX 5070 Ti.
"""
from __future__ import annotations

import torch
import torch.nn as nn

from .model import MoECapsuleLayer, squash
from .layers import (
    RMSNorm,
    GQAttention,
    EBTRefinement,
    RecurrentDepth,
    MultiPlaneMemory,
    CortexPool,
    build_rope,
)
from .advanced_layers import HybridSSMAttentionBlock, MLAttention, build_rope_yarn


class TransformerBlock(nn.Module):
    """RMSNorm -> GQA attention -> residual; RMSNorm -> MoE capsule FFN -> residual."""

    def __init__(self, d_model: int, n_heads: int, n_kv_heads: int, num_experts: int,
                 top_k: int, d_hidden: int, *, attn_kind: str = "gqa",
                 kv_latent_dim: int | None = None, expert_kind: str = "swiglu") -> None:
        super().__init__()
        self.attn_norm = RMSNorm(d_model)
        if attn_kind == "mla":
            self.attn = MLAttention(d_model, n_heads, kv_latent_dim or max(8, d_model // 4))
        else:
            self.attn = GQAttention(d_model, n_heads, n_kv_heads)
        self.ffn_norm = RMSNorm(d_model)
        self.moe = MoECapsuleLayer(d_model, d_hidden, num_experts, top_k, expert_kind=expert_kind)

    def forward(self, h: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
        h = h + self.attn(self.attn_norm(h), cos, sin)
        h = h + self.moe(self.ffn_norm(h))
        return h


class NexusNetTransformer(nn.Module):
    def __init__(
        self,
        *,
        vocab_size: int,
        num_classes: int,
        d_model: int = 48,
        n_heads: int = 4,
        n_kv_heads: int = 2,
        num_experts: int = 6,
        top_k: int = 2,
        d_hidden: int = 96,
        max_steps: int = 3,
        num_planes: int = 11,
        ebt_steps: int = 2,
        harmonic: bool = True,
        core_kind: str = "transformer",       # "transformer" | "hybrid" (SSM+attn fusion)
        attn_kind: str = "gqa",               # "gqa" | "mla" (latent KV)
        d_state: int = 16,                    # SSM state size (hybrid core)
        kv_latent_dim: int | None = None,     # MLA latent size
        rope_scale: float = 1.0,              # YaRN context-extension factor (1.0 = plain RoPE)
        rope_original_max: int = 256,         # YaRN: original trained context window
        expert_kind: str = "swiglu",          # "swiglu" | "mini" (each expert a mini-NexusNet)
    ) -> None:
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.harmonic = harmonic
        self.core_kind = core_kind
        self.attn_kind = attn_kind
        self.rope_scale = rope_scale
        self.rope_original_max = rope_original_max
        self.rope_mscale = 1.0

        self.embed = nn.Embedding(vocab_size, d_model)
        if core_kind == "hybrid":
            block: nn.Module = HybridSSMAttentionBlock(
                d_model, n_heads, n_kv_heads, num_experts, top_k, d_hidden,
                d_state=d_state, attn_kind=attn_kind, kv_latent_dim=kv_latent_dim,
                expert_kind=expert_kind,
            )
        else:
            block = TransformerBlock(
                d_model, n_heads, n_kv_heads, num_experts, top_k, d_hidden,
                attn_kind=attn_kind, kv_latent_dim=kv_latent_dim, expert_kind=expert_kind,
            )
        self.recurrent = RecurrentDepth(block, d_model, max_steps=max_steps)
        self.ebt_norm = RMSNorm(d_model)
        self.ebt = EBTRefinement(d_model, steps=ebt_steps)
        self.mem_norm = RMSNorm(d_model)
        self.memory = MultiPlaneMemory(d_model, num_planes=num_planes)
        self.cortex_norm = RMSNorm(d_model)
        self.cortex = CortexPool(d_model)
        self.head = nn.Linear(d_model, num_classes)

    def trunk(self, token_ids: torch.Tensor) -> torch.Tensor:
        B, T = token_ids.shape
        h = self.embed(token_ids)                                # (B, T, d_model)
        if self.rope_scale != 1.0:
            cos, sin, self.rope_mscale = build_rope_yarn(
                T, self.head_dim, original_max_pos=self.rope_original_max,
                scale=self.rope_scale, harmonic=self.harmonic, device=h.device,
            )                                                    # YaRN long-context scaling
        else:
            cos, sin = build_rope(T, self.head_dim, harmonic=self.harmonic, device=h.device)
        h = self.recurrent(h, cos, sin)                          # recurrent depth (attn + MoE)
        h = h + self.ebt(self.ebt_norm(h))                       # EBT deliberation
        h = h + self.memory(self.mem_norm(h))                    # multi-plane memory
        return self.cortex(self.cortex_norm(h))                  # (B, d_model) cortex aggregation

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        return self.head(self.trunk(token_ids))

    def pose(self, token_ids: torch.Tensor) -> torch.Tensor:
        return squash(self.trunk(token_ids))

    def update_load_bias(self, update_rate: float = 0.001) -> None:
        self.recurrent.block.moe.update_load_bias(update_rate)

    def num_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
