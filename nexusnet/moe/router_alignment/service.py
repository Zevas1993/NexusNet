from __future__ import annotations

from ..adapter_registry import AdapterRegistry
from ..expert_adapter import ExpertAdapterService


class ExpertRouterAlignmentService:
    def __init__(self, *, registry: AdapterRegistry | None = None, adapters: ExpertAdapterService | None = None):
        self.registry = registry or AdapterRegistry()
        self.adapters = adapters or ExpertAdapterService()

    def snapshot(self, *, router_id: str, expert_ids: list[str]) -> dict:
        router = self.registry.resolve(router_id)
        items = []
        for expert_id in expert_ids:
            expert = self.registry.resolve(expert_id)
            plan = self.adapters.projection_plan(router_spec=router, expert_spec=expert)
            items.append(
                {
                    "expert_id": expert_id,
                    "expert_family": expert.get("family"),
                    "projection_plan": plan,
                    "harness_checks": {
                        "shape_introspection": True,
                        "router_to_expert_bridge": bool(plan["compatible"]),
                        "projection_required": bool(plan["needs_projection"]),
                        "lora_bridge_enabled": bool(plan["lora_bridge"]["enabled"]),
                    },
                }
            )
        incompatible_expert_ids = [item["expert_id"] for item in items if not item["projection_plan"]["compatible"]]
        projection_required_expert_ids = [item["expert_id"] for item in items if item["projection_plan"]["needs_projection"]]
        context_bridge_expert_ids = [item["expert_id"] for item in items if item["projection_plan"]["needs_context_bridge"]]
        alignment_blockers: list[str] = []
        if incompatible_expert_ids:
            alignment_blockers.append("incompatible_router_expert_shapes")
        if projection_required_expert_ids:
            alignment_blockers.append("projection_bridge_required")
        if context_bridge_expert_ids:
            alignment_blockers.append("context_bridge_required")
        if incompatible_expert_ids:
            max_safe_native_mode = "teacher_fallback"
        elif projection_required_expert_ids or context_bridge_expert_ids:
            max_safe_native_mode = "native_shadow"
        else:
            max_safe_native_mode = "native_live_guarded"
        return {
            "status_label": "IMPLEMENTATION BRANCH",
            "router": self.adapters.shape_signature(router),
            "experts": items,
            "compatible_count": sum(1 for item in items if item["projection_plan"]["compatible"]),
            "projection_required_count": sum(1 for item in items if item["projection_plan"]["needs_projection"]),
            "context_bridge_count": sum(1 for item in items if item["projection_plan"]["needs_context_bridge"]),
            "projection_required_expert_ids": projection_required_expert_ids,
            "context_bridge_expert_ids": context_bridge_expert_ids,
            "incompatible_expert_ids": incompatible_expert_ids,
            "alignment_blockers": alignment_blockers,
            "alignment_hold_required": bool(alignment_blockers),
            "max_safe_native_mode": max_safe_native_mode,
            "ready_for_shadow_fusion": all(item["projection_plan"]["compatible"] for item in items),
            "ready_for_challenger_shadow": not incompatible_expert_ids and not context_bridge_expert_ids,
            "ready_for_live_guarded": max_safe_native_mode == "native_live_guarded",
        }
