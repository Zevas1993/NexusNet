from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


class LifecycleEventLogService:
    def __init__(self, *, artifacts_dir: Path | str):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "lifecycle-events"

    def record(
        self,
        *,
        event_type: str,
        subject: str,
        payload: dict[str, Any] | None = None,
        trace_ids: list[str] | None = None,
        severity: str = "info",
    ) -> dict[str, Any]:
        event = {
            "event_id": new_id("event"),
            "event_type": event_type,
            "subject": subject,
            "severity": severity,
            "created_at": utcnow().isoformat(),
            "trace_ids": list(trace_ids or []),
            "payload": payload or {},
        }
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{event['event_id']}.json"
        path.write_text(json.dumps(event, indent=2), encoding="utf-8")
        event["artifact_path"] = str(path)
        path.write_text(json.dumps(event, indent=2), encoding="utf-8")
        return event

    def list(
        self,
        *,
        event_type: str | None = None,
        subject_prefix: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        if not self.output_dir.exists():
            return items
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if event_type and payload.get("event_type") != event_type:
                continue
            if subject_prefix and not str(payload.get("subject") or "").startswith(subject_prefix):
                continue
            items.append(payload)
            if len(items) >= limit:
                break
        return items

    def summary(
        self,
        *,
        event_type: str | None = None,
        subject_prefix: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        items = self.list(event_type=event_type, subject_prefix=subject_prefix, limit=limit)
        counts: dict[str, int] = {}
        for item in items:
            key = str(item.get("event_type") or "unknown")
            counts[key] = counts.get(key, 0) + 1
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "event_count": len(items),
            "event_type": event_type,
            "subject_prefix": subject_prefix,
            "event_type_counts": counts,
            "latest_event": items[0] if items else None,
            "items": items,
        }
