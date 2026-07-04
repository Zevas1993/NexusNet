from __future__ import annotations

from nexusnet.release_health_heartbeat_supervisor_repair import (
    build_release_health_heartbeat_supervisor_repair_run_plan,
)


def test_release_health_heartbeat_supervisor_repair_run_plan_registers_eval_and_shapes_actions() -> None:
    plan = build_release_health_heartbeat_supervisor_repair_run_plan(
        payload={
            "command": "pytest tests/heartbeat_probe.py -q",
            "timeout_seconds": 30,
            "approved_by": "admin-user",
            "approval_ref": "operator-review::heartbeat-supervisor-repair",
        },
        supervisor={
            "latest_pulse": {
                "pulse_id": "pulse-a",
                "loop_id": "loop-a-top",
                "heartbeat_id": "heartbeat-a",
                "loop": {
                    "loop_id": "loop-a",
                    "repair_queue": {
                        "latest_update_id": "update::release-wrapper-health-heartbeat-loop::abc123",
                    },
                },
            },
        },
        proposal={
            "update_id": "update::release-wrapper-health-heartbeat-loop::abc123",
            "eval_refs": [
                "eval::release-wrapper-runtime::heartbeat-suite",
                "evals-ao-artifact::release-wrapper::gate-a",
            ],
            "rollback_plan": "heartbeat-supervisor-safe-file-rollback",
            "monitoring_plan": "pytest fallback.py -q",
        },
        registered_suite_ids=set(),
        default_command="pytest tests/default_probe.py -q",
        digest=lambda value: f"digest::{value}",
    )

    assert plan["status"] == "planned"
    assert plan["repair_scope"] == "whole-system-admin-approved-update-path"
    assert plan["update_id"] == "update::release-wrapper-health-heartbeat-loop::abc123"
    assert plan["source_pulse_id"] == "pulse-a"
    assert plan["source_loop_id"] == "loop-a"
    assert plan["source_heartbeat_id"] == "heartbeat-a"
    assert plan["suite_id"] == "eval::release-wrapper-runtime::heartbeat-suite"
    assert plan["gate_refs"] == ["evals-ao-artifact::release-wrapper::gate-a"]
    assert plan["command"] == "pytest tests/heartbeat_probe.py -q"
    assert plan["timeout_seconds"] == 30
    assert plan["admin_approval_payload"] == {
        "approved_by": "admin-user",
        "approval_ref": "operator-review::heartbeat-supervisor-repair",
    }
    assert plan["sandbox_tests_payload"] == {
        "command": "pytest tests/heartbeat_probe.py -q",
        "timeout_seconds": 30,
    }
    assert plan["register_eval_suite"] is True
    assert plan["eval_suite_request"]["suite_id"] == "eval::release-wrapper-runtime::heartbeat-suite"
    assert plan["eval_suite_request"]["target_surfaces"] == [
        "release-wrapper-health-heartbeat-supervisor",
        "release-wrapper-health-heartbeat-loop",
    ]
    assert plan["eval_suite_request"]["benchmark_refs"] == [
        "pulse-a",
        "loop-a",
        "heartbeat-a",
        "update::release-wrapper-health-heartbeat-loop::abc123",
        "evals-ao-artifact::release-wrapper::gate-a",
    ]
    assert plan["eval_suite_request"]["metadata"]["replay_template"]["payload"]["run_id"] == (
        "shadow-run::digest::update::release-wrapper-health-heartbeat-loop::abc123"
        "eval::release-wrapper-runtime::heartbeat-suite"
    )
    assert plan["raw_content_included"] is False
    assert plan["active_production_mutation_allowed"] is False
    assert plan["active_production_mutated"] is False


