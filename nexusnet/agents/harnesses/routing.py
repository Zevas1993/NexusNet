from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexusnet.policy import PolicyKernel


TaskType = Literal[
    "backend_coding",
    "unit_tests",
    "scripts",
    "ui_design",
    "code_review",
    "security_review",
    "docs",
    "research",
]
DataSensitivity = Literal["public", "internal", "confidential", "regulated", "secret"]


class HarnessRouteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_type: TaskType = "backend_coding"
    data_sensitivity: DataSensitivity = "internal"
    requires_local: bool = False
    requires_tool_use: bool = False
    requires_ui_taste: bool = False
    requires_code_review: bool = False
    cost_priority: bool = False
    operator_approved_external: bool = False
    dangerously_skip_permissions: bool = False
    source_kind: str = "normal"
    upstream_aitune_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class HarnessModelRouter:
    def __init__(self, routes: list[dict[str, Any]]):
        self.routes = routes
        self.policy_kernel = PolicyKernel.default()
        self._recommendations: list[dict[str, Any]] = []

    @classmethod
    def default(cls) -> "HarnessModelRouter":
        return cls(_default_routes())

    def summary(self) -> dict[str, Any]:
        blocked_count = sum(1 for item in self._recommendations if item.get("decision") == "blocked")
        latest_recommendation = self._recommendations[-1] if self._recommendations else None
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "harness-model-routing",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if blocked_count else "live-bound",
            "route_count": len(self.routes),
            "routing_profiles": list(self.routes),
            "recommendation_count": len(self._recommendations),
            "blocked_count": blocked_count,
            "latest_recommendation": latest_recommendation,
            "recommendations": list(self._recommendations[-10:]),
            "security_rules": _security_rules(),
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
            "routing_boundary": "model-proxies-and-cheap-routes-are-adapters-not-brain-authority",
            "source_refs": _source_refs(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "control_panel_label": "Harness Model Router",
            "source_documents": [
                "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md#cheap-model-harness-routing",
                "https://github.com/Alishahryar1/free-claude-code",
                "https://github.com/coleam00/ai-transformation-workshop",
            ],
            "selection_axes": [
                "task_type",
                "data_sensitivity",
                "cost_priority",
                "tool_use",
                "ui_taste",
                "review_independence",
                "sandbox_permissions",
            ],
        }

    def recommend(self, request: HarnessRouteRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, HarnessRouteRequest) else HarnessRouteRequest.model_validate(request)
        blocked_reasons = _blocked_reasons(normalized)
        security_findings = _security_findings(normalized)
        upstream_aitune_gate = _upstream_aitune_gate(normalized.upstream_aitune_gate)
        upstream_aitune_blocked = _upstream_aitune_gate_blocked(upstream_aitune_gate)
        if upstream_aitune_blocked:
            blocked_reasons.append("router_alignment_blocks_upstream_aitune_gate")
        scored = [
            {
                "route": route,
                "score": _route_score(route, normalized),
                "reason_codes": _reason_codes(route, normalized),
            }
            for route in self.routes
        ]
        scored.sort(key=lambda item: (item["score"], item["route"]["route_id"]), reverse=True)
        selected = scored[0]["route"]
        reason_codes = list(scored[0]["reason_codes"])
        if upstream_aitune_blocked:
            reason_codes = list(dict.fromkeys(reason_codes + ["upstream_aitune_gate_blocked"]))

        decision = "blocked" if blocked_reasons else "allow"
        if (
            decision == "allow"
            and selected["privacy_posture"] == "external-proxy"
            and normalized.data_sensitivity in {"internal", "confidential", "regulated", "secret"}
            and not normalized.operator_approved_external
        ):
            decision = "needs_operator_approval"
            blocked_reasons.append("external_proxy_requires_operator_approval_for_non_public_data")

        policy_targets = [
            {
                "target_id": f"harness-route::{selected['route_id']}",
                "target_type": "protocol_adapter",
                "metadata": {
                    "enabled": decision != "blocked",
                    "trust_envelope": {
                        "authority": "NexusBrain",
                        "route_id": selected["route_id"],
                        "privacy_posture": selected["privacy_posture"],
                        "data_sensitivity": normalized.data_sensitivity,
                    },
                },
            }
        ]
        if upstream_aitune_blocked:
            policy_targets.append(
                {
                    "target_id": f"harness-route-runtime::{selected['route_id']}",
                    "target_type": "tool_execution",
                    "metadata": {
                        "write_enabled": True,
                        "sandboxed": False,
                        "upstream_aitune_gate": upstream_aitune_gate,
                    },
                }
            )
        policy_scan = self.policy_kernel.scan(policy_targets)

        result = {
            "status_label": "LOCKED CANON",
            "surface_id": "harness-model-routing",
            "authority": "NexusBrain",
            "decision": decision,
            "runtime_state": "degraded" if decision == "blocked" else "live-bound",
            "request": normalized.model_dump(mode="json"),
            "selected_route": selected,
            "score": scored[0]["score"],
            "reason_codes": reason_codes,
            "ranked_routes": [
                {
                    "route_id": item["route"]["route_id"],
                    "score": item["score"],
                    "privacy_posture": item["route"]["privacy_posture"],
                    "role": item["route"]["role"],
                }
                for item in scored
            ],
            "blocked_reasons": blocked_reasons,
            "upstream_aitune_gate": upstream_aitune_gate,
            "security_findings": security_findings,
            "caveats": _caveats(normalized, selected),
            "required_controls": _required_controls(),
            "policy_scan": policy_scan.model_dump(mode="json"),
            "decision_rule": "Route model work by task fit, sensitivity, tool needs, UI taste, cost, review independence, and sandbox permission state.",
        }
        self._recommendations.append(result)
        return result


