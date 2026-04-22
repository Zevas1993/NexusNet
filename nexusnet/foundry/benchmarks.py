from __future__ import annotations

import json
from pathlib import Path

from nexus.storage import NexusStore

from ..schemas import DistillationArtifactRecord, IndependenceMetrics
from ..teachers.schema_versions import TeacherSchemaRegistry
from .takeover_trends import TakeoverTrendAnalyzer
from .takeover_scorecard import TakeoverScorecardBuilder
from .teacher_delta import TeacherDeltaAnalyzer


class FoundryBenchmarkSuite:
    def __init__(
        self,
        *,
        store: NexusStore | None = None,
        artifacts_dir: Path | None = None,
        schema_registry: TeacherSchemaRegistry | None = None,
        cohort_takeover: object | None = None,
        replacement_readiness: object | None = None,
    ):
        self.store = store
        self.artifacts_dir = artifacts_dir
        self.schema_registry = schema_registry
        self.cohort_takeover = cohort_takeover
        self.replacement_readiness = replacement_readiness
        self._delta = TeacherDeltaAnalyzer()
        self._scorecards = TakeoverScorecardBuilder()
        self._trends = TakeoverTrendAnalyzer(store=store, artifacts_dir=artifacts_dir, schema_registry=schema_registry) if store is not None and artifacts_dir is not None and schema_registry is not None else None

    def evaluate(self, *, artifact: DistillationArtifactRecord, independence: IndependenceMetrics | None = None) -> dict:
        independence = independence or IndependenceMetrics()
        teacher_evidence = dict(artifact.metadata.get("teacher_evidence", {}))
        dependency_ratio = independence.dependency_ratio
        native_generation = independence.native_generation
        disagreement_delta = float(teacher_evidence.get("teacher_disagreement_delta", 0.0) or 0.0)
        takeover_readiness = round(
            max(
                0.0,
                min(
                    1.0,
                    (native_generation + (1.0 - dependency_ratio) + (1.0 - min(disagreement_delta, 1.0))) / 3.0,
                ),
            ),
            3,
        )
        takeover_rollbackability = True
        deltas = self._delta.compare(
            teacher_evidence=teacher_evidence,
            dependency_ratio=dependency_ratio,
            native_generation=native_generation,
        )
        scorecard = self._scorecards.build(
            subject=str(teacher_evidence.get("subject") or artifact.name),
            teacher_evidence_bundle_id=teacher_evidence.get("bundle_id"),
            metrics={
                "dependency_ratio": dependency_ratio,
                "native_generation": native_generation,
                "takeover_readiness": takeover_readiness,
                "teacher_disagreement_delta": disagreement_delta,
                "takeover_rollbackability": 1.0 if takeover_rollbackability else 0.0,
            },
            deltas=deltas,
        )
        if self.schema_registry is not None:
            scorecard = scorecard.model_copy(update=self.schema_registry.envelope("takeover-scorecard"))
        if self.store is not None:
            payload = scorecard.model_dump(mode="json")
            if self.artifacts_dir is not None:
                relative = f"foundry/takeover-scorecards/{scorecard.subject}/{scorecard.scorecard_id}.json"
                path = self.store.write_artifact(relative, json.dumps(payload, indent=2))
                scorecard = scorecard.model_copy(update={"artifact_path": path})
                payload = scorecard.model_dump(mode="json")
            self.store.save_takeover_scorecard(payload)
        trend_report = (
            self._trends.build(
                subject=scorecard.subject,
                threshold_set_id=scorecard.threshold_set_id,
                threshold_version=scorecard.threshold_version,
            )
            if self._trends is not None
            else None
        )
        cohort_governance = (
            self.cohort_takeover.evaluate(
                subject=scorecard.subject,
                teacher_evidence=teacher_evidence,
                benchmark_summary={
                    "takeover_scorecard_id": scorecard.scorecard_id,
                    "takeover_trend_report_id": trend_report.trend_id if trend_report is not None else None,
                },
            )
            if self.cohort_takeover is not None
            else {"fleet_summaries": [], "cohort_scorecards": [], "cohort_gate_ready": False}
        )
        replacement_readiness = (
            self.replacement_readiness.decide(
                subject=scorecard.subject,
                teacher_id=(teacher_evidence.get("selected_teacher_roles") or {}).get("primary", "unknown-teacher"),
                threshold_set_id=scorecard.threshold_set_id,
                threshold_version=scorecard.threshold_version,
                subject_trend_ready=bool(trend_report and trend_report.ready),
                fleet_gate_ready=all(item.get("ready") for item in cohort_governance.get("fleet_summaries", []))
                if cohort_governance.get("fleet_summaries")
                else False,
                cohort_gate_ready=all(item.get("ready") for item in cohort_governance.get("cohort_scorecards", []))
                if cohort_governance.get("cohort_scorecards")
                else False,
                external_evaluation_passed=False,
                rollback_ready=takeover_rollbackability,
                governance_signed_off=False,
                metrics={
                    "dependency_ratio_trend": trend_report.dependency_ratio_trend if trend_report is not None else 0.0,
                    "native_generation_trend": trend_report.native_generation_trend if trend_report is not None else 0.0,
                    "teacher_disagreement_delta_trend": trend_report.teacher_disagreement_delta_trend if trend_report is not None else 0.0,
                },
                evidence_refs={
                    "takeover_scorecard_id": scorecard.scorecard_id,
                    "takeover_trend_report_id": trend_report.trend_id if trend_report is not None else None,
                    "fleet_summary_ids": [item.get("summary_id") for item in cohort_governance.get("fleet_summaries", [])],
                    "cohort_scorecard_ids": [item.get("cohort_id") for item in cohort_governance.get("cohort_scorecards", [])],
                },
            )
            if self.replacement_readiness is not None
            else None
        )
        if replacement_readiness is not None and self.schema_registry is not None:
            replacement_readiness = replacement_readiness.model_copy(update=self.schema_registry.envelope("replacement-readiness-report"))
        if replacement_readiness is not None and self.store is not None:
            payload = replacement_readiness.model_dump(mode="json")
            if self.artifacts_dir is not None:
                relative = f"foundry/replacement-readiness/{scorecard.subject}/{replacement_readiness.report_id}.json"
                path = self.store.write_artifact(relative, json.dumps(payload, indent=2))
                replacement_readiness = replacement_readiness.model_copy(update={"artifact_path": path})
                payload = replacement_readiness.model_dump(mode="json")
            self.store.save_replacement_readiness_report(payload)
        return {
            "status_label": "LOCKED CANON",
            "sample_count": artifact.sample_count,
            "dependency_ratio": dependency_ratio,
            "native_generation": native_generation,
            "teacher_replacement_ready": independence.teacher_replacement_ready,
            "teacher_disagreement_delta": disagreement_delta,
            "teacher_replacement_candidate": teacher_evidence.get("teacher_replacement_candidate"),
            "takeover_readiness": takeover_readiness,
            "takeover_rollbackability": takeover_rollbackability,
            "native_vs_primary_delta": deltas["native_vs_primary_delta"],
            "native_vs_secondary_delta": deltas["native_vs_secondary_delta"],
            "native_vs_arbitration_delta": deltas["native_vs_arbitration_delta"],
            "native_vs_historical_baseline_delta": deltas["native_vs_historical_baseline_delta"],
            "native_vs_wrapper_slices": {
                "native_generation": native_generation,
                "dependency_ratio": dependency_ratio,
                "teacher_disagreement_delta": disagreement_delta,
                "sample_count": artifact.sample_count,
            },
            "teacher_evidence": teacher_evidence,
            "teacher_evidence_bundle_id": teacher_evidence.get("bundle_id"),
            "threshold_set_id": scorecard.threshold_set_id,
            "takeover_scorecard_id": scorecard.scorecard_id,
            "takeover_scorecard": scorecard.model_dump(mode="json"),
            "takeover_trend_report_id": trend_report.trend_id if trend_report is not None else None,
            "takeover_trend_report": trend_report.model_dump(mode="json") if trend_report is not None else None,
            "fleet_summaries": cohort_governance.get("fleet_summaries", []),
            "cohort_scorecards": cohort_governance.get("cohort_scorecards", []),
            "cohort_gate_ready": cohort_governance.get("cohort_gate_ready", False),
            "replacement_readiness_report_id": replacement_readiness.report_id if replacement_readiness is not None else None,
            "replacement_readiness": replacement_readiness.model_dump(mode="json") if replacement_readiness is not None else None,
            "wrapper_to_native_score": round((artifact.sample_count / 1000.0) + native_generation + takeover_readiness, 3),
        }
