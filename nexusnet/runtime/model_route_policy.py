from __future__ import annotations

from typing import Any, Literal


PrivacyClass = Literal["local_only", "allow_cloud", "external_ok"]
RiskLevel = Literal["low", "medium", "high", "critical"]
RouteTier = Literal["simple", "standard", "complex", "reasoning", "default"]

TIER_ORDER: dict[str, int] = {
    "simple": 0,
    "standard": 1,
    "complex": 2,
    "reasoning": 3,
    "default": 1,
}

ROUTING_ORDER = [
    "privacy_policy",
    "explicit_override",
    "policy_route",
    "specificity_route",
    "complexity_route",
    "capability_provider_selection",
    "fallback_selection",
    "execution_trace_recording",
]

SPECIFICITY_DEFAULT_TIERS: dict[str, RouteTier] = {
    "coding": "complex",
    "web_browsing": "standard",
    "data_analysis": "complex",
    "image_generation": "default",
    "video_generation": "default",
    "social_media": "standard",
    "email_management": "standard",
    "calendar_management": "simple",
    "trading": "reasoning",
}

FALLBACK_POLICY = {
    "enabled": True,
    "strategy": "cheapest_capable_then_stronger",
    "retry_on": [
        "timeout",
        "transport_error",
        "rate_limit",
        "provider_unavailable",
        "model_unavailable",
        "upstream_5xx",
    ],
    "do_not_retry_on": [
        "malformed_request",
        "missing_credentials",
        "safety_block",
        "policy_refusal",
    ],
}


def stronger_tier(left: RouteTier, right: RouteTier) -> RouteTier:
    return left if TIER_ORDER[left] >= TIER_ORDER[right] else right


def privacy_gate(privacy_class: PrivacyClass) -> dict[str, Any]:
    allow_cloud = privacy_class in {"allow_cloud", "external_ok"}
    return {
        "privacy_class": privacy_class,
        "allow_cloud": allow_cloud,
        "allow_external_proxy": privacy_class == "external_ok",
        "require_provider_allowlist": privacy_class in {"allow_cloud", "external_ok"},
        "policy_order": "privacy-safety-before-cost",
    }


def governance_gate(*, risk_level: RiskLevel, specificity_category: str | None, tier: str) -> dict[str, Any]:
    requires_human = risk_level in {"high", "critical"} or specificity_category == "trading" or tier == "reasoning"
    return {
        "requires_human_approval": requires_human,
        "risk_level": risk_level,
        "approval_reason": "high-risk-or-reasoning-route" if requires_human else "none",
        "promotion_boundary": "route-decisions-can-execute-only-inside-nexusnet-policy-and-human-gates",
    }


def route_findings(*, risk_level: RiskLevel, specificity_category: str | None, gate: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if gate.get("requires_human_approval") and risk_level in {"high", "critical"}:
        findings.append(
            {
                "rule_id": "high_risk_requires_human_approval",
                "severity": "hard_fail",
                "message": "High-risk inference routes require human approval before execution.",
            }
        )
    if specificity_category == "trading":
        findings.append(
            {
                "rule_id": "trading_routes_require_reasoning_and_human_approval",
                "severity": "hard_fail",
                "message": "Trading-related routes are reasoning-tier and blocked pending human approval.",
            }
        )
    return findings


def operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/inference-economy-router"},
        "route": {"method": "POST", "endpoint": "/ops/brain/inference-economy-router/route"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/inference-economy-router"},
    }


def required_controls() -> list[str]:
    return [
        "privacy_first_route_gate",
        "explicit_override_audit",
        "specificity_routing",
        "complexity_scoring",
        "capability_threshold_selection",
        "local_provider_support",
        "manifest_adapter_optional",
        "fallback_classifier",
        "cost_and_baseline_ledger",
        "redacted_trace_metadata",
    ]
