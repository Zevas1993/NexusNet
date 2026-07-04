"""B3 - EBT deliberation (canon C11/C12; source: Energy-Based Transformers 2507.02092).

An EBT assigns an ENERGY to every (context, candidate) pair; lower energy = more compatible.
Prediction = start from a guess and MINIMIZE energy by gradient descent until convergence. This
is "thinking" / System-2: more optimization steps = more deliberation. The hazard-exit gate stops
when the energy stops improving (convergence) or the step budget is exhausted.

v0 uses a convex diagonal energy so the descent is exact, monotone, and fully testable:
    E(z) = 0.5 * sum_i A_i * z_i^2 - sum_i b_i * z_i        (A_i > 0  => strictly convex bowl)
    grad_i = A_i * z_i - b_i
    z <- z - lr * grad                                       (descent; with lr*A_i < 1, monotone)
    fixed point z*_i = b_i / A_i                             (global minimum)

The context vector deterministically defines the metric A (curvature) and the pull b (target),
so the energy is a learned-style compatibility surface, not an external label. Shadow-only.
"""
from __future__ import annotations

from typing import Any

from . import tensor_ops as ops

Vector = list[float]


class EnergyField:
    """Deterministic convex energy field built from a context vector."""

    def __init__(self, context: Vector) -> None:
        if not context:
            raise ValueError("context must be non-empty")
        self.context = list(context)
        # Curvature A_i in (0, 1]: sigmoid of context keeps it positive and bounded so a fixed
        # learning rate stays in the monotone-descent regime (lr * A_i < 1).
        self.A = [0.25 + 0.75 * ops.sigmoid(c) for c in context]   # in (0.25, 1.0)
        # Pull target b_i derived from the context (the compatibility direction).
        self.b = [ops.gelu(c) for c in context]

    def energy(self, z: Vector) -> float:
        return sum(
            0.5 * self.A[i] * z[i] * z[i] - self.b[i] * z[i] for i in range(len(z))
        )

    def grad(self, z: Vector) -> Vector:
        return [self.A[i] * z[i] - self.b[i] for i in range(len(z))]

    def fixed_point(self) -> Vector:
        return [self.b[i] / self.A[i] for i in range(len(self.b))]


def deliberate(
    context: Vector,
    *,
    max_steps: int = 16,
    lr: float = 0.5,
    tol: float = 1e-6,
) -> dict[str, Any]:
    """Predict-by-energy-minimization. Returns the refined candidate + the deliberation trace."""
    field = EnergyField(context)
    z: Vector = [0.0] * len(context)
    energies: list[float] = [field.energy(z)]
    hazards: list[float] = []
    converged = False
    steps_used = 0

    for _ in range(max(1, max_steps)):
        grad = field.grad(z)
        z = [z[i] - lr * grad[i] for i in range(len(z))]
        e_new = field.energy(z)
        improvement = energies[-1] - e_new          # >= 0 in the monotone regime
        energies.append(e_new)
        steps_used += 1
        # Hazard of exiting THIS step: high when the relative improvement is small (converging).
        denom = abs(energies[-2]) + 1.0
        hazard = ops.sigmoid(6.0 * (1.0 - (improvement / denom) / max(tol, 1e-9)))
        hazards.append(max(0.0, min(1.0, hazard)))
        if improvement < tol:
            converged = True
            break

    exit_schedule = ops.hazard_exit_schedule(hazards) if hazards else {
        "exit_probabilities": [], "final_survival": 1.0, "exit_entropy": 0.0
    }
    return {
        "candidate": z,
        "energy_trajectory": energies,
        "final_energy": energies[-1],
        "steps_used": steps_used,
        "converged": converged,
        "fixed_point": field.fixed_point(),
        "exit_schedule": exit_schedule,
        "deliberation_budget": max(1, max_steps),
        "production_mutation_allowed": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
