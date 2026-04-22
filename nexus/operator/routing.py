from __future__ import annotations

from typing import Any


class ExpertSelector:
    def __init__(self, runtime_configs: dict[str, Any]):
        self.expert_config = runtime_configs.get("experts", {})
        self.router_config = runtime_configs.get("router", {})

    def select(self, text: str, *, use_retrieval: bool = False) -> str:
        low = text.lower()
        keyword_map = self.router_config.get("keyword_map", {})
        capsules = self.expert_config.get("capsules", {})
        for capsule, keywords in keyword_map.items():
            if capsule not in capsules:
                continue
            if not capsules.get(capsule, {}).get("enabled", True):
                continue
            if any(keyword in low for keyword in keywords):
                return capsule
        if any(token in low for token in ["def ", "class ", "traceback", "exception", "compile", "debug"]):
            if capsules.get("coder", {}).get("enabled", True):
                return "coder"
        if use_retrieval and any(token in low for token in ["what", "which", "who", "when", "where", "why", "source", "citation", "support"]):
            if capsules.get("researcher", {}).get("enabled", True):
                return "researcher"
        return self.router_config.get("default_expert", "conversationalist")
