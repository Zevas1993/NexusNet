from __future__ import annotations

from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file
from nexus.schemas import ModelRegistration

from .aitune_adapter import AITuneAdapter
from .aitune_artifacts import AITuneArtifactStore
from .aitune_benchmarks import AITuneBenchmarkSuite
from .aitune_capability import AITuneCapabilityInspector, aitune_capability_card
from .aitune_validation import AITuneValidationMatrix


class AITuneQESProvider:
    def __init__(self, *, config_dir: Path, artifacts_dir: Path, runtime_configs: dict[str, Any]):
        self.config_dir = config_dir
        self.artifacts_dir = artifacts_dir
        repo_default = Path(__file__).resolve().parents[3] / "runtime" / "config" / "aitune.yaml"
        self.config = runtime_configs.get("aitune") or load_yaml_file(config_dir / "aitune.yaml", load_yaml_file(repo_default, {}))
        self.runtime_configs = runtime_configs
        self.inspector = AITuneCapabilityInspector({**runtime_configs, "aitune": self.config})
        self.adapter = AITuneAdapter(config=self.config, artifacts_dir=artifacts_dir)
        self.artifacts = AITuneArtifactStore(artifacts_dir)
        self.benchmarks = AITuneBenchmarkSuite(config=self.config)
        self.validation = AITuneValidationMatrix(config=self.config, artifacts=self.artifacts, adapter=self.adapter)

    def capability_summary(self) -> dict[str, Any]:
        return self.inspector.detect()

    def capability_card(self) -> dict[str, Any]:
        return aitune_capability_card(capability=self.capability_summary()).model_dump(mode="json")

    def summary(self, model: ModelRegistration | None = None) -> dict[str, Any]:
        capability = self.capability_summary()
        applicability = self.applicability(model) if model is not None else None
        target_registry = list((self.config.get("applicability") or {}).get("target_registry", []))
        latest_validation = self.artifacts.latest_validation_report(model_id=model.model_id if model is not None else None)
        latest_health = self.artifacts.latest_health_report(model_id=model.model_id if model is not None else None)
        latest_execution_plan = self.artifacts.latest_execution_plan(model_id=model.model_id if model is not None else None)
        latest_benchmark = self.artifacts.latest_benchmark_report(model_id=model.model_id if model is not None else None)
        latest_tuned_artifact = self.artifacts.latest_tuned_artifact_metadata(model_id=model.model_id if model is not None else None)
        latest_runner_report = self.artifacts.latest_runner_report(model_id=model.model_id if model is not None else None)
        latest_execution_plan_markdown_path = self.artifacts.latest_execution_plan_markdown_path(model_id=model.model_id if model is not None else None)
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "provider_name": "aitune",
            "capability": capability,
            "applicability": applicability,
            "supported_lane_readiness": self.validation.readiness(
                capability=capability,
                applicability=applicability,
                model_id=model.model_id if model is not None else "unbound",
            ),
            "target_registry": target_registry,
            "target_registry_ids": [item.get("target_id") for item in target_registry],
            "repo_audit": self.repo_audit(),
            "validation_matrix": self.validation.matrix(capability=capability, applicability=applicability, model_id=model.model_id if model is not None else "unbound"),
            "latest_validation": latest_validation,
            "latest_health_report": latest_health,
            "latest_execution_plan": latest_execution_plan,
            "latest_execution_plan_markdown_path": latest_execution_plan_markdown_path,
            "latest_benchmark": latest_benchmark,
            "latest_tuned_artifact": latest_tuned_artifact,
            "latest_runner_report": latest_runner_report,
            "config": {
                "enabled": bool(self.config.get("enabled", False)),
                "allow_live_invoke": bool(self.config.get("allow_live_invoke", False)),
                "backend_preferences": list((self.config.get("backend_preferences") or {}).get("order", [])),
                "allowed_runtimes": list((self.config.get("applicability") or {}).get("allowed_runtimes", [])),
            },
        }

    def applicability(self, model: ModelRegistration | None) -> dict[str, Any]:
        if model is None:
            return {
                "eligible": False,
                "reason": "No model selected for AITune applicability audit.",
                "target_lane": "unbound",
            }
        cfg = self.config.get("applicability", {}) or {}
        blocked_runtimes = set(cfg.get("blocked_runtimes", []))
        allowed_runtimes = set(cfg.get("allowed_runtimes", []))
        blocked_quantizations = {value.lower() for value in cfg.get("blocked_quantizations", [])}
        quantizations = {str(value).lower() for value in model.capability_card.quantization}
        runtime_name = model.runtime_name
        target_lane = self._target_lane(model)
        reasons: list[str] = []
        if runtime_name in blocked_runtimes:
            reasons.append(f"Runtime '{runtime_name}' is a blocked dedicated or incompatible lane for AITune.")
        if allowed_runtimes and runtime_name not in allowed_runtimes:
            reasons.append(f"Runtime '{runtime_name}' is outside the PyTorch-native allowlist.")
        if blocked_quantizations & quantizations:
            reasons.append("Quantization profile is already in a blocked dedicated format such as GGUF.")
        eligible = not reasons and runtime_name in allowed_runtimes
        target_registry = list((self.config.get("applicability") or {}).get("target_registry", []))
        return {
            "eligible": eligible,
            "reason": "AITune may benchmark this PyTorch-native lane." if eligible else " ".join(reasons),
            "target_lane": target_lane,
            "source_model": model.model_id,
            "source_runtime": runtime_name,
            "host_specific": bool((self.config.get("rollout") or {}).get("host_specific_default", True)),
            "portable": False,
            "rollback_reference": f"runtime::{runtime_name}::{model.model_id}",
            "preferred_backends": list((self.config.get("backend_preferences") or {}).get("order", [])),
            "target_registry": target_registry,
            "target_registry_ids": [item.get("target_id") for item in target_registry],
        }

    def benchmark(self, model: ModelRegistration) -> dict[str, Any]:
        capability = self.capability_summary()
        applicability = self.applicability(model)
        compatibility_artifact = self.artifacts.write_compatibility_report(
            model_id=model.model_id,
            payload={
                "capability": capability,
                "applicability": applicability,
                "audit": self.repo_audit(),
            },
        )
        if not capability.get("available", False) or not applicability.get("eligible", False):
            skipped = {
                "status": "skipped",
                "reason": applicability.get("reason") if applicability.get("eligible", False) is False else "AITune capability unavailable.",
                "selected_backend": None,
                "artifact_lineage": {},
                "errors": [],
            }
            benchmark_path = self.artifacts.write_benchmark_report(
                model_id=model.model_id,
                payload={
                    "status": "skipped",
                    "capability": capability,
                    "applicability": applicability,
                    "rollback_reference": applicability.get("rollback_reference"),
                },
            )
            return self.benchmarks.build_result(
                model=model,
                capability=capability,
                applicability=applicability,
                adapter_result=skipped,
                compatibility_artifact_path=compatibility_artifact,
                benchmark_artifact_path=benchmark_path,
                tuned_artifact_path=None,
            )

        work_dir = self.artifacts_dir / "runtime" / "aitune" / "work" / model.model_id.replace("/", "__")
        adapter_result = self.adapter.tune(
            capability=capability,
            model_id=model.model_id,
            module_kind=applicability.get("target_lane", "pytorch-native"),
            backend_preferences=applicability.get("preferred_backends", []),
            work_dir=work_dir,
        )
        tuned_artifact_path = None
        if adapter_result.get("status") == "completed":
            tuned_artifact_path = self.artifacts.write_tuned_artifact_metadata(
                model_id=model.model_id,
                payload={
                    "selected_backend": adapter_result.get("selected_backend"),
                    "artifact_lineage": adapter_result.get("artifact_lineage"),
                    "host_specific": applicability.get("host_specific", True),
                    "portable": applicability.get("portable", False),
                },
            )
        benchmark_path = self.artifacts.write_benchmark_report(
            model_id=model.model_id,
            payload={
                "status": adapter_result.get("status"),
                "capability": capability,
                "applicability": applicability,
                "adapter_result": adapter_result,
                "tuned_artifact_path": tuned_artifact_path,
            },
        )
        return self.benchmarks.build_result(
            model=model,
            capability=capability,
            applicability=applicability,
            adapter_result=adapter_result,
            compatibility_artifact_path=compatibility_artifact,
            benchmark_artifact_path=benchmark_path,
            tuned_artifact_path=tuned_artifact_path,
        )

    def validate(self, model: ModelRegistration | None = None, *, simulate: bool = False) -> dict[str, Any]:
        capability = self.capability_summary()
        applicability = self.applicability(model) if model is not None else None
        return self.validation.run(
            capability=capability,
            applicability=applicability,
            model_id=model.model_id if model is not None else "unbound",
            simulate=simulate,
        )

    def repo_audit(self) -> dict[str, Any]:
        return {
            "fit": list((self.config.get("applicability") or {}).get("target_registry", [])),
            "avoid": [
                {"lane": "llama.cpp / GGUF", "reason": "non-PyTorch dedicated format"},
                {"lane": "vLLM / SGLang / TensorRT-LLM", "reason": "dedicated serving backends remain canonical when already the better path"},
                {"lane": "Windows + Python 3.13 default dev flow", "reason": "unsupported or intentionally skip-safe for current AITune lane"},
            ],
            "status_label": "EXPLORATORY / PROTOTYPE",
        }

    def _target_lane(self, model: ModelRegistration) -> str:
        text = " ".join(
            [
                model.model_id,
                model.display_name,
                " ".join(model.tags or []),
                " ".join(model.capability_card.preferred_tasks or []),
            ]
        ).lower()
        hints = (self.config.get("applicability") or {}).get("target_hints", {})
        for lane, values in hints.items():
            if any(value.lower() in text for value in values):
                return lane
        return "pytorch-native-transformers" if model.runtime_name == "transformers" else "unsupported"
