from __future__ import annotations

from dataclasses import replace
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


def test_nanochat_assimilation_target_is_anchored_at_each_implementation_seam():
    from nexusnet.runtime.evolutionary_inference.dream_lab import DREAM_LAB_ASSIMILATION_TARGET_IDS
    from nexusnet.runtime.evolutionary_inference.hardware import HARDWARE_PROFILE_ASSIMILATION_TARGET_IDS
    from nexusnet.runtime.evolutionary_inference.synthesis import INFERENCE_EVOLUTION_ASSIMILATION_TARGET_IDS

    expected_target = "nanochat-constrained-hardware-reference"

    assert expected_target in HARDWARE_PROFILE_ASSIMILATION_TARGET_IDS
    assert expected_target in INFERENCE_EVOLUTION_ASSIMILATION_TARGET_IDS
    assert expected_target in DREAM_LAB_ASSIMILATION_TARGET_IDS


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
    records = {record.method_id: record for record in registry.method_records()}
    assert set(records) == {f"primitive::{primitive_id}" for primitive_id in registry.list_ids()}
    assert records["primitive::transfer.double-buffered"].source_kind == "primitive-family"
    assert records["primitive::transfer.double-buffered"].assimilation_paths == ["primitive"]
    assert records["primitive::transfer.double-buffered"].maturity == "primitive-extracted"
    assert records["primitive::transfer.double-buffered"].tunable_controls == [
        "buffer_depth",
        "chunk_bytes",
        "prefetch_depth",
    ]
    assert records["primitive::transfer.double-buffered"].reproduced_capabilities == [
        "copy-compute-overlap",
        "limited-vram-staging",
    ]


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


def test_complete_system_records_sanitized_live_moe_residency_evidence(tmp_path):
    from nexusnet.runtime.evolutionary_inference import EvolutionaryInferenceSystem, SLOProfile, WorkloadProfile
    from nexusnet.runtime.moe_residency import (
        ArchitectureTierHardware,
        MoEArchitectureDescriptor,
        MoEArchitectureTierPlanner,
        MoEResidencyTelemetry,
    )

    system = EvolutionaryInferenceSystem(
        artifacts_dir=tmp_path,
        discoverer=_discoverer(),
        calibration_limits=CalibrationLimits(memory_bytes=64 * 1024, memory_rounds=1, compute_iterations=1000),
    )
    system.attach_model(_metadata())
    selected = system.select_plan(WorkloadProfile(prompt_tokens=32, max_new_tokens=16), SLOProfile())
    tier_plan = MoEArchitectureTierPlanner().plan(
        MoEArchitectureDescriptor(
            model_ref="model:fixture",
            layer_count=2,
            experts_per_layer=4,
            experts_per_token=1,
            dense_core_bytes=64 * 1024,
            expert_bytes=8 * 1024,
            kv_cache_bytes_per_token=32,
            runtime_buffer_bytes=1024,
            storage_bytes=128 * 1024,
            model_digest="b" * 64,
        ),
        ArchitectureTierHardware(0, 2 * 1024**2, 4 * 1024**2, 1.0),
        context_tokens=64,
    )
    telemetry = MoEResidencyTelemetry.from_runtime_evidence(
        tier_plan,
        {
            "plan_ref": tier_plan.plan_id,
            "manifest_refs": ["manifest:fixture-layer"],
            "runtime_state": "tiered-warm",
            "layers": [{"tier_metrics": {"hot_hits": 6, "ram_hits": 2, "storage_misses": 2, "bytes_read": 4096}}],
        },
        generated_tokens=8,
        measurements_ms=[100, 100, 200],
        execution_plan_id=selected.plan_id,
        model_fingerprint_id=system.fingerprint.fingerprint_id,
    )

    with pytest.raises(ValueError, match="model fingerprint"):
        system.record_residency_evidence(
            replace(telemetry, model_fingerprint_id="model-fingerprint::other"),
            quality_equivalent=True,
            stable=True,
        )

    with pytest.raises(ValueError, match="quality equivalence"):
        system.record_residency_evidence(telemetry, quality_equivalent=False, stable=True)

    evidence = system.record_residency_evidence(telemetry, quality_equivalent=True, stable=True)
    status = system.status()

    assert evidence.plan.plan_id == selected.plan_id
    assert evidence.throughput_tokens_s == pytest.approx(20.0)
    assert status["residency_evidence"][selected.plan_id]["cache_hit_rate"] == pytest.approx(0.8)
    assert status["residency_evidence"][selected.plan_id]["gpu_mode"] == "auto"
    assert "prompt" not in str(status).lower()

    system.attach_model(_metadata(quantization="q5_k_m"))
    assert system.status()["residency_evidence"] == {}


