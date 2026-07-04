from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel


QuantObjective = Literal[
    "local_cpu_privacy",
    "balanced_quality_latency",
    "long_context_throughput",
    "minimum_vram",
    "training_or_adapter",
]


class QuantizationRecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    model_id: str
    runtime_targets: list[str] = Field(default_factory=list)
    hardware_snapshot: dict[str, Any] = Field(default_factory=dict)
    objective: QuantObjective = "balanced_quality_latency"
    context_tokens: int = 8192
    upstream_runtime_scorecard_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class QuantizationCatalog:
    def __init__(self, *, artifacts_dir: Path | None = None, methods: list[dict[str, Any]] | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.records_dir = self.artifacts_dir / "runtime" / "quantization-catalog" if self.artifacts_dir else None
        if self.records_dir is not None:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        self.methods = methods or _default_methods()
        self.kv_cache_candidates = _kv_cache_candidates()
        self._memory_recommendations: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()

    @classmethod
    def default(cls, *, artifacts_dir: Path | None = None) -> "QuantizationCatalog":
        return cls(artifacts_dir=artifacts_dir)

    def recommend(self, request: QuantizationRecommendationRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = (
            request
            if isinstance(request, QuantizationRecommendationRequest)
            else QuantizationRecommendationRequest.model_validate(request)
        )
        candidates = [_score_method(method, normalized) for method in self.methods]
        candidates.sort(key=lambda item: item["score"], reverse=True)
        selected = candidates[0]
        kv_cache_plan = _kv_cache_plan(normalized, self.kv_cache_candidates)
        upstream_runtime_scorecard_gate = _upstream_runtime_scorecard_gate(normalized.upstream_runtime_scorecard_gate)
        promotion_blockers = _quantization_promotion_blockers(upstream_runtime_scorecard_gate)
        reason_codes = _reason_codes(normalized, selected, kv_cache_plan)
        if promotion_blockers:
            reason_codes.append("quantization_catalog_blocks_runtime_scorecard_gate")
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized, selected, kv_cache_plan))
        recommendation = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "quantization-catalog",
            "request_id": normalized.request_id,
            "model_id": normalized.model_id,
            "status": "blocked" if promotion_blockers else "recommended-shadow",
            "runtime_state": "degraded" if promotion_blockers else "live-bound",
            "created_at": utcnow().isoformat(),
            "selected_method": selected,
            "candidates": candidates,
            "kv_cache_plan": kv_cache_plan,
            "reason_codes": reason_codes,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "upstream_runtime_scorecard_gate": upstream_runtime_scorecard_gate,
            "promotion_allowed": not promotion_blockers,
            "promotion_blockers": promotion_blockers,
            "promotion_boundary": "benchmark-hardware-fit-license-provenance-rollback-before-promotion",
            "metadata": normalized.metadata,
        }
        self._persist(recommendation)
        return recommendation

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        recommendations = self._list_recommendations(limit=limit)
        latest = recommendations[0] if recommendations else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if latest.get("status") == "blocked" else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "quantization-catalog",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "method_count": len(self.methods),
            "kv_cache_candidate_count": len(self.kv_cache_candidates),
            "recommendation_count": len(recommendations),
            "blocked_count": sum(1 for recommendation in recommendations if recommendation.get("status") == "blocked"),
            "latest_recommendation": latest,
            "methods": self.methods,
            "kv_cache_candidates": self.kv_cache_candidates,
            "recommendations": recommendations,
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md",
                "docs/NEXUSNET_OPEN_FIRST_RESEARCH_EXPANSION_2026-04-28.md",
                "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
            ],
            "watch_items": ["TurboQuant", "KIVI", "KVQuant", "MXFP4", "NVFP4", "BOF4", "AutoRound", "HQQ"],
            "catalog_boundary": "recommendation-and-shadow-research-only-no-live-requantization",
        }

    def _persist(self, recommendation: dict[str, Any]) -> None:
        self._memory_recommendations.insert(0, recommendation)
        self._memory_recommendations = self._memory_recommendations[:50]
        if self.records_dir is not None:
            safe_id = recommendation["request_id"].replace(":", "_").replace("/", "_")
            path = self.records_dir / f"{safe_id}.json"
            recommendation["artifact_path"] = str(path)
            path.write_text(json.dumps(recommendation, indent=2), encoding="utf-8")

    def _list_recommendations(self, *, limit: int) -> list[dict[str, Any]]:
        recommendations = list(self._memory_recommendations)
        seen = {item.get("request_id") for item in recommendations}
        if self.records_dir is not None:
            for path in self.records_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("request_id") not in seen:
                    recommendations.append(payload)
        recommendations.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return recommendations[:limit]


