from __future__ import annotations

from types import SimpleNamespace

import pytest

from nexusnet.runtime.evolutionary_inference import (
    BoundedHostCalibrator,
    CalibrationLimits,
    EvolutionaryInferenceFoundation,
    HardwareCapabilityDiscoverer,
    RuntimeModelMetadata,
    UnsupportedModelFeatureError,
    fingerprint_from_runtime_metadata,
)


def test_portable_transfer_is_measured_equivalent_bounded_and_preemptible(tmp_path):
    from nexusnet.runtime.evolutionary_inference import HardwareCalibrationLab, TransferExecutor, TransferRequest

    executor = TransferExecutor(storage_dir=tmp_path)
    pageable = executor.execute(
        TransferRequest(kind="pageable", bytes=256 * 1024, chunk_bytes=64 * 1024, repeat_count=3)
    )
    storage = executor.execute(
        TransferRequest(kind="storage", bytes=128 * 1024, chunk_bytes=32 * 1024, repeat_count=2)
    )
    preempted = executor.execute(
        TransferRequest(kind="double-buffered", bytes=256 * 1024, chunk_bytes=64 * 1024, repeat_count=2),
        cancel_check=lambda: True,
    )

    assert pageable.status == "completed"
    assert pageable.checksum_equivalent is True
    assert len(pageable.duration_ms) == 3
    assert pageable.effective_bandwidth_gib_s > 0
    assert storage.status == "completed"
    assert storage.bytes_moved == 128 * 1024 * 2 * 2
    assert not list(tmp_path.glob("transfer-*"))
    assert preempted.status == "preempted"
    assert preempted.bytes_moved == 0

    calibrated = HardwareCalibrationLab(executor, calibration_bytes=64 * 1024).calibrate(_discoverer().discover())
    portable_links = [link for link in calibrated.links if link.kind != "accelerator-transfer"]
    assert portable_links
    assert all(link.measured_bandwidth_gib_s and link.measured_bandwidth_gib_s > 0 for link in portable_links)


def test_synthesizer_and_pareto_adapt_to_hardware_and_slo(tmp_path):
    from nexusnet.runtime.evolutionary_inference import (
        ExecutionPlanSynthesizer,
        HardwareNode,
        PlanBenchmark,
        ParetoController,
        SLOProfile,
        TransferExecutor,
        WorkloadProfile,
        fingerprint_from_runtime_metadata,
    )

    fingerprint = fingerprint_from_runtime_metadata(_metadata())
    workload = WorkloadProfile(prompt_tokens=512, max_new_tokens=128, batch_size=1)
    latency_slo = SLOProfile(objective="latency", max_peak_vram_bytes=3 * 1024**3)
    memory_slo = SLOProfile(objective="memory", max_peak_vram_bytes=3 * 1024**3)
    graph = _discoverer().discover()
    graph = graph.model_copy(
        update={
            "nodes": graph.nodes
            + [
                HardwareNode(
                    node_id="gpu:cuda:0",
                    kind="gpu",
                    name="bounded-gpu",
                    backend="cuda",
                    memory_bytes=3 * 1024**3,
                    capabilities=["cuda", "device-memory"],
                )
            ]
        }
    )
    synthesizer = ExecutionPlanSynthesizer()
    latency_plans = synthesizer.synthesize(graph, fingerprint, workload, latency_slo)
    memory_plans = synthesizer.synthesize(graph, fingerprint, workload, memory_slo)

    assert any("transfer.double-buffered" in plan.primitive_ids for plan in latency_plans)
    assert latency_plans != memory_plans
    assert all(
        plan.fallback_plan_id == "plan::portable-reference"
        for plan in latency_plans
        if plan.plan_id != "plan::portable-reference"
    )

    benchmark = PlanBenchmark(TransferExecutor(storage_dir=tmp_path))
    evidence = [benchmark.run(plan, workload, repeat_count=3) for plan in latency_plans]
    frontier = ParetoController().frontier(evidence)
    assert frontier
    assert all(item.quality_equivalent and item.repeat_count >= 3 for item in frontier)
    assert ParetoController().select(frontier, latency_slo).plan.plan_id
    assert ParetoController().select(frontier, memory_slo).plan.plan_id

    tradeoff_latency = evidence[0].model_copy(
        update={
            "plan": evidence[0].plan.model_copy(update={"plan_id": "plan::latency-tradeoff"}),
            "warm_latency_ms": 1.0,
            "throughput_tokens_s": 100.0,
            "peak_ram_bytes": 8 * 1024**2,
            "peak_vram_bytes": 2 * 1024**3,
            "bytes_moved": 8 * 1024**2,
            "uncertainty": 0.01,
            "stable": True,
        }
    )
    tradeoff_memory = evidence[0].model_copy(
        update={
            "plan": evidence[0].plan.model_copy(update={"plan_id": "plan::memory-tradeoff"}),
            "warm_latency_ms": 5.0,
            "throughput_tokens_s": 20.0,
            "peak_ram_bytes": 64 * 1024,
            "peak_vram_bytes": 0,
            "bytes_moved": 64 * 1024,
            "uncertainty": 0.01,
            "stable": True,
        }
    )
    tradeoff_frontier = ParetoController().frontier([tradeoff_latency, tradeoff_memory])
    assert ParetoController().select(tradeoff_frontier, latency_slo).plan.plan_id == "plan::latency-tradeoff"
    assert ParetoController().select(tradeoff_frontier, memory_slo).plan.plan_id == "plan::memory-tradeoff"


