from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from nexus.schemas import CritiqueReport, Message, RetrievalHit, new_id, utcnow


StatusLabel = Literal[
    "LOCKED CANON",
    "STRONG ACCEPTED DIRECTION",
    "IMPLEMENTATION BRANCH",
    "EXPLORATORY / PROTOTYPE",
    "UNRESOLVED CONFLICT",
]

ArtifactLineage = Literal["live-derived", "dream-derived", "blended-derived"]
PromotionCandidateKind = Literal["runtime-profile", "retrieval-policy", "federated-update", "native-takeover"]


class CapabilityProfile(BaseModel):
    model_id: str
    runtime_name: str
    adapter_role: Literal["base", "teacher", "specialist", "student"] = "teacher"
    modalities: list[str] = Field(default_factory=lambda: ["text"])
    context_window: int = 4096
    supports_tools: bool = False
    supports_streaming: bool = False
    supports_multimodal: bool = False
    preferred_domains: list[str] = Field(default_factory=list)
    known_limits: list[str] = Field(default_factory=list)
    telemetry: dict[str, Any] = Field(default_factory=dict)


class SessionContext(BaseModel):
    session_id: str = Field(default_factory=lambda: new_id("session"))
    trace_id: str = Field(default_factory=lambda: new_id("braintrace"))
    ao: str | None = None
    expert: str | None = None
    task_type: str = "chat"
    use_retrieval: bool = True
    memory_budget: int = 6
    compression_target_tokens: int = 512
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class CompressionTrace(BaseModel):
    strategy: str
    original_chars: int
    compressed_chars: int
    estimated_tokens_before: int
    estimated_tokens_after: int
    loss_estimate: float
    summary: str


class InferenceTrace(BaseModel):
    trace_id: str
    session_id: str
    model_id: str
    runtime_name: str
    adapter_id: str
    adapter_role: str
    started_at: datetime
    completed_at: datetime | None = None
    latency_ms: int = 0
    input_preview: str = ""
    output_preview: str = ""
    retrieval_hit_count: int = 0
    memory_records_written: int = 0
    compression: CompressionTrace | None = None
    critique_id: str | None = None
    status: Literal["ok", "warning", "error"] = "ok"
    error: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    log_path: str | None = None


class BrainGenerateResult(BaseModel):
    trace_id: str
    session_id: str
    model_id: str
    runtime_name: str
    adapter_id: str
    output: str
    retrieval_hits: list[RetrievalHit] = Field(default_factory=list)
    critique: CritiqueReport | None = None
    inference_trace: InferenceTrace
    citations: list[dict[str, Any]] = Field(default_factory=list)
    compression: CompressionTrace | None = None
    used_memory_count: int = 0
    attached_role: str = "teacher"
    runtime_selection: dict[str, Any] = Field(default_factory=dict)
    retrieval_policy_decision: dict[str, Any] = Field(default_factory=dict)
    promotion_references: list[str] = Field(default_factory=list)


class BenchmarkCase(BaseModel):
    case_id: str = Field(default_factory=lambda: new_id("benchcase"))
    prompt: str
    expected_substrings: list[str] = Field(default_factory=list)
    model_hint: str | None = None
    expert: str | None = None
    use_retrieval: bool = False
    max_latency_ms: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BenchmarkCaseResult(BaseModel):
    case_id: str
    passed: bool
    score: float
    latency_ms: int
    output_preview: str
    matched_substrings: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)


