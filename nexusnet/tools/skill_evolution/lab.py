from __future__ import annotations

from collections import Counter
from typing import Any

from nexus.schemas import new_id, utcnow


class SkillEvolutionLab:
    def _pattern_for(self, trajectory: dict[str, Any]) -> str:
        if trajectory.get("pattern"):
            return str(trajectory["pattern"])
        sequence = trajectory.get("tool_sequence") or trajectory.get("tools") or []
        if sequence:
            return " -> ".join(str(item) for item in sequence)
        return "unclassified"

    def summarize_trajectories(self, trajectories: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        trajectories = trajectories or []
        pattern_counts = Counter(self._pattern_for(item) for item in trajectories)
        recurring = [{"pattern": pattern, "count": count} for pattern, count in pattern_counts.most_common(10)]
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "trajectory_count": len(trajectories),
            "recurring_patterns": recurring,
            "governance": {
                "requires_evalsao": True,
                "requires_promotion_review": True,
                "requires_rollback": True,
            },
        }

    def build_proposals(self, trajectories: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        summary = self.summarize_trajectories(trajectories)
        proposals = []
        for item in summary["recurring_patterns"]:
            proposals.append(
                {
                    "proposal_id": new_id("skillproposal"),
                    "created_at": utcnow().isoformat(),
                    "status": "shadow",
                    "pattern": item["pattern"],
                    "occurrence_count": item["count"],
                    "review_required": True,
                    "promotion_required": True,
                    "rollback_ready": True,
                    "privacy_preserving": True,
                    "suggested_skill_id": f"skill::{item['pattern'].replace(' ', '-').replace('>', '').replace(':', '')[:48].lower()}",
                }
            )
        return proposals
