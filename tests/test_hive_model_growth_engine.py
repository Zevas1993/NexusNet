from __future__ import annotations

import json

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.growth import GrowthCycleRequest, HiveModelGrowthEngine
from tests.test_nexus_phase1_foundation import make_project


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_growth_engine_dry_run_writes_replayable_cycle_contracts(tmp_path):
    engine = HiveModelGrowthEngine(artifacts_dir=tmp_path)

    result = engine.start_dry_run(
        GrowthCycleRequest(
            cycle_id="cycle:cyc_demo_001",
            target_node_id="node:expert_coder",
            target_node_type="Expert",
            target_capabilities=["multi_file_patch", "test_repair", "terminal_recovery"],
            student_kind="child_expert",
            birth_reason="Repeated failures on multi-file repair tasks.",
            teacher_pairing_refs=[
                "teacher:qwen3-coder-next",
                "teacher:devstral-2",
                "node:expert_critique",
            ],
            source_refs=["source:licensed_synthetic_code_cases"],
        )
    )

    assert result["surface_id"] == "hive-model-growth-engine"
    assert result["cycle_id"] == "cycle:cyc_demo_001"
    assert result["state"] == "shadow_specialist"
    assert result["actual_weight_mutation_allowed"] is False
    assert result["teacher_ejection_eligible"] is False
    assert result["artifact_refs"]["dataset_manifest"] == "dataset:ds_demo_001"

    cycle_dir = tmp_path / "growth" / "cycles" / "cyc_demo_001"
    assert (cycle_dir / "cycle.json").is_file()
    assert (cycle_dir / "events.jsonl").is_file()
    assert (cycle_dir / "datasets" / "dataset_manifest.json").is_file()
    assert (cycle_dir / "datasets" / "teacher_free_hidden.manifest.json").is_file()
    assert (cycle_dir / "students" / "model_genome.yaml").is_file()
    assert (cycle_dir / "training-runs" / "train_demo_001" / "training_run.json").is_file()
    assert (cycle_dir / "evals" / "eval_demo_001" / "scorecard.json").is_file()
    assert (cycle_dir / "reviewer-monitor" / "decision.json").is_file()
    assert (cycle_dir / "rollbacks" / "rewind_proof.json").is_file()

    cycle = _read_json(cycle_dir / "cycle.json")
    assert cycle["schema_version"] == "growth_cycle.v0.1"
    assert cycle["header"]["artifact_type"] == "growth_cycle"
    assert cycle["header"]["hash"].startswith("sha256:")
    assert cycle["state_refs"]["dataset_manifest_ref"] == "dataset:ds_demo_001"
    assert cycle["governance"]["human_approval_required"] is True

    material_scout = _read_json(cycle_dir / "material-scout" / "scout_manifest.json")
    assert material_scout["dataset_radar"]["surface_id"] == "living-dataset-radar"
    assert material_scout["dataset_radar"]["teacher_access_rule"] == "teacher councils request material through Dataset Radar only"
    assert material_scout["dataset_radar"]["lineage_split_policy"]["train_source_ids"] == [
        "the-stack-v2",
        "stack-edu",
        "codesearchnet",
    ]
    assert material_scout["dataset_radar"]["lineage_split_policy"]["sealed_eval_source_ids"] == [
        "swe-bench",
        "swe-gym",
    ]
    source_candidates = _read_jsonl(cycle_dir / "material-scout" / "source_candidates.jsonl")
    assert {"the-stack-v2", "stack-edu", "codesearchnet", "context7", "swe-bench", "swe-gym"}.issubset(
        {candidate["dataset_radar_source_id"] for candidate in source_candidates}
    )
    assert any(candidate["usable_for_training"] is False and candidate["split_gate"] == "teacher_free_hidden" for candidate in source_candidates)

    council = _read_json(cycle_dir / "teacher-council" / "council_manifest.json")
    assert council["material_access_rule"] == "dataset-radar-only"
    assert council["dataset_radar_ref"] == "material-scout/dataset_radar_lineage.json"

    hidden = _read_json(cycle_dir / "datasets" / "teacher_free_hidden.manifest.json")
    assert hidden["header"]["artifact_type"] == "hidden_eval_manifest"
    assert hidden["header"]["hash"].startswith("sha256:")
    assert hidden["sealed"] is True
    assert hidden["visible_to_training"] is False
    assert hidden["visible_to_teacher_council"] is False
    assert hidden["source_ids"] == ["swe-bench", "swe-gym"]
    assert hidden["blocked_from_training_splits"] is True
    assert hidden["split_policy_ref"] == "dataset_manifest.dataset_radar_lineage.split_policy"
    assert hidden["leakage_scan"]["status"] == "passed"

    dataset = _read_json(cycle_dir / "datasets" / "dataset_manifest.json")
    assert dataset["splits"]["train"]["case_count"] == 6
    assert dataset["splits"]["teacher_free_hidden"]["visible_to_training"] is False
    assert dataset["splits"]["teacher_free_hidden"]["visible_to_teacher_council"] is False
    assert dataset["splits"]["teacher_free_hidden"]["source_ids"] == ["swe-bench", "swe-gym"]
    assert dataset["splits"]["teacher_free_hidden"]["blocked_from_train"] is True
    assert dataset["splits"]["teacher_free_hidden"]["split_policy_ref"] == "dataset_radar_lineage.split_policy"
    assert dataset["privacy_summary"]["private_raw_cases"] == 0
    assert dataset["dataset_radar_lineage"]["source_ids"] == ["the-stack-v2", "stack-edu", "codesearchnet", "context7", "swe-bench", "swe-gym"]
    assert dataset["dataset_radar_lineage"]["split_policy"]["teacher_context_only_source_ids"] == ["context7"]
    assert dataset["dataset_radar_lineage"]["split_policy"]["sealed_eval_source_ids"] == ["swe-bench", "swe-gym"]

    birth = _read_json(cycle_dir / "students" / "student_birth_record.json")
    assert birth["dataset_radar_lineage"]["split_policy"]["train_source_ids"] == [
        "the-stack-v2",
        "stack-edu",
        "codesearchnet",
    ]

    genome = (cycle_dir / "students" / "model_genome.yaml").read_text(encoding="utf-8")
    assert "dataset_radar_split_policy" in genome
    assert "swe-bench" in genome

    training = _read_json(cycle_dir / "training-runs" / "train_demo_001" / "training_run.json")
    assert training["support_state"] == "dry_run_supported"
    assert training["actual_weight_mutation_allowed"] is False
    assert "qlora" in training["declared_methods"]
    training_plan = (cycle_dir / "training-runs" / "train_demo_001" / "training_plan.yaml").read_text(encoding="utf-8")
    assert "dataset_radar_source_review_passed" in training_plan
    assert "hidden_eval_attestation_passed" in training_plan
    assert "human_approval_recorded" in training_plan
    prerequisites = training["dataset_radar_training_prerequisites"]
    assert prerequisites["source_review_required"] is True
    assert prerequisites["hidden_eval_attestation_required"] is True
    assert prerequisites["human_approval_required"] is True
    assert prerequisites["sealed_eval_source_ids"] == ["swe-bench", "swe-gym"]
    assert prerequisites["actual_weight_mutation_blocked_until"] == [
        "dataset_radar_source_review_passed",
        "hidden_eval_attestation_passed",
        "sandbox_gpu_profile_ready",
        "human_approval_recorded",
    ]

    hidden_attestation = _read_json(cycle_dir / "evals" / "eval_demo_001" / "hidden_eval_attestation.json")
    assert hidden_attestation["source_ids"] == ["swe-bench", "swe-gym"]
    assert hidden_attestation["split_policy_ref"] == "datasets/dataset_manifest.json#dataset_radar_lineage.split_policy"
    assert hidden_attestation["teacher_visible"] is False

    reviewer = _read_json(cycle_dir / "reviewer-monitor" / "decision.json")
    assert reviewer["decision"] == "shadow_specialist"
    assert reviewer["parent_comparison"]["passed"] is True
    assert reviewer["teacher_comparison"]["passed"] is False
    assert reviewer["hard_gates"]["dataset_radar_source_review_passed"] is False
    assert reviewer["hard_gates"]["hidden_eval_attestation_passed"] is True
    assert reviewer["hard_gates"]["sealed_eval_not_teacher_visible"] is True
    assert reviewer["hard_gates"]["actual_weight_mutation_allowed"] is False
    assert reviewer["teacher_ejection_eligible"] is False

    rewind = _read_json(cycle_dir / "rollbacks" / "rewind_proof.json")
    assert rewind["header"]["artifact_type"] == "rewind_proof"
    assert rewind["header"]["hash"].startswith("sha256:")


