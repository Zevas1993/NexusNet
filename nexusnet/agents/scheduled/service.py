from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file
from .history import ScheduledHistoryService


class ScheduledAgentService:
    def __init__(self, *, config_dir: Path, runtime_configs: dict[str, Any], store: Any, artifacts_dir: Path, execution_store: Any | None = None):
        repo_default = Path(__file__).resolve().parents[3] / "runtime" / "config" / "openjarvis_lane.yaml"
        self.config = runtime_configs.get("openjarvis_lane") or load_yaml_file(
            config_dir / "openjarvis_lane.yaml",
            load_yaml_file(repo_default, {}),
        )
        self.store = store
        self.history = ScheduledHistoryService(artifacts_dir=artifacts_dir, execution_store=execution_store)

    def summary(self) -> dict[str, Any]:
        workflows = list((self.config.get("scheduled_agents") or []))
        traces = self.store.list_traces(limit=100)
        scheduled_traces = [
            trace
            for trace in traces
            if trace.get("wrapper_mode") == "scheduled-monitor"
            or trace.get("selected_agent") == "monitor-operative-agent"
        ]
        history = self.history.summary(workflows=workflows, traces=traces)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "workflow_count": len(workflows),
            "workflows": workflows,
            "recent_scheduled_trace_count": len(scheduled_traces),
            "history": history,
            "governance": {
                "memory_required": True,
                "traceability_required": True,
                "promotion_bypass_allowed": False,
            },
        }

    def history_detail(self, artifact_id: str) -> dict[str, Any] | None:
        return self.history.detail(artifact_id)

    def record_execution(self, *, workflow_id: str, execution: dict[str, Any]) -> dict[str, Any] | None:
        workflow = next((item for item in (self.config.get("scheduled_agents") or []) if item.get("workflow_id") == workflow_id), None)
        if workflow is None:
            return None
        return self.history.record_execution(workflow=workflow, execution=execution)
