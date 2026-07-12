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
from .models import ModelRegistry, ModelRuntimePlanner
from .operator import OperatorKernel
from .operator.routing import ExpertSelector
from .permissions import PermissionContext
from .retrieval import RetrievalService
from .runtimes import RuntimeRegistry
from .storage import NexusStore
from .tools import ToolRegistry
from nexusnet.agents.delegation import DelegationPlanner
from nexusnet.agents.harnesses import HarnessImprovementLedger, HarnessModelRouter, HarnessProviderRegistry
from nexusnet.agents.pipelines import AgenticPipelineRuntime
from nexusnet.agents.parallel import ParallelExecutionAdvisor
from nexusnet.agents.subagents import SubagentExecutionService
from nexusnet.agents import AgentOpportunityDiscovery, BrainAgentRegistry, SandboxAgentFactory
from nexusnet.adapters.dataset_forge import DatasetForge
from nexusnet.adapters.decision_gate import FineTuneDecisionGate
from nexusnet.adapters.forge import AdapterForgeRegistry
from nexusnet.adapters.training_planner import AdapterTrainingPlanner
from nexusnet.agents.scheduled import ScheduledAgentService
from nexusnet.adaptive_capabilities import AdaptiveCapabilityService
from nexusnet.assimilation import AssimilationControlPlane
from nexusnet.autonomous_growth import AutonomousGrowthControlPlane
from nexusnet.aos import build_default_ao_registry as build_brain_ao_registry
from nexusnet.browser import BrowserContextMemory, BrowserProfilePolicy
from nexusnet.canon import NexusNetCanonRegistry
from nexusnet.core import AutonomousUpdateController, CoreEvidenceBridge, EBTScoringContract, NexusBrain, NexusNetCore, SelfReviewGate
from nexusnet.core.self_improvement import SelfImprovementLineageRegistry
from nexusnet.curriculum import CurriculumEngine, DatasetRadar
from nexusnet.curriculum.skill_refinement import SkillRefinementService
from nexusnet.context_graph import ContextGraphService
from nexusnet.distillation import DistillationDatasetBuilder
from nexusnet.dreaming import RecursiveDreamEngine
from nexusnet.evals.cost_energy import CostEnergyEvaluationService
from nexusnet.evals.red_team import RedTeamEvidenceService
from nexusnet.evals.red_team.gateway_scenarios import GatewayScenarioCatalog
from nexusnet.evals import EvalRegistry, EvalSuiteService, ExternalBehaviorEvaluator, TraceFirstEvalRegistry, VerifierSearchRegistry
from nexusnet.events import LifecycleEventLogService
from nexusnet.execution_authority import ExecutionAuthorityService
from nexusnet.experts.council import ExpertCouncil
from nexusnet.factory_orchestration import FactoryOrchestrationService
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
from nexusnet.growth import HiveModelGrowthEngine, NexusNetProductionSpine
from nexusnet.harness_engineering import HarnessEngineeringService
from nexusnet.hive import HiveNeuralSubstrate
from nexusnet.knowledge import KnowledgeArtifactCompiler
from nexusnet.memory import MemoryGovernanceService, MemoryNode, MemoryPlaneRegistry, MemoryQualityLedger, NexusEngramIndex
from nexusnet.memory.operating_system import MemoryOperatingSystem
from nexusnet.protocols import GovernedProtocolAdapterRegistry, ProtocolCapabilityRegistry, ProtocolSecurityLayer
from nexusnet.promotions import PromotionCohortGate, PromotionService, TeacherEvidenceService
from nexusnet.promotions.trend_gating import PromotionTrendGate
from nexusnet.product_sweep import ProductSweepGatekeeper
from nexusnet.memory.graph_bridge import MemoryGraphBridge
from nexusnet.operations import AssimilationTargetCatalog, AssimilationTargetRegistry, BrainOperationsService, CodegraphGate
from nexusnet.package_candidates import PackageCandidateService
from nexusnet.parallel_runs import ParallelRunService
from nexusnet.plan_review import PlanReviewService
from nexusnet.protocols import ProtocolTrustRegistry
from nexusnet.guardrails.persistent_instructions import PersistentGuardrailService
from nexusnet.providers.acp import ACPProviderCatalog
from nexusnet.research import ForwardRadarRegistry
from nexusnet.recipes import RecipeCatalogService, RecipeExecutionStore, RecipeHistoryService
from nexusnet.runbooks.history import RunbookHistoryService
from nexusnet.retrieval import RetrievalPlanner
from nexusnet.retrieval.graphrag import GraphRAGEvaluator, GraphRAGIngestionService, GraphRAGRetriever
from nexusnet.retrieval.evals import RetrievalRerankBenchmarkSuite
from nexusnet.retrieval.rerank import RetrievalRerankOperationalBenchmarkSuite, RetrievalRerankPromotionBridge
from nexusnet.reflection import MetaReflectionEngine
from nexusnet.research_scout import ResearchScoutService
from nexusnet.runtime.acp import ACPBridgeService
from nexusnet.runtime import BrainRuntimeRegistry, RuntimeScorecardService
from nexusnet.runtime.cache_ledger import EffectiveContextCacheLedger
from nexusnet.runtime.edge_router import EdgeWorkloadRouter
from nexusnet.runtime.inference_economy_router import InferenceEconomyRouter
from nexusnet.runtime.inference_architecture import InferenceArchitectureRegistry
from nexusnet.runtime.model_passport import EdgeModelCertificationRegistry
from nexusnet.runtime.quantization.catalog import QuantizationCatalog
from nexusnet.runtime.doctor import RuntimeDoctorService
from nexusnet.runtime.gateway import LocalRuntimeGateway
from nexusnet.runtime.init import RuntimeBootstrapService
from nexusnet.runtime.product_profiles import ProductRuntimeProfileRegistry
from nexusnet.runtime.sandbox import SandboxPolicyService
from nexusnet.runtime.workload_scorecards import RuntimeWorkloadScorecardRegistry
from nexusnet.authority import AuthorityIntegritySpine
from nexusnet.developmental import DevelopmentalCortexService
from nexusnet.evals.federation import EvalFederationRegistry
from nexusnet.evidence import EvidenceStore
from nexusnet.evolution import UniversalEvolutionService
from nexusnet.hive.self_improvement_engine import default_engine
from nexusnet.runtime.decision_ledger import RuntimeDecisionLedger
from nexusnet.runtime_optimizer import AdaptiveRuntimeProfiler
from nexusnet.security import ArtifactTrustRegistry
from nexusnet.self_improvement import SelfImprovementService
from nexusnet.tools.action_harness import ToolActionHarness
from nexusnet.teachers import (
    TeacherBenchmarkFleetAnalyzer,
    TeacherCohortAnalyzer,
    TeacherRegistry,
    TeacherSchemaMigrationHelper,
)
from nexusnet.teachers.trends import TeacherTrendAnalyzer
from nexusnet.telemetry import NormalizedTelemetryService
from nexusnet.temporal.retriever import TemporalRetriever
from nexusnet.telemetry import ConceptTelemetryRegistry, GenAITraceRegistry
from nexusnet.tier5 import Tier5FallbackService
from nexusnet.tools import ExtensionCatalogService, GatewayApprovalService, GatewayPolicyEngine, SkillCatalogService, SkillPackageRegistry
from nexusnet.tools.adversary_review import AdversaryReviewService
from nexusnet.tools.permissions import ToolPermissionService
from nexusnet.tools.skill_evolution import SkillEvolutionLab
from nexusnet.training import TrainingDatasetExporter
from nexusnet.ui_surface import WrapperSurfaceService
from nexusnet.visuals import NexusVisualizerService
from nexusnet.vision import EdgeVisionLaneService, MultimodalComputerUseController, OperatorEventRegistry
from nexusnet.workflows import WorkflowCatalogService
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
    model_runtime_planner: ModelRuntimePlanner
    memory: MemoryService
    retrieval: RetrievalService
    critique: CritiqueEngine
    governance: GovernanceService
    experiments: ExperimentService
    curriculum: CurriculumRegistrar
    dreaming: DreamShadowPool
    foundry: DatasetRefinery
    tool_registry: ToolRegistry
    brain_canon: NexusNetCanonRegistry
    brain_ebt: EBTScoringContract
    brain_trace_evals: TraceFirstEvalRegistry
    brain: NexusBrain
    nexusnet_core: NexusNetCore
    brain_teachers: TeacherRegistry
    brain_aos: Any
    brain_agent_registry: BrainAgentRegistry
    brain_memory_node: MemoryNode
    brain_memory_planes: MemoryPlaneRegistry
    brain_memory_quality: Any
    brain_engram_memory: Any
    brain_memory_os: MemoryOperatingSystem
    brain_runtime_registry: BrainRuntimeRegistry
    brain_protocol_security: ProtocolSecurityLayer
    brain_protocol_adapters: GovernedProtocolAdapterRegistry
    brain_product_runtime_profiles: ProductRuntimeProfileRegistry
    brain_training_exporter: TrainingDatasetExporter
    brain_product_sweep_gatekeeper: ProductSweepGatekeeper
    brain_expert_council: ExpertCouncil
    brain_lifecycle_events: Any
    brain_workflows: Any
    brain_parallel_runs: Any
    brain_package_candidates: Any
    brain_plan_review: Any
    brain_assimilation: AssimilationControlPlane
    brain_normalized_telemetry: NormalizedTelemetryService
    brain_eval_suites: EvalSuiteService
    brain_runtime_scorecards: RuntimeScorecardService
    brain_adaptive_capabilities: AdaptiveCapabilityService
    brain_research_scout: ResearchScoutService
    brain_self_improvement: SelfImprovementService
    brain_tier5_fallback: Tier5FallbackService
    brain_context_graph: ContextGraphService
    brain_factory_orchestration: FactoryOrchestrationService
    brain_execution_authority: ExecutionAuthorityService
    brain_harness_engineering: HarnessEngineeringService
    brain_protocol_capabilities: ProtocolCapabilityRegistry
    brain_memory_governance: MemoryGovernanceService
    brain_autonomous_growth: AutonomousGrowthControlPlane
    brain_gateway: Any
    brain_runtime_optimizer: AdaptiveRuntimeProfiler
    brain_runtime_init: Any
    brain_runtime_doctor: Any
    brain_edge_vision: Any
    brain_edge_workload_router: Any
    brain_multimodal_computer_use: Any
    brain_operator_events: Any
    brain_inference_economy_router: Any
    brain_inference_architecture: Any
    brain_cache_ledger: Any
    brain_runtime_workload_scorecards: Any
    brain_quantization_catalog: Any
    brain_edge_model_certification: Any
    brain_protocol_trust_registry: Any
    brain_browser_context: Any
    brain_browser_profile_policy: Any
    brain_dataset_radar: Any
    brain_dataset_forge: Any
    brain_knowledge_artifacts: Any
    brain_adapter_registry: Any
    brain_fine_tune_decision_gate: Any
    brain_adapter_training: Any
    brain_growth_engine: Any
    brain_production_spine: Any
    brain_recipe_catalog: Any
    brain_recipe_history: Any
    brain_runbook_history: Any
    brain_skill_catalog: Any
    brain_extension_catalog: Any
    brain_skill_repository: Any
    brain_skill_evolution: Any
    brain_skill_refinement: Any
    brain_assimilation_targets: Any
    brain_codegraph_gate: Any
    brain_subagents: Any
    brain_agent_opportunities: Any
    brain_agentic_pipelines: Any
    brain_sandbox_agent_factory: SandboxAgentFactory
    brain_harness_providers: Any
    brain_harness_router: Any
    brain_harness_improvement_ledger: Any
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
    brain_eval_registry: Any
    brain_artifact_trust_registry: Any
    brain_autonomous_updates: Any
    brain_genai_observability: Any
    brain_concept_telemetry: Any
    brain_self_review: Any
    brain_self_improvement_lineage: Any
    brain_verifier_search: Any
    brain_forward_radar: Any
    brain_hive_substrate: HiveNeuralSubstrate
    brain_developmental_cortex: Any
    brain_authority_spine: Any
    brain_evidence_store: Any
    brain_evolution: UniversalEvolutionService
    brain_eval_federation: Any
    brain_tool_action_harness: Any
    brain_runtime_decision_ledger: Any
    brain_assimilation_catalog: Any
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
    brain_retrieval_planner: Any
    brain_operations: Any
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
    brain_aos = build_brain_ao_registry(artifacts_dir=paths.artifacts_dir)
    agent_registry = build_default_agent_registry()
    tool_registry = ToolRegistry()
    runtime_registry = RuntimeRegistry(paths, store, runtime_configs)
    runtime_registry.bootstrap()
    model_registry = ModelRegistry(store, runtime_registry, runtime_configs)
    model_registry.bootstrap()
    model_runtime_planner = ModelRuntimePlanner(runtime_registry=runtime_registry, runtime_configs=runtime_configs)
    memory = MemoryService(paths, store)
    brain_memory_node = MemoryNode(project_root=paths.project_root, runtime_configs=runtime_configs)
    runtime_configs["planes"] = brain_memory_node.summary()["raw_config"]
    brain_memory_planes = brain_memory_node.registry
    brain_memory_quality = MemoryQualityLedger(artifacts_dir=paths.artifacts_dir)
    brain_engram_memory = NexusEngramIndex(artifacts_dir=paths.artifacts_dir)
    brain_canon = NexusNetCanonRegistry(
        persistence_path=paths.artifacts_dir / "canon" / "assimilation_registry_overrides.json"
    )
    brain_ebt = EBTScoringContract()
    brain_trace_evals = TraceFirstEvalRegistry()
    brain_memory_os = MemoryOperatingSystem(paths.artifacts_dir / "memory" / "memory_os_records.json")
    brain_protocol_security = ProtocolSecurityLayer()
    brain_protocol_adapters = GovernedProtocolAdapterRegistry(brain_protocol_security)
    brain_product_runtime_profiles = ProductRuntimeProfileRegistry()
    brain_training_exporter = TrainingDatasetExporter(paths.artifacts_dir)
    brain_product_sweep_gatekeeper = ProductSweepGatekeeper(
        canon=brain_canon,
        memory_os=brain_memory_os,
        protocol_security=brain_protocol_security,
        protocol_adapters=brain_protocol_adapters,
        runtime_profiles=brain_product_runtime_profiles,
        trace_evals=brain_trace_evals,
    )
    brain_expert_council = ExpertCouncil()
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
    nexusnet_core = NexusNetCore(
        paths=paths,
        brain=brain,
        hardware_scanner=brain_runtime_registry.hardware_scanner,
        system_profiler=brain_runtime_registry.system_profiler,
        memory_node=brain_memory_node,
    )
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
    brain_retrieval_planner = RetrievalPlanner(artifacts_dir=paths.artifacts_dir)
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
    brain_lifecycle_events = LifecycleEventLogService(artifacts_dir=paths.artifacts_dir)
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
    brain_package_candidates = PackageCandidateService(
        artifacts_dir=paths.artifacts_dir,
        events=brain_lifecycle_events,
    )
    brain_plan_review = PlanReviewService(
        artifacts_dir=paths.artifacts_dir,
        events=brain_lifecycle_events,
    )
    brain_workflows = WorkflowCatalogService(
        config_dir=paths.config_dir,
        artifacts_dir=paths.artifacts_dir,
        runtime_configs=runtime_configs,
        execution_store=brain_recipe_execution_store,
        gateway=brain_gateway,
        events=brain_lifecycle_events,
    )
    brain_parallel_runs = ParallelRunService(
        project_root=paths.project_root,
        artifacts_dir=paths.artifacts_dir,
        gateway=brain_gateway,
        workflow_service=brain_workflows,
        events=brain_lifecycle_events,
    )
    brain_assimilation = AssimilationControlPlane(
        artifacts_dir=paths.artifacts_dir,
        events=brain_lifecycle_events,
    )
    brain_normalized_telemetry = NormalizedTelemetryService(
        events=brain_lifecycle_events,
        store=store,
    )
    brain_eval_suites = EvalSuiteService(
        artifacts_dir=paths.artifacts_dir,
        events=brain_lifecycle_events,
    )
    brain_runtime_scorecards = RuntimeScorecardService(
        artifacts_dir=paths.artifacts_dir,
        runtime_registry=brain_runtime_registry,
        events=brain_lifecycle_events,
    )
    brain_adaptive_capabilities = AdaptiveCapabilityService(
        artifacts_dir=paths.artifacts_dir,
        runtime_scorecards=brain_runtime_scorecards,
        events=brain_lifecycle_events,
    )
    brain_research_scout = ResearchScoutService(
        artifacts_dir=paths.artifacts_dir,
        assimilation=brain_assimilation,
        events=brain_lifecycle_events,
    )
    brain_self_improvement = SelfImprovementService(
        artifacts_dir=paths.artifacts_dir,
        events=brain_lifecycle_events,
        product_sweep=brain_product_sweep_gatekeeper,
    )
    brain_tier5_fallback = Tier5FallbackService(
        artifacts_dir=paths.artifacts_dir,
        events=brain_lifecycle_events,
    )
    brain_context_graph = ContextGraphService(
        artifacts_dir=paths.artifacts_dir,
        events=brain_lifecycle_events,
    )
    brain_factory_orchestration = FactoryOrchestrationService(
        artifacts_dir=paths.artifacts_dir,
        events=brain_lifecycle_events,
    )
    brain_execution_authority = ExecutionAuthorityService(
        artifacts_dir=paths.artifacts_dir,
        events=brain_lifecycle_events,
    )
    brain_harness_engineering = HarnessEngineeringService(
        artifacts_dir=paths.artifacts_dir,
        events=brain_lifecycle_events,
    )
    brain_protocol_capabilities = ProtocolCapabilityRegistry(
        protocol_adapters=brain_protocol_adapters,
        security_layer=brain_protocol_security,
    )
    brain_memory_governance = MemoryGovernanceService(
        memory_os=brain_memory_os,
        artifacts_dir=paths.artifacts_dir,
        events=brain_lifecycle_events,
    )
    brain_autonomous_growth = AutonomousGrowthControlPlane(
        artifacts_dir=paths.artifacts_dir,
        events=brain_lifecycle_events,
        execution_authority=brain_execution_authority,
        assimilation=brain_assimilation,
        harness_engineering=brain_harness_engineering,
        eval_suites=brain_eval_suites,
        runtime_scorecards=brain_runtime_scorecards,
        memory_governance=brain_memory_governance,
        research_scout=brain_research_scout,
    )
    brain_runtime_optimizer = AdaptiveRuntimeProfiler(runtime_registry, model_registry, runtime_configs)
    brain_edge_vision = EdgeVisionLaneService(
        config_dir=paths.config_dir,
        artifacts_dir=paths.artifacts_dir,
        runtime_configs=runtime_configs,
    )
    brain_edge_workload_router = EdgeWorkloadRouter(artifacts_dir=paths.artifacts_dir)
    brain_multimodal_computer_use = MultimodalComputerUseController(
        artifacts_dir=paths.artifacts_dir,
        edge_router=brain_edge_workload_router,
    )
    brain_operator_events = OperatorEventRegistry(artifacts_dir=paths.artifacts_dir)
    brain_inference_economy_router = InferenceEconomyRouter(artifacts_dir=paths.artifacts_dir)
    brain_inference_architecture = InferenceArchitectureRegistry(artifacts_dir=paths.artifacts_dir)
    brain_cache_ledger = EffectiveContextCacheLedger(artifacts_dir=paths.artifacts_dir)
    brain_runtime_workload_scorecards = RuntimeWorkloadScorecardRegistry(artifacts_dir=paths.artifacts_dir)
    brain_quantization_catalog = QuantizationCatalog.default(artifacts_dir=paths.artifacts_dir)
    brain_edge_model_certification = EdgeModelCertificationRegistry(artifacts_dir=paths.artifacts_dir)
    brain_protocol_trust_registry = ProtocolTrustRegistry(artifacts_dir=paths.artifacts_dir)
    brain_browser_context = BrowserContextMemory(artifacts_dir=paths.artifacts_dir)
    brain_browser_profile_policy = BrowserProfilePolicy(artifacts_dir=paths.artifacts_dir)
    brain_dataset_radar = DatasetRadar(artifacts_dir=paths.artifacts_dir)
    brain_dataset_forge = DatasetForge(artifacts_dir=paths.artifacts_dir, dataset_radar=brain_dataset_radar)
    brain_knowledge_artifacts = KnowledgeArtifactCompiler(artifacts_dir=paths.artifacts_dir, source_root=paths.project_root)
    brain_adapter_registry = AdapterForgeRegistry(artifacts_dir=paths.artifacts_dir)
    brain_fine_tune_decision_gate = FineTuneDecisionGate(artifacts_dir=paths.artifacts_dir)
    brain_adapter_training = AdapterTrainingPlanner(artifacts_dir=paths.artifacts_dir)
    brain_growth_engine = HiveModelGrowthEngine(artifacts_dir=paths.artifacts_dir)
    brain_production_spine = NexusNetProductionSpine(artifacts_dir=paths.artifacts_dir)
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
    brain_assimilation_targets = AssimilationTargetRegistry(artifacts_dir=paths.artifacts_dir)
    brain_codegraph_gate = CodegraphGate(artifacts_dir=paths.artifacts_dir)
    brain_subagents = SubagentExecutionService(
        artifacts_dir=paths.artifacts_dir,
        runtime_configs=runtime_configs,
    )
    brain_agent_opportunities = AgentOpportunityDiscovery(artifacts_dir=paths.artifacts_dir)
    brain_agentic_pipelines = AgenticPipelineRuntime(artifacts_dir=paths.artifacts_dir)
    brain_sandbox_agent_factory = SandboxAgentFactory(artifacts_dir=paths.artifacts_dir)
    brain_harness_providers = HarnessProviderRegistry.default()
    brain_harness_router = HarnessModelRouter.default()
    brain_harness_improvement_ledger = HarnessImprovementLedger(artifacts_dir=paths.artifacts_dir)
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
    brain_eval_registry = EvalRegistry.default(artifacts_dir=paths.artifacts_dir)
    brain_artifact_trust_registry = ArtifactTrustRegistry(artifacts_dir=paths.artifacts_dir)
    brain_autonomous_updates = AutonomousUpdateController(artifacts_dir=paths.artifacts_dir)
    brain_genai_observability = GenAITraceRegistry(artifacts_dir=paths.artifacts_dir)
    brain_concept_telemetry = ConceptTelemetryRegistry(artifacts_dir=paths.artifacts_dir)
    brain_self_review = SelfReviewGate(artifacts_dir=paths.artifacts_dir)
    brain_self_improvement_lineage = SelfImprovementLineageRegistry(artifacts_dir=paths.artifacts_dir)
    brain_verifier_search = VerifierSearchRegistry(artifacts_dir=paths.artifacts_dir)
    brain_forward_radar = ForwardRadarRegistry(artifacts_dir=paths.artifacts_dir)
    brain_hive_substrate = HiveNeuralSubstrate(artifacts_dir=paths.artifacts_dir)
    brain.hive_substrate = brain_hive_substrate
    brain_developmental_cortex = DevelopmentalCortexService(artifacts_dir=paths.artifacts_dir)
    brain_authority_spine = AuthorityIntegritySpine(artifacts_dir=paths.artifacts_dir)
    brain_evidence_store = EvidenceStore(artifacts_dir=paths.artifacts_dir)
    brain_evolution = UniversalEvolutionService(
        artifacts_dir=paths.artifacts_dir,
        owner_brain_ref="brain:NexusBrain",
        prerequisite_evidence={
            "canon": "service:NexusNetCanonRegistry",
            "mother_brain_authority": "brain:NexusBrain",
            "isolation": "service:SandboxPolicyService",
            "evidence": "service:EvidenceStore",
            "checkpoint": "service:HiveNeuralSubstrate:checkpoint",
            "replay": "service:HiveNeuralSubstrate:replay",
            "governance": "service:GovernanceService",
            "rollback": "service:HiveNeuralSubstrate:rollback",
        },
        legacy_engine=default_engine(),
    )
    brain_eval_federation = EvalFederationRegistry(artifacts_dir=paths.artifacts_dir)
    brain_tool_action_harness = ToolActionHarness(artifacts_dir=paths.artifacts_dir)
    brain_runtime_decision_ledger = RuntimeDecisionLedger(artifacts_dir=paths.artifacts_dir)
    brain_assimilation_catalog = AssimilationTargetCatalog()
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
        brain_assimilation_targets=brain_assimilation_targets,
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
        dataset_radar=brain_dataset_radar,
        harness_provider_registry=brain_harness_providers,
        harness_model_router=brain_harness_router,
        assimilation_targets=brain_assimilation_targets,
        retrieval_planner=brain_retrieval_planner,
        self_improvement_lineage=brain_self_improvement_lineage,
        verifier_search=brain_verifier_search,
        browser_profile_policy=brain_browser_profile_policy,
        operator_events=brain_operator_events,
        edge_model_certification=brain_edge_model_certification,
        concept_telemetry=brain_concept_telemetry,
        codegraph_gate=brain_codegraph_gate,
        developmental_cortex=brain_developmental_cortex,
        authority_spine=brain_authority_spine,
        evidence_store=brain_evidence_store,
        eval_federation=brain_eval_federation,
        tool_action_harness=brain_tool_action_harness,
        runtime_decision_ledger=brain_runtime_decision_ledger,
        assimilation_catalog=brain_assimilation_catalog,
    )
    brain_operations = BrainOperationsService(
        store=store,
        ao_registry=brain_aos,
        agent_registry=brain_agent_registry,
        teacher_registry=brain_teachers,
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
        model_runtime_planner=model_runtime_planner,
        nexusnet_core=nexusnet_core,
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
        model_runtime_planner=model_runtime_planner,
        memory=memory,
        retrieval=retrieval,
        critique=critique,
        governance=governance,
        experiments=experiments,
        curriculum=curriculum,
        dreaming=dreaming,
        foundry=foundry,
        tool_registry=tool_registry,
        brain_canon=brain_canon,
        brain_ebt=brain_ebt,
        brain_trace_evals=brain_trace_evals,
        brain=brain,
        nexusnet_core=nexusnet_core,
        brain_teachers=brain_teachers,
        brain_aos=brain_aos,
        brain_agent_registry=brain_agent_registry,
        brain_memory_node=brain_memory_node,
        brain_memory_planes=brain_memory_planes,
        brain_memory_quality=brain_memory_quality,
        brain_engram_memory=brain_engram_memory,
        brain_memory_os=brain_memory_os,
        brain_runtime_registry=brain_runtime_registry,
        brain_protocol_security=brain_protocol_security,
        brain_protocol_adapters=brain_protocol_adapters,
        brain_product_runtime_profiles=brain_product_runtime_profiles,
        brain_training_exporter=brain_training_exporter,
        brain_product_sweep_gatekeeper=brain_product_sweep_gatekeeper,
        brain_expert_council=brain_expert_council,
        brain_lifecycle_events=brain_lifecycle_events,
        brain_workflows=brain_workflows,
        brain_parallel_runs=brain_parallel_runs,
        brain_package_candidates=brain_package_candidates,
        brain_plan_review=brain_plan_review,
        brain_assimilation=brain_assimilation,
        brain_normalized_telemetry=brain_normalized_telemetry,
        brain_eval_suites=brain_eval_suites,
        brain_runtime_scorecards=brain_runtime_scorecards,
        brain_adaptive_capabilities=brain_adaptive_capabilities,
        brain_research_scout=brain_research_scout,
        brain_self_improvement=brain_self_improvement,
        brain_tier5_fallback=brain_tier5_fallback,
        brain_context_graph=brain_context_graph,
        brain_factory_orchestration=brain_factory_orchestration,
        brain_execution_authority=brain_execution_authority,
        brain_harness_engineering=brain_harness_engineering,
        brain_protocol_capabilities=brain_protocol_capabilities,
        brain_memory_governance=brain_memory_governance,
        brain_autonomous_growth=brain_autonomous_growth,
        brain_gateway=brain_gateway,
        brain_runtime_optimizer=brain_runtime_optimizer,
        brain_runtime_init=brain_runtime_init,
        brain_runtime_doctor=brain_runtime_doctor,
        brain_edge_vision=brain_edge_vision,
        brain_edge_workload_router=brain_edge_workload_router,
        brain_multimodal_computer_use=brain_multimodal_computer_use,
        brain_operator_events=brain_operator_events,
        brain_inference_economy_router=brain_inference_economy_router,
        brain_inference_architecture=brain_inference_architecture,
        brain_cache_ledger=brain_cache_ledger,
        brain_runtime_workload_scorecards=brain_runtime_workload_scorecards,
        brain_quantization_catalog=brain_quantization_catalog,
        brain_edge_model_certification=brain_edge_model_certification,
        brain_protocol_trust_registry=brain_protocol_trust_registry,
        brain_browser_context=brain_browser_context,
        brain_browser_profile_policy=brain_browser_profile_policy,
        brain_dataset_radar=brain_dataset_radar,
        brain_dataset_forge=brain_dataset_forge,
        brain_knowledge_artifacts=brain_knowledge_artifacts,
        brain_adapter_registry=brain_adapter_registry,
        brain_fine_tune_decision_gate=brain_fine_tune_decision_gate,
        brain_adapter_training=brain_adapter_training,
        brain_growth_engine=brain_growth_engine,
        brain_production_spine=brain_production_spine,
        brain_recipe_catalog=brain_recipe_catalog,
        brain_recipe_history=brain_recipe_history,
        brain_runbook_history=brain_runbook_history,
        brain_skill_catalog=brain_skill_catalog,
        brain_extension_catalog=brain_extension_catalog,
        brain_skill_repository=brain_skill_repository,
        brain_skill_evolution=brain_skill_evolution,
        brain_skill_refinement=brain_skill_refinement,
        brain_assimilation_targets=brain_assimilation_targets,
        brain_codegraph_gate=brain_codegraph_gate,
        brain_subagents=brain_subagents,
        brain_agent_opportunities=brain_agent_opportunities,
        brain_agentic_pipelines=brain_agentic_pipelines,
        brain_sandbox_agent_factory=brain_sandbox_agent_factory,
        brain_harness_providers=brain_harness_providers,
        brain_harness_router=brain_harness_router,
        brain_harness_improvement_ledger=brain_harness_improvement_ledger,
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
        brain_eval_registry=brain_eval_registry,
        brain_artifact_trust_registry=brain_artifact_trust_registry,
        brain_autonomous_updates=brain_autonomous_updates,
        brain_genai_observability=brain_genai_observability,
        brain_concept_telemetry=brain_concept_telemetry,
        brain_self_review=brain_self_review,
        brain_self_improvement_lineage=brain_self_improvement_lineage,
        brain_verifier_search=brain_verifier_search,
        brain_forward_radar=brain_forward_radar,
        brain_hive_substrate=brain_hive_substrate,
        brain_developmental_cortex=brain_developmental_cortex,
        brain_authority_spine=brain_authority_spine,
        brain_evidence_store=brain_evidence_store,
        brain_evolution=brain_evolution,
        brain_eval_federation=brain_eval_federation,
        brain_tool_action_harness=brain_tool_action_harness,
        brain_runtime_decision_ledger=brain_runtime_decision_ledger,
        brain_assimilation_catalog=brain_assimilation_catalog,
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
        brain_retrieval_planner=brain_retrieval_planner,
        brain_operations=brain_operations,
        brain_visualizer=brain_visualizer,
        operator=operator,
    )
