from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TakeoverThresholdSpec:
    threshold_set_id: str
    version: int
    weighted_score_min: float
    metric_rules: dict[str, dict[str, float | str]]


class TakeoverThresholdRegistry:
    def __init__(self):
        self.default = TakeoverThresholdSpec(
            threshold_set_id="takeover-v2026-r1",
            version=1,
            weighted_score_min=0.78,
            metric_rules={
                "dependency_ratio": {"operator": "max", "value": 0.35},
                "native_generation": {"operator": "min", "value": 0.65},
                "takeover_readiness": {"operator": "min", "value": 0.72},
                "teacher_disagreement_delta": {"operator": "max", "value": 0.55},
                "native_vs_primary_delta": {"operator": "min", "value": 0.05},
                "native_vs_secondary_delta": {"operator": "min", "value": 0.00},
                "takeover_rollbackability": {"operator": "min", "value": 1.00},
            },
        )

    def resolve(self) -> TakeoverThresholdSpec:
        return self.default
