from .backend_selector import QESBackendSelector
from .benchmark_matrix import QESBenchmarkMatrix
from .profile_registry import QESProfileRegistry
from .runtime_metrics import QESRuntimeMetrics

__all__ = [
    "AITuneAdapter",
    "AITuneSupportedLaneMatrix",
    "AITuneCapabilityInspector",
    "AITuneQESProvider",
    "AITuneValidationRunner",
    "AITuneValidationMatrix",
    "QESBackendSelector",
    "QESBenchmarkMatrix",
    "QESProfileRegistry",
    "QESRuntimeMetrics",
]


def __getattr__(name: str):
    if name == "AITuneAdapter":
        from .aitune_adapter import AITuneAdapter

        return AITuneAdapter
    if name == "AITuneSupportedLaneMatrix":
        from .aitune_matrix import AITuneSupportedLaneMatrix

        return AITuneSupportedLaneMatrix
    if name == "AITuneCapabilityInspector":
        from .aitune_capability import AITuneCapabilityInspector

        return AITuneCapabilityInspector
    if name == "AITuneQESProvider":
        from .aitune_provider import AITuneQESProvider

        return AITuneQESProvider
    if name == "AITuneValidationRunner":
        from .aitune_runner import AITuneValidationRunner

        return AITuneValidationRunner
    if name == "AITuneValidationMatrix":
        from .aitune_validation import AITuneValidationMatrix

        return AITuneValidationMatrix
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
