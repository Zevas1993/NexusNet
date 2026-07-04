# Open-World Expert Ontology Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first shippable NexusNet foundation for open-world experts and teacher candidates: typed expert ontology, domain risk panels, bootstrap high-risk domains, and a teacher candidate universe registry.

**Architecture:** Add two focused registry modules instead of editing the large runtime spine first. `nexusnet/experts/ontology.py` owns domain expertise, risk tiers, evidence standards, and routing panel requirements. `nexusnet/teachers/candidate_universe.py` owns changing model/tool teacher candidates, quarantine state, and promotion blockers.

**Tech Stack:** Python 3.11+, Pydantic v2, pytest, existing NexusNet package exports, GitNexus change detection.

---

## Scope Boundary

This plan implements the foundation slice from the approved design:

- Expert ontology schema and static bootstrap domain taxonomy.
- Risk-tier and evidence-standard metadata.
- Teacher/model/tool candidate universe schema.
- Tests proving crypto, finance, medical, holistic medicine, security, and formal-verification coverage.

This plan intentionally does not implement AO registry expansion, API routes, control-panel UI, recursive dream integration, temporary task-force lifecycle, expert merge/split, or auto-research ingestion. Those attach cleanly after this foundation exists.

## File Structure

- Create: `nexusnet/experts/ontology.py`
  - Owns `ExpertOntologyEntry`, `DomainPanel`, `OpenWorldExpertOntology`, bootstrap entries, domain classification, panel rules, and coverage lookup.
- Modify: `nexusnet/experts/__init__.py`
  - Exports the ontology registry and models.
- Create: `nexusnet/teachers/candidate_universe.py`
  - Owns `TeacherCandidate`, candidate status and role types, `TeacherCandidateUniverse`, promotion blocker checks, and bootstrap watchlist entries.
- Modify: `nexusnet/teachers/__init__.py`
  - Exports the candidate universe registry and models.
- Create: `tests/test_open_world_expert_ontology.py`
  - Tests ontology bootstrap, high-risk panel routing, coverage lookup, and temporary expert registration behavior.
- Create: `tests/test_teacher_candidate_universe.py`
  - Tests candidate quarantine, promotion blockers, and an evidenced shadow candidate.

## GitNexus Guardrails

- Before editing existing functions/classes/methods, run GitNexus impact analysis for the symbol and report risk.
- This plan only adds new modules and appends package exports. If implementation changes an existing function/class/method beyond package exports, stop and run `mcp__gitnexus.impact` for that symbol first.
- Before final completion, run GitNexus detect-changes for `NexusNet` and report the affected scope. If the MCP tool is unavailable, state that limitation and use `git diff --stat` plus focused tests as fallback evidence.

---

### Task 1: Add Failing Expert Ontology Tests

**Files:**
- Create: `tests/test_open_world_expert_ontology.py`

- [ ] **Step 1: Create the test file**

