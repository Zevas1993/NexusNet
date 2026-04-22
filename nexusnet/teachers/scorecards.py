from __future__ import annotations

from typing import Any

from ..schemas import TeacherScorecard
from .benchmarks import TeacherBenchmarkRegistry
from .thresholds import TeacherThresholdSpec


def build_teacher_scorecard(
    *,
    subject: str,
    benchmark_family: str,
    metrics: dict[str, float],
    benchmark_registry: TeacherBenchmarkRegistry,
    threshold_spec: TeacherThresholdSpec,
) -> TeacherScorecard:
    family = benchmark_registry.family(subject, benchmark_family)
    weight_profile = dict(family.get("default_dimensions", {}))
    total_weight = sum(weight_profile.values()) or 1.0
    normalized_contributions: dict[str, float] = {}
    failure_reasons: list[str] = []
    passed = True

    for dimension, rule in threshold_spec.metric_rules.items():
        value = _as_float(metrics.get(dimension, 0.0))
        operator = str(rule.get("operator", "min"))
        threshold = _as_float(rule.get("value", 0.0))
        dimension_passed, normalized = _evaluate_dimension(value=value, operator=operator, threshold=threshold)
        normalized_contributions[dimension] = normalized
        if not dimension_passed:
            passed = False
            failure_reasons.append(
                f"{dimension} failed {operator} threshold {threshold:.2f} with value {value:.2f}"
            )

    weighted_score = round(
        sum(normalized_contributions.get(name, _as_float(metrics.get(name, 0.0))) * weight for name, weight in weight_profile.items())
        / total_weight,
        3,
    )
    if weighted_score < threshold_spec.weighted_score_min:
        passed = False
        failure_reasons.append(
            f"weighted_score below threshold {threshold_spec.weighted_score_min:.2f} ({weighted_score:.2f})"
        )

    return TeacherScorecard(
        subject=subject,
        benchmark_family_id=benchmark_family,
        threshold_set_id=threshold_spec.threshold_set_id,
        threshold_version=threshold_spec.version,
        weighted_score=weighted_score,
        passed=passed,
        metrics={key: round(_as_float(value), 3) for key, value in metrics.items()},
        thresholds={
            "weighted_score_min": threshold_spec.weighted_score_min,
            "metric_rules": threshold_spec.metric_rules,
            "weight_profile": weight_profile,
        },
        weight_profile=weight_profile,
        failure_reasons=failure_reasons,
        status_label=threshold_spec.canon_status,
    )


def _evaluate_dimension(*, value: float, operator: str, threshold: float) -> tuple[bool, float]:
    clamped_value = max(0.0, min(value, 1.0))
    if operator == "max":
        return value <= threshold, round(max(0.0, min(1.0, 1.0 - clamped_value)), 3)
    if operator == "eq":
        return value == threshold, 1.0 if value == threshold else 0.0
    return value >= threshold, round(clamped_value, 3)


def _as_float(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if value is None:
        return 0.0
    return float(value)
