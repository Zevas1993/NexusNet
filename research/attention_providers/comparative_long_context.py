from __future__ import annotations

from typing import Any


class ComparativeLongContextSuite:
    def __init__(self, *, runtime_profiles: list[dict[str, Any]] | None = None, retrieval_config: dict[str, Any] | None = None):
        self.runtime_profiles = runtime_profiles or []
        self.retrieval_config = retrieval_config or {}

    def baseline_catalog(self) -> list[dict[str, Any]]:
        return [
            {
                "provider_name": "accepted-dense-kv",
                "status_label": "LOCKED CANON",
                "comparison_kind": "accepted-in-repo-provider-path",
                "source_refs": ["core/engines/transformers_engine.py", "runtime/config/inference.yaml"],
                "notes": [
                    "Represents the accepted dense-KV long-context path in the current repo runtime stack.",
                    "Used as the primary memory-efficiency and latency comparison anchor for TriAttention research.",
                ],
            },
            {
                "provider_name": "accepted-windowed-hybrid",
                "status_label": "LOCKED CANON",
                "comparison_kind": "accepted-in-repo-provider-path",
                "source_refs": ["nexus/retrieval/service.py", "runtime/config/retrieval.yaml"],
                "notes": [
                    "Represents the accepted windowed or hybrid long-context path that relies on retrieval and budgeted context shaping.",
                    "Used as the accepted stability and retrieval-grounded baseline for TriAttention comparisons.",
                ],
            },
        ]

    def runtime_anchor_catalog(self) -> list[dict[str, Any]]:
        anchors: list[dict[str, Any]] = []
        for profile in self.runtime_profiles:
            runtime_name = str(profile.get("runtime_name") or "")
            if runtime_name not in {"transformers", "vllm", "onnx-genai", "llama.cpp"}:
                continue
            observed_latency_ms = self._observed_latency_ms(profile)
            observed_throughput = self._observed_throughput(profile, observed_latency_ms=observed_latency_ms)
            anchors.append(
                {
                    "provider_name": f"accepted-runtime::{runtime_name}",
                    "runtime_name": runtime_name,
                    "available": bool(profile.get("available", False)),
                    "backend_type": profile.get("backend_type"),
                    "health_mode": ((profile.get("health") or {}).get("mode")),
                    "observed_latency_ms": observed_latency_ms,
                    "observed_throughput_tokens_per_s": observed_throughput,
                    "measurement_mode": "runtime-profile-latency-anchored" if observed_latency_ms is not None else "health-anchored-heuristic",
                    "source_refs": self._runtime_source_refs(runtime_name),
                    "notes": [
                        f"Derived from the accepted in-repo runtime profile for {runtime_name}.",
                        "Used as a runtime-aware long-context comparison anchor for TriAttention research.",
                    ],
                }
            )
        if self._windowed_hybrid_enabled():
            anchors.append(
                {
                    "provider_name": "accepted-runtime::retrieval-windowed-hybrid",
                    "runtime_name": "retrieval-windowed-hybrid",
                    "available": True,
                    "backend_type": "retrieval-windowed",
                    "health_mode": "config-anchored",
                    "observed_latency_ms": None,
                    "observed_throughput_tokens_per_s": None,
                    "measurement_mode": "config-anchored-heuristic",
                    "source_refs": ["nexus/retrieval/service.py", "runtime/config/retrieval.yaml"],
                    "notes": [
                        "Derived from the active retrieval policy configuration.",
                        "Represents the accepted in-repo long-context path that trades context growth for retrieval-grounded windowing.",
                    ],
                }
            )
        return anchors

    def runtime_anchor_cases(self, *, context_tokens: int) -> list[dict[str, Any]]:
        scale = max(context_tokens, 1024) / 1024.0
        cases: list[dict[str, Any]] = []
        for anchor in self.runtime_anchor_catalog():
            runtime_name = anchor["runtime_name"]
            available = bool(anchor.get("available", False))
            kv_memory, throughput, latency, stability, reasoning, regression = self._runtime_anchor_metrics(
                runtime_name=runtime_name,
                scale=scale,
                anchor=anchor,
            )
            cases.append(
                {
                    "provider_name": anchor["provider_name"],
                    "comparison_kind": "accepted-runtime-anchor",
                    "source_refs": anchor["source_refs"],
                    "available": available,
                    "backend_type": anchor.get("backend_type"),
                    "source_health": anchor.get("health_mode"),
                    "measurement_mode": anchor.get("measurement_mode"),
                    "observed_latency_ms": anchor.get("observed_latency_ms"),
                    "observed_throughput_tokens_per_s": anchor.get("observed_throughput_tokens_per_s"),
                    "context_tokens": context_tokens,
                    "kv_memory_mb": round(kv_memory, 3),
                    "throughput_tokens_per_s": round(throughput, 3),
                    "latency_ms": round(latency, 3),
                    "stability_score": round(stability, 3),
                    "reasoning_quality": round(reasoning, 3),
                    "long_context_regression": round(regression, 3),
                }
            )
        return cases

    def _runtime_source_refs(self, runtime_name: str) -> list[str]:
        mapping = {
            "transformers": ["nexus/runtimes/registry.py", "runtime/config/inference.yaml", "core/inference/transformers.py"],
            "vllm": ["nexus/runtimes/registry.py", "runtime/config/inference.yaml", "nexusnet/runtime/backends/vllm_backend.py"],
            "onnx-genai": ["runtime/config/inference.yaml", "nexusnet/runtime/backends/onnx_genai_backend.py"],
            "llama.cpp": ["nexus/runtimes/registry.py", "runtime/config/inference.yaml", "nexusnet/runtime/backends/llama_cpp_backend.py"],
        }
        return mapping.get(runtime_name, ["runtime/config/inference.yaml"])

    def _windowed_hybrid_enabled(self) -> bool:
        stage1 = (self.retrieval_config.get("stage1") or {})
        sources = (stage1.get("sources") or {})
        return bool(sources.get("graph") or sources.get("memory") or sources.get("temporal"))

    def _observed_latency_ms(self, profile: dict[str, Any]) -> float | None:
        metrics = profile.get("metrics") or {}
        health_metrics = ((profile.get("health") or {}).get("metrics") or {})
        candidate = metrics.get("latency_ms") or health_metrics.get("latency_ms") or profile.get("ttft_ms")
        if candidate in {None, 0, 0.0}:
            return None
        try:
            value = float(candidate)
        except (TypeError, ValueError):
            return None
        return value if value > 0 else None

    def _observed_throughput(self, profile: dict[str, Any], *, observed_latency_ms: float | None) -> float | None:
        candidate = profile.get("throughput_tokens_per_s")
        try:
            if candidate is not None:
                value = float(candidate)
                if value > 0:
                    return value
        except (TypeError, ValueError):
            pass
        if observed_latency_ms is None:
            return None
        return max(1.0, round(1000.0 / max(observed_latency_ms, 1.0), 3))

    def _runtime_anchor_metrics(self, *, runtime_name: str, scale: float, anchor: dict[str, Any]) -> tuple[float, float, float, float, float, float]:
        observed_latency = anchor.get("observed_latency_ms")
        observed_throughput = anchor.get("observed_throughput_tokens_per_s")
        health_mode = str(anchor.get("health_mode") or "unknown")
        if runtime_name == "transformers":
            kv_factor, throughput_floor, latency_base, latency_growth = 0.94, 7.0, 20.5, 5.8
            stability_base, reasoning_base, regression_factor = 0.92, 0.89, 0.014
        elif runtime_name == "vllm":
            kv_factor, throughput_floor, latency_base, latency_growth = 0.86, 11.0, 17.2, 4.9
            stability_base, reasoning_base, regression_factor = 0.93, 0.9, 0.013
        elif runtime_name == "onnx-genai":
            kv_factor, throughput_floor, latency_base, latency_growth = 0.8, 10.0, 16.8, 4.6
            stability_base, reasoning_base, regression_factor = 0.9, 0.87, 0.014
        elif runtime_name == "llama.cpp":
            kv_factor, throughput_floor, latency_base, latency_growth = 0.76, 8.0, 19.4, 5.5
            stability_base, reasoning_base, regression_factor = 0.88, 0.84, 0.016
        else:
            kv_factor, throughput_floor, latency_base, latency_growth = 0.78, 10.0, 17.0, 4.8
            stability_base, reasoning_base, regression_factor = 0.91, 0.88, 0.013
        kv_memory = 180.0 * scale * kv_factor
        if observed_latency is not None:
            latency = observed_latency * (1.0 + max(scale - 1.0, 0.0) * 0.12)
            throughput = max(throughput_floor, (observed_throughput or throughput_floor) / max(1.0 + (scale - 1.0) * 0.14, 1.0))
        else:
            latency = latency_base + scale * latency_growth
            throughput = max(throughput_floor, 120.0 / max(scale, 1.0))
        if health_mode in {"live", "deterministic"}:
            stability_bias = 0.01
            reasoning_bias = 0.01
            regression_bias = -0.002
        elif health_mode in {"stub", "dry", "unconfigured", "unreachable"}:
            stability_bias = -0.02
            reasoning_bias = -0.02
            regression_bias = 0.004
        else:
            stability_bias = 0.0
            reasoning_bias = 0.0
            regression_bias = 0.0
        stability = max(0.55, stability_base - (scale * 0.013) + stability_bias)
        reasoning = max(0.55, reasoning_base - (scale * 0.012) + reasoning_bias)
        regression = min(0.35, scale * regression_factor + regression_bias)
        return kv_memory, throughput, latency, stability, reasoning, regression

    def baseline_cases(self, *, context_tokens: int) -> list[dict[str, Any]]:
        scale = max(context_tokens, 1024) / 1024.0
        catalog = {item["provider_name"]: item for item in self.baseline_catalog()}
        return [
            {
                "provider_name": "accepted-dense-kv",
                "comparison_kind": catalog["accepted-dense-kv"]["comparison_kind"],
                "source_refs": catalog["accepted-dense-kv"]["source_refs"],
                "context_tokens": context_tokens,
                "kv_memory_mb": round(180.0 * scale, 3),
                "throughput_tokens_per_s": round(max(6.0, 78.0 / scale), 3),
                "latency_ms": round(22.0 + scale * 6.5, 3),
                "stability_score": round(max(0.58, 0.96 - (scale * 0.012)), 3),
                "reasoning_quality": round(max(0.6, 0.93 - (scale * 0.009)), 3),
                "long_context_regression": round(min(0.35, scale * 0.015), 3),
            },
            {
                "provider_name": "accepted-windowed-hybrid",
                "comparison_kind": catalog["accepted-windowed-hybrid"]["comparison_kind"],
                "source_refs": catalog["accepted-windowed-hybrid"]["source_refs"],
                "context_tokens": context_tokens,
                "kv_memory_mb": round(180.0 * scale * 0.82, 3),
                "throughput_tokens_per_s": round(max(9.0, 104.0 / scale), 3),
                "latency_ms": round(18.0 + scale * 5.4, 3),
                "stability_score": round(max(0.56, 0.9 - (scale * 0.015)), 3),
                "reasoning_quality": round(max(0.56, 0.87 - (scale * 0.017)), 3),
                "long_context_regression": round(min(0.33, scale * 0.017), 3),
            },
        ]
