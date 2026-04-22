from __future__ import annotations

from ..schemas import FederatedReviewDecision


class FederatedReviewGate:
    def decide(self, *, candidate_id: str, evaluator_decision: str, reviewer: str = "EvalsAO") -> FederatedReviewDecision:
        decision = "approved" if evaluator_decision == "approved" else "shadow"
        rationale = (
            "Candidate is eligible for full-system review and guarded rollout." if decision == "approved" else
            "Candidate remains shadow-only until the external evaluator clears it."
        )
        return FederatedReviewDecision(candidate_id=candidate_id, decision=decision, reviewer=reviewer, rationale=rationale)