def test_primitive_registry_rejects_unavailable_and_conflicting_compositions():
    from nexusnet.runtime.evolutionary_inference import InferencePrimitiveRegistry

    registry = InferencePrimitiveRegistry.default()
    assert registry.validate_composition(["portable.cpu-reference", "transfer.pageable"]) == []
    assert "primitive-conflict" in registry.validate_composition(
        ["portable.cpu-reference", "transfer.pageable", "transfer.accelerator-resident"]
    )
    assert "unknown-primitive" in registry.validate_composition(["external.unimplemented-method"])


def test_complete_system_promotes_rolls_back_and_dreams_without_raw_content(tmp_path):
    from nexusnet.runtime.evolutionary_inference import (
        CapacityGate,
        EvolutionaryInferenceSystem,
        RuntimeObservation,
        SLOProfile,
        WorkloadProfile,
    )

    system = EvolutionaryInferenceSystem(
        artifacts_dir=tmp_path,
        discoverer=_discoverer(),
        calibration_limits=CalibrationLimits(memory_bytes=128 * 1024, memory_rounds=1, compute_iterations=1000),
    )
    attached = system.attach_model(_metadata(provenance_ref="private/model/path"))
    selected = system.select_plan(
        WorkloadProfile(prompt_tokens=128, max_new_tokens=64, batch_size=1),
        SLOProfile(objective="balanced"),
    )
    dream = system.run_dream_cycle(
        CapacityGate(serving_idle=True, thermal_ok=True, memory_ok=True, power_ok=True, budget_remaining=3),
    )

    assert attached.fingerprint_id.startswith("model-fingerprint::")
    assert selected.plan_id
    assert dream.status in {"promoted", "rejected"}
    assert dream.trials_completed > 0
    active_before = system.status()["active_plan"]
    if active_before != "plan::portable-reference":
        outcome = system.observe(
            RuntimeObservation(plan_id=active_before, latency_ms=999999, quality_equivalent=False, stable=False)
        )
        assert outcome == "rolled-back"
        assert system.status()["active_plan"] == "plan::portable-reference"
    blocked = system.run_dream_cycle(
        CapacityGate(serving_idle=False, thermal_ok=True, memory_ok=True, power_ok=True, budget_remaining=3)
    )
    assert blocked.status == "gated"
    serialized = str(system.status())
    assert "private/model/path" not in serialized
    assert "prompt" not in serialized.lower()
    restarted = EvolutionaryInferenceSystem(
        artifacts_dir=tmp_path,
        discoverer=_discoverer(),
        calibration_limits=CalibrationLimits(memory_bytes=128 * 1024, memory_rounds=1, compute_iterations=1000),
    )
    assert set(restarted.status()["verified_plan_ids"]) >= set(system.status()["verified_plan_ids"])


