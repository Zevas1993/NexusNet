"""B5 - MemoryNode (canon C04M0004/0050/0099): the multi-plane memory neuron.

Each MemoryNode is a "neuron as subvectors": one subvector per cognitive PLANE. Cross-plane
attention lets planes attend to one another (learnable-style scaled dot-product, normalized to a
distribution). Typed hyperedges connect nodes (dual-graph: per-plane + whole-brain core graph).
Modern-Hopfield one-step recall gives fast associative episodic retrieval.

11 canon planes: conceptual, temporal, emotional, procedural, imaginal, social, ethical,
metacognitive, goal, spatial, predictive. Pure-Python, deterministic, shadow-only.
"""
from __future__ import annotations

from typing import Any

from . import tensor_ops as ops

Vector = list[float]

PLANES: tuple[str, ...] = (
    "conceptual", "temporal", "emotional", "procedural", "imaginal",
    "social", "ethical", "metacognitive", "goal", "spatial", "predictive",
)

# Canon hyperedge types (edges.yaml).
EDGE_TYPES: tuple[str, ...] = ("trusts", "aligned_with", "predicts")


class MemoryNode:
    def __init__(self, *, node_id: str, planes: dict[str, Vector]) -> None:
        missing = [p for p in PLANES if p not in planes]
        if missing:
            raise ValueError(f"missing planes: {missing}")
        dims = {len(planes[p]) for p in PLANES}
        if len(dims) != 1:
            raise ValueError("all planes must share one dimension")
        self.node_id = node_id
        self.planes = {p: list(planes[p]) for p in PLANES}
        self.d_plane = dims.pop()
        self.edges: list[dict[str, str]] = []

    def add_edge(self, *, edge_type: str, target_node_id: str) -> None:
        if edge_type not in EDGE_TYPES:
            raise ValueError(f"unknown edge type {edge_type!r}; allowed {EDGE_TYPES}")
        self.edges.append({"type": edge_type, "target": target_node_id})

    def cross_plane_attention(self, query_plane: str) -> dict[str, Any]:
        """Scaled dot-product attention from query_plane over all planes; returns a distribution."""
        if query_plane not in PLANES:
            raise ValueError(f"unknown plane {query_plane!r}")
        q = self.planes[query_plane]
        scale = self.d_plane ** 0.5
        scores = [ops.dot(q, self.planes[p]) / scale for p in PLANES]
        attn = ops.softmax(scores)
        mixed = [0.0] * self.d_plane
        for weight, p in zip(attn, PLANES):
            for d in range(self.d_plane):
                mixed[d] += weight * self.planes[p][d]
        return {
            "query_plane": query_plane,
            "attention": {p: attn[i] for i, p in enumerate(PLANES)},
            "attention_vector": attn,
            "mixed": mixed,
        }

    def core_vector(self) -> Vector:
        """Whole-brain-core projection: mean over planes (the global graph binding)."""
        core = [0.0] * self.d_plane
        for p in PLANES:
            for d in range(self.d_plane):
                core[d] += self.planes[p][d] / len(PLANES)
        return core


class HopfieldStore:
    """Modern Hopfield associative memory: one-step retrieval p = softmax(beta * X q); out = X^T p."""

    def __init__(self) -> None:
        self.patterns: list[Vector] = []

    def store(self, pattern: Vector) -> None:
        self.patterns.append(list(pattern))

    def recall(self, query: Vector, *, beta: float = 8.0) -> dict[str, Any]:
        if not self.patterns:
            raise ValueError("no stored patterns")
        scores = [beta * ops.dot(p, query) for p in self.patterns]
        weights = ops.softmax(scores)
        d = len(self.patterns[0])
        retrieved = [0.0] * d
        for w, pattern in zip(weights, self.patterns):
            for i in range(d):
                retrieved[i] += w * pattern[i]
        nearest_index = max(range(len(self.patterns)), key=lambda i: ops.dot(self.patterns[i], query))
        return {
            "retrieved": retrieved,
            "weights": weights,
            "nearest_index": nearest_index,
            "nearest_pattern": self.patterns[nearest_index],
        }
