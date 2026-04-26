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

    def summary(self) -> dict[str, Any]:
        return {
            "status": "fail_closed",
            "protocols": ["mcp", "a2a", "ag-ui"],
            "external_tools_default": "deny_until_policy_allows",
            "audit_event_count": len(self._audit_log),
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
