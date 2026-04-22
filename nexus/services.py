from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agents import build_default_agent_registry
from .ao import build_default_ao_registry
from .config import VERSION, build_paths, ensure_paths, load_runtime_configs
from .critique import CritiqueEngine
from .curriculum import CurriculumRegistrar
from .doctor import build_doctor_report
from .dreaming import DreamShadowPool
from .experiments import ExperimentService
from .foundry import DatasetRefinery
from .governance import GovernanceService
from .manifest import build_workspace_manifest
from .memory import MemoryService
from .models import ModelRegistry
from .operator import OperatorKernel
from .operator.routing import ExpertSelector
from .permissions import PermissionContext
from .retrieval import RetrievalService
from .runtimes import RuntimeRegistry
from .storage import NexusStore
from .tools import ToolRegistry
from nexusnet.agents.delegation import DelegationPlanner
from nexusnet.agents.parallel import ParallelExecutionAdvisor
from nexusnet.agents.subagents import SubagentExecutionService
from nexusnet.agents import BrainAgentRegistry
from nexusnet.agents.scheduled import ScheduledAgentService
from nexusnet.aos import build_default_ao_registry as build_brain_ao_registry
from nexusnet.core import CoreEvidenceBridge, NexusBrain
from nexusnet.curriculum import CurriculumEngine
from nexusnet.curriculum.skill_refinement import SkillRefinementService
from nexusnet.distillation import DistillationDatasetBuilder
from nexusnet.dreaming import RecursiveDreamEngine
from nexusnet.evals.cost_energy import CostEnergyEvaluationService
from nexusnet.evals.red_team import RedTeamEvidenceService
from nexusnet.evals.red_team.gateway_scenarios import GatewayScenarioCatalog
from nexusnet.evals import ExternalBehaviorEvaluator
from nexusnet.federation import FederatedReviewGate, GlobalRolloutPlanner
from nexusnet.federation.skills import GovernedSkillRepository
from nexusnet.federation.flower import FlowerCoordinator, FlowerSimulationHarness
from nexusnet.foundry import (
    CohortTakeoverAnalyzer,
    FoundryBenchmarkSuite,
    FoundryRefinery,
    FoundryRetirementHooks,
    NativePromotionGate,
    ReplacementCohortAnalyzer,
    ReplacementReadinessAdvisor,
)
from nexusnet.foundry.takeover_trends import TakeoverTrendAnalyzer
from nexusnet.graph.store import LocalGraphStore
from nexusnet.memory import MemoryNode, MemoryPlaneRegistry
from nexusnet.promotions import PromotionCohortGate, PromotionService, TeacherEvidenceService
from nexusnet.promotions.trend_gating import PromotionTrendGate
from nexusnet.memory.graph_bridge import MemoryGraphBridge
from nexusnet.guardrails.persistent_instructions import PersistentGuardrailService
from nexusnet.providers.acp import ACPProviderCatalog
from nexusnet.recipes import RecipeCatalogService, RecipeExecutionStore, RecipeHistoryService
from nexusnet.runbooks.history import RunbookHistoryService
from nexusnet.retrieval.graphrag import GraphRAGEvaluator, GraphRAGIngestionService, GraphRAGRetriever
from nexusnet.retrieval.evals import RetrievalRerankBenchmarkSuite
from nexusnet.retrieval.rerank import RetrievalRerankOperationalBenchmarkSuite, RetrievalRerankPromotionBridge
from nexusnet.reflection import MetaReflectionEngine
from nexusnet.runtime.acp import ACPBridgeService
from nexusnet.runtime import BrainRuntimeRegistry
from nexusnet.runtime.doctor import RuntimeDoctorService
from nexusnet.runtime.gateway import LocalRuntimeGateway
from nexusnet.runtime.init import RuntimeBootstrapService
from nexusnet.runtime.sandbox import SandboxPolicyService
from nexusnet.runtime_optimizer import AdaptiveRuntimeProfiler
from nexusnet.teachers import (
    TeacherBenchmarkFleetAnalyzer,
    TeacherCohortAnalyzer,
    TeacherRegistry,
    TeacherSchemaMigrationHelper,
)
from nexusnet.teachers.trends import TeacherTrendAnalyzer
from nexusnet.temporal.retriever import TemporalRetriever
from nexusnet.tools import ExtensionCatalogService, GatewayApprovalService, GatewayPolicyEngine, SkillCatalogService, SkillPackageRegistry
from nexusnet.tools.adversary_review import AdversaryReviewService
from nexusnet.tools.permissions import ToolPermissionService
from nexusnet.tools.skill_evolution import SkillEvolutionLab
from nexusnet.ui_surface import WrapperSurfaceService
from nexusnet.visuals import NexusVisualizerService
from nexusnet.vision import EdgeVisionLaneService
from nexusnet.benchmarks.agent_harness import AgentHarnessBenchmarkCatalog
from nexusnet.agents.teams import AgentTeamRegistry
from research.interpretability.guardrail_analysis import GuardrailAnalysisService
from research.red_team.refusal_circuit_review import RefusalCircuitReviewService
from research.attention_providers import AttentionBenchmarkSuite, AttentionProviderRegistry


