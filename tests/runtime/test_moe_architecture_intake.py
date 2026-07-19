from __future__ import annotations

import pytest


GiB = 1024**3
MiB = 1024**2


def _descriptor(**overrides):
    from nexusnet.runtime.moe_residency import MoEArchitectureDescriptor

    payload = {
        "model_ref": "model:architecture-fixture",
        "layer_count": 4,
        "experts_per_layer": 8,
        "experts_per_token": 2,
        "dense_core_bytes": 6 * GiB,
        "expert_bytes": 256 * MiB,
        "kv_cache_bytes_per_token": 64 * 1024,
        "runtime_buffer_bytes": 512 * MiB,
        "storage_bytes": 16 * GiB,
        "model_digest": "a" * 64,
    }
    payload.update(overrides)
    return MoEArchitectureDescriptor(**payload)


def test_architecture_intake_admits_cpu_ram_tiering_and_estimates_cold_storage_ceiling():
    from nexusnet.runtime.moe_residency import ArchitectureTierHardware, MoEArchitectureTierPlanner

    plan = MoEArchitectureTierPlanner().plan(
        _descriptor(),
        ArchitectureTierHardware(
            gpu_available_bytes=0,
            ram_available_bytes=12 * GiB,
            storage_available_bytes=32 * GiB,
            storage_bandwidth_gib_s=4.0,
        ),
        context_tokens=4096,
    )

    assert plan.admission_state == "admitted"
    assert plan.dense_residency_tier == "ram"
    assert plan.total_expert_count == 32
    assert plan.gpu_expert_slots == 0
    assert 0 < plan.ram_expert_slots < plan.total_expert_count
    assert plan.cold_store_required is True
    assert plan.cold_expert_bytes_per_token == 4 * 2 * 256 * MiB
    assert plan.cold_storage_tokens_s_ceiling == pytest.approx(2.0)


def test_architecture_intake_prefers_gpu_dense_residency_and_fails_closed_when_dense_does_not_fit():
    from nexusnet.runtime.moe_residency import (
        ArchitectureTierHardware,
        GPUAccelerationPolicy,
        MoEArchitectureTierPlanner,
    )

    planner = MoEArchitectureTierPlanner()
    gpu_plan = planner.plan(
        _descriptor(),
        ArchitectureTierHardware(
            gpu_available_bytes=10 * GiB,
            ram_available_bytes=16 * GiB,
            storage_available_bytes=32 * GiB,
            storage_bandwidth_gib_s=2.0,
            gpu_runtime_available=True,
            gpu_device_ref="cuda:0",
        ),
        context_tokens=1024,
        gpu_policy=GPUAccelerationPolicy(mode="on"),
    )
    blocked = planner.plan(
        _descriptor(dense_core_bytes=20 * GiB),
        ArchitectureTierHardware(
            gpu_available_bytes=0,
            ram_available_bytes=16 * GiB,
            storage_available_bytes=32 * GiB,
            storage_bandwidth_gib_s=2.0,
        ),
        context_tokens=1024,
    )

    assert gpu_plan.admission_state == "admitted"
    assert gpu_plan.dense_residency_tier == "gpu"
    assert gpu_plan.gpu_expert_slots > 0
    assert blocked.admission_state == "blocked"
    assert "dense_working_set_exceeds_available_memory" in blocked.blockers


def test_architecture_plan_identity_includes_hardware_profile_and_storage_bandwidth():
    from nexusnet.runtime.moe_residency import ArchitectureTierHardware, MoEArchitectureTierPlanner

    planner = MoEArchitectureTierPlanner()
    slow = planner.plan(
        _descriptor(),
        ArchitectureTierHardware(0, 16 * GiB, 32 * GiB, 1.0),
        context_tokens=1024,
    )
    fast = planner.plan(
        _descriptor(),
        ArchitectureTierHardware(0, 16 * GiB, 32 * GiB, 4.0),
        context_tokens=1024,
    )

    assert slow.plan_id != fast.plan_id
    assert slow.hardware_profile_id != fast.hardware_profile_id
    assert slow.cold_storage_tokens_s_ceiling != fast.cold_storage_tokens_s_ceiling


def test_gpu_acceleration_is_a_per_inference_off_on_auto_policy():
    from nexusnet.runtime.moe_residency import (
        ArchitectureTierHardware,
        GPUAccelerationPolicy,
        MoEArchitectureTierPlanner,
    )

    planner = MoEArchitectureTierPlanner()
    hardware = ArchitectureTierHardware(
        10 * GiB,
        16 * GiB,
        32 * GiB,
        4.0,
        gpu_runtime_available=True,
        gpu_device_ref="cuda:0",
    )
    disabled = planner.plan(
        _descriptor(), hardware, context_tokens=1024, gpu_policy=GPUAccelerationPolicy(mode="off")
    )
    forced = planner.plan(
        _descriptor(), hardware, context_tokens=1024, gpu_policy=GPUAccelerationPolicy(mode="on")
    )
    unverified_auto = planner.plan(
        _descriptor(), hardware, context_tokens=1024, gpu_policy=GPUAccelerationPolicy(mode="auto")
    )
    verified_auto = planner.plan(
        _descriptor(),
        hardware,
        context_tokens=1024,
        gpu_policy=GPUAccelerationPolicy(
            mode="auto",
            verified_hardware_profile_id=hardware.hardware_profile_id,
        ),
    )
    unavailable = planner.plan(
        _descriptor(),
        ArchitectureTierHardware(10 * GiB, 16 * GiB, 32 * GiB, 4.0),
        context_tokens=1024,
        gpu_policy=GPUAccelerationPolicy(mode="on"),
    )

    assert disabled.gpu_acceleration_enabled is False
    assert disabled.dense_residency_tier == "ram"
    assert disabled.gpu_expert_slots == 0
    assert forced.gpu_acceleration_enabled is True
    assert forced.dense_residency_tier == "gpu"
    assert forced.expert_device == "cuda:0"
    assert unverified_auto.gpu_acceleration_enabled is False
    assert verified_auto.gpu_acceleration_enabled is True
    assert len({disabled.plan_id, forced.plan_id, unverified_auto.plan_id, verified_auto.plan_id}) == 4
    assert unavailable.admission_state == "blocked"
    assert "gpu_acceleration_requested_but_unavailable" in unavailable.blockers