```python
from __future__ import annotations

from nexusnet.experts import ExpertOntologyEntry, build_default_expert_ontology


def test_bootstrap_ontology_covers_high_risk_domains_with_required_panels():
    ontology = build_default_expert_ontology()

    expected_domains = {"crypto", "finance", "medical", "holistic_medicine", "legal", "security"}
    actual_domains = {entry.domain for entry in ontology.list_entries()}
    assert expected_domains.issubset(actual_domains)

    crypto_panel = ontology.panel_for_domain("crypto")
    assert crypto_panel.risk_tier == "high"
    assert crypto_panel.required_roles == [
        "domain_expert",
        "risk_compliance_expert",
        "evidence_verifier",
        "critic",
        "source_retriever",
    ]

    holistic = ontology.get("holistic:evidence-reviewer")
    assert holistic is not None
    assert holistic.risk_tier == "high"
    assert "contraindication_screening" in holistic.forbidden_actions
    assert "peer_reviewed" in holistic.evidence_standard
    assert "medical-safety-reviewer" in holistic.verifier_pool


def test_domain_classifier_routes_crypto_finance_and_holistic_queries_to_high_risk_panels():
    ontology = build_default_expert_ontology()

    crypto = ontology.classify_domain("Audit this Solidity bridge contract and tokenomics risk.")
    assert crypto.domain == "crypto"
    assert crypto.risk_tier == "high"
    assert "risk_compliance_expert" in crypto.required_roles

    finance = ontology.classify_domain("Build a portfolio risk model for taxable brokerage allocation.")
    assert finance.domain == "finance"
    assert finance.risk_tier == "high"
    assert "evidence_verifier" in finance.required_roles

    holistic = ontology.classify_domain("Check supplement and herbal interactions with sleep medication.")
    assert holistic.domain == "holistic_medicine"
    assert holistic.risk_tier == "high"
    assert "source_retriever" in holistic.required_roles


def test_capability_lookup_finds_formal_methods_and_world_model_experts():
    ontology = build_default_expert_ontology()

    formal = ontology.coverage_for(["formal_methods", "proof"])
    assert [entry.expert_id for entry in formal] == ["formal:methods-verifier"]

    world = ontology.coverage_for(["simulation", "world_model"])
    assert [entry.expert_id for entry in world] == ["world:world-model-researcher"]


def test_temporary_expert_registration_is_shadow_scoped_and_does_not_replace_bootstrap():
    ontology = build_default_expert_ontology()
    before_count = len(ontology.list_entries())

    temporary = ExpertOntologyEntry(
        expert_id="temporary:runtime-crypto-risk-taskforce",
        display_name="Runtime Crypto Risk Task Force",
        domain="crypto",
        subdomain="runtime-risk",
        capability_traits=["runtime", "crypto", "risk"],
        risk_tier="high",
        regulated_status="regulated",
        evidence_standard=["official_docs", "benchmark_result"],
        allowed_actions=["analysis", "sandbox_recommendation"],
        forbidden_actions=["asset_transfer", "private_key_handling"],
        source_requirements=["official_protocol_docs", "security_audit_refs"],
        teacher_pool=["qwen3-coder-next", "deepseek-v4-pro"],
        critic_pool=["critique"],
        verifier_pool=["security", "legal-risk", "finance-risk"],
        retriever_pool=["retrieval"],
        eval_family=["smart-contract-security", "financial-risk"],
        update_cadence="live_problem_ttl",
        promotion_gates=["sandbox_eval", "security_review", "operator_approval"],
        fallback_experts=["security:smart-contract-auditor"],
        merge_candidates=["security:smart-contract-auditor"],
        retirement_policy="ttl_expiry_or_failed_eval",
        metadata={"temporary": True, "production_mutation_allowed": False},
    )

    ontology.register(temporary)

    assert len(ontology.list_entries()) == before_count + 1
    assert ontology.get("temporary:runtime-crypto-risk-taskforce") == temporary
    assert ontology.get("security:smart-contract-auditor") is not None
    assert ontology.get("temporary:runtime-crypto-risk-taskforce").metadata["production_mutation_allowed"] is False
```

- [ ] **Step 2: Run the ontology tests and verify they fail**

Run:

```powershell
pytest tests/test_open_world_expert_ontology.py -q
```

Expected: FAIL with `ModuleNotFoundError` or import error for `ExpertOntologyEntry` / `build_default_expert_ontology`.

- [ ] **Step 3: Commit the failing test**

```powershell
git add tests/test_open_world_expert_ontology.py
git commit -m "test: define open-world expert ontology behavior"
```

---

### Task 2: Implement Expert Ontology Registry

**Files:**
- Create: `nexusnet/experts/ontology.py`
- Modify: `nexusnet/experts/__init__.py`
- Test: `tests/test_open_world_expert_ontology.py`

- [ ] **Step 1: Create `nexusnet/experts/ontology.py`**

