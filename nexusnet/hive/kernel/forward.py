"""One real forward pass over the Hive Neural Substrate planes.

Composes the computed ops in tensor_ops into a single deterministic pass:
typed input -> harmonic embed -> golden-angle rotary -> softmax attention -> harmonic
top-k router -> GeGLU experts -> RMSNorm residual -> output projection. Every step produces
real numbers. Shadow-only evidence; no production mutation, no native weight training.
"""
from __future__ import annotations

import math
from typing import Any

from . import tensor_ops as ops


class HiveTensorKernel:
    def __init__(self, *, d_model: int = 16, top_k: int = 2) -> None:
        self.d_model = d_model
        self.top_k = top_k

    def _embed(self, token_values: list[float]) -> list[float]:
        # Deterministic projection of typed token values into d_model, then L2 normalize.
        vec = [0.0] * self.d_model
        for i, value in enumerate(token_values):
            vec[i % self.d_model] += float(value)
        return ops.l2_normalize(vec)

    def forward(
        self,
        *,
        token_values: list[float],
        position: int,
        expert_capability_overlaps: list[int],
    ) -> dict[str, Any]:
        # 1. Embedding plane.
        embedded = self._embed(token_values)

        # 2. Temporal/positional plane: golden-angle rotary + harmonic positional encoding.
        rotated = list(embedded)
        for k in range(self.d_model // 2):
            rotated[2 * k], rotated[2 * k + 1] = ops.rotary_pair(
                embedded[2 * k], embedded[2 * k + 1], position=position, k=k
            )
        positional = ops.harmonic_positional_encoding(position=position, dim=self.d_model)
        contextualized = [r + 0.1 * p for r, p in zip(rotated, positional)]

        # 3. Attention/focus plane: scaled dot-product softmax over the d_model channels.
        d_k = self.d_model
        scores = [contextualized[i] * rotated[i] / (d_k ** 0.5) for i in range(self.d_model)]
        attention = ops.softmax(scores)
        attended = [attention[i] * contextualized[i] for i in range(self.d_model)]

        # 4. Sparse MoE router plane: harmonic-resonance-biased top-k gate.
        gate_logits = [ops.dot(attended, _expert_vector(e, self.d_model)) for e in range(len(expert_capability_overlaps))]
        router_gate = ops.harmonic_resonance_gate(
            capability_overlaps=expert_capability_overlaps,
            gate_logits=gate_logits,
            top_k=self.top_k,
        )

        # 5. Expert computation plane: GeGLU per selected expert, phi-weighted mix.
        expert_out = [0.0] * self.d_model
        for e, weight in enumerate(router_gate):
            if weight <= 0.0:
                continue
            ev = _expert_vector(e, self.d_model)
            gated = ops.geglu([a * ev[i] for i, a in enumerate(attended)], attended)
            for i in range(self.d_model):
                expert_out[i] += weight * gated[i]

        # 6. Residual + RMSNorm plane (pre-norm residual).
        residual = [contextualized[i] + expert_out[i] for i in range(self.d_model)]
        normalized = ops.rms_norm(residual)

        # 7. Recurrent exit gate evidence (single-step schedule here).
        hazard = ops.sigmoid(ops.dot(normalized, _expert_vector(0, self.d_model)))
        exit_schedule = ops.hazard_exit_schedule([hazard])

        # 8. Output projection.
        output = [ops.gelu(x) for x in normalized]

        return {
            "surface_id": "hive-tensor-kernel",
            "authority": "NexusBrain",
            "d_model": self.d_model,
            "top_k": self.top_k,
            "embedded_norm": round(ops.norm(embedded), 8),
            "attention": attention,
            "router_gate": router_gate,
            "router_active_experts": [e for e, g in enumerate(router_gate) if g > 0.0],
            "output": output,
            "output_norm": round(ops.norm(output), 8),
            "exit_schedule": exit_schedule,
            "harmonic": {
                "phi": ops.PHI,
                "golden_angle_radians": ops.GOLDEN_ANGLE_RADIANS,
                "phi_weights": [round(ops.phi_weight(e), 8) for e in range(len(expert_capability_overlaps))],
                "harmonic_ratios": ops.HARMONIC_RATIOS,
                "fibonacci": ops.FIBONACCI[: self.d_model],
            },
            "production_mutation_allowed": False,
            "raw_activation_values_stored": True,
            "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
        }


def _expert_vector(expert_index: int, dim: int) -> list[float]:
    """Deterministic per-expert capability vector (phi-phase basis, unit norm)."""
    vec = []
    for i in range(dim):
        vec.append(math.cos((expert_index + 1) * ops.GOLDEN_ANGLE_RADIANS * (i + 1)))
    return ops.l2_normalize(vec)