def test_growth_engine_carries_dataset_radar_material_request_into_birth_lineage(tmp_path):
    engine = HiveModelGrowthEngine(artifacts_dir=tmp_path)
    material_request = engine.dataset_radar.material_request(
        {
            "session_id": "growth-material-request",
            "operator_actor": "Teacher Council",
            "teacher_ref": "teacher:qwen3-coder-next",
            "target_node": "Coder Expert",
            "requested_split": "train",
            "allowed_use": "train",
        }
    )

    result = engine.start_dry_run(
        {
            "cycle_id": "cycle:cyc_material_001",
            "target_node_id": "node:expert_coder",
            "target_node_type": "Expert",
            "target_capabilities": ["multi_file_patch", "test_repair"],
            "student_kind": "child_expert",
            "birth_reason": "Birth Coder child from Dataset Radar approved teacher material request.",
            "teacher_pairing_refs": ["teacher:qwen3-coder-next", "teacher:devstral-2", "node:expert_critique"],
            "material_request_ref": material_request["material_request_id"],
        }
    )

    assert result["artifact_refs"]["material_request"] == material_request["material_request_id"]
    cycle_dir = tmp_path / "growth" / "cycles" / "cyc_material_001"
    material_replay = _read_json(cycle_dir / "material-scout" / "material_request.json")
    assert material_replay["material_request_id"] == material_request["material_request_id"]
    assert "the-stack-v2" in material_replay["approved_source_ids"]

    scout = _read_json(cycle_dir / "material-scout" / "scout_manifest.json")
    assert scout["dataset_radar"]["material_request_ref"] == material_request["material_request_id"]
    assert scout["dataset_radar"]["approved_source_ids"] == material_request["approved_source_ids"]

    dataset = _read_json(cycle_dir / "datasets" / "dataset_manifest.json")
    assert dataset["dataset_radar_lineage"]["material_request_ref"] == material_request["material_request_id"]
    assert dataset["dataset_radar_lineage"]["source_ids"] == material_request["approved_source_ids"]

    birth = _read_json(cycle_dir / "students" / "student_birth_record.json")
    assert birth["material_request_ref"] == material_request["material_request_id"]
    assert birth["dataset_radar_lineage"]["approved_source_ids"] == material_request["approved_source_ids"]

    genome = (cycle_dir / "students" / "model_genome.yaml").read_text(encoding="utf-8")
    assert material_request["material_request_id"] in genome
    assert "dataset_radar_material_request_ref" in genome


