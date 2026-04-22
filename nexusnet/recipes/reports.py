from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id


def build_recipe_execution_report(*, artifacts_dir: Path, record: dict[str, Any]) -> dict[str, Any]:
    report_id = new_id("recipereport")
    report_dir = Path(artifacts_dir) / "recipes" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    payload_path = report_dir / f"{report_id}.json"
    markdown_path = report_dir / f"{report_id}.md"
    execution_kind = record.get("execution_kind")
    if execution_kind == "gateway":
        human_summary = (
            f"gateway flow `{record.get('recipe_id')}` via {record.get('trigger_source')} "
            f"finished as {record.get('status')} with "
            f"{len(record.get('extension_bundle_ids', []))} extension bundles, "
            f"{len(record.get('linked_trace_ids', []))} linked traces, and "
            f"{len(record.get('adversary_review_report_ids', []))} adversary review artifacts "
            f"across {', '.join(record.get('flow_families', [])) or 'uncategorized'} families."
        )
    else:
        human_summary = (
            f"{execution_kind} `{record.get('recipe_id')}` "
            f"via {record.get('trigger_source')} finished as {record.get('status')} "
            f"with {len(record.get('linked_subagent_ids', []))} subagents, "
            f"{len(record.get('artifacts_produced', []))} artifacts, and "
            f"{', '.join(record.get('flow_families', [])) or 'uncategorized'} flow families."
        )
    report_payload = {
        "report_id": report_id,
        "execution_id": record.get("execution_id"),
        "human_summary": human_summary,
        "status": record.get("status"),
        "recipe_id": record.get("recipe_id"),
        "execution_kind": record.get("execution_kind"),
        "schedule_id": record.get("schedule_id"),
        "flow_families": record.get("flow_families", []),
        "linked_trace_ids": record.get("linked_trace_ids", []),
        "linked_subagent_ids": record.get("linked_subagent_ids", []),
        "artifacts_produced": record.get("artifacts_produced", []),
        "policy_path_count": len(record.get("policy_path", [])),
        "approval_path": record.get("approval_path", {}),
        "gateway_decision_path": record.get("gateway_decision_path", []),
        "gateway_resolution_id": record.get("gateway_resolution_id"),
        "gateway_execution_id": record.get("gateway_execution_id"),
        "gateway_report_id": record.get("gateway_report_id"),
        "execution_path": record.get("execution_path", []),
        "approval_fallback_chain": record.get("approval_fallback_chain", []),
        "adversary_review_report_ids": record.get("adversary_review_report_ids", []),
        "linked_report_ids": record.get("linked_report_ids", []),
        "extension_bundle_ids": record.get("extension_bundle_ids", []),
        "extension_policy_set_ids": record.get("extension_policy_set_ids", []),
        "extension_bundle_families": record.get("extension_bundle_families", []),
        "extension_provenance": record.get("extension_provenance", []),
        "metadata": record.get("metadata", {}),
    }
    markdown = "\n".join(
        [
            f"# Recipe Execution Report {report_id}",
            "",
            f"- Recipe/Runbook: `{record.get('recipe_id')}`",
            f"- Kind: `{record.get('execution_kind')}`",
            f"- Trigger: `{record.get('trigger_source')}`",
            f"- Schedule: `{record.get('schedule_id') or 'none'}`",
            f"- Status: `{record.get('status')}`",
            f"- Flow families: {', '.join(record.get('flow_families', [])) or 'none'}",
            f"- AO Targets: {', '.join(record.get('ao_association', [])) or 'none'}",
            f"- Linked traces: {', '.join(record.get('linked_trace_ids', [])) or 'none'}",
            f"- Linked subagents: {', '.join(record.get('linked_subagent_ids', [])) or 'none'}",
            f"- Linked reports: {', '.join(record.get('linked_report_ids', [])) or 'none'}",
            f"- Gateway resolution: `{record.get('gateway_resolution_id') or 'none'}`",
            f"- Gateway execution: `{record.get('gateway_execution_id') or 'none'}`",
            f"- Gateway report: `{record.get('gateway_report_id') or 'none'}`",
            f"- Gateway decisions: {', '.join([step.get('resolution_id', 'unknown') for step in record.get('gateway_decision_path', [])]) or 'none'}",
            f"- Execution path stages: {', '.join([step.get('stage', 'unknown') for step in record.get('execution_path', [])]) or 'none'}",
            f"- Approval chain length: `{len(record.get('approval_fallback_chain', []))}`",
            f"- Adversary reports: {', '.join(record.get('adversary_review_report_ids', [])) or 'none'}",
            f"- Extension bundles: {', '.join(record.get('extension_bundle_ids', [])) or 'none'}",
            f"- Extension policy sets: {', '.join(record.get('extension_policy_set_ids', [])) or 'none'}",
            f"- Extension bundle families: {', '.join(record.get('extension_bundle_families', [])) or 'none'}",
            f"- Extension provenance artifacts: {', '.join([item.get('artifact_id', 'unknown') for item in record.get('extension_provenance', [])]) or 'none'}",
            f"- Artifacts: {', '.join(record.get('artifacts_produced', [])) or 'none'}",
            "",
            "## Human Summary",
            human_summary,
        ]
    )
    payload_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    return {
        "report_id": report_id,
        "human_summary": human_summary,
        "payload_path": str(payload_path),
        "markdown_path": str(markdown_path),
    }