def test_release_health_heartbeat_supervisor_repair_run_plan_builds_subsystem_envelopes() -> None:
    plan = build_release_health_heartbeat_supervisor_repair_run_plan(
        payload={
            "command": "pytest tests/heartbeat_probe.py -q",
            "timeout_seconds": 30,
            "approved_by": "admin-user",
            "approval_ref": "operator-review::heartbeat-supervisor-repair",
        },
        supervisor={
            "latest_pulse": {
                "pulse_id": "pulse-a",
                "loop_id": "loop-a-top",
                "heartbeat_id": "heartbeat-a",
                "loop": {
                    "loop_id": "loop-a",
                    "repair_queue": {
                        "latest_update_id": "update::release-wrapper-health-heartbeat-loop::abc123",
                    },
                    "whole_system_repair_candidates": [
                        {
                            "candidate_id": "whole-system-gate::production-spine-release-manifest",
                            "gate_id": "production-spine-release-manifest",
                            "status": "blocked",
                            "target_surfaces": ["production-spine", "release-manifest"],
                            "blocking_check_ids": ["release-manifest-rollup"],
                            "missing_check_ids": [],
                            "nonblocking_check_ids": [],
                            "evidence_refs": ["release-manifest-rollup::blocked"],
                            "raw_content_included": False,
                            "active_production_mutation_allowed": False,
                        },
                        {
                            "candidate_id": "whole-system-gate::authority-evidence-tool-governance",
                            "gate_id": "authority-evidence-tool-governance",
                            "status": "blocked",
                            "target_surfaces": [
                                "authority-spine",
                                "eval-runtime-governance",
                                "tool-action-harness",
                            ],
                            "blocking_check_ids": ["authority-evidence-tool-governance"],
                            "missing_check_ids": ["tool-action-shadow-plan"],
                            "nonblocking_check_ids": [],
                            "evidence_refs": ["authority-evidence-tool-governance::blocked"],
                            "raw_content_included": False,
                            "active_production_mutation_allowed": False,
                        },
                    ],
                },
            },
        },
        proposal={
            "update_id": "update::release-wrapper-health-heartbeat-loop::abc123",
            "eval_refs": [
                "eval::release-wrapper-runtime::heartbeat-suite",
                "evals-ao-artifact::release-wrapper::gate-a",
            ],
            "target_surfaces": [
                "release-wrapper-health-heartbeat-loop",
                "production-spine",
                "authority-spine",
                "eval-runtime-governance",
                "tool-action-harness",
            ],
            "rollback_plan": "heartbeat-supervisor-safe-file-rollback",
            "monitoring_plan": "pytest fallback.py -q",
        },
        registered_suite_ids=set(),
        default_command="pytest tests/default_probe.py -q",
        digest=lambda value: f"digest::{value}",
    )

    envelopes = plan["subsystem_repair_envelopes"]

    assert plan["subsystem_repair_envelope_count"] == 2
    assert [envelope["gate_id"] for envelope in envelopes] == [
        "production-spine-release-manifest",
        "authority-evidence-tool-governance",
    ]
    assert envelopes[0]["target_surfaces"] == ["production-spine", "release-manifest"]
    assert envelopes[0]["eval_suite_id"] == "eval::release-wrapper-runtime::heartbeat-suite"
    assert envelopes[0]["sandbox_command_ref"].startswith("pytest::")
    assert envelopes[0]["admin_approval_ref"] == "operator-review::heartbeat-supervisor-repair"
    assert envelopes[0]["apply_ref"] == "autonomous-update-apply::update::release-wrapper-health-heartbeat-loop::abc123"
    assert envelopes[0]["rollback_ref"] == "autonomous-update-rollback::update::release-wrapper-health-heartbeat-loop::abc123"
    assert envelopes[0]["honest_status_label"] == "planned-admin-approval-required"
    assert envelopes[0]["action_statuses"] == {
        "admin_approval": "pending-admin-approval",
        "shadow_eval_replay": "not-run",
        "sandbox_tests": "not-run",
        "apply": "not-applied",
        "rollback": "not-rolled-back",
    }
    assert envelopes[0]["raw_content_included"] is False
    assert envelopes[0]["active_production_mutation_allowed"] is False
    assert envelopes[0]["active_production_mutated"] is False
    assert plan["eval_suite_request"]["metadata"]["subsystem_repair_envelope_count"] == 2
    assert plan["eval_suite_request"]["metadata"]["subsystem_repair_envelope_refs"] == [
        "subsystem-repair-envelope::production-spine-release-manifest::digest::production-spine-release-manifest",
        "subsystem-repair-envelope::authority-evidence-tool-governance::digest::authority-evidence-tool-governance",
    ]


