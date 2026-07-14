from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from threading import Event, Lock
from typing import Any

import pytest
import torch
import torch.nn as nn

from nexusnet.hive.net.lm import NexusNetLM
from nexusnet.hive.net.model import MoECapsuleLayer, SwiGLUExpert
from nexusnet.runtime.moe_residency import (
    ExpertHeatPolicy,
    ExpertResidencyEvidence,
    ExpertIntegrityError,
    ExpertTensorManifest,
    HardwareMemorySnapshot,
    ColibriAssimilationProvenance,
    AdaptiveSpeculationController,
    MoEResidencyPlanner,
    MoEResidencyRequest,
    RouteTransitionPrefetcher,
    TieredExpertStore,
    TieredSwiGLUExecutionBackend,
    attach_tiered_moe_runtime,
    compute_model_identity,
    package_swiglu_experts,
)


def _request(**overrides) -> MoEResidencyRequest:
    values = {
        "model_ref": "model:nexusnet-fixture",
        "hardware": HardwareMemorySnapshot(
            gpu_available_bytes=1_000,
            ram_available_bytes=2_000,
            storage_available_bytes=1_000_000,
        ),
        "dense_core_bytes": 400,
        "kv_cache_bytes": 100,
        "runtime_buffer_bytes": 100,
        "gpu_headroom_bytes": 100,
        "ram_headroom_bytes": 200,
        "expert_bytes": 100,
        "expert_count": 30,
    }
    hardware_updates = {
        key: overrides.pop(key)
        for key in list(overrides)
        if key in {"gpu_available_bytes", "ram_available_bytes", "storage_available_bytes"}
    }
    values.update(overrides)
    if hardware_updates:
        values["hardware"] = HardwareMemorySnapshot(
            gpu_available_bytes=hardware_updates.get("gpu_available_bytes", 1_000),
            ram_available_bytes=hardware_updates.get("ram_available_bytes", 2_000),
            storage_available_bytes=hardware_updates.get("storage_available_bytes", 1_000_000),
        )
    return MoEResidencyRequest(**values)


def test_planner_rejects_when_dense_working_set_does_not_fit() -> None:
    plan = MoEResidencyPlanner().plan(
        _request(
            gpu_available_bytes=100,
            dense_core_bytes=80,
            kv_cache_bytes=10,
            runtime_buffer_bytes=10,
            gpu_headroom_bytes=20,
        )
    )

    assert plan.admission_state == "blocked"
    assert "dense_core_exceeds_gpu_working_set" in plan.blockers
    assert plan.gpu_expert_slots == 0


def test_planner_assigns_hot_warm_and_cold_expert_capacity() -> None:
    plan = MoEResidencyPlanner().plan(_request())

    assert plan.admission_state == "admitted"
    assert plan.gpu_expert_slots == 3
    assert plan.ram_expert_slots == 17
    assert plan.cold_store_required is True
    assert plan.cold_store_bytes > 3_000
    assert plan.expected_bottleneck == "storage-warmup"


def test_plan_identity_includes_ram_headroom_and_computed_outcome() -> None:
    planner = MoEResidencyPlanner()

    first = planner.plan(_request(ram_headroom_bytes=200))
    second = planner.plan(_request(ram_headroom_bytes=300))

    assert first.plan_id != second.plan_id
    assert first.ram_expert_slots != second.ram_expert_slots


def test_planner_requires_gpu_expert_workspace_and_host_staging() -> None:
    no_gpu_slot = MoEResidencyPlanner().plan(
        _request(
            gpu_available_bytes=700,
            dense_core_bytes=400,
            kv_cache_bytes=100,
            runtime_buffer_bytes=100,
            gpu_headroom_bytes=100,
        )
    )
    no_ram_staging = MoEResidencyPlanner().plan(
        _request(ram_available_bytes=350, ram_headroom_bytes=200)
    )

    assert "gpu_expert_workspace_unavailable" in no_gpu_slot.blockers
    assert "ram_expert_staging_workspace_unavailable" in no_ram_staging.blockers


def test_planner_blocks_when_cold_expert_storage_does_not_fit() -> None:
    plan = MoEResidencyPlanner().plan(_request(storage_available_bytes=100))

    assert "cold_expert_storage_insufficient" in plan.blockers


