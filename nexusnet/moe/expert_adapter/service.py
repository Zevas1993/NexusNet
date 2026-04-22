from __future__ import annotations


class ExpertAdapterService:
    def shape_signature(self, spec: dict) -> dict:
        return {
            "component_id": spec.get("component_id"),
            "family": spec.get("family"),
            "hidden_size": int(spec.get("hidden_size") or 0),
            "routing_dim": int(spec.get("routing_dim") or 0),
            "context_window": int(spec.get("context_window") or 0),
            "adapter_rank": int(spec.get("adapter_rank") or 0),
            "component_type": spec.get("component_type"),
        }

    def projection_plan(self, *, router_spec: dict, expert_spec: dict) -> dict:
        router = self.shape_signature(router_spec)
        expert = self.shape_signature(expert_spec)
        hidden_mismatch = router["hidden_size"] != expert["hidden_size"]
        routing_mismatch = router["routing_dim"] != expert["routing_dim"]
        context_mismatch = router["context_window"] != expert["context_window"]
        compatible = all(value > 0 for value in (router["hidden_size"], router["routing_dim"], expert["hidden_size"], expert["routing_dim"]))
        return {
            "adapter_id": f"adapter::{router['component_id']}->{expert['component_id']}",
            "compatible": compatible,
            "needs_projection": hidden_mismatch or routing_mismatch,
            "needs_hidden_projection": hidden_mismatch,
            "needs_router_projection": routing_mismatch,
            "needs_context_bridge": context_mismatch,
            "hidden_projection": (
                {"from_hidden_size": expert["hidden_size"], "to_hidden_size": router["hidden_size"], "kind": "linear-projection"}
                if hidden_mismatch
                else None
            ),
            "router_projection": (
                {"from_routing_dim": expert["routing_dim"], "to_routing_dim": router["routing_dim"], "kind": "router-alignment"}
                if routing_mismatch
                else None
            ),
            "lora_bridge": {
                "enabled": compatible,
                "rank": max(4, min(router["adapter_rank"], expert["adapter_rank"] or router["adapter_rank"], 32)),
            },
            "router_signature": router,
            "expert_signature": expert,
        }