@dataclass
class NexusServices:
    version: str
    paths: Any
    runtime_configs: dict[str, Any]
    permission_context: PermissionContext
    store: NexusStore
    ao_registry: Any
    agent_registry: Any
    runtime_registry: RuntimeRegistry
    model_registry: ModelRegistry
    memory: MemoryService
    retrieval: RetrievalService
    critique: CritiqueEngine
    governance: GovernanceService
    experiments: ExperimentService
    curriculum: CurriculumRegistrar
    dreaming: DreamShadowPool
    foundry: DatasetRefinery
    tool_registry: ToolRegistry
    brain: NexusBrain
    brain_teachers: TeacherRegistry
    brain_aos: Any
    brain_agent_registry: BrainAgentRegistry
    brain_memory_node: MemoryNode
    brain_memory_planes: MemoryPlaneRegistry
    brain_runtime_registry: BrainRuntimeRegistry
    brain_gateway: Any
    brain_runtime_optimizer: AdaptiveRuntimeProfiler
    brain_runtime_init: Any
    brain_runtime_doctor: Any
    brain_edge_vision: Any
    brain_recipe_catalog: Any
    brain_recipe_history: Any
    brain_runbook_history: Any
    brain_skill_catalog: Any
    brain_extension_catalog: Any
    brain_skill_repository: Any
    brain_skill_evolution: Any
    brain_skill_refinement: Any
    brain_subagents: Any
    brain_delegation: Any
    brain_parallel: Any
    brain_acp_bridge: Any
    brain_permissions: Any
    brain_sandbox: Any
    brain_persistent_guardrails: Any
    brain_adversary_review: Any
    brain_agent_harness: Any
    brain_agent_teams: Any
    brain_scheduled_agents: Any
    brain_attention_registry: Any
    brain_attention_benchmarks: Any
    brain_cost_energy: Any
    brain_guardrail_analysis: Any
    brain_red_team_review: Any
    brain_red_team_evaluator: Any
    brain_ui_surface: WrapperSurfaceService
    brain_evaluator: ExternalBehaviorEvaluator
    brain_dreaming: RecursiveDreamEngine
    brain_reflection: MetaReflectionEngine
    brain_curriculum: CurriculumEngine
    brain_distillation: DistillationDatasetBuilder
    brain_graph_ingestion: Any
    brain_graph_retriever: Any
    brain_graph_evaluator: Any
    brain_federation_coordinator: Any
    brain_federation_simulation: Any
    brain_federation_review_gate: Any
    brain_global_rollout: Any
    brain_foundry_refinery: Any
    brain_foundry_benchmarks: Any
    brain_foundry_promotion: Any
    brain_foundry_retirement: Any
    brain_promotions: Any
    brain_teacher_evidence: Any
    brain_teacher_trends: Any
    brain_takeover_trends: Any
    brain_promotion_trend_gate: Any
    brain_teacher_fleets: Any
    brain_teacher_cohorts: Any
    brain_promotion_cohort_gate: Any
    brain_retrieval_rerank_bench: Any
    brain_retrieval_rerank_ops: Any
    brain_visualizer: Any
    operator: OperatorKernel

    def doctor_report(self) -> dict[str, Any]:
        profiles = [profile.model_dump(mode="json") for profile in self.runtime_registry.list_profiles()]
        return build_doctor_report(
            paths=self.paths,
            runtime_profiles=profiles,
            model_count=len(self.model_registry.list_models()),
            tool_count=len(self.tool_registry.list()),
        )

    def workspace_manifest(self) -> str:
        return build_workspace_manifest(self)