def test_promotion_state_restarts_native_candidates_require_approval_and_drift_is_negative_prior(tmp_path):
    from nexusnet.runtime.evolutionary_inference import (
        EvolutionMemory,
        ExecutionPlan,
        PlanBenchmark,
        PlanPromotionController,
        RuntimeObservation,
        TransferExecutor,
        WorkloadProfile,
    )

    memory_path = tmp_path / "memory.json"
    policy_path = tmp_path / "policy.json"
    memory = EvolutionMemory(memory_path)
    controller = PlanPromotionController(policy_path, memory)
    plan = ExecutionPlan(
        plan_id="plan::reversible-challenger",
        primitive_ids=["portable.cpu-reference", "transfer.pageable"],
        parameters={"chunk_bytes": 64 * 1024},
        fallback_plan_id="plan::portable-reference",
        estimated_peak_ram_bytes=64 * 1024,
        estimated_peak_vram_bytes=0,
        feature_key="hardware-graph-workload-feature",
    )
    evidence = PlanBenchmark(TransferExecutor(storage_dir=tmp_path)).run(
        plan, WorkloadProfile(prompt_tokens=16, max_new_tokens=16), repeat_count=3
    )

    assert controller.promote(evidence, None) == "promoted"
    restarted = PlanPromotionController(policy_path, EvolutionMemory(memory_path))
    assert restarted.active_plan_id == plan.plan_id
    native = evidence.model_copy(
        update={"plan": plan.model_copy(update={"plan_id": "plan::native", "approval_required": True, "reversible": False})}
    )
    assert restarted.promote(native, evidence) == "approval-required"
    assert restarted.observe(
        RuntimeObservation(plan_id=plan.plan_id, latency_ms=99999, quality_equivalent=False, stable=False)
    ) == "rolled-back"
    assert restarted.active_plan_id == "plan::portable-reference"
    summary = EvolutionMemory(memory_path).summary()
    assert summary["outcomes"]["promoted"] == 1
    assert summary["outcomes"]["approval-required"] == 1
    assert summary["outcomes"]["rolled-back"] == 1


def test_dream_cycle_preempts_without_mutating_active_policy(tmp_path):
    from nexusnet.runtime.evolutionary_inference import CapacityGate, EvolutionaryInferenceSystem, SLOProfile, WorkloadProfile

    system = EvolutionaryInferenceSystem(
        artifacts_dir=tmp_path,
        discoverer=_discoverer(),
        calibration_limits=CalibrationLimits(memory_bytes=64 * 1024, memory_rounds=1, compute_iterations=1000),
    )
    system.attach_model(_metadata())
    system.select_plan(WorkloadProfile(prompt_tokens=32, max_new_tokens=16), SLOProfile())
    active_before = system.status()["active_plan"]
    checks = iter([False, True, True])
    result = system.run_dream_cycle(
        CapacityGate(serving_idle=True, thermal_ok=True, memory_ok=True, power_ok=True, budget_remaining=3),
        cancel_check=lambda: next(checks, True),
    )

    assert result.status == "preempted-safe-checkpoint"
    assert system.status()["active_plan"] == active_before


def test_verified_plan_parameters_reach_ollama_and_llamacpp_runtime_adapters(tmp_path, monkeypatch):
    from nexus.runtimes.registry import LlamaCppRuntimeAdapter, OllamaRuntimeAdapter
    import core.engines.llamacpp_engine as llama_engine_module
    import nexus.runtimes.registry as runtime_module

    selection = {
        "plan_id": "plan::verified-runtime",
        "verified": True,
        "parameters": {
            "gpu_layers": 12,
            "runtime_batch_tokens": 384,
            "context_tokens": 8192,
            "max_new_tokens": 96,
        },
    }
    captured_http = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"response": "ok"}

    monkeypatch.setattr(runtime_module.requests, "post", lambda url, json, timeout: captured_http.update(json) or Response())
    ollama = OllamaRuntimeAdapter()
    ollama.live = True
    assert ollama.generate(prompt="hello", messages=[], model_id="local/model", metadata={"evolutionary_inference": selection}) == "ok"
    assert captured_http["options"] == {"num_ctx": 8192, "num_batch": 384, "num_gpu": 12}
    captured_http.clear()
    unverified = {**selection, "verified": False}
    ollama.generate(prompt="hello", messages=[], model_id="local/model", metadata={"evolutionary_inference": unverified})
    assert "options" not in captured_http

    model_path = tmp_path / "model.gguf"
    model_path.write_bytes(b"gguf")
    captured_engine = {}

    class FakeEngine:
        def __init__(self, path, **kwargs):
            captured_engine.update({"path": path, **kwargs})

        def generate(self, prompt, **kwargs):
            captured_engine.update(kwargs)
            return "generated"

    monkeypatch.setattr(llama_engine_module, "LlamaCppEngine", FakeEngine)
    llamacpp = LlamaCppRuntimeAdapter({"model_path": str(model_path)})
    assert llamacpp.generate(prompt="hello", messages=[], model_id="local/model", metadata={"evolutionary_inference": selection}) == "generated"
    assert captured_engine["n_gpu_layers"] == 12
    assert captured_engine["n_batch"] == 384
    assert captured_engine["n_ctx"] == 8192
    assert captured_engine["max_new_tokens"] == 96


