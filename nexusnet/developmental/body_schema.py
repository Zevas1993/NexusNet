from __future__ import annotations

from typing import Any

from .contracts import NexusBodySchemaSnapshot


def _safe_int(value: Any) -> int:
    if value is None or value == "" or isinstance(value, bool):
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


class NexusBodySchemaBuilder:
    def snapshot(
        self,
        *,
        runtime_state: dict[str, Any] | None = None,
        memory_state: dict[str, Any] | None = None,
        authority_state: dict[str, Any] | None = None,
        eval_state: dict[str, Any] | None = None,
        tool_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        states = {
            "runtime": runtime_state or {},
            "memory": memory_state or {},
            "authority": authority_state or {},
            "eval": eval_state or {},
            "tool": tool_state or {},
        }
        degraded = [
            name
            for name, state in states.items()
            if state.get("runtime_state") == "degraded" or _safe_int(state.get("blocked_count")) > 0
        ]
        blocked = [
            name
            for name, state in states.items()
            if _safe_int(state.get("blocked_count")) > 0 or str(state.get("status") or "").startswith("blocked")
        ]
        counts = {
            "runtime": _safe_int((runtime_state or {}).get("provider_count") or (runtime_state or {}).get("route_count")),
            "memory": _safe_int((memory_state or {}).get("claim_count") or (memory_state or {}).get("record_count")),
            "authority": _safe_int((authority_state or {}).get("grant_count") or (authority_state or {}).get("adapter_count")),
            "eval": _safe_int((eval_state or {}).get("suite_count") or (eval_state or {}).get("search_count")),
            "tool": _safe_int((tool_state or {}).get("plan_count")),
        }
        runtime_label = "degraded" if degraded or blocked else (
            "live-bound" if any(counts.values()) else "static-canon"
        )
        return NexusBodySchemaSnapshot(
            runtime_state=runtime_label,
            capability_counts=counts,
            degraded_surfaces=sorted(set(degraded)),
            blocked_surfaces=sorted(set(blocked)),
        ).model_dump(mode="json")