```python
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

    def register(self, entry: ExpertOntologyEntry | dict[str, Any]) -> ExpertOntologyEntry:
        normalized = entry if isinstance(entry, ExpertOntologyEntry) else ExpertOntologyEntry.model_validate(entry)
        self._entries[normalized.expert_id] = normalized
        return normalized

    def get(self, expert_id: str) -> ExpertOntologyEntry | None:
        return self._entries.get(expert_id)

    def list_entries(self, *, domain: str | None = None, risk_tier: RiskTier | None = None) -> list[ExpertOntologyEntry]:
        entries = list(self._entries.values())
        if domain is not None:
            entries = [entry for entry in entries if entry.domain == domain]
        if risk_tier is not None:
            entries = [entry for entry in entries if entry.risk_tier == risk_tier]
        return sorted(entries, key=lambda entry: entry.expert_id)

    def coverage_for(self, capability_traits: Iterable[str]) -> list[ExpertOntologyEntry]:
        requested = {trait.strip().lower() for trait in capability_traits if trait.strip()}
        matches = [
            entry
            for entry in self._entries.values()
            if requested.issubset({trait.lower() for trait in entry.capability_traits})
        ]
        return sorted(matches, key=lambda entry: entry.expert_id)

    def classify_domain(self, text: str) -> DomainPanel:
        normalized = text.lower()
        if any(token in normalized for token in ["solidity", "smart contract", "token", "defi", "blockchain", "wallet"]):
            return self.panel_for_domain("crypto")
        if any(token in normalized for token in ["portfolio", "taxable", "brokerage", "finance", "market", "banking"]):
            return self.panel_for_domain("finance")
        if any(token in normalized for token in ["supplement", "herbal", "holistic", "functional medicine", "wellness"]):
            return self.panel_for_domain("holistic_medicine")
        if any(token in normalized for token in ["diagnosis", "clinical", "medication", "radiology", "pathology"]):
            return self.panel_for_domain("medical")
        if any(token in normalized for token in ["contract", "jurisdiction", "legal", "regulation", "compliance"]):
            return self.panel_for_domain("legal")
        if any(token in normalized for token in ["exploit", "malware", "credential", "vulnerability", "security"]):
            return self.panel_for_domain("security")
        return self.panel_for_domain("general")

    def panel_for_domain(self, domain: str) -> DomainPanel:
        entries = self.list_entries(domain=domain)
        risk_tier: RiskTier = "medium"
        if any(entry.risk_tier == "critical" for entry in entries):
            risk_tier = "critical"
        elif any(entry.risk_tier == "high" for entry in entries):
            risk_tier = "high"
        elif any(entry.risk_tier == "low" for entry in entries):
            risk_tier = "low"

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
    ]
```

- [ ] **Step 2: Export ontology symbols**

Edit `nexusnet/experts/__init__.py` to exactly:

```python
from .execution import InternalExpertExecutionService
from .harness import InternalExpertHarnessService
from .ontology import DomainPanel, ExpertOntologyEntry, OpenWorldExpertOntology, build_default_expert_ontology
from .runtime import InternalExpertRuntimeService

__all__ = [
    "DomainPanel",
    "ExpertOntologyEntry",
    "InternalExpertExecutionService",
    "InternalExpertHarnessService",
    "InternalExpertRuntimeService",
    "OpenWorldExpertOntology",
    "build_default_expert_ontology",
]
```

- [ ] **Step 3: Run the ontology tests and verify they pass**

Run:

```powershell
pytest tests/test_open_world_expert_ontology.py -q
```

Expected: `4 passed`.

- [ ] **Step 4: Run import smoke**

Run:

```powershell
python -c "from nexusnet.experts import build_default_expert_ontology; print(len(build_default_expert_ontology().list_entries()))"
```

Expected: `7`

- [ ] **Step 5: Commit ontology implementation**

```powershell
git add nexusnet/experts/ontology.py nexusnet/experts/__init__.py tests/test_open_world_expert_ontology.py
git commit -m "feat: add open-world expert ontology"
```

---

### Task 3: Add Failing Teacher Candidate Universe Tests

**Files:**
- Create: `tests/test_teacher_candidate_universe.py`

- [ ] **Step 1: Create the test file**