def test_evolutionary_system_exposes_colibri_architecture_intake_as_a_live_governed_capability(tmp_path):
    from nexusnet.runtime.evolutionary_inference import EvolutionaryInferenceSystem

    system = EvolutionaryInferenceSystem(
        artifacts_dir=tmp_path,
        discoverer=_discoverer(),
        calibration_limits=CalibrationLimits(memory_bytes=64 * 1024, memory_rounds=1, compute_iterations=1000),
    )

    intake = system.status()["moe_architecture_intake"]

    assert intake["implementation_state"] == "available"
    assert intake["supported_dense_residency_tiers"] == ["gpu", "ram"]
    assert intake["gpu_acceleration_modes"] == ["off", "on", "auto"]
    assert intake["policy_mutation_allowed"] is False
    assert "explicit_architecture_descriptor" in intake["required_controls"]
    assert "per_inference_gpu_toggle" in intake["required_controls"]
    assert "exact_profile_gpu_benefit_gate" in intake["required_controls"]


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


def test_promotion_requires_material_pareto_gain_without_unbounded_regression(tmp_path):
    from nexusnet.runtime.evolutionary_inference import (
        ExecutionPlan,
        PlanBenchmark,
        PlanPromotionController,
        TransferExecutor,
        WorkloadProfile,
    )

    plan = ExecutionPlan(
        plan_id="plan::pareto-champion",
        primitive_ids=["portable.cpu-reference", "transfer.pageable"],
        parameters={
            "chunk_bytes": 64 * 1024,
            "pareto_max_regression_ratio": 0.05,
            "pareto_min_improvement_ratio": 0.01,
        },
        fallback_plan_id="plan::portable-reference",
        estimated_peak_ram_bytes=64 * 1024,
        estimated_peak_vram_bytes=0,
        feature_key="pareto-feature",
    )
    champion = PlanBenchmark(TransferExecutor(storage_dir=tmp_path)).run(
        plan, WorkloadProfile(prompt_tokens=16, max_new_tokens=16), repeat_count=3
    ).model_copy(
        update={
            "warm_latency_ms": 10.0,
            "throughput_tokens_s": 100.0,
            "peak_ram_bytes": 1000,
            "peak_vram_bytes": 1000,
            "bytes_moved": 1000,
            "uncertainty": 0.05,
        }
    )
    fast_but_unbounded = champion.model_copy(
        update={
            "plan": plan.model_copy(update={"plan_id": "plan::fast-but-unbounded"}),
            "warm_latency_ms": 8.0,
            "throughput_tokens_s": 110.0,
            "peak_ram_bytes": 1250,
        }
    )
    bounded_pareto_gain = champion.model_copy(
        update={
            "plan": plan.model_copy(update={"plan_id": "plan::bounded-pareto-gain"}),
            "warm_latency_ms": 8.0,
            "throughput_tokens_s": 110.0,
            "peak_ram_bytes": 1040,
        }
    )

    assert PlanPromotionController._improves(fast_but_unbounded, champion) is False
    assert PlanPromotionController._improves(bounded_pareto_gain, champion) is True


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
    from nexus.runtimes.registry import LlamaCppRuntimeAdapter, OllamaRuntimeAdapter, TGIRuntimeAdapter
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
            "threads": 8,
            "batch_threads": 4,
            "cache_type_k": "q8_0",
            "cache_type_v": "q4_0",
            "flash_attention": True,
            "offload_kqv": True,
            "main_gpu": 1,
            "split_mode": "layer",
            "tensor_split": "0.6,0.4",
        },
    }
    captured_http = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"response": "ok", "generated_text": "generated-by-tgi"}

    monkeypatch.setattr(runtime_module.requests, "post", lambda url, json, timeout: captured_http.update(json) or Response())
    ollama = OllamaRuntimeAdapter()
    ollama.live = True
    assert ollama.generate(prompt="hello", messages=[], model_id="local/model", metadata={"evolutionary_inference": selection}) == "ok"
    assert captured_http["options"] == {
        "num_ctx": 8192,
        "num_batch": 384,
        "num_gpu": 12,
        "num_predict": 96,
        "main_gpu": 1,
        "num_thread": 8,
    }
    captured_http.clear()
    unverified = {**selection, "verified": False}
    ollama.generate(prompt="hello", messages=[], model_id="local/model", metadata={"evolutionary_inference": unverified})
    assert "options" not in captured_http

    captured_http.clear()
    tgi = TGIRuntimeAdapter({"endpoint": "http://127.0.0.1:8080"})
    tgi.live = True
    assert tgi.generate(
        prompt="hello",
        messages=[],
        model_id="local/model",
        metadata={"evolutionary_inference": selection},
    ) == "generated-by-tgi"
    assert captured_http == {"inputs": "hello", "parameters": {"max_new_tokens": 96}}

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
    assert captured_engine["n_threads"] == 8
    assert captured_engine["n_threads_batch"] == 4
    assert captured_engine["cache_type_k"] == "q8_0"
    assert captured_engine["cache_type_v"] == "q4_0"
    assert captured_engine["flash_attn"] is True
    assert captured_engine["offload_kqv"] is True
    assert captured_engine["main_gpu"] == 1
    assert captured_engine["split_mode"] == "layer"
    assert captured_engine["tensor_split"] == "0.6,0.4"
    assert captured_engine["max_new_tokens"] == 96


