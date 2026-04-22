from __future__ import annotations

from typing import Any


class PersistentGuardrailService:
    def __init__(self, *, runtime_configs: dict[str, Any]):
        security = (runtime_configs.get("goose_lane") or {}).get("security") or {}
        self.guardrails = list(security.get("persistent_guardrails") or [])

    def summary(self) -> dict[str, Any]:
        enabled = [item for item in self.guardrails if item.get("enabled", True)]
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "enabled_guardrail_count": len(enabled),
            "guardrails": enabled,
            "always_injected": True,
        }

    def injected_instructions(self, *, tool_name: str | None = None) -> list[str]:
        instructions: list[str] = []
        for guardrail in self.guardrails:
            if not guardrail.get("enabled", True):
                continue
            applies_to = set(guardrail.get("applies_to", []))
            if tool_name is None or tool_name in applies_to or not applies_to:
                instructions.append(str(guardrail.get("instruction", "")))
        return instructions
