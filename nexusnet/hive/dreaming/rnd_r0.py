"""RND-R0 - Recursive Neural Dreaming x R-Zero co-evolution (canon C38: RND-R0 hybrid).

Data-free self-curriculum: a CHALLENGER proposes tasks at a difficulty near the SOLVER's frontier
(neither trivial nor impossible), the solver attempts them, and both co-evolve. Learning is most
informative when difficulty ~= competence (success prob ~0.5), so the solver gains the most there;
the challenger then tracks the rising frontier. Deterministic, shadow-only.

Invariants: solver competence is monotonically non-decreasing and bounded in [0,1]; the challenger's
difficulty stays within a margin band of the solver's competence (frontier curriculum).
"""
from __future__ import annotations

from typing import Any

from ..kernel import tensor_ops as ops


def rnd_r0_coevolve(
    *,
    rounds: int = 30,
    init_competence: float = 0.1,
    learn_rate: float = 0.08,
    frontier_margin: float = 0.1,
    sharpness: float = 8.0,
) -> dict[str, Any]:
    if not 0.0 <= init_competence <= 1.0:
        raise ValueError("init_competence must be in [0, 1]")
    competence = init_competence
    difficulty = min(1.0, competence + frontier_margin)
    history: list[dict[str, float]] = []

    for _ in range(max(1, rounds)):
        p_solve = ops.sigmoid(sharpness * (competence - difficulty))
        informativeness = 4.0 * p_solve * (1.0 - p_solve)      # peaks at the frontier (p=0.5)
        competence = competence + learn_rate * informativeness * (1.0 - competence)
        difficulty = min(1.0, competence + frontier_margin)    # challenger tracks the frontier
        history.append({
            "competence": competence,
            "difficulty": difficulty,
            "p_solve": p_solve,
            "informativeness": informativeness,
        })

    return {
        "final_competence": competence,
        "final_difficulty": difficulty,
        "history": history,
        "rounds": max(1, rounds),
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
