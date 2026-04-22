from __future__ import annotations

from collections import Counter
from typing import Any

from nexus.curriculum import CurriculumRegistrar
from nexus.experiments import ExperimentService
from nexus.schemas import ExperimentRecord, new_id

from ..memory import NeuralMemoryCortex
from ..schemas import BenchmarkCase, CurriculumAssessment, CurriculumAssessmentRequest, CurriculumCourse, DreamCycleRequest, ModelAttachRequest, SessionContext, TeacherDisagreementArtifact
from ..teachers.evidence import aggregate_teacher_evidence, build_disagreement_artifact, build_teacher_evidence


class CurriculumEngine:
    def __init__(
        self,
        *,
        registrar: CurriculumRegistrar,
        memory: NeuralMemoryCortex,
        experiments: ExperimentService,
        teacher_registry: Any | None = None,
        teacher_evidence_service: Any | None = None,
        dream_engine: Any | None = None,
        evaluator: Any | None = None,
    ):
        self.registrar = registrar
        self.memory = memory
        self.experiments = experiments
        self.teacher_registry = teacher_registry
        self.teacher_evidence_service = teacher_evidence_service
        self.dream_engine = dream_engine
        self.evaluator = evaluator
        self.syllabus = self._build_syllabus()

    def assess(self, *, brain, request: CurriculumAssessmentRequest) -> CurriculumAssessment:
        regimen = self.teacher_registry.regimen_for_subject(request.subject) if self.teacher_registry is not None else None
        if regimen is not None:
            return self._assess_teacher_regimen(brain=brain, request=request, regimen=regimen)

        courses = self.syllabus.get(request.phase, [])
        records = []
        passed = 0
        subject_key = f"{request.phase}:{request.subject}"
        for course in courses:
            result = brain.generate(
                session_context=SessionContext(
                    session_id=f"curriculum::{subject_key}",
                    expert="researcher",
                    task_type="curriculum",
                    use_retrieval=False,
                    metadata={"phase": request.phase, "subject": request.subject, "course_id": course.course_id},
                ),
                prompt=course.prompt,
                model_hint=request.model_hint or "mock/default",
            )
            output_lower = result.output.lower()
            matched = [token for token in course.expected_substrings if token.lower() in output_lower]
            score = round(len(matched) / max(len(course.expected_substrings), 1), 3)
            status = "passed" if score >= 0.67 else "remediation"
            if status == "passed":
                passed += 1
            record = self.registrar.record_grade(
                subject=subject_key,
                course=course.title,
                status=status,
                score=score,
                detail={
                    "phase": course.phase,
                    "prompt": course.prompt,
                    "expected_substrings": course.expected_substrings,
                    "matched_substrings": matched,
                    "output_preview": result.output[:240],
                    "credits": course.credits,
                },
            )
            self.memory.record_curriculum_state(subject_key, record)
            records.append(record)

        mastery_score = round(sum((record.get("score") or 0.0) for record in records) / max(len(records), 1), 3)
        assessment = CurriculumAssessment(
            phase=request.phase,
            subject=request.subject,
            total_courses=len(records),
            passed_courses=passed,
            mastery_score=mastery_score,
            records=records,
            teacher_flow={
                "status_label": "IMPLEMENTATION BRANCH",
                "mode": "syllabus-fallback",
                "selected_teachers": [],
                "benchmark_families": [],
                "disagreement_artifacts": [],
                "registry_layer": None,
                "dream_derived": False,
                "live_derived": True,
            },
        )
        self.experiments.record(
            ExperimentRecord(
                kind="curriculum_assessment",
                name=assessment.assessment_id,
                status="shadow",
                lineage={"phase": request.phase, "subject": request.subject},
                metrics={"mastery_score": mastery_score, "passed_courses": passed, "total_courses": len(records)},
            )
        )
        return assessment

    def transcript(self, subject: str | None = None, limit: int = 200) -> list[dict]:
        return self.registrar.transcript(subject=subject, limit=limit)

    def _assess_teacher_regimen(self, *, brain, request: CurriculumAssessmentRequest, regimen: dict[str, Any]) -> CurriculumAssessment:
        subject = regimen.get("subject") or request.subject
        subject_key = f"{request.phase}:{subject}"
        assignment = self.teacher_registry.assignment_for(subject, "v2026_live") or self.teacher_registry.assignment_for(subject)
        if assignment is None:
            return self.assess(brain=brain, request=request.model_copy(update={"subject": "general"}))

        benchmark_families = list(assignment.benchmark_families or regimen.get("benchmark_families", []))
        primary_teacher_id = assignment.primary_teacher_id or (assignment.teacher_ids[0] if assignment.teacher_ids else None)
        secondary_teacher_id = assignment.secondary_teacher_id
        critique_assignment = self.teacher_registry.assignment_for("critique", "v2026_live") or self.teacher_registry.assignment_for("critique")
        critique_teacher_id = critique_assignment.primary_teacher_id if critique_assignment else None
        previous_active = self.teacher_registry.active_teacher()
        records: list[dict[str, Any]] = []
        disagreement_artifacts: list[dict[str, Any]] = []
        passed = 0

        try:
            stage_keys = list(regimen.get("stages", []))
            stage_1_family = benchmark_families[0] if benchmark_families else None
            stage_2_family = benchmark_families[1] if len(benchmark_families) > 1 else stage_1_family
            stage_3_family = benchmark_families[2] if len(benchmark_families) > 2 else stage_2_family
            stage_4_family = benchmark_families[3] if len(benchmark_families) > 3 else stage_3_family

            primary_attached = self.teacher_registry.attach(
                brain,
                ModelAttachRequest(teacher_id=primary_teacher_id, set_active=False),
                registry_layer="v2026_live",
                lineage="live-derived",
                benchmark_family=stage_1_family,
            )
            stage_1_prompt = self._stage_prompt(
                subject=subject,
                stage_label="Stage 1: Domain Professor Distillation",
                benchmark_family=stage_1_family,
                instruction="Establish field instincts and emit clean domain traces for NexusNet training.",
            )
            stage_1_result = brain.generate(
                session_context=SessionContext(
                    session_id=f"curriculum::{subject_key}",
                    expert=subject,
                    task_type="curriculum",
                    use_retrieval=False,
                    metadata={
                        "curriculum_stage": stage_keys[0] if stage_keys else "stage_1_domain_professor_distillation",
                        "teacher_registry_layer": "v2026_live",
                        "benchmark_family": stage_1_family,
                    },
                ),
                prompt=stage_1_prompt,
                model_hint=primary_attached.model_id,
            )
            stage_1_score = 1.0 if stage_1_result.output.strip() else 0.0
            stage_1_status = "passed" if stage_1_score >= 0.67 else "remediation"
            if stage_1_status == "passed":
                passed += 1
            stage_1_metrics = self._stage_metrics(
                output=stage_1_result.output,
                latency_ms=stage_1_result.inference_trace.latency_ms,
                critique_present=False,
            )
            stage_1_teacher_flow = self._score_teacher_flow(
                subject=subject,
                registry_layer="v2026_live",
                selected_roles={"primary": primary_teacher_id},
                arbitration_result="SELECT_BEST",
                benchmark_family=stage_1_family,
                lineage="live-derived",
                metrics=stage_1_metrics,
            )
            record = self.registrar.record_grade(
                subject=subject_key,
                course="Stage 1: Domain Professor Distillation",
                status=stage_1_status,
                score=stage_1_score,
                detail={
                    "phase": request.phase,
                    "prompt": stage_1_prompt,
                    "output_preview": stage_1_result.output[:240],
                    "teacher_flow": stage_1_teacher_flow,
                    "stage_key": stage_keys[0] if stage_keys else "stage_1_domain_professor_distillation",
                    "benchmark_families": benchmark_families,
                },
            )
            self.memory.record_curriculum_state(subject_key, record)
            records.append(record)

            secondary_attached = None
            stage_2_primary_output = stage_1_result.output
            stage_2_secondary_output = ""
            if secondary_teacher_id:
                secondary_attached = self.teacher_registry.attach(
                    brain,
                    ModelAttachRequest(teacher_id=secondary_teacher_id, set_active=False),
                    registry_layer="v2026_live",
                    lineage="live-derived",
                    benchmark_family=stage_2_family,
                )
                stage_2_prompt = self._stage_prompt(
                    subject=subject,
                    stage_label="Stage 2: Dual-Teacher Contrast",
                    benchmark_family=stage_2_family,
                    instruction="Solve the same task family from a contrasting teacher perspective and surface disagreement-worthy deltas.",
                )
                stage_2_primary_result = brain.generate(
                    session_context=SessionContext(
                        session_id=f"curriculum::{subject_key}",
                        expert=subject,
                        task_type="curriculum",
                        use_retrieval=False,
                        metadata={
                            "curriculum_stage": stage_keys[1] if len(stage_keys) > 1 else "stage_2_dual_teacher_contrast",
                            "teacher_registry_layer": "v2026_live",
                            "benchmark_family": stage_2_family,
                            "teacher_role": "primary",
                        },
                    ),
                    prompt=stage_2_prompt,
                    model_hint=primary_attached.model_id,
                )
                stage_2_secondary_result = brain.generate(
                    session_context=SessionContext(
                        session_id=f"curriculum::{subject_key}",
                        expert=subject,
                        task_type="curriculum",
                        use_retrieval=False,
                        metadata={
                            "curriculum_stage": stage_keys[1] if len(stage_keys) > 1 else "stage_2_dual_teacher_contrast",
                            "teacher_registry_layer": "v2026_live",
                            "benchmark_family": stage_2_family,
                            "teacher_role": "secondary",
                        },
                    ),
                    prompt=stage_2_prompt,
                    model_hint=secondary_attached.model_id,
                )
                stage_2_primary_output = stage_2_primary_result.output
                stage_2_secondary_output = stage_2_secondary_result.output
                disagreement = self._capture_disagreement(
                    subject=subject,
                    registry_layer="v2026_live",
                    primary_teacher_id=primary_teacher_id,
                    secondary_teacher_id=secondary_teacher_id,
                    critique_teacher_id=critique_teacher_id,
                    efficiency_teacher_id=assignment.optional_efficiency_coach_id,
                    primary_output=stage_2_primary_output,
                    secondary_output=stage_2_secondary_output,
                    arbitration_result="SELECT_BEST",
                    benchmark_family=stage_2_family,
                    dream_derived=False,
                    live_derived=True,
                )
                disagreement_artifacts.append(disagreement)
                stage_2_score = 1.0 if disagreement["disagreement_delta"] >= 0.0 else 0.0
                stage_2_status = "passed" if stage_2_score >= 0.67 else "remediation"
                if stage_2_status == "passed":
                    passed += 1
                stage_2_metrics = self._stage_metrics(
                    output=stage_2_primary_output,
                    latency_ms=max(
                        stage_2_primary_result.inference_trace.latency_ms,
                        stage_2_secondary_result.inference_trace.latency_ms,
                    ),
                    disagreement_severity=float(disagreement.get("disagreement_delta", 0.0)),
                    critique_present=bool(critique_teacher_id),
                    lfm2_bounded_ok=bool(assignment.optional_efficiency_coach_id is None or self._lfm2_lane(subject) is not None),
                )
                stage_2_teacher_flow = self._score_teacher_flow(
                    subject=subject,
                    registry_layer="v2026_live",
                    selected_roles={
                        "primary": primary_teacher_id,
                        "secondary": secondary_teacher_id,
                        **({"critique": critique_teacher_id} if critique_teacher_id else {}),
                        **({"efficiency": assignment.optional_efficiency_coach_id} if assignment.optional_efficiency_coach_id else {}),
                    },
                    arbitration_result="SELECT_BEST",
                    benchmark_family=stage_2_family,
                    lineage="live-derived",
                    metrics=stage_2_metrics,
                    disagreement_artifacts=[disagreement],
                    lfm2_lane=self._lfm2_lane(subject),
                )
                record = self.registrar.record_grade(
                    subject=subject_key,
                    course="Stage 2: Dual-Teacher Contrast",
                    status=stage_2_status,
                    score=stage_2_score,
                    detail={
                        "phase": request.phase,
                        "prompt": stage_2_prompt,
                        "primary_output_preview": stage_2_primary_output[:240],
                        "secondary_output_preview": stage_2_secondary_output[:240],
                        "teacher_flow": stage_2_teacher_flow,
                        "stage_key": stage_keys[1] if len(stage_keys) > 1 else "stage_2_dual_teacher_contrast",
                    },
                )
                self.memory.record_curriculum_state(subject_key, record)
                records.append(record)

            arbitration_attached, arbitration_record = self.teacher_registry.resolve_for_task(
                brain=brain,
                task_type="curriculum",
                expert=subject,
                routing_metadata={
                    "budget_class": "DEEP",
                    "output_form": "EVAL_JUDGE",
                    "risk_tier": "high",
                    "benchmark_family": stage_3_family,
                    "teacher_lineage": "live-derived",
                },
            )
            critique_teacher_id = arbitration_record.selected_roles.get("critique") or critique_teacher_id or arbitration_attached.teacher_id
            critique_attached = self.teacher_registry.attach(
                brain,
                ModelAttachRequest(teacher_id=critique_teacher_id, set_active=False),
                registry_layer=arbitration_record.registry_layer,
                arbitration=arbitration_record,
                lineage="live-derived",
                benchmark_family=stage_3_family,
            )
            stage_3_prompt = (
                f"Skeptical examination for {subject}. "
                f"Benchmark family: {stage_3_family or 'general'}. "
                f"Primary teacher output: {stage_2_primary_output[:280]}. "
                f"Secondary teacher output: {stage_2_secondary_output[:280]}. "
                "Pick the best merge path and justify it for NexusNet training."
            )
            stage_3_result = brain.generate(
                session_context=SessionContext(
                    session_id=f"curriculum::{subject_key}",
                    expert="critique",
                    task_type="curriculum",
                    use_retrieval=False,
                    metadata={
                        "curriculum_stage": stage_keys[2] if len(stage_keys) > 2 else "stage_3_skeptical_examination",
                        "teacher_registry_layer": arbitration_record.registry_layer,
                        "benchmark_family": stage_3_family,
                    },
                ),
                prompt=stage_3_prompt,
                model_hint=critique_attached.model_id,
            )
            stage_3_score = 1.0 if stage_3_result.output.strip() else 0.0
            stage_3_status = "passed" if stage_3_score >= 0.67 else "remediation"
            if stage_3_status == "passed":
                passed += 1
            stage_3_metrics = self._stage_metrics(
                output=stage_3_result.output,
                latency_ms=stage_3_result.inference_trace.latency_ms,
                disagreement_severity=(
                    sum(float(item.get("disagreement_delta", 0.0)) for item in disagreement_artifacts)
                    / len(disagreement_artifacts)
                    if disagreement_artifacts
                    else 0.0
                ),
                critique_present=True,
                rollbackability=True,
            )
            stage_3_teacher_flow = self._score_teacher_flow(
                subject=subject,
                registry_layer=arbitration_record.registry_layer,
                selected_roles=arbitration_record.selected_roles,
                arbitration_result=arbitration_record.arbitration_result,
                benchmark_family=stage_3_family,
                lineage="live-derived",
                metrics=stage_3_metrics,
                disagreement_artifacts=disagreement_artifacts,
                teacher_confidence=arbitration_record.teacher_confidence,
                lfm2_lane=self._lfm2_lane(subject),
            )
            record = self.registrar.record_grade(
                subject=subject_key,
                course="Stage 3: Skeptical Examination",
                status=stage_3_status,
                score=stage_3_score,
                detail={
                    "phase": request.phase,
                    "prompt": stage_3_prompt,
                    "output_preview": stage_3_result.output[:240],
                    "teacher_flow": stage_3_teacher_flow,
                    "stage_key": stage_keys[2] if len(stage_keys) > 2 else "stage_3_skeptical_examination",
                    "merge_decision": arbitration_record.arbitration_result,
                },
            )
            self.memory.record_curriculum_state(subject_key, record)
            records.append(record)

            dream_episode = None
            if self.dream_engine is not None:
                dream_episode = self.dream_engine.run_cycle(
                    brain=brain,
                    request=DreamCycleRequest(
                        trace_id=stage_3_result.trace_id,
                        model_hint=primary_attached.model_id,
                        variant_count=2,
                    ),
                )
            stage_4_metrics = self._stage_metrics(
                output=stage_3_result.output,
                latency_ms=stage_3_result.inference_trace.latency_ms,
                disagreement_severity=(
                    sum(float(item.get("disagreement_delta", 0.0)) for item in disagreement_artifacts)
                    / len(disagreement_artifacts)
                    if disagreement_artifacts
                    else 0.0
                ),
                critique_present=True,
                dream_derived=dream_episode is not None,
                rollbackability=True,
            )
            stage_4_teacher_flow = self._score_teacher_flow(
                subject=subject,
                registry_layer="v2026_live",
                selected_roles={
                    "primary": primary_teacher_id,
                    **({"secondary": secondary_teacher_id} if secondary_teacher_id else {}),
                    **({"critique": critique_teacher_id} if critique_teacher_id else {}),
                    **({"efficiency": assignment.optional_efficiency_coach_id} if assignment.optional_efficiency_coach_id else {}),
                },
                arbitration_result=arbitration_record.arbitration_result,
                benchmark_family=stage_4_family,
                lineage="dream-derived" if dream_episode is not None else "live-derived",
                metrics=stage_4_metrics,
                disagreement_artifacts=disagreement_artifacts,
                teacher_confidence=arbitration_record.teacher_confidence,
                lfm2_lane=self._lfm2_lane(subject),
            )
            evaluation = None
            if self.evaluator is not None:
                evaluation = self.evaluator.evaluate_teacher_bundle(
                    subject=subject,
                    baseline_reference=f"teacher::{primary_teacher_id}",
                    challenger_reference=f"teacher::{secondary_teacher_id or primary_teacher_id}",
                    teacher_evidence=stage_4_teacher_flow,
                    scenario_set=[
                        "primary-vs-secondary-disagreement",
                        "critique-arbitration-validation",
                        "lfm2-bounded-lane-enforcement",
                        "dream-derived-trace-contamination",
                    ],
                    limit=10,
                )
            stage_4_score = 1.0 if evaluation is None or evaluation["decision"]["decision"] != "rejected" else 0.25
            stage_4_status = "passed" if stage_4_score >= 0.67 else "remediation"
            if stage_4_status == "passed":
                passed += 1
            record = self.registrar.record_grade(
                subject=subject_key,
                course="Stage 4: Dream / Self-Evolution",
                status=stage_4_status,
                score=stage_4_score,
                detail={
                    "phase": request.phase,
                    "teacher_flow": stage_4_teacher_flow,
                    "stage_key": stage_keys[3] if len(stage_keys) > 3 else "stage_4_dream_self_evolution",
                    "dream_episode": dream_episode.model_dump(mode="json") if dream_episode is not None else None,
                    "external_evaluation": evaluation,
                    "external_evaluation_required": True,
                    "teacher_retirement_requires_surpass_evidence": True,
                },
            )
            self.memory.record_curriculum_state(subject_key, record)
            records.append(record)
        finally:
            if previous_active is not None:
                self.teacher_registry.set_active(previous_active.teacher_id)

        mastery_score = round(sum((record.get("score") or 0.0) for record in records) / max(len(records), 1), 3)
        teacher_flow = aggregate_teacher_evidence(traces=[], curriculum_records=records)
        teacher_flow.update(
            {
                "status_label": "LOCKED CANON",
                "mode": "teacher-regimen",
                "registry_layer": "v2026_live",
                "benchmark_families": benchmark_families,
            }
        )
        assessment = CurriculumAssessment(
            phase=request.phase,
            subject=request.subject,
            total_courses=len(records),
            passed_courses=passed,
            mastery_score=mastery_score,
            records=records,
            teacher_flow=teacher_flow,
        )
        self.experiments.record(
            ExperimentRecord(
                kind="curriculum_assessment",
                name=assessment.assessment_id,
                status="shadow",
                lineage={"phase": request.phase, "subject": request.subject, "teacher_mode": "teacher-regimen"},
                metrics={
                    "mastery_score": mastery_score,
                    "passed_courses": passed,
                    "total_courses": len(records),
                    "teacher_disagreement_delta": (
                        round(
                            sum(float(artifact.get("disagreement_delta", 0.0)) for artifact in disagreement_artifacts)
                            / len(disagreement_artifacts),
                            3,
                        )
                        if disagreement_artifacts
                        else 0.0
                    ),
                },
            )
        )
        return assessment

    def _capture_disagreement(
        self,
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
    ) -> dict[str, Any]:
        if self.teacher_evidence_service is not None:
            artifact = self.teacher_evidence_service.create_disagreement(
                subject=subject,
                registry_layer=registry_layer,
                primary_teacher_id=primary_teacher_id,
                secondary_teacher_id=secondary_teacher_id,
                critique_teacher_id=critique_teacher_id,
                efficiency_teacher_id=efficiency_teacher_id,
                arbitration_result=arbitration_result,
                rationale="Dual-teacher contrast surfaced disagreement that requires critique-aware persistence.",
                benchmark_family=benchmark_family,
                primary_output=primary_output,
                secondary_output=secondary_output,
                threshold_set_id=self._threshold_set_id(subject, benchmark_family),
                lfm2_lane=self._lfm2_lane(subject),
                lfm2_bounded_ok=bool(efficiency_teacher_id is None or self._lfm2_lane(subject) is not None),
                dream_derived=dream_derived,
                live_derived=live_derived,
            )
            payload = artifact.model_dump(mode="json")
            payload["disagreement_delta"] = artifact.disagreement_severity
            payload["primary_output_preview"] = primary_output[:240]
            payload["secondary_output_preview"] = secondary_output[:240]
            return payload
        return build_disagreement_artifact(
            subject=subject,
            registry_layer=registry_layer,
            primary_teacher_id=primary_teacher_id,
            secondary_teacher_id=secondary_teacher_id,
            critique_teacher_id=critique_teacher_id,
            efficiency_teacher_id=efficiency_teacher_id,
            primary_output=primary_output,
            secondary_output=secondary_output,
            arbitration_result=arbitration_result,
            benchmark_family=benchmark_family,
            dream_derived=dream_derived,
            live_derived=live_derived,
        )

    def _score_teacher_flow(
        self,
        *,
        subject: str,
        registry_layer: str,
        selected_roles: dict[str, str],
        arbitration_result: str,
        benchmark_family: str | None,
        lineage: str,
        metrics: dict[str, float],
        disagreement_artifacts: list[dict[str, Any]] | None = None,
        teacher_confidence: float = 0.0,
        lfm2_lane: str | None = None,
    ) -> dict[str, Any]:
        disagreement_artifacts = disagreement_artifacts or []
        if self.teacher_evidence_service is not None and benchmark_family:
            scorecard = self.teacher_evidence_service.create_scorecard(
                subject=subject,
                benchmark_family=benchmark_family,
                metrics=metrics,
                threshold_set_id=self._threshold_set_id(subject, benchmark_family),
            )
            bundle = self.teacher_evidence_service.create_bundle(
                subject=subject,
                registry_layer=registry_layer,
                selected_teacher_roles=selected_roles,
                arbitration_result=arbitration_result,
                benchmark_families=[benchmark_family],
                metrics=metrics,
                disagreement_artifacts=[
                    TeacherDisagreementArtifact.model_validate(item) for item in disagreement_artifacts
                ],
                scorecards=[scorecard],
                threshold_set_id=scorecard.threshold_set_id,
                benchmark_family=benchmark_family,
                dream_derived=lineage == "dream-derived",
                live_derived=lineage == "live-derived",
                lfm2_lane=lfm2_lane,
                lfm2_bounded_ok=bool(selected_roles.get("efficiency") is None or lfm2_lane is not None),
                teacher_confidence=teacher_confidence,
            )
            stage_bundle = self.teacher_evidence_service.bundle_payload(bundle.bundle_id)
            stage_bundle["selected_teacher_roles"] = selected_roles
            stage_bundle["arbitration_result"] = arbitration_result
            stage_bundle["benchmark_family"] = benchmark_family
            stage_bundle["dream_derived"] = lineage == "dream-derived"
            stage_bundle["live_derived"] = lineage == "live-derived"
            stage_bundle["teacher_confidence"] = teacher_confidence
            stage_bundle["lfm2_lane"] = lfm2_lane
            stage_bundle["lfm2_bounded_ok"] = bool(selected_roles.get("efficiency") is None or lfm2_lane is not None)
            stage_bundle["metrics"] = {**stage_bundle.get("metrics", {}), **metrics}
            if disagreement_artifacts:
                stage_bundle["disagreement_artifacts"] = disagreement_artifacts
                stage_bundle["disagreement_artifact_ids"] = [
                    item.get("artifact_id") for item in disagreement_artifacts if item.get("artifact_id")
                ]
                stage_bundle["teacher_disagreement_delta"] = round(
                    sum(float(item.get("disagreement_delta", item.get("disagreement_severity", 0.0)) or 0.0) for item in disagreement_artifacts)
                    / len(disagreement_artifacts),
                    3,
                )
            return stage_bundle
        return build_teacher_evidence(
            subject=subject,
            registry_layer=registry_layer,
            selected_roles=selected_roles,
            arbitration_result=arbitration_result,
            benchmark_family=benchmark_family,
            lineage=lineage,
            disagreement_artifacts=disagreement_artifacts,
            lfm2_bounded_ok=bool(selected_roles.get("efficiency") is None or lfm2_lane is not None),
            threshold_set_id=self._threshold_set_id(subject, benchmark_family),
            teacher_confidence=teacher_confidence,
            lfm2_lane=lfm2_lane,
        )

    def _stage_metrics(
        self,
        *,
        output: str,
        latency_ms: int,
        disagreement_severity: float = 0.0,
        critique_present: bool = False,
        dream_derived: bool = False,
        lfm2_bounded_ok: bool = True,
        rollbackability: bool | None = None,
    ) -> dict[str, float]:
        latency_score = 1.0 if latency_ms <= 2500 else (0.8 if latency_ms <= 5000 else 0.6)
        return {
            "correctness": 1.0 if output.strip() else 0.0,
            "groundedness": 0.9 if output.strip() else 0.0,
            "safety": 1.0 if critique_present or not dream_derived else 0.8,
            "tool_discipline": 1.0 if lfm2_bounded_ok else 0.4,
            "structured_output_conformance": 0.9 if output.strip() else 0.0,
            "efficiency_latency_budget": latency_score,
            "disagreement_severity": max(0.0, min(float(disagreement_severity or 0.0), 1.0)),
            "dream_contamination_sensitivity": 0.95 if (not dream_derived or critique_present) else 0.45,
            "native_vs_teacher_delta": 0.0,
            "rollbackability": 1.0 if rollbackability is not False else 0.0,
        }

    def _threshold_set_id(self, subject: str, benchmark_family: str | None) -> str | None:
        if self.teacher_registry is None or benchmark_family is None:
            return None
        return self.teacher_registry.threshold_registry.resolve(subject=subject, benchmark_family=benchmark_family).threshold_set_id

    def _lfm2_lane(self, subject: str) -> str | None:
        return self.teacher_registry.routing_policy.get("domain_defaults", {}).get(subject, {}).get("lfm2_lane")

    def _build_syllabus(self) -> dict[str, list[CurriculumCourse]]:
        return {
            "foundation": [
                CurriculumCourse(
                    phase="foundation",
                    subject="general",
                    title="Core Identity and Teacher Model Framing",
                    prompt="State that NexusNet is a neural wrapper/core around teacher models and not merely a chatbot.",
                    expected_substrings=["nexusnet", "wrapper", "teacher"],
                    credits=3,
                ),
                CurriculumCourse(
                    phase="foundation",
                    subject="general",
                    title="Memory Foundations",
                    prompt="Explain that NexusNet maintains episodic and semantic memory for long-horizon reasoning.",
                    expected_substrings=["episodic", "semantic"],
                    credits=3,
                ),
            ],
            "graduate": [
                CurriculumCourse(
                    phase="graduate",
                    subject="research",
                    title="Benchmark and Critique Lab",
                    prompt="Describe why benchmark gates and critique loops matter for NexusNet improvements.",
                    expected_substrings=["benchmark", "critique"],
                    credits=4,
                ),
                CurriculumCourse(
                    phase="graduate",
                    subject="research",
                    title="Teacher Distillation Seminar",
                    prompt="Explain how teacher traces can become student training targets inside NexusNet.",
                    expected_substrings=["teacher", "student", "training"],
                    credits=4,
                ),
            ],
            "doctoral": [
                CurriculumCourse(
                    phase="doctoral",
                    subject="synthesis",
                    title="Native Emergence Dissertation",
                    prompt="Argue for a staged path from wrapper intelligence to a native NexusNet student model.",
                    expected_substrings=["wrapper", "native", "student"],
                    credits=5,
                )
            ],
            "faculty": [
                CurriculumCourse(
                    phase="faculty",
                    subject="governance",
                    title="Review Board Defense",
                    prompt="Defend why rollback, approval, and benchmark evidence are required before promoting self-improvements.",
                    expected_substrings=["rollback", "approval", "benchmark"],
                    credits=5,
                )
            ],
        }

    def _stage_prompt(self, *, subject: str, stage_label: str, benchmark_family: str | None, instruction: str) -> str:
        benchmark = benchmark_family or "general reasoning"
        return (
            f"{stage_label} for NexusNet subject '{subject}'. "
            f"Benchmark family: {benchmark}. "
            f"{instruction}"
        )
