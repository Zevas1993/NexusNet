from __future__ import annotations

from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Any

from .artifacts import ScheduledArtifactStore
from .reports import build_scheduled_report


class ScheduledHistoryService:
    def __init__(self, *, artifacts_dir: Path, execution_store: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.store = ScheduledArtifactStore(artifacts_dir=artifacts_dir)
        self.execution_store = execution_store

    def capture(self, *, workflows: list[dict[str, Any]], traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        scheduled_traces = [
            trace
            for trace in traces
            if trace.get("wrapper_mode") == "scheduled-monitor"
            or trace.get("selected_agent") == "monitor-operative-agent"
        ]
        executions = self.execution_store.list_executions(limit=200) if self.execution_store is not None else []
        for workflow in workflows:
            related_executions = self._matching_executions(workflow=workflow, executions=executions)
            related_trace_ids = [
                trace_id
                for record in related_executions
                for trace_id in record.get("linked_trace_ids", [])
                if trace_id
            ]
            related_traces = [
                trace
                for trace in scheduled_traces
                if trace.get("trace_id") in set(related_trace_ids)
            ] or scheduled_traces
            last_execution = related_executions[0] if related_executions else None
            last_trace = related_traces[0] if related_traces else None
            last_run = (
                (last_execution or {}).get("ended_at")
                or (last_execution or {}).get("started_at")
                or (last_trace or {}).get("started_at")
                or (last_trace or {}).get("timestamp")
            )
            next_run = self._next_run(last_run=last_run, cadence=str(workflow.get("cadence", "")))
            recent_statuses = [
                *(record.get("status") for record in related_executions if record.get("status")),
                *(trace.get("status") for trace in related_traces if trace.get("status")),
            ]
            linked_report_ids = sorted(
                {
                    report_id
                    for record in related_executions
                    for report_id in record.get("linked_report_ids", [])
                    if report_id
                }
            )
            linked_execution_ids = [record.get("execution_id") for record in related_executions if record.get("execution_id")]
            gateway_resolution_ids = sorted(
                {
                    step.get("resolution_id")
                    for record in related_executions
                    for step in record.get("gateway_decision_path", [])
                    if step.get("resolution_id")
                }
            )
            adversary_review_report_ids = sorted(
                {
                    report_id
                    for record in related_executions
                    for report_id in record.get("adversary_review_report_ids", [])
                    if report_id
                }
            )
            payload = {
                "artifact_kind": "scheduled-snapshot",
                "schedule_id": workflow.get("workflow_id"),
                "source_report_id": (((last_execution or {}).get("report") or {}).get("report_id")),
                "last_run": last_run,
                "next_run": next_run,
                "last_status": (last_execution or {}).get("status") or (last_trace or {}).get("status"),
                "success_failure_trend": self._trend(recent_statuses),
                "output_artifact_refs": sorted(
                    {
                        artifact
                        for record in related_executions
                        for artifact in record.get("artifacts_produced", [])
                        if artifact
                    }
                ),
                "escalation_path": self._escalation_path(workflow=workflow, executions=related_executions),
                "retry_path": (
                    "safe-fallback-retry"
                    if any((trace.get("metrics") or {}).get("fallback_used") for trace in related_traces[:5])
                    or any(record.get("status") != "success" for record in related_executions[:5])
                    else "stable"
                ),
                "linked_trace_ids": sorted(
                    {
                        *(trace.get("trace_id") for trace in related_traces[:5] if trace.get("trace_id")),
                        *related_trace_ids,
                    }
                ),
                "linked_report_ids": linked_report_ids,
                "linked_execution_ids": linked_execution_ids,
                "gateway_resolution_ids": gateway_resolution_ids,
                "adversary_review_report_ids": adversary_review_report_ids,
            }
            snapshot_signature = json.dumps(
                {
                    "workflow_id": workflow.get("workflow_id"),
                    "last_run": payload["last_run"],
                    "next_run": payload["next_run"],
                    "last_status": payload["last_status"],
                    "success_failure_trend": payload["success_failure_trend"],
                    "output_artifact_refs": payload["output_artifact_refs"],
                    "linked_trace_ids": payload["linked_trace_ids"],
                    "linked_report_ids": payload["linked_report_ids"],
                    "linked_execution_ids": payload["linked_execution_ids"],
                    "gateway_resolution_ids": payload["gateway_resolution_ids"],
                    "adversary_review_report_ids": payload["adversary_review_report_ids"],
                    "retry_path": payload["retry_path"],
                    "escalation_path": payload["escalation_path"],
                },
                sort_keys=True,
            )
            latest = self.store.latest_for(str(workflow.get("workflow_id")))
            if (
                latest
                and last_execution
                and latest.get("artifact_kind") == "scheduled-execution"
                and latest.get("source_execution_id") == last_execution.get("execution_id")
            ):
                records.append(latest)
                continue
            if latest and latest.get("snapshot_signature") == snapshot_signature:
                records.append(latest)
                continue
            payload["snapshot_signature"] = snapshot_signature
            record = self.store.record(workflow=workflow, payload=payload)
            report = build_scheduled_report(artifacts_dir=self.artifacts_dir, record=record)
            record["report"] = report
            record["output_artifact_refs"] = sorted(set([*record.get("output_artifact_refs", []), report["payload_path"], report["markdown_path"]]))
            Path(record["artifact_path"]).write_text(json.dumps(record, indent=2), encoding="utf-8")
            records.append(record)
        return records

    def record_execution(self, *, workflow: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
        last_run = execution.get("ended_at") or execution.get("started_at")
        existing = self.store.list(workflow_id=str(workflow.get("workflow_id")), limit=20)
        recent_statuses = [execution.get("status")] + [item.get("last_status") for item in existing if item.get("last_status")]
        payload = {
            "artifact_kind": "scheduled-execution",
            "schedule_id": workflow.get("workflow_id"),
            "source_execution_id": execution.get("execution_id"),
            "source_execution_kind": execution.get("execution_kind"),
            "source_report_id": (((execution.get("report") or {}).get("report_id"))),
            "trigger_source": execution.get("trigger_source"),
            "last_run": last_run,
            "next_run": self._next_run(last_run=last_run, cadence=str(workflow.get("cadence", ""))),
            "last_status": execution.get("status"),
            "success_failure_trend": self._trend(recent_statuses),
            "output_artifact_refs": sorted(set(execution.get("artifacts_produced", []))),
            "escalation_path": self._escalation_path(workflow=workflow, executions=[execution]),
            "retry_path": (
                "safe-fallback-retry"
                if execution.get("status") != "success" or bool(execution.get("approval_fallback_chain"))
                else "stable"
            ),
            "linked_trace_ids": list(execution.get("linked_trace_ids", [])),
            "linked_report_ids": list(execution.get("linked_report_ids", [])),
            "linked_execution_ids": [execution.get("execution_id")] if execution.get("execution_id") else [],
            "gateway_resolution_ids": [
                step.get("resolution_id")
                for step in execution.get("gateway_decision_path", [])
                if step.get("resolution_id")
            ],
            "adversary_review_report_ids": list(execution.get("adversary_review_report_ids", [])),
        }
        payload["snapshot_signature"] = json.dumps(
            {
                "workflow_id": workflow.get("workflow_id"),
                "execution_id": execution.get("execution_id"),
                "trigger_source": execution.get("trigger_source"),
                "status": execution.get("status"),
                "linked_trace_ids": execution.get("linked_trace_ids", []),
                "linked_report_ids": execution.get("linked_report_ids", []),
            },
            sort_keys=True,
        )
        record = self.store.record(workflow=workflow, payload=payload)
        report = build_scheduled_report(artifacts_dir=self.artifacts_dir, record=record)
        record["report"] = report
        record["output_artifact_refs"] = sorted(set([*record.get("output_artifact_refs", []), report["payload_path"], report["markdown_path"]]))
        record["linked_report_ids"] = sorted(set([*record.get("linked_report_ids", []), report["report_id"]]))
        Path(record["artifact_path"]).write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record

    def summary(self, *, workflows: list[dict[str, Any]], traces: list[dict[str, Any]], limit: int = 10) -> dict[str, Any]:
        captured = self.capture(workflows=workflows, traces=traces)
        items = self.store.list(limit=limit)
        latest_artifacts_by_workflow = {
            str(workflow.get("workflow_id")): self.store.latest_for(str(workflow.get("workflow_id")))
            for workflow in workflows
            if workflow.get("workflow_id")
        }
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "workflow_count": len(workflows),
            "history_count": len(items),
            "latest_artifact": items[0] if items else None,
            "latest_report_id": ((((items[0] if items else {}) or {}).get("report") or {}).get("report_id")),
            "latest_linked_trace_ids": ((items[0] if items else {}) or {}).get("linked_trace_ids", []),
            "latest_linked_report_ids": ((items[0] if items else {}) or {}).get("linked_report_ids", []),
            "latest_artifacts_by_workflow": latest_artifacts_by_workflow,
            "captured_this_summary": [item.get("artifact_id") for item in captured],
            "items": items,
        }

    def detail(self, artifact_id: str) -> dict[str, Any] | None:
        for item in self.store.list(limit=200):
            if item.get("artifact_id") != artifact_id:
                continue
            report = item.get("report") or {}
            payload = None
            markdown = None
            if report.get("payload_path"):
                try:
                    payload = json.loads(Path(report["payload_path"]).read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    payload = None
            if report.get("markdown_path"):
                try:
                    markdown = Path(report["markdown_path"]).read_text(encoding="utf-8")
                except OSError:
                    markdown = None
            return {
                "status_label": "STRONG ACCEPTED DIRECTION",
                "item": item,
                "report_payload": payload,
                "report_markdown": markdown,
            }
        return None

    def _next_run(self, *, last_run: str | None, cadence: str) -> str | None:
        if not last_run:
            return None
        try:
            anchor = datetime.fromisoformat(str(last_run).replace("Z", "+00:00"))
        except ValueError:
            return None
        cadence = cadence.lower()
        if cadence.startswith("every-") and cadence.endswith("m"):
            minutes = int(cadence.removeprefix("every-").removesuffix("m"))
            return (anchor + timedelta(minutes=minutes)).isoformat()
        if cadence == "daily":
            return (anchor + timedelta(days=1)).isoformat()
        return None

    def _trend(self, statuses: list[str | None]) -> str:
        normalized = [status for status in statuses if status]
        if not normalized:
            return "no-history"
        failures = sum(1 for status in normalized[:10] if status in {"warning", "error", "failed", "failure"})
        if failures >= 3:
            return "degraded"
        if failures >= 1:
            return "mixed"
        return "stable"

    def _matching_executions(self, *, workflow: dict[str, Any], executions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        workflow_id = str(workflow.get("workflow_id") or "")
        trigger_aliases = {f"schedule:{workflow_id}", f"scheduled:{workflow_id}"}
        return [
            record
            for record in executions
            if record.get("schedule_id") == workflow_id or record.get("trigger_source") in trigger_aliases
        ]

    def _escalation_path(self, *, workflow: dict[str, Any], executions: list[dict[str, Any]]) -> str:
        if any(record.get("adversary_review_report_ids") for record in executions):
            return "SafetyAO/CritiqueAO/manual-review"
        approval_decisions = {((record.get("approval_path") or {}).get("decision")) for record in executions}
        if "ask" in approval_decisions or workflow.get("approval_policy") == "ask":
            return "approval-gate"
        if "allow-if-approved" in approval_decisions:
            return "allow-if-approved"
        return "none"
