from __future__ import annotations

from typing import Any


class ACPProviderCatalog:
    def __init__(self, *, runtime_configs: dict[str, Any]):
        acp = (runtime_configs.get("goose_lane") or {}).get("acp") or {}
        self.enabled = bool(acp.get("enabled", False))
        self.providers = list(acp.get("providers") or [])

    def summary(self) -> dict[str, Any]:
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "enabled": self.enabled,
            "provider_count": len(self.providers),
            "providers": self.providers,
        }
