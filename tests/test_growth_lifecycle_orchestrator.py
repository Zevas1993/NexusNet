from __future__ import annotations

import json
import zipfile

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.growth import NexusNetProductionSpine
from nexusnet.growth.production_spine import _validate_lifecycle_replay_consistency
from nexusnet.security.project_key_store import ProjectLocalSigningKeyStore
from tests.test_nexus_phase1_foundation import make_project


def lifecycle_request() -> dict:
    return {
        "lifecycle_id": "lifecycle:coder_birth_001",
        "cycle_id": "cycle:cyc_lifecycle_001",
        "target_node_ref": "node:expert_coder",
        "student_id": "student:stu_lifecycle_001",
        "student_kind": "child_expert",
        "capabilities": ["multi_file_patch", "test_repair"],
        "operator_approved": True,
        "human_approved": False,
        "teacher_outputs": [
            {"teacher_ref": "teacher:qwen3-coder-next", "license_state": "approved_train", "score": 0.88, "output_ref": "out:qwen"},
            {"teacher_ref": "teacher:devstral-2", "license_state": "approved_train", "score": 0.85, "output_ref": "out:devstral"},
            {"teacher_ref": "node:expert_critique", "license_state": "internal", "score": 0.91, "output_ref": "out:critique"},
        ],
        "validator_results": [
            {"validator_ref": "validator:unit_tests", "passed": True, "score": 1.0},
            {"validator_ref": "validator:security", "passed": True, "score": 0.95},
        ],
        "training_dataset": [
            {"x": 0.0, "y": 1.0},
            {"x": 1.0, "y": 3.0},
            {"x": 2.0, "y": 5.0},
            {"x": 3.0, "y": 7.0},
        ],
        "shadow_input": {"x": 4.0},
        "route_features": {"coding": 0.8, "reasoning": 0.5, "risk": 0.2},
        "route_candidates": [
            {"node_ref": "node:expert_coder", "weights": {"coding": 0.7, "reasoning": 0.1, "risk": -0.2}},
            {"node_ref": "student:stu_lifecycle_001", "weights": {"coding": 0.6, "reasoning": 0.5, "risk": -0.1}},
        ],
        "hidden_eval_cases": [
            {"x": 4.0, "y": 9.0, "parent_prediction": 7.5, "teacher_prediction": 8.0},
            {"x": 5.0, "y": 11.0, "parent_prediction": 9.0, "teacher_prediction": 10.0},
            {"x": 6.0, "y": 13.0, "parent_prediction": 10.5, "teacher_prediction": 12.0},
        ],
        "hidden_eval_attestation": {
            "sealed": True,
            "visible_to_training": False,
            "visible_to_teacher_council": False,
            "leakage_scan": {"status": "passed", "train_overlap": 0, "teacher_output_overlap": 0},
        },
        "federation": {
            "consent_granted": True,
            "local_metrics": {"success_rate": 0.84, "failure_rate": 0.05, "latency_ms": 120.0, "sample_count": 50},
        },
        "runtime_benchmarks": [
            {"method": "q4_k_m", "backend": "llama.cpp", "tokens_per_second": 45.0, "memory_gb": 4.8, "quality_score": 0.91, "kv_cache": "quantized_kv"},
            {"method": "q5_k_m", "backend": "llama.cpp", "tokens_per_second": 38.0, "memory_gb": 5.8, "quality_score": 0.935, "kv_cache": "low_rank_kv"},
        ],
        "raw_private_data": "private text must not persist",
    }


