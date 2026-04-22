from __future__ import annotations

from typing import Any

from nexus.models import ModelRegistry
from nexus.runtimes import RuntimeRegistry

from ..schemas import QuantizationDecision, RuntimeOptimizationCandidate, TokenBudgetProfile
from .hardware_scanner import HardwareScanner


class AdaptiveSystemProfiler:
    def __init__(
        self,
        runtime_registry: RuntimeRegistry,
        model_registry: ModelRegistry,
        runtime_configs: dict[str, Any],
        hardware_scanner: HardwareScanner | None = None,
    ):
        self.runtime_registry = runtime_registry
        self.model_registry = model_registry
        self.runtime_configs = runtime_configs
        self.hardware_scanner = hardware_scanner or HardwareScanner(runtime_configs)

    def device_profile(self):
        return self.hardware_scanner.scan()

    def token_budget_profile(self) -> TokenBudgetProfile:
        qes = self.runtime_configs.get("qes", {})
        budget = qes.get("token_budget", {})
        return TokenBudgetProfile(
            profile_name=budget.get("profile_name", "default"),
            summary_fraction=float(budget.get("summary_fraction", 0.5)),
            preview_fraction=float(budget.get("preview_fraction", 0.3)),
            instruction_fraction=float(budget.get("instruction_fraction", 0.15)),
            reserve_fraction=float(budget.get("reserve_fraction", 0.05)),
        )

    def candidate_profiles(self, model_hint: str | None = None) -> list[RuntimeOptimizationCandidate]:
        model = self.model_registry.resolve_model(model_hint)
        device_profile = self.device_profile()
        safe_mode = bool(device_profile.safe_mode)
        candidates: list[RuntimeOptimizationCandidate] = []
        for profile in self.runtime_registry.list_profiles():
            baseline_latency = float(profile.metrics.get("latency_ms", 250 if profile.available else 900))
            power = 0.20 if profile.runtime_name in {"mock", "ollama", "llama.cpp", "transformers"} else 0.60
            quality = 0.8 if profile.available else 0.35
            if safe_mode and profile.runtime_name in {"vllm", "openai-compatible"}:
                baseline_latency += 50.0
                power += 0.15
            quantization = self._preferred_quantization(model_id=model.model_id, available_quantizations=model.capability_card.quantization or ["dynamic"])
            candidates.append(
                RuntimeOptimizationCandidate(
                    runtime_name=profile.runtime_name,
                    model_id=model.model_id,
                    quantization=quantization,
                    estimated_latency_ms=baseline_latency,
                    estimated_quality=quality,
                    estimated_power=power,
                    source="qes-shadow",
                )
            )
        return sorted(candidates, key=lambda candidate: (candidate.estimated_latency_ms, -candidate.estimated_quality))

    def quantization_decision(self, model_hint: str | None = None) -> QuantizationDecision:
        model = self.model_registry.resolve_model(model_hint)
        selected = self._preferred_quantization(
            model_id=model.model_id,
            available_quantizations=model.capability_card.quantization or ["dynamic"],
        )
        return QuantizationDecision(
            model_id=model.model_id,
            selected_quantization=selected,
            rationale="Selected from the hardware-aware QES profile with safe-mode fallback preserved.",
        )

    def execution_plan(self, *, model_hint: str | None = None, requested_runtime: str | None = None, selection_decision: dict[str, Any] | None = None) -> dict[str, Any]:
        device_profile = self.device_profile().model_dump(mode="json")
        model = self.model_registry.resolve_model(model_hint)
        runtime_candidates = [candidate.model_dump(mode="json") for candidate in self.candidate_profiles(model.model_id)]
        selected_runtime_name = requested_runtime or (selection_decision or {}).get("selected_runtime_name") or model.runtime_name
        safe_mode = bool(device_profile.get("safe_mode"))
        return {
            "status_label": "LOCKED CANON",
            "model_id": model.model_id,
            "selected_runtime_name": selected_runtime_name,
            "selection_decision": selection_decision or {},
            "hardware_profile": device_profile,
            "token_budget_profile": self.token_budget_profile().model_dump(mode="json"),
            "quantization_decision": self.quantization_decision(model.model_id).model_dump(mode="json"),
            "runtime_candidates": runtime_candidates,
            "safe_mode_fallback": safe_mode,
            "long_context_profile": device_profile.get("long_context_profile", {}),
            "qes_policy": self.runtime_configs.get("qes", {}),
        }

    def summary(self, model_hint: str | None = None) -> dict[str, Any]:
        model = self.model_registry.resolve_model(model_hint)
        return {
            "status_label": "LOCKED CANON",
            "device_profile": self.device_profile().model_dump(mode="json"),
            "token_budget_profile": self.token_budget_profile().model_dump(mode="json"),
            "quantization_decision": self.quantization_decision(model.model_id).model_dump(mode="json"),
            "candidates": [candidate.model_dump(mode="json") for candidate in self.candidate_profiles(model.model_id)],
        }

    def _preferred_quantization(self, *, model_id: str, available_quantizations: list[str]) -> str:
        device_profile = self.device_profile()
        quant_cfg = self.runtime_configs.get("quant_profile", {})
        configured = quant_cfg.get("default")
        if configured:
            return configured
        if device_profile.safe_mode:
            for candidate in ("int4", "q4", "int8", "dynamic", "gguf"):
                if candidate in available_quantizations:
                    return candidate
        return available_quantizations[0] if available_quantizations else "dynamic"