class BenchmarkRun(BaseModel):
    run_id: str = Field(default_factory=lambda: new_id("benchrun"))
    suite_name: str
    model_id: str
    runtime_name: str
    case_count: int
    pass_rate: float
    avg_latency_ms: float
    results: list[BenchmarkCaseResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    artifact_path: str | None = None


class DreamCycleRequest(BaseModel):
    trace_id: str | None = None
    seed: str | None = None
    model_hint: str | None = None
    variant_count: int = 3


class DreamVariant(BaseModel):
    variant_id: str = Field(default_factory=lambda: new_id("dreamvar"))
    mode: Literal["failure_replay", "counterfactual", "adversarial", "future_rehearsal"] = "failure_replay"
    prompt: str
    output_preview: str = ""
    latency_ms: int = 0
    critique_status: str = "ok"
    scores: dict[str, float] = Field(default_factory=dict)


class DreamEpisode(BaseModel):
    dream_id: str
    seed: str
    source_trace_id: str | None = None
    status: Literal["shadow", "rejected", "promoted"] = "shadow"
    lineage: ArtifactLineage = "dream-derived"
    variants: list[DreamVariant] = Field(default_factory=list)
    aggregate_score: float = 0.0
    findings: list[str] = Field(default_factory=list)
    artifact_path: str | None = None
    created_at: datetime = Field(default_factory=utcnow)


class ReflectionFinding(BaseModel):
    category: Literal["hallucination", "retrieval", "runtime", "latency", "memory", "governance", "benchmark", "dreaming"]
    severity: Literal["info", "warning", "critical"] = "info"
    detail: str
    trace_id: str | None = None
    critique_id: str | None = None


class ReflectionReport(BaseModel):
    report_id: str = Field(default_factory=lambda: new_id("reflect"))
    scope: str = "recent"
    findings: list[ReflectionFinding] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class CurriculumCourse(BaseModel):
    course_id: str = Field(default_factory=lambda: new_id("course"))
    phase: Literal["foundation", "graduate", "doctoral", "faculty"]
    subject: str
    title: str
    prompt: str
    expected_substrings: list[str] = Field(default_factory=list)
    credits: int = 1
    prerequisites: list[str] = Field(default_factory=list)


class CurriculumAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: new_id("assess"))
    phase: str
    subject: str
    total_courses: int
    passed_courses: int
    mastery_score: float
    records: list[dict[str, Any]] = Field(default_factory=list)
    teacher_flow: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class CurriculumAssessmentRequest(BaseModel):
    phase: Literal["foundation", "graduate", "doctoral", "faculty"] = "foundation"
    subject: str = "general"
    model_hint: str | None = None


class DistillationExportRequest(BaseModel):
    name: str
    trace_limit: int = 100
    include_dreams: bool = True
    include_curriculum: bool = True


class DistillationExportResult(BaseModel):
    export_id: str = Field(default_factory=lambda: new_id("distill"))
    name: str
    sample_count: int
    artifact_path: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class ModelAttachRequest(BaseModel):
    model_hint: str | None = None
    teacher_id: str | None = None
    attach_role: Literal["teacher", "specialist", "student"] = "teacher"
    set_active: bool = True


class TeacherCapabilityCard(BaseModel):
    teacher_id: str
    modalities: list[str] = Field(default_factory=lambda: ["text"])
    supports_tools: bool = False
    supports_structured_output: bool = False
    best_for: list[str] = Field(default_factory=list)
    budget_class: str = "standard"
    risk_tier: str = "medium"
    context_window: int = 4096
    locality: str = "local_first"
    reasoning_modes: list[str] = Field(default_factory=list)
    hardware_targets: list[str] = Field(default_factory=list)
    bounded_lanes: list[str] = Field(default_factory=list)


class TeacherProfile(BaseModel):
    teacher_id: str
    canonical_name: str
    role: str
    role_tags: list[str] = Field(default_factory=list)
    lineage: str
    status_label: StatusLabel
    registry_layers: list[str] = Field(default_factory=list)
    model_hints: list[str] = Field(default_factory=list)
    specialties: list[str] = Field(default_factory=list)
    capability_card: TeacherCapabilityCard | None = None
    mentor: bool = False
    arbitration_weight: float = 1.0
    retirement: dict[str, Any] = Field(default_factory=dict)
    available: bool = False
    retired: bool = False
    notes: list[str] = Field(default_factory=list)


class AttachedTeacher(BaseModel):
    teacher_id: str
    model_id: str
    attach_role: str
    active: bool = True
    status_label: StatusLabel = "LOCKED CANON"
    provenance: dict[str, Any] = Field(default_factory=dict)
    attached_at: datetime = Field(default_factory=utcnow)


class TeacherArbitrationRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: new_id("arb"))
    task_type: str
    expert: str | None = None
    registry_layer: str = "v2026_live"
    candidates: list[str] = Field(default_factory=list)
    selected_teacher_id: str
    selected_teacher_ids: list[str] = Field(default_factory=list)
    selected_roles: dict[str, str] = Field(default_factory=dict)
    local_vs_remote: str | None = None
    reasoning_mode: str | None = None
    arbitration_result: str = "SELECT_BEST"
    benchmark_family: str | None = None
    teacher_confidence: float = 0.0
    dream_lineage: ArtifactLineage = "live-derived"
    native_takeover_candidate_id: str | None = None
    rationale: str
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class TeacherAssignment(BaseModel):
    subject: str
    subject_display_name: str | None = None
    registry_layer: str = "historical"
    teacher_ids: list[str] = Field(default_factory=list)
    arbitration_policy: str = "weighted-availability"
    routing_mode: str = "best-ensemble-per-role"
    primary_teacher_id: str | None = None
    secondary_teacher_id: str | None = None
    critique_arbiter_subject: str | None = None
    critique_arbiter_teacher_id: str | None = None
    optional_efficiency_coach_id: str | None = None
    locality_preference: str | None = None
    historical_anchor_ref: str | None = None
    evaluation_family: list[str] = Field(default_factory=list)
    benchmark_families: list[str] = Field(default_factory=list)
    fallback_teacher_ids: list[str] = Field(default_factory=list)
    auxiliary: bool = False
    roster_position: int | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class TeacherRoutingDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("teachroute"))
    subject: str
    registry_layer: str = "v2026_live"
    candidates: list[str] = Field(default_factory=list)
    selected_teacher_id: str
    selected_teacher_ids: list[str] = Field(default_factory=list)
    selected_roles: dict[str, str] = Field(default_factory=dict)
    policy: str
    fallback_chain: list[str] = Field(default_factory=list)
    arbitration_needed: bool = False
    arbitration_trigger: str | None = None
    locality_preference: str | None = None
    budget_class: str | None = None
    output_form: str | None = None
    risk_tier: str | None = None
    modality: str | None = None
    teacher_confidence: float = 0.0
    benchmark_family: str | None = None
    historical_anchor_ref: str | None = None
    rationale: str
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class TeacherRetirementDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("teachret"))
    teacher_id: str
    registry_layer: str = "v2026_live"
    decision: Literal["hold", "shadow", "retire"] = "hold"
    rationale: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    rollback_required: bool = True
    governance_required: bool = True
    external_evaluation_required: bool = True
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class TeacherScorecard(BaseModel):
    scorecard_id: str = Field(default_factory=lambda: new_id("teachscore"))
    subject: str
    benchmark_family_id: str
    threshold_set_id: str
    threshold_version: int
    schema_family: str = "teacher-scorecard"
    schema_version: int = 1
    schema_compatibility: dict[str, Any] = Field(default_factory=dict)
    weighted_score: float
    passed: bool
    metrics: dict[str, float] = Field(default_factory=dict)
    thresholds: dict[str, Any] = Field(default_factory=dict)
    weight_profile: dict[str, float] = Field(default_factory=dict)
    failure_reasons: list[str] = Field(default_factory=list)
    artifact_path: str | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class TeacherDisagreementArtifact(BaseModel):
    artifact_id: str = Field(default_factory=lambda: new_id("teachdis"))
    subject: str
    registry_layer: str
    schema_family: str = "teacher-disagreement-artifact"
    schema_version: int = 1
    schema_compatibility: dict[str, Any] = Field(default_factory=dict)
    primary_teacher_id: str
    secondary_teacher_id: str | None = None
    critique_teacher_id: str | None = None
    efficiency_teacher_id: str | None = None
    arbitration_result: str
    rationale: str
    benchmark_family: str | None = None
    threshold_set_id: str | None = None
    dream_derived: bool = False
    live_derived: bool = True
    disagreement_severity: float = 0.0
    teacher_confidence: float = 0.0
    native_takeover_candidate_id: str | None = None
    lfm2_lane: str | None = None
    lfm2_bounded_ok: bool = True
    metrics: dict[str, Any] = Field(default_factory=dict)
    artifact_refs: dict[str, str] = Field(default_factory=dict)
    artifact_path: str | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class TeacherEvidenceBundle(BaseModel):
    bundle_id: str = Field(default_factory=lambda: new_id("teachev"))
    subject: str
    registry_layer: str
    schema_family: str = "teacher-evidence-bundle"
    schema_version: int = 1
    schema_compatibility: dict[str, Any] = Field(default_factory=dict)
    selected_teachers: list[str] = Field(default_factory=list)
    selected_teacher_roles: dict[str, str] = Field(default_factory=dict)
    arbitration_result: str | None = None
    benchmark_families: list[str] = Field(default_factory=list)
    benchmark_family: str | None = None
    threshold_set_id: str | None = None
    threshold_version: int | None = None
    disagreement_artifact_ids: list[str] = Field(default_factory=list)
    scorecards: list[TeacherScorecard] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    native_takeover_candidate_id: str | None = None
    dream_derived: bool = False
    live_derived: bool = True
    lfm2_lane: str | None = None
    lfm2_bounded_ok: bool = True
    teacher_confidence: float = 0.0
    artifacts: dict[str, str] = Field(default_factory=dict)
    artifact_path: str | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class TakeoverScorecard(BaseModel):
    scorecard_id: str = Field(default_factory=lambda: new_id("takeoverscore"))
    subject: str
    teacher_evidence_bundle_id: str | None = None
    threshold_set_id: str
    threshold_version: int
    schema_family: str = "takeover-scorecard"
    schema_version: int = 1
    schema_compatibility: dict[str, Any] = Field(default_factory=dict)
    weighted_score: float
    passed: bool
    metrics: dict[str, Any] = Field(default_factory=dict)
    deltas: dict[str, float] = Field(default_factory=dict)
    rollbackable: bool = False
    artifact_path: str | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class RetirementShadowRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: new_id("retshadow"))
    teacher_id: str
    registry_layer: str = "v2026_live"
    decision: Literal["hold", "shadow", "retire"] = "hold"
    schema_family: str = "retirement-shadow-record"
    schema_version: int = 1
    schema_compatibility: dict[str, Any] = Field(default_factory=dict)
    rationale: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    threshold_set_id: str | None = None
    takeover_scorecard_id: str | None = None
    external_evaluation_passed: bool = False
    rollback_ready: bool = False
    governance_signed_off: bool = False
    artifact_path: str | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class TeacherTrendScorecard(BaseModel):
    trend_id: str = Field(default_factory=lambda: new_id("teachtrend"))
    subject: str
    benchmark_family_id: str
    threshold_set_id: str
    trend_threshold_set_id: str
    threshold_version: int
    trend_version: int
    schema_family: str = "teacher-trend-scorecard"
    schema_version: int = 1
    schema_compatibility: dict[str, Any] = Field(default_factory=dict)
    run_count: int
    valid_run_count: int
    weighted_score_mean: float
    weighted_score_variance: float
    weighted_score_slope: float
    disagreement_mean: float = 0.0
    disagreement_slope: float = 0.0
    recent_regression_spike: bool = False
    stable: bool = False
    ready: bool = False
    recent_scorecard_ids: list[str] = Field(default_factory=list)
    recent_artifact_ids: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class TakeoverTrendReport(BaseModel):
    trend_id: str = Field(default_factory=lambda: new_id("takeovertrend"))
    subject: str
    threshold_set_id: str
    trend_threshold_set_id: str
    threshold_version: int
    trend_version: int
    schema_family: str = "takeover-trend-report"
    schema_version: int = 1
    schema_compatibility: dict[str, Any] = Field(default_factory=dict)
    run_count: int
    valid_run_count: int
    weighted_score_mean: float
    weighted_score_variance: float
    weighted_score_slope: float
    dependency_ratio_trend: float
    native_generation_trend: float
    teacher_disagreement_delta_trend: float
    native_vs_primary_trend: float
    native_vs_secondary_trend: float
    rollback_risk_trend: float
    recent_regression_spike: bool = False
    stable: bool = False
    ready: bool = False
    recent_scorecard_ids: list[str] = Field(default_factory=list)
    latest_teacher_evidence_bundle_id: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class TeacherBenchmarkFleetSummary(BaseModel):
    summary_id: str = Field(default_factory=lambda: new_id("teachfleet"))
    fleet_id: str
    window_id: str
    threshold_set_id: str
    threshold_version: int
    schema_family: str = "teacher-benchmark-fleet-summary"
    schema_version: int = 1
    schema_compatibility: dict[str, Any] = Field(default_factory=dict)
    subject: str | None = None
    teacher_pair_id: str | None = None
    budget_class: str | None = None
    output_form: str | None = None
    risk_tier: str | None = None
    locality: str | None = None
    hardware_class: str | None = None
    lineage: ArtifactLineage | None = None
    run_count: int
    valid_run_count: int
    weighted_score_mean: float
    weighted_score_variance: float
    passing_run_ratio: float
    disagreement_mean: float = 0.0
    recent_regression_spike: bool = False
    stable: bool = False
    ready: bool = False
    scorecard_ids: list[str] = Field(default_factory=list)
    evidence_bundle_ids: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class TeacherCohortScorecard(BaseModel):
    cohort_id: str = Field(default_factory=lambda: new_id("teachcohort"))
    cohort_key: str
    fleet_id: str
    window_id: str
    threshold_set_id: str
    threshold_version: int
    schema_family: str = "teacher-cohort-scorecard"
    schema_version: int = 1
    schema_compatibility: dict[str, Any] = Field(default_factory=dict)
    subject: str | None = None
    teacher_pair_id: str | None = None
    budget_class: str | None = None
    hardware_class: str | None = None
    lineage: ArtifactLineage | None = None
    run_count: int
    valid_run_count: int
    stability_score: float
    variance: float
    disagreement_trend: float
    outperformance_consistency: float
    regression_spike_count: int
    rollback_risk: float
    dream_contamination_sensitivity: float
    hardware_sensitivity: float
    stable: bool = False
    ready: bool = False
    fleet_summary_ids: list[str] = Field(default_factory=list)
    takeover_scorecard_ids: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class ReplacementReadinessReport(BaseModel):
    report_id: str = Field(default_factory=lambda: new_id("replready"))
    subject: str
    teacher_id: str
    threshold_set_id: str | None = None
    threshold_version: int | None = None
    schema_family: str = "replacement-readiness-report"
    schema_version: int = 1
    schema_compatibility: dict[str, Any] = Field(default_factory=dict)
    subject_trend_ready: bool = False
    fleet_gate_ready: bool = False
    cohort_gate_ready: bool = False
    external_evaluation_passed: bool = False
    rollback_ready: bool = False
    governance_signed_off: bool = False
    ready: bool = False
    replacement_mode: Literal["hold", "shadow", "replace"] = "hold"
    metrics: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class AOPlan(BaseModel):
    ao_name: str
    status_label: StatusLabel = "LOCKED CANON"
    reason: str
    risk_tier: Literal["low", "medium", "high"] = "medium"
    goals: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)


