from __future__ import annotations

from typing import Any


class VisionLatencyProfileRegistry:
    def __init__(self, config: dict[str, Any]):
        self.config = config

    def list_profiles(self) -> dict[str, Any]:
        return self.config.get("latency_profiles", {}) or {}