def test_release_health_heartbeat_supervisor_repair_run_plan_preserves_native_recovery_governance() -> None:
    plan = build_release_health_heartbeat_supervisor_repair_run_plan(
        payload={
            "command": "pytest tests/heartbeat_probe.py -q",
            "timeout_seconds": 30,
            "approved_by": "admin-user",
            "approval_ref": "operator-review::heartbeat-supervisor-repair",
        },
        supervisor={
            "latest_pulse": {
                "pulse_id": "pulse-native-project-heartbeat",
                "loop_id": "loop-native-project-heartbeat-top",
                "heartbeat_id": "heartbeat-native-project-heartbeat",
                "loop": {
                    "loop_id": "loop-native-project-heartbeat",
                    "repair_queue": {
                        "latest_update_id": "update::release-wrapper-health-heartbeat-loop::native-project",
                    },
                    "whole_system_repair_candidates": [
                        {
                            "candidate_id": (
                                "native-project-heartbeat-recovery::"
                                "project-heartbeat::blocked-forward-pass"
                            ),
                            "gate_id": "native-project-heartbeat-recovery-governance",
                            "status": "degraded-recovery-governed",
                            "target_surfaces": [
                                "native-hive-runtime",
                                "native-project-heartbeat",
                                "native-project-heartbeat-failure-recovery-governance",
                                "autonomous-updates",
                                "sandboxed-self-repair",
                            ],
                            "blocking_check_ids": [
                                "native-project-heartbeat-failure-recovery-governance"
                            ],
                            "missing_check_ids": [],
                            "nonblocking_check_ids": [],
                            "evidence_refs": [
                                "health-event::blocked",
                                "route-around::native-heartbeat",
                                "hive-substrate/project-heartbeats/_index.jsonl",
                                "native_project_heartbeat_blocked",
                            ],
                            "recovery_governance": {
                                "surface_id": "native-project-heartbeat-failure-recovery-governance",
                                "status": "degraded-recovery-governed",
                                "runtime_state": "degraded",
                                "blocked_forward_pass": True,
                                "self_healing_route_available": True,
                                "admin_governance_required": True,
                                "sandbox_eval_required": True,
                                "rollback_required": True,
                                "recovery_action": "route-around-and-queue-governed-repair",
                                "evidence_refs": [
                                    "health-event::blocked",
                                    "route-around::native-heartbeat",
                                ],
                                "raw_content_included": False,
                                "active_production_mutation_allowed": False,
                                "active_production_mutated": False,
                            },
                            "raw_content_included": False,
                            "active_production_mutation_allowed": False,
                            "active_production_mutated": False,
                        }
                    ],
                },
            },
        },
        proposal={
            "update_id": "update::release-wrapper-health-heartbeat-loop::native-project",
            "eval_refs": [
                "eval::release-wrapper-runtime::heartbeat-suite",
                "evals-ao-artifact::release-wrapper::gate-a",
            ],
            "target_surfaces": [
                "release-wrapper-health-heartbeat-loop",
                "native-project-heartbeat-failure-recovery-governance",
                "autonomous-updates",
                "sandboxed-self-repair",
            ],
            "rollback_plan": "heartbeat-supervisor-safe-file-rollback",
            "monitoring_plan": "pytest fallback.py -q",
        },
        registered_suite_ids=set(),
        default_command="pytest tests/default_probe.py -q",
        digest=lambda value: f"digest::{value}",
    )

    envelope = plan["subsystem_repair_envelopes"][0]

    assert plan["subsystem_repair_envelope_count"] == 1
    assert envelope["gate_id"] == "native-project-heartbeat-recovery-governance"
    assert envelope["status"] == "planned"
    assert envelope["target_surfaces"] == [
        "native-hive-runtime",
        "native-project-heartbeat",
        "native-project-heartbeat-failure-recovery-governance",
        "autonomous-updates",
        "sandboxed-self-repair",
    ]
    assert envelope["recovery_governance"]["status"] == "degraded-recovery-governed"
    assert envelope["recovery_governance"]["blocked_forward_pass"] is True
    assert envelope["recovery_governance"]["self_healing_route_available"] is True
    assert envelope["recovery_governance"]["admin_governance_required"] is True
    assert envelope["recovery_governance"]["sandbox_eval_required"] is True
    assert envelope["recovery_governance"]["rollback_required"] is True
    assert "health-event::blocked" in envelope["evidence_refs"]
    assert "route-around::native-heartbeat" in envelope["evidence_refs"]
    assert envelope["raw_content_included"] is False
    assert envelope["active_production_mutation_allowed"] is False
    assert envelope["active_production_mutated"] is False


def test_release_health_heartbeat_supervisor_repair_run_plan_blocks_missing_update_id() -> None:
    plan = build_release_health_heartbeat_supervisor_repair_run_plan(
        payload={},
        supervisor={"latest_pulse": {"loop": {"repair_queue": {}}}},
        proposal={},
        registered_suite_ids=set(),
        default_command="pytest tests/default_probe.py -q",
        digest=lambda value: value,
    )

    assert plan["status"] == "blocked-missing-update-id"
    assert plan["http_status"] == 400
    assert plan["detail"] == "heartbeat supervisor repair requires a pulse repair proposal update_id"
    assert plan["raw_content_included"] is False
    assert plan["active_production_mutation_allowed"] is False
    assert plan["active_production_mutated"] is False
