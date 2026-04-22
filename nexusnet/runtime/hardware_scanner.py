from __future__ import annotations

import os
import platform
from typing import Any

from ..schemas import DeviceProfile


class HardwareScanner:
    def __init__(self, runtime_configs: dict[str, Any] | None = None):
        self.runtime_configs = runtime_configs or {}

    def scan(self) -> DeviceProfile:
        ram_gb = None
        vram_gb = None
        gpu_summary = "unreported"
        try:
            import psutil  # type: ignore

            ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        except Exception:
            ram_gb = None
        try:
            import torch  # type: ignore

            if torch.cuda.is_available():
                device_index = torch.cuda.current_device()
                props = torch.cuda.get_device_properties(device_index)
                gpu_summary = str(props.name)
                vram_gb = round(props.total_memory / (1024**3), 2)
        except Exception:
            vram_gb = None
        ram_pressure = self._pressure_label(ram_gb, low=16.0, critical=8.0)
        vram_pressure = self._pressure_label(vram_gb, low=12.0, critical=6.0, missing_label="unreported")
        safe_mode = bool((ram_gb is not None and ram_gb < 16.0) or (vram_gb is not None and vram_gb < 8.0))
        context_cap = self._context_cap(ram_gb=ram_gb, vram_gb=vram_gb)
        return DeviceProfile(
            platform=platform.platform(),
            python_version=platform.python_version(),
            cpu_count=os.cpu_count() or 1,
            ram_gb=ram_gb,
            vram_gb=vram_gb,
            gpu_summary=gpu_summary,
            thermal_mode="unknown",
            ram_pressure=ram_pressure,
            vram_pressure=vram_pressure,
            safe_mode=safe_mode,
            max_context_tokens=context_cap,
            long_context_profile={
                "ambition_tokens": 1_000_000,
                "host_cap_tokens": context_cap,
                "target_profile": "million-token-ambition" if context_cap >= 1_000_000 else "bounded-long-context",
            },
            local_first=True,
        )

    def _context_cap(self, *, ram_gb: float | None, vram_gb: float | None) -> int:
        if (ram_gb or 0.0) >= 128 or (vram_gb or 0.0) >= 48:
            return 1_000_000
        if (ram_gb or 0.0) >= 64 or (vram_gb or 0.0) >= 24:
            return 262_144
        if (ram_gb or 0.0) >= 24 or (vram_gb or 0.0) >= 12:
            return 131_072
        return 32_768

    def _pressure_label(self, value: float | None, *, low: float, critical: float, missing_label: str = "unknown") -> str:
        if value is None:
            return missing_label
        if value <= critical:
            return "critical"
        if value <= low:
            return "elevated"
        return "stable"