```python
from __future__ import annotations

from nexusnet.teachers import TeacherCandidate, build_default_teacher_candidate_universe


def test_candidate_universe_bootstraps_watchlist_without_active_promotion():
    universe = build_default_teacher_candidate_universe()

    leanstral = universe.get("leanstral-1-5")
    assert leanstral is not None
    assert leanstral.candidate_status == "watchlist"
    assert "verifier" in leanstral.teacher_roles
    assert "formal_methods" in leanstral.domain_scope
    assert universe.promotion_blockers("leanstral-1-5") == [
        "candidate_status_not_shadow_or_canary",
        "license_gate_not_approved",
        "privacy_gate_not_approved",
        "hardware_gate_not_approved",
        "cost_gate_not_approved",
        "benchmark_refs_missing",
    ]


def test_quarantined_unlicensed_candidate_is_blocked_from_promotion():
    universe = build_default_teacher_candidate_universe()
    candidate = TeacherCandidate(
        candidate_id="frontier-remote-council",
        model_or_tool_id="remote/frontier-council",
        provider="remote",
        source_url="https://example.invalid/frontier",
        candidate_status="quarantined",
        teacher_roles=["critic", "judge"],
        license_gate="needs_review",
        privacy_gate="blocked",
        hardware_gate="not_required",
        cost_gate="needs_review",
        eval_family=["agentic-reasoning"],
        domain_scope=["orchestration"],
        risk_scope=["high"],
        source_refs=["model-card::frontier-council"],
    )
    universe.register(candidate)

    assert universe.get("frontier-remote-council") == candidate
    assert universe.promotion_allowed("frontier-remote-council") is False
    assert "privacy_gate_blocked" in universe.promotion_blockers("frontier-remote-council")


def test_evidenced_shadow_candidate_can_be_promotion_ready():
    universe = build_default_teacher_candidate_universe()
    universe.register(
        {
            "candidate_id": "qwen3-coder-next-shadow",
            "model_or_tool_id": "Qwen/Qwen3-Coder-Next",
            "provider": "huggingface",
            "source_url": "https://huggingface.co/Qwen/Qwen3-Coder-Next",
            "candidate_status": "shadow",
            "teacher_roles": ["generator", "critic"],
            "license_gate": "approved",
            "privacy_gate": "approved",
            "hardware_gate": "approved",
            "cost_gate": "approved",
            "eval_family": ["coding", "agentic-software"],
            "domain_scope": ["software", "coding"],
            "risk_scope": ["medium"],
            "source_refs": ["hf::Qwen/Qwen3-Coder-Next"],
            "benchmark_refs": ["eval::swebench-shadow"],
            "replacement_candidates": ["devstral-2"],
        }
    )

    assert universe.promotion_allowed("qwen3-coder-next-shadow") is True
    summary = universe.summary()
    assert summary["candidate_count"] >= 4
    assert summary["promotion_ready_count"] == 1
    assert "qwen3-coder-next-shadow" in summary["promotion_ready_candidate_ids"]
```

- [ ] **Step 2: Run the candidate universe tests and verify they fail**

Run:

```powershell
pytest tests/test_teacher_candidate_universe.py -q
```

Expected: FAIL with import error for `TeacherCandidate` / `build_default_teacher_candidate_universe`.

- [ ] **Step 3: Commit the failing test**

```powershell
git add tests/test_teacher_candidate_universe.py
git commit -m "test: define teacher candidate universe behavior"
```

---

### Task 4: Implement Teacher Candidate Universe

**Files:**
- Create: `nexusnet/teachers/candidate_universe.py`
- Modify: `nexusnet/teachers/__init__.py`
- Test: `tests/test_teacher_candidate_universe.py`

- [ ] **Step 1: Create `nexusnet/teachers/candidate_universe.py`**

