from __future__ import annotations

import json
import subprocess
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from nexusnet.runtime.evolutionary_inference import (
    BoundedHostCalibrator,
    CalibrationLimits,
    CandidateFeasibilityEvaluator,
    EvolutionaryInferenceFoundation,
    HardwareCapabilityDiscoverer,
    InferencePrimitiveRegistry,
    ModelExecutionFingerprint,
    fingerprint_from_metadata,
    synthetic_model_fingerprint,
)


def test_synthetic_model_fingerprint_is_strict_deterministic_and_sanitized():
    first = synthetic_model_fingerprint()
    second = synthetic_model_fingerprint()

    assert first == second
    assert first.source_kind == "trusted-synthetic"
    assert first.fingerprint_id.startswith("model-fingerprint::")
    assert first.architecture_family == "synthetic-transformer"
    assert first.parameter_count > 0
    assert first.tensor_bytes > 0
    serialized = json.dumps(first.model_dump(mode="json"))
    assert "model_path" not in serialized
    assert "prompt" not in serialized
    assert "content" not in serialized

    with pytest.raises(ValidationError):
        ModelExecutionFingerprint.model_validate(
            {
                **first.model_dump(mode="json"),
                "raw_model_path": "C:/private/models/model.gguf",
            }
        )


def test_model_fingerprint_normalizes_execution_metadata_without_retaining_source_fields():
    fingerprint = fingerprint_from_metadata(
        {
            "architecture_family": "MixtralForCausalLM",
            "parameter_count": 46_700_000_000,
            "tensor_bytes": 26_000_000_000,
            "quantization": "Q4_K_M",
            "context_length": 32_768,
            "layer_count": 32,
            "expert_count": 8,
            "experts_per_token": 2,
            "modalities": ["text"],
            "model_path": "F:/models/private/mixtral.gguf",
            "prompt": "must never persist",
        }
    )

    assert fingerprint.source_kind == "metadata"
    assert fingerprint.architecture_family == "mixtralforcausallm"
    assert fingerprint.expert_count == 8
    assert fingerprint.experts_per_token == 2
    serialized = json.dumps(fingerprint.model_dump(mode="json"))
    assert "private" not in serialized
    assert "must never persist" not in serialized


def test_hardware_discovery_builds_portable_graph_and_sanitized_cuda_observation():
    commands: list[tuple[str, ...]] = []

    def runner(command: list[str], timeout: float):
        commands.append(tuple(command))
        if command[0] == "nvidia-smi":
            return subprocess.CompletedProcess(command, 0, "NVIDIA RTX Test, 24576, 550.1\n", "")
        raise FileNotFoundError(command[0])

    discoverer = HardwareCapabilityDiscoverer(
        command_runner=runner,
        system_name="Windows",
        machine="AMD64",
        processor_name="Test CPU",
        logical_cpu_count=16,
        total_memory_bytes=64 * 1024**3,
        disk_usage_reader=lambda _: SimpleNamespace(total=2 * 1024**4, free=1024**4),
        storage_root="F:/",
    )

    graph = discoverer.discover()

    assert {node.kind for node in graph.nodes} >= {"cpu", "system-ram", "storage", "gpu"}
    gpu = next(node for node in graph.nodes if node.kind == "gpu")
    assert gpu.backend == "cuda"
    assert gpu.memory_bytes == 24_576 * 1024**2
    assert any(item.backend == "cuda" and item.available for item in graph.adapters)
    assert any(item.backend == "rocm" and not item.available for item in graph.adapters)
    assert any(item.backend == "metal" and item.reason_code == "unsupported-platform" for item in graph.adapters)
    assert any(command[0] == "nvidia-smi" for command in commands)
    serialized = json.dumps(graph.model_dump(mode="json"))
    assert "ChrisBoyd" not in serialized
    assert "hostname" not in serialized.lower()
    assert len(graph.host_fingerprint) == 32


