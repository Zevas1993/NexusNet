from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


OperatorKind = Literal["browser_operator", "desktop_operator", "terminal_operator", "file_operator", "mcp_tool_operator"]
ActionKind = Literal[
    "browser_click",
    "browser_type",
    "desktop_observe",
    "desktop_click",
    "terminal_command",
    "file_read",
    "file_write",
    "mcp_tool_call",
]
PermissionScope = Literal[
    "browser_only",
    "desktop_observe_only",
    "desktop_control",
    "terminal_only",
    "file_read_only",
    "file_write",
    "mcp_tool_only",
]


class OperatorEventRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    run_id: str
    operator_kind: OperatorKind
    action_kind: ActionKind
    permission_scope: PermissionScope
    target_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_refs: list[str] = Field(default_factory=list)
    stop_window_ms: int = Field(default=1000, ge=0)
    rollback_ref: str = ""
    result: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OperatorEventRegistry:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "vision" / "operator-events" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._memory_events: list[dict[str, Any]] = []

    def record(self, request: OperatorEventRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, OperatorEventRequest) else OperatorEventRequest.model_validate(request)
        findings = _findings(normalized)
        event = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "operator-events",
            "event_id": normalized.event_id,
            "run_id": normalized.run_id,
            "operator_kind": normalized.operator_kind,
            "action_kind": normalized.action_kind,
            "permission_scope": normalized.permission_scope,
            "status": "blocked" if findings else "recorded",
            "runtime_state": "degraded" if findings else "live-bound",
            "created_at": utcnow().isoformat(),
            "target_confidence": normalized.target_confidence,
            "evidence_refs": normalized.evidence_refs,
            "stop_window_ms": normalized.stop_window_ms,
            "receipt": {
                "request": normalized.model_dump(mode="json"),
                "rollback_available": bool(normalized.rollback_ref),
                "rollback_ref": normalized.rollback_ref,
                "result": normalized.result,
            },
            "event_stream_contract": "observation-plan-action-result-correction",
            "findings": findings,
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._persist(event)
        return event

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        events = self._list_events(limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "operator-events",
            "authority": "NexusBrain",
            "runtime_state": "degraded"
            if any(event.get("status") == "blocked" for event in events)
            else ("live-bound" if events else "static-canon"),
            "event_count": len(events),
            "blocked_count": sum(1 for event in events if event.get("status") == "blocked"),
            "latest_event": events[0] if events else None,
            "events": events,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, event: dict[str, Any]) -> None:
        self._memory_events.insert(0, event)
        self._memory_events = self._memory_events[:50]
        if self.records_dir is not None:
            path = self.records_dir / f"{event['event_id'].replace(':', '_')}.json"
            event["artifact_path"] = str(path)
            path.write_text(json.dumps(event, indent=2), encoding="utf-8")

    def _list_events(self, *, limit: int) -> list[dict[str, Any]]:
        return self._memory_events[:limit]


def _findings(request: OperatorEventRequest) -> list[dict[str, str]]:
    findings = []
    allowed_pairs = {
        "browser_operator": {"browser_click", "browser_type"},
        "desktop_operator": {"desktop_observe", "desktop_click"},
        "terminal_operator": {"terminal_command"},
        "file_operator": {"file_read", "file_write"},
        "mcp_tool_operator": {"mcp_tool_call"},
    }
    if request.action_kind not in allowed_pairs[request.operator_kind]:
        findings.append(
            {
                "rule_id": "operator_event_blocks_permission_escalation",
                "severity": "hard_fail",
                "message": "Operator action is outside the granted operator class.",
            }
        )
    high_authority_actions = {
        "browser_click",
        "browser_type",
        "desktop_click",
        "terminal_command",
        "file_write",
        "mcp_tool_call",
    }
    if request.action_kind in high_authority_actions and request.target_confidence < 0.75:
        findings.append(
            {
                "rule_id": "operator_event_requires_target_confidence",
                "severity": "hard_fail",
                "message": "High-authority actions require target confidence of at least 0.75.",
            }
        )
    if request.action_kind in high_authority_actions and not request.evidence_refs:
        findings.append(
            {
                "rule_id": "operator_event_requires_evidence_refs",
                "severity": "hard_fail",
                "message": "High-authority actions require evidence references.",
            }
        )
    return findings


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/operator-events"},
        "record": {"method": "POST", "endpoint": "/ops/brain/operator-events"},
    }
