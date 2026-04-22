from __future__ import annotations

from ..schemas import ReplacementReadinessReport, TeacherReplacementDecision


class ReplacementGovernanceAdvisor:
    def decide(
        self,
        *,
        teacher_id: str,
        replacement_target: str,
        readiness: ReplacementReadinessReport,
    ) -> TeacherReplacementDecision:
        decision = "replace" if readiness.ready else "shadow"
        rationale = (
            "Teacher replacement cleared subject trend, fleet, cohort, external evaluation, rollback, and governance gates."
            if readiness.ready
            else "Teacher replacement remains shadow-only until subject trend, fleet, cohort, external evaluation, rollback, and governance gates all pass."
        )
        return TeacherReplacementDecision(
            teacher_id=teacher_id,
            replacement_target=replacement_target,
            decision=decision,
            rationale=rationale,
            evidence={"replacement_readiness": readiness.model_dump(mode="json")},
        )