def test_optional_accelerator_adapters_degrade_without_breaking_portable_discovery():
    def missing_runner(command: list[str], timeout: float):
        raise FileNotFoundError(command[0])

    graph = HardwareCapabilityDiscoverer(
        command_runner=missing_runner,
        system_name="Linux",
        machine="aarch64",
        processor_name="Portable CPU",
        logical_cpu_count=8,
        total_memory_bytes=16 * 1024**3,
        disk_usage_reader=lambda _: SimpleNamespace(total=512 * 1024**3, free=256 * 1024**3),
        storage_root="/",
    ).discover()

    assert {node.kind for node in graph.nodes} == {"cpu", "system-ram", "storage"}
    assert {adapter.reason_code for adapter in graph.adapters} >= {"tool-not-found", "unsupported-platform"}


def test_bounded_host_calibration_emits_finite_cpu_and_memory_metrics_only():
    limits = CalibrationLimits(memory_bytes=1024 * 1024, memory_rounds=2, compute_iterations=5000)
    metrics = BoundedHostCalibrator(limits=limits).calibrate()

    assert {metric.metric_id for metric in metrics} == {"memory-copy-gib-s", "cpu-scalar-mops"}
    assert all(metric.value > 0 for metric in metrics)
    assert all(metric.duration_ms > 0 for metric in metrics)
    assert all(metric.sample_count > 0 for metric in metrics)
    assert {target for metric in metrics for target in metric.target_node_ids} <= {"cpu:0", "ram:0"}
    assert limits.memory_bytes == 1024 * 1024
    assert limits.memory_rounds == 2

    with pytest.raises(ValidationError):
        CalibrationLimits(memory_bytes=17 * 1024 * 1024)


def test_default_primitive_registry_assimilates_portable_and_existing_moe_capabilities():
    registry = InferencePrimitiveRegistry.default()

    portable = registry.get("portable.cpu-reference")
    moe = registry.get("moe.selective-residency")

    assert portable.implementation_state == "available"
    assert portable.compatible_model_families == ["all"]
    assert portable.evidence_state == "portable-reference"
    assert moe.implementation_state == "available"
    assert moe.adapter_path == "nexusnet.runtime.moe_residency"
    assert moe.compatible_model_families == ["moe"]
    assert "tiered-expert-residency" in moe.effects
    assert registry.list_ids() == [
        "moe.selective-residency",
        "portable.cpu-reference",
        "transfer.accelerator-resident",
        "transfer.double-buffered",
        "transfer.pageable",
        "transfer.storage-staging",
        "transfer.unified-memory",
    ]


def test_inference_method_record_supports_whole_engine_and_primitive_assimilation():
    from nexusnet.runtime.evolutionary_inference import InferenceMethodRecord

    method = InferenceMethodRecord(
        method_id="runtime::example",
        version="1.2.3",
        source_kind="external-engine",
        source_digest="sha256:source",
        artifact_digest="sha256:artifact",
        rights={
            "inference": "allowed",
            "evaluation": "allowed",
            "derivative": "review-required",
            "redistribution": "blocked",
        },
        claimed_capabilities=["paged-kv", "continuous-batching"],
        reproduced_capabilities=["paged-kv"],
        supported_model_families=["transformer"],
        supported_operator_families=["attention", "gemm"],
        supported_formats=["safetensors"],
        supported_precisions=["fp16", "int8"],
        supported_hardware=["cuda"],
        tunable_controls=["context_tokens", "runtime_batch_tokens"],
        known_conflicts=[],
        fallback_method_id="runtime::portable-reference",
        maturity="reproduced",
        assimilation_paths=["whole-engine", "primitive"],
    )

    assert method.assimilation_paths == ["whole-engine", "primitive"]
    assert method.reproduced_capabilities == ["paged-kv"]
    assert method.rights["redistribution"] == "blocked"


