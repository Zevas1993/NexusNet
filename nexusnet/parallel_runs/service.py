from __future__ import annotations

import hashlib
import json
import os
import socket
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class ParallelRunService:
    SUPPORTED_SOURCE_TYPES = {"github_issue", "local_spec", "manual"}
    SUPPORTED_DATABASE_MODES = {"none", "sqlite_clone", "neon_branch_candidate"}
    REVIEW_LANES = {"fresh_context", "adversarial", "human"}
    REVIEW_DECISIONS = {"approved", "changes_requested", "blocked"}
    SELF_HEALING_CATEGORIES = {
        "missing_spec",
        "weak_plan",
        "unsafe_tool_request",
        "missing_validation",
        "model_mismatch",
        "environment_conflict",
        "gate_gap",
        "review_gap",
    }
    SELF_HEALING_TARGETS = {"workflow", "recipe", "prompt", "skill", "gate", "test", "docs"}
    DEFAULT_WORKFLOW_ID = "nexus-parallel-issue-to-pr"

    def __init__(
        self,
        *,
        project_root: Path | str,
        artifacts_dir: Path | str,
        gateway: Any | None = None,
        workflow_service: Any | None = None,
        events: Any | None = None,
        base_port: int = 4100,
    ):
        self.project_root = Path(project_root)
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "parallel-runs"
        self.gateway = gateway
        self.workflow_service = workflow_service
        self.events = events
        self.base_port = base_port

    def prepare(
        self,
        *,
        source_type: str,
        source_ref: str,
        base_branch: str = "main",
        workspace_id: str = "default",
        agent_id: str = "standard-wrapper-agent",
        database_mode: str = "none",
        requested_tools: list[str] | None = None,
        requested_extensions: list[str] | None = None,
        validation_profile: str = "python-fast",
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        source_type = str(source_type)
        source_ref = str(source_ref)
        database_mode = str(database_mode)
        if source_type not in self.SUPPORTED_SOURCE_TYPES:
            raise ValueError(f"unsupported source_type: {source_type}")
        if database_mode not in self.SUPPORTED_DATABASE_MODES:
            raise ValueError(f"unsupported database_mode: {database_mode}")

        linked_trace_ids = list(linked_trace_ids or [])
        run_id = self._run_id(
            source_type=source_type,
            source_ref=source_ref,
            base_branch=base_branch,
            workspace_id=workspace_id,
        )
        branch_name = f"codex/agent-run-{self._slug(source_type)}-{self._slug(source_ref, max_length=80)}"
        worktree_path = self.project_root / ".worktrees" / "agent-runs" / run_id
        port_allocations = [
            {
                "name": "app",
                "port": self._allocate_port(run_id=run_id),
                "base_port": self.base_port,
                "strategy": "stable-hash-plus-probe",
            }
        ]
        dependency_bootstrap = self._dependency_bootstrap()
        database_isolation = self._database_isolation(
            mode=database_mode,
            run_id=run_id,
            branch_name=branch_name,
            worktree_path=worktree_path,
        )
        effective_requested_tools = sorted(
            set(
                [
                    "git.worktree.create",
                    "filesystem.write",
                    *(requested_tools or []),
                ]
            )
        )
        effective_requested_extensions = sorted(set(requested_extensions or []))
        gateway_resolution = self._gateway_resolution(
            agent_id=agent_id,
            workspace_id=workspace_id,
            requested_tools=effective_requested_tools,
            requested_extensions=effective_requested_extensions,
            linked_trace_ids=linked_trace_ids,
            run_id=run_id,
        )
        workflow_execution = self._record_workflow(
            run_id=run_id,
            source_type=source_type,
            source_ref=source_ref,
            workspace_id=workspace_id,
            agent_id=agent_id,
            database_mode=database_mode,
            validation_profile=validation_profile,
            requested_tools=effective_requested_tools,
            requested_extensions=effective_requested_extensions,
            linked_trace_ids=linked_trace_ids,
        )
        existing = self.get(run_id) or {}
        reviews = list(existing.get("reviews", []) or [])
        self_healing_signals = list(existing.get("self_healing_signals", []) or [])
        durable_ledger = self._durable_ledger(
            run_id=run_id,
            source_type=source_type,
            source_ref=source_ref,
            branch_name=branch_name,
            worktree_path=worktree_path,
            workflow_execution=workflow_execution,
        )
        record = {
            "run_id": run_id,
            "status": "prepared",
            "created_at": existing.get("created_at") or utcnow().isoformat(),
            "updated_at": utcnow().isoformat(),
            "source": {"source_type": source_type, "source_ref": source_ref},
            "base_branch": base_branch,
            "branch_name": branch_name,
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "worktree_path": self._display_path(worktree_path),
            "worktree": {
                "path": self._display_path(worktree_path),
                "state": "planned_only",
                "created": False,
                "mutation_requires_gateway": True,
                "cleanup_state": "not_started",
            },
            "port_allocations": port_allocations,
            "database_isolation": database_isolation,
            "dependency_bootstrap": dependency_bootstrap,
            "validation": {
                "profile": validation_profile,
                "state": "ready_for_gated_validation",
                "e2e_artifacts_required": True,
                "artifacts": [],
            },
            "workflow_execution_id": ((workflow_execution.get("execution_history") or {}).get("execution_id")),
            "workflow_execution": workflow_execution,
            "durable_ledger": durable_ledger,
            "gateway_resolution_id": (gateway_resolution or {}).get("resolution_id"),
            "gateway_decision_path": (gateway_resolution or {}).get("gateway_decision_path", []),
            "policy_path": (gateway_resolution or {}).get("policy_path", []),
            "approval_path": (gateway_resolution or {}).get("approval_path", {"decision": "deny"}),
            "requested_tools": effective_requested_tools,
            "requested_extensions": effective_requested_extensions,
            "review_summary": self._review_summary(reviews),
            "self_healing_summary": self._self_healing_summary(self_healing_signals),
            "reviews": reviews,
            "self_healing_signals": self_healing_signals,
            "cleanup_state": "not_started",
            "execution_allowed": False,
            "mutation_allowed": False,
            "policy": {
                "decision": "hold",
                "gateway_required": True,
                "product_sweep_required": True,
                "worktree_creation_allowed": False,
                "pr_creation_allowed": False,
                "push_allowed": False,
                "package_execution_allowed": False,
                "reason": "parallel-run-metadata-only-until-policy-grant",
            },
            "events": {},
            "artifacts_produced": self._workflow_artifacts(workflow_execution, gateway_resolution),
        }
        self._write(record)
        self._record_prepare_events(record)
        record["events"] = self._event_summary(run_id)
        self._write(record)
        return record

    def review(
        self,
        *,
        run_id: str,
        lane: str,
        decision: str,
        reviewer: str = "operator",
        findings: list[dict[str, Any]] | None = None,
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        if lane not in self.REVIEW_LANES:
            raise ValueError(f"unsupported review lane: {lane}")
        if decision not in self.REVIEW_DECISIONS:
            raise ValueError(f"unsupported review decision: {decision}")
        record = self._require(run_id)
        findings = list(findings or [])
        linked_trace_ids = list(linked_trace_ids or [])
        if self.events:
            self.events.record(
                event_type="parallel_run.review_requested",
                subject=f"parallel-run:{run_id}",
                trace_ids=linked_trace_ids,
                payload={"lane": lane, "decision": decision, "reviewer": reviewer},
            )
        review = {
            "review_id": new_id("parallelreview"),
            "created_at": utcnow().isoformat(),
            "lane": lane,
            "decision": decision,
            "reviewer": reviewer,
            "findings": findings,
            "linked_trace_ids": linked_trace_ids,
            "execution_allowed": False,
            "mutation_allowed": False,
        }
        record.setdefault("reviews", []).append(review)
        record["review_summary"] = self._review_summary(record["reviews"])
        record["status"] = {
            "approved": "review_approved",
            "changes_requested": "review_changes_requested",
            "blocked": "review_blocked",
        }[decision]
        record["updated_at"] = utcnow().isoformat()
        if self.events:
            self.events.record(
                event_type="parallel_run.review_completed",
                subject=f"parallel-run:{run_id}",
                trace_ids=linked_trace_ids,
                payload={"review_id": review["review_id"], "lane": lane, "decision": decision, "finding_count": len(findings)},
            )
        record["events"] = self._event_summary(run_id)
        self._write(record)
        return record

    def self_healing_report(
        self,
        *,
        run_id: str,
        signals: list[dict[str, Any]],
        linked_trace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        record = self._require(run_id)
        linked_trace_ids = list(linked_trace_ids or [])
        normalized_signals: list[dict[str, Any]] = []
        for signal in signals:
            category = str(signal.get("category") or "")
            target = str(signal.get("target") or "")
            if category not in self.SELF_HEALING_CATEGORIES:
                raise ValueError(f"unsupported self-healing category: {category}")
            if target not in self.SELF_HEALING_TARGETS:
                raise ValueError(f"unsupported self-healing target: {target}")
            normalized = {
                "signal_id": new_id("parallelsignal"),
                "created_at": utcnow().isoformat(),
                "category": category,
                "target": target,
                "message": str(signal.get("message") or ""),
                "source": str(signal.get("source") or "operator"),
                "linked_trace_ids": linked_trace_ids,
                "mutation_allowed": False,
            }
            normalized_signals.append(normalized)

        record.setdefault("self_healing_signals", []).extend(normalized_signals)
        record["self_healing_summary"] = self._self_healing_summary(record["self_healing_signals"])
        record["updated_at"] = utcnow().isoformat()
        if self.events:
            for signal in normalized_signals:
                self.events.record(
                    event_type="parallel_run.self_healing_signal_recorded",
                    subject=f"parallel-run:{run_id}",
                    trace_ids=linked_trace_ids,
                    payload={
                        "signal_id": signal["signal_id"],
                        "category": signal["category"],
                        "target": signal["target"],
                        "mutation_allowed": False,
                    },
                )
        record["events"] = self._event_summary(run_id)
        self._write(record)
        return record

    def summary(self, *, source_type: str | None = None, status: str | None = None, limit: int = 50) -> dict[str, Any]:
        items = self.list(source_type=source_type, status=status, limit=limit)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "run_count": len(items),
            "source_type": source_type,
            "status": status,
            "status_counts": self._counts(items, "status"),
            "source_type_counts": self._source_counts(items),
            "latest_run": items[0] if items else None,
            "execution_allowed": False,
            "mutation_allowed": False,
            "event_log": self.events.summary(subject_prefix="parallel-run:", limit=200) if self.events else {},
            "items": items,
        }

    def history(self, *, source_type: str | None = None, status: str | None = None, limit: int = 50) -> dict[str, Any]:
        summary = self.summary(source_type=source_type, status=status, limit=limit)
        return {
            **summary,
            "event_type_counts": (summary.get("event_log") or {}).get("event_type_counts", {}),
        }

    def list(self, *, source_type: str | None = None, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        if not self.output_dir.exists():
            return items
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if source_type and (payload.get("source") or {}).get("source_type") != source_type:
                continue
            if status and payload.get("status") != status:
                continue
            items.append(payload)
            if len(items) >= limit:
                break
        return items

    def get(self, run_id: str) -> dict[str, Any] | None:
        path = self.output_dir / f"{run_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def _gateway_resolution(
        self,
        *,
        agent_id: str,
        workspace_id: str,
        requested_tools: list[str],
        requested_extensions: list[str],
        linked_trace_ids: list[str],
        run_id: str,
    ) -> dict[str, Any] | None:
        if self.gateway is None:
            return None
        return self.gateway.resolve(
            agent_id=agent_id,
            workspace_id=workspace_id,
            requested_tools=requested_tools,
            requested_extensions=requested_extensions,
            require_user_approval=True,
            trigger_source=f"parallel:{run_id}",
            linked_trace_ids=linked_trace_ids,
            record_gateway_flow=True,
        )

    def _record_workflow(
        self,
        *,
        run_id: str,
        source_type: str,
        source_ref: str,
        workspace_id: str,
        agent_id: str,
        database_mode: str,
        validation_profile: str,
        requested_tools: list[str],
        requested_extensions: list[str],
        linked_trace_ids: list[str],
    ) -> dict[str, Any]:
        if self.workflow_service is None or self.workflow_service.get(self.DEFAULT_WORKFLOW_ID) is None:
            return {}
        return self.workflow_service.execute(
            workflow_id=self.DEFAULT_WORKFLOW_ID,
            trigger_source=f"parallel:{run_id}",
            workspace_id=workspace_id,
            agent_id=agent_id,
            parameter_set={
                "run_id": run_id,
                "source_type": source_type,
                "source_ref": source_ref,
                "database_mode": database_mode,
                "validation_profile": validation_profile,
            },
            linked_trace_ids=linked_trace_ids,
            requested_tools=requested_tools,
            requested_extensions=requested_extensions,
            approval_path={"decision": "ask", "approval_is_execution_authority": False},
            status="prepared",
        )

    def _dependency_bootstrap(self) -> dict[str, Any]:
        dependency_files = [
            name
            for name in ["pyproject.toml", "requirements.txt", "package.json", "pnpm-lock.yaml", "poetry.lock"]
            if (self.project_root / name).exists()
        ]
        if not dependency_files:
            status = "not_required"
        else:
            status = "policy_blocked"
        return {
            "status": status,
            "detected_files": dependency_files,
            "install_executed": False,
            "reason": "metadata-only-v1" if dependency_files else "no-dependency-manifest-detected",
        }

    def _database_isolation(self, *, mode: str, run_id: str, branch_name: str, worktree_path: Path) -> dict[str, Any]:
        if mode == "none":
            return {"mode": mode, "state": "not_requested", "mutation_allowed": False}
        if mode == "sqlite_clone":
            return {
                "mode": mode,
                "state": "planned_clone",
                "source": self._display_path(self.project_root / "runtime" / "nexus.sqlite"),
                "target": self._display_path(worktree_path / "runtime" / "nexus.sqlite"),
                "clone_created": False,
                "mutation_allowed": False,
            }
        neon_configured = bool(os.environ.get("NEON_DATABASE_URL") or os.environ.get("NEON_API_KEY"))
        return {
            "mode": mode,
            "state": "metadata_only",
            "branch_name": self._slug(f"{branch_name}-{run_id}", max_length=90),
            "credentials_detected": neon_configured,
            "branch_created": False,
            "credentials_redacted": True,
            "mutation_allowed": False,
        }

    def _durable_ledger(
        self,
        *,
        run_id: str,
        source_type: str,
        source_ref: str,
        branch_name: str,
        worktree_path: Path,
        workflow_execution: dict[str, Any],
    ) -> dict[str, Any]:
        workflow_history = workflow_execution.get("execution_history") or {}
        return {
            "ledger_kind": "parallel-agent-run-ledger",
            "metadata_only": True,
            "mutation_allowed": False,
            "execution_allowed": False,
            "run_id": run_id,
            "source_type": source_type,
            "source_ref": source_ref,
            "branch_name": branch_name,
            "worktree_path": self._display_path(worktree_path),
            "checkpoint_count": 4,
            "checkpoints": [
                {"checkpoint_id": f"{run_id}:source-intake", "state": "recorded", "mutation_allowed": False},
                {"checkpoint_id": f"{run_id}:worktree-plan", "state": "planned_only", "mutation_allowed": False},
                {"checkpoint_id": f"{run_id}:validation-profile", "state": "recorded", "mutation_allowed": False},
                {"checkpoint_id": f"{run_id}:review-lanes", "state": "awaiting_review", "mutation_allowed": False},
            ],
            "resume": {
                "state": "planned_only",
                "requires_gateway_grant": True,
                "requires_product_sweep_pass": True,
            },
            "interrupts": [
                {
                    "reason": "worktree_creation_requires_policy",
                    "operator_visible": True,
                    "mutation_allowed": False,
                }
            ],
            "replay": {
                "deterministic_replay_supported": True,
                "source_type": source_type,
                "source_ref": source_ref,
                "workflow_execution_id": workflow_history.get("execution_id"),
            },
            "human_state_edit": {"allowed": False, "approval_path": "gateway-and-product-sweep-required"},
        }

    def _allocate_port(self, *, run_id: str) -> int:
        used = self._used_ports(excluding_run_id=run_id)
        offset = int(hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:6], 16) % 900
        candidate = self.base_port + offset
        while candidate in used or not self._port_available(candidate):
            candidate += 1
        return candidate

    def _used_ports(self, *, excluding_run_id: str) -> set[int]:
        used: set[int] = set()
        for item in self.list(limit=500):
            if item.get("run_id") == excluding_run_id:
                continue
            for allocation in item.get("port_allocations", []) or []:
                try:
                    used.add(int(allocation.get("port")))
                except (TypeError, ValueError):
                    continue
        return used

    def _port_available(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.05)
            return sock.connect_ex(("127.0.0.1", port)) != 0

    def _record_prepare_events(self, record: dict[str, Any]) -> None:
        if not self.events:
            return
        run_id = record["run_id"]
        subject = f"parallel-run:{run_id}"
        self.events.record(event_type="parallel_run.worktree_planned", subject=subject, payload=record["worktree"])
        for allocation in record.get("port_allocations", []):
            self.events.record(event_type="parallel_run.port_allocated", subject=subject, payload=allocation)
        self.events.record(event_type="parallel_run.database_isolation_selected", subject=subject, payload=record["database_isolation"])
        self.events.record(
            event_type="parallel_run.validation_started",
            subject=subject,
            payload={
                "profile": record["validation"]["profile"],
                "state": "metadata_only_profile_recorded",
                "executed": False,
                "execution_allowed": False,
            },
        )
        self.events.record(
            event_type="parallel_run.validation_completed",
            subject=subject,
            payload={
                "profile": record["validation"]["profile"],
                "state": record["validation"]["state"],
                "artifact_count": len(record["validation"].get("artifacts", []) or []),
                "executed": False,
                "execution_allowed": False,
            },
        )
        self.events.record(
            event_type="parallel_run.cleanup_recorded",
            subject=subject,
            payload={
                "cleanup_state": record["cleanup_state"],
                "worktree_created": record["worktree"]["created"],
                "executed": False,
                "mutation_allowed": False,
            },
        )
        self.events.record(
            event_type="parallel_run.prepared",
            subject=subject,
            payload={
                "source": record["source"],
                "branch_name": record["branch_name"],
                "worktree_path": record["worktree_path"],
                "execution_allowed": False,
                "mutation_allowed": False,
            },
        )

    def _workflow_artifacts(self, workflow_execution: dict[str, Any], gateway_resolution: dict[str, Any] | None) -> list[str]:
        artifacts: set[str] = set()
        if (gateway_resolution or {}).get("artifact_path"):
            artifacts.add(str((gateway_resolution or {}).get("artifact_path")))
        if workflow_execution.get("artifact_path"):
            artifacts.add(str(workflow_execution["artifact_path"]))
        for artifact in ((workflow_execution.get("execution_history") or {}).get("artifacts_produced") or []):
            if artifact:
                artifacts.add(str(artifact))
        return sorted(artifacts)

    def _event_summary(self, run_id: str) -> dict[str, Any]:
        if not self.events:
            return {}
        return self.events.summary(subject_prefix=f"parallel-run:{run_id}", limit=100)

    def _write(self, record: dict[str, Any]) -> None:
        path = self.output_dir / f"{record['run_id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        record["artifact_path"] = self._display_path(path)
        artifacts = set(record.get("artifacts_produced", []) or [])
        artifacts.add(record["artifact_path"])
        record["artifacts_produced"] = sorted(artifacts)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _require(self, run_id: str) -> dict[str, Any]:
        record = self.get(run_id)
        if record is None:
            raise KeyError(run_id)
        return record

    def _run_id(self, *, source_type: str, source_ref: str, base_branch: str, workspace_id: str) -> str:
        seed = f"{source_type}\n{source_ref}\n{base_branch}\n{workspace_id}"
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:10]
        return f"prun_{self._slug(source_type)}-{self._slug(source_ref, max_length=64)}_{digest}"

    def _review_summary(self, reviews: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "review_count": len(reviews),
            "lane_counts": self._counts(reviews, "lane"),
            "decision_counts": self._counts(reviews, "decision"),
            "latest_review": reviews[-1] if reviews else None,
        }

    def _self_healing_summary(self, signals: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "signal_count": len(signals),
            "category_counts": self._counts(signals, "category"),
            "target_counts": self._counts(signals, "target"),
            "latest_signal": signals[-1] if signals else None,
        }

    def _source_counts(self, items: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            source_type = str((item.get("source") or {}).get("source_type") or "unknown")
            counts[source_type] = counts.get(source_type, 0) + 1
        return counts

    def _counts(self, items: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = str(item.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _slug(self, value: Any, *, max_length: int = 120) -> str:
        slug = "".join(ch if ch.isalnum() else "-" for ch in str(value).lower()).strip("-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        return (slug or "unknown")[:max_length].strip("-") or "unknown"

    def _display_path(self, path: Path) -> str:
        return str(path).replace("\\", "/")