def test_growth_engine_carries_knowledge_artifact_refs_into_growth_lineage(tmp_path):
    engine = HiveModelGrowthEngine(artifacts_dir=tmp_path)

    result = engine.start_dry_run(
        {
            "cycle_id": "cycle:cyc_kac_001",
            "target_node_id": "node:expert_coder",
            "target_node_type": "Expert",
            "target_capabilities": ["multi_file_patch", "test_repair"],
            "student_kind": "child_expert",
            "birth_reason": "Use compiled NexusNet context to seed teacher council curriculum.",
            "teacher_pairing_refs": ["teacher:qwen3-coder-next", "teacher:devstral-2", "node:expert_critique"],
            "knowledge_artifact_refs": ["kac://architecture_review/abc123", "kac://dataset_radar/def456"],
        }
    )

    assert result["artifact_refs"]["knowledge_artifacts"] == [
        "kac://architecture_review/abc123",
        "kac://dataset_radar/def456",
    ]

    cycle_dir = tmp_path / "growth" / "cycles" / "cyc_kac_001"
    cycle = _read_json(cycle_dir / "cycle.json")
    assert cycle["refs"]["knowledge_artifact_refs"] == [
        "kac://architecture_review/abc123",
        "kac://dataset_radar/def456",
    ]
    assert cycle["state_refs"]["knowledge_artifact_refs"] == [
        "kac://architecture_review/abc123",
        "kac://dataset_radar/def456",
    ]

    scout = _read_json(cycle_dir / "material-scout" / "scout_manifest.json")
    assert scout["compiled_knowledge"]["artifact_refs"] == [
        "kac://architecture_review/abc123",
        "kac://dataset_radar/def456",
    ]
    assert scout["compiled_knowledge"]["access_rule"] == "artifact-refs-only-through-KRC"
    assert scout["compiled_knowledge"]["requires_krc_runtime_context_allowed"] is True
    assert scout["compiled_knowledge"]["blocks_stale_or_quarantined_context"] is True

    curriculum = (cycle_dir / "curriculum" / "curriculum.yaml").read_text(encoding="utf-8")
    assert "knowledge_artifact_refs" in curriculum
    assert "kac://architecture_review/abc123" in curriculum

    council = _read_json(cycle_dir / "teacher-council" / "council_manifest.json")
    assert council["compiled_knowledge_access"]["artifact_refs"] == [
        "kac://architecture_review/abc123",
        "kac://dataset_radar/def456",
    ]
    assert council["compiled_knowledge_access"]["mutation_allowed"] is False
    assert council["compiled_knowledge_access"]["requires_krc_runtime_context_allowed"] is True

    accepted_cases = _read_jsonl(cycle_dir / "teacher-council" / "accepted_cases.jsonl")
    assert accepted_cases[0]["knowledge_artifact_refs"] == [
        "kac://architecture_review/abc123",
        "kac://dataset_radar/def456",
    ]

    dataset = _read_json(cycle_dir / "datasets" / "dataset_manifest.json")
    assert dataset["knowledge_artifact_lineage"]["artifact_refs"] == [
        "kac://architecture_review/abc123",
        "kac://dataset_radar/def456",
    ]
    assert dataset["knowledge_artifact_lineage"]["visibility"] == "teacher-council-and-training-context"
    assert dataset["knowledge_artifact_lineage"]["requires_krc_runtime_context_allowed"] is True

    birth = _read_json(cycle_dir / "students" / "student_birth_record.json")
    assert birth["knowledge_artifact_lineage"]["artifact_refs"] == [
        "kac://architecture_review/abc123",
        "kac://dataset_radar/def456",
    ]
    assert birth["knowledge_artifact_lineage"]["blocks_stale_or_quarantined_context"] is True

    genome = (cycle_dir / "students" / "model_genome.yaml").read_text(encoding="utf-8")
    assert "knowledge_artifact_refs" in genome
    assert "kac://dataset_radar/def456" in genome


