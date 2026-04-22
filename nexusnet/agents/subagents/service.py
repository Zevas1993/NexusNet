from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class SubagentExecutionService:
    def __init__(self, *, artifacts_dir: Path, runtime_configs: dict[str, Any]):
        self.artifacts_dir = artifacts_dir
        self.config = ((runtime_configs.get("goose_lane") or {}).get("subagents") or {})
        self._runs: list[dict[str, Any]] = []

    def execute(
        self,
        *,
        recipe_id: str | None = None,
        parent_task: str,
        workers: list[dict[str, Any]],
        mode: str = "sequential",
        trigger_source: str | None = None,
        inherited_tools: list[str] | None = None,
        inherited_extensions: list[str] | None = None,
        linked_trace_ids: list[str] | None = None,
        policy_path: list[dict[str, Any]] | None = None,
        approval_path: dict[str, Any] | None = None,
        gateway_resolution: dict[str, Any] | None = None,
        approval_fallback_chain: list[dict[str, Any]] | None = None,
        adversary_review_report_ids: list[str] | None = None,
        linked_report_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        inherited_tools = list(inherited_tools or [])
        inherited_extensions = list(inherited_extensions or [])
        run = {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "run_id": new_id("subagents"),
            "recipe_id": recipe_id,
            "parent_task": parent_task,
            "mode": mode,
            "trigger_source": trigger_source or f"subagent-plan:{mode}",
            "temporary_lifecycle": bool(self.config.get("temporary_lifecycle", True)),
            "governance_mutation_allowed": bool(self.config.get("governance_mutation_allowed", False)),
            "created_at": utcnow().isoformat(),
            "linked_trace_ids": list(linked_trace_ids or []),
            "policy_path": list(policy_path or []),
            "approval_path": approval_path or {},
            "gateway_resolution": gateway_resolution or {},
            "approval_fallback_chain": list(approval_fallback_chain or []),
            "adversary_review_report_ids": list(adversary_review_report_ids or []),
            "linked_report_ids": list(linked_report_ids or []),
            "workers": [],
        }
        for index, worker in enumerate(workers):
            requested_tools = list(worker.get("requested_tools") or [])
            requested_extensions = list(worker.get("requested_extensions") or [])
            allowed_tools = sorted(set(requested_tools).intersection(inherited_tools or requested_tools))
            allowed_extensions = sorted(set(requested_extensions).intersection(inherited_extensions or requested_extensions))
            run["workers"].append(
                {
                    "subagent_id": worker.get("subagent_id") or new_id("worker"),
                    "ordinal": index,
                    "task": worker.get("task"),
                    "requested_tools": requested_tools,
                    "allowed_tools": allowed_tools,
                    "requested_extensions": requested_extensions,
                    "allowed_extensions": allowed_extensions,
                    "requested_policy_set_ids": worker.get("requested_policy_set_ids", []),
                    "requested_bundle_families": worker.get("requested_bundle_families", []),
                    "tool_calls": worker.get("tool_calls", []),
                    "result_summary": worker.get("result_summary") or "bounded-worker-plan",
                }
            )
        artifact = self.artifacts_dir / "agents" / "subagents" / f"{run['run_id']}.json"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(json.dumps(run, indent=2), encoding="utf-8")
        run["artifact_path"] = str(artifact)
        self._runs.insert(0, run)
        self._runs = self._runs[:20]
        return run

    def summary(self) -> dict[str, Any]:
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "recent_run_count": len(self._runs),
            "latest_run": self._runs[0] if self._runs else None,
            "recent_runs": self._runs[:5],
            "max_parallel": int(self.config.get("max_parallel", 1)),
        }
