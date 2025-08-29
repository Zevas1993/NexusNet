
from __future__ import annotations
import os, requests
def call(prompt: str) -> str:
    url = os.environ.get("TGI_ENDPOINT", "http://127.0.0.1:8080/generate")
    try:
        r = requests.post(url, json={"inputs": prompt, "parameters": {"max_new_tokens": 128}}, timeout=30)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
        return ""
    except Exception:
        return ""
