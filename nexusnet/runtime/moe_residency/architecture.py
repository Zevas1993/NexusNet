from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from statistics import median
from typing import Literal, Mapping, Sequence

from .schemas import MoEResidencyPlan


_MODEL_REF = re.compile(r"^[a-z0-9][a-z0-9_.:-]{0,255}$")
_RUNTIME_STATES = {"tiered-warming", "tiered-cold", "tiered-warm", "tiered-degraded"}
_METRICS = {"hot_hits", "ram_hits", "storage_misses", "bytes_read"}


@dataclass(frozen=True)
class MoEArchitectureDescriptor:
    """Explicit, metadata-only topology needed to plan tiered MoE residency."""

    model_ref: str
    layer_count: int
    experts_per_layer: int
    experts_per_token: int
    dense_core_bytes: int
    expert_bytes: int
    kv_cache_bytes_per_token: int
    runtime_buffer_bytes: int
    storage_bytes: int
    model_digest: str | None = None

    def __post_init__(self) -> None:
        if not _MODEL_REF.fullmatch(self.model_ref):
            raise ValueError("model_ref must be a sanitized stable reference")
        if self.model_digest is not None and not re.fullmatch(r"[0-9a-f]{64}", self.model_digest):
            raise ValueError("model_digest must be a lowercase SHA-256 digest")
        if self.layer_count <= 0 or self.experts_per_layer <= 0:
            raise ValueError("layer_count and experts_per_layer must be positive")
        if not 0 < self.experts_per_token <= self.experts_per_layer:
            raise ValueError("experts_per_token must be positive and no greater than experts_per_layer")
        values = (
            self.dense_core_bytes,
            self.expert_bytes,
            self.kv_cache_bytes_per_token,
            self.runtime_buffer_bytes,
            self.storage_bytes,
        )
        if any(value <= 0 for value in values):
            raise ValueError("architecture byte values must be positive")

    @property
    def total_expert_count(self) -> int:
        return self.layer_count * self.experts_per_layer

    @property
    def cold_expert_bytes_per_token(self) -> int:
        return self.layer_count * self.experts_per_token * self.expert_bytes

    @property
    def total_expert_bytes(self) -> int:
        return self.total_expert_count * self.expert_bytes


@dataclass(frozen=True)
class ArchitectureTierHardware:
    gpu_available_bytes: int
    ram_available_bytes: int
    storage_available_bytes: int
    storage_bandwidth_gib_s: float | None
    gpu_headroom_bytes: int = 0
    ram_headroom_bytes: int = 0
    gpu_runtime_available: bool = False
    gpu_device_ref: str | None = None

    def __post_init__(self) -> None:
        values = (
            self.gpu_available_bytes,
            self.ram_available_bytes,
            self.storage_available_bytes,
            self.gpu_headroom_bytes,
            self.ram_headroom_bytes,
        )
        if any(value < 0 for value in values):
            raise ValueError("hardware byte values must be non-negative")
        if self.storage_bandwidth_gib_s is not None and (
            not math.isfinite(self.storage_bandwidth_gib_s) or self.storage_bandwidth_gib_s <= 0
        ):
            raise ValueError("storage_bandwidth_gib_s must be finite and positive when supplied")
        if self.gpu_device_ref is not None and not _MODEL_REF.fullmatch(self.gpu_device_ref):
            raise ValueError("gpu_device_ref must be a sanitized stable reference")
        if self.gpu_runtime_available and (
            self.gpu_available_bytes <= 0 or self.gpu_device_ref is None
        ):
            raise ValueError("available gpu runtime requires memory telemetry and a device reference")

    @property
    def hardware_profile_id(self) -> str:
        payload = {
            "gpu_available_bytes": self.gpu_available_bytes,
            "ram_available_bytes": self.ram_available_bytes,
            "storage_available_bytes": self.storage_available_bytes,
            "storage_bandwidth_gib_s": self.storage_bandwidth_gib_s,
            "gpu_headroom_bytes": self.gpu_headroom_bytes,
            "ram_headroom_bytes": self.ram_headroom_bytes,
            "gpu_runtime_available": self.gpu_runtime_available,
            "gpu_device_ref": self.gpu_device_ref,
        }
        return "hardware-profile:" + hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()[:20]


