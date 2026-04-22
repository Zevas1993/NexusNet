from __future__ import annotations

from typing import Any

from ..foundry.takeover_trends import TakeoverTrendAnalyzer
from ..teachers.trends import TeacherTrendAnalyzer


class PromotionTrendGate:
    def __init__(self, *, teacher_trends: TeacherTrendAnalyzer, takeover_trends: TakeoverTrendAnalyzer):
        self.teacher_trends = teacher_trends
        self.takeover_trends = takeover_trends

    def evaluate(
        self,
        *,
        candidate_kind: str | None,
        candidate_traceability: dict[str, Any],
        teacher_evidence: dict[str, Any],
    ) -> dict[str, Any]:
        if not teacher_evidence:
            return {
                "applicable": False,
                "passed": True,
                "rationale": "No teacher-linked trend gate applies to this candidate.",
                "teacher_trends": [],
                "takeover_trend": None,
            }

        subject = str(teacher_evidence.get("subject") or candidate_traceability.get("subject") or "general")
        threshold_set_id = str(teacher_evidence.get("threshold_set_id") or candidate_traceability.get("threshold_set_id") or "teacher-v2026-r1")
        threshold_version = int((teacher_evidence.get("scorecards") or [{}])[0].get("threshold_version", 1))
        benchmark_families = teacher_evidence.get("benchmark_families") or ([teacher_evidence.get("benchmark_family")] if teacher_evidence.get("benchmark_family") else [])
        teacher_trends = [
            self.teacher_trends.build(
                subject=subject,
                benchmark_family=benchmark_family,
                threshold_set_id=threshold_set_id,
                threshold_version=threshold_version,
            ).model_dump(mode="json")
            for benchmark_family in benchmark_families
        ]
        passed = all(item.get("ready") for item in teacher_trends) if teacher_trends else True
        takeover_trend = None
        if candidate_kind == "native-takeover":
            takeover_scorecard = candidate_traceability.get("takeover_scorecard") or teacher_evidence.get("takeover_scorecard") or {}
            takeover_threshold_set_id = str(takeover_scorecard.get("threshold_set_id") or "takeover-v2026-r1")
            takeover_threshold_version = int(takeover_scorecard.get("threshold_version", 1))
            takeover_trend = self.takeover_trends.build(
                subject=subject,
                threshold_set_id=takeover_threshold_set_id,
                threshold_version=takeover_threshold_version,
            ).model_dump(mode="json")
            passed = passed and bool(takeover_trend.get("ready"))
        rationale = (
            "Candidate cleared repeated-run trend gates."
            if passed
            else "Candidate remains blocked by repeated-run trend gates, insufficient run stability, or recent regression."
        )
        return {
            "applicable": True,
            "passed": passed,
            "rationale": rationale,
            "teacher_trends": teacher_trends,
            "takeover_trend": takeover_trend,
        }