def test_execution_fit_receipt_accounts_for_moe_kv_and_unsupported_controls():
    from nexusnet.runtime.evolutionary_inference import (
        ExecutionFitEstimator,
        ExecutionFitRequest,
        HardwareNode,
        RuntimeCapabilityProfile,
        RuntimeModelMetadata,
        fingerprint_from_runtime_metadata,
    )

    graph = HardwareCapabilityDiscoverer(
        command_runner=lambda command, timeout: (_ for _ in ()).throw(FileNotFoundError(command[0])),
        system_name="Linux",
        machine="x86_64",
        processor_name="CPU",
        logical_cpu_count=16,
        total_memory_bytes=64 * 1024**3,
        disk_usage_reader=lambda _: SimpleNamespace(total=2 * 1024**4, free=1024**4),
        storage_root="/",
    ).discover()
    graph = graph.model_copy(
        update={
            "nodes": graph.nodes
            + [
                HardwareNode(
                    node_id="gpu:cuda:0",
                    kind="gpu",
                    name="constrained-gpu",
                    backend="cuda",
                    memory_bytes=8 * 1024**3,
                    capabilities=["cuda", "device-memory"],
                )
            ]
        }
    )
    fingerprint = fingerprint_from_runtime_metadata(
        RuntimeModelMetadata(
            architecture_family="sparse-transformer",
            parameter_count=46_700_000_000,
            tensor_bytes=26 * 1024**3,
            quantization="q4_k_m",
            context_length=32768,
            layer_count=32,
            expert_count=8,
            experts_per_token=2,
            operator_families=["attention", "grouped-gemm"],
            tensor_groups=[
                {"group_id": "dense", "bytes": 6 * 1024**3, "dtype": "int4", "layout": "row-major"},
                {"group_id": "experts", "bytes": 20 * 1024**3, "dtype": "int4", "layout": "expert-major"},
            ],
            state_and_kv_contract={"kind": "paged-kv", "bytes_per_token": 131072},
            sparsity_and_router_contract={"kind": "top-k", "k": 2},
            rights_and_artifact_refs=["artifact::trusted-model-metadata"],
        )
    )
    capabilities = RuntimeCapabilityProfile(
        runtime_name="runtime::example",
        runtime_version="1.2.3",
        implementation_digest="sha256:runtime",
        capability_state="verified",
        supported_controls=["context_tokens", "runtime_batch_tokens", "cpu_moe"],
        observable_controls=["context_tokens", "runtime_batch_tokens", "cpu_moe"],
    )
    request = ExecutionFitRequest(
        request_id="fit-request::one",
        plan_id="plan::mixed-moe",
        model_fingerprint=fingerprint,
        hardware=graph,
        runtime_capabilities=capabilities,
        requested_context_tokens=8192,
        max_new_tokens=256,
        batch_size=1,
        concurrent_requests=1,
        runtime_buffer_bytes=512 * 1024**2,
        requested_controls={
            "context_tokens": 8192,
            "runtime_batch_tokens": 256,
            "cpu_moe": True,
            "cache_type_k": "q8_0",
        },
        required_controls=["context_tokens", "cpu_moe"],
    )

    receipt = ExecutionFitEstimator().evaluate(request)

    assert receipt.decision == "degraded"
    assert receipt.dense_weight_bytes == 6 * 1024**3
    assert receipt.expert_weight_bytes == 20 * 1024**3
    assert receipt.active_expert_bytes == 5 * 1024**3
    assert receipt.kv_cache_bytes == 8192 * 131072
    assert receipt.placement["dense"] == "gpu"
    assert receipt.placement["experts"] == "ram"
    assert {binding.control: binding.status for binding in receipt.control_bindings} == {
        "cache_type_k": "unsupported",
        "context_tokens": "applied",
        "cpu_moe": "applied",
        "runtime_batch_tokens": "applied",
    }
    assert "optional-control-unsupported" in receipt.reason_codes
    assert "required-control-unsupported" not in receipt.reason_codes

    missing_required = ExecutionFitEstimator().evaluate(
        request.model_copy(update={"required_controls": ["context_tokens", "threads"]})
    )
    assert missing_required.decision == "rejected"
    assert {binding.control: binding.status for binding in missing_required.control_bindings}["threads"] == "rejected"
    assert "required-control-missing" in missing_required.reason_codes

    multi_gpu_graph = graph.model_copy(
        update={
            "nodes": graph.nodes
            + [
                HardwareNode(
                    node_id="gpu:cuda:1",
                    kind="gpu",
                    name="second-constrained-gpu",
                    backend="cuda",
                    memory_bytes=8 * 1024**3,
                    capabilities=["cuda", "device-memory"],
                )
            ]
        }
    )
    compact_fingerprint = fingerprint_from_runtime_metadata(
        RuntimeModelMetadata(
            architecture_family="dense-transformer",
            parameter_count=20_000_000_000,
            tensor_bytes=12 * 1024**3,
            quantization="q4_k_m",
            context_length=32768,
            layer_count=32,
            operator_families=["attention", "gemm"],
            tensor_groups=[
                {"group_id": "dense", "bytes": 12 * 1024**3, "dtype": "int4", "layout": "row-major"}
            ],
            state_and_kv_contract={"kind": "paged-kv", "bytes_per_token": 131072},
            rights_and_artifact_refs=["artifact::trusted-model-metadata"],
        )
    )
    multi_gpu_capabilities = capabilities.model_copy(
        update={
            "supported_controls": capabilities.supported_controls + ["tensor_split"],
            "observable_controls": capabilities.observable_controls + ["tensor_split"],
        }
    )
    conservative_receipt = ExecutionFitEstimator().evaluate(
        request.model_copy(
            update={
                "model_fingerprint": compact_fingerprint,
                "hardware": multi_gpu_graph,
                "runtime_capabilities": multi_gpu_capabilities,
                "requested_controls": {"context_tokens": 8192},
                "required_controls": ["context_tokens"],
            }
        )
    )
    split_receipt = ExecutionFitEstimator().evaluate(
        request.model_copy(
            update={
                "model_fingerprint": compact_fingerprint,
                "hardware": multi_gpu_graph,
                "runtime_capabilities": multi_gpu_capabilities,
                "requested_controls": {"context_tokens": 8192, "tensor_split": "0.5,0.5"},
                "required_controls": ["context_tokens", "tensor_split"],
            }
        )
    )

    assert conservative_receipt.placement["dense"] == "ram"
    assert split_receipt.placement["dense"] == "gpu"

    constrained_nodes = [
        node.model_copy(update={"memory_bytes": 15 * 1024**3})
        if node.kind == "system-ram"
        else node
        for node in multi_gpu_graph.nodes
        if node.kind != "gpu"
    ]
    constrained_receipt = ExecutionFitEstimator().evaluate(
        request.model_copy(
            update={
                "model_fingerprint": compact_fingerprint,
                "hardware": multi_gpu_graph.model_copy(update={"nodes": constrained_nodes}),
                "runtime_capabilities": multi_gpu_capabilities,
                "requested_controls": {"context_tokens": 8192},
                "required_controls": ["context_tokens"],
            }
        )
    )
    context_binding = {
        binding.control: binding for binding in constrained_receipt.control_bindings
    }["context_tokens"]

    assert constrained_receipt.decision == "degraded"
    assert 256 < constrained_receipt.selected_context_tokens < 8192
    assert context_binding.applied_value == constrained_receipt.selected_context_tokens
    assert context_binding.status == "degraded"

    unbound_context_receipt = ExecutionFitEstimator().evaluate(
        request.model_copy(
            update={
                "model_fingerprint": compact_fingerprint,
                "hardware": multi_gpu_graph.model_copy(update={"nodes": constrained_nodes}),
                "runtime_capabilities": multi_gpu_capabilities,
                "requested_controls": {},
                "required_controls": [],
            }
        )
    )
    assert unbound_context_receipt.decision == "rejected"
    assert "context-reduction-unbound" in unbound_context_receipt.reason_codes


