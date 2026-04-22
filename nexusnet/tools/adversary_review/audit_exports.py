from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id


class AdversaryAuditExportService:
    def __init__(self, *, artifacts_dir: Path):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "security" / "adversary_review" / "audit_exports"

    def write(self, *, review: dict[str, Any]) -> dict[str, Any]:
        export_id = new_id("advaudit")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        payload_path = self.output_dir / f"{export_id}.json"
        markdown_path = self.output_dir / f"{export_id}.md"
        human_summary = (
            f"Audit export `{export_id}` captures adversary review `{review.get('review_id')}` "
            f"with decision `{review.get('decision')}` under `{review.get('failure_policy')}`."
        )
        payload = {
            "export_id": export_id,
            "review_id": review.get("review_id"),
            "decision": review.get("decision"),
            "failure_policy": review.get("failure_policy"),
            "risk_families": review.get("risk_families", []),
            "trigger_source": review.get("trigger_source"),
            "requested_tools": review.get("requested_tools", []),
            "allowed_tools": review.get("allowed_tools", []),
            "requested_extensions": review.get("requested_extensions", []),
            "allowed_extensions": review.get("allowed_extensions", []),
            "policy_path": review.get("policy_path", []),
            "decision_provenance": review.get("decision_provenance", {}),
            "linked_report_ids": [((review.get("report") or {}).get("report_id"))] if ((review.get("report") or {}).get("report_id")) else [],
            "human_summary": human_summary,
        }
        markdown = "\n".join(
            [
                f"# Adversary Audit Export {export_id}",
                "",
                f"- Review: `{review.get('review_id')}`",
                f"- Decision: `{review.get('decision')}`",
                f"- Failure policy: `{review.get('failure_policy')}`",
                f"- Trigger source: `{review.get('trigger_source') or 'none'}`",
                f"- Risk families: {', '.join(review.get('risk_families', [])) or 'none'}",
                f"- Requested tools: {', '.join(review.get('requested_tools', [])) or 'none'}",
                f"- Allowed tools: {', '.join(review.get('allowed_tools', [])) or 'none'}",
                f"- Requested extensions: {', '.join(review.get('requested_extensions', [])) or 'none'}",
                f"- Allowed extensions: {', '.join(review.get('allowed_extensions', [])) or 'none'}",
                "",
                "## Decision Provenance",
                json.dumps(review.get("decision_provenance", {}), indent=2),
                "",
                "## Policy Path",
                json.dumps(review.get("policy_path", []), indent=2),
                "",
                "## Human Summary",
                human_summary,
            ]
        )
        payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        markdown_path.write_text(markdown, encoding="utf-8")
        return {
            "export_id": export_id,
            "human_summary": human_summary,
            "payload_path": str(payload_path),
            "markdown_path": str(markdown_path),
        }

    def write_compare(self, *, left: dict[str, Any], right: dict[str, Any], diff: dict[str, Any]) -> dict[str, Any]:
        export_id = f"advauditcompare_{_slug(left.get('review_id'))}_{_slug(right.get('review_id'))}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        payload_path = self.output_dir / f"{export_id}.json"
        markdown_path = self.output_dir / f"{export_id}.md"
        human_summary = (
            f"Audit compare `{left.get('review_id')}` vs `{right.get('review_id')}` "
            f"tracks `{left.get('decision')}` -> `{right.get('decision')}` across "
            f"{len(diff.get('risk_families_added', [])) + len(diff.get('risk_families_removed', []))} risk-family deltas."
        )
        payload = {
            "export_id": export_id,
            "left": left,
            "right": right,
            "diff": diff,
            "human_summary": human_summary,
        }
        markdown = "\n".join(
            [
                f"# Adversary Audit Compare {export_id}",
                "",
                "## Decision Delta",
                f"- Left review: `{left.get('review_id')}`",
                f"- Right review: `{right.get('review_id')}`",
                f"- Decision change: `{left.get('decision')}` -> `{right.get('decision')}`",
                "",
                "## Risk And Scope Delta",
                f"- Risk families added: {', '.join(diff.get('risk_families_added', [])) or 'none'}",
                f"- Risk families removed: {', '.join(diff.get('risk_families_removed', [])) or 'none'}",
                f"- Requested tools added: {', '.join(diff.get('requested_tools_added', [])) or 'none'}",
                f"- Requested extensions added: {', '.join(diff.get('requested_extensions_added', [])) or 'none'}",
                f"- Requested tools removed: {', '.join(diff.get('requested_tools_removed', [])) or 'none'}",
                f"- Requested extensions removed: {', '.join(diff.get('requested_extensions_removed', [])) or 'none'}",
                "",
                "## Human Summary",
                human_summary,
            ]
        )
        payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        markdown_path.write_text(markdown, encoding="utf-8")
        return {
            "export_id": export_id,
            "human_summary": human_summary,
            "payload_path": str(payload_path),
            "markdown_path": str(markdown_path),
        }


def _slug(value: Any) -> str:
    return "".join(ch if str(ch).isalnum() else "_" for ch in str(value or "unknown")).strip("_").lower()
