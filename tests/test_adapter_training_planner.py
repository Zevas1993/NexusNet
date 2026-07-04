from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.adapters.training_planner import AdapterTrainingPlanRequest, AdapterTrainingPlanner
from tests.test_nexus_phase1_foundation import make_project


def test_adapter_training_planner_creates_shadow_plan_for_local_qlora_with_eval_and_gguf_export():
    planner = AdapterTrainingPlanner()

    plan = planner.plan(
        AdapterTrainingPlanRequest(
            plan_id="training::code-ao-style-v1",
            adapter_id="adapter::code-ao-style-v1",
            dataset_manifest_id="dataset::code-ao-style-v1",
            base_model_id="Qwen/Qwen3.5-27B",
            model_size_billion=27,
            method="qlora",
            framework="peft",
            raw_token_count=1_250_000,
            transformed_example_count=18_000,
            contains_private_data=False,
            license_status="approved",
            operator_approved=True,
            target_hardware={
                "vendor": "nvidia",
                "vram_gb": 24,
                "cuda_available": True,
            },
            export_targets=["adapter", "merged", "gguf"],
            eval_refs=["eval::style-heldout", "eval::tool-routing"],
            provenance_refs=["dataset::code-ao-style-v1", "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md"],
            rollback_adapter_id="adapter::code-ao-style-v0",
        )
    )

    assert plan["status_label"] == "LOCKED CANON"
    assert plan["authority"] == "NexusBrain"
    assert plan["surface_id"] == "adapter-training"
    assert plan["status"] == "planned-shadow"
    assert plan["training_boundary"] == "plan-only-no-weight-update-without-operator-run-command"
    assert plan["hardware_posture"]["state"] == "nvidia-cuda-ready"
    assert [stage["stage_id"] for stage in plan["stages"]] == [
        "data-collection",
        "dataset-engineering",
        "lora-training",
        "evaluation",
        "gguf-export",
    ]
    assert plan["policy_scan"]["summary"]["allow_merge"] is True
    assert {
        "dataset_manifest",
        "prompt_response_pairs",
        "license_privacy_gate",
        "hardware_vram_fit",
        "lora_qlora_config",
        "eval_before_after",
        "gguf_export",
        "rollback_adapter",
    }.issubset(set(plan["required_controls"]))


def test_adapter_training_planner_blocks_private_unlicensed_or_underverified_runs():
    planner = AdapterTrainingPlanner()

    plan = planner.plan(
        {
            "plan_id": "training::unsafe-private-full",
            "adapter_id": "adapter::unsafe-private-full",
            "dataset_manifest_id": "dataset::private-raw-transcripts",
            "base_model_id": "Qwen/Qwen3.5-27B",
            "model_size_billion": 27,
            "method": "full",
            "framework": "other",
            "raw_token_count": 20_000,
            "transformed_example_count": 80,
            "contains_private_data": True,
            "license_status": "needs_review",
            "operator_approved": False,
            "target_hardware": {
                "vendor": "apple",
                "vram_gb": 8,
                "mlx_available": False,
            },
            "export_targets": ["merged"],
            "eval_refs": [],
            "provenance_refs": [],
            "rollback_adapter_id": "",
        }
    )

    assert plan["status"] == "blocked"
    assert plan["hardware_posture"]["state"] == "hardware-insufficient"
    assert plan["policy_scan"]["summary"]["allow_merge"] is False
    assert {
        "adapter_training_private_data_requires_operator_approval",
        "adapter_training_requires_approved_license",
        "adapter_training_requires_eval_refs",
        "adapter_training_requires_more_dataset_examples",
        "adapter_training_full_finetune_blocked_for_mvp",
        "adapter_training_hardware_insufficient",
        "adapter_training_requires_rollback_adapter",
    }.issubset({finding["rule_id"] for finding in plan["training_findings"]})


