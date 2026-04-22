from __future__ import annotations

from pathlib import Path

from nexus.services import build_services
from nexusnet.runtime.qes.aitune_adapter import AITuneAdapter
from tests.test_nexus_phase1_foundation import make_project, _write_yaml


def test_aitune_summary_is_gracefully_unavailable_in_default_dev_fixture(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    summary = services.brain_runtime_registry.summary("transformers/TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    aitune = summary["aitune"]

    assert aitune["status_label"] == "EXPLORATORY / PROTOTYPE"
    assert aitune["capability"]["available"] is False
    assert aitune["capability"]["provider_health"] in {"disabled", "incompatible"}
    assert "aitune" in {card["runtime_name"] for card in summary["capability_cards"]}


def test_aitune_applicability_is_bounded_to_pytorch_native_lanes(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))
    provider = services.brain_runtime_registry.aitune_provider

    transformers_model = services.model_registry.resolve_model("transformers/TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    llama_model = services.model_registry.resolve_model(f"llama.cpp/{project_root / 'models' / 'missing.gguf'}")
    vllm_model = services.model_registry.resolve_model("vllm/default")

    assert provider.applicability(transformers_model)["eligible"] is True
    assert provider.applicability(transformers_model)["target_lane"] == "pytorch-native-transformers"
    assert provider.applicability(llama_model)["eligible"] is False
    assert provider.applicability(vllm_model)["eligible"] is False


def test_aitune_benchmark_writes_skip_artifacts_without_breaking_qes(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    benchmark = services.brain_runtime_registry.benchmark("transformers/TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    aitune = benchmark["aitune"]

    assert aitune["status"] == "skipped"
    assert aitune["records"] == []
    assert Path(aitune["artifacts"]["compatibility"]).exists()
    assert Path(aitune["artifacts"]["benchmark"]).exists()
    assert Path(benchmark["artifact_path"]).exists()


def test_aitune_adapter_can_normalize_completed_result_with_fake_module(tmp_path: Path, monkeypatch):
    adapter = AITuneAdapter(config={"allow_live_invoke": True}, artifacts_dir=tmp_path)

    class FakeAITune:
        @staticmethod
        def autotune(model_id=None, module_kind=None, backends=None, artifacts_dir=None):
            return {
                "backend": (backends or ["torch-inductor"])[0],
                "metrics": {
                    "latency_ms": 22.5,
                    "throughput_tokens_per_s": 44.0,
                    "correctness": 0.995,
                },
                "artifact_path": str(Path(artifacts_dir) / "compiled.engine"),
            }

    monkeypatch.setattr(adapter, "_load_module", lambda: FakeAITune)
    result = adapter.tune(
        capability={"available": True},
        model_id="transformers/fake",
        module_kind="pytorch-native-transformers",
        backend_preferences=["torch-inductor", "torchao"],
        work_dir=tmp_path / "aitune-work",
    )

    assert result["status"] == "completed"
    assert result["selected_backend"] == "torch-inductor"
    assert result["metrics"]["correctness"] == 0.995
    assert result["artifact_lineage"]["surface"] == "autotune"