def test_growth_lifecycle_orchestrator_runs_closed_loop_with_replay_and_gates(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)

    lifecycle = spine.run_growth_lifecycle(lifecycle_request())

    assert lifecycle["status"] == "closed_loop_complete"
    assert lifecycle["production_mutation_allowed"] is False
    assert lifecycle["teacher_review"]["status"] == "teacher_review_complete"
    assert lifecycle["training"]["status"] == "sandbox_training_complete"
    assert lifecycle["training_backend_plan"]["status"] == "sandbox_backend_plan_ready"
    assert lifecycle["training"]["artifacts"]["checkpoint_path"].endswith("checkpoint.json")
    assert lifecycle["training_replay_evidence"]["status"] == "ready"
    assert lifecycle["training_replay_evidence"]["math_contract"]["loss"] == "L = mean((y_hat - y)^2)"
    assert lifecycle["training_replay_evidence"]["optimizer_state"]["optimizer"] == "batch_gradient_descent"
    assert lifecycle["training_replay_evidence"]["optimizer_state"]["steps"] == 120
    assert lifecycle["training_replay_evidence"]["operator_visible"] is True
    assert lifecycle["training"]["exports"]["adapter"]["state"] == "sandbox_candidate"
    assert lifecycle["child_execution"]["status"] == "shadow_executed"
    assert lifecycle["child_execution"]["weights_source"] == "sandbox_runner_checkpoint"
    assert lifecycle["child_execution_replay_evidence"]["status"] == "ready"
    assert lifecycle["child_execution_replay_evidence"]["callable_runtime_verified"] is True
    assert lifecycle["child_execution_replay_evidence"]["runtime_pathway"]["used_hive_blackboard"] is True
    assert lifecycle["hive_route_replay_evidence"]["status"] == "ready"
    assert lifecycle["hive_route_replay_evidence"]["selected_nodes"] == lifecycle["hive_route"]["selected_nodes"]
    assert lifecycle["hive_route_replay_evidence"]["routing_weight_update"]["promotion_required"] is True
    assert lifecycle["tensor_runtime_replay_evidence"]["status"] == "ready"
    assert lifecycle["tensor_runtime_replay_evidence"]["op_count"] == 3
    assert lifecycle["tensor_runtime_replay_evidence"]["checkpoint"]["restore_validated"] is True
    assert lifecycle["reviewer_confidence_evidence"]["status"] == "ready"
    assert lifecycle["reviewer_confidence_evidence"]["teacher_surpass_rate"] == 1.0
    assert lifecycle["reviewer_confidence_evidence"]["teacher_ejection_eligible"] is False
    assert lifecycle["reviewer_confidence_evidence"]["ejection_readiness_evidence"]["status"] == "gated"
    assert lifecycle["reviewer_confidence_evidence"]["ejection_readiness_evidence"]["teacher_ejection_allowed"] is False
    assert lifecycle["reviewer_confidence_evidence"]["ejection_readiness_evidence"]["pending_window_count"] == 3
    assert lifecycle["node_registry_replay_evidence"]["status"] == "blocked"
    assert lifecycle["node_registry_replay_evidence"]["rollback_restorable"] is True
    assert lifecycle["node_registry_replay_evidence"]["parent_retirement_allowed"] is False
    assert lifecycle["node_registry_replay_evidence"]["canary_promotion_guard_evidence"]["status"] == "gated"
    assert lifecycle["node_registry_replay_evidence"]["canary_promotion_guard_evidence"]["active_deployment_allowed"] is False
    assert lifecycle["federated_influence_replay_evidence"]["status"] == "ready"
    assert lifecycle["federated_influence_replay_evidence"]["consent_granted"] is True
    assert lifecycle["federated_influence_replay_evidence"]["differential_privacy"]["enabled"] is True
    assert lifecycle["recursive_dream_replay_evidence"]["status"] == "ready"
    assert lifecycle["recursive_dream_replay_evidence"]["candidate_count"] == 3
    assert lifecycle["recursive_dream_replay_evidence"]["growth_seed"]["sandbox_only"] is True
    assert lifecycle["runtime_foundry_replay_evidence"]["status"] == "ready"
    assert lifecycle["runtime_foundry_replay_evidence"]["benchmark_count"] == 2
    assert lifecycle["runtime_foundry_replay_evidence"]["promotion_blocker"] == "human_approval_required"
    assert lifecycle["runtime_foundry_replay_evidence"]["runtime_canary_guard_evidence"]["active_runtime_method_allowed"] is False
    assert lifecycle["productization_replay_evidence"]["status"] == "blocked"
    assert "secret_scan_passed" in lifecycle["productization_replay_evidence"]["open_gates"]
    assert lifecycle["productization_replay_evidence"]["shareable_artifact_boundary"] == "installer_or_release_bundle_only"
    assert lifecycle["lifecycle_evidence_chain"]["status"] == "gated"
    assert lifecycle["lifecycle_evidence_chain"]["evidence_count"] == 13
    assert lifecycle["lifecycle_evidence_chain"]["ready_count"] >= 7
    assert lifecycle["lifecycle_evidence_chain"]["blocked_count"] >= 5
    assert "productization_replay_evidence" in lifecycle["lifecycle_evidence_chain"]["blocked_evidence_ids"]
    assert lifecycle["lifecycle_evidence_chain"]["mutation_boundary"] == "read-only-lifecycle-proof-chain-no-production-mutation"
    assert lifecycle["lifecycle_evidence_chain"]["operator_visible"] is True
    assert lifecycle["artifact_bridge"]["training_checkpoint_path"] == lifecycle["training"]["artifacts"]["checkpoint_path"]
    assert lifecycle["artifact_bridge"]["adapter_manifest_path"] == lifecycle["training"]["artifacts"]["adapter_manifest_path"]
    assert lifecycle["training"]["exports"]["adapter"]["bundle_path"].endswith("adapter_artifact_bundle.zip")
    assert lifecycle["artifact_bridge"]["adapter_bundle_path"] == lifecycle["training"]["exports"]["adapter"]["bundle_path"]
    assert lifecycle["hive_route"]["status"] == "shadow_routed"
    assert lifecycle["tensor_program"]["status"] == "executed_tensor_program"
    assert lifecycle["sealed_eval"]["status"] == "sealed_eval_complete"
    assert lifecycle["artifact_bridge"]["eval_scorecard_path"] == lifecycle["sealed_eval"]["artifacts"]["eval_scorecard_path"]
    assert lifecycle["artifact_bridge"]["child_execution_report_path"] == lifecycle["child_execution"]["artifacts"]["execution_report_path"]
    assert lifecycle["sealed_eval"]["score_comparison"]["student_parent_surpass_margin"] > 0
    assert lifecycle["sealed_eval"]["score_comparison"]["student_teacher_surpass_margin"] > 0
    assert lifecycle["sealed_eval"]["reviewer_consistency"]["teacher_ejection_eligible"] is False
    assert lifecycle["sealed_eval"]["reviewer_consistency"]["pending_window_count"] == 3
    assert lifecycle["sealed_eval"]["ejection_readiness_evidence"]["status"] == "gated"
    assert lifecycle["sealed_eval"]["ejection_readiness_evidence"]["parent_retirement_allowed"] is False
    assert lifecycle["sealed_eval"]["ejection_readiness_evidence"]["pending_window_count"] == 3
    assert lifecycle["sealed_eval"]["hidden_eval_attestation"]["leakage_scan"]["status"] == "passed"
    assert lifecycle["replay_consistency"]["passed"] is True
    assert lifecycle["replay_consistency"]["missing_bridge_paths"] == []
    assert lifecycle["replay_consistency"]["bridge_paths_missing_from_replay"] == []
    assert lifecycle["replay_consistency"]["bridge_hash_mismatches"] == []
    assert lifecycle["replay_consistency"]["expected_signature_state"] == "unsigned_v0"
    assert lifecycle["replay_consistency"]["bridge_signature_state_mismatches"] == []
    assert lifecycle["node_registry"]["decision"] == "blocked"
    assert lifecycle["node_registry"]["adapter_artifact_trust_status"] == "quarantined"
    assert lifecycle["node_registry"]["adapter_artifact_trust_clear"] is False
    assert lifecycle["node_registry_snapshot"]["status"] == "node_registry_snapshot_ready"
    assert lifecycle["node_registry_snapshot"]["adapter_artifact_trust_status"] == "quarantined"
    assert lifecycle["node_registry_snapshot"]["adapter_artifact_trust_clear"] is False
    assert lifecycle["node_registry_snapshot"]["lifecycle_replay"]["replay_consistency"]["passed"] is True
    assert "eval_promotion_not_allowed" in lifecycle["node_registry"]["blocked_reasons"]
    assert "adapter_artifact_trust_clear_required" in lifecycle["node_registry"]["blocked_reasons"]
    assert lifecycle["federation"]["status"] == "accepted_sanitized_packet"
    assert lifecycle["dream_cycle"]["status"] == "dream_candidates_materialized"
    assert lifecycle["runtime_foundry"]["status"] == "benchmark_complete"
    assert lifecycle["runtime_foundry"]["promotion_evidence"]["best_method"] == "q5_k_m"
    assert lifecycle["runtime_foundry"]["promotion_evidence"]["promotion_blocker"] == "human_approval_required"
    assert lifecycle["deep_replay"]["status"] == "deep_replay_ready"
    assert lifecycle["deep_replay"]["signature_policy"]["current_signature_state"] == "unsigned_v0"
    assert lifecycle["deep_replay"]["signature_policy"]["next_signature_state"] == "signed_ed25519"
    assert lifecycle["deep_replay"]["signature_policy"]["production_promotion_requires_real_signing"] is True
    assert lifecycle["signer_readiness"]["status"] == "blocked"
    assert lifecycle["signer_readiness"]["production_mutation_blocker"] == "real_signing_required"
    assert lifecycle["signer_readiness"]["current_signature_state"] == "unsigned_v0"
    assert lifecycle["signer_readiness"]["next_signature_state"] == "signed_ed25519"
    assert lifecycle["signer_readiness"]["unsigned_state_allowed_for"] == ["sandbox", "shadow", "local_replay"]
    assert "real_signing_required" in lifecycle["blocked_reasons"]
    assert "sandbox_runner_training" in lifecycle["deep_replay"]["drilldowns"]
    assert "growth_lifecycle" in lifecycle["deep_replay"]["drilldowns"]
    assert lifecycle["productization"]["release_ready"] is False
    assert lifecycle["closed_loop_summary"]["teacher_reviewed"] is True
    assert lifecycle["closed_loop_summary"]["child_trained"] is True
    assert lifecycle["closed_loop_summary"]["child_promoted"] is False
    assert lifecycle["closed_loop_summary"]["parent_retired"] is False

    lifecycle_dir = tmp_path / "growth" / "production-spine" / "cyc_lifecycle_001" / "growth-lifecycles" / "coder_birth_001"
    assert (lifecycle_dir / "lifecycle_report.json").is_file()
    assert (lifecycle_dir / "lifecycle_events.jsonl").is_file()
    lifecycle_events = [json.loads(line) for line in (lifecycle_dir / "lifecycle_events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {"step": "replay_consistency", "status": "passed", "checked_bridge_path_count": 11} in lifecycle_events
    assert any(event["step"] == "training_replay_evidence" and event["status"] == "ready" for event in lifecycle_events)
    assert any(event["step"] == "child_execution_replay_evidence" and event["status"] == "ready" for event in lifecycle_events)
    assert any(event["step"] == "hive_route_replay_evidence" and event["status"] == "ready" for event in lifecycle_events)
    assert any(event["step"] == "tensor_runtime_replay_evidence" and event["status"] == "ready" for event in lifecycle_events)
    assert any(event["step"] == "reviewer_confidence_evidence" and event["status"] == "ready" for event in lifecycle_events)
    assert any(event["step"] == "node_registry_replay_evidence" and event["status"] == "blocked" for event in lifecycle_events)
    assert any(event["step"] == "federated_influence_replay_evidence" and event["status"] == "ready" for event in lifecycle_events)
    assert any(event["step"] == "recursive_dream_replay_evidence" and event["status"] == "ready" for event in lifecycle_events)
    assert any(event["step"] == "runtime_foundry_replay_evidence" and event["status"] == "ready" for event in lifecycle_events)
    assert any(event["step"] == "productization_replay_evidence" and event["status"] == "blocked" for event in lifecycle_events)
    assert any(event["step"] == "lifecycle_evidence_chain" and event["status"] == "gated" for event in lifecycle_events)
    assert "private text must not persist" not in (lifecycle_dir / "lifecycle_report.json").read_text(encoding="utf-8")
    artifact_index = lifecycle["deep_replay"]["artifacts"]["artifact_index_path"]
    artifact_records = [json.loads(line) for line in open(artifact_index, encoding="utf-8") if line.strip()]
    assert all(record["signature_state"] == "unsigned_v0" for record in artifact_records)
    replay_types = {record["artifact_type"] for record in artifact_records}
    assert {
        "sandbox_training_report",
        "sandbox_loss_trace",
        "sandbox_checkpoint",
        "sandbox_adapter_bundle",
        "sandbox_adapter_manifest",
        "sandbox_gguf_export_plan",
        "sandbox_quantization_manifest",
        "growth_lifecycle_report",
        "growth_lifecycle_event_log",
        "node_registry_snapshot",
    }.issubset(replay_types)
    adapter_records = [record for record in artifact_records if record["relative_path"].endswith("adapter_artifact_bundle.zip")]
    assert len(adapter_records) == 1
    assert adapter_records[0]["artifact_type"] == "sandbox_adapter_bundle"
    assert lifecycle["artifact_trust"]["adapter_artifact_scan"]["artifact_type"] == "adapter"
    assert lifecycle["artifact_trust"]["adapter_artifact_scan"]["metadata"]["source"] == "sandbox_adapter_artifact_bundle"
    assert lifecycle["artifact_trust"]["adapter_artifact_scan"]["metadata"]["relative_path"].endswith("adapter_artifact_bundle.zip")


def test_growth_lifecycle_orchestrator_is_exposed_through_api_and_scorecard(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post("/ops/brain/production-spine/growth-lifecycles", json=lifecycle_request())

    assert response.status_code == 200
    assert response.json()["status"] == "closed_loop_complete"
    assert response.json()["production_mutation_allowed"] is False

    summary = client.get("/ops/brain/production-spine")
    assert summary.status_code == 200
    assert summary.json()["lifecycle_count"] == 1
    assert summary.json()["latest_lifecycle_replay_consistency"]["passed"] is True

    scorecard = client.get("/ops/brain/canon/production-spine")
    assert scorecard.status_code == 200
    assert scorecard.json()["lifecycle_count"] == 1
    assert scorecard.json()["latest_lifecycle"]["status"] == "closed_loop_complete"
    assert scorecard.json()["latest_lifecycle_replay_consistency"]["passed"] is True
    assert scorecard.json()["latest_lifecycle_artifact_bridge"]["training_checkpoint_path"].endswith("checkpoint.json")
    assert scorecard.json()["latest_lifecycle_training_replay_evidence"]["optimizer_state"]["steps"] == 120
    assert scorecard.json()["latest_lifecycle_child_execution_replay_evidence"]["callable_runtime_verified"] is True
    assert scorecard.json()["latest_lifecycle_hive_route_replay_evidence"]["routing_mode"] == "native_hive_moe_sparse_top_k"
    assert scorecard.json()["latest_lifecycle_tensor_runtime_replay_evidence"]["op_count"] == 3
    assert scorecard.json()["latest_lifecycle_reviewer_confidence_evidence"]["teacher_ejection_eligible"] is False
    assert scorecard.json()["latest_lifecycle_reviewer_confidence_evidence"]["ejection_readiness_evidence"]["status"] == "gated"
    assert scorecard.json()["latest_lifecycle_node_registry_replay_evidence"]["rollback_restorable"] is True
    assert scorecard.json()["latest_lifecycle_node_registry_snapshot"]["status"] == "node_registry_snapshot_ready"
    assert scorecard.json()["latest_lifecycle_node_registry_replay_evidence"]["reviewer_window_retirement_evidence"]["status"] == "not_required"
    assert scorecard.json()["latest_lifecycle_federated_influence_replay_evidence"]["consent_granted"] is True
    assert scorecard.json()["latest_lifecycle_recursive_dream_replay_evidence"]["candidate_count"] == 3
    assert scorecard.json()["latest_lifecycle_runtime_foundry_replay_evidence"]["benchmark_count"] == 2
    assert scorecard.json()["latest_lifecycle_productization_replay_evidence"]["release_ready"] is False
    assert scorecard.json()["latest_lifecycle_evidence_chain"]["status"] == "gated"
    assert scorecard.json()["latest_lifecycle_evidence_chain"]["evidence_count"] == 13
    assert "productization_replay_evidence" in scorecard.json()["latest_lifecycle_evidence_chain"]["blocked_evidence_ids"]
    finish_map = scorecard.json()["finish_readiness_map"]
    assert finish_map["status"] == "blocked"
    assert finish_map["gate_count"] == 12
    assert finish_map["mutation_boundary"] == "read-only-finish-map-no-production-mutation"
    assert finish_map["lifecycle_evidence_chain_ref"] == "chain:coder_birth_001"
    gates_by_id = {gate["gate_id"]: gate for gate in finish_map["gates"]}
    assert gates_by_id["real_training_runner"]["status"] == "gated"
    assert "production_training_runner_not_enabled" in gates_by_id["real_training_runner"]["blockers"]
    assert gates_by_id["real_training_runner"]["next_operator_action"] == "assess_real_training_gate"
    assert gates_by_id["sealed_eval_gauntlet"]["status"] == "gated"
    assert "reviewer_window_advancement_missing" in gates_by_id["sealed_eval_gauntlet"]["blockers"]
    assert gates_by_id["sealed_eval_gauntlet"]["next_operator_action"] == "record_reviewer_window"
    assert gates_by_id["runtime_quantization_foundry"]["status"] == "gated"
    assert gates_by_id["productization"]["status"] == "blocked"
    assert "record_reviewer_window" in finish_map["next_operator_actions"]
    assert "assess_productization" in finish_map["next_operator_actions"]
    productization_template = scorecard.json()["productization_readiness_request_template"]
    assert productization_template["endpoint"] == "/ops/brain/production-spine/productization-readiness"
    assert productization_template["ready_to_submit"] is False
    assert productization_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert productization_template["template"]["adapter_artifact_trust_clear"] is False
    assert productization_template["template"]["adapter_artifact_trust_status"] == "quarantined"
    assert "secret_scan_passed" in productization_template["missing_proof_fields"]
    assert "support_bundle" in productization_template["missing_proof_fields"]
    assert "ci_packaging" in productization_template["missing_proof_fields"]
    assert "adapter_artifact_trust_clear" in productization_template["missing_proof_fields"]
    runtime_foundry_template = scorecard.json()["runtime_quantization_foundry_request_template"]
    assert runtime_foundry_template["endpoint"] == "/ops/brain/production-spine/runtime-benchmarks"
    assert runtime_foundry_template["ready_to_submit"] is False
    assert runtime_foundry_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert runtime_foundry_template["template"]["model_ref"] == "student:stu_lifecycle_001"
    assert runtime_foundry_template["template"]["backend_run_verified"] is True
    assert len(runtime_foundry_template["template"]["candidates"]) == 2
    assert "human_approved" in runtime_foundry_template["missing_proof_fields"]
    assert "runtime_shadow_window_passed" in runtime_foundry_template["missing_proof_fields"]
    assert "hidden_eval_delta_review_passed" in runtime_foundry_template["missing_proof_fields"]
    reviewer_window_template = scorecard.json()["reviewer_window_request_template"]
    assert reviewer_window_template["endpoint"] == "/ops/brain/production-spine/reviewer-windows"
    assert reviewer_window_template["ready_to_submit"] is False
    assert reviewer_window_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert reviewer_window_template["template"]["eval_id"] == "eval:coder_birth_001"
    assert reviewer_window_template["template"]["student_id"] == "student:stu_lifecycle_001"
    assert reviewer_window_template["template"]["window"] == "shadow_runtime"
    assert "initial_eval" in reviewer_window_template["template"]["passed_windows"]
    assert "teacher_ejection_review_requested" in reviewer_window_template["missing_proof_fields"]
    assert "human_approved" in reviewer_window_template["missing_proof_fields"]
    assert "governance_approved" in reviewer_window_template["missing_proof_fields"]
    node_registry_template = scorecard.json()["node_registry_decision_request_template"]
    assert node_registry_template["endpoint"] == "/ops/brain/production-spine/node-registry-decisions"
    assert node_registry_template["ready_to_submit"] is False
    assert node_registry_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert node_registry_template["template"]["student_id"] == "student:stu_lifecycle_001"
    assert node_registry_template["template"]["parent_node_ref"] == "node:expert_coder"
    assert node_registry_template["template"]["action"] == "promote_child"
    assert node_registry_template["template"]["eval_scorecard_path"].endswith("eval_scorecard.json")
    assert node_registry_template["template"]["adapter_artifact_trust_status"] == "quarantined"
    assert node_registry_template["template"]["adapter_artifact_trust_clear"] is False
    assert "human_approved" in node_registry_template["missing_proof_fields"]
    assert "eval_promotion_allowed" in node_registry_template["missing_proof_fields"]
    assert "adapter_artifact_trust_clear" in node_registry_template["missing_proof_fields"]
    assert "shadow_runtime_window_passed" in node_registry_template["missing_proof_fields"]
    federated_template = scorecard.json()["federated_packet_request_template"]
    assert federated_template["endpoint"] == "/ops/brain/production-spine/federated-packets"
    assert federated_template["ready_to_submit"] is True
    assert federated_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert federated_template["template"]["source_node_ref"] == "node:expert_coder"
    assert federated_template["template"]["consent_granted"] is True
    assert federated_template["template"]["raw_content_included"] is False
    assert federated_template["template"]["local_metrics"]["success_rate"] == 0.84
    assert federated_template["missing_proof_fields"] == []
    dream_template = scorecard.json()["recursive_dream_cycle_request_template"]
    assert dream_template["endpoint"] == "/ops/brain/production-spine/dream-cycles"
    assert dream_template["ready_to_submit"] is True
    assert dream_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert dream_template["template"]["target_node_ref"] == "node:expert_coder"
    assert dream_template["template"]["student_id"] == "student:stu_lifecycle_001"
    assert dream_template["template"]["federated_packet_signature"].startswith("sha256:")
    assert dream_template["template"]["dream_temperature"] == 0.95
    assert dream_template["missing_proof_fields"] == []
    tensor_template = scorecard.json()["tensor_program_request_template"]
    assert tensor_template["endpoint"] == "/ops/brain/production-spine/tensor-programs"
    assert tensor_template["ready_to_submit"] is True
    assert tensor_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert tensor_template["template"]["parameter_refs"]["student"] == "student:stu_lifecycle_001"
    assert len(tensor_template["template"]["ops"]) == 3
    assert tensor_template["template"]["checkpoint"]["restore_validated"] is True
    assert tensor_template["missing_proof_fields"] == []
    hive_route_template = scorecard.json()["hive_moe_route_request_template"]
    assert hive_route_template["endpoint"] == "/ops/brain/production-spine/hive-moe-routes"
    assert hive_route_template["ready_to_submit"] is True
    assert hive_route_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert hive_route_template["template"]["task_features"]["coding"] == 0.8
    assert len(hive_route_template["template"]["candidates"]) == 2
    assert hive_route_template["template"]["top_k"] == 2
    assert hive_route_template["missing_proof_fields"] == []
    child_execution_template = scorecard.json()["child_execution_request_template"]
    assert child_execution_template["endpoint"] == "/ops/brain/production-spine/child-executions"
    assert child_execution_template["ready_to_submit"] is True
    assert child_execution_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert child_execution_template["template"]["student_id"] == "student:stu_lifecycle_001"
    assert child_execution_template["template"]["weights_path"].endswith("checkpoint.json")
    assert child_execution_template["template"]["adapter_bundle_path"].endswith("adapter_artifact_bundle.zip")
    assert child_execution_template["template"]["preferred_weight_artifact"] == "adapter_bundle"
    assert child_execution_template["template"]["input"]["x"] == 4.0
    assert child_execution_template["template"]["neural_bus_required"] is True
    assert child_execution_template["template"]["hive_blackboard_required"] is True
    assert child_execution_template["template"]["eval_hook_required"] is True
    assert child_execution_template["missing_proof_fields"] == []
    sealed_eval_template = scorecard.json()["sealed_eval_gauntlet_request_template"]
    assert sealed_eval_template["endpoint"] == "/ops/brain/production-spine/eval-gauntlets"
    assert sealed_eval_template["ready_to_submit"] is False
    assert sealed_eval_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert sealed_eval_template["template"]["eval_id"] == "eval:coder_birth_001"
    assert sealed_eval_template["template"]["student_id"] == "student:stu_lifecycle_001"
    assert sealed_eval_template["template"]["parent_node_ref"] == "node:expert_coder"
    assert sealed_eval_template["template"]["weights_path"].endswith("checkpoint.json")
    assert sealed_eval_template["template"]["adapter_bundle_path"].endswith("adapter_artifact_bundle.zip")
    assert sealed_eval_template["template"]["preferred_weight_artifact"] == "adapter_bundle"
    assert sealed_eval_template["template"]["hidden_eval_case_count"] == 3
    assert len(sealed_eval_template["template"]["hidden_eval_case_hashes"]) == 3
    assert sealed_eval_template["template"]["hidden_eval_attestation_path"].endswith("hidden_eval_attestation.json")
    assert sealed_eval_template["template"]["comparison_matrix_path"].endswith("comparison_matrix.json")
    assert sealed_eval_template["template"]["student_parent_surpass_margin"] > 0
    assert sealed_eval_template["template"]["student_teacher_surpass_margin"] > 0
    assert sealed_eval_template["template"]["lower_confidence_surpass_bound"] > 0
    assert sealed_eval_template["template"]["teacher_ejection_allowed"] is False
    assert sealed_eval_template["template"]["teacher_ejection_blocker"] == "teacher_ejection_requires_post_promotion_consistency_windows"
    assert "sealed_hidden_case_material_required" in sealed_eval_template["missing_proof_fields"]
    teacher_template = scorecard.json()["teacher_council_review_request_template"]
    assert teacher_template["endpoint"] == "/ops/brain/production-spine/teacher-council-reviews"
    assert teacher_template["ready_to_submit"] is False
    assert teacher_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert teacher_template["template"]["review_id"] == "teacher:coder_birth_001"
    assert teacher_template["template"]["target_node_ref"] == "node:expert_coder"
    assert teacher_template["template"]["teacher_count"] == 3
    assert teacher_template["template"]["license_gate_passed"] is True
    assert teacher_template["template"]["accepted_teacher_ref"] == "node:expert_critique"
    assert teacher_template["template"]["disagreement_score"] > 0
    assert teacher_template["template"]["validator_summary"]["all_passed"] is True
    assert teacher_template["template"]["validator_summary"]["validator_count"] == 2
    assert teacher_template["template"]["compiled_knowledge_context"]["allowed"] is True
    assert "teacher_outputs_payload_required" in teacher_template["missing_proof_fields"]
    sandbox_template = scorecard.json()["sandbox_training_run_request_template"]
    assert sandbox_template["endpoint"] == "/ops/brain/production-spine/training-runs"
    assert sandbox_template["ready_to_submit"] is True
    assert sandbox_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert sandbox_template["template"]["student_id"] == "student:stu_lifecycle_001"
    assert sandbox_template["template"]["training_backend_plan_ref"] == "train_backend:coder_birth_001"
    assert sandbox_template["template"]["dataset_manifest_ref"] == "dataset:coder_birth_001"
    assert sandbox_template["template"]["method"] == "lora"
    assert sandbox_template["template"]["framework"] == "peft"
    assert "sequence_distillation" in sandbox_template["template"]["training_modes"]
    assert sandbox_template["template"]["operator_approved"] is True
    assert sandbox_template["template"]["support_state"] == "sandbox_supported"
    assert sandbox_template["template"]["checkpoint_path"].endswith("checkpoint.json")
    assert sandbox_template["template"]["adapter_bundle_path"].endswith("adapter_artifact_bundle.zip")
    assert sandbox_template["template"]["optimizer_state"]["steps"] == 120
    assert sandbox_template["template"]["training_dataset_row_count"] == 4
    assert "adapter" in sandbox_template["template"]["export_targets"]
    assert sandbox_template["missing_proof_fields"] == []
    deep_replay_template = scorecard.json()["deep_replay_bundle_request_template"]
    assert deep_replay_template["endpoint"] == "/ops/brain/production-spine/deep-replay"
    assert deep_replay_template["ready_to_submit"] is True
    assert deep_replay_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert deep_replay_template["template"]["replay_id"] == "replay:coder_birth_001"
    assert deep_replay_template["template"]["current_signature_state"] == "unsigned_v0"
    assert deep_replay_template["template"]["next_signature_state"] == "signed_ed25519"
    assert deep_replay_template["template"]["production_promotion_requires_real_signing"] is True
    assert deep_replay_template["template"]["real_signing_blocker"] == "ed25519_key_management_not_configured"
    assert deep_replay_template["template"]["deep_replay_bundle_path"].endswith("deep_replay_bundle.json")
    assert deep_replay_template["template"]["artifact_index_path"].endswith("artifact_index.jsonl")
    assert "growth_lifecycle" in deep_replay_template["template"]["drilldowns"]
    assert "sandbox_runner_training" in deep_replay_template["template"]["drilldowns"]
    assert deep_replay_template["template"]["artifact_trust_scan"]["source"] == "deep_replay_bundle"
    assert deep_replay_template["template"]["artifact_trust_scan"]["quarantined_count"] > 0
    assert "real_signing_required" in deep_replay_template["template"]["artifact_trust_scan"]["promotion_blockers"]
    assert "signing_key_file" in deep_replay_template["optional_signature_fields"]
    assert deep_replay_template["missing_proof_fields"] == []
    artifact_trust_template = scorecard.json()["artifact_trust_scan_request_template"]
    assert artifact_trust_template["endpoint"] == "/ops/brain/artifact-trust/scans"
    assert artifact_trust_template["ready_to_submit"] is True
    assert artifact_trust_template["template"]["artifact_id"].startswith("deep-replay::replay:coder_birth_001::")
    assert artifact_trust_template["template"]["artifact_type"] == "adapter"
    assert artifact_trust_template["template"]["uri"].endswith("adapter_artifact_bundle.zip")
    assert artifact_trust_template["template"]["license_status"] == "approved"
    assert artifact_trust_template["template"]["checksum"].startswith("sha256:")
    assert artifact_trust_template["template"]["provenance_refs"][0].endswith("deep_replay_bundle.json")
    assert artifact_trust_template["template"]["signature_ref"] == ""
    assert artifact_trust_template["template"]["metadata"]["source"] == "sandbox_adapter_artifact_bundle"
    assert artifact_trust_template["template"]["metadata"]["replay_id"] == "replay:coder_birth_001"
    assert artifact_trust_template["template"]["metadata"]["relative_path"].endswith("adapter_artifact_bundle.zip")
    assert artifact_trust_template["template"]["latest_scan_status"] == "quarantined"
    assert artifact_trust_template["template"]["signature_required_for_trust"] is True
    assert "real_signing_required" in artifact_trust_template["promotion_blockers"]
    assert artifact_trust_template["missing_proof_fields"] == []
    signing_key_template = scorecard.json()["project_local_signing_key_request_template"]
    assert signing_key_template["endpoint"] == "/ops/brain/production-spine/signing-keys/project-local"
    assert signing_key_template["ready_to_submit"] is False
    assert signing_key_template["template"]["key_id"] == "artifact_signing_key"
    assert signing_key_template["template"]["key_file_path"].endswith("artifact_signing_key.enc.json")
    assert signing_key_template["template"]["passphrase_required"] is True
    assert signing_key_template["template"]["passphrase_persisted"] is False
    assert signing_key_template["template"]["seed_generated_if_omitted"] is True
    assert signing_key_template["template"]["deep_replay_request_fields"] == ["signing_key_file", "signing_key_passphrase"]
    assert signing_key_template["template"]["current_signer_status"] == "blocked"
    assert signing_key_template["template"]["production_mutation_blocker"] == "real_signing_required"
    assert "passphrase" in signing_key_template["manual_secret_fields"]
    assert "passphrase" in signing_key_template["missing_proof_fields"]
    signed_replay_template = scorecard.json()["signed_deep_replay_handoff_request_template"]
    assert signed_replay_template["endpoint"] == "/ops/brain/production-spine/deep-replay"
    assert signed_replay_template["ready_to_submit"] is False
    assert signed_replay_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert signed_replay_template["template"]["source_replay_id"] == "replay:coder_birth_001"
    assert signed_replay_template["template"]["replay_id"] == "replay:coder_birth_001_signed"
    assert signed_replay_template["template"]["signing_key_file"].endswith("artifact_signing_key.enc.json")
    assert signed_replay_template["template"]["signing_key_file_exists"] is False
    assert signed_replay_template["template"]["signing_key_passphrase_provided"] is False
    assert signed_replay_template["template"]["target_signature_state"] == "signed_ed25519"
    assert signed_replay_template["template"]["current_signature_state"] == "unsigned_v0"
    assert signed_replay_template["template"]["artifact_trust_quarantined_count"] > 0
    assert "signing_key_passphrase" in signed_replay_template["manual_secret_fields"]
    assert "signing_key_file_created" in signed_replay_template["missing_proof_fields"]
    assert "signing_key_passphrase" in signed_replay_template["missing_proof_fields"]
    signed_rescan_template = scorecard.json()["signed_replay_artifact_trust_rescan_request_template"]
    assert signed_rescan_template["endpoint"] == "/ops/brain/production-spine/signed-replay-artifact-trust-rescans"
    assert signed_rescan_template["ready_to_submit"] is False
    assert signed_rescan_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert signed_rescan_template["template"]["source_replay_id"] == "replay:coder_birth_001"
    assert signed_rescan_template["template"]["target_replay_id"] == "replay:coder_birth_001_signed"
    assert signed_rescan_template["template"]["target_signature_state"] == "signed_ed25519"
    assert signed_rescan_template["template"]["current_artifact_trust_status"] == "quarantined"
    assert signed_rescan_template["template"]["source_quarantined_count"] > 0
    assert signed_rescan_template["template"]["source_adapter_artifact_status"] == "quarantined"
    assert signed_rescan_template["template"]["source_adapter_artifact_relative_path"].endswith("adapter_artifact_bundle.zip")
    assert signed_rescan_template["template"]["expected_adapter_artifact_trust_status_after_rescan"] == "trusted"
    assert signed_rescan_template["template"]["adapter_scan_request_template"]["artifact_type"] == "adapter"
    assert signed_rescan_template["template"]["adapter_scan_request_template"]["metadata"]["source"] == "sandbox_adapter_artifact_bundle"
    assert signed_rescan_template["template"]["expected_quarantined_count_after_rescan"] == 0
    assert signed_rescan_template["template"]["expected_trusted_count_after_rescan"] == deep_replay_template["template"]["artifact_count"]
    assert signed_rescan_template["template"]["source_artifact_index_path"].endswith("artifact_index.jsonl")
    assert signed_rescan_template["template"]["signed_artifact_index_path"].endswith("artifact_index.jsonl")
    assert "coder_birth_001_signed" in signed_rescan_template["template"]["signed_artifact_index_path"]
    assert "signed_deep_replay_bundle_path" in signed_rescan_template["missing_proof_fields"]
    assert "signed_artifact_index_path" in signed_rescan_template["missing_proof_fields"]
    assert "signed_replay_artifact_signatures" in signed_rescan_template["missing_proof_fields"]
    promotion_handoff_template = scorecard.json()["real_training_promotion_handoff_request_template"]
    assert promotion_handoff_template["endpoint"] == "/ops/brain/production-spine/real-training-gates"
    assert promotion_handoff_template["ready_to_submit"] is False
    assert promotion_handoff_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert promotion_handoff_template["template"]["student_id"] == "student:stu_lifecycle_001"
    assert promotion_handoff_template["template"]["target_signed_replay_id"] == "replay:coder_birth_001_signed"
    assert promotion_handoff_template["template"]["production_mutation_requested"] is False
    assert promotion_handoff_template["template"]["operator_approved"] is False
    assert promotion_handoff_template["template"]["human_approved"] is False
    assert promotion_handoff_template["template"]["allow_real_weight_mutation"] is False
    assert promotion_handoff_template["template"]["artifact_trust_clear"] is False
    assert promotion_handoff_template["template"]["adapter_artifact_trust_status"] == "quarantined"
    assert promotion_handoff_template["template"]["adapter_artifact_trust_clear"] is False
    assert promotion_handoff_template["template"]["source_adapter_artifact_relative_path"].endswith("adapter_artifact_bundle.zip")
    assert promotion_handoff_template["template"]["expected_adapter_artifact_trust_status_after_rescan"] == "trusted"
    assert promotion_handoff_template["template"]["signed_replay_trust_clear"] is False
    assert promotion_handoff_template["template"]["sealed_eval_passed"] is True
    assert promotion_handoff_template["template"]["reviewer_windows_ready"] is False
    assert "trusted_signed_replay_required" in promotion_handoff_template["promotion_blockers"]
    assert "trusted_adapter_artifact_required" in promotion_handoff_template["promotion_blockers"]
    assert "human_approved" in promotion_handoff_template["missing_proof_fields"]
    assert "operator_approved" in promotion_handoff_template["missing_proof_fields"]
    assert "allow_real_weight_mutation" in promotion_handoff_template["manual_approval_fields"]
    node_activation_template = scorecard.json()["runtime_node_activation_handoff_request_template"]
    assert node_activation_template["endpoint"] == "/ops/brain/production-spine/node-registry-decisions"
    assert node_activation_template["ready_to_submit"] is False
    assert node_activation_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert node_activation_template["template"]["student_id"] == "student:stu_lifecycle_001"
    assert node_activation_template["template"]["parent_node_ref"] == "node:expert_coder"
    assert node_activation_template["template"]["requested_runtime_state"] == "canary"
    assert node_activation_template["template"]["current_runtime_state"] == "shadow"
    assert node_activation_template["template"]["rollback_restorable"] is True
    assert node_activation_template["template"]["signed_replay_trust_clear"] is False
    assert node_activation_template["template"]["adapter_artifact_trust_clear"] is False
    assert node_activation_template["template"]["adapter_artifact_trust_status"] == "quarantined"
    assert node_activation_template["template"]["reviewer_windows_ready"] is False
    assert node_activation_template["template"]["canary_window_passed"] is False
    assert "trusted_signed_replay_required" in node_activation_template["activation_blockers"]
    assert "trusted_adapter_artifact_required" in node_activation_template["activation_blockers"]
    assert "adapter_artifact_trust_clear" in node_activation_template["missing_proof_fields"]
    assert "reviewer_windows_ready" in node_activation_template["missing_proof_fields"]
    assert "human_approved" in node_activation_template["missing_proof_fields"]
    runtime_health_template = scorecard.json()["active_runtime_health_monitor_request_template"]
    assert runtime_health_template["endpoint"] == "/ops/brain/production-spine/runtime-health-monitors"
    assert runtime_health_template["ready_to_submit"] is False
    assert runtime_health_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert runtime_health_template["template"]["student_id"] == "student:stu_lifecycle_001"
    assert runtime_health_template["template"]["target_node_ref"] == "node:expert_coder"
    assert runtime_health_template["template"]["current_runtime_state"] == "shadow"
    assert runtime_health_template["template"]["monitor_window"] == "canary_runtime"
    assert runtime_health_template["template"]["rollback_snapshot_path"].endswith("rollback_snapshot.json")
    assert runtime_health_template["template"]["max_error_rate"] == 0.02
    assert runtime_health_template["template"]["max_p95_latency_ms"] == 2000
    assert runtime_health_template["template"]["max_route_share"] == 0.1
    assert runtime_health_template["template"]["auto_disable_on_blocker"] is True
    assert runtime_health_template["template"]["signed_replay_trust_clear"] is False
    assert runtime_health_template["template"]["adapter_artifact_trust_clear"] is False
    assert runtime_health_template["template"]["adapter_artifact_trust_status"] == "quarantined"
    assert "trusted_signed_replay_required" in runtime_health_template["health_blockers"]
    assert "trusted_adapter_artifact_required" in runtime_health_template["health_blockers"]
    assert "adapter_artifact_trust_clear" in runtime_health_template["missing_proof_fields"]
    assert "canary_or_active_runtime_state" in runtime_health_template["missing_proof_fields"]
    assert "health_window_started" in runtime_health_template["missing_proof_fields"]
    runtime_health_preview = client.post(
        "/ops/brain/production-spine/runtime-health-monitors",
        json=runtime_health_template["template"],
    )
    assert runtime_health_preview.status_code == 200
    runtime_health_manifest = runtime_health_preview.json()
    assert runtime_health_manifest["status"] == "manifest_preview_ready"
    assert runtime_health_manifest["monitor_id"] == "runtime-health:cycle:cyc_lifecycle_001"
    assert runtime_health_manifest["decision"] == "blocked"
    assert runtime_health_manifest["runtime_activation_allowed"] is False
    assert runtime_health_manifest["auto_disable_on_blocker"] is True
    assert runtime_health_manifest["current_runtime_state"] == "shadow"
    assert runtime_health_manifest["monitor_window"] == "canary_runtime"
    assert runtime_health_manifest["adapter_artifact_trust_status"] == "quarantined"
    assert runtime_health_manifest["adapter_artifact_trust_clear"] is False
    assert runtime_health_manifest["artifacts"]["monitor_manifest_path"].endswith("runtime_health_monitor_manifest.json")
    assert runtime_health_manifest["source_count"] > 0
    assert "private text must not persist" not in json.dumps(runtime_health_manifest)
    ejection_handoff_template = scorecard.json()["teacher_ejection_parent_retirement_handoff_request_template"]
    assert ejection_handoff_template["endpoint"] == "/ops/brain/production-spine/teacher-ejection-reviews"
    assert ejection_handoff_template["ready_to_submit"] is False
    assert ejection_handoff_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert ejection_handoff_template["template"]["student_id"] == "student:stu_lifecycle_001"
    assert ejection_handoff_template["template"]["parent_node_ref"] == "node:expert_coder"
    assert ejection_handoff_template["template"]["teacher_ejection_allowed"] is False
    assert ejection_handoff_template["template"]["parent_retirement_allowed"] is False
    assert ejection_handoff_template["template"]["post_promotion_window_passed"] is False
    assert ejection_handoff_template["template"]["ivy_grade_review_passed"] is False
    assert ejection_handoff_template["template"]["greatly_outperforms_parent"] is False
    assert ejection_handoff_template["template"]["child_retained_after_parent_retirement"] is True
    assert ejection_handoff_template["template"]["rollback_retention_required"] is True
    assert ejection_handoff_template["template"]["adapter_artifact_trust_status"] == "quarantined"
    assert ejection_handoff_template["template"]["adapter_artifact_trust_clear"] is False
    assert "post_promotion_window_passed" in ejection_handoff_template["missing_proof_fields"]
    assert "ivy_grade_review_passed" in ejection_handoff_template["missing_proof_fields"]
    assert "greatly_outperforms_parent" in ejection_handoff_template["missing_proof_fields"]
    assert "adapter_artifact_trust_clear" in ejection_handoff_template["missing_proof_fields"]
    ejection_preview = client.post(
        "/ops/brain/production-spine/teacher-ejection-reviews",
        json=ejection_handoff_template["template"],
    )
    assert ejection_preview.status_code == 200
    ejection_manifest = ejection_preview.json()
    assert ejection_manifest["status"] == "manifest_preview_ready"
    assert ejection_manifest["review_id"] == "teacher-ejection:cycle:cyc_lifecycle_001"
    assert ejection_manifest["decision"] == "blocked"
    assert ejection_manifest["teacher_ejection_mutation_allowed"] is False
    assert ejection_manifest["parent_retirement_mutation_allowed"] is False
    assert ejection_manifest["teacher_ejection_allowed"] is False
    assert ejection_manifest["parent_retirement_allowed"] is False
    assert ejection_manifest["child_retained_after_parent_retirement"] is True
    assert ejection_manifest["adapter_artifact_trust_status"] == "quarantined"
    assert ejection_manifest["adapter_artifact_trust_clear"] is False
    assert "adapter_artifact_trust_clear" in ejection_manifest["final_review_artifact_blockers"]
    assert ejection_manifest["artifacts"]["review_manifest_path"].endswith("teacher_ejection_review_manifest.json")
    assert ejection_manifest["source_count"] > 0
    assert "private text must not persist" not in json.dumps(ejection_manifest)
    support_bundle_template = scorecard.json()["production_support_bundle_export_request_template"]
    assert support_bundle_template["endpoint"] == "/ops/brain/production-spine/support-bundles"
    assert support_bundle_template["ready_to_submit"] is False
    assert support_bundle_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert support_bundle_template["template"]["bundle_id"] == "support-bundle:cycle:cyc_lifecycle_001"
    assert support_bundle_template["template"]["redact_secrets"] is True
    assert support_bundle_template["template"]["include_raw_private_data"] is False
    assert support_bundle_template["template"]["workspace_paths_redacted"] is True
    assert support_bundle_template["template"]["include_growth_cycle"] is True
    assert support_bundle_template["template"]["include_deep_replay"] is True
    assert support_bundle_template["template"]["include_artifact_trust"] is True
    assert support_bundle_template["template"]["adapter_artifact_trust_status"] == "quarantined"
    assert support_bundle_template["template"]["adapter_artifact_trust_clear"] is False
    assert support_bundle_template["template"]["include_kac_refs"] is True
    assert support_bundle_template["template"]["include_runtime_health"] is True
    assert support_bundle_template["template"]["support_bundle_path"].endswith("support_bundle.zip")
    assert "secret_scan_passed" in support_bundle_template["missing_proof_fields"]
    assert "support_bundle_destination" in support_bundle_template["missing_proof_fields"]
    support_bundle_preview = client.post(
        "/ops/brain/production-spine/support-bundles",
        json=support_bundle_template["template"],
    )
    assert support_bundle_preview.status_code == 200
    support_bundle_manifest = support_bundle_preview.json()
    assert support_bundle_manifest["status"] == "manifest_preview_ready"
    assert support_bundle_manifest["bundle_id"] == "support-bundle:cycle:cyc_lifecycle_001"
    assert support_bundle_manifest["zip_created"] is False
    assert support_bundle_manifest["redact_secrets"] is True
    assert support_bundle_manifest["include_raw_private_data"] is False
    assert support_bundle_manifest["workspace_paths_redacted"] is True
    assert support_bundle_manifest["adapter_artifact_trust_status"] == "quarantined"
    assert support_bundle_manifest["adapter_artifact_trust_clear"] is False
    assert support_bundle_manifest["artifacts"]["support_manifest_path"].endswith("support_bundle_manifest.json")
    assert support_bundle_manifest["source_count"] > 0
    assert "private text must not persist" not in json.dumps(support_bundle_manifest)
    first_run_template = scorecard.json()["first_run_readiness_request_template"]
    assert first_run_template["endpoint"] == "/ops/brain/production-spine/first-run-readiness"
    assert first_run_template["ready_to_submit"] is False
    assert first_run_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert first_run_template["template"]["readiness_id"] == "first-run:cycle:cyc_lifecycle_001"
    assert first_run_template["template"]["local_cache_controls_ready"] is True
    assert first_run_template["template"]["model_download_manager_ready"] is True
    assert first_run_template["template"]["buyer_launcher_ready"] is True
    assert first_run_template["template"]["support_bundle_ready"] is False
    assert first_run_template["template"]["crash_diagnostics_ready"] is True
    assert first_run_template["template"]["buyer_safe_defaults"] is True
    assert first_run_template["template"]["adapter_artifact_trust_status"] == "quarantined"
    assert first_run_template["template"]["adapter_artifact_trust_clear"] is False
    assert first_run_template["template"]["project_local_signing_key_ready"] is False
    assert first_run_template["template"]["key_file_path"].endswith("artifact_signing_key.enc.json")
    assert first_run_template["template"]["model_cache_root_path"].endswith("model-cache")
    assert "local_cache_controls" not in first_run_template["missing_proof_fields"]
    assert "model_download_manager" not in first_run_template["missing_proof_fields"]
    assert "buyer_launcher" not in first_run_template["missing_proof_fields"]
    assert "support_bundle" in first_run_template["missing_proof_fields"]
    assert "adapter_artifact_trust_clear" in first_run_template["missing_proof_fields"]
    assert "project_local_signing_key_ready" in first_run_template["missing_proof_fields"]
    first_run_preview = client.post(
        "/ops/brain/production-spine/first-run-readiness",
        json=first_run_template["template"],
    )
    assert first_run_preview.status_code == 200
    first_run_manifest = first_run_preview.json()
    assert first_run_manifest["status"] == "manifest_preview_ready"
    assert first_run_manifest["readiness_id"] == "first-run:cycle:cyc_lifecycle_001"
    assert first_run_manifest["decision"] == "blocked"
    assert first_run_manifest["installer_mutation_allowed"] is False
    assert first_run_manifest["local_cache_controls_ready"] is True
    assert first_run_manifest["model_download_manager_ready"] is True
    assert first_run_manifest["buyer_launcher_ready"] is True
    assert first_run_manifest["support_bundle_ready"] is False
    assert first_run_manifest["crash_diagnostics_ready"] is True
    assert first_run_manifest["adapter_artifact_trust_status"] == "quarantined"
    assert first_run_manifest["adapter_artifact_trust_clear"] is False
    assert first_run_manifest["artifacts"]["readiness_manifest_path"].endswith("first_run_readiness_manifest.json")
    assert first_run_manifest["source_count"] > 0
    assert "private text must not persist" not in json.dumps(first_run_manifest)
    crash_diagnostics_template = scorecard.json()["crash_diagnostics_export_request_template"]
    assert crash_diagnostics_template["endpoint"] == "/ops/brain/production-spine/crash-diagnostics"
    assert crash_diagnostics_template["ready_to_submit"] is False
    assert crash_diagnostics_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert crash_diagnostics_template["template"]["diagnostics_id"] == "crash-diagnostics:cycle:cyc_lifecycle_001"
    assert crash_diagnostics_template["template"]["crash_diagnostics_ready"] is True
    assert crash_diagnostics_template["template"]["support_bundle_ready"] is False
    assert crash_diagnostics_template["template"]["redact_secrets"] is True
    assert crash_diagnostics_template["template"]["include_raw_private_data"] is False
    assert crash_diagnostics_template["template"]["workspace_paths_redacted"] is True
    assert crash_diagnostics_template["template"]["include_app_logs"] is True
    assert crash_diagnostics_template["template"]["include_runtime_health"] is True
    assert crash_diagnostics_template["template"]["include_support_bundle"] is True
    assert crash_diagnostics_template["template"]["include_deep_replay"] is True
    assert crash_diagnostics_template["template"]["include_artifact_trust"] is True
    assert crash_diagnostics_template["template"]["adapter_artifact_trust_status"] == "quarantined"
    assert crash_diagnostics_template["template"]["adapter_artifact_trust_clear"] is False
    assert crash_diagnostics_template["template"]["diagnostics_bundle_path"].endswith("crash_diagnostics.json")
    assert crash_diagnostics_template["template"]["support_bundle_path"].endswith("support_bundle.zip")
    assert "secret_scan_passed" in crash_diagnostics_template["missing_proof_fields"]
    assert "support_bundle" in crash_diagnostics_template["missing_proof_fields"]
    assert "diagnostics_destination" in crash_diagnostics_template["missing_proof_fields"]
    crash_diagnostics_preview = client.post(
        "/ops/brain/production-spine/crash-diagnostics",
        json=crash_diagnostics_template["template"],
    )
    assert crash_diagnostics_preview.status_code == 200
    crash_diagnostics_manifest = crash_diagnostics_preview.json()
    assert crash_diagnostics_manifest["status"] == "manifest_preview_ready"
    assert crash_diagnostics_manifest["diagnostics_id"] == "crash-diagnostics:cycle:cyc_lifecycle_001"
    assert crash_diagnostics_manifest["logs_packaged"] is False
    assert crash_diagnostics_manifest["redact_secrets"] is True
    assert crash_diagnostics_manifest["include_raw_private_data"] is False
    assert crash_diagnostics_manifest["workspace_paths_redacted"] is True
    assert crash_diagnostics_manifest["adapter_artifact_trust_status"] == "quarantined"
    assert crash_diagnostics_manifest["adapter_artifact_trust_clear"] is False
    assert crash_diagnostics_manifest["artifacts"]["diagnostics_manifest_path"].endswith("crash_diagnostics_manifest.json")
    assert crash_diagnostics_manifest["source_count"] > 0
    assert "private text must not persist" not in json.dumps(crash_diagnostics_manifest)
    release_template = scorecard.json()["release_packaging_handoff_request_template"]
    assert release_template["endpoint"] == "/ops/brain/production-spine/release-packages"
    assert release_template["ready_to_submit"] is False
    assert release_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert release_template["template"]["release_id"] == "release-package:cycle:cyc_lifecycle_001"
    assert release_template["template"]["ci_packaging_ready"] is False
    assert release_template["template"]["buyer_launcher_ready"] is True
    assert release_template["template"]["support_bundle_ready"] is False
    assert release_template["template"]["crash_diagnostics_ready"] is True
    assert release_template["template"]["first_run_readiness_ready"] is False
    assert release_template["template"]["buyer_safe_defaults"] is True
    assert release_template["template"]["artifact_signing_ready"] is False
    assert release_template["template"]["artifact_trust_clear"] is False
    assert release_template["template"]["adapter_artifact_trust_status"] == "quarantined"
    assert release_template["template"]["adapter_artifact_trust_clear"] is False
    assert release_template["template"]["package_output_path"].endswith("release_package.zip")
    assert release_template["template"]["include_installer"] is True
    assert release_template["template"]["include_support_bundle"] is True
    assert release_template["template"]["include_crash_diagnostics"] is True
    assert release_template["template"]["include_first_run_readiness"] is True
    assert "ci_packaging" in release_template["missing_proof_fields"]
    assert "support_bundle" in release_template["missing_proof_fields"]
    assert "release_destination" in release_template["missing_proof_fields"]
    assert "artifact_signing_ready" in release_template["missing_proof_fields"]
    assert "artifact_trust_clear" in release_template["missing_proof_fields"]
    assert "adapter_artifact_trust_clear" in release_template["missing_proof_fields"]
    release_preview = client.post(
        "/ops/brain/production-spine/release-packages",
        json=release_template["template"],
    )
    assert release_preview.status_code == 200
    release_manifest = release_preview.json()
    assert release_manifest["status"] == "manifest_preview_ready"
    assert release_manifest["release_id"] == "release-package:cycle:cyc_lifecycle_001"
    assert release_manifest["package_created"] is False
    assert release_manifest["installer_created"] is False
    assert release_manifest["buyer_release_allowed"] is False
    assert release_manifest["include_installer"] is True
    assert release_manifest["include_support_bundle"] is True
    assert release_manifest["include_crash_diagnostics"] is True
    assert release_manifest["adapter_artifact_trust_clear"] is False
    assert "adapter_artifact_trust_clear" in release_manifest["package_creation_blockers"]
    assert release_manifest["artifacts"]["release_manifest_path"].endswith("release_package_manifest.json")
    assert release_manifest["source_count"] > 0
    assert "private text must not persist" not in json.dumps(release_manifest)
    go_no_go_template = scorecard.json()["release_go_no_go_review_request_template"]
    assert go_no_go_template["endpoint"] == "/ops/brain/production-spine/release-go-no-go"
    assert go_no_go_template["ready_to_submit"] is False
    assert go_no_go_template["template"]["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert go_no_go_template["template"]["review_id"] == "release-go-no-go:cycle:cyc_lifecycle_001"
    assert go_no_go_template["template"]["release_packaging_ready"] is False
    assert go_no_go_template["template"]["first_run_readiness_ready"] is False
    assert go_no_go_template["template"]["crash_diagnostics_ready"] is True
    assert go_no_go_template["template"]["support_bundle_ready"] is False
    assert go_no_go_template["template"]["artifact_trust_clear"] is False
    assert go_no_go_template["template"]["adapter_artifact_trust_status"] == "quarantined"
    assert go_no_go_template["template"]["adapter_artifact_trust_clear"] is False
    assert go_no_go_template["template"]["signed_replay_trust_clear"] is False
    assert go_no_go_template["template"]["reviewer_windows_ready"] is False
    assert go_no_go_template["template"]["operator_approved"] is False
    assert go_no_go_template["template"]["human_approved"] is False
    assert go_no_go_template["template"]["buyer_release_allowed"] is False
    assert "release_packaging_ready" in go_no_go_template["missing_proof_fields"]
    assert "first_run_readiness_ready" in go_no_go_template["missing_proof_fields"]
    assert "support_bundle" in go_no_go_template["missing_proof_fields"]
    assert "trusted_adapter_artifact_required" in go_no_go_template["missing_proof_fields"]
    assert "trusted_signed_replay_required" in go_no_go_template["missing_proof_fields"]
    assert "human_approved" in go_no_go_template["missing_proof_fields"]
    go_no_go_preview = client.post(
        "/ops/brain/production-spine/release-go-no-go",
        json=go_no_go_template["template"],
    )
    assert go_no_go_preview.status_code == 200
    go_no_go_manifest = go_no_go_preview.json()
    assert go_no_go_manifest["status"] == "manifest_preview_ready"
    assert go_no_go_manifest["review_id"] == "release-go-no-go:cycle:cyc_lifecycle_001"
    assert go_no_go_manifest["decision"] == "blocked"
    assert go_no_go_manifest["buyer_release_allowed"] is False
    assert go_no_go_manifest["release_mutation_allowed"] is False
    assert go_no_go_manifest["artifact_trust_clear"] is False
    assert go_no_go_manifest["adapter_artifact_trust_clear"] is False
    assert "trusted_adapter_artifact_required" in go_no_go_manifest["release_blockers"]
    assert go_no_go_manifest["human_approved"] is False
    assert go_no_go_manifest["artifacts"]["review_manifest_path"].endswith("release_go_no_go_manifest.json")
    assert go_no_go_manifest["source_count"] > 0
    assert "private text must not persist" not in json.dumps(go_no_go_manifest)
    actions = scorecard.json()["operator_actions"]
    assert actions["run_growth_lifecycle"]["endpoint"] == "/ops/brain/production-spine/growth-lifecycles"
    assert actions["export_support_bundle"]["endpoint"] == "/ops/brain/production-spine/support-bundles"
    assert actions["record_first_run_readiness"]["endpoint"] == "/ops/brain/production-spine/first-run-readiness"
    assert actions["export_crash_diagnostics"]["endpoint"] == "/ops/brain/production-spine/crash-diagnostics"
    assert actions["preview_release_package"]["endpoint"] == "/ops/brain/production-spine/release-packages"
    assert actions["review_release_go_no_go"]["endpoint"] == "/ops/brain/production-spine/release-go-no-go"
    assert actions["monitor_runtime_health"]["endpoint"] == "/ops/brain/production-spine/runtime-health-monitors"
    assert actions["review_teacher_ejection"]["endpoint"] == "/ops/brain/production-spine/teacher-ejection-reviews"
    assert (
        actions["run_signed_replay_artifact_trust_rescan"]["endpoint"]
        == "/ops/brain/production-spine/signed-replay-artifact-trust-rescans"
    )
    assert actions["inspect_manifest_previews"]["endpoint"] == "/ops/brain/production-spine/manifest-previews"
    assert actions["inspect_manifest_previews"]["method"] == "GET"
    manifest_index = client.get(
        "/ops/brain/production-spine/manifest-previews",
        params={"cycle_id": "cycle:cyc_lifecycle_001"},
    )
    assert manifest_index.status_code == 200
    manifest_payload = manifest_index.json()
    assert manifest_payload["status"] == "manifest_preview_index_ready"
    assert manifest_payload["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert manifest_payload["manifest_count"] >= 7
    assert manifest_payload["mutation_allowed"] is False
    manifest_types = set(manifest_payload["manifest_types"])
    assert "support_bundle_manifest_preview.v0.1" in manifest_types
    assert "first_run_readiness_manifest_preview.v0.1" in manifest_types
    assert "crash_diagnostics_manifest_preview.v0.1" in manifest_types
    assert "release_package_manifest_preview.v0.1" in manifest_types
    assert "release_go_no_go_manifest_preview.v0.1" in manifest_types
    assert "runtime_health_monitor_manifest_preview.v0.1" in manifest_types
    assert "teacher_ejection_review_manifest_preview.v0.1" in manifest_types
    manifests_by_type = {
        item["schema_version"]: item
        for item in manifest_payload["manifests"]
        if item.get("schema_version")
    }
    assert (
        manifests_by_type["support_bundle_manifest_preview.v0.1"]["adapter_artifact_trust_status"]
        == "quarantined"
    )
    assert manifests_by_type["support_bundle_manifest_preview.v0.1"]["adapter_artifact_trust_clear"] is False
    assert (
        manifests_by_type["release_go_no_go_manifest_preview.v0.1"]["adapter_artifact_trust_status"]
        == "quarantined"
    )
    assert manifests_by_type["release_go_no_go_manifest_preview.v0.1"]["adapter_artifact_trust_clear"] is False
    assert manifest_payload["adapter_trust_summary"]["quarantined_count"] >= 2
    assert manifest_payload["adapter_trust_summary"]["trusted_count"] == 0
    assert manifest_payload["adapter_trust_summary"]["clear_count"] == 0
    scorecard_after_manifest_previews = client.get("/ops/brain/canon/production-spine")
    assert (
        scorecard_after_manifest_previews.json()["latest_manifest_preview_index"]["adapter_trust_summary"][
            "quarantined_count"
        ]
        >= 2
    )
    assert str(project_root) not in json.dumps(manifest_payload)
    assert "private text must not persist" not in json.dumps(manifest_payload)

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "latest_lifecycle_replay_consistency" in app_js
    assert "Replay consistency" in app_js
    assert "artifact bridge" in app_js
    assert "reviewer_consistency" in app_js
    assert "teacher ejection" in app_js
    assert "promotion_evidence" in app_js
    assert "Runtime foundry" in app_js
    assert "quality delta" in app_js
    assert "expected_signature_state" in app_js
    assert "signature mismatches" in app_js
    assert "integrity_state" in app_js
    assert "integrity blockers" in app_js
    assert "signature_policy" in app_js
    assert "signed_ed25519" in app_js
    assert "real signing" in app_js
    assert "signer_readiness" in app_js
    assert "production signer" in app_js
    assert "signing_configuration_state" in app_js
    assert "secret persisted" in app_js
    assert "encrypted key file" in app_js
    assert "durable signer" in app_js
    assert "storage scope" in app_js
    assert "bridge_signature_verification_failures" in app_js
    assert "signature verification failures" in app_js
    assert "signature_summary" in app_js
    assert "signing coverage" in app_js
    assert "artifact_trust" in app_js
    assert "trusted replay artifacts" in app_js
    assert "Growth Engine gate" in app_js
    assert "growth_engine_gate" in app_js
    assert "adapter_training_plan_status" in app_js
    assert "artifact trust promotion" in app_js
    assert "promotion_blockers" in app_js
    assert "Sandbox training math replay" in app_js
    assert "training_replay_evidence" in app_js
    assert "math contract" in app_js
    assert "optimizer state" in app_js
    assert "Child execution replay" in app_js
    assert "child_execution_replay_evidence" in app_js
    assert "callable runtime" in app_js
    assert "Hive-MoE route replay" in app_js
    assert "hive_route_replay_evidence" in app_js
    assert "routing mode" in app_js
    assert "Tensor runtime replay" in app_js
    assert "tensor_runtime_replay_evidence" in app_js
    assert "result digest" in app_js
    assert "Reviewer confidence evidence" in app_js
    assert "reviewer_confidence_evidence" in app_js
    assert "Ejection readiness" in app_js
    assert "pending ejection windows" in app_js
    assert "teacher surpass rate" in app_js
    assert "Node registry replay" in app_js
    assert "node_registry_replay_evidence" in app_js
    assert "Node registry snapshot" in app_js
    assert "node registry snapshot trust" in app_js
    assert "node registry snapshot clear" in app_js
    assert "parent retirement" in app_js
    assert "Reviewer-window retirement" in app_js
    assert "reviewer_window_retirement_evidence" in app_js
    assert "active canary" in app_js
    assert "canary window" in app_js
    assert "Federated influence replay" in app_js
    assert "federated_influence_replay_evidence" in app_js
    assert "secure agg" in app_js
    assert "Recursive dream replay" in app_js
    assert "recursive_dream_replay_evidence" in app_js
    assert "sandbox seed" in app_js
    assert "Runtime foundry replay" in app_js
    assert "runtime_foundry_replay_evidence" in app_js
    assert "backend proof" in app_js
    assert "runtime canary" in app_js
    assert "eval delta" in app_js
    assert "Productization replay" in app_js
    assert "productization_replay_evidence" in app_js
    assert "support bundle" in app_js
    assert "Lifecycle evidence chain" in app_js
    assert "latest_lifecycle_evidence_chain" in app_js
    assert "evidence blocks" in app_js
    assert "Finish readiness map" in app_js
    assert "finish_readiness_map" in app_js
    assert "finish gates" in app_js
    assert "Real training execution gate" in app_js
    assert "latest_real_training_execution_gate" in app_js
    assert "weight mutation" in app_js
    assert "Real training artifact trust" in app_js
    assert "artifact_trust_handoff" in app_js
    assert "Real training replay drilldowns" in app_js
    assert "latest_deep_replay_drilldown_summary" in app_js
    assert "real_training_artifact_trust" in app_js
    assert "Real training gate request template" in app_js
    assert "real_training_gate_request_template" in app_js
    assert "Productization readiness request template" in app_js
    assert "productization_readiness_request_template" in app_js
    assert "productization adapter trust" in app_js
    assert "productization adapter clear" in app_js
    assert "Runtime quantization foundry request template" in app_js
    assert "runtime_quantization_foundry_request_template" in app_js
    assert "Reviewer-window request template" in app_js
    assert "reviewer_window_request_template" in app_js
    assert "Node registry decision request template" in app_js
    assert "node_registry_decision_request_template" in app_js
    assert "node adapter trust" in app_js
    assert "node adapter clear" in app_js
    assert "Federated packet request template" in app_js
    assert "federated_packet_request_template" in app_js
    assert "Recursive dream-cycle request template" in app_js
    assert "recursive_dream_cycle_request_template" in app_js
    assert "Tensor program request template" in app_js
    assert "tensor_program_request_template" in app_js
    assert "Hive-MoE route request template" in app_js
    assert "hive_moe_route_request_template" in app_js
    assert "Child execution request template" in app_js
    assert "child_execution_request_template" in app_js
    assert "preferred artifact" in app_js
    assert "preferred_weight_artifact" in app_js
    assert "Sealed eval-gauntlet request template" in app_js
    assert "sealed_eval_gauntlet_request_template" in app_js
    assert "sealed preferred artifact" in app_js
    assert "sealed adapter bundle" in app_js
    assert "Teacher council review request template" in app_js
    assert "teacher_council_review_request_template" in app_js
    assert "Sandbox training-run request template" in app_js
    assert "sandbox_training_run_request_template" in app_js
    assert "adapter bundle" in app_js
    assert "adapter_bundle_path" in app_js
    assert "Training backend plan request template" in app_js
    assert "training_backend_plan_request_template" in app_js
    assert "Deep replay bundle request template" in app_js
    assert "deep_replay_bundle_request_template" in app_js
    assert "Artifact trust scan request template" in app_js
    assert "artifact_trust_scan_request_template" in app_js
    assert "adapter artifact trust" in app_js
    assert "adapter relative path" in app_js
    assert "adapter quarantine" in app_js
    assert "Project-local signing key request template" in app_js
    assert "project_local_signing_key_request_template" in app_js
    assert "Signed deep replay handoff request template" in app_js
    assert "signed_deep_replay_handoff_request_template" in app_js
    assert "Signed replay artifact-trust rescan request template" in app_js
    assert "signed_replay_artifact_trust_rescan_request_template" in app_js
    assert "signed adapter trust" in app_js
    assert "signed adapter path" in app_js
    assert "Real-training promotion handoff request template" in app_js
    assert "real_training_promotion_handoff_request_template" in app_js
    assert "adapter trust gate" in app_js
    assert "adapter trust clear" in app_js
    assert "Runtime node activation handoff request template" in app_js
    assert "runtime_node_activation_handoff_request_template" in app_js
    assert "runtime adapter trust" in app_js
    assert "runtime adapter clear" in app_js
    assert "Active runtime health monitor request template" in app_js
    assert "active_runtime_health_monitor_request_template" in app_js
    assert "health adapter trust" in app_js
    assert "health adapter clear" in app_js
    assert "Teacher ejection / parent retirement handoff request template" in app_js
    assert "teacher_ejection_parent_retirement_handoff_request_template" in app_js
    assert "Production support-bundle export request template" in app_js
    assert "production_support_bundle_export_request_template" in app_js
    assert "support adapter trust" in app_js
    assert "support adapter clear" in app_js
    assert "First-run readiness request template" in app_js
    assert "first_run_readiness_request_template" in app_js
    assert "first-run adapter trust" in app_js
    assert "first-run adapter clear" in app_js
    assert "Crash diagnostics export request template" in app_js
    assert "crash_diagnostics_export_request_template" in app_js
    assert "crash adapter trust" in app_js
    assert "crash adapter clear" in app_js
    assert "Release packaging handoff request template" in app_js
    assert "release_packaging_handoff_request_template" in app_js
    assert "release adapter trust" in app_js
    assert "release adapter clear" in app_js
    assert "Release go/no-go review request template" in app_js
    assert "release_go_no_go_review_request_template" in app_js
    assert "go/no-go adapter trust" in app_js
    assert "go/no-go adapter clear" in app_js
    assert "operatorActionEntries.record_reviewer_window" in app_js
    assert "operatorActionEntries.inspect_manifest_previews" in app_js
    assert "ejection adapter trust" in app_js
    assert "ejection adapter clear" in app_js
    assert "Manifest preview index" in app_js
    assert "manifest-preview replay index" in app_js
    assert "manifest adapter trust" in app_js
    assert "manifest adapter clear" in app_js
    assert "manifest trusted count" in app_js
    assert "manifest quarantined count" in app_js
    assert "Live production-spine action endpoints" in app_js


def test_growth_lifecycle_orchestrator_records_blocked_training_without_crashing(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = lifecycle_request()
    request.update(
        {
            "lifecycle_id": "lifecycle:blocked_private_training",
            "cycle_id": "cycle:cyc_lifecycle_blocked",
            "operator_approved": False,
            "contains_private_data": True,
            "raw_private_data": "blocked private lifecycle payload must not persist",
        }
    )

    lifecycle = spine.run_growth_lifecycle(request)

    assert lifecycle["status"] == "closed_loop_blocked"
    assert lifecycle["training_backend_plan"]["status"] == "blocked"
    assert lifecycle["training"]["status"] == "blocked"
    assert lifecycle["child_execution"]["status"] == "blocked"
    assert lifecycle["sealed_eval"]["status"] == "blocked"
    assert lifecycle["sealed_eval"]["ejection_readiness_evidence"]["status"] == "blocked"
    assert lifecycle["sealed_eval"]["ejection_readiness_evidence"]["teacher_ejection_allowed"] is False
    assert lifecycle["sealed_eval"]["reviewer_confidence_evidence"]["ejection_readiness_evidence"]["status"] == "blocked"
    assert "training_blocked" in lifecycle["blocked_reasons"]
    assert lifecycle["production_mutation_allowed"] is False

    lifecycle_dir = tmp_path / "growth" / "production-spine" / "cyc_lifecycle_blocked" / "growth-lifecycles" / "blocked_private_training"
    report_text = (lifecycle_dir / "lifecycle_report.json").read_text(encoding="utf-8")
    assert "blocked private lifecycle payload must not persist" not in report_text


def test_growth_lifecycle_orchestrator_blocks_growth_engine_adapter_gate(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = lifecycle_request()
    request.update(
        {
            "lifecycle_id": "lifecycle:growth_gate_blocked",
            "cycle_id": "cycle:cyc_growth_gate_blocked",
            "adapter_training_plan_ref": "adapter-plan:blocked_dataset_radar_review",
            "adapter_training_plan_status": "blocked",
            "growth_gate": {
                "gate_id": "growth_engine_adapter_training_gate",
                "allowed": False,
                "blockers": [
                    {
                        "rule_id": "growth_engine_adapter_training_gate_blocked",
                        "severity": "hard_fail",
                        "message": "Dataset Radar training review gate blocked the adapter plan.",
                    }
                ],
            },
        }
    )

    lifecycle = spine.run_growth_lifecycle(request)

    assert lifecycle["status"] == "closed_loop_blocked"
    assert lifecycle["production_mutation_allowed"] is False
    assert lifecycle["growth_engine_gate"]["allowed"] is False
    assert lifecycle["growth_engine_gate"]["adapter_training_plan_status"] == "blocked"
    assert lifecycle["growth_engine_gate"]["adapter_training_plan_ref"] == "adapter-plan:blocked_dataset_radar_review"
    assert "growth_engine_adapter_training_plan_blocked" in lifecycle["blocked_reasons"]
    assert "growth_engine_adapter_training_gate_blocked" in lifecycle["blocked_reasons"]
    assert lifecycle["closed_loop_summary"]["child_promoted"] is False
    assert lifecycle["closed_loop_summary"]["growth_engine_gate_clear"] is False
    assert lifecycle["artifact_trust"]["promotion_allowed"] is False
    assert "growth_engine_adapter_training_gate_blocked" in lifecycle["artifact_trust"]["promotion_blockers"]
    assert lifecycle["productization"]["release_ready"] is False

    scorecard = spine.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["blocked_lifecycle_count"] == 1
    assert scorecard["latest_lifecycle"]["status"] == "closed_loop_blocked"


def test_growth_lifecycle_orchestrator_can_clear_signer_gate_with_configured_seed(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = lifecycle_request()
    seed_hex = "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
    request["signing_seed_hex"] = seed_hex

    lifecycle = spine.run_growth_lifecycle(request)

    assert lifecycle["deep_replay"]["signature_policy"]["current_signature_state"] == "signed_ed25519"
    assert lifecycle["replay_consistency"]["expected_signature_state"] == "signed_ed25519"
    assert lifecycle["signer_readiness"]["status"] == "ready"
    assert lifecycle["signer_readiness"]["production_mutation_blocker"] is None
    assert lifecycle["closed_loop_summary"]["signer_ready"] is True
    assert "real_signing_required" not in lifecycle["blocked_reasons"]
    assert lifecycle["deep_replay"]["signature_policy"]["signing_secret_persisted"] is False
    assert lifecycle["signer_readiness"]["signing_secret_persisted"] is False
    assert lifecycle["artifact_trust"]["source"] == "deep_replay_bundle"
    assert lifecycle["artifact_trust"]["trusted_count"] == lifecycle["deep_replay"]["artifact_count"]
    assert lifecycle["artifact_trust"]["quarantined_count"] == 0
    assert lifecycle["closed_loop_summary"]["artifact_trusted"] is True

    lifecycle_report_text = open(lifecycle["artifacts"]["lifecycle_report_path"], encoding="utf-8").read()
    deep_replay_text = open(lifecycle["deep_replay"]["artifacts"]["deep_replay_bundle_path"], encoding="utf-8").read()
    artifact_index_text = open(lifecycle["deep_replay"]["artifacts"]["artifact_index_path"], encoding="utf-8").read()
    artifact_index_records = [json.loads(line) for line in artifact_index_text.splitlines() if line.strip()]
    assert all(not record["relative_path"].startswith("security/artifact-trust") for record in artifact_index_records)
    assert seed_hex not in lifecycle_report_text
    assert seed_hex not in deep_replay_text
    assert seed_hex not in artifact_index_text


def test_growth_lifecycle_orchestrator_uses_project_local_encrypted_signing_key_file(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = lifecycle_request()
    seed = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
    passphrase = "project-local-lifecycle-passphrase"
    key_file = tmp_path / "runtime" / "security" / "signing" / "artifact_signing_key.enc.json"
    ProjectLocalSigningKeyStore.create(key_file, seed=seed, passphrase=passphrase)
    request["signing_key_file"] = str(key_file)
    request["signing_key_passphrase"] = passphrase

    lifecycle = spine.run_growth_lifecycle(request)

    signature_policy = lifecycle["deep_replay"]["signature_policy"]
    assert signature_policy["current_signature_state"] == "signed_ed25519"
    assert signature_policy["signing_key_source"] == "project_local_encrypted_key_file"
    assert signature_policy["signing_secret_persisted"] is False
    assert signature_policy["encrypted_key_file_persisted"] is True
    assert signature_policy["signing_key_storage_scope"] == "project_local_encrypted_file"
    assert lifecycle["signer_readiness"]["status"] == "ready"
    assert lifecycle["signer_readiness"]["durable_project_local_signer"] is True
    assert lifecycle["signer_readiness"]["encrypted_key_file_persisted"] is True

    lifecycle_report_text = open(lifecycle["artifacts"]["lifecycle_report_path"], encoding="utf-8").read()
    deep_replay_text = open(lifecycle["deep_replay"]["artifacts"]["deep_replay_bundle_path"], encoding="utf-8").read()
    artifact_index_text = open(lifecycle["deep_replay"]["artifacts"]["artifact_index_path"], encoding="utf-8").read()
    assert seed.hex() not in lifecycle_report_text
    assert seed.hex() not in deep_replay_text
    assert seed.hex() not in artifact_index_text
    assert passphrase not in lifecycle_report_text
    assert passphrase not in deep_replay_text
    assert passphrase not in artifact_index_text


def test_signed_replay_artifact_trust_rescan_updates_live_lifecycle_scorecard(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(project_root))

    lifecycle = client.post("/ops/brain/production-spine/growth-lifecycles", json=lifecycle_request())
    assert lifecycle.status_code == 200
    initial_scorecard = client.get("/ops/brain/canon/production-spine")
    assert initial_scorecard.status_code == 200
    initial_rescan_template = initial_scorecard.json()["signed_replay_artifact_trust_rescan_request_template"]
    assert initial_rescan_template["ready_to_submit"] is False
    assert "signed_artifact_index_path" in initial_rescan_template["missing_proof_fields"]

    passphrase = "project-local-rescan-passphrase"
    key_template = initial_scorecard.json()["project_local_signing_key_request_template"]["template"]
    key_created = client.post(
        "/ops/brain/production-spine/signing-keys/project-local",
        json={
            "key_id": key_template["key_id"],
            "key_file_path": key_template["key_file_path"],
            "passphrase": passphrase,
            "seed_hex": "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        },
    )
    assert key_created.status_code == 200
    assert key_created.json()["status"] == "created"

    handoff = client.get("/ops/brain/canon/production-spine").json()["signed_deep_replay_handoff_request_template"]
    signed_replay_request = handoff["template"]
    signed_replay_request["signing_key_passphrase"] = passphrase
    signed_replay = client.post("/ops/brain/production-spine/deep-replay", json=signed_replay_request)
    assert signed_replay.status_code == 200
    assert signed_replay.json()["signature_policy"]["current_signature_state"] == "signed_ed25519"

    signed_scorecard = client.get("/ops/brain/canon/production-spine")
    signed_rescan_template = signed_scorecard.json()["signed_replay_artifact_trust_rescan_request_template"]
    assert signed_rescan_template["ready_to_submit"] is True
    assert signed_rescan_template["missing_proof_fields"] == []
    assert signed_rescan_template["template"]["signed_artifact_signature_summary"]["all_signed"] is True

    rescan = client.post(
        "/ops/brain/production-spine/signed-replay-artifact-trust-rescans",
        json=signed_rescan_template["template"],
    )

    assert rescan.status_code == 200
    assert rescan.json()["status"] == "trusted_rescan_recorded"
    assert rescan.json()["cycle_id"] == "cycle:cyc_lifecycle_001"
    assert rescan.json()["source_replay_id"] == "replay:coder_birth_001"
    assert rescan.json()["target_replay_id"] == "replay:coder_birth_001_signed"
    assert rescan.json()["artifact_trust"]["quarantined_count"] == 0
    assert rescan.json()["artifact_trust"]["adapter_artifact_trust_status"] == "trusted"
    assert rescan.json()["adapter_artifact_trust_clear"] is True
    assert rescan.json()["active_production_mutation_allowed"] is False
    assert rescan.json()["raw_content_included"] is False
    assert passphrase not in json.dumps(rescan.json(), sort_keys=True)

    updated_scorecard = client.get("/ops/brain/canon/production-spine").json()
    latest_lifecycle = updated_scorecard["latest_lifecycle"]
    assert latest_lifecycle["artifact_trust"]["adapter_artifact_trust_status"] == "trusted"
    assert latest_lifecycle["artifact_trust"]["quarantined_count"] == 0
    assert latest_lifecycle["artifact_trust"]["signed_replay_artifact_trust_rescan_ref"].endswith(
        "signed_replay_artifact_trust_rescan.json"
    )
    assert latest_lifecycle["closed_loop_summary"]["artifact_trusted"] is True
    assert latest_lifecycle["production_mutation_allowed"] is False

    promotion_template = updated_scorecard["real_training_promotion_handoff_request_template"]["template"]
    assert promotion_template["adapter_artifact_trust_status"] == "trusted"
    assert promotion_template["adapter_artifact_trust_clear"] is True
    assert "trusted_adapter_artifact_required" not in updated_scorecard[
        "real_training_promotion_handoff_request_template"
    ]["promotion_blockers"]
    first_run_template = updated_scorecard["first_run_readiness_request_template"]
    assert first_run_template["template"]["adapter_artifact_trust_status"] == "trusted"
    assert first_run_template["template"]["adapter_artifact_trust_clear"] is True
    assert "adapter_artifact_trust_clear" not in first_run_template["missing_proof_fields"]
    release_template = updated_scorecard["release_packaging_handoff_request_template"]
    assert release_template["template"]["adapter_artifact_trust_status"] == "trusted"
    assert release_template["template"]["adapter_artifact_trust_clear"] is True
    assert "adapter_artifact_trust_clear" not in release_template["missing_proof_fields"]


def test_post_rescan_runtime_activation_and_health_update_live_lifecycle_scorecard(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(project_root))

    lifecycle = client.post("/ops/brain/production-spine/growth-lifecycles", json=lifecycle_request())
    assert lifecycle.status_code == 200

    passphrase = "project-local-runtime-activation-passphrase"
    key_template = client.get("/ops/brain/canon/production-spine").json()["project_local_signing_key_request_template"][
        "template"
    ]
    key_created = client.post(
        "/ops/brain/production-spine/signing-keys/project-local",
        json={
            "key_id": key_template["key_id"],
            "key_file_path": key_template["key_file_path"],
            "passphrase": passphrase,
            "seed_hex": "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        },
    )
    assert key_created.status_code == 200

    signed_handoff = client.get("/ops/brain/canon/production-spine").json()["signed_deep_replay_handoff_request_template"]
    signed_replay_request = signed_handoff["template"]
    signed_replay_request["signing_key_passphrase"] = passphrase
    signed_replay = client.post("/ops/brain/production-spine/deep-replay", json=signed_replay_request)
    assert signed_replay.status_code == 200
    assert signed_replay.json()["signature_policy"]["current_signature_state"] == "signed_ed25519"

    signed_rescan_template = client.get("/ops/brain/canon/production-spine").json()[
        "signed_replay_artifact_trust_rescan_request_template"
    ]
    rescan = client.post(
        "/ops/brain/production-spine/signed-replay-artifact-trust-rescans",
        json=signed_rescan_template["template"],
    )
    assert rescan.status_code == 200
    assert rescan.json()["status"] == "trusted_rescan_recorded"

    reviewer_request = client.get("/ops/brain/canon/production-spine").json()["reviewer_window_request_template"]["template"]
    reviewer_request.update(
        {
            "advancement_id": "reviewer-window:post_rescan_runtime_all_windows",
            "window": "post_promotion",
            "window_status": "passed",
            "passed_windows": ["initial_eval", "shadow_runtime", "canary"],
            "lower_confidence_surpass_bound": 0.08,
            "required_lower_confidence_margin": 0.01,
            "teacher_ejection_review_requested": True,
            "parent_retirement_review_requested": True,
            "human_approved": True,
            "governance_approved": True,
        }
    )
    reviewer = client.post("/ops/brain/production-spine/reviewer-windows", json=reviewer_request)
    assert reviewer.status_code == 200
    assert reviewer.json()["ejection_readiness_evidence"]["status"] == "ready"

    activation_template = client.get("/ops/brain/canon/production-spine").json()[
        "runtime_node_activation_handoff_request_template"
    ]["template"]
    activation_request = dict(activation_template)
    activation_request.update(
        {
            "decision_id": "decision:activate_runtime_canary_post_rescan",
            "action": "activate_child_runtime",
            "requested_runtime_state": "canary",
            "current_runtime_state": "shadow",
            "human_approved": True,
            "reviewer_windows_ready": True,
            "shadow_runtime_window_passed": True,
            "canary_window_passed": False,
        }
    )
    activation = client.post("/ops/brain/production-spine/node-registry-decisions", json=activation_request)
    assert activation.status_code == 200
    assert activation.json()["decision"] == "activate_child_runtime"
    assert activation.json()["student_state"] == "canary"
    assert activation.json()["node_registry_replay_evidence"]["student_state"] == "canary"
    assert activation.json()["node_registry_replay_evidence"]["adapter_artifact_trust_clear"] is True
    assert activation.json()["node_registry_snapshot"]["status"] == "node_registry_snapshot_ready"

    after_activation = client.get("/ops/brain/canon/production-spine").json()
    assert after_activation["latest_lifecycle"]["node_registry"]["decision"] == "activate_child_runtime"
    assert after_activation["latest_lifecycle"]["node_registry_replay_evidence"]["student_state"] == "canary"
    assert after_activation["latest_lifecycle"]["node_registry_snapshot"]["status"] == "node_registry_snapshot_ready"
    runtime_health_template = after_activation["active_runtime_health_monitor_request_template"]["template"]
    assert runtime_health_template["current_runtime_state"] == "canary"
    assert runtime_health_template["adapter_artifact_trust_clear"] is True
    assert runtime_health_template["rollback_restorable"] is True

    runtime_health_request = dict(runtime_health_template)
    runtime_health_request.update(
        {
            "monitor_id": "runtime-health:post_rescan_canary",
            "health_window_started": True,
            "route_share_observed": 0.05,
            "error_rate_observed": 0.0,
            "p95_latency_ms_observed": 250,
        }
    )
    runtime_health = client.post("/ops/brain/production-spine/runtime-health-monitors", json=runtime_health_request)
    assert runtime_health.status_code == 200
    assert runtime_health.json()["decision"] == "ready"
    assert runtime_health.json()["health_report_created"] is True

    updated_scorecard = client.get("/ops/brain/canon/production-spine").json()
    latest_lifecycle = updated_scorecard["latest_lifecycle"]
    assert latest_lifecycle["runtime_health_monitor"]["decision"] == "ready"
    assert latest_lifecycle["runtime_health_monitor"]["health_report_created"] is True
    assert updated_scorecard["active_runtime_health_monitor_request_template"]["template"]["health_window_started"] is True
    assert updated_scorecard["finish_readiness_map"]["gates"][6]["gate_id"] == "durable_node_registry"
    assert updated_scorecard["finish_readiness_map"]["gates"][6]["status"] == "ready"
    assert passphrase not in json.dumps(updated_scorecard, sort_keys=True)


def test_release_manifest_previews_update_live_lifecycle_scorecard(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(project_root))

    lifecycle = client.post("/ops/brain/production-spine/growth-lifecycles", json=lifecycle_request())
    assert lifecycle.status_code == 200

    passphrase = "project-local-release-manifest-passphrase"
    scorecard = client.get("/ops/brain/canon/production-spine").json()
    key_template = scorecard["project_local_signing_key_request_template"]["template"]
    key_created = client.post(
        "/ops/brain/production-spine/signing-keys/project-local",
        json={
            "key_id": key_template["key_id"],
            "key_file_path": key_template["key_file_path"],
            "passphrase": passphrase,
            "seed_hex": "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        },
    )
    assert key_created.status_code == 200

    signed_request = client.get("/ops/brain/canon/production-spine").json()["signed_deep_replay_handoff_request_template"][
        "template"
    ]
    signed_request["signing_key_passphrase"] = passphrase
    signed_replay = client.post("/ops/brain/production-spine/deep-replay", json=signed_request)
    assert signed_replay.status_code == 200

    signed_rescan_template = client.get("/ops/brain/canon/production-spine").json()[
        "signed_replay_artifact_trust_rescan_request_template"
    ]
    rescan = client.post(
        "/ops/brain/production-spine/signed-replay-artifact-trust-rescans",
        json=signed_rescan_template["template"],
    )
    assert rescan.status_code == 200
    assert rescan.json()["adapter_artifact_trust_clear"] is True

    reviewer_request = client.get("/ops/brain/canon/production-spine").json()["reviewer_window_request_template"]["template"]
    reviewer_request.update(
        {
            "advancement_id": "reviewer-window:release_manifest_all_windows",
            "window": "post_promotion",
            "window_status": "passed",
            "passed_windows": ["initial_eval", "shadow_runtime", "canary"],
            "lower_confidence_surpass_bound": 0.08,
            "required_lower_confidence_margin": 0.01,
            "teacher_ejection_review_requested": True,
            "parent_retirement_review_requested": True,
            "human_approved": True,
            "governance_approved": True,
        }
    )
    reviewer = client.post("/ops/brain/production-spine/reviewer-windows", json=reviewer_request)
    assert reviewer.status_code == 200
    assert reviewer.json()["ejection_readiness_evidence"]["status"] == "ready"

    productization_request = client.get("/ops/brain/canon/production-spine").json()[
        "productization_readiness_request_template"
    ]["template"]
    for gate in (
        "local_cache_controls",
        "secret_scan_passed",
        "model_download_manager",
        "support_bundle",
        "crash_diagnostics",
        "ci_packaging",
        "buyer_launcher",
        "docs_complete",
        "buyer_safe_defaults",
        "runtime_gates_clear",
        "artifact_signing_ready",
        "artifact_trust_clear",
        "adapter_artifact_trust_clear",
    ):
        productization_request[gate] = True
    productization = client.post(
        "/ops/brain/production-spine/productization-readiness",
        json=productization_request,
    )
    assert productization.status_code == 200
    assert productization.json()["release_ready"] is True

    after_productization = client.get("/ops/brain/canon/production-spine").json()
    assert after_productization["latest_lifecycle"]["productization"]["release_ready"] is True
    assert after_productization["latest_lifecycle"]["productization_replay_evidence"]["release_ready"] is True

    support_request = after_productization["production_support_bundle_export_request_template"]["template"]
    support_request["support_bundle_destination"] = str(tmp_path / "operator-exports" / "support_bundle.zip")
    support = client.post("/ops/brain/production-spine/support-bundles", json=support_request)
    assert support.status_code == 200
    assert support.json()["zip_created"] is True

    first_run_request = client.get("/ops/brain/canon/production-spine").json()["first_run_readiness_request_template"][
        "template"
    ]
    first_run_request["operator_approved"] = True
    first_run = client.post("/ops/brain/production-spine/first-run-readiness", json=first_run_request)
    assert first_run.status_code == 200
    assert first_run.json()["decision"] == "ready"
    assert first_run.json()["readiness_bundle_created"] is True

    diagnostics_request = client.get("/ops/brain/canon/production-spine").json()["crash_diagnostics_export_request_template"][
        "template"
    ]
    diagnostics_request["diagnostics_destination"] = str(tmp_path / "operator-exports" / "crash_diagnostics.json")
    diagnostics = client.post("/ops/brain/production-spine/crash-diagnostics", json=diagnostics_request)
    assert diagnostics.status_code == 200
    assert diagnostics.json()["logs_packaged"] is True

    release_request = client.get("/ops/brain/canon/production-spine").json()["release_packaging_handoff_request_template"][
        "template"
    ]
    assert release_request["first_run_readiness_ready"] is True
    release_request["release_destination"] = str(tmp_path / "operator-exports" / "release_package.zip")
    release_package = client.post("/ops/brain/production-spine/release-packages", json=release_request)
    assert release_package.status_code == 200
    assert release_package.json()["package_created"] is True
    assert release_package.json()["buyer_release_allowed"] is True

    go_no_go_request = client.get("/ops/brain/canon/production-spine").json()["release_go_no_go_review_request_template"][
        "template"
    ]
    assert go_no_go_request["release_packaging_ready"] is True
    assert go_no_go_request["first_run_readiness_ready"] is True
    go_no_go_request.update(
        {
            "operator_approved": True,
            "human_approved": True,
            "buyer_release_allowed": True,
        }
    )
    go_no_go = client.post("/ops/brain/production-spine/release-go-no-go", json=go_no_go_request)
    assert go_no_go.status_code == 200
    assert go_no_go.json()["decision"] == "approved"
    assert go_no_go.json()["release_mutation_allowed"] is False

    updated_scorecard = client.get("/ops/brain/canon/production-spine").json()
    latest_lifecycle = updated_scorecard["latest_lifecycle"]
    assert latest_lifecycle["support_bundle_manifest"]["zip_created"] is True
    assert latest_lifecycle["first_run_readiness"]["decision"] == "ready"
    assert latest_lifecycle["crash_diagnostics"]["logs_packaged"] is True
    assert latest_lifecycle["release_package"]["package_created"] is True
    assert latest_lifecycle["release_go_no_go"]["decision"] == "approved"
    release_rollup = updated_scorecard["release_manifest_status_rollup"]
    assert release_rollup["status"] == "approved"
    assert release_rollup["support_bundle_status"] == "ready"
    assert release_rollup["first_run_status"] == "ready"
    assert release_rollup["crash_diagnostics_status"] == "ready"
    assert release_rollup["release_package_status"] == "ready"
    assert release_rollup["go_no_go_status"] == "approved"
    assert release_rollup["buyer_release_allowed"] is True
    assert release_rollup["release_mutation_allowed"] is False
    assert passphrase not in json.dumps(updated_scorecard, sort_keys=True)


def test_growth_lifecycle_orchestrator_accepts_productization_gate_proofs(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = lifecycle_request()
    request["human_approved"] = True
    request["signing_seed_hex"] = "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
    request["productization_readiness"] = {
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

    lifecycle = spine.run_growth_lifecycle(request)

    assert lifecycle["productization"]["release_ready"] is True
    assert lifecycle["productization"]["open_gates"] == []
    assert lifecycle["productization_replay_evidence"]["status"] == "ready"
    assert lifecycle["productization_replay_evidence"]["release_ready"] is True
    assert lifecycle["productization_replay_evidence"]["open_gates"] == []

    finish_map = spine.scorecard()["finish_readiness_map"]
    gates_by_id = {gate["gate_id"]: gate for gate in finish_map["gates"]}
    assert gates_by_id["productization"]["status"] == "ready"
    assert "assess_productization" not in finish_map["next_operator_actions"]


def test_support_bundle_export_creates_sanitized_zip_only_after_gates(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = {
        "cycle_id": "cycle:support_bundle_zip",
        "bundle_id": "support-bundle:zip_gate",
        "student_id": "student:zip_gate",
        "target_node_ref": "node:expert_coder",
        "redact_secrets": True,
        "include_raw_private_data": False,
        "workspace_paths_redacted": True,
        "include_growth_cycle": True,
        "include_deep_replay": True,
        "include_artifact_trust": True,
        "include_kac_refs": True,
        "include_runtime_health": True,
        "source_refs": {
            "growth_cycle": str(tmp_path / "runtime" / "private" / "growth_cycle.json"),
            "local_note": "private text must not persist",
        },
    }

    blocked = spine.build_support_bundle_manifest(request)

    assert blocked["zip_created"] is False
    assert blocked["zip_creation_allowed"] is False
    assert "secret_scan_passed" in blocked["zip_creation_blockers"]
    assert "support_bundle_destination" in blocked["zip_creation_blockers"]

    allowed = spine.build_support_bundle_manifest(
        {
            **request,
            "secret_scan_passed": True,
            "support_bundle_destination": "operator-approved-local-support-handoff",
        }
    )

    assert allowed["zip_created"] is True
    assert allowed["zip_creation_allowed"] is True
    assert allowed["zip_creation_blockers"] == []
    assert allowed["artifacts"]["support_bundle_path"].endswith("support_bundle.zip")
    assert "private text must not persist" not in json.dumps(allowed)

    with zipfile.ZipFile(allowed["artifacts"]["support_bundle_path"]) as bundle:
        names = set(bundle.namelist())
        manifest_text = bundle.read("support_bundle_manifest.json").decode("utf-8")

    assert "support_bundle_manifest.json" in names
    assert "support_bundle_events.jsonl" in names
    assert "private text must not persist" not in manifest_text
    assert str(tmp_path) not in manifest_text


def test_crash_diagnostics_export_writes_sanitized_bundle_only_after_gates(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = {
        "cycle_id": "cycle:crash_diagnostics_bundle",
        "diagnostics_id": "crash-diagnostics:bundle_gate",
        "student_id": "student:diagnostics_gate",
        "target_node_ref": "node:expert_coder",
        "redact_secrets": True,
        "include_raw_private_data": False,
        "workspace_paths_redacted": True,
        "include_app_logs": True,
        "include_runtime_health": True,
        "include_support_bundle": True,
        "include_deep_replay": True,
        "include_artifact_trust": True,
        "source_refs": {
            "app_log": str(tmp_path / "runtime" / "private" / "app.log"),
            "operator_note": "private text must not persist",
        },
    }

    blocked = spine.build_crash_diagnostics_manifest(request)

    assert blocked["logs_packaged"] is False
    assert blocked["log_packaging_allowed"] is False
    assert "secret_scan_passed" in blocked["log_packaging_blockers"]
    assert "diagnostics_destination" in blocked["log_packaging_blockers"]
    assert "crash_diagnostics_ready" in blocked["log_packaging_blockers"]
    assert "support_bundle" in blocked["log_packaging_blockers"]

    allowed = spine.build_crash_diagnostics_manifest(
        {
            **request,
            "secret_scan_passed": True,
            "diagnostics_destination": "operator-approved-local-diagnostics-handoff",
            "crash_diagnostics_ready": True,
            "support_bundle_ready": True,
        }
    )

    assert allowed["logs_packaged"] is True
    assert allowed["log_packaging_allowed"] is True
    assert allowed["log_packaging_blockers"] == []
    assert allowed["artifacts"]["diagnostics_bundle_path"].endswith("crash_diagnostics.json")
    assert "private text must not persist" not in json.dumps(allowed)

    diagnostics_text = open(allowed["artifacts"]["diagnostics_bundle_path"], encoding="utf-8").read()
    assert "private text must not persist" not in diagnostics_text
    assert str(tmp_path) not in diagnostics_text
    diagnostics_payload = json.loads(diagnostics_text)
    assert diagnostics_payload["schema_version"] == "crash_diagnostics_bundle.v0.1"
    assert diagnostics_payload["source_count"] == 2


def test_release_packaging_creates_sanitized_zip_only_after_release_gates(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = {
        "cycle_id": "cycle:release_package_zip",
        "release_id": "release-package:zip_gate",
        "student_id": "student:release_gate",
        "target_node_ref": "node:expert_coder",
        "include_installer": True,
        "include_support_bundle": True,
        "include_crash_diagnostics": True,
        "include_first_run_readiness": True,
        "redact_secrets": True,
        "include_raw_private_data": False,
        "workspace_paths_redacted": True,
        "source_refs": {
            "support_bundle": str(tmp_path / "runtime" / "private" / "support_bundle.zip"),
            "operator_note": "private text must not persist",
        },
    }

    blocked = spine.build_release_package_manifest(request)

    assert blocked["package_created"] is False
    assert blocked["package_creation_allowed"] is False
    assert "release_destination" in blocked["package_creation_blockers"]
    assert "ci_packaging_ready" in blocked["package_creation_blockers"]
    assert "support_bundle" in blocked["package_creation_blockers"]
    assert "crash_diagnostics" in blocked["package_creation_blockers"]
    assert "first_run_readiness" in blocked["package_creation_blockers"]
    assert "artifact_signing_ready" in blocked["package_creation_blockers"]
    assert "artifact_trust_clear" in blocked["package_creation_blockers"]
    assert "adapter_artifact_trust_clear" in blocked["package_creation_blockers"]

    allowed = spine.build_release_package_manifest(
        {
            **request,
            "release_destination": "operator-approved-local-release-handoff",
            "ci_packaging_ready": True,
            "buyer_launcher_ready": True,
            "buyer_safe_defaults": True,
            "support_bundle_ready": True,
            "crash_diagnostics_ready": True,
            "first_run_readiness_ready": True,
            "artifact_signing_ready": True,
            "artifact_trust_clear": True,
            "adapter_artifact_trust_clear": True,
        }
    )

    assert allowed["package_created"] is True
    assert allowed["package_creation_allowed"] is True
    assert allowed["buyer_release_allowed"] is True
    assert allowed["package_creation_blockers"] == []
    assert allowed["artifacts"]["release_package_path"].endswith("release_package.zip")
    assert "private text must not persist" not in json.dumps(allowed)

    with zipfile.ZipFile(allowed["artifacts"]["release_package_path"]) as package:
        names = set(package.namelist())
        manifest_text = package.read("release_package_manifest.json").decode("utf-8")

    assert "release_package_manifest.json" in names
    assert "release_package_events.jsonl" in names
    assert "private text must not persist" not in manifest_text
    assert str(tmp_path) not in manifest_text


def test_first_run_readiness_writes_sanitized_bundle_only_when_ready(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = {
        "cycle_id": "cycle:first_run_bundle",
        "readiness_id": "first-run:bundle_gate",
        "student_id": "student:first_run_gate",
        "target_node_ref": "node:expert_coder",
        "redact_secrets": True,
        "include_raw_private_data": False,
        "workspace_paths_redacted": True,
        "source_refs": {
            "model_cache_root": str(tmp_path / "runtime" / "private" / "model-cache"),
            "operator_note": "private text must not persist",
        },
    }

    blocked = spine.build_first_run_readiness_manifest(request)

    assert blocked["decision"] == "blocked"
    assert blocked["readiness_bundle_created"] is False
    assert blocked["readiness_bundle_allowed"] is False
    assert "local_cache_controls_ready" in blocked["readiness_blockers"]
    assert "project_local_signing_key_ready" in blocked["readiness_blockers"]
    assert "adapter_artifact_trust_clear" in blocked["readiness_blockers"]

    allowed = spine.build_first_run_readiness_manifest(
        {
            **request,
            "local_cache_controls_ready": True,
            "model_download_manager_ready": True,
            "buyer_launcher_ready": True,
            "support_bundle_ready": True,
            "crash_diagnostics_ready": True,
            "project_local_signing_key_ready": True,
            "buyer_safe_defaults": True,
            "adapter_artifact_trust_clear": True,
            "operator_approved": True,
        }
    )

    assert allowed["decision"] == "ready"
    assert allowed["readiness_bundle_created"] is True
    assert allowed["readiness_bundle_allowed"] is True
    assert allowed["installer_mutation_allowed"] is False
    assert allowed["cache_mutation_allowed"] is False
    assert allowed["artifacts"]["readiness_bundle_path"].endswith("first_run_readiness.json")
    assert "private text must not persist" not in json.dumps(allowed)

    readiness_text = open(allowed["artifacts"]["readiness_bundle_path"], encoding="utf-8").read()
    assert "private text must not persist" not in readiness_text
    assert str(tmp_path) not in readiness_text
    readiness_payload = json.loads(readiness_text)
    assert readiness_payload["schema_version"] == "first_run_readiness_bundle.v0.1"
    assert readiness_payload["decision"] == "ready"


def test_release_go_no_go_writes_final_review_artifact_only_after_approval_gates(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = {
        "cycle_id": "cycle:release_go_no_go_artifact",
        "review_id": "release-go-no-go:artifact_gate",
        "release_id": "release-package:artifact_gate",
        "student_id": "student:go_no_go_gate",
        "target_node_ref": "node:expert_coder",
        "release_destination": "operator-approved-local-release-handoff",
        "workspace_paths_redacted": True,
        "source_refs": {
            "release_package": str(tmp_path / "runtime" / "private" / "release_package.zip"),
            "operator_note": "private text must not persist",
        },
    }

    blocked = spine.build_release_go_no_go_manifest(request)

    assert blocked["decision"] == "blocked"
    assert blocked["review_artifact_created"] is False
    assert blocked["review_artifact_allowed"] is False
    assert "release_packaging_ready" in blocked["review_artifact_blockers"]
    assert "trusted_adapter_artifact_required" in blocked["review_artifact_blockers"]
    assert "human_approved" in blocked["review_artifact_blockers"]

    approved = spine.build_release_go_no_go_manifest(
        {
            **request,
            "release_packaging_ready": True,
            "first_run_readiness_ready": True,
            "crash_diagnostics_ready": True,
            "support_bundle_ready": True,
            "artifact_trust_clear": True,
            "adapter_artifact_trust_clear": True,
            "signed_replay_trust_clear": True,
            "reviewer_windows_ready": True,
            "operator_approved": True,
            "human_approved": True,
            "buyer_release_allowed": True,
        }
    )

    assert approved["decision"] == "approved"
    assert approved["review_artifact_created"] is True
    assert approved["review_artifact_allowed"] is True
    assert approved["review_artifact_blockers"] == []
    assert approved["release_mutation_allowed"] is False
    assert approved["artifacts"]["review_artifact_path"].endswith("release_go_no_go_review.json")
    assert "private text must not persist" not in json.dumps(approved)

    review_text = open(approved["artifacts"]["review_artifact_path"], encoding="utf-8").read()
    assert "private text must not persist" not in review_text
    assert str(tmp_path) not in review_text
    review_payload = json.loads(review_text)
    assert review_payload["schema_version"] == "release_go_no_go_final_review.v0.1"
    assert review_payload["decision"] == "approved"


def test_runtime_health_monitor_writes_report_only_when_health_window_passes(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = {
        "cycle_id": "cycle:runtime_health_report",
        "monitor_id": "runtime-health:report_gate",
        "student_id": "student:runtime_health_gate",
        "target_node_ref": "node:expert_coder",
        "current_runtime_state": "shadow",
        "signed_replay_trust_clear": False,
        "rollback_restorable": False,
        "health_window_started": False,
        "max_error_rate": 0.02,
        "max_p95_latency_ms": 2000,
        "max_route_share": 0.10,
        "error_rate_observed": 0.04,
        "p95_latency_ms_observed": 2300,
        "route_share_observed": 0.15,
        "workspace_paths_redacted": True,
        "source_refs": {
            "runtime_log": str(tmp_path / "runtime" / "private" / "runtime.log"),
            "operator_note": "private text must not persist",
        },
    }

    blocked = spine.build_runtime_health_monitor_manifest(request)

    assert blocked["decision"] == "blocked"
    assert blocked["health_report_created"] is False
    assert blocked["health_report_allowed"] is False
    assert "trusted_signed_replay_required" in blocked["health_report_blockers"]
    assert "error_rate_exceeded" in blocked["health_report_blockers"]
    assert "p95_latency_exceeded" in blocked["health_report_blockers"]
    assert "route_share_exceeded" in blocked["health_report_blockers"]

    ready = spine.build_runtime_health_monitor_manifest(
        {
            **request,
            "current_runtime_state": "canary",
            "signed_replay_trust_clear": True,
            "rollback_restorable": True,
            "health_window_started": True,
            "error_rate_observed": 0.01,
            "p95_latency_ms_observed": 1200,
            "route_share_observed": 0.05,
        }
    )

    assert ready["decision"] == "ready"
    assert ready["health_report_created"] is True
    assert ready["health_report_allowed"] is True
    assert ready["runtime_activation_allowed"] is False
    assert ready["health_report_blockers"] == []
    assert ready["artifacts"]["health_report_path"].endswith("runtime_health_report.json")
    assert "private text must not persist" not in json.dumps(ready)

    report_text = open(ready["artifacts"]["health_report_path"], encoding="utf-8").read()
    assert "private text must not persist" not in report_text
    assert str(tmp_path) not in report_text
    report_payload = json.loads(report_text)
    assert report_payload["schema_version"] == "runtime_health_report.v0.1"
    assert report_payload["decision"] == "ready"


def test_teacher_ejection_review_writes_final_artifact_only_after_retirement_gates(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = {
        "cycle_id": "cycle:teacher_ejection_review",
        "review_id": "teacher-ejection:artifact_gate",
        "eval_id": "eval:teacher_ejection_gate",
        "student_id": "student:teacher_ejection_gate",
        "parent_node_ref": "node:expert_coder",
        "teacher_ejection_allowed": False,
        "parent_retirement_allowed": False,
        "post_promotion_window_passed": False,
        "ivy_grade_review_passed": False,
        "greatly_outperforms_parent": False,
        "rollback_restorable": False,
        "child_retained_after_parent_retirement": True,
        "rollback_retention_required": True,
        "workspace_paths_redacted": True,
        "source_refs": {
            "review_notes": "private text must not persist",
            "eval_path": str(tmp_path / "runtime" / "private" / "eval_scorecard.json"),
        },
    }

    blocked = spine.build_teacher_ejection_review_manifest(request)

    assert blocked["decision"] == "blocked"
    assert blocked["final_review_artifact_created"] is False
    assert blocked["final_review_artifact_allowed"] is False
    assert "teacher_ejection_allowed" in blocked["final_review_artifact_blockers"]
    assert "parent_retirement_allowed" in blocked["final_review_artifact_blockers"]

    trust_blocked = spine.build_teacher_ejection_review_manifest(
        {
            **request,
            "teacher_ejection_allowed": True,
            "parent_retirement_allowed": True,
            "post_promotion_window_passed": True,
            "ivy_grade_review_passed": True,
            "greatly_outperforms_parent": True,
            "rollback_restorable": True,
        }
    )

    assert trust_blocked["decision"] == "blocked"
    assert trust_blocked["final_review_artifact_created"] is False
    assert trust_blocked["final_review_artifact_allowed"] is False
    assert trust_blocked["adapter_artifact_trust_status"] == "not_recorded"
    assert trust_blocked["adapter_artifact_trust_clear"] is False
    assert "adapter_artifact_trust_clear" in trust_blocked["final_review_artifact_blockers"]

    approved = spine.build_teacher_ejection_review_manifest(
        {
            **request,
            "teacher_ejection_allowed": True,
            "parent_retirement_allowed": True,
            "post_promotion_window_passed": True,
            "ivy_grade_review_passed": True,
            "greatly_outperforms_parent": True,
            "rollback_restorable": True,
            "adapter_artifact_trust_status": "trusted",
            "adapter_artifact_trust_clear": True,
        }
    )

    assert approved["decision"] == "approved"
    assert approved["final_review_artifact_created"] is True
    assert approved["final_review_artifact_allowed"] is True
    assert approved["adapter_artifact_trust_status"] == "trusted"
    assert approved["adapter_artifact_trust_clear"] is True
    assert approved["teacher_ejection_mutation_allowed"] is False
    assert approved["parent_retirement_mutation_allowed"] is False
    assert approved["final_review_artifact_blockers"] == []
    assert approved["artifacts"]["final_review_artifact_path"].endswith("teacher_ejection_final_review.json")
    assert "private text must not persist" not in json.dumps(approved)

    final_review_text = open(approved["artifacts"]["final_review_artifact_path"], encoding="utf-8").read()
    assert "private text must not persist" not in final_review_text
    assert str(tmp_path) not in final_review_text
    final_review = json.loads(final_review_text)
    assert final_review["schema_version"] == "teacher_ejection_final_review.v0.1"
    assert final_review["decision"] == "approved"


def test_child_execution_can_consume_sandbox_adapter_bundle(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    lifecycle = spine.run_growth_lifecycle(lifecycle_request())

    execution = spine.execute_child_node(
        {
            "cycle_id": lifecycle["cycle_id"],
            "execution_id": "exec:adapter_bundle_only",
            "student_id": lifecycle["student_id"],
            "input": {"x": 4.0},
            "adapter_bundle_path": lifecycle["artifact_bridge"]["adapter_bundle_path"],
        }
    )

    assert execution["status"] == "shadow_executed"
    assert execution["weights_source"] == "sandbox_adapter_bundle_checkpoint"
    assert execution["production_output_allowed"] is False
    assert execution["child_execution_replay_evidence"]["callable_runtime_verified"] is True
    assert execution["child_execution_replay_evidence"]["weights_source"] == "sandbox_adapter_bundle_checkpoint"


def test_sealed_eval_can_consume_sandbox_adapter_bundle(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    lifecycle = spine.run_growth_lifecycle(lifecycle_request())

    eval_review = spine.run_sealed_eval_review(
        {
            "eval_id": "eval:adapter_bundle_only",
            "cycle_id": lifecycle["cycle_id"],
            "student_id": lifecycle["student_id"],
            "parent_node_ref": lifecycle["target_node_ref"],
            "adapter_bundle_path": lifecycle["artifact_bridge"]["adapter_bundle_path"],
            "hidden_eval_cases": lifecycle_request()["hidden_eval_cases"],
            "teacher_license_gate_passed": True,
            "human_approved": True,
        }
    )

    assert eval_review["status"] == "sealed_eval_complete"
    assert eval_review["weights_source"] == "sandbox_adapter_bundle_checkpoint"
    assert eval_review["student_beats_parent"] is True
    assert eval_review["student_beats_teacher_council"] is True
    assert "weights_missing_or_untrusted" not in json.dumps(eval_review)
    assert eval_review["promotion_allowed"] is True
    assert eval_review["teacher_ejection_allowed"] is False


def test_finish_map_marks_sealed_eval_ready_with_reviewer_window_advancement(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = lifecycle_request()
    request["human_approved"] = True

    lifecycle = spine.run_growth_lifecycle(request)
    reviewer_window = spine.record_reviewer_window_advancement(
        {
            "cycle_id": lifecycle["cycle_id"],
            "advancement_id": "reviewer-window:ready_finish_map",
            "eval_id": lifecycle["sealed_eval"]["eval_id"],
            "student_id": lifecycle["student_id"],
            "window": "post_promotion",
            "window_status": "passed",
            "passed_windows": ["initial_eval", "shadow_runtime", "canary"],
            "parent_surpass_rate": 1.0,
            "teacher_surpass_rate": 1.0,
            "lower_confidence_surpass_bound": lifecycle["sealed_eval"]["lower_confidence_surpass_bound"],
            "teacher_ejection_review_requested": True,
            "parent_retirement_review_requested": True,
            "human_approved": True,
            "governance_approved": True,
        }
    )
    assert reviewer_window["ejection_readiness_evidence"]["status"] == "ready"

    finish_map = spine.scorecard()["finish_readiness_map"]
    gates_by_id = {gate["gate_id"]: gate for gate in finish_map["gates"]}
    assert gates_by_id["sealed_eval_gauntlet"]["status"] == "ready"
    assert gates_by_id["sealed_eval_gauntlet"]["blockers"] == []
    assert "record_reviewer_window" not in finish_map["next_operator_actions"]


def test_growth_lifecycle_orchestrator_blocks_invalid_signing_seed_with_configuration_error(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    request = lifecycle_request()
    request["signing_seed_hex"] = "not-a-valid-ed25519-seed"

    lifecycle = spine.run_growth_lifecycle(request)

    assert lifecycle["deep_replay"]["signature_policy"]["current_signature_state"] == "unsigned_v0"
    assert lifecycle["deep_replay"]["signature_policy"]["signing_configuration_state"] == "configured_invalid"
    assert lifecycle["deep_replay"]["signature_policy"]["real_signing_blocker"] == "ed25519_signing_seed_invalid"
    assert lifecycle["signer_readiness"]["status"] == "blocked"
    assert lifecycle["signer_readiness"]["signing_configuration_state"] == "configured_invalid"
    assert lifecycle["signer_readiness"]["real_signing_blocker"] == "ed25519_signing_seed_invalid"
    assert lifecycle["closed_loop_summary"]["signer_ready"] is False
    assert "real_signing_required" in lifecycle["blocked_reasons"]


def test_lifecycle_replay_consistency_reports_tamper_integrity_blockers(tmp_path):
    spine = NexusNetProductionSpine(artifacts_dir=tmp_path)
    lifecycle = spine.run_growth_lifecycle(lifecycle_request())
    artifact_bridge = lifecycle["artifact_bridge"]
    deep_replay = lifecycle["deep_replay"]

    checkpoint_path = artifact_bridge["training_checkpoint_path"]
    with open(checkpoint_path, "a", encoding="utf-8") as handle:
        handle.write("\n{\"tamper\": true}\n")

    artifact_index_path = deep_replay["artifacts"]["artifact_index_path"]
    records = [json.loads(line) for line in open(artifact_index_path, encoding="utf-8") if line.strip()]
    for record in records:
        if record["artifact_path"] == artifact_bridge["adapter_manifest_path"]:
            record["signature_state"] = "invalid_signature_state"
    with open(artifact_index_path, "w", encoding="utf-8") as handle:
        handle.write("".join(json.dumps(record, sort_keys=True) + "\n" for record in records))

    consistency = _validate_lifecycle_replay_consistency(artifact_bridge, deep_replay)

    assert consistency["passed"] is False
    assert consistency["integrity_state"] == "failed"
    assert "bridge_hash_mismatches" in consistency["integrity_blockers"]
    assert "bridge_signature_state_mismatches" in consistency["integrity_blockers"]
    assert consistency["bridge_hash_mismatches"] == ["training_checkpoint_path"]
    assert consistency["bridge_signature_state_mismatches"] == ["adapter_manifest_path"]
