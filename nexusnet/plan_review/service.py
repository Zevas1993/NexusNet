from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class PlanReviewService:
    def __init__(self, *, artifacts_dir: Path | str, events: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "plan-reviews"
        self.events = events

    def review(
        self,
        *,
        title: str,
        content: str,
        decision: str,
        plan_id: str | None = None,
        reviewer: str = "operator",
        annotations: list[dict[str, Any]] | None = None,
        linked_workflow_id: str | None = None,
    ) -> dict[str, Any]:
        plan_id = plan_id or new_id("plan")
        annotations = list(annotations or [])
        existing = self.get(plan_id)
        versions = list((existing or {}).get("versions", []))
        previous_content = versions[-1]["content"] if versions else None
        version = len(versions) + 1
        versions.append(
            {
                "version": version,
                "created_at": utcnow().isoformat(),
                "content": content,
                "content_length": len(content),
            }
        )
        risk_flags = self._risk_flags(content)
        status = "approved_for_validation" if decision == "approved" else "changes_requested" if decision == "denied" else "review_pending"
        reviews = list((existing or {}).get("reviews", []))
        latest_review = {
            "review_id": new_id("planreview"),
            "created_at": utcnow().isoformat(),
            "decision": decision,
            "reviewer": reviewer,
            "annotations": annotations,
            "linked_workflow_id": linked_workflow_id,
        }
        reviews.append(latest_review)
        record = {
            "plan_id": plan_id,
            "title": title,
            "status": status,
            "created_at": (existing or {}).get("created_at") or utcnow().isoformat(),
            "updated_at": utcnow().isoformat(),
            "linked_workflow_id": linked_workflow_id or (existing or {}).get("linked_workflow_id"),
            "execution_allowed": False,
            "mutation_allowed": False,
            "gateway_required": True,
            "risk_flags": risk_flags,
            "versions": versions,
            "reviews": reviews,
            "latest_review": latest_review,
            "diff_from_previous": {
                "changed": previous_content is not None and previous_content != content,
                "previous_version": version - 1 if previous_content is not None else None,
                "current_version": version,
            },
            "analytics": self._analytics(reviews),
            "policy": {
                "approval_is_execution_authority": False,
                "approved_state": "approved_for_validation",
                "execution_requires_gateway": True,
                "product_sweep_required": True,
            },
        }
        path = self.output_dir / f"{plan_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        if self.events:
            self.events.record(
                event_type="plan.reviewed",
                subject=f"plan:{plan_id}",
                payload={
                    "decision": decision,
                    "status": status,
                    "version": version,
                    "risk_flags": risk_flags,
                },
            )
            if decision == "denied":
                self.events.record(
                    event_type="approval.denied",
                    subject=f"plan:{plan_id}",
                    payload={"review_id": latest_review["review_id"], "annotation_count": len(annotations)},
                )
            elif decision == "approved":
                self.events.record(
                    event_type="approval.recorded",
                    subject=f"plan:{plan_id}",
                    payload={"review_id": latest_review["review_id"], "grants_execution": False},
                )
        return record

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        items = self.list(limit=limit)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "plan_count": len(items),
            "latest_plan": items[0] if items else None,
            "status_counts": self._status_counts(items),
            "denial_analytics": self.denial_analytics(items),
            "event_log": self.events.summary(subject_prefix="plan:", limit=100) if self.events else {},
            "items": items,
        }

    def list(self, *, limit: int = 50) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        if not self.output_dir.exists():
            return items
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            items.append(payload)
            if len(items) >= limit:
                break
        return items

    def get(self, plan_id: str) -> dict[str, Any] | None:
        path = self.output_dir / f"{plan_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def denial_analytics(self, items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        items = items or self.list(limit=200)
        blockers: dict[str, int] = {}
        denied_count = 0
        for item in items:
            for review in item.get("reviews", []):
                if review.get("decision") != "denied":
                    continue
                denied_count += 1
                for annotation in review.get("annotations", []) or []:
                    message = str(annotation.get("message") or "").strip()
                    if message:
                        blockers[message] = blockers.get(message, 0) + 1
        return {"denied_count": denied_count, "common_blockers": blockers}

    def _analytics(self, reviews: list[dict[str, Any]]) -> dict[str, Any]:
        approved_count = sum(1 for review in reviews if review.get("decision") == "approved")
        denied_count = sum(1 for review in reviews if review.get("decision") == "denied")
        annotation_count = sum(len(review.get("annotations", []) or []) for review in reviews)
        return {
            "approved_count": approved_count,
            "denied_count": denied_count,
            "annotation_count": annotation_count,
            "review_count": len(reviews),
        }

    def _status_counts(self, items: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            status = str(item.get("status") or "unknown")
            counts[status] = counts.get(status, 0) + 1
        return counts

    def _risk_flags(self, content: str) -> list[str]:
        normalized = content.lower()
        flags: set[str] = set()
        if "approval grants live execution" in normalized or "bypasses policy" in normalized:
            flags.add("approval-is-not-execution-authority")
        if "install arbitrary npm" in normalized or "run them in core" in normalized:
            flags.add("arbitrary-package-execution-risk")
        return sorted(flags)
