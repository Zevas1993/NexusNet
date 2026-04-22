from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests

from ..config import NexusPaths, env_flag
from ..schemas import Message, RuntimeProfile
from ..storage import NexusStore
from .base import RuntimeAdapter, prompt_from_messages


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
            "max_tokens": 256,
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

    def health(self) -> dict[str, Any]:
        ready = self.model_path.exists()
        return {"available": ready, "mode": "live" if ready else "stub", "model_path": str(self.model_path), "capabilities": {"text": True}}

    def generate(self, *, prompt: str | None, messages: list[Message], model_id: str, expert: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        if not self.model_path.exists():
            return f"[llama.cpp:stub] {prompt_from_messages(messages, prompt)[:240]}"
        if self._engine is None:
            from core.engines.llamacpp_engine import LlamaCppEngine  # type: ignore

            self._engine = LlamaCppEngine(str(self.model_path))
        return self._engine.generate(prompt_from_messages(messages, prompt))


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
