from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


RiskTier = Literal["low", "medium", "high", "critical"]
RegulatedStatus = Literal["unregulated", "sensitive", "regulated", "blocked"]
EvidenceStandard = Literal[
    "peer_reviewed",
    "official_docs",
    "regulatory_source",
    "benchmark_result",
    "repo_source",
    "model_card",
    "empirical_internal_eval",
    "expert_consensus",
    "anecdotal",
    "speculative",
    "unsafe_or_disallowed",
]
_RISK_ORDER: dict[RiskTier, int] = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class DomainPanel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: str
    risk_tier: RiskTier
    required_roles: list[str] = Field(default_factory=list)
    evidence_standard: list[EvidenceStandard] = Field(default_factory=list)
    blocked_without_panel: bool = False


class ExpertOntologyEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expert_id: str
    display_name: str
    domain: str
    subdomain: str
    capability_traits: list[str] = Field(default_factory=list)
    risk_tier: RiskTier = "medium"
    regulated_status: RegulatedStatus = "unregulated"
    evidence_standard: list[EvidenceStandard] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    source_requirements: list[str] = Field(default_factory=list)
    teacher_pool: list[str] = Field(default_factory=list)
    critic_pool: list[str] = Field(default_factory=list)
    verifier_pool: list[str] = Field(default_factory=list)
    retriever_pool: list[str] = Field(default_factory=list)
    eval_family: list[str] = Field(default_factory=list)
    update_cadence: str = "weekly_research_refresh"
    promotion_gates: list[str] = Field(default_factory=list)
    fallback_experts: list[str] = Field(default_factory=list)
    merge_candidates: list[str] = Field(default_factory=list)
    retirement_policy: str = "retire_or_merge_after_repeated_regression"
    metadata: dict[str, Any] = Field(default_factory=dict)


class OpenWorldExpertOntology:
    def __init__(self, entries: Iterable[ExpertOntologyEntry] | None = None) -> None:
        self._entries: dict[str, ExpertOntologyEntry] = {}
        for entry in entries or []:
            self.register(entry)

    def register(self, entry: ExpertOntologyEntry | dict[str, Any], *, replace: bool = False) -> ExpertOntologyEntry:
        normalized = ExpertOntologyEntry.model_validate(
            entry.model_dump(mode="python") if isinstance(entry, ExpertOntologyEntry) else entry
        )
        if normalized.expert_id in self._entries and not replace:
            raise ValueError(f"Expert ontology entry already registered: {normalized.expert_id}")
        stored = normalized.model_copy(deep=True)
        self._entries[normalized.expert_id] = stored
        return stored.model_copy(deep=True)

    def get(self, expert_id: str) -> ExpertOntologyEntry | None:
        entry = self._entries.get(expert_id)
        return entry.model_copy(deep=True) if entry is not None else None

    def list_entries(self, *, domain: str | None = None, risk_tier: RiskTier | None = None) -> list[ExpertOntologyEntry]:
        entries = list(self._entries.values())
        if domain is not None:
            entries = [entry for entry in entries if entry.domain == domain]
        if risk_tier is not None:
            entries = [entry for entry in entries if entry.risk_tier == risk_tier]
        return [entry.model_copy(deep=True) for entry in sorted(entries, key=lambda entry: entry.expert_id)]

    def coverage_for(self, capability_traits: Iterable[str]) -> list[ExpertOntologyEntry]:
        requested = {trait.strip().lower() for trait in capability_traits if trait.strip()}
        matches = [
            entry
            for entry in self._entries.values()
            if requested.issubset({trait.lower() for trait in entry.capability_traits})
        ]
        return [entry.model_copy(deep=True) for entry in sorted(matches, key=lambda entry: entry.expert_id)]

    def classify_domain(self, text: str) -> DomainPanel:
        normalized = text.lower()
        if any(token in normalized for token in ["solidity", "smart contract", "token", "defi", "blockchain", "wallet"]):
            return self.panel_for_domain("crypto")
        if any(
            token in normalized
            for token in [
                "portfolio",
                "taxable",
                "brokerage",
                "finance",
                "financial",
                "market",
                "banking",
                "stock",
                "stocks",
                "investment",
                "investing",
                "securities",
            ]
        ):
            return self.panel_for_domain("finance")
        if any(token in normalized for token in ["supplement", "herbal", "holistic", "functional medicine", "wellness"]):
            return self.panel_for_domain("holistic_medicine")
        if any(
            token in normalized
            for token in [
                "diagnosis",
                "clinical",
                "medication",
                "radiology",
                "pathology",
                "medical",
                "treatment",
                "patient",
                "hipaa",
                "healthcare",
                "health data",
            ]
        ):
            return self.panel_for_domain("medical")
        if any(token in normalized for token in ["contract", "jurisdiction", "legal", "regulation", "compliance"]):
            return self.panel_for_domain("legal")
        if any(token in normalized for token in ["exploit", "malware", "credential", "vulnerability", "security"]):
            return self.panel_for_domain("security")
        return self.panel_for_domain("general")

    def panel_for_domain(self, domain: str) -> DomainPanel:
        entries = [entry for entry in self._entries.values() if entry.domain == domain]
        risk_tier = _max_risk_tier(entries)

        high_risk = risk_tier in {"high", "critical"}
        required_roles = (
            ["domain_expert", "risk_compliance_expert", "evidence_verifier", "critic", "source_retriever"]
            if high_risk
            else ["domain_expert", "critic"]
        )
        evidence = sorted({standard for entry in entries for standard in entry.evidence_standard})
        return DomainPanel(
            domain=domain,
            risk_tier=risk_tier,
            required_roles=required_roles,
            evidence_standard=evidence,
            blocked_without_panel=high_risk,
        )


