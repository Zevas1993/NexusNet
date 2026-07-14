from __future__ import annotations

import hashlib
import json

from .schemas import MoEResidencyPlan, MoEResidencyRequest


class MoEResidencyPlanner:
    """Conservative GPU/RAM/storage admission for sparse-MoE inference."""

    def plan(self, request: MoEResidencyRequest) -> MoEResidencyPlan:
        dense_working_set = (
            request.dense_core_bytes
            + request.kv_cache_bytes
            + request.runtime_buffer_bytes
            + request.gpu_headroom_bytes
        )
        blockers: list[str] = []
        if request.hardware.gpu_available_bytes <= 0:
            blockers.append("gpu_memory_telemetry_unavailable")
        if request.hardware.ram_available_bytes <= 0:
            blockers.append("ram_memory_telemetry_unavailable")
        if dense_working_set > request.hardware.gpu_available_bytes:
            blockers.append("dense_core_exceeds_gpu_working_set")
        if request.ram_headroom_bytes > request.hardware.ram_available_bytes:
            blockers.append("ram_headroom_exceeds_available_memory")

        gpu_budget = max(0, request.hardware.gpu_available_bytes - dense_working_set)
        ram_budget = max(0, request.hardware.ram_available_bytes - request.ram_headroom_bytes)
        gpu_slots = min(request.expert_count, gpu_budget // request.expert_bytes)
        remaining = max(0, request.expert_count - gpu_slots)
        ram_cache_budget = max(0, ram_budget - request.expert_bytes)
        ram_slots = min(remaining, ram_cache_budget // request.expert_bytes)
        if not blockers and gpu_slots < 1:
            blockers.append("gpu_expert_workspace_unavailable")
        if not blockers and ram_budget < 2 * request.expert_bytes:
            blockers.append("ram_expert_staging_workspace_unavailable")
        cold_store_required = gpu_slots + ram_slots < request.expert_count
        # Storage is the immutable source of truth for every expert, including
        # experts currently cached in RAM or on the accelerator.
        cold_store_bytes = request.expert_count * request.expert_bytes
        if not blockers and cold_store_bytes > request.hardware.storage_available_bytes:
            blockers.append("cold_expert_storage_insufficient")
        if blockers:
            gpu_slots = 0
            ram_slots = 0
            cold_store_required = True

        payload = {
            "model_ref": request.model_ref,
            "dense_working_set": dense_working_set,
            "gpu_available": request.hardware.gpu_available_bytes,
            "ram_available": request.hardware.ram_available_bytes,
            "storage_available": request.hardware.storage_available_bytes,
            "gpu_headroom": request.gpu_headroom_bytes,
            "ram_headroom": request.ram_headroom_bytes,
            "kv_cache": request.kv_cache_bytes,
            "runtime_buffers": request.runtime_buffer_bytes,
            "expert_bytes": request.expert_bytes,
            "expert_count": request.expert_count,
            "gpu_slots": int(gpu_slots),
            "ram_slots": int(ram_slots),
            "blockers": blockers,
            "cold_store_required": cold_store_required,
            "cold_store_bytes": cold_store_bytes,
        }
        plan_id = "moe-plan:" + hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()[:16]
        expected_bottleneck = (
            "blocked"
            if blockers
            else "storage-warmup"
            if cold_store_required
            else "host-transfer"
            if ram_slots
            else "compute"
        )
        return MoEResidencyPlan(
            plan_id=plan_id,
            model_ref=request.model_ref,
            admission_state="blocked" if blockers else "admitted",
            blockers=tuple(blockers),
            gpu_expert_slots=int(gpu_slots),
            ram_expert_slots=int(ram_slots),
            cold_store_required=cold_store_required,
            expected_bottleneck=expected_bottleneck,
            dense_working_set_bytes=dense_working_set,
            gpu_available_bytes=request.hardware.gpu_available_bytes,
            ram_available_bytes=request.hardware.ram_available_bytes,
            storage_available_bytes=request.hardware.storage_available_bytes,
            cold_store_bytes=cold_store_bytes,
            expert_bytes=request.expert_bytes,
            expert_count=request.expert_count,
        )
