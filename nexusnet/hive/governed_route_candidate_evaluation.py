"""Governed evaluation for shadow route candidates."""
from __future__ import annotations

import hashlib
from typing import Any

from nexus.schemas import new_id


GOVERNED_ROUTE_CANDIDATE_EVALUATION_SURFACE_ID = "hive-governed-route-candidate-evaluation"
GOVERNED_ROUTE_CANDIDATE_EVALUATION_LEDGER_ID = "hive-governed-route-candidate-evaluation-ledger-v0"
GOVERNED_ROUTE_CANDIDATE_APPROVAL_SURFACE_ID = "hive-governed-route-candidate-approval"
GOVERNED_ROUTE_CANDIDATE_APPROVAL_LEDGER_ID = "hive-governed-route-candidate-approval-ledger-v0"
GOVERNED_ROUTE_CANDIDATE_ROLLBACK_SURFACE_ID = "hive-governed-route-candidate-rollback"
GOVERNED_ROUTE_CANDIDATE_ROLLBACK_LEDGER_ID = "hive-governed-route-candidate-rollback-ledger-v0"
MINIMUM_ROUTE_DELTA = 0.01


def evaluate_governed_route_candidate(
    *,
    run_id: str,
    session_id: str,
    task_id: str,
    created_at: str,
    shadow_routing: dict[str, Any],
    checkpoint: dict[str, Any],
    policy_scan: dict[str, Any],
    human_governance_approval: bool = False,
    evaluation_id: str | None = None,
    artifact_path: str | None = None,
) -> dict[str, Any]:
    quality = shadow_routing.get("quality_comparison") or {}
    baseline_order = [str(item) for item in quality.get("baseline_order") or shadow_routing.get("baseline_selected_node_ids") or []]
    candidate_order = [str(item) for item in quality.get("shadow_order") or []]
    quality_delta = _float(quality.get("quality_delta"))
    candidate_count = len(shadow_routing.get("prior_weighted_candidates") or [])
    policy_hard_fail_count = _policy_hard_fail_count(policy_scan)
    sandbox_passed = bool(checkpoint.get("checkpoint_id")) and bool(checkpoint.get("restore_validation"))
    shadow_eval_passed = candidate_count > 0 and quality_delta >= MINIMUM_ROUTE_DELTA
    policy_passed = policy_hard_fail_count == 0
    missing_evidence = []
    if not shadow_eval_passed:
        missing_evidence.append("shadow_route_eval_delta")
    if not sandbox_passed:
        missing_evidence.append("closed_sandbox_replay")
    if not policy_passed:
        missing_evidence.append("policy_scan_clear")
    if not human_governance_approval:
        missing_evidence.append("human_governance_approval")
    if missing_evidence:
        gate_state = (
            "blocked_pending_admin_approval"
            if missing_evidence == ["human_governance_approval"]
            else "blocked_pending_eval_sandbox_or_policy"
        )
    else:
        gate_state = "approved_for_shadow_apply_only"
    status = "approved-shadow-route-candidate" if gate_state == "approved_for_shadow_apply_only" else "blocked-pending-admin-approval"
    honest_status_label = (
        "route-candidate-evaluated-admin-approved-shadow-only"
        if gate_state == "approved_for_shadow_apply_only"
        else "route-candidate-evaluated-awaiting-admin-approval"
    )
    eval_id = evaluation_id or new_id("governed_route_eval")
    candidate_id = f"route-candidate::{_safe_ref(str(shadow_routing.get('shadow_routing_id') or eval_id))}"
    return {
        "status_label": "LOCKED CANON",
        "authority": "NexusBrain",
        "surface_id": GOVERNED_ROUTE_CANDIDATE_EVALUATION_SURFACE_ID,
        "evaluation_id": eval_id,
        "run_id": run_id,
        "session_id": session_id,
        "task_id": task_id,
        "created_at": created_at,
        "status": status,
        "honest_status_label": honest_status_label,
        "source_shadow_routing_ref": shadow_routing.get("shadow_routing_id"),
        "prior_ledger_ref": shadow_routing.get("prior_ledger_ref"),
        "prior_update_count": int(shadow_routing.get("prior_update_count") or 0),
        "candidate_route": {
            "candidate_route_id": candidate_id,
            "baseline_node_order": baseline_order,
            "candidate_node_order": candidate_order,
            "quality_delta": quality_delta,
            "minimum_delta_required": MINIMUM_ROUTE_DELTA,
            "candidate_count": candidate_count,
            "candidate_nodes": [
                {
                    "node_id": str(candidate.get("node_id") or "node:unknown"),
                    "baseline_resonance_score": _float(candidate.get("baseline_resonance_score")),
                    "sanitized_prior_weight": _float(candidate.get("sanitized_prior_weight")),
                    "shadow_weight": _float(candidate.get("shadow_weight")),
                }
                for candidate in shadow_routing.get("prior_weighted_candidates") or []
            ],
        },
        "shadow_eval": {
            "status": "passed-shadow" if shadow_eval_passed else "blocked",
            "external_evaluator_refs": ["ao::EvalsAO", "ao::RouterAO", "ao::CritiqueAO"],
            "self_grading_allowed": False,
            "metric": "shadow_route_quality_delta",
            "quality_delta": quality_delta,
            "minimum_delta_required": MINIMUM_ROUTE_DELTA,
            "regression_count": 0 if shadow_eval_passed else 1,
        },
        "closed_sandbox_replay": {
            "status": "passed" if sandbox_passed else "missing",
            "checkpoint_ref": checkpoint.get("checkpoint_id"),
            "restore_validation": checkpoint.get("restore_validation") or {},
            "replay_scope": "route-order-metadata-only",
            "active_route_mutated": False,
        },
        "policy_scan": {
            "status": "passed" if policy_passed else "blocked",
            "active_hard_fail_count": policy_hard_fail_count,
            "raw_policy_payload_included": False,
        },
        "admin_approval": {
            "approval_required": True,
            "approval_state": "approved" if human_governance_approval else "pending",
            "required_aos": ["AdminAO", "GovernanceAO", "SecurityAO", "EvalsAO"],
            "operator_visible": True,
        },
        "rollback_plan": {
            "rollback_plan_id": f"rollback-plan::{_safe_ref(eval_id)}",
            "restore_ref": checkpoint.get("checkpoint_id"),
            "baseline_node_order": baseline_order,
            "candidate_node_order": candidate_order,
            "rollback_state": "available-before-apply",
        },
        "promotion_gate": {
            "gate_state": gate_state,
            "missing_evidence": missing_evidence,
            "active_route_mutated": False,
            "active_production_mutated": False,
            "promotion_scope": "shadow-route-candidate-only",
            "required_evidence": [
                "shadow_route_eval_delta",
                "closed_sandbox_replay",
                "policy_scan_clear",
                "human_governance_approval",
                "rollback_plan",
            ],
        },
        "apply_state": "not-applied-shadow-candidate-only",
        "active_route_mutated": False,
        "active_production_mutated": False,
        "raw_content_included": False,
        "artifact_path": artifact_path,
    }


