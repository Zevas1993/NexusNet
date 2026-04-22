from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from nexusnet.core import CoreExecutionPolicyEngine, NativeExecutionPlanner
from nexusnet.experts import InternalExpertExecutionService
from nexusnet.schemas import SessionContext
from tests.test_nexus_phase1_foundation import make_project


def test_brain_generate_uses_teacher_primary_policy_without_evidence(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    result = services.brain.generate(
        session_context=SessionContext(session_id="core-policy", expert="researcher", use_retrieval=False),
        prompt="Summarize the current evidence-aware execution path.",
        model_hint="mock/default",
    )

    core_execution = result.inference_trace.metrics["core_execution"]
    policy = core_execution["execution_policy"]
    native_execution = core_execution["native_execution"]

    assert policy["execution_mode"] == "teacher_fallback"
    assert policy["proposed_execution_mode"] == "teacher_fallback"
    assert policy["legacy_execution_mode"] == "teacher-primary"
    assert policy["governed_action"] in {"keep_teacher_fallback", "require_more_evidence"}
    assert policy["selected_internal_experts"]
    assert policy["teacher_fallback_required"] is True
    assert "teacher_evidence_anchor_missing" in policy["fallback_triggers"]
    assert native_execution["enabled"] is False
    assert native_execution["teacher_fallback_path"] == "teacher-attached-model"
    assert core_execution["model_attachment"]["execution_mode"] == "teacher_fallback"
    assert core_execution["model_attachment"]["proposed_execution_mode"] == "teacher_fallback"
    assert core_execution["model_attachment"]["legacy_execution_mode"] == "teacher-primary"
    assert core_execution["model_attachment"]["governed_action"] in {"keep_teacher_fallback", "require_more_evidence"}
    assert core_execution["model_attachment"]["execution_policy_id"] == policy["policy_id"]


def test_evidence_driven_policy_promotes_native_planner_and_internal_expert_harness(tmp_path: Path):
    project_root = make_project(tmp_path)
    app = create_app(str(project_root))
    client = TestClient(app)
    services = app.state.services

    chat = client.post(
        "/chat",
        json={
            "session_id": "fusion-evidence",
            "message": "Research the source evidence and citation path for native growth.",
            "teacher_id": "mixtral-8x7b",
            "rag": False,
        },
    )
    assert chat.status_code == 200
    first_trace_id = chat.json()["trace_id"]

    dream = client.post(
        "/ops/brain/dream",
        json={"trace_id": first_trace_id, "model_hint": "mock/default", "variant_count": 2},
    )
    assert dream.status_code == 200

    distill = client.post(
        "/ops/brain/distill-dataset",
        json={"name": "fusion-evidence-dataset", "trace_limit": 20, "include_dreams": True, "include_curriculum": True},
    )
    assert distill.status_code == 200
    native_candidate_id = distill.json()["native_takeover_candidate"]["candidate_id"]

    follow_up = client.post(
        "/chat",
        json={
            "session_id": "fusion-evidence",
            "message": "Research how the core should use native growth evidence now.",
            "teacher_id": "mixtral-8x7b",
            "rag": False,
        },
    )
    assert follow_up.status_code == 200
    trace_id = follow_up.json()["trace_id"]

    stored_trace = services.store.get_trace(trace_id)
    core_execution = ((stored_trace or {}).get("metrics") or {}).get("core_execution", {})
    policy = core_execution["execution_policy"]
    native_execution = core_execution["native_execution"]
    promotion_linkage = core_execution["promotion_linkage"]

    assert policy["proposed_execution_mode"] in {"native_challenger_shadow", "native_planner_live", "native_live_guarded"}
    assert policy["execution_mode"] in {"native_shadow", "native_challenger_shadow", "native_planner_live", "native_live_guarded"}
    assert policy["governed_action"] in {
        "allow_native_shadow",
        "allow_native_challenger_shadow",
        "allow_native_live_guarded",
        "keep_teacher_fallback",
        "require_more_evidence",
    }
    assert policy["dream_influence"]["consider_challenger"] is True
    assert policy["takeover_readiness"]["native_takeover_candidate_id"] == native_candidate_id
    assert native_execution["enabled"] is True
    assert native_execution["output_count"] >= 1
    assert native_execution["disagreement_count"] >= 1
    assert native_execution["teacher_fallback_path"] == "teacher-attached-model"
    assert native_execution["native_candidate"]["candidate_id"].startswith("nativeexec::")
    assert native_execution["native_candidate"]["activation_mode"] in {
        "shadow-advisory-draft",
        "challenger-shadow-draft",
        "planner-live-draft",
        "guarded-live-draft",
        "teacher-fallback-only",
    }
    assert native_execution["native_candidate"]["confidence"] >= 0.0
    assert promotion_linkage["candidate_id"] == native_candidate_id
    assert promotion_linkage["governed_action"] in {
        "allow_native_shadow",
        "allow_native_challenger_shadow",
        "allow_native_live_guarded",
        "keep_teacher_fallback",
        "require_more_evidence",
        "hold_for_alignment",
        "rollback_to_teacher",
    }
    assert promotion_linkage["execution_action"] in {
        "keep_in_shadow",
        "promote_challenger_shadow",
        "allow_guarded_live",
        "fall_back_to_teacher",
        "require_more_evidence",
    }
    assert core_execution["model_attachment"]["execution_mode"] == policy["execution_mode"]
    assert core_execution["model_attachment"]["evidence_refs"]["native_takeover_candidate_id"] == native_candidate_id
    assert core_execution["model_attachment"]["promotion_action"] == promotion_linkage["execution_action"]
    assert core_execution["model_attachment"]["native_candidate_id"] == native_execution["native_candidate"]["candidate_id"]
    assert promotion_linkage["behavior_loop"]["next_step"] in {
        "expand_shadow_execution",
        "run_teacher_challenger_comparison",
        "teacher_verify_native_candidate",
        "strengthen_guarded_live_readiness",
        "resolve_alignment_blockers",
        "collect_more_evidence",
        "stay_teacher_primary",
        "rollback_and_rebuild_evidence",
    }
    assert core_execution["model_attachment"]["native_execution_verdict"] in {
        "shadow-advisory",
        "challenger-shadow-compare",
        "planner-live-guidance",
        "guarded-live-supported",
        "guarded-live-blocked",
        "teacher-fallback",
        "alignment-hold",
    }


def test_core_summary_and_wrapper_surface_expose_execution_policy_and_internal_expert_preview(tmp_path: Path):
    project_root = make_project(tmp_path)
    app = create_app(str(project_root))
    client = TestClient(app)

    client.post(
        "/chat",
        json={
            "session_id": "fusion-surface",
            "message": "Research the source evidence and citation path for native growth.",
            "teacher_id": "mixtral-8x7b",
            "rag": False,
        },
    )
    latest_trace_id = client.post(
        "/chat",
        json={
            "session_id": "fusion-surface",
            "message": "Research how the core should use native growth evidence now.",
            "teacher_id": "mixtral-8x7b",
            "rag": False,
        },
    ).json()["trace_id"]

    core = client.get("/ops/brain/core", params={"session_id": "fusion-surface", "expert": "researcher"})
    assert core.status_code == 200
    core_payload = core.json()

    assert core_payload["execution_policy"]["policy_id"].startswith("core-policy::")
    assert core_payload["native_execution_preview"]["teacher_fallback_path"] == "teacher-attached-model"
    assert core_payload["promotion_linkage_preview"]["governed_action"] in {
        "allow_native_shadow",
        "allow_native_challenger_shadow",
        "allow_native_live_guarded",
        "keep_teacher_fallback",
        "require_more_evidence",
        "hold_for_alignment",
        "rollback_to_teacher",
    }
    assert core_payload["promotion_linkage_preview"]["execution_action"] in {
        "keep_in_shadow",
        "promote_challenger_shadow",
        "allow_guarded_live",
        "fall_back_to_teacher",
        "require_more_evidence",
    }

    wrapper = client.get("/ops/brain/wrapper-surface", params={"session_id": "fusion-surface"})
    assert wrapper.status_code == 200
    core_execution = wrapper.json()["core_execution"]

    assert core_execution["latest_trace_id"] == latest_trace_id
    assert core_execution["execution_mode"] in {
        "teacher_fallback",
        "native_shadow",
        "native_challenger_shadow",
        "native_planner_live",
        "native_live_guarded",
    }
    assert core_execution["proposed_execution_mode"] in {
        "teacher_fallback",
        "native_shadow",
        "native_challenger_shadow",
        "native_planner_live",
        "native_live_guarded",
        None,
    }
    assert core_execution["policy_id"].startswith("core-policy::")
    assert isinstance(core_execution["internal_expert_ids"], list)
    assert core_execution["governed_action"] in {
        "allow_native_shadow",
        "allow_native_challenger_shadow",
        "allow_native_live_guarded",
        "keep_teacher_fallback",
        "require_more_evidence",
        "hold_for_alignment",
        "rollback_to_teacher",
        None,
    }
    assert core_execution["promotion_action"] in {
        "keep_in_shadow",
        "promote_challenger_shadow",
        "allow_guarded_live",
        "fall_back_to_teacher",
        "require_more_evidence",
        None,
    }
    assert core_execution["native_activation_mode"] in {
        "shadow-advisory-draft",
        "challenger-shadow-draft",
        "planner-live-draft",
        "guarded-live-draft",
        "teacher-fallback-only",
        None,
    }
    assert core_execution["behavior_next_step"] in {
        "expand_shadow_execution",
        "run_teacher_challenger_comparison",
        "teacher_verify_native_candidate",
        "strengthen_guarded_live_readiness",
        "resolve_alignment_blockers",
        "collect_more_evidence",
        "stay_teacher_primary",
        "rollback_and_rebuild_evidence",
        None,
    }


def test_guarded_live_execution_stays_bounded_and_can_fall_back_to_teacher():
    engine = CoreExecutionPolicyEngine()
    planner = NativeExecutionPlanner()
    internal_execution = InternalExpertExecutionService()

    evidence_feeds = {
        "subject": "researcher",
        "teacher_evidence": {
            "bundle_count": 1,
            "latest_bundle_id": "teachbundle-1",
            "selected_teachers": ["mixtral-8x7b"],
            "benchmark_families": ["native-growth"],
            "lfm2_bounded_ok": True,
        },
        "dreaming": {
            "artifact_count": 2,
            "latest_dream_id": "dream-1",
        },
        "foundry": {
            "lineage_artifact_count": 1,
            "latest_distillation_artifact_id": "distill-1",
            "latest_source_kinds": ["trace", "dream"],
            "latest_native_takeover_candidate_id": "nativecand-1",
            "latest_native_candidate_review_status": "approved",
            "latest_native_candidate_rollback_reference": "rollback::nativecand-1",
            "latest_takeover_scorecard_id": "score-1",
            "latest_takeover_trend_report_id": "trend-1",
            "latest_takeover_scorecard_passed": True,
            "latest_takeover_weighted_score": 0.91,
            "latest_takeover_rollbackable": True,
            "latest_replacement_readiness_report_id": "repl-1",
            "latest_fleet_summary_ids": ["fleet-1"],
            "latest_cohort_scorecard_ids": ["cohort-1"],
            "latest_replacement_mode": "replace",
            "latest_replacement_ready": True,
            "latest_replacement_external_evaluation_passed": True,
            "latest_replacement_governance_signed_off": True,
            "latest_replacement_rollback_ready": True,
            "replacement_modes": ["replace", "shadow"],
            "guarded_live_ready": True,
            "latest_promotion_decision_id": "promodec-1",
            "latest_promotion_decision": "approved",
        },
    }
    fusion_scaffold = {
        "router": "mixtral-router",
        "backbone": "mixtral",
        "expert_ids": ["nexusnet-general-mini", "devstral-coder"],
        "alignment": {"ready_for_shadow_fusion": True},
        "neural_bus": {"bus_id": "neuralbus-1"},
        "cortex_peer": {"peer_id": "cortex-1"},
    }
    runtime_execution_plan = {
        "selected_runtime_name": "mock",
        "safe_mode_fallback": False,
        "hardware_profile": {"max_context_tokens": 131072},
        "quantization_decision": {"selected_quantization": "int8"},
    }
    memory_node_context = {
        "active_planes": ["conceptual", "temporal", "imaginal"],
        "dreaming_planes": ["imaginal"],
        "foundry_evidence_planes": ["metacognitive", "goal"],
        "projection_names": ["3-plane", "8-plane", "11-plane"],
    }

    policy = engine.decide(
        trace_id="guarded-live-trace",
        session_id="guarded-live-session",
        task_type="research",
        selected_expert="researcher",
        requested_model_id="mock/default",
        runtime_execution_plan=runtime_execution_plan,
        memory_node_context=memory_node_context,
        fusion_scaffold=fusion_scaffold,
        evidence_feeds=evidence_feeds,
        teacher_registry_layer="v2026_live",
        teacher_id="mixtral-8x7b",
    )
    assert policy["execution_mode"] == "native_live_guarded"
    assert policy["takeover_readiness"]["guarded_live_ready"] is True
    assert policy["governed_action"] == "allow_native_live_guarded"

    native_plan = planner.plan(
        trace_id="guarded-live-trace",
        selected_expert="researcher",
        execution_policy=policy,
        fusion_scaffold=fusion_scaffold,
        memory_node_context=memory_node_context,
        evidence_feeds=evidence_feeds,
    )
    native_execution = internal_execution.execute(
        prompt="Explain how NexusNet should execute native growth safely.",
        selected_expert="researcher",
        native_execution_plan=native_plan,
        execution_policy=policy,
        evidence_feeds=evidence_feeds,
    )
    assert native_execution["fallback_triggered"] is True
    assert "guarded_live_disagreement" in native_execution["fallback_triggers"]
    assert native_execution["guarded_live_allowed"] is False
    assert native_execution["native_candidate"]["blocked_reason"] == "runtime-fallback-triggered"

    promotion_linkage = planner.promotion_linkage(
        selected_expert="researcher",
        execution_policy=policy,
        native_execution_plan=native_plan,
        native_execution_result=native_execution,
        evidence_feeds=evidence_feeds,
    )
    assert promotion_linkage["governed_action"] == "rollback_to_teacher"
    assert promotion_linkage["effective_execution_mode"] == "teacher_fallback"
    assert promotion_linkage["execution_action"] == "fall_back_to_teacher"
    assert promotion_linkage["rollback_reference"] == "rollback::nativecand-1"


def test_governed_action_clamps_proposed_mode_to_shadow():
    engine = CoreExecutionPolicyEngine()

    evidence_feeds = {
        "teacher_evidence": {
            "bundle_count": 1,
            "latest_bundle_id": "teachbundle-2",
            "selected_teachers": ["mixtral-8x7b"],
            "benchmark_families": ["native-growth"],
            "lfm2_bounded_ok": True,
        },
        "dreaming": {
            "artifact_count": 2,
            "latest_dream_id": "dream-2",
        },
        "foundry": {
            "lineage_artifact_count": 1,
            "latest_distillation_artifact_id": "distill-2",
            "latest_source_kinds": ["trace", "dream"],
            "latest_native_takeover_candidate_id": "nativecand-2",
            "latest_native_candidate_review_status": "review",
            "latest_takeover_scorecard_id": "score-2",
            "latest_takeover_trend_report_id": "trend-2",
            "latest_takeover_scorecard_passed": True,
            "latest_takeover_weighted_score": 0.88,
            "latest_takeover_rollbackable": True,
            "latest_replacement_readiness_report_id": "repl-2",
            "latest_replacement_mode": "replace",
            "latest_replacement_ready": True,
            "latest_replacement_external_evaluation_passed": True,
            "latest_replacement_governance_signed_off": True,
            "latest_replacement_rollback_ready": True,
            "replacement_modes": ["replace", "shadow"],
            "guarded_live_ready": True,
            "latest_native_governed_action": "allow_native_shadow",
            "latest_native_governed_action_reason": "Governance keeps this candidate shadow-only despite stronger readiness signals.",
            "latest_native_governed_action_source": "promotion-decision",
        },
    }
    policy = engine.decide(
        trace_id="governed-shadow-clamp",
        session_id="governed-shadow-clamp",
        task_type="research",
        selected_expert="researcher",
        requested_model_id="mock/default",
        runtime_execution_plan={
            "selected_runtime_name": "mock",
            "safe_mode_fallback": False,
            "hardware_profile": {"max_context_tokens": 131072},
            "quantization_decision": {"selected_quantization": "int8"},
        },
        memory_node_context={
            "active_planes": ["conceptual", "temporal", "imaginal"],
            "dreaming_planes": ["imaginal"],
            "foundry_evidence_planes": ["metacognitive", "goal"],
        },
        fusion_scaffold={
            "router": "mixtral-router",
            "backbone": "mixtral",
            "expert_ids": ["nexusnet-research-mini", "nexusnet-general-mini"],
            "alignment": {"ready_for_shadow_fusion": True},
        },
        evidence_feeds=evidence_feeds,
        teacher_registry_layer="v2026_live",
        teacher_id="mixtral-8x7b",
    )

    assert policy["proposed_execution_mode"] == "native_live_guarded"
    assert policy["execution_mode"] == "native_shadow"
    assert policy["governed_action"] == "allow_native_shadow"
    assert policy["governance_clamped_execution"] is True
    assert "governed_action_clamped::allow_native_shadow" in policy["fallback_triggers"]


def test_alignment_hold_clamps_live_readiness_to_shadow_mode():
    engine = CoreExecutionPolicyEngine()

    evidence_feeds = {
        "teacher_evidence": {
            "bundle_count": 1,
            "latest_bundle_id": "teachbundle-3",
            "selected_teachers": ["mixtral-8x7b"],
            "benchmark_families": ["native-growth"],
            "lfm2_bounded_ok": True,
        },
        "dreaming": {
            "artifact_count": 3,
            "latest_dream_id": "dream-3",
        },
        "foundry": {
            "lineage_artifact_count": 2,
            "latest_distillation_artifact_id": "distill-3",
            "latest_source_kinds": ["trace", "dream"],
            "latest_native_takeover_candidate_id": "nativecand-3",
            "latest_native_candidate_review_status": "approved",
            "latest_takeover_scorecard_id": "score-3",
            "latest_takeover_trend_report_id": "trend-3",
            "latest_takeover_scorecard_passed": True,
            "latest_takeover_weighted_score": 0.93,
            "latest_takeover_rollbackable": True,
            "latest_replacement_readiness_report_id": "repl-3",
            "latest_replacement_mode": "replace",
            "latest_replacement_ready": True,
            "latest_replacement_external_evaluation_passed": True,
            "latest_replacement_governance_signed_off": True,
            "latest_replacement_rollback_ready": True,
            "replacement_modes": ["replace", "shadow"],
            "guarded_live_ready": True,
            "latest_native_governed_action": "allow_native_live_guarded",
            "latest_native_governed_action_reason": "Promotion and evaluator evidence allow guarded live if the core path stays bounded.",
            "latest_native_governed_action_source": "promotion-decision",
        },
    }

    policy = engine.decide(
        trace_id="alignment-hold-trace",
        session_id="alignment-hold-session",
        task_type="research",
        selected_expert="researcher",
        requested_model_id="mock/default",
        runtime_execution_plan={
            "selected_runtime_name": "mock",
            "safe_mode_fallback": False,
            "hardware_profile": {"max_context_tokens": 131072},
            "quantization_decision": {"selected_quantization": "int8"},
        },
        memory_node_context={
            "active_planes": ["conceptual", "temporal", "imaginal"],
            "dreaming_planes": ["imaginal"],
            "foundry_evidence_planes": ["metacognitive", "goal"],
        },
        fusion_scaffold={
            "router": "mixtral-router",
            "backbone": "mixtral",
                "expert_ids": ["nexusnet-research-mini", "nexusnet-general-mini"],
                "alignment": {
                    "ready_for_shadow_fusion": True,
                    "ready_for_challenger_shadow": True,
                    "ready_for_live_guarded": True,
                    "alignment_hold_required": True,
                    "alignment_blockers": ["projection_bridge_required", "context_bridge_required"],
                    "max_safe_native_mode": "native_shadow",
                "projection_required_count": 2,
                "context_bridge_count": 2,
                "incompatible_expert_ids": [],
            },
        },
        evidence_feeds=evidence_feeds,
        teacher_registry_layer="v2026_live",
        teacher_id="mixtral-8x7b",
    )

    assert policy["proposed_execution_mode"] == "native_live_guarded"
    assert policy["execution_mode"] == "native_shadow"
    assert policy["governed_action"] == "hold_for_alignment"
    assert policy["alignment_summary"]["alignment_hold_required"] is True
    assert policy["alignment_summary"]["max_safe_native_mode"] == "native_shadow"
    assert "alignment_hold_required" in policy["fallback_triggers"]
    assert "alignment_max_safe_mode::native_shadow" in policy["fallback_triggers"]


def test_alignment_hold_runtime_blocks_planner_live_and_recommends_shadow():
    internal_execution = InternalExpertExecutionService()

    native_execution = internal_execution.execute(
        prompt="Explain how native execution should stay bounded while alignment work is still pending.",
        selected_expert="researcher",
        native_execution_plan={
            "execution_id": "nativeexec::alignment-runtime",
            "enabled": True,
            "execution_mode": "native_planner_live",
            "legacy_execution_mode": "native-planner-live",
            "selected_internal_experts": ["nexusnet-research-mini", "nexusnet-general-mini"],
            "primary_expert_id": "nexusnet-research-mini",
            "teacher_fallback_path": "teacher-attached-model",
            "fallback_triggers": [],
            "challenger_compare_required": False,
            "guarded_live_enabled": False,
            "live_guidance_enabled": True,
            "alignment_hold_required": True,
            "alignment_blockers": ["projection_bridge_required"],
            "memory_planes": ["conceptual", "imaginal"],
        },
        execution_policy={
            "policy_id": "core-policy::alignment-runtime",
            "evidence_refs": {
                "teacher_bundle_id": "teachbundle-4",
                "native_takeover_candidate_id": "nativecand-4",
            },
        },
        evidence_feeds={
            "teacher_evidence": {
                "latest_bundle_id": "teachbundle-4",
            },
            "foundry": {
                "latest_native_takeover_candidate_id": "nativecand-4",
            },
        },
    )

    assert native_execution["fallback_triggered"] is True
    assert "alignment_hold_runtime" in native_execution["runtime_fallback_triggers"]
    assert native_execution["teacher_comparison"]["verdict"] == "alignment-hold"
    assert native_execution["recommended_execution_mode"] == "native_shadow"
    assert native_execution["native_candidate"]["blocked_reason"] == "alignment-hold-active"
    assert native_execution["native_response_outline"]
    assert any("Alignment hold remains active" in item for item in native_execution["prompt_guidance"])
