from __future__ import annotations

import json
import re
from pathlib import Path

from nexus.storage import NexusStore

from ..schemas import TeacherTrendScorecard
from .schema_versions import TeacherSchemaRegistry
from .trend_scorecards import build_teacher_trend_scorecard
from .trend_thresholds import TeacherTrendThresholdRegistry

_PATH_SAFE = re.compile(r"[^A-Za-z0-9_.-]+")


def series_mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 3) if values else 0.0


def series_variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return round(sum((value - mean) ** 2 for value in values) / len(values), 4)


def series_slope(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    x_values = list(range(len(values)))
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(values) / len(values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
    denominator = sum((x - x_mean) ** 2 for x in x_values) or 1.0
    return round(numerator / denominator, 4)


def recent_regression_spike(values: list[float], threshold: float) -> bool:
    if len(values) < 2:
        return False
    prior_peak = max(values[:-1])
    return (prior_peak - values[-1]) > threshold


class TeacherTrendAnalyzer:
    def __init__(
        self,
        *,
        store: NexusStore,
        artifacts_dir: Path,
        schema_registry: TeacherSchemaRegistry,
        threshold_registry: TeacherTrendThresholdRegistry | None = None,
    ):
        self.store = store
        self.artifacts_dir = artifacts_dir
        self.schema_registry = schema_registry
        self.threshold_registry = threshold_registry or TeacherTrendThresholdRegistry()

    def build(
        self,
        *,
        subject: str,
        benchmark_family: str,
        threshold_set_id: str,
        threshold_version: int,
        limit: int = 12,
    ) -> TeacherTrendScorecard:
        scorecards = [
            item
            for item in reversed(self.store.list_teacher_scorecards(subject=subject, limit=500))
            if item.get("benchmark_family_id") == benchmark_family and item.get("threshold_set_id") == threshold_set_id
        ][-limit:]
        disagreements = [
            item
            for item in reversed(self.store.list_teacher_disagreement_artifacts(subject=subject, limit=500))
            if item.get("benchmark_family") == benchmark_family or not item.get("benchmark_family")
        ][-limit:]

        weighted_scores = [float(item.get("weighted_score", 0.0) or 0.0) for item in scorecards]
        pass_bools = [bool(item.get("passed")) for item in scorecards]
        disagreement_values = [
            float(item.get("disagreement_severity", item.get("metrics", {}).get("disagreement_delta", 0.0)) or 0.0)
            for item in disagreements
        ]
        threshold = self.threshold_registry.resolve(subject)
        metrics = {
            "passing_run_ratio": round((sum(1 for passed in pass_bools if passed) / len(pass_bools)), 3) if pass_bools else 0.0,
            "minimum_valid_runs": threshold.minimum_valid_runs,
            "recent_weighted_scores": weighted_scores,
            "recent_disagreement": disagreement_values,
        }
        trend = build_teacher_trend_scorecard(
            subject=subject,
            benchmark_family=benchmark_family,
            threshold_set_id=threshold_set_id,
            threshold_version=threshold_version,
            threshold_spec=threshold,
            run_count=len(scorecards),
            valid_run_count=len(scorecards),
            weighted_score_mean=series_mean(weighted_scores),
            weighted_score_variance=series_variance(weighted_scores),
            weighted_score_slope=series_slope(weighted_scores),
            disagreement_mean=series_mean(disagreement_values),
            disagreement_slope=series_slope(disagreement_values),
            recent_regression_spike=recent_regression_spike(weighted_scores, threshold.maximum_recent_regression_spike),
            recent_scorecard_ids=[item.get("scorecard_id") for item in scorecards],
            recent_artifact_ids=[item.get("artifact_id") for item in disagreements],
            metrics=metrics,
        ).model_copy(update=self.schema_registry.envelope("teacher-trend-scorecard"))
        return self.persist(trend)

    def persist(self, trend: TeacherTrendScorecard) -> TeacherTrendScorecard:
        family_segment = _PATH_SAFE.sub("-", trend.benchmark_family_id).strip("-") or "benchmark-family"
        relative = f"teachers/trends/{trend.subject}/{family_segment}/{trend.trend_id}.json"
        payload = trend.model_dump(mode="json")
        path = self.store.write_artifact(relative, json.dumps(payload, indent=2))
        updated = trend.model_copy(update={"artifact_path": path})
        self.store.save_teacher_trend_scorecard(updated.model_dump(mode="json"))
        return updated

    def latest(
        self,
        *,
        subject: str,
        benchmark_family: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        return self.store.list_teacher_trend_scorecards(subject=subject, benchmark_family_id=benchmark_family, limit=limit)
