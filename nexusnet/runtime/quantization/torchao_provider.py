from __future__ import annotations

from .base_provider import QuantizationProvider
from ...schemas import QuantizationDecision


class TorchAOQuantizationProvider(QuantizationProvider):
    provider_name = "torchao"
    status_label = "IMPLEMENTATION BRANCH"

    def plan(self, *, model_id: str, available_quantizations: list[str]) -> QuantizationDecision:
        preferred = "int8"
        if preferred not in available_quantizations:
            preferred = available_quantizations[0] if available_quantizations else "dynamic"
        return QuantizationDecision(
            model_id=model_id,
            selected_quantization=preferred,
            rationale="TorchAO-compatible plan selected for QES shadow benchmarking and local-first fallback.",
        )