def test_growth_engine_blocks_kac_refs_when_runtime_context_evidence_is_disallowed(tmp_path):
    engine = HiveModelGrowthEngine(artifacts_dir=tmp_path)

    result = engine.start_dry_run(
        {
            "cycle_id": "cycle:cyc_kac_blocked_001",
            "target_node_id": "node:expert_coder",
            "target_node_type": "Expert",
            "target_capabilities": ["multi_file_patch", "test_repair"],
            "student_kind": "child_expert",
            "birth_reason": "Blocked compiled context cannot seed a growth cycle.",
            "teacher_pairing_refs": ["teacher:qwen3-coder-next", "node:expert_critique"],
            "knowledge_artifact_refs": ["kac://architecture_review/blocked"],
            "knowledge_artifact_runtime_contexts": [
                {
                    "artifact_id": "kac://architecture_review/blocked",
                    "runtime_context_allowed": False,
                    "fallback_state": "compiled_artifact_stale",
                }
            ],
        }
    )

    assert result["status"] == "blocked"
    blocker_rule_ids = {blocker["rule_id"] for blocker in result["growth_gate"]["blockers"]}
    assert "growth_engine_kac_runtime_context_blocked" in blocker_rule_ids

    cycle_dir = tmp_path / "growth" / "cycles" / "cyc_kac_blocked_001"
    scout = _read_json(cycle_dir / "material-scout" / "scout_manifest.json")
    assert scout["compiled_knowledge"]["allowed"] is False
    assert scout["compiled_knowledge"]["blocked_artifact_refs"] == ["kac://architecture_review/blocked"]
    assert "compiled_artifact_stale" in scout["compiled_knowledge"]["blocked_reasons"]


