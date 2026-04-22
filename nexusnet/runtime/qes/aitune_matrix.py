from __future__ import annotations

from typing import Any


class AITuneSupportedLaneMatrix:
    def __init__(self, *, config: dict[str, Any]):
        self.config = config

    def supported_lane(self) -> dict[str, Any]:
        lane = self.config.get("supported_lane", {}) or {}
        compatibility = self.config.get("compatibility", {}) or {}
        return {
            "status": str(lane.get("status", "ready-on-supported-host")),
            "platform": str((compatibility.get("platform_allowlist") or ["Linux"])[0]),
            "python_max_minor": int(compatibility.get("python_max_minor", 12)),
            "nvidia_required": bool(compatibility.get("require_nvidia_gpu", True)),
            "torch_required": bool(compatibility.get("require_torch", True)),
            "runner_command": str(lane.get("runner_command", "python -m nexusnet.runtime.qes.aitune_runner --model <model_id>")),
            "mock_validation_command": str(
                lane.get("mock_validation_command", "python -m nexusnet.runtime.qes.aitune_runner --model <model_id> --simulate --json")
            ),
            "execution_modes": list(lane.get("execution_modes", ["skip-safe", "simulate", "live"])),
            "host_requirements": list(
                lane.get(
                    "host_requirements",
                    [
                        "Linux host in the allowlist.",
                        "Python 3.12 or earlier.",
                        "PyTorch with CUDA and visible NVIDIA devices.",
                        "AITune installed and importable.",
                    ],
                )
            ),
            "container_guidance": list(
                lane.get(
                    "container_guidance",
                    [
                        "Use Linux with NVIDIA Container Toolkit or equivalent GPU pass-through.",
                        "Use Python 3.12 or earlier and install aitune plus torch with CUDA support.",
                    ],
                )
            ),
            "devcontainer_guidance": list(
                lane.get(
                    "devcontainer_guidance",
                    [
                        "Base on Ubuntu 22.04 or newer.",
                        "Expose NVIDIA devices and CUDA libraries inside the devcontainer.",
                    ],
                )
            ),
            "ci_guidance": list(
                lane.get(
                    "ci_guidance",
                    [
                        "Gate live validation behind Linux plus NVIDIA runners only.",
                        "Keep unsupported jobs in mock or skip-safe mode.",
                    ],
                )
            ),
            "artifact_expectations": list(
                lane.get(
                    "artifact_expectations",
                    [
                        "compatibility report",
                        "validation report",
                        "runner report",
                        "benchmark evidence",
                        "tuned artifact metadata",
                        "execution plan markdown",
                    ],
                )
            ),
            "preflight_commands": list(
                lane.get(
                    "preflight_commands",
                    [
                        "python -c \"import sys,platform; print(platform.platform()); print(sys.version)\"",
                        "python -c \"import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.device_count())\"",
                        "nvidia-smi",
                    ],
                )
            ),
            "artifact_collection_commands": list(
                lane.get(
                    "artifact_collection_commands",
                    [
                        "find runtime/artifacts/runtime/aitune -maxdepth 3 -type f",
                    ],
                )
            ),
            "docs": list(
                lane.get(
                    "docs",
                    [
                        "docs/aitune_supported_lane.md",
                        "docs/aitune_linux_nvidia_validation.md",
                    ],
                )
            ),
        }

    def current_host_assessment(self, *, capability: dict[str, Any], applicability: dict[str, Any] | None = None, model_id: str = "unbound") -> dict[str, Any]:
        applicability = applicability or {"eligible": False, "reason": "No concrete model selected for validation."}
        execution_ready = bool(capability.get("available", False) and applicability.get("eligible", False))
        return {
            "model_id": model_id,
            "provider_health": capability.get("provider_health"),
            "platform_name": capability.get("platform_name"),
            "python_version": capability.get("python_version"),
            "torch_available": bool(capability.get("torch_available", False)),
            "torch_cuda_available": bool(capability.get("torch_cuda_available", False)),
            "cuda_device_count": int(capability.get("cuda_device_count", 0) or 0),
            "nvidia_gpu_present": bool(capability.get("nvidia_gpu_present", False)),
            "applicable": bool(applicability.get("eligible", False)),
            "execution_ready_here": execution_ready,
            "skip_reasons": list(capability.get("reasons", [])) + ([] if applicability.get("eligible", False) else [str(applicability.get("reason"))]),
        }

    def matrix(
        self,
        *,
        capability: dict[str, Any] | None = None,
        applicability: dict[str, Any] | None = None,
        model_id: str = "unbound",
    ) -> dict[str, Any]:
        compatibility = self.config.get("compatibility", {}) or {}
        target_registry = list((self.config.get("applicability") or {}).get("target_registry", []))
        scenarios = list((self.config.get("validation_matrix") or {}).get("scenarios", []))
        current_host = (
            self.current_host_assessment(capability=capability, applicability=applicability, model_id=model_id)
            if capability is not None
            else None
        )
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "platform_allowlist": list(compatibility.get("platform_allowlist", [])),
            "python_max_minor": compatibility.get("python_max_minor"),
            "require_nvidia_gpu": bool(compatibility.get("require_nvidia_gpu", True)),
            "target_registry": target_registry,
            "scenarios": scenarios,
            "supported_lane": self.supported_lane(),
            "current_host": current_host,
        }
