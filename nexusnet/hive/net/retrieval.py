"""Wave-5: retrieval-augmented + knowledge-graph grounding, with persistence and selective decay.

Canon (Overlay memory row; Aspect 5): the network must GROUND its forward pass in retrieved memory
(GraphRAG/LightRAG/HippoRAG-style) and a knowledge graph, persist that memory across runs (the
1M-token core), and forget intelligently (selective memory decay). This module makes those real:

  - MemoryStore               an episodic store (key/value/text + salience + last-access) with cosine
                              retrieval, selective decay/eviction, and save/load persistence.
  - RetrievalAugmentedMemory  a trainable module that retrieves top-k memory values for a hidden
                              state and cross-attends them in (differentiable grounding).
  - KnowledgeGraph            nodes + edges with subgraph (node + neighbors) retrieval (GraphRAG).
  - GraphGroundedMemory       attend a hidden state over a retrieved subgraph's embeddings.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import torch
import torch.nn as nn

from .layers import RMSNorm


class MemoryStore:
    """Episodic key/value memory with salience, selective decay, and persistence (the token core)."""

    def __init__(self, dim: int) -> None:
        self.dim = dim
        self.keys: list[list[float]] = []
        self.values: list[list[float]] = []
        self.texts: list[str] = []
        self.salience: list[float] = []
        self.last_access: list[float] = []

    def __len__(self) -> int:
        return len(self.keys)

    def add(self, key: torch.Tensor, value: torch.Tensor, *, text: str = "",
            salience: float = 1.0, t: float = 0.0) -> None:
        self.keys.append(key.detach().reshape(-1).tolist())
        self.values.append(value.detach().reshape(-1).tolist())
        self.texts.append(text)
        self.salience.append(float(salience))
        self.last_access.append(float(t))

    def retrieve(self, query: torch.Tensor, k: int = 4, *, t: float | None = None):
        """Top-k by (cosine similarity * salience). Bumps salience/last-access of retrieved entries."""
        if not self.keys:
            return torch.empty(0, self.dim), [], []
        keys = torch.tensor(self.keys, dtype=torch.float32)
        q = query.detach().reshape(-1).float()
        sims = torch.nn.functional.cosine_similarity(keys, q.unsqueeze(0), dim=-1)
        sal = torch.tensor(self.salience)
        score = sims * sal
        kk = min(k, len(self.keys))
        top = torch.topk(score, kk).indices.tolist()
        for i in top:                                            # access reinforces memory
            self.salience[i] = min(4.0, self.salience[i] + 0.5)
            if t is not None:
                self.last_access[i] = float(t)
        values = torch.tensor([self.values[i] for i in top], dtype=torch.float32)
        return values, [self.texts[i] for i in top], top

    def decay(self, *, now: float, half_life: float = 100.0, min_salience: float = 0.1) -> int:
        """Selective memory decay: salience *= 0.5**(dt/half_life); evict entries below the floor."""
        keep_idx = []
        for i in range(len(self.keys)):
            dt = max(0.0, now - self.last_access[i])
            self.salience[i] *= 0.5 ** (dt / max(1e-6, half_life))
            if self.salience[i] >= min_salience:
                keep_idx.append(i)
        evicted = len(self.keys) - len(keep_idx)
        if evicted:
            self.keys = [self.keys[i] for i in keep_idx]
            self.values = [self.values[i] for i in keep_idx]
            self.texts = [self.texts[i] for i in keep_idx]
            self.salience = [self.salience[i] for i in keep_idx]
            self.last_access = [self.last_access[i] for i in keep_idx]
        return evicted

    def save(self, path: str) -> str:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({
            "dim": self.dim, "keys": self.keys, "values": self.values, "texts": self.texts,
            "salience": self.salience, "last_access": self.last_access,
        }), encoding="utf-8")
        return str(p)

    @classmethod
    def load(cls, path: str) -> "MemoryStore":
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        store = cls(d["dim"])
        store.keys, store.values, store.texts = d["keys"], d["values"], d["texts"]
        store.salience, store.last_access = d["salience"], d["last_access"]
        return store


class RetrievalAugmentedMemory(nn.Module):
    """Ground the hidden state in retrieved memory: pool -> retrieve top-k values -> cross-attend in."""

    def __init__(self, d_model: int, k: int = 4) -> None:
        super().__init__()
        self.k = k
        self.norm = RMSNorm(d_model)
        self.attn = nn.MultiheadAttention(d_model, num_heads=1, batch_first=True)
        self.d_model = d_model

    def forward(self, h: torch.Tensor, store: MemoryStore) -> torch.Tensor:
        if len(store) == 0:
            return h
        B, T, D = h.shape
        query = h.mean(dim=1).mean(dim=0)                        # pooled query vector
        values, _texts, _idx = store.retrieve(query, self.k)
        if values.numel() == 0:
            return h
        mem = values.to(h.device).unsqueeze(0).expand(B, -1, -1)  # (B, k, D)
        grounded, _ = self.attn(self.norm(h), mem, mem)          # attend tokens over memory
        return h + grounded


class KnowledgeGraph:
    """A small knowledge graph: node embeddings + undirected edges, with GraphRAG subgraph retrieval."""

    def __init__(self, dim: int) -> None:
        self.dim = dim
        self.nodes: dict[str, list[float]] = {}
        self.adj: dict[str, set[str]] = {}

    def add_node(self, node_id: str, embedding: torch.Tensor) -> None:
        self.nodes[node_id] = embedding.detach().reshape(-1).tolist()
        self.adj.setdefault(node_id, set())

    def add_edge(self, a: str, b: str) -> None:
        self.adj.setdefault(a, set()).add(b)
        self.adj.setdefault(b, set()).add(a)

    def neighbors(self, node_id: str) -> list[str]:
        return sorted(self.adj.get(node_id, set()))

    def subgraph_embeddings(self, node_id: str) -> torch.Tensor:
        """Embeddings of the node + its neighbors (the GraphRAG retrieval unit)."""
        ids = [node_id] + self.neighbors(node_id)
        rows = [self.nodes[i] for i in ids if i in self.nodes]
        if not rows:
            return torch.empty(0, self.dim)
        return torch.tensor(rows, dtype=torch.float32)


class GraphGroundedMemory(nn.Module):
    """Attend a hidden state over a retrieved knowledge-graph subgraph (node + neighbors)."""

    def __init__(self, d_model: int) -> None:
        super().__init__()
        self.norm = RMSNorm(d_model)
        self.attn = nn.MultiheadAttention(d_model, num_heads=1, batch_first=True)

    def forward(self, h: torch.Tensor, graph: KnowledgeGraph, node_id: str) -> torch.Tensor:
        sub = graph.subgraph_embeddings(node_id)
        if sub.numel() == 0:
            return h
        B = h.shape[0]
        ctx = sub.to(h.device).unsqueeze(0).expand(B, -1, -1)
        grounded, _ = self.attn(self.norm(h), ctx, ctx)
        return h + grounded
