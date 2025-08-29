
import os, platform, shutil
from typing import Dict, Any

def scan_hardware() -> Dict[str, Any]:
    info = {
        "os": platform.system(),
        "cpu_count": os.cpu_count(),
        "gpu": None,
        "cuda": False
    }
    # Try torch if available
    try:
        import torch
        info["cuda"] = bool(torch.cuda.is_available())
        if info["cuda"]:
            info["gpu"] = torch.cuda.get_device_name(0)
    except Exception:
        pass
    # llama.cpp availability
    info["llama_cpp_available"] = shutil.which("llama-cli") is not None
    return info

def local_first_policy() -> Dict[str, Any]:
    hw = scan_hardware()
    policy = {
        "prefer_local": True,
        "allow_cloud": False,
        "reason": "Respect $0 startup; enable cloud only if user configures API keys."
    }
    return {"hardware": hw, "policy": policy}
