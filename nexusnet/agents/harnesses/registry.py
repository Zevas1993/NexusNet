from __future__ import annotations

from typing import Any

from nexusnet.policy import PolicyKernel


class HarnessProviderRegistry:
    def __init__(self, providers: list[dict[str, Any]]):
        self.providers = providers
        self.policy_kernel = PolicyKernel.default()
        self._recommendations: list[dict[str, Any]] = []

    @classmethod
    def default(cls) -> "HarnessProviderRegistry":
        return cls(
            [
                {
                    "provider_id": "custom-code",
                    "label": "Custom NexusNet Code Harness",
                    "tier": "custom-code",
                    "model_control": "maximum",
                    "memory_portability": "nexus-owned",
                    "sandbox_model": "operator-selected",
                    "sandbox_choice": True,
                    "self_hostable": True,
                    "protocol_support": ["MCP", "A2A", "ACP", "AG-UI"],
                    "privacy_posture": "local-first",
                    "lock_in_risk": "low",
                    "caveats": ["highest-engineering-responsibility"],
                },
                {
                    "provider_id": "openai-agents-sdk",
                    "label": "OpenAI Agents SDK",
                    "tier": "agent-sdk",
                    "model_control": "high",
                    "memory_portability": "nexus-owned",
                    "sandbox_model": "bring-your-own-provider",
                    "sandbox_choice": True,
                    "self_hostable": True,
                    "protocol_support": ["MCP", "workspace-sandbox"],
                    "privacy_posture": "deployment-dependent",
                    "lock_in_risk": "medium",
                    "caveats": ["best-with-provider-native-model-capabilities"],
                },
                {
                    "provider_id": "langgraph-deep-agents",
                    "label": "LangGraph / Deep Agents",
                    "tier": "agent-framework",
                    "model_control": "high",
                    "memory_portability": "nexus-owned-if-self-hosted",
                    "sandbox_model": "pluggable",
                    "sandbox_choice": True,
                    "self_hostable": True,
                    "protocol_support": ["MCP", "A2A"],
                    "privacy_posture": "deployment-dependent",
                    "lock_in_risk": "medium",
                    "caveats": ["deployment-platform-may-add-saas-dependency"],
                },
                {
                    "provider_id": "claude-managed-agents",
                    "label": "Claude Managed Agents",
                    "tier": "managed-infrastructure",
                    "model_control": "provider-tuned",
                    "memory_portability": "provider-managed",
                    "sandbox_model": "provider-managed",
                    "sandbox_choice": False,
                    "self_hostable": False,
                    "protocol_support": ["MCP"],
                    "privacy_posture": "managed-cloud",
                    "lock_in_risk": "high",
                    "caveats": ["research-preview-features", "closed-harness-memory-risk"],
                },
                {
                    "provider_id": "vertex-ai-agent-builder",
                    "label": "Vertex AI Agent Builder",
                    "tier": "managed-infrastructure",
                    "model_control": "multi-model-cloud",
                    "memory_portability": "cloud-managed",
                    "sandbox_model": "cloud-managed",
                    "sandbox_choice": False,
                    "self_hostable": False,
                    "protocol_support": ["cloud-tools"],
                    "privacy_posture": "managed-cloud",
                    "lock_in_risk": "medium",
                    "caveats": ["cloud-governance-required"],
                },
                {
                    "provider_id": "bedrock-agent-core",
                    "label": "Amazon Bedrock Agent Core",
                    "tier": "managed-infrastructure",
                    "model_control": "multi-model-cloud",
                    "memory_portability": "cloud-managed",
                    "sandbox_model": "cloud-managed",
                    "sandbox_choice": False,
                    "self_hostable": False,
                    "protocol_support": ["cloud-tools"],
                    "privacy_posture": "managed-cloud",
                    "lock_in_risk": "medium",
                    "caveats": ["cloud-governance-required"],
                },
                {
                    "provider_id": "n8n-visual-agent",
                    "label": "n8n Visual Agent Workflows",
                    "tier": "visual-low-code",
                    "model_control": "workflow-configured",
                    "memory_portability": "workflow-export",
                    "sandbox_model": "workflow-runtime",
                    "sandbox_choice": False,
                    "self_hostable": True,
                    "protocol_support": ["webhooks", "workflow-tools"],
                    "privacy_posture": "deployment-dependent",
                    "lock_in_risk": "medium",
                    "caveats": ["less-flexible-than-code-harnesses"],
                },
            ]
        )

    def summary(self) -> dict[str, Any]:
        blocked_count = sum(1 for item in self._recommendations if item.get("decision") == "blocked")
        latest_recommendation = self._recommendations[-1] if self._recommendations else None
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "harness-provider-registry",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if blocked_count else "live-bound",
            "provider_count": len(self.providers),
            "providers": list(self.providers),
            "recommendation_count": len(self._recommendations),
            "blocked_count": blocked_count,
            "latest_recommendation": latest_recommendation,
            "recommendations": list(self._recommendations[-10:]),
            "promotion_boundary": "external-harnesses-remain-adapters-not-brain-authority",
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        return {
            **self.summary(),
            "source_document": "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
            "research_source_ids": ["YT-05"],
            "selection_axes": [
                "model_control",
                "memory_portability",
                "sandbox_model",
                "protocol_support",
                "privacy_posture",
                "lock_in_risk",
                "self_hosting",
            ],
        }

    def recommend(self, requirements: dict[str, Any]) -> dict[str, Any]:
        upstream_aitune_gate = _upstream_aitune_gate(requirements.get("upstream_aitune_gate") or {})
        upstream_aitune_blocked = _upstream_aitune_gate_blocked(upstream_aitune_gate)
        blocked_reasons: list[str] = []
        if upstream_aitune_blocked:
            blocked_reasons.append("router_alignment_blocks_upstream_aitune_gate")
        scored = [
            {
                "provider": provider,
                "score": self._score(provider, requirements),
                "reason_codes": self._reason_codes(provider, requirements),
            }
            for provider in self.providers
        ]
        scored.sort(key=lambda item: (item["score"], item["provider"]["provider_id"] == "custom-code"), reverse=True)
        selected = scored[0]
        decision = "blocked" if blocked_reasons else "allow"
        reason_codes = list(selected["reason_codes"])
        if upstream_aitune_blocked:
            reason_codes = list(dict.fromkeys(reason_codes + ["upstream_aitune_gate_blocked"]))
        policy_targets = [
            {
                "target_id": f"harness::{selected['provider']['provider_id']}",
                "target_type": "protocol_adapter",
                "metadata": {
                    "enabled": decision != "blocked",
                    "trust_envelope": {
                        "authority": "NexusBrain",
                        "provider_id": selected["provider"]["provider_id"],
                        "memory_owner": selected["provider"]["memory_portability"],
                    },
                },
            }
        ]
        if upstream_aitune_blocked:
            policy_targets.append(
                {
                    "target_id": f"harness-provider-runtime::{selected['provider']['provider_id']}",
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
            "authority": "NexusBrain",
            "decision": decision,
            "runtime_state": "degraded" if decision == "blocked" else "live-bound",
            "requirements": requirements,
            "selected_provider": selected["provider"],
            "score": selected["score"],
            "reason_codes": reason_codes,
            "ranked_providers": [
                {"provider_id": item["provider"]["provider_id"], "score": item["score"], "lock_in_risk": item["provider"]["lock_in_risk"]}
                for item in scored
            ],
            "blocked_reasons": blocked_reasons,
            "upstream_aitune_gate": upstream_aitune_gate,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "decision_rule": "NexusBrain selects harness adapters by control, memory portability, sandbox choice, privacy, and lock-in risk.",
        }
        self._recommendations.append(result)
        return result

    def _score(self, provider: dict[str, Any], requirements: dict[str, Any]) -> int:
        score = 0
        if provider["lock_in_risk"] == "low":
            score += 4
        elif provider["lock_in_risk"] == "medium":
            score += 2
        if provider["memory_portability"].startswith("nexus-owned"):
            score += 4
        elif "export" in provider["memory_portability"]:
            score += 2
        if provider["sandbox_choice"]:
            score += 3
        if provider["self_hostable"]:
            score += 3
        if provider["privacy_posture"] == "local-first":
            score += 3
        if requirements.get("requires_self_hosting") and not provider["self_hostable"]:
            score -= 8
        if requirements.get("requires_memory_portability") and not provider["memory_portability"].startswith("nexus-owned"):
            score -= 6
        if requirements.get("requires_sandbox_choice") and not provider["sandbox_choice"]:
            score -= 5
        return score

    def _reason_codes(self, provider: dict[str, Any], requirements: dict[str, Any]) -> list[str]:
        reasons: list[str] = []
        if provider["memory_portability"].startswith("nexus-owned"):
            reasons.append("memory_portability")
        if provider["sandbox_choice"]:
            reasons.append("sandbox_choice")
        if provider["self_hostable"]:
            reasons.append("self_hosting")
        if provider["lock_in_risk"] == "low":
            reasons.append("low_lock_in")
        if requirements.get("use_case"):
            reasons.append(f"use_case::{requirements['use_case']}")
        return reasons


def _required_controls() -> list[str]:
    return [
        "brain_hands_separation",
        "memory_portability_score",
        "sandbox_choice_score",
        "lock_in_risk_label",
        "credential_vault_boundary",
        "protocol_trust_envelope",
        "operator_selection_evidence",
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


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/harness-providers"},
        "recommend": {"method": "POST", "endpoint": "/ops/brain/harness-providers/recommend"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/harness-providers"},
    }
