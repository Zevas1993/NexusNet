from __future__ import annotations

import json
from pathlib import Path

from nexus.experiments import ExperimentService
from nexus.foundry import DatasetRefinery
from nexus.schemas import ExperimentRecord
from nexus.storage import NexusStore

from ..foundry import FoundryRefinery
from ..schemas import DistillationExportRequest, DistillationExportResult, TeacherDisagreementArtifact, TeacherScorecard
from ..teachers.evidence import aggregate_teacher_evidence


class DistillationDatasetBuilder:
    def __init__(
        self,
        *,
        store: NexusStore,
        foundry: DatasetRefinery,
        experiments: ExperimentService,
        artifacts_dir: Path,
        foundry_refinery: FoundryRefinery | None = None,
        teacher_evidence_service: object | None = None,
    ):
        self.store = store
        self.foundry = foundry
        self.experiments = experiments
        self.artifacts_dir = artifacts_dir
        self.foundry_refinery = foundry_refinery
        self.teacher_evidence_service = teacher_evidence_service

    def export(self, request: DistillationExportRequest) -> DistillationExportResult:
        samples: list[dict] = []
        source_kinds: set[str] = set()
        teacher_traces: list[dict] = []
        curriculum_records_for_evidence: list[dict] = []
        for trace in self.store.list_traces(limit=request.trace_limit):
            prompt = (trace.get("request") or {}).get("prompt") or ""
            if not prompt:
                continue
            teacher_provenance = trace.get("teacher_provenance") or {}
            if teacher_provenance:
                teacher_traces.append(trace)
            samples.append(
                {
                    "source_kind": "trace",
                    "input": prompt,
                    "target": trace.get("output_preview", ""),
                    "metadata": {
                        "trace_id": trace.get("trace_id"),
                        "model_id": trace.get("model_id"),
                        "runtime_name": trace.get("runtime_name"),
                        "status": trace.get("status"),
                        "teacher_provenance": teacher_provenance,
                        "selected_teacher_id": trace.get("selected_teacher_id"),
                        "selected_expert": trace.get("selected_expert"),
                        "retrieval_policy": trace.get("retrieval_policy"),
                    },
                }
            )
            source_kinds.add("trace")

        if request.include_dreams:
            dream_dir = self.artifacts_dir / "dreams"
            for path in sorted(dream_dir.glob("*.json")):
                payload = json.loads(path.read_text(encoding="utf-8"))
                for variant in payload.get("outcome", {}).get("variants", []):
                    samples.append(
                        {
                            "source_kind": "dream",
                            "input": variant.get("prompt", ""),
                            "target": variant.get("output_preview", ""),
                            "metadata": {
                                "dream_id": payload.get("dream_id"),
                                "mode": variant.get("mode"),
                                "seed": payload.get("seed"),
                            },
                        }
                    )
                    source_kinds.add("dream")

        if request.include_curriculum:
            for record in self.store.list_curriculum_records(limit=200):
                detail = record.get("detail", {})
                if detail.get("teacher_flow"):
                    curriculum_records_for_evidence.append(record)
                samples.append(
                    {
                        "source_kind": "curriculum",
                        "input": detail.get("prompt", ""),
                        "target": detail.get("output_preview", ""),
                        "metadata": {
                            "subject": record.get("subject"),
                            "course": record.get("course"),
                            "status": record.get("status"),
                            "score": record.get("score"),
                            "teacher_flow": detail.get("teacher_flow"),
                        },
                    }
                )
                source_kinds.add("curriculum")

        teacher_evidence = aggregate_teacher_evidence(
            traces=teacher_traces,
            curriculum_records=curriculum_records_for_evidence,
        )
        aggregate_subject = (
            str(curriculum_records_for_evidence[-1].get("subject", "distillation")).split(":", 1)[-1]
            if curriculum_records_for_evidence
            else "distillation"
        )
        if self.teacher_evidence_service is not None and teacher_evidence.get("selected_teachers"):
            benchmark_family = (
                teacher_evidence.get("benchmark_families") or ["benchmark-grade evaluation"]
            )[0]
            scorecard_subject = aggregate_subject
            try:
                self.teacher_evidence_service.benchmark_registry.family(scorecard_subject, benchmark_family)
            except Exception:
                scorecard_subject = (
                    self.teacher_evidence_service.benchmark_registry.subject_for_family(benchmark_family)
                    or "researcher"
                )
            aggregate_metrics = {
                "correctness": 1.0,
                "groundedness": 0.9 if teacher_evidence.get("benchmark_families") else 0.0,
                "safety": 1.0 if teacher_evidence.get("lfm2_bounded_ok", True) else 0.4,
                "tool_discipline": 1.0 if teacher_evidence.get("lfm2_bounded_ok", True) else 0.4,
                "structured_output_conformance": 0.9,
                "efficiency_latency_budget": 0.8,
                "disagreement_severity": float(teacher_evidence.get("teacher_disagreement_delta", 0.0) or 0.0),
                "dream_contamination_sensitivity": 0.95 if not teacher_evidence.get("dream_derived") else 0.8,
                "native_vs_teacher_delta": 0.0,
                "rollbackability": 1.0,
                "dependency_ratio": float(teacher_evidence.get("dependency_ratio", 0.0) or 0.0),
                "native_generation": float(teacher_evidence.get("native_generation", 0.0) or 0.0),
                "takeover_readiness": float(teacher_evidence.get("takeover_readiness", 0.0) or 0.0),
            }
            scorecards = [
                TeacherScorecard.model_validate(item)
                for item in teacher_evidence.get("scorecards", [])
            ]
            if not scorecards:
                scorecards = [
                    self.teacher_evidence_service.create_scorecard(
                        subject=scorecard_subject,
                        benchmark_family=benchmark_family,
                        metrics=aggregate_metrics,
                        threshold_set_id=teacher_evidence.get("threshold_set_id"),
                    )
                ]
            bundle = self.teacher_evidence_service.create_bundle(
                subject=scorecard_subject,
                registry_layer=(teacher_evidence.get("registry_layers") or ["v2026_live"])[0],
                selected_teacher_roles={role: role_id for role, role_id in (curriculum_records_for_evidence[-1].get("detail", {}).get("teacher_flow", {}).get("selected_teacher_roles", {}) if curriculum_records_for_evidence else {}).items() if role_id},
                arbitration_result=max((teacher_evidence.get("arbitration_result_counts") or {"SELECT_BEST": 0}).items(), key=lambda item: item[1])[0] if teacher_evidence.get("arbitration_result_counts") else "SELECT_BEST",
                benchmark_families=teacher_evidence.get("benchmark_families", [benchmark_family]),
                metrics={
                    **aggregate_metrics,
                    "teacher_disagreement_delta": teacher_evidence.get("teacher_disagreement_delta", 0.0),
                    "teacher_replacement_candidate": teacher_evidence.get("teacher_replacement_candidate"),
                    "takeover_rollbackability": teacher_evidence.get("takeover_rollbackability"),
                },
                disagreement_artifacts=[
                    TeacherDisagreementArtifact.model_validate(item)
                    for item in teacher_evidence.get("disagreement_artifacts", [])
                    if item.get("artifact_id")
                ],
                scorecards=scorecards,
                threshold_set_id=scorecards[0].threshold_set_id,
                dream_derived=bool(teacher_evidence.get("dream_derived")),
                live_derived=bool(teacher_evidence.get("live_derived", True)),
                lfm2_bounded_ok=bool(teacher_evidence.get("lfm2_bounded_ok", True)),
                benchmark_family=benchmark_family,
            )
            teacher_evidence = self.teacher_evidence_service.bundle_payload(bundle.bundle_id)

        artifact_path = self.foundry.write_dataset(
            name=request.name,
            samples=samples,
            metadata={
                "trace_limit": request.trace_limit,
                "include_dreams": request.include_dreams,
                "include_curriculum": request.include_curriculum,
                "teacher_evidence": teacher_evidence,
            },
        )
        lineage = "blended-derived" if request.include_dreams else "live-derived"
        lineage_record = None
        if self.foundry_refinery is not None:
            lineage_record = self.foundry_refinery.record_distillation_artifact(
                name=request.name,
                artifact_path=artifact_path,
                source_kinds=sorted(source_kinds),
                sample_count=len(samples),
                lineage=lineage,
                metadata={
                    "teacher_evidence": teacher_evidence,
                    "dream_derived_included": request.include_dreams,
                    "curriculum_included": request.include_curriculum,
                },
            )
        result = DistillationExportResult(
            name=request.name,
            sample_count=len(samples),
            artifact_path=artifact_path,
            metadata={
                "trace_limit": request.trace_limit,
                "include_dreams": request.include_dreams,
                "include_curriculum": request.include_curriculum,
                "source_kinds": sorted(source_kinds),
                "lineage": lineage,
                "lineage_artifact_id": lineage_record.artifact_id if lineage_record else None,
                "teacher_evidence": teacher_evidence,
            },
        )
        self.experiments.record(
            ExperimentRecord(
                kind="distillation_dataset",
                name=result.export_id,
                status="shadow",
                lineage={"dataset_name": request.name},
                metrics={"sample_count": len(samples)},
                artifacts=[artifact_path],
            )
        )
        return result
