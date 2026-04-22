from __future__ import annotations


class MixtralDevstralHarness:
    def build(self, *, selected_expert: str | None = None) -> dict:
        expert_ids = ["devstral-coder", "nexusnet-general-mini"]
        if selected_expert in {"researcher", "research"}:
            expert_ids.append("nexusnet-research-mini")
        elif selected_expert in {"coder", "coding"}:
            expert_ids.insert(0, "devstral-coder")
        else:
            expert_ids.append("nexusnet-research-mini")
        return {
            "status_label": "IMPLEMENTATION BRANCH",
            "branch_lineage": "mixtral-devstral-nexusnet",
            "backbone": "mixtral",
            "router_id": "mixtral-router",
            "devstral_integrated": True,
            "mini_nexusnet_per_expert": True,
            "cortex_peer": "cortex-peer",
            "expert_ids": list(dict.fromkeys(expert_ids)),
        }