def test_growth_engine_blocks_cycles_from_review_blocked_adapter_training_plan(tmp_path):
    engine = HiveModelGrowthEngine(artifacts_dir=tmp_path)

    result = engine.start_dry_run(
        {
            "cycle_id": "cycle:cyc_blocked_adapter_001",
            "target_node_id": "node:expert_coder",
            "target_node_type": "Expert",
            "target_capabilities": ["multi_file_patch", "test_repair"],
            "student_kind": "child_expert",
            "birth_reason": "Attempted Coder child birth from a review-blocked adapter plan.",
            "teacher_pairing_refs": ["teacher:qwen3-coder-next", "teacher:devstral-2", "node:expert_critique"],
            "source_refs": ["source:dataset_radar_review_blocked"],
            "adapter_training_plan_ref": "training::review-blocked-code-adapter",
            "adapter_training_plan_status": "blocked",
            "adapter_training_gate": {
                "allowed": False,
                "blocked_source_ids": ["the-stack-v2"],
                "reason": "Dataset Radar source review has unresolved privacy evidence.",
            },
            "adapter_training_findings": [
                {
                    "rule_id": "adapter_training_dataset_radar_training_review_blocked",
                    "severity": "hard_fail",
                    "message": "Dataset Radar training-review blockers must be cleared before adapter planning.",
                }
            ],
        }
    )

    assert result["state"] == "blocked"
    assert result["adapter_training_plan_ref"] == "training::review-blocked-code-adapter"
    assert result["growth_gate"]["allowed"] is False

    cycle_dir = tmp_path / "growth" / "cycles" / "cyc_blocked_adapter_001"
    cycle = _read_json(cycle_dir / "cycle.json")
    assert cycle["status"] == "blocked"
    assert cycle["state_refs"]["adapter_training_plan_ref"] == "training::review-blocked-code-adapter"
    assert cycle["governance"]["promotion_allowed"] is False
    assert cycle["governance"]["actual_weight_mutation_allowed"] is False

    blocked_reasons = _read_jsonl(cycle_dir / "blocked_reasons.jsonl")
    assert {reason["rule_id"] for reason in blocked_reasons}.issuperset(
        {
            "growth_engine_adapter_training_plan_blocked",
            "growth_engine_adapter_training_gate_blocked",
            "growth_engine_adapter_training_hard_fail_findings",
        }
    )

    reviewer = _read_json(cycle_dir / "reviewer-monitor" / "decision.json")
    assert reviewer["decision"] == "blocked"
    assert reviewer["hard_gates"]["adapter_training_plan_ready"] is False

    scorecard = engine.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["blocked_count"] == 1
    assert scorecard["latest_cycle"]["status"] == "blocked"


def test_growth_engine_summary_and_scorecard_are_control_panel_ready(tmp_path):
    engine = HiveModelGrowthEngine(artifacts_dir=tmp_path)
    engine.start_dry_run(
        {
            "cycle_id": "cycle:cyc_demo_002",
            "target_node_id": "node:ao_evals",
            "target_node_type": "AO",
            "target_capabilities": ["eval_gauntlet", "rubric_regression"],
            "student_kind": "child_ao",
            "birth_reason": "Need a stricter reviewer monitor for student/teacher comparisons.",
            "teacher_pairing_refs": ["teacher:deepseek-v4-pro", "teacher:qwen3-30b-a3b"],
            "source_refs": ["source:licensed_eval_rubrics"],
        }
    )

    summary = engine.summary()
    assert summary["surface_id"] == "hive-model-growth-engine"
    assert summary["cycle_count"] == 1
    assert summary["shadow_specialist_count"] == 1
    assert summary["latest_cycle"]["cycle_id"] == "cycle:cyc_demo_002"

    scorecard = engine.scorecard()
    assert scorecard["runtime_state"] == "live-bound"
    assert scorecard["mutation_boundary"] == "dry-run-no-weight-update"
    assert scorecard["teacher_ejection_boundary"] == "blocked-until-reviewer-consistency-window-passes"
    assert "growth_cycle" in scorecard["required_artifacts"]
    assert scorecard["operator_actions"]["birth_shadow_student"]["endpoint"] == "/ops/brain/growth-engine/cycles"


def test_growth_engine_replay_keys_reflect_missing_artifacts(tmp_path):
    # A cycle directory with no artifact files must not advertise replayable artifacts.
    engine = HiveModelGrowthEngine(artifacts_dir=tmp_path)
    cycle_dir = engine.store.cycles_dir / "cyc_empty_001"
    cycle_dir.mkdir(parents=True, exist_ok=True)
    (cycle_dir / "cycle.json").write_text(
        json.dumps({"cycle_id": "cycle:cyc_empty_001", "status": "shadow_only", "created_at": "2026-05-30T00:00:00+00:00"}),
        encoding="utf-8",
    )

    summary = engine.summary()
    assert summary["cycle_count"] == 1
    # No artifacts on disk -> no replay keys, and every availability flag is False.
    assert summary["latest_cycle_artifact_replay_keys"] == []
    availability = summary["latest_cycle_artifact_replay_availability"]
    assert availability  # the 14 artifact slots are still enumerated
    assert all(present is False for present in availability.values())
    assert "model_genome" in availability and availability["model_genome"] is False


