from __future__ import annotations

from nexusnet.schemas import DeviceProfile


def build_device_profile(*, platform_name: str, python_version: str, cpu_count: int, ram_gb: float | None, gpu_summary: str | None) -> DeviceProfile:
    return DeviceProfile(
        platform=platform_name,
        python_version=python_version,
        cpu_count=cpu_count,
        ram_gb=ram_gb,
        gpu_summary=gpu_summary,
        thermal_mode="unknown",
        local_first=True,
        status_label="LOCKED CANON",
    )
