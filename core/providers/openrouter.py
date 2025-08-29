
from __future__ import annotations
import os, httpx

class OpenRouterClient:
    def __init__(self, api_key: str | None = None, base: str | None = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY","")
        self.base = base or "https://openrouter.ai/api/v1"
    def complete(self, prompt: str, model: str = "openrouter/openai/gpt-3.5", max_tokens: int = 256, temperature: float = 0.7) -> str:
        if not self.api_key:
            raise RuntimeError("OpenRouter API key missing")
        payload = {"model": model, "prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        r = httpx.post(f"{self.base}/completions", json=payload, headers=headers, timeout=120.0)
        r.raise_for_status()
        j = r.json()
        if "choices" in j and j["choices"]:
            return j["choices"][0].get("text","")
        return str(j)
