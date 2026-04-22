from __future__ import annotations

from typing import Any


class GovernedSkillRepository:
    def __init__(self):
        self._proposals = [
            {
                "proposal_id": "skill-proposal::trajectory-cluster",
                "status": "shadow",
                "source": "trajectory-aggregation",
                "review_required": True,
                "rollback_ready": True,
            }
        ]

    def record_proposals(self, proposals: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for proposal in proposals:
            existing = next((item for item in self._proposals if item["proposal_id"] == proposal["proposal_id"]), None)
            if existing is None:
                self._proposals.insert(0, dict(proposal))
        self._proposals = self._proposals[:100]
        return list(proposals)

    def summary(self) -> dict[str, Any]:
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "repository_kind": "governed-shared-skills",
            "proposal_count": len(self._proposals),
            "items": list(self._proposals),
        }
