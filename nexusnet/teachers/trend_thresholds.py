from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TeacherTrendThresholdSpec:
    trend_threshold_set_id: str
    version: int
    minimum_valid_runs: int
    maximum_variance: float
    minimum_weighted_score_mean: float
    minimum_weighted_score_slope: float
    maximum_recent_regression_spike: float
    maximum_disagreement_mean: float
    maximum_disagreement_slope: float
    minimum_passing_run_ratio: float
    canon_status: str = "LOCKED CANON"


class TeacherTrendThresholdRegistry:
    def __init__(self):
        self.default = TeacherTrendThresholdSpec(
            trend_threshold_set_id="teacher-trend-v2026-r1",
            version=1,
            minimum_valid_runs=3,
            maximum_variance=0.020,
            minimum_weighted_score_mean=0.76,
            minimum_weighted_score_slope=0.000,
            maximum_recent_regression_spike=0.100,
            maximum_disagreement_mean=0.55,
            maximum_disagreement_slope=0.080,
            minimum_passing_run_ratio=0.67,
        )
        self.subject_overrides = {
            "security": {
                "minimum_weighted_score_mean": 0.82,
                "maximum_variance": 0.015,
                "maximum_disagreement_mean": 0.45,
            },
            "critique": {
                "minimum_weighted_score_mean": 0.80,
                "maximum_variance": 0.018,
                "maximum_disagreement_mean": 0.40,
            },
            "toolsmith": {
                "minimum_weighted_score_mean": 0.79,
                "maximum_variance": 0.018,
            },
        }

    def resolve(self, subject: str) -> TeacherTrendThresholdSpec:
        override = self.subject_overrides.get(subject, {})
        return TeacherTrendThresholdSpec(
            trend_threshold_set_id=self.default.trend_threshold_set_id,
            version=self.default.version,
            minimum_valid_runs=int(override.get("minimum_valid_runs", self.default.minimum_valid_runs)),
            maximum_variance=float(override.get("maximum_variance", self.default.maximum_variance)),
            minimum_weighted_score_mean=float(override.get("minimum_weighted_score_mean", self.default.minimum_weighted_score_mean)),
            minimum_weighted_score_slope=float(override.get("minimum_weighted_score_slope", self.default.minimum_weighted_score_slope)),
            maximum_recent_regression_spike=float(override.get("maximum_recent_regression_spike", self.default.maximum_recent_regression_spike)),
            maximum_disagreement_mean=float(override.get("maximum_disagreement_mean", self.default.maximum_disagreement_mean)),
            maximum_disagreement_slope=float(override.get("maximum_disagreement_slope", self.default.maximum_disagreement_slope)),
            minimum_passing_run_ratio=float(override.get("minimum_passing_run_ratio", self.default.minimum_passing_run_ratio)),
            canon_status=self.default.canon_status,
        )

    def metadata(self) -> dict:
        return {
            "status_label": self.default.canon_status,
            "threshold_set_id": self.default.trend_threshold_set_id,
            "version": self.default.version,
            "minimum_valid_runs": self.default.minimum_valid_runs,
            "subject_overrides": self.subject_overrides,
        }
