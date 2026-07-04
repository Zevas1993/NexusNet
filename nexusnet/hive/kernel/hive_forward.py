"""B8 - CapsuleHiveKernel: the assembled real neural-network forward (capsule + EBT + cortex + geometry).

This is the canon hive forward as one object: the B4 capsule-router/EBT path produces pose vectors
and a deliberated output; the B6 Cortex applies global-workspace ignition and per-expert dream
routing over those poses; the B8 geometry layer attaches the per-plane Platonic/harmonic signature
(Euler == 2). Pure-Python, deterministic, shadow-only - every decision still flows through the
existing policy / eval / governance gates; nothing here mutates production or trains native weights.
"""
from __future__ import annotations

from typing import Any

from . import tensor_ops as ops
from .capsule_forward import CapsuleForward
from .cortex import Cortex
from .geometry import all_plane_signatures


class CapsuleHiveKernel:
    def __init__(
        self,
        *,
        d_model: int = 16,
        d_pose: int = 8,
        num_experts: int = 6,
        top_k: int = 2,
        deliberation_steps: int = 16,
        ignition_ratio: float = 0.5,
    ) -> None:
        self.forward_kernel = CapsuleForward(
            d_model=d_model,
            d_pose=d_pose,
            num_experts=num_experts,
            top_k=top_k,
            deliberation_steps=deliberation_steps,
        )
        self.cortex = Cortex(ignition_ratio=ignition_ratio)

    def forward(
        self,
        *,
        token_values: list[float],
        position: int,
        expert_capability_overlaps: list[int] | None = None,
        dream_mode: str = "individual",
    ) -> dict[str, Any]:
        fwd = self.forward_kernel.forward(
            token_values=token_values,
            position=position,
            expert_capability_overlaps=expert_capability_overlaps,
        )
        # B6: cortex ignition + dream direction over the lower capsule poses.
        ignition = self.cortex.ignite(
            saliences=fwd["capsule_presence"], poses=fwd["capsule_poses"]
        )
        dreams = self.cortex.direct_dreams(
            poses=fwd["capsule_poses"], broadcast=ignition["broadcast"], mode=dream_mode
        )
        # B8: geometry + harmonic cadence per plane.
        geometry = all_plane_signatures()
        return {
            "surface_id": "capsule-hive-kernel",
            "authority": "NexusBrain",
            "computed": True,                       # real numbers, not a formula_ref label
            "forward": fwd,
            "cortex_ignition": ignition,
            "cortex_dreams": dreams,
            "geometry_signature": geometry,
            "euler_invariant_holds": all(
                g["euler_characteristic"] == 2 for g in geometry.values()
            ),
            "harmonic": {
                "phi": ops.PHI,
                "golden_angle_radians": ops.GOLDEN_ANGLE_RADIANS,
                "harmonic_ratios": ops.HARMONIC_RATIOS,
            },
            "production_mutation_allowed": False,
            "native_weight_training": False,
            "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
        }
