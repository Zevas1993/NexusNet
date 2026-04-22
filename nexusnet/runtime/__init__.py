__all__ = ["AdaptiveSystemProfiler", "BrainRuntimeRegistry", "HardwareScanner"]


def __getattr__(name: str):
    if name == "AdaptiveSystemProfiler":
        from .adaptive_system_profiler import AdaptiveSystemProfiler

        return AdaptiveSystemProfiler
    if name == "BrainRuntimeRegistry":
        from .registry import BrainRuntimeRegistry

        return BrainRuntimeRegistry
    if name == "HardwareScanner":
        from .hardware_scanner import HardwareScanner

        return HardwareScanner
    raise AttributeError(name)
