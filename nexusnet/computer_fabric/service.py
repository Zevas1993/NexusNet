from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from nexus.schemas import utcnow

from .approvals import ApprovalQueue
from .firewall import PromptInjectionFirewall
from .models import ComputerSessionRequest, ComputerSessionSummary, EnvironmentClass
from .providers import ProviderRegistry
from .secrets import SecretsBroker
from .snapshots import SnapshotRewindRecorder


class ComputerFabricService:
    HARD_BLOCK_REASONS = {
        "host-write-blocked",
        "unrestricted-network-blocked",
        "secret-read-blocked",
        "unknown-privacy-local-only",
        "prompt-injection-suspected",
        "external-evidence-instruction-blocked",
    }

    def __init__(self, *, artifacts_dir: Path):
        self.artifacts_dir = Path(artifacts_dir)
        self.sessions_dir = self.artifacts_dir / "computer-fabric" / "sessions"
        self.providers = ProviderRegistry()
        self.snapshots = SnapshotRewindRecorder()
        self.approvals = ApprovalQueue()
        self.secrets = SecretsBroker()
        self.firewall = PromptInjectionFirewall()

    def start_session(self, request: ComputerSessionRequest) -> ComputerSessionSummary:
        session_id = f"computer_{uuid4().hex[:12]}"
        environment_class = self._select_environment(request)
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        blocked_reasons: list[str] = []
        policy = self._compile_policy(request=request, environment_class=environment_class, blocked_reasons=blocked_reasons)
        firewall_report = self.firewall.scan(session_dir=session_dir, metadata=request.metadata)
        for finding in firewall_report["findings"]:
            if finding not in blocked_reasons:
                blocked_reasons.append(finding)
        policy["blocked_reasons"] = blocked_reasons
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
        self._record_event(events, "prompt_firewall.scanned", {"findings": firewall_report["findings"]})
        self._record_event(events, "provider.prepared", {"provider": policy["provider"]})
        approvals = self.approvals.record(
            session_dir=session_dir,
            session_id=session_id,
            blocked_reasons=blocked_reasons,
            scope=request.project_scope,
        )
        for approval in approvals:
            self._record_event(events, "approval.requested", {"approval_id": approval["approval_id"]})
        secret_bindings = self.secrets.bind(
            session_dir=session_dir,
            session_id=session_id,
            secret_ref=request.metadata.get("secret_ref"),
            provider_id=policy["provider_registry"]["selected_provider"]["provider_id"],
        )
        for binding in secret_bindings:
            self._record_event(events, "secret.reference_bound", {"binding_id": binding["binding_id"]})

        artifacts: list[dict[str, Any]] = []
        artifact_paths: list[Path] = []
        status = "failed-policy" if self._has_hard_policy_block(blocked_reasons) else "completed-review-required"
        if status != "failed-policy":
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
            artifact_paths.append(artifact_path)
            artifacts.append(artifact)
            self._record_event(events, "artifact.created", {"artifact_id": artifact["artifact_id"]})
            self._record_event(events, "artifact.scanned", {"artifact_id": artifact["artifact_id"], "trust_status": "trusted"})

        if environment_class == EnvironmentClass.PERSISTENT:
            self._write_json(
                session_dir / "persistent-health.json",
                {
                    "session_id": session_id,
                    "computer_id": f"persistent_{session_id}",
                    "status": "planned",
                    "schedule": request.schedule,
                    "uptime_state": "not-started",
                    "resource_quota": {"cpu": "bounded", "disk": "session-artifacts"},
                    "public_service_hosting": "blocked-without-separate-approval",
                    "last_checked_at": utcnow().isoformat(),
                },
            )
            self._record_event(events, "persistent.health_recorded", {"health_ref": "persistent-health.json"})

        snapshot_record = self.snapshots.record(session_dir=session_dir, artifact_paths=artifact_paths, policy=policy)
        self._record_event(events, "snapshot.created", {"checkpoint_id": snapshot_record["snapshot"]["checkpoint_id"]})
        self._record_event(events, "cleanup.proof_recorded", {"proof_status": snapshot_record["cleanup"]["proof_status"]})

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

    def scorecard(self) -> dict[str, Any]:
        session_summaries = self._read_session_summaries()
        environment_counts = {item.value: 0 for item in EnvironmentClass}
        trusted_artifact_count = 0
        blocked_artifact_count = 0
        latest_session = None
        for summary in session_summaries:
            environment = str(summary.get("environment_class", ""))
            if environment in environment_counts:
                environment_counts[environment] += 1
            trust = summary.get("trust_summary") or {}
            trusted_artifact_count += int(trust.get("trusted_artifact_count") or 0)
            blocked_artifact_count += int(trust.get("blocked_artifact_count") or 0)
            latest_session = latest_session or summary

        return {
            "control_panel_label": "Computer Fabric",
            "status_label": "MVP IMPLEMENTED - POLICY GATED",
            "session_count": len(session_summaries),
            "environment_counts": environment_counts,
            "trust": {
                "trusted_artifact_count": trusted_artifact_count,
                "blocked_artifact_count": blocked_artifact_count,
            },
            "environment_classes": [
                "Ephemeral Computer",
                "Persistent Computer",
                "Operator Computer",
            ],
            "latest_session": latest_session,
            "promotion_boundary": "no-production-mutation-without-review",
            "required_operator_surfaces": [
                "active sessions",
                "pending approvals",
                "artifact trust",
                "replay ledger",
                "cleanup state",
            ],
        }

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
        self._add_safety_findings(request=request, blocked_reasons=blocked_reasons)
        provider_registry = self.providers.summary(
            requested_provider=str(request.metadata.get("provider") or "") or None,
            environment_class=environment_class,
        )
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
            "provider_registry": provider_registry,
            "filesystem_policy": filesystem_policy,
            "network_policy": network_policy,
            "credential_policy": credential_policy,
            "schedule_policy": schedule_policy,
            "approval_policy": {"required_for": approval_required},
            "execution_boundary": execution_boundary,
            "required_checks": list(request.required_checks),
            "blocked_reasons": blocked_reasons,
        }

    def _add_safety_findings(self, *, request: ComputerSessionRequest, blocked_reasons: list[str]) -> None:
        requested_tools = set(request.requested_tools)
        if "filesystem.host_write" in requested_tools:
            blocked_reasons.append("host-write-blocked")
        if "network.unrestricted" in requested_tools:
            blocked_reasons.append("unrestricted-network-blocked")
        if "secrets.read" in requested_tools:
            blocked_reasons.append("secret-read-blocked")
        if "browser.action" in requested_tools:
            blocked_reasons.append("browser-action-requires-approval")
        if request.privacy_class == "unknown":
            blocked_reasons.append("unknown-privacy-local-only")

        untrusted_text = " ".join(
            [
                request.goal,
                request.task_type,
                " ".join(str(value) for value in request.metadata.values()),
            ]
        ).lower()
        if "ignore previous instructions" in untrusted_text or "upload secrets" in untrusted_text:
            blocked_reasons.append("prompt-injection-suspected")
        if "secrets.reference" in requested_tools:
            blocked_reasons.append("credential-use-requires-approval")

    def _has_hard_policy_block(self, blocked_reasons: list[str]) -> bool:
        return any(reason in self.HARD_BLOCK_REASONS for reason in blocked_reasons)

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

    def _read_session_summaries(self) -> list[dict[str, Any]]:
        if not self.sessions_dir.exists():
            return []
        summaries: list[dict[str, Any]] = []
        for path in sorted(self.sessions_dir.glob("*/session-summary.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                summaries.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
        return summaries