class AOExecutionTrace(BaseModel):
    execution_id: str = Field(default_factory=lambda: new_id("aotrace"))
    session_id: str
    ao_name: str
    plan: AOPlan
    selected_teacher_id: str | None = None
    selected_expert: str | None = None
    created_at: datetime = Field(default_factory=utcnow)


class AORegistrySnapshot(BaseModel):
    active_aos: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class MemoryPlaneConfig(BaseModel):
    plane_name: str
    conceptual_plane: str
    operational: bool = True
    description: str
    aliases: list[str] = Field(default_factory=list)
    projection_roles: list[str] = Field(default_factory=list)
    token_budget_ratio: float | None = None
    status_label: StatusLabel = "UNRESOLVED CONFLICT"


class MemorySchemaVersion(BaseModel):
    schema_name: str = "nexusnet-memory-planes"
    version: int = 1
    status_label: StatusLabel = "UNRESOLVED CONFLICT"
    migration_notes: list[str] = Field(default_factory=list)


class MemoryProjectionView(BaseModel):
    projection_name: str
    source_planes: list[str] = Field(default_factory=list)
    grouped_records: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)


class MemoryProjectionAdapter(BaseModel):
    projection_name: str
    source_planes: list[str] = Field(default_factory=list)
    status_label: StatusLabel = "UNRESOLVED CONFLICT"
    description: str


