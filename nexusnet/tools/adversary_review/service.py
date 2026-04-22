from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow
from .audit_exports import AdversaryAuditExportService
from .policies import AdversaryRiskPolicyEngine
from .reports import AdversaryReviewReporter


class AdversaryReviewService:
    def __init__(self, *, artifacts_dir: Path, runtime_configs: dict[str, Any]):
        security = (runtime_configs.get("goose_lane") or {}).get("security") or {}
        self.config = (security.get("adversary_review") or {})
        self.artifacts_dir = artifacts_dir
        self.policy_engine = AdversaryRiskPolicyEngine()
        self.reporter = AdversaryReviewReporter(artifacts_dir=artifacts_dir)
        self.audit_exports = AdversaryAuditExportService(artifacts_dir=artifacts_dir)
        self._latest_review: dict[str, Any] | None = None
        self._history: list[dict[str, Any]] = []

    def review(
        self,
        *,
        subject: str,
        requested_tools: list[str] | None = None,
        risk_level: str = "medium",
        reviewer_status: str = "available",
        summary: str | None = None,
        fallback_reason: str | None = None,
        policy_path: list[dict[str, Any]] | None = None,
        multi_step: bool | None = None,
        approval_requested: bool | None = None,
        approval_required: bool | None = None,
        allowed_tools: list[str] | None = None,
        requested_extensions: list[str] | None = None,
        allowed_extensions: list[str] | None = None,
        trigger_source: str | None = None,
    ) -> dict[str, Any]:
        requested_tools = list(requested_tools or [])
        escalations = list(self.config.get("escalation_targets") or [])
        assessment = self.policy_engine.assess(
            requested_tools=requested_tools,
            fallback_reason=fallback_reason,
            policy_path=policy_path,
            multi_step=multi_step,
            approval_requested=approval_requested,
            approval_required=approval_required,
            allowed_tools=allowed_tools,
            requested_extensions=requested_extensions,
            allowed_extensions=allowed_extensions,
            trigger_source=trigger_source,
        )
        effective_risk_level = "critical" if risk_level == "critical" else assessment.get("risk_level", risk_level)
        high_risk = effective_risk_level in {"high", "critical"} or assessment.get("high_risk", False)
        if "ambiguous-tool-binding-risk" in assessment.get("risk_families", []):
            decision = "deny"
            rationale = "Ambiguous gateway binding is treated as fail-closed."
        elif "extension-acp-privilege-inheritance-confusion-risk" in assessment.get("risk_families", []):
            decision = "escalate"
            rationale = "ACP or extension privilege inheritance confusion requires explicit bounded review."
        elif "bundle-level-permission-escalation-attempt-risk" in assessment.get("risk_families", []):
            decision = "escalate"
            rationale = "Extension bundle permission escalation attempts require explicit bounded review."
        elif "recipe-subagent-privilege-confusion-risk" in assessment.get("risk_families", []):
            decision = "escalate"
            rationale = "Subagent privilege confusion requires explicit bounded review."
        elif "chained-approval-bypass-risk" in assessment.get("risk_families", []):
            decision = "deny"
            rationale = "Chained approval bypass attempts are treated as fail-closed."
        elif high_risk and reviewer_status != "available":
            decision = "escalate" if escalations else "deny"
            rationale = "Reviewer unavailable on a high-risk path; fail-open is not permitted."
        elif effective_risk_level == "critical":
            decision = "escalate"
            rationale = "Critical path requires explicit SafetyAO/CritiqueAO/manual review."
        elif "multi-step-escalation-risk" in assessment.get("risk_families", []):
            decision = "escalate"
            rationale = "Multi-step high-risk chains escalate for bounded review."
        elif high_risk:
            decision = "allow-with-review"
            rationale = "High-risk path stays bounded behind an explicit adversary review outcome."
        else:
            decision = "allow"
            rationale = "Low-risk path may proceed within current guardrails."
        review = {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "review_id": new_id("advreview"),
            "subject": subject,
            "requested_tools": requested_tools,
            "risk_level": effective_risk_level,
            "risk_families": assessment.get("risk_families", []),
            "reviewer_status": reviewer_status,
            "decision": decision,
            "rationale": rationale,
            "fail_open_allowed": False,
            "failure_policy": self.config.get("failure_policy", "fail-closed-or-escalate"),
            "escalation_targets": escalations,
            "summary": summary or rationale,
            "fallback_reason": fallback_reason,
            "policy_path": policy_path or [],
            "multi_step_escalation": "multi-step-escalation-risk" in assessment.get("risk_families", []),
            "trigger_source": trigger_source,
            "allowed_tools": list(allowed_tools or []),
            "requested_extensions": list(requested_extensions or []),
            "allowed_extensions": list(allowed_extensions or []),
            "decision_provenance": {
                "assessment": assessment,
                "reviewer_status": reviewer_status,
                "escalation_targets": escalations,
                "approval_required": approval_required,
                "approval_requested": approval_requested,
            },
            "created_at": utcnow().isoformat(),
        }
        artifact_path = self.artifacts_dir / "security" / "adversary_review" / f"{review['review_id']}.json"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(json.dumps(review, indent=2), encoding="utf-8")
        review["artifact_path"] = str(artifact_path)
        review["report"] = self.reporter.write(review=review)
        review["audit_export"] = self.audit_exports.write(review=review)
        self._latest_review = review
        self._history.insert(0, review)
        self._history = self._history[:25]
        artifact_path.write_text(json.dumps(review, indent=2), encoding="utf-8")
        return review

    def summary(self) -> dict[str, Any]:
        family_counts: dict[str, int] = {}
        for review in self._history:
            for family in review.get("risk_families", []):
                family_counts[family] = family_counts.get(family, 0) + 1
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "failure_policy": self.config.get("failure_policy", "fail-closed-or-escalate"),
            "high_risk_tools": list(self.config.get("high_risk_tools") or []),
            "latest_review": self._latest_review,
            "recent_reviews": self._history[:10],
            "family_counts": family_counts,
            "latest_report_id": (((self._latest_review or {}).get("report") or {}).get("report_id")),
            "latest_audit_export_id": (((self._latest_review or {}).get("audit_export") or {}).get("export_id")),
            "quarantine_required": False,
            "compare_refs": {
                "recent_reviews": "/ops/brain/security/adversary-reviews",
                "review_detail_template": "/ops/brain/security/adversary-reviews/{review_id}",
                "review_compare": "/ops/brain/security/adversary-reviews/compare",
                "audit_export_template": "/ops/brain/security/adversary-reviews/{review_id}/audit-export",
            },
        }

    def detail(self, review_id: str) -> dict[str, Any] | None:
        review = next((item for item in self._history if item.get("review_id") == review_id), None)
        if review is None:
            path = self.artifacts_dir / "security" / "adversary_review" / f"{review_id}.json"
            if not path.exists():
                return None
            try:
                review = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None
        report = review.get("report") or {}
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
        audit_export = review.get("audit_export") or {}
        audit_payload = None
        audit_markdown = None
        if audit_export.get("payload_path"):
            try:
                audit_payload = json.loads(Path(audit_export["payload_path"]).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                audit_payload = None
        if audit_export.get("markdown_path"):
            try:
                audit_markdown = Path(audit_export["markdown_path"]).read_text(encoding="utf-8")
            except OSError:
                audit_markdown = None
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "item": review,
            "report_payload": payload,
            "report_markdown": markdown,
            "audit_export_payload": audit_payload,
            "audit_export_markdown": audit_markdown,
            "compare_refs": {
                "recent_reviews": "/ops/brain/security/adversary-reviews",
                "review_compare": "/ops/brain/security/adversary-reviews/compare",
                "audit_export_template": "/ops/brain/security/adversary-reviews/{review_id}/audit-export",
            },
        }

    def audit_export_detail(self, review_id: str) -> dict[str, Any] | None:
        detail = self.detail(review_id)
        if detail is None:
            return None
        review = detail.get("item") or {}
        audit_export = review.get("audit_export") or {}
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "review_id": review_id,
            "audit_export": audit_export,
            "payload": detail.get("audit_export_payload"),
            "markdown": detail.get("audit_export_markdown"),
        }

    def compare(self, left_review_id: str, right_review_id: str) -> dict[str, Any] | None:
        left = self.detail(left_review_id)
        right = self.detail(right_review_id)
        if left is None or right is None:
            return None
        left_item = left.get("item") or {}
        right_item = right.get("item") or {}
        left_risks = set(left_item.get("risk_families", []))
        right_risks = set(right_item.get("risk_families", []))
        left_tools = set(left_item.get("requested_tools", []))
        right_tools = set(right_item.get("requested_tools", []))
        left_extensions = set(left_item.get("requested_extensions", []))
        right_extensions = set(right_item.get("requested_extensions", []))
        diff = {
            "decision_changed": left_item.get("decision") != right_item.get("decision"),
            "risk_level_changed": left_item.get("risk_level") != right_item.get("risk_level"),
            "trigger_source_changed": left_item.get("trigger_source") != right_item.get("trigger_source"),
            "risk_families_added": sorted(right_risks - left_risks),
            "risk_families_removed": sorted(left_risks - right_risks),
            "requested_tools_added": sorted(right_tools - left_tools),
            "requested_tools_removed": sorted(left_tools - right_tools),
            "requested_extensions_added": sorted(right_extensions - left_extensions),
            "requested_extensions_removed": sorted(left_extensions - right_extensions),
            "allowed_extensions_left": left_item.get("allowed_extensions", []),
            "allowed_extensions_right": right_item.get("allowed_extensions", []),
            "fail_open_allowed_left": left_item.get("fail_open_allowed"),
            "fail_open_allowed_right": right_item.get("fail_open_allowed"),
            "audit_export_left": ((left_item.get("audit_export") or {}).get("export_id")),
            "audit_export_right": ((right_item.get("audit_export") or {}).get("export_id")),
        }
        export = self.audit_exports.write_compare(
            left=self._compare_card(left_item),
            right=self._compare_card(right_item),
            diff=diff,
        )
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "left": self._compare_card(left_item),
            "right": self._compare_card(right_item),
            "scene_delta": {
                "refs": {
                    "left": left_review_id,
                    "right": right_review_id,
                },
                "hot_subjects": [
                    {
                        "subject": risk,
                        "delta": (1 if risk in right_risks else 0) - (1 if risk in left_risks else 0),
                    }
                    for risk in sorted(left_risks | right_risks)
                    if risk in left_risks.symmetric_difference(right_risks)
                ],
                "hot_links": [
                    {"link_id": "requested_tool_count_delta", "delta": len(right_tools) - len(left_tools)},
                    {"link_id": "requested_extension_count_delta", "delta": len(right_extensions) - len(left_extensions)},
                ],
            },
            "diff": diff,
            "export": export,
            "compare_refs": {
                "recent_reviews": "/ops/brain/security/adversary-reviews",
                "review_detail_template": "/ops/brain/security/adversary-reviews/{review_id}",
            },
        }

    def _compare_card(self, review: dict[str, Any]) -> dict[str, Any]:
        return {
            "review_id": review.get("review_id"),
            "decision": review.get("decision"),
            "risk_level": review.get("risk_level"),
            "risk_families": review.get("risk_families", []),
            "trigger_source": review.get("trigger_source"),
            "requested_tools": review.get("requested_tools", []),
            "requested_extensions": review.get("requested_extensions", []),
            "allowed_extensions": review.get("allowed_extensions", []),
            "report_id": ((review.get("report") or {}).get("report_id")),
            "audit_export_id": ((review.get("audit_export") or {}).get("export_id")),
        }
