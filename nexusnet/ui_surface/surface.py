from __future__ import annotations

from nexus.memory import MemoryService
from nexus.schemas import MemoryQuery
from nexus.storage import NexusStore

from ..agents import BrainAgentRegistry
from ..aos import AssistantOrchestratorRegistry
from ..memory import MemoryPlaneRegistry
from ..runtime import BrainRuntimeRegistry
from ..runtime_optimizer import AdaptiveRuntimeProfiler
from ..schemas import WrapperMode, WrapperSurfaceState
from ..teachers import TeacherRegistry
from ..teachers.evidence import aggregate_teacher_evidence


def default_wrapper_modes() -> list[WrapperMode]:
    return [
        WrapperMode(
            mode_id="standard-chat",
            label="Standard Wrapper",
            description="Direct wrapped-model interaction through the NexusNet cognition layer.",
            status_label="LOCKED CANON",
        ),
        WrapperMode(
            mode_id="openclaw",
            label="OpenClaw Surface",
            description="Agentic wrapper mode for tool-heavy task execution and operator-style flows.",
            status_label="STRONG ACCEPTED DIRECTION",
        ),
        WrapperMode(
            mode_id="hermes-agent",
            label="Hermes Agent Surface",
            description="Agentic wrapper mode for guided task execution and broader assistant workflows.",
            status_label="STRONG ACCEPTED DIRECTION",
        ),
        WrapperMode(
            mode_id="scheduled-monitor",
            label="Scheduled Monitor Surface",
            description="Persistent monitoring workflow with memory, traceability, and governed approvals.",
            status_label="STRONG ACCEPTED DIRECTION",
        ),
    ]


