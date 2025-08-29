
from __future__ import annotations
import os
from .base import BaseEngine
from utils.http import post_json

class TGIEngine(BaseEngine):
    name = "tgi"
    def __init__(self):
        self.base = os.environ.get("TGI_BASE_URL", "http://127.0.0.1:8080")
        self.live = os.environ.get("LIVE_ENGINES","0") == "1"

    def generate(self, prompt: str, **kw) -> str:
        if not self.live:
            return f"[tgi:dry] {prompt}"
        j = post_json(self.base + "/generate", {"inputs": prompt, "parameters": {"max_new_tokens": 64}}, timeout=3, retries=2)
        if isinstance(j, dict) and "generated_text" in j:
            return (j["generated_text"] or "").strip() or f"[tgi] {prompt}"
        return f"[tgi] {prompt}"