def governed_route_candidate_evaluation_ledger(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    latest = evaluations[0] if evaluations else {}
    return {
        "ledger_id": GOVERNED_ROUTE_CANDIDATE_EVALUATION_LEDGER_ID,
        "surface_id": "hive-governed-route-candidate-evaluation-ledger",
        "evaluation_count": len(evaluations),
        "latest_evaluation_id": latest.get("evaluation_id"),
        "blocked_count": sum(1 for item in evaluations if str(item.get("status") or "").startswith("blocked")),
        "approved_shadow_count": sum(1 for item in evaluations if item.get("status") == "approved-shadow-route-candidate"),
        "active_route_mutated": False,
        "active_production_mutated": False,
        "promotion_boundary": "candidate-routes-remain-shadow-only-until-external-eval-sandbox-policy-admin-approval-and-rollback-plan",
    }


def approve_governed_route_candidate(
    *,
    evaluation: dict[str, Any],
    eval_replay: dict[str, Any],
    approved_by: str,
    created_at: str,
    approval_id: str | None = None,
    artifact_path: str | None = None,
) -> dict[str, Any]:
    candidate_route = evaluation.get("candidate_route") or {}
    baseline_order = [str(item) for item in candidate_route.get("baseline_node_order") or []]
    candidate_order = [str(item) for item in candidate_route.get("candidate_node_order") or []]
    replay_passed = (
        eval_replay.get("status") == "passed-shadow"
        and eval_replay.get("promotion_allowed") is True
        and eval_replay.get("operator_approved") is True
    )
    approved = replay_passed and bool(approved_by)
    approval_ref = approval_id or new_id("governed_route_approval")
    overlay_id = f"session-shadow-route-overlay::{_safe_ref(approval_ref)}"
    status = "shadow-route-applied" if approved else "blocked-pending-eval-replay-or-admin-approval"
    honest_status_label = (
        "session-shadow-route-overlay-active"
        if approved
        else "route-candidate-approval-blocked-pending-eval-replay-or-admin-approval"
    )
    return {
        "status_label": "LOCKED CANON",
        "authority": "NexusBrain",
        "surface_id": GOVERNED_ROUTE_CANDIDATE_APPROVAL_SURFACE_ID,
        "approval_id": approval_ref,
        "evaluation_id": evaluation.get("evaluation_id"),
        "run_id": evaluation.get("run_id"),
        "session_id": evaluation.get("session_id"),
        "task_id": evaluation.get("task_id"),
        "created_at": created_at,
        "status": status,
        "honest_status_label": honest_status_label,
        "approval_state": "admin-approved" if approved else "blocked",
        "source_shadow_routing_ref": evaluation.get("source_shadow_routing_ref"),
        "source_evaluation_ref": evaluation.get("evaluation_id"),
        "eval_replay": {
            "surface_id": eval_replay.get("surface_id"),
            "run_id": eval_replay.get("run_id"),
            "suite_id": eval_replay.get("suite_id"),
            "status": eval_replay.get("status"),
            "promotion_allowed": eval_replay.get("promotion_allowed"),
            "operator_approved": eval_replay.get("operator_approved"),
            "evidence_refs": eval_replay.get("evidence_refs") or [],
            "trace_refs": eval_replay.get("trace_refs") or [],
            "evaluator_refs": eval_replay.get("evaluator_refs") or [],
            "artifact_path": eval_replay.get("artifact_path"),
        },
        "admin_approval": {
            "approval_required": True,
            "approval_state": "approved" if approved else "blocked",
            "approved_by_ref": approved_by,
            "approved_by_digest": _privacy_digest(approved_by),
            "approved_at": created_at,
            "required_aos": ["AdminAO", "GovernanceAO", "SecurityAO", "EvalsAO"],
            "operator_visible": True,
        },
        "shadow_route_overlay": {
            "overlay_id": overlay_id,
            "overlay_state": "active-session-shadow" if approved else "blocked",
            "active_scope": "session-shadow-only",
            "baseline_node_order": baseline_order,
            "candidate_node_order": candidate_order,
            "applied_node_order": candidate_order,
            "source_eval_ref": evaluation.get("evaluation_id"),
            "source_eval_shadow_run_ref": eval_replay.get("run_id"),
            "rollback_plan_ref": (evaluation.get("rollback_plan") or {}).get("rollback_plan_id"),
            "session_shadow_route_mutated": approved,
            "active_route_mutated": False,
            "active_production_mutated": False,
        },
        "rollback_plan": {
            "rollback_plan_id": f"rollback-plan::{_safe_ref(str(evaluation.get('evaluation_id') or approval_ref))}",
            "restore_ref": (evaluation.get("rollback_plan") or {}).get("restore_ref"),
            "baseline_node_order": baseline_order,
            "candidate_node_order": candidate_order,
            "rollback_available": approved,
            "rollback_state": "available-after-shadow-apply" if approved else "blocked",
        },
        "promotion_gate": {
            "gate_state": "passed_for_session_shadow_overlay" if approved else "blocked",
            "required_evidence": [
                "eval_registry_shadow_replay",
                "human_governance_approval",
                "closed_sandbox_replay",
                "rollback_plan",
            ],
            "missing_evidence": [] if approved else ["eval_registry_shadow_replay_or_admin_approval"],
            "session_shadow_route_mutated": approved,
            "active_route_mutated": False,
            "active_production_mutated": False,
            "promotion_scope": "session-shadow-route-overlay-only",
        },
        "apply_state": "applied-session-shadow-overlay" if approved else "not-applied",
        "active_route_mutated": False,
        "session_shadow_route_mutated": approved,
        "active_production_mutated": False,
        "raw_content_included": False,
        "artifact_path": artifact_path,
    }


def rollback_governed_route_candidate(
    *,
    approval: dict[str, Any],
    reason: str,
    created_at: str,
    rollback_id: str | None = None,
    artifact_path: str | None = None,
) -> dict[str, Any]:
    overlay = approval.get("shadow_route_overlay") or {}
    rollback_ref = rollback_id or new_id("governed_route_rollback")
    return {
        "status_label": "LOCKED CANON",
        "authority": "NexusBrain",
        "surface_id": GOVERNED_ROUTE_CANDIDATE_ROLLBACK_SURFACE_ID,
        "rollback_id": rollback_ref,
        "approval_id": approval.get("approval_id"),
        "evaluation_id": approval.get("evaluation_id"),
        "run_id": approval.get("run_id"),
        "session_id": approval.get("session_id"),
        "task_id": approval.get("task_id"),
        "created_at": created_at,
        "rollback_state": "rolled_back",
        "honest_status_label": "session-shadow-route-overlay-rolled-back",
        "restored_node_order": [str(item) for item in overlay.get("baseline_node_order") or []],
        "previous_candidate_node_order": [str(item) for item in overlay.get("candidate_node_order") or []],
        "source_overlay_ref": overlay.get("overlay_id"),
        "rollback_restored": True,
        "session_shadow_route_mutated": True,
        "active_route_mutated": False,
        "active_production_mutated": False,
        "privacy_boundary": {
            "reason_digest": _privacy_digest(reason),
            "raw_reason_exported": False,
        },
        "artifact_path": artifact_path,
    }


def governed_route_candidate_approval_ledger(
    approvals: list[dict[str, Any]],
    rollbacks: list[dict[str, Any]],
) -> dict[str, Any]:
    latest = approvals[0] if approvals else {}
    rolled_back_approval_ids = {
        str(item.get("approval_id"))
        for item in rollbacks
        if item.get("rollback_state") == "rolled_back" and item.get("approval_id")
    }
    return {
        "ledger_id": GOVERNED_ROUTE_CANDIDATE_APPROVAL_LEDGER_ID,
        "surface_id": "hive-governed-route-candidate-approval-ledger",
        "approval_count": len(approvals),
        "latest_approval_id": latest.get("approval_id"),
        "active_session_shadow_overlay_count": sum(
            1
            for item in approvals
            if item.get("status") == "shadow-route-applied"
            and str(item.get("approval_id")) not in rolled_back_approval_ids
        ),
        "rolled_back_count": len(rolled_back_approval_ids),
        "active_route_mutated": False,
        "active_production_mutated": False,
        "promotion_boundary": "approvals-only-activate-session-shadow-route-overlays-until-rollback-or-production-gate",
    }


def governed_route_candidate_rollback_ledger(rollbacks: list[dict[str, Any]]) -> dict[str, Any]:
    latest = rollbacks[0] if rollbacks else {}
    return {
        "ledger_id": GOVERNED_ROUTE_CANDIDATE_ROLLBACK_LEDGER_ID,
        "surface_id": "hive-governed-route-candidate-rollback-ledger",
        "rollback_count": len(rollbacks),
        "latest_rollback_id": latest.get("rollback_id"),
        "restored_count": sum(1 for item in rollbacks if item.get("rollback_restored") is True),
        "active_route_mutated": False,
        "active_production_mutated": False,
        "rollback_boundary": "rollbacks-disable-session-shadow-overlays-and-restore-baseline-route-order-metadata",
    }


def _policy_hard_fail_count(policy_scan: dict[str, Any]) -> int:
    summary = policy_scan.get("summary") if isinstance(policy_scan, dict) else {}
    if isinstance(summary, dict):
        return int(summary.get("active_hard_fail_count") or 0)
    return int(getattr(summary, "active_hard_fail_count", 0) or 0)


def _float(value: Any) -> float:
    try:
        return round(float(value or 0.0), 6)
    except (TypeError, ValueError):
        return 0.0


def _safe_ref(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_", ":"} else "-" for ch in value)[:96] or "unknown"


def _privacy_digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
