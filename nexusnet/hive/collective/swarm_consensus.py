"""Swarm decision-making (Particle Swarm Optimization) for route/parameter consensus.

Decentralized particles each get pulled toward their own best (pbest) and the global best (gbest):

    v <- w*v + c1*r1*(pbest - x) + c2*r2*(gbest - x)
    x <- x + v

Canon use: route/parameter consensus across capsules; gbest = the Cortex's global pick, pbest = each
capsule's local model (reference-frame swarm). Minimization. Deterministic via a seeded LCG so runs
are replayable. Invariant: the global-best score is monotonically non-increasing across iterations.
Shadow-only.
"""
from __future__ import annotations

from typing import Any, Callable

from ._rng import DeterministicRNG

Vector = list[float]


def pso_minimize(
    fitness: Callable[[Vector], float],
    *,
    dim: int,
    bounds: tuple[float, float] = (-5.0, 5.0),
    num_particles: int = 12,
    iterations: int = 30,
    inertia: float = 0.7,
    cognitive: float = 1.4,
    social: float = 1.4,
    seed: int = 0,
) -> dict[str, Any]:
    rng = DeterministicRNG(seed)
    low, high = bounds
    positions: list[Vector] = [[rng.uniform(low, high) for _ in range(dim)] for _ in range(num_particles)]
    velocities: list[Vector] = [[0.0] * dim for _ in range(num_particles)]
    pbest = [list(p) for p in positions]
    pbest_score = [fitness(p) for p in positions]
    gbest_index = min(range(num_particles), key=lambda i: pbest_score[i])
    gbest = list(pbest[gbest_index])
    gbest_score = pbest_score[gbest_index]
    history: list[float] = [gbest_score]

    for _ in range(iterations):
        for i in range(num_particles):
            for d in range(dim):
                r1, r2 = rng.random(), rng.random()
                velocities[i][d] = (
                    inertia * velocities[i][d]
                    + cognitive * r1 * (pbest[i][d] - positions[i][d])
                    + social * r2 * (gbest[d] - positions[i][d])
                )
                positions[i][d] += velocities[i][d]
                # Clamp into bounds.
                positions[i][d] = max(low, min(high, positions[i][d]))
            score = fitness(positions[i])
            if score < pbest_score[i]:
                pbest_score[i] = score
                pbest[i] = list(positions[i])
                if score < gbest_score:
                    gbest_score = score
                    gbest = list(positions[i])
        history.append(gbest_score)

    return {
        "gbest": gbest,
        "gbest_score": gbest_score,
        "score_history": history,
        "iterations": iterations,
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
