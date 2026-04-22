from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.storage import NexusStore

from ..schemas import TeacherBenchmarkFleetSummary, TeacherCohortScorecard
from .cohort_scorecards import build_teacher_cohort_scorecard
from .cohort_thresholds import TeacherCohortThresholdRegistry
from .fleets import TeacherBenchmarkFleetAnalyzer
from .schema_versions import TeacherSchemaRegistry
from .trends import recent_regression_spike, series_mean, series_slope, series_variance


class TeacherCohortAnalyzer:
    def __init__(
        self,
        *,
        store: NexusStore,
        artifacts_dir: Path,
        fleet_analyzer: TeacherBenchmarkFleetAnalyzer,
        threshold_registry: TeacherCohortThresholdRegistry,
        schema_registry: TeacherSchemaRegistry,
    ):
        self.store = store
        self.artifacts_dir = artifacts_dir
        self.fleet_analyzer = fleet_analyzer
        self.threshold_registry = threshold_registry
        self.schema_registry = schema_registry

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
        native_takeover_candidate_id: str | None = None,
    ) -> TeacherCohortScorecard:
        fleet_summary = self.fleet_analyzer.build(
            fleet_id=fleet_id,
            window_id=window_id,
            subject=subject,
            teacher_pair_id=teacher_pair_id,
            budget_class=budget_class,
            output_form=output_form,
            risk_tier=risk_tier,
            locality=locality,
            hardware_class=hardware_class,
            lineage=lineage,
        )
        bundles = self.fleet_analyzer.matching_bundles(
            fleet_id=fleet_id,
            window_id=fleet_summary.window_id,
            subject=subject,
            teacher_pair_id=teacher_pair_id,
            budget_class=budget_class,
            output_form=output_form,
            risk_tier=risk_tier,
            locality=locality,
            hardware_class=hardware_class,
            lineage=lineage,
        )
        bundle_ids = {bundle.get("bundle_id") for bundle in bundles}
        takeover_scorecards = [
            scorecard
            for scorecard in self.store.list_takeover_scorecards(subject=subject, limit=500)
            if (
                not bundle_ids
                or scorecard.get("teacher_evidence_bundle_id") in bundle_ids
                or scorecard.get("bundle_id") in bundle_ids
            )
        ]
        if native_takeover_candidate_id:
            bundle_ids = {
                bundle.get("bundle_id")
                for bundle in bundles
                if bundle.get("native_takeover_candidate_id") == native_takeover_candidate_id
            }
            takeover_scorecards = [
                scorecard
                for scorecard in takeover_scorecards
                if scorecard.get("teacher_evidence_bundle_id") in bundle_ids or scorecard.get("bundle_id") in bundle_ids
            ]

        weighted_scores = [float(item.get("weighted_score", 0.0) or 0.0) for item in takeover_scorecards] or list(
            fleet_summary.metrics.get("recent_weighted_scores", [])
        )
        disagreement_series = [float(bundle.get("metrics", {}).get("teacher_disagreement_delta", 0.0) or 0.0) for bundle in bundles]
        contamination_scores = [
            float(scorecard.get("metrics", {}).get("dream_contamination_sensitivity", 0.0) or 0.0)
            for bundle in bundles
            for scorecard in bundle.get("scorecards", [])
        ]
        contamination_risk = [round(max(0.0, 1.0 - value), 4) for value in contamination_scores]
        rollback_risk = [
            0.0 if scorecard.get("rollbackable", False) else 1.0
            for scorecard in takeover_scorecards
        ]
        outperformance = [
            1.0
            if float(scorecard.get("deltas", {}).get("native_vs_primary_delta", 0.0) or 0.0) >= 0.0
            and float(scorecard.get("deltas", {}).get("native_vs_secondary_delta", 0.0) or 0.0) >= 0.0
            else 0.0
            for scorecard in takeover_scorecards
        ]
        if not outperformance:
            outperformance = [fleet_summary.passing_run_ratio] if fleet_summary.run_count else []
        hardware_buckets: dict[str, list[float]] = {}
        for bundle in bundles:
            bucket = str(bundle.get("metrics", {}).get("hardware_class", "unknown"))
            scores = [float(scorecard.get("weighted_score", 0.0) or 0.0) for scorecard in bundle.get("scorecards", [])]
            hardware_buckets.setdefault(bucket, []).extend(scores)
        hardware_means = [series_mean(scores) for scores in hardware_buckets.values() if scores]
        hardware_sensitivity = round((max(hardware_means) - min(hardware_means)), 4) if len(hardware_means) > 1 else 0.0

        threshold_subject = subject or (bundles[-1].get("subject") if bundles else "general")
        threshold = self.threshold_registry.resolve(threshold_subject)
        variance = series_variance(weighted_scores)
        regression_spikes = int(recent_regression_spike(weighted_scores, 0.10))
        stability_score = round(
            max(
                0.0,
                min(
                    1.0,
                    (
                        fleet_summary.passing_run_ratio
                        + max(0.0, 1.0 - min(variance / max(threshold.maximum_variance, 0.001), 1.0))
                        + max(0.0, 1.0 - min(series_mean(rollback_risk), 1.0))
                    )
                    / 3.0,
                ),
            ),
            3,
        )
        stable = (
            fleet_summary.ready
            and fleet_summary.valid_run_count >= threshold.minimum_valid_runs
            and variance <= threshold.maximum_variance
            and regression_spikes <= threshold.maximum_regression_spikes
        )
        ready = stable and all(
            [
                stability_score >= threshold.minimum_stability_score,
                series_mean(outperformance) >= threshold.minimum_outperformance_consistency,
                series_mean(rollback_risk) <= threshold.maximum_rollback_risk,
                series_mean(contamination_risk) <= threshold.maximum_dream_contamination_sensitivity if contamination_risk else True,
                hardware_sensitivity <= threshold.maximum_hardware_sensitivity,
            ]
        )
        cohort = build_teacher_cohort_scorecard(
            cohort_key="::".join(
                item
                for item in [
                    fleet_id,
                    fleet_summary.window_id,
                    subject or "all-subjects",
                    teacher_pair_id or "all-pairs",
                    hardware_class or "all-hardware",
                    lineage or "all-lineage",
                ]
                if item
            ),
            fleet_id=fleet_id,
            window_id=fleet_summary.window_id,
            threshold_set_id=threshold.threshold_set_id,
            threshold_version=threshold.version,
            subject=subject,
            teacher_pair_id=teacher_pair_id,
            budget_class=budget_class,
            hardware_class=hardware_class,
            lineage=lineage,
            run_count=max(fleet_summary.run_count, len(takeover_scorecards)),
            valid_run_count=max(fleet_summary.valid_run_count, len(takeover_scorecards)),
            stability_score=stability_score,
            variance=variance,
            disagreement_trend=series_slope(disagreement_series),
            outperformance_consistency=series_mean(outperformance),
            regression_spike_count=regression_spikes,
            rollback_risk=series_mean(rollback_risk),
            dream_contamination_sensitivity=series_mean(contamination_risk),
            hardware_sensitivity=hardware_sensitivity,
            stable=stable,
            ready=ready,
            fleet_summary_ids=[fleet_summary.summary_id],
            takeover_scorecard_ids=[item.get("scorecard_id") for item in takeover_scorecards],
            metrics={
                "fleet_summary": fleet_summary.model_dump(mode="json"),
                "hardware_buckets": hardware_buckets,
                "recent_outperformance": outperformance,
                "recent_rollback_risk": rollback_risk,
                "recent_contamination_scores": contamination_scores,
                "recent_contamination_risk": contamination_risk,
            },
        ).model_copy(update=self.schema_registry.envelope("teacher-cohort-scorecard"))
        return self.persist(cohort)

    def persist(self, cohort: TeacherCohortScorecard) -> TeacherCohortScorecard:
        relative = f"teachers/cohorts/{cohort.fleet_id}/{cohort.window_id}/{cohort.cohort_id}.json"
        payload = cohort.model_dump(mode="json")
        path = self.store.write_artifact(relative, json.dumps(payload, indent=2))
        updated = cohort.model_copy(update={"artifact_path": path})
        self.store.save_teacher_cohort_scorecard(updated.model_dump(mode="json"))
        return updated
