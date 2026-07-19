from __future__ import annotations

from hashlib import sha256
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import requests

from nexusnet.runtime.evolutionary_inference.primitives import InferencePrimitiveRegistry
from nexusnet.runtime.evolutionary_inference.schemas import InferenceMethodRecord
from nexusnet.runtime.scorecards import RuntimeScorecardService

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
from nexusnet.runtime.accelerator_packs.calibration import CalibrationLedger, CalibrationRecord
from nexusnet.runtime.accelerator_packs.lifecycle import PackCircuitBreaker
from nexusnet.runtime.accelerator_packs.contracts import WorkloadKind


class MockRuntimeAdapter(RuntimeAdapter):
    runtime_name = "mock"
    backend_type = "deterministic"

    def health(self) -> dict[str, Any]:
        return {"available": True, "mode": "deterministic", "capabilities": {"text": True}, "metrics": {"latency_ms": 1}}

    def generate(self, *, prompt: str | None, messages: list[Message], model_id: str, expert: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        self.verified_runtime_parameters(metadata)
        text = prompt_from_messages(messages, prompt).strip()
        preview = text[:240] if text else "No prompt provided."
        hint = f" expert={expert}" if expert else ""
        return f"[mock runtime{hint}] {preview}"


class OllamaRuntimeAdapter(RuntimeAdapter):
    runtime_name = "ollama"
    backend_type = "local-http"
    supported_runtime_controls = frozenset(
        {
            "context_tokens",
            "gpu_layers",
            "main_gpu",
            "max_new_tokens",
            "runtime_batch_tokens",
            "threads",
        }
    )
    observable_runtime_controls = supported_runtime_controls

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
        parameters = self.verified_runtime_parameters(metadata)
        text = prompt_from_messages(messages, prompt)
        if not self.live:
            return f"[ollama:dry] {text[:240]}"
        payload = {"model": model_id.split("/", 1)[-1] if "/" in model_id else self.default_model, "prompt": text}
        if parameters:
            payload["options"] = {
                "num_ctx": int(parameters.get("context_tokens", 4096)),
                "num_batch": int(parameters.get("runtime_batch_tokens", 256)),
                "num_gpu": int(parameters.get("gpu_layers", 0)),
                "num_predict": int(parameters.get("max_new_tokens", 256)),
            }
            if "main_gpu" in parameters:
                payload["options"]["main_gpu"] = int(parameters["main_gpu"])
            if "threads" in parameters:
                payload["options"]["num_thread"] = int(parameters["threads"])
        response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "")


