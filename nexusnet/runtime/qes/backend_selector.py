from __future__ import annotations

from nexus.config import env_flag
from nexus.models import ModelRegistry
from nexus.runtimes import RuntimeRegistry

from ...schemas import BackendSelectionDecision


class QESBackendSelector:
    def __init__(self, runtime_registry: RuntimeRegistry, model_registry: ModelRegistry, runtime_configs: dict):
        self.runtime_registry = runtime_registry
        self.model_registry = model_registry
        self.runtime_configs = runtime_configs

    def select(self, model_hint: str | None = None) -> BackendSelectionDecision:
        model = self.model_registry.resolve_model(model_hint)
        inference_cfg = self.runtime_configs.get("inference", {})
        policy = inference_cfg.get("policy", {}) or {}
        prefer_local = bool(policy.get("prefer_local", True))
        product_mode = env_flag("NEXUSNET_PRODUCT_MODE", bool(policy.get("product_mode", False)))
        allow_mock = env_flag("NEXUSNET_ALLOW_MOCK_RUNTIME", bool(policy.get("allow_mock_runtime", not product_mode)))
        preferred = model.runtime_name
        fallback_order = ["llama.cpp", "onnx-genai", "transformers", "ollama", "vllm", "openai-compatible", "mock"]
        if not prefer_local:
            fallback_order = ["vllm", "openai-compatible", "ollama", "llama.cpp", "onnx-genai", "transformers", "mock"]
        fallback_order = [
            runtime_name
            for runtime_name in fallback_order
            if runtime_name in self.runtime_registry.adapters and (runtime_name != "mock" or allow_mock)
        ]
        selected = preferred
        try:
            if not self.runtime_registry.get_adapter(preferred).profile().available:
                selected = next(
                    (
                    runtime_name
                    for runtime_name in fallback_order
                        if self.runtime_registry.get_adapter(runtime_name).profile().available
                    ),
                    preferred,
                )
        except Exception:
            selected = "mock" if allow_mock and "mock" in self.runtime_registry.adapters else preferred
        return BackendSelectionDecision(
            model_id=model.model_id,
            selected_runtime_name=selected,
            fallback_runtime_names=fallback_order,
            rationale=(
                "QES-compatible backend selection tied to local-first runtime profiling, "
                "registered fallback lanes, and product-mode mock policy."
            ),
        )
