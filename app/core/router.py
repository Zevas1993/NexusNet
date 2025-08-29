import os

from typing import List, Dict
from .config import settings

class ExpertRouter:
    def __init__(self):
        self.state = {"trust": {name: 0.5 for name in settings.experts.get("capsules", {}).keys()}}

    def route(self, messages: List[Dict[str,str]]) -> str:
        # Plane-aware simple heuristic: pick expert by keyword mapping
        text = " ".join([m.get("content","") for m in messages if m.get("role")=="user"]).lower()
        mapping = settings.router.get("keyword_map", {})
        for expert, keywords in mapping.items():
            if any(kw.lower() in text for kw in keywords) and settings.experts["capsules"].get(expert,{}).get("enabled", True):
                return expert
        # Default
        return settings.router.get("default_expert", "conversationalist")

    def toggle_expert(self, name: str, enabled: bool):
        if name not in settings.experts.get("capsules", {}):
            raise ValueError(f"Unknown expert '{name}'")
        settings.experts["capsules"][name]["enabled"] = bool(enabled)
        from .config import save_yaml, CONFIG_ROOT
        save_yaml(os.path.join(CONFIG_ROOT, "experts.yaml"), settings.experts)
