
from __future__ import annotations
import httpx, os

class LMStudioEngine:
    def __init__(self, model: str = "local"):
        self.model = model
        self.base = os.environ.get("LMSTUDIO_BASE", "http://127.0.0.1:1234")
    def generate(self, prompt: str, **kw) -> str:
        r = httpx.post(f"{self.base}/v1/completions",
                       json={"model": self.model, "prompt": prompt, "max_tokens": kw.get("max_new_tokens",256),
                             "temperature": kw.get("temperature",0.7)}, timeout=120.0)
        r.raise_for_status(); j = r.json()
        if "choices" in j and j["choices"]: return j["choices"][0].get("text","")
        return str(j)