```python
from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


CandidateStatus = Literal["watchlist", "quarantined", "benchmarked", "shadow", "canary", "active", "retired", "blocked"]
TeacherRole = Literal["generator", "critic", "verifier", "retriever", "simulator", "compact_apprentice", "judge"]
GateStatus = Literal["approved", "blocked", "needs_review", "not_required"]


class TeacherCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    model_or_tool_id: str
    provider: str
    source_url: str
    candidate_status: CandidateStatus = "watchlist"
    teacher_roles: list[TeacherRole] = Field(default_factory=list)
    license_gate: GateStatus = "needs_review"
    privacy_gate: GateStatus = "needs_review"
    hardware_gate: GateStatus = "needs_review"
    cost_gate: GateStatus = "needs_review"
    eval_family: list[str] = Field(default_factory=list)
    domain_scope: list[str] = Field(default_factory=list)
    risk_scope: list[str] = Field(default_factory=list)
    last_researched_at: str | None = None
    source_refs: list[str] = Field(default_factory=list)
    benchmark_refs: list[str] = Field(default_factory=list)
    replacement_candidates: list[str] = Field(default_factory=list)
    retirement_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TeacherCandidateUniverse:
    def __init__(self, candidates: Iterable[TeacherCandidate] | None = None) -> None:
        self._candidates: dict[str, TeacherCandidate] = {}
        for candidate in candidates or []:
            self.register(candidate)

    def register(self, candidate: TeacherCandidate | dict[str, Any]) -> TeacherCandidate:
        normalized = candidate if isinstance(candidate, TeacherCandidate) else TeacherCandidate.model_validate(candidate)
        self._candidates[normalized.candidate_id] = normalized
        return normalized

    def get(self, candidate_id: str) -> TeacherCandidate | None:
        return self._candidates.get(candidate_id)

    def list_candidates(
        self,
        *,
        status: CandidateStatus | None = None,
        role: TeacherRole | None = None,
        domain: str | None = None,
    ) -> list[TeacherCandidate]:
        candidates = list(self._candidates.values())
        if status is not None:
            candidates = [candidate for candidate in candidates if candidate.candidate_status == status]
        if role is not None:
            candidates = [candidate for candidate in candidates if role in candidate.teacher_roles]
        if domain is not None:
            candidates = [candidate for candidate in candidates if domain in candidate.domain_scope]
        return sorted(candidates, key=lambda candidate: candidate.candidate_id)

    def promotion_allowed(self, candidate_id: str) -> bool:
        return not self.promotion_blockers(candidate_id)

    def promotion_blockers(self, candidate_id: str) -> list[str]:
        candidate = self.get(candidate_id)
        if candidate is None:
            return ["candidate_missing"]

        blockers: list[str] = []
        if candidate.candidate_status not in {"shadow", "canary"}:
            blockers.append("candidate_status_not_shadow_or_canary")
        for gate_name in ("license_gate", "privacy_gate", "hardware_gate", "cost_gate"):
            gate_value = getattr(candidate, gate_name)
            if gate_value == "blocked":
                blockers.append(f"{gate_name}_blocked")
            elif gate_value not in {"approved", "not_required"}:
                blockers.append(f"{gate_name}_not_approved")
        if not candidate.source_refs:
            blockers.append("source_refs_missing")
        if not candidate.benchmark_refs:
            blockers.append("benchmark_refs_missing")
        if candidate.retirement_reason:
            blockers.append("candidate_retired")
        return blockers

    def summary(self) -> dict[str, Any]:
        candidates = self.list_candidates()
        promotion_ready = [candidate for candidate in candidates if self.promotion_allowed(candidate.candidate_id)]
        by_status: dict[str, int] = {}
        for candidate in candidates:
            by_status[candidate.candidate_status] = by_status.get(candidate.candidate_status, 0) + 1
        return {
            "surface_id": "teacher-candidate-universe",
            "candidate_count": len(candidates),
            "status_counts": by_status,
            "promotion_ready_count": len(promotion_ready),
            "promotion_ready_candidate_ids": [candidate.candidate_id for candidate in promotion_ready],
            "autonomy_rule": "new-teacher-candidates-start-watchlist-or-quarantined-and-require-source-license-privacy-hardware-cost-benchmark-gates-before-promotion",
        }


def build_default_teacher_candidate_universe() -> TeacherCandidateUniverse:
    return TeacherCandidateUniverse(
        [
            TeacherCandidate(
                candidate_id="leanstral-1-5",
                model_or_tool_id="mistralai/Leanstral-1.5-119B-A6B",
                provider="huggingface",
                source_url="https://huggingface.co/mistralai/Leanstral-1.5-119B-A6B",
                candidate_status="watchlist",
                teacher_roles=["verifier", "critic"],
                license_gate="needs_review",
                privacy_gate="needs_review",
                hardware_gate="needs_review",
                cost_gate="needs_review",
                eval_family=["formal-proof", "math", "code-verification"],
                domain_scope=["formal_methods", "math", "coding", "quantum"],
                risk_scope=["medium", "high"],
                source_refs=["hf::mistralai/Leanstral-1.5-119B-A6B"],
                replacement_candidates=["qwen3-coder-next", "deepseek-v4-pro"],
            ),
            TeacherCandidate(
                candidate_id="qwen3-coder-next",
                model_or_tool_id="Qwen/Qwen3-Coder-Next",
                provider="huggingface",
                source_url="https://huggingface.co/Qwen/Qwen3-Coder-Next",
                candidate_status="watchlist",
                teacher_roles=["generator", "critic"],
                license_gate="approved",
                privacy_gate="needs_review",
                hardware_gate="needs_review",
                cost_gate="needs_review",
                eval_family=["coding", "agentic-software"],
                domain_scope=["software", "coding"],
                risk_scope=["medium"],
                source_refs=["hf::Qwen/Qwen3-Coder-Next"],
            ),
            TeacherCandidate(
                candidate_id="medgemma-1-5-4b",
                model_or_tool_id="google/medgemma-1.5-4b-it",
                provider="huggingface",
                source_url="https://huggingface.co/google/medgemma-1.5-4b-it",
                candidate_status="quarantined",
                teacher_roles=["critic", "verifier"],
                license_gate="needs_review",
                privacy_gate="needs_review",
                hardware_gate="approved",
                cost_gate="approved",
                eval_family=["medical-safety", "clinical-reasoning"],
                domain_scope=["medical", "holistic_medicine"],
                risk_scope=["high"],
                source_refs=["hf::google/medgemma-1.5-4b-it"],
            ),
        ]
    )
```

