from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow


ProfileMode = Literal["nexus_owned_ephemeral", "nexus_owned_persistent", "real_user_profile"]


class BrowserProfilePolicyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    profile_mode: ProfileMode = "nexus_owned_ephemeral"
    session_scoped_permission: bool = False
    contains_private_data: bool = False
    provenance_ref: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserProfilePolicy:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "browser" / "profile-policy" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self._memory_records: list[dict[str, Any]] = []

    def evaluate(self, request: BrowserProfilePolicyRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, BrowserProfilePolicyRequest) else BrowserProfilePolicyRequest.model_validate(request)
        findings = _findings(normalized)
        decision = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "browser-profile-policy",
            "request_id": normalized.request_id,
            "profile_mode": normalized.profile_mode,
            "status": "blocked" if findings else "allowed",
            "runtime_state": "degraded" if findings else "live-bound",
            "created_at": utcnow().isoformat(),
            "session_scoped_permission": normalized.session_scoped_permission,
            "contains_private_data": normalized.contains_private_data,
            "provenance_ref": normalized.provenance_ref,
            "recommended_profile_mode": "nexus_owned_ephemeral" if findings else normalized.profile_mode,
            "findings": findings,
            "metadata": normalized.metadata,
            "operator_actions": _operator_actions(),
        }
        self._persist(decision)
        return decision

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        records = self._memory_records[:limit]
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "browser-profile-policy",
            "authority": "NexusBrain",
            "runtime_state": "degraded"
            if any(record.get("status") == "blocked" for record in records)
            else ("live-bound" if records else "static-canon"),
            "decision_count": len(records),
            "latest_decision": records[0] if records else None,
            "decisions": records,
            "operator_actions": _operator_actions(),
        }

    def _persist(self, decision: dict[str, Any]) -> None:
        self._memory_records.insert(0, decision)
        self._memory_records = self._memory_records[:50]
        if self.records_dir is not None:
            path = self.records_dir / f"{decision['request_id'].replace(':', '_')}.json"
            decision["artifact_path"] = str(path)
            path.write_text(json.dumps(decision, indent=2), encoding="utf-8")


def _findings(request: BrowserProfilePolicyRequest) -> list[dict[str, str]]:
    findings = []
    if request.profile_mode == "real_user_profile" and not request.session_scoped_permission:
        findings.append(
            {
                "rule_id": "real_browser_profile_requires_session_permission",
                "severity": "hard_fail",
                "message": "Real browser profiles require explicit session-scoped permission.",
            }
        )
    if request.contains_private_data and not request.provenance_ref:
        findings.append(
            {
                "rule_id": "private_browser_profile_requires_provenance",
                "severity": "hard_fail",
                "message": "Private browser profile use requires a provenance or consent reference.",
            }
        )
    return findings


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/browser/profile-policy"},
        "evaluate": {"method": "POST", "endpoint": "/ops/brain/browser/profile-policy"},
    }
