from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexusnet.teachers.candidate_universe import (
    TeacherCandidateUniverse,
    build_default_teacher_candidate_universe,
)

from .ontology import OpenWorldExpertOntology, build_default_expert_ontology


Cluster9NodeType = Literal[
    "core",
    "orchestrator",
    "assistant_orchestrator",
    "expert",
    "temporary_expert",
]
Cluster9LifecycleState = Literal["seed", "shadow", "active", "candidate", "retired"]
Cluster9IssueSeverity = Literal["info", "warning", "error"]


class Cluster9RoleNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    display_name: str
    node_type: Cluster9NodeType
    domain: str
    teacher_ids: list[str] = Field(default_factory=list)
    required_teacher_count: int = 2
    lifecycle_state: Cluster9LifecycleState = "seed"
    source_refs: list[str] = Field(default_factory=list)
    expert_ref: str | None = None
    ao_ref: str | None = None
    orchestrator_ref: str | None = None
    production_mutation_allowed: bool = False
    birth_gates: list[str] = Field(
        default_factory=lambda: [
            "source_refs",
            "teacher_pairing",
            "eval_evidence",
            "rollback_plan",
            "mother_brain_approval",
        ]
    )
    retirement_policy: str = "retire_or_merge_after_repeated_regression"
    metadata: dict[str, Any] = Field(default_factory=dict)


class Cluster9ReconciliationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    node_id: str
    severity: Cluster9IssueSeverity = "error"
    birth_blocking: bool = True
    message: str


class TeacherCapabilityPassport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    teacher_id: str
    candidate_status: str
    teacher_roles: list[str] = Field(default_factory=list)
    domain_scope: list[str] = Field(default_factory=list)
    risk_scope: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    promotion_allowed: bool = False
    promotion_blockers: list[str] = Field(default_factory=list)


class ExpertDomainPassport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    node_type: Cluster9NodeType
    domain: str
    risk_tier: str
    expert_ref: str | None
    required_teacher_count: int
    teacher_ids: list[str] = Field(default_factory=list)
    teacher_capabilities: list[TeacherCapabilityPassport] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    birth_gates: list[str] = Field(default_factory=list)
    production_mutation_allowed: bool = False
    mother_brain_authority: str = "NexusBrain"