def build_services(project_root: str | None = None) -> NexusServices:
    paths = ensure_paths(build_paths(project_root))
    runtime_configs = load_runtime_configs(paths)
    overrides = runtime_configs.get("overrides", {})
    permissions_cfg = overrides.get("permissions", {})
    permission_context = PermissionContext(
        mode=permissions_cfg.get("mode", "workspace-write"),
        allowed_tools=set(permissions_cfg.get("allowed_tools", [])),
        denied_tools=set(permissions_cfg.get("denied_tools", [])),
    )

    store = NexusStore(paths)
    ao_registry = build_default_ao_registry()
    brain_aos = build_brain_ao_registry()
    agent_registry = build_default_agent_registry()
    tool_registry = ToolRegistry()
    runtime_registry = RuntimeRegistry(paths, store, runtime_configs)
    runtime_registry.bootstrap()
    model_registry = ModelRegistry(store, runtime_registry, runtime_configs)
    model_registry.bootstrap()
    memory = MemoryService(paths, store)
    brain_memory_node = MemoryNode(project_root=paths.project_root, runtime_configs=runtime_configs)
    runtime_configs["planes"] = brain_memory_node.summary()["raw_config"]
    brain_memory_planes = brain_memory_node.registry
    brain_runtime_registry = BrainRuntimeRegistry(
        runtime_registry=runtime_registry,
        model_registry=model_registry,
        runtime_configs=runtime_configs,
        config_dir=paths.config_dir,
        artifacts_dir=paths.artifacts_dir,
    )
    brain_teachers = TeacherRegistry(model_registry, paths.config_dir)
    teacher_schema_manifest = TeacherSchemaMigrationHelper(config_dir=paths.config_dir, state_dir=paths.state_dir).ensure_manifest()
    brain_teachers.schema_manifest_path = teacher_schema_manifest["path"]
    graph_store = LocalGraphStore(paths.artifacts_dir)
    graph_bridge = MemoryGraphBridge(brain_memory_planes)
    brain_graph_ingestion = GraphRAGIngestionService(store=graph_store, graph_bridge=graph_bridge)
    brain_graph_retriever = GraphRAGRetriever(graph_store)
    brain_graph_evaluator = GraphRAGEvaluator()
    temporal_cfg = (runtime_configs.get("rag", {}) or {}).get("temporal", {}) or {}
    temporal_retriever = (
        TemporalRetriever(str(paths.runtime_dir / "temporal" / "tkg.sqlite"))
        if temporal_cfg.get("enabled", False)
        else None
    )
    retrieval = RetrievalService(
        paths,
        store,
        graph_retriever=brain_graph_retriever,
        graph_service=graph_store,
        memory_service=memory,
        temporal_retriever=temporal_retriever,
        retrieval_config=runtime_configs.get("retrieval", {}),
    )
    critique = CritiqueEngine(store)
    governance = GovernanceService(paths, store)
    experiments = ExperimentService(store)
    curriculum = CurriculumRegistrar(store)
    dreaming = DreamShadowPool(paths)
    foundry = DatasetRefinery(paths)
    brain = NexusBrain(
        paths=paths,
        store=store,
        runtime_registry=runtime_registry,
        model_registry=model_registry,
        memory=memory,
        retrieval=retrieval,
        critique=critique,
        brain_runtime_registry=brain_runtime_registry,
        teacher_registry=brain_teachers,
        memory_node=brain_memory_node,
    )
    brain.wake()
    brain.bootstrap_from_registry()
    brain_teacher_evidence = TeacherEvidenceService(
        store=store,
        artifacts_dir=paths.artifacts_dir,
        benchmark_registry=brain_teachers.benchmark_registry,
        schema_registry=brain_teachers.schema_registry,
    )
    brain_teacher_trends = TeacherTrendAnalyzer(
        store=store,
        artifacts_dir=paths.artifacts_dir,
        schema_registry=brain_teachers.schema_registry,
    )
    brain_takeover_trends = TakeoverTrendAnalyzer(
        store=store,
        artifacts_dir=paths.artifacts_dir,
        schema_registry=brain_teachers.schema_registry,
    )
    brain_promotion_trend_gate = PromotionTrendGate(
        teacher_trends=brain_teacher_trends,
        takeover_trends=brain_takeover_trends,
    )
    brain_teacher_fleets = TeacherBenchmarkFleetAnalyzer(
        store=store,
        artifacts_dir=paths.artifacts_dir,
        fleet_registry=brain_teachers.fleet_registry,
        window_registry=brain_teachers.fleet_window_registry,
        schema_registry=brain_teachers.schema_registry,
    )
    brain_teacher_cohorts = TeacherCohortAnalyzer(
        store=store,
        artifacts_dir=paths.artifacts_dir,
        fleet_analyzer=brain_teacher_fleets,
        threshold_registry=brain_teachers.cohort_threshold_registry,
        schema_registry=brain_teachers.schema_registry,
    )
    brain_retrieval_rerank_bench = RetrievalRerankBenchmarkSuite(
        artifacts_dir=paths.artifacts_dir,
        retrieval_service=retrieval,
    )
    brain_retrieval_rerank_ops = RetrievalRerankOperationalBenchmarkSuite(
        artifacts_dir=paths.artifacts_dir,
        retrieval_service=retrieval,
        retrieval_config=runtime_configs.get("retrieval", {}),
    )
    brain_retrieval_rerank_promotion = RetrievalRerankPromotionBridge(
        artifacts_dir=paths.artifacts_dir,
        retrieval_operational_bench=brain_retrieval_rerank_ops,
    )
    brain_replacement_cohorts = ReplacementCohortAnalyzer(
        fleet_registry=brain_teachers.fleet_registry,
        cohorts=brain_teacher_cohorts,
    )
    brain_replacement_readiness = ReplacementReadinessAdvisor()
    brain_promotion_cohort_gate = PromotionCohortGate(
        fleet_registry=brain_teachers.fleet_registry,
        fleet_analyzer=brain_teacher_fleets,
        replacement_cohorts=brain_replacement_cohorts,
        readiness=brain_replacement_readiness,
    )
    brain_agent_registry = BrainAgentRegistry(artifacts_dir=paths.artifacts_dir)
    brain_recipe_catalog = RecipeCatalogService(
        config_dir=paths.config_dir,
        runtime_configs=runtime_configs,
    )
    brain_recipe_execution_store = RecipeExecutionStore(artifacts_dir=paths.artifacts_dir)
    brain_recipe_history = RecipeHistoryService(
        execution_store=brain_recipe_execution_store,
        recipe_catalog=brain_recipe_catalog,
        artifacts_dir=paths.artifacts_dir,
    )
    brain_runbook_history = RunbookHistoryService(
        recipe_history=brain_recipe_history,
        recipe_catalog=brain_recipe_catalog,
        artifacts_dir=paths.artifacts_dir,
    )
    skill_registry = SkillPackageRegistry()
    brain_permissions = ToolPermissionService(permission_mode=permission_context.mode, runtime_configs=runtime_configs)
    brain_sandbox = SandboxPolicyService(runtime_configs=runtime_configs, permission_mode=permission_context.mode)
    brain_persistent_guardrails = PersistentGuardrailService(runtime_configs=runtime_configs)
    brain_adversary_review = AdversaryReviewService(artifacts_dir=paths.artifacts_dir, runtime_configs=runtime_configs)
    brain_acp_bridge = ACPBridgeService(
        catalog=ACPProviderCatalog(runtime_configs=runtime_configs),
        artifacts_dir=str(paths.artifacts_dir),
    )
    brain_extension_catalog = ExtensionCatalogService(
        runtime_configs=runtime_configs,
        project_root=str(paths.project_root),
        artifacts_dir=str(paths.artifacts_dir),
        permission_service=brain_permissions,
        sandbox_service=brain_sandbox,
        acp_bridge=brain_acp_bridge,
        adversary_review=brain_adversary_review,
    )
    brain_skill_catalog = SkillCatalogService(
        skill_registry=skill_registry,
        store=store,
        config=runtime_configs.get("openjarvis_lane", {}),
        extension_catalog=brain_extension_catalog,
    )
    brain_gateway = LocalRuntimeGateway(
        skill_registry=skill_registry,
        policy_engine=GatewayPolicyEngine(),
        approvals=GatewayApprovalService(store=store),
        skill_catalog=brain_skill_catalog,
        extension_catalog=brain_extension_catalog,
        permission_service=brain_permissions,
        sandbox_service=brain_sandbox,
        guardrail_service=brain_persistent_guardrails,
        adversary_review=brain_adversary_review,
        execution_store=brain_recipe_execution_store,
        artifacts_dir=paths.artifacts_dir,
    )
    brain_runtime_optimizer = AdaptiveRuntimeProfiler(runtime_registry, model_registry, runtime_configs)
    brain_edge_vision = EdgeVisionLaneService(
        config_dir=paths.config_dir,
        artifacts_dir=paths.artifacts_dir,
        runtime_configs=runtime_configs,
    )
    brain_runtime_init = RuntimeBootstrapService(
        config_dir=paths.config_dir,
        runtime_configs=runtime_configs,
        runtime_registry=runtime_registry,
        model_registry=model_registry,
        runtime_profiler=brain_runtime_optimizer,
        edge_vision_service=brain_edge_vision,
    )
    brain_runtime_doctor = RuntimeDoctorService(
        config_dir=paths.config_dir,
        runtime_configs=runtime_configs,
        runtime_registry=runtime_registry,
        runtime_profiler=brain_runtime_optimizer,
        init_service=brain_runtime_init,
        edge_vision_service=brain_edge_vision,
    )
    brain_skill_repository = GovernedSkillRepository()
    brain_skill_evolution = SkillEvolutionLab()
    brain_skill_refinement = SkillRefinementService()
    brain_subagents = SubagentExecutionService(
        artifacts_dir=paths.artifacts_dir,
        runtime_configs=runtime_configs,
    )
    brain_delegation = DelegationPlanner(
        recipe_service=brain_recipe_catalog,
        extension_catalog=brain_extension_catalog,
    )
    brain_parallel = ParallelExecutionAdvisor(
        max_parallel=int((((runtime_configs.get("goose_lane") or {}).get("subagents") or {}).get("max_parallel", 1))),
    )
    brain_agent_harness = AgentHarnessBenchmarkCatalog()
    brain_agent_teams = AgentTeamRegistry()
    brain_scheduled_agents = ScheduledAgentService(
        config_dir=paths.config_dir,
        runtime_configs=runtime_configs,
        store=store,
        artifacts_dir=paths.artifacts_dir,
        execution_store=brain_recipe_execution_store,
    )
    brain_attention_registry = AttentionProviderRegistry(features=runtime_configs.get("features", {}))
    brain_attention_benchmarks = AttentionBenchmarkSuite(
        artifacts_dir=paths.artifacts_dir,
        registry=brain_attention_registry,
        runtime_profile_provider=lambda: [profile.model_dump(mode="json") for profile in runtime_registry.list_profiles()],
        retrieval_config=runtime_configs.get("retrieval", {}),
    )
    brain_cost_energy = CostEnergyEvaluationService(config_dir=paths.config_dir, runtime_configs=runtime_configs)
    brain_guardrail_analysis = GuardrailAnalysisService(artifacts_dir=paths.artifacts_dir)
    brain_red_team_review = RefusalCircuitReviewService(
        artifacts_dir=paths.artifacts_dir,
        guardrail_analysis=brain_guardrail_analysis,
    )
    brain_gateway_scenarios = GatewayScenarioCatalog()
    brain_red_team_evaluator = RedTeamEvidenceService(
        review_service=brain_red_team_review,
        gateway_scenarios=brain_gateway_scenarios,
    )
    brain_foundry_refinery = FoundryRefinery(paths.artifacts_dir)
    brain_foundry_benchmarks = FoundryBenchmarkSuite(
        store=store,
        artifacts_dir=paths.artifacts_dir,
        schema_registry=brain_teachers.schema_registry,
        cohort_takeover=CohortTakeoverAnalyzer(replacement_cohorts=brain_replacement_cohorts),
        replacement_readiness=brain_replacement_readiness,
    )
    brain_foundry_promotion = NativePromotionGate()
    brain_foundry_retirement = FoundryRetirementHooks(store=store, artifacts_dir=paths.artifacts_dir, schema_registry=brain_teachers.schema_registry)
    brain_evaluator = ExternalBehaviorEvaluator(
        store=store,
        experiments=experiments,
        artifacts_dir=paths.artifacts_dir,
        teacher_evidence_service=brain_teacher_evidence,
        trend_gate=brain_promotion_trend_gate,
        cohort_gate=brain_promotion_cohort_gate,
        retrieval_bench=brain_retrieval_rerank_bench,
        retrieval_operational_bench=brain_retrieval_rerank_ops,
        cost_energy_service=brain_cost_energy,
    )
    brain_promotions = PromotionService(
        store=store,
        governance=governance,
        evaluator=brain_evaluator,
        retrieval_rerank_bridge=brain_retrieval_rerank_promotion,
    )
    brain_federation_coordinator = FlowerCoordinator(
        store=store,
        artifacts_dir=paths.artifacts_dir,
        promotions=brain_promotions,
    )
    brain_federation_simulation = FlowerSimulationHarness(brain_federation_coordinator)
    brain_federation_review_gate = FederatedReviewGate()
    brain_global_rollout = GlobalRolloutPlanner()
    brain_ui_surface = WrapperSurfaceService(
        store=store,
        memory=memory,
        teacher_registry=brain_teachers,
        ao_registry=brain_aos,
        agent_registry=brain_agent_registry,
        memory_planes=brain_memory_planes,
        brain_runtime_registry=brain_runtime_registry,
        brain_gateway=brain_gateway,
        runtime_profiler=brain_runtime_optimizer,
        brain_runtime_init=brain_runtime_init,
        brain_runtime_doctor=brain_runtime_doctor,
        brain_edge_vision=brain_edge_vision,
        brain_recipe_catalog=brain_recipe_catalog,
        brain_recipe_history=brain_recipe_history,
        brain_runbook_history=brain_runbook_history,
        brain_skill_catalog=brain_skill_catalog,
        brain_extension_catalog=brain_extension_catalog,
        brain_skill_repository=brain_skill_repository,
        brain_skill_evolution=brain_skill_evolution,
        brain_skill_refinement=brain_skill_refinement,
        brain_subagents=brain_subagents,
        brain_delegation=brain_delegation,
        brain_parallel=brain_parallel,
        brain_acp_bridge=brain_acp_bridge,
        brain_permissions=brain_permissions,
        brain_sandbox=brain_sandbox,
        brain_persistent_guardrails=brain_persistent_guardrails,
        brain_adversary_review=brain_adversary_review,
        brain_agent_harness=brain_agent_harness,
        brain_agent_teams=brain_agent_teams,
        brain_scheduled_agents=brain_scheduled_agents,
        brain_attention_registry=brain_attention_registry,
        brain_attention_benchmarks=brain_attention_benchmarks,
        brain_cost_energy=brain_cost_energy,
        brain_guardrail_analysis=brain_guardrail_analysis,
        brain_red_team_review=brain_red_team_review,
        brain_red_team_evaluator=brain_red_team_evaluator,
        graph_service=graph_store,
        federation_status_provider=brain_federation_coordinator.status,
        foundry_status_provider=lambda: {
            "status_label": "LOCKED CANON",
            "teacher_retirement": [decision.model_dump(mode="json") for decision in brain_teachers.retirement_decisions()],
            "native_takeover": [
                {
                    "candidate": candidate.model_dump(mode="json"),
                    "latest_decision": store.latest_promotion_decision(candidate.candidate_id),
                    "teacher_evidence": candidate.traceability.get("teacher_evidence", {}),
                    "teacher_evidence_bundle_id": candidate.teacher_evidence_bundle_id,
                    "takeover_trend_report": candidate.traceability.get("benchmark", {}).get("takeover_trend_report"),
                    "fleet_summaries": candidate.traceability.get("benchmark", {}).get("fleet_summaries", []),
                    "cohort_scorecards": candidate.traceability.get("benchmark", {}).get("cohort_scorecards", []),
                    "replacement_readiness": candidate.traceability.get("benchmark", {}).get("replacement_readiness"),
                }
                for candidate in brain_promotions.list_candidates(candidate_kind="native-takeover")
            ],
            "retirement_shadow_log": store.list_retirement_shadow_records(limit=50),
            "takeover_scorecards": store.list_takeover_scorecards(limit=50),
            "takeover_trends": store.list_takeover_trend_reports(limit=50),
            "fleet_summaries": store.list_teacher_benchmark_fleet_summaries(limit=50),
            "cohort_scorecards": store.list_teacher_cohort_scorecards(limit=50),
            "replacement_readiness_reports": store.list_replacement_readiness_reports(limit=50),
        },
        promotion_provider=brain_promotions.summary,
        retrieval_scorecard_provider=brain_retrieval_rerank_ops.summary,
        brain_core_summary_provider=brain.core_summary,
    )
    brain.evidence_bridge = CoreEvidenceBridge(
        store=store,
        artifacts_dir=paths.artifacts_dir,
        promotion_service=brain_promotions,
    )
    brain_visualizer = NexusVisualizerService(
        paths=paths,
        teacher_registry=brain_teachers,
        wrapper_surface=brain_ui_surface,
        store=store,
    )
    brain_dreaming = RecursiveDreamEngine(
        store=store,
        shadow_pool=dreaming,
        memory=brain.memory,
        experiments=experiments,
        governance=governance,
    )
    brain_reflection = MetaReflectionEngine(store=store)
    brain_curriculum = CurriculumEngine(
        registrar=curriculum,
        memory=brain.memory,
        experiments=experiments,
        teacher_registry=brain_teachers,
        teacher_evidence_service=brain_teacher_evidence,
        dream_engine=brain_dreaming,
        evaluator=brain_evaluator,
    )
    brain_distillation = DistillationDatasetBuilder(
        store=store,
        foundry=foundry,
        experiments=experiments,
        artifacts_dir=paths.artifacts_dir,
        foundry_refinery=brain_foundry_refinery,
        teacher_evidence_service=brain_teacher_evidence,
    )
    operator = OperatorKernel(
        store=store,
        ao_registry=ao_registry,
        agent_registry=agent_registry,
        model_registry=model_registry,
        runtime_registry=runtime_registry,
        memory=memory,
        retrieval=retrieval,
        critique=critique,
        governance=governance,
        experiments=experiments,
        expert_selector=ExpertSelector(runtime_configs),
        brain=brain,
        teacher_registry=brain_teachers,
        brain_aos=brain_aos,
        brain_agent_registry=brain_agent_registry,
        brain_runtime_registry=brain_runtime_registry,
        brain_gateway=brain_gateway,
        brain_promotions=brain_promotions,
    )
    return NexusServices(
        version=VERSION,
        paths=paths,
        runtime_configs=runtime_configs,
        permission_context=permission_context,
        store=store,
        ao_registry=ao_registry,
        agent_registry=agent_registry,
        runtime_registry=runtime_registry,
        model_registry=model_registry,
        memory=memory,
        retrieval=retrieval,
        critique=critique,
        governance=governance,
        experiments=experiments,
        curriculum=curriculum,
        dreaming=dreaming,
        foundry=foundry,
        tool_registry=tool_registry,
        brain=brain,
        brain_teachers=brain_teachers,
        brain_aos=brain_aos,
        brain_agent_registry=brain_agent_registry,
        brain_memory_node=brain_memory_node,
        brain_memory_planes=brain_memory_planes,
        brain_runtime_registry=brain_runtime_registry,
        brain_gateway=brain_gateway,
        brain_runtime_optimizer=brain_runtime_optimizer,
        brain_runtime_init=brain_runtime_init,
        brain_runtime_doctor=brain_runtime_doctor,
        brain_edge_vision=brain_edge_vision,
        brain_recipe_catalog=brain_recipe_catalog,
        brain_recipe_history=brain_recipe_history,
        brain_runbook_history=brain_runbook_history,
        brain_skill_catalog=brain_skill_catalog,
        brain_extension_catalog=brain_extension_catalog,
        brain_skill_repository=brain_skill_repository,
        brain_skill_evolution=brain_skill_evolution,
        brain_skill_refinement=brain_skill_refinement,
        brain_subagents=brain_subagents,
        brain_delegation=brain_delegation,
        brain_parallel=brain_parallel,
        brain_acp_bridge=brain_acp_bridge,
        brain_permissions=brain_permissions,
        brain_sandbox=brain_sandbox,
        brain_persistent_guardrails=brain_persistent_guardrails,
        brain_adversary_review=brain_adversary_review,
        brain_agent_harness=brain_agent_harness,
        brain_agent_teams=brain_agent_teams,
        brain_scheduled_agents=brain_scheduled_agents,
        brain_attention_registry=brain_attention_registry,
        brain_attention_benchmarks=brain_attention_benchmarks,
        brain_cost_energy=brain_cost_energy,
        brain_guardrail_analysis=brain_guardrail_analysis,
        brain_red_team_review=brain_red_team_review,
        brain_red_team_evaluator=brain_red_team_evaluator,
        brain_ui_surface=brain_ui_surface,
        brain_evaluator=brain_evaluator,
        brain_dreaming=brain_dreaming,
        brain_reflection=brain_reflection,
        brain_curriculum=brain_curriculum,
        brain_distillation=brain_distillation,
        brain_graph_ingestion=brain_graph_ingestion,
        brain_graph_retriever=brain_graph_retriever,
        brain_graph_evaluator=brain_graph_evaluator,
        brain_federation_coordinator=brain_federation_coordinator,
        brain_federation_simulation=brain_federation_simulation,
        brain_federation_review_gate=brain_federation_review_gate,
        brain_global_rollout=brain_global_rollout,
        brain_foundry_refinery=brain_foundry_refinery,
        brain_foundry_benchmarks=brain_foundry_benchmarks,
        brain_foundry_promotion=brain_foundry_promotion,
        brain_foundry_retirement=brain_foundry_retirement,
        brain_promotions=brain_promotions,
        brain_teacher_evidence=brain_teacher_evidence,
        brain_teacher_trends=brain_teacher_trends,
        brain_takeover_trends=brain_takeover_trends,
        brain_promotion_trend_gate=brain_promotion_trend_gate,
        brain_teacher_fleets=brain_teacher_fleets,
        brain_teacher_cohorts=brain_teacher_cohorts,
        brain_promotion_cohort_gate=brain_promotion_cohort_gate,
        brain_retrieval_rerank_bench=brain_retrieval_rerank_bench,
        brain_retrieval_rerank_ops=brain_retrieval_rerank_ops,
        brain_visualizer=brain_visualizer,
        operator=operator,
    )