def test_execution_fit_reconciliation_rejects_cross_plan_and_requires_rollback_on_memory_violation():
    from nexusnet.runtime.evolutionary_inference import (
        ExecutionFitReceipt,
        ExecutionFitReconciler,
        RuntimeObservation,
    )

    receipt = ExecutionFitReceipt(
        receipt_id="execution-fit::one",
        request_id="fit-request::one",
        plan_id="plan::one",
        model_fingerprint_id="model-fingerprint::one",
        hardware_fingerprint="hardware::one",
        runtime_name="runtime::one",
        decision="admitted",
        requested_context_tokens=4096,
        selected_context_tokens=4096,
        safe_context_tokens=8192,
        dense_weight_bytes=1024,
        expert_weight_bytes=0,
        active_expert_bytes=0,
        kv_cache_bytes=512,
        runtime_buffer_bytes=256,
        headroom_bytes=256,
        estimated_peak_ram_bytes=2048,
        estimated_peak_vram_bytes=0,
        placement={"dense": "ram", "experts": "ram", "kv-cache": "ram", "runtime-buffers": "ram"},
        predicted_bottleneck="ram",
        confidence=1.0,
    )
    reconciler = ExecutionFitReconciler(max_memory_regression_ratio=0.05)

    healthy = reconciler.reconcile(
        receipt,
        RuntimeObservation(
            plan_id="plan::one",
            latency_ms=10,
            quality_equivalent=True,
            stable=True,
            peak_ram_bytes=2000,
            peak_vram_bytes=0,
        ),
    )
    cross_plan = reconciler.reconcile(
        receipt,
        RuntimeObservation(
            plan_id="plan::other",
            latency_ms=10,
            quality_equivalent=True,
            stable=True,
            peak_ram_bytes=2000,
            peak_vram_bytes=0,
        ),
    )
    memory_violation = reconciler.reconcile(
        receipt,
        RuntimeObservation(
            plan_id="plan::one",
            latency_ms=10,
            quality_equivalent=True,
            stable=True,
            peak_ram_bytes=4096,
            peak_vram_bytes=0,
        ),
    )

    assert healthy.status == "healthy"
    assert healthy.reason_codes == ["fit-observation-within-bounds"]
    assert cross_plan.status == "rejected"
    assert cross_plan.reason_codes == ["fit-observation-plan-mismatch"]
    assert memory_violation.status == "rollback-required"
    assert memory_violation.reason_codes == ["peak-ram-exceeded-fit-receipt"]


