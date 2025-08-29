
from __future__ import annotations
import os, socket

def _port_open(host, port, timeout=0.25):
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except Exception:
        return False

def status() -> dict:
    return {
        "transformers": {"available": bool(os.environ.get("HF_MODEL_ID"))},
        "ollama": {"available": _port_open(os.environ.get("OLLAMA_HOST","127.0.0.1"), os.environ.get("OLLAMA_PORT","11434"))},
        "vllm":   {"available": _port_open(os.environ.get("VLLM_HOST","127.0.0.1"), os.environ.get("VLLM_PORT","8001"))},
        "tgi":    {"available": _port_open(os.environ.get("TGI_HOST","127.0.0.1"), os.environ.get("TGI_PORT","8080"))},
    }
