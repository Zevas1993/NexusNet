from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id


def build_extension_bundle_report(*, artifacts_dir: Path, record: dict[str, Any]) -> dict[str, Any]:
    report_id = new_id("extreport")
    report_dir = Path(artifacts_dir) / "extensions" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    payload_path = report_dir / f"{report_id}.json"
    markdown_path = report_dir / f"{report_id}.md"
    human_summary = (
        f"Extension bundle `{record.get('bundle_id')}` is "
        f"`{record.get('enabled_state')}` in workspace `{record.get('workspace_id')}` "
        f"with approval posture `{((record.get('approval_path') or {}).get('decision'))}` "
        f"under policy set `{record.get('policy_set_id')}` v`{record.get('policy_set_version')}`."
    )
    payload = {
        "report_id": report_id,
        "artifact_id": record.get("artifact_id"),
        "bundle_id": record.get("bundle_id"),
        "workspace_id": record.get("workspace_id"),
        "human_summary": human_summary,
        "policy_set_id": record.get("policy_set_id"),
        "policy_set_version": record.get("policy_set_version"),
        "bundle_family": record.get("bundle_family"),
        "enabled_state": record.get("enabled_state"),
        "workspace_scopes": record.get("workspace_scopes", []),
        "roots": record.get("roots", []),
        "allowed_tools": record.get("allowed_tools", []),
        "inherited_permissions": record.get("inherited_permissions", []),
        "risk_flags": record.get("risk_flags", []),
        "risk_flag_delta_from_previous": record.get("risk_flag_delta_from_previous", {}),
        "approval_path": record.get("approval_path", {}),
        "permission_mode": record.get("permission_mode"),
        "sandbox_posture": record.get("sandbox_posture"),
        "lineage_anchor_id": record.get("lineage_anchor_id"),
        "supersedes_artifact_id": record.get("supersedes_artifact_id"),
        "permission_delta_from_previous": record.get("permission_delta_from_previous", {}),
        "compatible_provider_ids": ((record.get("acp_compatibility") or {}).get("compatible_provider_ids", [])),
        "provider_count": ((record.get("acp_compatibility") or {}).get("provider_count")),
        "feature_missing": ((record.get("acp_compatibility") or {}).get("feature_missing", [])),
        "policy_status": (((record.get("policy_lifecycle") or {}).get("status"))),
        "policy_history_artifact_id": (((record.get("policy_lifecycle") or {}).get("artifact_id"))),
        "policy_history_report_id": ((((record.get("policy_lifecycle") or {}).get("report")) or {}).get("report_id")),
        "policy_lineage": (((record.get("policy_lifecycle") or {}).get("lineage")) or []),
        "policy_lineage_statuses": record.get("policy_lineage_statuses", []),
        "certification_status": record.get("certification_status"),
        "certification_artifact_id": record.get("certification_artifact_id"),
        "certification_report_id": record.get("certification_report_id"),
        "stable_certification_id": record.get("stable_certification_id"),
        "certification_lineage_depth": record.get("certification_lineage_depth", 0),
        "certification_lineage_statuses": record.get("certification_lineage_statuses", []),
        "historical_certification_artifact_ids": record.get("historical_certification_artifact_ids", []),
        "historical_certification_statuses": record.get("historical_certification_statuses", []),
        "restoration_detected": record.get("restoration_detected", False),
        "restored_from_policy_versions": record.get("restored_from_policy_versions", []),
        "restored_from_certification_artifact_ids": record.get("restored_from_certification_artifact_ids", []),
        "privilege_inheritance_confusion": record.get("privilege_inheritance_confusion", False),
        "adversary_review_report_ids": record.get("adversary_review_report_ids", []),
    }
    markdown = "\n".join(
        [
            f"# Extension Bundle Report {report_id}",
            "",
            "## Bundle State",
            f"- Bundle: `{record.get('bundle_id')}`",
            f"- Policy set: `{record.get('policy_set_id')}` v`{record.get('policy_set_version')}`",
            f"- Bundle family: `{record.get('bundle_family') or 'unknown'}`",
            f"- Workspace: `{record.get('workspace_id')}`",
            f"- Enabled state: `{record.get('enabled_state')}`",
            f"- Approval decision: `{((record.get('approval_path') or {}).get('decision'))}`",
            f"- Permission mode: `{record.get('permission_mode') or 'unknown'}`",
            f"- Sandbox posture: `{record.get('sandbox_posture') or 'unknown'}`",
            "",
            "## Scope And Permissions",
            f"- Workspace scopes: {', '.join(record.get('workspace_scopes', [])) or 'none'}",
            f"- Roots: {', '.join(record.get('roots', [])) or 'none'}",
            f"- Allowed tools: {', '.join(record.get('allowed_tools', [])) or 'none'}",
            f"- Inherited permissions: {', '.join(record.get('inherited_permissions', [])) or 'none'}",
            f"- Permission delta from previous: +{', '.join((record.get('permission_delta_from_previous') or {}).get('added', [])) or 'none'} / -{', '.join((record.get('permission_delta_from_previous') or {}).get('removed', [])) or 'none'}",
            "",
            "## Risk And ACP",
            f"- Risk flags: {', '.join(record.get('risk_flags', [])) or 'none'}",
            f"- Risk flag delta from previous: +{', '.join((record.get('risk_flag_delta_from_previous') or {}).get('added', [])) or 'none'} / -{', '.join((record.get('risk_flag_delta_from_previous') or {}).get('removed', [])) or 'none'}",
            f"- ACP compatible providers: {', '.join(((record.get('acp_compatibility') or {}).get('compatible_provider_ids', []))) or 'none'}",
            f"- ACP missing features: {', '.join(((record.get('acp_compatibility') or {}).get('feature_missing', []))) or 'none'}",
            f"- Privilege inheritance confusion: `{bool(record.get('privilege_inheritance_confusion', False))}`",
            f"- Adversary review reports: {', '.join(record.get('adversary_review_report_ids', [])) or 'none'}",
            "",
            "## Policy And Certification Lineage",
            f"- Policy lifecycle status: `{((record.get('policy_lifecycle') or {}).get('status')) or 'unknown'}`",
            f"- Policy history artifact: `{((record.get('policy_lifecycle') or {}).get('artifact_id')) or 'none'}`",
            f"- Policy lineage depth: `{len(((record.get('policy_lifecycle') or {}).get('lineage')) or [])}`",
            f"- Policy lineage statuses: {', '.join(record.get('policy_lineage_statuses', [])) or 'none'}",
            f"- Certification status: `{record.get('certification_status') or 'unknown'}`",
            f"- Certification artifact: `{record.get('certification_artifact_id') or 'none'}`",
            f"- Stable certification ID: `{record.get('stable_certification_id') or 'none'}`",
            f"- Certification lineage depth: `{record.get('certification_lineage_depth', 0)}`",
            f"- Certification lineage statuses: {', '.join(record.get('certification_lineage_statuses', [])) or 'none'}",
            f"- Historical certification artifacts: {', '.join(record.get('historical_certification_artifact_ids', [])) or 'none'}",
            f"- Historical certification statuses: {', '.join(record.get('historical_certification_statuses', [])) or 'none'}",
            f"- Restoration detected: `{bool(record.get('restoration_detected', False))}`",
            f"- Restored from policy versions: {', '.join(record.get('restored_from_policy_versions', [])) or 'none'}",
            f"- Restored from certification artifacts: {', '.join(record.get('restored_from_certification_artifact_ids', [])) or 'none'}",
            f"- Lineage anchor: `{record.get('lineage_anchor_id') or 'none'}`",
            f"- Supersedes artifact: `{record.get('supersedes_artifact_id') or 'none'}`",
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


def build_extension_bundle_certification_report(*, artifacts_dir: Path, record: dict[str, Any]) -> dict[str, Any]:
    report_id = new_id("extcertreport")
    report_dir = Path(artifacts_dir) / "extensions" / "certification_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    payload_path = report_dir / f"{report_id}.json"
    markdown_path = report_dir / f"{report_id}.md"
    human_summary = (
        f"Extension bundle `{record.get('bundle_id')}` certification is "
        f"`{record.get('certification_status')}` under policy set "
        f"`{record.get('policy_set_id')}` v`{record.get('policy_set_version')}`."
    )
    payload = {
        "report_id": report_id,
        "artifact_id": record.get("artifact_id"),
        "bundle_id": record.get("bundle_id"),
        "bundle_family": record.get("bundle_family"),
        "policy_set_id": record.get("policy_set_id"),
        "policy_set_version": record.get("policy_set_version"),
        "policy_status": record.get("policy_status"),
        "policy_history_artifact_id": record.get("policy_history_artifact_id"),
        "policy_history_report_id": record.get("policy_history_report_id"),
        "workspace_id": record.get("workspace_id"),
        "enabled_state": record.get("enabled_state"),
        "allowed_tools": record.get("allowed_tools", []),
        "inherited_permissions": record.get("inherited_permissions", []),
        "compatible_provider_ids": ((record.get("acp_compatibility") or {}).get("compatible_provider_ids", [])),
        "provider_count": ((record.get("acp_compatibility") or {}).get("provider_count")),
        "approval_path": record.get("approval_path", {}),
        "sandbox_posture": record.get("sandbox_posture"),
        "permission_mode": record.get("permission_mode"),
        "risk_flags": record.get("risk_flags", []),
        "risk_flag_delta_from_previous": record.get("risk_flag_delta_from_previous", {}),
        "permission_delta_from_previous": record.get("permission_delta_from_previous", {}),
        "adversary_review_report_ids": record.get("adversary_review_report_ids", []),
        "privilege_inheritance_confusion": record.get("privilege_inheritance_confusion", False),
        "recommended_remediation_actions": record.get("recommended_remediation_actions", []),
        "certification_status": record.get("certification_status"),
        "lineage_anchor_id": record.get("lineage_anchor_id"),
        "supersedes_artifact_id": record.get("supersedes_artifact_id"),
        "stable_certification_id": record.get("stable_certification_id"),
        "policy_lineage_statuses": record.get("policy_lineage_statuses", []),
        "restored_from_policy_versions": record.get("restored_from_policy_versions", []),
        "restored_from_certification_artifact_ids": record.get("restored_from_certification_artifact_ids", []),
        "restored_from_certification_statuses": record.get("restored_from_certification_statuses", []),
        "historical_certification_artifact_ids": record.get("historical_certification_artifact_ids", []),
        "historical_certification_statuses": record.get("historical_certification_statuses", []),
        "certification_lineage_depth": record.get("certification_lineage_depth", 0),
        "certification_lineage_statuses": record.get("certification_lineage_statuses", []),
        "historical_fixture_count": record.get("historical_fixture_count", 0),
        "latest_certification_transition": record.get("latest_certification_transition"),
        "restoration_detected": record.get("restoration_detected", False),
        "human_summary": human_summary,
    }
    markdown = "\n".join(
        [
            f"# Extension Certification Report {report_id}",
            "",
            "## Current Certification State",
            f"- Bundle: `{record.get('bundle_id')}`",
            f"- Family: `{record.get('bundle_family')}`",
            f"- Policy set: `{record.get('policy_set_id')}` v`{record.get('policy_set_version')}`",
            f"- Policy lifecycle status: `{record.get('policy_status') or 'unknown'}`",
            f"- Certification status: `{record.get('certification_status')}`",
            f"- Enabled state: `{record.get('enabled_state')}`",
            f"- Approval decision: `{((record.get('approval_path') or {}).get('decision'))}`",
            f"- Permission mode: `{record.get('permission_mode') or 'unknown'}`",
            f"- Sandbox posture: `{record.get('sandbox_posture') or 'unknown'}`",
            "",
            "## Permissions And Risk",
            f"- Allowed tools: {', '.join(record.get('allowed_tools', [])) or 'none'}",
            f"- Inherited permissions: {', '.join(record.get('inherited_permissions', [])) or 'none'}",
            f"- ACP compatible providers: {', '.join(((record.get('acp_compatibility') or {}).get('compatible_provider_ids', []))) or 'none'}",
            f"- Risk flags: {', '.join(record.get('risk_flags', [])) or 'none'}",
            f"- Risk flag delta from previous: +{', '.join((record.get('risk_flag_delta_from_previous') or {}).get('added', [])) or 'none'} / -{', '.join((record.get('risk_flag_delta_from_previous') or {}).get('removed', [])) or 'none'}",
            f"- Privilege inheritance confusion: `{bool(record.get('privilege_inheritance_confusion', False))}`",
            f"- Adversary review reports: {', '.join(record.get('adversary_review_report_ids', [])) or 'none'}",
            f"- Recommended actions: {', '.join(record.get('recommended_remediation_actions', [])) or 'none'}",
            "",
            "## Certification Lineage",
            f"- Lineage anchor: `{record.get('lineage_anchor_id') or 'none'}`",
            f"- Supersedes artifact: `{record.get('supersedes_artifact_id') or 'none'}`",
            f"- Stable certification ID: `{record.get('stable_certification_id') or 'none'}`",
            f"- Certification lineage depth: `{record.get('certification_lineage_depth', 0)}`",
            f"- Certification lineage statuses: {', '.join(record.get('certification_lineage_statuses', [])) or 'none'}",
            f"- Historical certification artifacts: {', '.join(record.get('historical_certification_artifact_ids', [])) or 'none'}",
            f"- Historical certification statuses: {', '.join(record.get('historical_certification_statuses', [])) or 'none'}",
            f"- Historical fixture count: `{record.get('historical_fixture_count', 0)}`",
            f"- Policy lineage statuses: {', '.join(record.get('policy_lineage_statuses', [])) or 'none'}",
            f"- Restored from policy versions: {', '.join(record.get('restored_from_policy_versions', [])) or 'none'}",
            f"- Restored from certification artifacts: {', '.join(record.get('restored_from_certification_artifact_ids', [])) or 'none'}",
            f"- Restored from certification statuses: {', '.join(record.get('restored_from_certification_statuses', [])) or 'none'}",
            f"- Restoration detected: `{bool(record.get('restoration_detected', False))}`",
            f"- Permission delta from previous: +{', '.join((record.get('permission_delta_from_previous') or {}).get('added', [])) or 'none'} / -{', '.join((record.get('permission_delta_from_previous') or {}).get('removed', [])) or 'none'}",
            f"- Latest transition: `{((record.get('latest_certification_transition') or {}).get('from_status')) or 'none'}` -> `{((record.get('latest_certification_transition') or {}).get('to_status')) or 'none'}`",
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


def build_extension_certification_compare_report(
    *,
    artifacts_dir: Path,
    left: dict[str, Any],
    right: dict[str, Any],
    diff: dict[str, Any],
) -> dict[str, Any]:
    report_id = (
        "extcertcompare_"
        f"{_slug(left.get('artifact_id'))}_{_slug(right.get('artifact_id'))}"
    )
    report_dir = Path(artifacts_dir) / "extensions" / "certification_compare_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    payload_path = report_dir / f"{report_id}.json"
    markdown_path = report_dir / f"{report_id}.md"
    human_summary = (
        f"Certification compare `{left.get('artifact_id')}` vs `{right.get('artifact_id')}` "
        f"tracks `{left.get('certification_status')}` -> `{right.get('certification_status')}` "
        f"with {len(diff.get('risk_flags_added', [])) + len(diff.get('risk_flags_removed', []))} risk deltas."
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
            f"# Extension Certification Compare Report {report_id}",
            "",
            "## Certification State",
            f"- Left artifact: `{left.get('artifact_id')}`",
            f"- Right artifact: `{right.get('artifact_id')}`",
            f"- Status change: `{left.get('certification_status')}` -> `{right.get('certification_status')}`",
            f"- Policy status change: `{left.get('policy_status')}` -> `{right.get('policy_status')}`",
            f"- Supersedes changed: `{bool(diff.get('supersedes_artifact_changed'))}`",
            "",
            "## Lineage And Restoration",
            f"- Lineage depth: `{diff.get('certification_lineage_depth_left', 0)}` -> `{diff.get('certification_lineage_depth_right', 0)}`",
            f"- Lineage statuses left: {', '.join(diff.get('certification_lineage_statuses_left', [])) or 'none'}",
            f"- Lineage statuses right: {', '.join(diff.get('certification_lineage_statuses_right', [])) or 'none'}",
            f"- Historical artifacts left: {', '.join(diff.get('historical_certification_artifact_ids_left', [])) or 'none'}",
            f"- Historical artifacts right: {', '.join(diff.get('historical_certification_artifact_ids_right', [])) or 'none'}",
            f"- Restored-from artifacts left: {', '.join(diff.get('restored_from_certification_artifact_ids_left', [])) or 'none'}",
            f"- Restored-from artifacts right: {', '.join(diff.get('restored_from_certification_artifact_ids_right', [])) or 'none'}",
            f"- Restoration detected changed: `{bool(diff.get('restoration_detected_changed'))}`",
            "",
            "## Permission And Risk Deltas",
            f"- Risk flags added: {', '.join(diff.get('risk_flags_added', [])) or 'none'}",
            f"- Risk flags removed: {', '.join(diff.get('risk_flags_removed', [])) or 'none'}",
            f"- Allowed tools added: {', '.join(diff.get('allowed_tools_added', [])) or 'none'}",
            f"- Allowed tools removed: {', '.join(diff.get('allowed_tools_removed', [])) or 'none'}",
            f"- Permission delta left: +{', '.join((diff.get('permission_delta_left') or {}).get('added', [])) or 'none'} / -{', '.join((diff.get('permission_delta_left') or {}).get('removed', [])) or 'none'}",
            f"- Permission delta right: +{', '.join((diff.get('permission_delta_right') or {}).get('added', [])) or 'none'} / -{', '.join((diff.get('permission_delta_right') or {}).get('removed', [])) or 'none'}",
            "",
            "## Review And Remediation",
            f"- Privilege inheritance confusion changed: `{bool(diff.get('privilege_inheritance_confusion_changed'))}`",
            f"- Adversary review reports added: {', '.join(diff.get('adversary_review_report_ids_added', [])) or 'none'}",
            f"- Adversary review reports removed: {', '.join(diff.get('adversary_review_report_ids_removed', [])) or 'none'}",
            f"- Remediation left: {', '.join(diff.get('remediation_actions_left', [])) or 'none'}",
            f"- Remediation right: {', '.join(diff.get('remediation_actions_right', [])) or 'none'}",
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
