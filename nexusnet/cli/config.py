
from __future__ import annotations
import os, json, sys
from pathlib import Path

def _ask(k, default=""):
    val = input(f"{k} [{default}]: ").strip()
    return val or default

def main():
    print("NexusNet config wizard (Ctrl+C to cancel)")
    env = {}
    print("=== Engines ===")
    env["HF_MODEL_ID"] = _ask("HF_MODEL_ID", os.environ.get("HF_MODEL_ID",""))
    env["OLLAMA_BASE_URL"] = _ask("OLLAMA_BASE_URL", os.environ.get("OLLAMA_BASE_URL","http://127.0.0.1:11434"))
    env["VLLM_BASE_URL"] = _ask("VLLM_BASE_URL", os.environ.get("VLLM_BASE_URL","http://127.0.0.1:8001"))
    env["TGI_BASE_URL"] = _ask("TGI_BASE_URL", os.environ.get("TGI_BASE_URL","http://127.0.0.1:8080"))
    p = Path(".env")
    with p.open("w", encoding="utf-8") as f:
        for k,v in env.items():
            f.write(f"{k}={v}\n")
    print(f"Wrote {p}")