class WrapperSurfaceService:
    def __init__(
        self,
        *,
        store: NexusStore,
        memory: MemoryService,
        teacher_registry: TeacherRegistry,
        ao_registry: AssistantOrchestratorRegistry,
        agent_registry: BrainAgentRegistry,
        memory_planes: MemoryPlaneRegistry,
        brain_runtime_registry: BrainRuntimeRegistry,
        brain_gateway: object | None = None,
        runtime_profiler: AdaptiveRuntimeProfiler,
        brain_runtime_init: object | None = None,
        brain_runtime_doctor: object | None = None,
        brain_edge_vision: object | None = None,
        brain_recipe_catalog: object | None = None,
        brain_recipe_history: object | None = None,
        brain_runbook_history: object | None = None,
        brain_skill_catalog: object | None = None,
        brain_extension_catalog: object | None = None,
        brain_skill_repository: object | None = None,
        brain_skill_evolution: object | None = None,
        brain_skill_refinement: object | None = None,
        brain_subagents: object | None = None,
        brain_delegation: object | None = None,
        brain_parallel: object | None = None,
        brain_acp_bridge: object | None = None,
        brain_permissions: object | None = None,
        brain_sandbox: object | None = None,
        brain_persistent_guardrails: object | None = None,
        brain_adversary_review: object | None = None,
        brain_agent_harness: object | None = None,
        brain_agent_teams: object | None = None,
        brain_scheduled_agents: object | None = None,
        brain_attention_registry: object | None = None,
        brain_attention_benchmarks: object | None = None,
        brain_cost_energy: object | None = None,
        brain_guardrail_analysis: object | None = None,
        brain_red_team_review: object | None = None,
        brain_red_team_evaluator: object | None = None,
        graph_service: object | None = None,
        federation_status_provider: object | None = None,
        foundry_status_provider: object | None = None,
        promotion_provider: object | None = None,
        retrieval_scorecard_provider: object | None = None,
        brain_core_summary_provider: object | None = None,
    ):
        self.store = store
        self.memory = memory
        self.teacher_registry = teacher_registry
        self.ao_registry = ao_registry
        self.agent_registry = agent_registry
        self.memory_planes = memory_planes
        self.brain_runtime_registry = brain_runtime_registry
        self.brain_gateway = brain_gateway
        self.runtime_profiler = runtime_profiler
        self.brain_runtime_init = brain_runtime_init
        self.brain_runtime_doctor = brain_runtime_doctor
        self.brain_edge_vision = brain_edge_vision
        self.brain_recipe_catalog = brain_recipe_catalog
        self.brain_recipe_history = brain_recipe_history
        self.brain_runbook_history = brain_runbook_history
        self.brain_skill_catalog = brain_skill_catalog
        self.brain_extension_catalog = brain_extension_catalog
        self.brain_skill_repository = brain_skill_repository
        self.brain_skill_evolution = brain_skill_evolution
        self.brain_skill_refinement = brain_skill_refinement
        self.brain_subagents = brain_subagents
        self.brain_delegation = brain_delegation
        self.brain_parallel = brain_parallel
        self.brain_acp_bridge = brain_acp_bridge
        self.brain_permissions = brain_permissions
        self.brain_sandbox = brain_sandbox
        self.brain_persistent_guardrails = brain_persistent_guardrails
        self.brain_adversary_review = brain_adversary_review
        self.brain_agent_harness = brain_agent_harness
        self.brain_agent_teams = brain_agent_teams
        self.brain_scheduled_agents = brain_scheduled_agents
        self.brain_attention_registry = brain_attention_registry
        self.brain_attention_benchmarks = brain_attention_benchmarks
        self.brain_cost_energy = brain_cost_energy
        self.brain_guardrail_analysis = brain_guardrail_analysis
        self.brain_red_team_review = brain_red_team_review
        self.brain_red_team_evaluator = brain_red_team_evaluator
        self.graph_service = graph_service
        self.federation_status_provider = federation_status_provider
        self.foundry_status_provider = foundry_status_provider
        self.promotion_provider = promotion_provider
        self.retrieval_scorecard_provider = retrieval_scorecard_provider
        self.brain_core_summary_provider = brain_core_summary_provider
        self._modes = default_wrapper_modes()

    def state(self, session_id: str | None = None) -> WrapperSurfaceState:
        active_teacher = self.teacher_registry.active_teacher()
        last_trace = self._last_trace(session_id)
        provenance = self.agent_registry.session_provenance(session_id) if session_id else None
        return WrapperSurfaceState(
            active_model_id=active_teacher.model_id if active_teacher else (last_trace.get("model_id") if last_trace else None),
            active_teacher_id=active_teacher.teacher_id if active_teacher else None,
            active_ao=last_trace.get("selected_ao") if last_trace else None,
            active_agent_id=provenance.active_agent_id if provenance else (last_trace.get("selected_agent") if last_trace else None),
            selected_runtime_name=((last_trace.get("runtime_selection") or {}).get("selected_runtime_name") if last_trace else None) or (last_trace.get("runtime_name") if last_trace else None),
            selected_backend_name=last_trace.get("runtime_name") if last_trace else None,
            modes=self._modes,
        )

    def snapshot(self, session_id: str | None = None) -> dict:
        last_trace = self._last_trace(session_id)
        live_core_summary = (
            self.brain_core_summary_provider(session_id=session_id)
            if callable(self.brain_core_summary_provider)
            else None
        )
        provenance = self.agent_registry.session_provenance(session_id) if session_id else None
        traces = self.store.list_traces(limit=50)
        teacher_traces = [trace for trace in traces if trace.get("teacher_provenance")]
        curriculum_records = self.store.list_curriculum_records(limit=100)
        teacher_evidence = aggregate_teacher_evidence(traces=teacher_traces, curriculum_records=curriculum_records)
        teacher_bundles = self.store.list_teacher_evidence_bundles(limit=50)
        disagreement_records = self.store.list_teacher_disagreement_artifacts(limit=50)
        teacher_scorecards = self.store.list_teacher_scorecards(limit=50)
        teacher_trends = self.store.list_teacher_trend_scorecards(limit=50)
        takeover_trends = self.store.list_takeover_trend_reports(limit=50)
        fleet_summaries = self.store.list_teacher_benchmark_fleet_summaries(limit=50)
        cohort_scorecards = self.store.list_teacher_cohort_scorecards(limit=50)
        replacement_readiness_reports = self.store.list_replacement_readiness_reports(limit=50)
        retirement_shadow_log = self.store.list_retirement_shadow_records(limit=50)
        recent_teacher_traces = [
            {
                "trace_id": trace.get("trace_id"),
                "session_id": trace.get("session_id"),
                "selected_teacher_id": trace.get("selected_teacher_id"),
                "registry_layer": (trace.get("teacher_provenance") or {}).get("registry_layer"),
                "selected_teacher_roles": (trace.get("teacher_provenance") or {}).get("selected_teacher_roles", {}),
                "arbitration_result": (trace.get("teacher_provenance") or {}).get("arbitration_result"),
                "benchmark_family": (trace.get("teacher_provenance") or {}).get("benchmark_family"),
                "threshold_set_id": (trace.get("teacher_provenance") or {}).get("threshold_set_id"),
                "native_takeover_candidate_id": (trace.get("teacher_provenance") or {}).get("native_takeover_candidate_id"),
            }
            for trace in teacher_traces[:20]
        ]
        if not recent_teacher_traces:
            recent_teacher_traces = [
                {
                    "trace_id": record.get("record_id"),
                    "session_id": record.get("subject"),
                    "selected_teacher_id": (record.get("detail", {}).get("teacher_flow", {}).get("selected_teacher_roles", {}) or {}).get("primary"),
                    "registry_layer": record.get("detail", {}).get("teacher_flow", {}).get("registry_layer"),
                    "selected_teacher_roles": record.get("detail", {}).get("teacher_flow", {}).get("selected_teacher_roles", {}),
                    "arbitration_result": record.get("detail", {}).get("teacher_flow", {}).get("arbitration_result"),
                    "benchmark_family": record.get("detail", {}).get("teacher_flow", {}).get("benchmark_family"),
                    "threshold_set_id": record.get("detail", {}).get("teacher_flow", {}).get("threshold_set_id"),
                    "bundle_id": record.get("detail", {}).get("teacher_flow", {}).get("bundle_id"),
                    "native_takeover_candidate_id": record.get("detail", {}).get("teacher_flow", {}).get("native_takeover_candidate_id"),
                }
                for record in curriculum_records[:20]
                if record.get("detail", {}).get("teacher_flow")
            ]
        recent_retrieval_traces = [
            {
                "trace_id": trace.get("trace_id"),
                "session_id": trace.get("session_id"),
                "retrieval_policy": trace.get("retrieval_policy"),
                "effective_policy": (trace.get("retrieval_policy_decision") or {}).get("effective_policy_mode")
                or trace.get("metrics", {}).get("retrieval_effective_policy"),
                "graph_contribution_count": trace.get("metrics", {}).get("graph_contribution_count", 0),
                "memory_contribution_count": trace.get("metrics", {}).get("memory_contribution_count", 0),
                "temporal_contribution_count": trace.get("metrics", {}).get("temporal_contribution_count", 0),
                "top_k_before_rerank": trace.get("metrics", {}).get("top_k_before_rerank", 0),
                "top_k_after_rerank": trace.get("metrics", {}).get("top_k_after_rerank", 0),
                "rerank_provider": trace.get("metrics", {}).get("rerank_provider"),
                "rerank_latency_delta_ms": trace.get("metrics", {}).get("rerank_latency_delta_ms", 0),
                "rerank_relevance_delta": trace.get("metrics", {}).get("rerank_relevance_delta", 0.0),
                "rerank_groundedness_delta": trace.get("metrics", {}).get("rerank_groundedness_delta", 0.0),
                "rerank_provenance_delta": trace.get("metrics", {}).get("rerank_provenance_delta", 0.0),
                "candidate_list_before_rerank": (trace.get("retrieval_policy_decision") or {}).get("candidate_list_before_rerank", []),
                "candidate_list_after_rerank": (trace.get("retrieval_policy_decision") or {}).get("candidate_list_after_rerank", []),
            }
            for trace in traces[:20]
            if trace.get("retrieval_policy")
        ]
        goose_recipe_summary = self.brain_recipe_catalog.summary() if self.brain_recipe_catalog is not None else None
        goose_recipe_history = self.brain_recipe_history.summary(execution_kind="recipe", limit=10) if self.brain_recipe_history is not None else None
        goose_runbook_history = self.brain_runbook_history.summary(limit=10) if self.brain_runbook_history is not None else None
        goose_gateway_summary = self.brain_gateway.summary(
            session_id=session_id,
            agent_id=(provenance.active_agent_id if provenance and provenance.active_agent_id else "standard-wrapper-agent"),
        ) if self.brain_gateway is not None else None
        goose_scheduled_summary = self.brain_scheduled_agents.summary() if self.brain_scheduled_agents is not None else None
        goose_acp_summary = self.brain_acp_bridge.summary() if self.brain_acp_bridge is not None else None
        goose_adversary_summary = self.brain_adversary_review.summary() if self.brain_adversary_review is not None else None
        goose_extension_summary = self.brain_extension_catalog.summary() if self.brain_extension_catalog is not None else None
        goose_extension_policy_sets = self.brain_extension_catalog.policy_set_summary() if self.brain_extension_catalog is not None else None
        goose_extension_policy_history = self.brain_extension_catalog.policy_history_summary() if self.brain_extension_catalog is not None else None
        goose_extension_policy_rollouts = self.brain_extension_catalog.policy_rollout_summary() if self.brain_extension_catalog is not None else None
        goose_extension_certifications = self.brain_extension_catalog.certification_summary() if self.brain_extension_catalog is not None else None
        snapshot = {
            "status_label": "LOCKED CANON",
            "state": self.state(session_id).model_dump(mode="json"),
            "recent_trace": last_trace,
            "core_execution": {
                "brain_first_execution": (
                    (live_core_summary or {}).get("brain_first_execution")
                    if live_core_summary is not None
                    else ((((last_trace.get("metrics") or {}).get("core_execution") or {}).get("brain_started_first")) if last_trace else None)
                ),
                "canonical_attach_seam": (
                    (live_core_summary or {}).get("canonical_attach_seam")
                    if live_core_summary is not None
                    else ((((last_trace.get("metrics") or {}).get("core_execution") or {}).get("canonical_attach_seam")) if last_trace else None)
                ),
                "latest_trace_id": (
                    (((live_core_summary or {}).get("traceability")) or {}).get("latest_trace_id")
                    if live_core_summary is not None
                    else (last_trace.get("trace_id") if last_trace else None)
                ),
                "latest_artifact_id": (
                    (((live_core_summary or {}).get("traceability")) or {}).get("latest_artifact_id")
                    if live_core_summary is not None
                    else ((((last_trace.get("metrics") or {}).get("core_execution") or {}).get("artifact_id")) if last_trace else None)
                ),
                "latest_artifact_path": (
                    (((live_core_summary or {}).get("traceability")) or {}).get("latest_artifact_path")
                    if live_core_summary is not None
                    else ((((last_trace.get("metrics") or {}).get("core_execution") or {}).get("artifact_path")) if last_trace else None)
                ),
                "selected_runtime_name": (
                    ((((live_core_summary or {}).get("runtime_execution_plan")) or {}).get("selected_runtime_name"))
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution") or {}).get("qes_execution_plan")) or {}).get("selected_runtime_name")) if last_trace else None)
                ),
                "memory_plane_count": (
                    (((live_core_summary or {}).get("memory_node")) or {}).get("plane_count")
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution") or {}).get("memory_node")) or {}).get("plane_count")) if last_trace else None)
                ),
                "fusion_backbone": (
                    (((live_core_summary or {}).get("fusion_scaffold")) or {}).get("backbone")
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution") or {}).get("fusion_scaffold")) or {}).get("backbone")) if last_trace else None)
                ),
                "evidence_feeds": (
                    (live_core_summary or {}).get("evidence_feeds")
                    if live_core_summary is not None
                    else ((((last_trace.get("metrics") or {}).get("core_execution") or {}).get("evidence_feeds")) if last_trace else None)
                ),
                "execution_mode": (
                    (((live_core_summary or {}).get("execution_policy")) or {}).get("execution_mode")
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("execution_policy")) or {}).get("execution_mode") if last_trace else None)
                ),
                "proposed_execution_mode": (
                    (((live_core_summary or {}).get("execution_policy")) or {}).get("proposed_execution_mode")
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("execution_policy")) or {}).get("proposed_execution_mode") if last_trace else None)
                ),
                "policy_id": (
                    (((live_core_summary or {}).get("execution_policy")) or {}).get("policy_id")
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("execution_policy")) or {}).get("policy_id") if last_trace else None)
                ),
                "native_execution_id": (
                    (((live_core_summary or {}).get("native_execution_preview")) or {}).get("execution_id")
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("native_execution")) or {}).get("execution_id") if last_trace else None)
                ),
                "promotion_action": (
                    (((live_core_summary or {}).get("promotion_linkage_preview")) or {}).get("execution_action")
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("promotion_linkage")) or {}).get("execution_action") if last_trace else None)
                ),
                "governed_action": (
                    (((live_core_summary or {}).get("promotion_linkage_preview")) or {}).get("governed_action")
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("promotion_linkage")) or {}).get("governed_action") if last_trace else None)
                ),
                "governed_action_source": (
                    (((live_core_summary or {}).get("promotion_linkage_preview")) or {}).get("governed_action_source")
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("promotion_linkage")) or {}).get("governed_action_source") if last_trace else None)
                ),
                "effective_execution_mode": (
                    (((live_core_summary or {}).get("promotion_linkage_preview")) or {}).get("effective_execution_mode")
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("promotion_linkage")) or {}).get("effective_execution_mode") if last_trace else None)
                ),
                "alignment_hold_required": (
                    (((live_core_summary or {}).get("promotion_linkage_preview")) or {}).get("alignment_hold_required")
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("promotion_linkage")) or {}).get("alignment_hold_required") if last_trace else None)
                ),
                "alignment_blockers": (
                    (((live_core_summary or {}).get("promotion_linkage_preview")) or {}).get("alignment_blockers", [])
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("promotion_linkage")) or {}).get("alignment_blockers", []) if last_trace else [])
                ),
                "native_candidate_id": (
                    (((((live_core_summary or {}).get("native_execution_preview")) or {}).get("native_candidate")) or {}).get("candidate_id")
                    if live_core_summary is not None
                    else ((((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("native_execution")) or {}).get("native_candidate")) or {}).get("candidate_id") if last_trace else None)
                ),
                "native_activation_mode": (
                    (((((live_core_summary or {}).get("native_execution_preview")) or {}).get("native_candidate")) or {}).get("activation_mode")
                    if live_core_summary is not None
                    else ((((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("native_execution")) or {}).get("native_candidate")) or {}).get("activation_mode") if last_trace else None)
                ),
                "promotion_decision_id": (
                    (((live_core_summary or {}).get("promotion_linkage_preview")) or {}).get("decision_id")
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("promotion_linkage")) or {}).get("decision_id") if last_trace else None)
                ),
                "behavior_next_step": (
                    ((((live_core_summary or {}).get("promotion_linkage_preview")) or {}).get("behavior_loop") or {}).get("next_step")
                    if live_core_summary is not None
                    else ((((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("promotion_linkage")) or {}).get("behavior_loop")) or {}).get("next_step") if last_trace else None)
                ),
                "fallback_triggers": (
                    (((live_core_summary or {}).get("execution_policy")) or {}).get("fallback_triggers", [])
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("execution_policy")) or {}).get("fallback_triggers", []) if last_trace else [])
                ),
                "internal_expert_ids": (
                    (((live_core_summary or {}).get("execution_policy")) or {}).get("selected_internal_experts", [])
                    if live_core_summary is not None
                    else ((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("execution_policy")) or {}).get("selected_internal_experts", []) if last_trace else [])
                ),
                "native_execution_verdict": (
                    ((((live_core_summary or {}).get("native_execution_preview")) or {}).get("teacher_comparison") or {}).get("verdict")
                    if live_core_summary is not None
                    else ((((((((last_trace.get("metrics") or {}).get("core_execution")) or {}).get("native_execution")) or {}).get("teacher_comparison")) or {}).get("verdict") if last_trace else None)
                ),
                "trace_detail_template": "/ops/traces/{trace_id}",
                "core_summary_ref": "/ops/brain/core",
            },
            "retrieval": {
                "status_label": "STRONG ACCEPTED DIRECTION",
                "config": {
                    "policy_mode_default": ((self.brain_runtime_registry.runtime_configs.get("retrieval", {}) or {}).get("policy_mode_default")),
                    "stage1": ((self.brain_runtime_registry.runtime_configs.get("retrieval", {}) or {}).get("stage1", {})),
                    "stage2": ((self.brain_runtime_registry.runtime_configs.get("retrieval", {}) or {}).get("stage2", {})),
                },
                "recent_traces": recent_retrieval_traces,
                "compare_refs": {
                    "rerank_benchmark": "/ops/brain/retrieval/rerank-benchmark",
                    "rerank_scorecard": "/ops/brain/retrieval/rerank-scorecard",
                    "promotion_evidence": "/ops/brain/retrieval/promotion-evidence",
                    "promotion_reviews": "/ops/brain/retrieval/promotion-reviews",
                    "promotion_review_detail_template": "/ops/brain/retrieval/promotion-reviews/{review_report_id}",
                },
                "scorecards": self.retrieval_scorecard_provider() if self.retrieval_scorecard_provider is not None else None,
                "promotion_evidence": [],
            },
            "gateway": goose_gateway_summary,
            "runtime_bootstrap": self.brain_runtime_init.summary() if self.brain_runtime_init is not None else None,
            "runtime_doctor": self.brain_runtime_doctor.summary() if self.brain_runtime_doctor is not None else None,
            "vision_edge": self.brain_edge_vision.summary() if self.brain_edge_vision is not None else None,
            "assimilation": {
                "goose": {
                    "recipes": {
                        **(goose_recipe_summary or {}),
                        "history": goose_recipe_history,
                        "runbook_history": goose_runbook_history,
                        "scheduled_history": (goose_scheduled_summary or {}).get("history"),
                        "compare_refs": {
                            "history": "/ops/brain/recipes/history",
                            "history_detail_template": "/ops/brain/recipes/history/{execution_id}",
                            "history_compare": "/ops/brain/recipes/history/compare",
                            "execute": "/ops/brain/recipes/execute",
                            "runbook_history": "/ops/brain/runbooks/history",
                            "runbook_history_detail_template": "/ops/brain/runbooks/history/{execution_id}",
                            "runbook_history_compare": "/ops/brain/runbooks/history/compare",
                            "runbook_execute": "/ops/brain/runbooks/execute",
                            "scheduled_history": "/ops/brain/agents/scheduled/history",
                            "scheduled_history_detail_template": "/ops/brain/agents/scheduled/history/{artifact_id}",
                        },
                    }
                    if goose_recipe_summary is not None
                    else None,
                    "gateway": goose_gateway_summary,
                    "extensions": goose_extension_summary,
                    "extension_policy_sets": goose_extension_policy_sets,
                    "extension_policy_history": goose_extension_policy_history,
                    "extension_policy_rollouts": goose_extension_policy_rollouts,
                    "extension_certifications": goose_extension_certifications,
                    "subagents": self.brain_subagents.summary() if self.brain_subagents is not None else None,
                    "delegation": self.brain_delegation.summary() if self.brain_delegation is not None else None,
                    "parallel": self.brain_parallel.summary() if self.brain_parallel is not None else None,
                    "acp": {
                        **(goose_acp_summary or {}),
                        "compare_refs": {
                            "summary": "/ops/brain/acp",
                            "health": "/ops/brain/acp/health",
                            "provider_detail_template": "/ops/brain/acp/providers/{provider_id}",
                            "provider_compare": "/ops/brain/acp/providers/compare",
                            "compatibility": "/ops/brain/acp/compatibility",
                        },
                    }
                    if goose_acp_summary is not None
                    else None,
                    "security": {
                        "permissions": self.brain_permissions.summary() if self.brain_permissions is not None else None,
                        "sandbox": self.brain_sandbox.summary() if self.brain_sandbox is not None else None,
                        "persistent_guardrails": self.brain_persistent_guardrails.summary() if self.brain_persistent_guardrails is not None else None,
                        "adversary_review": {
                            **(goose_adversary_summary or {}),
                            "compare_refs": {
                            "create_review": "/ops/brain/security/adversary-review",
                            "recent_reviews": "/ops/brain/security/adversary-reviews",
                            "review_detail_template": "/ops/brain/security/adversary-reviews/{review_id}",
                            "review_compare": "/ops/brain/security/adversary-reviews/compare",
                            "audit_export_template": "/ops/brain/security/adversary-reviews/{review_id}/audit-export",
                        },
                    }
                        if goose_adversary_summary is not None
                        else None,
                    },
                    "scheduled": goose_scheduled_summary,
                },
                "openjarvis_runtime": {
                    "init": self.brain_runtime_init.summary() if self.brain_runtime_init is not None else None,
                    "doctor": self.brain_runtime_doctor.summary() if self.brain_runtime_doctor is not None else None,
                    "skill_catalog": self.brain_skill_catalog.summary() if self.brain_skill_catalog is not None else None,
                    "scheduled_agents": goose_scheduled_summary,
                    "cost_energy": self.brain_cost_energy.summarize(traces[:50]) if self.brain_cost_energy is not None else None,
                },
                "skill_repository": self.brain_skill_repository.summary() if self.brain_skill_repository is not None else None,
                "skill_evolution": self.brain_skill_evolution.summarize_trajectories([]) if self.brain_skill_evolution is not None else None,
                "skill_refinement": self.brain_skill_refinement.propose(recurring_patterns=[]) if self.brain_skill_refinement is not None else None,
                "agent_harness": self.brain_agent_harness.summary() if self.brain_agent_harness is not None else None,
                "agent_teams": self.brain_agent_teams.summary() if self.brain_agent_teams is not None else None,
                "attention_research": self.brain_attention_registry.summary() if self.brain_attention_registry is not None else None,
                "attention_benchmarks": self.brain_attention_benchmarks.summary() if self.brain_attention_benchmarks is not None else None,
                "obliteratus_safe_boundary": {
                    "guardrail_analysis": self.brain_guardrail_analysis.summary() if self.brain_guardrail_analysis is not None else None,
                    "red_team_review": self.brain_red_team_review.summary() if self.brain_red_team_review is not None else None,
                    "red_team_eval": self.brain_red_team_evaluator.summary() if self.brain_red_team_evaluator is not None else None,
                },
            },
            "teachers": {
                "profiles": [profile.model_dump(mode="json") for profile in self.teacher_registry.list_profiles()],
                "attached": [teacher.model_dump(mode="json") for teacher in self.teacher_registry.list_attached()],
                "assignments": [assignment.model_dump(mode="json") for assignment in self.teacher_registry.list_assignments()],
                "metadata": self.teacher_registry.metadata(),
                "routing_policy": self.teacher_registry.routing_policy,
                "regimens": self.teacher_registry.regimens,
                "retirement": [decision.model_dump(mode="json") for decision in self.teacher_registry.retirement_decisions()],
                "visibility": {
                    "active_teacher_id": self.teacher_registry.active_teacher().teacher_id if self.teacher_registry.active_teacher() else None,
                    "teacher_evidence": teacher_evidence,
                    "recent_teacher_traces": recent_teacher_traces,
                    "benchmark_metadata": self.teacher_registry.benchmark_registry.metadata(),
                    "threshold_metadata": self.teacher_registry.threshold_registry.metadata(),
                    "schema_metadata": self.teacher_registry.schema_registry.metadata(),
                    "schema_manifest_path": self.teacher_registry.schema_manifest_path,
                    "evidence_bundles": teacher_bundles,
                    "disagreement_artifacts": disagreement_records,
                    "scorecards": teacher_scorecards,
                    "trend_scorecards": teacher_trends,
                    "takeover_trends": takeover_trends,
                    "fleet_summaries": fleet_summaries,
                    "cohort_scorecards": cohort_scorecards,
                    "replacement_readiness_reports": replacement_readiness_reports,
                    "retirement_shadow_log": retirement_shadow_log,
                    "inspection_controls": {
                        "registry_layers": sorted(self.teacher_registry.registry_layers.keys()),
                        "available_subjects": sorted({assignment.subject for assignment in self.teacher_registry.list_assignments()}),
                        "available_teacher_pairs": sorted(
                            {
                                "::".join(
                                    pair
                                    for pair in [
                                        assignment.primary_teacher_id,
                                        assignment.secondary_teacher_id,
                                    ]
                                    if pair
                                )
                                for assignment in self.teacher_registry.list_assignments()
                                if assignment.primary_teacher_id
                            }
                        ),
                        "available_fleets": self.teacher_registry.fleet_registry.metadata()["fleets"],
                        "available_windows": self.teacher_registry.fleet_window_registry.metadata()["windows"],
                        "trend_filters": ["subject", "benchmark_family_id", "teacher_id", "window_id"],
                        "cohort_filters": ["registry_layer", "expert_capsule", "teacher_pair", "hardware_class", "budget_class", "lineage"],
                        "compare_refs": {
                            "bundle_diff": "/ops/brain/teachers/evidence/diff",
                            "window_compare": "/ops/brain/teachers/cohorts/compare",
                            "disagreement_compare": "/ops/brain/visualizer/disagreements/compare",
                            "replacement_compare": "/ops/brain/visualizer/replacement-readiness/compare",
                            "route_compare": "/ops/brain/visualizer/route-activity/compare",
                            "replay": "/ops/brain/visualizer/replay",
                        },
                    },
                },
            },
            "aos": self.ao_registry.snapshot().model_dump(mode="json"),
            "agents": {
                "status_label": "LOCKED CANON",
                "capabilities": [capability.model_dump(mode="json") for capability in self.agent_registry.list_capabilities()],
                "session_provenance": self.agent_registry.session_provenance(session_id).model_dump(mode="json") if session_id else None,
            },
            "runtime": self.runtime_profiler.summary(),
            "brain_runtime": self.brain_runtime_registry.summary(),
            "memory_planes": {
                "metadata": self.memory_planes.metadata(),
                "configs": [config.model_dump(mode="json") for config in self.memory_planes.list_configs()],
                "projection_adapters": [adapter.model_dump(mode="json") for adapter in self.memory_planes.projection_adapters()],
            },
        }
        if self.graph_service is not None:
            snapshot["graph"] = self.graph_service.status()
        snapshot["assimilation"]["aitune"] = (snapshot.get("brain_runtime") or {}).get("aitune")
        snapshot["assimilation"]["compare_refs"] = {
            "aitune_execution_plan": "/ops/brain/aitune/execution-plan",
            "attention_comparative_summary": "/ops/brain/attention-providers/comparative-summary",
            "runtime_init": "/ops/brain/runtime/init",
            "runtime_doctor": "/ops/brain/runtime/doctor",
            "skill_catalog": "/ops/brain/skills/catalog",
            "scheduled_agents": "/ops/brain/agents/scheduled",
            "cost_energy": "/ops/brain/evals/cost-energy",
            "guardrail_analysis": "/ops/brain/research/guardrail-analysis",
            "refusal_circuit_review": "/ops/brain/research/refusal-circuit-review",
            "goose_recipes": "/ops/brain/recipes",
            "goose_runbooks": "/ops/brain/runbooks",
            "goose_recipe_history": "/ops/brain/recipes/history",
            "goose_recipe_history_compare": "/ops/brain/recipes/history/compare",
            "goose_runbook_history": "/ops/brain/runbooks/history",
            "goose_runbook_history_compare": "/ops/brain/runbooks/history/compare",
            "goose_gateway": "/ops/brain/gateway",
            "goose_gateway_history": "/ops/brain/gateway/history",
            "goose_gateway_history_detail_template": "/ops/brain/gateway/history/{execution_id}",
            "goose_gateway_history_compare": "/ops/brain/gateway/history/compare",
            "goose_extensions": "/ops/brain/extensions",
            "goose_extension_detail_template": "/ops/brain/extensions/{bundle_id}",
            "goose_extension_policy_sets": "/ops/brain/extensions/policy-sets",
            "goose_extension_policy_set_detail_template": "/ops/brain/extensions/policy-sets/{policy_set_id}",
            "goose_extension_policy_history": "/ops/brain/extensions/policy-history",
            "goose_extension_policy_history_detail_template": "/ops/brain/extensions/policy-history/{policy_set_id}",
            "goose_extension_policy_history_compare": "/ops/brain/extensions/policy-history/compare",
            "goose_extension_policy_rollouts": "/ops/brain/extensions/policy-rollouts",
            "goose_extension_certifications": "/ops/brain/extensions/certifications",
            "goose_extension_certification_detail_template": "/ops/brain/extensions/certifications/{artifact_id}",
            "goose_extension_certification_compare": "/ops/brain/extensions/certifications/compare",
            "goose_acp": "/ops/brain/acp",
            "goose_acp_health": "/ops/brain/acp/health",
            "goose_acp_provider_detail_template": "/ops/brain/acp/providers/{provider_id}",
            "goose_acp_provider_compare": "/ops/brain/acp/providers/compare",
            "goose_acp_compatibility": "/ops/brain/acp/compatibility",
            "goose_subagents": "/ops/brain/subagents",
            "goose_scheduled_history": "/ops/brain/agents/scheduled/history",
            "goose_security_permissions": "/ops/brain/security/permissions",
            "goose_security_sandbox": "/ops/brain/security/sandbox",
            "goose_security_adversary_reviews": "/ops/brain/security/adversary-reviews",
            "goose_security_adversary_review_detail_template": "/ops/brain/security/adversary-reviews/{review_id}",
            "goose_security_adversary_review_compare": "/ops/brain/security/adversary-reviews/compare",
            "goose_security_adversary_audit_export_template": "/ops/brain/security/adversary-reviews/{review_id}/audit-export",
        }
        snapshot["assimilation"]["compare_groups"] = {
            "goose_compare": {
                "group_names": [
                    "policy-lifecycle",
                    "certification-state",
                    "permission-deltas",
                    "approval-fallback",
                    "acp-readiness",
                    "adversary-outcome",
                    "gateway-execution-path",
                    "trace-and-artifacts",
                ],
                "group_descriptions": {
                    "policy-lifecycle": "status, version, rollback, and lineage deltas",
                    "certification-state": "certification, restoration, and lineage state changes",
                    "permission-deltas": "allowed-tool, permission, and privilege drift",
                    "approval-fallback": "approval posture and fallback-chain changes",
                    "acp-readiness": "probe, capability, version, and remediation deltas",
                    "adversary-outcome": "risk-family and decision-path changes",
                    "gateway-execution-path": "trigger, flow-family, extension, and traceability changes",
                    "trace-and-artifacts": "trace, report, and produced-artifact drift",
                },
                "default_expanded_groups": [
                    "policy-lifecycle",
                    "certification-state",
                    "acp-readiness",
                ],
                "collapse_actions": [
                    "expand-all",
                    "collapse-all",
                    "default-expanded",
                ],
            }
        }
        if self.federation_status_provider is not None:
            snapshot["federation"] = self.federation_status_provider()
        if self.foundry_status_provider is not None:
            snapshot["foundry"] = self.foundry_status_provider()
        if self.promotion_provider is not None:
            snapshot["promotions"] = self.promotion_provider()
        if "promotions" in snapshot:
            snapshot["promotions"]["teacher_evidence"] = [
                {
                    "candidate_id": item["candidate"]["candidate_id"],
                    "candidate_kind": item["candidate"]["candidate_kind"],
                    "teacher_evidence_bundle_id": item["candidate"].get("teacher_evidence_bundle_id"),
                    "threshold_set_id": item["candidate"].get("threshold_set_id"),
                    "teacher_evidence": item["candidate"]["traceability"].get("teacher_evidence", {}),
                    "takeover_trend_report": item["candidate"]["traceability"].get("benchmark", {}).get("takeover_trend_report"),
                    "fleet_summaries": item["candidate"]["traceability"].get("benchmark", {}).get("fleet_summaries", []),
                    "cohort_scorecards": item["candidate"]["traceability"].get("benchmark", {}).get("cohort_scorecards", []),
                    "replacement_readiness": item["candidate"]["traceability"].get("benchmark", {}).get("replacement_readiness"),
                }
                for item in snapshot["promotions"].get("items", [])
                if item["candidate"]["traceability"].get("teacher_evidence")
            ]
            snapshot["retrieval"]["promotion_evidence"] = []
            for item in snapshot["promotions"].get("items", []):
                if not item["candidate"]["traceability"].get("retrieval_rerank_evidence"):
                    continue
                evaluation_artifacts = item.get("latest_evaluation", {}).get("artifacts", {}) if item.get("latest_evaluation") else {}
                snapshot["retrieval"]["promotion_evidence"].append(
                    {
                        "candidate_id": item["candidate"]["candidate_id"],
                        "candidate_kind": item["candidate"]["candidate_kind"],
                        "subject_id": item["candidate"]["subject_id"],
                        "bundle_id": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("bundle_id"),
                        "scorecard_id": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("scorecard_id"),
                        "benchmark_family_id": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("benchmark_family_id"),
                        "threshold_set_id": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("threshold_set_id"),
                        "scorecard_passed": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("scorecard_passed"),
                        "artifact_path": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("artifact_path"),
                        "review_report_id": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("review_report_id"),
                        "review_headline": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("review_headline"),
                        "review_summary": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("review_summary", []),
                        "human_summary": (item["candidate"]["traceability"].get("retrieval_rerank_review") or {}).get("human_summary"),
                        "review_badges": (item["candidate"]["traceability"].get("retrieval_rerank_review") or {}).get("review_badges", {}),
                        "candidate_shift_count": (((item["candidate"]["traceability"].get("retrieval_rerank_review") or {}).get("candidate_shift_summary")) or {}).get("changed_count", 0),
                        "candidate_shift_summary": (item["candidate"]["traceability"].get("retrieval_rerank_review") or {}).get("candidate_shift_summary", {}),
                        "top_shift_preview": (item["candidate"]["traceability"].get("retrieval_rerank_review") or {}).get("top_shift_preview"),
                        "delta_summary": (item["candidate"]["traceability"].get("retrieval_rerank_review") or {}).get("delta_summary", {}),
                        "threshold_summary": (item["candidate"]["traceability"].get("retrieval_rerank_review") or {}).get("threshold_summary", {}),
                        "evaluator_artifact_summary": {
                            "artifact_count": len(evaluation_artifacts),
                            "artifact_ids": sorted(evaluation_artifacts.keys()),
                        },
                        "review_artifacts": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("review_artifacts", {}),
                        "reranker_provider": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("reranker_provider"),
                        "latency_delta_ms": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("latency_delta_ms"),
                        "relevance_delta": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("relevance_delta"),
                        "groundedness_delta": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("groundedness_delta"),
                        "provenance_delta": item["candidate"]["traceability"].get("retrieval_rerank_evidence", {}).get("provenance_delta"),
                        "evaluation_artifacts": evaluation_artifacts,
                        "latest_evaluation_decision": item.get("latest_evaluation", {}).get("decision") if item.get("latest_evaluation") else None,
                    }
                )
        goose = (snapshot.get("assimilation") or {}).get("goose") or {}
        snapshot["goose"] = {
            "recipes": goose.get("recipes"),
            "gateway": goose.get("gateway"),
            "extensions": goose.get("extensions"),
            "extension_policy_sets": goose.get("extension_policy_sets"),
            "extension_policy_history": goose.get("extension_policy_history"),
            "extension_policy_rollouts": goose.get("extension_policy_rollouts"),
            "extension_certifications": goose.get("extension_certifications"),
            "subagents": goose.get("subagents"),
            "delegation": goose.get("delegation"),
            "parallel": goose.get("parallel"),
            "scheduled": goose.get("scheduled"),
            "acp": goose.get("acp"),
            "security": goose.get("security"),
        }
        if session_id:
            records = self.memory.query(MemoryQuery(session_id=session_id, limit=500))
            snapshot["memory"] = self.memory.session_view(session_id)
            snapshot["memory"]["canonical_planes"] = self.memory_planes.canonical_groups(records)
        return snapshot

    def projection(self, session_id: str, projection_name: str) -> dict:
        records = self.memory.query(MemoryQuery(session_id=session_id, limit=500))
        return self.memory_planes.project(projection_name, records).model_dump(mode="json")

    def _last_trace(self, session_id: str | None) -> dict | None:
        traces = self.store.list_traces(limit=100)
        if session_id:
            for trace in traces:
                if trace.get("session_id") == session_id:
                    return trace
            return None
        return traces[0] if traces else None
