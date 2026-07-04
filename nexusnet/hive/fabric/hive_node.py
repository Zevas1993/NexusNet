"""A HiveNode - one brain in the fabric at a given scale (canon: fractal nested mini-brains).

Each node receives Neural-Bus summaries from its neighbours, aggregates them (weighted by 1 -
uncertainty), computes its own pose vector (squash), and - only if it ignites (sparse activation) -
re-emits its pose to connected nodes and posts its salience to the HiveBlackboard. Edges are TYPED
(trusts / aligned_with / predicts) per the canon hyperedge contract. Pure-Python, deterministic.
"""
from __future__ import annotations

import math
from typing import Any

from ..kernel import tensor_ops as ops
from ..kernel.capsule import squash, Vector
from .neural_bus import NeuralBus, NeuralBusMessage
from .blackboard import HiveBlackboard

NODE_TYPES = ("core", "orchestrator", "assistant_orchestrator", "expert")
EDGE_TYPES = ("trusts", "aligned_with", "predicts")


class HiveNode:
    def __init__(self, *, node_id: str, node_type: str, d_pose: int = 8, phase_index: int = 0) -> None:
        if node_type not in NODE_TYPES:
            raise ValueError(f"unknown node_type {node_type!r}; allowed {NODE_TYPES}")
        self.node_id = node_id
        self.node_type = node_type
        self.d_pose = d_pose
        self.phase_index = phase_index
        self.edges: dict[str, str] = {}                 # target_id -> edge_type
        self.last_pose: Vector = [0.0] * d_pose
        self.active = False
        self.activation_count = 0
        # Per-node Ivy-League teacher ensemble (canon: per expert / AO / orchestrator). Each entry is
        # {teacher_id, role in coach/critic/socratic/referee}. Teachers are EXTERNAL models the node is
        # distilled from during bootstrap, then replaced once the node surpasses them.
        self.teacher_binding: list[dict[str, str]] = []
        # Expert nodes carry a designed AREA OF EXPERTISE and a curriculum DERIVED FROM that domain
        # (canon: each capsule's curriculum is domain-specific, not a universal pipeline).
        self.area_of_expertise: str | None = None
        self.curriculum: dict[str, Any] | None = None
        # Sacred-geometry position in the Flower-of-Life field (set by the fabric topology).
        self.position: dict[str, Any] | None = None

    def connect(self, target_id: str, *, edge_type: str = "trusts") -> None:
        if edge_type not in EDGE_TYPES:
            raise ValueError(f"unknown edge_type {edge_type!r}; allowed {EDGE_TYPES}")
        self.edges[target_id] = edge_type

    def _transform(self, agg: Vector) -> Vector:
        """Node-specific golden-phase rotation of the aggregated input, then squash to a pose."""
        unit = ops.l2_normalize(agg)
        out = list(unit)
        for k in range(self.d_pose // 2):
            out[2 * k], out[2 * k + 1] = ops.rotary_pair(
                unit[2 * k], unit[2 * k + 1], position=self.phase_index + 1, k=k
            )
        return out                                       # norm-preserving: signal survives each hop

    @staticmethod
    def _child_key(child_id: str, dim: int) -> Vector:
        seed = sum(ord(c) for c in child_id)
        return ops.l2_normalize([math.cos((seed + 1) * ops.GOLDEN_ANGLE_RADIANS * (i + 1)) for i in range(dim)])

    def step(
        self,
        *,
        bus: NeuralBus,
        blackboard: HiveBlackboard,
        external_input: Vector | None = None,
        activation_threshold: float = 0.05,
        top_k_children: int = 2,
        incoming: list[NeuralBusMessage] | None = None,
        direction: str = "both",          # "down" (to children), "up" (to parents), or "both"
    ) -> dict[str, Any]:
        # 1. Receive Neural-Bus summaries and aggregate. `incoming` is pre-delivered by the fabric for
        #    CLOCKED, order-independent propagation (one level per step); else drain our own queue.
        agg = [0.0] * self.d_pose
        if external_input is not None:
            for i in range(min(self.d_pose, len(external_input))):
                agg[i] += external_input[i]
        if incoming is None:
            incoming = bus.deliver(self.node_id)
        for msg in incoming:
            # Pose summaries propagate at full strength (uncertainty is carried as a help/monitoring
            # signal, NOT a per-hop magnitude tax); aggregate magnitude => agreement across senders.
            for i in range(min(self.d_pose, len(msg.summary_embedding))):
                agg[i] += msg.summary_embedding[i]
        # 2. Salience = presence of arriving signal (squash of the aggregate magnitude).
        mag = ops.norm(agg)
        salience = (mag * mag) / (1.0 + mag * mag)        # in [0, 1)
        self.active = salience >= activation_threshold
        if not self.active:
            self.last_pose = [0.0] * self.d_pose
            return {"node_id": self.node_id, "node_type": self.node_type, "active": False,
                    "salience": salience, "messages_received": len(incoming), "messages_emitted": 0}
        # 3. Norm-preserving pose so the signal propagates through the hierarchy without vanishing.
        pose = self._transform(agg)
        self.last_pose = pose
        self.activation_count += 1
        # 4. Route by phase: DOWN to the top-k children by agreement (sparse), UP to all parents.
        parents = [t for t, et in self.edges.items() if et == "predicts"] if direction in ("up", "both") else []
        children = [t for t, et in self.edges.items() if et == "trusts"] if direction in ("down", "both") else []
        if children:
            children = sorted(
                children, key=lambda c: ops.dot(pose, self._child_key(c, self.d_pose)), reverse=True
            )[: max(1, min(top_k_children, len(children)))]
        emitted = 0
        for target_id in parents + children:
            bus.publish(NeuralBusMessage(
                source_id=self.node_id, target_id=target_id,
                summary_embedding=pose, uncertainty=1.0 - salience,
                request_for_help=salience < 0.25,
            ))
            emitted += 1
        blackboard.post(topic=f"{self.node_type}:{self.node_id}", node_id=self.node_id, salience=salience)
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "active": self.active,
            "salience": salience,
            "messages_received": len(incoming),
            "messages_emitted": emitted,
        }
