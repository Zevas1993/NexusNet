from __future__ import annotations

from typing import Any


def build_release_health_heartbeat_supervisor_pulse(
    *,
    schema_version: str,
    surface_id: str,
    state_artifact_ref: str,
    pulse_artifact_ref: str,
    pulse_id: str,
    generated_at: str,
    trigger: str,
    session_ref_digest: str | None,
    interval_seconds: int,
    loop: dict[str, Any],
) -> dict[str, Any]:
    failure_signal = (
        loop.get("failure_learning_signal")
        if isinstance(loop.get("failure_learning_signal"), dict)
        else {}
    )
    repair_queue = loop.get("repair_queue") if isinstance(loop.get("repair_queue"), dict) else {}
    pulse = {
        "schema_version": schema_version,
        "surface_id": surface_id,
        "pulse_id": pulse_id,
        "generated_at": generated_at,
        "authority": "NexusBrain",
        "status_label": "LOCKED CANON",
        "status": loop.get("status") or "unknown",
        "trigger": trigger,
        "loop_id": loop.get("loop_id"),
        "heartbeat_id": loop.get("latest_heartbeat_id"),
        "session_ref_digest": session_ref_digest,
        "manual_endpoint_used": False,
        "loop": loop,
        "failure_learning_signal_id": failure_signal.get("signal_id"),
        "repair_queue_status": repair_queue.get("status"),
        "timer": {
            "interval_seconds": interval_seconds,
            "sleep_performed": False,
            "background_thread_started": False,
            "scheduler_mode": "governed-product-path-due-tick",
        },
        "evidence_refs": [
            state_artifact_ref,
            pulse_artifact_ref,
            loop.get("loop_id"),
            loop.get("latest_heartbeat_id"),
            failure_signal.get("signal_id"),
        ],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": "sanitized-periodic-supervisor-pulse-and-loop-refs-only-no-prompts-outputs-session-ids-or-local-paths",
        "mutation_boundary": "periodic-supervisor-pulse-only-no-active-production-mutation",
    }
    pulse["evidence_refs"] = [str(ref) for ref in pulse["evidence_refs"] if str(ref or "")]
    return pulse
