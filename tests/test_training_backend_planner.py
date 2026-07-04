from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.growth import NexusNetProductionSpine
from tests.test_nexus_phase1_foundation import make_project


def backend_plan_request() -> dict:
    return {
        "cycle_id": "cycle:backend_plan_001",
        "plan_id": "train_backend:coder_qlora_001",
        "student_id": "student:coder_child_001",
        "base_model_ref": "model:qwen3-coder-next-local-cleared",
        "dataset_manifest_ref": "dataset:coder_child_001",
        "method": "qlora",
        "framework": "trl",
        "training_modes": ["sequence_distillation", "router_alignment", "validator_grounded_task_loss"],
        "teacher_refs": ["teacher:qwen3-coder-next", "teacher:devstral-2"],
        "license_state": "approved_train",
        "privacy_class": "internal",
        "contains_private_data": False,
        "eval_refs": ["eval:coder_hidden_001", "eval:security_regression_001"],
        "hidden_eval_attestation": {
            "sealed": True,
            "visible_to_training": False,
            "visible_to_teacher_council": False,
            "leakage_scan": {"status": "passed", "train_overlap": 0, "teacher_output_overlap": 0},
        },
        "rollback_ref": "rollback:coder_parent_v0",
        "export_targets": ["adapter", "merged", "gguf", "quantization_manifest"],
        "target_hardware": {"vendor": "nvidia", "vram_gb": 24, "cuda_available": True},
        "operator_approved": True,
        "human_approved": False,
        "dependency_report": {
            "transformers": {"available": True, "version": "4.x"},
            "peft": {"available": True, "version": "0.x"},
            "trl": {"available": True, "version": "0.x"},
            "accelerate": {"available": True, "version": "1.x"},
            "bitsandbytes": {"available": True, "version": "0.x"},
        },
    }


def test_training_backend_planner_writes_sandbox_invocation_contract(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    plan = spine.plan_training_backend(backend_plan_request())

    assert plan["status"] == "sandbox_backend_plan_ready"
    assert plan["method"] == "qlora"
    assert plan["framework"] == "trl"
    assert plan["production_mutation_allowed"] is False
    assert plan["actual_weight_mutation_allowed"] is False
    assert plan["execution_contract"]["sandbox_required"] is True
    assert "nexusnet.training.sandbox_runner" in " ".join(plan["execution_contract"]["command"])
    assert plan["dependency_report"]["ready"] is True
    assert {"adapter", "merged", "gguf", "quantization_manifest"}.issubset(plan["output_artifact_contract"])
    assert "human_approval" in plan["promotion_gate"]
    assert "sealed_eval_gauntlet" in plan["promotion_gate"]

    plan_dir = tmp_path / "growth" / "production-spine" / "backend_plan_001" / "training-backend-plans" / "coder_qlora_001"
    assert (plan_dir / "training_backend_plan.json").is_file()
    assert (plan_dir / "training_config.json").is_file()
    assert (plan_dir / "training_invocation.ps1").is_file()


def test_training_backend_planner_blocks_unapproved_or_incomplete_runs(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = backend_plan_request()
    request.update(
        {
            "plan_id": "train_backend:blocked",
            "license_state": "pending_review",
            "contains_private_data": True,
            "operator_approved": False,
            "eval_refs": [],
            "hidden_eval_attestation": {"sealed": False, "visible_to_training": True, "leakage_scan": {"status": "failed"}},
            "rollback_ref": "",
            "dependency_report": {"trl": {"available": False}},
        }
    )

    plan = spine.plan_training_backend(request)

    assert plan["status"] == "blocked"
    assert plan["dependency_report"]["ready"] is False
    assert {
        "license_not_approved_for_training",
        "private_data_requires_sanitization_or_operator_approval",
        "operator_approval_required",
        "eval_refs_required",
        "hidden_eval_attestation_required",
        "rollback_ref_required",
        "training_dependencies_missing",
    }.issubset(set(plan["blocked_reasons"]))
    assert plan["production_mutation_allowed"] is False


def test_training_backend_planner_api_and_scorecard_action(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post("/ops/brain/production-spine/training-backend-plans", json=backend_plan_request())

    assert response.status_code == 200
    assert response.json()["status"] == "sandbox_backend_plan_ready"

    scorecard = client.get("/ops/brain/canon/production-spine")
    assert scorecard.status_code == 200
    assert (
        scorecard.json()["operator_actions"]["plan_training_backend"]["endpoint"]
        == "/ops/brain/production-spine/training-backend-plans"
    )
    template = scorecard.json()["training_backend_plan_request_template"]
    assert template["endpoint"] == "/ops/brain/production-spine/training-backend-plans"
    assert template["ready_to_submit"] is True
    assert template["template"]["cycle_id"] == "cycle:backend_plan_001"
    assert template["template"]["plan_id"] == "train_backend:coder_qlora_001"
    assert template["template"]["student_id"] == "student:coder_child_001"
    assert template["template"]["method"] == "qlora"
    assert template["template"]["framework"] == "trl"
    assert template["template"]["support_state"] == "sandbox_backend_plan_ready"
    assert template["template"]["dependency_report"]["ready"] is True
    assert template["template"]["training_config_path"].endswith("training_config.json")
    assert template["template"]["training_invocation_path"].endswith("training_invocation.ps1")
    assert {"adapter", "merged", "gguf", "quantization_manifest"}.issubset(template["template"]["output_contract_targets"])
    assert template["missing_proof_fields"] == []
