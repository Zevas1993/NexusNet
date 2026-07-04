from __future__ import annotations

from datetime import datetime, timezone

from nexusnet.release_health_heartbeat_supervisor_runtime import (
    build_release_health_heartbeat_supervisor_tick_plan,
    build_release_health_heartbeat_supervisor_pulse_batch,
    build_release_health_heartbeat_supervisor_summary,
    build_release_health_heartbeat_supervisor_summary_plan,
    build_release_health_heartbeat_supervisor_tick_result,
    release_health_heartbeat_supervisor_loop_trigger,
    release_health_heartbeat_supervisor_pulse_id,
    release_health_heartbeat_supervisor_tick_settings,
    release_health_heartbeat_supervisor_due_status,
)


def test_release_health_heartbeat_supervisor_due_status_tracks_schedule_and_invalid_due_time() -> None:
    now = datetime(2026, 7, 3, 6, 0, tzinfo=timezone.utc)

    assert release_health_heartbeat_supervisor_due_status({"enabled": False}, now=now) == "disabled"
    assert (
        release_health_heartbeat_supervisor_due_status(
            {"enabled": True, "next_due_at": "2026-07-03T06:01:00+00:00"},
            now=now,
        )
        == "scheduled"
    )
    assert (
        release_health_heartbeat_supervisor_due_status(
            {"enabled": True, "next_due_at": "2026-07-03T05:59:59+00:00"},
            now=now,
        )
        == "due"
    )
    assert (
        release_health_heartbeat_supervisor_due_status(
            {"enabled": True, "next_due_at": "not-a-timestamp"},
            now=now,
        )
        == "due"
    )


def test_release_health_heartbeat_supervisor_summary_is_scoped_sanitized_and_evidence_linked() -> None:
    state = {
        "schema_version": "nexusnet-release-wrapper-health-heartbeat-supervisor-v1",
        "surface_id": "release-wrapper-health-heartbeat-supervisor",
        "status": "enabled",
        "enabled": True,
        "interval_seconds": 30,
        "last_tick_at": "2026-07-03T05:59:30+00:00",
        "next_due_at": "2026-07-03T06:00:00+00:00",
        "latest_pulse_id": "state-pulse-old",
        "latest_loop_id": "state-loop-old",
    }
    pulses = [
        {
            "pulse_id": "pulse-other",
            "loop_id": "loop-other",
            "session_ref_digest": "sha256:session-b",
            "raw_content_included": False,
        },
        {
            "pulse_id": "pulse-a",
            "loop_id": "loop-a",
            "session_ref_digest": "sha256:session-a",
            "raw_content_included": False,
        },
    ]
    repair_history = {
        "surface_id": "release-health-heartbeat-supervisor-repair-history",
        "status": "recorded",
        "latest_run_id": "run-a",
        "raw_content_included": False,
    }

    summary = build_release_health_heartbeat_supervisor_summary(
        state=state,
        pulses=pulses,
        repair_history=repair_history,
        session_ref_digest="session-a",
        state_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        pulse_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
        now=datetime(2026, 7, 3, 6, 0, tzinfo=timezone.utc),
    )

    assert summary["runtime_state"] == "live-evidence"
    assert summary["next_due_status"] == "due"
    assert summary["pulse_count"] == 1
    assert summary["global_pulse_count"] == 2
    assert summary["latest_pulse_id"] == "pulse-a"
    assert summary["latest_loop_id"] == "loop-a"
    assert summary["latest_pulse"]["pulse_id"] == "pulse-a"
    assert summary["repair_history"]["latest_run_id"] == "run-a"
    assert summary["timer"] == {
        "interval_seconds": 30,
        "next_due_at": "2026-07-03T06:00:00+00:00",
        "last_tick_at": "2026-07-03T05:59:30+00:00",
        "sleep_performed": False,
        "background_thread_started": False,
        "scheduler_mode": "governed-product-path-due-tick",
    }
    assert summary["evidence_refs"] == [
        "/ops/wrapper/release-runtime",
        "/ops/wrapper/status-card",
        "/ops/wrapper/release-health-heartbeat/supervisor/configure",
        "release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        "release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
        "loop-a",
    ]
    assert summary["raw_content_included"] is False
    assert summary["active_production_mutation_allowed"] is False
    assert summary["active_production_mutated"] is False


