from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _policy_slug(*parts: str) -> str:
    return "_".join(
        "".join(ch if ch.isalnum() else "_" for ch in str(part or "").lower()).strip("_")
        for part in parts
        if str(part or "").strip()
    )


def build_policy_lifecycle_report(*, artifacts_dir: Path, record: dict[str, Any]) -> dict[str, Any]:
    slug = _policy_slug(record.get("policy_set_id"), record.get("version"))
    report_id = f"policyreport_{slug}"
    report_dir = Path(artifacts_dir) / "extensions" / "policy_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    payload_path = report_dir / f"{report_id}.json"
    markdown_path = report_dir / f"{report_id}.md"
    human_summary = (
        f"Policy set `{record.get('policy_set_id')}` v`{record.get('version')}` is "
        f"`{record.get('status')}` for bundle family `{record.get('bundle_family')}` "
        f"with rollback reference `{record.get('rollback_reference') or 'none'}`."
    )
    payload = {
        "report_id": report_id,
        "artifact_id": record.get("artifact_id"),
        "policy_set_id": record.get("policy_set_id"),
        "version": record.get("version"),
        "bundle_family": record.get("bundle_family"),
        "status": record.get("status"),
        "created_from": record.get("created_from"),
        "supersedes": record.get("supersedes", []),
        "rollback_reference": record.get("rollback_reference"),
        "lineage_anchor_id": record.get("lineage_anchor_id"),
        "stable_policy_version_id": record.get("stable_policy_version_id"),
        "author": record.get("author"),
        "origin": record.get("origin"),
        "risk_flags": record.get("risk_flags", []),
        "effective_scope": record.get("effective_scope", {}),
        "created_at": record.get("created_at"),
        "activated_at": record.get("activated_at"),
        "retired_at": record.get("retired_at"),
        "linked_evidence_ids": record.get("linked_evidence_ids", []),
        "linked_report_ids": record.get("linked_report_ids", []),
        "status_history": record.get("status_history", []),
        "human_summary": human_summary,
    }
    markdown = "\n".join(
        [
            f"# Policy Lifecycle Report {report_id}",
            "",
            "## Lifecycle State",
            f"- Policy set: `{record.get('policy_set_id')}`",
            f"- Version: `{record.get('version')}`",
            f"- Bundle family: `{record.get('bundle_family')}`",
            f"- Status: `{record.get('status')}`",
            f"- Created from: `{record.get('created_from') or 'none'}`",
            f"- Supersedes: {', '.join(record.get('supersedes', [])) or 'none'}",
            f"- Rollback reference: `{record.get('rollback_reference') or 'none'}`",
            f"- Lineage anchor: `{record.get('lineage_anchor_id') or 'none'}`",
            f"- Stable version ID: `{record.get('stable_policy_version_id') or 'none'}`",
            "",
            "## Governance And Timing",
            f"- Author: `{record.get('author') or 'unknown'}`",
            f"- Origin: `{record.get('origin') or 'unknown'}`",
            f"- Risk flags: {', '.join(record.get('risk_flags', [])) or 'none'}",
            f"- Created at: `{record.get('created_at') or 'unknown'}`",
            f"- Activated at: `{record.get('activated_at') or 'none'}`",
            f"- Retired at: `{record.get('retired_at') or 'none'}`",
            "",
            "## Evidence And Reports",
            f"- Linked evidence IDs: {', '.join(record.get('linked_evidence_ids', [])) or 'none'}",
            f"- Linked report IDs: {', '.join(record.get('linked_report_ids', [])) or 'none'}",
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


def build_policy_compare_report(
    *,
    artifacts_dir: Path,
    left: dict[str, Any],
    right: dict[str, Any],
    diff: dict[str, Any],
) -> dict[str, Any]:
    report_id = f"policycompare_{_policy_slug(left.get('policy_set_id'), left.get('version'), right.get('policy_set_id'), right.get('version'))}"
    report_dir = Path(artifacts_dir) / "extensions" / "policy_compare_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    payload_path = report_dir / f"{report_id}.json"
    markdown_path = report_dir / f"{report_id}.md"
    human_summary = (
        f"Policy compare `{left.get('policy_set_id')}@{left.get('version')}` vs "
        f"`{right.get('policy_set_id')}@{right.get('version')}` highlights status "
        f"change `{left.get('status')}` -> `{right.get('status')}` and "
        f"{len(diff.get('risk_flags_added', [])) + len(diff.get('risk_flags_removed', []))} risk-flag deltas."
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
            f"# Policy Compare Report {report_id}",
            "",
            "## Lifecycle Delta",
            f"- Left: `{left.get('policy_set_id')}@{left.get('version')}`",
            f"- Right: `{right.get('policy_set_id')}@{right.get('version')}`",
            f"- Status change: `{left.get('status')}` -> `{right.get('status')}`",
            f"- Bundle family change: `{left.get('bundle_family')}` -> `{right.get('bundle_family')}`",
            f"- Rollback reference changed: `{bool(diff.get('rollback_reference_changed'))}`",
            f"- Lineage depth: `{diff.get('lineage_depth_left', 0)}` -> `{diff.get('lineage_depth_right', 0)}`",
            "",
            "## Risk And Evidence Delta",
            f"- Risk flags added: {', '.join(diff.get('risk_flags_added', [])) or 'none'}",
            f"- Risk flags removed: {', '.join(diff.get('risk_flags_removed', [])) or 'none'}",
            f"- Reports added: {', '.join(diff.get('linked_report_ids_added', [])) or 'none'}",
            f"- Reports removed: {', '.join(diff.get('linked_report_ids_removed', [])) or 'none'}",
            f"- Evidence added: {', '.join(diff.get('linked_evidence_ids_added', [])) or 'none'}",
            f"- Evidence removed: {', '.join(diff.get('linked_evidence_ids_removed', [])) or 'none'}",
            "",
            "## Transition Context",
            f"- Latest transition left: `{((diff.get('latest_status_transition_left') or {}).get('status')) or 'none'}`",
            f"- Latest transition right: `{((diff.get('latest_status_transition_right') or {}).get('status')) or 'none'}`",
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
