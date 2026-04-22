from __future__ import annotations

from typing import Any

from ..schemas import TakeoverScorecard
from .takeover_thresholds import TakeoverThresholdRegistry


class TakeoverScorecardBuilder:
    def __init__(self):
        self.thresholds = TakeoverThresholdRegistry()

    def build(
        self,
        *,
        subject: str,
        teacher_evidence_bundle_id: str | None,
        metrics: dict[str, Any],
        deltas: dict[str, float],
    ) -> TakeoverScorecard:
        threshold = self.thresholds.resolve()
        weight_profile = {
            "dependency_ratio": 0.16,
            "native_generation": 0.18,
            "takeover_readiness": 0.22,
            "teacher_disagreement_delta": 0.10,
            "native_vs_primary_delta": 0.18,
            "native_vs_secondary_delta": 0.08,
            "takeover_rollbackability": 0.08,
        }
        weighted = 0.0
        total = sum(weight_profile.values())
        passed = True
        for name, weight in weight_profile.items():
            value = float((deltas if name in deltas else metrics).get(name, 0.0) or 0.0)
            rule = threshold.metric_rules[name]
            operator = str(rule["operator"])
            limit = float(rule["value"])
            if operator == "max":
                passed = passed and value <= limit
                normalized = max(0.0, min(1.0, 1.0 - value))
            else:
                passed = passed and value >= limit
                normalized = max(0.0, min(1.0, value))
            weighted += normalized * weight
        weighted_score = round(weighted / total, 3)
        if weighted_score < threshold.weighted_score_min:
            passed = False
        return TakeoverScorecard(
            subject=subject,
            teacher_evidence_bundle_id=teacher_evidence_bundle_id,
            threshold_set_id=threshold.threshold_set_id,
            threshold_version=threshold.version,
            weighted_score=weighted_score,
            passed=passed,
            metrics={key: round(float(value), 3) for key, value in metrics.items()},
            deltas=deltas,
            rollbackable=bool(metrics.get("takeover_rollbackability")),
        )
