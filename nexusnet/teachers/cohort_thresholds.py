from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TeacherCohortThresholdSpec:
    threshold_set_id: str
    version: int
    minimum_valid_runs: int
    maximum_variance: float
    minimum_stability_score: float
    minimum_outperformance_consistency: float
    maximum_regression_spikes: int
    maximum_rollback_risk: float
    maximum_dream_contamination_sensitivity: float
    maximum_hardware_sensitivity: float
    canon_status: str = "LOCKED CANON"


class TeacherCohortThresholdRegistry:
    def __init__(self):
        self.default = TeacherCohortThresholdSpec(
            threshold_set_id="teacher-cohort-v2026-r1",
            version=1,
            minimum_valid_runs=5,
            maximum_variance=0.030,
            minimum_stability_score=0.70,
            minimum_outperformance_consistency=0.67,
            maximum_regression_spikes=0,
            maximum_rollback_risk=0.34,
            maximum_dream_contamination_sensitivity=0.35,
            maximum_hardware_sensitivity=0.20,
        )
        self.subject_overrides = {
            "security": {
                "minimum_valid_runs": 6,
                "maximum_variance": 0.020,
                "minimum_stability_score": 0.78,
                "maximum_dream_contamination_sensitivity": 0.22,
            },
            "critique": {
                "maximum_variance": 0.024,
                "minimum_outperformance_consistency": 0.72,
            },
            "toolsmith": {
                "minimum_stability_score": 0.74,
                "maximum_hardware_sensitivity": 0.16,
            },
        }

    def resolve(self, subject: str) -> TeacherCohortThresholdSpec:
        override = self.subject_overrides.get(subject, {})
        return TeacherCohortThresholdSpec(
            threshold_set_id=self.default.threshold_set_id,
            version=self.default.version,
            minimum_valid_runs=int(override.get("minimum_valid_runs", self.default.minimum_valid_runs)),
            maximum_variance=float(override.get("maximum_variance", self.default.maximum_variance)),
            minimum_stability_score=float(override.get("minimum_stability_score", self.default.minimum_stability_score)),
            minimum_outperformance_consistency=float(override.get("minimum_outperformance_consistency", self.default.minimum_outperformance_consistency)),
            maximum_regression_spikes=int(override.get("maximum_regression_spikes", self.default.maximum_regression_spikes)),
            maximum_rollback_risk=float(override.get("maximum_rollback_risk", self.default.maximum_rollback_risk)),
            maximum_dream_contamination_sensitivity=float(
                override.get("maximum_dream_contamination_sensitivity", self.default.maximum_dream_contamination_sensitivity)
            ),
            maximum_hardware_sensitivity=float(override.get("maximum_hardware_sensitivity", self.default.maximum_hardware_sensitivity)),
            canon_status=self.default.canon_status,
        )

    def metadata(self) -> dict:
        return {
            "status_label": self.default.canon_status,
            "threshold_set_id": self.default.threshold_set_id,
            "version": self.default.version,
            "minimum_valid_runs": self.default.minimum_valid_runs,
            "subject_overrides": self.subject_overrides,
        }