def _metadata(**overrides):
    payload = {
        "architecture_family": "sparse-transformer",
        "parameter_count": 46_700_000_000,
        "tensor_bytes": 26 * 1024**3,
        "quantization": "q4_k_m",
        "context_length": 32768,
        "layer_count": 32,
        "expert_count": 8,
        "experts_per_token": 2,
        "modalities": ["text"],
        "operator_families": ["attention", "grouped-gemm", "rmsnorm", "rope"],
        "tensor_groups": [
            {"group_id": "attention", "bytes": 6 * 1024**3, "dtype": "int4", "layout": "row-major"},
            {"group_id": "experts", "bytes": 20 * 1024**3, "dtype": "int4", "layout": "expert-major"},
        ],
        "state_and_kv_contract": {"kind": "paged-kv", "bytes_per_token": 131072},
        "sparsity_and_router_contract": {"kind": "top-k", "k": 2},
        "dynamic_shape_contract": {"batch": True, "sequence": True},
        "custom_operator_requirements": [],
        "rights_and_artifact_refs": ["artifact::trusted-model-metadata"],
        "unknown_or_unsupported_features": [],
        "provenance_ref": "source::one",
    }
    payload.update(overrides)
    return payload


def _discoverer(total_memory_bytes: int = 64 * 1024**3):
    return HardwareCapabilityDiscoverer(
        command_runner=lambda command, timeout: (_ for _ in ()).throw(FileNotFoundError(command[0])),
        system_name="Linux",
        machine="x86_64",
        processor_name="Portable CPU",
        logical_cpu_count=16,
        total_memory_bytes=total_memory_bytes,
        disk_usage_reader=lambda _: SimpleNamespace(total=2 * 1024**4, free=1024**4),
        storage_root="/",
    )


def test_runtime_fingerprint_uses_transferable_graph_features_not_provenance_identity():
    first = fingerprint_from_runtime_metadata(
        RuntimeModelMetadata.model_validate(_metadata(rights_and_artifact_refs=["C:/private/models/model.gguf"]))
    )
    second = fingerprint_from_runtime_metadata(
        _metadata(
            provenance_ref="source::different-model-id",
            rights_and_artifact_refs=["C:/private/models/model.gguf"],
        )
    )

    assert first.fingerprint_id == second.fingerprint_id
    assert first.graph_digest == second.graph_digest
    assert first.operator_families == ["attention", "grouped-gemm", "rmsnorm", "rope"]
    assert first.tensor_groups[1].group_id == "experts"
    assert first.source_kind == "metadata"
    serialized = first.model_dump_json()
    assert "different-model-id" not in serialized
    assert "provenance_ref" not in serialized
    assert "C:/private/models" not in serialized


def test_runtime_fingerprint_fails_closed_for_unknown_execution_features():
    with pytest.raises(UnsupportedModelFeatureError, match="custom::unsafe-op"):
        fingerprint_from_runtime_metadata(
            _metadata(unknown_or_unsupported_features=["custom::unsafe-op"])
        )


def test_hardware_startup_evidence_does_not_invent_a_synthetic_model(tmp_path):
    foundation = EvolutionaryInferenceFoundation(
        artifacts_dir=tmp_path,
        discoverer=_discoverer(),
        calibrator=BoundedHostCalibrator(
            limits=CalibrationLimits(memory_bytes=128 * 1024, memory_rounds=1, compute_iterations=1000)
        ),
    )

    evidence = foundation.establish_baseline()
    status = foundation.status()

    assert evidence.model_fingerprint is None
    assert evidence.feasibility is None
    assert status["runtime_state"] == "calibrated-awaiting-model"
    assert "model_fingerprint" not in status
    assert "synthetic" not in (tmp_path / status["artifact_ref"]).read_text(encoding="utf-8")
