
from __future__ import annotations
import os, shutil
from typing import Dict

def detect_env() -> Dict[str, bool]:
    return {
        "vllm": bool(os.environ.get("VLLM_ENDPOINT")),
        "tgi":  bool(os.environ.get("TGI_ENDPOINT")),
        "ollama": True if shutil.which("ollama") else False
    }
