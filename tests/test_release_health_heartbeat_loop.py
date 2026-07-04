from __future__ import annotations

from nexusnet.release_health_heartbeat_loop import build_release_health_heartbeat_loop_record


def test_release_health_heartbeat_loop_record_is_sanitized_and_tracks_blocked_repair_queue() -> None:
    record = build_release_health_heartbeat_loop_record(
        schema_version="nexusnet-release-wrapper-health-heartbeat-loop-v1",
        surface_id="release-wrapper-health-heartbeat-loop",
        artifact_ref="release-wrapper-runtime/release-health-heartbeat-loop.jsonl",
        heartbeat_artifact_ref="release-wrapper-runtime/release-health-heartbeat.jsonl",
        loop_id="release-health-heartbeat-loop::abc",
        generated_at="2026-07-03T04:00:00+00:00",
        next_due_at="2026-07-03T04:01:00+00:00",
        trigger="startup-auto",
        session_ref_digest="sha256:session-a",
        bounded_cycles=2,
        bounded_interval=60,
        bounded_retry_attempts=2,
        cycles=[
            {
                "cycle_index": 1,
                "status": "healthy",
                "heartbeat_id": "heartbeat-1",
                "blocked": False,
            },
            {
                "cycle_index": 2,
                "status": "blocked",
                "heartbeat_id": "heartbeat-2",
                "blocked": True,
            },
        ],
        blocked_cycles=[
            {
                "cycle_index": 2,
                "status": "blocked",
                "heartbeat_id": "heartbeat-2",
                "blocked": True,
            }
        ],
        backoff_seconds=[5],
        repair_queue={
            "status": "proposal-routed",
            "latest_update_id": "update::repair-1",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        },
        failure_learning_signal={
            "status": "recorded",
            "signal_id": "signal-1",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        },
    )

    assert record["schema_version"] == "nexusnet-release-wrapper-health-heartbeat-loop-v1"
    assert record["surface_id"] == "release-wrapper-health-heartbeat-loop"
    assert record["status"] == "blocked"
    assert record["runtime_state"] == "live-evidence"
    assert record["cycle_count"] == 2
    assert record["latest_heartbeat_id"] == "heartbeat-2"
    assert record["timer"] == {
        "interval_seconds": 60,
        "started_at": "2026-07-03T04:00:00+00:00",
        "next_due_at": "2026-07-03T04:01:00+00:00",
        "sleep_performed": False,
        "background_thread_started": False,
        "scheduler_mode": "bounded-sync-supervisor-run",
    }
    assert record["bounded_retry"] == {
        "bounded": True,
        "max_retry_attempts": 2,
        "attempt_count": 1,
        "backoff_seconds": [5],
        "policy": "exponential-backoff-recorded-no-sleep-no-active-production-mutation",
    }
    assert record["repair_queue"]["latest_update_id"] == "update::repair-1"
    assert record["failure_learning_signal"]["signal_id"] == "signal-1"
    assert record["evidence_refs"] == [
        "/ops/wrapper/release-runtime",
        "/ops/wrapper/release-readiness",
        "/ops/wrapper/release-health-heartbeat/run",
        "release-wrapper-runtime/release-health-heartbeat.jsonl",
        "signal-1",
    ]
    assert record["raw_content_included"] is False
    assert record["active_production_mutation_allowed"] is False
    assert record["active_production_mutated"] is False


