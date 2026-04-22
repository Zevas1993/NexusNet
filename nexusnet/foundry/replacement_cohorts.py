from __future__ import annotations

from typing import Any

from ..teachers.cohorts import TeacherCohortAnalyzer
from ..teachers.fleet_registry import TeacherBenchmarkFleetRegistry


class ReplacementCohortAnalyzer:
    def __init__(self, *, fleet_registry: TeacherBenchmarkFleetRegistry, cohorts: TeacherCohortAnalyzer):
        self.fleet_registry = fleet_registry
        self.cohorts = cohorts

    def build(
        self,
        *,
        subject: str,
        teacher_pair_id: str | None = None,
        budget_class: str | None = None,
        hardware_class: str | None = None,
        lineage: str | None = None,
        native_takeover_candidate_id: str | None = None,
    ) -> list[dict[str, Any]]:
        summaries: list[dict[str, Any]] = []
        for fleet_id in self.fleet_registry.preferred_fleet_ids(subject=subject, candidate_kind="native-takeover"):
            cohort = self.cohorts.build(
                fleet_id=fleet_id,
                window_id="medium",
                subject=subject,
                teacher_pair_id=teacher_pair_id,
                budget_class=budget_class,
                hardware_class=hardware_class,
                lineage=lineage,
                native_takeover_candidate_id=native_takeover_candidate_id,
            )
            summaries.append(cohort.model_dump(mode="json"))
        return summaries
