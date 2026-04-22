from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CoreEvidenceBridge:
    def __init__(
        self,
        *,
        store: Any,
        artifacts_dir: Path,
        promotion_service: Any | None = None,
    ):
        self.store = store
        self.artifacts_dir = Path(artifacts_dir)
        self.promotion_service = promotion_service

    def snapshot(
        self,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        subject: str | None = None,
        teacher_id: str | None = None,
    ) -> dict[str, Any]:
        trace = self._resolve_trace(trace_id=trace_id, session_id=session_id)
        selected_subject = (
            subject
            or ((trace or {}).get("selected_expert"))
            or ((((trace or {}).get("teacher_provenance") or {}).get("routing_decision")) or {}).get("subject")
        )
        selected_teacher_id = (
            teacher_id
            or ((trace or {}).get("selected_teacher_id"))
            or (((trace or {}).get("teacher_provenance") or {}).get("teacher_id"))
        )
        source_trace_id = trace_id or ((trace or {}).get("trace_id"))
        teacher_bundles = self._teacher_bundles(subject=selected_subject, teacher_id=selected_teacher_id)
        latest_bundle = teacher_bundles[0] if teacher_bundles else None
        dream_artifacts = self._dream_artifacts(source_trace_id=source_trace_id, session_id=session_id)
        latest_dream = dream_artifacts[0] if dream_artifacts else None
        distillation_lineage = self._distillation_lineage(
            subject=selected_subject,
            teacher_id=selected_teacher_id,
            teacher_bundle_id=(latest_bundle or {}).get("bundle_id"),
        )
        latest_lineage = distillation_lineage[0] if distillation_lineage else None
        native_takeover_candidates = self._native_takeover_candidates(
            subject=selected_subject,
            teacher_id=selected_teacher_id,
            teacher_bundle_id=(latest_bundle or {}).get("bundle_id"),
            distillation_artifact_id=(latest_lineage or {}).get("artifact_id"),
        )
        latest_candidate = native_takeover_candidates[0] if native_takeover_candidates else None
        takeover_scorecards = self.store.list_takeover_scorecards(subject=selected_subject, limit=50) if selected_subject else []
        latest_takeover_scorecard = takeover_scorecards[0] if takeover_scorecards else None
        replacement_readiness_reports = (
            self.store.list_replacement_readiness_reports(subject=selected_subject, limit=50) if selected_subject else []
        )
        latest_replacement_readiness = replacement_readiness_reports[0] if replacement_readiness_reports else None
        latest_promotion_decision = (
            self.store.latest_promotion_decision((latest_candidate or {}).get("candidate_id"))
            if latest_candidate and (latest_candidate or {}).get("candidate_id")
            else None
        )
        governed_behavior = (
            self.promotion_service.native_behavior_summary(
                subject_id=selected_subject,
                candidate_id=(latest_candidate or {}).get("candidate_id"),
            )
            if self.promotion_service is not None and hasattr(self.promotion_service, "native_behavior_summary")
            else {}
        )
        latest_candidate_benchmark = (((latest_candidate or {}).get("traceability") or {}).get("benchmark")) or {}
        takeover_scorecard_passed = bool((latest_takeover_scorecard or {}).get("passed"))
        takeover_rollbackable = bool((latest_takeover_scorecard or {}).get("rollbackable"))
        replacement_mode = (latest_replacement_readiness or {}).get("replacement_mode")
        replacement_ready = bool((latest_replacement_readiness or {}).get("ready"))
        replacement_external_evaluation = bool((latest_replacement_readiness or {}).get("external_evaluation_passed"))
        replacement_governance = bool((latest_replacement_readiness or {}).get("governance_signed_off"))
        replacement_rollback = bool((latest_replacement_readiness or {}).get("rollback_ready")) or takeover_rollbackable
        guarded_live_ready = all(
            [
                takeover_scorecard_passed,
                replacement_ready,
                replacement_external_evaluation,
                replacement_governance,
                replacement_rollback,
                replacement_mode == "replace",
            ]
        )
        return {
            "status_label": "IMPLEMENTATION BRANCH",
            "source_trace_id": source_trace_id,
            "session_id": session_id or ((trace or {}).get("session_id")),
            "subject": selected_subject,
            "teacher_id": selected_teacher_id,
            "teacher_evidence": {
                "bundle_count": len(teacher_bundles),
                "latest_bundle_id": (latest_bundle or {}).get("bundle_id"),
                "latest_threshold_set_id": (latest_bundle or {}).get("threshold_set_id"),
                "benchmark_families": (latest_bundle or {}).get("benchmark_families", []),
                "selected_teachers": (latest_bundle or {}).get("selected_teachers", []),
                "lfm2_bounded_ok": (latest_bundle or {}).get("lfm2_bounded_ok"),
            },
            "dreaming": {
                "artifact_count": len(dream_artifacts),
                "latest_dream_id": (latest_dream or {}).get("dream_id"),
                "latest_artifact_path": (latest_dream or {}).get("artifact_path"),
                "latest_source_trace_id": (((latest_dream or {}).get("scenario")) or {}).get("source_trace_id"),
            },
            "foundry": {
                "lineage_artifact_count": len(distillation_lineage),
                "latest_distillation_artifact_id": (latest_lineage or {}).get("artifact_id"),
                "latest_distillation_artifact_path": (latest_lineage or {}).get("artifact_path"),
                "latest_lineage": (latest_lineage or {}).get("lineage"),
                "latest_source_kinds": (latest_lineage or {}).get("source_kinds", []),
                "native_takeover_candidate_ids": [item.get("candidate_id") for item in native_takeover_candidates if item.get("candidate_id")],
                "latest_native_takeover_candidate_id": (latest_candidate or {}).get("candidate_id"),
                "latest_native_candidate_review_status": (latest_candidate or {}).get("review_status"),
                "latest_native_candidate_rollback_reference": (latest_candidate or {}).get("rollback_reference"),
                "latest_takeover_scorecard_id": (
                    latest_candidate_benchmark.get("takeover_scorecard_id")
                    or ((takeover_scorecards[0] if takeover_scorecards else {}).get("scorecard_id"))
                ),
                "latest_takeover_trend_report_id": ((latest_candidate_benchmark.get("takeover_trend_report")) or {}).get("trend_id"),
                "latest_takeover_scorecard_passed": takeover_scorecard_passed,
                "latest_takeover_weighted_score": (latest_takeover_scorecard or {}).get("weighted_score"),
                "latest_takeover_rollbackable": takeover_rollbackable,
                "latest_replacement_readiness_report_id": (
                    latest_candidate_benchmark.get("replacement_readiness_report_id")
                    or ((replacement_readiness_reports[0] if replacement_readiness_reports else {}).get("report_id"))
                ),
                "latest_fleet_summary_ids": [item.get("summary_id") for item in latest_candidate_benchmark.get("fleet_summaries", []) if item.get("summary_id")],
                "latest_cohort_scorecard_ids": [item.get("cohort_id") for item in latest_candidate_benchmark.get("cohort_scorecards", []) if item.get("cohort_id")],
                "latest_replacement_mode": replacement_mode,
                "latest_replacement_ready": replacement_ready,
                "latest_replacement_external_evaluation_passed": replacement_external_evaluation,
                "latest_replacement_governance_signed_off": replacement_governance,
                "latest_replacement_rollback_ready": replacement_rollback,
                "replacement_modes": sorted(
                    {item.get("replacement_mode") for item in replacement_readiness_reports if item.get("replacement_mode")}
                ),
                "guarded_live_ready": guarded_live_ready,
                "latest_promotion_decision_id": (latest_promotion_decision or {}).get("decision_id"),
                "latest_promotion_decision": (latest_promotion_decision or {}).get("decision"),
                "latest_promotion_governance_decision": (latest_promotion_decision or {}).get("governance_decision"),
                "latest_promotion_evaluator_decision": (latest_promotion_decision or {}).get("evaluator_decision"),
                "latest_native_governed_action": governed_behavior.get("governed_action"),
                "latest_native_governed_action_reason": governed_behavior.get("reason"),
                "latest_native_governed_action_source": governed_behavior.get("source"),
                "latest_native_governed_behavior_state_id": governed_behavior.get("behavior_state_id"),
                "latest_native_governed_decision_id": governed_behavior.get("decision_id"),
                "latest_native_governed_evaluation_id": governed_behavior.get("evaluation_id"),
                "latest_native_alignment_hold_required": governed_behavior.get("alignment_hold_required"),
                "latest_native_alignment_blockers": governed_behavior.get("alignment_blockers", []),
                "latest_native_alignment_max_safe_mode": governed_behavior.get("alignment_max_safe_mode"),
            },
        }

    def _resolve_trace(self, *, trace_id: str | None, session_id: str | None) -> dict[str, Any] | None:
        if trace_id:
            trace = self.store.get_trace(trace_id)
            if trace is not None:
                return trace
        traces = self.store.list_traces(limit=200)
        if session_id:
            for trace in traces:
                if trace.get("session_id") == session_id:
                    return trace
        return traces[0] if traces else None

    def _teacher_bundles(self, *, subject: str | None, teacher_id: str | None) -> list[dict[str, Any]]:
        bundles = self.store.list_teacher_evidence_bundles(limit=200)
        filtered = [
            item
            for item in bundles
            if (
                (subject is not None and item.get("subject") == subject)
                or (teacher_id is not None and teacher_id in (item.get("selected_teachers") or []))
            )
        ]
        return filtered or bundles[:10]

    def _dream_artifacts(self, *, source_trace_id: str | None, session_id: str | None) -> list[dict[str, Any]]:
        dream_dir = self.artifacts_dir / "dreams"
        if not dream_dir.exists():
            return []
        session_trace_ids = {
            trace.get("trace_id")
            for trace in self.store.list_traces(limit=200)
            if session_id and trace.get("session_id") == session_id and trace.get("trace_id")
        }
        payloads: list[dict[str, Any]] = []
        for path in sorted(dream_dir.glob("*.json"), reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            trace_ref = ((payload.get("scenario") or {}).get("source_trace_id"))
            if source_trace_id and trace_ref == source_trace_id:
                payloads.append(payload)
                continue
            if session_trace_ids and trace_ref in session_trace_ids:
                payloads.append(payload)
        return payloads

    def _distillation_lineage(
        self,
        *,
        subject: str | None,
        teacher_id: str | None,
        teacher_bundle_id: str | None,
    ) -> list[dict[str, Any]]:
        lineage_dir = self.artifacts_dir / "foundry" / "lineage"
        if not lineage_dir.exists():
            return []
        payloads: list[dict[str, Any]] = []
        for path in sorted(lineage_dir.glob("*.json"), reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            teacher_evidence = (payload.get("metadata") or {}).get("teacher_evidence") or {}
            if teacher_bundle_id and teacher_evidence.get("bundle_id") == teacher_bundle_id:
                payloads.append(payload)
                continue
            if teacher_id and teacher_id in (teacher_evidence.get("selected_teachers") or []):
                payloads.append(payload)
                continue
            if subject and teacher_evidence.get("subject") == subject:
                payloads.append(payload)
        return payloads

    def _native_takeover_candidates(
        self,
        *,
        subject: str | None,
        teacher_id: str | None,
        teacher_bundle_id: str | None,
        distillation_artifact_id: str | None,
    ) -> list[dict[str, Any]]:
        if self.promotion_service is None:
            return []
        candidates = []
        for candidate in self.promotion_service.list_candidates(candidate_kind="native-takeover", limit=200):
            traceability = candidate.traceability or {}
            teacher_evidence = traceability.get("teacher_evidence", {}) or {}
            distillation_artifact = traceability.get("distillation_artifact", {}) or {}
            if teacher_bundle_id and candidate.teacher_evidence_bundle_id == teacher_bundle_id:
                candidates.append(candidate.model_dump(mode="json"))
                continue
            if distillation_artifact_id and distillation_artifact.get("artifact_id") == distillation_artifact_id:
                candidates.append(candidate.model_dump(mode="json"))
                continue
            if teacher_id and teacher_id in (teacher_evidence.get("selected_teachers") or []):
                candidates.append(candidate.model_dump(mode="json"))
                continue
            if subject and teacher_evidence.get("subject") == subject:
                candidates.append(candidate.model_dump(mode="json"))
        return candidates