@dataclass(frozen=True)
class GPUAccelerationPolicy:
    mode: Literal["off", "on", "auto"] = "auto"
    verified_hardware_profile_id: str | None = None

    def __post_init__(self) -> None:
        if self.mode not in {"off", "on", "auto"}:
            raise ValueError("gpu acceleration mode is invalid")
        if self.verified_hardware_profile_id is not None and not _MODEL_REF.fullmatch(
            self.verified_hardware_profile_id
        ):
            raise ValueError("verified_hardware_profile_id must be a sanitized stable reference")
        if self.mode != "auto" and self.verified_hardware_profile_id is not None:
            raise ValueError("only auto mode accepts a verified hardware profile")


@dataclass(frozen=True)
class MoEArchitectureTierPlan:
    plan_id: str
    model_ref: str
    model_digest: str | None
    admission_state: str
    blockers: tuple[str, ...]
    dense_residency_tier: str | None
    total_expert_count: int
    gpu_expert_slots: int
    ram_expert_slots: int
    cold_store_required: bool
    dense_working_set_bytes: int
    cold_expert_bytes_per_token: int
    cold_storage_tokens_s_ceiling: float | None
    expert_bytes: int
    model_storage_bytes: int
    gpu_available_bytes: int
    ram_available_bytes: int
    storage_available_bytes: int
    hardware_profile_id: str
    gpu_mode: Literal["off", "on", "auto"]
    gpu_acceleration_enabled: bool
    expert_device: str | None

    def __post_init__(self) -> None:
        if self.admission_state not in {"admitted", "blocked"}:
            raise ValueError("admission_state is invalid")
        if self.dense_residency_tier not in {"gpu", "ram", None}:
            raise ValueError("dense_residency_tier is invalid")
        if self.gpu_mode not in {"off", "on", "auto"}:
            raise ValueError("gpu_mode is invalid")
        if self.gpu_acceleration_enabled != (self.expert_device is not None):
            raise ValueError("gpu acceleration decision and expert_device disagree")

    def to_executable_plan(self) -> MoEResidencyPlan:
        if self.admission_state != "admitted":
            raise RuntimeError(f"architecture plan is blocked: {', '.join(self.blockers)}")
        if self.model_digest is None:
            raise RuntimeError("architecture plan is not bound to a model identity")
        expected_bottleneck = (
            "storage-warmup"
            if self.cold_store_required
            else "host-transfer"
            if self.gpu_acceleration_enabled and self.dense_residency_tier == "ram"
            else "compute"
        )
        return MoEResidencyPlan(
            plan_id=self.plan_id,
            model_ref=self.model_ref,
            model_digest=self.model_digest,
            admission_state=self.admission_state,
            blockers=self.blockers,
            gpu_expert_slots=self.gpu_expert_slots,
            ram_expert_slots=self.ram_expert_slots,
            cold_store_required=self.cold_store_required,
            expected_bottleneck=expected_bottleneck,
            dense_working_set_bytes=self.dense_working_set_bytes,
            gpu_available_bytes=self.gpu_available_bytes,
            ram_available_bytes=self.ram_available_bytes,
            storage_available_bytes=self.storage_available_bytes,
            cold_store_bytes=self.model_storage_bytes,
            expert_bytes=self.expert_bytes,
            expert_count=self.total_expert_count,
            dense_residency_tier=self.dense_residency_tier,
            gpu_mode=self.gpu_mode,
            gpu_acceleration_enabled=self.gpu_acceleration_enabled,
            expert_device=self.expert_device,
            hardware_profile_id=self.hardware_profile_id,
        )