class MemoryConsolidationRecord(BaseModel):
    consolidation_id: str = Field(default_factory=lambda: new_id("sleep"))
    session_id: str
    source_planes: list[str] = Field(default_factory=list)
    target_planes: list[str] = Field(default_factory=list)
    summary: str
    created_at: datetime = Field(default_factory=utcnow)


class DreamPromotionCandidate(BaseModel):
    candidate_id: str = Field(default_factory=lambda: new_id("dreamcand"))
    dream_id: str
    aggregate_score: float
    rationale: str
    status: Literal["shadow", "review", "approved", "rejected"] = "shadow"
    created_at: datetime = Field(default_factory=utcnow)


class DreamPromotionDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("dreamdec"))
    candidate_id: str
    decision: Literal["approved", "rejected", "shadow"]
    reviewer: str
    rationale: str
    created_at: datetime = Field(default_factory=utcnow)


class CurriculumTrack(BaseModel):
    track_id: str = Field(default_factory=lambda: new_id("track"))
    phase: Literal["foundation", "graduate", "doctoral", "faculty"]
    subject: str
    title: str
    teacher_assignment: TeacherAssignment | None = None
    prerequisites: list[str] = Field(default_factory=list)


class OralDefenseResult(BaseModel):
    defense_id: str = Field(default_factory=lambda: new_id("defense"))
    subject: str
    question: str
    response_preview: str
    passed: bool
    critique_summary: str
    created_at: datetime = Field(default_factory=utcnow)


class DeviceProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: new_id("device"))
    platform: str
    python_version: str
    cpu_count: int
    ram_gb: float | None = None
    vram_gb: float | None = None
    gpu_summary: str | None = None
    thermal_mode: str = "unknown"
    ram_pressure: str = "unknown"
    vram_pressure: str = "unknown"
    safe_mode: bool = False
    max_context_tokens: int = 32768
    long_context_profile: dict[str, Any] = Field(default_factory=dict)
    local_first: bool = True
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class TokenBudgetProfile(BaseModel):
    profile_name: str = "default"
    summary_fraction: float = 0.5
    preview_fraction: float = 0.3
    instruction_fraction: float = 0.15
    reserve_fraction: float = 0.05


class RuntimeOptimizationCandidate(BaseModel):
    candidate_id: str = Field(default_factory=lambda: new_id("rtopt"))
    runtime_name: str
    model_id: str
    quantization: str
    estimated_latency_ms: float
    estimated_quality: float
    estimated_power: float
    source: str = "qes-shadow"
    lineage: ArtifactLineage = "live-derived"
    status_label: StatusLabel = "LOCKED CANON"


class QuantizationDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("qdec"))
    model_id: str
    selected_quantization: str
    rationale: str
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class BackendCapabilityCard(BaseModel):
    runtime_name: str
    backend_type: str
    status_label: StatusLabel
    local_first: bool = True
    supports_structured_output: bool = False
    supports_streaming: bool = False
    supports_gguf: bool = False
    supports_edge_portability: bool = False
    supports_tools: bool = False
    notes: list[str] = Field(default_factory=list)


class BackendSelectionDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("backend"))
    model_id: str
    selected_runtime_name: str
    fallback_runtime_names: list[str] = Field(default_factory=list)
    rationale: str
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class BenchmarkMatrixRecord(BaseModel):
    benchmark_id: str = Field(default_factory=lambda: new_id("qesbench"))
    model_id: str
    runtime_name: str
    metrics: dict[str, Any] = Field(default_factory=dict)
    lineage: ArtifactLineage = "live-derived"
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class PromotionCandidateRecord(BaseModel):
    candidate_id: str = Field(default_factory=lambda: new_id("promcand"))
    candidate_kind: PromotionCandidateKind
    subject_id: str
    baseline_reference: str
    challenger_reference: str
    lineage: ArtifactLineage = "live-derived"
    review_status: Literal["shadow", "review", "approved", "rejected"] = "shadow"
    status_label: StatusLabel = "LOCKED CANON"
    rollback_reference: str | None = None
    threshold_set_id: str | None = None
    teacher_evidence_bundle_id: str | None = None
    traceability: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class PromotionEvaluationRecord(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: new_id("promeval"))
    candidate_id: str
    candidate_kind: PromotionCandidateKind
    subject_id: str
    evaluator: str = "EvalsAO"
    decision: Literal["approved", "rejected", "shadow"] = "shadow"
    rationale: str
    baseline_reference: str
    challenger_reference: str
    scenario_set: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    threshold_set_id: str | None = None
    teacher_evidence_bundle_id: str | None = None
    artifacts: dict[str, str] = Field(default_factory=dict)
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class PromotionDecisionRecord(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("promdec"))
    candidate_id: str
    candidate_kind: PromotionCandidateKind
    subject_id: str
    evaluator_decision: Literal["approved", "rejected", "shadow"] = "shadow"
    governance_decision: Literal["approved", "rejected", "shadow"] = "shadow"
    decision: Literal["approved", "rejected", "shadow"] = "shadow"
    approver: str
    rationale: str
    rollback_reference: str | None = None
    threshold_set_id: str | None = None
    teacher_evidence_bundle_id: str | None = None
    artifacts: dict[str, str] = Field(default_factory=dict)
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class FederatedImprovementPackage(BaseModel):
    package_id: str = Field(default_factory=lambda: new_id("federated"))
    name: str
    candidate_kind: str
    artifact_path: str
    provenance: dict[str, Any] = Field(default_factory=dict)
    lineage: ArtifactLineage = "live-derived"
    status_label: StatusLabel = "STRONG ACCEPTED DIRECTION"
    created_at: datetime = Field(default_factory=utcnow)


class ReviewDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("review"))
    subject: str
    decision: Literal["approved", "rejected", "shadow"]
    reviewer: str
    rationale: str
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class IndependenceMetrics(BaseModel):
    dependency_ratio: float = 1.0
    native_generation: float = 0.0
    plane_maturity: dict[str, float] = Field(default_factory=dict)
    teacher_replacement_ready: bool = False
    created_at: datetime = Field(default_factory=utcnow)


class TeacherReplacementDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("replace"))
    teacher_id: str
    replacement_target: str
    decision: Literal["hold", "replace", "shadow"]
    rationale: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class StudentCheckpointRecord(BaseModel):
    checkpoint_id: str = Field(default_factory=lambda: new_id("student"))
    name: str
    artifact_path: str
    lineage: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class DistillationArtifactRecord(BaseModel):
    artifact_id: str = Field(default_factory=lambda: new_id("distillart"))
    name: str
    artifact_path: str
    source_kinds: list[str] = Field(default_factory=list)
    lineage: ArtifactLineage = "blended-derived"
    sample_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class NativePromotionDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("nativeprom"))
    subject: str
    decision: Literal["hold", "shadow", "promote"] = "hold"
    governed_action: Literal[
        "keep_teacher_fallback",
        "allow_native_shadow",
        "allow_native_challenger_shadow",
        "allow_native_live_guarded",
        "require_more_evidence",
        "hold_for_alignment",
        "rollback_to_teacher",
    ] = "require_more_evidence"
    execution_action: Literal[
        "keep_in_shadow",
        "promote_challenger_shadow",
        "allow_guarded_live",
        "fall_back_to_teacher",
        "require_more_evidence",
    ] = "require_more_evidence"
    rationale: str
    benchmark_summary: dict[str, Any] = Field(default_factory=dict)
    teacher_evidence: dict[str, Any] = Field(default_factory=dict)
    threshold_set_id: str | None = None
    takeover_scorecard_id: str | None = None
    takeover_trend_report_id: str | None = None
    fleet_summary_ids: list[str] = Field(default_factory=list)
    cohort_scorecard_ids: list[str] = Field(default_factory=list)
    replacement_readiness_report_id: str | None = None
    teacher_evidence_bundle_id: str | None = None
    rollback_reference: str | None = None
    governance_checks: dict[str, Any] = Field(default_factory=dict)
    evaluator_linkage: dict[str, Any] = Field(default_factory=dict)
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class CapabilityTakeoverRecord(BaseModel):
    takeover_id: str = Field(default_factory=lambda: new_id("takeover"))
    subject: str
    teacher_id: str
    internal_target: str
    decision: Literal["hold", "shadow", "takeover"] = "hold"
    rationale: str
    lineage: ArtifactLineage = "blended-derived"
    evidence: dict[str, Any] = Field(default_factory=dict)
    threshold_set_id: str | None = None
    teacher_evidence_bundle_id: str | None = None
    takeover_scorecard_id: str | None = None
    takeover_trend_report_id: str | None = None
    fleet_summary_ids: list[str] = Field(default_factory=list)
    cohort_scorecard_ids: list[str] = Field(default_factory=list)
    replacement_readiness_report_id: str | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class AgentCapabilityCard(BaseModel):
    agent_id: str
    label: str
    description: str
    modes: list[str] = Field(default_factory=list)
    policy_hooks: list[str] = Field(default_factory=list)
    status_label: StatusLabel
    tags: list[str] = Field(default_factory=list)