def _default_routes() -> list[dict[str, Any]]:
    return [
        {
            "route_id": "local-nexus-code-harness",
            "label": "Local NexusNet Code Harness",
            "provider_id": "custom-code",
            "role": "private_local_execution",
            "task_types": ["backend_coding", "unit_tests", "scripts", "docs", "research"],
            "privacy_posture": "local-first",
            "cost_posture": "owned-compute",
            "supports_tool_use": True,
            "backend_candidates": ["local-runtime", "lm-studio", "llama-cpp", "ollama"],
            "caveats": ["operator-maintained-runtime", "quality-varies-by-local-model"],
        },
        {
            "route_id": "premium-design-authority",
            "label": "Premium Design / Product Authority",
            "provider_id": "premium-model-harness",
            "role": "design_authority",
            "task_types": ["ui_design", "docs", "research"],
            "privacy_posture": "managed-provider",
            "cost_posture": "premium",
            "supports_tool_use": True,
            "backend_candidates": ["claude-or-openai-design-model"],
            "caveats": ["use_for_first-pass-visual-taste", "requires-provider-data-review"],
        },
        {
            "route_id": "cheap-tool-coding-proxy",
            "label": "Anthropic-Compatible Cheap Tool Coding Proxy",
            "provider_id": "anthropic-compatible-proxy",
            "role": "backend_heavy_lift",
            "task_types": ["backend_coding", "unit_tests", "scripts", "docs"],
            "privacy_posture": "external-proxy",
            "cost_posture": "low-cost",
            "supports_tool_use": True,
            "backend_candidates": [
                "deepseek-anthropic-api",
                "openrouter-model-router",
                "nvidia-nim",
                "lm-studio",
                "llama-cpp",
                "ollama",
            ],
            "caveats": ["public-or-low-risk-work-only", "raw-logs-off", "no-naked-secrets"],
        },
        {
            "route_id": "independent-code-reviewer",
            "label": "Independent Code Review Harness",
            "provider_id": "independent-review-harness",
            "role": "independent_reviewer",
            "task_types": ["code_review", "security_review"],
            "privacy_posture": "deployment-dependent",
            "cost_posture": "quality-first",
            "supports_tool_use": True,
            "backend_candidates": ["codex-reviewer", "local-review-model", "premium-review-model"],
            "caveats": ["must-not-review-own-unverified-change", "requires-diff-and-test-evidence"],
        },
        {
            "route_id": "free-model-cycle",
            "label": "Free Model Cycle",
            "provider_id": "openrouter-free-cycle",
            "role": "low_stakes_drafts",
            "task_types": ["docs", "research", "unit_tests"],
            "privacy_posture": "external-proxy",
            "cost_posture": "free-or-promo",
            "supports_tool_use": False,
            "backend_candidates": ["openrouter-free-models"],
            "caveats": ["rate-limit-risk", "quality-variance", "no-private-data"],
        },
    ]


