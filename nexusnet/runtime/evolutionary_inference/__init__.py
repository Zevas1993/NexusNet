from __future__ import annotations

from importlib import import_module


_EXPORT_MODULES = {
    "BoundedHostCalibrator": "calibration",
    "CalibrationLimits": "calibration",
    "CandidateFeasibilityEvaluator": "feasibility",
    "CapacityGate": "schemas",
    "DreamCycleEvidence": "schemas",
    "ExecutionFitEstimator": "feasibility",
    "ExecutionFitReconciliation": "schemas",
    "ExecutionFitReceipt": "schemas",
    "ExecutionFitReconciler": "feasibility",
    "ExecutionFitRequest": "schemas",
    "EvolutionMemory": "evolution_memory",
    "EvolutionaryInferenceFoundation": "foundation",
    "EvolutionaryInferenceSystem": "system",
    "ExecutionPlan": "schemas",
    "ExecutionPlanSynthesizer": "synthesis",
    "HardwareCapabilityDiscoverer": "hardware",
    "HardwareCapabilityGraph": "schemas",
    "HardwareCalibrationLab": "transfer",
    "HardwareNode": "schemas",
    "InferenceDreamLab": "dream_lab",
    "InferenceMethodRecord": "schemas",
    "InferencePrimitiveRegistry": "primitives",
    "ModelExecutionFingerprint": "schemas",
    "ParetoController": "pareto",
    "PlanBenchmark": "benchmark",
    "PlanEvidence": "schemas",
    "PlanPromotionController": "promotion",
    "RuntimeModelMetadata": "schemas",
    "RuntimeCapabilityProfile": "schemas",
    "RuntimeControlBinding": "schemas",
    "RuntimeControlReceipt": "schemas",
    "RuntimeObservation": "schemas",
    "SLOProfile": "schemas",
    "TransferEvidence": "schemas",
    "TransferExecutor": "transfer",
    "TransferRequest": "schemas",
    "UnsupportedModelFeatureError": "fingerprints",
    "WorkloadProfile": "schemas",
    "fingerprint_from_metadata": "fingerprints",
    "fingerprint_from_runtime_metadata": "fingerprints",
    "synthetic_model_fingerprint": "fingerprints",
}

__all__ = list(_EXPORT_MODULES)


def __getattr__(name: str) -> object:
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(f"{__name__}.{module_name}"), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted({*globals(), *__all__})