class MoEArchitectureTierPlanner:
    """Build a non-loading placement plan from model topology and hardware facts."""

    def plan(
        self,
        descriptor: MoEArchitectureDescriptor,
        hardware: ArchitectureTierHardware,
        *,
        context_tokens: int,
        gpu_policy: GPUAccelerationPolicy | None = None,
    ) -> MoEArchitectureTierPlan:
        if context_tokens < 0:
            raise ValueError("context_tokens must be non-negative")
        dense_working_set = (
            descriptor.dense_core_bytes
            + descriptor.runtime_buffer_bytes
            + descriptor.kv_cache_bytes_per_token * context_tokens
        )
        policy = gpu_policy or GPUAccelerationPolicy()
        hardware_profile_id = hardware.hardware_profile_id
        gpu_runtime_ready = (
            hardware.gpu_runtime_available
            and hardware.gpu_available_bytes > 0
            and hardware.gpu_device_ref is not None
        )
        if policy.mode == "off":
            gpu_enabled = False
        elif policy.mode == "on":
            gpu_enabled = gpu_runtime_ready
        else:
            gpu_enabled = (
                gpu_runtime_ready
                and policy.verified_hardware_profile_id == hardware_profile_id
            )
        blockers: list[str] = []
        if policy.mode == "on" and not gpu_runtime_ready:
            blockers.append("gpu_acceleration_requested_but_unavailable")
        if descriptor.storage_bytes > hardware.storage_available_bytes:
            blockers.append("model_storage_exceeds_available_storage")

        gpu_budget = max(0, hardware.gpu_available_bytes - hardware.gpu_headroom_bytes)
        gpu_dense = gpu_enabled and gpu_budget >= dense_working_set
        ram_dense = hardware.ram_available_bytes - hardware.ram_headroom_bytes >= dense_working_set
        if gpu_dense:
            dense_tier = "gpu"
            gpu_expert_slots = min(
                descriptor.total_expert_count,
                max(0, (gpu_budget - dense_working_set) // descriptor.expert_bytes),
            )
            ram_expert_budget = max(0, hardware.ram_available_bytes - hardware.ram_headroom_bytes)
        elif ram_dense:
            dense_tier = "ram"
            gpu_expert_slots = min(
                descriptor.total_expert_count,
                gpu_budget // descriptor.expert_bytes if gpu_enabled else 0,
            )
            ram_expert_budget = max(0, hardware.ram_available_bytes - hardware.ram_headroom_bytes - dense_working_set)
        else:
            dense_tier = None
            gpu_expert_slots = 0
            ram_expert_budget = 0
            blockers.append("dense_working_set_exceeds_available_memory")

        remaining = max(0, descriptor.total_expert_count - gpu_expert_slots)
        ram_expert_slots = min(remaining, ram_expert_budget // descriptor.expert_bytes)
        cold_required = gpu_expert_slots + ram_expert_slots < descriptor.total_expert_count
        if cold_required and hardware.storage_bandwidth_gib_s is None:
            blockers.append("storage_bandwidth_telemetry_unavailable")
        if blockers:
            dense_tier = None
            gpu_expert_slots = 0
            ram_expert_slots = 0
            cold_required = True

        ceiling = None
        if hardware.storage_bandwidth_gib_s is not None:
            ceiling = (hardware.storage_bandwidth_gib_s * 1024**3) / descriptor.cold_expert_bytes_per_token
        resolved_gpu_enabled = gpu_enabled and not blockers
        resolved_expert_device = hardware.gpu_device_ref if resolved_gpu_enabled else None
        payload = {
            "model_ref": descriptor.model_ref,
            "model_digest": descriptor.model_digest,
            "layers": descriptor.layer_count,
            "experts_per_layer": descriptor.experts_per_layer,
            "experts_per_token": descriptor.experts_per_token,
            "dense_working_set": dense_working_set,
            "gpu_slots": gpu_expert_slots,
            "ram_slots": ram_expert_slots,
            "blockers": blockers,
            "context_tokens": context_tokens,
            "hardware_profile_id": hardware_profile_id,
            "gpu_mode": policy.mode,
            "gpu_acceleration_enabled": resolved_gpu_enabled,
            "expert_device": resolved_expert_device,
            "verified_hardware_profile_id": policy.verified_hardware_profile_id,
        }
        plan_id = "moe-architecture-plan:" + hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()[:20]
        return MoEArchitectureTierPlan(
            plan_id=plan_id,
            model_ref=descriptor.model_ref,
            model_digest=descriptor.model_digest,
            admission_state="blocked" if blockers else "admitted",
            blockers=tuple(blockers),
            dense_residency_tier=dense_tier,
            total_expert_count=descriptor.total_expert_count,
            gpu_expert_slots=int(gpu_expert_slots),
            ram_expert_slots=int(ram_expert_slots),
            cold_store_required=cold_required,
            dense_working_set_bytes=dense_working_set,
            cold_expert_bytes_per_token=descriptor.cold_expert_bytes_per_token,
            cold_storage_tokens_s_ceiling=ceiling,
            expert_bytes=descriptor.expert_bytes,
            model_storage_bytes=descriptor.storage_bytes,
            gpu_available_bytes=hardware.gpu_available_bytes,
            ram_available_bytes=hardware.ram_available_bytes,
            storage_available_bytes=hardware.storage_available_bytes,
            hardware_profile_id=hardware_profile_id,
            gpu_mode=policy.mode,
            gpu_acceleration_enabled=resolved_gpu_enabled,
            expert_device=resolved_expert_device,
        )


@dataclass(frozen=True)
class MoEResidencyTelemetry:
    architecture_plan_id: str
    execution_plan_id: str
    model_ref: str
    model_digest: str
    model_fingerprint_id: str
    hardware_profile_id: str
    gpu_mode: Literal["off", "on", "auto"]
    gpu_acceleration_enabled: bool
    runtime_state: str
    sample_count: int
    measurements_ms: tuple[float, ...]
    generated_tokens: int
    cache_hit_rate: float
    bytes_per_token: float
    throughput_tokens_s: float
    bytes_read: int
    cold_storage_tokens_s_ceiling: float | None
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        references = (
            self.architecture_plan_id,
            self.execution_plan_id,
            self.model_ref,
            self.model_fingerprint_id,
            self.hardware_profile_id,
        )
        if any(not _MODEL_REF.fullmatch(reference) for reference in references):
            raise ValueError("telemetry identities must be sanitized stable references")
        if not re.fullmatch(r"[0-9a-f]{64}", self.model_digest):
            raise ValueError("model_digest must be a lowercase SHA-256 digest")
        if self.gpu_mode not in {"off", "on", "auto"}:
            raise ValueError("gpu_mode is invalid")
        if self.gpu_mode == "off" and self.gpu_acceleration_enabled:
            raise ValueError("gpu acceleration cannot be enabled when gpu_mode is off")
        if self.runtime_state not in _RUNTIME_STATES:
            raise ValueError("runtime_state is invalid")
        if self.sample_count != len(self.measurements_ms) or self.sample_count <= 0:
            raise ValueError("measurement count must match non-empty measurements")
        if self.generated_tokens <= 0 or self.bytes_read < 0:
            raise ValueError("generated_tokens must be positive and bytes_read non-negative")
        if any(not math.isfinite(value) or value <= 0 for value in self.measurements_ms):
            raise ValueError("measurements must be finite and positive")
        if not 0 <= self.cache_hit_rate <= 1 or self.bytes_per_token < 0 or self.throughput_tokens_s < 0:
            raise ValueError("telemetry ratios must be non-negative and bounded")

    @classmethod
    def from_runtime_evidence(
        cls,
        plan: MoEArchitectureTierPlan,
        runtime_evidence: Mapping[str, object],
        *,
        generated_tokens: int,
        measurements_ms: Sequence[float],
        execution_plan_id: str,
        model_fingerprint_id: str,
    ) -> "MoEResidencyTelemetry":
        if runtime_evidence.get("plan_ref") != plan.plan_id:
            raise ValueError("runtime evidence plan_ref does not match tier plan")
        if plan.model_digest is None:
            raise ValueError("tier plan must be bound to a model identity")
        manifest_refs = runtime_evidence.get("manifest_refs")
        if (
            not isinstance(manifest_refs, list)
            or not manifest_refs
            or any(not isinstance(item, str) or not _MODEL_REF.fullmatch(item) for item in manifest_refs)
        ):
            raise ValueError("runtime evidence requires sanitized non-empty manifest_refs")
        runtime_state = runtime_evidence.get("runtime_state")
        if not isinstance(runtime_state, str) or runtime_state not in _RUNTIME_STATES:
            raise ValueError("runtime evidence has an invalid runtime_state")
        layers = runtime_evidence.get("layers")
        if not isinstance(layers, list) or not layers:
            raise ValueError("runtime evidence requires non-empty layer metrics")
        aggregate = {key: 0 for key in _METRICS}
        for layer in layers:
            if not isinstance(layer, Mapping):
                raise ValueError("runtime evidence layer must be a mapping")
            metrics = layer.get("tier_metrics", {})
            if not isinstance(metrics, Mapping):
                raise ValueError("runtime evidence tier_metrics must be a mapping")
            for key in _METRICS:
                value = metrics.get(key, 0)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                    raise ValueError("runtime evidence metrics must be non-negative numbers")
                aggregate[key] += int(value)
        measurements = tuple(float(value) for value in measurements_ms)
        total_accesses = aggregate["hot_hits"] + aggregate["ram_hits"] + aggregate["storage_misses"]
        cache_hit_rate = (aggregate["hot_hits"] + aggregate["ram_hits"]) / total_accesses if total_accesses else 0.0
        total_duration_ms = sum(measurements)
        reason_codes = [f"residency-state:{runtime_state}"]
        if aggregate["storage_misses"]:
            reason_codes.append("storage-miss-observed")
        return cls(
            architecture_plan_id=plan.plan_id,
            execution_plan_id=execution_plan_id,
            model_ref=plan.model_ref,
            model_digest=plan.model_digest,
            model_fingerprint_id=model_fingerprint_id,
            hardware_profile_id=plan.hardware_profile_id,
            gpu_mode=plan.gpu_mode,
            gpu_acceleration_enabled=plan.gpu_acceleration_enabled,
            runtime_state=runtime_state,
            sample_count=len(measurements),
            measurements_ms=measurements,
            generated_tokens=generated_tokens,
            cache_hit_rate=cache_hit_rate,
            bytes_per_token=aggregate["bytes_read"] / generated_tokens,
            throughput_tokens_s=generated_tokens * 1000 / total_duration_ms,
            bytes_read=aggregate["bytes_read"],
            cold_storage_tokens_s_ceiling=plan.cold_storage_tokens_s_ceiling,
            reason_codes=tuple(reason_codes),
        )

    @property
    def plan_id(self) -> str:
        return self.execution_plan_id

    @property
    def cold_latency_ms(self) -> float:
        return self.measurements_ms[0]

    @property
    def warm_latency_ms(self) -> float:
        return float(median(self.measurements_ms[1:] or self.measurements_ms))

    def as_dict(self) -> dict[str, object]:
        return {
            "architecture_plan_id": self.architecture_plan_id,
            "execution_plan_id": self.execution_plan_id,
            "model_ref": self.model_ref,
            "model_digest": self.model_digest,
            "model_fingerprint_id": self.model_fingerprint_id,
            "hardware_profile_id": self.hardware_profile_id,
            "gpu_mode": self.gpu_mode,
            "gpu_acceleration_enabled": self.gpu_acceleration_enabled,
            "runtime_state": self.runtime_state,
            "sample_count": self.sample_count,
            "cache_hit_rate": self.cache_hit_rate,
            "bytes_per_token": self.bytes_per_token,
            "throughput_tokens_s": self.throughput_tokens_s,
            "bytes_read": self.bytes_read,
            "cold_storage_tokens_s_ceiling": self.cold_storage_tokens_s_ceiling,
            "reason_codes": list(self.reason_codes),
            "privacy_boundary": "numeric-runtime-metrics-and-sanitized-references-only",
        }
