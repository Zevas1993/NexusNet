from __future__ import annotations

from ..base import BrainRuntimeBackend
from ..capabilities import vllm_capability_card


class VLLMBackend(BrainRuntimeBackend):
    runtime_name = "vllm"
    backend_type = "openai-http"
    status_label = "IMPLEMENTATION BRANCH"

    def available(self) -> bool:
        endpoint = self.config.get("endpoint")
        return bool(endpoint)

    def capability_card(self):
        return vllm_capability_card()
