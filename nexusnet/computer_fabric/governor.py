from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow


class PersistentComputerGovernor:
    def record(self, *, session_dir: Path, session_id: str, schedule: str | None) -> dict[str, Any]:
        governor = {
            "session_id": session_id,
            "created_at": utcnow().isoformat(),
            "uptime_policy": {"mode": "scheduled-only", "schedule": schedule, "max_continuous_hours": 0},
            "disk_policy": {"quota": "bounded", "cleanup_required": True},
            "network_policy": {"egress": "task-scoped", "inbound": "blocked"},
            "public_url_policy": {"allowed": False, "approval_required": True},
            "port_policy": {"open_ports": [], "default": "closed"},
            "cost_policy": {"budget": "operator-approved", "metering_required": True},
            "backup_policy": {"mode": "artifact-export-only", "restore_required_before_promotion": True},
            "kill_switch": {"enabled": True, "operator_visible": True},
        }
        (session_dir / "persistent-governor.json").write_text(json.dumps(governor, indent=2, sort_keys=True), encoding="utf-8")
        return governor