def test_growth_engine_api_visualizer_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/growth-engine/cycles",
        json={
            "cycle_id": "cycle:cyc_api_001",
            "target_node_id": "node:expert_coder",
            "target_node_type": "Expert",
            "target_capabilities": ["multi_file_patch", "test_repair"],
            "student_kind": "child_expert",
            "birth_reason": "API dry-run birth for a stricter Coder child.",
            "teacher_pairing_refs": ["teacher:qwen3-coder-next", "teacher:devstral-2", "node:expert_critique"],
            "source_refs": ["source:licensed_synthetic_code_cases"],
        },
    )
    assert response.status_code == 200
    assert response.json()["state"] == "shadow_specialist"

    summary = client.get("/ops/brain/growth-engine")
    assert summary.status_code == 200
    assert summary.json()["cycle_count"] == 1

    scorecard = client.get("/ops/brain/canon/growth-engine")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["mutation_boundary"] == "dry-run-no-weight-update"
    assert scorecard_payload["latest_reviewer_decision"]["hard_gates"]["dataset_radar_source_review_passed"] is False
    assert scorecard_payload["latest_reviewer_decision"]["hard_gates"]["hidden_eval_attestation_passed"] is True
    assert scorecard_payload["latest_training_run"]["dataset_radar_training_prerequisites"][
        "actual_weight_mutation_blocked_until"
    ] == [
        "dataset_radar_source_review_passed",
        "hidden_eval_attestation_passed",
        "sandbox_gpu_profile_ready",
        "human_approval_recorded",
    ]
    assert scorecard_payload["latest_hidden_eval_attestation"]["teacher_visible"] is False
    assert scorecard_payload["latest_hidden_eval_attestation"]["source_ids"] == ["swe-bench", "swe-gym"]
    assert scorecard_payload["latest_teacher_council_manifest"]["material_access_rule"] == "dataset-radar-only"
    assert (
        scorecard_payload["latest_teacher_council_manifest"]["dataset_radar_ref"]
        == "material-scout/dataset_radar_lineage.json"
    )
    assert scorecard_payload["latest_teacher_council_evidence"]["teacher_output_count"] == 12
    assert scorecard_payload["latest_teacher_council_evidence"]["accepted_case_count"] == 12
    assert scorecard_payload["latest_teacher_council_evidence"]["validator_result_count"] == 12
    assert scorecard_payload["latest_teacher_council_evidence"]["critique_count"] == 12
    assert scorecard_payload["latest_teacher_council_evidence"]["rejected_variant_count"] == 1
    assert scorecard_payload["latest_dataset_manifest"]["splits"]["train"]["case_count"] == 6
    assert scorecard_payload["latest_dataset_manifest"]["splits"]["validation"]["case_count"] == 2
    assert scorecard_payload["latest_dataset_manifest"]["splits"]["teacher_free_hidden"]["case_count"] == 1
    assert scorecard_payload["latest_dataset_manifest"]["splits"]["teacher_free_hidden"]["visible_to_training"] is False
    assert (
        scorecard_payload["latest_dataset_manifest"]["splits"]["teacher_free_hidden"]["visible_to_teacher_council"]
        is False
    )
    assert scorecard_payload["latest_dataset_manifest"]["dataset_radar_lineage"]["source_ids"] == [
        "the-stack-v2",
        "stack-edu",
        "codesearchnet",
        "context7",
        "swe-bench",
        "swe-gym",
    ]
    assert scorecard_payload["latest_dataset_manifest"]["dataset_radar_lineage"]["split_policy"][
        "teacher_context_only_source_ids"
    ] == ["context7"]
    assert scorecard_payload["latest_dataset_manifest"]["dataset_radar_lineage"]["split_policy"][
        "sealed_eval_source_ids"
    ] == ["swe-bench", "swe-gym"]
    assert scorecard_payload["latest_student_birth_record"]["student_kind"] == "child_expert"
    assert scorecard_payload["latest_student_birth_record"]["shadow_only"] is True
    assert scorecard_payload["latest_student_birth_record"]["parent_node_refs"] == ["node:expert_coder"]
    assert scorecard_payload["latest_model_genome"]["model_family"] == "nexusnet_hive_moe"
    assert scorecard_payload["latest_model_genome"]["architecture"]["adapter_type"] == "lora"
    assert scorecard_payload["latest_model_genome"]["moe_role"]["activation_policy"]["shadow_only"] is True
    assert scorecard_payload["latest_model_genome"]["moe_role"]["activation_policy"]["top_k"] == 2
    assert scorecard_payload["latest_training_loss_trace_summary"]["step_count"] == 3
    assert scorecard_payload["latest_training_loss_trace_summary"]["first_loss"] == 1.0
    assert scorecard_payload["latest_training_loss_trace_summary"]["last_loss"] == 0.84
    assert scorecard_payload["latest_training_loss_trace_summary"]["final_step"] == 2
    assert scorecard_payload["latest_training_loss_trace_summary"]["modes"] == ["dry_run"]
    assert scorecard_payload["latest_training_checkpoint_summary"]["checkpoint_count"] == 1
    assert scorecard_payload["latest_training_checkpoint_summary"]["restore_validated_count"] == 1
    assert scorecard_payload["latest_training_checkpoint_summary"]["weight_snapshot_states"] == [
        "not_created_in_dry_run"
    ]
    assert scorecard_payload["latest_training_output_artifacts"]["artifact_count"] == 1
    assert scorecard_payload["latest_training_output_artifacts"]["artifact_refs"] == ["genome:genome_api_001"]
    assert scorecard_payload["latest_eval_scorecard"]["status"] == "passed_for_shadow_only"
    assert scorecard_payload["latest_eval_scorecard"]["student_score"] == 0.852


    assert scorecard_payload["latest_eval_comparison_matrix"]["student_vs_parent_margin"] == 0.042
    assert scorecard_payload["latest_eval_comparison_matrix"]["student_vs_teacher_council_margin"] == -0.02
    assert scorecard_payload["latest_eval_case_results_summary"]["case_count"] == 12
    assert scorecard_payload["latest_eval_case_results_summary"]["student_pass_count"] == 12
    assert scorecard_payload["latest_eval_case_results_summary"]["parent_pass_count"] == 9
    assert scorecard_payload["latest_eval_case_results_summary"]["teacher_pass_count"] == 12
    assert "model_genome" in scorecard_payload["latest_cycle_artifact_replay_keys"]
    assert "eval_case_results_summary" in scorecard_payload["latest_cycle_artifact_replay_keys"]
    # Replay keys must reflect artifacts actually present, not a static list.
    replay_availability = scorecard_payload["latest_cycle_artifact_replay_availability"]
    assert replay_availability["model_genome"] is True
    assert replay_availability["eval_case_results_summary"] is True
    assert set(scorecard_payload["latest_cycle_artifact_replay_keys"]) == {
        key for key, present in replay_availability.items() if present
    }

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "growth-engine-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["growth_engine_scorecard"]["cycle_count"] == 1

    cycle_detail = client.get("/ops/brain/growth-engine/cycles/cyc_api_001")
    assert cycle_detail.status_code == 200
    cycle_replay = cycle_detail.json()["artifact_replay"]
    assert cycle_replay["student_birth_record"]["student_kind"] == "child_expert"
    assert cycle_replay["model_genome"]["model_family"] == "nexusnet_hive_moe"
    assert cycle_replay["training_checkpoint_summary"]["restore_validated_count"] == 1
    assert cycle_replay["eval_case_results_summary"]["case_count"] == 12

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "growth-engine-cockpit"}).json()
    assert blackbox["scorecard_refs"]["growth_engine"] == "/ops/brain/canon/growth-engine"
    growth_frame = next(frame for frame in blackbox["frames"] if frame["frame_id"] == "growth-engine")
    assert "/ops/brain/growth-engine/cycles" in growth_frame["evidence_refs"]
    assert "/ops/brain/growth-engine/cycles/{cycle_id}" in growth_frame["replay_refs"]
    assert "teacher_ejection_block" in growth_frame["compliance_controls"]
    assert "dataset_radar_source_review_gate" in growth_frame["compliance_controls"]
    assert "hidden_eval_attestation_gate" in growth_frame["compliance_controls"]
    assert "sealed_eval_teacher_visibility_gate" in growth_frame["compliance_controls"]
    assert "actual_weight_mutation_block" in growth_frame["compliance_controls"]
    assert "actual_weight_mutation_blocked_until" in growth_frame["compliance_controls"]
    assert "training_prerequisite_blockers" in growth_frame["compliance_controls"]
    assert "teacher_council_evidence_replay" in growth_frame["compliance_controls"]
    assert "dataset_split_replay" in growth_frame["compliance_controls"]
    assert "dataset_radar_lineage_replay" in growth_frame["compliance_controls"]
    assert "student_birth_record_replay" in growth_frame["compliance_controls"]
    assert "model_genome_replay" in growth_frame["compliance_controls"]
    assert "training_loss_trace_replay" in growth_frame["compliance_controls"]
    assert "training_checkpoint_replay" in growth_frame["compliance_controls"]
    assert "training_output_artifact_replay" in growth_frame["compliance_controls"]
    assert "eval_scorecard_replay" in growth_frame["compliance_controls"]
    assert "eval_comparison_matrix_replay" in growth_frame["compliance_controls"]
    assert "eval_case_results_replay" in growth_frame["compliance_controls"]

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Hive Model Growth Engine" in ui.text
    assert "growthEngineScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderGrowthEngineScorecard" in app_js
    assert "/ops/brain/canon/growth-engine" in app_js
    assert "Growth Engine adapter-plan gate" in app_js
    assert "growth_engine_adapter_training_gate" in app_js
    assert "adapter_training_plan_ready" in app_js
    assert "Growth Engine hard gates" in app_js
    assert "Growth Engine training prerequisites" in app_js
    assert "Growth Engine hidden eval attestation" in app_js
    assert "Growth Engine teacher council replay" in app_js
    assert "Growth Engine teacher council evidence" in app_js
    assert "Growth Engine dataset split replay" in app_js
    assert "Growth Engine Dataset Radar lineage" in app_js
    assert "Growth Engine student birth replay" in app_js
    assert "Growth Engine model genome replay" in app_js
    assert "Growth Engine training loss trace replay" in app_js
    assert "latest_training_loss_trace_summary" in app_js
    assert "Growth Engine training checkpoint replay" in app_js
    assert "latest_training_checkpoint_summary" in app_js
    assert "Growth Engine training output artifacts" in app_js
    assert "Growth Engine eval scorecard replay" in app_js
    assert "latest_eval_comparison_matrix" in app_js
    assert "latest_eval_case_results_summary" in app_js
    assert "Growth Engine per-cycle replay endpoint" in app_js
    assert "latest_cycle_artifact_replay_keys" in app_js
    assert "artifact_replay keys" in app_js
    assert "/ops/brain/growth-engine/cycles/" in app_js
    # The per-cycle replay endpoint must actually be fetched and rendered, not just printed.
    assert "inspectLatestGrowthCycleReplay" in app_js
    assert "data-growth-cycle-replay" in app_js
    assert "fetchJSON(`/ops/brain/growth-engine/cycles/" in app_js
    assert "renderGrowthCycleArtifactReplay" in app_js
    assert "latest_cycle_artifact_replay_availability" in app_js
    assert "model_family" in app_js
    assert "activation_policy" in app_js
    assert "teacher_context_only_source_ids" in app_js
    assert "sealed_eval_source_ids" in app_js
    assert "teacher_free_hidden" in app_js
    assert "teacher_output_count" in app_js
    assert "accepted_case_count" in app_js
    assert "dataset-radar-only" in app_js
    assert "teacher_visible" in app_js
    assert "actual_weight_mutation_blocked_until" in app_js
    assert "sandbox_gpu_profile_ready" in app_js
    assert "dataset_radar_source_review_passed" in app_js
    assert "hidden_eval_attestation_passed" in app_js
    assert "sealed_eval_not_teacher_visible" in app_js
    assert "actual_weight_mutation_allowed" in app_js


