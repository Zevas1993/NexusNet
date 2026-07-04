from __future__ import annotations

import json

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.growth import NexusNetProductionSpine
from tests.test_nexus_phase1_foundation import make_project


def test_production_spine_executes_all_finish_surfaces_with_gates(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    result = spine.run_completion_cycle(
        {
            "cycle_id": "cycle:cyc_prod_001",
            "target_node_ref": "node:expert_coder",
            "student_id": "student:stu_prod_001",
            "student_kind": "child_expert",
            "capabilities": ["multi_file_patch", "test_repair", "terminal_recovery"],
            "teacher_refs": ["teacher:qwen3-coder-next", "teacher:devstral-2", "node:expert_critique"],
            "operator_approved": False,
            "raw_private_data": "do not persist this value",
        }
    )

    assert result["status_label"] == "LOCKED CANON"
    assert result["surface_id"] == "nexusnet-production-spine"
    assert result["cycle_id"] == "cycle:cyc_prod_001"

    training = result["real_training_runner"]
    assert training["support_state"] == "sandbox_ready"
    assert training["actual_weight_mutation_allowed"] is False
    assert training["blocked_reason"] == "operator_approval_required_for_weight_mutation"
    assert {"lora", "qlora", "dpo", "grpo"}.issubset(set(training["supported_methods"]))

    child_execution = result["child_node_execution"]
    assert child_execution["callable"] is True
    assert child_execution["execution_result"]["used_neural_bus"] is True
    assert child_execution["execution_result"]["used_hive_blackboard"] is True
    assert child_execution["execution_result"]["status"] == "shadow_executed"

    moe = result["native_hive_moe_runtime"]
    assert moe["selected_nodes"] == ["node:expert_coder", "student:stu_prod_001"]
    assert moe["routing_weight_update"]["promotion_required"] is True

    tensor = result["tensor_runtime_kernel"]
    assert tensor["matmul_result"] == [[19, 22], [43, 50]]
    assert tensor["activation_delta"]["l2"] > 0

    teacher = result["teacher_council_automation"]
    assert teacher["license_gate"]["passed"] is True
    assert teacher["disagreement_score"] > 0
    assert teacher["reviewer_window"]["required_windows"] == 4

    evals = result["sealed_eval_gauntlet"]
    assert evals["hidden_eval_opened_by"] == "EvalGauntlet"
    assert evals["student_beats_parent"] is True
    assert evals["student_beats_teacher_council"] is False
    assert evals["promotion_allowed"] is False

    registry = result["durable_node_registry"]
    assert registry["student_state"] == "shadow"
    assert registry["parent_state"] == "active"
    assert registry["rollback_restorable"] is True

    federation = result["federated_learning_loop"]
    assert federation["raw_content_included"] is False
    assert federation["contains_personal_data"] is False
    assert federation["packet_signature"].startswith("sha256:")
    assert federation["shadow_influence_ready"] is True

    dream = result["recursive_dream_execution"]
    assert dream["candidate_count"] == 3
    assert "expert_merge_candidate" in dream["candidate_types"]

    foundry = result["runtime_quantization_foundry"]
    assert foundry["benchmark_count"] == 3
    assert foundry["promotion_allowed"] is False
    assert foundry["best_candidate"]["method"] == "q4_k_m"

    replay = result["deep_replay_ui"]
    assert replay["cycle_replay_ref"].endswith("cycle_replay.json")
    assert "model_genome" in replay["drilldowns"]
    assert "teacher_outputs" in replay["drilldowns"]

    product = result["productization"]
    assert product["buyer_safe_defaults"] is True
    assert product["release_ready"] is False
    assert "real_weight_training_approval" in product["open_gates"]

    replay_file = tmp_path / "growth" / "production-spine" / "cyc_prod_001" / "cycle_replay.json"
    assert replay_file.is_file()


def test_production_spine_api_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/production-spine/cycles",
        json={
            "cycle_id": "cycle:cyc_prod_api_001",
            "target_node_ref": "node:expert_coder",
            "student_id": "student:stu_prod_api_001",
            "student_kind": "child_expert",
            "capabilities": ["multi_file_patch", "test_repair"],
            "teacher_refs": ["teacher:qwen3-coder-next", "teacher:devstral-2", "node:expert_critique"],
            "operator_approved": False,
            "raw_private_data": "must not persist",
        },
    )
    assert response.status_code == 200
    assert response.json()["productization"]["release_ready"] is False

    summary = client.get("/ops/brain/production-spine")
    assert summary.status_code == 200
    assert summary.json()["cycle_count"] == 1

    scorecard = client.get("/ops/brain/canon/production-spine")
    assert scorecard.status_code == 200
    assert scorecard.json()["runtime_state"] == "degraded"
    assert scorecard.json()["blocked_cycle_count"] == 1
    assert scorecard.json()["finish_surface_count"] == 12
    assert scorecard.json()["operator_actions"]["run_sandbox_training"]["endpoint"] == "/ops/brain/production-spine/training-runs"
    assert scorecard.json()["operator_actions"]["assess_real_training_gate"]["endpoint"] == "/ops/brain/production-spine/real-training-gates"
    assert scorecard.json()["operator_actions"]["run_deep_replay"]["endpoint"] == "/ops/brain/production-spine/deep-replay"
    assert scorecard.json()["operator_actions"]["create_project_local_signing_key"]["endpoint"] == "/ops/brain/production-spine/signing-keys/project-local"
    assert scorecard.json()["operator_actions"]["record_reviewer_window"]["endpoint"] == "/ops/brain/production-spine/reviewer-windows"

    blocked_real_training = client.post(
        "/ops/brain/production-spine/real-training-gates",
        json={"cycle_id": "cycle:cyc_prod_api_001", "gate_id": "real_training_blocked"},
    )
    assert blocked_real_training.status_code == 200
    assert blocked_real_training.json()["status"] == "blocked"
    assert "allow_real_weight_mutation_required" in blocked_real_training.json()["blocked_reasons"]
    assert blocked_real_training.json()["artifact_trust_handoff"]["status"] == "blocked"
    assert "artifact_signing_ready_required" in blocked_real_training.json()["artifact_trust_handoff"]["blockers"]
    assert blocked_real_training.json()["execution_started"] is False

    scorecard_after_blocked_real_training = client.get("/ops/brain/canon/production-spine")
    assert scorecard_after_blocked_real_training.status_code == 200
    blocked_gates_by_id = {
        gate["gate_id"]: gate
        for gate in scorecard_after_blocked_real_training.json()["finish_readiness_map"]["gates"]
    }
    blocked_real_training_gate = blocked_gates_by_id["real_training_runner"]
    assert blocked_real_training_gate["status"] == "blocked"
    assert "trusted_artifact_refs_required" in blocked_real_training_gate["blockers"]
    assert "artifact_signing_ready_required" in blocked_real_training_gate["blockers"]
    assert blocked_real_training_gate["next_operator_action"] == "assess_real_training_gate"

    ready_real_training = client.post(
        "/ops/brain/production-spine/real-training-gates",
        json={
            "cycle_id": "cycle:cyc_prod_api_001",
            "gate_id": "real_training_ready",
            "operator_approved": True,
            "human_approved": True,
            "allow_real_weight_mutation": True,
            "license_state": "approved_train",
            "training_backend_plan_ref": "train_backend:ready",
            "dataset_manifest_ref": "dataset:ready",
            "hidden_eval_attestation": {
                "sealed": True,
                "visible_to_training": False,
                "visible_to_teacher_council": False,
                "leakage_scan": {"status": "passed", "train_overlap": 0, "teacher_output_overlap": 0},
            },
            "dependency_report": {
                "transformers": {"available": True, "version": "test"},
                "peft": {"available": True, "version": "test"},
                "accelerate": {"available": True, "version": "test"},
            },
            "artifact_signing_ready": True,
            "artifact_trust_clear": True,
            "artifact_trust_registry_ref": "artifact-trust:api_ready",
            "trusted_artifact_refs": ["artifact:signed_training_plan", "artifact:signed_dataset_manifest"],
        },
    )
    assert ready_real_training.status_code == 200
    assert ready_real_training.json()["status"] == "real_training_gate_ready"
    assert ready_real_training.json()["artifact_trust_handoff"]["status"] == "ready"
    assert ready_real_training.json()["artifact_trust_handoff"]["trusted_artifact_refs"] == ["artifact:signed_training_plan", "artifact:signed_dataset_manifest"]
    assert ready_real_training.json()["production_weight_mutation_allowed"] is True
    assert ready_real_training.json()["execution_started"] is False

    scorecard_after_real_training = client.get("/ops/brain/canon/production-spine")
    assert scorecard_after_real_training.status_code == 200
    assert scorecard_after_real_training.json()["latest_real_training_execution_gate"]["status"] == "real_training_gate_ready"
    gates_by_id = {
        gate["gate_id"]: gate
        for gate in scorecard_after_real_training.json()["finish_readiness_map"]["gates"]
    }
    assert gates_by_id["real_training_runner"]["status"] == "ready"

    reviewer_window = client.post(
        "/ops/brain/production-spine/reviewer-windows",
        json={
            "cycle_id": "cycle:cyc_prod_api_001",
            "advancement_id": "reviewer-window:api_canary_001",
            "eval_id": "eval:api_gauntlet_001",
            "student_id": "student:stu_prod_api_001",
            "window": "canary",
            "window_status": "passed",
            "parent_surpass_rate": 0.96,
            "teacher_surpass_rate": 0.97,
            "lower_confidence_surpass_bound": 0.05,
            "human_approved": False,
            "governance_approved": False,
        },
    )
    assert reviewer_window.status_code == 200
    assert reviewer_window.json()["status"] == "reviewer_window_recorded"
    assert reviewer_window.json()["window"] == "canary"
    assert reviewer_window.json()["teacher_ejection_allowed"] is False
    assert reviewer_window.json()["parent_retirement_allowed"] is False
    assert reviewer_window.json()["ejection_readiness_evidence"]["status"] == "gated"
    assert "post_promotion" in reviewer_window.json()["ejection_readiness_evidence"]["pending_windows"]
    assert reviewer_window.json()["artifacts"]["advancement_path"].endswith("reviewer_window_advancement.json")

    scorecard_after_window = client.get("/ops/brain/canon/production-spine")
    assert scorecard_after_window.status_code == 200
    assert scorecard_after_window.json()["reviewer_window_advancement_count"] == 1
    assert scorecard_after_window.json()["latest_reviewer_window_advancement"]["window"] == "canary"

    seed_hex = "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
    passphrase = "api-project-local-key-passphrase"
    signing_key = client.post(
        "/ops/brain/production-spine/signing-keys/project-local",
        json={"key_id": "api_artifact_signing_key", "seed_hex": seed_hex, "passphrase": passphrase},
    )
    assert signing_key.status_code == 200
    assert signing_key.json()["status"] == "created"
    assert signing_key.json()["encrypted_key_file_persisted"] is True
    assert signing_key.json()["signing_secret_persisted"] is False
    assert seed_hex not in json.dumps(signing_key.json())
    assert passphrase not in json.dumps(signing_key.json())

    signed_replay = client.post(
        "/ops/brain/production-spine/deep-replay",
        json={
            "cycle_id": "cycle:cyc_prod_api_001",
            "replay_id": "replay:api_signed_key_file",
            "signing_key_file": signing_key.json()["key_file_path"],
            "signing_key_passphrase": passphrase,
        },
    )
    assert signed_replay.status_code == 200
    assert signed_replay.json()["signature_policy"]["signing_key_source"] == "project_local_encrypted_key_file"
    assert signed_replay.json()["signature_policy"]["encrypted_key_file_persisted"] is True
    assert signed_replay.json()["signature_policy"]["signing_secret_persisted"] is False
    assert "reviewer_window_history" in signed_replay.json()["drilldowns"]
    assert "real_training_artifact_trust" in signed_replay.json()["drilldowns"]
    assert signed_replay.json()["artifact_type_counts"]["real_training_gate"] >= 1
    assert signed_replay.json()["artifact_type_counts"]["real_training_gate_event_log"] >= 1
    signed_replay_records = [
        json.loads(line)
        for line in open(signed_replay.json()["artifacts"]["artifact_index_path"], encoding="utf-8")
        if line.strip()
    ]
    assert any(record["artifact_type"] == "reviewer_window_advancement" for record in signed_replay_records)
    assert any("reviewer-windows/" in record["relative_path"] for record in signed_replay_records)
    assert any(record["artifact_type"] == "real_training_gate" for record in signed_replay_records)
    assert any(record["artifact_type"] == "real_training_gate_event_log" for record in signed_replay_records)
    assert any("real-training-gates/" in record["relative_path"] for record in signed_replay_records)
    assert seed_hex not in json.dumps(signed_replay.json())
    assert passphrase not in json.dumps(signed_replay.json())

    scorecard_after_signed_replay = client.get("/ops/brain/canon/production-spine")
    assert scorecard_after_signed_replay.status_code == 200
    drilldown_summary = scorecard_after_signed_replay.json()["latest_deep_replay_drilldown_summary"]
    assert drilldown_summary["status"] == "ready"
    assert drilldown_summary["has_real_training_artifact_trust"] is True
    assert "real_training_artifact_trust" in drilldown_summary["drilldowns"]
    assert drilldown_summary["artifact_type_counts"]["real_training_gate"] >= 1
    assert drilldown_summary["artifact_type_counts"]["real_training_gate_event_log"] >= 1
    real_training_template = scorecard_after_signed_replay.json()["real_training_gate_request_template"]
    assert real_training_template["endpoint"] == "/ops/brain/production-spine/real-training-gates"
    assert real_training_template["ready_to_submit"] is False
    assert real_training_template["template"]["cycle_id"] == "cycle:cyc_prod_api_001"
    assert real_training_template["template"]["artifact_signing_ready"] is True
    assert real_training_template["template"]["artifact_trust_clear"] is True
    assert len(real_training_template["template"]["trusted_artifact_refs"]) >= 2
    assert "operator_approved" in real_training_template["manual_approval_fields"]
    assert "human_approved" in real_training_template["manual_approval_fields"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "production-spine-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["production_spine_scorecard"]["cycle_count"] == 1

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Production Spine" in ui.text
    assert "productionSpineScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderProductionSpineScorecard" in app_js
    assert "/ops/brain/canon/production-spine" in app_js
    assert "Reviewer window advancement" in app_js
    assert "latest_reviewer_window_advancement" in app_js
    assert "record_reviewer_window" in app_js
    assert "operatorActions" in app_js
    production_renderer = app_js[
        app_js.index("function renderProductionSpineScorecard"):
        app_js.index("function renderDatasetForgeScorecard")
    ]
    assert "upstream agent opportunity gate" in production_renderer
    assert "upstream_agent_opportunity_gate" in production_renderer

    missing_passphrase = client.post(
        "/ops/brain/production-spine/signing-keys/project-local",
        json={"key_id": "missing_passphrase", "seed_hex": seed_hex},
    )
    assert missing_passphrase.status_code == 200
    assert missing_passphrase.json()["status"] == "blocked"
    assert missing_passphrase.json()["blocked_reason"] == "signing_key_passphrase_required"
    assert missing_passphrase.json()["signing_secret_persisted"] is False
    assert seed_hex not in json.dumps(missing_passphrase.json())

    outside_path = tmp_path / "outside-key.enc.json"
    out_of_root = client.post(
        "/ops/brain/production-spine/signing-keys/project-local",
        json={
            "key_id": "outside_root",
            "seed_hex": seed_hex,
            "passphrase": "operator-passphrase",
            "key_file_path": str(outside_path),
        },
    )
    assert out_of_root.status_code == 200
    assert out_of_root.json()["status"] == "blocked"
    assert out_of_root.json()["blocked_reason"] == "key_file_path_must_be_project_local"
    assert out_of_root.json()["encrypted_key_file_persisted"] is False
    assert not outside_path.exists()
    assert seed_hex not in json.dumps(out_of_root.json())

    training_response = client.post(
        "/ops/brain/production-spine/training-runs",
        json={
            "run_id": "train:proof_api_001",
            "cycle_id": "cycle:cyc_prod_api_001",
            "student_id": "student:stu_prod_api_001",
            "operator_approved": True,
            "training_scope": "sandbox_proof",
            "dataset": [
                {"x": 0.0, "y": 1.0},
                {"x": 1.0, "y": 3.0},
                {"x": 2.0, "y": 5.0},
            ],
        },
    )
    assert training_response.status_code == 200
    assert training_response.json()["status"] == "trained_sandbox_proof"
    assert training_response.json()["production_mutation_allowed"] is False

    child_response = client.post(
        "/ops/brain/production-spine/child-executions",
        json={
            "execution_id": "exec:child_api_001",
            "cycle_id": "cycle:cyc_prod_api_001",
            "student_id": "student:stu_prod_api_001",
            "input": {"x": 4.0},
            "weights_path": training_response.json()["artifacts"]["weights_path"],
        },
    )
    assert child_response.status_code == 200
    assert child_response.json()["status"] == "shadow_executed"
    assert child_response.json()["used_neural_bus"] is True
    assert child_response.json()["production_output_allowed"] is False

    route_response = client.post(
        "/ops/brain/production-spine/hive-moe-routes",
        json={
            "route_id": "route:moe_api_001",
            "cycle_id": "cycle:cyc_prod_api_001",
            "task_features": {"coding": 0.8, "reasoning": 0.5, "risk": 0.2},
            "candidates": [
                {"node_ref": "node:expert_coder", "weights": {"coding": 0.7, "reasoning": 0.1, "risk": -0.2}},
                {"node_ref": "student:stu_prod_api_001", "weights": {"coding": 0.6, "reasoning": 0.5, "risk": -0.1}},
                {"node_ref": "node:expert_writer", "weights": {"coding": 0.1, "reasoning": 0.2, "risk": 0.0}},
            ],
            "top_k": 2,
        },
    )
    assert route_response.status_code == 200
    assert route_response.json()["status"] == "shadow_routed"
    assert route_response.json()["active_route_mutation_allowed"] is False

    tensor_response = client.post(
        "/ops/brain/production-spine/tensor-programs",
        json={
            "program_id": "tensor:program_api_001",
            "cycle_id": "cycle:cyc_prod_api_001",
            "parameter_refs": {"w": "param:w_demo", "b": "param:b_demo"},
            "ops": [
                {"op": "matmul", "name": "projection", "left": [[1, 2], [3, 4]], "right": [[2], [1]]},
                {"op": "relu", "name": "activation", "input": [-1, 0, 3]},
                {"op": "softmax", "name": "gate", "input": [1.0, 2.0, 3.0]},
            ],
        },
    )
    assert tensor_response.status_code == 200
    assert tensor_response.json()["status"] == "executed_tensor_program"
    assert tensor_response.json()["production_parameter_mutation_allowed"] is False

    eval_response = client.post(
        "/ops/brain/production-spine/eval-gauntlets",
        json={
            "eval_id": "eval:gauntlet_api_001",
            "cycle_id": "cycle:cyc_prod_api_001",
            "student_id": "student:stu_prod_api_001",
            "parent_node_ref": "node:expert_coder",
            "weights_path": training_response.json()["artifacts"]["weights_path"],
            "hidden_eval_cases": [
                {"x": 4.0, "y": 9.0, "parent_prediction": 7.5, "teacher_prediction": 8.0},
                {"x": 5.0, "y": 11.0, "parent_prediction": 9.0, "teacher_prediction": 10.0},
                {"x": 6.0, "y": 13.0, "parent_prediction": 10.5, "teacher_prediction": 12.0},
            ],
            "teacher_license_gate_passed": True,
            "human_approved": False,
        },
    )
    assert eval_response.status_code == 200
    assert eval_response.json()["status"] == "sealed_eval_complete"
    assert eval_response.json()["promotion_allowed"] is False

    registry_response = client.post(
        "/ops/brain/production-spine/node-registry-decisions",
        json={
            "decision_id": "decision:blocked_api",
            "cycle_id": "cycle:cyc_prod_api_001",
            "student_id": "student:stu_prod_api_001",
            "parent_node_ref": "node:expert_coder",
            "eval_scorecard_path": eval_response.json()["artifacts"]["eval_scorecard_path"],
            "action": "promote_child",
            "human_approved": True,
        },
    )
    assert registry_response.status_code == 200
    assert registry_response.json()["decision"] == "blocked"
    assert "eval_promotion_not_allowed" in registry_response.json()["blocked_reasons"]

    federated_response = client.post(
        "/ops/brain/production-spine/federated-packets",
        json={
            "packet_id": "fed:packet_api_001",
            "cycle_id": "cycle:cyc_prod_api_001",
            "source_node_ref": "node:expert_coder",
            "consent_granted": True,
            "local_metrics": {"success_rate": 0.84, "failure_rate": 0.05, "latency_ms": 120.0, "sample_count": 50},
            "capability_tags": ["multi_file_patch", "test_repair"],
            "raw_prompt": "must not persist",
        },
    )
    assert federated_response.status_code == 200
    assert federated_response.json()["status"] == "accepted_sanitized_packet"
    assert federated_response.json()["raw_content_included"] is False

    dream_response = client.post(
        "/ops/brain/production-spine/dream-cycles",
        json={
            "dream_id": "dream:cycle_api_001",
            "cycle_id": "cycle:cyc_prod_api_001",
            "target_node_ref": "node:expert_coder",
            "student_id": "student:stu_dream_api",
            "failure_refs": ["failure:multi_file_patch_edge_case"],
            "federated_packet_signature": federated_response.json()["packet_signature"],
            "dream_temperature": 0.95,
            "critic_temperature": 0.15,
        },
    )
    assert dream_response.status_code == 200
    assert dream_response.json()["status"] == "dream_candidates_materialized"
    assert dream_response.json()["production_mutation_allowed"] is False

    foundry_response = client.post(
        "/ops/brain/production-spine/runtime-benchmarks",
        json={
            "benchmark_id": "bench:runtime_api_001",
            "cycle_id": "cycle:cyc_prod_api_001",
            "model_ref": "model:nexusnet-child-demo",
            "hardware_profile": {"device": "local_cpu", "memory_gb": 16},
            "baseline_quality_score": 0.93,
            "candidates": [
                {"method": "q4_k_m", "backend": "llama.cpp", "tokens_per_second": 45.0, "memory_gb": 4.8, "quality_score": 0.91, "kv_cache": "quantized_kv"},
                {"method": "q5_k_m", "backend": "llama.cpp", "tokens_per_second": 38.0, "memory_gb": 5.8, "quality_score": 0.935, "kv_cache": "low_rank_kv"},
            ],
            "backend_run_verified": True,
            "human_approved": False,
        },
    )
    assert foundry_response.status_code == 200
    assert foundry_response.json()["status"] == "benchmark_complete"
    assert foundry_response.json()["production_runtime_mutation_allowed"] is False

    replay_response = client.post(
        "/ops/brain/production-spine/deep-replay",
        json={"cycle_id": "cycle:cyc_prod_api_001", "replay_id": "replay:bundle_api_001"},
    )
    assert replay_response.status_code == 200
    assert replay_response.json()["status"] == "deep_replay_ready"
    assert replay_response.json()["developer_visible"] is True

    productization_response = client.post(
        "/ops/brain/production-spine/productization-readiness",
        json={
            "readiness_id": "release:blocked_api",
            "cycle_id": "cycle:cyc_prod_api_001",
            "local_cache_controls": True,
            "secret_scan_passed": False,
            "model_download_manager": True,
            "support_bundle": False,
            "crash_diagnostics": True,
            "ci_packaging": False,
            "buyer_launcher": True,
            "docs_complete": False,
            "buyer_safe_defaults": True,
            "runtime_gates_clear": False,
        },
    )
    assert productization_response.status_code == 200
    assert productization_response.json()["release_ready"] is False
    assert "secret_scan_passed" in productization_response.json()["open_gates"]

    teacher_response = client.post(
        "/ops/brain/production-spine/teacher-council-reviews",
        json={
            "review_id": "teacher:review_api_001",
            "cycle_id": "cycle:cyc_prod_api_001",
            "target_node_ref": "node:expert_coder",
            "teacher_outputs": [
                {"teacher_ref": "teacher:qwen3-coder-next", "license_state": "approved_train", "score": 0.88, "output_ref": "out:qwen"},
                {"teacher_ref": "node:expert_critique", "license_state": "internal", "score": 0.91, "output_ref": "out:critique"},
            ],
            "validator_results": [{"validator_ref": "validator:unit_tests", "passed": True, "score": 1.0}],
        },
    )
    assert teacher_response.status_code == 200
    assert teacher_response.json()["status"] == "teacher_review_complete"
    assert teacher_response.json()["license_gate"]["passed"] is True


def test_sandbox_training_proof_mutates_tiny_weights_without_production_promotion(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    report = spine.run_sandbox_training_proof(
        {
            "run_id": "train:proof_001",
            "cycle_id": "cycle:cyc_prod_001",
            "student_id": "student:stu_prod_001",
            "operator_approved": True,
            "training_scope": "sandbox_proof",
            "dataset": [
                {"x": 0.0, "y": 1.0},
                {"x": 1.0, "y": 3.0},
                {"x": 2.0, "y": 5.0},
                {"x": 3.0, "y": 7.0},
            ],
            "raw_private_data": "must not be persisted",
        }
    )

    assert report["status"] == "trained_sandbox_proof"
    assert report["support_state"] == "sandbox_supported"
    assert report["actual_weight_mutation_allowed"] is True
    assert report["production_mutation_allowed"] is False
    assert report["privacy_scan"]["raw_private_data_persisted"] is False
    assert report["loss"]["initial"] > report["loss"]["final"]
    assert report["weights"]["w"] > 1.5
    assert report["weights"]["b"] > 0.5
    assert report["checkpoint"]["hash"].startswith("sha256:")
    assert report["artifacts"]["weights_path"].endswith("weights.json")

    run_dir = tmp_path / "growth" / "production-spine" / "cyc_prod_001" / "sandbox-training" / "proof_001"
    assert (run_dir / "weights.json").is_file()
    assert (run_dir / "loss_trace.jsonl").is_file()
    assert (run_dir / "training_report.json").is_file()
    assert "must not be persisted" not in (run_dir / "training_report.json").read_text(encoding="utf-8")


def test_sandbox_training_proof_blocks_without_operator_approval_or_private_data(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    report = spine.run_sandbox_training_proof(
        {
            "run_id": "train:proof_blocked",
            "cycle_id": "cycle:cyc_prod_blocked",
            "student_id": "student:stu_prod_blocked",
            "operator_approved": False,
            "training_scope": "sandbox_proof",
            "dataset": [{"x": 0.0, "y": 1.0}],
            "contains_private_data": True,
        }
    )

    assert report["status"] == "blocked"
    assert report["actual_weight_mutation_allowed"] is False
    assert "operator_approval_required" in report["blocked_reasons"]
    assert "private_data_not_allowed_in_sandbox_proof" in report["blocked_reasons"]
    assert not (tmp_path / "growth" / "production-spine" / "cyc_prod_blocked" / "sandbox-training" / "proof_blocked" / "weights.json").exists()


def test_child_node_execution_uses_sandbox_weights_neural_bus_and_blackboard(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    training = spine.run_sandbox_training_proof(
        {
            "run_id": "train:proof_child_exec",
            "cycle_id": "cycle:cyc_child_exec",
            "student_id": "student:stu_child_exec",
            "operator_approved": True,
            "training_scope": "sandbox_proof",
            "dataset": [
                {"x": 0.0, "y": 1.0},
                {"x": 1.0, "y": 3.0},
                {"x": 2.0, "y": 5.0},
                {"x": 3.0, "y": 7.0},
            ],
        }
    )

    execution = spine.execute_child_node(
        {
            "execution_id": "exec:child_001",
            "cycle_id": "cycle:cyc_child_exec",
            "student_id": "student:stu_child_exec",
            "input": {"x": 4.0},
            "weights_path": training["artifacts"]["weights_path"],
        }
    )

    assert execution["status"] == "shadow_executed"
    assert execution["used_neural_bus"] is True
    assert execution["used_hive_blackboard"] is True
    assert execution["production_output_allowed"] is False
    assert 8.5 < execution["prediction"] < 9.5
    assert execution["route_decision"]["selected_node"] == "student:stu_child_exec"
    assert execution["evaluator_hook"]["required_before_promotion"] is True
    assert execution["child_execution_replay_evidence"]["status"] == "ready"
    assert execution["child_execution_replay_evidence"]["callable_runtime_verified"] is True
    assert execution["child_execution_replay_evidence"]["weights_source"] == "sandbox_proof_weights"
    assert execution["child_execution_replay_evidence"]["runtime_pathway"]["used_neural_bus"] is True
    assert execution["child_execution_replay_evidence"]["mutation_boundary"] == "shadow-child-execution-only-no-production-output-or-node-registry-mutation"
    assert execution["child_execution_replay_evidence"]["input_digest"].startswith("sha256:")
    assert execution["child_execution_replay_evidence"]["weights_hash"].startswith("sha256:")

    exec_dir = tmp_path / "growth" / "production-spine" / "cyc_child_exec" / "child-executions" / "child_001"
    assert (exec_dir / "neural_bus.jsonl").is_file()
    assert (exec_dir / "hive_blackboard.json").is_file()
    assert (exec_dir / "execution_report.json").is_file()


def test_child_node_execution_blocks_missing_or_untrusted_weights(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    execution = spine.execute_child_node(
        {
            "execution_id": "exec:blocked_child",
            "cycle_id": "cycle:cyc_child_blocked",
            "student_id": "student:stu_child_blocked",
            "input": {"x": 4.0},
            "weights_path": str(tmp_path / "missing-weights.json"),
        }
    )

    assert execution["status"] == "blocked"
    assert "weights_missing_or_untrusted" in execution["blocked_reasons"]
    assert execution["production_output_allowed"] is False


def test_hive_moe_shadow_route_executes_sparse_top_k_and_writes_route_artifacts(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    route = spine.run_hive_moe_shadow_route(
        {
            "route_id": "route:moe_001",
            "cycle_id": "cycle:cyc_moe_route",
            "task_features": {
                "coding": 0.8,
                "reasoning": 0.5,
                "risk": 0.2,
            },
            "candidates": [
                {"node_ref": "node:expert_coder", "weights": {"coding": 0.7, "reasoning": 0.1, "risk": -0.2}},
                {"node_ref": "student:stu_child_exec", "weights": {"coding": 0.6, "reasoning": 0.5, "risk": -0.1}},
                {"node_ref": "node:expert_writer", "weights": {"coding": 0.1, "reasoning": 0.2, "risk": 0.0}},
            ],
            "top_k": 2,
        }
    )

    assert route["status"] == "shadow_routed"
    assert route["selected_nodes"] == ["student:stu_child_exec", "node:expert_coder"]
    assert route["top_k"] == 2
    assert route["active_route_mutation_allowed"] is False
    assert route["routing_weight_update"]["promotion_required"] is True
    assert route["route_quality"]["confidence"] > 0
    assert route["hive_route_replay_evidence"]["status"] == "ready"
    assert route["hive_route_replay_evidence"]["routing_mode"] == "native_hive_moe_sparse_top_k"
    assert route["hive_route_replay_evidence"]["selected_nodes"] == route["selected_nodes"]
    assert route["hive_route_replay_evidence"]["task_feature_digest"].startswith("sha256:")
    assert route["hive_route_replay_evidence"]["mutation_boundary"] == "shadow-route-only-no-active-router-weight-mutation"
    assert route["hive_route_replay_evidence"]["routing_weight_update"]["promotion_required"] is True

    route_dir = tmp_path / "growth" / "production-spine" / "cyc_moe_route" / "hive-moe-routes" / "moe_001"
    assert (route_dir / "route_decision.json").is_file()
    assert (route_dir / "route_events.jsonl").is_file()


def test_hive_tensor_program_executes_graph_ops_and_optimizer_state(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    tensor = spine.execute_tensor_program(
        {
            "program_id": "tensor:program_001",
            "cycle_id": "cycle:cyc_tensor_kernel",
            "parameter_refs": {"w": "param:w_demo", "b": "param:b_demo"},
            "ops": [
                {"op": "matmul", "name": "projection", "left": [[1, 2], [3, 4]], "right": [[2], [1]]},
                {"op": "relu", "name": "activation", "input": [-1, 0, 3]},
                {"op": "softmax", "name": "gate", "input": [1.0, 2.0, 3.0]},
                {"op": "linear_update", "name": "optimizer_step", "w": 0.0, "b": 0.0, "x": 2.0, "y": 5.0, "learning_rate": 0.1},
            ],
        }
    )

    assert tensor["status"] == "executed_tensor_program"
    assert tensor["op_count"] == 4
    assert tensor["results"]["projection"] == [[4], [10]]
    assert tensor["results"]["activation"] == [0, 0, 3]
    assert round(sum(tensor["results"]["gate"]), 6) == 1.0
    assert tensor["optimizer_state"]["updated_parameters"]["w"] > 0
    assert tensor["production_parameter_mutation_allowed"] is False
    assert tensor["tensor_runtime_replay_evidence"]["status"] == "ready"
    assert tensor["tensor_runtime_replay_evidence"]["op_count"] == 4
    assert tensor["tensor_runtime_replay_evidence"]["parameter_refs"]["w"] == "param:w_demo"
    assert tensor["tensor_runtime_replay_evidence"]["optimizer_state"]["optimizer"] == "shadow_sgd_v0"
    assert tensor["tensor_runtime_replay_evidence"]["checkpoint"]["hash"].startswith("sha256:")
    assert tensor["tensor_runtime_replay_evidence"]["mutation_boundary"] == "shadow-tensor-program-only-no-production-parameter-mutation"

    tensor_dir = tmp_path / "growth" / "production-spine" / "cyc_tensor_kernel" / "tensor-programs" / "program_001"
    assert (tensor_dir / "tensor_program_report.json").is_file()
    assert (tensor_dir / "tensor_trace.jsonl").is_file()


def test_sealed_eval_gauntlet_compares_child_parent_and_teacher_with_reviewer_bounds(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    training = spine.run_sandbox_training_proof(
        {
            "run_id": "train:proof_eval",
            "cycle_id": "cycle:cyc_eval_gauntlet",
            "student_id": "student:stu_eval",
            "operator_approved": True,
            "training_scope": "sandbox_proof",
            "dataset": [
                {"x": 0.0, "y": 1.0},
                {"x": 1.0, "y": 3.0},
                {"x": 2.0, "y": 5.0},
                {"x": 3.0, "y": 7.0},
            ],
        }
    )

    eval_report = spine.run_sealed_eval_review(
        {
            "eval_id": "eval:gauntlet_001",
            "cycle_id": "cycle:cyc_eval_gauntlet",
            "student_id": "student:stu_eval",
            "parent_node_ref": "node:expert_coder",
            "weights_path": training["artifacts"]["weights_path"],
            "hidden_eval_cases": [
                {"x": 4.0, "y": 9.0, "parent_prediction": 7.5, "teacher_prediction": 8.0},
                {"x": 5.0, "y": 11.0, "parent_prediction": 9.0, "teacher_prediction": 10.0},
                {"x": 6.0, "y": 13.0, "parent_prediction": 10.5, "teacher_prediction": 12.0},
            ],
            "teacher_license_gate_passed": True,
            "human_approved": False,
        }
    )

    assert eval_report["status"] == "sealed_eval_complete"
    assert eval_report["hidden_eval_visible_to_training"] is False
    assert eval_report["student_beats_parent"] is True
    assert eval_report["student_beats_teacher_council"] is True
    assert eval_report["promotion_allowed"] is False
    assert eval_report["teacher_ejection_allowed"] is False
    assert eval_report["reviewer_monitor"]["windows_required"] == 4
    assert eval_report["reviewer_consistency"]["passed_window_count"] == 1
    assert eval_report["reviewer_consistency"]["pending_window_count"] == 3
    assert eval_report["reviewer_consistency"]["teacher_ejection_eligible"] is False
    assert eval_report["reviewer_consistency"]["reviewer_windows_path"].endswith("reviewer_windows.jsonl")
    assert eval_report["reviewer_confidence_evidence"]["status"] == "ready"
    assert eval_report["reviewer_confidence_evidence"]["parent_surpass_rate"] == 1.0
    assert eval_report["reviewer_confidence_evidence"]["teacher_surpass_rate"] == 1.0
    assert eval_report["reviewer_confidence_evidence"]["lower_confidence_surpass_bound"] > 0
    assert eval_report["reviewer_confidence_evidence"]["teacher_ejection_eligible"] is False
    assert eval_report["reviewer_confidence_evidence"]["teacher_ejection_blocker"] == "teacher_ejection_requires_post_promotion_consistency_windows"
    assert eval_report["reviewer_confidence_evidence"]["ejection_readiness_evidence"]["status"] == "gated"
    assert eval_report["reviewer_confidence_evidence"]["ejection_readiness_evidence"]["teacher_ejection_allowed"] is False
    assert eval_report["ejection_readiness_evidence"]["status"] == "gated"
    assert eval_report["ejection_readiness_evidence"]["parent_retirement_allowed"] is False
    assert eval_report["ejection_readiness_evidence"]["pending_window_count"] == 3
    assert eval_report["lower_confidence_surpass_bound"] > 0
    assert eval_report["score_comparison"]["student_score"] == eval_report["student_score"]
    assert eval_report["score_comparison"]["student_parent_surpass_margin"] > 0
    assert eval_report["score_comparison"]["student_teacher_surpass_margin"] > 0
    assert eval_report["score_comparison"]["comparison_matrix_path"].endswith("comparison_matrix.json")
    assert eval_report["hidden_eval_attestation"]["leakage_scan"]["status"] == "passed"
    assert eval_report["hidden_eval_attestation"]["case_count"] == 3

    eval_dir = tmp_path / "growth" / "production-spine" / "cyc_eval_gauntlet" / "eval-gauntlets" / "gauntlet_001"
    assert (eval_dir / "eval_scorecard.json").is_file()
    assert (eval_dir / "hidden_eval_attestation.json").is_file()
    attestation = json.loads((eval_dir / "hidden_eval_attestation.json").read_text(encoding="utf-8"))
    assert attestation["leakage_scan"]["train_overlap"] == 0
    assert attestation["leakage_scan"]["teacher_output_overlap"] == 0
    assert attestation["leakage_scan"]["status"] == "passed"
    assert (eval_dir / "comparison_matrix.json").is_file()
    assert (eval_dir / "reviewer_windows.jsonl").is_file()


def test_durable_node_registry_promotes_child_and_retires_parent_with_rollback(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    training = spine.run_sandbox_training_proof(
        {
            "run_id": "train:proof_registry",
            "cycle_id": "cycle:cyc_registry",
            "student_id": "student:stu_registry",
            "operator_approved": True,
            "training_scope": "sandbox_proof",
            "dataset": [
                {"x": 0.0, "y": 1.0},
                {"x": 1.0, "y": 3.0},
                {"x": 2.0, "y": 5.0},
                {"x": 3.0, "y": 7.0},
            ],
        }
    )
    eval_report = spine.run_sealed_eval_review(
        {
            "eval_id": "eval:registry_001",
            "cycle_id": "cycle:cyc_registry",
            "student_id": "student:stu_registry",
            "parent_node_ref": "node:expert_coder",
            "weights_path": training["artifacts"]["weights_path"],
            "hidden_eval_cases": [
                {"x": 4.0, "y": 9.0, "parent_prediction": 6.0, "teacher_prediction": 7.5},
                {"x": 5.0, "y": 11.0, "parent_prediction": 7.0, "teacher_prediction": 9.5},
                {"x": 6.0, "y": 13.0, "parent_prediction": 8.0, "teacher_prediction": 11.5},
            ],
            "teacher_license_gate_passed": True,
            "human_approved": True,
        }
    )

    blocked_without_adapter_trust = spine.apply_node_registry_decision(
        {
            "decision_id": "decision:promote_registry_blocked_adapter_trust",
            "cycle_id": "cycle:cyc_registry",
            "student_id": "student:stu_registry",
            "parent_node_ref": "node:expert_coder",
            "eval_scorecard_path": eval_report["artifacts"]["eval_scorecard_path"],
            "action": "promote_child",
            "human_approved": True,
        }
    )

    assert blocked_without_adapter_trust["decision"] == "blocked"
    assert "adapter_artifact_trust_clear_required" in blocked_without_adapter_trust["blocked_reasons"]
    assert blocked_without_adapter_trust["adapter_artifact_trust_status"] == "not_recorded"
    assert blocked_without_adapter_trust["adapter_artifact_trust_clear"] is False
    assert blocked_without_adapter_trust["node_registry_replay_evidence"]["adapter_artifact_trust_status"] == "not_recorded"
    assert blocked_without_adapter_trust["node_registry_replay_evidence"]["adapter_artifact_trust_clear"] is False

    promotion = spine.apply_node_registry_decision(
        {
            "decision_id": "decision:promote_registry",
            "cycle_id": "cycle:cyc_registry",
            "student_id": "student:stu_registry",
            "parent_node_ref": "node:expert_coder",
            "eval_scorecard_path": eval_report["artifacts"]["eval_scorecard_path"],
            "action": "promote_child",
            "adapter_artifact_trust_status": "trusted",
            "adapter_artifact_trust_clear": True,
            "human_approved": True,
        }
    )

    assert promotion["decision"] == "promote_child"
    assert promotion["student_state"] == "permanent_active"
    assert promotion["parent_state"] == "active"
    assert promotion["rollback_restorable"] is True
    assert promotion["adapter_artifact_trust_status"] == "trusted"
    assert promotion["adapter_artifact_trust_clear"] is True
    assert promotion["node_registry_replay_evidence"]["status"] == "ready"
    assert promotion["node_registry_replay_evidence"]["student_state"] == "permanent_active"
    assert promotion["node_registry_replay_evidence"]["adapter_artifact_trust_status"] == "trusted"
    assert promotion["node_registry_replay_evidence"]["adapter_artifact_trust_clear"] is True
    assert promotion["node_registry_replay_evidence"]["parent_retirement_allowed"] is False
    assert promotion["node_registry_replay_evidence"]["rollback_restorable"] is True
    assert promotion["canary_promotion_guard_evidence"]["status"] == "gated"
    assert promotion["canary_promotion_guard_evidence"]["active_deployment_allowed"] is False
    assert "shadow_runtime_window_required" in promotion["canary_promotion_guard_evidence"]["blockers"]
    assert "canary_window_required" in promotion["canary_promotion_guard_evidence"]["blockers"]

    canary_promotion = spine.apply_node_registry_decision(
        {
            "decision_id": "decision:promote_registry_canary",
            "cycle_id": "cycle:cyc_registry",
            "student_id": "student:stu_registry",
            "parent_node_ref": "node:expert_coder",
            "eval_scorecard_path": eval_report["artifacts"]["eval_scorecard_path"],
            "action": "promote_child",
            "adapter_artifact_trust_status": "trusted",
            "adapter_artifact_trust_clear": True,
            "human_approved": True,
            "shadow_runtime_window_passed": True,
            "canary_window_passed": True,
        }
    )

    assert canary_promotion["canary_promotion_guard_evidence"]["status"] == "ready"
    assert canary_promotion["canary_promotion_guard_evidence"]["active_deployment_allowed"] is True
    assert canary_promotion["node_registry_replay_evidence"]["canary_promotion_guard_evidence"]["status"] == "ready"

    retirement_without_reviewer_windows = spine.apply_node_registry_decision(
        {
            "decision_id": "decision:retire_parent",
            "cycle_id": "cycle:cyc_registry",
            "student_id": "student:stu_registry",
            "parent_node_ref": "node:expert_coder",
            "eval_scorecard_path": eval_report["artifacts"]["eval_scorecard_path"],
            "action": "retire_parent",
            "adapter_artifact_trust_status": "trusted",
            "adapter_artifact_trust_clear": True,
            "human_approved": True,
            "ivy_grade_review_passed": True,
            "greatly_outperforms_parent": True,
        }
    )

    assert retirement_without_reviewer_windows["decision"] == "blocked"
    assert "reviewer_window_advancement_required_for_parent_retirement" in retirement_without_reviewer_windows["blocked_reasons"]
    assert retirement_without_reviewer_windows["parent_retirement_allowed"] is False
    assert retirement_without_reviewer_windows["reviewer_window_retirement_evidence"]["status"] == "blocked"

    reviewer_window = spine.record_reviewer_window_advancement(
        {
            "cycle_id": "cycle:cyc_registry",
            "advancement_id": "reviewer-window:registry_post_promotion",
            "eval_id": "eval:registry_001",
            "student_id": "student:stu_registry",
            "window": "post_promotion",
            "window_status": "passed",
            "passed_windows": ["initial_eval", "shadow_runtime", "canary"],
            "parent_surpass_rate": 1.0,
            "teacher_surpass_rate": 1.0,
            "lower_confidence_surpass_bound": 0.05,
            "teacher_ejection_review_requested": True,
            "parent_retirement_review_requested": True,
            "human_approved": True,
            "governance_approved": True,
        }
    )
    assert reviewer_window["ejection_readiness_evidence"]["status"] == "ready"
    assert reviewer_window["parent_retirement_allowed"] is True

    retirement = spine.apply_node_registry_decision(
        {
            "decision_id": "decision:retire_parent_with_reviewer_windows",
            "cycle_id": "cycle:cyc_registry",
            "student_id": "student:stu_registry",
            "parent_node_ref": "node:expert_coder",
            "eval_scorecard_path": eval_report["artifacts"]["eval_scorecard_path"],
            "reviewer_window_advancement_path": reviewer_window["artifacts"]["advancement_path"],
            "action": "retire_parent",
            "adapter_artifact_trust_status": "trusted",
            "adapter_artifact_trust_clear": True,
            "human_approved": True,
            "ivy_grade_review_passed": True,
            "greatly_outperforms_parent": True,
        }
    )

    assert retirement["decision"] == "retire_parent"
    assert retirement["student_state"] == "permanent_active"
    assert retirement["parent_state"] == "retired_rollback_restorable"
    assert retirement["parent_retirement_allowed"] is True
    assert retirement["adapter_artifact_trust_status"] == "trusted"
    assert retirement["adapter_artifact_trust_clear"] is True
    assert retirement["reviewer_window_retirement_evidence"]["status"] == "ready"
    assert retirement["reviewer_window_retirement_evidence"]["parent_retirement_allowed"] is True
    assert retirement["node_registry_replay_evidence"]["parent_state"] == "retired_rollback_restorable"
    assert retirement["node_registry_replay_evidence"]["parent_retirement_allowed"] is True
    assert retirement["node_registry_replay_evidence"]["adapter_artifact_trust_status"] == "trusted"
    assert retirement["node_registry_replay_evidence"]["adapter_artifact_trust_clear"] is True
    assert retirement["node_registry_replay_evidence"]["reviewer_window_retirement_evidence"]["status"] == "ready"
    assert retirement["node_registry_replay_evidence"]["mutation_boundary"] == "node-registry-mutation-only-after-eval-human-approval-with-rollback"
    assert retirement["canary_promotion_guard_evidence"]["active_deployment_allowed"] is False
    assert "post_promotion_window_required_for_parent_retirement" in retirement["canary_promotion_guard_evidence"]["blockers"]

    registry_dir = tmp_path / "growth" / "production-spine" / "cyc_registry" / "node-registry"
    assert (registry_dir / "active_node_registry.json").is_file()
    assert (registry_dir / "node_registry_events.jsonl").is_file()
    assert (registry_dir / "rollback_snapshot.json").is_file()

    snapshot = spine.node_registry_snapshot(
        {
            "snapshot_id": "snapshot:registry_adapter_trust",
            "cycle_id": "cycle:cyc_registry",
        }
    )

    assert snapshot["adapter_artifact_trust_status"] == "trusted"
    assert snapshot["adapter_artifact_trust_clear"] is True
    assert snapshot["active_roster"]["student:stu_registry"]["adapter_artifact_trust_status"] == "trusted"
    assert snapshot["active_roster"]["student:stu_registry"]["adapter_artifact_trust_clear"] is True


def test_reviewer_window_advancement_blocks_unknown_passed_windows_without_crashing(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    reviewer_window = spine.record_reviewer_window_advancement(
        {
            "cycle_id": "cycle:cyc_registry",
            "advancement_id": "reviewer-window:bad_passed_window",
            "eval_id": "eval:registry_001",
            "student_id": "student:stu_registry",
            "window": "canary",
            "window_status": "passed",
            "passed_windows": ["initial_eval", "unknown_window"],
            "lower_confidence_surpass_bound": 0.05,
            "teacher_ejection_review_requested": True,
            "human_approved": True,
            "governance_approved": True,
        }
    )

    assert reviewer_window["status"] == "blocked"
    assert "reviewer_window_unknown_passed_window" in reviewer_window["blocked_reasons"]
    assert reviewer_window["ejection_readiness_evidence"]["passed_windows"] == ["initial_eval", "canary"]
    assert reviewer_window["ejection_readiness_evidence"]["teacher_ejection_allowed"] is False


def test_federated_learning_loop_writes_signed_sanitized_packet_and_shadow_influence(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    packet = spine.submit_federated_influence_packet(
        {
            "packet_id": "fed:packet_001",
            "cycle_id": "cycle:cyc_federation",
            "source_node_ref": "node:expert_coder",
            "consent_granted": True,
            "local_metrics": {
                "success_rate": 0.84,
                "failure_rate": 0.05,
                "latency_ms": 120.0,
                "sample_count": 50,
            },
            "capability_tags": ["multi_file_patch", "test_repair"],
            "raw_prompt": "private content must not persist",
            "raw_output": "private output must not persist",
        }
    )

    assert packet["status"] == "accepted_sanitized_packet"
    assert packet["raw_content_included"] is False
    assert packet["contains_personal_data"] is False
    assert packet["packet_signature"].startswith("sha256:")
    assert packet["secure_aggregation_ready"] is True
    assert packet["differential_privacy"]["enabled"] is True
    assert packet["poisoning_scan"]["passed"] is True
    assert packet["trust_score"] > 0.5
    assert packet["shadow_routing_influence"]["active_route_mutation_allowed"] is False
    assert packet["federated_influence_replay_evidence"]["status"] == "ready"
    assert packet["federated_influence_replay_evidence"]["consent_granted"] is True
    assert packet["federated_influence_replay_evidence"]["differential_privacy"]["enabled"] is True
    assert packet["federated_influence_replay_evidence"]["poisoning_scan"]["passed"] is True
    assert packet["federated_influence_replay_evidence"]["trust_score"] == packet["trust_score"]
    assert packet["federated_influence_replay_evidence"]["mutation_boundary"] == "sanitized-federated-influence-only-no-active-routing-without-promotion"

    packet_dir = tmp_path / "growth" / "production-spine" / "cyc_federation" / "federation"
    assert (packet_dir / "sanitized_packets.jsonl").is_file()
    assert (packet_dir / "secure_aggregate.json").is_file()
    assert "private content must not persist" not in (packet_dir / "sanitized_packets.jsonl").read_text(encoding="utf-8")


def test_federated_learning_loop_blocks_without_consent(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    packet = spine.submit_federated_influence_packet(
        {
            "packet_id": "fed:blocked",
            "cycle_id": "cycle:cyc_federation_blocked",
            "source_node_ref": "node:expert_coder",
            "consent_granted": False,
            "local_metrics": {"success_rate": 0.84},
        }
    )

    assert packet["status"] == "blocked"
    assert "federation_consent_required" in packet["blocked_reasons"]
    assert packet["shadow_routing_influence"]["active_route_mutation_allowed"] is False
    assert packet["federated_influence_replay_evidence"]["status"] == "blocked"
    assert packet["federated_influence_replay_evidence"]["consent_granted"] is False


def test_recursive_dream_cycle_materializes_candidates_and_growth_seed(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    packet = spine.submit_federated_influence_packet(
        {
            "packet_id": "fed:dream_seed",
            "cycle_id": "cycle:cyc_dream",
            "source_node_ref": "node:expert_coder",
            "consent_granted": True,
            "local_metrics": {"success_rate": 0.72, "failure_rate": 0.18, "latency_ms": 200.0, "sample_count": 40},
            "capability_tags": ["test_repair"],
        }
    )

    dream = spine.run_recursive_dream_cycle(
        {
            "dream_id": "dream:cycle_001",
            "cycle_id": "cycle:cyc_dream",
            "target_node_ref": "node:expert_coder",
            "student_id": "student:stu_dream_candidate",
            "failure_refs": ["failure:multi_file_patch_edge_case"],
            "federated_packet_signature": packet["packet_signature"],
            "knowledge_artifact_refs": ["kac://architecture_review/abc123"],
            "dream_temperature": 0.95,
            "critic_temperature": 0.15,
        }
    )

    assert dream["status"] == "dream_candidates_materialized"
    assert dream["dream_temperature"] > dream["critic_temperature"]
    assert dream["candidate_count"] == 3
    assert "expert_merge_candidate" in dream["candidate_types"]
    assert "runtime_method_candidate" in dream["candidate_types"]
    assert dream["growth_seed"]["student_kind"] == "child_expert"
    assert dream["compiled_knowledge_context"]["artifact_refs"] == ["kac://architecture_review/abc123"]
    assert dream["compiled_knowledge_context"]["mutation_allowed"] is False
    assert dream["compiled_knowledge_context"]["requires_krc_runtime_context_allowed"] is True
    assert dream["compiled_knowledge_context"]["blocks_stale_or_quarantined_context"] is True
    assert dream["growth_seed"]["knowledge_artifact_refs"] == ["kac://architecture_review/abc123"]
    assert dream["production_mutation_allowed"] is False
    assert dream["recursive_dream_replay_evidence"]["status"] == "ready"
    assert dream["recursive_dream_replay_evidence"]["candidate_count"] == 3
    assert dream["recursive_dream_replay_evidence"]["knowledge_artifact_refs"] == ["kac://architecture_review/abc123"]
    assert dream["recursive_dream_replay_evidence"]["compiled_knowledge_context_allowed"] is True
    assert dream["recursive_dream_replay_evidence"]["compiled_knowledge_context_mutation_allowed"] is False
    assert dream["recursive_dream_replay_evidence"]["growth_seed"]["sandbox_only"] is True
    assert all(candidate["sandbox_required"] for candidate in dream["candidates"])
    assert all(candidate["critic_review"]["status"] == "accepted_for_sandbox" for candidate in dream["candidates"])

    dream_dir = tmp_path / "growth" / "production-spine" / "cyc_dream" / "dream-cycles" / "cycle_001"
    assert (dream_dir / "dream_cycle.json").is_file()
    assert (dream_dir / "dream_candidates.jsonl").is_file()
    assert (dream_dir / "growth_seed.json").is_file()


def test_recursive_dream_cycle_blocks_disallowed_kac_runtime_context(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    dream = spine.run_recursive_dream_cycle(
        {
            "dream_id": "dream:kac_blocked",
            "cycle_id": "cycle:cyc_dream_kac_blocked",
            "target_node_ref": "node:expert_coder",
            "student_id": "student:stu_dream_blocked",
            "knowledge_artifact_refs": ["kac://architecture_review/blocked"],
            "knowledge_artifact_runtime_contexts": [
                {
                    "artifact_id": "kac://architecture_review/blocked",
                    "runtime_context_allowed": False,
                    "fallback_state": "compiled_artifact_quarantined",
                }
            ],
        }
    )

    assert dream["status"] == "blocked"
    assert dream["candidate_count"] == 0
    assert "kac_runtime_context_not_allowed" in dream["blocked_reasons"]
    assert dream["compiled_knowledge_context"]["allowed"] is False
    assert dream["compiled_knowledge_context"]["blocked_artifact_refs"] == ["kac://architecture_review/blocked"]
    assert dream["production_mutation_allowed"] is False
    assert dream["recursive_dream_replay_evidence"]["status"] == "blocked"
    assert dream["recursive_dream_replay_evidence"]["blocked_artifact_refs"] == ["kac://architecture_review/blocked"]


def test_production_spine_blocks_raw_retrieval_fallback_as_kac_runtime_context(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    fallback_context = {
        "fallback_state": "raw_retrieval_fallback",
        "runtime_context_allowed": False,
        "runtime_context_role": "raw_retrieval_recall_only",
        "artifact_refs": [],
    }

    review = spine.run_teacher_council_review(
        {
            "review_id": "teacher:kac_raw_fallback_blocked",
            "cycle_id": "cycle:cyc_teacher_kac_raw_fallback",
            "target_node_ref": "node:expert_coder",
            "knowledge_artifact_refs": [],
            "knowledge_artifact_runtime_contexts": [fallback_context],
            "teacher_outputs": [
                {
                    "teacher_ref": "teacher:qwen3-coder-next",
                    "license_state": "approved_train",
                    "score": 0.88,
                    "output_ref": "out:qwen",
                }
            ],
            "validator_results": [{"validator_ref": "validator:unit_tests", "passed": True, "score": 1.0}],
        }
    )
    assert review["status"] == "blocked"
    assert review["compiled_knowledge_context"]["blocked_reasons"] == ["raw_retrieval_fallback"]
    assert review["compiled_knowledge_context"]["blocks_raw_retrieval_fallback_context"] is True

    dream = spine.run_recursive_dream_cycle(
        {
            "dream_id": "dream:kac_raw_fallback_blocked",
            "cycle_id": "cycle:cyc_dream_kac_raw_fallback",
            "target_node_ref": "node:expert_coder",
            "student_id": "student:stu_dream_raw_fallback",
            "knowledge_artifact_refs": [],
            "knowledge_artifact_runtime_contexts": [fallback_context],
        }
    )
    assert dream["status"] == "blocked"
    assert dream["candidate_count"] == 0
    assert dream["compiled_knowledge_context"]["blocked_reasons"] == ["raw_retrieval_fallback"]
    assert dream["compiled_knowledge_context"]["blocks_raw_retrieval_fallback_context"] is True


def test_runtime_quantization_foundry_scores_backend_candidates_without_promotion(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    foundry = spine.run_runtime_quantization_benchmark(
        {
            "benchmark_id": "bench:runtime_001",
            "cycle_id": "cycle:cyc_foundry",
            "model_ref": "model:nexusnet-child-demo",
            "hardware_profile": {"device": "local_cpu", "memory_gb": 16},
            "baseline_quality_score": 0.93,
            "candidates": [
                {"method": "q4_k_m", "backend": "llama.cpp", "tokens_per_second": 45.0, "memory_gb": 4.8, "quality_score": 0.91, "kv_cache": "quantized_kv"},
                {"method": "q5_k_m", "backend": "llama.cpp", "tokens_per_second": 38.0, "memory_gb": 5.8, "quality_score": 0.935, "kv_cache": "low_rank_kv"},
                {"method": "fp16", "backend": "transformers", "tokens_per_second": 20.0, "memory_gb": 11.2, "quality_score": 0.95, "kv_cache": "full_kv"},
            ],
            "backend_run_verified": True,
            "human_approved": False,
        }
    )

    assert foundry["status"] == "benchmark_complete"
    assert foundry["best_candidate"]["method"] == "q5_k_m"
    assert foundry["promotion_allowed"] is False
    assert foundry["promotion_blocker"] == "human_approval_required"
    assert foundry["production_runtime_mutation_allowed"] is False
    assert foundry["benchmark_count"] == 3
    assert foundry["kv_cache_methods_tested"] == ["full_kv", "low_rank_kv", "quantized_kv"]
    assert foundry["promotion_evidence"]["best_method"] == "q5_k_m"
    assert foundry["promotion_evidence"]["best_backend"] == "llama.cpp"
    assert foundry["promotion_evidence"]["quality_delta"] > 0
    assert foundry["promotion_evidence"]["tokens_per_second"] == 38.0
    assert foundry["promotion_evidence"]["promotion_blocker"] == "human_approval_required"
    assert foundry["runtime_foundry_replay_evidence"]["status"] == "ready"
    assert foundry["runtime_foundry_replay_evidence"]["backend_run_verified"] is True
    assert foundry["runtime_foundry_replay_evidence"]["benchmark_count"] == 3
    assert foundry["runtime_foundry_replay_evidence"]["best_candidate"]["method"] == "q5_k_m"
    assert foundry["runtime_foundry_replay_evidence"]["promotion_blocker"] == "human_approval_required"
    assert foundry["runtime_foundry_replay_evidence"]["mutation_boundary"] == "runtime-method-promotion-requires-backend-proof-hidden-eval-and-human-approval"
    assert foundry["runtime_canary_guard_evidence"]["status"] == "gated"
    assert foundry["runtime_canary_guard_evidence"]["active_runtime_method_allowed"] is False
    assert "runtime_shadow_window_required" in foundry["runtime_canary_guard_evidence"]["blockers"]
    assert "hidden_eval_delta_review_required" in foundry["runtime_canary_guard_evidence"]["blockers"]

    canary_foundry = spine.run_runtime_quantization_benchmark(
        {
            "benchmark_id": "bench:runtime_canary_001",
            "cycle_id": "cycle:cyc_foundry",
            "model_ref": "model:nexusnet-child-demo",
            "hardware_profile": {"device": "local_cpu", "memory_gb": 16},
            "baseline_quality_score": 0.93,
            "candidates": [
                {"method": "q5_k_m", "backend": "llama.cpp", "tokens_per_second": 38.0, "memory_gb": 5.8, "quality_score": 0.935, "kv_cache": "low_rank_kv"},
            ],
            "backend_run_verified": True,
            "human_approved": True,
            "runtime_shadow_window_passed": True,
            "runtime_canary_window_passed": True,
            "hidden_eval_delta_review_passed": True,
        }
    )

    assert canary_foundry["promotion_allowed"] is True
    assert canary_foundry["runtime_canary_guard_evidence"]["status"] == "ready"
    assert canary_foundry["runtime_canary_guard_evidence"]["active_runtime_method_allowed"] is True
    assert canary_foundry["runtime_foundry_replay_evidence"]["runtime_canary_guard_evidence"]["status"] == "ready"

    foundry_dir = tmp_path / "growth" / "production-spine" / "cyc_foundry" / "runtime-foundry" / "runtime_001"
    assert (foundry_dir / "benchmark_report.json").is_file()
    assert (foundry_dir / "benchmark_results.jsonl").is_file()
    assert (foundry_dir / "promotion_gate.json").is_file()


def test_deep_replay_bundle_indexes_cycle_artifacts_for_developer_drilldown(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    training = spine.run_sandbox_training_proof(
        {
            "run_id": "train:proof_replay",
            "cycle_id": "cycle:cyc_replay",
            "student_id": "student:stu_replay",
            "operator_approved": True,
            "training_scope": "sandbox_proof",
            "dataset": [{"x": 0.0, "y": 1.0}, {"x": 1.0, "y": 3.0}],
        }
    )
    spine.execute_child_node(
        {
            "execution_id": "exec:replay_child",
            "cycle_id": "cycle:cyc_replay",
            "student_id": "student:stu_replay",
            "input": {"x": 2.0},
            "weights_path": training["artifacts"]["weights_path"],
        }
    )
    spine.run_hive_moe_shadow_route(
        {
            "route_id": "route:replay",
            "cycle_id": "cycle:cyc_replay",
            "task_features": {"coding": 0.8},
            "candidates": [{"node_ref": "student:stu_replay", "weights": {"coding": 0.8}}],
            "top_k": 1,
        }
    )
    replay = spine.build_deep_replay_bundle(
        {
            "cycle_id": "cycle:cyc_replay",
            "replay_id": "replay:bundle_001",
            "knowledge_artifact_refs": ["kac://architecture_review/abc123"],
        }
    )

    assert replay["status"] == "deep_replay_ready"
    assert replay["developer_visible"] is True
    assert replay["compiled_knowledge_context"]["artifact_refs"] == ["kac://architecture_review/abc123"]
    assert replay["compiled_knowledge_context"]["mutation_allowed"] is False
    assert replay["artifact_count"] >= 6
    assert "sandbox_training" in replay["drilldowns"]
    assert "child_execution" in replay["drilldowns"]
    assert "route_diff" in replay["drilldowns"]
    assert replay["production_mutation_allowed"] is False

    replay_dir = tmp_path / "growth" / "production-spine" / "cyc_replay" / "deep-replay" / "bundle_001"
    assert (replay_dir / "deep_replay_bundle.json").is_file()
    assert (replay_dir / "artifact_index.jsonl").is_file()
    artifact_index = [
        json.loads(line)
        for line in (replay_dir / "artifact_index.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    kac_records = [record for record in artifact_index if record["artifact_type"] == "knowledge_artifact_ref"]
    assert kac_records[0]["artifact_path"] == "kac://architecture_review/abc123"
    assert kac_records[0]["relative_path"].startswith("knowledge-artifacts/")
    assert kac_records[0]["requires_krc_runtime_context_allowed"] is True
    assert kac_records[0]["blocks_stale_or_quarantined_context"] is True
    assert kac_records[0]["runtime_gate_source"] == "KnowledgeArtifactCompiler.query"


def test_productization_readiness_gate_blocks_until_buyer_safe_requirements_pass(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    blocked = spine.assess_productization_readiness(
        {
            "readiness_id": "release:blocked",
            "cycle_id": "cycle:cyc_productization",
            "local_cache_controls": True,
            "secret_scan_passed": False,
            "model_download_manager": True,
            "support_bundle": False,
            "crash_diagnostics": True,
            "ci_packaging": False,
            "buyer_launcher": True,
            "docs_complete": False,
            "buyer_safe_defaults": True,
            "runtime_gates_clear": False,
        }
    )

    assert blocked["release_ready"] is False
    assert "secret_scan_passed" in blocked["open_gates"]
    assert "support_bundle" in blocked["open_gates"]
    assert "runtime_gates_clear" in blocked["open_gates"]
    assert "artifact_signing_ready" in blocked["open_gates"]
    assert "artifact_trust_clear" in blocked["open_gates"]
    assert "adapter_artifact_trust_clear" in blocked["open_gates"]
    assert blocked["productization_replay_evidence"]["status"] == "blocked"
    assert blocked["productization_replay_evidence"]["secret_scan_passed"] is False
    assert blocked["productization_replay_evidence"]["shareable_artifact_boundary"] == "installer_or_release_bundle_only"

    ready = spine.assess_productization_readiness(
        {
            "readiness_id": "release:ready",
            "cycle_id": "cycle:cyc_productization",
            "local_cache_controls": True,
            "secret_scan_passed": True,
            "model_download_manager": True,
            "support_bundle": True,
            "crash_diagnostics": True,
            "ci_packaging": True,
            "buyer_launcher": True,
            "docs_complete": True,
            "buyer_safe_defaults": True,
            "runtime_gates_clear": True,
            "artifact_signing_ready": True,
            "artifact_trust_clear": True,
            "adapter_artifact_trust_clear": True,
        }
    )

    assert ready["release_ready"] is True
    assert ready["open_gates"] == []
    assert ready["shareable_artifact_boundary"] == "installer_or_release_bundle_only"
    assert ready["productization_replay_evidence"]["status"] == "ready"
    assert ready["productization_replay_evidence"]["release_ready"] is True
    assert ready["productization_replay_evidence"]["open_gates"] == []

    product_dir = tmp_path / "growth" / "production-spine" / "cyc_productization" / "productization"
    assert (product_dir / "readiness_report.json").is_file()
    assert (product_dir / "readiness_events.jsonl").is_file()


def test_productization_readiness_blocks_upstream_agent_opportunity_gate(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    blocked = spine.assess_productization_readiness(
        {
            "readiness_id": "release:blocked-agent-opportunity",
            "cycle_id": "cycle:cyc_productization_agent_gate",
            "local_cache_controls": True,
            "secret_scan_passed": True,
            "model_download_manager": True,
            "support_bundle": True,
            "crash_diagnostics": True,
            "ci_packaging": True,
            "buyer_launcher": True,
            "docs_complete": True,
            "buyer_safe_defaults": True,
            "runtime_gates_clear": True,
            "artifact_signing_ready": True,
            "artifact_trust_clear": True,
            "adapter_artifact_trust_clear": True,
            "upstream_agent_opportunity_gate": {
                "ready_for_agent_build": False,
                "opportunity_gate_state": "blocked-by-forward-radar",
                "blockers": ["forward_radar_promotion_gate_required"],
            },
        }
    )

    assert blocked["release_ready"] is False
    assert blocked["status"] == "blocked"
    assert "upstream_agent_opportunity_gate_clear" in blocked["open_gates"]
    assert blocked["upstream_agent_opportunity_gate"]["ready_for_agent_build"] is False
    assert "forward_radar_promotion_gate_required" in blocked["upstream_agent_opportunity_gate"]["blockers"]
    assert blocked["productization_replay_evidence"]["upstream_agent_opportunity_gate"]["ready_for_agent_build"] is False


def test_teacher_council_review_gates_license_and_scores_disagreement(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    review = spine.run_teacher_council_review(
        {
            "review_id": "teacher:review_001",
            "cycle_id": "cycle:cyc_teacher_review",
            "target_node_ref": "node:expert_coder",
            "teacher_outputs": [
                {"teacher_ref": "teacher:qwen3-coder-next", "license_state": "approved_train", "score": 0.88, "output_ref": "out:qwen"},
                {"teacher_ref": "teacher:devstral-2", "license_state": "approved_train", "score": 0.84, "output_ref": "out:devstral"},
                {"teacher_ref": "node:expert_critique", "license_state": "internal", "score": 0.91, "output_ref": "out:critique"},
            ],
            "validator_results": [
                {"validator_ref": "validator:unit_tests", "passed": True, "score": 1.0},
                {"validator_ref": "validator:security", "passed": True, "score": 0.95},
            ],
        }
    )

    assert review["status"] == "teacher_review_complete"
    assert review["license_gate"]["passed"] is True
    assert review["accepted_teacher_ref"] == "node:expert_critique"
    assert review["disagreement_score"] > 0
    assert review["validator_summary"]["all_passed"] is True
    assert review["reviewer_window"]["required_windows"] == 4

    blocked = spine.run_teacher_council_review(
        {
            "review_id": "teacher:blocked",
            "cycle_id": "cycle:cyc_teacher_review",
            "target_node_ref": "node:expert_coder",
            "teacher_outputs": [
                {"teacher_ref": "teacher:frontier-api", "license_state": "blocked_anti_distillation", "score": 0.99, "output_ref": "out:blocked"}
            ],
            "validator_results": [{"validator_ref": "validator:unit_tests", "passed": True, "score": 1.0}],
        }
    )

    assert blocked["status"] == "blocked"
    assert "teacher_license_not_approved" in blocked["blocked_reasons"]

    council_dir = tmp_path / "growth" / "production-spine" / "cyc_teacher_review" / "teacher-council" / "review_001"
    assert (council_dir / "council_decision.json").is_file()
    assert (council_dir / "teacher_outputs.jsonl").is_file()
    assert (council_dir / "validator_results.jsonl").is_file()


def test_teacher_council_review_records_knowledge_artifact_refs_as_context_only(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    review = spine.run_teacher_council_review(
        {
            "review_id": "teacher:kac_review",
            "cycle_id": "cycle:cyc_teacher_kac",
            "target_node_ref": "node:expert_coder",
            "knowledge_artifact_refs": ["kac://architecture_review/abc123"],
            "teacher_outputs": [
                {
                    "teacher_ref": "teacher:qwen3-coder-next",
                    "license_state": "approved_train",
                    "score": 0.88,
                    "output_ref": "out:qwen",
                },
                {
                    "teacher_ref": "node:expert_critique",
                    "license_state": "internal",
                    "score": 0.91,
                    "output_ref": "out:critique",
                },
            ],
            "validator_results": [{"validator_ref": "validator:unit_tests", "passed": True, "score": 1.0}],
        }
    )

    assert review["status"] == "teacher_review_complete"
    assert review["compiled_knowledge_context"]["artifact_refs"] == ["kac://architecture_review/abc123"]
    assert review["compiled_knowledge_context"]["mutation_allowed"] is False
    assert review["compiled_knowledge_context"]["access_rule"] == "artifact-refs-only-through-KRC"
    assert review["compiled_knowledge_context"]["requires_krc_runtime_context_allowed"] is True
    assert review["compiled_knowledge_context"]["blocks_stale_or_quarantined_context"] is True

    council_dir = tmp_path / "growth" / "production-spine" / "cyc_teacher_kac" / "teacher-council" / "kac_review"
    decision = json.loads((council_dir / "council_decision.json").read_text(encoding="utf-8"))
    assert decision["compiled_knowledge_context"]["artifact_refs"] == ["kac://architecture_review/abc123"]
    assert decision["compiled_knowledge_context"]["requires_krc_runtime_context_allowed"] is True


def test_teacher_council_review_blocks_disallowed_kac_runtime_context(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    review = spine.run_teacher_council_review(
        {
            "review_id": "teacher:kac_blocked_review",
            "cycle_id": "cycle:cyc_teacher_kac_blocked",
            "target_node_ref": "node:expert_coder",
            "knowledge_artifact_refs": ["kac://architecture_review/blocked"],
            "knowledge_artifact_runtime_contexts": [
                {
                    "artifact_id": "kac://architecture_review/blocked",
                    "runtime_context_allowed": False,
                    "fallback_state": "compiled_artifact_stale",
                }
            ],
            "teacher_outputs": [
                {
                    "teacher_ref": "teacher:qwen3-coder-next",
                    "license_state": "approved_train",
                    "score": 0.88,
                    "output_ref": "out:qwen",
                }
            ],
            "validator_results": [{"validator_ref": "validator:unit_tests", "passed": True, "score": 1.0}],
        }
    )

    assert review["status"] == "blocked"
    assert "kac_runtime_context_not_allowed" in review["blocked_reasons"]
    assert review["compiled_knowledge_context"]["allowed"] is False
    assert review["compiled_knowledge_context"]["blocked_reasons"] == ["compiled_artifact_stale"]
