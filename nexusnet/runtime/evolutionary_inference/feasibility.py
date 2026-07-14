from __future__ import annotations

from .primitives import InferencePrimitiveRegistry
from .schemas import (
    CandidateFeasibility,
    FeasibilityCandidate,
    HardwareCapabilityGraph,
    ModelExecutionFingerprint,
)


class CandidateFeasibilityEvaluator:
    def evaluate(
        self,
        *,
        graph: HardwareCapabilityGraph,
        fingerprint: ModelExecutionFingerprint,
        registry: InferencePrimitiveRegistry,
    ) -> CandidateFeasibility:
        ram_bytes = max(
            (node.memory_bytes or 0 for node in graph.nodes if node.kind == "system-ram"),
            default=0,
        )
        gpu_bytes = max(
            (node.memory_bytes or 0 for node in graph.nodes if node.kind == "gpu"),
            default=0,
        )
        is_moe = fingerprint.expert_count > 0 and fingerprint.experts_per_token > 0
        candidates: list[FeasibilityCandidate] = []

        portable = registry.get("portable.cpu-reference")
        portable_fits = portable.implementation_state == "available" and fingerprint.tensor_bytes <= ram_bytes * 0.85
        candidates.append(
            FeasibilityCandidate(
                primitive_id=portable.primitive_id,
                feasible=portable_fits,
                score=0.45 if is_moe else 0.75,
                reason_codes=["portable-system-memory-fit"] if portable_fits else ["insufficient-system-memory"],
            )
        )

        moe = registry.get("moe.selective-residency")
        expert_working_set = (
            fingerprint.tensor_bytes * fingerprint.experts_per_token / fingerprint.expert_count if is_moe else 0
        )
        moe_fits = (
            is_moe
            and moe.implementation_state == "available"
            and gpu_bytes > 0
            and fingerprint.tensor_bytes <= ram_bytes * 0.9
            and expert_working_set <= gpu_bytes * 0.9
        )
        moe_reasons = ["limited-vram-tiered-residency"] if moe_fits and gpu_bytes < fingerprint.tensor_bytes else []
        if not moe_fits:
            if not is_moe:
                moe_reasons.append("model-is-not-moe")
            elif gpu_bytes <= 0:
                moe_reasons.append("accelerator-unavailable")
            elif fingerprint.tensor_bytes > ram_bytes * 0.9:
                moe_reasons.append("insufficient-system-memory")
            elif expert_working_set > gpu_bytes * 0.9:
                moe_reasons.append("expert-working-set-exceeds-vram")
            else:
                moe_reasons.append("primitive-unavailable")
        candidates.append(
            FeasibilityCandidate(
                primitive_id=moe.primitive_id,
                feasible=moe_fits,
                score=0.9 if moe_fits else 0,
                reason_codes=moe_reasons,
            )
        )

        feasible = sorted(
            (candidate for candidate in candidates if candidate.feasible),
            key=lambda candidate: (-candidate.score, candidate.primitive_id),
        )
        if not feasible:
            blockers = sorted(
                {
                    reason
                    for candidate in candidates
                    for reason in candidate.reason_codes
                    if reason in {"insufficient-system-memory", "expert-working-set-exceeds-vram", "accelerator-unavailable"}
                }
            )
            return CandidateFeasibility(
                status="blocked",
                selected_primitive_id=None,
                candidates=candidates,
                reason_codes=["no-feasible-inference-primitive"],
                blockers=blockers or ["no-available-primitive"],
                confidence=0,
            )

        selected = feasible[0]
        return CandidateFeasibility(
            status="shadow-feasible",
            selected_primitive_id=selected.primitive_id,
            candidates=candidates,
            reason_codes=selected.reason_codes,
            blockers=[],
            confidence=selected.score,
        )
