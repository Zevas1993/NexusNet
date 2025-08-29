
from __future__ import annotations
import os
from .base import BaseEngine
from utils.http import post_json

class VLLMEngine(BaseEngine):
    name = "vllm"
    def __init__(self):
        self.base = os.environ.get("VLLM_BASE_URL", "http://127.0.0.1:8001")
        self.model = os.environ.get("VLLM_MODEL", "local")
        self.live = os.environ.get("LIVE_ENGINES","0") == "1"

    def generate(self, prompt: str, **kw) -> str:
        if not self.live:
            return f"[vllm:dry] {prompt}"
        j = post_json(self.base + "/v1/completions", {"model": self.model, "prompt": prompt, "max_tokens": 64}, timeout=3, retries=2)
        if isinstance(j, dict) and j.get("choices"):
            return j["choices"][0].get("text") or f"[vllm] {prompt}"
        return f"[vllm] {prompt}"