def _route_score(route: dict[str, Any], request: HarnessRouteRequest) -> int:
    score = 0
    if request.task_type in route["task_types"]:
        score += 8
    else:
        score -= 6
    if request.cost_priority and route["cost_posture"] in {"low-cost", "free-or-promo", "owned-compute"}:
        score += 4
    if request.cost_priority and request.data_sensitivity == "public" and route["cost_posture"] == "low-cost":
        score += 3
    if request.requires_tool_use and route["supports_tool_use"]:
        score += 3
    if request.requires_tool_use and not route["supports_tool_use"]:
        score -= 5
    if request.requires_local:
        score += 12 if route["privacy_posture"] == "local-first" else -20
    if request.data_sensitivity in {"confidential", "regulated", "secret"}:
        score += 12 if route["privacy_posture"] == "local-first" else -18
    elif request.data_sensitivity == "internal" and route["privacy_posture"] == "external-proxy":
        score -= 4
    if request.requires_ui_taste or request.task_type == "ui_design":
        score += 14 if route["role"] == "design_authority" else -8
    if request.requires_code_review or request.task_type in {"code_review", "security_review"}:
        score += 14 if route["role"] == "independent_reviewer" else -8
    return score


def _reason_codes(route: dict[str, Any], request: HarnessRouteRequest) -> list[str]:
    reasons: list[str] = []
    if request.task_type in route["task_types"]:
        reasons.append("task_fit")
    if request.cost_priority and route["cost_posture"] in {"low-cost", "free-or-promo", "owned-compute"}:
        reasons.append("cost_priority")
    if request.requires_tool_use and route["supports_tool_use"]:
        reasons.append("tool_use")
    if route["privacy_posture"] == "local-first":
        reasons.append("local_privacy")
    if route["role"] == "design_authority" and (request.requires_ui_taste or request.task_type == "ui_design"):
        reasons.append("ui_taste_authority")
    if route["role"] == "independent_reviewer" and (request.requires_code_review or request.task_type in {"code_review", "security_review"}):
        reasons.append("review_independence")
    return reasons


def _blocked_reasons(request: HarnessRouteRequest) -> list[str]:
    reasons: list[str] = []
    if request.dangerously_skip_permissions:
        reasons.append("dangerously_skip_permissions_blocked")
    if request.source_kind in {"leaked_source", "proprietary_source_collection", "untrusted_source_code_collection"}:
        reasons.append("untrusted_source_code_must_not_be_imported")
    return reasons


def _security_findings(request: HarnessRouteRequest) -> list[str]:
    findings: list[str] = []
    if request.data_sensitivity in {"internal", "confidential", "regulated", "secret"}:
        findings.append("external_proxy_data_boundary")
    if request.data_sensitivity in {"regulated", "secret"}:
        findings.append("local_route_required")
    return findings


def _caveats(request: HarnessRouteRequest, selected: dict[str, Any]) -> list[str]:
    caveats = list(selected.get("caveats", []))
    if request.task_type == "ui_design" or request.requires_ui_taste:
        caveats.append("cheap_model_style_extension_only")
    if selected["privacy_posture"] == "external-proxy":
        caveats.append("do_not_send_api_keys_secrets_or-regulated-data")
    return sorted(set(caveats))


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


def _security_rules() -> list[str]:
    return [
        "regulated_or_secret_data_requires_local_route",
        "no_raw_logging",
        "dangerously_skip_permissions_blocked",
        "untrusted_source_code_must_not_be_imported",
        "ui_design_requires_design_authority",
        "external_proxy_requires_operator_approval_for_non_public_data",
    ]


def _required_controls() -> list[str]:
    return [
        "data_classification",
        "external_provider_boundary",
        "no_raw_logging",
        "credential_vault_boundary",
        "sandbox_permission_gate",
        "source_license_review",
        "operator_route_evidence",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/harness-routing"},
        "recommend": {"method": "POST", "endpoint": "/ops/brain/harness-routing/recommend"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/harness-routing"},
    }


def _source_refs() -> list[dict[str, str]]:
    return [
        {
            "source_id": "free-claude-code",
            "url": "https://github.com/Alishahryar1/free-claude-code",
            "used_as": "adapter-pattern-reference-only",
        },
        {
            "source_id": "ai-transformation-workshop",
            "url": "https://github.com/coleam00/ai-transformation-workshop",
            "used_as": "agentic-workflow-reference",
        },
        {
            "source_id": "collection-claude-code-source-code",
            "url": "https://github.com/chauncygu/collection-claude-code-source-code",
            "used_as": "source-governance-risk-signal-no-code-imported",
        },
    ]