def test_release_health_heartbeat_supervisor_summary_plan_assembles_scoped_repair_history() -> None:
    def safe_ref(value: str) -> str:
        return f"safe::{value}"

    plan = build_release_health_heartbeat_supervisor_summary_plan(
        state={
            "schema_version": "nexusnet-release-wrapper-health-heartbeat-supervisor-v1",
            "surface_id": "release-wrapper-health-heartbeat-supervisor",
            "status": "enabled",
            "enabled": True,
            "interval_seconds": 30,
            "last_tick_at": "2026-07-03T05:59:30+00:00",
            "next_due_at": "2026-07-03T06:00:00+00:00",
            "latest_pulse_id": "state-pulse-old",
            "latest_loop_id": "state-loop-old",
        },
        pulses=[
            {
                "pulse_id": "pulse-b",
                "loop_id": "loop-b",
                "heartbeat_id": "heartbeat-b",
                "session_ref_digest": "sha256:session-b",
                "loop": {"repair_queue": {"latest_update_id": "update-b"}},
                "raw_content_included": False,
            },
            {
                "pulse_id": "pulse-a",
                "loop_id": "loop-a",
                "heartbeat_id": "heartbeat-a",
                "session_ref_digest": "sha256:session-a",
                "loop": {"repair_queue": {"latest_update_id": "update-a"}},
                "raw_content_included": False,
            },
        ],
        readiness_runs=[
            {
                "run_id": "run-a",
                "status": "completed-heartbeat-supervisor-repair",
                "session_ref_digest": "session-a",
                "update_id": "safe::update-a",
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
                "run_id": "run-b",
                "status": "completed-heartbeat-supervisor-repair",
                "session_ref_digest": "session-b",
                "update_id": "safe::update-b",
            },
        ],
        session_ref_digest="session-a",
        state_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        pulse_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
        now=datetime(2026, 7, 3, 6, 0, tzinfo=timezone.utc),
        safe_ref=safe_ref,
    )

    summary = plan["summary"]

    assert plan["scoped_pulse_count"] == 1
    assert plan["global_pulse_count"] == 2
    assert plan["raw_content_included"] is False
    assert plan["active_production_mutation_allowed"] is False
    assert plan["active_production_mutated"] is False
    assert summary["pulse_count"] == 1
    assert summary["global_pulse_count"] == 2
    assert summary["latest_pulse_id"] == "pulse-a"
    assert summary["latest_loop_id"] == "loop-a"
    assert summary["repair_history"]["repair_count"] == 1
    assert summary["repair_history"]["global_repair_count"] == 2
    assert summary["repair_history"]["latest_run_id"] == "run-a"
    assert summary["repair_history"]["latest_update_id"] == "update-a"
    assert summary["repair_history"]["latest_safe_update_id"] == "safe::update-a"
    assert summary["repair_history"]["latest_pulse_id"] == "pulse-a"
    assert summary["repair_history"]["latest_loop_id"] == "loop-a"
    assert summary["repair_history"]["latest_heartbeat_id"] == "heartbeat-a"
    assert summary["repair_history"]["raw_content_included"] is False
    assert summary["repair_history"]["active_production_mutation_allowed"] is False
    assert summary["repair_history"]["active_production_mutated"] is False
    assert summary["evidence_refs"] == [
        "/ops/wrapper/release-runtime",
        "/ops/wrapper/status-card",
        "/ops/wrapper/release-health-heartbeat/supervisor/configure",
        "release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        "release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
        "loop-a",
    ]
    assert summary["raw_content_included"] is False
    assert summary["active_production_mutation_allowed"] is False
    assert summary["active_production_mutated"] is False


def test_release_health_heartbeat_supervisor_tick_helpers_are_bounded_and_sanitized() -> None:
    settings = release_health_heartbeat_supervisor_tick_settings(
        {"max_pulses_per_tick": 99, "interval_seconds": 0}
    )

    assert settings == {"max_pulses": 5, "interval_seconds": 60}
    assert release_health_heartbeat_supervisor_loop_trigger("wrapper-interaction-periodic") == (
        "periodic-wrapper-interaction-auto"
    )
    assert release_health_heartbeat_supervisor_loop_trigger("boot") == "periodic-boot"
    assert (
        release_health_heartbeat_supervisor_pulse_id(
            generated_at="2026-07-03T06:10:00+00:00",
            trigger="wrapper-interaction-periodic",
            loop_id_or_index="loop-a",
            digest=lambda value: f"digest::{value}",
        )
        == "release-health-heartbeat-supervisor-pulse::digest::2026-07-03T06:10:00+00:00wrapper-interaction-periodicloop-a"
    )

    disabled = build_release_health_heartbeat_supervisor_tick_result(
        summary={"status": "disabled", "raw_content_included": True},
        pulse_emitted=False,
        tick_result="disabled",
    )
    pulsed = build_release_health_heartbeat_supervisor_tick_result(
        summary={"status": "enabled"},
        pulse_emitted=True,
        tick_result="pulsed",
        emitted_pulse_count=3,
    )

    assert disabled["pulse_emitted"] is False
    assert disabled["tick_result"] == "disabled"
    assert disabled["raw_content_included"] is False
    assert disabled["active_production_mutation_allowed"] is False
    assert disabled["active_production_mutated"] is False
    assert "emitted_pulse_count" not in disabled
    assert pulsed["pulse_emitted"] is True
    assert pulsed["tick_result"] == "pulsed"
    assert pulsed["emitted_pulse_count"] == 3
    assert pulsed["raw_content_included"] is False
    assert pulsed["active_production_mutation_allowed"] is False
    assert pulsed["active_production_mutated"] is False


