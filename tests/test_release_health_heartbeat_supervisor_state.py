from __future__ import annotations

from datetime import datetime, timezone

from nexusnet.release_health_heartbeat_supervisor_state import (
    build_release_health_heartbeat_supervisor_configure_plan,
    build_release_health_heartbeat_supervisor_config_state,
    build_release_health_heartbeat_supervisor_default_state,
    build_release_health_heartbeat_supervisor_ticked_state,
)


def test_release_health_heartbeat_supervisor_default_state_is_sanitized_bounded_and_ref_linked() -> None:
    now = datetime(2026, 7, 3, 5, 0, tzinfo=timezone.utc)

    state = build_release_health_heartbeat_supervisor_default_state(
        current_state={
            "enabled": True,
            "interval_seconds": 9_999,
            "max_pulses_per_tick": 99,
            "configured_at": "2026-07-03T04:00:00+00:00",
            "configured_by_ref": "operator::admin-ref",
            "last_tick_at": "2026-07-03T04:30:00+00:00",
            "latest_pulse_id": "pulse-old",
            "latest_loop_id": "loop-old",
            "session_ref_digest": "sha256:session-a",
            "raw_content_included": True,
            "active_production_mutation_allowed": True,
            "active_production_mutated": True,
        },
        schema_version="nexusnet-release-wrapper-health-heartbeat-supervisor-v1",
        surface_id="release-wrapper-health-heartbeat-supervisor",
        state_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        pulse_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
        now=now,
    )

    assert state["schema_version"] == "nexusnet-release-wrapper-health-heartbeat-supervisor-v1"
    assert state["surface_id"] == "release-wrapper-health-heartbeat-supervisor"
    assert state["status"] == "enabled"
    assert state["enabled"] is True
    assert state["interval_seconds"] == 3600
    assert state["max_pulses_per_tick"] == 5
    assert state["configured_at"] == "2026-07-03T04:00:00+00:00"
    assert state["configured_by_ref"] == "operator::admin-ref"
    assert state["last_tick_at"] == "2026-07-03T04:30:00+00:00"
    assert state["next_due_at"] == "2026-07-03T06:00:00+00:00"
    assert state["latest_pulse_id"] == "pulse-old"
    assert state["latest_loop_id"] == "loop-old"
    assert state["session_ref_digest"] == "sha256:session-a"
    assert state["state_ref"] == "release-wrapper-runtime/release-health-heartbeat-supervisor.json"
    assert state["artifact_ref"] == "release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl"
    assert state["raw_content_included"] is False
    assert state["active_production_mutation_allowed"] is False
    assert state["active_production_mutated"] is False
    assert state["privacy_boundary"] == (
        "sanitized-release-health-supervisor-timers-status-counts-and-refs-only-no-prompts-outputs-session-ids-or-local-paths"
    )
    assert state["mutation_boundary"] == (
        "periodic-supervisor-status-and-safe-heartbeat-proposals-only-no-active-production-mutation"
    )


def test_release_health_heartbeat_supervisor_config_state_is_sanitized_and_bounded() -> None:
    configured_at = datetime(2026, 7, 3, 5, 0, tzinfo=timezone.utc)
    previous = {
        "schema_version": "nexusnet-release-wrapper-health-heartbeat-supervisor-v1",
        "surface_id": "release-wrapper-health-heartbeat-supervisor",
        "last_tick_at": "2026-07-03T04:58:00+00:00",
        "latest_pulse_id": "pulse-old",
        "latest_loop_id": "loop-old",
        "state_ref": "release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        "artifact_ref": "release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
    }

    state = build_release_health_heartbeat_supervisor_config_state(
        previous_state=previous,
        enabled=True,
        interval_seconds=9_999,
        max_pulses_per_tick=99,
        configured_at=configured_at,
        configured_by_ref="operator::admin-ref",
        session_ref_digest="sha256:session-a",
        schedule_immediately=False,
    )

    assert state["schema_version"] == "nexusnet-release-wrapper-health-heartbeat-supervisor-v1"
    assert state["surface_id"] == "release-wrapper-health-heartbeat-supervisor"
    assert state["status"] == "enabled"
    assert state["enabled"] is True
    assert state["interval_seconds"] == 3600
    assert state["max_pulses_per_tick"] == 5
    assert state["configured_at"] == "2026-07-03T05:00:00+00:00"
    assert state["configured_by_ref"] == "operator::admin-ref"
    assert state["last_tick_at"] == "2026-07-03T04:58:00+00:00"
    assert state["next_due_at"] == "2026-07-03T06:00:00+00:00"
    assert state["latest_pulse_id"] == "pulse-old"
    assert state["latest_loop_id"] == "loop-old"
    assert state["session_ref_digest"] == "sha256:session-a"
    assert state["raw_content_included"] is False
    assert state["active_production_mutation_allowed"] is False
    assert state["active_production_mutated"] is False


