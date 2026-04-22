from __future__ import annotations

from pathlib import Path

from ..base import BrainRuntimeBackend
from ..capabilities import onnx_genai_capability_card


class ONNXGenAIBackend(BrainRuntimeBackend):
    runtime_name = "onnx-genai"
    backend_type = "portable-runtime"
    status_label = "IMPLEMENTATION BRANCH"

    def available(self) -> bool:
        model_path = self.config.get("model_path")
        if model_path:
            return Path(model_path).exists()
        return bool(self.config.get("endpoint"))

    def capability_card(self):
        return onnx_genai_capability_card()
