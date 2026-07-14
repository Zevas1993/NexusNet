from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


AdmissionState = Literal["admitted", "blocked"]


@dataclass(frozen=True)
class HardwareMemorySnapshot:
    gpu_available_bytes: int
    ram_available_bytes: int
    def __post_init__(self) -> None:
        if self.gpu_available_bytes < 0 or self.ram_available_bytes < 0:
            raise ValueError("available memory values must be non-negative")


@dataclass(frozen=True)
class MoEResidencyRequest:
    model_ref: str
    hardware: HardwareMemorySnapshot
    dense_core_bytes: int
    kv_cache_bytes: int
    runtime_buffer_bytes: int
    gpu_headroom_bytes: int
    ram_headroom_bytes: int
    expert_bytes: int
    expert_count: int

    def __post_init__(self) -> None:
        if not self.model_ref.strip():
            raise ValueError("model_ref is required")
        values = (
            self.dense_core_bytes,
            self.kv_cache_bytes,
            self.runtime_buffer_bytes,
            self.gpu_headroom_bytes,
            self.ram_headroom_bytes,
        )
        if any(value < 0 for value in values):
            raise ValueError("memory requirements must be non-negative")
        if self.expert_bytes <= 0:
            raise ValueError("expert_bytes must be positive")
        if self.expert_count <= 0:
            raise ValueError("expert_count must be positive")


@dataclass(frozen=True)
class MoEResidencyPlan:
    plan_id: str
    model_ref: str
    admission_state: AdmissionState
    blockers: tuple[str, ...]
    gpu_expert_slots: int
    ram_expert_slots: int
    cold_store_required: bool
    expected_bottleneck: str
    dense_working_set_bytes: int
    gpu_available_bytes: int
    ram_available_bytes: int