def test_release_health_heartbeat_supervisor_pulse_batch_builds_sanitized_linked_pulses() -> None:
    batch = build_release_health_heartbeat_supervisor_pulse_batch(
        schema_version="nexusnet-release-wrapper-health-heartbeat-supervisor-v1",
        surface_id="release-wrapper-health-heartbeat-supervisor",
        state_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        pulse_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
        trigger="wrapper-interaction-periodic",
        session_ref_digest="sha256:session-a",
        interval_seconds=5,
        generated_loops=[
            {
                "index": 0,
                "generated_at": "2026-07-03T06:10:00+00:00",
                "loop": {
                    "loop_id": "loop-a",
                    "latest_heartbeat_id": "heartbeat-a",
                    "status": "proposal-routed",
                    "failure_learning_signal": {"signal_id": "signal-a", "raw_content_included": False},
                    "repair_queue": {"status": "proposal-routed"},
                },
            },
            {
                "index": 1,
                "generated_at": "2026-07-03T06:10:01+00:00",
                "loop": {
                    "latest_heartbeat_id": "heartbeat-b",
                    "status": "ok",
                    "failure_learning_signal": {"signal_id": "signal-b", "raw_content_included": False},
                    "repair_queue": {"status": "not-required"},
                },
            },
        ],
        digest=lambda value: f"digest::{value}",
    )

    pulses = batch["pulses"]

    assert batch["emitted_pulse_count"] == 2
    assert batch["latest_pulse"]["heartbeat_id"] == "heartbeat-b"
    assert pulses[0]["pulse_id"] == (
        "release-health-heartbeat-supervisor-pulse::digest::"
        "2026-07-03T06:10:00+00:00wrapper-interaction-periodicloop-a"
    )
    assert pulses[1]["pulse_id"] == (
        "release-health-heartbeat-supervisor-pulse::digest::"
        "2026-07-03T06:10:01+00:00wrapper-interaction-periodic1"
    )
    assert pulses[0]["trigger"] == "wrapper-interaction-periodic"
    assert pulses[0]["session_ref_digest"] == "sha256:session-a"
    assert pulses[0]["manual_endpoint_used"] is False
    assert pulses[0]["loop_id"] == "loop-a"
    assert pulses[1]["loop_id"] is None
    assert pulses[1]["heartbeat_id"] == "heartbeat-b"
    assert pulses[0]["timer"]["interval_seconds"] == 5
    assert pulses[0]["evidence_refs"] == [
        "release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        "release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
        "loop-a",
        "heartbeat-a",
        "signal-a",
    ]
    assert batch["raw_content_included"] is False
    assert batch["active_production_mutation_allowed"] is False
    assert batch["active_production_mutated"] is False
    assert all(pulse["raw_content_included"] is False for pulse in pulses)
    assert all(pulse["active_production_mutation_allowed"] is False for pulse in pulses)


