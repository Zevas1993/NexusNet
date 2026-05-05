from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from nexus.schemas import utcnow


class ApprovalQueue:
    APPROVAL_REASONS = {
        "browser-action-requires-approval",
        "public-service-hosting-requires-approval",
        "credential-use-requires-approval",
        "local-command-requires-approval",
    }

    def record(self, *, session_dir: Path, session_id: str, blocked_reasons: list[str], scope: str) -> list[dict[str, Any]]:
        approvals = [
            {
                "approval_id": f"approval_{uuid4().hex[:12]}",
                "session_id": session_id,
                "requested_action": reason.replace("-requires-approval", ""),
                "risk": "high" if "credential" in reason or "browser" in reason else "medium",
                "scope": scope,
                "expires_at": "session-end",
                "operator_decision": "pending",
                "evidence_refs": ["manifest.json", "policy.json", "events.jsonl"],
                "created_at": utcnow().isoformat(),
            }
            for reason in blocked_reasons
            if reason in self.APPROVAL_REASONS
        ]
        if approvals:
            (session_dir / "approvals.jsonl").write_text(
                "\n".join(json.dumps(item, sort_keys=True) for item in approvals) + "\n",
                encoding="utf-8",
            )
        return approvals
