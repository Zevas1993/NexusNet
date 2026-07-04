from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import new_id, utcnow
from nexusnet.policy import PolicyKernel, PolicyTarget


PipelineMode = Literal["sequential", "parallel", "review-loop"]


class PipelineBlockSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    block_id: str
    role: str
    expected_output: str
    profile_id: str | None = None
    dependencies: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    requested_extensions: list[str] = Field(default_factory=list)
    context_mode: str = "fresh-subprocess"


class AgenticPipelineRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = "default"
    pipeline_id: str
    goal: str
    profile_id: str = "nexusbrain-governed-dev"
    requested_by: str = "NexusBrain"
    mode: PipelineMode = "sequential"
    blocks: list[PipelineBlockSpec] = Field(default_factory=list)
    policy_targets: list[PolicyTarget | dict[str, Any]] = Field(default_factory=list)
    upstream_aitune_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgenticPipelineRuntime:
    def __init__(self, *, artifacts_dir: Path):
        self.artifacts_dir = Path(artifacts_dir)
        self.runs_dir = self.artifacts_dir / "agents" / "pipelines" / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.policy_kernel = PolicyKernel.default()

    def start(self, request: AgenticPipelineRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, AgenticPipelineRequest) else AgenticPipelineRequest.model_validate(request)
        created_at = utcnow().isoformat()
        run_id = new_id("agentic_pipeline")
        blocks = list(normalized.blocks or _default_blocks())
        upstream_aitune_gate = _upstream_aitune_gate(normalized.upstream_aitune_gate)
        upstream_aitune_blocked = _upstream_aitune_gate_blocked(upstream_aitune_gate)
        policy_targets = list(normalized.policy_targets)
        if upstream_aitune_blocked:
            policy_targets.append(
                {
                    "target_id": f"agentic-pipeline-runtime::{normalized.pipeline_id}",
                    "target_type": "tool_execution",
                    "metadata": {
                        "write_enabled": True,
                        "sandboxed": False,
                        "upstream_aitune_gate": upstream_aitune_gate,
                    },
                }
            )
        policy_scan = self.policy_kernel.scan(policy_targets)
        policy_blocked = policy_scan.summary.active_hard_fail_count > 0
        lifecycle_state = (
            "blocked_by_upstream_aitune_gate"
            if upstream_aitune_blocked
            else ("blocked_by_policy" if policy_blocked else "completed")
        )
        artifact_path = self.runs_dir / f"{run_id}.json"
        manifest = {
            "manifest_id": f"manifest::{run_id}",
            "pipeline_id": normalized.pipeline_id,
            "goal": normalized.goal,
            "profile_id": normalized.profile_id,
            "mode": normalized.mode,
            "fresh_context_per_block": True,
            "artifact_mode": "repo-disk-ledger",
            "compressed_summary_mode": "block-summary-plus-run-ledger",
            "branch_policy": {
                "isolated_worktree_required": True,
                "branch_prefix": "codex/",
                "merge_requires_policy_scan": True,
            },
            "governance": {
                "authority": "NexusBrain",
                "policy_kernel_ref": "/ops/brain/policy/scan",
                "promotion_gate": "policy-scan-plus-manager-review",
            },
        }
        block_payloads = [
            {
                "block_id": block.block_id,
                "role": block.role,
                "expected_output": block.expected_output,
                "profile_id": block.profile_id or normalized.profile_id,
                "dependencies": list(block.dependencies),
                "allowed_tools": list(block.allowed_tools),
                "requested_extensions": list(block.requested_extensions),
                "context_mode": block.context_mode,
                "status": (
                    "blocked-upstream-gate"
                    if upstream_aitune_blocked
                    else ("blocked" if policy_blocked and block.role == "policy" else "completed")
                ),
            }
            for block in blocks
        ]
        events = self._events(
            run_id=run_id,
            session_id=normalized.session_id,
            request=normalized,
            blocks=block_payloads,
            policy_scan=policy_scan.model_dump(mode="json"),
            lifecycle_state=lifecycle_state,
            created_at=created_at,
        )
        run = {
            "status_label": "LOCKED CANON",
            "run_id": run_id,
            "session_id": normalized.session_id,
            "pipeline_id": normalized.pipeline_id,
            "authority": "NexusBrain",
            "requested_by": normalized.requested_by,
            "goal": normalized.goal,
            "lifecycle_state": lifecycle_state,
            "runtime_state": "degraded" if lifecycle_state.startswith("blocked") else "live-bound",
            "created_at": created_at,
            "manifest": manifest,
            "blocks": block_payloads,
            "events": events,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "upstream_aitune_gate": upstream_aitune_gate,
            "artifact_path": str(artifact_path),
            "metadata": normalized.metadata,
        }
        artifact_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
        return run

    def summary(self, *, session_id: str | None = None, limit: int = 20) -> dict[str, Any]:
        runs = self._list_runs(session_id=session_id, limit=limit)
        blocked_count = sum(1 for run in runs if str(run.get("lifecycle_state") or "").startswith("blocked"))
        latest = runs[0] if runs else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if str(latest.get("lifecycle_state") or "").startswith("blocked") else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "agentic-pipeline-runtime",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "session_id": session_id,
            "run_count": len(runs),
            "blocked_count": blocked_count,
            "latest_run": latest,
            "recent_runs": runs[: min(limit, 10)],
            "required_controls": _required_controls(),
            "promotion_boundary": "pipeline-runs-require-manifest-events-policy-scan-manager-review-and-artifact-ledger",
            "operator_actions": _operator_actions(),
        }

    def scorecard(self, *, session_id: str | None = None) -> dict[str, Any]:
        summary = self.summary(session_id=session_id)
        return {
            **summary,
            "pipeline_runtime_state": summary["runtime_state"],
            "source_document": "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
            "research_source_ids": ["YT-02", "YT-04"],
            "block_contract": [
                "fresh_subprocess_context",
                "manifest_before_execution",
                "artifact_output_after_block",
                "event_emission",
                "policy_gate",
                "manager_review",
            ],
        }

    def _list_runs(self, *, session_id: str | None, limit: int) -> list[dict[str, Any]]:
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

    def _events(
        self,
        *,
        run_id: str,
        session_id: str,
        request: AgenticPipelineRequest,
        blocks: list[dict[str, Any]],
        policy_scan: dict[str, Any],
        lifecycle_state: str,
        created_at: str,
    ) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = [
            _event(
                run_id,
                session_id,
                "pipeline_created",
                "NexusBrain",
                f"Created {request.pipeline_id} for {request.goal}",
                created_at,
            )
        ]
        for block in blocks:
            if block["status"] == "blocked-upstream-gate":
                events.append(
                    _event(
                        run_id,
                        session_id,
                        "upstream_aitune_gate_blocked",
                        block["role"],
                        f"Skipped {block['block_id']} because upstream AITune/QES runtime evidence is blocked.",
                        created_at,
                        block_id=block["block_id"],
                    )
                )
                continue
            events.append(
                _event(
                    run_id,
                    session_id,
                    "block_started",
                    block["role"],
                    f"Started {block['block_id']} with {block['context_mode']}",
                    created_at,
                    block_id=block["block_id"],
                )
            )
            events.append(
                _event(
                    run_id,
                    session_id,
                    "block_completed",
                    block["role"],
                    f"Completed {block['block_id']} as {block['status']}",
                    created_at,
                    block_id=block["block_id"],
                )
            )
        events.append(
            _event(
                run_id,
                session_id,
                "policy_scan_completed",
                "PolicyKernel",
                f"Policy scan allow_merge={policy_scan['summary']['allow_merge']}",
                created_at,
                metadata={"active_hard_fail_count": policy_scan["summary"]["active_hard_fail_count"]},
            )
        )
        events.append(
            _event(
                run_id,
                session_id,
                "pipeline_blocked" if lifecycle_state == "blocked_by_policy" else "pipeline_completed",
                "NexusBrain",
                lifecycle_state,
                created_at,
            )
        )
        return events


