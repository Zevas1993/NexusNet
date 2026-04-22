from __future__ import annotations

from ..schemas import ReplacementReadinessReport, RetirementShadowRecord, TeacherReplacementDecision, TakeoverScorecard, TakeoverTrendReport


class TeacherRetirementGovernance:
    def review(
        self,
        *,
        teacher_id: str,
        registry_layer: str,
        takeover_scorecard: TakeoverScorecard | None,
        takeover_trend_report: TakeoverTrendReport | None,
        replacement_decision: TeacherReplacementDecision | None,
        replacement_readiness: ReplacementReadinessReport | None,
        external_evaluation_passed: bool,
        rollback_ready: bool,
        governance_signed_off: bool,
    ) -> RetirementShadowRecord:
        if registry_layer == "historical":
            return RetirementShadowRecord(
                teacher_id=teacher_id,
                registry_layer=registry_layer,
                decision="hold",
                rationale="Historical teacher canon is immutable and cannot enter retirement shadow review.",
                evidence={"historical_immutable": True},
                external_evaluation_passed=False,
                rollback_ready=False,
                governance_signed_off=False,
            )

        gates_pass = all(
            [
                takeover_scorecard is not None and takeover_scorecard.passed,
                takeover_trend_report is not None and takeover_trend_report.ready,
                replacement_decision is not None,
                replacement_readiness is not None and replacement_readiness.ready,
                external_evaluation_passed,
                rollback_ready,
                governance_signed_off,
            ]
        )
        return RetirementShadowRecord(
            teacher_id=teacher_id,
            registry_layer=registry_layer,
            decision="shadow" if gates_pass else "hold",
            rationale=(
                "Teacher enters shadow retirement review because repeated benchmark surpass evidence, external evaluation, rollback, and governance gates are satisfied."
                if gates_pass
                else "Teacher remains active because retirement shadow evidence gates are incomplete or trend stability is insufficient."
            ),
            evidence={
                "takeover_scorecard": takeover_scorecard.model_dump(mode="json") if takeover_scorecard else None,
                "takeover_trend_report": takeover_trend_report.model_dump(mode="json") if takeover_trend_report else None,
                "replacement_decision": replacement_decision.model_dump(mode="json") if replacement_decision else None,
                "replacement_readiness": replacement_readiness.model_dump(mode="json") if replacement_readiness else None,
            },
            threshold_set_id=takeover_scorecard.threshold_set_id if takeover_scorecard else None,
            takeover_scorecard_id=takeover_scorecard.scorecard_id if takeover_scorecard else None,
            external_evaluation_passed=external_evaluation_passed,
            rollback_ready=rollback_ready,
            governance_signed_off=governance_signed_off,
        )
