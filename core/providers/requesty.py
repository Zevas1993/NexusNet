
from __future__ import annotations
import os, httpx

class RequestyClient:
    def __init__(self, api_key: str | None = None, base: str | None = None):
        self.api_key = api_key or os.environ.get("REQUESTY_API_KEY","")
        self.base = base or os.environ.get("REQUESTY_BASE","https://api.requesty.ai")
    def complete(self, prompt: str, model: str = "meta-llama/Meta-Llama-3-8B-Instruct", max_tokens: int = 256, temperature: float = 0.7) -> str:
        if not self.api_key:
            raise RuntimeError("Requesty API key missing")
        payload = {"model": model, "input": prompt, "max_tokens": max_tokens, "temperature": temperature}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        r = httpx.post(f"{self.base}/v1/completions", json=payload, headers=headers, timeout=120.0)
        r.raise_for_status()
        j = r.json()
        try:
            return j["choices"][0]["text"]
        except Exception:
            return str(j)
