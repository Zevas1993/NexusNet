from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import new_id, utcnow
from nexusnet.policy import PolicyKernel

from .inference_cost_ledger import build_cost_ledger
from .manifest_adapter import ManifestAdapter
from .model_route_policy import (
    ROUTING_ORDER,
    SPECIFICITY_DEFAULT_TIERS,
    PrivacyClass,
    RiskLevel,
    RouteTier,
    governance_gate,
    operator_actions,
    privacy_gate,
    required_controls,
    route_findings,
    stronger_tier,
)
from .model_scoring import score_request, scoring_messages
from .model_tier_assignment import assign_model
from .provider_fallbacks import fallback_policy, fallback_routes_for
from .provider_registry import provider_catalog
from .task_specificity_router import detect_specificity


class InferenceRouteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    agent_id: str
    messages: list[dict[str, Any]]
    task_type: str | None = None
    tools: list[dict[str, Any]] = Field(default_factory=list)
    max_tokens: int | None = None
    privacy_class: PrivacyClass = "local_only"
    risk_level: RiskLevel = "medium"
    force_tier: RouteTier | None = None
    force_provider: str | None = None
    force_model: str | None = None
    upstream_aitune_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InferenceEconomyRouter:
    def __init__(self, *, artifacts_dir: Path | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.decisions_dir = self.artifacts_dir / "runtime" / "inference-economy-router" if self.artifacts_dir else None
        if self.decisions_dir is not None:
            self.decisions_dir.mkdir(parents=True, exist_ok=True)
        self._memory_decisions: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()
        self.manifest_adapter = ManifestAdapter.default()

    def route(self, request: InferenceRouteRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, InferenceRouteRequest) else InferenceRouteRequest.model_validate(request)
        p_gate = privacy_gate(normalized.privacy_class)
        relevant_messages = scoring_messages(normalized.messages)
        specificity = detect_specificity(
            task_type=normalized.task_type,
            messages=relevant_messages,
            tools=normalized.tools,
        )
        scoring = score_request(
            messages=normalized.messages,
            tools=normalized.tools,
            max_tokens=normalized.max_tokens,
        )
        complexity_tier: RouteTier = scoring["tier"]
        specificity_tier = (
            SPECIFICITY_DEFAULT_TIERS.get(str(specificity.get("category")), complexity_tier)
            if specificity.get("category")
            else complexity_tier
        )
        tier = normalized.force_tier or stronger_tier(complexity_tier, specificity_tier)
        if normalized.risk_level == "critical":
            tier = "reasoning"

        assignment = assign_model(
            tier=tier,
            specificity_category=specificity.get("category"),
            allow_cloud=bool(p_gate["allow_cloud"]),
            allow_external_proxy=bool(p_gate["allow_external_proxy"]),
            tools=normalized.tools,
            force_provider=normalized.force_provider,
            force_model=normalized.force_model,
        )
        selected_route = assignment["selected_route"]
        fallbacks = fallback_routes_for(
            selected_route=selected_route,
            tier=tier,
            specificity_category=specificity.get("category"),
            allow_cloud=bool(p_gate["allow_cloud"]),
            allow_external_proxy=bool(p_gate["allow_external_proxy"]),
            tools=normalized.tools,
        )
        g_gate = governance_gate(
            risk_level=normalized.risk_level,
            specificity_category=specificity.get("category"),
            tier=tier,
        )
        upstream_aitune_gate = _upstream_aitune_gate(normalized.upstream_aitune_gate)
        upstream_aitune_blocked = _upstream_aitune_gate_blocked(upstream_aitune_gate)
        findings = route_findings(
            risk_level=normalized.risk_level,
            specificity_category=specificity.get("category"),
            gate=g_gate,
        )
        if upstream_aitune_blocked:
            findings.append(
                {
                    "rule_id": "router_alignment_blocks_upstream_aitune_gate",
                    "severity": "hard_block",
                    "message": "Inference routing cannot claim routed or live-bound readiness while upstream AITune/QES execution evidence is blocked.",
                }
            )
        reason_codes = _reason_codes(specificity=specificity, scoring=scoring, tier=tier)
        if upstream_aitune_blocked:
            reason_codes = list(dict.fromkeys(reason_codes + ["upstream_aitune_gate_blocked"]))
        output_tokens = normalized.max_tokens or _default_output_tokens(tier)
        cost_ledger = build_cost_ledger(
            trace_id=normalized.trace_id,
            agent_id=normalized.agent_id,
            selected_route=selected_route,
            input_tokens=int(scoring["token_count"]),
            output_tokens=output_tokens,
        )
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized, selected_route, findings, p_gate))
        blocked = bool(findings) or policy_scan.summary.active_hard_fail_count > 0
        status = "blocked-upstream-gate" if upstream_aitune_blocked else (
            "blocked-pending-human-approval" if blocked else "routed-shadow"
        )
        decision = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "inference-economy-router",
            "decision_id": new_id("inference_route"),
            "trace_id": normalized.trace_id,
            "agent_id": normalized.agent_id,
            "created_at": utcnow().isoformat(),
            "status": status,
            "runtime_state": "degraded" if blocked else "live-bound",
            "routing_order": ROUTING_ORDER,
            "tier": tier,
            "provider": assignment["provider"],
            "model": assignment["model"],
            "reason": _reason(specificity=specificity, scoring=scoring, tier=tier, assignment=assignment),
            "confidence": round(max(float(scoring["confidence"]), float(specificity.get("confidence") or 0.0)), 3),
            "specificity_category": specificity.get("category"),
            "specificity": specificity,
            "scoring": scoring,
            "privacy_gate": p_gate,
            "governance_gate": g_gate,
            "upstream_aitune_gate": upstream_aitune_gate,
            "route_findings": findings,
            "reason_codes": reason_codes,
            "fallback_policy": fallback_policy(),
            "fallback_routes": fallbacks,
            "cost_ledger": cost_ledger,
            "estimated_cost_usd": cost_ledger["estimated_cost_usd"],
            "baseline_cost_usd": cost_ledger["baseline_cost_usd"],
            "source": "native",
            "manifest_adapter": _manifest_adapter_summary(self.manifest_adapter),
            "policy_scan": policy_scan.model_dump(mode="json"),
            "operator_actions": operator_actions(),
            "required_controls": required_controls(),
            "metadata": normalized.metadata,
        }
        self._persist(decision)
        return decision

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        decisions = self._list_decisions(limit=limit)
        latest = decisions[0] if decisions else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if latest.get("runtime_state") == "degraded" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "inference-economy-router",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "decision_count": len(decisions),
            "routed_count": sum(1 for decision in decisions if decision.get("status") == "routed-shadow"),
            "blocked_count": sum(1 for decision in decisions if str(decision.get("status", "")).startswith("blocked")),
            "latest_decision": latest,
            "recent_decisions": decisions,
            "provider_catalog": provider_catalog(),
            "manifest_adapter": _manifest_adapter_summary(self.manifest_adapter),
            "required_controls": required_controls(),
            "operator_actions": operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "control_panel_label": "Inference Economy Router / Manifest Assimilation",
            "source_documents": [
                "docs/manifest_assimilation.md",
                "docs/model_routing_strategy.md",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#pb-2026-05-03-053---manifest-inspired-inference-economy-router",
                "https://github.com/mnfst/manifest",
            ],
            "routing_boundary": "manifest-style-cost-routing-is-subordinate-to-nexusbrain-privacy-policy-governance-and-eval-gates",
            "implementation_mode": "native-router-primary-manifest-adapter-optional",
        }

    def _persist(self, decision: dict[str, Any]) -> None:
        self._memory_decisions = [
            item for item in self._memory_decisions if item.get("decision_id") != decision.get("decision_id")
        ]
        self._memory_decisions.insert(0, decision)
        self._memory_decisions = self._memory_decisions[:50]
        if self.decisions_dir is not None:
            path = self.decisions_dir / f"{decision['decision_id']}.json"
            decision["artifact_path"] = str(path)
            path.write_text(json.dumps(decision, indent=2), encoding="utf-8")

    def _list_decisions(self, *, limit: int) -> list[dict[str, Any]]:
        decisions = list(self._memory_decisions)
        seen = {decision.get("decision_id") for decision in decisions}
        if self.decisions_dir is not None:
            for path in self.decisions_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("decision_id") not in seen:
                    decisions.append(payload)
        decisions.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return decisions[:limit]


