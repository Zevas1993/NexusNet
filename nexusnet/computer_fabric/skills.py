from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from nexus.schemas import utcnow

from .models import ComputerSessionRequest


class ComputerSkillCompiler:
    def compile(
        self,
        *,
        session_dir: Path,
        session_id: str,
        request: ComputerSessionRequest,
        artifacts: list[dict[str, Any]],
        blocked_reasons: list[str],
    ) -> dict[str, Any]:
        candidate = {
            "skill_candidate_id": f"computerskill_{uuid4().hex[:12]}",
            "session_id": session_id,
            "created_at": utcnow().isoformat(),
            "status": "review-required",
            "inputs": {
                "goal": request.goal,
                "task_type": request.task_type,
                "schedule": request.schedule,
            },
            "allowed_tools": list(request.requested_tools),
            "scripts": [],
            "required_checks": list(request.required_checks),
            "failure_modes": sorted(blocked_reasons),
            "expected_artifacts": [item["artifact_type"] for item in artifacts],
            "evals": ["computer-fabric-policy", "artifact-trust", "cleanup-proof"],
            "rollback": "delete-skill-candidate-and-replay-session",
        }
        (session_dir / "skill-candidate.json").write_text(json.dumps(candidate, indent=2, sort_keys=True), encoding="utf-8")
        return candidate