- [ ] **Step 2: Export candidate universe symbols**

Edit `nexusnet/teachers/__init__.py` by adding this import block:

```python
from .candidate_universe import TeacherCandidate, TeacherCandidateUniverse, build_default_teacher_candidate_universe
```

Add these names to `__all__`:

```python
    "TeacherCandidate",
    "TeacherCandidateUniverse",
    "build_default_teacher_candidate_universe",
```

- [ ] **Step 3: Run candidate universe tests**

Run:

```powershell
pytest tests/test_teacher_candidate_universe.py -q
```

Expected: `3 passed`.

- [ ] **Step 4: Run import smoke**

Run:

```powershell
python -c "from nexusnet.teachers import build_default_teacher_candidate_universe; print(build_default_teacher_candidate_universe().summary()['candidate_count'])"
```

Expected: `3`

- [ ] **Step 5: Commit candidate universe implementation**

```powershell
git add nexusnet/teachers/candidate_universe.py nexusnet/teachers/__init__.py tests/test_teacher_candidate_universe.py
git commit -m "feat: add teacher candidate universe registry"
```

---

### Task 5: Run Foundation Integration Verification

**Files:**
- Verify: `nexusnet/experts/ontology.py`
- Verify: `nexusnet/teachers/candidate_universe.py`
- Verify: `tests/test_open_world_expert_ontology.py`
- Verify: `tests/test_teacher_candidate_universe.py`

- [ ] **Step 1: Run focused test batch**

Run:

```powershell
pytest tests/test_open_world_expert_ontology.py tests/test_teacher_candidate_universe.py -q
```

Expected: `7 passed`.

- [ ] **Step 2: Run adjacent committed registry tests**

Run:

```powershell
pytest tests/test_teacher_registry.py -q
```

Expected: all tests pass. The untracked forward-radar registry surface present in the main checkout is intentionally excluded from this isolated worktree's baseline because it is not part of the committed branch state.

- [ ] **Step 3: Run syntax compile on changed modules**

Run:

```powershell
python -m py_compile nexusnet/experts/ontology.py nexusnet/teachers/candidate_universe.py
```

Expected: no output and exit code `0`.

- [ ] **Step 4: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected: no output and exit code `0`.

- [ ] **Step 5: Run GitNexus detect-changes**

Run:

```json
mcp__gitnexus.detect_changes({"repo": "NexusNet", "scope": "all"})
```

Expected: changes are limited to new ontology/candidate registry modules, package exports, and the two focused test files. Report any broader dirty-tree noise separately as pre-existing or unrelated if it appears.

- [ ] **Step 6: Commit verification note if needed**

If implementation added a small docs note or changed this plan while executing, commit it separately:

```powershell
git add docs/superpowers/plans/2026-07-04-open-world-expert-ontology-foundation.md
git commit -m "docs: update open-world ontology implementation plan"
```

Do not commit unrelated dirty-tree files.

## Follow-On Plans After This Foundation

After this foundation passes, write separate plans for:

1. AO registry expansion using the new ontology and candidate universe.
2. Recursive dreaming candidate metadata integration.
3. Temporary task-force expert lifecycle.
4. Expert merge/split lifecycle and rollback.
5. Auto-research source intake and candidate universe refresh.
6. Promotion tribunal and UI/control-panel visibility.
