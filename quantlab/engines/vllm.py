
from __future__ import annotations
import os, requests
def call(prompt: str) -> str:
    url = os.environ.get("VLLM_ENDPOINT", "http://127.0.0.1:8001/generate")
    try:
        r = requests.post(url, json={"prompt": prompt, "max_tokens": 128}, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get("text","") if isinstance(data, dict) else str(data)
    except Exception:
        return ""
