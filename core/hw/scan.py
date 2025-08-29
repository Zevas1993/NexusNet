
from __future__ import annotations
import psutil, platform
try: import torch
except Exception: torch = None

def scan():
    gpu, cuda, vram_gb = False, False, 0.0
    if torch is not None and torch.cuda.is_available():
        gpu, cuda = True, True
        try:
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        except Exception:
            vram_gb = 0.0
    return {
        "cpu_cores": psutil.cpu_count(logical=True),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "platform": platform.system(),
        "gpu": gpu, "cuda": cuda, "vram_gb": round(vram_gb, 2),
    }

def suggest():
    hw = scan()
    if hw["gpu"] and hw["vram_gb"] >= 6: return {"precision":"float16","device":"cuda"}
    return {"precision":"float32","device":"cpu"}
