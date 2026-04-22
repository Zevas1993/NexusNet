from __future__ import annotations

from collections import Counter
from typing import Any

from ..schemas import TeacherDisagreementArtifact, TeacherEvidenceBundle, TeacherScorecard
from .disagreement import build_teacher_disagreement, disagreement_payload
from .evidence_bundle import build_teacher_evidence_bundle, evidence_bundle_payload


def disagreement_delta(*, primary_output: str, secondary_output: str) -> float:
    primary_tokens = set(primary_output.lower().split())
    secondary_tokens = set(secondary_output.lower().split())
    if not primary_tokens and not secondary_tokens:
        return 0.0
    overlap = len(primary_tokens & secondary_tokens)
    union = max(len(primary_tokens | secondary_tokens), 1)
    return round(1.0 - (overlap / union), 3)


def build_disagreement_artifact(
    *,
    subject: str,
    registry_layer: str,
    primary_teacher_id: str,
    secondary_teacher_id: str | None,
    critique_teacher_id: str | None,
    efficiency_teacher_id: str | None,
    primary_output: str,
    secondary_output: str,
    arbitration_result: str,
    benchmark_family: str | None,
    dream_derived: bool,
    live_derived: bool,
    native_takeover_candidate_id: str | None = None,
    threshold_set_id: str | None = None,
    rationale: str | None = None,
    teacher_confidence: float = 0.0,
    lfm2_lane: str | None = None,
    lfm2_bounded_ok: bool = True,
) -> dict[str, Any]:
    artifact = build_teacher_disagreement(
        subject=subject,
        registry_layer=registry_layer,
        primary_teacher_id=primary_teacher_id,
        secondary_teacher_id=secondary_teacher_id,
        critique_teacher_id=critique_teacher_id,
        efficiency_teacher_id=efficiency_teacher_id,
        arbitration_result=arbitration_result,
        rationale=rationale or "Teacher disagreement captured for curriculum/foundry/promotion review.",
        benchmark_family=benchmark_family,
        threshold_set_id=threshold_set_id,
        primary_output=primary_output,
        secondary_output=secondary_output,
        teacher_confidence=teacher_confidence,
        lfm2_lane=lfm2_lane,
        lfm2_bounded_ok=lfm2_bounded_ok,
        dream_derived=dream_derived,
        live_derived=live_derived,
        native_takeover_candidate_id=native_takeover_candidate_id,
    )
    return disagreement_payload(artifact, primary_output=primary_output, secondary_output=secondary_output)


def build_teacher_evidence(
    *,
    subject: str,
    registry_layer: str,
    selected_roles: dict[str, str],
    arbitration_result: str,
    benchmark_family: str | None,
    lineage: str,
    disagreement_artifacts: list[dict[str, Any]] | None = None,
    native_takeover_candidate_id: str | None = None,
    dependency_ratio: float | None = None,
    native_generation: float | None = None,
    takeover_readiness: float | None = None,
    teacher_replacement_candidate: dict[str, Any] | str | None = None,
    takeover_rollbackability: bool | None = None,
    lfm2_bounded_ok: bool = True,
    threshold_set_id: str | None = None,
    scorecards: list[dict[str, Any]] | None = None,
    teacher_confidence: float = 0.0,
    lfm2_lane: str | None = None,
) -> dict[str, Any]:
    disagreement_artifacts = disagreement_artifacts or []
    scorecard_models = [TeacherScorecard.model_validate(item) for item in (scorecards or [])]
    disagreement_models = [TeacherDisagreementArtifact.model_validate(item) for item in disagreement_artifacts]
    bundle = build_teacher_evidence_bundle(
        subject=subject,
        registry_layer=registry_layer,
        selected_teacher_roles=selected_roles,
        arbitration_result=arbitration_result,
        benchmark_families=[benchmark_family] if benchmark_family else [],
        threshold_set_id=threshold_set_id,
        scorecards=scorecard_models,
        disagreement_artifacts=disagreement_models,
        metrics={
            "dependency_ratio": dependency_ratio,
            "native_generation": native_generation,
            "takeover_readiness": takeover_readiness,
            "teacher_replacement_candidate": teacher_replacement_candidate,
            "takeover_rollbackability": takeover_rollbackability,
            "lfm2_bounded_ok": lfm2_bounded_ok,
            "teacher_confidence": teacher_confidence,
        },
        native_takeover_candidate_id=native_takeover_candidate_id,
        dream_derived=lineage == "dream-derived",
        live_derived=lineage == "live-derived",
        lfm2_lane=lfm2_lane,
        lfm2_bounded_ok=lfm2_bounded_ok,
        teacher_confidence=teacher_confidence,
        benchmark_family=benchmark_family,
    )
    return evidence_bundle_payload(bundle, disagreement_artifacts=disagreement_models)


