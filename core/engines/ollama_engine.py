
from __future__ import annotations
import httpx, os

class OllamaEngine:
    def __init__(self, model: str = "llama3"):
        self.model = model
        self.base = os.environ.get("OLLAMA_BASE", "http://127.0.0.1:11434")
    def generate(self, prompt: str, **kw) -> str:
        r = httpx.post(f"{self.base}/api/generate", json={"model": self.model, "prompt": prompt, "stream": False}, timeout=120.0)
        r.raise_for_status(); return r.json().get("response","")
