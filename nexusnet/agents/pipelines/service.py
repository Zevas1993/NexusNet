from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
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
        self._lock = RLock()

    def start(self, request: AgenticPipelineRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, AgenticPipelineRequest) else AgenticPipelineRequest.model_validate(request)
        created_at = utcnow().isoformat()
        run_id = new_id("agentic_pipeline")
        blocks = list(normalized.blocks or _default_blocks())
        dependency_graph = _dependency_graph(blocks)
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
            else (
                "blocked_by_policy"
                if policy_blocked
                else ("blocked_by_invalid_dependencies" if dependency_graph["invalid"] else "completed")
            )
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
                    else (
                        "blocked"
                        if policy_blocked and block.role == "policy"
                        else (
                            "blocked-invalid-dependency"
                            if any(item["block_id"] == block.block_id for item in dependency_graph["unknown_dependency_refs"])
                            else ("blocked-dependency-graph" if dependency_graph["invalid"] else "completed")
                        )
                    )
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
            "dependency_graph": dependency_graph,
            "events": events,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "upstream_aitune_gate": upstream_aitune_gate,
            "artifact_path": str(artifact_path),
            "metadata": normalized.metadata,
        }
        artifact_path.write_text(json.dumps(run, indent=2), encoding="utf-8")
        return run

    def start_scheduled(self, request: AgenticPipelineRequest | dict[str, Any]) -> dict[str, Any]:
        run = self.start(request)
        if run["lifecycle_state"] != "completed":
            return run
        for block in run["blocks"]:
            block["status"] = "waiting-dependencies" if block["dependencies"] else "ready"
            block["output_ref"] = None
        run["lifecycle_state"] = "scheduled"
        run["runtime_state"] = "live-bound"
        run["scheduler"] = {
            "state": "live",
            "ready_block_ids": sorted(
                block["block_id"] for block in run["blocks"] if block["status"] == "ready"
            ),
            "claimed_block_ids": [],
            "completed_block_ids": [],
        }
        run["events"] = [
            event
            for event in run.get("events") or []
            if event.get("event_type")
            not in {"block_started", "block_completed", "pipeline_completed"}
        ]
        run["events"].append(
            {
                "event_id": new_id("agentic_pipeline_event"),
                "event_type": "dependency_schedule_created",
                "run_id": run["run_id"],
                "created_at": utcnow().isoformat(),
                "ready_block_ids": run["scheduler"]["ready_block_ids"],
            }
        )
        self._write_run(run)
        return run

    def claim_ready_blocks(self, run_id: str, *, max_count: int = 1) -> dict[str, Any]:
        if max_count < 1 or max_count > 16:
            raise ValueError("max_count must be between 1 and 16")
        with self._lock:
            run = self._load_run(run_id)
            if run.get("lifecycle_state") not in {"scheduled", "running"}:
                raise PermissionError("pipeline run is not eligible for dependency scheduling")
            ready = sorted(
                (block for block in run["blocks"] if block.get("status") == "ready"),
                key=lambda block: block["block_id"],
            )[:max_count]
            claimed_at = utcnow().isoformat()
            for block in ready:
                block["status"] = "running"
                block["claimed_at"] = claimed_at
            if ready:
                run["lifecycle_state"] = "running"
                run["scheduler"]["claimed_block_ids"] = sorted(
                    block["block_id"] for block in run["blocks"] if block.get("status") == "running"
                )
                run["scheduler"]["ready_block_ids"] = sorted(
                    block["block_id"] for block in run["blocks"] if block.get("status") == "ready"
                )
                run["events"].append(
                    {
                        "event_id": new_id("agentic_pipeline_event"),
                        "event_type": "dependency_ready_blocks_claimed",
                        "run_id": run_id,
                        "created_at": claimed_at,
                        "block_ids": [block["block_id"] for block in ready],
                    }
                )
                self._write_run(run)
            return {**run, "claimed_blocks": ready}

    def complete_block(
        self,
        run_id: str,
        *,
        block_id: str,
        output_ref: str,
        succeeded: bool = True,
    ) -> dict[str, Any]:
        if succeeded and not output_ref.strip():
            raise ValueError("successful block completion requires output_ref")
        with self._lock:
            run = self._load_run(run_id)
            block = next((item for item in run["blocks"] if item["block_id"] == block_id), None)
            if block is None:
                raise KeyError(f"unknown pipeline block: {block_id}")
            if block.get("status") != "running":
                raise PermissionError(f"pipeline block must be running before completion: {block_id}")

            completed_at = utcnow().isoformat()
            block["status"] = "completed" if succeeded else "failed"
            block["output_ref"] = output_ref if succeeded else None
            block["completed_at"] = completed_at
            newly_ready: list[str] = []
            if succeeded:
                statuses = {item["block_id"]: item["status"] for item in run["blocks"]}
                for candidate in run["blocks"]:
                    if candidate.get("status") != "waiting-dependencies":
                        continue
                    if all(statuses.get(dependency) == "completed" for dependency in candidate["dependencies"]):
                        candidate["status"] = "ready"
                        newly_ready.append(candidate["block_id"])
            run["lifecycle_state"] = (
                "blocked_block_failure"
                if not succeeded
                else (
                    "completed"
                    if all(item.get("status") == "completed" for item in run["blocks"])
                    else "running"
                )
            )
            run["runtime_state"] = "degraded" if not succeeded else "live-bound"
            run["scheduler"]["state"] = "completed" if run["lifecycle_state"] == "completed" else run["lifecycle_state"]
            run["scheduler"]["ready_block_ids"] = sorted(
                item["block_id"] for item in run["blocks"] if item.get("status") == "ready"
            )
            run["scheduler"]["claimed_block_ids"] = sorted(
                item["block_id"] for item in run["blocks"] if item.get("status") == "running"
            )
            run["scheduler"]["completed_block_ids"] = sorted(
                item["block_id"] for item in run["blocks"] if item.get("status") == "completed"
            )
            run["events"].append(
                {
                    "event_id": new_id("agentic_pipeline_event"),
                    "event_type": "dependency_block_completed" if succeeded else "dependency_block_failed",
                    "run_id": run_id,
                    "created_at": completed_at,
                    "block_id": block_id,
                    "output_ref": output_ref if succeeded else None,
                    "newly_ready_block_ids": sorted(newly_ready),
                }
            )
            self._write_run(run)
            return {**run, "newly_ready_block_ids": sorted(newly_ready)}

    def _load_run(self, run_id: str) -> dict[str, Any]:
        path = self.runs_dir / f"{run_id}.json"
        if not path.exists():
            raise KeyError(f"unknown agentic pipeline run: {run_id}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_run(self, run: dict[str, Any]) -> None:
        path = self.runs_dir / f"{run['run_id']}.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(run, indent=2), encoding="utf-8")
        temporary.replace(path)

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
            if block["status"].startswith("blocked-"):
                events.append(
                    _event(
                        run_id,
                        session_id,
                        "block_blocked",
                        block["role"],
                        f"Blocked {block['block_id']} as {block['status']}",
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
                "pipeline_blocked" if lifecycle_state.startswith("blocked") else "pipeline_completed",
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


def _dependency_graph(blocks: list[PipelineBlockSpec]) -> dict[str, Any]:
    block_ids = [block.block_id for block in blocks]
    known_ids = set(block_ids)
    dependencies_by_block = {
        block.block_id: sorted(dependency_id for dependency_id in block.dependencies if dependency_id in known_ids)
        for block in blocks
    }
    unknown_dependency_refs = [
        {"block_id": block.block_id, "dependency_id": dependency_id}
        for block in blocks
        for dependency_id in block.dependencies
        if dependency_id not in known_ids
    ]
    duplicate_block_ids = sorted({block_id for block_id in block_ids if block_ids.count(block_id) > 1})
    cycle_block_ids = _cyclic_block_ids(dependencies_by_block)
    reverse_edges = {block_id: [] for block_id in sorted(known_ids)}
    for block_id, dependencies in dependencies_by_block.items():
        for dependency_id in dependencies:
            reverse_edges[dependency_id].append(block_id)
    reverse_edges = {block_id: sorted(dependents) for block_id, dependents in reverse_edges.items()}
    return {
        "nodes": block_ids,
        "edges": [
            {"from_block_id": dependency_id, "to_block_id": block.block_id}
            for block in blocks
            for dependency_id in block.dependencies
            if dependency_id in known_ids
        ],
        "unknown_dependency_refs": unknown_dependency_refs,
        "duplicate_block_ids": duplicate_block_ids,
        "cycle_block_ids": cycle_block_ids,
        "blocks": reverse_edges,
        "blocked_by": {block_id: dependencies_by_block.get(block_id, []) for block_id in sorted(known_ids)},
        "parallel_ready_block_ids": sorted(
            block_id for block_id, dependencies in dependencies_by_block.items() if not dependencies
        ),
        "topological_order": _topological_order(dependencies_by_block, reverse_edges),
        "invalid": bool(unknown_dependency_refs or duplicate_block_ids or cycle_block_ids),
    }


def _cyclic_block_ids(dependencies_by_block: dict[str, list[str]]) -> list[str]:
    visited: set[str] = set()
    visiting: list[str] = []
    cycle_ids: set[str] = set()

    def visit(block_id: str) -> None:
        if block_id in visiting:
            cycle_ids.update(visiting[visiting.index(block_id) :])
            return
        if block_id in visited:
            return
        visiting.append(block_id)
        for dependency_id in dependencies_by_block.get(block_id, []):
            visit(dependency_id)
        visiting.pop()
        visited.add(block_id)

    for block_id in dependencies_by_block:
        visit(block_id)
    return sorted(cycle_ids)


def _topological_order(
    dependencies_by_block: dict[str, list[str]],
    reverse_edges: dict[str, list[str]],
) -> list[str]:
    remaining = {block_id: len(dependencies) for block_id, dependencies in dependencies_by_block.items()}
    ready = sorted(block_id for block_id, count in remaining.items() if count == 0)
    ordered: list[str] = []
    while ready:
        block_id = ready.pop(0)
        ordered.append(block_id)
        for dependent in reverse_edges.get(block_id, []):
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                ready.append(dependent)
                ready.sort()
    return ordered


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
        "create_scheduled_run": {
            "method": "POST",
            "endpoint": "/ops/brain/agentic-pipelines/scheduled-runs",
        },
        "claim_ready": {
            "method": "POST",
            "endpoint": "/ops/brain/agentic-pipelines/runs/{run_id}/claim-ready",
        },
        "complete_block": {
            "method": "POST",
            "endpoint": "/ops/brain/agentic-pipelines/runs/{run_id}/blocks/{block_id}/complete",
        },
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/agentic-pipelines"},
    }
