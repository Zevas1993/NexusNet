from nexus.schemas import utcnow
from nexusnet.hive.governed_route_candidate_evaluation import (
    approve_governed_route_candidate,
    evaluate_governed_route_candidate,
    rollback_governed_route_candidate,
)


def test_governed_route_candidate_evaluation_blocks_active_route_mutation_until_admin_approval():
    evaluation = evaluate_governed_route_candidate(
        run_id="hive-forward-route-eval-001",
        session_id="route-eval-session",
        task_id="route-eval-task",
        created_at=utcnow().isoformat(),
        shadow_routing={
            "shadow_routing_id": "shadow-routing-001",
            "prior_ledger_ref": "federated-prior-ledger-v0",
            "prior_update_count": 2,
            "prior_weighted_candidates": [
                {
                    "node_id": "expert:runtime",
                    "baseline_resonance_score": 0.7,
                    "sanitized_prior_weight": 0.72,
                    "shadow_weight": 0.772,
                },
                {
                    "node_id": "node:nexus-brain",
                    "baseline_resonance_score": 0.5,
                    "sanitized_prior_weight": 0.0,
                    "shadow_weight": 0.5,
                },
            ],
            "quality_comparison": {
                "baseline_route_quality": 0.6,
                "shadow_route_quality": 0.636,
                "quality_delta": 0.036,
                "baseline_order": ["node:nexus-brain", "expert:runtime"],
                "shadow_order": ["expert:runtime", "node:nexus-brain"],
            },
        },
        checkpoint={
            "checkpoint_id": "hive-checkpoint-001",
            "restore_validation": {"restore_state": "validated_metadata_only"},
        },
        policy_scan={
            "summary": {"active_hard_fail_count": 0},
            "findings": [],
        },
        human_governance_approval=False,
    )

    assert evaluation["surface_id"] == "hive-governed-route-candidate-evaluation"
    assert evaluation["status"] == "blocked-pending-admin-approval"
    assert evaluation["candidate_route"]["candidate_node_order"] == [
        "expert:runtime",
        "node:nexus-brain",
    ]
    assert evaluation["candidate_route"]["baseline_node_order"] == [
        "node:nexus-brain",
        "expert:runtime",
    ]
    assert evaluation["shadow_eval"]["status"] == "passed-shadow"
    assert evaluation["closed_sandbox_replay"]["status"] == "passed"
    assert evaluation["promotion_gate"]["gate_state"] == "blocked_pending_admin_approval"
    assert evaluation["promotion_gate"]["active_route_mutated"] is False
    assert evaluation["admin_approval"]["approval_state"] == "pending"
    assert evaluation["rollback_plan"]["restore_ref"] == "hive-checkpoint-001"
    assert evaluation["active_route_mutated"] is False
    assert evaluation["active_production_mutated"] is False
    assert evaluation["raw_content_included"] is False

    serialized = repr(evaluation)
    assert "Project-Caldera" not in serialized
    assert "C:\\Users\\ChrisBoyd" not in serialized


def test_governed_route_candidate_admin_approval_records_shadow_apply_and_rollback():
    evaluation = evaluate_governed_route_candidate(
        run_id="hive-forward-route-eval-apply-001",
        session_id="route-apply-session",
        task_id="route-apply-task",
        created_at=utcnow().isoformat(),
        shadow_routing={
            "shadow_routing_id": "shadow-routing-apply-001",
            "prior_ledger_ref": "federated-prior-ledger-v0",
            "prior_update_count": 3,
            "prior_weighted_candidates": [
                {
                    "node_id": "expert:runtime",
                    "baseline_resonance_score": 0.7,
                    "sanitized_prior_weight": 0.9,
                    "shadow_weight": 0.79,
                },
                {
                    "node_id": "node:nexus-brain",
                    "baseline_resonance_score": 0.5,
                    "sanitized_prior_weight": 0.0,
                    "shadow_weight": 0.5,
                },
            ],
            "quality_comparison": {
                "baseline_route_quality": 0.6,
                "shadow_route_quality": 0.645,
                "quality_delta": 0.045,
                "baseline_order": ["node:nexus-brain", "expert:runtime"],
                "shadow_order": ["expert:runtime", "node:nexus-brain"],
            },
        },
        checkpoint={
            "checkpoint_id": "hive-checkpoint-apply-001",
            "restore_validation": {"restore_state": "validated_metadata_only"},
        },
        policy_scan={"summary": {"active_hard_fail_count": 0}},
        human_governance_approval=False,
    )

    eval_replay = {
        "surface_id": "eval-shadow-run",
        "run_id": "route-eval-shadow-run-001",
        "suite_id": "eval::hive-route-candidate::001",
        "status": "passed-shadow",
        "promotion_allowed": True,
        "operator_approved": True,
    }
    approval = approve_governed_route_candidate(
        evaluation=evaluation,
        eval_replay=eval_replay,
        approved_by="admin::route-operator",
        created_at=utcnow().isoformat(),
        approval_id="route-approval-001",
        artifact_path="artifacts/hive/route-candidate-approvals/route-approval-001.json",
    )

    assert approval["surface_id"] == "hive-governed-route-candidate-approval"
    assert approval["approval_id"] == "route-approval-001"
    assert approval["evaluation_id"] == evaluation["evaluation_id"]
    assert approval["status"] == "shadow-route-applied"
    assert approval["approval_state"] == "admin-approved"
    assert approval["eval_replay"]["status"] == "passed-shadow"
    assert approval["eval_replay"]["promotion_allowed"] is True
    assert approval["shadow_route_overlay"]["overlay_state"] == "active-session-shadow"
    assert approval["shadow_route_overlay"]["baseline_node_order"] == [
        "node:nexus-brain",
        "expert:runtime",
    ]
    assert approval["shadow_route_overlay"]["candidate_node_order"] == [
        "expert:runtime",
        "node:nexus-brain",
    ]
    assert approval["shadow_route_overlay"]["active_scope"] == "session-shadow-only"
    assert approval["promotion_gate"]["session_shadow_route_mutated"] is True
    assert approval["promotion_gate"]["active_route_mutated"] is False
    assert approval["promotion_gate"]["active_production_mutated"] is False
    assert approval["raw_content_included"] is False

    rollback = rollback_governed_route_candidate(
        approval=approval,
        reason="Operator rejected the route overlay after shadow review.",
        created_at=utcnow().isoformat(),
        rollback_id="route-rollback-001",
        artifact_path="artifacts/hive/route-candidate-rollbacks/route-rollback-001.json",
    )

    assert rollback["surface_id"] == "hive-governed-route-candidate-rollback"
    assert rollback["rollback_id"] == "route-rollback-001"
    assert rollback["approval_id"] == approval["approval_id"]
    assert rollback["rollback_state"] == "rolled_back"
    assert rollback["restored_node_order"] == ["node:nexus-brain", "expert:runtime"]
    assert rollback["previous_candidate_node_order"] == ["expert:runtime", "node:nexus-brain"]
    assert rollback["rollback_restored"] is True
    assert rollback["active_route_mutated"] is False
    assert rollback["active_production_mutated"] is False
    assert rollback["privacy_boundary"]["raw_reason_exported"] is False
