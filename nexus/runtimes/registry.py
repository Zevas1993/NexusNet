from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests

from ..config import NexusPaths, env_flag
from ..schemas import Message, RuntimeProfile
from ..storage import NexusStore
from .base import RuntimeAdapter, prompt_from_messages
from nexusnet.runtime.accelerator_packs.route_selection import (
    RouteEvidence,
    RouteRequest,
    RouteUnavailableError,
    RuntimeModeStore,
    VerifiedRouteSelector,
    normalize_execution_mode,
)


class MockRuntimeAdapter(RuntimeAdapter):
    runtime_name = "mock"
    backend_type = "deterministic"

    def health(self) -> dict[str, Any]:
        return {"available": True, "mode": "deterministic", "capabilities": {"text": True}, "metrics": {"latency_ms": 1}}

    def generate(self, *, prompt: str | None, messages: list[Message], model_id: str, expert: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        text = prompt_from_messages(messages, prompt).strip()
        preview = text[:240] if text else "No prompt provided."
        hint = f" expert={expert}" if expert else ""
        return f"[mock runtime{hint}] {preview}"


class OllamaRuntimeAdapter(RuntimeAdapter):
    runtime_name = "ollama"
    backend_type = "local-http"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.default_model = os.environ.get("OLLAMA_MODEL", "llama3.1")
        self.live = env_flag("LIVE_ENGINES", False)

    def health(self) -> dict[str, Any]:
        if not self.live:
            return {"available": False, "mode": "dry", "base_url": self.base_url}
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            response.raise_for_status()
            return {"available": True, "mode": "live", "base_url": self.base_url, "capabilities": {"text": True}}
        except Exception as exc:
            return {"available": False, "mode": "error", "base_url": self.base_url, "error": str(exc)}

    def generate(self, *, prompt: str | None, messages: list[Message], model_id: str, expert: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        text = prompt_from_messages(messages, prompt)
        if not self.live:
            return f"[ollama:dry] {text[:240]}"
        payload = {"model": model_id.split("/", 1)[-1] if "/" in model_id else self.default_model, "prompt": text}
        parameters = _verified_runtime_parameters(metadata)
        if parameters:
            payload["options"] = {
                "num_ctx": int(parameters.get("context_tokens", 4096)),
                "num_batch": int(parameters.get("runtime_batch_tokens", 256)),
                "num_gpu": int(parameters.get("gpu_layers", 0)),
            }
        response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "")


class OpenAICompatibleRuntimeAdapter(RuntimeAdapter):
    runtime_name = "openai-compatible"
    backend_type = "openai-http"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        base_url = os.environ.get("OPENAI_COMPAT_BASE_URL") or self.config.get("base_url") or ""
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ.get("OPENAI_COMPAT_API_KEY", self.config.get("api_key", ""))
        self.default_model = self.config.get("model", "default")

    def health(self) -> dict[str, Any]:
        if not self.base_url:
            return {"available": False, "mode": "unconfigured"}
        return {"available": True, "mode": "configured", "base_url": self.base_url, "capabilities": {"text": True, "structured_output": True}}

    def generate(self, *, prompt: str | None, messages: list[Message], model_id: str, expert: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        if not self.base_url:
            return f"[openai-compatible:dry] {prompt_from_messages(messages, prompt)[:240]}"
        payload_messages = [{"role": message.role, "content": message.content} for message in messages]
        if prompt and not payload_messages:
            payload_messages = [{"role": "user", "content": prompt}]
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"model": model_id.split("/", 1)[-1] if "/" in model_id else self.default_model, "messages": payload_messages}
        parameters = _verified_runtime_parameters(metadata)
        if parameters:
            payload["max_tokens"] = int(parameters.get("max_new_tokens", 256))
        response = requests.post(f"{self.base_url}/v1/chat/completions", json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")


class VLLMRuntimeAdapter(OpenAICompatibleRuntimeAdapter):
    runtime_name = "vllm"
    backend_type = "openai-http"


class LMStudioRuntimeAdapter(RuntimeAdapter):
    runtime_name = "lmstudio"
    backend_type = "openai-http"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        base_url = os.environ.get("LMSTUDIO_BASE") or self.config.get("base_url") or "http://127.0.0.1:1234"
        self.base_url = base_url.rstrip("/")
        self.default_model = self.config.get("model", "local")

    def health(self) -> dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=2)
            response.raise_for_status()
            return {"available": True, "mode": "live", "base_url": self.base_url, "capabilities": {"text": True}}
        except Exception as exc:
            return {"available": False, "mode": "unreachable", "base_url": self.base_url, "error": str(exc)}

    def generate(self, *, prompt: str | None, messages: list[Message], model_id: str, expert: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        payload = {
            "model": model_id.split("/", 1)[-1] if "/" in model_id else self.default_model,
            "prompt": prompt_from_messages(messages, prompt),
            "max_tokens": int(_verified_runtime_parameters(metadata).get("max_new_tokens", 256)),
        }
        response = requests.post(f"{self.base_url}/v1/completions", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("text", "")


class TransformersRuntimeAdapter(RuntimeAdapter):
    runtime_name = "transformers"
    backend_type = "local-python"

    def health(self) -> dict[str, Any]:
        try:
            from core.inference.transformers import available  # type: ignore

            ready = bool(available())
        except Exception:
            ready = False
        return {"available": ready, "mode": "live" if ready else "stub", "capabilities": {"text": True}}

    def generate(self, *, prompt: str | None, messages: list[Message], model_id: str, expert: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        try:
            from core.inference.transformers import generate  # type: ignore

            return generate(prompt_from_messages(messages, prompt))
        except Exception:
            return f"[transformers:stub] {prompt_from_messages(messages, prompt)[:240]}"


class LlamaCppRuntimeAdapter(RuntimeAdapter):
    runtime_name = "llama.cpp"
    backend_type = "local-python"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.model_path = Path(self.config.get("model_path", "models/tiny/tinyllama.gguf"))
        self._engine = None
        self._engine_plan_id: str | None = None

    def health(self) -> dict[str, Any]:
        ready = self.model_path.exists()
        return {"available": ready, "mode": "live" if ready else "stub", "model_path": str(self.model_path), "capabilities": {"text": True}}

    def generate(self, *, prompt: str | None, messages: list[Message], model_id: str, expert: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        if not self.model_path.exists():
            return f"[llama.cpp:stub] {prompt_from_messages(messages, prompt)[:240]}"
        selection = (metadata or {}).get("evolutionary_inference") or {}
        parameters = _verified_runtime_parameters(metadata)
        plan_id = str(selection.get("plan_id")) if parameters else "plan::runtime-default"
        if self._engine is None or self._engine_plan_id != plan_id:
            from core.engines.llamacpp_engine import LlamaCppEngine  # type: ignore

            self._engine = LlamaCppEngine(
                str(self.model_path),
                n_ctx=int(parameters.get("context_tokens", 4096)),
                n_gpu_layers=int(parameters.get("gpu_layers", 0)),
                n_batch=int(parameters.get("runtime_batch_tokens", 256)),
            )
            self._engine_plan_id = plan_id
        return self._engine.generate(
            prompt_from_messages(messages, prompt),
            max_new_tokens=int(parameters.get("max_new_tokens", 256)),
        )


class RuntimeRegistry:
    def __init__(self, paths: NexusPaths, store: NexusStore, runtime_configs: dict[str, Any]):
        self.paths = paths
        self.store = store
        self.runtime_configs = runtime_configs
        inference_cfg = runtime_configs.get("inference", {})
        self.adapters: dict[str, RuntimeAdapter] = {
            "mock": MockRuntimeAdapter({}),
            "ollama": OllamaRuntimeAdapter(inference_cfg.get("ollama", {})),
            "openai-compatible": OpenAICompatibleRuntimeAdapter(inference_cfg.get("openai_compatible", {})),
            "vllm": VLLMRuntimeAdapter({"base_url": inference_cfg.get("vllm", {}).get("endpoint", ""), "model": inference_cfg.get("vllm", {}).get("model", "default")}),
            "lmstudio": LMStudioRuntimeAdapter({"base_url": os.environ.get("LMSTUDIO_BASE", "http://127.0.0.1:1234"), "model": "local"}),
            "transformers": TransformersRuntimeAdapter(inference_cfg.get("transformers", {})),
            "llama.cpp": LlamaCppRuntimeAdapter(inference_cfg.get("llama_cpp", {})),
        }
        self._accelerator_adapters: dict[str, RuntimeAdapter] = {}
        self._accelerator_selector = VerifiedRouteSelector()
        self._runtime_mode_store = RuntimeModeStore(paths.state_dir / "runtime-acceleration-mode.json")

    def bootstrap(self) -> None:
        self.refresh_profiles()

    def refresh_profiles(self) -> list[RuntimeProfile]:
        profiles = []
        for runtime_name, adapter in self.adapters.items():
            profile = adapter.profile()
            profiles.append(profile)
            self.store.upsert_runtime_profile(runtime_name, profile.model_dump(mode="json"), profile.updated_at.isoformat())
        return profiles

    def list_profiles(self) -> list[RuntimeProfile]:
        stored = [RuntimeProfile.model_validate(payload) for payload in self.store.list_runtime_profiles()]
        return stored or self.refresh_profiles()

    def get_adapter(self, runtime_name: str) -> RuntimeAdapter:
        return self.adapters[runtime_name]

    def choose(self, preferred_runtime: str | None = None) -> RuntimeAdapter:
        if preferred_runtime and preferred_runtime in self.adapters:
            return self.adapters[preferred_runtime]
        for runtime_name in ["ollama", "llama.cpp", "transformers", "vllm", "lmstudio", "openai-compatible"]:
            profile = self.adapters[runtime_name].profile()
            if profile.available:
                return self.adapters[runtime_name]
        return self.adapters["mock"]

    def register_accelerator_route(self, evidence: RouteEvidence, adapter: RuntimeAdapter) -> None:
        if not evidence.verified or not evidence.healthy or not evidence.correctness_passed or evidence.quarantined:
            raise ValueError("accelerator routes require verified, healthy correctness evidence")
        self._accelerator_adapters[evidence.route_id] = adapter
        self._accelerator_selector.register(evidence)

    def choose_execution_route(self, mode: str | None = None) -> RuntimeAdapter:
        stored_mode = self._runtime_mode_store.status()["execution_mode"]
        execution_mode = normalize_execution_mode(mode or stored_mode)
        decision = self._accelerator_selector.select(RouteRequest(execution_mode=execution_mode))
        if not decision.available or decision.route_id is None:
            raise RouteUnavailableError(",".join(decision.reason_codes))
        return self._accelerator_adapters[decision.route_id]

    def set_execution_mode(self, requested_mode: str) -> dict[str, Any]:
        self._runtime_mode_store.set_mode(requested_mode)
        return self.accelerator_status()

    def accelerator_status(self) -> dict[str, Any]:
        mode = self._runtime_mode_store.status()
        decision = self._accelerator_selector.select(RouteRequest(execution_mode=mode["execution_mode"]))
        routes = [
            {
                "route_id": evidence.route_id,
                "pack_id": evidence.pack_id,
                "pack_version": evidence.pack_version,
                "device_node_id": evidence.device_node_id,
                "device_kind": evidence.device_kind,
                "execution_modes": [item.value for item in evidence.execution_modes],
                "verified": evidence.verified,
                "healthy": evidence.healthy,
                "correctness_passed": evidence.correctness_passed,
                "quarantined": evidence.quarantined,
                "calibration_score": evidence.calibration_score,
            }
            for evidence in self._accelerator_selector.routes()
        ]
        return {
            "status_label": "VERIFIED" if decision.available else "DEGRADED",
            "mode": mode,
            "routes": routes,
            "active_decision": decision.model_dump(mode="json"),
        }


def _verified_runtime_parameters(metadata: dict[str, Any] | None) -> dict[str, Any]:
    selection = (metadata or {}).get("evolutionary_inference")
    if not isinstance(selection, dict) or selection.get("verified") is not True:
        return {}
    parameters = selection.get("parameters")
    return dict(parameters) if isinstance(parameters, dict) else {}
