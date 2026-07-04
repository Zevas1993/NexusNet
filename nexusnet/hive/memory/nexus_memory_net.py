"""NexusMemoryNet - the canon 1M-token memory core (six named components).

Long-context handling on consumer hardware without overloading the context window or hallucinating
(C38/C39). Six deterministic, pure-Python components, composed by NexusMemoryNet.process():

  1. Sparse Pre-Filter        - cheaply drop low-relevance tokens before attention.
  2. Token Clusterer /         - cluster similar surviving tokens; compress each cluster to a centroid
     Semantic Compressor         (semantic compression).
  3. Dual-Track Attention      - a LOCAL track (recent tokens) + a GLOBAL track (compressed centroids);
                                 each track's attention sums to 1, blended by a gate.
  4. External Memory Router    - decide per query whether to answer from in-context vs external memory.
  5. Compressed Summary        - inject a single compressed summary vector built from the centroids.
     Injector
  6. Position Encoding         - RoPE base with a YaRN-style scale for context extension.
     Overhaul

Shadow-only; deterministic; no production mutation.
"""
from __future__ import annotations

import math
from typing import Any

from ..kernel import tensor_ops as ops

Vector = list[float]


# --- 1. Sparse Pre-Filter ---

def sparse_pre_filter(*, relevances: list[float], keep_fraction: float = 0.5) -> dict[str, Any]:
    """Keep the top keep_fraction of tokens by relevance (at least one)."""
    if not relevances:
        raise ValueError("need at least one token")
    if not 0.0 < keep_fraction <= 1.0:
        raise ValueError("keep_fraction must be in (0, 1]")
    n = len(relevances)
    keep_n = max(1, math.ceil(keep_fraction * n))
    kept = sorted(range(n), key=lambda i: relevances[i], reverse=True)[:keep_n]
    return {"kept_indices": sorted(kept), "kept_count": keep_n, "total": n}


# --- 2. Token Clusterer / Semantic Compressor ---

