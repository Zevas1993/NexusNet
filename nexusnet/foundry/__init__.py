from __future__ import annotations

from importlib import import_module

__all__ = [
    "FoundryBenchmarkSuite",
    "FoundryRefinery",
    "FoundryRetirementHooks",
    "CohortTakeoverAnalyzer",
    "NativePromotionGate",
    "ReplacementCohortAnalyzer",
    "ReplacementGovernanceAdvisor",
    "ReplacementReadinessAdvisor",
    "TakeoverScorecardBuilder",
    "TakeoverThresholdRegistry",
    "TakeoverTrendAnalyzer",
    "TeacherDeltaAnalyzer",
    "TeacherReplacementAdvisor",
]

_EXPORTS = {
    "FoundryBenchmarkSuite": (".benchmarks", "FoundryBenchmarkSuite"),
    "CohortTakeoverAnalyzer": (".cohort_takeover", "CohortTakeoverAnalyzer"),
    "NativePromotionGate": (".promotion", "NativePromotionGate"),
    "FoundryRefinery": (".refinery", "FoundryRefinery"),
    "FoundryRetirementHooks": (".retirement", "FoundryRetirementHooks"),
    "ReplacementCohortAnalyzer": (".replacement_cohorts", "ReplacementCohortAnalyzer"),
    "ReplacementGovernanceAdvisor": (".replacement_governance", "ReplacementGovernanceAdvisor"),
    "ReplacementReadinessAdvisor": (".replacement_readiness", "ReplacementReadinessAdvisor"),
    "TakeoverScorecardBuilder": (".takeover_scorecard", "TakeoverScorecardBuilder"),
    "TakeoverThresholdRegistry": (".takeover_thresholds", "TakeoverThresholdRegistry"),
    "TakeoverTrendAnalyzer": (".takeover_trends", "TakeoverTrendAnalyzer"),
    "TeacherDeltaAnalyzer": (".teacher_delta", "TeacherDeltaAnalyzer"),
    "TeacherReplacementAdvisor": (".teacher_replacement", "TeacherReplacementAdvisor"),
}


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module_name, attribute_name = _EXPORTS[name]
    module = import_module(module_name, __name__)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value
