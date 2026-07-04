"""Differential Evolution (canon `differential_evolution` protocol; Storn-Price).

Population-based optimizer that evolves expert genomes / router policies / prompt-policies:

    mutation:  v_i = x_r1 + F * (x_r2 - x_r3)        (r1,r2,r3 distinct; F in [0,2])
    crossover: u_i[j] = v_i[j] if rand() <= CR else x_i[j]
    selection: keep u_i if fitness(u_i) better than fitness(x_i), else keep x_i   (elitist)

Fitness = the eval scorecard (minimization here). Invariant: selection is elitist, so the best
population fitness NEVER worsens across generations. Deterministic (seeded LCG), shadow-only.
"""
from __future__ import annotations

from typing import Any, Callable

from ._rng import DeterministicRNG

Vector = list[float]


def differential_evolution(
    fitness: Callable[[Vector], float],
    *,
    dim: int,
    bounds: tuple[float, float] = (-5.0, 5.0),
    pop_size: int = 16,
    F: float = 0.6,
    CR: float = 0.9,
    generations: int = 40,
    seed: int = 0,
) -> dict[str, Any]:
    if pop_size < 4:
        raise ValueError("DE needs at least 4 individuals (r1,r2,r3 distinct from i)")
    rng = DeterministicRNG(seed)
    low, high = bounds
    pop: list[Vector] = [[rng.uniform(low, high) for _ in range(dim)] for _ in range(pop_size)]
    scores = [fitness(ind) for ind in pop]
    best_index = min(range(pop_size), key=lambda i: scores[i])
    best = list(pop[best_index])
    best_score = scores[best_index]
    best_history: list[float] = [best_score]

    for _ in range(generations):
        for i in range(pop_size):
            # Pick three distinct indices, all != i.
            idxs = [j for j in range(pop_size) if j != i]
            r1 = idxs[rng.randint(0, len(idxs) - 1)]
            idxs2 = [j for j in idxs if j != r1]
            r2 = idxs2[rng.randint(0, len(idxs2) - 1)]
            idxs3 = [j for j in idxs2 if j != r2]
            r3 = idxs3[rng.randint(0, len(idxs3) - 1)]
            mutant = [
                pop[r1][d] + F * (pop[r2][d] - pop[r3][d]) for d in range(dim)
            ]
            mutant = [max(low, min(high, v)) for v in mutant]
            # Crossover (ensure at least one dim comes from the mutant: j_rand).
            j_rand = rng.randint(0, dim - 1)
            trial = [
                mutant[d] if (rng.random() <= CR or d == j_rand) else pop[i][d]
                for d in range(dim)
            ]
            trial_score = fitness(trial)
            if trial_score <= scores[i]:          # elitist selection
                pop[i] = trial
                scores[i] = trial_score
                if trial_score < best_score:
                    best_score = trial_score
                    best = list(trial)
        best_history.append(best_score)

    return {
        "best": best,
        "best_score": best_score,
        "best_history": best_history,
        "generations": generations,
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
