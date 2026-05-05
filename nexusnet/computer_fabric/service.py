from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from nexus.schemas import utcnow

from .models import ComputerSessionRequest, ComputerSessionSummary, EnvironmentClass


class ComputerFabricService:
    def __init__(self, *, artifacts_dir: Path):
        self.artifacts_dir = Path(artifacts_dir)
        self.sessions_dir = self.artifacts_dir / "computer-fabric" / "sessions"

    def start_session(self, request: ComputerSessionRequest) -> ComputerSessionSummary:
        session_id = f"computer_{uuid4().hex[:12]}"
        environment_class = self._select_environment(request)
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        blocked_reasons: list[str] = []
        policy = self._compile_policy(request=request, environment_class=environment_class, blocked_reasons=blocked_reasons)
        manifest = self._build_manifest(
            request=request,
            session_id=session_id,
            environment_class=environment_class,
            policy=policy,
        )
        self._write_json(session_dir / "manifest.json", manifest)
        self._write_json(session_dir / "policy.json", policy)

        events: list[dict[str, Any]] = []
        self._record_event(events, "session.created", {"session_id": session_id})
        self._record_event(events, "policy.compiled", {"blocked_reasons": blocked_reasons})
        self._record_event(events, "provider.prepared", {"provider": policy["provider"]})

        artifacts: list[dict[str, Any]] = []
        status = "failed-policy" if blocked_reasons else "completed-review-required"
        if not blocked_reasons:
            artifact_path = session_dir / "summary.md"
            artifact_path.write_text(
                "\n".join(
                    [
                        f"# Computer Fabric Session {session_id}",
                        "",
                        f"Goal: {request.goal}",
                        f"Environment: {environment_class.value}",
                        "Status: completed with review required before promotion.",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            artifact = self._artifact_record(
                session_id=session_id,
                path=artifact_path,
                artifact_type="document",
                privacy_class=request.privacy_class,
            )
            artifacts.append(artifact)
            self._record_event(events, "artifact.created", {"artifact_id": artifact["artifact_id"]})
            self._record_event(events, "artifact.scanned", {"artifact_id": artifact["artifact_id"], "trust_status": "trusted"})

        trust_summary = {
            "session_id": session_id,
            "trusted_artifact_count": len([item for item in artifacts if item["trust_status"] == "trusted"]),
            "blocked_artifact_count": len([item for item in artifacts if item["trust_status"] == "blocked"]),
            "promotion_allowed": False,
            "promotion_boundary": "no-production-mutation-without-review",
        }
        self._write_events(session_dir / "events.jsonl", events)
        self._write_json(session_dir / "artifact-index.json", {"artifacts": artifacts})
        self._write_json(session_dir / "trust-scan-summary.json", trust_summary)
        self._write_json(
            session_dir / "session-summary.json",
            {
                "session_id": session_id,
                "environment_class": environment_class.value,
                "status": status,
                "artifact_count": len(artifacts),
                "blocked_reasons": blocked_reasons,
                "trust_summary": trust_summary,
            },
        )

        return ComputerSessionSummary(
            session_id=session_id,
            environment_class=environment_class,
            status=status,
            session_dir=session_dir,
            policy=policy,
            event_types=[event["event_type"] for event in events],
            artifact_count=len(artifacts),
            blocked_reasons=blocked_reasons,
            trust_summary=trust_summary,
        )

    def _select_environment(self, request: ComputerSessionRequest) -> EnvironmentClass:
        if request.requested_environment is not None:
            return request.requested_environment
        task_text = f"{request.task_type} {request.goal}".lower()
        if any(token in task_text for token in ("scheduled", "daily", "monitor", "24/7", "database", "bot")):
            return EnvironmentClass.PERSISTENT
        if any(token in task_text for token in ("logged-in", "private dashboard", "local folder", "desktop", "operator")):
            return EnvironmentClass.OPERATOR
        return EnvironmentClass.EPHEMERAL

    def _compile_policy(
        self,
        *,
        request: ComputerSessionRequest,
        environment_class: EnvironmentClass,
        blocked_reasons: list[str],
    ) -> dict[str, Any]:
        if environment_class == EnvironmentClass.EPHEMERAL:
            filesystem_policy = {"write_scope": "session-artifacts-only"}
            network_policy = {"mode": "task-scoped-egress"}
            credential_policy = {"mode": "none"}
            schedule_policy = {"mode": "not-scheduled"}
            approval_required = ["production-mutation", "credential-use", "host-write"]
            execution_boundary = "sandbox-artifacts-only"
            provider = "repo-local-session"
        elif environment_class == EnvironmentClass.PERSISTENT:
            filesystem_policy = {"write_scope": "persistent-computer-artifacts"}
            network_policy = {"mode": "scheduled-task-egress"}
            credential_policy = {"mode": "reference-only"}
            schedule_policy = {"mode": "persistent-scheduled" if request.schedule else "persistent-manual"}
            approval_required = ["public-service-hosting", "credential-use", "production-mutation"]
            execution_boundary = "persistent-governed"
            provider = "persistent-local-proposal"
        else:
            filesystem_policy = {"write_scope": "operator-granted-scope-only"}
            network_policy = {"mode": "authenticated-browser-or-local-only"}
            credential_policy = {"mode": "operator-session-only"}
            schedule_policy = {"mode": "not-scheduled"}
            approval_required = ["browser-action", "local-command", "file-write", "credential-use"]
            execution_boundary = "observe-first"
            provider = "operator-observe-first"

        return {
            "environment_class": environment_class.value,
            "provider": provider,
            "filesystem_policy": filesystem_policy,
            "network_policy": network_policy,
            "credential_policy": credential_policy,
            "schedule_policy": schedule_policy,
            "approval_policy": {"required_for": approval_required},
            "execution_boundary": execution_boundary,
            "required_checks": list(request.required_checks),
            "blocked_reasons": blocked_reasons,
        }

    def _build_manifest(
        self,
        *,
        request: ComputerSessionRequest,
        session_id: str,
        environment_class: EnvironmentClass,
        policy: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "created_at": utcnow().isoformat(),
            "goal": request.goal,
            "task_type": request.task_type,
            "environment_class": environment_class.value,
            "project_scope": request.project_scope,
            "privacy_class": request.privacy_class,
            "requested_tools": list(request.requested_tools),
            "required_checks": list(request.required_checks),
            "schedule": request.schedule,
            "metadata": dict(request.metadata),
            "policy_ref": "policy.json",
            "artifact_contract": "artifact-index.json",
            "replay_contract": "events.jsonl",
            "rollback_contract": "no-production-mutation-without-review",
            "policy": policy,
        }

    def _artifact_record(
        self,
        *,
        session_id: str,
        path: Path,
        artifact_type: str,
        privacy_class: str,
    ) -> dict[str, Any]:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return {
            "artifact_id": f"artifact_{uuid4().hex[:12]}",
            "session_id": session_id,
            "path": str(path),
            "artifact_type": artifact_type,
            "created_by_action": "session.summary",
            "checksum": f"sha256:{digest}",
            "signature_ref": None,
            "provenance_refs": [f"computer-session:{session_id}"],
            "license_status": "project-local-generated",
            "privacy_class": privacy_class,
            "export_allowed": privacy_class in {"public", "project-internal"},
            "trust_status": "trusted",
            "promotion_allowed": False,
        }

    def _record_event(self, events: list[dict[str, Any]], event_type: str, payload: dict[str, Any]) -> None:
        events.append({"event_type": event_type, "created_at": utcnow().isoformat(), "payload": payload})

    def _write_events(self, path: Path, events: list[dict[str, Any]]) -> None:
        path.write_text("\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n", encoding="utf-8")

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
