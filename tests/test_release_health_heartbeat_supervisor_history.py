from __future__ import annotations

from nexusnet.release_health_heartbeat_supervisor_history import (
    build_release_health_heartbeat_supervisor_repair_history,
)


def test_release_health_heartbeat_supervisor_repair_history_is_sanitized_and_replayable() -> None:
    def safe_ref(value: str) -> str:
        return f"safe::{value}"

    history = build_release_health_heartbeat_supervisor_repair_history(
        readiness_runs=[
            {
                "run_id": "run-1",
                "status": "completed-heartbeat-supervisor-repair",
                "session_ref_digest": "session-a",
                "update_id": "safe::update-1",
                "actions": {
                    "admin_approval": {"status": "approved"},
                    "shadow_eval_replay": {"status": "passed"},
                    "sandbox_tests": {"status": "passed"},
                    "apply": {"status": "applied"},
                    "rollback": {"status": "rolled-back"},
                },
                "active_production_mutated": False,
            },
            {
                "run_id": "run-2",
                "status": "completed-heartbeat-supervisor-repair",
                "session_ref_digest": "session-b",
                "update_id": "safe::update-2",
            },
        ],
        pulses=[
            {
                "pulse_id": "pulse-1",
                "loop_id": "loop-1",
                "heartbeat_id": "heartbeat-1",
                "loop": {"repair_queue": {"latest_update_id": "update-1"}},
            }
        ],
        session_ref_digest="session-a",
        safe_ref=safe_ref,
    )

    assert history["status"] == "recorded"
    assert history["scope"] == "session"
    assert history["repair_count"] == 1
    assert history["global_repair_count"] == 2
    assert history["latest_run_id"] == "run-1"
    assert history["latest_update_id"] == "update-1"
    assert history["latest_safe_update_id"] == "safe::update-1"
    assert history["latest_pulse_id"] == "pulse-1"
    assert history["latest_loop_id"] == "loop-1"
    assert history["latest_heartbeat_id"] == "heartbeat-1"
    assert history["raw_content_included"] is False
    assert history["active_production_mutation_allowed"] is False
    assert history["active_production_mutated"] is False
    assert history["repairs"][0]["action_statuses"] == {
        "admin_approval": "approved",
        "shadow_eval_replay": "passed",
        "sandbox_tests": "passed",
        "apply": "applied",
        "rollback": "rolled-back",
    }
