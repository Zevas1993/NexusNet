
from __future__ import annotations
import subprocess

def call(prompt: str, model: str = "llama3") -> str:
    try:
        cp = subprocess.run(["ollama","run",model,prompt], capture_output=True, text=True, timeout=60)
        return cp.stdout.strip()
    except Exception:
        return ""
