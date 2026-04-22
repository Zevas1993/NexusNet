from __future__ import annotations

from typing import Any

from .triattention import TriAttentionProviderCard


class AttentionProviderRegistry:
    def __init__(self, *, features: dict[str, Any] | None = None):
        self.features = features or {}
        self._providers = {"triattention": TriAttentionProviderCard()}

    def get_provider(self, provider_name: str) -> Any | None:
        return self._providers.get(provider_name)

    def summary(self) -> dict[str, Any]:
        enabled = bool((self.features.get("research") or {}).get("triattention", False))
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "providers": [self._providers["triattention"].summary(enabled=enabled)],
        }