def test_growth_engine_public_surfaces_hide_local_artifact_paths(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    created = client.post(
        "/ops/brain/growth-engine/cycles",
        json={
            "cycle_id": "cycle:cyc_public_paths_001",
            "target_node_id": "node:expert_coder",
            "target_node_type": "Expert",
            "target_capabilities": ["multi_file_patch", "test_repair"],
            "student_kind": "child_expert",
            "birth_reason": "Public growth evidence must not expose local artifact paths.",
            "teacher_pairing_refs": ["teacher:qwen3-coder-next", "teacher:devstral-2"],
            "source_refs": ["source:licensed_synthetic_code_cases"],
        },
    )
    assert created.status_code == 200

    summary = client.get("/ops/brain/growth-engine")
    assert summary.status_code == 200
    replay = client.get("/ops/brain/growth-engine/cycles/cyc_public_paths_001")
    assert replay.status_code == 200
    visualizer = client.get("/ops/brain/visualizer/state")
    assert visualizer.status_code == 200

    serialized = json.dumps(
        {
            "created": created.json(),
            "summary": summary.json(),
            "replay": replay.json(),
            "growth_scorecard": visualizer.json()["overlay_state"]["control_panel"]["growth_engine_scorecard"],
        },
        sort_keys=True,
    )
    assert str(project_root) not in serialized
    assert "_cycle_dir" not in serialized
    assert '"cycle_dir"' not in serialized
    assert '"control_panel_replay"' not in serialized
