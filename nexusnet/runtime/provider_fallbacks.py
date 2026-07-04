from __future__ import annotations

from typing import Any

from .model_route_policy import FALLBACK_POLICY, RouteTier
from .model_tier_assignment import _capability_mark
from .provider_registry import candidate_routes, model_from_route, provider_from_route


def fallback_routes_for(
    *,
    selected_route: dict[str, Any],
    tier: RouteTier,
    specificity_category: str | None,
    allow_cloud: bool,
    allow_external_proxy: bool,
    tools: list[dict[str, Any]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    candidates = [
        _capability_mark(route, tier=tier, specificity_category=specificity_category, tools=tools)
        for route in candidate_routes(allow_cloud=allow_cloud, allow_external_proxy=allow_external_proxy)
    ]
    candidates = [
        route
        for route in candidates
        if route["eligible"]
        and not (
            route["provider_id"] == selected_route["provider_id"]
            and route["model_id"] == selected_route["model_id"]
        )
    ]
    candidates.sort(key=lambda route: (float(route.get("cost_per_1m_input") or 0.0) + float(route.get("cost_per_1m_output") or 0.0), -route["quality_score"]))
    return [
        {
            "provider_id": route["provider_id"],
            "model_id": route["model_id"],
            "provider": provider_from_route(route),
            "model": model_from_route(route),
            "fallback_index": index,
            "retry_classes": FALLBACK_POLICY["retry_on"],
        }
        for index, route in enumerate(candidates[:limit], start=1)
    ]


def fallback_policy() -> dict[str, Any]:
    return dict(FALLBACK_POLICY)
