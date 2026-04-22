from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.storage import NexusStore

from ..schemas import TeacherDisagreementArtifact, TeacherEvidenceBundle, TeacherScorecard
from ..teachers.benchmarks import TeacherBenchmarkRegistry
from ..teachers.schema_versions import TeacherSchemaRegistry
from ..teachers.disagreement import build_teacher_disagreement, disagreement_payload
from ..teachers.evidence_bundle import build_teacher_evidence_bundle, evidence_bundle_payload
from ..teachers.scorecards import build_teacher_scorecard


class TeacherEvidenceService:
    def __init__(
        self,
        *,
        store: NexusStore,
        artifacts_dir: Path,
        benchmark_registry: TeacherBenchmarkRegistry,
        schema_registry: TeacherSchemaRegistry,
    ):
        self.store = store
        self.artifacts_dir = artifacts_dir
        self.benchmark_registry = benchmark_registry
        self.schema_registry = schema_registry

    def create_scorecard(
        self,
        *,
        subject: str,
        benchmark_family: str,
        metrics: dict[str, float],
        threshold_set_id: str | None = None,
    ) -> TeacherScorecard:
        threshold_spec = self.benchmark_registry.resolve_threshold_spec(subject, benchmark_family, threshold_set_id)
        scorecard = build_teacher_scorecard(
            subject=subject,
            benchmark_family=benchmark_family,
            metrics=metrics,
            benchmark_registry=self.benchmark_registry,
            threshold_spec=threshold_spec,
        )
        return self.persist_scorecard(scorecard)

    def persist_scorecard(self, scorecard: TeacherScorecard) -> TeacherScorecard:
        scorecard = scorecard.model_copy(update=self.schema_registry.envelope("teacher-scorecard"))
        relative = f"teachers/scorecards/{scorecard.subject}/{scorecard.scorecard_id}.json"
        payload = scorecard.model_dump(mode="json")
        path = self.store.write_artifact(relative, json.dumps(payload, indent=2))
        updated = scorecard.model_copy(update={"artifact_path": path})
        self.store.save_teacher_scorecard(updated.model_dump(mode="json"))
        return updated

    def create_disagreement(
        self,
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
        primary_output: str,
        secondary_output: str,
        threshold_set_id: str | None = None,
        teacher_confidence: float = 0.0,
        lfm2_lane: str | None = None,
        lfm2_bounded_ok: bool = True,
        dream_derived: bool = False,
        live_derived: bool = True,
        native_takeover_candidate_id: str | None = None,
    ) -> TeacherDisagreementArtifact:
        artifact = build_teacher_disagreement(
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
            primary_output=primary_output,
            secondary_output=secondary_output,
            teacher_confidence=teacher_confidence,
            lfm2_lane=lfm2_lane,
            lfm2_bounded_ok=lfm2_bounded_ok,
            dream_derived=dream_derived,
            live_derived=live_derived,
            native_takeover_candidate_id=native_takeover_candidate_id,
        )
        artifact = artifact.model_copy(update=self.schema_registry.envelope("teacher-disagreement-artifact"))
        relative = f"teachers/disagreements/{subject}/{artifact.artifact_id}.json"
        payload = disagreement_payload(artifact, primary_output=primary_output, secondary_output=secondary_output)
        path = self.store.write_artifact(relative, json.dumps(payload, indent=2))
        updated = artifact.model_copy(update={"artifact_path": path, "artifact_refs": {"json": path}})
        self.store.save_teacher_disagreement_artifact(updated.model_dump(mode="json"))
        return updated

    def create_bundle(
        self,
        *,
        subject: str,
        registry_layer: str,
        selected_teacher_roles: dict[str, str],
        arbitration_result: str | None,
        benchmark_families: list[str],
        metrics: dict[str, Any] | None = None,
        disagreement_artifacts: list[TeacherDisagreementArtifact] | None = None,
        scorecards: list[TeacherScorecard] | None = None,
        threshold_set_id: str | None = None,
        native_takeover_candidate_id: str | None = None,
        dream_derived: bool = False,
        live_derived: bool = True,
        lfm2_lane: str | None = None,
        lfm2_bounded_ok: bool = True,
        teacher_confidence: float = 0.0,
        benchmark_family: str | None = None,
    ) -> TeacherEvidenceBundle:
        disagreement_artifacts = disagreement_artifacts or []
        scorecards = scorecards or []
        bundle = build_teacher_evidence_bundle(
            subject=subject,
            registry_layer=registry_layer,
            selected_teacher_roles=selected_teacher_roles,
            arbitration_result=arbitration_result,
            benchmark_families=benchmark_families,
            threshold_set_id=threshold_set_id or (scorecards[0].threshold_set_id if scorecards else None),
            scorecards=scorecards,
            disagreement_artifacts=disagreement_artifacts,
            metrics=metrics or {},
            native_takeover_candidate_id=native_takeover_candidate_id,
            dream_derived=dream_derived,
            live_derived=live_derived,
            lfm2_lane=lfm2_lane,
            lfm2_bounded_ok=lfm2_bounded_ok,
            teacher_confidence=teacher_confidence,
            benchmark_family=benchmark_family,
        )
        bundle = bundle.model_copy(update=self.schema_registry.envelope("teacher-evidence-bundle"))
        payload = evidence_bundle_payload(bundle, disagreement_artifacts=disagreement_artifacts)
        relative = f"teachers/evidence/{subject}/{bundle.bundle_id}.json"
        path = self.store.write_artifact(relative, json.dumps(payload, indent=2))
        updated = bundle.model_copy(update={"artifact_path": path, "artifacts": {"json": path}})
        self.store.save_teacher_evidence_bundle(updated.model_dump(mode="json"))
        return updated

    def score_bundle(
        self,
        *,
        subject: str,
        registry_layer: str,
        selected_teacher_roles: dict[str, str],
        arbitration_result: str | None,
        benchmark_family: str,
        metrics: dict[str, float],
        disagreement_artifacts: list[TeacherDisagreementArtifact] | None = None,
        threshold_set_id: str | None = None,
        native_takeover_candidate_id: str | None = None,
        dream_derived: bool = False,
        live_derived: bool = True,
        lfm2_lane: str | None = None,
        lfm2_bounded_ok: bool = True,
        teacher_confidence: float = 0.0,
    ) -> dict[str, Any]:
        scorecard = self.create_scorecard(
            subject=subject,
            benchmark_family=benchmark_family,
            metrics=metrics,
            threshold_set_id=threshold_set_id,
        )
        bundle = self.create_bundle(
            subject=subject,
            registry_layer=registry_layer,
            selected_teacher_roles=selected_teacher_roles,
            arbitration_result=arbitration_result,
            benchmark_families=[benchmark_family],
            metrics=metrics,
            disagreement_artifacts=disagreement_artifacts,
            scorecards=[scorecard],
            threshold_set_id=scorecard.threshold_set_id,
            native_takeover_candidate_id=native_takeover_candidate_id,
            dream_derived=dream_derived,
            live_derived=live_derived,
            lfm2_lane=lfm2_lane,
            lfm2_bounded_ok=lfm2_bounded_ok,
            teacher_confidence=teacher_confidence,
            benchmark_family=benchmark_family,
        )
        return self.bundle_payload(bundle.bundle_id)

    def bundle_payload(self, bundle_id: str) -> dict[str, Any]:
        payload = self.store.get_teacher_evidence_bundle(bundle_id)
        if payload is None:
            raise KeyError(bundle_id)
        disagreement_artifacts = [
            artifact
            for artifact in self.store.list_teacher_disagreement_artifacts(subject=payload["subject"], limit=500)
            if artifact["artifact_id"] in set(payload.get("disagreement_artifact_ids", []))
        ]
        payload["disagreement_artifacts"] = disagreement_artifacts
        payload["teacher_disagreement_delta"] = payload.get("metrics", {}).get("teacher_disagreement_delta", 0.0)
        payload["lfm2_bounded_ok"] = payload.get("metrics", {}).get("lfm2_bounded_ok", True)
        payload["teacher_confidence"] = payload.get("metrics", {}).get("teacher_confidence", payload.get("teacher_confidence", 0.0))
        payload["trend_scorecards"] = [
            item
            for family in payload.get("benchmark_families", [])
            for item in self.store.list_teacher_trend_scorecards(
                subject=payload["subject"],
                benchmark_family_id=family,
                limit=1,
            )
        ]
        payload["fleet_summaries"] = self.store.list_teacher_benchmark_fleet_summaries(subject=payload["subject"], limit=10)
        payload["cohort_scorecards"] = self.store.list_teacher_cohort_scorecards(subject=payload["subject"], limit=10)
        payload["replacement_readiness_reports"] = self.store.list_replacement_readiness_reports(subject=payload["subject"], limit=10)
        return payload

    def list_bundles(self, *, subject: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        return [self.bundle_payload(item["bundle_id"]) for item in self.store.list_teacher_evidence_bundles(subject=subject, limit=limit)]
