from __future__ import annotations

from typing import Any


class TeacherDeltaAnalyzer:
    def compare(self, *, teacher_evidence: dict[str, Any], dependency_ratio: float, native_generation: float) -> dict[str, float]:
        disagreement_delta = float(teacher_evidence.get("teacher_disagreement_delta", 0.0) or 0.0)
        primary_gap = round(native_generation - dependency_ratio, 3)
        secondary_baseline = max(0.0, min(1.0, dependency_ratio - (disagreement_delta / 2.0)))
        secondary_gap = round(native_generation - secondary_baseline, 3)
        scorecards = list(teacher_evidence.get("scorecards", []))
        arbitration_baseline = round(
            sum(float(item.get("weighted_score", 0.0) or 0.0) for item in scorecards) / len(scorecards),
            3,
        ) if scorecards else secondary_baseline
        historical_baseline = round(
            sum(float((item.get("thresholds", {}) or {}).get("weighted_score_min", 0.74) or 0.74) for item in scorecards) / len(scorecards),
            3,
        ) if scorecards else 0.74
        return {
            "teacher_disagreement_delta": disagreement_delta,
            "native_vs_primary_delta": primary_gap,
            "native_vs_secondary_delta": secondary_gap,
            "native_vs_arbitration_delta": round(native_generation - arbitration_baseline, 3),
            "native_vs_historical_baseline_delta": round(native_generation - historical_baseline, 3),
        }
