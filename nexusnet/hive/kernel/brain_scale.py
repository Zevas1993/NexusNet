"""B7 - Fractal scale runner (canon PB-018: fractal self-similarity).

The SAME capsule-EBT forward interface runs at every brain scale - the mother brain over experts,
an Orchestrator over Assistant-Orchestrators, an AO over experts, an expert over its skills. Each
scale may override the kernel config (experts may differ inside), but the contract (pose-vector in,
forward-evidence out) is identical. Shadow-only.
"""
from __future__ import annotations

from typing import Any

from .capsule_forward import CapsuleForward

# Outer -> inner nesting of the hive.
BRAIN_SCALES: tuple[str, ...] = ("primary", "orchestrator", "assistant_orchestrator", "expert")


class FractalScaleRunner:
    def __init__(
        self,
        *,
        base_config: dict[str, Any] | None = None,
        scale_overrides: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self.base_config = dict(base_config or {})
        self.scale_overrides = scale_overrides or {}

    def _config_for(self, scale: str) -> dict[str, Any]:
        config = dict(self.base_config)
        config.update(self.scale_overrides.get(scale, {}))
        return config

    def run_scale(self, scale: str, *, token_values: list[float], position: int) -> dict[str, Any]:
        if scale not in BRAIN_SCALES:
            raise ValueError(f"unknown scale {scale!r}; allowed {BRAIN_SCALES}")
        kernel = CapsuleForward(**self._config_for(scale))
        result = kernel.forward(token_values=token_values, position=position)
        result["brain_scale"] = scale
        return result

    def run_all(self, *, token_values: list[float], position: int) -> dict[str, Any]:
        """Run the identical forward at every scale; the primary output cascades inward as input."""
        results: dict[str, Any] = {}
        cascade = list(token_values)
        for scale in BRAIN_SCALES:
            res = self.run_scale(scale, token_values=cascade, position=position)
            results[scale] = res
            cascade = res["output"]  # inner scale consumes the outer scale's projection
        return {
            "scales": list(BRAIN_SCALES),
            "results": results,
            "production_mutation_allowed": False,
            "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
        }
