from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import new_id, utcnow
from nexusnet.operations import CodegraphGate, CodegraphRunManifestRequest
from nexusnet.policy import PolicyKernel


SandboxProvider = Literal["docker", "podman", "vercel", "local-devcontainer", "custom"]


class SandboxAgentFactoryRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = "default"
    backlog_ref: str
    target_branch: str = "main"
    task_ids: list[str] = Field(default_factory=list)
    agent_profile: str = "claude-code"
    sandbox_provider: SandboxProvider = "docker"
    workflow_template: str = "parallel-planner-review-merge"
    max_parallel_agents: int = Field(default=1, ge=1, le=16)
    prompts: dict[str, str] = Field(default_factory=dict)
    required_checks: list[str] = Field(default_factory=list)
    requested_permissions: list[str] = Field(default_factory=list)
    upstream_aitune_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SandboxAgentFactory:
    def __init__(self, *, artifacts_dir: Path | str | None = None) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.runs_dir = self.artifacts_dir / "agents" / "sandbox-factory" / "runs" if self.artifacts_dir else None
        if self.runs_dir is not None:
            self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.policy_kernel = PolicyKernel.default()
        self.codegraph_gate = CodegraphGate(artifacts_dir=self.artifacts_dir)

    def start(self, request: SandboxAgentFactoryRunRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = (
            request
            if isinstance(request, SandboxAgentFactoryRunRequest)
            else SandboxAgentFactoryRunRequest.model_validate(request)
        )
        created_at = utcnow().isoformat()
        run_id = new_id("sandbox_factory")
        immune_findings = _immune_findings(normalized.requested_permissions)
        upstream_aitune_gate = _upstream_aitune_gate(normalized.upstream_aitune_gate)
        upstream_aitune_blocked = _upstream_aitune_gate_blocked(upstream_aitune_gate)
        codegraph_manifest = self.codegraph_gate.evaluate(_codegraph_manifest_request(normalized, run_id))
        policy_scan = self.policy_kernel.scan(
            _policy_targets(normalized, immune_findings, upstream_aitune_gate, codegraph_manifest)
        )
        blocked = bool(immune_findings) or policy_scan.summary.active_hard_fail_count > 0 or upstream_aitune_blocked
        lifecycle_state = "blocked-upstream-gate" if upstream_aitune_blocked else ("blocked" if blocked else "planned")
        task_ids = normalized.task_ids or ["backlog:auto-select"]
        blocks = _workflow_blocks(
            normalized,
            task_ids,
            blocked=blocked,
            upstream_aitune_blocked=upstream_aitune_blocked,
        )
        manifest = {
            "manifest_id": f"manifest::{run_id}",
            "backlog_ref": normalized.backlog_ref,
            "target_branch": normalized.target_branch,
            "task_ids": task_ids,
            "agent_profile": normalized.agent_profile,
            "sandbox_provider": normalized.sandbox_provider,
            "workflow_template": normalized.workflow_template,
            "max_parallel_agents": normalized.max_parallel_agents,
            "worktree_strategy": "one-worktree-per-task",
            "branch_prefix": "codex/sandbox-agent/",
            "merge_policy": "reviewed-tests-pass-policy-clean",
            "prompt_contract": {
                "prompt_args_enabled": True,
                "dynamic_context_commands": "sandbox-scoped-only",
                "prompt_keys": sorted(normalized.prompts.keys()),
            },
            "required_checks": normalized.required_checks,
            "permission_boundary": {
                "host_home_write": "blocked",
                "network_unrestricted": "blocked",
                "merge_without_review": "blocked",
                "default_network": "deny-by-default-unless-task-scoped",
                "write_scope": "sandbox-worktree-only",
            },
        }
        checkpoint = {
            "checkpoint_id": new_id("sandbox_checkpoint"),
            "created_at": created_at,
            "checkpoint_type": "pre-afk-run",
            "rewind_scope": "worktree-branch-artifact-ledger",
            "target_branch": normalized.target_branch,
            "task_count": len(task_ids),
        }
        artifact_path = self._artifact_path(run_id)
        result = {
            "status_label": "LOCKED CANON",
            "surface_id": "sandbox-agent-factory",
            "authority": "NexusBrain",
            "run_id": run_id,
            "session_id": normalized.session_id,
            "created_at": created_at,
            "lifecycle_state": lifecycle_state,
            "runtime_state": "degraded" if blocked else "live-bound",
            "manifest": manifest,
            "blocks": blocks,
            "checkpoint": checkpoint,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "immune_findings": immune_findings,
            "codegraph_manifest": codegraph_manifest,
            "upstream_aitune_gate": upstream_aitune_gate,
            "events": _events(
                run_id=run_id,
                session_id=normalized.session_id,
                created_at=created_at,
                blocked=blocked,
                upstream_aitune_blocked=upstream_aitune_blocked,
                parallel_count=min(normalized.max_parallel_agents, len(task_ids)),
            ),
            "artifact_path": str(artifact_path) if artifact_path else None,
            "metadata": normalized.metadata,
        }
        self._persist(artifact_path, result)
        return result

    def summary(self, *, session_id: str | None = None, limit: int = 20) -> dict[str, Any]:
        runs = self._list_runs(session_id=session_id, limit=limit)
        blocked_count = sum(1 for run in runs if str(run.get("lifecycle_state") or "").startswith("blocked"))
        latest = runs[0] if runs else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if str(latest.get("lifecycle_state") or "").startswith("blocked") else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "sandbox-agent-factory",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "session_id": session_id,
            "run_count": len(runs),
            "blocked_count": blocked_count,
            "latest_run": latest,
            "recent_runs": runs[: min(limit, 10)],
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
            "factory_boundary": "nexus-native-sandbox-agent-orchestration-not-direct-package-dependency",
        }

    def scorecard(self, *, session_id: str | None = None) -> dict[str, Any]:
        summary = self.summary(session_id=session_id)
        return {
            **summary,
            "runtime_state": summary["runtime_state"],
            "control_panel_label": "Sandbox Agent Factory",
            "source_documents": [
                "https://github.com/mattpocock/sandcastle",
                "https://www.sourcepulse.org/projects/27307520",
                "https://gist.github.com/opticom/c0e5e6954874b1991e3c9b0ab7cfefe1",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-01-015",
            ],
            "architecture_contract": [
                "programmatic_run_contract",
                "sandbox_provider_abstraction",
                "worktree_per_agent",
                "backlog_task_picker",
                "planner_implementer_reviewer_merger_flow",
                "merge_back_policy_gate",
                "logs_and_artifacts_per_run",
            ],
        }

    def _artifact_path(self, run_id: str) -> Path | None:
        return self.runs_dir / f"{run_id}.json" if self.runs_dir else None

    def _persist(self, path: Path | None, payload: dict[str, Any]) -> None:
        if path is not None:
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _list_runs(self, *, session_id: str | None, limit: int) -> list[dict[str, Any]]:
        if self.runs_dir is None or not self.runs_dir.exists():
            return []
        runs: list[dict[str, Any]] = []
        for path in self.runs_dir.glob("*.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if session_id and payload.get("session_id") != session_id:
                continue
            runs.append(payload)
        runs.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return runs[:limit]


def _workflow_blocks(
    request: SandboxAgentFactoryRunRequest,
    task_ids: list[str],
    *,
    blocked: bool,
    upstream_aitune_blocked: bool,
) -> list[dict[str, Any]]:
    parallel_count = min(request.max_parallel_agents, len(task_ids))
    blocked_status = "blocked-upstream-gate" if upstream_aitune_blocked else "blocked"
    return [
        {
            "block_id": "planner",
            "role": "planner",
            "agent_profile": request.agent_profile,
            "sandbox_provider": request.sandbox_provider,
            "branch": f"codex/sandbox-agent/planner-{_slug(request.session_id)}",
            "status": blocked_status if blocked else "queued",
            "expected_output": "unblocked task plan with dependency and risk notes",
        },
        {
            "block_id": "implementer",
            "role": "implementer",
            "agent_profile": request.agent_profile,
            "sandbox_provider": request.sandbox_provider,
            "parallel_instances": parallel_count,
            "branches": [f"codex/sandbox-agent/{_slug(task_id)}" for task_id in task_ids[:parallel_count]],
            "status": blocked_status if blocked else "queued",
            "expected_output": "commits inside isolated sandbox worktrees",
        },
        {
            "block_id": "reviewer",
            "role": "reviewer",
            "agent_profile": "adversarial-reviewer",
            "sandbox_provider": request.sandbox_provider,
            "status": blocked_status if blocked else "queued",
            "expected_output": "diff review with required check evidence",
        },
        {
            "block_id": "merger",
            "role": "merger",
            "agent_profile": "senior-merger",
            "sandbox_provider": request.sandbox_provider,
            "target_branch": request.target_branch,
            "status": blocked_status if blocked else "gated",
            "expected_output": "merge-ready branch only after review, tests, policy scan, and rollback metadata",
        },
    ]


def _immune_findings(permissions: list[str]) -> list[dict[str, Any]]:
    rules = {
        "host_home_write": "Host home directory writes are never allowed for AFK sandbox agents.",
        "network_unrestricted": "Unrestricted network access is blocked; network access must be task scoped.",
        "merge_without_review": "Merge-back requires reviewer and policy gate evidence.",
    }
    findings: list[dict[str, Any]] = []
    for permission in permissions:
        if permission not in rules:
            continue
        findings.append(
            {
                "finding_id": f"immune::{permission}",
                "rule_id": f"{permission}_blocked",
                "severity": "hard_fail",
                "blocked": True,
                "message": rules[permission],
                "required_evidence": ["sandbox_scope", "review_gate", "policy_scan", "rollback_checkpoint"],
            }
        )
    return findings


def _policy_targets(
    request: SandboxAgentFactoryRunRequest,
    immune_findings: list[dict[str, Any]],
    upstream_aitune_gate: dict[str, Any],
    codegraph_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    write_enabled = bool(request.task_ids)
    unsafe_requested = bool(immune_findings)
    targets = [
        {
            "target_id": f"sandbox-agent::{request.session_id}",
            "target_type": "tool_execution",
            "metadata": {
                "write_enabled": write_enabled,
                "sandboxed": not unsafe_requested,
                "tool_scope": "sandbox-worktree-only" if not unsafe_requested else "",
            },
        },
        {
            "target_id": f"code-change::{request.session_id}",
            "target_type": "code_change",
            "metadata": {
                "tests_provided": bool(request.required_checks),
                "required_checks": request.required_checks,
                "codegraph_manifest_ref": codegraph_manifest.get("manifest_id") if codegraph_manifest.get("status") == "allowed" else "",
                "codegraph_status": codegraph_manifest.get("status"),
            },
        },
        {
            "target_id": f"autonomous-update::{request.session_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": True,
                "rollback_plan": "worktree-branch-checkpoint" if not unsafe_requested else "",
                "monitoring_plan": "artifact-ledger-and-control-panel-scorecard" if request.required_checks and not unsafe_requested else "",
            },
        },
    ]
    if _upstream_aitune_gate_blocked(upstream_aitune_gate):
        targets.append(
            {
                "target_id": f"sandbox-agent-upstream-runtime::{request.session_id}",
                "target_type": "tool_execution",
                "metadata": {
                    "write_enabled": True,
                    "sandboxed": False,
                    "upstream_aitune_gate": upstream_aitune_gate,
                },
            }
        )
    return targets


def _events(
    *,
    run_id: str,
    session_id: str,
    created_at: str,
    blocked: bool,
    upstream_aitune_blocked: bool,
    parallel_count: int,
) -> list[dict[str, Any]]:
    specs = [
        ("run.created", "SandboxAgentFactory", "Created AFK sandbox factory run."),
        ("planner.queued", "PlannerAgent", "Queued backlog planner inside sandbox."),
        ("implementers.parallelized", "ImplementerAgents", f"Queued {parallel_count} parallel implementer lane(s)."),
        ("reviewer.queued", "ReviewerAgent", "Queued adversarial review lane."),
        ("merger.gated", "MergerAgent", "Merge-back gated by checks, review, policy, and rollback metadata."),
        (
            "upstream_aitune_gate_blocked" if upstream_aitune_blocked else ("run.blocked" if blocked else "run.planned"),
            "NexusBrain",
            "Blocked AFK sandbox run because upstream AITune/QES runtime evidence is blocked."
            if upstream_aitune_blocked
            else ("Blocked unsafe AFK permissions." if blocked else "Run is planned and waiting for operator execution."),
        ),
    ]
    return [
        {
            "event_id": f"{run_id}::{event_type}",
            "run_id": run_id,
            "session_id": session_id,
            "event_type": event_type,
            "actor": actor,
            "detail": detail,
            "created_at": created_at,
        }
        for event_type, actor, detail in specs
    ]


def _codegraph_manifest_request(
    request: SandboxAgentFactoryRunRequest,
    run_id: str,
) -> CodegraphRunManifestRequest:
    """Build the plan-stage codegraph manifest for an AFK factory run.

    The factory itself does not edit the repository; it plans worktree-isolated agent work.
    This plan-stage manifest registers the codegraph context for the orchestration and records
    that each downstream sandbox code edit must carry its own impact and detect-changes evidence
    before merge. Operators may pass real graph evidence through ``metadata['codegraph']`` to make
    the plan carry concrete indexed/worktree commits, impact risk, and detect-changes refs; a
    stale index or HIGH/CRITICAL impact then blocks the plan through the same gate.
    """
    codegraph = request.metadata.get("codegraph") or {}
    indexed_commit = str(codegraph.get("indexed_commit") or "plan-stage")
    worktree_commit = str(codegraph.get("worktree_commit") or indexed_commit)
    impact_risk = str(codegraph.get("impact_risk") or "not_required")
    # Default is a plan-stage research_only manifest (the factory orchestrates rather than edits).
    # Operators can declare a concrete code_edit plan with real graph evidence, which then makes
    # stale-index and HIGH/CRITICAL-impact runs block through the same gate.
    run_kind = str(codegraph.get("run_kind") or "research_only")
    return CodegraphRunManifestRequest(
        manifest_id=f"codegraph::sandbox-factory::{run_id}",
        run_kind=run_kind,  # type: ignore[arg-type]
        indexed_repo=str(codegraph.get("indexed_repo") or "NexusNet"),
        indexed_commit=indexed_commit,
        worktree_commit=worktree_commit,
        graph_query_ref=str(codegraph.get("graph_query_ref") or "sandbox-agent-factory::plan"),
        impact_target=str(codegraph.get("impact_target") or ""),
        impact_risk=impact_risk,  # type: ignore[arg-type]
        affected_processes=list(codegraph.get("affected_processes") or []),
        detect_changes_ref=str(codegraph.get("detect_changes_ref") or f"sandbox-agent-factory::{request.session_id}"),
        metadata={
            "stage": "afk-orchestration-plan",
            "downstream_code_edit_requires_codegraph_evidence": True,
            "downstream_run_kind": "code_edit",
            "session_id": request.session_id,
        },
    )


def _upstream_aitune_gate(gate: dict[str, Any]) -> dict[str, Any]:
    blockers = list(gate.get("blockers") or gate.get("readiness_blockers") or [])
    status = str(gate.get("status") or "not_provided")
    can_execute_here = gate.get("can_execute_here")
    if can_execute_here is False and not blockers:
        blockers.append("upstream_aitune_execution_not_ready")
    if status in {"blocked", "blocked-upstream-gate"} and not blockers:
        blockers.append("upstream_aitune_gate_blocked")
    return {
        **gate,
        "status": status,
        "can_execute_here": can_execute_here,
        "blockers": blockers,
    }


def _upstream_aitune_gate_blocked(gate: dict[str, Any]) -> bool:
    return bool(
        gate.get("can_execute_here") is False
        or gate.get("status") in {"blocked", "blocked-upstream-gate"}
        or gate.get("blockers")
    )


def _required_controls() -> list[str]:
    return [
        "worktree_per_agent",
        "sandbox_provider_abstraction",
        "backlog_label_filter",
        "planner_implementer_reviewer_merger_flow",
        "merge_back_policy_gate",
        "logs_and_artifacts_per_run",
        "permissioned_afk_execution",
        "required_checks_before_merge",
        "rollback_checkpoint",
    ]


def _operator_actions() -> dict[str, dict[str, Any]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/sandbox-agent-factory"},
        "create_run": {"method": "POST", "endpoint": "/ops/brain/sandbox-agent-factory/runs"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/sandbox-agent-factory"},
    }


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-").lower()
    return slug or "task"