def test_release_health_heartbeat_loop_record_routes_whole_system_subsystem_repair_candidates() -> None:
    whole_system_boot_contract = {
        "surface_id": "whole-system-release-boot-contract",
        "status": "blocked",
        "product_scope": "whole-system",
        "subsystem_gates": [
            {
                "gate_id": "production-spine-release-manifest",
                "status": "blocked",
                "blocking_check_ids": ["release-manifest-rollup"],
                "missing_check_ids": [],
                "nonblocking_check_ids": [],
                "evidence_refs": ["release-manifest-rollup::blocked"],
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            },
            {
                "gate_id": "native-hive-runtime-heartbeat",
                "status": "blocked",
                "blocking_check_ids": ["native-hive-heartbeat"],
                "missing_check_ids": ["native-hive-heartbeat-watchdog"],
                "nonblocking_check_ids": [],
                "evidence_refs": ["native-hive-heartbeat::stale"],
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            },
            {
                "gate_id": "federation-runtime-path",
                "status": "blocked",
                "blocking_check_ids": ["federated-packet"],
                "missing_check_ids": [],
                "nonblocking_check_ids": ["peer-shadow-proposal"],
                "evidence_refs": ["federated-packet::missing"],
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            },
            {
                "gate_id": "authority-evidence-tool-governance",
                "status": "blocked",
                "blocking_check_ids": ["authority-evidence-tool-governance"],
                "missing_check_ids": [],
                "nonblocking_check_ids": [],
                "evidence_refs": ["authority-evidence-tool-governance::blocked"],
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            },
            {
                "gate_id": "visualizer-control-panel-surface",
                "status": "pass",
                "blocking_check_ids": [],
                "missing_check_ids": [],
                "nonblocking_check_ids": [],
                "evidence_refs": ["/ops/brain/visualizer/state"],
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            },
        ],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
    }
    record = build_release_health_heartbeat_loop_record(
        schema_version="nexusnet-release-wrapper-health-heartbeat-loop-v1",
        surface_id="release-wrapper-health-heartbeat-loop",
        artifact_ref="release-wrapper-runtime/release-health-heartbeat-loop.jsonl",
        heartbeat_artifact_ref="release-wrapper-runtime/release-health-heartbeat.jsonl",
        loop_id="release-health-heartbeat-loop::whole-system",
        generated_at="2026-07-03T04:00:00+00:00",
        next_due_at="2026-07-03T04:01:00+00:00",
        trigger="startup-auto",
        session_ref_digest="sha256:session-a",
        bounded_cycles=1,
        bounded_interval=60,
        bounded_retry_attempts=1,
        cycles=[
            {
                "cycle_index": 1,
                "status": "blocked",
                "heartbeat_id": "heartbeat-1",
                "blocked": True,
                "whole_system_boot_contract": whole_system_boot_contract,
            }
        ],
        blocked_cycles=[
            {
                "cycle_index": 1,
                "status": "blocked",
                "heartbeat_id": "heartbeat-1",
                "blocked": True,
                "whole_system_boot_contract": whole_system_boot_contract,
            }
        ],
        backoff_seconds=[5],
        repair_queue={
            "status": "proposal-routed",
            "latest_update_id": "update::repair-1",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        },
        failure_learning_signal={
            "status": "recorded",
            "signal_id": "signal-1",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        },
    )

    gate_ids = {candidate["gate_id"] for candidate in record["whole_system_repair_candidates"]}
    target_surfaces = set(record["repair_queue"]["target_surfaces"])

    assert gate_ids == {
        "production-spine-release-manifest",
        "native-hive-runtime-heartbeat",
        "federation-runtime-path",
        "authority-evidence-tool-governance",
    }
    assert {
        "production-spine",
        "native-hive-runtime",
        "growth-engine",
        "federation-runtime",
        "authority-spine",
        "eval-runtime-governance",
        "tool-action-harness",
    }.issubset(target_surfaces)
    assert record["repair_queue"]["whole_system_candidate_count"] == 4
    assert record["whole_system_repair_candidates"][0]["raw_content_included"] is False
    assert record["whole_system_repair_candidates"][0]["active_production_mutation_allowed"] is False
    assert record["whole_system_repair_candidates"][0]["active_production_mutated"] is False


