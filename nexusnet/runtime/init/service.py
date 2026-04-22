from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file


class RuntimeBootstrapService:
    def __init__(
        self,
        *,
        config_dir: Path,
        runtime_configs: dict[str, Any],
        runtime_registry: Any,
        model_registry: Any,
        runtime_profiler: Any,
        edge_vision_service: Any,
    ):
        repo_default = Path(__file__).resolve().parents[3] / "runtime" / "config" / "openjarvis_lane.yaml"
        self.config = runtime_configs.get("openjarvis_lane") or load_yaml_file(
            config_dir / "openjarvis_lane.yaml",
            load_yaml_file(repo_default, {}),
        )
        self.runtime_registry = runtime_registry
        self.model_registry = model_registry
        self.runtime_profiler = runtime_profiler
        self.edge_vision_service = edge_vision_service

    def summary(self) -> dict[str, Any]:
        presets = self._preset_catalog()
        return {
            "status_label": self.config.get("canon_status", "STRONG ACCEPTED DIRECTION"),
            "enabled": bool(self.config.get("enabled", True)),
            "local_first_default": bool(self.config.get("local_first_default", True)),
            "first_run_checklist": [
                "Detect available local runtimes and hardware posture.",
                "Recommend the best local-first preset before any cloud fallback.",
                "Keep gateway approvals and wrapper surfaces visible from the first run.",
                "Only suggest cloud fallback when local runtime fit is genuinely insufficient.",
            ],
            "preset_catalog": presets,
            "recommended_preset": self.recommend(),
            "device_profile": self.runtime_profiler.device_profile().model_dump(mode="json"),
            "doctor_ref": "/ops/brain/runtime/doctor",
        }

    def recommend(self, use_case: str | None = None) -> dict[str, Any]:
        profiles = [profile.model_dump(mode="json") for profile in self.runtime_registry.list_profiles()]
        available_runtimes = [profile["runtime_name"] for profile in profiles if profile.get("available")]
        device_profile = self.runtime_profiler.device_profile().model_dump(mode="json")
        ram_gb = float(device_profile.get("ram_gb") or 0.0)
        gpu_present = any(name in {"vllm", "transformers"} for name in available_runtimes)
        presets = self._preset_catalog()
        preset_lookup = {item["preset_id"]: item for item in presets}

        if use_case and use_case in preset_lookup:
            selected = preset_lookup[use_case]
        elif gpu_present and "deep-research" in preset_lookup:
            selected = preset_lookup["deep-research"]
        elif ram_gb and ram_gb <= 16 and "simple-chat" in preset_lookup:
            selected = preset_lookup["simple-chat"]
        elif self.edge_vision_service.summary().get("enabled") and "scheduled-monitor" in preset_lookup:
            selected = preset_lookup["scheduled-monitor"]
        else:
            selected = preset_lookup.get("code-assistant") or next(iter(preset_lookup.values()), {})

        preferred_runtimes = list(selected.get("preferred_runtimes", []))
        recommended_runtime = next((name for name in preferred_runtimes if name in available_runtimes), None)
        local_only = bool(recommended_runtime)
        return {
            "preset_id": selected.get("preset_id"),
            "label": selected.get("label"),
            "wrapper_mode": selected.get("wrapper_mode"),
            "agent_id": selected.get("agent_id"),
            "recommended_runtime": recommended_runtime or (available_runtimes[0] if available_runtimes else None),
            "recommended_model_id": self.model_registry.list_models()[0].model_id if self.model_registry.list_models() else None,
            "local_only": local_only,
            "cloud_only_when_necessary": bool((self.config.get("doctor") or {}).get("cloud_only_when_necessary", True)),
            "rationale": self._recommendation_rationale(
                selected=selected,
                available_runtimes=available_runtimes,
                device_profile=device_profile,
            ),
        }

    def recommendation_matrix(self) -> list[dict[str, Any]]:
        available_runtimes = [
            profile.runtime_name for profile in self.runtime_registry.list_profiles() if profile.available
        ]
        matrix = []
        for preset in self._preset_catalog():
            preferred = list(preset.get("preferred_runtimes", []))
            matrix.append(
                {
                    "preset_id": preset["preset_id"],
                    "label": preset["label"],
                    "wrapper_mode": preset["wrapper_mode"],
                    "agent_id": preset["agent_id"],
                    "recommended_runtime": next((name for name in preferred if name in available_runtimes), None),
                    "local_fit": any(name in available_runtimes for name in preferred),
                    "scheduled": preset.get("scheduled", False),
                    "retrieval_policy": preset.get("retrieval_policy"),
                    "cloud_fallback_allowed": preset.get("cloud_fallback_allowed", False),
                }
            )
        return matrix

    def _preset_catalog(self) -> list[dict[str, Any]]:
        presets = []
        for preset_id, payload in (self.config.get("presets") or {}).items():
            item = dict(payload)
            item["preset_id"] = preset_id
            presets.append(item)
        presets.sort(key=lambda item: item["preset_id"])
        return presets

    def _recommendation_rationale(self, *, selected: dict[str, Any], available_runtimes: list[str], device_profile: dict[str, Any]) -> list[str]:
        rationale = [
            "Local-first preset recommendation built from available runtimes and device posture.",
            f"Visible runtimes: {', '.join(available_runtimes) if available_runtimes else 'none detected'}.",
            f"CPU count: {device_profile.get('cpu_count')} | RAM: {device_profile.get('ram_gb') or 'unreported'} GB.",
        ]
        if selected.get("scheduled"):
            rationale.append("Selected preset preserves persistent/scheduled workflow support without creating a second control plane.")
        if selected.get("cloud_fallback_allowed", False):
            rationale.append("Cloud fallback remains allowed only when local fit is insufficient.")
        else:
            rationale.append("Preset remains local-only unless the operator explicitly changes the lane.")
        return rationale