def test_adapter_training_planner_blocks_dataset_radar_review_blocked_fine_tune_decision():
    planner = AdapterTrainingPlanner()

    plan = planner.plan(
        {
            "plan_id": "training::review-blocked-code-adapter",
            "adapter_id": "adapter::review-blocked-code-adapter",
            "dataset_manifest_id": "dataset::review-blocked-code-adapter",
            "dataset_manifest_status": "needs_review",
            "dataset_radar_training_review_gate": {
                "allowed": False,
                "blocked_source_ids": ["the-stack-v2"],
                "blockers": [
                    {
                        "source_id": "the-stack-v2",
                        "review_state": "review_required",
                        "blocking_fields": ["privacy_evidence"],
                        "reason": "Dataset Radar source review packet has unresolved privacy evidence.",
                    }
                ],
            },
            "fine_tune_decision_status": "blocked",
            "fine_tune_adapter_training_allowed": False,
            "base_model_id": "Qwen/Qwen3.5-9B",
            "model_size_billion": 9,
            "method": "lora",
            "framework": "peft",
            "raw_token_count": 900_000,
            "transformed_example_count": 12_000,
            "contains_private_data": False,
            "license_status": "approved",
            "operator_approved": True,
            "target_hardware": {"vendor": "nvidia", "vram_gb": 16, "cuda_available": True},
            "export_targets": ["adapter"],
            "eval_refs": ["eval::review-blocked-heldout"],
            "provenance_refs": ["dataset::review-blocked-code-adapter"],
            "rollback_adapter_id": "adapter::review-blocked-code-adapter-prev",
        }
    )

    assert plan["status"] == "blocked"
    assert plan["dataset_manifest_status"] == "needs_review"
    assert plan["dataset_radar_training_review_gate"]["allowed"] is False
    assert plan["fine_tune_adapter_training_allowed"] is False
    assert {
        "adapter_training_requires_ready_dataset_manifest",
        "adapter_training_dataset_radar_training_review_blocked",
        "adapter_training_requires_fine_tune_decision_allowance",
    }.issubset({finding["rule_id"] for finding in plan["training_findings"]})

    scorecard = planner.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["blocked_count"] == 1
    assert scorecard["latest_plan"]["status"] == "blocked"


def test_adapter_training_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/adapter-training/plans",
        json={
            "plan_id": "training::api-qora",
            "adapter_id": "adapter::api-qora",
            "dataset_manifest_id": "dataset::api-qora",
            "base_model_id": "Qwen/Qwen3.5-9B",
            "model_size_billion": 9,
            "method": "lora",
            "framework": "peft",
            "raw_token_count": 900_000,
            "transformed_example_count": 12_000,
            "contains_private_data": False,
            "license_status": "approved",
            "operator_approved": True,
            "target_hardware": {"vendor": "nvidia", "vram_gb": 16, "cuda_available": True},
            "export_targets": ["adapter", "gguf"],
            "eval_refs": ["eval::api-heldout"],
            "provenance_refs": ["dataset::api-qora"],
            "rollback_adapter_id": "adapter::api-qora-prev",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "planned-shadow"

    summary = client.get("/ops/brain/adapter-training")
    assert summary.status_code == 200
    assert summary.json()["plan_count"] == 1

    scorecard = client.get("/ops/brain/canon/adapter-training")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["plan"]["endpoint"] == "/ops/brain/adapter-training/plans"
    assert {"data-collection", "dataset-engineering", "lora-training", "evaluation", "gguf-export"}.issubset(
        {stage["stage_id"] for stage in scorecard_payload["canonical_stages"]}
    )

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "adapter-training-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["adapter_training_scorecard"]["plan_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "adapter-training-cockpit"}).json()
    assert blackbox["scorecard_refs"]["adapter_training"] == "/ops/brain/canon/adapter-training"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Adapter Training Planner" in ui.text
    assert "adapterTrainingScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderAdapterTrainingScorecard" in app_js
    assert "/ops/brain/canon/adapter-training" in app_js
    assert "Adapter training DatasetForge review gate" in app_js
    assert "fine_tune_decision_allowance" in app_js
    assert "adapter_training_dataset_radar_training_review_blocked" in app_js
