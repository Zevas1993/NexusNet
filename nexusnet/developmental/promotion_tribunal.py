from __future__ import annotations

from typing import Any

from .contracts import PromotionTribunalDecision


class PromotionTribunal:
    def decide(
        self,
        *,
        case_id: str,
        candidate_ref: str,
        requested_state: str,
        policy_scan: dict[str, Any],
        eval_gate: dict[str, Any],
        artifact_trust: dict[str, Any],
        self_review: dict[str, Any],
        memory_quality: dict[str, Any],
        rollback: dict[str, Any],
        operator_approved: bool,
    ) -> dict[str, Any]:
        blockers = []
        if _policy_hard_fail_count(policy_scan) > 0:
            blockers.append("policy_scan_not_clear")
        if eval_gate.get("promotion_allowed") is not True:
            blockers.append("eval_gate_not_clear")
        if artifact_trust.get("promotion_allowed") is not True:
            blockers.append("artifact_trust_not_clear")
        if self_review.get("status") not in {"accepted-shadow", "passed", "review-passed"}:
            blockers.append("self_review_not_clear")
        if memory_quality.get("status") not in {"verified", "claim-grounded", "not_required"}:
            blockers.append("memory_quality_not_clear")
        if rollback.get("rollback_restorable") is not True:
            blockers.append("rollback_not_restorable")
        if not operator_approved and requested_state in {"canary", "active"}:
            blockers.append("operator_approval_required")
        active_allowed = requested_state == "active" and not blockers and operator_approved
        decision = "rejected"
        if not blockers and requested_state == "shadow":
            decision = "accepted-shadow"
        elif not blockers and requested_state == "canary":
            decision = "accepted-canary-request"
        elif active_allowed:
            decision = "accepted-active-request"
        return PromotionTribunalDecision(
            case_id=case_id,
            candidate_ref=candidate_ref,
            requested_state=requested_state,
            decision=decision,
            blockers=sorted(set(blockers)),
            active_promotion_allowed=active_allowed,
        ).model_dump(mode="json")


def _policy_hard_fail_count(policy_scan: dict[str, Any]) -> int:
    summary = policy_scan.get("summary") or {}
    if isinstance(summary, dict):
        return int(summary.get("active_hard_fail_count") or 0)
    return 0
