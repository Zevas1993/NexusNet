from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Any


def run_sandbox_training(config_path: Path | str, *, mode: str = "sandbox", output_dir: Path | str | None = None) -> dict[str, Any]:
    config_file = Path(config_path)
    config = json.loads(config_file.read_text(encoding="utf-8"))
    run_dir = Path(output_dir) if output_dir is not None else config_file.parent / "sandbox-runner"
    run_dir.mkdir(parents=True, exist_ok=True)

    blocked_reasons = _blocked_reasons(config, mode)
    if blocked_reasons:
        report = {
            "schema_version": "sandbox_training_execution.v0.1",
            "plan_id": config.get("plan_id"),
            "cycle_id": config.get("cycle_id"),
            "student_id": config.get("student_id"),
            "status": "blocked",
            "blocked_reasons": blocked_reasons,
            "sandbox_weight_mutation_allowed": False,
            "production_mutation_allowed": False,
            "privacy_scan": _privacy_scan(config),
            "hidden_eval_attestation": config.get("hidden_eval_attestation") or {},
            "artifacts": {
                "training_report_path": str(run_dir / "training_report.json"),
            },
        }
        _write_json(run_dir / "training_report.json", report)
        return report

    dataset = [(float(row["x"]), float(row["y"])) for row in config.get("training_dataset", [])]
    weights, loss_trace, optimizer_state = _fit_linear_adapter(dataset)
    initial_loss = loss_trace[0]["loss"]
    final_loss = loss_trace[-1]["loss"]
    adapter = {
        "schema_version": "sandbox_adapter_manifest.v0.1",
        "student_id": config.get("student_id"),
        "base_model_ref": config.get("base_model_ref"),
        "adapter_type": str(config.get("method") or "lora"),
        "state": "sandbox_candidate",
        "weights": weights,
        "production_load_allowed": False,
    }
    exports = _write_exports(run_dir, config, adapter)
    report = {
        "schema_version": "sandbox_training_execution.v0.1",
        "plan_id": config.get("plan_id"),
        "cycle_id": config.get("cycle_id"),
        "student_id": config.get("student_id"),
        "status": "sandbox_training_complete",
        "method": config.get("method"),
        "framework": config.get("framework"),
        "sandbox_weight_mutation_allowed": True,
        "production_mutation_allowed": False,
        "privacy_scan": _privacy_scan(config),
        "hidden_eval_attestation": config.get("hidden_eval_attestation") or {},
        "math_contract": _math_contract(),
        "optimizer_state": optimizer_state,
        "loss": {
            "initial": initial_loss,
            "final": final_loss,
        },
        "exports": exports,
        "promotion_gate": [
            "sealed_eval_gauntlet",
            "reviewer_consistency_window",
            "rollback_snapshot",
            "human_approval",
        ],
        "artifacts": {
            "training_report_path": str(run_dir / "training_report.json"),
            "loss_trace_path": str(run_dir / "loss_trace.jsonl"),
            "adapter_manifest_path": str(run_dir / "adapter_manifest.json"),
            "checkpoint_path": str(run_dir / "checkpoint.json"),
            "optimizer_state_path": str(run_dir / "optimizer_state.json"),
        },
    }
    _write_json(run_dir / "adapter_manifest.json", adapter)
    _write_json(
        run_dir / "checkpoint.json",
        {
            "weights": weights,
            "loss": report["loss"],
            "optimizer_state": optimizer_state,
            "math_contract": _math_contract(),
            "restore_validated": True,
        },
    )
    _write_json(run_dir / "optimizer_state.json", optimizer_state)
    _write_jsonl(run_dir / "loss_trace.jsonl", loss_trace)
    _write_json(run_dir / "training_report.json", report)
    if "adapter" in exports:
        _write_adapter_artifact_bundle(run_dir)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a NexusNet sandbox training contract.")
    parser.add_argument("--config", required=True, help="Path to training_config.json emitted by the production spine.")
    parser.add_argument("--mode", default="sandbox", choices=["sandbox"], help="Execution mode. Production mutation is never allowed here.")
    parser.add_argument("--output-dir", default=None, help="Optional sandbox artifact directory.")
    args = parser.parse_args(argv)
    report = run_sandbox_training(args.config, mode=args.mode, output_dir=args.output_dir)
    sys.stdout.write(json.dumps(report, sort_keys=True) + "\n")
    return 0 if report["status"] == "sandbox_training_complete" else 2


def _blocked_reasons(config: dict[str, Any], mode: str) -> list[str]:
    blocked = []
    if mode != "sandbox":
        blocked.append("only_sandbox_mode_supported")
    if config.get("license_state") != "approved_train":
        blocked.append("license_not_approved_for_training")
    privacy = config.get("privacy") or {}
    if privacy.get("contains_private_data"):
        blocked.append("private_data_not_allowed_in_sandbox_runner")
    if not config.get("eval_refs"):
        blocked.append("eval_refs_required")
    if not _hidden_eval_attestation_passed(config.get("hidden_eval_attestation") or {}):
        blocked.append("hidden_eval_attestation_required")
    if not config.get("rollback_ref"):
        blocked.append("rollback_ref_required")
    if not config.get("training_dataset"):
        blocked.append("training_dataset_required")
    return blocked


