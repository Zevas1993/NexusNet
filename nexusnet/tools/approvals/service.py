from __future__ import annotations

from typing import Any


class GatewayApprovalService:
    def __init__(self, *, store: Any):
        self.store = store

    def snapshot(self, *, limit: int = 20) -> dict:
        decisions = self.store.list_approvals(limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "recent_decisions": decisions,
            "approval_required_states": sorted({decision.get("decision") for decision in decisions if decision.get("decision")}),
        }
