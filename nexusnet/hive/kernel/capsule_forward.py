"""B4 - Capsule Router + full forward path (canon C12M0056/0060/0064 Input Preprocessing Engine).

Composes the real building blocks into the section-3 forward path:

    raw input
      -> input normalization (RMSNorm)
      -> typed harmonic embedding
      -> golden-angle rotary + harmonic positional encoding
      -> lower expert CAPSULES emit pose vectors                       (B1)
      -> sparse activation (harmonic-resonance top-k over presence)    (router plane)
      -> routing-by-agreement to higher/cortex capsules               (B2)
      -> EBT energy-minimization deliberation on the consolidation     (B3)
      -> residual + RMSNorm
      -> output projection

Every step produces real numbers. Sparse activation controls compute; full monitoring is preserved
in the returned evidence. Shadow-only; no production mutation, no native weight training.
"""
from __future__ import annotations

import math
from typing import Any

from . import tensor_ops as ops
from .capsule import CapsuleNeuron, Vector
from .agreement_routing import route_by_agreement
from .ebt import deliberate


class CapsuleForward:
    def __init__(
        self,
        *,
        d_model: int = 16,
        d_pose: int = 8,
        num_experts: int = 6,
        top_k: int = 2,
        num_cortex: int = 1,
        deliberation_steps: int = 16,
    ) -> None:
        if top_k > num_experts:
            raise ValueError("top_k cannot exceed num_experts")
        self.d_model = d_model
        self.d_pose = d_pose
        self.num_experts = num_experts
        self.top_k = top_k
        self.num_cortex = num_cortex
        self.deliberation_steps = deliberation_steps
        self.experts = [
            CapsuleNeuron(domain_index=e, d_in=d_model, d_hidden=2 * d_model, d_out=d_pose)
            for e in range(num_experts)
        ]

    def _embed(self, token_values: list[float]) -> Vector:
        vec = [0.0] * self.d_model
        for i, value in enumerate(token_values):
            vec[i % self.d_model] += float(value)
        return ops.l2_normalize(vec)

    def _contextualize(self, embedded: Vector, position: int) -> Vector:
        rotated = list(embedded)
        for k in range(self.d_model // 2):
            rotated[2 * k], rotated[2 * k + 1] = ops.rotary_pair(
                embedded[2 * k], embedded[2 * k + 1], position=position, k=k
            )
        pe = ops.harmonic_positional_encoding(position=position, dim=self.d_model)
        return [r + 0.1 * p for r, p in zip(rotated, pe)]

    def forward(
        self,
        *,
        token_values: list[float],
        position: int,
        expert_capability_overlaps: list[int] | None = None,
    ) -> dict[str, Any]:
        if expert_capability_overlaps is None:
            expert_capability_overlaps = [1] * self.num_experts
        if len(expert_capability_overlaps) != self.num_experts:
            raise ValueError("capability overlaps must match num_experts")

        embedded = self._embed(token_values)
        context = self._contextualize(embedded, position)

        # B1: every lower expert capsule emits a pose vector.
        capsule_outs = [cap.forward(context) for cap in self.experts]
        presence = [c["pose_length"] for c in capsule_outs]

        # Router plane: harmonic-resonance top-k gate over capsule presence -> sparse activation.
        gate = ops.harmonic_resonance_gate(
            capability_overlaps=expert_capability_overlaps,
            gate_logits=presence,
            top_k=self.top_k,
        )
        active = [e for e, g in enumerate(gate) if g > 0.0]
        # Saliency attention over experts (sums to 1) for monitoring.
        attention = ops.softmax(presence)

        # B2: routing-by-agreement from the active lower capsules to the cortex capsules.
        lower_poses = [capsule_outs[e]["pose"] for e in active]
        routing = route_by_agreement(
            lower_poses, num_higher=self.num_cortex, d_higher=self.d_pose, iterations=3
        )
        # Gate-weighted consolidation of cortex poses into a single decision context.
        consolidated = [0.0] * self.d_pose
        for hp in routing["higher_poses"]:
            for d in range(self.d_pose):
                consolidated[d] += hp[d] / max(1, self.num_cortex)

        # B3: EBT deliberation refines the consolidated decision by energy minimization.
        deliberation = deliberate(
            consolidated, max_steps=self.deliberation_steps, lr=0.5, tol=1e-6
        )
        refined = deliberation["candidate"]

        # Residual + RMSNorm, then output projection.
        residual = [consolidated[i] + refined[i] for i in range(self.d_pose)]
        normalized = ops.rms_norm(residual)
        output = [ops.gelu(x) for x in normalized]

        finite = all(math.isfinite(x) for x in output)
        return {
            "surface_id": "hive-capsule-forward",
            "authority": "NexusBrain",
            "d_model": self.d_model,
            "d_pose": self.d_pose,
            "num_experts": self.num_experts,
            "top_k": self.top_k,
            "capsule_presence": presence,
            "capsule_poses": [c["pose"] for c in capsule_outs],
            "router_gate": gate,
            "router_active_experts": active,
            "attention": attention,
            "routing_coupling": routing["coupling"],
            "cortex_poses": routing["higher_poses"],
            "deliberation_steps_used": deliberation["steps_used"],
            "deliberation_converged": deliberation["converged"],
            "final_energy": deliberation["final_energy"],
            "exit_schedule": deliberation["exit_schedule"],
            "output": output,
            "output_norm": round(ops.norm(output), 8),
            "output_finite": finite,
            "production_mutation_allowed": False,
            "raw_activation_values_stored": True,
            "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
        }
