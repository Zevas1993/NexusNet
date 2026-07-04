"""The Neural Bus - bandwidth-efficient message passing between hive nodes (canon C01M0057).

Nodes do NOT ship full hidden state to each other; they ship the canon Neural-Bus tuple:
    (source_id, target_id, summary_embedding[pose vector], uncertainty, request_for_help, token_ids)
The pose vector IS the summary; uncertainty is the inverse of the squash length. This keeps inter-node
traffic small (summaries, not full activations). The bus tracks bandwidth so the efficiency is auditable.

Pure-Python, deterministic, shadow-only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

Vector = list[float]


@dataclass
class NeuralBusMessage:
    source_id: str
    target_id: str | None              # None = broadcast to all subscribers
    summary_embedding: Vector          # the pose vector (the summary), NOT full hidden state
    uncertainty: float = 0.0           # 1 - squash length
    request_for_help: bool = False
    token_ids: list[int] = field(default_factory=list)

    def bandwidth_floats(self) -> int:
        """Floats actually moved: the summary + a tiny header (vs full hidden state if sent raw)."""
        return len(self.summary_embedding) + 3


class NeuralBus:
    def __init__(self) -> None:
        self._queues: dict[str, list[NeuralBusMessage]] = {}
        self._subscribers: set[str] = set()
        self.bandwidth_floats_used: int = 0
        self.message_count: int = 0

    def register(self, node_id: str) -> None:
        self._queues.setdefault(node_id, [])
        self._subscribers.add(node_id)

    def publish(self, message: NeuralBusMessage) -> None:
        self.message_count += 1
        self.bandwidth_floats_used += message.bandwidth_floats()
        if message.target_id is None:
            for node_id in self._subscribers:
                if node_id != message.source_id:
                    self._queues.setdefault(node_id, []).append(message)
        else:
            self._queues.setdefault(message.target_id, []).append(message)

    def deliver(self, node_id: str) -> list[NeuralBusMessage]:
        """Drain and return the messages waiting for a node."""
        msgs = self._queues.get(node_id, [])
        self._queues[node_id] = []
        return msgs

    def efficiency(self, *, full_state_dim: int) -> dict[str, Any]:
        """How much cheaper the summary traffic was vs shipping full hidden state per message."""
        full_cost = self.message_count * full_state_dim
        return {
            "messages": self.message_count,
            "summary_floats_moved": self.bandwidth_floats_used,
            "full_state_floats_if_raw": full_cost,
            "bandwidth_saving_ratio": (1.0 - self.bandwidth_floats_used / full_cost) if full_cost else 0.0,
            "production_mutation_allowed": False,
        }