def _score_method(method: dict[str, Any], request: QuantizationRecommendationRequest) -> dict[str, Any]:
    score = 0
    runtime_fit = method["runtime_fit"]
    targets = request.runtime_targets or []
    matching_targets = [target for target in targets if runtime_fit.get(target) in {"native", "supported", "experimental"}]
    score += len(matching_targets) * 20
    hardware = request.hardware_snapshot
    objective = request.objective
    if objective == "local_cpu_privacy" and method["format"] == "GGUF":
        score += 80
    if objective == "balanced_quality_latency" and method["method_id"] in {"awq-w4a16", "gptq-w4a16", "fp8-w8a8"}:
        score += 45
    if objective == "minimum_vram" and method["storage_bits"] <= 4:
        score += 35
    if objective == "training_or_adapter" and method["method_id"] == "nf4-qlora":
        score += 80
    if hardware.get("local_gpu") and method["gpu_friendly"]:
        score += 25
    if not hardware.get("local_gpu") and method["cpu_friendly"]:
        score += 25
    if method["status"] == "required-baseline":
        score += 5
    candidate = dict(method)
    candidate["score"] = score
    candidate["matching_runtime_targets"] = matching_targets
    return candidate


def _kv_cache_plan(request: QuantizationRecommendationRequest, candidates: list[dict[str, Any]]) -> dict[str, Any]:
    long_context = request.context_tokens >= 32768 or request.objective == "long_context_throughput"
    selected_policy = "fp8-kv-cache" if request.hardware_snapshot.get("local_gpu") and long_context else "int8-kv-cache"
    shadow_candidates = [candidate for candidate in candidates if candidate["status"] in {"research-candidate", "shadow-only"}]
    return {
        "selected_policy": selected_policy,
        "context_tokens": request.context_tokens,
        "long_context": long_context,
        "shadow_candidates": shadow_candidates,
        "active_boundary": "shadow-candidates-require-plugin-benchmark-and-needle-recall-gate",
    }


def _reason_codes(
    request: QuantizationRecommendationRequest,
    selected: dict[str, Any],
    kv_cache_plan: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    if selected["format"] == "GGUF":
        reasons.append("buyer_friendly_single_file")
    if selected["gpu_friendly"]:
        reasons.append("gpu_kernel_fit")
    if selected["cpu_friendly"]:
        reasons.append("cpu_fallback_fit")
    if kv_cache_plan["long_context"]:
        reasons.append("kv_cache_quantization")
    if request.objective:
        reasons.append(request.objective)
    return reasons


def _upstream_runtime_scorecard_gate(gate: dict[str, Any]) -> dict[str, Any]:
    blockers = sorted(
        {
            str(item)
            for item in [
                *(gate.get("blockers") or []),
                *(gate.get("promotion_blockers") or []),
            ]
            if str(item)
        }
    )
    return {
        "promotion_allowed": gate.get("promotion_allowed"),
        "status": gate.get("status") or ("blocked" if gate.get("promotion_allowed") is False or blockers else "not_provided"),
        "blockers": blockers,
        "source": gate.get("source") or "runtime_workload_scorecards",
    }


def _quantization_promotion_blockers(upstream_runtime_scorecard_gate: dict[str, Any]) -> list[str]:
    blockers = list(upstream_runtime_scorecard_gate.get("blockers") or [])
    if upstream_runtime_scorecard_gate.get("promotion_allowed") is False:
        blockers.append("runtime_scorecard_promotion_not_allowed")
    if upstream_runtime_scorecard_gate.get("status") == "blocked":
        blockers.append("runtime_scorecard_blocked")
    return sorted(set(str(item) for item in blockers if str(item)))


def _policy_targets(
    request: QuantizationRecommendationRequest,
    selected: dict[str, Any],
    kv_cache_plan: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "target_id": f"quantization-artifact::{request.request_id}",
            "target_type": "artifact",
            "metadata": {
                "promotion_requested": True,
                "license_state": "approved",
                "provenance_refs": selected.get("source_refs") or [],
            },
        },
        {
            "target_id": f"quantization-update::{request.request_id}",
            "target_type": "autonomous_update",
            "metadata": {
                "promotion_requested": False,
                "rollback_plan": "shadow-benchmark-before-active-runtime-change",
                "monitoring_plan": kv_cache_plan["active_boundary"],
            },
        },
    ]


