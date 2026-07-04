from __future__ import annotations

from nexusnet.release_health_heartbeat_supervisor_pulse import (
    build_release_health_heartbeat_supervisor_pulse,
)


def test_release_health_heartbeat_supervisor_pulse_is_sanitized_and_links_loop_evidence() -> None:
    loop = {
        "loop_id": "release-health-heartbeat-loop::abc",
        "status": "blocked",
        "latest_heartbeat_id": "heartbeat-1",
        "failure_learning_signal": {
            "signal_id": "signal-1",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        },
        "repair_queue": {
            "status": "proposal-routed",
            "latest_update_id": "update::repair-1",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        },
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }

    pulse = build_release_health_heartbeat_supervisor_pulse(
        schema_version="nexusnet-release-wrapper-health-heartbeat-supervisor-v1",
        surface_id="release-wrapper-health-heartbeat-supervisor",
        state_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        pulse_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
        pulse_id="release-health-heartbeat-supervisor-pulse::abc",
        generated_at="2026-07-03T04:30:00+00:00",
        trigger="wrapper-interaction-periodic",
        session_ref_digest="sha256:session-a",
        interval_seconds=1,
        loop=loop,
    )

    assert pulse["schema_version"] == "nexusnet-release-wrapper-health-heartbeat-supervisor-v1"
    assert pulse["surface_id"] == "release-wrapper-health-heartbeat-supervisor"
    assert pulse["pulse_id"] == "release-health-heartbeat-supervisor-pulse::abc"
    assert pulse["status"] == "blocked"
    assert pulse["trigger"] == "wrapper-interaction-periodic"
    assert pulse["loop_id"] == "release-health-heartbeat-loop::abc"
    assert pulse["heartbeat_id"] == "heartbeat-1"
    assert pulse["session_ref_digest"] == "sha256:session-a"
    assert pulse["manual_endpoint_used"] is False
    assert pulse["loop"] == loop
    assert pulse["failure_learning_signal_id"] == "signal-1"
    assert pulse["repair_queue_status"] == "proposal-routed"
    assert pulse["timer"] == {
        "interval_seconds": 1,
        "sleep_performed": False,
        "background_thread_started": False,
        "scheduler_mode": "governed-product-path-due-tick",
    }
    assert pulse["evidence_refs"] == [
        "release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        "release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
        "release-health-heartbeat-loop::abc",
        "heartbeat-1",
        "signal-1",
    ]
    assert pulse["raw_content_included"] is False
    assert pulse["active_production_mutation_allowed"] is False
    assert pulse["active_production_mutated"] is False
