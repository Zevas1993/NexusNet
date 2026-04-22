from __future__ import annotations

from pathlib import Path

from nexus.storage import NexusStore

from ..schemas import CapabilityTakeoverRecord, ReplacementReadinessReport, TakeoverScorecard, TakeoverTrendReport, TeacherRetirementDecision
from ..teachers.schema_versions import TeacherSchemaRegistry
from ..teachers.retirement_governance import TeacherRetirementGovernance
from ..teachers.retirement_shadow_log import RetirementShadowLog
from .teacher_replacement import TeacherReplacementAdvisor


class FoundryRetirementHooks:
    def __init__(
        self,
        *,
        store: NexusStore | None = None,
        artifacts_dir: Path | None = None,
        schema_registry: TeacherSchemaRegistry | None = None,
    ):
        self.store = store
        self.schema_registry = schema_registry
        self.shadow_log = RetirementShadowLog(store=store, artifacts_dir=artifacts_dir) if store is not None and artifacts_dir is not None else None
        self._replacement = TeacherReplacementAdvisor()
        self._governance = TeacherRetirementGovernance()

    def takeover_candidate(
        self,
        decision: TeacherRetirementDecision,
        *,
        benchmark_summary: dict | None = None,
        teacher_evidence: dict | None = None,
        evaluator_decision: str = "shadow",
        governance_signed_off: bool = False,
    ) -> CapabilityTakeoverRecord:
        benchmark_summary = benchmark_summary or {}
        teacher_evidence = teacher_evidence or {}
        takeover_scorecard = TakeoverScorecard.model_validate(benchmark_summary.get("takeover_scorecard", {}))
        takeover_trend_report = TakeoverTrendReport.model_validate(benchmark_summary.get("takeover_trend_report", {}))
        replacement_readiness = (
            ReplacementReadinessReport.model_validate(benchmark_summary.get("replacement_readiness", {}))
            if benchmark_summary.get("replacement_readiness")
            else None
        )
        rollbackable = bool(benchmark_summary.get("takeover_rollbackability", False))
        replacement = self._replacement.decide(
            teacher_id=decision.teacher_id,
            replacement_target=f"native::{decision.teacher_id}",
            readiness=replacement_readiness
            or ReplacementReadinessReport(
                subject="teacher-replacement",
                teacher_id=decision.teacher_id,
                threshold_set_id=benchmark_summary.get("threshold_set_id"),
                subject_trend_ready=bool(takeover_trend_report.ready),
                fleet_gate_ready=False,
                cohort_gate_ready=False,
                external_evaluation_passed=evaluator_decision == "approved",
                rollback_ready=rollbackable,
                governance_signed_off=governance_signed_off,
                ready=False,
                replacement_mode="hold",
            ),
        )
        shadow_record = self._governance.review(
            teacher_id=decision.teacher_id,
            registry_layer=decision.registry_layer,
            takeover_scorecard=takeover_scorecard,
            takeover_trend_report=takeover_trend_report,
            replacement_decision=replacement,
            replacement_readiness=replacement_readiness,
            external_evaluation_passed=evaluator_decision == "approved",
            rollback_ready=rollbackable,
            governance_signed_off=governance_signed_off,
        )
        if self.schema_registry is not None:
            shadow_record = shadow_record.model_copy(update=self.schema_registry.envelope("retirement-shadow-record"))
        if self.shadow_log is not None:
            shadow_record = self.shadow_log.persist(shadow_record)
        return CapabilityTakeoverRecord(
            subject="teacher-replacement",
            teacher_id=decision.teacher_id,
            internal_target=f"native::{decision.teacher_id}",
            decision="shadow" if replacement.decision != "replace" else "takeover",
            rationale=replacement.rationale,
            evidence={
                "teacher_retirement_decision": decision.model_dump(mode="json"),
                "teacher_replacement_decision": replacement.model_dump(mode="json"),
                "benchmark_summary": benchmark_summary,
                "teacher_evidence": teacher_evidence,
                "retirement_shadow_record": shadow_record.model_dump(mode="json"),
                "takeover_readiness": benchmark_summary.get("takeover_readiness", 0.0),
                "takeover_rollbackability": rollbackable,
                "takeover_trend_report": takeover_trend_report.model_dump(mode="json"),
                "replacement_readiness": replacement_readiness.model_dump(mode="json") if replacement_readiness else None,
            },
            threshold_set_id=benchmark_summary.get("threshold_set_id"),
            teacher_evidence_bundle_id=teacher_evidence.get("bundle_id"),
            takeover_scorecard_id=takeover_scorecard.scorecard_id,
            takeover_trend_report_id=takeover_trend_report.trend_id,
            fleet_summary_ids=[item.get("summary_id") for item in benchmark_summary.get("fleet_summaries", [])],
            cohort_scorecard_ids=[item.get("cohort_id") for item in benchmark_summary.get("cohort_scorecards", [])],
            replacement_readiness_report_id=benchmark_summary.get("replacement_readiness_report_id"),
        )