def test_feasibility_selects_global_primitives_without_mutating_policy():
    cpu_graph = HardwareCapabilityDiscoverer(
        command_runner=lambda command, timeout: (_ for _ in ()).throw(FileNotFoundError(command[0])),
        system_name="Linux",
        machine="x86_64",
        processor_name="CPU",
        logical_cpu_count=8,
        total_memory_bytes=16 * 1024**3,
        disk_usage_reader=lambda _: SimpleNamespace(total=512 * 1024**3, free=256 * 1024**3),
        storage_root="/",
    ).discover()
    dense = fingerprint_from_metadata(
        {
            "architecture_family": "llama",
            "parameter_count": 3_000_000_000,
            "tensor_bytes": 3 * 1024**3,
            "quantization": "q4",
            "context_length": 8192,
            "layer_count": 28,
        }
    )

    feasibility = CandidateFeasibilityEvaluator().evaluate(
        graph=cpu_graph,
        fingerprint=dense,
        registry=InferencePrimitiveRegistry.default(),
    )

    assert feasibility.status == "shadow-feasible"
    assert feasibility.selected_primitive_id == "portable.cpu-reference"
    assert feasibility.policy_mutation_allowed is False
    assert feasibility.confidence > 0


def test_feasibility_prefers_selective_residency_for_moe_on_limited_vram_and_blocks_impossible_capacity():
    def cuda_runner(command: list[str], timeout: float):
        if command[0] == "nvidia-smi":
            return subprocess.CompletedProcess(command, 0, "Limited GPU, 8192, 550.1\n", "")
        raise FileNotFoundError(command[0])

    constrained_graph = HardwareCapabilityDiscoverer(
        command_runner=cuda_runner,
        system_name="Windows",
        machine="AMD64",
        processor_name="CPU",
        logical_cpu_count=16,
        total_memory_bytes=64 * 1024**3,
        disk_usage_reader=lambda _: SimpleNamespace(total=2 * 1024**4, free=1024**4),
        storage_root="F:/",
    ).discover()
    moe_model = fingerprint_from_metadata(
        {
            "architecture_family": "mixtral",
            "parameter_count": 46_700_000_000,
            "tensor_bytes": 26 * 1024**3,
            "quantization": "q4_k_m",
            "context_length": 32768,
            "layer_count": 32,
            "expert_count": 8,
            "experts_per_token": 2,
        }
    )

    feasible = CandidateFeasibilityEvaluator().evaluate(
        graph=constrained_graph,
        fingerprint=moe_model,
        registry=InferencePrimitiveRegistry.default(),
    )

    assert feasible.status == "shadow-feasible"
    assert feasible.selected_primitive_id == "moe.selective-residency"
    assert "limited-vram-tiered-residency" in feasible.reason_codes

    impossible = fingerprint_from_metadata(
        {
            "architecture_family": "dense-transformer",
            "parameter_count": 200_000_000_000,
            "tensor_bytes": 100 * 1024**3,
            "quantization": "q4",
            "context_length": 4096,
            "layer_count": 80,
        }
    )
    blocked = CandidateFeasibilityEvaluator().evaluate(
        graph=constrained_graph,
        fingerprint=impossible,
        registry=InferencePrimitiveRegistry.default(),
    )

    assert blocked.status == "blocked"
    assert blocked.selected_primitive_id is None
    assert "insufficient-system-memory" in blocked.blockers