def build_execution_compare_report(
    *,
    artifacts_dir: Path,
    left: dict[str, Any],
    right: dict[str, Any],
    diff: dict[str, Any],
) -> dict[str, Any]:
    report_id = (
        "execcompare_"
        f"{_slug(left.get('execution_id'))}_{_slug(right.get('execution_id'))}"
    )
    report_dir = Path(artifacts_dir) / "recipes" / "compare_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    payload_path = report_dir / f"{report_id}.json"
    markdown_path = report_dir / f"{report_id}.md"
    human_summary = (
        f"Execution compare `{left.get('execution_id')}` vs `{right.get('execution_id')}` "
        f"tracks `{left.get('status')}` -> `{right.get('status')}` across "
        f"{len(diff.get('flow_families_added', [])) + len(diff.get('flow_families_removed', []))} flow-family deltas."
    )
    payload = {
        "report_id": report_id,
        "left": left,
        "right": right,
        "diff": diff,
        "human_summary": human_summary,
    }
    markdown = "\n".join(
        [
            f"# Execution Compare Report {report_id}",
            "",
            "## Execution Delta",
            f"- Left execution: `{left.get('execution_id')}`",
            f"- Right execution: `{right.get('execution_id')}`",
            f"- Status change: `{left.get('status')}` -> `{right.get('status')}`",
            f"- Trigger change: `{left.get('trigger_source')}` -> `{right.get('trigger_source')}`",
            "",
            "## Flow And Policy Delta",
            f"- Flow families added: {', '.join(diff.get('flow_families_added', [])) or 'none'}",
            f"- Flow families removed: {', '.join(diff.get('flow_families_removed', [])) or 'none'}",
            f"- Policy sets added: {', '.join(diff.get('extension_policy_set_ids_added', [])) or 'none'}",
            f"- Policy sets removed: {', '.join(diff.get('extension_policy_set_ids_removed', [])) or 'none'}",
            f"- Bundle families added: {', '.join(diff.get('extension_bundle_families_added', [])) or 'none'}",
            f"- Bundle families removed: {', '.join(diff.get('extension_bundle_families_removed', [])) or 'none'}",
            "",
            "## Trace And Report Delta",
            f"- Linked trace IDs added: {', '.join(diff.get('linked_trace_ids_added', [])) or 'none'}",
            f"- Linked trace IDs removed: {', '.join(diff.get('linked_trace_ids_removed', [])) or 'none'}",
            f"- Linked report IDs added: {', '.join(diff.get('linked_report_ids_added', [])) or 'none'}",
            f"- Linked report IDs removed: {', '.join(diff.get('linked_report_ids_removed', [])) or 'none'}",
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


def _slug(value: Any) -> str:
    return "".join(ch if str(ch).isalnum() else "_" for ch in str(value or "unknown")).strip("_").lower()
