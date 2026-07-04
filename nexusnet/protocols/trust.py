from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


ProtocolId = Literal["MCP", "A2A", "ACP", "AG-UI", "webhook", "message-bus"]


class ProtocolAdapterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    adapter_id: str
    protocol: ProtocolId
    endpoint: str
    enabled: bool = False
    identity_ref: str = ""
    consent_ref: str = ""
    permissions: list[str] = Field(default_factory=list)
    revocation_ref: str = ""
    sandboxed: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProtocolTrustRegistry:
    def __init__(self, *, artifacts_dir: Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.adapters_dir = self.artifacts_dir / "protocols" / "trust-registry" if self.artifacts_dir else None
        if self.adapters_dir is not None:
            self.adapters_dir.mkdir(parents=True, exist_ok=True)
        self._memory_adapters: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    def register(self, request: ProtocolAdapterRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, ProtocolAdapterRequest) else ProtocolAdapterRequest.model_validate(request)
        trust_envelope = _trust_envelope(normalized)
        trust_findings = _trust_findings(normalized)
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized, trust_envelope))
        blocked = bool(trust_findings) or policy_scan.summary.active_hard_fail_count > 0
        record = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "protocol-trust-registry",
            "adapter_id": normalized.adapter_id,
            "protocol": normalized.protocol,
            "endpoint": normalized.endpoint,
            "enabled": normalized.enabled,
            "status": "blocked" if blocked else ("trusted-shadow" if normalized.enabled else "trusted-disabled"),
            "created_at": utcnow().isoformat(),
            "trust_envelope": trust_envelope,
            "trust_findings": trust_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "metadata": normalized.metadata,
        }
        self._persist(record)
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        adapters = self._list_adapters(limit=limit)
        blocked_count = sum(1 for adapter in adapters if adapter.get("status") == "blocked")
        latest_adapter = adapters[0] if adapters else None
        runtime_state = "static-canon"
        if adapters:
            runtime_state = "degraded" if blocked_count or latest_adapter.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "protocol-trust-registry",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "adapter_count": len(adapters),
            "trusted_count": sum(1 for adapter in adapters if str(adapter.get("status", "")).startswith("trusted")),
            "blocked_count": blocked_count,
            "latest_adapter": latest_adapter,
            "adapters": adapters,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md",
                "docs/NEXUSNET_RESEARCH_CANDIDATE_DOSSIER_2026-04-28.md",
            ],
            "protocol_boundary": "protocol-adapters-are-hands-under-nexusbrain-trust-review",
            "protocols": ["MCP", "A2A", "ACP", "AG-UI"],
        }

    def _persist(self, record: dict[str, Any]) -> None:
        self._memory_adapters.insert(0, record)
        self._memory_adapters = self._memory_adapters[:50]
        if self.adapters_dir is not None:
            safe_id = record["adapter_id"].replace(":", "_").replace("/", "_")
            path = self.adapters_dir / f"{safe_id}.json"
            record["artifact_path"] = str(path)
            path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _list_adapters(self, *, limit: int) -> list[dict[str, Any]]:
        adapters = list(self._memory_adapters)
        seen = {adapter.get("adapter_id") for adapter in adapters}
        if self.adapters_dir is not None:
            for path in self.adapters_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("adapter_id") not in seen:
                    adapters.append(payload)
        adapters.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return adapters[:limit]


def _trust_envelope(request: ProtocolAdapterRequest) -> dict[str, Any]:
    complete = bool(
        request.identity_ref
        and request.consent_ref
        and request.permissions
        and request.revocation_ref
        and request.sandboxed
    )
    return {
        "complete": complete,
        "identity_ref": request.identity_ref,
        "consent_ref": request.consent_ref,
        "permissions": request.permissions,
        "revocation_ref": request.revocation_ref,
        "sandboxed": request.sandboxed,
    }


def _trust_findings(request: ProtocolAdapterRequest) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not request.enabled:
        return findings
    checks = [
        ("protocol_adapter_requires_identity", request.identity_ref, "Enabled protocol adapters require identity references."),
        ("protocol_adapter_requires_consent", request.consent_ref, "Enabled protocol adapters require consent references."),
        ("protocol_adapter_requires_permissions", request.permissions, "Enabled protocol adapters require scoped permissions."),
        ("protocol_adapter_requires_revocation", request.revocation_ref, "Enabled protocol adapters require revocation references."),
        ("protocol_adapter_requires_sandbox", request.sandboxed, "Enabled protocol adapters require sandbox boundaries."),
    ]
    for rule_id, value, message in checks:
        if not value:
            findings.append({"rule_id": rule_id, "severity": "hard_fail", "message": message})
    return findings


def _policy_targets(request: ProtocolAdapterRequest, trust_envelope: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"protocol::{request.adapter_id}",
            "target_type": "protocol_adapter",
            "metadata": {
                "enabled": request.enabled,
                "trust_envelope": trust_envelope["complete"],
            },
        }
    ]


def _required_controls() -> list[str]:
    return [
        "mcp_a2a_acp_agui_adapters",
        "agent_identity",
        "operator_consent",
        "scoped_permissions",
        "revocation",
        "sandbox_boundary",
        "audit_visibility",
        "trust_envelope_policy_scan",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/protocol-trust"},
        "register_adapter": {"method": "POST", "endpoint": "/ops/brain/protocol-trust/adapters"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/protocol-trust-registry"},
    }
