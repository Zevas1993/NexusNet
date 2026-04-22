from __future__ import annotations

from pathlib import Path

from ..base import BrainRuntimeBackend
from ..capabilities import llama_cpp_capability_card


class LlamaCppBackend(BrainRuntimeBackend):
    runtime_name = "llama.cpp"
    backend_type = "local-python"
    status_label = "IMPLEMENTATION BRANCH"

    def available(self) -> bool:
        model_path = Path(self.config.get("model_path", ""))
        return model_path.exists()

    def capability_card(self):
        return llama_cpp_capability_card()
