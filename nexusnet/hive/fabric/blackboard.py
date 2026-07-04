"""The HiveBlackboard - stigmergic shared coordination surface (canon: HiveBlackboard priority trails).

Nodes coordinate INDIRECTLY by posting signals to a shared board; others read the strongest signals.
Each post deposits "pheromone" on its topic; trails EVAPORATE every tick (mandatory decay, auditable)
so stale coordination fades and there is no permanent silent bias. Built on the collective stigmergy
pheromone field. Pure-Python, deterministic, shadow-only.
"""
from __future__ import annotations

from typing import Any

from ..collective.stigmergy import PheromoneField


class HiveBlackboard:
    def __init__(self, *, evaporation_rate: float = 0.2) -> None:
        self._field = PheromoneField(evaporation_rate=evaporation_rate)
        self._signals: dict[str, dict[str, Any]] = {}   # topic -> latest signal payload

    def post(self, *, topic: str, node_id: str, salience: float, payload: dict[str, Any] | None = None) -> None:
        if salience < 0.0:
            raise ValueError("salience must be non-negative")
        self._field.step({topic: salience})              # deposit + evaporate-on-write handled by step
        self._signals[topic] = {"node_id": node_id, "salience": salience, "payload": payload or {}}

    def tick(self) -> None:
        """Evaporate all trails one step (no deposits) - stale coordination fades."""
        self._field.step()

    def strength(self, topic: str) -> float:
        return self._field.strength(topic)

    def read_top(self, k: int = 3) -> list[dict[str, Any]]:
        """The k strongest active topics (trail strength), with their latest signal."""
        ranked = sorted(self._field.trails.items(), key=lambda kv: kv[1], reverse=True)
        out = []
        for topic, strength in ranked[:k]:
            if strength <= 0.0:
                continue
            entry = {"topic": topic, "strength": strength}
            entry.update(self._signals.get(topic, {}))
            out.append(entry)
        return out

    def snapshot(self) -> dict[str, Any]:
        return {
            "trails": dict(self._field.trails),
            "routing_affinity": self._field.routing_affinity(),
            "active_topics": [t for t, s in self._field.trails.items() if s > 1e-9],
            "production_mutation_allowed": False,
        }