class Cluster9TeacherReconciliationRegistry:
    def __init__(
        self,
        nodes: Iterable[Cluster9RoleNode | dict[str, Any]] | None = None,
        *,
        ontology: OpenWorldExpertOntology | None = None,
        teacher_universe: TeacherCandidateUniverse | None = None,
    ) -> None:
        self._nodes: dict[str, Cluster9RoleNode] = {}
        self._ontology = ontology or build_default_expert_ontology()
        self._teacher_universe = teacher_universe or build_default_teacher_candidate_universe()
        for node in nodes or []:
            self.register(node)

    def register(
        self,
        node: Cluster9RoleNode | dict[str, Any],
        *,
        replace: bool = False,
    ) -> Cluster9RoleNode:
        normalized = Cluster9RoleNode.model_validate(
            node.model_dump(mode="python") if isinstance(node, Cluster9RoleNode) else node
        )
        if normalized.node_id in self._nodes and not replace:
            raise ValueError(f"Cluster 9 role node already registered: {normalized.node_id}")
        stored = normalized.model_copy(deep=True)
        self._nodes[stored.node_id] = stored
        return stored.model_copy(deep=True)

    def get(self, node_id: str) -> Cluster9RoleNode | None:
        node = self._nodes.get(node_id)
        return node.model_copy(deep=True) if node is not None else None

    def list_nodes(
        self,
        *,
        node_type: Cluster9NodeType | None = None,
        domain: str | None = None,
    ) -> list[Cluster9RoleNode]:
        nodes = list(self._nodes.values())
        if node_type is not None:
            nodes = [node for node in nodes if node.node_type == node_type]
        if domain is not None:
            nodes = [node for node in nodes if node.domain == domain]
        return [node.model_copy(deep=True) for node in sorted(nodes, key=lambda node: node.node_id)]

    def nodes_missing_teacher_pairing(self) -> list[Cluster9RoleNode]:
        return [
            node
            for node in self.list_nodes()
            if len(_distinct_nonblank(node.teacher_ids)) < node.required_teacher_count
        ]

    def validate(self) -> list[Cluster9ReconciliationIssue]:
        issues: list[Cluster9ReconciliationIssue] = []
        for node in self.list_nodes():
            teacher_count = len(_distinct_nonblank(node.teacher_ids))
            if teacher_count < node.required_teacher_count:
                issues.append(
                    Cluster9ReconciliationIssue(
                        code="teacher_pairing_below_minimum",
                        node_id=node.node_id,
                        message=(
                            f"{node.node_id} has {teacher_count} distinct teachers; "
                            f"{node.required_teacher_count} required."
                        ),
                    )
                )
            if node.expert_ref and self._ontology.get(node.expert_ref) is None:
                issues.append(
                    Cluster9ReconciliationIssue(
                        code="expert_ref_missing",
                        node_id=node.node_id,
                        message=f"{node.node_id} references unknown expert ontology entry {node.expert_ref}.",
                    )
                )
            if not _distinct_nonblank(node.source_refs):
                issues.append(
                    Cluster9ReconciliationIssue(
                        code="source_refs_missing",
                        node_id=node.node_id,
                        severity="warning",
                        birth_blocking=False,
                        message=f"{node.node_id} has no source refs for reconciliation traceability.",
                    )
                )
            if node.node_type == "temporary_expert":
                if node.lifecycle_state != "shadow":
                    issues.append(
                        Cluster9ReconciliationIssue(
                            code="temporary_expert_not_shadow",
                            node_id=node.node_id,
                            message="Temporary live-problem experts must remain shadow scoped.",
                        )
                    )
                if node.production_mutation_allowed:
                    issues.append(
                        Cluster9ReconciliationIssue(
                            code="temporary_expert_can_mutate_production",
                            node_id=node.node_id,
                            message="Temporary live-problem experts cannot mutate production directly.",
                        )
                    )
            for teacher_id in _distinct_nonblank(node.teacher_ids):
                if self._teacher_universe.get(teacher_id) is None:
                    issues.append(
                        Cluster9ReconciliationIssue(
                            code="teacher_candidate_profile_missing",
                            node_id=node.node_id,
                            severity="warning",
                            birth_blocking=False,
                            message=f"{node.node_id} references teacher {teacher_id} outside candidate universe.",
                        )
                    )
        return sorted(issues, key=lambda issue: (issue.node_id, issue.code))

    def teacher_capability_passport(self, teacher_id: str) -> TeacherCapabilityPassport:
        candidate = self._teacher_universe.get(teacher_id)
        if candidate is None:
            return TeacherCapabilityPassport(
                teacher_id=teacher_id,
                candidate_status="missing",
                promotion_blockers=["candidate_missing"],
            )
        return TeacherCapabilityPassport(
            teacher_id=candidate.candidate_id,
            candidate_status=candidate.candidate_status,
            teacher_roles=list(candidate.teacher_roles),
            domain_scope=list(candidate.domain_scope),
            risk_scope=list(candidate.risk_scope),
            source_refs=list(candidate.source_refs),
            promotion_allowed=self._teacher_universe.promotion_allowed(candidate.candidate_id),
            promotion_blockers=self._teacher_universe.promotion_blockers(candidate.candidate_id),
        )

    def expert_domain_passport(self, node_id: str) -> ExpertDomainPassport:
        node = self._required_node(node_id)
        expert = self._ontology.get(node.expert_ref) if node.expert_ref else None
        risk_tier = expert.risk_tier if expert is not None else "medium"
        domain = expert.domain if expert is not None else node.domain
        return ExpertDomainPassport(
            node_id=node.node_id,
            node_type=node.node_type,
            domain=domain,
            risk_tier=risk_tier,
            expert_ref=node.expert_ref,
            required_teacher_count=node.required_teacher_count,
            teacher_ids=_distinct_nonblank(node.teacher_ids),
            teacher_capabilities=[
                self.teacher_capability_passport(teacher_id)
                for teacher_id in _distinct_nonblank(node.teacher_ids)
            ],
            source_refs=list(node.source_refs),
            birth_gates=list(node.birth_gates),
            production_mutation_allowed=node.production_mutation_allowed,
        )

    def summary(self) -> dict[str, Any]:
        issues = self.validate()
        nodes = self.list_nodes()
        node_type_counts: dict[str, int] = {}
        for node in nodes:
            node_type_counts[node.node_type] = node_type_counts.get(node.node_type, 0) + 1
        return {
            "surface_id": "cluster9-teacher-expert-reconciliation",
            "node_count": len(nodes),
            "node_type_counts": node_type_counts,
            "pairing_gap_count": len(self.nodes_missing_teacher_pairing()),
            "issue_count": len(issues),
            "birth_blocking_issue_count": sum(1 for issue in issues if issue.birth_blocking),
            "nonblocking_issue_count": sum(1 for issue in issues if not issue.birth_blocking),
            "final_roster_claimed": False,
            "mother_brain_authority": "NexusBrain",
            "autonomy_rule": (
                "cluster9-reconciliation-is-a-shadow-first-roster-and-passport-surface; "
                "birth-merge-split-retire-requires-eval-teacher-rollback-and-mother-brain-approval"
            ),
        }

    def _required_node(self, node_id: str) -> Cluster9RoleNode:
        node = self.get(node_id)
        if node is None:
            raise KeyError(f"Cluster 9 role node not found: {node_id}")
        return node


