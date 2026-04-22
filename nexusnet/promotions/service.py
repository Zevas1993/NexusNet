from __future__ import annotations

from typing import Any

from nexus.governance import GovernanceService
from nexus.schemas import ApprovalRequest
from nexus.storage import NexusStore

from ..evals import ExternalBehaviorEvaluator
from ..schemas import PromotionCandidateRecord, PromotionDecisionRecord, PromotionEvaluationRecord, PromotionCandidateKind


class PromotionService:
    def __init__(
        self,
        *,
        store: NexusStore,
        governance: GovernanceService,
        evaluator: ExternalBehaviorEvaluator,
        retrieval_rerank_bridge: Any | None = None,
    ):
        self.store = store
        self.governance = governance
        self.evaluator = evaluator
        self.retrieval_rerank_bridge = retrieval_rerank_bridge

    def create_candidate(
        self,
        *,
        candidate_kind: PromotionCandidateKind,
        subject_id: str,
        baseline_reference: str,
        challenger_reference: str,
        lineage: str,
        status_label: str = "LOCKED CANON",
        rollback_reference: str | None = None,
        traceability: dict[str, Any] | None = None,
    ) -> PromotionCandidateRecord:
        traceability = dict(traceability or {})
        if candidate_kind == "retrieval-policy" and self.retrieval_rerank_bridge is not None:
            traceability = self.retrieval_rerank_bridge.enrich_traceability(
                subject_id=subject_id,
                challenger_reference=challenger_reference,
                traceability=traceability,
            )
        teacher_evidence = dict(traceability.get("teacher_evidence", {}))
        threshold_set_id = traceability.get("threshold_set_id") or teacher_evidence.get("threshold_set_id")
        teacher_evidence_bundle_id = traceability.get("teacher_evidence_bundle_id") or teacher_evidence.get("bundle_id")
        for existing in self.list_candidates(candidate_kind=candidate_kind, limit=500):
            if existing.subject_id == subject_id and existing.challenger_reference == challenger_reference:
                merged_traceability = dict(existing.traceability)
                merged_traceability.update(traceability)
                updated = existing.model_copy(
                    update={
                        "threshold_set_id": threshold_set_id or existing.threshold_set_id,
                        "teacher_evidence_bundle_id": teacher_evidence_bundle_id or existing.teacher_evidence_bundle_id,
                        "traceability": merged_traceability,
                    }
                )
                self.store.save_promotion_candidate(updated.model_dump(mode="json"))
                return updated
        record = PromotionCandidateRecord(
            candidate_kind=candidate_kind,
            subject_id=subject_id,
            baseline_reference=baseline_reference,
            challenger_reference=challenger_reference,
            lineage=lineage,
            status_label=status_label,
            rollback_reference=rollback_reference,
            threshold_set_id=threshold_set_id,
            teacher_evidence_bundle_id=teacher_evidence_bundle_id,
            traceability=traceability,
        )
        self.store.save_promotion_candidate(record.model_dump(mode="json"))
        self.governance.record_event("promotion.candidate.created", record.model_dump(mode="json"))
        return record

    def list_candidates(self, *, candidate_kind: str | None = None, limit: int = 200) -> list[PromotionCandidateRecord]:
        return [
            PromotionCandidateRecord.model_validate(payload)
            for payload in self.store.list_promotion_candidates(candidate_kind=candidate_kind, limit=limit)
        ]

    def get_candidate(self, candidate_id: str) -> PromotionCandidateRecord | None:
        payload = self.store.get_promotion_candidate(candidate_id)
        if payload is None:
            return None
        return PromotionCandidateRecord.model_validate(payload)

    def evaluate_candidate(
        self,
        *,
        candidate_id: str,
        scenario_set: list[str] | None = None,
        candidate_metrics: dict[str, float] | None = None,
        limit: int = 25,
    ) -> PromotionEvaluationRecord:
        candidate = self.get_candidate(candidate_id)
        if candidate is None:
            raise KeyError(candidate_id)
        report = self.evaluator.evaluate_candidate(
            subject=candidate.subject_id,
            baseline_reference=candidate.baseline_reference,
            challenger_reference=candidate.challenger_reference,
            scenario_set=scenario_set or [],
            candidate_metrics=candidate_metrics or {},
            candidate_kind=candidate.candidate_kind,
            candidate_traceability=candidate.traceability,
            limit=limit,
        )
        artifact_paths = {key: value for key, value in report["artifacts"].items() if value}
        evaluation = PromotionEvaluationRecord(
            candidate_id=candidate.candidate_id,
            candidate_kind=candidate.candidate_kind,
            subject_id=candidate.subject_id,
            decision=report["decision"]["decision"],
            rationale=report["decision"]["rationale"],
            baseline_reference=candidate.baseline_reference,
            challenger_reference=candidate.challenger_reference,
            scenario_set=report.get("scenario_set", scenario_set or []),
            metrics=report["metrics"],
            threshold_set_id=candidate.threshold_set_id,
            teacher_evidence_bundle_id=candidate.teacher_evidence_bundle_id,
            artifacts=artifact_paths,
            status_label=candidate.status_label,
        )
        self.store.save_promotion_evaluation(evaluation.model_dump(mode="json"))
        updated_candidate = candidate.model_copy(
            update={
                "review_status": "review" if evaluation.decision == "approved" else "shadow",
            }
        )
        self.store.save_promotion_candidate(updated_candidate.model_dump(mode="json"))
        self.governance.record_event("promotion.candidate.evaluated", evaluation.model_dump(mode="json"))
        return evaluation

    def decide_candidate(
        self,
        *,
        candidate_id: str,
        approver: str,
        requested_decision: str = "approved",
        rationale: str | None = None,
    ) -> PromotionDecisionRecord:
        candidate = self.get_candidate(candidate_id)
        if candidate is None:
            raise KeyError(candidate_id)
        evaluation_payload = self.store.latest_promotion_evaluation(candidate_id)
        evaluator_decision = (
            PromotionEvaluationRecord.model_validate(evaluation_payload).decision
            if evaluation_payload is not None
            else "shadow"
        )
        if requested_decision == "rejected":
            final_decision = "rejected"
            governance_decision = "rejected"
            final_rationale = rationale or "Promotion rejected during governed review."
        elif requested_decision == "shadow":
            final_decision = "shadow"
            governance_decision = "shadow"
            final_rationale = rationale or "Candidate remains shadow-only pending later promotion."
        elif evaluator_decision != "approved":
            final_decision = "shadow"
            governance_decision = "shadow"
            final_rationale = rationale or "Candidate remains shadow-only until EvalsAO approval is recorded."
        else:
            final_decision = "approved"
            governance_decision = "approved"
            final_rationale = rationale or "Candidate cleared EvalsAO and governance approval."

        rollback = self.governance.prepare_rollback(
            subject=candidate.subject_id,
            target_version=candidate.challenger_reference,
            metadata={"candidate_id": candidate.candidate_id, "candidate_kind": candidate.candidate_kind},
        )
        self.governance.record_approval(
            ApprovalRequest(
                subject=candidate.subject_id,
                decision=governance_decision,
                approver=approver,
                rationale=final_rationale,
                metadata={"candidate_id": candidate.candidate_id, "candidate_kind": candidate.candidate_kind},
            )
        )
        decision = PromotionDecisionRecord(
            candidate_id=candidate.candidate_id,
            candidate_kind=candidate.candidate_kind,
            subject_id=candidate.subject_id,
            evaluator_decision=evaluator_decision,
            governance_decision=governance_decision,
            decision=final_decision,
            approver=approver,
            rationale=final_rationale,
            rollback_reference=rollback.rollback_id,
            threshold_set_id=candidate.threshold_set_id,
            teacher_evidence_bundle_id=candidate.teacher_evidence_bundle_id,
            artifacts={"rollback": rollback.rollback_id},
            status_label=candidate.status_label,
        )
        self.store.save_promotion_decision(decision.model_dump(mode="json"))
        updated_candidate = candidate.model_copy(
            update={
                "review_status": "approved" if final_decision == "approved" else ("rejected" if final_decision == "rejected" else "shadow"),
                "rollback_reference": rollback.rollback_id,
            }
        )
        self.store.save_promotion_candidate(updated_candidate.model_dump(mode="json"))
        self.governance.record_event("promotion.candidate.decided", decision.model_dump(mode="json"))
        return decision

    def native_behavior_summary(
        self,
        *,
        subject_id: str | None = None,
        candidate_id: str | None = None,
    ) -> dict[str, Any]:
        candidate: PromotionCandidateRecord | None = None
        if candidate_id:
            candidate = self.get_candidate(candidate_id)
        elif subject_id:
            for item in self.list_candidates(candidate_kind="native-takeover", limit=200):
                if item.subject_id == subject_id:
                    candidate = item
                    break
        if candidate is None:
            return {
                "status_label": "LOCKED CANON",
                "behavior_state_id": f"nativebehavior::{subject_id or candidate_id or 'unknown'}",
                "candidate_id": candidate_id,
                "subject_id": subject_id,
                "governed_action": "require_more_evidence",
                "reason": "No native-takeover candidate is available for governed behavioralization.",
                "source": "no-candidate",
                "review_status": None,
                "evaluation_id": None,
                "evaluation_decision": None,
                "decision_id": None,
                "decision": None,
                "rollback_reference": None,
                "teacher_evidence_bundle_id": None,
                "threshold_set_id": None,
            }

        latest_evaluation = self.store.latest_promotion_evaluation(candidate.candidate_id)
        latest_decision = self.store.latest_promotion_decision(candidate.candidate_id)
        benchmark = dict(candidate.traceability.get("benchmark", {}))
        alignment = dict(candidate.traceability.get("alignment") or benchmark.get("alignment") or {})
        takeover_scorecard = dict(candidate.traceability.get("takeover_scorecard") or benchmark.get("takeover_scorecard") or {})
        replacement_readiness = dict(benchmark.get("replacement_readiness") or {})
        takeover_passed = bool(takeover_scorecard.get("passed"))
        alignment_hold_required = bool(alignment.get("alignment_hold_required"))
        alignment_blockers = list(alignment.get("alignment_blockers") or [])
        alignment_max_safe_mode = alignment.get("max_safe_native_mode")
        governed_action = "require_more_evidence"
        reason = "Native candidate needs more evaluator, rollback, or governance evidence before behavior can advance."
        source = "candidate-review-status"

        if (latest_decision or {}).get("decision") == "rejected":
            governed_action = "rollback_to_teacher"
            reason = "Governed promotion decision rejected the candidate and requires rollback to the teacher path."
            source = "promotion-decision"
        elif alignment_hold_required and (
            (latest_decision or {}).get("decision") in {"approved", "shadow"}
            or (latest_evaluation or {}).get("decision") == "approved"
            or takeover_passed
        ):
            governed_action = "hold_for_alignment"
            reason = "Evidence supports bounded native advancement, but Expert–Router Alignment is still blocking escalation past the current safe mode."
            source = "alignment-hold"
        elif (latest_decision or {}).get("decision") == "approved":
            if takeover_passed and replacement_readiness.get("ready") and replacement_readiness.get("external_evaluation_passed") and replacement_readiness.get("governance_signed_off") and (replacement_readiness.get("rollback_ready") or candidate.rollback_reference):
                governed_action = "allow_native_live_guarded"
                reason = "Governed promotion decision and replacement readiness permit bounded guarded-live native behavior."
            else:
                governed_action = "allow_native_challenger_shadow"
                reason = "Governed promotion is approved, but replacement readiness remains insufficient for guarded live behavior."
            source = "promotion-decision"
        elif (latest_decision or {}).get("decision") == "shadow":
            governed_action = "allow_native_challenger_shadow" if takeover_passed or candidate.review_status in {"review", "approved"} else "allow_native_shadow"
            reason = "Governed promotion keeps the candidate shadow-only while allowing bounded challenger behavior."
            source = "promotion-decision"
        elif (latest_evaluation or {}).get("decision") == "rejected":
            governed_action = "keep_teacher_fallback"
            reason = "Evaluator artifacts rejected the current candidate, so the teacher path remains primary."
            source = "promotion-evaluation"
        elif (latest_evaluation or {}).get("decision") == "approved" and takeover_passed:
            governed_action = "allow_native_challenger_shadow"
            reason = "Evaluator artifacts support challenger-shadow behavior, but governance approval for guarded live is not yet recorded."
            source = "promotion-evaluation"
        elif candidate.review_status == "approved" and takeover_passed:
            governed_action = "allow_native_challenger_shadow"
            reason = "Candidate review status supports challenger-shadow behavior while full governed live approval remains pending."
        elif candidate.review_status in {"review", "shadow"} or benchmark.get("replacement_readiness_report_id") or benchmark.get("takeover_scorecard_id"):
            governed_action = "allow_native_shadow"
            reason = "Partial benchmark or review evidence supports bounded native shadow behavior."
        elif candidate.review_status == "rejected":
            governed_action = "rollback_to_teacher"
            reason = "Candidate review status is rejected and requires a teacher-path rollback."

        return {
            "status_label": "LOCKED CANON",
            "behavior_state_id": f"nativebehavior::{candidate.candidate_id}",
            "candidate_id": candidate.candidate_id,
            "subject_id": candidate.subject_id,
            "governed_action": governed_action,
            "reason": reason,
            "source": source,
            "review_status": candidate.review_status,
            "evaluation_id": (latest_evaluation or {}).get("evaluation_id"),
            "evaluation_decision": (latest_evaluation or {}).get("decision"),
            "decision_id": (latest_decision or {}).get("decision_id"),
            "decision": (latest_decision or {}).get("decision"),
            "rollback_reference": candidate.rollback_reference or (latest_decision or {}).get("rollback_reference"),
            "teacher_evidence_bundle_id": candidate.teacher_evidence_bundle_id,
            "threshold_set_id": candidate.threshold_set_id,
            "alignment_hold_required": alignment_hold_required,
            "alignment_blockers": alignment_blockers,
            "alignment_max_safe_mode": alignment_max_safe_mode,
        }

    def summary(self) -> dict[str, Any]:
        candidates = self.list_candidates(limit=200)
        output = []
        retrieval_policy_evidence = []
        for candidate in candidates:
            latest_evaluation = self.store.latest_promotion_evaluation(candidate.candidate_id)
            rerank_evidence = candidate.traceability.get("retrieval_rerank_evidence", {})
            if rerank_evidence:
                evaluation_artifacts = {
                    key: value
                    for key, value in (latest_evaluation or {}).get("artifacts", {}).items()
                    if key in {"retrieval_rerank_evidence", "retrieval_rerank_review", "assimilation_artifacts", "assimilation_scorecards"}
                }
                retrieval_policy_evidence.append(
                    {
                        "candidate_id": candidate.candidate_id,
                        "subject_id": candidate.subject_id,
                        "bundle_id": rerank_evidence.get("bundle_id"),
                        "scorecard_id": rerank_evidence.get("scorecard_id"),
                        "benchmark_family_id": rerank_evidence.get("benchmark_family_id"),
                        "threshold_set_id": rerank_evidence.get("threshold_set_id"),
                        "artifact_path": rerank_evidence.get("artifact_path"),
                        "scorecard_passed": rerank_evidence.get("scorecard_passed"),
                        "review_report_id": rerank_evidence.get("review_report_id"),
                        "review_headline": rerank_evidence.get("review_headline"),
                        "review_summary": rerank_evidence.get("review_summary", []),
                        "human_summary": (candidate.traceability.get("retrieval_rerank_review") or {}).get("human_summary"),
                        "review_badges": (candidate.traceability.get("retrieval_rerank_review") or {}).get("review_badges", {}),
                        "candidate_shift_count": (((candidate.traceability.get("retrieval_rerank_review") or {}).get("candidate_shift_summary")) or {}).get("changed_count", 0),
                        "candidate_shift_summary": (candidate.traceability.get("retrieval_rerank_review") or {}).get("candidate_shift_summary", {}),
                        "top_shift_preview": (candidate.traceability.get("retrieval_rerank_review") or {}).get("top_shift_preview"),
                        "delta_summary": (candidate.traceability.get("retrieval_rerank_review") or {}).get("delta_summary", {}),
                        "threshold_summary": (candidate.traceability.get("retrieval_rerank_review") or {}).get("threshold_summary", {}),
                        "evaluator_artifact_summary": {
                            "artifact_count": len(evaluation_artifacts),
                            "artifact_ids": sorted(evaluation_artifacts.keys()),
                        },
                        "review_artifacts": rerank_evidence.get("review_artifacts", {}),
                        "reranker_provider": rerank_evidence.get("reranker_provider"),
                        "latency_delta_ms": rerank_evidence.get("latency_delta_ms"),
                        "relevance_delta": rerank_evidence.get("relevance_delta"),
                        "groundedness_delta": rerank_evidence.get("groundedness_delta"),
                        "provenance_delta": rerank_evidence.get("provenance_delta"),
                        "evaluation_artifacts": evaluation_artifacts,
                        "latest_evaluation_decision": (latest_evaluation or {}).get("decision"),
                    }
                )
            output.append(
                {
                    "candidate": candidate.model_dump(mode="json"),
                    "latest_evaluation": latest_evaluation,
                    "latest_decision": self.store.latest_promotion_decision(candidate.candidate_id),
                }
            )
        return {
            "status_label": "LOCKED CANON",
            "count": len(output),
            "items": output,
            "retrieval_policy_evidence": retrieval_policy_evidence,
        }
