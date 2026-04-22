from .schemas import BenchmarkCase, BenchmarkRun, BrainGenerateResult, CapabilityProfile, InferenceTrace, SessionContext

__all__ = [
    "BenchmarkCase",
    "BenchmarkRun",
    "BrainGenerateResult",
    "CapabilityProfile",
    "InferenceTrace",
    "NexusBrain",
    "SessionContext",
]

__version__ = "0.6.0-phase1"


def __getattr__(name: str):
    if name == "NexusBrain":
        from .core import NexusBrain

        return NexusBrain
    raise AttributeError(name)