def test_heat_policy_requires_hysteresis_before_replacing_hot_expert() -> None:
    policy = ExpertHeatPolicy(slot_count=1, hysteresis=0.25)
    policy.touch("layer0:expert0", count=8)
    assert policy.repin() == ("layer0:expert0",)

    policy.touch("layer0:expert1", count=9)
    assert policy.repin() == ("layer0:expert0",)

    policy.touch("layer0:expert1", count=8)
    assert policy.repin() == ("layer0:expert1",)


def test_heat_decay_is_deterministic_and_preserves_minimum_observed_heat() -> None:
    policy = ExpertHeatPolicy(slot_count=2)
    policy.touch("layer0:expert0", count=5)
    policy.touch("layer0:expert1", count=2)

    policy.decay()

    assert policy.heat("layer0:expert0") == 2
    assert policy.heat("layer0:expert1") == 1


def test_heat_recency_cannot_overpower_a_much_hotter_expert_after_long_uptime() -> None:
    policy = ExpertHeatPolicy(slot_count=1, hysteresis=0.25)
    policy.touch("layer0:hot", count=100)
    assert policy.repin() == ("layer0:hot",)

    for index in range(30_000):
        policy.touch(f"layer0:cold-{index}")

    assert policy.repin() == ("layer0:hot",)


def _package_fixture(tmp_path: Path):
    torch.manual_seed(11)
    experts = nn.ModuleList([SwiGLUExpert(4, 8), SwiGLUExpert(4, 8)])
    manifest = package_swiglu_experts(
        experts,
        tmp_path,
        model_ref="model:nexusnet-fixture",
        layer_id="0",
    )
    return experts, manifest


def test_packaged_expert_round_trips_without_pickle(tmp_path: Path) -> None:
    experts, manifest = _package_fixture(tmp_path)
    store = TieredExpertStore(manifest, ram_slots=1, hot_slots=0)

    loaded = store.acquire(0, torch.device("cpu"))

    assert loaded["w_gate.weight"].equal(experts[0].w_gate.weight)
    assert loaded["w_value.bias"].equal(experts[0].w_value.bias)
    assert manifest.experts[0].path.endswith(".safetensors")
    assert not list(tmp_path.glob("*.pt"))
    assert not list(tmp_path.glob("*.pkl"))