def test_release_health_heartbeat_supervisor_tick_plan_runs_due_loops_and_shapes_persistence_plan() -> None:
    now_values = iter(
        [
            datetime(2026, 7, 3, 6, 0, tzinfo=timezone.utc),
            datetime(2026, 7, 3, 6, 0, 1, tzinfo=timezone.utc),
            datetime(2026, 7, 3, 6, 0, 2, tzinfo=timezone.utc),
            datetime(2026, 7, 3, 6, 0, 3, tzinfo=timezone.utc),
            datetime(2026, 7, 3, 6, 0, 4, tzinfo=timezone.utc),
        ]
    )
    loop_calls: list[dict[str, object]] = []

    def now() -> datetime:
        return next(now_values)

    def run_loop(options: dict[str, object]) -> dict[str, object]:
        loop_calls.append(dict(options))
        return {
            "schema_version": "nexusnet-release-wrapper-health-heartbeat-loop-v1",
            "loop_id": f"loop-{options['index']}",
            "latest_heartbeat_id": f"heartbeat-{options['index']}",
            "status": "proposal-routed",
            "failure_learning_signal": {
                "signal_id": f"signal-{options['index']}",
                "raw_content_included": False,
            },
            "repair_queue": {"status": "proposal-routed"},
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        }

    plan = build_release_health_heartbeat_supervisor_tick_plan(
        state={
            "schema_version": "nexusnet-release-wrapper-health-heartbeat-supervisor-v1",
            "surface_id": "release-wrapper-health-heartbeat-supervisor",
            "status": "enabled",
            "enabled": True,
            "interval_seconds": 5,
            "max_pulses_per_tick": 2,
            "next_due_at": "2026-07-03T05:59:59+00:00",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        },
        pulses=[],
        repair_history={"surface_id": "repair-history", "raw_content_included": False},
        session_ref_digest="session-a",
        trigger="wrapper-interaction-periodic",
        schema_version="nexusnet-release-wrapper-health-heartbeat-supervisor-v1",
        surface_id="release-wrapper-health-heartbeat-supervisor",
        loop_schema_version="nexusnet-release-wrapper-health-heartbeat-loop-v1",
        state_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        pulse_artifact_ref="release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
        now=now,
        digest=lambda value: f"digest::{value}",
        run_loop=run_loop,
    )

    assert loop_calls == [
        {
            "index": 0,
            "trigger": "periodic-wrapper-interaction-auto",
            "interval_seconds": 5,
        },
        {
            "index": 1,
            "trigger": "periodic-wrapper-interaction-auto",
            "interval_seconds": 5,
        },
    ]
    assert plan["tick_result"] == "pulsed"
    assert plan["persist_state"] is True
    assert plan["persist_summary"] is True
    assert len(plan["pulses"]) == 2
    assert len(plan["all_pulses"]) == 2
    assert plan["state"]["last_tick_at"] == "2026-07-03T06:00:03+00:00"
    assert plan["state"]["next_due_at"] == "2026-07-03T06:00:08+00:00"
    assert plan["state"]["latest_pulse_id"] == plan["pulses"][-1]["pulse_id"]
    assert plan["summary"]["latest_pulse_id"] == plan["pulses"][-1]["pulse_id"]
    assert plan["result"]["tick_result"] == "pulsed"
    assert plan["result"]["pulse_emitted"] is True
    assert plan["result"]["emitted_pulse_count"] == 2
    assert plan["result"]["raw_content_included"] is False
    assert all(pulse["session_ref_digest"] == "sha256:session-a" for pulse in plan["pulses"])
    assert all(pulse["manual_endpoint_used"] is False for pulse in plan["pulses"])


def test_release_health_heartbeat_supervisor_tick_plan_skips_disabled_and_not_due_without_loop_calls() -> None:
    loop_calls: list[dict[str, object]] = []

    def run_loop(options: dict[str, object]) -> dict[str, object]:
        loop_calls.append(dict(options))
        return {}

    common = {
        "pulses": [],
        "repair_history": {"surface_id": "repair-history", "raw_content_included": False},
        "session_ref_digest": "session-a",
        "trigger": "wrapper-interaction-periodic",
        "schema_version": "nexusnet-release-wrapper-health-heartbeat-supervisor-v1",
        "surface_id": "release-wrapper-health-heartbeat-supervisor",
        "loop_schema_version": "nexusnet-release-wrapper-health-heartbeat-loop-v1",
        "state_artifact_ref": "release-wrapper-runtime/release-health-heartbeat-supervisor.json",
        "pulse_artifact_ref": "release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
        "now": lambda: datetime(2026, 7, 3, 6, 0, tzinfo=timezone.utc),
        "digest": lambda value: f"digest::{value}",
        "run_loop": run_loop,
    }

    disabled = build_release_health_heartbeat_supervisor_tick_plan(
        state={"enabled": False, "status": "disabled"},
        **common,
    )
    not_due = build_release_health_heartbeat_supervisor_tick_plan(
        state={
            "enabled": True,
            "status": "enabled",
            "next_due_at": "2026-07-03T06:01:00+00:00",
        },
        **common,
    )

    assert loop_calls == []
    assert disabled["tick_result"] == "disabled"
    assert disabled["persist_state"] is False
    assert disabled["persist_summary"] is False
    assert disabled["result"]["pulse_emitted"] is False
    assert not_due["tick_result"] == "not-due"
    assert not_due["persist_state"] is False
    assert not_due["persist_summary"] is False
    assert not_due["result"]["pulse_emitted"] is False