def test_foundation_persists_sanitized_atomic_evidence_and_restores_after_restart(tmp_path):
    discoverer = HardwareCapabilityDiscoverer(
        command_runner=lambda command, timeout: (_ for _ in ()).throw(FileNotFoundError(command[0])),
        system_name="Linux",
        machine="x86_64",
        processor_name="Portable CPU",
        logical_cpu_count=8,
        total_memory_bytes=16 * 1024**3,
        disk_usage_reader=lambda _: SimpleNamespace(total=512 * 1024**3, free=256 * 1024**3),
        storage_root="/private/home/ChrisBoyd",
    )
    calibrator = BoundedHostCalibrator(
        limits=CalibrationLimits(memory_bytes=256 * 1024, memory_rounds=1, compute_iterations=1000)
    )
    foundation = EvolutionaryInferenceFoundation(
        artifacts_dir=tmp_path,
        discoverer=discoverer,
        calibrator=calibrator,
    )

    evidence = foundation.establish_baseline(model_fingerprint=synthetic_model_fingerprint())
    status = foundation.status()

    assert status["runtime_state"] == "live-evidence"
    assert status["artifact_ref"] == "runtime/evolutionary-inference/foundation-v1.json"
    assert status["policy_mutation_allowed"] is False
    assert {"portable.cpu-reference", "moe.selective-residency", "transfer.pageable", "transfer.double-buffered"} <= set(
        status["primitive_ids"]
    )
    assert evidence.feasibility.status == "shadow-feasible"
    artifact_path = tmp_path / status["artifact_ref"]
    assert artifact_path.exists()
    assert not artifact_path.with_suffix(".tmp").exists()
    serialized = artifact_path.read_text(encoding="utf-8")
    assert "ChrisBoyd" not in serialized
    assert "/private/home" not in serialized
    assert "prompt" not in serialized

    restarted = EvolutionaryInferenceFoundation(artifacts_dir=tmp_path)
    restarted_status = restarted.status()
    assert restarted_status["runtime_state"] == "live-evidence"
    assert restarted_status["evidence_id"] == status["evidence_id"]
    assert restarted_status["feasibility"] == status["feasibility"]


def test_foundation_reports_corrupt_persisted_evidence_as_degraded_without_fabrication(tmp_path):
    artifact = tmp_path / "runtime" / "evolutionary-inference" / "foundation-v1.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("{not-json", encoding="utf-8")

    foundation = EvolutionaryInferenceFoundation(artifacts_dir=tmp_path)
    status = foundation.status(ensure_baseline=True)

    assert status["runtime_state"] == "degraded-evidence"
    assert status["reason_codes"] == ["persisted-evidence-invalid"]
    assert status["policy_mutation_allowed"] is False
    assert "feasibility" not in status
    assert artifact.read_text(encoding="utf-8") == "{not-json"


def test_foundation_status_degrades_when_baseline_discovery_fails(tmp_path):
    class FailingDiscoverer:
        def discover(self):
            raise OSError("private device detail must not escape")

    foundation = EvolutionaryInferenceFoundation(
        artifacts_dir=tmp_path,
        discoverer=FailingDiscoverer(),
    )

    status = foundation.status(ensure_baseline=True)

    assert status["runtime_state"] == "degraded-evidence"
    assert status["reason_codes"] == ["baseline-establishment-failed"]
    assert status["policy_mutation_allowed"] is False
    assert "private device detail" not in json.dumps(status)
    assert not (tmp_path / "runtime" / "evolutionary-inference" / "foundation-v1.json").exists()
    CandidateFeasibilityEvaluator,
    InferencePrimitiveRegistry,
