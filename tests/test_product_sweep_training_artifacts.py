from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_training_reward_specs_eval_reports_and_inventory_are_artifact_backed(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    dataset = client.post(
        "/ops/brain/training/export-dataset",
        json={
            "name": "artifact-loop-dataset",
            "records": [
                {
                    "trace_id": "trace-artifact-loop-1",
                    "prompt": "Route a memory-sensitive prompt.",
                    "output": "Use the memory-weaver capsule with provenance.",
                    "provenance": [{"source": "trace", "id": "trace-artifact-loop-1"}],
                    "teacher_source": {"teacher_id": "qwen3-30b-a3b"},
                    "capsule_source": {"capsule_id": "memory-weaver", "status": "locked"},
                    "safety_labels": ["policy_checked"],
                    "eval_target": "trace-first-evals",
                    "license_metadata": {"status": "candidate_requires_review"},
                }
            ],
        },
    )
    assert dataset.status_code == 200

    reward = client.post(
        "/ops/brain/training/reward-spec",
        json={
            "name": "artifact-loop-reward",
            "objectives": ["trace_completeness", "memory_provenance", "policy_compliance"],
            "metrics": {"trace_completeness": 1.0, "memory_provenance": 1.0},
            "safety_constraints": ["no_unapproved_tool_execution", "no_secret_form_elicitation"],
            "provenance": [{"source": "product-sweep-plan", "phase": "phase-8"}],
        },
    )
    assert reward.status_code == 200
    reward_payload = reward.json()
    assert reward_payload["status"] == "draft_reward_spec"
    assert reward_payload["checkpoint_promotion_ready"] is False
    assert Path(reward_payload["artifact_path"]).exists()

    report = client.post(
        "/ops/brain/training/eval-report",
        json={
            "name": "artifact-loop-eval",
            "dataset_artifact_path": dataset.json()["artifact_path"],
            "reward_spec_path": reward_payload["artifact_path"],
            "scenario_ids": ["route-choice-basic", "memory-recall-temporal"],
            "results": {"route-choice-basic": "passed", "memory-recall-temporal": "passed"},
            "license_status": "candidate_requires_review",
            "security_gate_status": "not_run",
        },
    )
    assert report.status_code == 200
    report_payload = report.json()
    assert report_payload["status"] == "evaluation_report"
    assert report_payload["promotion_recommendation"] == "hold"
    assert {"approved_license_required", "security_gate_pass_required"} <= set(report_payload["blocked_by"])
    assert Path(report_payload["artifact_path"]).exists()

    inventory = client.get("/ops/brain/training/artifacts")
    assert inventory.status_code == 200
    artifact_types = {item["artifact_type"] for item in inventory.json()["artifacts"]}
    assert {"dataset_manifest", "reward_spec", "eval_report"} <= artifact_types