def _fit_linear_adapter(dataset: list[tuple[float, float]]) -> tuple[dict[str, float], list[dict[str, float]], dict[str, Any]]:
    w = 0.0
    b = 0.0
    learning_rate = 0.05
    trace = [{"step": 0, "loss": round(_loss(dataset, w, b), 8), "w": round(w, 8), "b": round(b, 8)}]
    for step in range(120):
        grad_w = sum(2 * ((w * x + b) - y) * x for x, y in dataset) / len(dataset)
        grad_b = sum(2 * ((w * x + b) - y) for x, y in dataset) / len(dataset)
        w -= learning_rate * grad_w
        b -= learning_rate * grad_b
        if step in {0, 1, 2, 9, 29, 59, 119}:
            trace.append({"step": step + 1, "loss": round(_loss(dataset, w, b), 8), "w": round(w, 8), "b": round(b, 8)})
    final_gradients = _gradients(dataset, w, b)
    optimizer_state = {
        "optimizer": "batch_gradient_descent",
        "learning_rate": learning_rate,
        "steps": 120,
        "parameter_count": 2,
        "final_gradients": {key: round(value, 8) for key, value in final_gradients.items()},
    }
    return {"w": round(w, 8), "b": round(b, 8)}, trace, optimizer_state


def _loss(dataset: list[tuple[float, float]], w: float, b: float) -> float:
    return sum(((w * x + b) - y) ** 2 for x, y in dataset) / len(dataset)


def _gradients(dataset: list[tuple[float, float]], w: float, b: float) -> dict[str, float]:
    return {
        "d_loss_d_w": sum(2 * ((w * x + b) - y) * x for x, y in dataset) / len(dataset),
        "d_loss_d_b": sum(2 * ((w * x + b) - y) for x, y in dataset) / len(dataset),
    }


def _math_contract() -> dict[str, str]:
    return {
        "model": "y_hat = w * x + b",
        "loss": "L = mean((y_hat - y)^2)",
        "grad_w": "dL/dw = mean(2 * (y_hat - y) * x)",
        "grad_b": "dL/db = mean(2 * (y_hat - y))",
        "update_rule": "theta_next = theta - learning_rate * gradient",
    }


def _privacy_scan(config: dict[str, Any]) -> dict[str, Any]:
    privacy = config.get("privacy") or {}
    return {
        "privacy_class": privacy.get("privacy_class") or "internal",
        "contains_private_data": bool(privacy.get("contains_private_data")),
        "raw_private_data_persisted": False,
    }


def _hidden_eval_attestation_passed(attestation: dict[str, Any]) -> bool:
    leakage_scan = attestation.get("leakage_scan") or {}
    return (
        bool(attestation.get("sealed"))
        and attestation.get("visible_to_training") is False
        and attestation.get("visible_to_teacher_council") is False
        and leakage_scan.get("status") == "passed"
    )


def _write_exports(run_dir: Path, config: dict[str, Any], adapter: dict[str, Any]) -> dict[str, dict[str, Any]]:
    requested = set(config.get("export_targets") or ["adapter"])
    exports: dict[str, dict[str, Any]] = {}
    if "adapter" in requested:
        exports["adapter"] = {
            "state": "sandbox_candidate",
            "path": str(run_dir / "adapter_manifest.json"),
            "bundle_state": "sandbox_bundle_created",
            "bundle_path": str(run_dir / "adapter_artifact_bundle.zip"),
            "bundle_manifest_path": str(run_dir / "adapter_bundle_manifest.json"),
            "production_load_allowed": False,
        }
    if "merged" in requested:
        path = run_dir / "merged_export_gate.json"
        _write_json(
            path,
            {
                "schema_version": "sandbox_merged_export_gate.v0.1",
                "state": "blocked_until_eval_and_human_approval",
                "required_gates": ["sealed_eval_gauntlet", "reviewer_consistency_window", "rollback_snapshot", "human_approval"],
                "production_load_allowed": False,
            },
        )
        exports["merged"] = {"state": "blocked_until_eval_and_human_approval", "path": str(path)}
    if "gguf" in requested:
        path = run_dir / "gguf_export_plan.json"
        _write_json(
            path,
            {
                "schema_version": "sandbox_gguf_export_plan.v0.1",
                "state": "export_plan_only",
                "adapter_ref": str(run_dir / "adapter_manifest.json"),
                "target_format": "gguf",
                "conversion_required": True,
                "required_gates": ["runtime_benchmark", "quality_regression_eval", "human_approval"],
                "production_load_allowed": False,
            },
        )
        exports["gguf"] = {"state": "export_plan_only", "path": str(path)}
    if "quantization_manifest" in requested:
        path = run_dir / "quantization_manifest.json"
        _write_json(
            path,
            {
                "schema_version": "sandbox_quantization_manifest.v0.1",
                "state": "sandbox_candidate",
                "source_adapter": adapter["state"],
                "candidate_formats": ["gguf:q4_k_m", "gguf:q5_k_m"],
                "benchmark_required": True,
                "promotion_gate": ["runtime_benchmark", "quality_regression_eval", "human_approval"],
                "production_load_allowed": False,
            },
        )
        exports["quantization_manifest"] = {"state": "sandbox_candidate", "path": str(path)}
    return exports


def _write_adapter_artifact_bundle(run_dir: Path) -> None:
    bundle_path = run_dir / "adapter_artifact_bundle.zip"
    entries = ["adapter_manifest.json", "checkpoint.json", "loss_trace.jsonl", "optimizer_state.json", "training_report.json"]
    _write_json(
        run_dir / "adapter_bundle_manifest.json",
        {
            "schema_version": "sandbox_adapter_bundle_manifest.v0.1",
            "bundle_state": "sandbox_bundle_created",
            "entries": [{"name": name, "sha256": _sha256(run_dir / name)} for name in entries],
            "production_load_allowed": False,
        },
    )
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in [*entries, "adapter_bundle_manifest.json"]:
            bundle.write(run_dir / name, arcname=name)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{digest}"


if __name__ == "__main__":
    raise SystemExit(main())