def test_llamacpp_engine_normalizes_verified_kv_thread_and_placement_controls(monkeypatch):
    from types import SimpleNamespace
    import core.engines.llamacpp_engine as engine_module

    captured = {}

    class FakeLlama:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(engine_module, "Llama", FakeLlama)
    monkeypatch.setattr(
        engine_module,
        "llama_cpp",
        SimpleNamespace(
            GGML_TYPE_F16=1,
            GGML_TYPE_Q8_0=8,
            GGML_TYPE_Q4_0=4,
            LLAMA_SPLIT_MODE_NONE=0,
            LLAMA_SPLIT_MODE_LAYER=1,
            LLAMA_SPLIT_MODE_ROW=2,
        ),
        raising=False,
    )

    engine_module.LlamaCppEngine(
        "model.gguf",
        n_threads=8,
        n_threads_batch=4,
        cache_type_k="q8_0",
        cache_type_v="q4_0",
        flash_attn=True,
        offload_kqv=True,
        main_gpu=1,
        split_mode="row",
        tensor_split="0.6,0.4",
    )

    assert captured["n_threads"] == 8
    assert captured["n_threads_batch"] == 4
    assert captured["type_k"] == 8
    assert captured["type_v"] == 4
    assert captured["flash_attn"] is True
    assert captured["offload_kqv"] is True
    assert captured["main_gpu"] == 1
    assert captured["split_mode"] == 2
    assert captured["tensor_split"] == [0.6, 0.4]


