from __future__ import annotations

from ..schemas import CapabilityTakeoverRecord, DistillationArtifactRecord, TeacherReplacementDecision


def foundry_provenance_payload(*, artifact: DistillationArtifactRecord, teacher_decisions: list[TeacherReplacementDecision]) -> dict:
    return {
        "artifact": artifact.model_dump(mode="json"),
        "teacher_replacements": [decision.model_dump(mode="json") for decision in teacher_decisions],
        "teacher_evidence": artifact.metadata.get("teacher_evidence", {}),
        "teacher_evidence_bundle_id": (artifact.metadata.get("teacher_evidence", {}) or {}).get("bundle_id"),
    }


def capability_takeover_record(
    *,
    subject: str,
    teacher_id: str,
    internal_target: str,
    rationale: str,
    evidence: dict | None = None,
) -> CapabilityTakeoverRecord:
    return CapabilityTakeoverRecord(
        subject=subject,
        teacher_id=teacher_id,
        internal_target=internal_target,
        decision="shadow",
        rationale=rationale,
        evidence=evidence or {},
        teacher_evidence_bundle_id=(evidence or {}).get("teacher_evidence", {}).get("bundle_id"),
        threshold_set_id=(evidence or {}).get("benchmark_summary", {}).get("threshold_set_id"),
        takeover_scorecard_id=(evidence or {}).get("benchmark_summary", {}).get("takeover_scorecard_id"),
        takeover_trend_report_id=(evidence or {}).get("benchmark_summary", {}).get("takeover_trend_report_id"),
        fleet_summary_ids=[item.get("summary_id") for item in (evidence or {}).get("benchmark_summary", {}).get("fleet_summaries", [])],
        cohort_scorecard_ids=[item.get("cohort_id") for item in (evidence or {}).get("benchmark_summary", {}).get("cohort_scorecards", [])],
        replacement_readiness_report_id=(evidence or {}).get("benchmark_summary", {}).get("replacement_readiness_report_id"),
    )
