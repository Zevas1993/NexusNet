from __future__ import annotations

from pathlib import Path

from nexus.config import build_paths, ensure_paths
from nexus.models import ModelRegistry
from nexus.runtimes import RuntimeRegistry
from nexus.storage import NexusStore


def _write_inference_config(project_root: Path) -> None:
    config_dir = project_root / "runtime" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "inference.yaml").write_text(
        "\n".join(
            [
                "transformers:",
                "  model: TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                "llama_cpp:",
                f"  model_path: {project_root / 'models' / 'missing.gguf'}",
                "vllm:",
                "  endpoint: null",
                "openai_compatible:",
                "  model: gpt-4.1-mini",
            ]
        ),
        encoding="utf-8",
    )
    (project_root / ".nexus.json").write_text(
        '{"aliases":{"fast":"openai/gpt-4.1-mini"},"permissions":{"mode":"workspace-write"}}',
        encoding="utf-8",
    )


def test_model_registry_bootstraps_configured_runtime_candidates(tmp_path: Path):
    project_root = tmp_path / "workspace"
    _write_inference_config(project_root)
    paths = ensure_paths(build_paths(project_root))
    runtime_configs = {
        "inference": {
            "transformers": {"model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"},
            "llama_cpp": {"model_path": str(project_root / "models" / "missing.gguf")},
            "vllm": {"endpoint": None},
            "openai_compatible": {"model": "gpt-4.1-mini"},
        },
        "overrides": {"aliases": {"fast": "openai/gpt-4.1-mini"}},
    }
    store = NexusStore(paths)
    runtime_registry = RuntimeRegistry(paths, store, runtime_configs)
    runtime_registry.bootstrap()

    registry = ModelRegistry(store, runtime_registry, runtime_configs)
    registry.bootstrap()

    model_ids = {model.model_id for model in registry.list_models()}
    assert "mock/default" in model_ids
    assert "transformers/TinyLlama/TinyLlama-1.1B-Chat-v1.0" in model_ids
    assert f"llama.cpp/{project_root / 'models' / 'missing.gguf'}" in model_ids
    assert "vllm/default" in model_ids

    fast = registry.resolve_model("fast")
    assert fast.runtime_name == "openai-compatible"
    assert fast.metadata["alias"] == "fast"


def test_model_registry_resolves_dynamic_runtime_hints(tmp_path: Path):
    paths = ensure_paths(build_paths(tmp_path / "workspace"))
    store = NexusStore(paths)
    runtime_configs = {"inference": {}, "overrides": {}}
    runtime_registry = RuntimeRegistry(paths, store, runtime_configs)
    runtime_registry.bootstrap()
    registry = ModelRegistry(store, runtime_registry, runtime_configs)
    registry.bootstrap()

    transformed = registry.resolve_model("transformers/Custom/Research-Model")
    assert transformed.model_id == "transformers/Custom/Research-Model"
    assert transformed.runtime_name == "transformers"

    fallback = registry.resolve_model("unknown-model")
    assert fallback.model_id == "mock/default"