def test_current_runtime_adapters_publish_versioned_control_capabilities():
    from nexus.runtimes.registry import (
        LlamaCppRuntimeAdapter,
        LMStudioRuntimeAdapter,
        MockRuntimeAdapter,
        OllamaRuntimeAdapter,
        OpenAICompatibleRuntimeAdapter,
        TGIRuntimeAdapter,
        TransformersRuntimeAdapter,
        VLLMRuntimeAdapter,
    )

    adapters = [
        MockRuntimeAdapter(),
        OllamaRuntimeAdapter(),
        OpenAICompatibleRuntimeAdapter(),
        TGIRuntimeAdapter(),
        VLLMRuntimeAdapter(),
        LMStudioRuntimeAdapter(),
        TransformersRuntimeAdapter(),
        LlamaCppRuntimeAdapter(),
    ]
    profiles = {adapter.runtime_name: adapter.runtime_capability_profile() for adapter in adapters}

    assert set(profiles) == {
        "llama.cpp",
        "lmstudio",
        "mock",
        "ollama",
        "openai-compatible",
        "tgi",
        "transformers",
        "vllm",
    }
    assert profiles["ollama"].supported_controls == [
        "context_tokens",
        "gpu_layers",
        "main_gpu",
        "max_new_tokens",
        "runtime_batch_tokens",
        "threads",
    ]
    assert profiles["llama.cpp"].supported_controls == [
        "batch_threads",
        "cache_type_k",
        "cache_type_v",
        "context_tokens",
        "flash_attention",
        "gpu_layers",
        "main_gpu",
        "max_new_tokens",
        "offload_kqv",
        "runtime_batch_tokens",
        "split_mode",
        "tensor_split",
        "threads",
    ]
    assert profiles["transformers"].supported_controls == ["max_new_tokens", "temperature", "top_p"]
    assert profiles["tgi"].supported_controls == ["max_new_tokens"]
    assert profiles["vllm"].supported_controls == ["max_new_tokens"]
    assert all(profile.implementation_digest.startswith("sha256:") for profile in profiles.values())
    assert all(profile.capability_state == "verified" for profile in profiles.values())


