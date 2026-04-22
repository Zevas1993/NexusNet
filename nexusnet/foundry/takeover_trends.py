from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from nexus.storage import NexusStore

from ..schemas import TakeoverTrendReport
from ..teachers.schema_versions import TeacherSchemaRegistry
from ..teachers.trends import recent_regression_spike, series_mean, series_slope, series_variance


@dataclass(frozen=True)
class TakeoverTrendThresholdSpec:
    trend_threshold_set_id: str
    version: int
    minimum_valid_runs: int
    maximum_variance: float
    minimum_weighted_score_mean: float
    minimum_weighted_score_slope: float
    maximum_recent_regression_spike: float
    maximum_dependency_ratio_slope: float
    minimum_native_generation_slope: float
    minimum_native_vs_primary_trend: float
    minimum_native_vs_secondary_trend: float
    maximum_rollback_risk_trend: float
    canon_status: str = "LOCKED CANON"


class TakeoverTrendAnalyzer:
    def __init__(self, *, store: NexusStore, artifacts_dir: Path, schema_registry: TeacherSchemaRegistry):
        self.store = store
        self.artifacts_dir = artifacts_dir
        self.schema_registry = schema_registry
        self.threshold = TakeoverTrendThresholdSpec(
            trend_threshold_set_id="takeover-trend-v2026-r1",
            version=1,
            minimum_valid_runs=3,
            maximum_variance=0.025,
            minimum_weighted_score_mean=0.78,
            minimum_weighted_score_slope=0.000,
            maximum_recent_regression_spike=0.100,
            maximum_dependency_ratio_slope=0.020,
            minimum_native_generation_slope=0.000,
            minimum_native_vs_primary_trend=0.000,
            minimum_native_vs_secondary_trend=0.000,
            maximum_rollback_risk_trend=0.000,
        )

    def build(self, *, subject: str, threshold_set_id: str, threshold_version: int, limit: int = 12) -> TakeoverTrendReport:
        scorecards = [
            item
            for item in reversed(self.store.list_takeover_scorecards(subject=subject, limit=500))
            if item.get("threshold_set_id") == threshold_set_id
        ][-limit:]
        weighted_scores = [float(item.get("weighted_score", 0.0) or 0.0) for item in scorecards]
        dependency_ratio = [float(item.get("metrics", {}).get("dependency_ratio", 0.0) or 0.0) for item in scorecards]
        native_generation = [float(item.get("metrics", {}).get("native_generation", 0.0) or 0.0) for item in scorecards]
        disagreement_delta = [float(item.get("metrics", {}).get("teacher_disagreement_delta", 0.0) or 0.0) for item in scorecards]
        native_vs_primary = [float(item.get("deltas", {}).get("native_vs_primary_delta", 0.0) or 0.0) for item in scorecards]
        native_vs_secondary = [float(item.get("deltas", {}).get("native_vs_secondary_delta", 0.0) or 0.0) for item in scorecards]
        rollback_risk = [0.0 if item.get("rollbackable") else 1.0 for item in scorecards]

        stable = (
            len(scorecards) >= self.threshold.minimum_valid_runs
            and series_variance(weighted_scores) <= self.threshold.maximum_variance
            and not recent_regression_spike(weighted_scores, self.threshold.maximum_recent_regression_spike)
        )
        ready = stable and all(
            [
                series_mean(weighted_scores) >= self.threshold.minimum_weighted_score_mean,
                series_slope(weighted_scores) >= self.threshold.minimum_weighted_score_slope,
                series_slope(dependency_ratio) <= self.threshold.maximum_dependency_ratio_slope,
                series_slope(native_generation) >= self.threshold.minimum_native_generation_slope,
                series_slope(native_vs_primary) >= self.threshold.minimum_native_vs_primary_trend,
                series_slope(native_vs_secondary) >= self.threshold.minimum_native_vs_secondary_trend,
                series_slope(rollback_risk) <= self.threshold.maximum_rollback_risk_trend,
            ]
        )
        trend = TakeoverTrendReport(
            subject=subject,
            threshold_set_id=threshold_set_id,
            trend_threshold_set_id=self.threshold.trend_threshold_set_id,
            threshold_version=threshold_version,
            trend_version=self.threshold.version,
            run_count=len(scorecards),
            valid_run_count=len(scorecards),
            weighted_score_mean=series_mean(weighted_scores),
            weighted_score_variance=series_variance(weighted_scores),
            weighted_score_slope=series_slope(weighted_scores),
            dependency_ratio_trend=series_slope(dependency_ratio),
            native_generation_trend=series_slope(native_generation),
            teacher_disagreement_delta_trend=series_slope(disagreement_delta),
            native_vs_primary_trend=series_slope(native_vs_primary),
            native_vs_secondary_trend=series_slope(native_vs_secondary),
            rollback_risk_trend=series_slope(rollback_risk),
            recent_regression_spike=recent_regression_spike(weighted_scores, self.threshold.maximum_recent_regression_spike),
            stable=stable,
            ready=ready,
            recent_scorecard_ids=[item.get("scorecard_id") for item in scorecards],
            latest_teacher_evidence_bundle_id=scorecards[-1].get("teacher_evidence_bundle_id") if scorecards else None,
            metrics={
                "minimum_valid_runs": self.threshold.minimum_valid_runs,
                "recent_weighted_scores": weighted_scores,
                "recent_dependency_ratio": dependency_ratio,
                "recent_native_generation": native_generation,
            },
            status_label=self.threshold.canon_status,
        ).model_copy(update=self.schema_registry.envelope("takeover-trend-report"))
        return self.persist(trend)

    def persist(self, trend: TakeoverTrendReport) -> TakeoverTrendReport:
        relative = f"foundry/takeover-trends/{trend.subject}/{trend.trend_id}.json"
        payload = trend.model_dump(mode="json")
        path = self.store.write_artifact(relative, json.dumps(payload, indent=2))
        updated = trend.model_copy(update={"artifact_path": path})
        self.store.save_takeover_trend_report(updated.model_dump(mode="json"))
        return updated

    def metadata(self) -> dict:
        return {
            "status_label": self.threshold.canon_status,
            "trend_threshold_set_id": self.threshold.trend_threshold_set_id,
            "version": self.threshold.version,
            "minimum_valid_runs": self.threshold.minimum_valid_runs,
        }
