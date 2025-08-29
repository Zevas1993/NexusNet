
from __future__ import annotations
import os, anyio, httpx
from core.engines.token_counters import count_text
from services.metrics import begin_stream, tick_stream, end_stream

class VLLMClient:
    def __init__(self, base: str | None = None, model: str | None = None):
        self.base = (base or os.getenv("VLLM_URL") or "http://127.0.0.1:8000/v1").rstrip("/")
        self.model = model or os.getenv("VLLM_MODEL") or "auto"

    def chat(self, messages, **kw) -> str:
        async def _go():
            async with httpx.AsyncClient(timeout=60) as c:
                payload = {"model": self.model, "messages": messages}
                payload.update(kw or {})
                r = await c.post(f"{self.base}/chat/completions", json=payload)
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"]
        begin_stream()
        text = anyio.run(_go)
        tick_stream(count_text(text))
        end_stream(0)
        return text
