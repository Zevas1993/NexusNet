from __future__ import annotations

from ..schemas import GlobalRolloutDecision


class GlobalRolloutPlanner:
    def decide(self, *, candidate_id: str, review_decision: str, evaluator_decision: str) -> GlobalRolloutDecision:
        if review_decision == "approved" and evaluator_decision == "approved":
            decision = "rollout"
            rationale = "Candidate cleared local review, external evaluation, and remains rollback-ready."
        else:
            decision = "shadow"
            rationale = "Candidate remains shadow-only because the global review chain is incomplete."
        return GlobalRolloutDecision(candidate_id=candidate_id, decision=decision, rationale=rationale, rollback_ready=True)
