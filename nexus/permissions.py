from __future__ import annotations

from dataclasses import dataclass, field

from .schemas import ToolManifest


@dataclass
class PermissionContext:
    mode: str = "workspace-write"
    allowed_tools: set[str] = field(default_factory=set)
    denied_tools: set[str] = field(default_factory=set)

    def authorize(self, manifest: ToolManifest) -> dict[str, str | bool]:
        if manifest.tool_name in self.denied_tools:
            return {"allowed": False, "reason": "tool explicitly denied"}
        if self.allowed_tools and manifest.tool_name not in self.allowed_tools:
            return {"allowed": False, "reason": "tool not in allowed set"}
        if self.mode == "danger-full-access":
            return {"allowed": True, "reason": "full access mode"}
        if self.mode == "read-only" and manifest.permission_class not in {"readonly", "internal"}:
            return {"allowed": False, "reason": "read-only mode blocks mutating tool classes"}
        return {"allowed": True, "reason": f"mode={self.mode}"}
