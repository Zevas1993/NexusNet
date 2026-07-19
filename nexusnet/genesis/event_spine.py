from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


GENESIS_EVENT_SPINE_SCHEMA = "nexusnet-genesis-event-spine-v1"
GENESIS_EVENT_SPINE_SURFACE_ID = "genesis-event-spine"
GENESIS_EVENT_SPINE_EVENT_REF = "genesis/event-spine/events.jsonl"
GENESIS_EVENT_SPINE_BLACKBOARD_REF = "genesis/event-spine/hive_blackboard_snapshots.jsonl"
GENESIS_EVENT_SPINE_PLANE_TRACE_REF = "genesis/event-spine/plane_traces.jsonl"

_UNSAFE_REF_MARKERS = (
    "raw-prompt",
    "raw-output",
    "secret",
    "token",
    "password",
    "api-key",
    "apikey",
    ":\\",
    "runtime/test-fixtures",
)


class GenesisEventSpineService:
    """Shared append-only event spine for Genesis runtime surfaces."""

    def __init__(self, *, artifacts_dir: Path | str, project_root: Path | str | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.project_root = Path(project_root) if project_root is not None else None
        self.spine_dir = self.artifacts_dir / "genesis" / "event-spine"
        self.events_path = self.spine_dir / "events.jsonl"
        self.blackboard_path = self.spine_dir / "hive_blackboard_snapshots.jsonl"
        self.plane_trace_path = self.spine_dir / "plane_traces.jsonl"

    def publish_event(
        self,
        *,
        event_type: str,
        source_surface_id: str,
        correlation_ref: str,
        session_ref_digest: str | None = None,
        source_hive_run_ref: str | None = None,
        heartbeat_record_id: str | None = None,
        privacy_label: str = "sanitized-genesis-event",
        artifact_refs: list[str | None] | None = None,
        planes: list[str] | None = None,
        priority_trails: list[dict[str, Any]] | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        created = created_at or _utcnow()
        safe_artifact_refs = _sanitize_refs(artifact_refs or [])
        safe_planes = _dedupe([str(plane) for plane in (planes or ["runtime", "governance", "event"])])[:12]
        seed = json.dumps(
            {
                "event_type": event_type,
                "source_surface_id": source_surface_id,
                "correlation_ref": correlation_ref,
                "session_ref_digest": session_ref_digest,
                "source_hive_run_ref": source_hive_run_ref,
                "heartbeat_record_id": heartbeat_record_id,
                "artifact_refs": safe_artifact_refs,
                "created_at": created,
            },
            sort_keys=True,
        )
        digest = _digest(seed)
        event_ref = f"genesis-event::{digest}"
        snapshot_ref = f"hive-blackboard::{digest}"
        trace_ref = f"plane-trace::{digest}"
        event = {
            "schema_version": "nexusnet-neural-bus-event-envelope-v1",
            "surface_id": "genesis-event-spine-event",
            "event_ref": event_ref,
            "event_type": str(event_type),
            "source_surface_id": str(source_surface_id),
            "correlation_ref": _safe_ref(correlation_ref),
            "activation_ref": f"activation::{digest}",
            "session_ref_digest": session_ref_digest,
            "source_hive_run_ref": _safe_ref(source_hive_run_ref),
            "heartbeat_record_id": _safe_ref(heartbeat_record_id),
            "event_privacy_label": str(privacy_label),
            "artifact_bound": True,
            "artifact_refs": safe_artifact_refs[:32],
            "created_at": created,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        blackboard = {
            "schema_version": "nexusnet-hive-blackboard-snapshot-v1",
            "surface_id": "genesis-event-spine-hive-blackboard-snapshot",
            "snapshot_ref": snapshot_ref,
            "event_ref": event_ref,
            "source_surface_id": str(source_surface_id),
            "correlation_ref": event["correlation_ref"],
            "session_ref_digest": session_ref_digest,
            "source_heartbeat_record_id": event["heartbeat_record_id"],
            "state": "genesis-event-spine-projected",
            "priority_trails": _priority_trails(
                priority_trails=priority_trails or [],
                fallback_ref=event["correlation_ref"],
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        plane_trace = {
            "schema_version": "nexusnet-plane-trace-ledger-v1",
            "surface_id": "genesis-event-spine-plane-trace",
            "trace_ref": trace_ref,
            "event_ref": event_ref,
            "source_surface_id": str(source_surface_id),
            "correlation_ref": event["correlation_ref"],
            "session_ref_digest": session_ref_digest,
            "source_heartbeat_record_id": event["heartbeat_record_id"],
            "source_hive_run_ref": event["source_hive_run_ref"],
            "planes": safe_planes,
            "artifact_bound_downstream_consumption_required": True,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
        self._append_unique_jsonl(self.events_path, event, key="event_ref", key_value=event_ref)
        self._append_unique_jsonl(self.blackboard_path, blackboard, key="snapshot_ref", key_value=snapshot_ref)
        self._append_unique_jsonl(self.plane_trace_path, plane_trace, key="trace_ref", key_value=trace_ref)
        return {
            "schema_version": "nexusnet-genesis-event-spine-projection-v1",
            "surface_id": "genesis-event-spine-projection",
            "event_ref": event_ref,
            "blackboard_snapshot_ref": snapshot_ref,
            "plane_trace_ref": trace_ref,
            "event_type": str(event_type),
            "source_surface_id": str(source_surface_id),
            "correlation_ref": event["correlation_ref"],
            "session_ref_digest": session_ref_digest,
            "typed_event_envelope": event,
            "hive_blackboard_snapshot": blackboard,
            "plane_trace": plane_trace,
            "evidence_refs": _sanitize_refs(
                [
                    GENESIS_EVENT_SPINE_EVENT_REF,
                    GENESIS_EVENT_SPINE_BLACKBOARD_REF,
                    GENESIS_EVENT_SPINE_PLANE_TRACE_REF,
                    event_ref,
                    snapshot_ref,
                    trace_ref,
                    *safe_artifact_refs,
                ]
            )[:48],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    def summary(
        self,
        session_id: str | None = None,
        *,
        session_ref_digest: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        digest = session_ref_digest or (_privacy_digest(session_id) if session_id else None)
        all_events = [event for event in self._read_jsonl(self.events_path) if _is_valid_event(event)]
        all_blackboards = [item for item in self._read_jsonl(self.blackboard_path) if _is_valid_blackboard(item)]
        all_traces = [item for item in self._read_jsonl(self.plane_trace_path) if _is_valid_trace(item)]
        scoped_events = _filter_by_session(all_events, digest)
        scoped_blackboards = _filter_by_session(all_blackboards, digest)
        scoped_traces = _filter_by_session(all_traces, digest)
        latest = scoped_events[-1] if scoped_events else None
        event_type_counts: dict[str, int] = {}
        for event in scoped_events:
            event_type = str(event.get("event_type") or "unknown")
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        visible = list(reversed(scoped_events))[: max(1, int(limit))]
        return {
            "schema_version": GENESIS_EVENT_SPINE_SCHEMA,
            "surface_id": GENESIS_EVENT_SPINE_SURFACE_ID,
            "status": "live-control-plane" if latest else "not-observed",
            "honest_status_label": (
                "genesis-shared-event-spine-live-control-plane"
                if latest
                else "genesis-shared-event-spine-not-observed"
            ),
            "authority": "NexusBrain",
            "mode": "append-only-file-backed",
            "session_ref_digest": digest,
            "event_count": len(scoped_events),
            "global_event_count": len(all_events),
            "blackboard_snapshot_count": len(scoped_blackboards),
            "global_blackboard_snapshot_count": len(all_blackboards),
            "plane_trace_count": len(scoped_traces),
            "global_plane_trace_count": len(all_traces),
            "latest_event_ref": latest.get("event_ref") if latest else None,
            "latest_event_type": latest.get("event_type") if latest else None,
            "latest_correlation_ref": latest.get("correlation_ref") if latest else None,
            "event_type_counts": event_type_counts,
            "events": visible,
            "artifact_refs": {
                "events": GENESIS_EVENT_SPINE_EVENT_REF,
                "blackboard_snapshots": GENESIS_EVENT_SPINE_BLACKBOARD_REF,
                "plane_traces": GENESIS_EVENT_SPINE_PLANE_TRACE_REF,
            },
            "evidence_refs": _sanitize_refs(
                [
                    GENESIS_EVENT_SPINE_EVENT_REF,
                    GENESIS_EVENT_SPINE_BLACKBOARD_REF,
                    GENESIS_EVENT_SPINE_PLANE_TRACE_REF,
                    latest.get("event_ref") if latest else None,
                ]
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-genesis-event-spine-refs-digests-counts-types-and-status-only-"
                "no-prompts-outputs-session-ids-local-paths-or-raw-content"
            ),
            "mutation_boundary": "append-only-shared-genesis-event-spine-no-production-mutation",
        }

    def _append_unique_jsonl(self, path: Path, packet: dict[str, Any], *, key: str, key_value: str) -> None:
        self.spine_dir.mkdir(parents=True, exist_ok=True)
        if path.is_file():
            for existing in self._read_jsonl(path):
                if str(existing.get(key) or "") == key_value:
                    return
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(packet, sort_keys=True) + "\n")

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.is_file():
            return []
        records: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
        return records


def _is_valid_event(record: dict[str, Any]) -> bool:
    return (
        isinstance(record, dict)
        and record.get("schema_version") == "nexusnet-neural-bus-event-envelope-v1"
        and record.get("surface_id") == "genesis-event-spine-event"
        and bool(record.get("event_ref"))
        and bool(record.get("event_type"))
        and record.get("raw_content_included") is False
        and record.get("active_production_mutation_allowed") is False
        and record.get("active_production_mutated") is False
    )


def _is_valid_blackboard(record: dict[str, Any]) -> bool:
    return (
        isinstance(record, dict)
        and record.get("schema_version") == "nexusnet-hive-blackboard-snapshot-v1"
        and record.get("surface_id") == "genesis-event-spine-hive-blackboard-snapshot"
        and bool(record.get("snapshot_ref"))
        and record.get("raw_content_included") is False
        and record.get("active_production_mutation_allowed") is False
        and record.get("active_production_mutated") is False
    )


def _is_valid_trace(record: dict[str, Any]) -> bool:
    return (
        isinstance(record, dict)
        and record.get("schema_version") == "nexusnet-plane-trace-ledger-v1"
        and record.get("surface_id") == "genesis-event-spine-plane-trace"
        and bool(record.get("trace_ref"))
        and record.get("raw_content_included") is False
        and record.get("active_production_mutation_allowed") is False
        and record.get("active_production_mutated") is False
    )


def _filter_by_session(records: list[dict[str, Any]], session_ref_digest: str | None) -> list[dict[str, Any]]:
    if not session_ref_digest:
        return records
    return [
        record
        for record in records
        if str(record.get("session_ref_digest") or "") == session_ref_digest
    ]


def _priority_trails(*, priority_trails: list[dict[str, Any]], fallback_ref: str) -> list[dict[str, Any]]:
    trails: list[dict[str, Any]] = []
    for trail in priority_trails:
        if not isinstance(trail, dict):
            continue
        artifact_ref = _safe_ref(trail.get("artifact_ref")) or fallback_ref
        trails.append(
            {
                "topic": str(trail.get("topic") or "genesis-event"),
                "strength": float(trail.get("strength") or 1.0),
                "artifact_ref": artifact_ref,
            }
        )
    if not trails:
        trails.append({"topic": "genesis-event", "strength": 1.0, "artifact_ref": fallback_ref})
    return trails[:12]


def _sanitize_refs(value: Any) -> list[str]:
    if isinstance(value, str):
        candidates = [value]
    elif isinstance(value, list):
        candidates = value
    else:
        candidates = []
    return _dedupe(
        [
            _safe_ref(candidate)
            for candidate in candidates
            if _safe_ref(candidate)
        ]
    )


def _safe_ref(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    if not text or ".." in text or _unsafe_ref(text):
        return ""
    return text[:220]


def _unsafe_ref(value: str) -> bool:
    normalized = value.lower().replace("\\", "/")
    return any(marker in normalized for marker in _UNSAFE_REF_MARKERS)


def _dedupe(values: list[str | None]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _privacy_digest(value: str | None) -> str:
    return "sha256:" + hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
