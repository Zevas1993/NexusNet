from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class AITuneValidationRunner:
    def __init__(self, *, config: dict[str, Any], artifacts: Any, matrix: Any, adapter: Any | None = None):
        self.config = config
        self.artifacts = artifacts
        self.matrix = matrix
        self.adapter = adapter

    def readiness(self, *, capability: dict[str, Any], applicability: dict[str, Any] | None = None, model_id: str = "unbound") -> dict[str, Any]:
        supported_lane = self.matrix.supported_lane()
        applicable = applicability or {
            "eligible": False,
            "reason": "No concrete model selected for AITune validation.",
            "target_lane": "unbound",
        }
        can_execute_here = bool(capability.get("available", False) and applicable.get("eligible", False))
        status = "ready-to-run-here" if can_execute_here else "ready-on-supported-host"
        return {
            "status": status,
            "can_execute_here": can_execute_here,
            "target_lane": applicable.get("target_lane"),
            "runner_command": supported_lane.get("runner_command"),
            "docs": supported_lane.get("docs", []),
            "container_guidance": supported_lane.get("container_guidance", []),
            "devcontainer_guidance": supported_lane.get("devcontainer_guidance", []),
            "ci_guidance": supported_lane.get("ci_guidance", []),
            "execution_modes": supported_lane.get("execution_modes", []),
            "mock_validation_command": supported_lane.get("mock_validation_command"),
            "preflight_commands": supported_lane.get("preflight_commands", []),
            "artifact_collection_commands": supported_lane.get("artifact_collection_commands", []),
            "model_id": model_id,
        }

    def run(
        self,
        *,
        capability: dict[str, Any],
        applicability: dict[str, Any] | None = None,
        model_id: str = "unbound",
        simulate: bool = False,
    ) -> dict[str, Any]:
        applicable = applicability or {
            "eligible": False,
            "reason": "No concrete model selected for AITune validation.",
            "target_lane": "unbound",
        }
        matrix_payload = self.matrix.matrix(capability=capability, applicability=applicable, model_id=model_id)
        readiness = self.readiness(capability=capability, applicability=applicable, model_id=model_id)
        can_execute_here = bool(readiness.get("can_execute_here"))
        execute_live = bool(can_execute_here and self.adapter is not None and bool(self.config.get("allow_live_invoke", False)))
        execution_mode = "simulate" if simulate and not execute_live else ("live" if execute_live else "skip-safe")
        current_status = "validation-ready" if can_execute_here else "skipped"
        if simulate and not execute_live:
            current_status = "simulated-supported-lane"
        health_report = self._health_report(
            capability=capability,
            applicability=applicable,
            readiness=readiness,
            model_id=model_id,
            execution_mode=execution_mode,
        )
        execution_plan = self._execution_plan(
            capability=capability,
            applicability=applicable,
            readiness=readiness,
            model_id=model_id,
            simulate=simulate,
        )
        execution_plan_markdown = self._execution_plan_markdown(execution_plan)
        runner_payload = {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "current_status": current_status,
            "execution_mode": execution_mode,
            "capability": capability,
            "applicability": applicable,
            "matrix": matrix_payload,
            "supported_lane": readiness,
            "skip_reason": None if can_execute_here else " ".join(capability.get("reasons", [])),
            "host_specific": bool((self.config.get("rollout") or {}).get("host_specific_default", True)),
            "portable": False,
            "rollback_reference": applicable.get("rollback_reference"),
            "benchmark_evidence": {},
            "health_report": health_report,
            "execution_plan": execution_plan,
        }
        if execute_live:
            work_dir = Path(self.artifacts.artifacts_dir) / "runtime" / "aitune" / "validation-work" / model_id.replace("/", "__")
            adapter_result = self.adapter.tune(
                capability=capability,
                model_id=model_id,
                module_kind=applicable.get("target_lane", "pytorch-native-transformers"),
                backend_preferences=list((self.config.get("backend_preferences") or {}).get("order", [])),
                work_dir=work_dir,
            )
            runner_payload["current_status"] = adapter_result.get("status", current_status)
            runner_payload["benchmark_evidence"] = {
                    "selected_backend": adapter_result.get("selected_backend"),
                    "metrics": adapter_result.get("metrics", {}),
                    "artifact_lineage": adapter_result.get("artifact_lineage", {}),
                }
        elif simulate:
            runner_payload["benchmark_evidence"] = self._simulated_benchmark_evidence(
                capability=capability,
                applicability=applicable,
                model_id=model_id,
            )
            runner_payload["skip_reason"] = runner_payload["skip_reason"] or "Simulated supported-lane execution requested on a non-live host."
        benchmark_artifact = self.artifacts.write_benchmark_report(
            model_id=model_id,
            payload={
                "status": runner_payload["current_status"],
                "execution_mode": execution_mode,
                "capability": capability,
                "applicability": applicable,
                "benchmark_evidence": runner_payload["benchmark_evidence"],
                "rollback_reference": applicable.get("rollback_reference"),
                "host_specific": runner_payload["host_specific"],
                "portable": runner_payload["portable"],
            },
        )
        tuned_artifact = None
        if runner_payload["benchmark_evidence"].get("selected_backend") or execution_mode == "simulate":
            tuned_artifact = self.artifacts.write_tuned_artifact_metadata(
                model_id=model_id,
                payload={
                    "status": runner_payload["current_status"],
                    "execution_mode": execution_mode,
                    "selected_backend": runner_payload["benchmark_evidence"].get("selected_backend"),
                    "artifact_lineage": runner_payload["benchmark_evidence"].get("artifact_lineage", {}),
                    "host_specific": runner_payload["host_specific"],
                    "portable": runner_payload["portable"],
                    "rollback_reference": applicable.get("rollback_reference"),
                },
            )
        health_artifact = self.artifacts.write_health_report(model_id=model_id, payload=health_report)
        execution_plan_artifact = self.artifacts.write_execution_plan(model_id=model_id, payload=execution_plan)
        execution_plan_markdown_artifact = self.artifacts.write_execution_plan_markdown(model_id=model_id, markdown=execution_plan_markdown)
        runner_payload["health_artifact_path"] = health_artifact
        runner_payload["execution_plan_artifact_path"] = execution_plan_artifact
        runner_payload["execution_plan_markdown_path"] = execution_plan_markdown_artifact
        runner_payload["benchmark_artifact_path"] = benchmark_artifact
        runner_payload["tuned_artifact_path"] = tuned_artifact
        validation_artifact = self.artifacts.write_validation_report(model_id=model_id, payload=runner_payload)
        runner_artifact = self.artifacts.write_runner_report(
            model_id=model_id,
            payload={
                "supported_lane": readiness,
                "matrix": matrix_payload,
                "capability": capability,
                "applicability": applicable,
                "health_report": health_report,
                "execution_plan": execution_plan,
                "execution_plan_markdown_path": execution_plan_markdown_artifact,
                "benchmark_artifact_path": benchmark_artifact,
                "tuned_artifact_path": tuned_artifact,
            },
        )
        runner_payload["artifact_path"] = validation_artifact
        runner_payload["runner_artifact_path"] = runner_artifact
        return runner_payload

    def _health_report(
        self,
        *,
        capability: dict[str, Any],
        applicability: dict[str, Any],
        readiness: dict[str, Any],
        model_id: str,
        execution_mode: str,
    ) -> dict[str, Any]:
        return {
            "model_id": model_id,
            "provider_health": capability.get("provider_health"),
            "available": bool(capability.get("available", False)),
            "platform_name": capability.get("platform_name"),
            "python_version": capability.get("python_version"),
            "torch_available": bool(capability.get("torch_available", False)),
            "torch_cuda_available": bool(capability.get("torch_cuda_available", False)),
            "nvidia_gpu_present": bool(capability.get("nvidia_gpu_present", False)),
            "eligible_target_lane": applicability.get("target_lane"),
            "eligible_here": bool(applicability.get("eligible", False)),
            "can_execute_here": bool(readiness.get("can_execute_here", False)),
            "execution_mode": execution_mode,
            "reasons": list(capability.get("reasons", [])),
        }

    def _execution_plan(
        self,
        *,
        capability: dict[str, Any],
        applicability: dict[str, Any],
        readiness: dict[str, Any],
        model_id: str,
        simulate: bool,
    ) -> dict[str, Any]:
        supported_lane = self.matrix.supported_lane()
        live_command = supported_lane.get("runner_command")
        if model_id and "<model_id>" in str(live_command):
            live_command = str(live_command).replace("<model_id>", model_id)
        simulate_command = supported_lane.get("mock_validation_command")
        if model_id and "<model_id>" in str(simulate_command):
            simulate_command = str(simulate_command).replace("<model_id>", model_id)
        return {
            "model_id": model_id,
            "target_lane": applicability.get("target_lane"),
            "simulate": simulate,
            "runner_command": supported_lane.get("runner_command"),
            "mock_validation_command": supported_lane.get("mock_validation_command"),
            "resolved_live_command": live_command,
            "resolved_simulate_command": simulate_command,
            "execution_modes": supported_lane.get("execution_modes", []),
            "host_requirements": supported_lane.get("host_requirements", []),
            "preflight_commands": supported_lane.get("preflight_commands", []),
            "artifact_collection_commands": supported_lane.get("artifact_collection_commands", []),
            "docs": supported_lane.get("docs", []),
            "container_guidance": supported_lane.get("container_guidance", []),
            "devcontainer_guidance": supported_lane.get("devcontainer_guidance", []),
            "ci_guidance": supported_lane.get("ci_guidance", []),
            "artifact_expectations": supported_lane.get("artifact_expectations", []),
            "ready_to_run_here": bool(readiness.get("can_execute_here", False)),
            "provider_health": capability.get("provider_health"),
            "execution_steps": [
                {
                    "step_id": "preflight",
                    "label": "Run preflight checks",
                    "commands": supported_lane.get("preflight_commands", []),
                },
                {
                    "step_id": "simulate",
                    "label": "Run simulate validation on any host",
                    "commands": [simulate_command],
                },
                {
                    "step_id": "live",
                    "label": "Run live validation on Linux plus NVIDIA",
                    "commands": [live_command],
                },
                {
                    "step_id": "collect-artifacts",
                    "label": "Collect generated artifacts for audit and rollback review",
                    "commands": supported_lane.get("artifact_collection_commands", []),
                },
            ],
        }

    def _execution_plan_markdown(self, execution_plan: dict[str, Any]) -> str:
        return "\n".join(
            [
                f"# AITune Supported Lane Execution Plan {execution_plan.get('model_id')}",
                "",
                f"- Target lane: {execution_plan.get('target_lane')}",
                f"- Ready to run here: {execution_plan.get('ready_to_run_here')}",
                f"- Provider health: {execution_plan.get('provider_health')}",
                "",
                "## Host Requirements",
                *[f"- {item}" for item in execution_plan.get("host_requirements", [])],
                "",
                "## Preflight Commands",
                *[f"- `{item}`" for item in execution_plan.get("preflight_commands", [])],
                "",
                "## Simulate Command",
                f"- `{execution_plan.get('resolved_simulate_command')}`",
                "",
                "## Live Command",
                f"- `{execution_plan.get('resolved_live_command')}`",
                "",
                "## Execution Steps",
                *[
                    f"- {step.get('label')}: {', '.join(step.get('commands', []))}"
                    for step in execution_plan.get("execution_steps", [])
                ],
                "",
                "## Artifact Expectations",
                *[f"- {item}" for item in execution_plan.get("artifact_expectations", [])],
                "",
                "## Artifact Collection Commands",
                *[f"- `{item}`" for item in execution_plan.get("artifact_collection_commands", [])],
                "",
                "## Guidance",
                *[f"- {item}" for item in execution_plan.get("container_guidance", [])],
                *[f"- {item}" for item in execution_plan.get("devcontainer_guidance", [])],
                *[f"- {item}" for item in execution_plan.get("ci_guidance", [])],
            ]
        )

    def _simulated_benchmark_evidence(
        self,
        *,
        capability: dict[str, Any],
        applicability: dict[str, Any],
        model_id: str,
    ) -> dict[str, Any]:
        backend_preferences = list((self.config.get("backend_preferences") or {}).get("order", []))
        selected_backend = backend_preferences[0] if backend_preferences else "torch-inductor"
        return {
            "mode": "simulated-supported-lane",
            "model_id": model_id,
            "selected_backend": selected_backend,
            "metrics": {
                "latency_ms": 27.5,
                "throughput_tokens_per_s": 41.0,
                "correctness": float((self.config.get("benchmark_defaults") or {}).get("correctness_floor", 0.98)),
            },
            "artifact_lineage": {
                "surface": "simulated-supported-lane",
                "request": {
                    "model_id": model_id,
                    "module_kind": applicability.get("target_lane"),
                    "backend_preferences": backend_preferences,
                },
                "raw_artifact_path": None,
            },
            "host_constraints": list(capability.get("reasons", [])),
        }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run or simulate the NexusNet AITune supported-lane validation workflow.")
    parser.add_argument("--project-root", default=".", help="Project root used to build NexusNet services.")
    parser.add_argument("--model", dest="model_hint", default=None, help="Model hint for the target lane.")
    parser.add_argument("--simulate", action="store_true", help="Produce a supported-lane dry run on unsupported hosts.")
    parser.add_argument("--json", dest="emit_json", action="store_true", help="Emit machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    from nexus.services import build_services

    parser = _build_parser()
    args = parser.parse_args(argv)
    services = build_services(args.project_root)
    model = services.model_registry.resolve_model(args.model_hint) if args.model_hint else None
    payload = services.brain_runtime_registry.aitune_provider.validate(model, simulate=args.simulate)
    if args.emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"AITune validation status: {payload['current_status']}")
        print(f"Supported lane: {payload['supported_lane']['status']}")
        print(f"Execution mode: {payload['execution_mode']}")
        if payload.get("skip_reason"):
            print(f"Skip reason: {payload['skip_reason']}")
        print(f"Execution plan artifact: {payload['execution_plan_artifact_path']}")
        print(f"Execution plan markdown: {payload.get('execution_plan_markdown_path')}")
        print(f"Runner artifact: {payload['runner_artifact_path']}")
        print(f"Validation artifact: {payload['artifact_path']}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
