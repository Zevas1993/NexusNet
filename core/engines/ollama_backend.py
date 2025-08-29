
from __future__ import annotations
import os
from .base import BaseEngine
from utils.http import post_json

class OllamaEngine(BaseEngine):
    name = "ollama"
    def __init__(self):
        self.base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "llama3.1")
        self.live = os.environ.get("LIVE_ENGINES","0") == "1"

    def generate(self, prompt: str, **kw) -> str:
        if not self.live:
            return f"[ollama:dry] {prompt}"
        j = post_json(self.base + "/api/generate", {"model": self.model, "prompt": prompt}, timeout=3, retries=2)
        if isinstance(j, dict) and "response" in j:
            return j["response"]
        return f"[ollama] {prompt}"
