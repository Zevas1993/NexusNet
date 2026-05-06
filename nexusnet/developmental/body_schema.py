from __future__ import annotations

from typing import Any

from .contracts import NexusBodySchemaSnapshot


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
            if state.get("runtime_state") == "degraded" or int(state.get("blocked_count") or 0) > 0
        ]
        blocked = [
            name
            for name, state in states.items()
            if int(state.get("blocked_count") or 0) > 0 or str(state.get("status") or "").startswith("blocked")
        ]
        counts = {
            "runtime": int((runtime_state or {}).get("provider_count") or (runtime_state or {}).get("route_count") or 0),
            "memory": int((memory_state or {}).get("claim_count") or (memory_state or {}).get("record_count") or 0),
            "authority": int((authority_state or {}).get("grant_count") or (authority_state or {}).get("adapter_count") or 0),
            "eval": int((eval_state or {}).get("suite_count") or (eval_state or {}).get("search_count") or 0),
            "tool": int((tool_state or {}).get("plan_count") or 0),
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
