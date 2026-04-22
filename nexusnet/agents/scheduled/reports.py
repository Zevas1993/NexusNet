from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id


def build_scheduled_report(*, artifacts_dir: Path, record: dict[str, Any]) -> dict[str, Any]:
    report_id = new_id("schedreport")
    report_dir = Path(artifacts_dir) / "scheduled" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    payload_path = report_dir / f"{report_id}.json"
    markdown_path = report_dir / f"{report_id}.md"
    human_summary = (
        f"Scheduled workflow `{record.get('workflow_id')}` "
        f"last ran at {record.get('last_run')} and reports trend "
        f"{record.get('success_failure_trend', 'unknown')}."
    )
    payload = {
        "report_id": report_id,
        "artifact_id": record.get("artifact_id"),
        "workflow_id": record.get("workflow_id"),
        "human_summary": human_summary,
        "artifact_kind": record.get("artifact_kind", "scheduled-snapshot"),
        "source_report_id": record.get("source_report_id"),
        "last_run": record.get("last_run"),
        "next_run": record.get("next_run"),
        "last_status": record.get("last_status"),
        "success_failure_trend": record.get("success_failure_trend"),
        "output_artifact_refs": record.get("output_artifact_refs", []),
        "linked_trace_ids": record.get("linked_trace_ids", []),
        "linked_report_ids": record.get("linked_report_ids", []),
        "linked_execution_ids": record.get("linked_execution_ids", []),
        "gateway_resolution_ids": record.get("gateway_resolution_ids", []),
        "adversary_review_report_ids": record.get("adversary_review_report_ids", []),
    }
    markdown = "\n".join(
        [
            f"# Scheduled Workflow Report {report_id}",
            "",
            f"- Workflow: `{record.get('workflow_id')}`",
            f"- Artifact kind: `{record.get('artifact_kind', 'scheduled-snapshot')}`",
            f"- Source report: `{record.get('source_report_id') or 'none'}`",
            f"- Last run: `{record.get('last_run')}`",
            f"- Next run: `{record.get('next_run')}`",
            f"- Last status: `{record.get('last_status') or 'unknown'}`",
            f"- Trend: `{record.get('success_failure_trend')}`",
            f"- Escalation path: {record.get('escalation_path') or 'none'}",
            f"- Retry path: {record.get('retry_path') or 'none'}",
            f"- Linked traces: {', '.join(record.get('linked_trace_ids', [])) or 'none'}",
            f"- Linked reports: {', '.join(record.get('linked_report_ids', [])) or 'none'}",
            f"- Linked executions: {', '.join(record.get('linked_execution_ids', [])) or 'none'}",
            "",
            "## Human Summary",
            human_summary,
        ]
    )
    payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    return {
        "report_id": report_id,
        "human_summary": human_summary,
        "payload_path": str(payload_path),
        "markdown_path": str(markdown_path),
    }
