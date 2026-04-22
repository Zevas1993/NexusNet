from __future__ import annotations

from typing import Any


class SandboxPolicyService:
    def __init__(self, *, runtime_configs: dict[str, Any], permission_mode: str):
        security = (runtime_configs.get("goose_lane") or {}).get("security") or {}
        self.permission_mode = permission_mode
        self.profiles = list(security.get("sandbox_profiles") or [])
        self.modes = list(security.get("permission_modes") or [])

    def summary(self) -> dict[str, Any]:
        mode = next((item for item in self.modes if item.get("mode_id") == self.permission_mode), None)
        profile_id = (mode or {}).get("sandbox_profile")
        profile = next((item for item in self.profiles if item.get("profile_id") == profile_id), None)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "permission_mode": self.permission_mode,
            "active_profile": profile or {"profile_id": profile_id or "unbound"},
            "profiles": self.profiles,
            "network_access": (profile or {}).get("network_access", "blocked"),
            "filesystem_scope": (profile or {}).get("filesystem_scope", "workspace-only"),
        }
