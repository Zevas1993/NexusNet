from __future__ import annotations

from typing import Any


PROJECT_HEARTBEAT_NATIVE_RECORD_SCHEMA = "nexusnet-native-project-heartbeat-record-v1"
PROJECT_HEARTBEAT_NATIVE_RECORD_SURFACE_ID = "hive-native-project-heartbeat-record"
PROJECT_HEARTBEAT_NATIVE_REPLAY_REF = "hive-substrate/project-heartbeats/_index.jsonl"

_UNSAFE_REF_MARKERS = (
    "raw-prompt",
    "raw-output",
    "secret",
    "token",
    "password",
    "api-key",
    "apikey",
)


def native_project_heartbeat_record(
    *,
    record_id: str,
    heartbeat: dict[str, Any],
    recorded_at: str,
) -> dict[str, Any]:
    lanes = [
        compact_project_heartbeat_lane_for_native_record(lane)
        for lane in (heartbeat.get("lanes") if isinstance(heartbeat.get("lanes"), list) else [])
        if isinstance(lane, dict)
    ]
    failure_recovery_governance = compact_failure_recovery_governance(
        heartbeat.get("failure_recovery_governance")
    )
    return {
        "schema_version": PROJECT_HEARTBEAT_NATIVE_RECORD_SCHEMA,
        "surface_id": PROJECT_HEARTBEAT_NATIVE_RECORD_SURFACE_ID,
        "record_id": record_id,
        "replay_ref": PROJECT_HEARTBEAT_NATIVE_REPLAY_REF,
        "heartbeat_id": heartbeat.get("heartbeat_id"),
        "status": str(heartbeat.get("status") or "unknown"),
        "runtime_state": str(
            heartbeat.get("runtime_state")
            or ("live-bound" if heartbeat.get("status") == "alive" else "degraded")
        ),
        "generated_at": heartbeat.get("generated_at") or recorded_at,
        "recorded_at": recorded_at,
        "source_run_id": heartbeat.get("source_run_id"),
        "source_trace_ref": heartbeat.get("source_trace_ref"),
        "session_id": None,
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
        "failure_recovery_governance": failure_recovery_governance,
        "evidence_refs": sanitized_artifact_refs(heartbeat.get("evidence_refs"))[:48],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": (
            "native-project-heartbeat-record-status-counts-and-artifact-refs-only-no-prompts-outputs-session-ids-or-local-paths"
        ),
        "mutation_boundary": "native-project-heartbeat-record-only-no-active-production-mutation",
    }


def compact_failure_recovery_governance(governance: Any) -> dict[str, Any]:
    if not isinstance(governance, dict):
        return {
            "surface_id": "native-project-heartbeat-failure-recovery-governance",
            "status": "not-emitted",
            "runtime_state": "unknown",
            "blocked_forward_pass": False,
            "self_healing_route_available": False,
            "admin_governance_required": False,
            "sandbox_eval_required": False,
            "rollback_required": False,
            "recovery_action": "not-emitted",
            "policy_allow_merge": False,
            "immune_finding_count": 0,
            "evidence_refs": [],
            "operator_governance_boundary": "native-heartbeat-record-only",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }
    return {
        "surface_id": str(
            governance.get("surface_id") or "native-project-heartbeat-failure-recovery-governance"
        ),
        "authority": str(governance.get("authority") or "NexusBrain"),
        "status": str(governance.get("status") or "unknown"),
        "runtime_state": str(governance.get("runtime_state") or "unknown"),
        "blocked_forward_pass": bool(governance.get("blocked_forward_pass")),
        "self_healing_route_available": bool(governance.get("self_healing_route_available")),
        "admin_governance_required": bool(governance.get("admin_governance_required")),
        "sandbox_eval_required": bool(governance.get("sandbox_eval_required")),
        "rollback_required": bool(governance.get("rollback_required")),
        "recovery_action": str(governance.get("recovery_action") or ""),
        "policy_allow_merge": governance.get("policy_allow_merge") is True,
        "immune_finding_count": int(governance.get("immune_finding_count") or 0),
        "evidence_refs": sanitized_artifact_refs(governance.get("evidence_refs"))[:24],
        "operator_governance_boundary": str(governance.get("operator_governance_boundary") or ""),
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def attach_native_project_heartbeat_replay(
    heartbeat: dict[str, Any],
    native_record: dict[str, Any],
) -> dict[str, Any]:
    record_id = str(native_record.get("record_id") or "")
    heartbeat["native_replay_ref"] = PROJECT_HEARTBEAT_NATIVE_REPLAY_REF
    heartbeat["native_replay_record_id"] = record_id
    heartbeat["native_replay_surface_id"] = PROJECT_HEARTBEAT_NATIVE_RECORD_SURFACE_ID
    heartbeat["runtime_state"] = heartbeat.get("runtime_state") or (
        "live-bound" if heartbeat.get("status") == "alive" else "degraded"
    )
    heartbeat["evidence_refs"] = dedupe_strings(
        [
            *sanitized_artifact_refs(heartbeat.get("evidence_refs")),
            PROJECT_HEARTBEAT_NATIVE_REPLAY_REF,
            record_id,
        ]
    )[:48]
    for lane in heartbeat.get("lanes") or []:
        if isinstance(lane, dict):
            lane["artifact_refs"] = sanitized_artifact_refs(lane.get("artifact_refs"))[:12]
        if isinstance(lane, dict) and lane.get("lane_id") == "storage-replay":
            lane["artifact_refs"] = dedupe_strings(
                [
                    *sanitized_artifact_refs(lane.get("artifact_refs")),
                    PROJECT_HEARTBEAT_NATIVE_REPLAY_REF,
                    record_id,
                ]
            )[:12]
    return heartbeat


def compact_project_heartbeat_lane_for_native_record(lane: dict[str, Any]) -> dict[str, Any]:
    blockers = lane.get("blockers") if isinstance(lane.get("blockers"), list) else []
    return {
        "lane_id": str(lane.get("lane_id") or ""),
        "status": str(lane.get("status") or "unknown"),
        "artifact_refs": sanitized_artifact_refs(lane.get("artifact_refs"))[:12],
        "blockers": dedupe_strings([str(blocker) for blocker in blockers if str(blocker or "")])[:12],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def sanitized_artifact_refs(values: Any) -> list[str]:
    if isinstance(values, str):
        candidates = [values]
    elif isinstance(values, list):
        candidates = values
    else:
        candidates = []
    return dedupe_strings(
        [
            str(value)
            for value in candidates
            if str(value or "").strip() and not _contains_unsafe_ref_marker(str(value))
        ]
    )


def dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _contains_unsafe_ref_marker(value: str) -> bool:
    normalized = value.lower()
    return any(marker in normalized for marker in _UNSAFE_REF_MARKERS)