def test_manifest_reopens_with_canonical_identity_validation(tmp_path: Path) -> None:
    _, manifest = _package_fixture(tmp_path)

    reopened = ExpertTensorManifest.read_json(
        tmp_path / "manifest.json",
        expected_model_ref="model:nexusnet-fixture",
        expected_layer_id="0",
        expected_expert_count=2,
    )

    assert reopened == manifest
    payload = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    payload["manifest_id"] = "expert-manifest:0000000000000000"
    (tmp_path / "manifest.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ExpertIntegrityError, match="canonical"):
        ExpertTensorManifest.read_json(tmp_path / "manifest.json")


def test_digest_mismatch_fails_closed(tmp_path: Path) -> None:
    _, manifest = _package_fixture(tmp_path)
    expert_path = Path(manifest.root_dir) / manifest.experts[0].path
    expert_path.write_bytes(b"corrupt")

    with pytest.raises(ExpertIntegrityError, match="does not match"):
        TieredExpertStore(manifest, ram_slots=1, hot_slots=0).acquire(
            0,
            torch.device("cpu"),
        )


def test_packaging_rejects_layer_id_path_traversal(tmp_path: Path) -> None:
    experts = nn.ModuleList([SwiGLUExpert(4, 8)])

    with pytest.raises(ValueError, match="layer_id"):
        package_swiglu_experts(
            experts,
            tmp_path,
            model_ref="model:nexusnet-fixture",
            layer_id="../escape",
        )


def test_store_rejects_shard_larger_than_configured_bound(tmp_path: Path) -> None:
    _, manifest = _package_fixture(tmp_path)
    shard_size = manifest.experts[0].size_bytes
    store = TieredExpertStore(
        manifest,
        ram_slots=1,
        hot_slots=0,
        max_shard_bytes=shard_size - 1,
    )

    with pytest.raises(ExpertIntegrityError, match="configured bound"):
        store.acquire(0, torch.device("cpu"))


def test_ram_slot_eviction_is_visible_in_store_evidence(tmp_path: Path) -> None:
    _, manifest = _package_fixture(tmp_path)
    store = TieredExpertStore(manifest, ram_slots=1, hot_slots=0)

    store.acquire(0, torch.device("cpu"))
    store.acquire(1, torch.device("cpu"))
    store.acquire(0, torch.device("cpu"))

    evidence = store.evidence()
    assert evidence["storage_misses"] == 3
    assert evidence["ram_hits"] == 0
    assert evidence["ram_evictions"] == 2
    assert evidence["bytes_read"] > 0


def test_tiered_backend_matches_resident_moe_output(tmp_path: Path) -> None:
    torch.manual_seed(7)
    layer = MoECapsuleLayer(4, 8, num_experts=3, top_k=2).eval()
    x = torch.randn(6, 4)
    expected = layer(x)
    backend = TieredSwiGLUExecutionBackend.from_layer(
        layer,
        tmp_path,
        model_ref="model:nexusnet-fixture",
        layer_id="0",
        ram_slots=1,
        hot_slots=1,
    )

    layer.set_execution_backend(backend)
    actual = layer(x)

    torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    assert backend.evidence()["storage_misses"] > 0


def test_tiered_backend_cannot_be_attached_while_layer_is_training(tmp_path: Path) -> None:
    layer = MoECapsuleLayer(4, 8, num_experts=2, top_k=1).eval()
    backend = TieredSwiGLUExecutionBackend.from_layer(
        layer,
        tmp_path,
        model_ref="model:nexusnet-fixture",
        layer_id="0",
        ram_slots=1,
        hot_slots=0,
    )
    layer.train()

    with pytest.raises(RuntimeError, match="inference-only"):
        layer.set_execution_backend(backend)


def test_attached_tiered_backend_fails_closed_if_layer_switches_to_training(tmp_path: Path) -> None:
    layer = MoECapsuleLayer(4, 8, num_experts=2, top_k=1).eval()
    backend = TieredSwiGLUExecutionBackend.from_layer(
        layer,
        tmp_path,
        model_ref="model:nexusnet-fixture",
        layer_id="0",
        ram_slots=1,
        hot_slots=0,
    )
    layer.set_execution_backend(backend)
    layer.train()

    with pytest.raises(RuntimeError, match="inference-only"):
        layer(torch.randn(2, 4))


def test_tiered_backend_can_release_and_restore_resident_expert_parameters(tmp_path: Path) -> None:
    torch.manual_seed(19)
    layer = MoECapsuleLayer(4, 8, num_experts=3, top_k=2).eval()
    x = torch.randn(5, 4)
    expected = layer(x)
    expected_state = {name: tensor.clone() for name, tensor in layer.state_dict().items()}
    resident_parameter_count = sum(parameter.numel() for parameter in layer.parameters())

    backend = TieredSwiGLUExecutionBackend.from_layer(
        layer,
        tmp_path,
        model_ref="model:nexusnet-fixture",
        layer_id="0",
        ram_slots=1,
        hot_slots=1,
        release_resident=True,
    )
    layer.set_execution_backend(backend)

    assert sum(parameter.numel() for parameter in layer.parameters()) < resident_parameter_count
    torch.testing.assert_close(layer(x), expected, rtol=0, atol=0)
    attached_state = layer.state_dict()
    assert attached_state.keys() == expected_state.keys()
    for name, tensor in expected_state.items():
        torch.testing.assert_close(attached_state[name], tensor, rtol=0, atol=0)

    backend.restore_resident(layer)
    layer.set_execution_backend(None)

    assert sum(parameter.numel() for parameter in layer.parameters()) == resident_parameter_count
    torch.testing.assert_close(layer(x), expected, rtol=0, atol=0)
    layer.train()
    with pytest.raises(RuntimeError, match="optimizer rebind"):
        layer(x)
    layer.acknowledge_optimizer_rebind()
    layer(x).sum().backward()


def test_existing_manifest_can_attach_after_restart_without_repackaging(tmp_path: Path) -> None:
    torch.manual_seed(19)
    original = MoECapsuleLayer(4, 8, num_experts=2, top_k=1).eval()
    restarted = deepcopy(original)
    inputs = torch.randn(5, 4)
    expected = restarted(inputs)
    manifest = package_swiglu_experts(
        original.experts,
        tmp_path,
        model_ref="model:nexusnet-fixture",
        layer_id="restart",
    )

    backend = TieredSwiGLUExecutionBackend.from_manifest(
        restarted,
        tmp_path / "manifest.json",
        model_ref=manifest.model_ref,
        layer_id=manifest.layer_id,
        ram_slots=1,
        hot_slots=1,
        release_resident=True,
    )
    restarted.set_execution_backend(backend)

    torch.testing.assert_close(restarted(inputs), expected, rtol=0, atol=0)


def test_attached_layer_tracks_dtype_migration_in_cache_and_restore(tmp_path: Path) -> None:
    torch.manual_seed(29)
    layer = MoECapsuleLayer(4, 8, num_experts=2, top_k=1).eval()
    reference = deepcopy(layer).half()
    inputs = torch.randn(5, 4).half()
    expected = reference(inputs)
    backend = TieredSwiGLUExecutionBackend.from_layer(
        layer,
        tmp_path,
        model_ref="model:nexusnet-fixture",
        layer_id="dtype",
        ram_slots=1,
        hot_slots=1,
        release_resident=True,
    )
    layer.set_execution_backend(backend)

    layer.half()
    actual = layer(inputs)
    attached_state = layer.state_dict()
    assert all(tensor.dtype == torch.float16 for tensor in attached_state.values())
    backend.restore_resident(layer)
    layer.set_execution_backend(None)

    torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    assert all(parameter.dtype == torch.float16 for parameter in layer.parameters())


def test_released_resident_experts_must_be_restored_before_backend_detach(tmp_path: Path) -> None:
    layer = MoECapsuleLayer(4, 8, num_experts=2, top_k=1).eval()
    backend = TieredSwiGLUExecutionBackend.from_layer(
        layer,
        tmp_path,
        model_ref="model:nexusnet-fixture",
        layer_id="0",
        ram_slots=1,
        hot_slots=0,
        release_resident=True,
    )
    layer.set_execution_backend(backend)

    with pytest.raises(RuntimeError, match="restore resident experts"):
        layer.set_execution_backend(None)


def test_native_lm_runs_end_to_end_with_all_moe_layers_storage_backed(tmp_path: Path) -> None:
    torch.manual_seed(23)
    model = NexusNetLM(
        vocab_size=32,
        d_model=16,
        n_heads=4,
        n_kv_heads=2,
        num_experts=3,
        top_k=2,
        d_hidden=24,
        num_layers=2,
    ).eval()
    token_ids = torch.tensor([[1, 2, 3, 4]])
    expected = model(token_ids)
    resident_parameter_count = sum(parameter.numel() for parameter in model.parameters())
    largest_expert_bytes = max(
        sum(parameter.numel() * parameter.element_size() for parameter in block.moe.experts[0].parameters())
        for block in model.blocks
    )
    plan = MoEResidencyPlanner().plan(
        _request(
            model_ref="model:nexusnet-lm-fixture",
            model_digest=compute_model_identity(model),
            expert_count=6,
            expert_bytes=largest_expert_bytes,
            gpu_available_bytes=12_000,
            ram_available_bytes=20_000,
        )
    )

    attachment = attach_tiered_moe_runtime(
        model,
        tmp_path,
        plan=plan,
        model_ref="model:nexusnet-lm-fixture",
        release_resident=True,
    )
    actual = model(token_ids)

    assert len(attachment.backends) == 2
    assert sum(parameter.numel() for parameter in model.parameters()) < resident_parameter_count
    torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    assert all(item["storage_misses"] > 0 for item in attachment.evidence())

    repeated = model(token_ids)
    attachment.wait_for_prefetch()

    torch.testing.assert_close(repeated, expected, rtol=0, atol=0)
    assert attachment.evidence()[1]["prefetch_requests"] > 0

    runtime_evidence = attachment.runtime_evidence()
    assert runtime_evidence["plan_ref"] == plan.plan_id
    assert len(runtime_evidence["manifest_refs"]) == 2
    assert runtime_evidence["runtime_state"] in {
        "tiered-cold",
        "tiered-warm",
        "tiered-warming",
    }
    assert "prompt" not in json.dumps(runtime_evidence).lower()
    next_window = attachment.runtime_evidence()
    assert next_window["runtime_state"] == "tiered-warming"
    assert all(not layer["tier_metrics"] for layer in next_window["layers"])

    for _ in range(20):
        model(token_ids)
    assert attachment.pending_prefetch_count <= 2 * len(attachment.backends)

    attachment.restore()

    assert sum(parameter.numel() for parameter in model.parameters()) == resident_parameter_count
    torch.testing.assert_close(model(token_ids), expected, rtol=0, atol=0)


def test_model_attachment_rejects_blocked_residency_plan(tmp_path: Path) -> None:
    model = NexusNetLM(
        vocab_size=16,
        d_model=8,
        n_heads=2,
        n_kv_heads=1,
        num_experts=2,
        top_k=1,
        d_hidden=12,
        num_layers=1,
    ).eval()
    blocked_plan = MoEResidencyPlanner().plan(
        _request(
            gpu_available_bytes=100,
            dense_core_bytes=80,
            kv_cache_bytes=10,
            runtime_buffer_bytes=10,
            gpu_headroom_bytes=20,
        )
    )

    with pytest.raises(RuntimeError, match="residency plan is blocked"):
        attach_tiered_moe_runtime(
            model,
            tmp_path,
            plan=blocked_plan,
            model_ref="model:nexusnet-fixture",
        )


def test_model_attachment_rejects_plan_for_different_expert_layout(tmp_path: Path) -> None:
    model = NexusNetLM(
        vocab_size=16,
        d_model=8,
        n_heads=2,
        n_kv_heads=1,
        num_experts=2,
        top_k=1,
        d_hidden=12,
        num_layers=1,
    ).eval()
    mismatched_plan = MoEResidencyPlanner().plan(
        _request(
            model_ref="model:other",
            expert_count=99,
            expert_bytes=1,
        )
    )

    with pytest.raises(RuntimeError, match="model_ref"):
        attach_tiered_moe_runtime(
            model,
            tmp_path,
            plan=mismatched_plan,
            model_ref="model:nexusnet-fixture",
        )


def test_model_attachment_rejects_same_topology_with_different_weights(tmp_path: Path) -> None:
    torch.manual_seed(1)
    planned = NexusNetLM(
        vocab_size=16, d_model=8, n_heads=2, n_kv_heads=1,
        num_experts=2, top_k=1, d_hidden=12, num_layers=1,
    ).eval()
    torch.manual_seed(2)
    different = NexusNetLM(
        vocab_size=16, d_model=8, n_heads=2, n_kv_heads=1,
        num_experts=2, top_k=1, d_hidden=12, num_layers=1,
    ).eval()
    expert_bytes = max(
        sum(parameter.numel() * parameter.element_size() for parameter in expert.parameters())
        for expert in planned.blocks[0].moe.experts
    )
    plan = MoEResidencyPlanner().plan(
        _request(
            model_ref="model:nexusnet-lm-fixture",
            model_digest=compute_model_identity(planned),
            expert_count=2,
            expert_bytes=expert_bytes,
            gpu_available_bytes=10_000,
            ram_available_bytes=20_000,
        )
    )

    with pytest.raises(RuntimeError, match="model identity"):
        attach_tiered_moe_runtime(
            different,
            tmp_path,
            plan=plan,
            model_ref="model:nexusnet-lm-fixture",
        )


def test_prefetch_learns_layer_transition_without_changing_route_authority() -> None:
    prefetcher = RouteTransitionPrefetcher(max_candidates=2)
    for _ in range(4):
        prefetcher.observe("0", (1, 2), "1", (3,))
    prefetcher.observe("0", (1, 2), "1", (4,))

    assert prefetcher.candidates("0", (1, 2), "1") == (3, 4)


def test_store_prefetch_warms_ram_and_records_useful_hit(tmp_path: Path) -> None:
    _, manifest = _package_fixture(tmp_path)
    store = TieredExpertStore(manifest, ram_slots=1, hot_slots=0)

    future = store.prefetch(0, torch.device("cpu"))
    future.result(timeout=5)
    store.acquire(0, torch.device("cpu"))

    evidence = store.evidence()
    assert evidence["prefetch_requests"] == 1
    assert evidence["prefetch_hits"] == 1
    assert evidence["storage_misses"] == 1


def test_failed_prefetch_cleans_inflight_state_without_poisoning_demand(tmp_path: Path) -> None:
    _, manifest = _package_fixture(tmp_path)
    expert_path = Path(manifest.root_dir) / manifest.experts[0].path
    expert_path.write_bytes(b"corrupt")
    store = TieredExpertStore(manifest, ram_slots=1, hot_slots=0)

    future = store.prefetch(0, torch.device("cpu"))
    with pytest.raises(ExpertIntegrityError):
        future.result(timeout=5)

    evidence = store.evidence()
    assert evidence["prefetch_failures"] == 1
    assert evidence["inflight_prefetches"] == 0


def test_concurrent_prefetch_reserves_one_same_key_load(tmp_path: Path) -> None:
    _, manifest = _package_fixture(tmp_path)
    store = TieredExpertStore(manifest, ram_slots=1, hot_slots=0)
    real_submit = store._prefetch_executor.submit
    first_submit_entered = Event()
    release_first_submit = Event()
    calls_lock = Lock()
    submit_calls = 0

    def controlled_submit(*args, **kwargs):
        nonlocal submit_calls
        with calls_lock:
            submit_calls += 1
            ordinal = submit_calls
        if ordinal == 1:
            first_submit_entered.set()
            assert release_first_submit.wait(timeout=5)
        else:
            release_first_submit.set()
        return real_submit(*args, **kwargs)

    store._prefetch_executor.submit = controlled_submit
    with ThreadPoolExecutor(max_workers=2) as callers:
        first_outer = callers.submit(store.prefetch, 0, torch.device("cpu"))
        assert first_submit_entered.wait(timeout=5)
        second_outer = callers.submit(store.prefetch, 0, torch.device("cpu"))
        second = second_outer.result(timeout=5)
        release_first_submit.set()
        first = first_outer.result(timeout=5)

    assert first is second
    first.result(timeout=5)
    assert submit_calls == 1


def test_concurrent_cold_demand_coalesces_storage_read_without_cache(tmp_path: Path) -> None:
    _, manifest = _package_fixture(tmp_path)
    store = TieredExpertStore(manifest, ram_slots=0, hot_slots=0)
    real_load = store._load_from_storage
    first_load_entered = Event()
    release_first_load = Event()
    second_started = Event()
    calls_lock = Lock()
    load_calls = 0

    def controlled_load(expert_id: int):
        nonlocal load_calls
        with calls_lock:
            load_calls += 1
            ordinal = load_calls
        if ordinal == 1:
            first_load_entered.set()
            assert release_first_load.wait(timeout=5)
        return real_load(expert_id)

    def second_acquire():
        second_started.set()
        return store.acquire(0, torch.device("cpu"))

    store._load_from_storage = controlled_load
    with ThreadPoolExecutor(max_workers=2) as callers:
        first = callers.submit(store.acquire, 0, torch.device("cpu"))
        assert first_load_entered.wait(timeout=5)
        second = callers.submit(second_acquire)
        assert second_started.wait(timeout=5)
        release_first_load.set()
        first.result(timeout=5)
        second.result(timeout=5)

    assert load_calls == 1


def test_ram_eviction_marks_unused_prefetch_as_wasted(tmp_path: Path) -> None:
    _, manifest = _package_fixture(tmp_path)
    store = TieredExpertStore(manifest, ram_slots=1, hot_slots=0)

    store.prefetch(0, torch.device("cpu")).result(timeout=5)
    store.acquire(1, torch.device("cpu"))

    assert store.evidence()["prefetch_wasted"] == 1


def test_hot_pin_prevents_lru_eviction_by_unpinned_expert(tmp_path: Path) -> None:
    _, manifest = _package_fixture(tmp_path)
    store = TieredExpertStore(manifest, ram_slots=2, hot_slots=1)
    device = torch.device("cpu")
    store.acquire(0, device)
    store.pin((0,), device)

    store.acquire(1, device)
    hot_hits_before = store.evidence()["hot_hits"]
    store.acquire(0, device)

    evidence = store.evidence()
    assert evidence["hot_hits"] == hot_hits_before + 1
    assert evidence["pinned_hot_experts"] == [0]


def test_active_lease_prevents_hot_expert_eviction(tmp_path: Path) -> None:
    _, manifest = _package_fixture(tmp_path)
    store = TieredExpertStore(manifest, ram_slots=2, hot_slots=1)
    device = torch.device("cpu")

    with store.lease(0, device):
        store.acquire(1, device)
        hot_hits_before = store.evidence()["hot_hits"]
        store.acquire(0, device)
        assert store.evidence()["hot_hits"] == hot_hits_before + 1
        assert store.evidence()["active_leases"] == 1

    assert store.evidence()["active_leases"] == 0


def test_adaptive_speculation_disables_slower_profile_despite_high_acceptance() -> None:
    controller = AdaptiveSpeculationController(min_trials=2, min_speedup=1.02)
    controller.observe(
        "disk-cold",
        baseline_seconds=1.0,
        candidate_seconds=1.2,
        accepted=8,
        proposed=8,
    )
    controller.observe(
        "disk-cold",
        baseline_seconds=1.0,
        candidate_seconds=1.1,
        accepted=8,
        proposed=8,
    )

    state = controller.state("disk-cold")
    assert controller.enabled("disk-cold") is False
    assert state.reason == "non_positive_end_to_end_benefit"
    assert state.acceptance_rate == 1.0
    assert state.speedup < 1.0


def test_disabled_speculation_profile_uses_target_only_decode() -> None:
    controller = AdaptiveSpeculationController(min_trials=1, min_speedup=1.0)
    controller.observe(
        "resident",
        baseline_seconds=1.0,
        candidate_seconds=2.0,
        accepted=4,
        proposed=4,
    )
    calls: list[str] = []

    def target_only(*args: Any, **kwargs: Any) -> dict[str, str]:
        calls.append("target")
        return {"mode": "target"}

    def speculative(*args: Any, **kwargs: Any) -> dict[str, str]:
        calls.append("speculative")
        return {"mode": "speculative"}

    result = controller.decode(
        "resident",
        target_only=target_only,
        speculative=speculative,
    )

    assert result == {"mode": "target"}
    assert calls == ["target"]


def test_enabled_decode_cannot_bypass_target_verification_for_tensors() -> None:
    controller = AdaptiveSpeculationController(min_trials=1, min_speedup=0.01)
    calls: list[str] = []

    result = controller.decode(
        "resident",
        target_only=lambda: calls.append("target") or torch.tensor([1, 2]),
        speculative=lambda: calls.append("speculative") or torch.tensor([1, 2]),
    )

    assert torch.equal(result, torch.tensor([1, 2]))
    assert calls == ["target", "speculative"]


def test_speculation_run_measures_and_target_verifies_candidate() -> None:
    timestamps = iter((0.0, 1.0, 1.0, 3.0))
    controller = AdaptiveSpeculationController(
        min_trials=1,
        min_speedup=1.0,
        clock=lambda: next(timestamps),
    )

    result = controller.run(
        "storage-cold",
        target_only=lambda: {"tokens": [1, 2], "accepted": 0, "proposed": 0},
        speculative=lambda: {"tokens": [1, 2], "accepted": 2, "proposed": 2},
        equivalent=lambda target, candidate: target["tokens"] == candidate["tokens"],
    )

    assert result["tokens"] == [1, 2]
    assert controller.state("storage-cold").enabled is False
    assert controller.state("storage-cold").reason == "non_positive_end_to_end_benefit"


def test_speculation_run_rejects_candidate_that_differs_from_target() -> None:
    timestamps = iter((0.0, 1.0, 1.0, 1.5))
    controller = AdaptiveSpeculationController(clock=lambda: next(timestamps))

    result = controller.run(
        "storage-cold",
        target_only=lambda: {"tokens": [1, 2]},
        speculative=lambda: {"tokens": [1, 3], "accepted": 2, "proposed": 2},
        equivalent=lambda target, candidate: target["tokens"] == candidate["tokens"],
    )

    assert result == {"tokens": [1, 2]}
    assert controller.state("storage-cold").enabled is False
    assert controller.state("storage-cold").reason == "target_verification_mismatch"


def test_speculation_run_falls_back_when_candidate_fails() -> None:
    timestamps = iter((0.0, 1.0, 1.0))
    controller = AdaptiveSpeculationController(clock=lambda: next(timestamps))

    def fail() -> dict[str, object]:
        raise RuntimeError("candidate failed")

    result = controller.run(
        "storage-cold",
        target_only=lambda: {"tokens": [1, 2]},
        speculative=fail,
    )

    assert result == {"tokens": [1, 2]}
    assert controller.state("storage-cold").enabled is False
    assert controller.state("storage-cold").reason == "candidate_execution_failed"


def test_evidence_contains_runtime_metrics_but_no_prompt_content() -> None:
    evidence = ExpertResidencyEvidence(
        plan_ref="moe-plan:fixture",
        manifest_ref="expert-manifest:fixture",
    )
    evidence.record_store_metrics(
        {
            "storage_misses": 3,
            "ram_hits": 5,
            "hot_hits": 7,
            "bytes_read": 4096,
            "prefetch_requests": 2,
            "prefetch_hits": 1,
        }
    )
    evidence.record_fallback("load_timeout")

    payload = evidence.snapshot()

    assert payload["fallback_events"] == ["load_timeout"]
    assert payload["tier_metrics"]["bytes_read"] == 4096
    assert "prompt" not in json.dumps(payload).lower()
    assert "completion" not in json.dumps(payload).lower()


def test_evidence_refs_and_runtime_states_are_sanitized() -> None:
    with pytest.raises(ValueError, match="sanitized"):
        ExpertResidencyEvidence(
            plan_ref="moe-plan:fixture prompt text",
            manifest_ref="expert-manifest:fixture",
        )

    warming = ExpertResidencyEvidence(
        plan_ref="moe-plan:fixture",
        manifest_ref="expert-manifest:fixture",
    )
    assert warming.snapshot()["runtime_state"] == "tiered-warming"
    warming.record_store_metrics({"storage_misses": 1})
    assert warming.snapshot()["runtime_state"] == "tiered-cold"
    warming.record_store_metrics({"ram_hits": 1})
    assert warming.snapshot()["runtime_state"] == "tiered-warm"


def test_evidence_rejects_invalid_metrics_and_degrades_on_load_failure() -> None:
    evidence = ExpertResidencyEvidence(
        plan_ref="moe-plan:fixture",
        manifest_ref="expert-manifest:fixture",
    )
    with pytest.raises(ValueError, match="finite non-negative"):
        evidence.record_store_metrics({"bytes_read": -1})

    evidence.record_store_metrics({"prefetch_failures": 1})
    payload = evidence.snapshot()
    assert payload["runtime_state"] == "tiered-degraded"
    assert payload["fallback_events"] == ["prefetch_failed"]


def test_colibri_provenance_is_commit_pinned_and_excludes_server_integration() -> None:
    provenance = ColibriAssimilationProvenance()
    payload = provenance.as_dict()

    assert payload["repository"] == "https://github.com/JustVugg/colibri"
    assert payload["commit"] == "748787c3afa8ab336bb51bf616f212a04f209bba"
    assert payload["license"] == "Apache-2.0"
    assert "c/tier.h" in payload["eligible_attributed_sources"]
    assert "c/resource_plan.py" in payload["eligible_attributed_sources"]
    assert "c/openai_server.py" in payload["excluded_sources"]
    assert payload["assimilation_classification"] == "independent-behavioral-assimilation"
    assert payload["source_sha256"]["c/tier.h"] == (
        "1971c5325fc4ffe5dce17e50d7781dc64ef31d14ebf354cb2452ca6c13a3d495"
    )
    assert payload["license_file"] == "docs/third-party/licenses/Apache-2.0-Colibri.txt"