def aggregate_teacher_evidence(
    *,
    traces: list[dict[str, Any]],
    curriculum_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    curriculum_records = curriculum_records or []
    selected_teachers: set[str] = set()
    benchmark_families: set[str] = set()
    registry_layers: set[str] = set()
    disagreement_artifacts: list[dict[str, Any]] = []
    arbitration_results: Counter[str] = Counter()
    scorecards: list[dict[str, Any]] = []
    scorecard_ids: set[str] = set()
    bundle_ids: set[str] = set()
    dream_derived = False
    live_derived = False
    native_takeover_ids: set[str] = set()
    lfm2_bounded_ok = True
    threshold_set_id: str | None = None

    for trace in traces:
        provenance = trace.get("teacher_provenance") or {}
        if not provenance:
            continue
        registry_layer = provenance.get("registry_layer")
        if registry_layer:
            registry_layers.add(registry_layer)
        selected_teachers.update(provenance.get("selected_teachers") or [])
        benchmark_family = provenance.get("benchmark_family")
        if benchmark_family:
            benchmark_families.add(benchmark_family)
        arbitration_result = provenance.get("arbitration_result")
        if arbitration_result:
            arbitration_results[arbitration_result] += 1
        dream_derived = dream_derived or bool(provenance.get("dream_derived"))
        live_derived = live_derived or bool(provenance.get("live_derived"))
        candidate_id = provenance.get("native_takeover_candidate_id")
        if candidate_id:
            native_takeover_ids.add(candidate_id)
        selected_roles = provenance.get("selected_teacher_roles") or {}
        subject = (provenance.get("routing_decision") or {}).get("subject") or trace.get("selected_expert") or "unknown"
        efficiency_teacher_id = selected_roles.get("efficiency")
        if efficiency_teacher_id:
            allowed_subjects = {"router", "toolsmith", "memory-weaver", "security", "curriculum-architect"}
            if subject not in allowed_subjects:
                lfm2_bounded_ok = False
        if len(selected_roles) > 1 or arbitration_result != "SELECT_BEST":
            disagreement_artifacts.append(
                {
                    "trace_id": trace.get("trace_id"),
                    "session_id": trace.get("session_id"),
                    "subject": subject,
                    "registry_layer": registry_layer,
                    "selected_teacher_roles": selected_roles,
                    "arbitration_result": arbitration_result,
                    "benchmark_family": benchmark_family,
                    "dream_derived": provenance.get("dream_derived", False),
                    "live_derived": provenance.get("live_derived", False),
                    "native_takeover_candidate_id": candidate_id,
                    "teacher_confidence": provenance.get("teacher_confidence"),
                }
            )

    for record in curriculum_records:
        detail = record.get("detail") or {}
        teacher_flow = detail.get("teacher_flow") or {}
        selected_teachers.update(teacher_flow.get("selected_teachers") or [])
        benchmark_families.update(teacher_flow.get("benchmark_families") or detail.get("benchmark_families") or [])
        if teacher_flow.get("benchmark_family"):
            benchmark_families.add(teacher_flow["benchmark_family"])
        disagreement_artifacts.extend(teacher_flow.get("disagreement_artifacts") or [])
        if teacher_flow.get("registry_layer"):
            registry_layers.add(teacher_flow["registry_layer"])
        arbitration_results.update(teacher_flow.get("arbitration_result_counts") or {})
        if teacher_flow.get("arbitration_result"):
            arbitration_results[teacher_flow["arbitration_result"]] += 1
        dream_derived = dream_derived or bool(teacher_flow.get("dream_derived"))
        live_derived = live_derived or bool(teacher_flow.get("live_derived"))
        if teacher_flow.get("bundle_id"):
            bundle_ids.add(teacher_flow["bundle_id"])
        if teacher_flow.get("threshold_set_id") and threshold_set_id is None:
            threshold_set_id = teacher_flow.get("threshold_set_id")
        for scorecard in teacher_flow.get("scorecards") or []:
            scorecard_id = scorecard.get("scorecard_id")
            if scorecard_id and scorecard_id in scorecard_ids:
                continue
            if scorecard_id:
                scorecard_ids.add(scorecard_id)
            scorecards.append(scorecard)
        native_takeover_candidate_id = teacher_flow.get("native_takeover_candidate_id")
        if native_takeover_candidate_id:
            native_takeover_ids.add(native_takeover_candidate_id)
        lfm2_bounded_ok = lfm2_bounded_ok and bool(teacher_flow.get("lfm2_bounded_ok", True))

    replacement_candidate = None
    if disagreement_artifacts:
        latest = disagreement_artifacts[-1]
        replacement_candidate = (
            (latest.get("selected_teacher_roles") or {}).get("primary")
            or latest.get("primary_teacher_id")
        )
    disagreement_values = [
        float(artifact.get("disagreement_delta", artifact.get("disagreement_severity", 0.0)) or 0.0)
        for artifact in disagreement_artifacts
        if artifact.get("disagreement_delta") is not None or artifact.get("disagreement_severity") is not None
    ]
    return {
        "selected_teachers": sorted(selected_teachers),
        "registry_layers": sorted(registry_layers),
        "benchmark_families": sorted(benchmark_families),
        "arbitration_result_counts": dict(arbitration_results),
        "disagreement_artifacts": disagreement_artifacts,
        "disagreement_artifact_ids": [artifact.get("artifact_id") for artifact in disagreement_artifacts if artifact.get("artifact_id")],
        "teacher_disagreement_delta": round(sum(disagreement_values) / len(disagreement_values), 3) if disagreement_values else 0.0,
        "dream_derived": dream_derived,
        "live_derived": live_derived,
        "native_takeover_candidate_ids": sorted(native_takeover_ids),
        "teacher_replacement_candidate": replacement_candidate,
        "lfm2_bounded_ok": lfm2_bounded_ok,
        "scorecards": scorecards,
        "scorecard_ids": sorted(scorecard_ids),
        "bundle_ids": sorted(bundle_ids),
        "threshold_set_id": threshold_set_id,
    }
