from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


class KnowledgeArtifactStore:
    def __init__(self, artifacts_dir: Path | str | None = None):
        self.root = Path(artifacts_dir) / "knowledge" if artifacts_dir is not None else None
        self.artifacts_dir = self.root / "artifacts" if self.root is not None else None
        self.index_path = self.root / "index.jsonl" if self.root is not None else None
        self.query_events_path = self.root / "query-events.jsonl" if self.root is not None else None
        if self.artifacts_dir is not None:
            self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self._memory_artifacts: dict[str, dict[str, Any]] = {}
        self._memory_query_events: list[dict[str, Any]] = []

    def save(self, artifact: dict[str, Any]) -> dict[str, Any]:
        self._memory_artifacts[artifact["artifact_id"]] = artifact
        if self.artifacts_dir is not None and self.index_path is not None:
            path = self.artifacts_dir / f"{_safe_filename(artifact['artifact_id'])}.json"
            artifact = {**artifact, "artifact_path": str(path)}
            self._memory_artifacts[artifact["artifact_id"]] = artifact
            path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            self.index_path.open("a", encoding="utf-8").write(
                json.dumps(
                    {
                        "artifact_id": artifact["artifact_id"],
                        "artifact_hash": artifact["artifact_hash"],
                        "task_family": artifact["task_family"],
                        "status": artifact["status"],
                        "artifact_path": str(path),
                        "source_ref_gate": {
                            "allowed": (artifact.get("source_ref_security_gate") or {}).get("allowed", True),
                            "requested_count": (artifact.get("source_ref_security_gate") or {}).get("requested_count", 0),
                            "allowed_count": (artifact.get("source_ref_security_gate") or {}).get("allowed_count", 0),
                            "blocked_count": (artifact.get("source_ref_security_gate") or {}).get("blocked_count", 0),
                            "blocked_reason_counts": (artifact.get("source_ref_security_gate") or {}).get(
                                "blocked_reason_counts", {}
                            ),
                        },
                        "artifact_trust_preview": {
                            "status": (artifact.get("artifact_trust_preview") or {}).get("status", "not_scanned"),
                            "trust_decision": (artifact.get("artifact_trust_preview") or {}).get(
                                "trust_decision", "not_scanned"
                            ),
                            "reason_codes": (artifact.get("artifact_trust_preview") or {}).get("reason_codes", []),
                            "persisted": bool((artifact.get("artifact_trust_preview") or {}).get("persisted", False)),
                        },
                    },
                    sort_keys=True,
                )
                + "\n"
            )
        return artifact

    def get(self, artifact_id: str) -> dict[str, Any] | None:
        if artifact_id in self._memory_artifacts:
            return self._memory_artifacts[artifact_id]
        if self.artifacts_dir is None:
            return None
        path = self.artifacts_dir / f"{_safe_filename(artifact_id)}.json"
        if not path.exists():
            return None
        try:
            artifact = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        self._memory_artifacts[artifact_id] = artifact
        return artifact

    def list(self, *, limit: int = 50, task_family: str | None = None) -> list[dict[str, Any]]:
        artifacts = list(self._memory_artifacts.values())
        seen = {artifact.get("artifact_id") for artifact in artifacts}
        if self.artifacts_dir is not None:
            for path in self.artifacts_dir.glob("*.json"):
                try:
                    artifact = json.loads(path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                if artifact.get("artifact_id") not in seen:
                    artifacts.append(artifact)
                    seen.add(artifact.get("artifact_id"))
        if task_family:
            artifacts = [artifact for artifact in artifacts if artifact.get("task_family") == task_family]
        artifacts.sort(key=lambda item: (item.get("freshness") or {}).get("compiled_at") or "", reverse=True)
        return artifacts[:limit]

    def record_query(self, event: dict[str, Any]) -> dict[str, Any]:
        existing_events = self.query_events(limit=100000)
        latest_event = existing_events[0] if existing_events else None
        event_sequence = event.get("event_sequence") or len(existing_events) + 1
        payload = {
            **event,
            "recorded_at": event.get("recorded_at") or _utcnow(),
            "event_sequence": event_sequence,
            "previous_event_hash": event.get("previous_event_hash")
            or (latest_event or {}).get("event_hash")
            or "genesis",
        }
        payload["event_id"] = event.get("event_id") or f"kac-query:{_sha256(payload)[:16]}"
        payload["event_hash"] = event.get("event_hash") or f"sha256:{_sha256(payload)}"
        self._memory_query_events.append(payload)
        if self.query_events_path is not None:
            self.query_events_path.parent.mkdir(parents=True, exist_ok=True)
            self.query_events_path.open("a", encoding="utf-8").write(json.dumps(payload, sort_keys=True) + "\n")
        return payload

    def query_events(self, *, limit: int = 50) -> list[dict[str, Any]]:
        events = list(self._memory_query_events)
        seen = {event.get("event_id") for event in events}
        if self.query_events_path is not None and self.query_events_path.exists():
            for line in self.query_events_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("event_id") not in seen:
                    events.append(event)
                    seen.add(event.get("event_id"))
        events.sort(key=lambda item: (item.get("recorded_at") or "", int(item.get("event_sequence") or 0)), reverse=True)
        return events[:limit]


def _safe_filename(artifact_id: str) -> str:
    return (
        artifact_id.replace("://", "__")
        .replace("/", "_")
        .replace(":", "_")
        .replace("\\", "_")
    )


def _sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
