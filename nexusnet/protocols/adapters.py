from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from nexusnet.canon.registry import SecurityPolicy

from .security import ProtocolName, ProtocolSecurityLayer


AdapterStatus = Literal["disabled", "denied", "enabled_gated"]


class ProtocolAdapterPolicyRequest(BaseModel):
    enable_requested: bool = False
    server_id: str | None = None
    identity_required: bool = True
    sandbox_required: bool = True
    permissions: list[str] = Field(default_factory=list)
    elicitation_modes: list[str] = Field(default_factory=list)
    approval_required: bool = True


class GovernedProtocolAdapter(BaseModel):
    adapter_id: str
    protocol: ProtocolName
    status: AdapterStatus = "disabled"
    execution_enabled: bool = False
    security_envelope_required: bool = True
    reason: str = "disabled_until_policy_allows"
    deny_reason: str | None = None
    server_id: str | None = None
    policy: dict[str, Any] = Field(default_factory=dict)


class GovernedProtocolAdapterRegistry:
    """Governed MCP/A2A/AG-UI adapter layer above raw security decisions."""

    def __init__(self, security_layer: ProtocolSecurityLayer):
        self.security_layer = security_layer
        self._adapters: dict[str, GovernedProtocolAdapter] = {
            "mcp": GovernedProtocolAdapter(adapter_id="mcp", protocol="mcp"),
            "a2a": GovernedProtocolAdapter(adapter_id="a2a", protocol="a2a"),
            "ag-ui": GovernedProtocolAdapter(adapter_id="ag-ui", protocol="ag-ui"),
        }

    def list_adapters(self) -> dict[str, Any]:
        adapters = [adapter.model_dump(mode="json") for adapter in self._adapters.values()]
        return {
            "external_execution_default": "deny_until_user_consent",
            "enabled_adapter_count": len([item for item in adapters if item["status"] == "enabled_gated"]),
            "adapters": adapters,
        }

    def get_adapter(self, adapter_id: str) -> GovernedProtocolAdapter | None:
        return self._adapters.get(adapter_id)

    def apply_policy(self, adapter_id: str, request: ProtocolAdapterPolicyRequest) -> dict[str, Any]:
        adapter = self._adapters[adapter_id]
        deny_reason = self._deny_reason(adapter.protocol, request)
        policy = SecurityPolicy(
            tool_id=f"{adapter.protocol}::*",
            protocol=adapter.protocol,
            identity_required=request.identity_required,
            sandbox_required=request.sandbox_required,
            permissions=list(request.permissions),
            elicitation_modes=list(request.elicitation_modes),
            approval_required=request.approval_required,
            deny_reason=deny_reason,
            status="candidate" if deny_reason is None else "disabled",
            evidence=["GovernedProtocolAdapterRegistry", "ProtocolSecurityLayer"],
            license="internal_policy",
            verified_at="2026-04-26",
        )
        if deny_reason:
            updated = adapter.model_copy(
                update={
                    "status": "denied",
                    "execution_enabled": False,
                    "reason": "policy_denied",
                    "deny_reason": deny_reason,
                    "server_id": request.server_id,
                    "policy": policy.model_dump(mode="json"),
                }
            )
        elif request.enable_requested:
            updated = adapter.model_copy(
                update={
                    "status": "enabled_gated",
                    "execution_enabled": False,
                    "reason": "enabled_but_requires_user_consent_per_attempt",
                    "deny_reason": None,
                    "server_id": request.server_id,
                    "policy": policy.model_dump(mode="json"),
                }
            )
        else:
            updated = adapter.model_copy(
                update={
                    "status": "disabled",
                    "execution_enabled": False,
                    "reason": "disabled_by_policy",
                    "deny_reason": None,
                    "server_id": request.server_id,
                    "policy": policy.model_dump(mode="json"),
                }
            )
        self._adapters[adapter_id] = updated
        return {"adapter": updated.model_dump(mode="json")}

    def _deny_reason(self, protocol: ProtocolName, request: ProtocolAdapterPolicyRequest) -> str | None:
        if request.enable_requested and not request.identity_required:
            return "identity_required"
        if request.enable_requested and not request.sandbox_required:
            return "sandbox_required"
        if request.enable_requested and not request.approval_required:
            return "approval_required"
        allowed_permissions = {
            "mcp": {"read", "write", "network"},
            "a2a": {"delegate", "read"},
            "ag-ui": {"emit", "read"},
        }
        if any(permission not in allowed_permissions[protocol] for permission in request.permissions):
            return "permission_not_allowed"
        if protocol == "mcp" and request.enable_requested:
            servers = {server["server_id"]: server for server in self.security_layer.servers()}
            if not request.server_id or request.server_id not in servers:
                return "registered_server_required"
        return None
