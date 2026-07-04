from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


def _bounded_interval_seconds(value: int) -> int:
    return max(1, min(int(value or 60), 3600))


def _bounded_max_pulses(value: int) -> int:
    return max(1, min(int(value or 1), 5))


def build_release_health_heartbeat_supervisor_default_state(
    *,
    current_state: dict[str, Any],
    schema_version: str,
    surface_id: str,
    state_artifact_ref: str,
    pulse_artifact_ref: str,
    now: datetime,
) -> dict[str, Any]:
    state = dict(current_state) if isinstance(current_state, dict) else {}
    interval_seconds = _bounded_interval_seconds(state.get("interval_seconds") or 60)
    next_due_at = str(state.get("next_due_at") or (now + timedelta(seconds=interval_seconds)).isoformat())
    enabled = bool(state.get("enabled"))
    return {
        "schema_version": schema_version,
        "surface_id": surface_id,
        "status": "enabled" if enabled else "disabled",
        "enabled": enabled,
        "interval_seconds": interval_seconds,
        "max_pulses_per_tick": _bounded_max_pulses(state.get("max_pulses_per_tick") or 1),
        "configured_at": str(state.get("configured_at") or now.isoformat()),
        "configured_by_ref": str(state.get("configured_by_ref") or "operator::unconfigured"),
        "last_tick_at": state.get("last_tick_at"),
        "next_due_at": next_due_at,
        "latest_pulse_id": state.get("latest_pulse_id"),
        "latest_loop_id": state.get("latest_loop_id"),
        "session_ref_digest": state.get("session_ref_digest"),
        "artifact_ref": pulse_artifact_ref,
        "state_ref": state_artifact_ref,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": "sanitized-release-health-supervisor-timers-status-counts-and-refs-only-no-prompts-outputs-session-ids-or-local-paths",
        "mutation_boundary": "periodic-supervisor-status-and-safe-heartbeat-proposals-only-no-active-production-mutation",
    }


def build_release_health_heartbeat_supervisor_configure_plan(
    *,
    current_state: dict[str, Any],
    schema_version: str,
    surface_id: str,
    state_artifact_ref: str,
    pulse_artifact_ref: str,
    enabled: bool,
    interval_seconds: int,
    max_pulses_per_tick: int,
    configured_at: datetime,
    configured_by_ref: str,
    session_ref_digest: str | None,
    schedule_immediately: bool,
) -> dict[str, Any]:
    previous = build_release_health_heartbeat_supervisor_default_state(
        current_state=current_state,
        schema_version=schema_version,
        surface_id=surface_id,
        state_artifact_ref=state_artifact_ref,
        pulse_artifact_ref=pulse_artifact_ref,
        now=configured_at,
    )
    state = build_release_health_heartbeat_supervisor_config_state(
        previous_state=previous,
        enabled=enabled,
        interval_seconds=interval_seconds,
        max_pulses_per_tick=max_pulses_per_tick,
        configured_at=configured_at,
        configured_by_ref=configured_by_ref,
        session_ref_digest=session_ref_digest,
        schedule_immediately=schedule_immediately,
    )
    summary_session_ref_digest = None
    if session_ref_digest:
        summary_session_ref_digest = str(session_ref_digest).removeprefix("sha256:")
    return {
        "state": state,
        "persist_state": True,
        "summary_session_ref_digest": summary_session_ref_digest,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def build_release_health_heartbeat_supervisor_config_state(
    *,
    previous_state: dict[str, Any],
    enabled: bool,
    interval_seconds: int,
    max_pulses_per_tick: int,
    configured_at: datetime,
    configured_by_ref: str,
    session_ref_digest: str | None,
    schedule_immediately: bool,
) -> dict[str, Any]:
    bounded_interval = _bounded_interval_seconds(interval_seconds)
    bounded_pulses = _bounded_max_pulses(max_pulses_per_tick)
    next_due_at = configured_at if schedule_immediately else configured_at + timedelta(seconds=bounded_interval)
    return {
        **previous_state,
        "status": "enabled" if enabled else "disabled",
        "enabled": bool(enabled),
        "interval_seconds": bounded_interval,
        "max_pulses_per_tick": bounded_pulses,
        "configured_at": configured_at.isoformat(),
        "configured_by_ref": configured_by_ref,
        "last_tick_at": previous_state.get("last_tick_at"),
        "next_due_at": next_due_at.isoformat(),
        "session_ref_digest": session_ref_digest,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def build_release_health_heartbeat_supervisor_ticked_state(
    *,
    previous_state: dict[str, Any],
    ticked_at: datetime,
    interval_seconds: int,
    latest_pulse: dict[str, Any],
) -> dict[str, Any]:
    bounded_interval = _bounded_interval_seconds(interval_seconds)
    return {
        **previous_state,
        "last_tick_at": ticked_at.isoformat(),
        "next_due_at": (ticked_at + timedelta(seconds=bounded_interval)).isoformat(),
        "latest_pulse_id": latest_pulse.get("pulse_id"),
        "latest_loop_id": latest_pulse.get("loop_id"),
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }
