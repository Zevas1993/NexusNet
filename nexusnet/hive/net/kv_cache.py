"""Wave-11: incremental per-layer KV cache for fast autoregressive decoding.

Without a cache, generating each token re-runs attention over the whole prefix (O(T^2) per token).
A KV cache stores each layer's already-roped K/V so a decode step only computes the new token's
Q/K/V and attends over the cached past - the standard fast-decode path. `LayerKVCache` is one layer's
slot; `cached_generate` drives a prefill + incremental-decode loop and is verified to produce the
SAME greedy tokens as the uncached path.
"""
from __future__ import annotations

import torch

from .layers import build_rope


class LayerKVCache:
    """One attention layer's KV cache (pre-GQA-repeat K/V, shape (B, n_kv_heads, T, head_dim))."""

    def __init__(self) -> None:
        self.k: torch.Tensor | None = None
        self.v: torch.Tensor | None = None

    def append(self, k: torch.Tensor, v: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if self.k is None:
            self.k, self.v = k, v
        else:
            self.k = torch.cat([self.k, k], dim=2)
            self.v = torch.cat([self.v, v], dim=2)
        return self.k, self.v

    @property
    def length(self) -> int:
        return 0 if self.k is None else self.k.shape[2]


@torch.no_grad()
def cached_generate(model, prompt_ids: list[int], *, max_new_tokens: int = 32, greedy: bool = True,
                    temperature: float = 1.0) -> dict:
    """Autoregressive generation with a per-layer KV cache. `model` is a NexusNetLM.

    Prefill the prompt in one pass (filling the caches), then decode one token at a time, each step
    computing attention only for the new token against the cached past.
    """
    model.eval()
    device = model.embed.weight.device
    total = len(prompt_ids) + max_new_tokens
    cos_full, sin_full = build_rope(total, model.head_dim, harmonic=True, device=device)
    caches = [LayerKVCache() for _ in model.blocks]
    ids = list(prompt_ids)

    def _head(h: torch.Tensor) -> torch.Tensor:
        if getattr(model, "use_ebt", False) and model.ebt is not None:
            h = h + model.ebt(model.ebt_norm(h))
        return model.head(model.norm(h))

    # prefill over the whole prompt
    x = torch.tensor([ids], dtype=torch.long, device=device)
    h = model.embed(x)
    n = len(ids)
    for block, cache in zip(model.blocks, caches):
        h = h + block.attn(block.attn_norm(h), cos_full[:n], sin_full[:n], cache=cache, start_pos=0)
        h = h + block.moe(block.ffn_norm(h))
    logits = _head(h)[0, -1]
    nxt = int(logits.argmax()) if greedy else int(
        torch.multinomial(torch.softmax(logits / max(1e-6, temperature), -1), 1))
    ids.append(nxt)

    # incremental decode: one token at a time against the cache
    for _ in range(max_new_tokens - 1):
        pos = len(ids) - 1
        x = torch.tensor([[ids[-1]]], dtype=torch.long, device=device)
        h = model.embed(x)
        for block, cache in zip(model.blocks, caches):
            h = h + block.attn(block.attn_norm(h), cos_full[pos:pos + 1], sin_full[pos:pos + 1],
                               cache=cache, start_pos=pos)
            h = h + block.moe(block.ffn_norm(h))
        logits = _head(h)[0, -1]
        nxt = int(logits.argmax()) if greedy else int(
            torch.multinomial(torch.softmax(logits / max(1e-6, temperature), -1), 1))
        ids.append(nxt)

    return {"ids": ids, "cache_length": caches[0].length, "prompt_len": len(prompt_ids)}
