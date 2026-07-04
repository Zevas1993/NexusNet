"""NexusNetLM - the trainable causal language model (the thing that gets 'birthed').

A real next-token LM on the canon core: token embedding -> stacked causal-GQA + sparse-MoE-capsule
blocks (RMSNorm pre-norm, RoPE + harmonic positions, DeepSeek loss-free balancing) -> weight-tied
LM head. Optional EBT energy-refinement before the head. Trains by next-token cross-entropy; supports
autoregressive generation. `.to("cuda")` for the GPU box.

(The full EBT / recurrent-depth / multi-plane-memory / cortex stack is demonstrated end-to-end in
NexusNetTransformer; here EBT is an opt-in flag so language training stays fast.)
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from .layers import (
    RMSNorm, GQAttention, EBTRefinement, RecurrentDepth, MultiPlaneMemory, CortexPool, build_rope,
)
from .model import MoECapsuleLayer
from .tokenizer import VOCAB_SIZE


class CausalLMBlock(nn.Module):
    def __init__(self, d_model, n_heads, n_kv_heads, num_experts, top_k, d_hidden):
        super().__init__()
        self.attn_norm = RMSNorm(d_model)
        self.attn = GQAttention(d_model, n_heads, n_kv_heads, causal=True)
        self.ffn_norm = RMSNorm(d_model)
        self.moe = MoECapsuleLayer(d_model, d_hidden, num_experts, top_k)

    def forward(self, h, cos, sin):
        h = h + self.attn(self.attn_norm(h), cos, sin)
        h = h + self.moe(self.ffn_norm(h))
        return h


class NexusNetLM(nn.Module):
    def __init__(
        self,
        *,
        vocab_size: int = VOCAB_SIZE,
        d_model: int = 96,
        n_heads: int = 4,
        n_kv_heads: int = 2,
        num_experts: int = 4,
        top_k: int = 2,
        d_hidden: int = 192,
        num_layers: int = 3,
        use_ebt: bool = False,
        ebt_steps: int = 1,
        full_features: bool = False,
    ) -> None:
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.full_features = full_features
        self.embed = nn.Embedding(vocab_size, d_model)
        self.blocks = nn.ModuleList([
            CausalLMBlock(d_model, n_heads, n_kv_heads, num_experts, top_k, d_hidden)
            for _ in range(num_layers)
        ])
        use_ebt = use_ebt or full_features                # full feature parity requires EBT
        self.use_ebt = use_ebt
        self.ebt_norm = RMSNorm(d_model) if use_ebt else None
        self.ebt = EBTRefinement(d_model, steps=ebt_steps) if use_ebt else None
        # full_features: carry ALL native wrapper features so a born model has parity with the wrapper.
        # recurrent depth (Ouro/ACT), multi-plane MemoryNode, and a Cortex global-workspace readout.
        # All causal-safe: recurrent block is causal; MultiPlaneMemory mixes PLANES within each token
        # (no cross-token leak); CortexPool is an auxiliary detached summary, never fed forward causally.
        if full_features:
            self.recurrent = RecurrentDepth(
                CausalLMBlock(d_model, n_heads, n_kv_heads, num_experts, top_k, d_hidden),
                d_model, max_steps=2)
            self.mem_norm = RMSNorm(d_model)
            self.memory = MultiPlaneMemory(d_model, num_planes=11)
            self.cortex = CortexPool(d_model)
            self.last_summary = None
        self.norm = RMSNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size, bias=False)
        # GPT-style init (std 0.02) so logits start at a sane scale: init CE ~= ln(vocab), not ~90.
        self.apply(self._init_weights)
        # scale residual-output projections by 1/sqrt(2*num_layers) for deep-stack stability (GPT-2).
        residual_scale = (2 * num_layers) ** -0.5
        with torch.no_grad():
            for block in self.blocks:
                block.attn.o_proj.weight.mul_(residual_scale)
                for expert in block.moe.experts:
                    expert.w_out.weight.mul_(residual_scale)
        self.head.weight = self.embed.weight              # weight tying (after init)

    @staticmethod
    def _init_weights(module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        B, T = token_ids.shape
        h = self.embed(token_ids)
        cos, sin = build_rope(T, self.head_dim, harmonic=True, device=h.device)
        for block in self.blocks:
            h = block(h, cos, sin)
        if self.full_features:
            h = self.recurrent(h, cos, sin)               # recurrent-depth (Ouro/ACT) - causal
            h = h + self.memory(self.mem_norm(h))         # multi-plane MemoryNode (per-token, no leak)
        if self.use_ebt:
            h = h + self.ebt(self.ebt_norm(h))            # EBT deliberation
        if self.full_features:
            self.last_summary = self.cortex(self.norm(h)).detach()   # Cortex readout (auxiliary)
        return self.head(self.norm(h))                    # (B, T, vocab)

    @torch.no_grad()
    def generate(self, prompt_ids, *, max_new_tokens=32, temperature=1.0, greedy=True, context=64):
        self.eval()
        device = self.embed.weight.device
        ids = list(prompt_ids)
        for _ in range(max_new_tokens):
            window = ids[-context:]
            x = torch.tensor([window], dtype=torch.long, device=device)
            logits = self(x)[0, -1]                        # last-position logits
            if greedy:
                nxt = int(torch.argmax(logits))
            else:
                probs = torch.softmax(logits / max(1e-6, temperature), dim=-1)
                nxt = int(torch.multinomial(probs, 1))
            ids.append(nxt)
        return ids

    @torch.no_grad()
    def generate_cached(self, prompt_ids, *, max_new_tokens=32, greedy=True, temperature=1.0):
        """Fast autoregressive generation with a per-layer incremental KV cache (Wave 11).
        Produces the same greedy tokens as `generate`, at far fewer attention FLOPs per token."""
        from .kv_cache import cached_generate
        return cached_generate(self, list(prompt_ids), max_new_tokens=max_new_tokens,
                               greedy=greedy, temperature=temperature)["ids"]

    def update_load_bias(self, update_rate: float = 0.001) -> None:
        for block in self.blocks:
            block.moe.update_load_bias(update_rate)

    def num_parameters(self) -> int:
        # tied head shares embed weights; count unique params.
        seen, total = set(), 0
        for p in self.parameters():
            if id(p) in seen:
                continue
            seen.add(id(p))
            total += p.numel()
        return total
