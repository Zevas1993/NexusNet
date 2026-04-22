from __future__ import annotations

import platform
import sys
from typing import Any

from .config import VERSION, NexusPaths


def build_doctor_report(*, paths: NexusPaths, runtime_profiles: list[dict[str, Any]], model_count: int, tool_count: int) -> dict[str, Any]:
    available_runtimes = [profile["runtime_name"] for profile in runtime_profiles if profile.get("available")]
    return {
        "ok": True,
        "version": VERSION,
        "python": {"version": platform.python_version(), "executable": sys.executable},
        "paths": {
            "project_root": str(paths.project_root),
            "database": str(paths.database_path),
            "ui_dir": str(paths.ui_dir),
            "artifacts_dir": str(paths.artifacts_dir),
        },
        "checks": {
            "database_exists": paths.database_path.exists(),
            "ui_present": paths.ui_dir.exists(),
            "runtime_count": len(runtime_profiles),
            "live_runtimes": available_runtimes,
            "model_count": model_count,
            "tool_count": tool_count,
        },
    }
