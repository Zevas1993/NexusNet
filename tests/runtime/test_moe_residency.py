from __future__ import annotations

import json
from pathlib import Path
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
    HardwareMemorySnapshot,
    ColibriAssimilationProvenance,
    AdaptiveSpeculationController,
    MoEResidencyPlanner,
    MoEResidencyRequest,
    RouteTransitionPrefetcher,
    TieredExpertStore,
    TieredSwiGLUExecutionBackend,
    attach_tiered_moe_runtime,
    package_swiglu_experts,
)


def _request(**overrides) -> MoEResidencyRequest:
    values = {
        "model_ref": "model:nexusnet-fixture",
        "hardware": HardwareMemorySnapshot(
            gpu_available_bytes=1_000,
            ram_available_bytes=2_000,
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
        if key in {"gpu_available_bytes", "ram_available_bytes"}
    }
    values.update(overrides)
    if hardware_updates:
        values["hardware"] = HardwareMemorySnapshot(
            gpu_available_bytes=hardware_updates.get("gpu_available_bytes", 1_000),
            ram_available_bytes=hardware_updates.get("ram_available_bytes", 2_000),
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
    assert plan.ram_expert_slots == 18
    assert plan.cold_store_required is True
    assert plan.expected_bottleneck == "storage-warmup"


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


def test_digest_mismatch_fails_closed(tmp_path: Path) -> None:
    _, manifest = _package_fixture(tmp_path)
    expert_path = Path(manifest.root_dir) / manifest.experts[0].path
    expert_path.write_bytes(b"corrupt")

    with pytest.raises(ExpertIntegrityError, match="digest mismatch"):
        TieredExpertStore(manifest, ram_slots=1, hot_slots=0).acquire(
            0,
            torch.device("cpu"),
        )


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

    backend.restore_resident(layer)
    layer.set_execution_backend(None)

    assert sum(parameter.numel() for parameter in layer.parameters()) == resident_parameter_count
    torch.testing.assert_close(layer(x), expected, rtol=0, atol=0)


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
    plan = MoEResidencyPlanner().plan(
        _request(
            model_ref="model:nexusnet-lm-fixture",
            expert_count=6,
            gpu_available_bytes=1_500,
            ram_available_bytes=2_000,
        )
    )

    attachment = attach_tiered_moe_runtime(
        model,
        tmp_path,
        plan=plan,
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
        attach_tiered_moe_runtime(model, tmp_path, plan=blocked_plan)


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


def test_colibri_provenance_is_commit_pinned_and_excludes_server_integration() -> None:
    provenance = ColibriAssimilationProvenance()
    payload = provenance.as_dict()

    assert payload["repository"] == "https://github.com/JustVugg/colibri"
    assert payload["commit"] == "748787c3afa8ab336bb51bf616f212a04f209bba"
    assert payload["license"] == "Apache-2.0"
    assert "c/tier.h" in payload["eligible_attributed_sources"]
    assert "c/resource_plan.py" in payload["eligible_attributed_sources"]
    assert "c/openai_server.py" in payload["excluded_sources"]