def _default_output_tokens(tier: str) -> int:
    return {
        "simple": 128,
        "standard": 512,
        "complex": 2048,
        "reasoning": 4096,
        "default": 512,
    }.get(tier, 512)


def _reason(*, specificity: dict[str, Any], scoring: dict[str, Any], tier: str, assignment: dict[str, Any]) -> str:
    category = specificity.get("category") or "generic"
    return (
        f"privacy-first {assignment['capability_rule']} selected {assignment['provider']['provider_id']} "
        f"for {category} request at {tier} tier; scoring roles={','.join(scoring.get('roles_scored') or []) or 'none'}."
    )


def _reason_codes(*, specificity: dict[str, Any], scoring: dict[str, Any], tier: str) -> list[str]:
    reasons = [f"tier::{tier}", f"complexity::{scoring['tier']}"]
    if specificity.get("category"):
        reasons.append(f"specificity::{specificity['category']}")
    reasons.extend(scoring.get("signals") or [])
    return reasons


def _policy_targets(
    request: InferenceRouteRequest,
    selected_route: dict[str, Any],
    findings: list[dict[str, str]],
    p_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"inference-route::{request.trace_id}",
            "target_type": "protocol_adapter",
            "metadata": {
                "enabled": True,
                "trust_envelope": {
                    "authority": "NexusBrain",
                    "provider": selected_route["provider_id"],
                    "privacy_class": request.privacy_class,
                    "allow_cloud": p_gate["allow_cloud"],
                },
            },
        },
        {
            "target_id": f"inference-cost-ledger::{request.trace_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": False,
                "license_state": "approved",
                "provenance_refs": ["route-contract", "cost-ledger"],
                "route_findings": [finding["rule_id"] for finding in findings],
            },
        },
    ]


def _upstream_aitune_gate(gate: dict[str, Any]) -> dict[str, Any]:
    blockers = list(gate.get("blockers") or gate.get("readiness_blockers") or [])
    status = str(gate.get("status") or "not_provided")
    can_execute_here = gate.get("can_execute_here")
    if can_execute_here is False and not blockers:
        blockers.append("upstream_aitune_execution_not_ready")
    if status in {"blocked", "blocked-upstream-gate"} and not blockers:
        blockers.append("upstream_aitune_gate_blocked")
    return {
        **gate,
        "status": status,
        "can_execute_here": can_execute_here,
        "blockers": blockers,
    }


def _upstream_aitune_gate_blocked(gate: dict[str, Any]) -> bool:
    return bool(
        gate.get("can_execute_here") is False
        or gate.get("status") in {"blocked", "blocked-upstream-gate"}
        or gate.get("blockers")
    )


def _manifest_adapter_summary(adapter: ManifestAdapter) -> dict[str, Any]:
    return {
        "enabled": True,
        "base_url": adapter.config.base_url,
        "model": adapter.config.model,
        "capture_response_headers": adapter.config.capture_response_headers,
        "required_env": adapter.required_env(),
        "role": "optional-openai-compatible-proxy-adapter-not-nexusnet-brain",
    }
