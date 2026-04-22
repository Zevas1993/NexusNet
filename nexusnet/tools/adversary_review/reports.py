from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id


class AdversaryReviewReporter:
    def __init__(self, *, artifacts_dir: Path):
        self.artifacts_dir = Path(artifacts_dir)
        self.report_dir = self.artifacts_dir / "security" / "adversary_review" / "reports"

    def write(self, *, review: dict[str, Any]) -> dict[str, Any]:
        report_id = new_id("advreport")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        payload_path = self.report_dir / f"{report_id}.json"
        markdown_path = self.report_dir / f"{report_id}.md"
        human_summary = (
            f"Adversary review `{review.get('review_id')}` assessed "
            f"{', '.join(review.get('risk_families', [])) or 'low-risk-path'} "
            f"and decided `{review.get('decision')}`."
        )
        payload = {
            "report_id": report_id,
            "review_id": review.get("review_id"),
            "decision": review.get("decision"),
            "risk_families": review.get("risk_families", []),
            "human_summary": human_summary,
            "trigger_source": review.get("trigger_source"),
            "requested_tools": review.get("requested_tools", []),
            "linked_allowed_tools": review.get("allowed_tools", []),
            "requested_extensions": review.get("requested_extensions", []),
            "allowed_extensions": review.get("allowed_extensions", []),
            "approval_required": (review.get("decision_provenance") or {}).get("approval_required"),
            "approval_requested": (review.get("decision_provenance") or {}).get("approval_requested"),
            "failure_policy": review.get("failure_policy"),
            "decision_provenance": review.get("decision_provenance", {}),
            "policy_path": review.get("policy_path", []),
        }
        markdown = "\n".join(
            [
                f"# Adversary Review Report {report_id}",
                "",
                f"- Review: `{review.get('review_id')}`",
                f"- Decision: `{review.get('decision')}`",
                f"- Risk families: {', '.join(review.get('risk_families', [])) or 'none'}",
                f"- Failure policy: `{review.get('failure_policy')}`",
                f"- Trigger source: `{review.get('trigger_source') or 'none'}`",
                f"- Requested tools: {', '.join(review.get('requested_tools', [])) or 'none'}",
                f"- Allowed tools: {', '.join(review.get('allowed_tools', [])) or 'none'}",
                f"- Requested extensions: {', '.join(review.get('requested_extensions', [])) or 'none'}",
                f"- Allowed extensions: {', '.join(review.get('allowed_extensions', [])) or 'none'}",
                f"- Policy path length: `{len(review.get('policy_path', []))}`",
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
