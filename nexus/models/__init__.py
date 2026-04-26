from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..runtimes import RuntimeRegistry
from ..schemas import CapabilityCard, ModelRegistration
from ..storage import NexusStore


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ModelRegistry:
    """Registry-backed model catalog used by the platform shell and brain core."""

    def __init__(
        self,
        store: NexusStore,
        runtime_registry: RuntimeRegistry,
        runtime_configs: dict[str, Any] | None = None,
    ):
        self.store = store
        self.runtime_registry = runtime_registry
        self.runtime_configs = runtime_configs or {}
        self.inference_config = self.runtime_configs.get("inference", {}) or {}
        self.overrides = self.runtime_configs.get("overrides", {}) or {}

    def bootstrap(self) -> None:
        for registration in self._default_registrations():
            self._upsert(registration)

    def list_models(self) -> list[ModelRegistration]:
        stored = [ModelRegistration.model_validate(payload) for payload in self.store.list_models()]
        return stored or self._default_registrations()

    def resolve_model(self, model_hint: str | None = None, expert: str | None = None) -> ModelRegistration:
        hint = (model_hint or "").strip()
        if not hint:
            return self._with_resolution_metadata(self._by_id("mock/default"), model_hint, expert)

        alias_target = self._aliases().get(hint)
        if alias_target:
            resolved = self._resolve_alias(alias=hint, target=alias_target)
            return self._with_resolution_metadata(resolved, model_hint, expert, alias=hint, alias_target=alias_target)

        for registration in self.list_models():
            if registration.model_id == hint:
                return self._with_resolution_metadata(registration, model_hint, expert)

        dynamic = self._dynamic_registration(hint)
        if dynamic is not None:
            return self._with_resolution_metadata(dynamic, model_hint, expert)

        fallback = self._by_id("mock/default")
        return self._with_resolution_metadata(fallback, model_hint, expert, fallback_reason="unknown_model_hint")

    def summary(self) -> dict[str, Any]:
        models = self.list_models()
        return {
            "model_count": len(models),
            "models": [model.model_dump(mode="json") for model in models],
            "aliases": self._aliases(),
            "runtimes": sorted({model.runtime_name for model in models}),
        }

    def _default_registrations(self) -> list[ModelRegistration]:
        inference = self.inference_config
        transformers_model = str(
            (inference.get("transformers") or {}).get("model")
            or "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        )
        llama_model_path = str(
            (inference.get("llama_cpp") or {}).get("model_path")
            or Path("models") / "tiny" / "tinyllama.gguf"
        )
        vllm_model = str((inference.get("vllm") or {}).get("model") or "default")
        openai_model = str((inference.get("openai_compatible") or {}).get("model") or "gpt-4.1-mini")
        lmstudio_model = str((inference.get("lmstudio") or {}).get("model") or "local")

        return [
            self._registration(
                model_id="mock/default",
                runtime_name="mock",
                display_name="Deterministic Mock Runtime",
                model_family="mock",
                available=True,
                tags=["baseline", "deterministic", "test-safe"],
                context_window=8192,
                preferred_tasks=["smoke", "tests", "fallback"],
                known_weaknesses=["Not a real language model; deterministic echo only."],
            ),
            self._registration(
                model_id=f"transformers/{transformers_model}",
                runtime_name="transformers",
                display_name=f"Transformers {transformers_model}",
                model_family="transformers",
                available=True,
                tags=["local", "candidate", "pytorch-native"],
                context_window=4096,
                preferred_tasks=["local-inference", "experiments"],
                known_weaknesses=["Requires local Python model dependencies for live execution."],
            ),
            self._registration(
                model_id=f"llama.cpp/{llama_model_path}",
                runtime_name="llama.cpp",
                display_name=f"llama.cpp {Path(llama_model_path).name}",
                model_family="gguf",
                available=True,
                tags=["local", "gguf", "candidate"],
                context_window=4096,
                quantization=["q4", "q5", "q8"],
                preferred_tasks=["constrained-device", "offline"],
                known_weaknesses=["Requires the configured GGUF path to exist for live execution."],
            ),
            self._registration(
                model_id=f"vllm/{vllm_model}",
                runtime_name="vllm",
                display_name=f"vLLM {vllm_model}",
                model_family="openai-compatible-serving",
                available=True,
                tags=["serving", "candidate", "long-context"],
                context_window=32768,
                supports_tools=True,
                supports_structured_output=True,
                preferred_tasks=["gpu-serving", "batch-inference"],
                known_weaknesses=["Requires a configured vLLM endpoint before live execution."],
            ),
            self._registration(
                model_id=f"openai-compatible/{openai_model}",
                runtime_name="openai-compatible",
                display_name=f"OpenAI-compatible {openai_model}",
                model_family="openai-compatible",
                available=True,
                tags=["cloud-or-local-http", "alias-target", "teacher-capable"],
                context_window=128000,
                supports_tools=True,
                supports_structured_output=True,
                preferred_tasks=["fast-path", "structured-output", "teacher"],
                known_weaknesses=["Requires configured base URL for live external execution."],
            ),
            self._registration(
                model_id=f"lmstudio/{lmstudio_model}",
                runtime_name="lmstudio",
                display_name=f"LM Studio {lmstudio_model}",
                model_family="openai-compatible-local",
                available=True,
                tags=["local-http", "candidate"],
                context_window=8192,
                preferred_tasks=["desktop-local", "manual-runtime"],
                known_weaknesses=["Requires LM Studio server to be reachable."],
            ),
        ]

    def _registration(
        self,
        *,
        model_id: str,
        runtime_name: str,
        display_name: str,
        model_family: str,
        available: bool,
        tags: list[str],
        context_window: int,
        preferred_tasks: list[str],
        known_weaknesses: list[str],
        quantization: list[str] | None = None,
        supports_tools: bool = False,
        supports_structured_output: bool = False,
    ) -> ModelRegistration:
        now = _utcnow()
        capability_card = CapabilityCard(
            model_id=model_id,
            model_family=model_family,
            runtime_name=runtime_name,
            context_window=context_window,
            supports_tools=supports_tools,
            supports_structured_output=supports_structured_output,
            quantization=quantization or [],
            preferred_tasks=preferred_tasks,
            known_weaknesses=known_weaknesses,
        )
        return ModelRegistration(
            model_id=model_id,
            runtime_name=runtime_name,
            display_name=display_name,
            default_expert=None,
            available=available,
            tags=tags,
            metadata={
                "source": "model-registry-bootstrap",
                "runtime_profile_known": runtime_name in self.runtime_registry.adapters,
                "status": "registered_candidate",
            },
            capability_card=capability_card,
            created_at=now,
            updated_at=now,
        )

    def _upsert(self, registration: ModelRegistration) -> None:
        payload = registration.model_dump(mode="json")
        self.store.upsert_model(
            registration.model_id,
            registration.runtime_name,
            payload,
            registration.created_at.isoformat(),
            registration.updated_at.isoformat(),
        )

    def _by_id(self, model_id: str) -> ModelRegistration:
        for registration in self.list_models():
            if registration.model_id == model_id:
                return registration
        for registration in self._default_registrations():
            if registration.model_id == model_id:
                return registration
        raise KeyError(model_id)

    def _aliases(self) -> dict[str, str]:
        aliases = self.overrides.get("aliases", {}) if isinstance(self.overrides, dict) else {}
        return {str(key): str(value) for key, value in aliases.items()}

    def _resolve_alias(self, *, alias: str, target: str) -> ModelRegistration:
        target = target.strip()
        direct = self._find_exact(target)
        if direct is not None:
            return direct
        if target.startswith("openai/"):
            return self._dynamic_registration(f"openai-compatible/{target.split('/', 1)[1]}", alias=alias) or self._by_id("mock/default")
        if target.startswith("openai-compatible/"):
            return self._dynamic_registration(target, alias=alias) or self._by_id("mock/default")
        dynamic = self._dynamic_registration(target, alias=alias)
        return dynamic or self._by_id("mock/default")

    def _find_exact(self, model_id: str) -> ModelRegistration | None:
        for registration in self.list_models():
            if registration.model_id == model_id:
                return registration
        return None

    def _dynamic_registration(self, hint: str, *, alias: str | None = None) -> ModelRegistration | None:
        runtime_name, _, model_name = hint.partition("/")
        runtime_aliases = {
            "openai": "openai-compatible",
            "openai-compatible": "openai-compatible",
            "vllm": "vllm",
            "transformers": "transformers",
            "llama.cpp": "llama.cpp",
            "lmstudio": "lmstudio",
            "mock": "mock",
            "ollama": "ollama",
        }
        resolved_runtime = runtime_aliases.get(runtime_name)
        if not resolved_runtime or not model_name:
            return None
        model_id = hint if runtime_name != "openai" else f"openai-compatible/{model_name}"
        registration = self._registration(
            model_id=model_id,
            runtime_name=resolved_runtime,
            display_name=f"{resolved_runtime} {model_name}",
            model_family=resolved_runtime,
            available=True,
            tags=["dynamic", "resolved-from-hint"],
            context_window=128000 if resolved_runtime == "openai-compatible" else 8192,
            supports_tools=resolved_runtime in {"openai-compatible", "vllm"},
            supports_structured_output=resolved_runtime in {"openai-compatible", "vllm"},
            preferred_tasks=["dynamic-resolution"],
            known_weaknesses=["Dynamically resolved hints still require runtime health checks before live use."],
        )
        registration.metadata.update({"dynamic": True, "alias": alias} if alias else {"dynamic": True})
        return registration

    def _with_resolution_metadata(
        self,
        registration: ModelRegistration,
        model_hint: str | None,
        expert: str | None,
        *,
        alias: str | None = None,
        alias_target: str | None = None,
        fallback_reason: str | None = None,
    ) -> ModelRegistration:
        cloned = registration.model_copy(deep=True)
        cloned.metadata.update(
            {
                "requested_hint": model_hint,
                "requested_expert": expert,
            }
        )
        if alias is not None:
            cloned.metadata["alias"] = alias
        if alias_target is not None:
            cloned.metadata["alias_target"] = alias_target
        if fallback_reason is not None:
            cloned.metadata["fallback_reason"] = fallback_reason
        return cloned


__all__ = ["ModelRegistry"]
