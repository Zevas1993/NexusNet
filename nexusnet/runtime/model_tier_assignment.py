from __future__ import annotations

from typing import Any

from .model_route_policy import RouteTier
from .provider_registry import candidate_routes, model_from_route, provider_from_route


def assign_model(
    *,
    tier: RouteTier,
    specificity_category: str | None,
    allow_cloud: bool,
    allow_external_proxy: bool,
    tools: list[dict[str, Any]],
    force_provider: str | None = None,
    force_model: str | None = None,
) -> dict[str, Any]:
    routes = candidate_routes(allow_cloud=allow_cloud, allow_external_proxy=allow_external_proxy)
    capable = [_capability_mark(route, tier=tier, specificity_category=specificity_category, tools=tools) for route in routes]
    capable = [route for route in capable if route["eligible"]]
    if force_provider:
        forced = [route for route in capable if route["provider_id"] == force_provider]
        capable = forced or capable
    if force_model:
        forced = [route for route in capable if route["model_id"] == force_model]
        capable = forced or capable
    if not capable:
        routes = candidate_routes(allow_cloud=False, allow_external_proxy=False)
        capable = [_capability_mark(route, tier="simple", specificity_category=None, tools=[]) for route in routes]
    selected = _select(capable, tier=tier)
    return {
        "selected_route": selected,
        "provider": provider_from_route(selected),
        "model": model_from_route(selected),
        "candidate_count": len(capable),
        "capability_rule": _selection_rule(tier),
    }


def _capability_mark(
    route: dict[str, Any],
    *,
    tier: RouteTier,
    specificity_category: str | None,
    tools: list[dict[str, Any]],
) -> dict[str, Any]:
    marked = dict(route)
    blockers: list[str] = []
    if tier != "default" and tier not in route["tier_fit"]:
        blockers.append(f"tier::{tier}")
    if tier == "reasoning" and not route["reasoning_capable"]:
        blockers.append("reasoning-required")
    if tools and not route["tool_capable"]:
        blockers.append("tool-capable-required")
    if specificity_category and specificity_category not in {"calendar_management", "social_media"}:
        capability = "tools" if specificity_category == "trading" else specificity_category
        if capability not in route["capabilities"] and "tools" not in route["capabilities"]:
            blockers.append(f"specificity::{specificity_category}")
    marked["eligible"] = not blockers
    marked["blockers"] = blockers
    return marked


def _select(routes: list[dict[str, Any]], *, tier: RouteTier) -> dict[str, Any]:
    if tier == "simple":
        return sorted(routes, key=lambda route: (_cost(route), -route["quality_score"]))[0]
    if tier == "standard":
        sufficient = [route for route in routes if route["quality_score"] >= 2.0] or routes
        return sorted(sufficient, key=lambda route: (_cost(route), not route["tool_capable"], -route["quality_score"]))[0]
    if tier == "complex":
        return sorted(routes, key=lambda route: (-route["quality_score"], _cost(route)))[0]
    if tier == "reasoning":
        reasoning = [route for route in routes if route["reasoning_capable"]] or routes
        return sorted(reasoning, key=lambda route: (-route["quality_score"], _cost(route)))[0]
    return sorted(routes, key=lambda route: (_cost(route), -route["quality_score"]))[0]


def _selection_rule(tier: RouteTier) -> str:
    return {
        "simple": "cheapest_capable",
        "standard": "cheapest_with_min_quality_tool_capable_preferred",
        "complex": "highest_quality_cost_tiebreak",
        "reasoning": "highest_quality_reasoning_capable",
        "default": "default_route",
    }[tier]


def _cost(route: dict[str, Any]) -> float:
    return float(route.get("cost_per_1m_input") or 0.0) + float(route.get("cost_per_1m_output") or 0.0)
