from __future__ import annotations

import importlib
import importlib.util
import platform
import shutil
import sys
from typing import Any

from nexus.config import env_flag

from ...schemas import BackendCapabilityCard


class AITuneCapabilityInspector:
    def __init__(self, runtime_configs: dict[str, Any]):
        self.runtime_configs = runtime_configs
        self.config = runtime_configs.get("aitune", {}) or {}
        self.features = runtime_configs.get("features", {}) or {}

    def detect(self) -> dict[str, Any]:
        compatibility = self.config.get("compatibility", {}) or {}
        allowlist = list(compatibility.get("platform_allowlist", ["Linux"]))
        python_max_minor = int(compatibility.get("python_max_minor", 12))
        require_nvidia = bool(compatibility.get("require_nvidia_gpu", True))
        require_torch = bool(compatibility.get("require_torch", True))

        feature_enabled = bool((self.features.get("runtime") or {}).get("aitune", False)) or env_flag("NEXUS_ENABLE_AITUNE", False)
        config_enabled = bool(self.config.get("enabled", False)) or env_flag("NEXUS_ENABLE_AITUNE", False)

        platform_name = platform.system()
        python_supported = sys.version_info < (3, python_max_minor + 1)
        platform_supported = platform_name in allowlist

        module_spec = importlib.util.find_spec("aitune")
        module_installed = module_spec is not None
        module_version = None
        api_surface: list[str] = []
        import_error = None
        if module_installed:
            try:
                module = importlib.import_module("aitune")
                module_version = getattr(module, "__version__", None)
                api_surface = [name for name in ["autotune", "tune", "AITuner"] if hasattr(module, name)]
            except Exception as exc:  # pragma: no cover - defensive runtime path
                import_error = str(exc)

        torch_available = importlib.util.find_spec("torch") is not None
        torch_version = None
        torch_cuda_available = False
        cuda_device_count = 0
        if torch_available:
            try:
                import torch  # type: ignore

                torch_version = getattr(torch, "__version__", None)
                torch_cuda_available = bool(torch.cuda.is_available())
                cuda_device_count = int(torch.cuda.device_count()) if torch_cuda_available else 0
            except Exception:  # pragma: no cover - defensive runtime path
                torch_available = False

        nvidia_gpu_present = bool(torch_cuda_available or shutil.which("nvidia-smi"))
        reasons: list[str] = []
        if not feature_enabled:
            reasons.append("Feature flag features.runtime.aitune is disabled.")
        if not config_enabled:
            reasons.append("AITune provider config is disabled.")
        if not module_installed:
            reasons.append("AITune package is not installed.")
        if import_error:
            reasons.append(f"AITune import failed: {import_error}")
        if not python_supported:
            reasons.append(f"Python {sys.version_info.major}.{sys.version_info.minor} is outside AITune's supported < 3.13 range.")
        if not platform_supported:
            reasons.append(f"Platform {platform_name} is outside the supported allowlist: {', '.join(allowlist)}.")
        if require_torch and not torch_available:
            reasons.append("PyTorch is unavailable for AITune-managed nn.Module or pipeline lanes.")
        if require_nvidia and not nvidia_gpu_present:
            reasons.append("No NVIDIA GPU path was detected for AITune GPU-accelerated tuning.")

        available = all(
            [
                feature_enabled,
                config_enabled,
                module_installed,
                python_supported,
                platform_supported,
                (torch_available or not require_torch),
                (nvidia_gpu_present or not require_nvidia),
                import_error is None,
            ]
        )
        health = "available" if available else ("disabled" if not feature_enabled or not config_enabled else "incompatible")
        return {
            "provider_name": "aitune",
            "status_label": "EXPLORATORY / PROTOTYPE",
            "feature_enabled": feature_enabled,
            "config_enabled": config_enabled,
            "module_installed": module_installed,
            "module_version": module_version,
            "python_supported": python_supported,
            "platform_supported": platform_supported,
            "torch_available": torch_available,
            "torch_version": torch_version,
            "torch_cuda_available": torch_cuda_available,
            "cuda_device_count": cuda_device_count,
            "nvidia_gpu_present": nvidia_gpu_present,
            "available": available,
            "provider_health": health,
            "api_surface": api_surface,
            "platform_name": platform_name,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "recommended_distros": list(compatibility.get("recommended_distros", [])),
            "backend_preferences": list((self.config.get("backend_preferences") or {}).get("order", [])),
            "reasons": reasons,
        }


def aitune_capability_card(*, capability: dict[str, Any]) -> BackendCapabilityCard:
    notes = [
        "Optional subordinate QES autotuning lane for PyTorch-native modules and pipelines.",
        "Never replaces dedicated serving backends when vLLM, SGLang, TensorRT-LLM, or llama.cpp are the canonical better fit.",
    ]
    if not capability.get("available", False):
        notes.append("Gracefully unavailable in unsupported or unconfigured environments.")
    return BackendCapabilityCard(
        runtime_name="aitune",
        backend_type="pytorch-autotune",
        status_label="EXPLORATORY / PROTOTYPE",
        local_first=True,
        supports_structured_output=False,
        supports_streaming=False,
        supports_gguf=False,
        supports_edge_portability=False,
        supports_tools=False,
        notes=notes + list(capability.get("reasons", []))[:3],
    )
