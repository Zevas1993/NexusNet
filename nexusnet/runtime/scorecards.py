from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow


class RuntimeScorecardService:
    PROVIDERS = [
        {
            "provider_id": "onnxruntime-ep",
            "name": "ONNX Runtime Execution Providers",
            "mode": "local",
            "cloud_local_mode": "local",
            "openai_compatible": False,
            "tool_calling": False,
            "hardware_tier_fit": ["tier_1_constrained_edge", "tier_2_mainstream_local", "tier_3_premium_local"],
            "formats": ["onnx"],
            "quantization": "int8_int4_provider_dependent",
        },
        {
            "provider_id": "executorch",
            "name": "ExecuTorch",
            "mode": "local",
            "cloud_local_mode": "local",
            "openai_compatible": False,
            "tool_calling": False,
            "hardware_tier_fit": ["tier_0_tiny_edge", "tier_1_constrained_edge", "tier_2_mainstream_local"],
            "formats": ["pte", "torch"],
            "quantization": "edge_quantized",
        },
        {
            "provider_id": "litert",
            "name": "LiteRT",
            "mode": "local",
            "cloud_local_mode": "local",
            "openai_compatible": False,
            "tool_calling": False,
            "hardware_tier_fit": ["tier_0_tiny_edge", "tier_1_constrained_edge"],
            "formats": ["tflite"],
            "quantization": "int8_float16",
        },
        {
            "provider_id": "mlc-llm",
            "name": "MLC LLM",
            "mode": "local",
            "cloud_local_mode": "local",
            "openai_compatible": True,
            "tool_calling": False,
            "hardware_tier_fit": ["tier_2_mainstream_local", "tier_3_premium_local"],
            "formats": ["mlc", "safetensors"],
            "quantization": "mlc_quantized",
        },
        {
            "provider_id": "webllm",
            "name": "WebLLM",
            "mode": "local",
            "cloud_local_mode": "local_browser",
            "openai_compatible": True,
            "tool_calling": False,
            "hardware_tier_fit": ["tier_2_mainstream_local", "tier_3_premium_local"],
            "formats": ["webgpu", "mlc"],
            "quantization": "webgpu_quantized",
        },
        {
            "provider_id": "llama-cpp",
            "name": "llama.cpp",
            "mode": "local",
            "cloud_local_mode": "local",
            "openai_compatible": True,
            "tool_calling": True,
            "hardware_tier_fit": ["tier_1_constrained_edge", "tier_2_mainstream_local", "tier_3_premium_local"],
            "formats": ["gguf"],
            "quantization": "gguf_quantized",
        },
        {
            "provider_id": "openvino-genai",
            "name": "OpenVINO GenAI",
            "mode": "local",
            "cloud_local_mode": "local",
            "openai_compatible": False,
            "tool_calling": False,
            "hardware_tier_fit": ["tier_2_mainstream_local", "tier_3_premium_local", "tier_4_local_server"],
            "formats": ["openvino-ir", "onnx"],
            "quantization": "int8_int4_provider_dependent",
        },
        {
            "provider_id": "qnn",
            "name": "Qualcomm QNN",
            "mode": "local",
            "cloud_local_mode": "local",
            "openai_compatible": False,
            "tool_calling": False,
            "hardware_tier_fit": ["tier_1_constrained_edge", "tier_2_mainstream_local", "tier_3_premium_local"],
            "formats": ["qnn", "onnx"],
            "quantization": "int8_npu_candidate",
        },
        {
            "provider_id": "coreml",
            "name": "Core ML",
            "mode": "local",
            "cloud_local_mode": "local",
            "openai_compatible": False,
            "tool_calling": False,
            "hardware_tier_fit": ["tier_1_constrained_edge", "tier_2_mainstream_local", "tier_3_premium_local"],
            "formats": ["coreml"],
            "quantization": "ane_quantized_candidate",
        },
        {
            "provider_id": "directml",
            "name": "DirectML",
            "mode": "local",
            "cloud_local_mode": "local",
            "openai_compatible": False,
            "tool_calling": False,
            "hardware_tier_fit": ["tier_2_mainstream_local", "tier_3_premium_local"],
            "formats": ["onnx"],
            "quantization": "provider_dependent",
        },
        {
            "provider_id": "vllm",
            "name": "vLLM",
            "mode": "remote_or_local",
            "cloud_local_mode": "local_server",
            "openai_compatible": True,
            "tool_calling": True,
            "hardware_tier_fit": ["tier_4_local_server"],
            "formats": ["safetensors"],
            "quantization": "awq_gptq_fp8_candidate",
        },
        {
            "provider_id": "sglang",
            "name": "SGLang",
            "mode": "remote_or_local",
            "cloud_local_mode": "local_server",
            "openai_compatible": True,
            "tool_calling": True,
            "hardware_tier_fit": ["tier_4_local_server"],
            "formats": ["safetensors"],
            "quantization": "server_dependent",
        },
        {
            "provider_id": "tgi",
            "name": "Text Generation Inference",
            "mode": "remote_or_local",
            "cloud_local_mode": "local_server",
            "openai_compatible": True,
            "tool_calling": False,
            "hardware_tier_fit": ["tier_4_local_server"],
            "formats": ["safetensors"],
            "quantization": "bitsandbytes_awq_eetq_candidate",
        },
        {
            "provider_id": "tensorrt-llm",
            "name": "TensorRT-LLM",
            "mode": "local",
            "cloud_local_mode": "local_server",
            "openai_compatible": False,
            "tool_calling": False,
            "hardware_tier_fit": ["tier_3_premium_local", "tier_4_local_server"],
            "formats": ["tensorrt", "onnx"],
            "quantization": "fp8_int8_fp16_candidate",
        },
        {
            "provider_id": "ollama",
            "name": "Ollama",
            "mode": "local",
            "cloud_local_mode": "local",
            "openai_compatible": True,
            "tool_calling": True,
            "hardware_tier_fit": ["tier_2_mainstream_local", "tier_3_premium_local"],
            "formats": ["gguf", "modelpack"],
            "quantization": "gguf_quantized",
        },
        {
            "provider_id": "lm-studio",
            "name": "LM Studio",
            "mode": "local",
            "cloud_local_mode": "local",
            "openai_compatible": True,
            "tool_calling": True,
            "hardware_tier_fit": ["tier_2_mainstream_local", "tier_3_premium_local"],
            "formats": ["gguf"],
            "quantization": "gguf_quantized",
        },
        {
            "provider_id": "litellm",
            "name": "LiteLLM",
            "mode": "router",
            "cloud_local_mode": "router",
            "openai_compatible": True,
            "tool_calling": True,
            "hardware_tier_fit": ["tier_3_premium_local", "tier_4_local_server", "tier_5_governed_cloud"],
            "formats": ["openai-compatible", "provider-native"],
            "quantization": "provider_dependent",
        },
        {
            "provider_id": "tier5-cloud-router",
            "name": "Governed Tier 5 Cloud Router",
            "mode": "cloud_router",
            "cloud_local_mode": "governed_cloud",
            "openai_compatible": True,
            "tool_calling": True,
            "hardware_tier_fit": ["tier_5_governed_cloud"],
            "formats": ["openai-compatible", "provider-native"],
            "quantization": "provider_declared",
        },
    ]

    def __init__(self, *, artifacts_dir: Path | str, runtime_registry: Any | None = None, events: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "runtime-scorecards"
        self.runtime_registry = runtime_registry
        self.events = events

    def summary(self) -> dict[str, Any]:
        items = [self._scorecard(provider) for provider in self.PROVIDERS]
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "scorecard_count": len(items),
            "external_server_started": False,
            "execution_allowed": False,
            "mutation_allowed": False,
            "items": items,
            "latest_evaluations": self._evaluations(limit=20),
        }

    def compact_summary(self) -> dict[str, Any]:
        payload = self.summary()
        return {
            "status_label": payload["status_label"],
            "scorecard_count": payload["scorecard_count"],
            "external_server_started": False,
            "execution_allowed": False,
            "provider_ids": [item["provider_id"] for item in payload["items"]],
            "latest_evaluation": payload["latest_evaluations"][0] if payload["latest_evaluations"] else None,
        }

    def evaluate(self, *, provider_id: str, endpoint_url: str | None = None, model_hint: str | None = None) -> dict[str, Any]:
        scorecard = self.get(provider_id)
        if scorecard is None:
            raise ValueError(f"unsupported runtime provider: {provider_id}")
        scorecard = {
            **scorecard,
            "endpoint_url": endpoint_url,
            "model_hint": model_hint,
            "evaluated_at": utcnow().isoformat(),
            "openai_compatible_probe": {
                "state": "metadata_only",
                "endpoint_url_recorded": bool(endpoint_url),
                "network_call_executed": False,
            },
            "external_server_started": False,
            "execution_allowed": False,
            "mutation_allowed": False,
        }
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{provider_id}-{self._stamp(scorecard['evaluated_at'])}.json"
        scorecard["artifact_path"] = str(path)
        path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
        if self.events:
            self.events.record(
                event_type="runtime.scorecard_evaluated",
                subject=f"runtime-scorecard:{provider_id}",
                payload={
                    "provider_id": provider_id,
                    "state": "metadata_only",
                    "execution_allowed": False,
                    "external_server_started": False,
                },
            )
        return {"status_label": "STRONG ACCEPTED DIRECTION", "scorecard": scorecard}

    def get(self, provider_id: str) -> dict[str, Any] | None:
        for item in self.summary()["items"]:
            if item["provider_id"] == provider_id:
                return item
        return None

    def _scorecard(self, provider: dict[str, Any]) -> dict[str, Any]:
        provider_id = str(provider["provider_id"])
        mode = str(provider["mode"])
        openai_compatible = bool(provider["openai_compatible"])
        tool_calling = bool(provider["tool_calling"])
        return {
            "provider_id": provider_id,
            "provider_name": provider["name"],
            "mode": mode,
            "local_remote_mode": mode,
            "cloud_local_mode": provider["cloud_local_mode"],
            "hardware_tier_fit": list(provider["hardware_tier_fit"]),
            "model_artifact_formats": list(provider["formats"]),
            "openai_compatible_probe": {"state": "metadata_only", "supported": openai_compatible, "network_call_executed": False},
            "ttft": {"state": "not_measured", "milliseconds": None},
            "throughput": {"state": "not_measured", "tokens_per_second": None},
            "structured_output_support": "unknown_requires_probe",
            "tool_calling_support": "declared_candidate" if tool_calling else "unknown_requires_probe",
            "context_limit": {"state": "not_measured", "tokens": None},
            "prefix_cache_behavior": "unknown_requires_probe",
            "quantization_support": provider["quantization"],
            "cost_posture": "operator_budget_required" if provider_id == "tier5-cloud-router" else "local_or_operator_configured",
            "offline_posture": "cloud_required_after_governance" if provider_id == "tier5-cloud-router" else "offline_capable_preferred",
            "privacy_posture": (
                "redaction_and_operator_approval_required"
                if provider_id == "tier5-cloud-router"
                else "local_first_or_operator_configured"
            ),
            "product_sweep_gate_ids": [
                "phase-7-runtime",
                "runtime-certification",
                "provider-governance",
                *(["tier5-cloud-fallback-gate", "privacy-redaction-gate", "cost-budget-gate"] if provider_id == "tier5-cloud-router" else []),
            ],
            "policy_path": [{"stage": "runtime-scorecard", "decision": "hold", "reason": "metadata-only-v1"}],
            "approval_path": {"decision": "not_requested"},
            "external_server_started": False,
            "execution_allowed": False,
            "mutation_allowed": False,
        }

    def _evaluations(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.output_dir.exists():
            return []
        items = []
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(items) >= limit:
                break
        return items

    def _stamp(self, value: str) -> str:
        return "".join(ch if ch.isalnum() else "-" for ch in value.lower()).strip("-")