class AgentExecutionRecord(BaseModel):
    execution_id: str = Field(default_factory=lambda: new_id("agentexec"))
    agent_id: str
    session_id: str
    trace_id: str
    wrapper_mode: str
    selected_ao: str | None = None
    selected_backend: str | None = None
    selected_runtime: str | None = None
    policy_hooks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class SessionAgentProvenance(BaseModel):
    session_id: str
    active_agent_id: str | None = None
    executions: list[AgentExecutionRecord] = Field(default_factory=list)
    status_label: StatusLabel = "LOCKED CANON"


class GraphNodeRecord(BaseModel):
    node_id: str
    label: str
    node_type: str
    content: str = ""
    plane_tags: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    status_label: StatusLabel = "STRONG ACCEPTED DIRECTION"


class GraphEdgeRecord(BaseModel):
    edge_id: str = Field(default_factory=lambda: new_id("gedge"))
    source_node_id: str
    target_node_id: str
    relation: str
    weight: float = 1.0
    plane_tags: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    status_label: StatusLabel = "STRONG ACCEPTED DIRECTION"


class GraphIngestRequest(BaseModel):
    source: str
    text: str
    session_id: str | None = None
    plane_hint: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphProvenanceRecord(BaseModel):
    provenance_id: str = Field(default_factory=lambda: new_id("gprov"))
    source: str
    source_trace_id: str | None = None
    source_doc_id: str | None = None
    session_id: str | None = None
    plane_tags: list[str] = Field(default_factory=list)
    lineage: ArtifactLineage = "live-derived"
    validity: dict[str, Any] = Field(default_factory=dict)
    status_label: StatusLabel = "LOCKED CANON"


class GraphHit(BaseModel):
    node_id: str
    label: str
    content: str
    score: float
    plane_tags: list[str] = Field(default_factory=list)
    provenance: GraphProvenanceRecord | None = None


class FederatedUpdatePacket(BaseModel):
    packet_id: str = Field(default_factory=lambda: new_id("fedpkt"))
    client_id: str
    candidate_kind: str
    artifact_path: str
    metrics: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    lineage: ArtifactLineage = "live-derived"
    signature: str | None = None
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class GlobalImprovementCandidate(BaseModel):
    candidate_id: str = Field(default_factory=lambda: new_id("globalcand"))
    packet_id: str
    subject: str
    review_status: Literal["shadow", "review", "approved", "rejected"] = "shadow"
    provenance: dict[str, Any] = Field(default_factory=dict)
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class FederatedReviewDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("fedreview"))
    candidate_id: str
    decision: Literal["approved", "rejected", "shadow"] = "shadow"
    reviewer: str
    rationale: str
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class GlobalRolloutDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("rollout"))
    candidate_id: str
    decision: Literal["hold", "shadow", "rollout"] = "hold"
    rationale: str
    rollback_ready: bool = True
    status_label: StatusLabel = "LOCKED CANON"
    created_at: datetime = Field(default_factory=utcnow)


class WrapperMode(BaseModel):
    mode_id: str
    label: str
    description: str
    status_label: StatusLabel


class WrapperSurfaceState(BaseModel):
    active_model_id: str | None = None
    active_teacher_id: str | None = None
    active_ao: str | None = None
    active_agent_id: str | None = None
    selected_runtime_name: str | None = None
    selected_backend_name: str | None = None
    modes: list[WrapperMode] = Field(default_factory=list)


class BrainGenerateRequest(BaseModel):
    session_context: SessionContext
    prompt: str | None = None
    messages: list[Message] = Field(default_factory=list)
    model_hint: str | None = None
    success_conditions: list[str] = Field(default_factory=list)
