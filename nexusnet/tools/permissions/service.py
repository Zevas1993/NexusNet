from __future__ import annotations

from typing import Any


class ToolPermissionService:
    def __init__(self, *, permission_mode: str, runtime_configs: dict[str, Any]):
        security = (runtime_configs.get("goose_lane") or {}).get("security") or {}
        self.permission_mode = permission_mode
        self.modes = list(security.get("permission_modes") or [])

    def summary(self) -> dict[str, Any]:
        active = next((mode for mode in self.modes if mode.get("mode_id") == self.permission_mode), None)
        if active is None:
            active = next((mode for mode in self.modes if mode.get("default")), None)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "active_mode": active or {"mode_id": self.permission_mode},
            "available_modes": self.modes,
            "high_risk_requires_review": bool((active or {}).get("high_risk_requires_review", True)),
        }

    def review_request(self, *, requested_tools: list[str], risk_level: str = "medium") -> dict[str, Any]:
        active = self.summary().get("active_mode") or {}
        write_allowed = bool(active.get("allow_workspace_writes", False))
        decision = "allow"
        rationale = "Permission mode permits the requested tool set."
        if risk_level in {"high", "critical"} and active.get("high_risk_requires_review", True):
            decision = "review-required"
            rationale = "High-risk request requires bounded adversary or operator review."
        elif not write_allowed and any(tool.endswith(".write") or tool == "filesystem.write" for tool in requested_tools):
            decision = "deny"
            rationale = "Active permission mode does not allow workspace writes."
        return {
            "permission_mode": active.get("mode_id", self.permission_mode),
            "requested_tools": requested_tools,
            "risk_level": risk_level,
            "decision": decision,
            "rationale": rationale,
        }
