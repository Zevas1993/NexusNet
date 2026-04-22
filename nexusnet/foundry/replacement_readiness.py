from __future__ import annotations

from ..schemas import ReplacementReadinessReport


class ReplacementReadinessAdvisor:
    def decide(
        self,
        *,
        subject: str,
        teacher_id: str,
        threshold_set_id: str | None,
        threshold_version: int | None,
        subject_trend_ready: bool,
        fleet_gate_ready: bool,
        cohort_gate_ready: bool,
        external_evaluation_passed: bool,
        rollback_ready: bool,
        governance_signed_off: bool,
        metrics: dict,
        evidence_refs: dict,
    ) -> ReplacementReadinessReport:
        ready = all(
            [
                subject_trend_ready,
                fleet_gate_ready,
                cohort_gate_ready,
                external_evaluation_passed,
                rollback_ready,
                governance_signed_off,
            ]
        )
        if ready:
            replacement_mode = "replace"
        elif subject_trend_ready or fleet_gate_ready or cohort_gate_ready:
            replacement_mode = "shadow"
        else:
            replacement_mode = "hold"
        return ReplacementReadinessReport(
            subject=subject,
            teacher_id=teacher_id,
            threshold_set_id=threshold_set_id,
            threshold_version=threshold_version,
            subject_trend_ready=subject_trend_ready,
            fleet_gate_ready=fleet_gate_ready,
            cohort_gate_ready=cohort_gate_ready,
            external_evaluation_passed=external_evaluation_passed,
            rollback_ready=rollback_ready,
            governance_signed_off=governance_signed_off,
            ready=ready,
            replacement_mode=replacement_mode,
            metrics=metrics,
            evidence_refs=evidence_refs,
        )
