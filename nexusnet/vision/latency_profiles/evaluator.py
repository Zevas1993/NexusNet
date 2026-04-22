from __future__ import annotations

from typing import Any


def evaluate_latency_profile(*, profile_id: str, profiles: dict[str, Any], max_resolution: int | None = None) -> dict[str, Any]:
    profile = dict((profiles or {}).get(profile_id, {}))
    configured_resolution = int(profile.get("max_resolution", 0) or 0)
    resolution = int(max_resolution or configured_resolution or 0)
    return {
        "profile_id": profile_id,
        "found": bool(profile),
        "latency_budget_ms": profile.get("latency_budget_ms"),
        "quality_bias": profile.get("quality_bias"),
        "intended_modes": list(profile.get("intended_modes", [])),
        "resolution_ok": resolution <= configured_resolution if configured_resolution else False,
        "max_resolution": configured_resolution,
    }