def test_runtime_binding_rejects_required_unsupported_controls_before_provider_call(monkeypatch):
    from nexus.runtimes.registry import OllamaRuntimeAdapter
    import nexus.runtimes.registry as runtime_module

    called = False

    def post(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("provider call must not happen")

    monkeypatch.setattr(runtime_module.requests, "post", post)
    adapter = OllamaRuntimeAdapter()
    adapter.live = True
    selection = {
        "plan_id": "plan::required-control",
        "verified": True,
        "parameters": {"context_tokens": 8192, "cache_type_k": "q8_0"},
        "required_controls": ["cache_type_k"],
    }

    with pytest.raises(RuntimeError, match="required runtime controls unsupported"):
        adapter.generate(
            prompt="hello",
            messages=[],
            model_id="local/model",
            metadata={"evolutionary_inference": selection},
        )

    receipt = adapter.control_binding_status()
    assert called is False
    assert receipt is not None
    assert receipt.decision == "rejected"
    assert receipt.reason_codes == ["required-control-unsupported"]
    assert {binding.control: binding.status for binding in receipt.bindings} == {
        "cache_type_k": "rejected",
        "context_tokens": "applied",
    }


def test_runtime_registry_exposes_whole_engine_method_records_without_new_registry_tree():
    from nexus.runtimes.registry import (
        LlamaCppRuntimeAdapter,
        MockRuntimeAdapter,
        OllamaRuntimeAdapter,
        RuntimeRegistry,
    )

    registry = object.__new__(RuntimeRegistry)
    registry.adapters = {
        "mock": MockRuntimeAdapter(),
        "ollama": OllamaRuntimeAdapter(),
        "llama.cpp": LlamaCppRuntimeAdapter(),
    }

    records = {record.method_id: record for record in registry.inference_method_records()}
    profiles = {profile.runtime_name: profile for profile in registry.runtime_capability_profiles()}

    assert {"runtime::llama.cpp", "runtime::mock", "runtime::ollama"} <= set(records)
    assert "primitive::portable.cpu-reference" in records
    assert "primitive::moe.selective-residency" in records
    assert records["runtime::ollama"].source_kind == "external-engine"
    assert records["runtime::ollama"].assimilation_paths == ["whole-engine"]
    assert records["runtime::ollama"].maturity == "adapted"
    assert records["runtime::ollama"].tunable_controls == [
        "context_tokens",
        "gpu_layers",
        "main_gpu",
        "max_new_tokens",
        "runtime_batch_tokens",
        "threads",
    ]
    assert profiles["llama.cpp"].implementation_digest == records["runtime::llama.cpp"].source_digest
    assert records["primitive::moe.selective-residency"].assimilation_paths == ["primitive"]
    researched_runtime_ids = {
        "runtime::coreml",
        "runtime::directml",
        "runtime::executorch",
        "runtime::litert",
        "runtime::mlc-llm",
        "runtime::onnx-genai",
        "runtime::onnxruntime-ep",
        "runtime::openvino-genai",
        "runtime::qnn",
        "runtime::sglang",
        "runtime::tensorrt-llm",
        "runtime::tgi",
        "runtime::webllm",
    }
    assert researched_runtime_ids <= set(records)
    assert records["runtime::tensorrt-llm"].maturity == "researched"
    assert records["runtime::tensorrt-llm"].assimilation_paths == ["whole-engine", "primitive"]
    assert len(records) == len({record.method_id for record in records.values()})


def test_runtime_adapter_rejects_fit_before_provider_call(monkeypatch):
    from nexus.runtimes.registry import OllamaRuntimeAdapter
    import nexus.runtimes.registry as runtime_module

    called = False

    def post(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("provider call must not happen")

    monkeypatch.setattr(runtime_module.requests, "post", post)
    adapter = OllamaRuntimeAdapter()
    adapter.live = True
    selection = {
        "plan_id": "plan::fit-rejected",
        "verified": True,
        "fit_required": True,
        "execution_fit_receipt": {
            "receipt_id": "execution-fit::blocked",
            "plan_id": "plan::fit-rejected",
            "decision": "rejected",
        },
        "parameters": {"context_tokens": 8192},
        "required_controls": ["context_tokens"],
    }

    with pytest.raises(RuntimeError, match="execution fit rejected"):
        adapter.generate(
            prompt="hello",
            messages=[],
            model_id="local/model",
            metadata={"evolutionary_inference": selection},
        )

    receipt = adapter.control_binding_status()
    assert called is False
    assert receipt is not None
    assert receipt.decision == "rejected"
    assert receipt.reason_codes == ["execution-fit-rejected"]


def test_runtime_adapter_excludes_planner_only_parameters_from_fitted_control_binding(monkeypatch):
    from nexus.runtimes.registry import OllamaRuntimeAdapter
    import nexus.runtimes.registry as runtime_module

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"response": "ok"}

    monkeypatch.setattr(runtime_module.requests, "post", lambda *args, **kwargs: Response())
    adapter = OllamaRuntimeAdapter()
    adapter.live = True
    selection = {
        "plan_id": "plan::fitted-controls",
        "verified": True,
        "fit_required": True,
        "execution_fit_receipt": {
            "plan_id": "plan::fitted-controls",
            "runtime_name": "ollama",
            "decision": "admitted",
            "control_bindings": [
                {"control": "context_tokens", "status": "applied"},
                {"control": "max_new_tokens", "status": "applied"},
            ],
        },
        "parameters": {
            "chunk_bytes": 512 * 1024,
            "buffer_depth": 2,
            "context_tokens": 4096,
            "max_new_tokens": 64,
        },
        "required_controls": ["context_tokens", "max_new_tokens"],
    }

    assert adapter.generate(
        prompt="hello",
        messages=[],
        model_id="local/model",
        metadata={"evolutionary_inference": selection},
    ) == "ok"

    receipt = adapter.control_binding_status()
    assert receipt is not None
    assert receipt.decision == "admitted"
    assert receipt.bound_parameters == {"context_tokens": 4096, "max_new_tokens": 64}
    assert {binding.control for binding in receipt.bindings} == {"context_tokens", "max_new_tokens"}

    empty_fit_receipt = adapter.bind_runtime_controls(
        {
            "evolutionary_inference": {
                "plan_id": "plan::planner-only",
                "verified": True,
                "fit_required": True,
                "execution_fit_receipt": {
                    "plan_id": "plan::planner-only",
                    "runtime_name": "ollama",
                    "decision": "admitted",
                    "control_bindings": [],
                },
                "parameters": {"chunk_bytes": 512 * 1024, "buffer_depth": 2},
                "required_controls": [],
            }
        }
    )
    assert empty_fit_receipt.decision == "admitted"
    assert empty_fit_receipt.bound_parameters == {}
    assert empty_fit_receipt.bindings == []

    reduced_context_receipt = adapter.bind_runtime_controls(
        {
            "evolutionary_inference": {
                "plan_id": "plan::safe-context",
                "verified": True,
                "fit_required": True,
                "execution_fit_receipt": {
                    "plan_id": "plan::safe-context",
                    "runtime_name": "ollama",
                    "decision": "degraded",
                    "control_bindings": [
                        {
                            "control": "context_tokens",
                            "requested_value": 4096,
                            "applied_value": 2048,
                            "status": "degraded",
                        }
                    ],
                },
                "parameters": {"context_tokens": 4096},
                "required_controls": ["context_tokens"],
            }
        }
    )
    assert reduced_context_receipt.decision == "degraded"
    assert reduced_context_receipt.bound_parameters == {"context_tokens": 2048}


def test_evolutionary_system_calculates_runtime_specific_fit_for_existing_plan(tmp_path):
    from nexus.runtimes.registry import OllamaRuntimeAdapter
    from nexusnet.runtime.evolutionary_inference import (
        EvolutionaryInferenceSystem,
        RuntimeObservation,
        SLOProfile,
        WorkloadProfile,
    )

    system = EvolutionaryInferenceSystem(
        artifacts_dir=tmp_path,
        discoverer=_discoverer(),
        calibration_limits=CalibrationLimits(memory_bytes=64 * 1024, memory_rounds=1, compute_iterations=1000),
    )
    system.attach_model(_metadata())
    workload = WorkloadProfile(prompt_tokens=128, max_new_tokens=64, batch_size=1)
    plan = system.select_plan(workload, SLOProfile())
    assert plan.parameters["threads"] == 8

    receipt = system.fit_plan(
        plan,
        workload,
        OllamaRuntimeAdapter().runtime_capability_profile(),
        required_controls=["context_tokens", "max_new_tokens"],
    )

    assert receipt.plan_id == plan.plan_id
    assert receipt.runtime_name == "ollama"
    assert receipt.model_fingerprint_id == system.fingerprint.fingerprint_id
    assert receipt.decision == "admitted"
    assert receipt.placement["dense"] == "ram"
    assert {binding.control: binding.status for binding in receipt.control_bindings} == {
        "context_tokens": "applied",
        "gpu_layers": "applied",
        "max_new_tokens": "applied",
        "runtime_batch_tokens": "applied",
        "threads": "applied",
    }
    assert system.status()["execution_fit_receipts"]["ollama"]["receipt_id"] == receipt.receipt_id

    reconciliation = system.reconcile_fit(
        RuntimeObservation(
            plan_id=plan.plan_id,
            latency_ms=10,
            quality_equivalent=True,
            stable=True,
            peak_ram_bytes=receipt.estimated_peak_ram_bytes,
            peak_vram_bytes=receipt.estimated_peak_vram_bytes,
        ),
        runtime_name="ollama",
    )
    assert reconciliation.status == "healthy"
    assert reconciliation.receipt_id == receipt.receipt_id
    assert system.status()["execution_fit_reconciliations"]["ollama"]["status"] == "healthy"


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
