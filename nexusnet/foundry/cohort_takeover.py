from __future__ import annotations

from typing import Any

from .replacement_cohorts import ReplacementCohortAnalyzer


class CohortTakeoverAnalyzer:
    def __init__(self, *, replacement_cohorts: ReplacementCohortAnalyzer):
        self.replacement_cohorts = replacement_cohorts

    def evaluate(
        self,
        *,
        subject: str,
        teacher_evidence: dict[str, Any],
        benchmark_summary: dict[str, Any],
    ) -> dict[str, Any]:
        metrics = teacher_evidence.get("metrics", {})
        roles = teacher_evidence.get("selected_teacher_roles", {})
        teacher_pair_id = None
        if roles.get("primary") and roles.get("secondary"):
            teacher_pair_id = f"{roles['primary']}::{roles['secondary']}"
        cohorts = self.replacement_cohorts.build(
            subject=subject,
            teacher_pair_id=teacher_pair_id,
            budget_class=metrics.get("budget_class"),
            hardware_class=metrics.get("hardware_class"),
            lineage="dream-derived" if teacher_evidence.get("dream_derived") and not teacher_evidence.get("live_derived") else None,
            native_takeover_candidate_id=teacher_evidence.get("native_takeover_candidate_id"),
        )
        return {
            "status_label": "LOCKED CANON",
            "fleet_summaries": [item.get("metrics", {}).get("fleet_summary") for item in cohorts],
            "cohort_scorecards": cohorts,
            "cohort_gate_ready": all(item.get("ready") for item in cohorts) if cohorts else False,
            "benchmark_summary_ref": benchmark_summary.get("takeover_scorecard_id"),
        }