def _max_risk_tier(entries: Iterable[ExpertOntologyEntry]) -> RiskTier:
    risks = [entry.risk_tier for entry in entries]
    if not risks:
        return "medium"
    return max(risks, key=lambda risk: _RISK_ORDER[risk])


def build_default_expert_ontology() -> OpenWorldExpertOntology:
    return OpenWorldExpertOntology(_bootstrap_entries())


def _bootstrap_entries() -> list[ExpertOntologyEntry]:
    return [
        ExpertOntologyEntry(
            expert_id="security:smart-contract-auditor",
            display_name="Smart Contract Security Auditor",
            domain="crypto",
            subdomain="smart-contract-security",
            capability_traits=["crypto", "security", "smart_contract", "audit"],
            risk_tier="high",
            regulated_status="regulated",
            evidence_standard=["official_docs", "repo_source", "benchmark_result"],
            allowed_actions=["analysis", "test_generation", "sandbox_recommendation"],
            forbidden_actions=["asset_transfer", "private_key_handling", "exploit_execution"],
            source_requirements=["protocol_docs", "contract_source", "audit_reports"],
            teacher_pool=["qwen3-coder-next", "devstral-2"],
            critic_pool=["critique"],
            verifier_pool=["security", "legal-risk", "finance-risk"],
            retriever_pool=["retrieval"],
            eval_family=["smart-contract-security", "static-analysis"],
            promotion_gates=["security_review", "license_gate", "sandbox_eval", "operator_approval"],
        ),
        ExpertOntologyEntry(
            expert_id="finance:risk-analyst",
            display_name="Financial Risk Analyst",
            domain="finance",
            subdomain="portfolio-risk",
            capability_traits=["finance", "risk", "portfolio"],
            risk_tier="high",
            regulated_status="regulated",
            evidence_standard=["official_docs", "regulatory_source", "benchmark_result"],
            allowed_actions=["education", "risk_analysis", "scenario_modeling"],
            forbidden_actions=["personalized_trade_instruction", "custody_action"],
            source_requirements=["market_data_ref", "regulatory_context", "risk_disclosure"],
            teacher_pool=["deepseek-v4-pro", "qwen3-30b-a3b"],
            critic_pool=["critique"],
            verifier_pool=["legal-risk", "finance-risk"],
            retriever_pool=["retrieval"],
            eval_family=["financial-risk", "numerical-reasoning"],
            promotion_gates=["regulatory_review", "source_verification", "operator_approval"],
        ),
        ExpertOntologyEntry(
            expert_id="medical:safety-reviewer",
            display_name="Medical Safety Reviewer",
            domain="medical",
            subdomain="clinical-safety",
            capability_traits=["medical", "safety", "clinical"],
            risk_tier="high",
            regulated_status="regulated",
            evidence_standard=["peer_reviewed", "regulatory_source", "official_docs"],
            allowed_actions=["education", "question_preparation", "literature_review"],
            forbidden_actions=["diagnosis", "treatment_directive", "emergency_triage_final_authority"],
            source_requirements=["clinical_source", "safety_disclaimer", "care_escalation_rule"],
            teacher_pool=["medgemma", "biomistral"],
            critic_pool=["critique"],
            verifier_pool=["medical-safety"],
            retriever_pool=["medical-retrieval"],
            eval_family=["medical-safety", "clinical-reasoning"],
            promotion_gates=["medical_safety_review", "source_verification", "operator_approval"],
        ),
        ExpertOntologyEntry(
            expert_id="holistic:evidence-reviewer",
            display_name="Holistic and Integrative Medicine Evidence Reviewer",
            domain="holistic_medicine",
            subdomain="integrative-evidence",
            capability_traits=["holistic_medicine", "nutrition", "supplements", "evidence_review"],
            risk_tier="high",
            regulated_status="regulated",
            evidence_standard=["peer_reviewed", "official_docs", "expert_consensus"],
            allowed_actions=["education", "evidence_grading", "interaction_question_preparation"],
            forbidden_actions=["contraindication_screening", "treatment_directive", "replace_clinician"],
            source_requirements=["peer_reviewed_source", "interaction_warning", "medical_escalation_rule"],
            teacher_pool=["medgemma", "qwen3-30b-a3b"],
            critic_pool=["critique"],
            verifier_pool=["medical-safety-reviewer"],
            retriever_pool=["medical-retrieval"],
            eval_family=["medical-safety", "claim-verification"],
            promotion_gates=["medical_safety_review", "evidence_grade_review", "operator_approval"],
        ),
        ExpertOntologyEntry(
            expert_id="legal:regulatory-risk",
            display_name="Legal and Regulatory Risk Expert",
            domain="legal",
            subdomain="regulatory-risk",
            capability_traits=["legal", "regulation", "risk"],
            risk_tier="high",
            regulated_status="regulated",
            evidence_standard=["regulatory_source", "official_docs"],
            allowed_actions=["education", "issue_spotting", "source_summary"],
            forbidden_actions=["jurisdiction_final_advice", "contract_execution"],
            source_requirements=["jurisdiction", "primary_legal_source"],
            teacher_pool=["deepseek-v4-pro", "qwen3-30b-a3b"],
            critic_pool=["critique"],
            verifier_pool=["legal-risk"],
            retriever_pool=["legal-retrieval"],
            eval_family=["legal-reasoning", "source-grounding"],
            promotion_gates=["legal_review", "source_verification", "operator_approval"],
        ),
        ExpertOntologyEntry(
            expert_id="formal:methods-verifier",
            display_name="Formal Methods Verifier",
            domain="software",
            subdomain="formal-methods",
            capability_traits=["formal_methods", "proof", "verification"],
            risk_tier="medium",
            regulated_status="sensitive",
            evidence_standard=["repo_source", "benchmark_result", "official_docs"],
            allowed_actions=["proof_review", "specification", "verification_plan"],
            forbidden_actions=["unchecked_production_mutation"],
            source_requirements=["source_code_ref", "test_or_proof_ref"],
            teacher_pool=["leanstral-1-5", "qwen3-coder-next"],
            critic_pool=["critique"],
            verifier_pool=["formal-methods"],
            retriever_pool=["retrieval"],
            eval_family=["formal-proof", "code-verification"],
            promotion_gates=["proof_check", "sandbox_eval"],
        ),
        ExpertOntologyEntry(
            expert_id="security:threat-modeler",
            display_name="Security Threat Modeler",
            domain="security",
            subdomain="threat-modeling",
            capability_traits=["security", "threat_modeling", "misuse_analysis", "secure_design"],
            risk_tier="high",
            regulated_status="sensitive",
            evidence_standard=["official_docs", "repo_source", "benchmark_result"],
            allowed_actions=["analysis", "threat_modeling", "mitigation_planning", "sandbox_recommendation"],
            forbidden_actions=["exploit_execution", "credential_access", "persistence_instruction"],
            source_requirements=["system_design_ref", "asset_inventory", "threat_context", "security_policy"],
            teacher_pool=["qwen3-coder-next", "devstral-2"],
            critic_pool=["critique"],
            verifier_pool=["security", "legal-risk"],
            retriever_pool=["retrieval"],
            eval_family=["threat-modeling", "misuse-safety", "secure-design"],
            promotion_gates=["security_review", "misuse_safety_review", "sandbox_eval", "operator_approval"],
        ),
        ExpertOntologyEntry(
            expert_id="world:world-model-researcher",
            display_name="World Model Researcher",
            domain="world_models",
            subdomain="simulation",
            capability_traits=["simulation", "world_model"],
            risk_tier="medium",
            regulated_status="sensitive",
            evidence_standard=["peer_reviewed", "benchmark_result", "official_docs"],
            allowed_actions=["simulation_plan", "model_comparison", "sandbox_recommendation"],
            forbidden_actions=["physical_action_without_safety_gate"],
            source_requirements=["benchmark_ref", "simulator_ref"],
            teacher_pool=["cosmos", "genie", "dreamer-v3", "muzero"],
            critic_pool=["critique"],
            verifier_pool=["simulation"],
            retriever_pool=["retrieval"],
            eval_family=["world-model", "robotics-sim"],
            promotion_gates=["simulation_eval", "safety_review"],
        ),
        ExpertOntologyEntry(
            expert_id="memory:agent-native-memory-architect",
            display_name="Agent-Native Memory Architect",
            domain="agent_native_memory",
            subdomain="memory-os",
            capability_traits=[
                "agent_native_memory",
                "selective_forgetting",
                "memory_eval",
                "temporal_memory",
            ],
            risk_tier="high",
            regulated_status="sensitive",
            evidence_standard=["official_docs", "benchmark_result", "empirical_internal_eval"],
            allowed_actions=["memory_schema_design", "retrieval_policy_review", "shadow_delta_review"],
            forbidden_actions=["unconsented_memory_write", "raw_private_memory_exposure"],
            source_requirements=["memory_source_ref", "privacy_class", "rollback_ref"],
            teacher_pool=["mem0-memory", "graphiti-zep-memory", "qwen3-coder-next"],
            critic_pool=["critique"],
            verifier_pool=["memory-quality", "privacy"],
            retriever_pool=["memory-retrieval"],
            eval_family=["memory-quality", "privacy-preservation", "retrieval-grounding"],
            promotion_gates=["MemoryEvolutionPassport", "privacy_review", "retrieval_eval", "operator_approval"],
        ),
        ExpertOntologyEntry(
            expert_id="memory:temporal-graph-memory-specialist",
            display_name="Temporal Graph Memory Specialist",
            domain="agent_native_memory",
            subdomain="temporal-graph-memory",
            capability_traits=["agent_native_memory", "temporal_graph", "contradiction_resolution"],
            risk_tier="high",
            regulated_status="sensitive",
            evidence_standard=["official_docs", "benchmark_result", "empirical_internal_eval"],
            allowed_actions=["temporal_link_review", "contradiction_review", "shadow_graph_memory_delta"],
            forbidden_actions=["stale_fact_promotion", "privacy_bypass"],
            source_requirements=["valid_time", "observed_time", "source_hash", "contradiction_refs"],
            teacher_pool=["graphiti-zep-memory", "mem0-memory"],
            critic_pool=["critique"],
            verifier_pool=["memory-quality", "graph-safety"],
            retriever_pool=["memory-retrieval", "graph-retrieval"],
            eval_family=["temporal-memory", "long-context-memory", "contradiction-detection"],
            promotion_gates=["MemoryEvolutionPassport", "GraphFactPassport", "privacy_review"],
        ),
        ExpertOntologyEntry(
            expert_id="graph:nexusgraph-evolution-specialist",
            display_name="NexusGraph Evolution Specialist",
            domain="nexus_graph",
            subdomain="graph-evolution",
            capability_traits=["graph", "graph_evolution", "impact_analysis", "ontology_evolution"],
            risk_tier="high",
            regulated_status="sensitive",
            evidence_standard=["official_docs", "repo_source", "benchmark_result"],
            allowed_actions=["shadow_graph_delta", "impact_analysis", "ontology_review"],
            forbidden_actions=["production_graph_mutation_without_gate", "permission_bypass"],
            source_requirements=["graph_delta", "affected_nodes", "affected_edges", "rollback_ref"],
            teacher_pool=["lightrag-graphrag", "graphiti-zep-memory", "qwen3-coder-next"],
            critic_pool=["critique"],
            verifier_pool=["graph-safety", "security"],
            retriever_pool=["graph-retrieval"],
            eval_family=["graphrag", "graph-query", "impact-analysis"],
            promotion_gates=["GraphEvolutionPassport", "GraphFactPassport", "privacy_review", "operator_approval"],
        ),
        ExpertOntologyEntry(
            expert_id="graph:graphrag-query-planner",
            display_name="GraphRAG Query Planner",
            domain="nexus_graph",
            subdomain="graphrag-query",
            capability_traits=["graph", "graphrag", "multi_hop_query", "retrieval_planning"],
            risk_tier="high",
            regulated_status="sensitive",
            evidence_standard=["official_docs", "benchmark_result", "empirical_internal_eval"],
            allowed_actions=["query_plan", "retrieval_plan", "source_grounding_review"],
            forbidden_actions=["uncited_answer_promotion", "private_subgraph_exposure"],
            source_requirements=["query_trace", "source_refs", "privacy_filter"],
            teacher_pool=["lightrag-graphrag", "graphiti-zep-memory"],
            critic_pool=["critique"],
            verifier_pool=["graph-eval", "privacy"],
            retriever_pool=["graph-retrieval"],
            eval_family=["graphrag", "multi-hop-retrieval", "source-grounding"],
            promotion_gates=["GraphQueryPassport", "GraphFactPassport", "privacy_review"],
        ),
        ExpertOntologyEntry(
            expert_id="quantum:code-researcher",
            display_name="Quantum Code Researcher",
            domain="quantum_research",
            subdomain="quantum-code",
            capability_traits=["quantum", "qiskit", "circuit_reasoning", "research"],
            risk_tier="medium",
            regulated_status="sensitive",
            evidence_standard=["peer_reviewed", "official_docs", "benchmark_result"],
            allowed_actions=["circuit_review", "qiskit_code_review", "research_synthesis"],
            forbidden_actions=["hardware_truth_claim", "unsafe_lab_instruction"],
            source_requirements=["paper_ref", "simulator_ref", "code_ref"],
            teacher_pool=["qiskit-quantum-code", "leanstral-1-5"],
            critic_pool=["critique"],
            verifier_pool=["formal-methods", "simulation"],
            retriever_pool=["research-retrieval"],
            eval_family=["quantum-circuit-reasoning", "formal-proof"],
            promotion_gates=["simulation_eval", "source_verification", "operator_approval"],
        ),
        ExpertOntologyEntry(
            expert_id="crypto:defi-risk-analyst",
            display_name="DeFi Risk Analyst",
            domain="crypto",
            subdomain="defi-risk",
            capability_traits=["crypto", "finance", "defi", "risk"],
            risk_tier="high",
            regulated_status="regulated",
            evidence_standard=["official_docs", "regulatory_source", "benchmark_result"],
            allowed_actions=["risk_analysis", "protocol_research", "scenario_modeling"],
            forbidden_actions=["asset_transfer", "private_key_handling", "personalized_trade_instruction"],
            source_requirements=["protocol_docs", "market_data_ref", "risk_disclosure"],
            teacher_pool=["market-risk-simulator", "deepseek-v4-pro", "qwen3-30b-a3b"],
            critic_pool=["critique"],
            verifier_pool=["security", "finance-risk", "legal-risk"],
            retriever_pool=["retrieval"],
            eval_family=["defi-risk", "financial-risk", "smart-contract-security"],
            promotion_gates=["security_review", "financial_risk_review", "operator_approval"],
        ),
        ExpertOntologyEntry(
            expert_id="finance:quant-researcher",
            display_name="Quant Finance Researcher",
            domain="finance",
            subdomain="quant-research",
            capability_traits=["finance", "quant", "market_simulation", "risk"],
            risk_tier="high",
            regulated_status="regulated",
            evidence_standard=["official_docs", "regulatory_source", "benchmark_result"],
            allowed_actions=["research", "risk_modeling", "scenario_modeling"],
            forbidden_actions=["personalized_trade_instruction", "custody_action"],
            source_requirements=["market_data_ref", "regulatory_context", "risk_disclosure"],
            teacher_pool=["market-risk-simulator", "deepseek-v4-pro", "qwen3-30b-a3b"],
            critic_pool=["critique"],
            verifier_pool=["finance-risk", "legal-risk"],
            retriever_pool=["retrieval"],
            eval_family=["financial-risk", "numerical-reasoning", "market-simulation"],
            promotion_gates=["regulatory_review", "source_verification", "operator_approval"],
        ),
        ExpertOntologyEntry(
            expert_id="dream:recursive-dream-reviewer",
            display_name="Recursive Dream Reviewer",
            domain="recursive_dreaming",
            subdomain="dream-review",
            capability_traits=["dream_review", "counterfactual_eval", "creative_proposal_review"],
            risk_tier="high",
            regulated_status="sensitive",
            evidence_standard=["empirical_internal_eval", "benchmark_result", "expert_consensus"],
            allowed_actions=["dream_proposal_review", "counterfactual_risk_review", "shadow_candidate_triage"],
            forbidden_actions=["production_mutation_without_eval", "unreviewed_high_temperature_output_promotion"],
            source_requirements=["dream_trace", "review_trace", "eval_delta", "rollback_ref"],
            teacher_pool=["qwen3-30b-a3b", "deepseek-v4-pro"],
            critic_pool=["critique"],
            verifier_pool=["evals", "safety"],
            retriever_pool=["memory-retrieval", "graph-retrieval"],
            eval_family=["dream-review", "self-improvement-safety", "novelty-vs-risk"],
            promotion_gates=["dream_review", "eval_evidence", "operator_approval"],
        ),
    ]