def _required_controls() -> list[str]:
    return [
        "method_family_catalog",
        "format_runtime_matrix",
        "hardware_fit_scoring",
        "kv_cache_policy",
        "turboquant_kv_shadow_lane",
        "benchmark_required",
        "artifact_license_provenance",
        "rollback_before_promotion",
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/quantization-catalog"},
        "recommend": {"method": "POST", "endpoint": "/ops/brain/quantization-catalog/recommend"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/quantization-catalog"},
    }


def _default_methods() -> list[dict[str, Any]]:
    return [
        {
            "method_id": "gguf-k-quants",
            "label": "GGUF K-quants / I-quants",
            "method_family": "Weight-only PTQ",
            "format": "GGUF",
            "storage_bits": 4,
            "runtime_fit": {"llama.cpp": "native", "ollama": "native", "lm-studio": "native", "vllm": "experimental"},
            "cpu_friendly": True,
            "gpu_friendly": True,
            "status": "required-baseline",
            "source_refs": ["GGUF spec", "llama.cpp quantize docs"],
        },
        {
            "method_id": "awq-w4a16",
            "label": "AWQ W4A16",
            "method_family": "Activation-aware weight-only PTQ",
            "format": "safetensors",
            "storage_bits": 4,
            "runtime_fit": {"vllm": "native", "sglang": "supported", "transformers": "supported", "tensorrt-llm": "native"},
            "cpu_friendly": False,
            "gpu_friendly": True,
            "status": "required-baseline",
            "source_refs": ["AWQ paper", "vLLM quantization docs"],
        },
        {
            "method_id": "gptq-w4a16",
            "label": "GPTQ W4A16",
            "method_family": "Second-order weight-only PTQ",
            "format": "safetensors",
            "storage_bits": 4,
            "runtime_fit": {"vllm": "native", "sglang": "supported", "transformers": "supported", "tensorrt-llm": "native"},
            "cpu_friendly": False,
            "gpu_friendly": True,
            "status": "required-baseline",
            "source_refs": ["GPTQ paper", "vLLM quantization docs"],
        },
        {
            "method_id": "fp8-w8a8",
            "label": "FP8 W8A8",
            "method_family": "Weight plus activation quantization",
            "format": "safetensors",
            "storage_bits": 8,
            "runtime_fit": {"vllm": "native", "sglang": "supported", "tensorrt-llm": "native", "transformers": "supported"},
            "cpu_friendly": False,
            "gpu_friendly": True,
            "status": "hardware-dependent",
            "source_refs": ["TensorRT-LLM quantization docs", "vLLM quantization docs"],
        },
        {
            "method_id": "exl2-flex",
            "label": "EXL2 flexible bits per weight",
            "method_family": "Runtime-specific local CUDA quantization",
            "format": "EXL2",
            "storage_bits": 4,
            "runtime_fit": {"exllamav2": "native"},
            "cpu_friendly": False,
            "gpu_friendly": True,
            "status": "runtime-specific",
            "source_refs": ["ExLlamaV2"],
        },
        {
            "method_id": "nf4-qlora",
            "label": "NF4 QLoRA",
            "method_family": "Adapter/fine-tuning memory compression",
            "format": "safetensors",
            "storage_bits": 4,
            "runtime_fit": {"transformers": "supported", "peft": "native", "trl": "native"},
            "cpu_friendly": False,
            "gpu_friendly": True,
            "status": "training-lane",
            "source_refs": ["bitsandbytes NF4 docs", "QLoRA"],
        },
        {
            "method_id": "onnx-int8",
            "label": "ONNX INT8",
            "method_family": "Edge/runtime package quantization",
            "format": "ONNX",
            "storage_bits": 8,
            "runtime_fit": {"onnxruntime": "native", "openvino": "supported", "directml": "supported"},
            "cpu_friendly": True,
            "gpu_friendly": True,
            "status": "edge-lane",
            "source_refs": ["ONNX Runtime quantization docs"],
        },
    ]


def _kv_cache_candidates() -> list[dict[str, Any]]:
    return [
        {
            "method_id": "fp8-kv-cache",
            "method_family": "KV-cache quantization",
            "status": "runtime-supported",
            "promotion_gates": ["runtime_support", "needle_recall_delta", "latency_delta"],
        },
        {
            "method_id": "int8-kv-cache",
            "method_family": "KV-cache quantization",
            "status": "runtime-supported",
            "promotion_gates": ["runtime_support", "needle_recall_delta", "latency_delta"],
        },
        {
            "method_id": "turboquant-kv",
            "method_family": "KV-cache quantization",
            "status": "research-candidate",
            "promotion_gates": ["benchmark_required", "plugin_review", "needle_recall_delta", "artifact_trust"],
        },
        {
            "method_id": "kivi-kv",
            "method_family": "KV-cache quantization",
            "status": "research-candidate",
            "promotion_gates": ["benchmark_required", "long_context_eval", "runtime_plugin"],
        },
    ]
