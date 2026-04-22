from __future__ import annotations

from ..schemas import NativePromotionDecision


class NativePromotionGate:
    GOVERNED_TO_EXECUTION_ACTION = {
        "keep_teacher_fallback": "fall_back_to_teacher",
        "allow_native_shadow": "keep_in_shadow",
        "allow_native_challenger_shadow": "promote_challenger_shadow",
        "allow_native_live_guarded": "allow_guarded_live",
        "require_more_evidence": "require_more_evidence",
        "hold_for_alignment": "keep_in_shadow",
        "rollback_to_teacher": "fall_back_to_teacher",
    }

    def decide(
        self,
        *,
        subject: str,
        benchmark_summary: dict,
        evaluator_decision: str = "shadow",
        teacher_evidence: dict | None = None,
    ) -> NativePromotionDecision:
        takeover_scorecard = benchmark_summary.get("takeover_scorecard", {})
        takeover_trend = benchmark_summary.get("takeover_trend_report", {})
        replacement_readiness = benchmark_summary.get("replacement_readiness", {})
        alignment = benchmark_summary.get("alignment", {})
        alignment_hold_required = bool(
            benchmark_summary.get("alignment_hold_required")
            or alignment.get("alignment_hold_required")
        )
        takeover_passed = (
            bool(takeover_scorecard.get("passed"))
            and bool(takeover_trend.get("ready"))
            and bool(benchmark_summary.get("cohort_gate_ready"))
            and replacement_readiness.get("replacement_mode") != "hold"
        )
        governance_checks = {
            "takeover_scorecard_passed": bool(takeover_scorecard.get("passed")),
            "takeover_trend_ready": bool(takeover_trend.get("ready")),
            "replacement_mode": replacement_readiness.get("replacement_mode"),
            "replacement_ready": bool(replacement_readiness.get("ready")),
            "external_evaluation_passed": bool(replacement_readiness.get("external_evaluation_passed")),
            "rollback_ready": bool(replacement_readiness.get("rollback_ready")),
            "governance_signed_off": bool(replacement_readiness.get("governance_signed_off")),
            "alignment_hold_required": alignment_hold_required,
            "alignment_blockers": list(alignment.get("alignment_blockers") or []),
            "alignment_max_safe_mode": alignment.get("max_safe_native_mode"),
        }
        proposed_execution_mode = benchmark_summary.get("proposed_execution_mode")
        if benchmark_summary.get("rollback_requested") or benchmark_summary.get("teacher_fallback_triggered"):
            decision = "hold"
            governed_action = "rollback_to_teacher"
            rationale = "Core execution must roll back to the teacher path because governed challenger checks produced blocking fallback or rollback conditions."
        elif alignment_hold_required:
            decision = "hold"
            governed_action = "hold_for_alignment"
            rationale = (
                "Foundry and evaluator evidence may justify native advancement, but Expert–Router Alignment still requires "
                "projection or context-bridge work before behavior can advance past bounded shadow execution."
            )
        elif evaluator_decision == "approved" and takeover_passed:
            decision = "promote"
            governed_action = "allow_native_live_guarded"
            rationale = "Native capability cleared takeover scorecard thresholds, repeated-run trend gates, cohort governance, and external evaluator approval."
        elif takeover_passed or proposed_execution_mode in {"native_challenger_shadow", "native_planner_live", "native_live_guarded"}:
            decision = "shadow"
            governed_action = "allow_native_challenger_shadow"
            rationale = "Native capability cleared benchmark and replacement shadow gates but still lacks final evaluator or governance approval for guarded live execution."
        elif benchmark_summary.get("takeover_scorecard_id") or benchmark_summary.get("replacement_readiness_report_id"):
            decision = "shadow"
            governed_action = "allow_native_shadow"
            rationale = "Native capability has partial foundry evidence and remains shadow-only until stronger evaluator, rollback, and governance signals exist."
        elif proposed_execution_mode == "teacher_fallback":
            decision = "hold"
            governed_action = "keep_teacher_fallback"
            rationale = "Governed behavior keeps the teacher path primary because bounded native execution is not yet justified."
        else:
            decision = "hold"
            governed_action = "require_more_evidence"
            rationale = "Native capability requires more foundry evidence before challenger shadow or guarded live execution should be considered."
        return NativePromotionDecision(
            subject=subject,
            decision=decision,
            governed_action=governed_action,
            execution_action=self.GOVERNED_TO_EXECUTION_ACTION[governed_action],
            rationale=rationale,
            benchmark_summary=benchmark_summary,
            teacher_evidence=teacher_evidence or {},
            threshold_set_id=benchmark_summary.get("threshold_set_id"),
            takeover_scorecard_id=benchmark_summary.get("takeover_scorecard_id"),
            takeover_trend_report_id=benchmark_summary.get("takeover_trend_report_id"),
            fleet_summary_ids=[item.get("summary_id") for item in benchmark_summary.get("fleet_summaries", [])],
            cohort_scorecard_ids=[item.get("cohort_id") for item in benchmark_summary.get("cohort_scorecards", [])],
            replacement_readiness_report_id=benchmark_summary.get("replacement_readiness_report_id"),
            teacher_evidence_bundle_id=(teacher_evidence or {}).get("bundle_id"),
            rollback_reference=benchmark_summary.get("rollback_reference"),
            governance_checks=governance_checks,
            evaluator_linkage={
                "evaluator_decision": evaluator_decision,
                "takeover_scorecard_id": benchmark_summary.get("takeover_scorecard_id"),
                "replacement_readiness_report_id": benchmark_summary.get("replacement_readiness_report_id"),
                "promotion_decision_id": benchmark_summary.get("promotion_decision_id"),
            },
        )