def build_default_cluster9_teacher_reconciliation_registry() -> Cluster9TeacherReconciliationRegistry:
    return Cluster9TeacherReconciliationRegistry(_default_cluster9_nodes())


def _distinct_nonblank(values: Iterable[str]) -> list[str]:
    distinct: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        distinct.append(normalized)
    return distinct


def _default_cluster9_nodes() -> list[Cluster9RoleNode]:
    formal_panel = ["leanstral-1-5", "qwen3-coder-next"]
    general_panel = ["qwen3-30b-a3b", "deepseek-v4-pro"]
    software_panel = ["qwen3-coder-next", "devstral-2"]
    memory_panel = ["mem0-memory", "graphiti-zep-memory"]
    graph_panel = ["lightrag-graphrag", "graphiti-zep-memory"]
    medical_panel = ["medgemma-1-5-4b", "qwen3-coder-next"]
    finance_crypto_panel = ["market-risk-simulator", "deepseek-v4-pro", "qwen3-30b-a3b"]
    quantum_panel = ["qiskit-quantum-code", "leanstral-1-5"]
    dream_panel = ["qwen3-30b-a3b", "deepseek-v4-pro"]
    return [
        Cluster9RoleNode(
            node_id="core.nexus-brain",
            display_name="NexusBrain Mother Brain",
            node_type="core",
            domain="mother_brain",
            teacher_ids=general_panel,
            source_refs=["cluster9::mother-brain-authority", "cluster13::nexusgraph-intelligence-fabric"],
            metadata={"owns_hive_authority": True},
        ),
        Cluster9RoleNode(
            node_id="orchestrator.teacher-lifecycle",
            display_name="Teacher Lifecycle Orchestrator",
            node_type="orchestrator",
            domain="teacher_lifecycle",
            teacher_ids=general_panel,
            orchestrator_ref="TeacherLifecycleOrchestrator",
            source_refs=["cluster9::teacher-council", "taxonomy::teacher-lifecycle"],
        ),
        Cluster9RoleNode(
            node_id="orchestrator.expert-evolution",
            display_name="Expert Evolution Orchestrator",
            node_type="orchestrator",
            domain="expert_evolution",
            teacher_ids=software_panel,
            orchestrator_ref="ExpertEvolutionOrchestrator",
            source_refs=["cluster9::expert-birth-registry", "taxonomy::expert-evolution"],
        ),
        Cluster9RoleNode(
            node_id="orchestrator.agent-native-memory",
            display_name="Agent-Native Memory Orchestrator",
            node_type="orchestrator",
            domain="agent_native_memory",
            teacher_ids=memory_panel,
            orchestrator_ref="AgentNativeMemoryOrchestrator",
            source_refs=["cluster5::agent-native-memory-os", "taxonomy::memory-orchestrators"],
        ),
        Cluster9RoleNode(
            node_id="orchestrator.nexus-graph",
            display_name="NexusGraph Orchestrator",
            node_type="orchestrator",
            domain="nexus_graph",
            teacher_ids=graph_panel,
            orchestrator_ref="NexusGraphOrchestrator",
            source_refs=["cluster13::nexusgraph-intelligence-fabric", "taxonomy::graph-orchestrators"],
        ),
        Cluster9RoleNode(
            node_id="orchestrator.memory-evolution",
            display_name="Memory Evolution Orchestrator",
            node_type="orchestrator",
            domain="agent_native_memory",
            teacher_ids=memory_panel,
            orchestrator_ref="MemoryEvolutionOrchestrator",
            source_refs=["cluster5::agentic-memory-evolution", "taxonomy::memory-orchestrators"],
        ),
        Cluster9RoleNode(
            node_id="orchestrator.graph-evolution",
            display_name="Graph Evolution Orchestrator",
            node_type="orchestrator",
            domain="nexus_graph",
            teacher_ids=graph_panel,
            orchestrator_ref="GraphEvolutionOrchestrator",
            source_refs=["cluster13::agentic-graphrag", "taxonomy::graph-orchestrators"],
        ),
        Cluster9RoleNode(
            node_id="orchestrator.recursive-dream",
            display_name="Recursive Dream Orchestrator",
            node_type="orchestrator",
            domain="recursive_dreaming",
            teacher_ids=dream_panel,
            orchestrator_ref="RecursiveDreamOrchestrator",
            source_refs=["cluster9::recursive-dreaming", "taxonomy::recursive-dreaming"],
        ),
        Cluster9RoleNode(
            node_id="ao.memory-quality",
            display_name="Memory Quality AO",
            node_type="assistant_orchestrator",
            domain="agent_native_memory",
            teacher_ids=memory_panel,
            ao_ref="MemoryQualityAO",
            source_refs=["cluster5::memory-quality", "taxonomy::memory-aos"],
        ),
        Cluster9RoleNode(
            node_id="ao.memory-privacy",
            display_name="Memory Privacy AO",
            node_type="assistant_orchestrator",
            domain="agent_native_memory",
            teacher_ids=memory_panel,
            ao_ref="MemoryPrivacyAO",
            source_refs=["cluster5::memory-privacy", "taxonomy::memory-aos"],
        ),
        Cluster9RoleNode(
            node_id="ao.memory-eval",
            display_name="Memory Eval AO",
            node_type="assistant_orchestrator",
            domain="agent_native_memory",
            teacher_ids=memory_panel,
            ao_ref="MemoryEvalAO",
            source_refs=["cluster5::memory-eval", "taxonomy::memory-aos"],
        ),
        Cluster9RoleNode(
            node_id="ao.graph-evolution",
            display_name="Graph Evolution AO",
            node_type="assistant_orchestrator",
            domain="nexus_graph",
            teacher_ids=graph_panel,
            ao_ref="GraphEvolutionAO",
            source_refs=["cluster13::graph-evolution", "taxonomy::graph-aos"],
        ),
        Cluster9RoleNode(
            node_id="ao.graph-query",
            display_name="Graph Query AO",
            node_type="assistant_orchestrator",
            domain="nexus_graph",
            teacher_ids=graph_panel,
            ao_ref="GraphQueryAO",
            source_refs=["cluster13::graph-query", "taxonomy::graph-aos"],
        ),
        Cluster9RoleNode(
            node_id="ao.graph-safety",
            display_name="Graph Safety AO",
            node_type="assistant_orchestrator",
            domain="nexus_graph",
            teacher_ids=graph_panel,
            ao_ref="GraphSafetyAO",
            source_refs=["cluster13::graph-safety", "taxonomy::graph-aos"],
        ),
        Cluster9RoleNode(
            node_id="ao.dream-review",
            display_name="Dream Review AO",
            node_type="assistant_orchestrator",
            domain="recursive_dreaming",
            teacher_ids=dream_panel,
            ao_ref="DreamReviewAO",
            source_refs=["cluster9::dream-review", "taxonomy::recursive-dreaming"],
        ),
        Cluster9RoleNode(
            node_id="ao.expert-forge",
            display_name="Expert Forge AO",
            node_type="assistant_orchestrator",
            domain="expert_evolution",
            teacher_ids=software_panel,
            ao_ref="ExpertForgeAO",
            source_refs=["cluster9::expert-birth-registry", "taxonomy::expert-evolution-aos"],
        ),
        Cluster9RoleNode(
            node_id="ao.expert-merge",
            display_name="Expert Merge AO",
            node_type="assistant_orchestrator",
            domain="expert_evolution",
            teacher_ids=software_panel,
            ao_ref="ExpertMergeAO",
            source_refs=["cluster10::expert-merge-overlap", "taxonomy::expert-evolution-aos"],
        ),
        Cluster9RoleNode(
            node_id="ao.medical",
            display_name="Medical AO",
            node_type="assistant_orchestrator",
            domain="medical",
            teacher_ids=medical_panel,
            ao_ref="MedicalAO",
            source_refs=["cluster9::medical-teachers", "taxonomy::medical-ao"],
        ),
        Cluster9RoleNode(
            node_id="expert.formal-methods-verifier",
            display_name="Formal Methods Verifier Expert",
            node_type="expert",
            domain="software",
            teacher_ids=formal_panel,
            expert_ref="formal:methods-verifier",
            source_refs=["cluster9::leanstral-formal-proof-teacher", "ontology::formal:methods-verifier"],
        ),
        Cluster9RoleNode(
            node_id="expert.memory-agent-native-memory-architect",
            display_name="Agent-Native Memory Architect Expert",
            node_type="expert",
            domain="agent_native_memory",
            teacher_ids=memory_panel,
            expert_ref="memory:agent-native-memory-architect",
            source_refs=["cluster5::agent-native-memory-os", "ontology::memory:agent-native-memory-architect"],
        ),
        Cluster9RoleNode(
            node_id="expert.memory-temporal-graph-memory-specialist",
            display_name="Temporal Graph Memory Specialist Expert",
            node_type="expert",
            domain="agent_native_memory",
            teacher_ids=memory_panel,
            expert_ref="memory:temporal-graph-memory-specialist",
            source_refs=["cluster5::temporal-graph-memory", "ontology::memory:temporal-graph-memory-specialist"],
        ),
        Cluster9RoleNode(
            node_id="expert.graph-nexusgraph-evolution-specialist",
            display_name="NexusGraph Evolution Specialist Expert",
            node_type="expert",
            domain="nexus_graph",
            teacher_ids=graph_panel,
            expert_ref="graph:nexusgraph-evolution-specialist",
            source_refs=["cluster13::graph-evolution", "ontology::graph:nexusgraph-evolution-specialist"],
        ),
        Cluster9RoleNode(
            node_id="expert.graph-graphrag-query-planner",
            display_name="GraphRAG Query Planner Expert",
            node_type="expert",
            domain="nexus_graph",
            teacher_ids=graph_panel,
            expert_ref="graph:graphrag-query-planner",
            source_refs=["cluster13::graphrag-query", "ontology::graph:graphrag-query-planner"],
        ),
        Cluster9RoleNode(
            node_id="expert.medical-safety-reviewer",
            display_name="Medical Safety Reviewer Expert",
            node_type="expert",
            domain="medical",
            teacher_ids=medical_panel,
            expert_ref="medical:safety-reviewer",
            source_refs=["cluster9::medical-teachers", "ontology::medical:safety-reviewer"],
        ),
        Cluster9RoleNode(
            node_id="expert.world-model-researcher",
            display_name="World Model Researcher Expert",
            node_type="expert",
            domain="world_models",
            teacher_ids=general_panel,
            expert_ref="world:world-model-researcher",
            source_refs=["cluster9::world-model-teachers", "ontology::world:world-model-researcher"],
        ),
        Cluster9RoleNode(
            node_id="expert.quantum-code-researcher",
            display_name="Quantum Code Researcher Expert",
            node_type="expert",
            domain="quantum_research",
            teacher_ids=quantum_panel,
            expert_ref="quantum:code-researcher",
            source_refs=["cluster9::quantum-teachers", "ontology::quantum:code-researcher"],
        ),
        Cluster9RoleNode(
            node_id="expert.crypto-defi-risk-analyst",
            display_name="DeFi Risk Analyst Expert",
            node_type="expert",
            domain="crypto",
            teacher_ids=finance_crypto_panel,
            expert_ref="crypto:defi-risk-analyst",
            source_refs=["cluster10::crypto-finance-overlap", "ontology::crypto:defi-risk-analyst"],
        ),
        Cluster9RoleNode(
            node_id="expert.finance-quant-researcher",
            display_name="Quant Finance Researcher Expert",
            node_type="expert",
            domain="finance",
            teacher_ids=finance_crypto_panel,
            expert_ref="finance:quant-researcher",
            source_refs=["cluster10::finance-expert-pack", "ontology::finance:quant-researcher"],
        ),
        Cluster9RoleNode(
            node_id="expert.dream-recursive-dream-reviewer",
            display_name="Recursive Dream Reviewer Expert",
            node_type="expert",
            domain="recursive_dreaming",
            teacher_ids=dream_panel,
            expert_ref="dream:recursive-dream-reviewer",
            source_refs=["cluster9::dream-review", "ontology::dream:recursive-dream-reviewer"],
        ),
        Cluster9RoleNode(
            node_id="temporary.runtime-crypto-risk-taskforce",
            display_name="Runtime Crypto Risk Task Force",
            node_type="temporary_expert",
            domain="crypto",
            teacher_ids=finance_crypto_panel,
            lifecycle_state="shadow",
            production_mutation_allowed=False,
            source_refs=["cluster9::live-problem-temporary-experts", "cluster10::crypto-finance-overlap"],
            retirement_policy="ttl_expiry_or_failed_eval",
            metadata={"temporary": True, "live_problem_spawn": True},
        ),
    ]
