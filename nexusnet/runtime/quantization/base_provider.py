from __future__ import annotations

from abc import ABC, abstractmethod

from ...schemas import QuantizationDecision


class QuantizationProvider(ABC):
    provider_name = "quantization-provider"
    status_label = "STRONG ACCEPTED DIRECTION"

    @abstractmethod
    def plan(self, *, model_id: str, available_quantizations: list[str]) -> QuantizationDecision:
        raise NotImplementedError