class OpenAICompatibleRuntimeAdapter(RuntimeAdapter):
    runtime_name = "openai-compatible"
    backend_type = "openai-http"
    supported_runtime_controls = frozenset({"max_new_tokens"})
    observable_runtime_controls = supported_runtime_controls

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
        parameters = self.verified_runtime_parameters(metadata)
        if not self.base_url:
            return f"[openai-compatible:dry] {prompt_from_messages(messages, prompt)[:240]}"
        payload_messages = [{"role": message.role, "content": message.content} for message in messages]
        if prompt and not payload_messages:
            payload_messages = [{"role": "user", "content": prompt}]
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"model": model_id.split("/", 1)[-1] if "/" in model_id else self.default_model, "messages": payload_messages}
        if parameters:
            payload["max_tokens"] = int(parameters.get("max_new_tokens", 256))
        response = requests.post(f"{self.base_url}/v1/chat/completions", json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")


class VLLMRuntimeAdapter(OpenAICompatibleRuntimeAdapter):
    runtime_name = "vllm"
    backend_type = "openai-http"


class TGIRuntimeAdapter(RuntimeAdapter):
    runtime_name = "tgi"
    backend_type = "text-generation-inference-http"
    supported_runtime_controls = frozenset({"max_new_tokens"})
    observable_runtime_controls = supported_runtime_controls

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.base_url = str(
            os.environ.get("TGI_BASE_URL")
            or self.config.get("endpoint")
            or "http://127.0.0.1:8080"
        ).rstrip("/")
        self.live = env_flag("LIVE_ENGINES", False)

    def health(self) -> dict[str, Any]:
        if not self.live:
            return {"available": False, "mode": "dry", "base_url": self.base_url}
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            response.raise_for_status()
            return {
                "available": True,
                "mode": "live",
                "base_url": self.base_url,
                "capabilities": {"text": True},
            }
        except Exception as exc:
            return {
                "available": False,
                "mode": "error",
                "base_url": self.base_url,
                "error": str(exc),
            }

    def generate(self, *, prompt: str | None, messages: list[Message], model_id: str, expert: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        parameters = self.verified_runtime_parameters(metadata)
        if not self.live:
            raise RuntimeError("TGI runtime is not live")
        payload = {
            "inputs": prompt_from_messages(messages, prompt),
            "parameters": {"max_new_tokens": int(parameters.get("max_new_tokens", 256))},
        }
        response = requests.post(f"{self.base_url}/generate", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            data = data[0] if data else {}
        return str(data.get("generated_text") or "") if isinstance(data, dict) else ""


class LMStudioRuntimeAdapter(RuntimeAdapter):
    runtime_name = "lmstudio"
    backend_type = "openai-http"
    supported_runtime_controls = frozenset({"max_new_tokens"})
    observable_runtime_controls = supported_runtime_controls

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
        parameters = self.verified_runtime_parameters(metadata)
        payload = {
            "model": model_id.split("/", 1)[-1] if "/" in model_id else self.default_model,
            "prompt": prompt_from_messages(messages, prompt),
            "max_tokens": int(parameters.get("max_new_tokens", 256)),
        }
        response = requests.post(f"{self.base_url}/v1/completions", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("text", "")


class TransformersRuntimeAdapter(RuntimeAdapter):
    runtime_name = "transformers"
    backend_type = "local-python"
    supported_runtime_controls = frozenset({"max_new_tokens", "temperature", "top_p"})
    observable_runtime_controls = supported_runtime_controls

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.default_model = str(self.config.get("model_id") or self.config.get("model") or "")
        self.device = str(self.config.get("device") or "cpu")
        self._engines: dict[str, Any] = {}

    def health(self) -> dict[str, Any]:
        if not self.default_model:
            return {"available": False, "mode": "unconfigured", "capabilities": {"text": True}}
        try:
            from core.inference.transformers import available  # type: ignore

            ready = bool(available())
        except Exception as exc:
            return {"available": False, "mode": "dependency-unavailable", "error": str(exc), "capabilities": {"text": True}}
        return {
            "available": ready,
            "mode": "ready" if ready else "dependency-unavailable",
            "model_id": self.default_model,
            "device": self.device,
            "capabilities": {"text": True},
        }

    def generate(self, *, prompt: str | None, messages: list[Message], model_id: str, expert: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        parameters = self.verified_runtime_parameters(metadata)
        selected_model = (model_id.split("/", 1)[-1] if model_id else "") or self.default_model
        if not selected_model:
            raise RuntimeError("Transformers runtime requires model_id configuration")
        from core.engines.transformers_engine import TransformersEngine  # type: ignore

        engine = self._engines.get(selected_model)
        if engine is None:
            engine = TransformersEngine(selected_model, device=self.device)
            self._engines[selected_model] = engine
        return engine.generate(
            prompt_from_messages(messages, prompt),
            max_new_tokens=int(parameters.get("max_new_tokens", 256)),
            temperature=float(parameters.get("temperature", 0.7)),
            top_p=float(parameters.get("top_p", 0.95)),
        )


class LlamaCppRuntimeAdapter(RuntimeAdapter):
    runtime_name = "llama.cpp"
    backend_type = "local-python"
    supported_runtime_controls = frozenset(
        {
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
        }
    )
    observable_runtime_controls = supported_runtime_controls

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.model_path = Path(self.config.get("model_path", "models/tiny/tinyllama.gguf"))
        self._engine = None
        self._engine_plan_id: str | None = None

    def health(self) -> dict[str, Any]:
        ready = self.model_path.exists()
        return {"available": ready, "mode": "ready" if ready else "missing-model", "model_path": str(self.model_path), "capabilities": {"text": True}}

    def generate(self, *, prompt: str | None, messages: list[Message], model_id: str, expert: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        selection = (metadata or {}).get("evolutionary_inference") or {}
        parameters = self.verified_runtime_parameters(metadata)
        if not self.model_path.exists():
            raise FileNotFoundError(f"llama.cpp model is missing: {self.model_path}")
        plan_id = str(selection.get("plan_id")) if parameters else "plan::runtime-default"
        if self._engine is None or self._engine_plan_id != plan_id:
            from core.engines.llamacpp_engine import LlamaCppEngine  # type: ignore

            self._engine = LlamaCppEngine(
                str(self.model_path),
                n_ctx=int(parameters.get("context_tokens", 4096)),
                n_gpu_layers=int(parameters.get("gpu_layers", 0)),
                n_batch=int(parameters.get("runtime_batch_tokens", 256)),
                n_threads=int(parameters["threads"]) if "threads" in parameters else None,
                n_threads_batch=(
                    int(parameters["batch_threads"]) if "batch_threads" in parameters else None
                ),
                cache_type_k=parameters.get("cache_type_k"),
                cache_type_v=parameters.get("cache_type_v"),
                flash_attn=bool(parameters.get("flash_attention", False)),
                offload_kqv=bool(parameters.get("offload_kqv", True)),
                main_gpu=int(parameters.get("main_gpu", 0)),
                split_mode=parameters.get("split_mode", "layer"),
                tensor_split=parameters.get("tensor_split"),
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
            "tgi": TGIRuntimeAdapter(inference_cfg.get("tgi", {})),
            "lmstudio": LMStudioRuntimeAdapter({"base_url": os.environ.get("LMSTUDIO_BASE", "http://127.0.0.1:1234"), "model": "local"}),
            "transformers": TransformersRuntimeAdapter(inference_cfg.get("transformers", {})),
            "llama.cpp": LlamaCppRuntimeAdapter(inference_cfg.get("llama_cpp", {})),
        }
        self._accelerator_adapters: dict[str, RuntimeAdapter] = {}
        self._accelerator_selector = VerifiedRouteSelector()
        self._runtime_mode_store = RuntimeModeStore(paths.state_dir / "runtime-acceleration-mode.json")
        self._accelerator_calibration = CalibrationLedger(paths.state_dir / "runtime-acceleration-calibration.json")
        self._accelerator_circuits = PackCircuitBreaker(
            paths.state_dir / "runtime-acceleration-circuits.json",
            failure_threshold=3,
        )

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

    def runtime_capability_profiles(self):
        return [self.adapters[name].runtime_capability_profile() for name in sorted(self.adapters)]

    def inference_method_records(self):
        records = {
            record.method_id: record
            for record in (
                self.adapters[name].inference_method_record() for name in sorted(self.adapters)
            )
        }
        declared_providers = [
            *RuntimeScorecardService.PROVIDERS,
            {
                "provider_id": "onnx-genai",
                "name": "ONNX Runtime GenAI",
                "mode": "local",
                "cloud_local_mode": "local",
                "openai_compatible": False,
                "tool_calling": False,
                "hardware_tier_fit": [
                    "tier_1_constrained_edge",
                    "tier_2_mainstream_local",
                    "tier_3_premium_local",
                ],
                "formats": ["onnx"],
                "quantization": "int8_int4_provider_dependent",
            },
        ]
        runtime_aliases = {"llama-cpp": "llama.cpp", "lm-studio": "lmstudio"}
        for provider in declared_providers:
            runtime_name = runtime_aliases.get(provider["provider_id"], provider["provider_id"])
            method_id = f"runtime::{runtime_name}"
            claimed_capabilities = [f"mode::{provider['mode']}"]
            if provider["openai_compatible"]:
                claimed_capabilities.append("openai-compatible")
            if provider["tool_calling"]:
                claimed_capabilities.append("tool-calling")
            existing = records.get(method_id)
            if existing is not None:
                records[method_id] = existing.model_copy(
                    update={
                        "claimed_capabilities": sorted(
                            set(existing.claimed_capabilities) | set(claimed_capabilities)
                        ),
                        "supported_formats": sorted(
                            set(existing.supported_formats) | set(provider["formats"])
                        ),
                        "supported_precisions": sorted(
                            set(existing.supported_precisions) | {provider["quantization"]}
                        ),
                        "supported_hardware": sorted(
                            set(existing.supported_hardware) | set(provider["hardware_tier_fit"])
                        ),
                    }
                )
                continue
            source_payload = json.dumps(provider, sort_keys=True, separators=(",", ":"))
            records[method_id] = InferenceMethodRecord(
                method_id=method_id,
                version="runtime-scorecard-v1",
                source_kind="external-engine",
                source_digest=f"sha256:{hashlib.sha256(source_payload.encode('utf-8')).hexdigest()}",
                rights={
                    "inference": "unknown",
                    "evaluation": "unknown",
                    "derivative": "unknown",
                    "redistribution": "unknown",
                },
                claimed_capabilities=sorted(claimed_capabilities),
                supported_formats=sorted(provider["formats"]),
                supported_precisions=[provider["quantization"]],
                supported_hardware=sorted(provider["hardware_tier_fit"]),
                maturity="researched",
                assimilation_paths=["whole-engine", "primitive"],
            )
        return [
            *(records[method_id] for method_id in sorted(records)),
            *InferencePrimitiveRegistry.default().method_records(),
        ]

    def get_adapter(self, runtime_name: str) -> RuntimeAdapter:
        return self.adapters[runtime_name]

    def choose(self, preferred_runtime: str | None = None) -> RuntimeAdapter:
        if preferred_runtime and preferred_runtime in self.adapters:
            return self.adapters[preferred_runtime]
        for runtime_name in ["ollama", "llama.cpp", "transformers", "vllm", "tgi", "lmstudio", "openai-compatible"]:
            profile = self.adapters[runtime_name].profile()
            if profile.available:
                return self.adapters[runtime_name]
        return self.adapters["mock"]
    def register_accelerator_route(self, evidence: RouteEvidence, adapter: RuntimeAdapter) -> None:
        if not evidence.verified or not evidence.healthy or not evidence.correctness_passed or evidence.quarantined:
            raise ValueError("accelerator routes require verified, healthy correctness evidence")
        if evidence.calibration_key is not None:
            record = self._accelerator_calibration.verified(evidence.calibration_key)
            if evidence.calibration_verified and record is None:
                raise ValueError("accelerator calibration must exist in the exact-key ledger")
            if record is not None:
                evidence = evidence.model_copy(
                    update={
                        "calibration_verified": True,
                        "calibration_outcome": "passed",
                        "calibration_score": record.score,
                        "evidence_refs": tuple(dict.fromkeys((*evidence.evidence_refs, *record.evidence_refs))),
                    }
                )
        self._accelerator_adapters[evidence.route_id] = adapter
        self._accelerator_selector.register(evidence)

    def record_accelerator_calibration(self, record: CalibrationRecord) -> CalibrationRecord:
        stored = self._accelerator_calibration.put(record)
        self._accelerator_selector.reconcile_calibration(stored)
        return stored

    def record_accelerator_failure(self, route_id: str, *, reason_code: str) -> dict[str, Any]:
        evidence = next((item for item in self._accelerator_selector.routes() if item.route_id == route_id), None)
        if evidence is None or evidence.calibration_key is None:
            raise ValueError("accelerator failure requires an exact calibration key")
        state = self._accelerator_circuits.record_failure(evidence.calibration_key, reason_code=reason_code)
        quarantined_routes: tuple[str, ...] = ()
        if state.opened:
            quarantined_routes = self._accelerator_selector.quarantine(
                pack_id=evidence.pack_id,
                pack_version=evidence.pack_version,
            )
        return {
            "route_id": route_id,
            "opened": state.opened,
            "failure_count": state.failure_count,
            "quarantined_routes": list(quarantined_routes),
        }

    def choose_execution_route(
        self,
        mode: str | None = None,
        *,
        model_hash: str | None = None,
        workload_profile_hash: str | None = None,
        workload: str | WorkloadKind = WorkloadKind.LLM_GENERATE,
    ) -> RuntimeAdapter:
        stored_mode = self._runtime_mode_store.status()["execution_mode"]
        execution_mode = normalize_execution_mode(mode or stored_mode)
        decision = self._accelerator_selector.select(
            RouteRequest(
                execution_mode=execution_mode,
                workload=workload,
                model_hash=model_hash,
                workload_profile_hash=workload_profile_hash,
            )
        )
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
                "device_ref": f"device::{sha256(evidence.device_node_id.encode('utf-8')).hexdigest()[:32]}",
                "device_kind": evidence.device_kind,
                "execution_modes": [item.value for item in evidence.execution_modes],
                "verified": evidence.verified,
                "healthy": evidence.healthy,
                "correctness_passed": evidence.correctness_passed,
                "quarantined": evidence.quarantined,
                "calibration_verified": evidence.calibration_verified,
                "calibration_outcome": evidence.calibration_outcome,
                "calibration_score": evidence.calibration_score,
            }
            for evidence in self._accelerator_selector.routes()
        ]
        verified_route_count = sum(
            1
            for route in routes
            if route["verified"] and route["healthy"] and route["correctness_passed"] and not route["quarantined"]
        )
        calibrated_route_count = sum(1 for route in routes if route["calibration_verified"])
        quarantined_route_count = sum(1 for route in routes if route["quarantined"])
        blockers: list[str] = []
        if verified_route_count == 0:
            blockers.append("no-verified-route")
        if calibrated_route_count == 0:
            blockers.append("calibration-required")
        if quarantined_route_count:
            blockers.append("route-quarantined")
        certification = {
            "route_count": len(routes),
            "verified_route_count": verified_route_count,
            "calibrated_route_count": calibrated_route_count,
            "quarantined_route_count": quarantined_route_count,
            "support_state": (
                "verified-calibrated"
                if verified_route_count and calibrated_route_count
                else "verified-uncalibrated"
                if verified_route_count
                else "unavailable"
            ),
            "blocker_codes": blockers,
        }
        return {
            "status_label": "VERIFIED" if decision.available else "DEGRADED",
            "mode": mode,
            "routes": routes,
            "active_decision": decision.model_dump(mode="json"),
            "calibration": self._accelerator_calibration.summary(),
            "circuits": self._accelerator_circuits.summary(),
            "certification": certification,
        }


def _verified_runtime_parameters(metadata: dict[str, Any] | None) -> dict[str, Any]:
    selection = (metadata or {}).get("evolutionary_inference")
    if not isinstance(selection, dict) or selection.get("verified") is not True:
        return {}
    parameters = selection.get("parameters")
    return dict(parameters) if isinstance(parameters, dict) else {}