def test_admitted_architecture_plan_converts_to_same_identity_executable_plan():
    from nexusnet.runtime.moe_residency import (
        ArchitectureTierHardware,
        GPUAccelerationPolicy,
        MoEArchitectureTierPlanner,
    )

    architecture_plan = MoEArchitectureTierPlanner().plan(
        _descriptor(),
        ArchitectureTierHardware(0, 16 * GiB, 32 * GiB, 4.0),
        context_tokens=1024,
        gpu_policy=GPUAccelerationPolicy(mode="off"),
    )
    executable = architecture_plan.to_executable_plan()

    assert executable.plan_id == architecture_plan.plan_id
    assert executable.model_digest == "a" * 64
    assert executable.dense_residency_tier == "ram"
    assert executable.gpu_mode == "off"
    assert executable.gpu_acceleration_enabled is False
    assert executable.expert_device is None

    identityless = MoEArchitectureTierPlanner().plan(
        _descriptor(model_digest=None),
        ArchitectureTierHardware(0, 16 * GiB, 32 * GiB, 4.0),
        context_tokens=1024,
    )
    with pytest.raises(RuntimeError, match="model identity"):
        identityless.to_executable_plan()


def test_architecture_intake_rejects_ambiguous_or_invalid_moe_layouts():
    from nexusnet.runtime.moe_residency import MoEArchitectureDescriptor

    with pytest.raises(ValueError, match="experts_per_token"):
        _descriptor(experts_per_token=9)
    with pytest.raises(ValueError, match="model_ref"):
        MoEArchitectureDescriptor(
            model_ref="private model path",
            layer_count=1,
            experts_per_layer=2,
            experts_per_token=1,
            dense_core_bytes=1,
            expert_bytes=1,
            kv_cache_bytes_per_token=1,
            runtime_buffer_bytes=1,
            storage_bytes=4,
        )


def test_runtime_telemetry_aggregates_existing_residency_evidence_without_content():
    from nexusnet.runtime.moe_residency import (
        ArchitectureTierHardware,
        MoEArchitectureTierPlanner,
        MoEResidencyTelemetry,
    )

    plan = MoEArchitectureTierPlanner().plan(
        _descriptor(),
        ArchitectureTierHardware(0, 16 * GiB, 32 * GiB, 4.0),
        context_tokens=1024,
    )
    telemetry = MoEResidencyTelemetry.from_runtime_evidence(
        plan,
        {
            "plan_ref": plan.plan_id,
            "manifest_refs": ["manifest:layer-0", "manifest:layer-1"],
            "runtime_state": "tiered-warm",
            "layers": [
                {"tier_metrics": {"hot_hits": 5, "ram_hits": 1, "storage_misses": 2, "bytes_read": 2048}},
                {"tier_metrics": {"hot_hits": 1, "ram_hits": 2, "storage_misses": 1, "bytes_read": 1024}},
            ],
        },
        generated_tokens=6,
        measurements_ms=[100, 100, 100],
        execution_plan_id="plan::portable-reference",
        model_fingerprint_id="model-fingerprint::fixture",
    )

    assert telemetry.cache_hit_rate == pytest.approx(0.75)
    assert telemetry.bytes_per_token == pytest.approx(512.0)
    assert telemetry.throughput_tokens_s == pytest.approx(20.0)
    assert telemetry.cold_storage_tokens_s_ceiling == pytest.approx(plan.cold_storage_tokens_s_ceiling)
    assert telemetry.architecture_plan_id == plan.plan_id
    assert telemetry.execution_plan_id == "plan::portable-reference"
    assert telemetry.model_digest == "a" * 64
    assert telemetry.hardware_profile_id == plan.hardware_profile_id
    assert telemetry.gpu_mode == "auto"
    assert not hasattr(telemetry, "for_plan")
    assert "prompt" not in str(telemetry.as_dict()).lower()


def test_runtime_telemetry_rejects_cross_plan_runtime_evidence():
    from nexusnet.runtime.moe_residency import (
        ArchitectureTierHardware,
        MoEArchitectureTierPlanner,
        MoEResidencyTelemetry,
    )

    plan = MoEArchitectureTierPlanner().plan(
        _descriptor(),
        ArchitectureTierHardware(0, 16 * GiB, 32 * GiB, 4.0),
        context_tokens=1024,
    )

    with pytest.raises(ValueError, match="plan_ref"):
        MoEResidencyTelemetry.from_runtime_evidence(
            plan,
            {
                "plan_ref": "moe-architecture-plan:other",
                "manifest_refs": ["manifest:layer-0"],
                "runtime_state": "tiered-warm",
                "layers": [{"tier_metrics": {}}],
            },
            generated_tokens=1,
            measurements_ms=[1.0],
            execution_plan_id="plan::portable-reference",
            model_fingerprint_id="model-fingerprint::fixture",
        )