def _default_blocks() -> list[PipelineBlockSpec]:
    return [
        PipelineBlockSpec(block_id="research", role="researcher", expected_output="source-grounded brief"),
        PipelineBlockSpec(block_id="planner", role="planner", expected_output="implementation manifest"),
        PipelineBlockSpec(block_id="policy-gate", role="policy", expected_output="policy scan"),
        PipelineBlockSpec(block_id="manager-review", role="reviewer", expected_output="promotion decision"),
    ]


def _event(
    run_id: str,
    session_id: str,
    event_type: str,
    actor: str,
    detail: str,
    created_at: str,
    *,
    block_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "event_id": f"{run_id}::{event_type}::{len(detail)}::{block_id or 'run'}",
        "run_id": run_id,
        "session_id": session_id,
        "event_type": event_type,
        "actor": actor,
        "block_id": block_id,
        "detail": detail,
        "created_at": created_at,
        "metadata": metadata or {},
    }


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
        "run_manifest",
        "fresh_context_blocks",
        "artifact_ledger",
        "event_stream",
        "deterministic_gate_checks",
        "policy_scan_report",
        "manager_review",
        "worktree_branch_metadata",
    ]


def _operator_actions() -> dict[str, dict[str, Any]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/agentic-pipelines"},
        "create_run": {"method": "POST", "endpoint": "/ops/brain/agentic-pipelines/runs"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/agentic-pipelines"},
    }
