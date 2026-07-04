from __future__ import annotations

import hashlib
import json
from typing import Any

from nexusnet.hive.project_heartbeat_replay import compact_failure_recovery_governance


PROJECT_HEARTBEAT_SCHEMA = "nexusnet-project-heartbeat-v1"
PROJECT_HEARTBEAT_SURFACE_ID = "nexusnet-project-heartbeat"
PROJECT_HEARTBEAT_HISTORY_SCHEMA = "nexusnet-release-wrapper-project-heartbeat-replay-v1"
PROJECT_HEARTBEAT_HISTORY_RECORD_SCHEMA = "nexusnet-release-wrapper-project-heartbeat-record-v1"
PROJECT_HEARTBEAT_HISTORY_SURFACE_ID = "release-wrapper-project-heartbeat-replay"
PROJECT_HEARTBEAT_HISTORY_RECORD_SURFACE_ID = "release-wrapper-project-heartbeat-record"
PROJECT_HEARTBEAT_HISTORY_REF = "release-wrapper-runtime/project-heartbeats.jsonl"
PROJECT_HEARTBEAT_HISTORY_PUBLIC_REF = f"artifacts/{PROJECT_HEARTBEAT_HISTORY_REF}"


def empty_release_project_heartbeat(
    *,
    session_ref_digest: str | None,
    status: str = "not-run",
    blocker: str = "project_heartbeat_not_observed",
) -> dict[str, Any]:
    return {
        "schema_version": PROJECT_HEARTBEAT_SCHEMA,
        "surface_id": PROJECT_HEARTBEAT_SURFACE_ID,
        "status": status,
        "runtime_state": "degraded" if status == "degraded" else "not-run",
        "honest_status_label": (
            "core-substrate-heartbeat-degraded"
            if status == "degraded"
            else "core-substrate-heartbeat-not-observed"
        ),
        "trigger": "hive-forward-pass",
        "heartbeat_id": None,
        "source_run_id": None,
        "source_trace_ref": None,
        "session_ref_digest": session_ref_digest,
        "lane_count": 0,
        "alive_lane_count": 0,
        "degraded_lane_count": 0,
        "lanes": [],
        "blockers": [blocker],
        "evidence_refs": [],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": (
            "sanitized-project-heartbeat-status-counts-and-refs-only-no-prompts-outputs-session-ids-or-local-paths"
        ),
        "mutation_boundary": "heartbeat-status-and-artifact-refs-only-no-active-production-mutation",
    }


def release_project_heartbeat_from_substrate(
    hive_substrate: Any,
    *,
    session_id: str | None,
    session_ref_digest: str | None,
) -> dict[str, Any]:
    if hive_substrate is None or not hasattr(hive_substrate, "summary"):
        return empty_release_project_heartbeat(session_ref_digest=session_ref_digest)
    try:
        substrate_summary = hive_substrate.summary(session_id=session_id)
    except Exception as exc:  # pragma: no cover - defensive release status boundary
        return empty_release_project_heartbeat(
            session_ref_digest=session_ref_digest,
            status="degraded",
            blocker=f"hive_substrate_summary_unavailable::{type(exc).__name__}",
        )
    heartbeat = (
        substrate_summary.get("project_heartbeat")
        if isinstance(substrate_summary.get("project_heartbeat"), dict)
        else None
    )
    if not heartbeat:
        return empty_release_project_heartbeat(session_ref_digest=session_ref_digest)
    if (
        heartbeat.get("surface_id") != PROJECT_HEARTBEAT_SURFACE_ID
        or heartbeat.get("schema_version") != PROJECT_HEARTBEAT_SCHEMA
        or heartbeat.get("raw_content_included") is not False
        or heartbeat.get("active_production_mutation_allowed") is not False
        or heartbeat.get("active_production_mutated") is not False
    ):
        return empty_release_project_heartbeat(
            session_ref_digest=session_ref_digest,
            status="degraded",
            blocker="project_heartbeat_sanitization_or_contract_failed",
        )
    compact = json.loads(json.dumps(heartbeat, default=str))
    compact.pop("session_id", None)
    compact["session_ref_digest"] = session_ref_digest
    compact.setdefault("runtime_state", "live-bound" if compact.get("status") == "alive" else "degraded")
    compact.setdefault("evidence_refs", [])
    compact.setdefault("blockers", [])
    compact.setdefault("privacy_boundary", "sanitized-project-heartbeat-status-counts-and-refs-only")
    compact.setdefault("mutation_boundary", "heartbeat-status-and-artifact-refs-only-no-active-production-mutation")
    return compact


