from __future__ import annotations

from ..schemas import TeacherTrendScorecard
from .trend_thresholds import TeacherTrendThresholdSpec


def build_teacher_trend_scorecard(
    *,
    subject: str,
    benchmark_family: str,
    threshold_set_id: str,
    threshold_version: int,
    threshold_spec: TeacherTrendThresholdSpec,
    run_count: int,
    valid_run_count: int,
    weighted_score_mean: float,
    weighted_score_variance: float,
    weighted_score_slope: float,
    disagreement_mean: float,
    disagreement_slope: float,
    recent_regression_spike: bool,
    recent_scorecard_ids: list[str],
    recent_artifact_ids: list[str],
    metrics: dict,
) -> TeacherTrendScorecard:
    passing_run_ratio = metrics.get("passing_run_ratio", 0.0)
    stable = (
        valid_run_count >= threshold_spec.minimum_valid_runs
        and weighted_score_variance <= threshold_spec.maximum_variance
        and not recent_regression_spike
    )
    ready = stable and all(
        [
            weighted_score_mean >= threshold_spec.minimum_weighted_score_mean,
            weighted_score_slope >= threshold_spec.minimum_weighted_score_slope,
            disagreement_mean <= threshold_spec.maximum_disagreement_mean,
            disagreement_slope <= threshold_spec.maximum_disagreement_slope,
            passing_run_ratio >= threshold_spec.minimum_passing_run_ratio,
        ]
    )
    return TeacherTrendScorecard(
        subject=subject,
        benchmark_family_id=benchmark_family,
        threshold_set_id=threshold_set_id,
        trend_threshold_set_id=threshold_spec.trend_threshold_set_id,
        threshold_version=threshold_version,
        trend_version=threshold_spec.version,
        run_count=run_count,
        valid_run_count=valid_run_count,
        weighted_score_mean=weighted_score_mean,
        weighted_score_variance=weighted_score_variance,
        weighted_score_slope=weighted_score_slope,
        disagreement_mean=disagreement_mean,
        disagreement_slope=disagreement_slope,
        recent_regression_spike=recent_regression_spike,
        stable=stable,
        ready=ready,
        recent_scorecard_ids=recent_scorecard_ids,
        recent_artifact_ids=recent_artifact_ids,
        metrics=metrics,
        status_label=threshold_spec.canon_status,
    )
