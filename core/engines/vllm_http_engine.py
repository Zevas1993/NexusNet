
from __future__ import annotations
import httpx

class VLLMHttpEngine:
    def __init__(self, url: str = "http://127.0.0.1:8000/generate"):
        self.url = url
    def generate(self, prompt: str, **kw) -> str:
        payload = {"prompt": prompt, "max_tokens": kw.get("max_new_tokens", 256), "temperature": kw.get("temperature", 0.7)}
        r = httpx.post(self.url, json=payload, timeout=60.0); r.raise_for_status()
        data = r.json(); return data.get("text") or data.get("output") or str(data)