def semantic_compress(*, vectors: list[Vector], num_clusters: int, iterations: int = 5) -> dict[str, Any]:
    """Deterministic k-means: every token assigned to nearest centroid; returns centroids."""
    if not vectors:
        raise ValueError("need at least one vector")
    k = max(1, min(num_clusters, len(vectors)))
    dim = len(vectors[0])
    # Deterministic seeding: evenly spaced picks across the input order.
    step = max(1, len(vectors) // k)
    centroids = [list(vectors[(i * step) % len(vectors)]) for i in range(k)]
    assignments = [0] * len(vectors)
    for _ in range(max(1, iterations)):
        # Assign.
        for ti, v in enumerate(vectors):
            assignments[ti] = min(range(k), key=lambda c: _sq_dist(v, centroids[c]))
        # Update.
        for c in range(k):
            members = [vectors[ti] for ti in range(len(vectors)) if assignments[ti] == c]
            if members:
                centroids[c] = [sum(m[d] for m in members) / len(members) for d in range(dim)]
    return {"centroids": centroids, "assignments": assignments, "num_clusters": k}


def _sq_dist(a: Vector, b: Vector) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


# --- 3. Dual-Track Attention ---

def dual_track_attention(
    *, query: Vector, local_track: list[Vector], global_track: list[Vector], local_gate: float = 0.5
) -> dict[str, Any]:
    """Blend a local (recent) attention readout with a global (compressed) one. Each track sums to 1."""
    if not 0.0 <= local_gate <= 1.0:
        raise ValueError("local_gate must be in [0, 1]")
    local_attn = _attend(query, local_track)
    global_attn = _attend(query, global_track)
    local_read = _readout(local_attn, local_track)
    global_read = _readout(global_attn, global_track)
    combined = [local_gate * lr + (1.0 - local_gate) * gr for lr, gr in zip(local_read, global_read)]
    return {
        "local_attention": local_attn,
        "global_attention": global_attn,
        "combined": combined,
        "local_gate": local_gate,
    }


def _attend(query: Vector, keys: list[Vector]) -> Vector:
    if not keys:
        return []
    scale = len(query) ** 0.5
    return ops.softmax([ops.dot(query, k) / scale for k in keys])


def _readout(attn: Vector, values: list[Vector]) -> Vector:
    if not values:
        return [0.0] * 0
    dim = len(values[0])
    out = [0.0] * dim
    for w, v in zip(attn, values):
        for d in range(dim):
            out[d] += w * v[d]
    return out


# --- 4. External Memory Router ---

def external_memory_router(
    *, in_context_score: float, external_score: float, margin: float = 0.05
) -> dict[str, Any]:
    """Route to whichever store scores higher by more than `margin`; else stay in-context."""
    if external_score > in_context_score + margin:
        route = "external_memory"
    else:
        route = "in_context"
    return {
        "route": route,
        "in_context_score": in_context_score,
        "external_score": external_score,
        "margin": margin,
    }


# --- 5. Compressed Summary Injector ---

def compressed_summary(*, centroids: list[Vector], weights: list[float] | None = None) -> Vector:
    """Build one injected summary vector as a weighted (default uniform) mean of centroids."""
    if not centroids:
        raise ValueError("need at least one centroid")
    if weights is None:
        weights = [1.0 / len(centroids)] * len(centroids)
    else:
        total = sum(weights) or 1.0
        weights = [w / total for w in weights]
    dim = len(centroids[0])
    summary = [0.0] * dim
    for w, c in zip(weights, centroids):
        for d in range(dim):
            summary[d] += w * c[d]
    return summary


# --- 6. Position Encoding Overhaul (RoPE + YaRN scale) ---

def long_context_scale(*, trained_context: int, target_context: int) -> float:
    """YaRN-style frequency scale to extend RoPE from trained_context to target_context (>=1)."""
    if trained_context <= 0 or target_context <= 0:
        raise ValueError("contexts must be positive")
    return max(1.0, target_context / trained_context)


class NexusMemoryNet:
    def __init__(self, *, keep_fraction: float = 0.5, num_clusters: int = 4, local_gate: float = 0.5) -> None:
        self.keep_fraction = keep_fraction
        self.num_clusters = num_clusters
        self.local_gate = local_gate

    def process(
        self,
        *,
        token_vectors: list[Vector],
        relevances: list[float],
        query: Vector,
        local_window: int = 8,
        trained_context: int = 4096,
        target_context: int = 1_000_000,
    ) -> dict[str, Any]:
        if len(token_vectors) != len(relevances):
            raise ValueError("token_vectors and relevances must align")
        # 1. Sparse pre-filter.
        pre = sparse_pre_filter(relevances=relevances, keep_fraction=self.keep_fraction)
        kept = [token_vectors[i] for i in pre["kept_indices"]]
        # 2. Semantic compression of the survivors into centroids (global memory).
        compressed = semantic_compress(vectors=kept, num_clusters=self.num_clusters)
        centroids = compressed["centroids"]
        # 3. Dual-track attention: local = most-recent kept tokens, global = centroids.
        local_track = kept[-local_window:]
        dual = dual_track_attention(
            query=query, local_track=local_track, global_track=centroids, local_gate=self.local_gate
        )
        # 4. External memory routing (scores from attention mass concentration).
        in_ctx = max(dual["local_attention"]) if dual["local_attention"] else 0.0
        ext = max(dual["global_attention"]) if dual["global_attention"] else 0.0
        route = external_memory_router(in_context_score=in_ctx, external_score=ext)
        # 5. Compressed summary injection.
        summary = compressed_summary(centroids=centroids)
        # 6. Long-context position scale.
        scale = long_context_scale(trained_context=trained_context, target_context=target_context)
        return {
            "surface_id": "nexus-memory-net",
            "pre_filter": pre,
            "num_centroids": compressed["num_clusters"],
            "dual_track": {
                "local_attention_sums_to_one": abs(sum(dual["local_attention"]) - 1.0) < 1e-9
                if dual["local_attention"] else True,
                "global_attention_sums_to_one": abs(sum(dual["global_attention"]) - 1.0) < 1e-9
                if dual["global_attention"] else True,
                "combined": dual["combined"],
            },
            "memory_route": route["route"],
            "injected_summary": summary,
            "long_context_scale": scale,
            "target_context": target_context,
            "production_mutation_allowed": False,
            "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
        }