def compact_project_heartbeat_history_record(
    heartbeat: dict[str, Any],
    *,
    observed_at: str,
    artifact_ref: str = PROJECT_HEARTBEAT_HISTORY_REF,
) -> dict[str, Any]:
    heartbeat_id = str(heartbeat.get("heartbeat_id") or "")
    generated_at = str(heartbeat.get("generated_at") or observed_at)
    record_digest = _privacy_digest(
        json.dumps(
            {
                "heartbeat_id": heartbeat_id,
                "source_run_id": heartbeat.get("source_run_id"),
                "generated_at": generated_at,
            },
            sort_keys=True,
            default=str,
        )
    )
    lanes = [
        _compact_project_heartbeat_lane(lane)
        for lane in (heartbeat.get("lanes") if isinstance(heartbeat.get("lanes"), list) else [])
        if isinstance(lane, dict)
    ]
    return {
        "schema_version": PROJECT_HEARTBEAT_HISTORY_RECORD_SCHEMA,
        "surface_id": PROJECT_HEARTBEAT_HISTORY_RECORD_SURFACE_ID,
        "record_id": f"project-heartbeat-record::{_safe_ref(heartbeat_id) or record_digest[:24]}",
        "heartbeat_id": heartbeat_id,
        "status": str(heartbeat.get("status") or "unknown"),
        "runtime_state": str(
            heartbeat.get("runtime_state")
            or ("live-bound" if heartbeat.get("status") == "alive" else "degraded")
        ),
        "generated_at": generated_at,
        "observed_at": observed_at,
        "source_run_id": heartbeat.get("source_run_id"),
        "source_trace_ref": heartbeat.get("source_trace_ref"),
        "session_ref_digest": heartbeat.get("session_ref_digest"),
        "lane_count": int(heartbeat.get("lane_count") or len(lanes)),
        "alive_lane_count": int(heartbeat.get("alive_lane_count") or 0),
        "degraded_lane_count": int(heartbeat.get("degraded_lane_count") or 0),
        "degraded_lane_ids": [
            str(lane_id)
            for lane_id in (heartbeat.get("degraded_lane_ids") or [])
            if str(lane_id or "")
        ][:24],
        "lanes": lanes[:24],
        "failure_recovery_governance": compact_failure_recovery_governance(
            heartbeat.get("failure_recovery_governance")
        ),
        "evidence_refs": _dedupe_strings(
            [str(ref) for ref in (heartbeat.get("evidence_refs") or []) if str(ref or "")]
        )[:48],
        "artifact_ref": artifact_ref,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": (
            "sanitized-project-heartbeat-record-status-counts-and-artifact-refs-only-no-prompts-outputs-session-ids-or-local-paths"
        ),
        "mutation_boundary": "project-heartbeat-record-only-no-active-production-mutation",
    }


def is_replayable_project_heartbeat_record(record: dict[str, Any]) -> bool:
    return (
        isinstance(record, dict)
        and record.get("schema_version") == PROJECT_HEARTBEAT_HISTORY_RECORD_SCHEMA
        and record.get("surface_id") == PROJECT_HEARTBEAT_HISTORY_RECORD_SURFACE_ID
        and bool(record.get("record_id"))
        and bool(record.get("heartbeat_id"))
        and bool(record.get("session_ref_digest"))
        and bool(record.get("observed_at"))
        and record.get("raw_content_included") is False
        and record.get("active_production_mutation_allowed") is False
        and record.get("active_production_mutated") is False
    )


def project_heartbeat_replay_summary(
    records: list[dict[str, Any]],
    *,
    session_ref_digest: str | None,
    status: str | None = None,
    artifact_ref: str = PROJECT_HEARTBEAT_HISTORY_REF,
) -> dict[str, Any]:
    scoped_records = [
        record
        for record in records
        if is_replayable_project_heartbeat_record(record)
        and (not session_ref_digest or str(record.get("session_ref_digest") or "") == session_ref_digest)
    ]
    latest = scoped_records[0] if scoped_records else None
    replay_status = status or ("replayed" if scoped_records else "not-observed")
    return {
        "schema_version": PROJECT_HEARTBEAT_HISTORY_SCHEMA,
        "surface_id": PROJECT_HEARTBEAT_HISTORY_SURFACE_ID,
        "status": replay_status,
        "runtime_state": "replayed-history" if replay_status == "replayed" else replay_status,
        "session_ref_digest": session_ref_digest,
        "heartbeat_count": len(scoped_records),
        "global_heartbeat_count": len([record for record in records if is_replayable_project_heartbeat_record(record)]),
        "latest_heartbeat_id": latest.get("heartbeat_id") if latest else None,
        "latest_record_id": latest.get("record_id") if latest else None,
        "latest_status": latest.get("status") if latest else "not-run",
        "latest_record": latest,
        "records": scoped_records[:20],
        "artifact_ref": artifact_ref,
        "evidence_refs": _dedupe_strings(
            [
                str(latest.get("heartbeat_id") if latest else ""),
                str(latest.get("record_id") if latest else ""),
                artifact_ref,
            ]
        ),
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": (
            "sanitized-project-heartbeat-replay-status-counts-and-record-refs-only-no-prompts-outputs-session-ids-or-local-paths"
        ),
        "mutation_boundary": "replay-status-and-artifact-refs-only-no-active-production-mutation",
    }


def _compact_project_heartbeat_lane(lane: dict[str, Any]) -> dict[str, Any]:
    artifact_refs = lane.get("artifact_refs") or lane.get("evidence_refs") or []
    return {
        "lane_id": str(lane.get("lane_id") or ""),
        "status": str(lane.get("status") or "unknown"),
        "artifact_refs": _dedupe_strings([str(ref) for ref in artifact_refs if str(ref or "")])[:12],
        "blockers": _dedupe_strings(
            [str(blocker) for blocker in (lane.get("blockers") or []) if str(blocker or "")]
        )[:12],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value or "")
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _privacy_digest(value: str) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def _safe_ref(value: str) -> str:
    return str(value or "").replace(":", "_").replace("/", "_").replace("\\", "_")
