from __future__ import annotations

from typing import Any


class CoreExecutionPolicyEngine:
    LEGACY_MODE_MAP = {
        "teacher_fallback": "teacher-primary",
        "native_shadow": "teacher-with-native-shadow",
        "native_planner_live": "native-planner-live",
        "native_challenger_shadow": "native-challenger-shadow",
        "native_live_guarded": "native-live-guarded",
    }
    MODE_ORDER = {
        "teacher_fallback": 0,
        "native_shadow": 1,
        "native_challenger_shadow": 2,
        "native_planner_live": 3,
        "native_live_guarded": 4,
    }
    GOVERNED_ACTION_MAX_MODE = {
        "keep_teacher_fallback": "teacher_fallback",
        "allow_native_shadow": "native_shadow",
        "allow_native_challenger_shadow": "native_challenger_shadow",
        "allow_native_live_guarded": "native_live_guarded",
        "require_more_evidence": "teacher_fallback",
        "hold_for_alignment": "native_shadow",
        "rollback_to_teacher": "teacher_fallback",
    }

    def decide(
        self,
        *,
        trace_id: str,
        session_id: str,
        task_type: str,
        selected_expert: str | None,
        requested_model_id: str,
        runtime_execution_plan: dict[str, Any] | None,
        memory_node_context: dict[str, Any] | None,
        fusion_scaffold: dict[str, Any] | None,
        evidence_feeds: dict[str, Any] | None,
        teacher_registry_layer: str | None = None,
        teacher_id: str | None = None,
    ) -> dict[str, Any]:
        runtime_execution_plan = dict(runtime_execution_plan or {})
        memory_node_context = dict(memory_node_context or {})
        fusion_scaffold = dict(fusion_scaffold or {})
        evidence_feeds = dict(evidence_feeds or {})
        teacher_evidence = dict(evidence_feeds.get("teacher_evidence") or {})
        dreaming = dict(evidence_feeds.get("dreaming") or {})
        foundry = dict(evidence_feeds.get("foundry") or {})

        normalized_expert = (selected_expert or "general").lower()
        alignment = dict(fusion_scaffold.get("alignment") or {})
        fusion_expert_ids = list(dict.fromkeys(fusion_scaffold.get("expert_ids") or []))
        if not fusion_expert_ids:
            fusion_expert_ids = ["nexusnet-general-mini"]

        reasons: list[str] = []
        teacher_bundle_count = int(teacher_evidence.get("bundle_count") or 0)
        dream_artifact_count = int(dreaming.get("artifact_count") or 0)
        lineage_artifact_count = int(foundry.get("lineage_artifact_count") or 0)
        takeover_candidate_id = foundry.get("latest_native_takeover_candidate_id")
        takeover_candidate_review_status = foundry.get("latest_native_candidate_review_status")
        replacement_modes = set(foundry.get("replacement_modes") or [])
        alignment_ready = bool(alignment.get("ready_for_shadow_fusion"))
        safe_mode_fallback = bool(runtime_execution_plan.get("safe_mode_fallback"))
        takeover_scorecard_passed = bool(foundry.get("latest_takeover_scorecard_passed"))
        takeover_weighted_score = foundry.get("latest_takeover_weighted_score")
        takeover_rollbackable = bool(foundry.get("latest_takeover_rollbackable"))
        replacement_mode = foundry.get("latest_replacement_mode")
        replacement_ready = bool(foundry.get("latest_replacement_ready"))
        replacement_external_evaluation = bool(foundry.get("latest_replacement_external_evaluation_passed"))
        replacement_governance = bool(foundry.get("latest_replacement_governance_signed_off"))
        replacement_rollback_ready = bool(foundry.get("latest_replacement_rollback_ready"))
        guarded_live_ready = bool(foundry.get("guarded_live_ready"))
        promotion_decision_id = foundry.get("latest_promotion_decision_id")
        promotion_decision = foundry.get("latest_promotion_decision")
        governed_action_from_foundry = foundry.get("latest_native_governed_action")
        governed_action_reason = foundry.get("latest_native_governed_action_reason")
        governed_action_source = foundry.get("latest_native_governed_action_source")
        governed_behavior_state_id = foundry.get("latest_native_governed_behavior_state_id")
        governed_decision_id = foundry.get("latest_native_governed_decision_id")
        governed_evaluation_id = foundry.get("latest_native_governed_evaluation_id")
        alignment_hold_required_from_foundry = bool(foundry.get("latest_native_alignment_hold_required"))
        alignment_blockers_from_foundry = list(foundry.get("latest_native_alignment_blockers") or [])
        alignment_max_safe_mode_from_foundry = foundry.get("latest_native_alignment_max_safe_mode")
        alignment_ready = bool(alignment.get("ready_for_shadow_fusion"))
        alignment_hold_required = bool(alignment.get("alignment_hold_required")) or alignment_hold_required_from_foundry
        alignment_blockers = list(dict.fromkeys((alignment.get("alignment_blockers") or []) + alignment_blockers_from_foundry))
        alignment_max_safe_mode = (
            alignment.get("max_safe_native_mode")
            or alignment_max_safe_mode_from_foundry
            or ("teacher_fallback" if not alignment_ready else "native_live_guarded")
        )
        ready_for_challenger_shadow = bool(alignment.get("ready_for_challenger_shadow", alignment_ready))
        ready_for_live_guarded = bool(alignment.get("ready_for_live_guarded", alignment_max_safe_mode == "native_live_guarded"))

        fallback_triggers: list[str] = []
        guarded_live_blockers: list[str] = []

        if not alignment_ready:
            fallback_triggers.append("router_alignment_incomplete")
        if safe_mode_fallback:
            fallback_triggers.append("runtime_safe_mode_active")
        if not teacher_bundle_count:
            fallback_triggers.append("teacher_evidence_anchor_missing")
        if not fusion_expert_ids:
            fallback_triggers.append("no_internal_experts_registered")

        if teacher_bundle_count:
            reasons.append("Teacher evidence bundle anchors expert weighting.")
        if dream_artifact_count:
            reasons.append("Dream episodes justify bounded challenger consideration.")
        if lineage_artifact_count:
            reasons.append("Foundry distillation lineage is available for native planning.")
        if takeover_candidate_id:
            reasons.append("Native takeover promotion refs are available for challenger and guarded-live decisions.")
        if takeover_candidate_review_status:
            reasons.append(f"Latest native candidate review status is {takeover_candidate_review_status}.")
        if not alignment_ready:
            reasons.append("Expert-router alignment is incomplete; the teacher path remains primary.")
        elif alignment_hold_required and alignment_blockers:
            reasons.append(
                "Expert–Router Alignment still requires bounded projection or context bridging before native behavior can advance past the current safe mode."
            )
        if safe_mode_fallback:
            reasons.append("Runtime safe mode is active; native live behavior remains bounded behind teacher fallback.")
        if guarded_live_ready:
            reasons.append("Foundry readiness, rollback, evaluator, and governance signals permit guarded live consideration.")
        elif takeover_candidate_id:
            if not takeover_scorecard_passed:
                guarded_live_blockers.append("takeover_scorecard_not_passed")
            if replacement_mode != "replace":
                guarded_live_blockers.append("replacement_mode_not_replace")
            if not replacement_ready:
                guarded_live_blockers.append("replacement_readiness_incomplete")
            if not replacement_external_evaluation:
                guarded_live_blockers.append("external_evaluation_missing")
            if not replacement_governance:
                guarded_live_blockers.append("governance_signoff_missing")
            if not replacement_rollback_ready:
                guarded_live_blockers.append("rollback_not_ready")

        weights = self._weight_experts(
            selected_expert=normalized_expert,
            expert_ids=fusion_expert_ids,
            teacher_bundle_count=teacher_bundle_count,
            dream_artifact_count=dream_artifact_count,
            lineage_artifact_count=lineage_artifact_count,
            takeover_candidate_present=bool(takeover_candidate_id),
        )
        selected_internal_experts = [item["expert_id"] for item in weights[:2]]

        native_shadow_requested = dream_artifact_count > 0 or lineage_artifact_count > 0
        challenger_shadow_requested = bool(
            takeover_candidate_id
            or (dream_artifact_count > 0 and lineage_artifact_count > 0)
            or replacement_modes.intersection({"shadow", "replace"})
        )
        planner_live_requested = bool(
            takeover_candidate_id
            and (takeover_scorecard_passed or replacement_modes.intersection({"shadow", "replace"}))
        )

        if fallback_triggers:
            proposed_execution_mode = "teacher_fallback"
            proposed_shadow_vs_live = "teacher-only"
        elif guarded_live_ready and ready_for_live_guarded:
            proposed_execution_mode = "native_live_guarded"
            proposed_shadow_vs_live = "guarded-live"
        elif planner_live_requested and ready_for_challenger_shadow:
            proposed_execution_mode = "native_planner_live"
            proposed_shadow_vs_live = "live-planner"
        elif challenger_shadow_requested:
            proposed_execution_mode = "native_challenger_shadow"
            proposed_shadow_vs_live = "challenger-shadow"
        elif native_shadow_requested:
            proposed_execution_mode = "native_shadow"
            proposed_shadow_vs_live = "shadow"
        else:
            proposed_execution_mode = "teacher_fallback"
            proposed_shadow_vs_live = "teacher-only"
            fallback_triggers.append("bounded_native_evidence_insufficient")

        governed_action = governed_action_from_foundry or self._default_governed_action(
            proposed_execution_mode=proposed_execution_mode,
            takeover_candidate_present=bool(takeover_candidate_id),
            guarded_live_ready=guarded_live_ready,
            fallback_triggers=fallback_triggers,
        )
        governed_action_reason_final = governed_action_reason or f"Default governed action {governed_action} applied from current core evidence posture."
        governed_action_source_final = governed_action_source or "core-evidence-default"
        execution_mode = self._apply_governed_action(
            proposed_execution_mode=proposed_execution_mode,
            governed_action=governed_action,
        )
        governance_clamped_execution = execution_mode != proposed_execution_mode
        if governance_clamped_execution:
            fallback_triggers.append(f"governed_action_clamped::{governed_action}")
            reasons.append(
                f"Governed action {governed_action} clamps proposed mode {proposed_execution_mode} to {execution_mode}."
            )
        alignment_clamped_execution = False
        alignment_capped_mode = self._apply_mode_limit(
            current_mode=execution_mode,
            max_mode=alignment_max_safe_mode,
        )
        if alignment_hold_required and alignment_capped_mode != execution_mode:
            alignment_clamped_execution = True
            execution_mode = alignment_capped_mode
            governed_action = "hold_for_alignment"
            governed_action_reason_final = (
                f"Expert–Router Alignment holds native execution at {alignment_max_safe_mode} until "
                f"{', '.join(alignment_blockers or ['alignment blockers'])} are resolved."
            )
            governed_action_source_final = "expert-router-alignment"
            fallback_triggers.append("alignment_hold_required")
            fallback_triggers.append(f"alignment_max_safe_mode::{alignment_max_safe_mode}")
            for blocker in alignment_blockers:
                fallback_triggers.append(f"alignment_blocker::{blocker}")
            reasons.append(
                f"Expert–Router Alignment caps the effective native execution mode at {alignment_max_safe_mode}."
            )
        if governed_action == "rollback_to_teacher":
            fallback_triggers.append("governed_rollback_to_teacher")
        elif governed_action == "keep_teacher_fallback":
            fallback_triggers.append("governed_teacher_fallback")
        elif governed_action == "require_more_evidence":
            fallback_triggers.append("governed_more_evidence_required")
        elif governed_action == "hold_for_alignment":
            fallback_triggers.append("governed_hold_for_alignment")
        fallback_triggers = list(dict.fromkeys(fallback_triggers))
        shadow_vs_live = self._shadow_vs_live_path(execution_mode)
        legacy_execution_mode = self.LEGACY_MODE_MAP.get(execution_mode)
        proposed_legacy_execution_mode = self.LEGACY_MODE_MAP.get(proposed_execution_mode)
        preferred_action_map = {
            "teacher_fallback": "fall_back_to_teacher",
            "native_shadow": "keep_in_shadow",
            "native_challenger_shadow": "promote_challenger_shadow",
            "native_planner_live": "promote_challenger_shadow",
            "native_live_guarded": "allow_guarded_live",
        }

        evidence_refs = {
            "teacher_bundle_id": teacher_evidence.get("latest_bundle_id"),
            "dream_id": dreaming.get("latest_dream_id"),
            "distillation_artifact_id": foundry.get("latest_distillation_artifact_id"),
            "native_takeover_candidate_id": takeover_candidate_id,
            "replacement_readiness_report_id": foundry.get("latest_replacement_readiness_report_id"),
            "takeover_scorecard_id": foundry.get("latest_takeover_scorecard_id"),
        }
        evidence_ref_count = sum(1 for value in evidence_refs.values() if value)

        return {
            "status_label": "IMPLEMENTATION BRANCH",
            "policy_id": f"core-policy::{trace_id}",
            "trace_id": trace_id,
            "session_id": session_id,
            "task_type": task_type,
            "requested_model_id": requested_model_id,
            "selected_expert": selected_expert,
            "teacher_id": teacher_id or evidence_feeds.get("teacher_id"),
            "teacher_registry_layer": teacher_registry_layer,
            "proposed_execution_mode": proposed_execution_mode,
            "proposed_legacy_execution_mode": proposed_legacy_execution_mode,
            "execution_mode": execution_mode,
            "legacy_execution_mode": legacy_execution_mode,
            "bounded_execution_modes": list(self.LEGACY_MODE_MAP.keys()),
            "shadow_vs_live_path": shadow_vs_live,
            "proposed_shadow_vs_live_path": proposed_shadow_vs_live,
            "governed_action": governed_action,
            "governed_action_reason": governed_action_reason_final,
            "governed_action_source": governed_action_source_final,
            "governed_behavior_state_id": governed_behavior_state_id,
            "governed_decision_id": governed_decision_id,
            "governed_evaluation_id": governed_evaluation_id,
            "governance_clamped_execution": governance_clamped_execution,
            "alignment_clamped_execution": alignment_clamped_execution,
            "teacher_fallback_required": True,
            "fallback_triggers": fallback_triggers,
            "teacher_evidence_influence": {
                "bundle_count": teacher_bundle_count,
                "bundle_id": teacher_evidence.get("latest_bundle_id"),
                "selected_teachers": teacher_evidence.get("selected_teachers", []),
                "benchmark_families": teacher_evidence.get("benchmark_families", []),
                "lfm2_bounded_ok": teacher_evidence.get("lfm2_bounded_ok"),
                "influence_level": "anchored" if teacher_bundle_count else "light",
            },
            "dream_influence": {
                "artifact_count": dream_artifact_count,
                "latest_dream_id": dreaming.get("latest_dream_id"),
                "consider_challenger": native_shadow_requested,
                "shadow_signal": native_shadow_requested,
            },
            "distillation_influence": {
                "lineage_artifact_count": lineage_artifact_count,
                "latest_distillation_artifact_id": foundry.get("latest_distillation_artifact_id"),
                "source_kinds": foundry.get("latest_source_kinds", []),
                "takeover_candidate_present": bool(takeover_candidate_id),
            },
            "takeover_readiness": {
                "native_takeover_candidate_id": takeover_candidate_id,
                "candidate_review_status": takeover_candidate_review_status,
                "replacement_readiness_report_id": foundry.get("latest_replacement_readiness_report_id"),
                "takeover_scorecard_id": foundry.get("latest_takeover_scorecard_id"),
                "takeover_scorecard_passed": takeover_scorecard_passed,
                "takeover_weighted_score": takeover_weighted_score,
                "replacement_mode": replacement_mode,
                "replacement_ready": replacement_ready,
                "external_evaluation_passed": replacement_external_evaluation,
                "governance_signed_off": replacement_governance,
                "rollback_ready": replacement_rollback_ready or takeover_rollbackable,
                "guarded_live_ready": guarded_live_ready,
                "guarded_live_blockers": guarded_live_blockers,
                "alignment_hold_required": alignment_hold_required,
                "alignment_blockers": alignment_blockers,
                "alignment_max_safe_mode": alignment_max_safe_mode,
                "promotion_decision_id": promotion_decision_id,
                "promotion_decision": promotion_decision,
                "governed_action": governed_action,
                "replacement_modes": sorted(replacement_modes),
                "shadow_vs_live_path": shadow_vs_live,
                "direct_native_takeover_allowed": False,
                "preferred_action": preferred_action_map.get(execution_mode),
            },
            "alignment_summary": {
                "ready_for_shadow_fusion": alignment_ready,
                "ready_for_challenger_shadow": ready_for_challenger_shadow,
                "ready_for_live_guarded": ready_for_live_guarded,
                "alignment_hold_required": alignment_hold_required,
                "alignment_blockers": alignment_blockers,
                "max_safe_native_mode": alignment_max_safe_mode,
                "projection_required_count": alignment.get("projection_required_count"),
                "context_bridge_count": alignment.get("context_bridge_count"),
                "incompatible_expert_ids": alignment.get("incompatible_expert_ids", []),
            },
            "expert_weighting": weights,
            "selected_internal_experts": selected_internal_experts,
            "memory_plane_bias": {
                "active_planes": memory_node_context.get("active_planes", []),
                "dreaming_planes": memory_node_context.get("dreaming_planes", []),
                "foundry_evidence_planes": memory_node_context.get("foundry_evidence_planes", []),
            },
            "runtime_qes_bias": {
                "selected_runtime_name": runtime_execution_plan.get("selected_runtime_name"),
                "safe_mode_fallback": runtime_execution_plan.get("safe_mode_fallback"),
                "max_context_tokens": ((runtime_execution_plan.get("hardware_profile") or {}).get("max_context_tokens")),
                "quantization": ((runtime_execution_plan.get("quantization_decision") or {}).get("selected_quantization")),
            },
            "alignment_ready": alignment_ready,
            "evidence_refs": evidence_refs,
            "evidence_ref_count": evidence_ref_count,
            "rollback_guard": {
                "rollback_mode": "teacher_fallback",
                "legacy_rollback_mode": self.LEGACY_MODE_MAP.get("teacher_fallback"),
                "fallback_path": "teacher-attached-model",
                "reason": "Evidence-driven native behavior stays bounded and teacher-verifiable.",
            },
            "decision_reasons": reasons or ["Teacher-backed attached-model execution remains the bounded default."],
        }

    def _default_governed_action(
        self,
        *,
        proposed_execution_mode: str,
        takeover_candidate_present: bool,
        guarded_live_ready: bool,
        fallback_triggers: list[str],
    ) -> str:
        if any(trigger.startswith("governed_") for trigger in fallback_triggers):
            return "rollback_to_teacher"
        if proposed_execution_mode == "teacher_fallback":
            return "keep_teacher_fallback"
        if guarded_live_ready:
            return "allow_native_live_guarded"
        if proposed_execution_mode in {"native_planner_live", "native_challenger_shadow"}:
            return "allow_native_challenger_shadow"
        if proposed_execution_mode == "native_shadow" or takeover_candidate_present:
            return "allow_native_shadow"
        return "require_more_evidence"

    def _apply_governed_action(self, *, proposed_execution_mode: str, governed_action: str) -> str:
        allowed_mode = self.GOVERNED_ACTION_MAX_MODE.get(governed_action, "teacher_fallback")
        return self._apply_mode_limit(current_mode=proposed_execution_mode, max_mode=allowed_mode)

    def _apply_mode_limit(self, *, current_mode: str, max_mode: str) -> str:
        current_rank = self.MODE_ORDER.get(current_mode, 0)
        allowed_rank = self.MODE_ORDER.get(max_mode, 0)
        effective_rank = min(current_rank, allowed_rank)
        for mode, rank in self.MODE_ORDER.items():
            if rank == effective_rank:
                return mode
        return "teacher_fallback"

    def _shadow_vs_live_path(self, execution_mode: str) -> str:
        return {
            "teacher_fallback": "teacher-only",
            "native_shadow": "shadow",
            "native_challenger_shadow": "challenger-shadow",
            "native_planner_live": "live-planner",
            "native_live_guarded": "guarded-live",
        }.get(execution_mode, "teacher-only")

    def _weight_experts(
        self,
        *,
        selected_expert: str,
        expert_ids: list[str],
        teacher_bundle_count: int,
        dream_artifact_count: int,
        lineage_artifact_count: int,
        takeover_candidate_present: bool,
    ) -> list[dict[str, Any]]:
        weighted: list[dict[str, Any]] = []
        for expert_id in expert_ids:
            normalized = expert_id.lower()
            score = 1.0
            if selected_expert in {"coder", "coding"}:
                score += 0.45 if ("devstral" in normalized or "coder" in normalized) else 0.10
            elif selected_expert in {"researcher", "research"}:
                score += 0.45 if "research" in normalized else 0.10
            elif "general" in normalized:
                score += 0.25
            if teacher_bundle_count:
                score += 0.20 if selected_expert in normalized or "general" in normalized else 0.10
            if dream_artifact_count and "nexusnet" in normalized:
                score += 0.15
            if lineage_artifact_count and "nexusnet" in normalized:
                score += 0.15
            if takeover_candidate_present and ("nexusnet" in normalized or "devstral" in normalized):
                score += 0.20
            weighted.append(
                {
                    "expert_id": expert_id,
                    "weight": score,
                    "family_bias": self._family_bias(expert_id),
                }
            )
        total = sum(item["weight"] for item in weighted) or 1.0
        normalized_weights = [
            {
                **item,
                "weight": round(item["weight"] / total, 4),
            }
            for item in weighted
        ]
        return sorted(normalized_weights, key=lambda item: item["weight"], reverse=True)

    def _family_bias(self, expert_id: str) -> str:
        normalized = expert_id.lower()
        if "devstral" in normalized:
            return "implementation-first"
        if "research" in normalized:
            return "evidence-first"
        return "synthesis-first"
