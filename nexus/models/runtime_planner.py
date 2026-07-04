from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from ..runtimes import RuntimeRegistry


class ModelRuntimePlanner:
    """Classifies a model request and maps it to explicit runtime lanes."""

    LANE_DEFINITIONS: list[dict[str, Any]] = [
        {
            "lane": "llama.cpp",
            "adapter_names": ["llama.cpp"],
            "formats": ["gguf"],
            "modalities": ["text", "embedding"],
            "quantization": ["gguf-q2", "gguf-q3", "gguf-q4", "gguf-q5", "gguf-q6", "gguf-q8"],
            "methods": ["GGUF", "CPU fallback", "partial GPU offload", "CUDA", "Metal", "HIP", "Vulkan", "SYCL", "OpenCL"],
            "best_for": ["consumer hardware", "offline local runs", "low memory", "workstation CPU/GPU"],
        },
        {
            "lane": "vllm",
            "adapter_names": ["vllm"],
            "formats": ["safetensors", "pytorch", "openai-compatible-server"],
            "modalities": ["text", "embedding", "vision-language"],
            "quantization": ["awq", "gptq", "fp8", "int8", "fp16", "bf16"],
            "methods": ["PagedAttention", "continuous batching", "tensor parallelism", "OpenAI-compatible API"],
            "best_for": ["high-throughput GPU serving", "server batching", "long context"],
        },
        {
            "lane": "sglang",
            "adapter_names": ["sglang"],
            "formats": ["safetensors", "pytorch", "openai-compatible-server"],
            "modalities": ["text", "vision-language"],
            "quantization": ["awq", "gptq", "fp8", "int8", "fp16", "bf16"],
            "methods": ["RadixAttention", "prefix caching", "structured outputs", "OpenAI-compatible API"],
            "best_for": ["high-throughput LLM/VLM serving", "agent workloads", "structured generation"],
        },
        {
            "lane": "tgi",
            "adapter_names": ["tgi"],
            "formats": ["safetensors", "pytorch", "openai-compatible-server"],
            "modalities": ["text", "embedding"],
            "quantization": ["awq", "gptq", "fp8", "int8", "fp16", "bf16"],
            "methods": ["continuous batching", "tensor parallelism", "SSE streaming", "Hugging Face Hub integration"],
            "best_for": ["production Hugging Face serving", "common transformer families", "streaming"],
        },
        {
            "lane": "tensorrt-llm",
            "adapter_names": ["tensorrt-llm"],
            "formats": ["safetensors", "pytorch", "engine"],
            "modalities": ["text", "vision-language"],
            "quantization": ["fp8", "int8", "int4", "fp16", "bf16"],
            "methods": ["NVIDIA engine build", "tensor parallelism", "pipeline parallelism", "KV-cache optimization"],
            "best_for": ["NVIDIA-optimized inference", "low latency GPU serving", "compiled deployment"],
        },
        {
            "lane": "transformers",
            "adapter_names": ["transformers"],
            "formats": ["safetensors", "pytorch"],
            "modalities": ["text", "embedding", "vision-language", "speech", "reranker"],
            "quantization": ["bitsandbytes-8bit", "bitsandbytes-4bit", "awq", "gptq", "fp16", "bf16"],
            "methods": ["device_map=auto", "bitsandbytes", "Accelerate"],
            "best_for": ["broad compatibility", "research fallback", "unsupported model exploration"],
        },
        {
            "lane": "mlc",
            "adapter_names": ["mlc"],
            "formats": ["mlc-package"],
            "modalities": ["text"],
            "quantization": ["compiled-int4", "compiled-int8", "compiled-fp16"],
            "methods": ["compiled graph", "mobile/browser deployment", "cross-device packaging"],
            "best_for": ["edge/mobile/browser", "compiled local deployment"],
        },
        {
            "lane": "onnx-genai",
            "adapter_names": ["onnx-genai"],
            "formats": ["onnx"],
            "modalities": ["text", "vision-language"],
            "quantization": ["int4", "int8", "fp16"],
            "methods": ["ONNX Runtime GenAI", "DirectML", "CUDA", "CPU execution provider"],
            "best_for": ["Windows DirectML", "edge devices", "compiled ONNX deployments"],
        },
        {
            "lane": "ollama",
            "adapter_names": ["ollama"],
            "formats": ["local-server"],
            "modalities": ["text", "embedding"],
            "quantization": ["server-managed"],
            "methods": ["local model server", "OpenAI-compatible option"],
            "best_for": ["desktop convenience", "developer setup"],
            "convenience": True,
        },
        {
            "lane": "lmstudio",
            "adapter_names": ["lmstudio"],
            "formats": ["local-server", "openai-compatible-server"],
            "modalities": ["text"],
            "quantization": ["server-managed"],
            "methods": ["desktop model server", "OpenAI-compatible API"],
            "best_for": ["desktop convenience", "manual local testing"],
            "convenience": True,
        },
        {
            "lane": "openai-compatible",
            "adapter_names": ["openai-compatible"],
            "formats": ["openai-compatible-server"],
            "modalities": ["text", "embedding", "vision-language"],
            "quantization": ["service-managed"],
            "methods": ["OpenAI-compatible API"],
            "best_for": ["external serving gateways", "hosted local/runtime endpoints"],
            "convenience": True,
        },
    ]

    def __init__(self, *, runtime_registry: RuntimeRegistry, runtime_configs: dict[str, Any]):
        self.runtime_registry = runtime_registry
        self.runtime_configs = runtime_configs

    def capabilities(self) -> dict[str, Any]:
        profiles = {profile.runtime_name: profile for profile in self.runtime_registry.list_profiles()}
        lanes = []
        for definition in self.LANE_DEFINITIONS:
            adapter_names = list(definition.get("adapter_names", []))
            registered = any(adapter_name in self.runtime_registry.adapters for adapter_name in adapter_names)
            available_profiles = [
                profiles[adapter_name]
                for adapter_name in adapter_names
                if adapter_name in profiles and profiles[adapter_name].available
            ]
            lanes.append(
                {
                    **definition,
                    "registered": registered,
                    "available": bool(available_profiles),
                    "available_adapters": [profile.runtime_name for profile in available_profiles],
                }
            )
        return {
            "status_label": "IMPLEMENTATION BRANCH",
            "policy": {
                "any_model_claim": "classified-and-routed-through-supported-lanes",
                "mock_runtime": "explicit-dev-test-only",
            },
            "lanes": lanes,
        }

    def plan(self, request: dict[str, Any] | Any) -> dict[str, Any]:
        payload = self._payload(request)
        model_id = str(payload.get("model_id") or payload.get("model_path") or "").strip()
        context_tokens = int(payload.get("context_tokens") or payload.get("context_window") or 4096)
        model_format = self._detect_format(model_id, payload)
        quantization = self._detect_quantization(model_id, payload, model_format)
        modality = str(payload.get("modality") or self._detect_modality(model_id))
        architecture = str(payload.get("architecture") or self._detect_architecture(model_id))
        supported_lanes = self._supported_lanes(model_id, model_format, quantization, modality)
        recommended_lane = supported_lanes[0] if supported_lanes else None
        fallback_lanes = supported_lanes[1:]
        blocked_reasons: list[str] = []
        required_conversion: list[str] = []

        if not model_id:
            blocked_reasons.append("missing-model-id")
        if model_format == "unknown":
            blocked_reasons.append("unsupported-model-format")
            required_conversion.append("convert-to-gguf-safetensors-onnx-or-mlc")
        if recommended_lane and recommended_lane not in self._registered_lane_names():
            blocked_reasons.append(f"runtime-adapter-not-registered:{recommended_lane}")
        if recommended_lane and recommended_lane in self._registered_lane_names() and not self._lane_available(recommended_lane):
            blocked_reasons.append(f"runtime-not-available:{recommended_lane}")

        readiness = "blocked" if "unsupported-model-format" in blocked_reasons or "missing-model-id" in blocked_reasons else "planned"
        if recommended_lane and self._lane_available(recommended_lane):
            readiness = "ready"

        memory_estimate = self._estimate_memory(model_id, context_tokens, quantization)
        plan_payload = {
            "model_id": model_id,
            "model_format": model_format,
            "architecture": architecture,
            "modality": modality,
            "quantization": quantization,
            "context_tokens": context_tokens,
            "recommended_lane": recommended_lane,
            "fallback_lanes": fallback_lanes,
            "supported_runtime_lanes": supported_lanes,
            "required_conversion": required_conversion,
            "memory_estimate": memory_estimate,
            "readiness": readiness,
            "blocked_reasons": blocked_reasons,
        }
        plan_payload["compatibility_plan_id"] = self._plan_id(plan_payload)
        return plan_payload

    def validate(self, request: dict[str, Any] | Any) -> dict[str, Any]:
        plan = self.plan(request)
        return {
            "ok": plan["readiness"] != "blocked",
            **plan,
        }

    def _payload(self, request: dict[str, Any] | Any) -> dict[str, Any]:
        if isinstance(request, dict):
            return dict(request)
        if hasattr(request, "model_dump"):
            return request.model_dump(mode="json")
        return dict(request or {})

    def _detect_format(self, model_id: str, payload: dict[str, Any]) -> str:
        explicit = payload.get("model_format") or payload.get("format")
        if explicit:
            return str(explicit).lower()
        normalized = model_id.replace("\\", "/").lower()
        suffix = Path(normalized).suffix
        if normalized.startswith(("ollama/", "lmstudio/")):
            return "local-server"
        if normalized.startswith(("openai/", "openai-compatible/", "vllm/", "sglang/", "tgi/")):
            return "openai-compatible-server"
        if normalized.startswith(("mlc/", "mlc-package/")) or suffix in {".mlc", ".so", ".tar"}:
            return "mlc-package"
        if suffix == ".gguf":
            return "gguf"
        if suffix == ".onnx":
            return "onnx"
        if suffix in {".safetensors"}:
            return "safetensors"
        if suffix in {".bin", ".pt", ".pth"}:
            return "pytorch"
        if suffix and "/" not in normalized:
            return "unknown"
        if suffix and suffix not in {".json"} and normalized.endswith(".foo"):
            return "unknown"
        if any(token in normalized for token in ("awq", "gptq", "fp8", "int8", "4bit", "8bit")):
            return "safetensors"
        if "/" in model_id:
            return "safetensors"
        return "unknown"

    def _detect_quantization(self, model_id: str, payload: dict[str, Any], model_format: str) -> str:
        explicit = payload.get("quantization")
        if explicit:
            return str(explicit).lower()
        normalized = model_id.replace("-", "_").replace(".", "_").lower()
        if model_format == "gguf":
            stem = Path(normalized).stem
            match = re.search(r"q[2-8](?:_[a-z0-9]+)*", stem)
            return match.group(0).removesuffix("_gguf") if match else "gguf"
        for token in ("awq", "gptq", "fp8", "int8", "int4", "bf16", "fp16"):
            if token in normalized:
                return token
        if "4bit" in normalized or "bnb_4" in normalized:
            return "bitsandbytes-4bit"
        if "8bit" in normalized or "bnb_8" in normalized:
            return "bitsandbytes-8bit"
        if model_format in {"local-server", "openai-compatible-server"}:
            return "server-managed"
        if model_format in {"onnx", "mlc-package"}:
            return "compiled"
        return "unquantized"

    def _detect_modality(self, model_id: str) -> str:
        normalized = model_id.lower()
        if any(token in normalized for token in ("embedding", "embed", "bge-", "e5-")):
            return "embedding"
        if any(token in normalized for token in ("reranker", "rerank")):
            return "reranker"
        if any(token in normalized for token in ("whisper", "speech", "audio")):
            return "speech"
        if any(token in normalized for token in ("vl", "vision", "llava", "qwen2-vl", "qwen2.5-vl")):
            return "vision-language"
        return "text"

    def _detect_architecture(self, model_id: str) -> str:
        normalized = model_id.lower()
        for family in ("mixtral", "mistral", "llama", "qwen", "deepseek", "gemma", "phi", "command", "yi"):
            if family in normalized:
                return family
        return "unknown"

    def _supported_lanes(self, model_id: str, model_format: str, quantization: str, modality: str) -> list[str]:
        normalized = model_id.lower()
        if model_format == "gguf":
            return ["llama.cpp"]
        if model_format == "onnx":
            return ["onnx-genai"]
        if model_format == "mlc-package":
            return ["mlc"]
        if model_format == "local-server":
            if normalized.startswith("ollama/"):
                return ["ollama", "llama.cpp", "openai-compatible"]
            if normalized.startswith("lmstudio/"):
                return ["lmstudio", "openai-compatible", "llama.cpp"]
            return ["openai-compatible", "ollama", "lmstudio"]
        if model_format == "openai-compatible-server":
            if normalized.startswith("vllm/"):
                return ["vllm", "openai-compatible"]
            if normalized.startswith("sglang/"):
                return ["sglang", "openai-compatible"]
            if normalized.startswith("tgi/"):
                return ["tgi", "openai-compatible"]
            return ["openai-compatible", "vllm", "sglang", "tgi", "lmstudio"]
        if model_format in {"safetensors", "pytorch"}:
            if modality == "speech":
                return ["transformers"]
            if modality == "reranker":
                return ["transformers", "tgi"]
            if quantization in {"awq", "gptq"}:
                return ["vllm", "sglang", "tgi", "transformers"]
            if quantization in {"fp8", "int8", "int4"}:
                return ["vllm", "sglang", "tensorrt-llm", "tgi", "transformers"]
            return ["vllm", "sglang", "tgi", "transformers"]
        return []

    def _estimate_memory(self, model_id: str, context_tokens: int, quantization: str) -> dict[str, Any]:
        params_b = self._parameter_count_b(model_id)
        bytes_per_parameter = 2.0
        if quantization.startswith("q4") or quantization in {"int4", "bitsandbytes-4bit", "compiled-int4"}:
            bytes_per_parameter = 0.5
        elif quantization.startswith("q5"):
            bytes_per_parameter = 0.625
        elif quantization.startswith("q6"):
            bytes_per_parameter = 0.75
        elif quantization.startswith("q8") or quantization in {"int8", "fp8", "bitsandbytes-8bit", "compiled-int8"}:
            bytes_per_parameter = 1.0
        elif quantization in {"bf16", "fp16", "unquantized"}:
            bytes_per_parameter = 2.0
        weight_gb = round(params_b * bytes_per_parameter, 2) if params_b else None
        kv_cache_gb = round(max(context_tokens, 1) / 4096 * max(params_b or 7.0, 1.0) * 0.08, 2)
        total_gb = round((weight_gb or 0.0) + kv_cache_gb, 2) if weight_gb is not None else None
        return {
            "parameter_count_b": params_b,
            "estimated_weight_gb": weight_gb,
            "estimated_kv_cache_gb": kv_cache_gb,
            "estimated_total_gb": total_gb,
            "assumptions": {
                "bytes_per_parameter": bytes_per_parameter,
                "context_tokens": context_tokens,
                "kv_cache_model": "coarse-family-agnostic",
            },
        }

    def _parameter_count_b(self, model_id: str) -> float | None:
        normalized = model_id.lower()
        mixture = re.search(r"(\d+)x(\d+(?:\.\d+)?)b", normalized)
        if mixture:
            return round(float(mixture.group(1)) * float(mixture.group(2)), 2)
        match = re.search(r"(\d+(?:\.\d+)?)\s*b", normalized)
        if match:
            return float(match.group(1))
        return None

    def _registered_lane_names(self) -> set[str]:
        registered: set[str] = set()
        for definition in self.LANE_DEFINITIONS:
            if any(adapter_name in self.runtime_registry.adapters for adapter_name in definition.get("adapter_names", [])):
                registered.add(definition["lane"])
        return registered

    def _lane_available(self, lane: str) -> bool:
        profiles = {profile.runtime_name: profile for profile in self.runtime_registry.list_profiles()}
        definition = next((item for item in self.LANE_DEFINITIONS if item["lane"] == lane), None)
        if definition is None:
            return False
        return any(
            adapter_name in profiles and profiles[adapter_name].available
            for adapter_name in definition.get("adapter_names", [])
        )

    def _plan_id(self, payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, default=str)
        return f"compat_{hashlib.sha1(canonical.encode('utf-8')).hexdigest()[:12]}"
