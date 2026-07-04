"""Wave-5: RAG + knowledge-graph grounding into the forward, persistence, selective decay."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    MemoryStore, RetrievalAugmentedMemory, KnowledgeGraph, GraphGroundedMemory,
)


def _store(dim=16, n=6, seed=0):
    g = torch.Generator().manual_seed(seed)
    s = MemoryStore(dim)
    for i in range(n):
        v = torch.randn(dim, generator=g)
        s.add(v, v, text=f"mem{i}", t=0.0)
    return s


# --- MemoryStore retrieval / decay / persistence ---

def test_retrieval_returns_most_similar_and_reinforces():
    s = _store()
    key0 = torch.tensor(s.keys[0])
    before = s.salience[0]
    values, texts, idx = s.retrieve(key0, k=3, t=1.0)
    assert idx[0] == 0 and texts[0] == "mem0"                  # exact key retrieves itself first
    assert values.shape == (3, s.dim)
    assert s.salience[0] > before                              # access reinforced it


def test_selective_decay_evicts_stale_low_salience():
    s = _store(n=5)
    # keep entry 0 fresh; let others go stale
    s.retrieve(torch.tensor(s.keys[0]), k=1, t=1000.0)
    evicted = s.decay(now=1000.0, half_life=10.0, min_salience=0.5)
    assert evicted >= 1                                        # stale ones decayed below floor
    assert len(s) == 5 - evicted


def test_memory_persistence_round_trip(tmp_path):
    s = _store()
    p = s.save(str(tmp_path / "mem.json"))
    r = MemoryStore.load(p)
    assert len(r) == len(s) and r.dim == s.dim
    q = torch.tensor(s.keys[2])
    assert r.retrieve(q, k=1)[2] == s.retrieve(q, k=1)[2]      # same retrieval after reload


# --- retrieval-augmented grounding into the forward (differentiable) ---

def test_retrieval_augmented_memory_grounds_and_backprops():
    s = _store(dim=16)
    ram = RetrievalAugmentedMemory(16, k=3)
    h = torch.randn(2, 5, 16, requires_grad=True)
    out = ram(h, s)
    assert out.shape == h.shape
    assert not torch.allclose(out, h)                          # grounding changed the hidden state
    out.sum().backward()
    assert h.grad.abs().sum() > 0
    assert ram.attn.in_proj_weight.grad is not None            # grounding params learn


def test_retrieval_with_empty_store_is_identity():
    ram = RetrievalAugmentedMemory(16, k=3)
    h = torch.randn(1, 4, 16)
    assert torch.allclose(ram(h, MemoryStore(16)), h)


# --- knowledge-graph grounding (GraphRAG) ---

def test_knowledge_graph_subgraph_and_grounding():
    g = KnowledgeGraph(16)
    for n in ("physics", "energy", "mass", "unrelated"):
        g.add_node(n, torch.randn(16))
    g.add_edge("physics", "energy")
    g.add_edge("physics", "mass")
    assert g.neighbors("physics") == ["energy", "mass"]
    sub = g.subgraph_embeddings("physics")
    assert sub.shape == (3, 16)                                # node + 2 neighbors
    ggm = GraphGroundedMemory(16)
    h = torch.randn(2, 4, 16, requires_grad=True)
    out = ggm(h, g, "physics")
    assert out.shape == h.shape and not torch.allclose(out, h)
    out.sum().backward()
    assert h.grad.abs().sum() > 0
