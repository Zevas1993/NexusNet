from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


AdmissionState = Literal["admitted", "blocked"]
GPUAccelerationMode = Literal["off", "on", "auto"]


@dataclass(frozen=True)
class HardwareMemorySnapshot:
    gpu_available_bytes: int
    ram_available_bytes: int
    storage_available_bytes: int = 0
    def __post_init__(self) -> None:
        if (
            self.gpu_available_bytes < 0
            or self.ram_available_bytes < 0
            or self.storage_available_bytes < 0
        ):
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
    model_digest: str | None = None

    def __post_init__(self) -> None:
        if not self.model_ref.strip():
            raise ValueError("model_ref is required")
        if self.model_digest is not None and (
            len(self.model_digest) != 64
            or any(character not in "0123456789abcdef" for character in self.model_digest)
        ):
            raise ValueError("model_digest must be a lowercase SHA-256 digest")
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
    model_digest: str | None
    admission_state: AdmissionState
    blockers: tuple[str, ...]
    gpu_expert_slots: int
    ram_expert_slots: int
    cold_store_required: bool
    expected_bottleneck: str
    dense_working_set_bytes: int
    gpu_available_bytes: int
    ram_available_bytes: int
    storage_available_bytes: int
    cold_store_bytes: int
    expert_bytes: int
    expert_count: int
    dense_residency_tier: Literal["gpu", "ram"] | None = None
    gpu_mode: GPUAccelerationMode = "auto"
    gpu_acceleration_enabled: bool = False
    expert_device: str | None = None
    hardware_profile_id: str | None = None

    def __post_init__(self) -> None:
        if self.gpu_mode not in {"off", "on", "auto"}:
            raise ValueError("gpu_mode is invalid")
        if self.dense_residency_tier not in {"gpu", "ram", None}:
            raise ValueError("dense_residency_tier is invalid")
        if self.gpu_mode == "off" and self.gpu_acceleration_enabled:
            raise ValueError("gpu acceleration cannot be enabled when gpu_mode is off")
        if self.gpu_acceleration_enabled and not self.expert_device:
            raise ValueError("enabled gpu acceleration requires expert_device")
        if not self.gpu_acceleration_enabled and self.expert_device is not None:
            raise ValueError("disabled gpu acceleration cannot select expert_device")
