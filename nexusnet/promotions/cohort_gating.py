from __future__ import annotations

from typing import Any

from ..foundry.replacement_cohorts import ReplacementCohortAnalyzer
from ..foundry.replacement_readiness import ReplacementReadinessAdvisor
from ..teachers.fleets import TeacherBenchmarkFleetAnalyzer
from ..teachers.fleet_registry import TeacherBenchmarkFleetRegistry


class PromotionCohortGate:
    def __init__(
        self,
        *,
        fleet_registry: TeacherBenchmarkFleetRegistry,
        fleet_analyzer: TeacherBenchmarkFleetAnalyzer,
        replacement_cohorts: ReplacementCohortAnalyzer,
        readiness: ReplacementReadinessAdvisor,
    ):
        self.fleet_registry = fleet_registry
        self.fleet_analyzer = fleet_analyzer
        self.replacement_cohorts = replacement_cohorts
        self.readiness = readiness

    def evaluate(
        self,
        *,
        candidate_kind: str | None,
        candidate_traceability: dict[str, Any],
        teacher_evidence: dict[str, Any],
        trend_report: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not teacher_evidence:
            return {
                "applicable": False,
                "passed": True,
                "rationale": "No teacher-linked cohort gate applies to this candidate.",
                "fleet_summaries": [],
                "cohort_scorecards": [],
                "replacement_readiness": None,
            }

        subject = str(teacher_evidence.get("subject") or candidate_traceability.get("subject") or "general")
        metrics = teacher_evidence.get("metrics", {})
        roles = teacher_evidence.get("selected_teacher_roles", {})
        teacher_pair_id = None
        if roles.get("primary") and roles.get("secondary"):
            teacher_pair_id = f"{roles['primary']}::{roles['secondary']}"
        lineage = None
        if teacher_evidence.get("dream_derived") and not teacher_evidence.get("live_derived"):
            lineage = "dream-derived"
        elif teacher_evidence.get("dream_derived") and teacher_evidence.get("live_derived"):
            lineage = "blended-derived"
        fleet_summaries = [
            self.fleet_analyzer.build(
                fleet_id=fleet_id,
                window_id="medium",
                subject=subject,
                teacher_pair_id=teacher_pair_id,
                budget_class=metrics.get("budget_class"),
                output_form=metrics.get("output_form"),
                risk_tier=metrics.get("risk_tier"),
                locality=metrics.get("locality"),
                hardware_class=metrics.get("hardware_class"),
                lineage=lineage,
            ).model_dump(mode="json")
            for fleet_id in self.fleet_registry.preferred_fleet_ids(subject=subject, candidate_kind=candidate_kind)
        ]
        cohort_scorecards = self.replacement_cohorts.build(
            subject=subject,
            teacher_pair_id=teacher_pair_id,
            budget_class=metrics.get("budget_class"),
            hardware_class=metrics.get("hardware_class"),
            lineage=lineage,
            native_takeover_candidate_id=teacher_evidence.get("native_takeover_candidate_id"),
        )
        readiness_report = None
        if candidate_kind == "native-takeover":
            readiness_report = self.readiness.decide(
                subject=subject,
                teacher_id=roles.get("primary") or "unknown-teacher",
                threshold_set_id=teacher_evidence.get("threshold_set_id"),
                threshold_version=int((teacher_evidence.get("scorecards") or [{}])[0].get("threshold_version", 1)),
                subject_trend_ready=bool(trend_report and trend_report.get("passed")),
                fleet_gate_ready=all(item.get("ready") for item in fleet_summaries) if fleet_summaries else False,
                cohort_gate_ready=all(item.get("ready") for item in cohort_scorecards) if cohort_scorecards else False,
                external_evaluation_passed=False,
                rollback_ready=bool(candidate_traceability.get("benchmark", {}).get("takeover_rollbackability", False)),
                governance_signed_off=False,
                metrics={
                    "dependency_ratio_trend": candidate_traceability.get("benchmark", {}).get("takeover_trend_report", {}).get("dependency_ratio_trend"),
                    "native_generation_trend": candidate_traceability.get("benchmark", {}).get("takeover_trend_report", {}).get("native_generation_trend"),
                },
                evidence_refs={
                    "fleet_summary_ids": [item.get("summary_id") for item in fleet_summaries],
                    "cohort_scorecard_ids": [item.get("cohort_id") for item in cohort_scorecards],
                    "takeover_trend_report_id": candidate_traceability.get("benchmark", {}).get("takeover_trend_report_id"),
                },
            ).model_dump(mode="json")
        passed = (all(item.get("ready") for item in fleet_summaries) if fleet_summaries else True) and (
            all(item.get("ready") for item in cohort_scorecards) if cohort_scorecards else True
        )
        if readiness_report is not None:
            passed = passed and readiness_report.get("replacement_mode") != "hold"
        rationale = (
            "Candidate cleared fleet and cohort evidence gates."
            if passed
            else "Candidate remains blocked by insufficient fleet coverage, unstable cohorts, or replacement readiness that is not yet governance-grade."
        )
        return {
            "applicable": True,
            "passed": passed,
            "rationale": rationale,
            "fleet_summaries": fleet_summaries,
            "cohort_scorecards": cohort_scorecards,
            "replacement_readiness": readiness_report,
        }
