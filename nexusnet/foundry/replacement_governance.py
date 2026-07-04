from __future__ import annotations

from ..schemas import ReplacementReadinessReport, TeacherReplacementDecision
from .readiness_authority import resolve_readiness_authority


class ReplacementGovernanceAdvisor:
    def decide(
        self,
        *,
        teacher_id: str,
        replacement_target: str,
        readiness: ReplacementReadinessReport,
    ) -> TeacherReplacementDecision:
        authority = resolve_readiness_authority(readiness.evidence_refs)
        can_replace = readiness.ready and authority["authoritative_readiness"]
        decision = "replace" if can_replace else "shadow"
        rationale = (
            "Teacher replacement cleared subject trend, fleet, cohort, external evaluation, rollback, and governance gates."
            if can_replace
            else "Teacher replacement remains shadow-only until subject trend, fleet, cohort, external evaluation, rollback, governance, and promotion-provenance-gate authority all pass."
        )
        return TeacherReplacementDecision(
            teacher_id=teacher_id,
            replacement_target=replacement_target,
            decision=decision,
            rationale=rationale,
            evidence={
                "replacement_readiness": readiness.model_dump(mode="json"),
                "readiness_authority": authority,
            },
        )
