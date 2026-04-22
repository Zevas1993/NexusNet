from __future__ import annotations

from collections import Counter
from typing import Any

from ..schemas import TeacherDisagreementArtifact, TeacherEvidenceBundle, TeacherScorecard


def build_teacher_evidence_bundle(
    *,
    subject: str,
    registry_layer: str,
    selected_teacher_roles: dict[str, str],
    arbitration_result: str | None,
    benchmark_families: list[str],
    threshold_set_id: str | None,
    scorecards: list[TeacherScorecard] | None = None,
    disagreement_artifacts: list[TeacherDisagreementArtifact] | None = None,
    metrics: dict[str, Any] | None = None,
    native_takeover_candidate_id: str | None = None,
    dream_derived: bool = False,
    live_derived: bool = True,
    lfm2_lane: str | None = None,
    lfm2_bounded_ok: bool = True,
    teacher_confidence: float = 0.0,
    benchmark_family: str | None = None,
) -> TeacherEvidenceBundle:
    scorecards = scorecards or []
    disagreement_artifacts = disagreement_artifacts or []
    disagreement_values = [float(artifact.disagreement_severity) for artifact in disagreement_artifacts]
    arbitration_counts = Counter(
        [artifact.arbitration_result for artifact in disagreement_artifacts if artifact.arbitration_result]
    )
    merged_metrics = {
        "teacher_disagreement_delta": round(sum(disagreement_values) / len(disagreement_values), 3) if disagreement_values else 0.0,
        "teacher_confidence": teacher_confidence,
        "dream_derived": dream_derived,
        "live_derived": live_derived,
        "lfm2_bounded_ok": lfm2_bounded_ok,
        "arbitration_result_counts": dict(arbitration_counts),
    }
    if metrics:
        merged_metrics.update(metrics)
    return TeacherEvidenceBundle(
        subject=subject,
        registry_layer=registry_layer,
        selected_teachers=sorted({teacher_id for teacher_id in selected_teacher_roles.values() if teacher_id}),
        selected_teacher_roles={key: value for key, value in selected_teacher_roles.items() if value},
        arbitration_result=arbitration_result,
        benchmark_families=sorted({family for family in benchmark_families if family}),
        benchmark_family=benchmark_family or (benchmark_families[0] if benchmark_families else None),
        threshold_set_id=threshold_set_id,
        threshold_version=scorecards[0].threshold_version if scorecards else None,
        disagreement_artifact_ids=[artifact.artifact_id for artifact in disagreement_artifacts],
        scorecards=scorecards,
        metrics=merged_metrics,
        native_takeover_candidate_id=native_takeover_candidate_id,
        dream_derived=dream_derived,
        live_derived=live_derived,
        lfm2_lane=lfm2_lane,
        lfm2_bounded_ok=lfm2_bounded_ok,
        teacher_confidence=teacher_confidence,
    )


def evidence_bundle_payload(
    bundle: TeacherEvidenceBundle,
    *,
    disagreement_artifacts: list[TeacherDisagreementArtifact] | None = None,
) -> dict[str, Any]:
    disagreement_artifacts = disagreement_artifacts or []
    payload = bundle.model_dump(mode="json")
    payload["disagreement_artifacts"] = [artifact.model_dump(mode="json") for artifact in disagreement_artifacts]
    payload["teacher_disagreement_delta"] = payload["metrics"].get("teacher_disagreement_delta", 0.0)
    payload["dependency_ratio"] = payload["metrics"].get("dependency_ratio")
    payload["native_generation"] = payload["metrics"].get("native_generation")
    payload["takeover_readiness"] = payload["metrics"].get("takeover_readiness")
    payload["teacher_replacement_candidate"] = payload["metrics"].get("teacher_replacement_candidate")
    payload["takeover_rollbackability"] = payload["metrics"].get("takeover_rollbackability")
    payload["lfm2_bounded_ok"] = payload.get("lfm2_bounded_ok", payload["metrics"].get("lfm2_bounded_ok", True))
    return payload
