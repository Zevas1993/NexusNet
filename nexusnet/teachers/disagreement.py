from __future__ import annotations

from typing import Any

from ..schemas import TeacherDisagreementArtifact


def build_teacher_disagreement(
    *,
    subject: str,
    registry_layer: str,
    primary_teacher_id: str,
    secondary_teacher_id: str | None,
    critique_teacher_id: str | None,
    efficiency_teacher_id: str | None,
    arbitration_result: str,
    rationale: str,
    benchmark_family: str | None,
    threshold_set_id: str | None,
    primary_output: str,
    secondary_output: str,
    teacher_confidence: float = 0.0,
    lfm2_lane: str | None = None,
    lfm2_bounded_ok: bool = True,
    dream_derived: bool = False,
    live_derived: bool = True,
    native_takeover_candidate_id: str | None = None,
) -> TeacherDisagreementArtifact:
    severity = _disagreement_delta(primary_output=primary_output, secondary_output=secondary_output)
    return TeacherDisagreementArtifact(
        subject=subject,
        registry_layer=registry_layer,
        primary_teacher_id=primary_teacher_id,
        secondary_teacher_id=secondary_teacher_id,
        critique_teacher_id=critique_teacher_id,
        efficiency_teacher_id=efficiency_teacher_id,
        arbitration_result=arbitration_result,
        rationale=rationale,
        benchmark_family=benchmark_family,
        threshold_set_id=threshold_set_id,
        dream_derived=dream_derived,
        live_derived=live_derived,
        disagreement_severity=severity,
        teacher_confidence=teacher_confidence,
        native_takeover_candidate_id=native_takeover_candidate_id,
        lfm2_lane=lfm2_lane,
        lfm2_bounded_ok=lfm2_bounded_ok,
        metrics={
            "disagreement_delta": severity,
            "correctness": 1.0 if primary_output.strip() and secondary_output.strip() else 0.0,
            "structured_output_conformance": 1.0 if arbitration_result else 0.0,
        },
    )


def disagreement_payload(artifact: TeacherDisagreementArtifact, *, primary_output: str, secondary_output: str) -> dict[str, Any]:
    payload = artifact.model_dump(mode="json")
    payload["primary_output_preview"] = primary_output[:240]
    payload["secondary_output_preview"] = secondary_output[:240]
    payload["disagreement_delta"] = artifact.disagreement_severity
    return payload


def _disagreement_delta(*, primary_output: str, secondary_output: str) -> float:
    primary_tokens = set(primary_output.lower().split())
    secondary_tokens = set(secondary_output.lower().split())
    if not primary_tokens and not secondary_tokens:
        return 0.0
    overlap = len(primary_tokens & secondary_tokens)
    union = max(len(primary_tokens | secondary_tokens), 1)
    return round(1.0 - (overlap / union), 3)
