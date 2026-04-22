from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class ScheduledArtifactStore:
    def __init__(self, *, artifacts_dir: Path):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "scheduled" / "history"

    def record(self, *, workflow: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        artifact_id = new_id("schedartifact")
        record = {
            "artifact_id": artifact_id,
            "workflow_id": workflow.get("workflow_id"),
            "label": workflow.get("label"),
            "created_at": utcnow().isoformat(),
            **payload,
        }
        path = self.output_dir / f"{artifact_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        record["artifact_path"] = str(path)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record

    def list(self, *, workflow_id: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        if not self.output_dir.exists():
            return items
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if workflow_id and payload.get("workflow_id") != workflow_id:
                continue
            items.append(payload)
            if len(items) >= limit:
                break
        return items

    def latest_for(self, workflow_id: str) -> dict[str, Any] | None:
        items = self.list(workflow_id=workflow_id, limit=1)
        return items[0] if items else None
