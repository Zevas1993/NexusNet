"""Stigmergy / Ant-Colony pheromone trails (canon: HiveBlackboard priority trails).

Indirect coordination through environment marks: agents deposit "pheromone" on the edges they use;
others follow strong trails; trails EVAPORATE so stale paths fade. ACO update:

    tau_ij <- (1 - rho) * tau_ij + sum_k delta_tau_ij^k        (rho = evaporation rate)

Canon safety inversion: decay (rho) is MANDATORY so old routes fade and the trail is auditable.
Invariant: with no deposits, every trail decays monotonically toward 0 (no permanent silent bias).
Pure-Python, deterministic, shadow-only.
"""
from __future__ import annotations

from typing import Any


class PheromoneField:
    def __init__(self, *, evaporation_rate: float = 0.1) -> None:
        if not 0.0 < evaporation_rate <= 1.0:
            raise ValueError("evaporation_rate must be in (0, 1]")
        self.rho = evaporation_rate
        self.trails: dict[str, float] = {}

    def strength(self, edge: str) -> float:
        return self.trails.get(edge, 0.0)

    def step(self, deposits: dict[str, float] | None = None) -> dict[str, float]:
        """One ACO update: evaporate all trails, then add this round's deposits."""
        deposits = deposits or {}
        # Evaporate every known edge (and any edge receiving a deposit).
        edges = set(self.trails) | set(deposits)
        updated: dict[str, float] = {}
        for edge in edges:
            evaporated = (1.0 - self.rho) * self.trails.get(edge, 0.0)
            updated[edge] = evaporated + max(0.0, deposits.get(edge, 0.0))
        self.trails = updated
        return dict(self.trails)

    def routing_affinity(self) -> dict[str, float]:
        """Normalized trail strengths as a routing-affinity distribution (sums to 1 if non-empty)."""
        total = sum(self.trails.values())
        if total <= 0.0:
            return {edge: 0.0 for edge in self.trails}
        return {edge: v / total for edge, v in self.trails.items()}

    def snapshot(self) -> dict[str, Any]:
        return {
            "evaporation_rate": self.rho,
            "trails": dict(self.trails),
            "routing_affinity": self.routing_affinity(),
            "production_mutation_allowed": False,
            "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
        }
