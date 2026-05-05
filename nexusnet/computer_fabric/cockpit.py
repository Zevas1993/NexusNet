from __future__ import annotations

from typing import Any


class ReplayCockpitBuilder:
    def build(self, *, session_summaries: list[dict[str, Any]]) -> dict[str, Any]:
        latest = session_summaries[0] if session_summaries else None
        return {
            "timeline_count": len(session_summaries),
            "latest_session_id": (latest or {}).get("session_id"),
            "panels": [
                "timeline",
                "command transcript",
                "file diff",
                "artifacts",
                "trust state",
                "approvals",
                "policy findings",
                "provider state",
                "cleanup proof",
                "promotion blockers",
            ],
            "promotion_blockers": ["no-production-mutation-without-review"],
        }
