from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from nexus.schemas import new_id


ProtocolName = Literal["mcp", "a2a", "ag-ui"]
DecisionStatus = Literal["allowed", "denied", "hold"]


class ToolAttempt(BaseModel):
    attempt_id: str = Field(default_factory=lambda: new_id("toolattempt"))
    tool_id: str
    protocol: ProtocolName
    server_signed: bool = False
    server_allowlisted: bool = False
    sandboxed: bool = False
    permissions: list[str] = Field(default_factory=list)
    elicitation_mode: str | None = None
    handles_secret: bool = False
    approval_granted: bool = False
    identity_metadata: dict[str, Any] = Field(default_factory=dict)


class ProtocolServerDefinition(BaseModel):
    server_id: str = Field(min_length=1)
    protocol: ProtocolName
    base_url: str = Field(min_length=1)
    signed: bool = False
    allowlisted: bool = False
    permissions: list[str] = Field(default_factory=list)


class ProtocolConsentRequest(BaseModel):
    server_id: str = Field(min_length=1)
    tool_id: str = Field(min_length=1)
    mode: Literal["accept", "decline", "cancel"]


class SecurityDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("security"))
    attempt_id: str
    tool_id: str
    protocol: ProtocolName
    status: DecisionStatus
    reason: str
    executed: bool = False
    audit_event: dict[str, Any] = Field(default_factory=dict)


class ProtocolSecurityLayer:
    """Fail-closed security envelope for MCP, A2A, and AG-UI candidates."""

    def __init__(self):
        self._audit_log: list[dict[str, Any]] = []
        self._servers: dict[str, ProtocolServerDefinition] = {}
        self._allowed_permissions = {
            "mcp": {"read", "write", "network"},
            "a2a": {"delegate", "read"},
            "ag-ui": {"emit", "read"},
        }

    def evaluate(self, attempt: ToolAttempt) -> SecurityDecision:
        reason: str | None = None
        status: DecisionStatus = "allowed"

        if attempt.protocol == "mcp" and not attempt.server_signed:
            reason = "mcp_server_definition_must_be_signed"
        elif attempt.protocol == "mcp" and not attempt.server_allowlisted:
            reason = "mcp_server_definition_must_be_allowlisted"
        elif not attempt.identity_metadata:
            reason = "identity_metadata_required"
        elif not attempt.sandboxed:
            reason = "sandbox_required"
        elif any(permission not in self._allowed_permissions[attempt.protocol] for permission in attempt.permissions):
            reason = "permission_not_allowed"
        elif attempt.handles_secret and attempt.elicitation_mode not in {"url", "out_of_band"}:
            reason = "secret_elicitation_requires_url_or_out_of_band"

        if reason is not None:
            status = "denied"
        elif not attempt.approval_granted:
            status = "hold"
            reason = "user_approval_required"
        else:
            reason = "policy_allowed"

        audit_event = self._audit(attempt, status, reason)
        return SecurityDecision(
            attempt_id=attempt.attempt_id,
            tool_id=attempt.tool_id,
            protocol=attempt.protocol,
            status=status,
            reason=reason,
            executed=False,
            audit_event=audit_event,
        )

    def audit_log(self) -> list[dict[str, Any]]:
        return list(self._audit_log)

    def register_server(self, definition: ProtocolServerDefinition) -> dict[str, Any]:
        reason: str | None = None
        if definition.protocol == "mcp" and not definition.signed:
            reason = "mcp_server_definition_must_be_signed"
        elif definition.protocol == "mcp" and not definition.allowlisted:
            reason = "mcp_server_definition_must_be_allowlisted"
        elif any(permission not in self._allowed_permissions[definition.protocol] for permission in definition.permissions):
            reason = "permission_not_allowed"

        status = "denied" if reason else "registered"
        if reason is None:
            self._servers[definition.server_id] = definition
            reason = "server_registered"

        event = {
            "event_id": new_id("securityaudit"),
            "action": "protocol.server.registration",
            "server_id": definition.server_id,
            "protocol": definition.protocol,
            "status": status,
            "reason": reason,
            "permissions": list(definition.permissions),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._audit_log.append(event)
        return {
            "server_id": definition.server_id,
            "protocol": definition.protocol,
            "status": status,
            "reason": reason,
            "audit_event": event,
        }

    def consent(self, request: ProtocolConsentRequest) -> SecurityDecision:
        server = self._servers.get(request.server_id)
        protocol: ProtocolName = server.protocol if server else "mcp"
        attempt = ToolAttempt(
            tool_id=request.tool_id,
            protocol=protocol,
            server_signed=bool(server.signed) if server else False,
            server_allowlisted=bool(server.allowlisted) if server else False,
            sandboxed=True,
            permissions=list(server.permissions) if server else [],
            approval_granted=request.mode == "accept",
            identity_metadata={"server_id": request.server_id, "consent_mode": request.mode} if server else {},
        )

        if server is None:
            audit_event = self._audit(attempt, "denied", "server_not_registered")
            return SecurityDecision(
                attempt_id=attempt.attempt_id,
                tool_id=attempt.tool_id,
                protocol=attempt.protocol,
                status="denied",
                reason="server_not_registered",
                executed=False,
                audit_event=audit_event,
            )
        if request.mode == "decline":
            audit_event = self._audit(attempt, "denied", "user_declined")
            return SecurityDecision(
                attempt_id=attempt.attempt_id,
                tool_id=attempt.tool_id,
                protocol=attempt.protocol,
                status="denied",
                reason="user_declined",
                executed=False,
                audit_event=audit_event,
            )
        if request.mode == "cancel":
            audit_event = self._audit(attempt, "hold", "user_cancelled")
            return SecurityDecision(
                attempt_id=attempt.attempt_id,
                tool_id=attempt.tool_id,
                protocol=attempt.protocol,
                status="hold",
                reason="user_cancelled",
                executed=False,
                audit_event=audit_event,
            )
        return self.evaluate(attempt)

    def servers(self) -> list[dict[str, Any]]:
        return [server.model_dump(mode="json") for server in self._servers.values()]

    def summary(self) -> dict[str, Any]:
        return {
            "status": "fail_closed",
            "protocols": ["mcp", "a2a", "ag-ui"],
            "external_tools_default": "deny_until_policy_allows",
            "audit_event_count": len(self._audit_log),
            "registered_server_count": len(self._servers),
            "secret_elicitation": "url_or_out_of_band_only",
            "mcp_elicitation_modes": ["accept", "decline", "cancel", "url", "out_of_band"],
        }

    def _audit(self, attempt: ToolAttempt, status: DecisionStatus, reason: str) -> dict[str, Any]:
        event = {
            "event_id": new_id("securityaudit"),
            "attempt_id": attempt.attempt_id,
            "tool_id": attempt.tool_id,
            "protocol": attempt.protocol,
            "status": status,
            "reason": reason,
            "permissions": list(attempt.permissions),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._audit_log.append(event)
        return event
