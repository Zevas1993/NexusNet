from __future__ import annotations

from pathlib import Path

from nexus.models import ModelRegistry
from nexus.runtimes import RuntimeRegistry

from ..schemas import BenchmarkMatrixRecord
from .backends.llama_cpp_backend import LlamaCppBackend
from .backends.onnx_genai_backend import ONNXGenAIBackend
from .backends.vllm_backend import VLLMBackend
from .capabilities import llama_cpp_capability_card, onnx_genai_capability_card, vllm_capability_card
from .gguf.catalog import GGUFCatalog
from .hardware_scanner import HardwareScanner
from .adaptive_system_profiler import AdaptiveSystemProfiler
from .qes.backend_selector import QESBackendSelector
from .qes.aitune_provider import AITuneQESProvider
from .qes.benchmark_matrix import QESBenchmarkMatrix
from .qes.profile_registry import QESProfileRegistry
from .qes.runtime_metrics import QESRuntimeMetrics
from .quantization.torchao_provider import TorchAOQuantizationProvider


class BrainRuntimeRegistry:
    def __init__(self, *, runtime_registry: RuntimeRegistry, model_registry: ModelRegistry, runtime_configs: dict, config_dir: Path, artifacts_dir: Path):
        self.runtime_registry = runtime_registry
        self.model_registry = model_registry
        self.runtime_configs = runtime_configs
        inference_cfg = runtime_configs.get("inference", {})
        self.backends = {
            "vllm": VLLMBackend(inference_cfg.get("vllm", {})),
            "llama.cpp": LlamaCppBackend(inference_cfg.get("llama_cpp", {})),
            "onnx-genai": ONNXGenAIBackend(inference_cfg.get("onnx_genai", {})),
        }
        self.qes_profiles = QESProfileRegistry(config_dir)
        self.selector = QESBackendSelector(runtime_registry, model_registry, runtime_configs)
        self.metrics = QESRuntimeMetrics(runtime_registry)
        self.benchmark_matrix = QESBenchmarkMatrix(artifacts_dir)
        self.gguf_catalog = GGUFCatalog(inference_cfg)
        self.quantization_provider = TorchAOQuantizationProvider()
        self.hardware_scanner = HardwareScanner(runtime_configs)
        self.system_profiler = AdaptiveSystemProfiler(
            runtime_registry=runtime_registry,
            model_registry=model_registry,
            runtime_configs=runtime_configs,
            hardware_scanner=self.hardware_scanner,
        )
        self.aitune_provider = AITuneQESProvider(
            config_dir=config_dir,
            artifacts_dir=artifacts_dir,
            runtime_configs=runtime_configs,
        )

    def capability_cards(self) -> list[dict]:
        host_cards = []
        for profile in self.runtime_registry.list_profiles():
            if profile.runtime_name == "vllm":
                host_cards.append(vllm_capability_card().model_dump(mode="json"))
            elif profile.runtime_name == "llama.cpp":
                host_cards.append(llama_cpp_capability_card().model_dump(mode="json"))
            else:
                host_cards.append(
                    {
                        "runtime_name": profile.runtime_name,
                        "backend_type": profile.backend_type,
                        "status_label": "IMPLEMENTATION BRANCH",
                        "local_first": profile.runtime_name not in {"openai-compatible", "vllm"},
                        "supports_structured_output": bool(profile.capabilities.get("structured_output")),
                        "supports_streaming": False,
                        "supports_gguf": profile.runtime_name == "llama.cpp",
                        "supports_edge_portability": profile.runtime_name in {"llama.cpp", "transformers"},
                        "supports_tools": bool(profile.capabilities.get("tools")),
                        "notes": ["Host-runtime compatibility card."],
                    }
                )
        host_cards.append(onnx_genai_capability_card().model_dump(mode="json"))
        host_cards.append(self.aitune_provider.capability_card())
        return host_cards

    def summary(self, model_hint: str | None = None) -> dict:
        model = self.model_registry.resolve_model(model_hint)
        decision = self.selector.select(model.model_id)
        metrics = self.metrics.collect()
        profiler_summary = self.system_profiler.summary(model.model_id)
        dream_seed = {
            "seed_kind": "runtime-qes-shadow",
            "model_id": model.model_id,
            "selected_runtime_name": decision.selected_runtime_name,
            "metrics": metrics,
        }
        return {
            "status_label": "LOCKED CANON",
            "model_id": model.model_id,
            "capability_cards": self.capability_cards(),
            "selection_decision": decision.model_dump(mode="json"),
            "quantization_decision": profiler_summary["quantization_decision"],
            "qes_profiles": self.qes_profiles.summary(),
            "aitune": self.aitune_provider.summary(model),
            "gguf_catalog": self.gguf_catalog.entries(),
            "runtime_metrics": metrics,
            "device_profile": profiler_summary["device_profile"],
            "token_budget_profile": profiler_summary["token_budget_profile"],
            "candidates": profiler_summary["candidates"],
            "dream_seed": dream_seed,
        }

    def core_execution_plan(self, *, model_hint: str | None = None, requested_runtime: str | None = None) -> dict:
        decision = self.selector.select(model_hint)
        return self.system_profiler.execution_plan(
            model_hint=model_hint,
            requested_runtime=requested_runtime,
            selection_decision=decision.model_dump(mode="json"),
        )

    def benchmark(self, model_hint: str | None = None) -> dict:
        model = self.model_registry.resolve_model(model_hint)
        records = []
        for metric in self.metrics.collect():
            records.append(
                BenchmarkMatrixRecord(
                    model_id=model.model_id,
                    runtime_name=metric["runtime_name"],
                    metrics={
                        "latency_ms": metric.get("metrics", {}).get("latency_ms", 0),
                        "ttft_ms": metric.get("ttft_ms", 0),
                        "throughput_tokens_per_s": metric.get("throughput_tokens_per_s", 0),
                        "failure_rate": metric.get("failure_rate", 0.0),
                    },
                    lineage="dream-derived" if metric["runtime_name"] == "mock" else "live-derived",
                )
            )
        aitune = self.aitune_provider.benchmark(model)
        for record in aitune.get("records", []):
            records.append(BenchmarkMatrixRecord.model_validate(record))
        artifact_path = self.benchmark_matrix.write(records)
        return {
            "status_label": "LOCKED CANON",
            "artifact_path": artifact_path,
            "records": [record.model_dump(mode="json") for record in records],
            "aitune": aitune,
        }
