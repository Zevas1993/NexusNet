"""Wave-6: real inference runtime - speculative decoding, prefix cache, continuous batching, KV math.

Canon Overlay runtime row: performance depends on speculative decoding, prefix caching / KV reuse,
and continuous batching. These are implemented here as real algorithms over NexusNetLM:

  - speculative_decode    a small DRAFT model proposes gamma tokens; the TARGET verifies them in one
                          batched forward and accepts the longest matching greedy prefix (+1 correction).
                          For greedy decoding the output is identical to target-only decoding, at fewer
                          target steps - the speculative-decoding correctness guarantee.
  - PrefixCache           caches the next-token logits for a token prefix (KV/prefix reuse); reports
                          hit rate so repeated prefixes skip recompute.
  - ContinuousBatcher     admits variable-length generation requests, steps them as one padded batch,
                          and retires finished ones (continuous batching scheduler).
  - kv_cache_report       KV-cache memory accounting + the MLA-latent compression saving.
"""
from __future__ import annotations

from typing import Any

import torch


@torch.no_grad()
def speculative_decode(
    target: torch.nn.Module,
    draft: torch.nn.Module,
    prompt_ids: list[int],
    *,
    max_new_tokens: int = 16,
    gamma: int = 4,
) -> dict[str, Any]:
    """Greedy speculative decoding. Returns the generated ids + acceptance stats."""
    target.eval()
    draft.eval()
    device = next(target.parameters()).device
    ids = list(prompt_ids)
    n_prompt = len(prompt_ids)
    proposed = accepted = target_forwards = 0
    while len(ids) - n_prompt < max_new_tokens:
        # DRAFT proposes gamma tokens greedily.
        draft_tokens: list[int] = []
        cur = list(ids)
        for _ in range(gamma):
            lg = draft(torch.tensor([cur], device=device))[0, -1]
            t = int(lg.argmax())
            draft_tokens.append(t)
            cur.append(t)
        proposed += gamma
        # TARGET verifies all gamma in one forward.
        seq = ids + draft_tokens
        logits = target(torch.tensor([seq], device=device))[0]   # (len(seq), V)
        target_forwards += 1
        base = len(ids) - 1
        acc = 0
        for j in range(gamma):
            pred = int(logits[base + j].argmax())
            if pred == draft_tokens[j]:
                acc += 1
            else:
                break
        ids.extend(draft_tokens[:acc])
        accepted += acc
        # append one token from the target (the correction at the first mismatch, or a bonus token)
        corr = int(logits[base + acc].argmax())
        ids.append(corr)
    ids = ids[: n_prompt + max_new_tokens]
    return {
        "ids": ids,
        "proposed": proposed,
        "accepted": accepted,
        "acceptance_rate": (accepted / proposed) if proposed else 0.0,
        "target_forwards": target_forwards,
    }


class PrefixCache:
    """Cache next-token logits keyed by a token prefix (prefix/KV reuse). Tracks hit rate."""

    def __init__(self) -> None:
        self._cache: dict[tuple[int, ...], torch.Tensor] = {}
        self.hits = 0
        self.misses = 0

    @torch.no_grad()
    def next_logits(self, model: torch.nn.Module, ids: list[int]) -> torch.Tensor:
        key = tuple(ids)
        cached = self._cache.get(key)
        if cached is not None:
            self.hits += 1
            return cached
        self.misses += 1
        device = next(model.parameters()).device
        logits = model(torch.tensor([ids], device=device))[0, -1].detach()
        self._cache[key] = logits
        return logits

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


class _Request:
    def __init__(self, req_id: str, ids: list[int], max_new: int) -> None:
        self.req_id = req_id
        self.ids = list(ids)
        self.max_new = max_new
        self.produced = 0
        self.done = False


class ContinuousBatcher:
    """Continuous batching: step admitted requests together as one padded batch; retire finished ones."""

    def __init__(self, model: torch.nn.Module, *, pad_id: int = 0) -> None:
        self.model = model
        self.pad_id = pad_id
        self.active: list[_Request] = []

    def admit(self, req_id: str, ids: list[int], max_new: int) -> None:
        self.active.append(_Request(req_id, ids, max_new))

    @torch.no_grad()
    def step(self) -> int:
        """One decode step across all active requests (single batched forward). Returns #active stepped."""
        running = [r for r in self.active if not r.done]
        if not running:
            return 0
        device = next(self.model.parameters()).device
        maxlen = max(len(r.ids) for r in running)
        batch = [[self.pad_id] * (maxlen - len(r.ids)) + r.ids for r in running]   # left-pad
        logits = self.model(torch.tensor(batch, device=device))                    # (R, maxlen, V)
        for i, r in enumerate(running):
            nxt = int(logits[i, -1].argmax())
            r.ids.append(nxt)
            r.produced += 1
            if r.produced >= r.max_new:
                r.done = True
        return len(running)

    def run(self, max_steps: int = 64) -> dict[str, list[int]]:
        steps = 0
        while any(not r.done for r in self.active) and steps < max_steps:
            self.step()
            steps += 1
        return {r.req_id: r.ids for r in self.active}


def kv_cache_report(
    *, n_layers: int, n_kv_heads: int, head_dim: int, seq_len: int,
    bytes_per_elem: int = 2, mla_latent_dim: int | None = None,
) -> dict[str, Any]:
    """KV-cache memory for the run, and the MLA-latent compression saving if MLA is used."""
    full_per_token = 2 * n_layers * n_kv_heads * head_dim          # K and V
    full_bytes = full_per_token * seq_len * bytes_per_elem
    report = {
        "full_kv_bytes": full_bytes,
        "full_kv_per_token": full_per_token,
        "seq_len": seq_len,
    }
    if mla_latent_dim is not None:
        mla_per_token = n_layers * mla_latent_dim                  # one latent per layer
        report["mla_kv_bytes"] = mla_per_token * seq_len * bytes_per_elem
        report["mla_per_token"] = mla_per_token
        report["compression_ratio"] = mla_per_token / full_per_token
    return report
