from __future__ import annotations

import json

from nexusnet.release_health_heartbeat_supervisor_storage import (
    append_release_health_heartbeat_supervisor_pulse,
    is_replayable_release_health_heartbeat_supervisor_pulse,
    is_replayable_release_health_heartbeat_supervisor_state,
    load_release_health_heartbeat_supervisor_pulses,
    load_release_health_heartbeat_supervisor_state,
    write_release_health_heartbeat_supervisor_state,
)


SUPERVISOR_SCHEMA = "nexusnet-release-wrapper-health-heartbeat-supervisor-v1"
SUPERVISOR_SURFACE_ID = "release-wrapper-health-heartbeat-supervisor"
LOOP_SCHEMA = "nexusnet-release-wrapper-health-heartbeat-loop-v1"


def _state(**overrides: object) -> dict[str, object]:
    state: dict[str, object] = {
        "schema_version": SUPERVISOR_SCHEMA,
        "surface_id": SUPERVISOR_SURFACE_ID,
        "status": "enabled",
        "enabled": True,
        "interval_seconds": 60,
        "max_pulses_per_tick": 1,
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }
    state.update(overrides)
    return state


def _pulse(index: int, **overrides: object) -> dict[str, object]:
    pulse: dict[str, object] = {
        "schema_version": SUPERVISOR_SCHEMA,
        "surface_id": SUPERVISOR_SURFACE_ID,
        "pulse_id": f"release-health-heartbeat-supervisor-pulse::{index}",
        "loop_id": f"release-health-heartbeat-loop::{index}",
        "manual_endpoint_used": False,
        "loop": {
            "schema_version": LOOP_SCHEMA,
            "loop_id": f"release-health-heartbeat-loop::{index}",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        },
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }
    pulse.update(overrides)
    return pulse


def test_release_health_heartbeat_supervisor_state_round_trips_primary_and_public_paths(tmp_path) -> None:
    primary = tmp_path / "private" / "supervisor.json"
    public = tmp_path / "public" / "supervisor.json"
    state = _state(session_ref_digest="sha256:session-a")

    write_release_health_heartbeat_supervisor_state(
        state,
        primary_path=primary,
        public_path=public,
    )

    assert json.loads(primary.read_text(encoding="utf-8")) == state
    assert json.loads(public.read_text(encoding="utf-8")) == state
    assert load_release_health_heartbeat_supervisor_state(
        candidate_paths=[primary, public],
        schema_version=SUPERVISOR_SCHEMA,
        surface_id=SUPERVISOR_SURFACE_ID,
    ) == state


def test_release_health_heartbeat_supervisor_state_loader_falls_back_to_sanitized_public_record(
    tmp_path,
) -> None:
    private = tmp_path / "private" / "supervisor.json"
    public = tmp_path / "public" / "supervisor.json"
    private.parent.mkdir(parents=True)
    public.parent.mkdir(parents=True)
    private.write_text("{not-json", encoding="utf-8")
    public_state = _state(status="disabled", enabled=False)
    public.write_text(json.dumps(public_state), encoding="utf-8")

    assert load_release_health_heartbeat_supervisor_state(
        candidate_paths=[private, public],
        schema_version=SUPERVISOR_SCHEMA,
        surface_id=SUPERVISOR_SURFACE_ID,
    ) == public_state


def test_release_health_heartbeat_supervisor_pulse_log_filters_and_caps_replay(tmp_path) -> None:
    primary = tmp_path / "private" / "supervisor.jsonl"
    public = tmp_path / "public" / "supervisor.jsonl"
    primary.parent.mkdir(parents=True)
    primary.write_text("{bad-json\n", encoding="utf-8")

    for index in range(105):
        append_release_health_heartbeat_supervisor_pulse(
            _pulse(index),
            primary_path=public,
        )
    append_release_health_heartbeat_supervisor_pulse(
        _pulse(106, raw_content_included=True),
        primary_path=public,
    )
    append_release_health_heartbeat_supervisor_pulse(
        _pulse(107, active_production_mutated=True),
        primary_path=public,
    )

    pulses = load_release_health_heartbeat_supervisor_pulses(
        candidate_paths=[primary, public],
        schema_version=SUPERVISOR_SCHEMA,
        surface_id=SUPERVISOR_SURFACE_ID,
        loop_schema_version=LOOP_SCHEMA,
        limit=100,
    )

    assert len(pulses) == 100
    assert pulses[0]["pulse_id"] == "release-health-heartbeat-supervisor-pulse::5"
    assert pulses[-1]["pulse_id"] == "release-health-heartbeat-supervisor-pulse::104"
    assert all(pulse["raw_content_included"] is False for pulse in pulses)
    assert all(pulse["active_production_mutated"] is False for pulse in pulses)


def test_release_health_heartbeat_supervisor_replay_guards_reject_unsafe_records() -> None:
    assert is_replayable_release_health_heartbeat_supervisor_state(
        _state(),
        schema_version=SUPERVISOR_SCHEMA,
        surface_id=SUPERVISOR_SURFACE_ID,
    )
    assert not is_replayable_release_health_heartbeat_supervisor_state(
        _state(raw_content_included=True),
        schema_version=SUPERVISOR_SCHEMA,
        surface_id=SUPERVISOR_SURFACE_ID,
    )
    assert not is_replayable_release_health_heartbeat_supervisor_state(
        _state(status="pending"),
        schema_version=SUPERVISOR_SCHEMA,
        surface_id=SUPERVISOR_SURFACE_ID,
    )

    assert is_replayable_release_health_heartbeat_supervisor_pulse(
        _pulse(1),
        schema_version=SUPERVISOR_SCHEMA,
        surface_id=SUPERVISOR_SURFACE_ID,
        loop_schema_version=LOOP_SCHEMA,
    )
    assert not is_replayable_release_health_heartbeat_supervisor_pulse(
        _pulse(1, manual_endpoint_used=True),
        schema_version=SUPERVISOR_SCHEMA,
        surface_id=SUPERVISOR_SURFACE_ID,
        loop_schema_version=LOOP_SCHEMA,
    )
    assert not is_replayable_release_health_heartbeat_supervisor_pulse(
        _pulse(
            1,
            loop={
                "schema_version": LOOP_SCHEMA,
                "raw_content_included": True,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            },
        ),
        schema_version=SUPERVISOR_SCHEMA,
        surface_id=SUPERVISOR_SURFACE_ID,
        loop_schema_version=LOOP_SCHEMA,
    )