def test_release_health_heartbeat_loop_routes_native_project_heartbeat_recovery_governance() -> None:
    project_heartbeat = {
        "schema_version": "nexusnet-project-heartbeat-v1",
        "surface_id": "nexusnet-project-heartbeat",
        "status": "degraded",
        "runtime_state": "degraded",
        "heartbeat_id": "project-heartbeat::blocked-forward-pass",
        "source_run_id": "hive-forward::blocked",
        "native_replay_ref": "hive-substrate/project-heartbeats/_index.jsonl",
        "native_replay_record_id": "native_project_heartbeat_blocked",
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "failure_recovery_governance": {
            "surface_id": "native-project-heartbeat-failure-recovery-governance",
            "status": "degraded-recovery-governed",
            "runtime_state": "degraded",
            "blocked_forward_pass": True,
            "self_healing_route_available": True,
            "admin_governance_required": True,
            "sandbox_eval_required": True,
            "rollback_required": True,
            "recovery_action": "route-around-and-queue-governed-repair",
            "evidence_refs": ["health-event::blocked", "route-around::native-heartbeat"],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
        },
    }

    record = build_release_health_heartbeat_loop_record(
        schema_version="nexusnet-release-wrapper-health-heartbeat-loop-v1",
        surface_id="release-wrapper-health-heartbeat-loop",
        artifact_ref="release-wrapper-runtime/release-health-heartbeat-loop.jsonl",
        heartbeat_artifact_ref="release-wrapper-runtime/release-health-heartbeat.jsonl",
        loop_id="release-health-heartbeat-loop::native-project-heartbeat",
        generated_at="2026-07-03T04:00:00+00:00",
        next_due_at="2026-07-03T04:01:00+00:00",
        trigger="wrapper-interaction-auto",
        session_ref_digest="sha256:session-a",
        bounded_cycles=1,
        bounded_interval=60,
        bounded_retry_attempts=1,
        cycles=[
            {
                "cycle_index": 1,
                "status": "blocked",
                "heartbeat_id": "heartbeat-1",
                "blocked": True,
                "project_heartbeat": project_heartbeat,
            }
        ],
        blocked_cycles=[
            {
                "cycle_index": 1,
                "status": "blocked",
                "heartbeat_id": "heartbeat-1",
                "blocked": True,
                "project_heartbeat": project_heartbeat,
            }
        ],
        backoff_seconds=[5],
        repair_queue={
            "status": "proposal-routed",
            "latest_update_id": "update::repair-1",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        },
        failure_learning_signal={
            "status": "recorded",
            "signal_id": "signal-1",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        },
    )

    candidates = {
        candidate["gate_id"]: candidate
        for candidate in record["whole_system_repair_candidates"]
    }
    candidate = candidates["native-project-heartbeat-recovery-governance"]

    assert candidate["candidate_id"] == (
        "native-project-heartbeat-recovery::project-heartbeat::blocked-forward-pass"
    )
    assert candidate["status"] == "degraded-recovery-governed"
    assert candidate["recovery_governance"]["surface_id"] == (
        "native-project-heartbeat-failure-recovery-governance"
    )
    assert candidate["recovery_governance"]["blocked_forward_pass"] is True
    assert candidate["recovery_governance"]["self_healing_route_available"] is True
    assert candidate["recovery_governance"]["admin_governance_required"] is True
    assert candidate["recovery_governance"]["sandbox_eval_required"] is True
    assert candidate["recovery_governance"]["rollback_required"] is True
    assert "native-project-heartbeat-failure-recovery-governance" in candidate["target_surfaces"]
    assert "autonomous-updates" in candidate["target_surfaces"]
    assert "sandboxed-self-repair" in candidate["target_surfaces"]
    assert "health-event::blocked" in candidate["evidence_refs"]
    assert "route-around::native-heartbeat" in candidate["evidence_refs"]
    assert "hive-substrate/project-heartbeats/_index.jsonl" in candidate["evidence_refs"]
    assert "native_project_heartbeat_blocked" in candidate["evidence_refs"]
    assert candidate["raw_content_included"] is False
    assert candidate["active_production_mutation_allowed"] is False
    assert candidate["active_production_mutated"] is False
    assert record["repair_queue"]["whole_system_candidate_gate_ids"] == [
        "native-project-heartbeat-recovery-governance"
    ]
    assert "native-project-heartbeat-failure-recovery-governance" in record["repair_queue"]["target_surfaces"]