def test_release_health_heartbeat_supervisor_configure_plan_defaults_persists_and_schedules_immediately() -> None:
    configured_at = datetime(2026, 7, 3, 5, 0, tzinfo=timezone.utc)

    plan = build_release_health_heartbeat_supervisor_configure_plan(
        current_state={
            "latest_pulse_id": "pulse-old",
            "latest_loop_id": "loop-old",
            "last_tick_at": "2026-07-03T04:58:00+00:00",
        },
        schema_version="nexusnet-release-wrapper-health-heartbeat-supervisor-v1",
        surface_id="release-wrapper-health-heartbeat-supervisor",
        state_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        pulse_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
        enabled=True,
        interval_seconds=0,
        max_pulses_per_tick=99,
        configured_at=configured_at,
        configured_by_ref="operator::admin-ref",
        session_ref_digest="sha256:session-a",
        schedule_immediately=True,
    )

    state = plan["state"]

    assert plan["persist_state"] is True
    assert plan["summary_session_ref_digest"] == "session-a"
    assert plan["raw_content_included"] is False
    assert plan["active_production_mutation_allowed"] is False
    assert plan["active_production_mutated"] is False
    assert state["status"] == "enabled"
    assert state["enabled"] is True
    assert state["interval_seconds"] == 60
    assert state["max_pulses_per_tick"] == 5
    assert state["configured_at"] == "2026-07-03T05:00:00+00:00"
    assert state["configured_by_ref"] == "operator::admin-ref"
    assert state["last_tick_at"] == "2026-07-03T04:58:00+00:00"
    assert state["next_due_at"] == "2026-07-03T05:00:00+00:00"
    assert state["latest_pulse_id"] == "pulse-old"
    assert state["latest_loop_id"] == "loop-old"
    assert state["state_ref"] == "release-wrapper-runtime/release-health-heartbeat-supervisor.json"
    assert state["artifact_ref"] == "release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl"
    assert state["raw_content_included"] is False
    assert state["active_production_mutation_allowed"] is False
    assert state["active_production_mutated"] is False


def test_release_health_heartbeat_supervisor_ticked_state_advances_due_time_and_latest_refs() -> None:
    ticked_at = datetime(2026, 7, 3, 5, 30, tzinfo=timezone.utc)
    previous = {
        "schema_version": "nexusnet-release-wrapper-health-heartbeat-supervisor-v1",
        "surface_id": "release-wrapper-health-heartbeat-supervisor",
        "enabled": True,
        "interval_seconds": 60,
        "next_due_at": "2026-07-03T05:30:00+00:00",
        "session_ref_digest": "sha256:session-a",
    }
    latest_pulse = {
        "pulse_id": "pulse-new",
        "loop_id": "loop-new",
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
    }

    state = build_release_health_heartbeat_supervisor_ticked_state(
        previous_state=previous,
        ticked_at=ticked_at,
        interval_seconds=60,
        latest_pulse=latest_pulse,
    )

    assert state["enabled"] is True
    assert state["last_tick_at"] == "2026-07-03T05:30:00+00:00"
    assert state["next_due_at"] == "2026-07-03T05:31:00+00:00"
    assert state["latest_pulse_id"] == "pulse-new"
    assert state["latest_loop_id"] == "loop-new"
    assert state["session_ref_digest"] == "sha256:session-a"
    assert state["raw_content_included"] is False
    assert state["active_production_mutation_allowed"] is False
    assert state["active_production_mutated"] is False
