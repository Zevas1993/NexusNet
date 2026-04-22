from __future__ import annotations

from copy import deepcopy


class AdapterRegistry:
    DEFAULT_SPECS = [
        {
            "component_id": "mixtral-backbone",
            "component_type": "backbone",
            "family": "mixtral",
            "hidden_size": 4096,
            "routing_dim": 64,
            "context_window": 131072,
            "adapter_rank": 16,
            "role_tags": ["backbone", "moe"],
        },
        {
            "component_id": "mixtral-router",
            "component_type": "router",
            "family": "mixtral-router",
            "hidden_size": 4096,
            "routing_dim": 64,
            "context_window": 131072,
            "adapter_rank": 8,
            "role_tags": ["router", "moe"],
        },
        {
            "component_id": "devstral-coder",
            "component_type": "expert",
            "family": "devstral",
            "hidden_size": 5120,
            "routing_dim": 64,
            "context_window": 131072,
            "adapter_rank": 32,
            "role_tags": ["coding", "expert"],
        },
        {
            "component_id": "nexusnet-research-mini",
            "component_type": "expert",
            "family": "mini-nexusnet",
            "hidden_size": 4096,
            "routing_dim": 48,
            "context_window": 262144,
            "adapter_rank": 16,
            "role_tags": ["research", "expert"],
        },
        {
            "component_id": "nexusnet-general-mini",
            "component_type": "expert",
            "family": "mini-nexusnet",
            "hidden_size": 3584,
            "routing_dim": 48,
            "context_window": 262144,
            "adapter_rank": 16,
            "role_tags": ["general", "expert"],
        },
        {
            "component_id": "cortex-peer",
            "component_type": "cortex",
            "family": "nexusnet-cortex",
            "hidden_size": 4096,
            "routing_dim": 64,
            "context_window": 262144,
            "adapter_rank": 8,
            "role_tags": ["cortex", "peer"],
        },
    ]

    def __init__(self, specs: list[dict] | None = None):
        self._specs = [deepcopy(item) for item in (specs or self.DEFAULT_SPECS)]
        self._by_id = {item["component_id"]: item for item in self._specs}

    def resolve(self, component_id: str) -> dict:
        return deepcopy(self._by_id[component_id])

    def list_specs(self) -> list[dict]:
        return [deepcopy(item) for item in self._specs]
