from __future__ import annotations

from typing import Any


class ProtocolCapabilityRegistry:
    PROTOCOLS = [
        ("mcp", "Model Context Protocol", ["tools", "resources", "prompts"], "per-server"),
        ("a2a", "Agent-to-Agent", ["task_delegation", "message_exchange"], "signed-or-configured"),
        ("ag-ui", "AG-UI", ["event_stream", "operator_ui"], "session"),
        ("openapi-action", "OpenAPI Action", ["http_action_manifest", "schema_validation"], "api-key-or-oauth"),
        ("local-provider", "Local Provider", ["openai_compatible", "local_runtime"], "local-config"),
    ]

    def __init__(self, *, protocol_adapters: Any | None = None, security_layer: Any | None = None):
        self.protocol_adapters = protocol_adapters
        self.security_layer = security_layer

    def summary(self) -> dict[str, Any]:
        capabilities = [self._capability(protocol_id, label, features, auth_mode) for protocol_id, label, features, auth_mode in self.PROTOCOLS]
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "capability_count": len(capabilities),
            "provider_registration_allowed": False,
            "tool_execution_allowed": False,
            "external_protocol_execution_allowed": False,
            "network_writes_allowed": False,
            "file_writes_allowed": False,
            "capabilities": capabilities,
            "adapter_summary": self._adapter_summary(),
            "security_summary": self.security_layer.summary() if self.security_layer else {},
        }

    def compact_summary(self) -> dict[str, Any]:
        payload = self.summary()
        return {
            "status_label": payload["status_label"],
            "capability_count": payload["capability_count"],
            "provider_registration_allowed": False,
            "external_protocol_execution_allowed": False,
            "protocol_ids": [item["protocol_id"] for item in payload["capabilities"]],
        }

    def _capability(self, protocol_id: str, label: str, features: list[str], auth_mode: str) -> dict[str, Any]:
        return {
            "protocol_id": protocol_id,
            "label": label,
            "discovery_data": {"features": features, "metadata_only": True},
            "auth_mode": auth_mode,
            "streaming_support": "candidate_declared" if protocol_id in {"mcp", "ag-ui", "local-provider"} else "unknown",
            "mutation_risk": "high",
            "data_egress_risk": "medium_to_high",
            "filesystem_posture": "deny_by_default",
            "network_posture": "deny_by_default",
            "sandbox_recommendation": "observe_only_until_policy_grant",
            "product_sweep_gate_ids": ["phase-4-security", "protocol-adapter-governance", "gateway-policy"],
            "provider_registration_allowed": False,
            "tool_execution_allowed": False,
            "external_protocol_execution_allowed": False,
            "mutation_allowed": False,
        }

    def _adapter_summary(self) -> dict[str, Any]:
        if self.protocol_adapters is None:
            return {}
        if hasattr(self.protocol_adapters, "summary"):
            return self.protocol_adapters.summary()
        if hasattr(self.protocol_adapters, "list_adapters"):
            return self.protocol_adapters.list_adapters()
        return {}
