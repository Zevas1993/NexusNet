from __future__ import annotations

import json
import subprocess
import sys
import zipfile

from nexusnet.growth import NexusNetProductionSpine
from tests.test_training_backend_planner import backend_plan_request


def test_training_sandbox_runner_executes_backend_plan_without_production_mutation(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = backend_plan_request()
    request["raw_private_data"] = "raw private payload must not persist"
    request["training_dataset"] = [
        {"x": 0.0, "y": 1.0},
        {"x": 1.0, "y": 3.0},
        {"x": 2.0, "y": 5.0},
        {"x": 3.0, "y": 7.0},
    ]
    plan = spine.plan_training_backend(request)
    config_path = plan["execution_contract"]["config_path"]

    completed = subprocess.run(
        [sys.executable, "-m", "nexusnet.training.sandbox_runner", "--config", config_path, "--mode", "sandbox"],
        cwd="F:/NexusNet/NexusNet",
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["status"] == "sandbox_training_complete"
    assert output["production_mutation_allowed"] is False
    assert output["sandbox_weight_mutation_allowed"] is True
    assert output["hidden_eval_attestation"]["sealed"] is True
    assert output["hidden_eval_attestation"]["visible_to_training"] is False
    assert output["math_contract"]["loss"] == "L = mean((y_hat - y)^2)"
    assert output["math_contract"]["update_rule"] == "theta_next = theta - learning_rate * gradient"
    assert output["optimizer_state"]["optimizer"] == "batch_gradient_descent"
    assert output["optimizer_state"]["parameter_count"] == 2
    assert output["loss"]["final"] < output["loss"]["initial"]
    assert output["exports"]["adapter"]["state"] == "sandbox_candidate"
    assert output["exports"]["adapter"]["bundle_state"] == "sandbox_bundle_created"
    assert output["exports"]["adapter"]["bundle_path"].endswith("adapter_artifact_bundle.zip")
    assert output["exports"]["adapter"]["bundle_manifest_path"].endswith("adapter_bundle_manifest.json")
    bundle_manifest = json.loads(open(output["exports"]["adapter"]["bundle_manifest_path"], encoding="utf-8").read())
    assert bundle_manifest["bundle_state"] == "sandbox_bundle_created"
    assert "optimizer_state.json" in {entry["name"] for entry in bundle_manifest["entries"]}
    assert all(str(entry["sha256"]).startswith("sha256:") for entry in bundle_manifest["entries"])
    assert output["exports"]["merged"]["state"] == "blocked_until_eval_and_human_approval"
    assert output["exports"]["merged"]["path"].endswith("merged_export_gate.json")
    merged_export_gate = json.loads(open(output["exports"]["merged"]["path"], encoding="utf-8").read())
    assert merged_export_gate["production_load_allowed"] is False
    assert {"sealed_eval_gauntlet", "human_approval"}.issubset(merged_export_gate["required_gates"])
    assert output["exports"]["gguf"]["state"] == "export_plan_only"
    gguf_export_plan = json.loads(open(output["exports"]["gguf"]["path"], encoding="utf-8").read())
    assert gguf_export_plan["target_format"] == "gguf"
    assert gguf_export_plan["conversion_required"] is True
    assert "runtime_benchmark" in gguf_export_plan["required_gates"]
    assert gguf_export_plan["production_load_allowed"] is False
    assert output["exports"]["quantization_manifest"]["state"] == "sandbox_candidate"
    quantization_manifest = json.loads(open(output["exports"]["quantization_manifest"]["path"], encoding="utf-8").read())
    assert quantization_manifest["candidate_formats"] == ["gguf:q4_k_m", "gguf:q5_k_m"]
    assert quantization_manifest["benchmark_required"] is True
    assert "runtime_benchmark" in quantization_manifest["promotion_gate"]
    assert quantization_manifest["production_load_allowed"] is False

    report_path = output["artifacts"]["training_report_path"]
    report_text = open(report_path, encoding="utf-8").read()
    assert "raw private payload must not persist" not in report_text
    checkpoint = json.loads(open(output["artifacts"]["checkpoint_path"], encoding="utf-8").read())
    assert checkpoint["math_contract"]["model"] == "y_hat = w * x + b"
    assert checkpoint["optimizer_state"]["steps"] == 120
    optimizer_state = json.loads(open(output["artifacts"]["optimizer_state_path"], encoding="utf-8").read())
    assert optimizer_state["optimizer"] == "batch_gradient_descent"
    assert optimizer_state["final_gradients"]["d_loss_d_w"] == output["optimizer_state"]["final_gradients"]["d_loss_d_w"]
    with zipfile.ZipFile(output["exports"]["adapter"]["bundle_path"]) as adapter_bundle:
        names = set(adapter_bundle.namelist())
        adapter_text = adapter_bundle.read("adapter_manifest.json").decode("utf-8")
    assert "adapter_manifest.json" in names
    assert "checkpoint.json" in names
    assert "loss_trace.jsonl" in names
    assert "optimizer_state.json" in names
    assert "training_report.json" in names
    assert "adapter_bundle_manifest.json" in names
    assert "raw private payload must not persist" not in adapter_text


def test_training_sandbox_runner_blocks_missing_hidden_eval_attestation(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = backend_plan_request()
    request["training_dataset"] = [{"x": 0.0, "y": 1.0}, {"x": 1.0, "y": 3.0}]
    plan = spine.plan_training_backend(request)
    config_path = plan["execution_contract"]["config_path"]
    config = json.loads(open(config_path, encoding="utf-8").read())
    config["hidden_eval_attestation"] = {"sealed": False, "visible_to_training": True, "leakage_scan": {"status": "failed"}}
    open(config_path, "w", encoding="utf-8").write(json.dumps(config, sort_keys=True))

    completed = subprocess.run(
        [sys.executable, "-m", "nexusnet.training.sandbox_runner", "--config", config_path, "--mode", "sandbox"],
        cwd="F:/NexusNet/NexusNet",
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 2
    output = json.loads(completed.stdout)
    assert output["status"] == "blocked"
    assert "hidden_eval_attestation_required" in output["blocked_reasons"]
    assert output["production_mutation_allowed"] is False
