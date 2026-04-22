from __future__ import annotations

from typing import Any

from ..foundry.promotion import NativePromotionGate


class NativeExecutionPlanner:
    LEGACY_MODE_MAP = {
        "teacher_fallback": "teacher-primary",
        "native_shadow": "teacher-with-native-shadow",
        "native_planner_live": "native-planner-live",
        "native_challenger_shadow": "native-challenger-shadow",
        "native_live_guarded": "native-live-guarded",
    }
    GOVERNED_ACTION_TO_MODE = {
        "keep_teacher_fallback": "teacher_fallback",
        "allow_native_shadow": "native_shadow",
        "allow_native_challenger_shadow": "native_challenger_shadow",
        "allow_native_live_guarded": "native_live_guarded",
        "require_more_evidence": "teacher_fallback",
        "hold_for_alignment": "native_shadow",
        "rollback_to_teacher": "teacher_fallback",
    }
    GOVERNED_ACTION_TO_EXECUTION_ACTION = {
        "keep_teacher_fallback": "fall_back_to_teacher",
        "allow_native_shadow": "keep_in_shadow",
        "allow_native_challenger_shadow": "promote_challenger_shadow",
        "allow_native_live_guarded": "allow_guarded_live",
        "require_more_evidence": "require_more_evidence",
        "hold_for_alignment": "keep_in_shadow",
        "rollback_to_teacher": "fall_back_to_teacher",
    }
    GOVERNED_ACTION_ORDER = {
        "rollback_to_teacher": 0,
        "keep_teacher_fallback": 0,
        "require_more_evidence": 0,
        "hold_for_alignment": 1,
        "allow_native_shadow": 1,
        "allow_native_challenger_shadow": 2,
        "allow_native_live_guarded": 3,
    }
    MODE_ORDER = {
        "teacher_fallback": 0,
        "native_shadow": 1,
        "native_challenger_shadow": 2,
        "native_planner_live": 3,
        "native_live_guarded": 4,
    }

    def __init__(self, *, promotion_gate: NativePromotionGate | None = None):
        self.promotion_gate = promotion_gate or NativePromotionGate()

    def plan(
        self,
        *,
        trace_id: str,
        selected_expert: str | None,
        execution_policy: dict[str, Any] | None,
        fusion_scaffold: dict[str, Any] | None,
        memory_node_context: dict[str, Any] | None,
        evidence_feeds: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        execution_policy = dict(execution_policy or {})
        fusion_scaffold = dict(fusion_scaffold or {})
        memory_node_context = dict(memory_node_context or {})
        evidence_feeds = dict(evidence_feeds or {})
        foundry = dict(evidence_feeds.get("foundry") or {})
        execution_mode = execution_policy.get("execution_mode", "teacher_fallback")
        proposed_execution_mode = execution_policy.get("proposed_execution_mode", execution_mode)
        governed_action = execution_policy.get("governed_action")
        selected_internal_experts = list(execution_policy.get("selected_internal_experts") or [])
        fallback_triggers = list(execution_policy.get("fallback_triggers") or [])
        guarded_live_enabled = execution_mode == "native_live_guarded"
        challenger_shadow_enabled = execution_mode == "native_challenger_shadow"
        shadow_enabled = execution_mode in {"native_shadow", "native_challenger_shadow"}
        planner_live_enabled = execution_mode == "native_planner_live"
        enabled = bool(selected_internal_experts) and execution_mode != "teacher_fallback"
        prompt_guidance_mode = "disabled"
        if guarded_live_enabled:
            prompt_guidance_mode = "guarded_live_verifier"
        elif planner_live_enabled:
            prompt_guidance_mode = "live_planner_prefix"
        elif challenger_shadow_enabled:
            prompt_guidance_mode = "challenger_shadow_compare"
        elif shadow_enabled:
            prompt_guidance_mode = "shadow_advisory"
        return {
            "status_label": "IMPLEMENTATION BRANCH",
            "execution_id": f"nativeexec::{trace_id}",
            "enabled": enabled,
            "execution_mode": execution_mode,
            "proposed_execution_mode": proposed_execution_mode,
            "legacy_execution_mode": self.LEGACY_MODE_MAP.get(execution_mode),
            "selected_expert": selected_expert,
            "selected_internal_experts": selected_internal_experts,
            "primary_expert_id": selected_internal_experts[0] if selected_internal_experts else None,
            "shadow_enabled": shadow_enabled,
            "challenger_shadow_enabled": challenger_shadow_enabled,
            "planner_live_enabled": planner_live_enabled,
            "guarded_live_enabled": guarded_live_enabled,
            "teacher_fallback_path": "teacher-attached-model",
            "router_id": fusion_scaffold.get("router"),
            "backbone": fusion_scaffold.get("backbone"),
            "neural_bus_id": ((fusion_scaffold.get("neural_bus") or {}).get("bus_id")),
            "cortex_peer_id": ((fusion_scaffold.get("cortex_peer") or {}).get("peer_id")),
            "memory_planes": memory_node_context.get("active_planes", []),
            "memory_projection_names": memory_node_context.get("projection_names", []),
            "bounded_host_execution": True,
            "fallback_triggers": fallback_triggers,
            "challenger_compare_required": challenger_shadow_enabled or guarded_live_enabled,
            "live_guidance_enabled": planner_live_enabled or guarded_live_enabled,
            "evidence_refs": execution_policy.get("evidence_refs", {}),
            "prompt_guidance_mode": prompt_guidance_mode,
            "governed_action": governed_action,
            "alignment_hold_required": ((execution_policy.get("alignment_summary") or {}).get("alignment_hold_required", False)),
            "alignment_blockers": ((execution_policy.get("alignment_summary") or {}).get("alignment_blockers", [])),
            "alignment_max_safe_mode": ((execution_policy.get("alignment_summary") or {}).get("max_safe_native_mode")),
            "fallback_reference": foundry.get("latest_native_candidate_rollback_reference"),
            "promotion_candidate_state": {
                "candidate_id": foundry.get("latest_native_takeover_candidate_id"),
                "review_status": foundry.get("latest_native_candidate_review_status"),
                "takeover_scorecard_passed": foundry.get("latest_takeover_scorecard_passed"),
                "replacement_mode": foundry.get("latest_replacement_mode"),
                "guarded_live_ready": foundry.get("guarded_live_ready"),
            },
            "guarded_live_budget": {
                "max_internal_experts": min(len(selected_internal_experts), 2),
                "teacher_verification_required": True,
                "rollback_required": True,
            },
        }

    def promotion_linkage(
        self,
        *,
        selected_expert: str | None,
        execution_policy: dict[str, Any] | None,
        native_execution_plan: dict[str, Any] | None,
        native_execution_result: dict[str, Any] | None,
        evidence_feeds: dict[str, Any] | None,
    ) -> dict[str, Any]:
        execution_policy = dict(execution_policy or {})
        native_execution_plan = dict(native_execution_plan or {})
        native_execution_result = dict(native_execution_result or {})
        evidence_feeds = dict(evidence_feeds or {})
        foundry = dict(evidence_feeds.get("foundry") or {})
        benchmark_summary = {
            "execution_mode": execution_policy.get("execution_mode"),
            "proposed_execution_mode": execution_policy.get("proposed_execution_mode"),
            "legacy_execution_mode": execution_policy.get("legacy_execution_mode"),
            "governed_action": execution_policy.get("governed_action"),
            "native_candidate_confidence": (((native_execution_result.get("native_candidate") or {}).get("confidence"))),
            "native_candidate_activation_mode": (((native_execution_result.get("native_candidate") or {}).get("activation_mode"))),
            "teacher_comparison_verdict": ((((native_execution_result.get("teacher_comparison") or {}).get("verdict")))),
            "takeover_scorecard_id": foundry.get("latest_takeover_scorecard_id"),
            "takeover_scorecard": {
                "scorecard_id": foundry.get("latest_takeover_scorecard_id"),
                "passed": foundry.get("latest_takeover_scorecard_passed"),
                "weighted_score": foundry.get("latest_takeover_weighted_score"),
                "rollbackable": foundry.get("latest_takeover_rollbackable"),
            },
            "takeover_trend_report_id": foundry.get("latest_takeover_trend_report_id"),
            "replacement_readiness_report_id": foundry.get("latest_replacement_readiness_report_id"),
            "replacement_readiness": {
                "report_id": foundry.get("latest_replacement_readiness_report_id"),
                "replacement_mode": foundry.get("latest_replacement_mode"),
                "ready": foundry.get("latest_replacement_ready"),
                "external_evaluation_passed": foundry.get("latest_replacement_external_evaluation_passed"),
                "rollback_ready": foundry.get("latest_replacement_rollback_ready"),
                "governance_signed_off": foundry.get("latest_replacement_governance_signed_off"),
            },
            "teacher_fallback_triggered": bool(native_execution_result.get("fallback_triggered")),
            "rollback_reference": foundry.get("latest_native_candidate_rollback_reference"),
            "promotion_decision_id": foundry.get("latest_promotion_decision_id"),
            "fleet_summaries": [{"summary_id": item} for item in foundry.get("latest_fleet_summary_ids", [])],
            "cohort_scorecards": [{"cohort_id": item} for item in foundry.get("latest_cohort_scorecard_ids", [])],
            "rollback_requested": execution_policy.get("governed_action") == "rollback_to_teacher",
            "alignment_hold_required": ((execution_policy.get("alignment_summary") or {}).get("alignment_hold_required", False)),
            "alignment": execution_policy.get("alignment_summary", {}),
        }
        evaluator_decision = (
            "approved"
            if foundry.get("latest_replacement_external_evaluation_passed") and foundry.get("latest_takeover_scorecard_passed")
            else "shadow"
        )
        promotion_decision = self.promotion_gate.decide(
            subject=selected_expert or evidence_feeds.get("subject") or "unknown-subject",
            benchmark_summary=benchmark_summary,
            evaluator_decision=evaluator_decision,
            teacher_evidence=evidence_feeds.get("teacher_evidence"),
        )
        fallback_triggered = bool(native_execution_result.get("fallback_triggered"))
        governed_action = promotion_decision.governed_action
        policy_governed_action = execution_policy.get("governed_action")
        if policy_governed_action:
            governed_action = self._merge_governed_actions(
                left=policy_governed_action,
                right=governed_action,
            )
        if native_execution_result.get("alignment_hold_required"):
            governed_action = self._merge_governed_actions(
                left="hold_for_alignment",
                right=governed_action,
            )
        if fallback_triggered:
            governed_action = "rollback_to_teacher"
        elif execution_policy.get("execution_mode") == "teacher_fallback":
            governed_action = execution_policy.get("governed_action") or (
                "keep_teacher_fallback" if execution_policy.get("fallback_triggers") else "allow_native_shadow"
            )
        effective_execution_mode = self._merge_execution_modes(
            execution_policy.get("execution_mode", "teacher_fallback"),
            self.GOVERNED_ACTION_TO_MODE.get(
                governed_action,
                execution_policy.get("execution_mode", "teacher_fallback"),
            ),
            native_execution_plan.get("alignment_max_safe_mode"),
            native_execution_result.get("recommended_execution_mode"),
        )
        return {
            "status_label": "IMPLEMENTATION BRANCH",
            "decision_id": promotion_decision.decision_id,
            "governed_action": governed_action,
            "governed_action_source": execution_policy.get("governed_action_source"),
            "governed_behavior_state_id": execution_policy.get("governed_behavior_state_id"),
            "governed_decision_id": execution_policy.get("governed_decision_id"),
            "governed_evaluation_id": execution_policy.get("governed_evaluation_id"),
            "execution_action": self.GOVERNED_ACTION_TO_EXECUTION_ACTION.get(governed_action, promotion_decision.execution_action),
            "subject": promotion_decision.subject,
            "execution_mode": execution_policy.get("execution_mode"),
            "proposed_execution_mode": execution_policy.get("proposed_execution_mode"),
            "effective_execution_mode": effective_execution_mode,
            "legacy_execution_mode": self.LEGACY_MODE_MAP.get(execution_policy.get("execution_mode")),
            "legacy_effective_execution_mode": self.LEGACY_MODE_MAP.get(effective_execution_mode),
            "native_execution_id": native_execution_plan.get("execution_id"),
            "candidate_id": foundry.get("latest_native_takeover_candidate_id"),
            "teacher_bundle_id": ((evidence_feeds.get("teacher_evidence") or {}).get("latest_bundle_id")),
            "takeover_scorecard_id": promotion_decision.takeover_scorecard_id,
            "takeover_trend_report_id": promotion_decision.takeover_trend_report_id,
            "replacement_readiness_report_id": promotion_decision.replacement_readiness_report_id,
            "rollback_reference": promotion_decision.rollback_reference,
            "governance_checks": promotion_decision.governance_checks,
            "evaluator_linkage": promotion_decision.evaluator_linkage,
            "teacher_fallback_triggered": fallback_triggered,
            "runtime_fallback_triggers": native_execution_result.get("runtime_fallback_triggers", []),
            "fallback_triggers": native_execution_result.get("fallback_triggers", []) or execution_policy.get("fallback_triggers", []),
            "alignment_hold_required": native_execution_result.get("alignment_hold_required", native_execution_plan.get("alignment_hold_required", False)),
            "alignment_blockers": native_execution_result.get("alignment_blockers", native_execution_plan.get("alignment_blockers", [])),
            "teacher_comparison": native_execution_result.get("teacher_comparison"),
            "native_candidate": native_execution_result.get("native_candidate"),
            "behavior_loop": {
                "loop_id": f"behloop::{promotion_decision.decision_id}",
                "next_step": self._next_step(
                    governed_action=governed_action,
                    teacher_comparison=native_execution_result.get("teacher_comparison", {}),
                    native_candidate=native_execution_result.get("native_candidate", {}),
                ),
                "teacher_verification_required": bool(
                    ((native_execution_result.get("native_candidate") or {}).get("teacher_verification_required"))
                ),
                "candidate_id": ((native_execution_result.get("native_candidate") or {}).get("candidate_id")),
                "candidate_confidence": ((native_execution_result.get("native_candidate") or {}).get("confidence")),
                "activation_mode": ((native_execution_result.get("native_candidate") or {}).get("activation_mode")),
            },
            "bounded_guardrails": {
                "teacher_fallback_path": native_execution_plan.get("teacher_fallback_path"),
                "guarded_live_allowed": bool(native_execution_result.get("guarded_live_allowed")),
                "challenger_compare_required": bool(native_execution_plan.get("challenger_compare_required")),
            },
            "rationale": promotion_decision.rationale,
            "benchmark_summary": benchmark_summary,
        }

    def _merge_governed_actions(self, *, left: str, right: str) -> str:
        left_rank = self.GOVERNED_ACTION_ORDER.get(left, 0)
        right_rank = self.GOVERNED_ACTION_ORDER.get(right, 0)
        return left if left_rank <= right_rank else right

    def _merge_execution_modes(self, *modes: str | None) -> str:
        selected: str | None = None
        selected_rank = float("inf")
        for mode in modes:
            if mode is None:
                continue
            rank = self.MODE_ORDER.get(mode, 0)
            if rank < selected_rank:
                selected = mode
                selected_rank = rank
        return selected or "teacher_fallback"

    def _next_step(
        self,
        *,
        governed_action: str,
        teacher_comparison: dict[str, Any],
        native_candidate: dict[str, Any],
    ) -> str:
        verdict = teacher_comparison.get("verdict")
        if governed_action == "rollback_to_teacher":
            return "rollback_and_rebuild_evidence"
        if governed_action == "keep_teacher_fallback":
            return "stay_teacher_primary"
        if governed_action == "require_more_evidence":
            return "collect_more_evidence"
        if governed_action == "hold_for_alignment":
            return "resolve_alignment_blockers"
        if governed_action == "allow_native_shadow":
            return "expand_shadow_execution"
        if governed_action == "allow_native_challenger_shadow":
            return "run_teacher_challenger_comparison"
        if governed_action == "allow_native_live_guarded":
            if verdict == "guarded-live-supported" and native_candidate.get("activation_allowed"):
                return "teacher_verify_native_candidate"
            return "strengthen_guarded_live_readiness"
        return "collect_more_evidence"
