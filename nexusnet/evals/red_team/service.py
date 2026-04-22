from __future__ import annotations

from typing import Any


class RedTeamEvidenceService:
    def __init__(self, *, review_service: Any, gateway_scenarios: Any | None = None):
        self.review_service = review_service
        self.gateway_scenarios = gateway_scenarios

    def summary(self) -> dict[str, Any]:
        review_summary = self.review_service.summary()
        latest = review_summary.get("latest_review")
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "research_only": True,
            "quarantine_required": True,
            "latest_review_id": latest.get("review_id") if latest else None,
            "latest_artifact_path": latest.get("artifact_path") if latest else None,
            "gateway_scenarios": self.gateway_scenarios.summary(recent_reviews=review_summary.get("recent_reviews", []))
            if self.gateway_scenarios is not None
            else None,
            "promotion_blocked_by_default": True,
        }
