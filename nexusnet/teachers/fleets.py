from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.storage import NexusStore

from ..schemas import TeacherBenchmarkFleetSummary
from .fleet_registry import TeacherBenchmarkFleetRegistry
from .fleet_windows import TeacherFleetWindowRegistry
from .schema_versions import TeacherSchemaRegistry
from .trend_thresholds import TeacherTrendThresholdRegistry
from .trends import recent_regression_spike, series_mean, series_variance


def _bundle_lineage(bundle: dict[str, Any]) -> str:
    if bundle.get("dream_derived") and bundle.get("live_derived"):
        return "blended-derived"
    if bundle.get("dream_derived"):
        return "dream-derived"
    return "live-derived"


def _teacher_pair_id(bundle: dict[str, Any]) -> str | None:
    roles = bundle.get("selected_teacher_roles", {})
    primary = roles.get("primary")
    secondary = roles.get("secondary")
    if primary and secondary:
        return f"{primary}::{secondary}"
    return primary


class TeacherBenchmarkFleetAnalyzer:
    def __init__(
        self,
        *,
        store: NexusStore,
        artifacts_dir: Path,
        fleet_registry: TeacherBenchmarkFleetRegistry,
        window_registry: TeacherFleetWindowRegistry,
        schema_registry: TeacherSchemaRegistry,
        trend_thresholds: TeacherTrendThresholdRegistry | None = None,
    ):
        self.store = store
        self.artifacts_dir = artifacts_dir
        self.fleet_registry = fleet_registry
        self.window_registry = window_registry
        self.schema_registry = schema_registry
        self.trend_thresholds = trend_thresholds or TeacherTrendThresholdRegistry()

    def matching_bundles(
        self,
        *,
        fleet_id: str,
        window_id: str | None = None,
        subject: str | None = None,
        teacher_pair_id: str | None = None,
        budget_class: str | None = None,
        output_form: str | None = None,
        risk_tier: str | None = None,
        locality: str | None = None,
        hardware_class: str | None = None,
        lineage: str | None = None,
    ) -> list[dict[str, Any]]:
        fleet = self.fleet_registry.resolve(fleet_id)
        window = self.window_registry.resolve(window_id)
        bundles = self.store.list_teacher_evidence_bundles(limit=2000)
        output: list[dict[str, Any]] = []
        for bundle in bundles:
            if subject and bundle.get("subject") != subject:
                continue
            if not subject and fleet.subjects and bundle.get("subject") not in fleet.subjects:
                continue
            if teacher_pair_id and _teacher_pair_id(bundle) != teacher_pair_id:
                continue
            bundle_lineage = _bundle_lineage(bundle)
            if lineage and bundle_lineage != lineage:
                continue
            metrics = bundle.get("metrics", {})
            if budget_class and metrics.get("budget_class") != budget_class:
                continue
            if output_form and metrics.get("output_form") != output_form:
                continue
            if risk_tier and metrics.get("risk_tier") != risk_tier:
                continue
            if locality and metrics.get("locality") != locality and bundle.get("registry_layer") != locality:
                continue
            if hardware_class and metrics.get("hardware_class") != hardware_class:
                continue
            bundle_families = set(bundle.get("benchmark_families", []))
            if fleet.benchmark_families and not bundle_families.intersection(fleet.benchmark_families):
                continue
            output.append(bundle)
        return output[: window.lookback_runs]

    def build(
        self,
        *,
        fleet_id: str,
        window_id: str | None = None,
        subject: str | None = None,
        teacher_pair_id: str | None = None,
        budget_class: str | None = None,
        output_form: str | None = None,
        risk_tier: str | None = None,
        locality: str | None = None,
        hardware_class: str | None = None,
        lineage: str | None = None,
    ) -> TeacherBenchmarkFleetSummary:
        fleet = self.fleet_registry.resolve(fleet_id)
        window = self.window_registry.resolve(window_id)
        bundles = self.matching_bundles(
            fleet_id=fleet_id,
            window_id=window.window_id,
            subject=subject,
            teacher_pair_id=teacher_pair_id,
            budget_class=budget_class,
            output_form=output_form,
            risk_tier=risk_tier,
            locality=locality,
            hardware_class=hardware_class,
            lineage=lineage,
        )
        scorecards = [
            scorecard
            for bundle in bundles
            for scorecard in bundle.get("scorecards", [])
            if not fleet.benchmark_families or scorecard.get("benchmark_family_id") in set(fleet.benchmark_families)
        ]
        weighted_scores = [float(item.get("weighted_score", 0.0) or 0.0) for item in scorecards]
        passing = [bool(item.get("passed")) for item in scorecards]
        disagreement = [float(bundle.get("metrics", {}).get("teacher_disagreement_delta", 0.0) or 0.0) for bundle in bundles]
        threshold_subject = subject or (bundles[-1].get("subject") if bundles else (fleet.subjects[0] if fleet.subjects else "general"))
        threshold = self.trend_thresholds.resolve(threshold_subject)
        passing_ratio = round((sum(1 for item in passing if item) / len(passing)), 3) if passing else 0.0
        stable = (
            len(scorecards) >= window.minimum_sample_count
            and series_variance(weighted_scores) <= threshold.maximum_variance
            and not recent_regression_spike(weighted_scores, threshold.maximum_recent_regression_spike)
        )
        ready = stable and series_mean(weighted_scores) >= threshold.minimum_weighted_score_mean and passing_ratio >= threshold.minimum_passing_run_ratio
        threshold_set_id = next((item.get("threshold_set_id") for item in scorecards if item.get("threshold_set_id")), fleet.threshold_set_id)
        threshold_version = int(next((item.get("threshold_version", 1) for item in scorecards if item.get("threshold_version") is not None), 1))
        summary = TeacherBenchmarkFleetSummary(
            fleet_id=fleet_id,
            window_id=window.window_id,
            threshold_set_id=str(threshold_set_id),
            threshold_version=threshold_version,
            subject=subject,
            teacher_pair_id=teacher_pair_id,
            budget_class=budget_class,
            output_form=output_form,
            risk_tier=risk_tier,
            locality=locality,
            hardware_class=hardware_class,
            lineage=lineage,
            run_count=len(scorecards),
            valid_run_count=len(scorecards),
            weighted_score_mean=series_mean(weighted_scores),
            weighted_score_variance=series_variance(weighted_scores),
            passing_run_ratio=passing_ratio,
            disagreement_mean=series_mean(disagreement),
            recent_regression_spike=recent_regression_spike(weighted_scores, threshold.maximum_recent_regression_spike),
            stable=stable,
            ready=ready,
            scorecard_ids=[item.get("scorecard_id") for item in scorecards],
            evidence_bundle_ids=[bundle.get("bundle_id") for bundle in bundles],
            metrics={
                "fleet_description": fleet.description,
                "fleet_canon_status": fleet.canon_status,
                "window": {
                    "window_id": window.window_id,
                    "lookback_runs": window.lookback_runs,
                    "minimum_sample_count": window.minimum_sample_count,
                    "maximum_age_days": window.maximum_age_days,
                },
                "families": fleet.benchmark_families,
                "subjects": fleet.subjects,
                "recent_weighted_scores": weighted_scores,
                "recent_disagreement": disagreement,
            },
        ).model_copy(update=self.schema_registry.envelope("teacher-benchmark-fleet-summary"))
        return self.persist(summary)

    def persist(self, summary: TeacherBenchmarkFleetSummary) -> TeacherBenchmarkFleetSummary:
        relative = f"teachers/fleets/{summary.fleet_id}/{summary.window_id}/{summary.summary_id}.json"
        payload = summary.model_dump(mode="json")
        path = self.store.write_artifact(relative, json.dumps(payload, indent=2))
        updated = summary.model_copy(update={"artifact_path": path})
        self.store.save_teacher_benchmark_fleet_summary(updated.model_dump(mode="json"))
        return updated
