from __future__ import annotations

from typing import Any


class VisualPerformanceAdvisor:
    def __init__(self, *, allow_depth_enhancement: bool):
        self.allow_depth_enhancement = allow_depth_enhancement

    def build_profile(
        self,
        *,
        snapshot: dict[str, Any],
        safe_mode_physiology: dict[str, Any],
        telemetry_window: dict[str, Any],
        source_status: dict[str, Any],
    ) -> dict[str, Any]:
        runtime_summary = snapshot.get("runtime") or {}
        device_profile = runtime_summary.get("device_profile") or {}
        cpu_count = int(device_profile.get("cpu_count") or 1)
        ram_gb = device_profile.get("ram_gb")
        gpu_summary = str(device_profile.get("gpu_summary", "unreported") or "unreported")
        reduced_baseline = bool(safe_mode_physiology.get("safe_mode")) or safe_mode_physiology.get("retry_state") != "stable"

        reasons: list[str] = []
        if safe_mode_physiology.get("safe_mode"):
            recommended = "safe"
            reasons.append("safe-mode contraction active")
        elif safe_mode_physiology.get("retry_state") != "stable":
            recommended = "safe"
            reasons.append("retry/fallback posture active")
        elif safe_mode_physiology.get("thermal_mode") not in {"unknown", "cool", "nominal"}:
            recommended = "balanced"
            reasons.append("thermal posture elevated")
        elif ram_gb is not None and float(ram_gb) < 8:
            recommended = "safe"
            reasons.append("memory budget below recommended balanced tier floor")
        elif cpu_count <= 4:
            recommended = "balanced"
            reasons.append("cpu count suggests balanced tier default")
        else:
            recommended = "full" if telemetry_window.get("trace_count", 0) < 10 else "balanced"
            reasons.append("default scene complexity guardrail")

        hardware_class = "safe"
        if cpu_count >= 12 and (ram_gb is None or float(ram_gb) >= 16):
            hardware_class = "full"
        elif cpu_count >= 6 and (ram_gb is None or float(ram_gb) >= 8):
            hardware_class = "balanced"

        return {
            "recommended_tier": recommended,
            "available_tiers": ["auto", "full", "balanced", "safe"],
            "frame_budget_ms": {"full": 16.7, "balanced": 22.0, "safe": 32.0},
            "reduced_motion_capable": True,
            "lazy_assets": ["depth-inspector", "replay-history", "diff-highlights"],
            "fallback_behaviors": [
                "disable-depth-subrenderer",
                "reduce-canvas-pulse-density",
                "prefer-static-svg-labeling",
            ],
            "client_autotune": {
                "enabled": True,
                "downgrade_after_frame_budget_breaches": 18,
                "upgrade_after_stable_frames": 90,
                "reduced_motion_baseline": reduced_baseline,
            },
            "device_capability_profile": {
                "cpu_count": cpu_count,
                "ram_gb": ram_gb,
                "gpu_summary": gpu_summary,
                "hardware_class": hardware_class,
                "thermal_mode": safe_mode_physiology.get("thermal_mode", "unknown"),
            },
            "depth_mode": {
                "allowed": self.allow_depth_enhancement,
                "available": self.allow_depth_enhancement,
                "active": False,
                "fallback_renderer": "svg-canvas",
                "renderer": "canvas-depth",
            },
            "reasons": reasons,
            "telemetry_bound": telemetry_window.get("fully_bound", False),
            "source_bound_ratio": source_status.get("bound_ratio", 0.0),
            "render_policy": runtime_summary.get("status_label", "LOCKED CANON"),
        }
