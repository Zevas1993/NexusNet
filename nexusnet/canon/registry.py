from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator


RegistryStatus = Literal[
    "locked",
    "candidate",
    "candidate_requires_pin",
    "unresolved",
    "disabled",
    "research_only",
    "diagnostic_only",
]


class EvidenceBackedRecord(BaseModel):
    status: RegistryStatus
    evidence: list[str] = Field(min_length=1)
    license: str = Field(min_length=1)
    verified_at: str = Field(min_length=1)

    @field_validator("evidence")
    @classmethod
    def evidence_items_must_be_present(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            raise ValueError("evidence items must be non-empty")
        return value


class CanonicalDecision(EvidenceBackedRecord):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    decision: str = Field(min_length=1)
    owner: str = "architecture"
    notes: str = ""


class ResearchCandidate(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    verified_at: str = Field(min_length=1)
    license: str = Field(min_length=1)
    evidence_level: str = Field(min_length=1)
    integration_status: RegistryStatus
    maturity: str = "candidate"
    replacement_target: str = Field(min_length=1)
    notes: str = Field(min_length=1)


class ExpertCapsule(EvidenceBackedRecord):
    capsule_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    roster_position: int = Field(ge=1)
    capabilities: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    eval_coverage: list[str] = Field(default_factory=list)
    memory_access: list[str] = Field(default_factory=list)
    teacher_policy: dict[str, Any] = Field(default_factory=dict)


class TeacherCapability(EvidenceBackedRecord):
    teacher_id: str
    capability_id: str
    provider_role: str = "replaceable_capability_provider"
    subjects: list[str] = Field(default_factory=list)
    modalities: list[str] = Field(default_factory=lambda: ["text"])


class ModelCandidate(EvidenceBackedRecord):
    model_id: str
    provider: str
    role: str
    runnable: bool = False


class RuntimeCandidate(EvidenceBackedRecord):
    runtime_id: str
    mode: str
    adapter: str
    runnable: bool = False
    fallback_profile: str = "mock"
    context_strategy: str = "effective_context"


class MemoryPlane(EvidenceBackedRecord):
    plane_id: str
    lifecycle: list[str] = Field(default_factory=list)
    provenance_required: bool = True


class MemoryOperation(EvidenceBackedRecord):
    operation_id: str
    allowed_states: list[str] = Field(default_factory=list)
    provenance_required: bool = True


class ProtocolAdapter(EvidenceBackedRecord):
    adapter_id: str
    protocol: Literal["mcp", "a2a", "ag-ui"]
    enabled_by_default: bool = False
    security_envelope_required: bool = True


class SecurityPolicy(EvidenceBackedRecord):
    tool_id: str
    protocol: Literal["mcp", "a2a", "ag-ui"]
    identity_required: bool = True
    sandbox_required: bool = True
    permissions: list[str] = Field(default_factory=list)
    elicitation_modes: list[str] = Field(default_factory=list)
    approval_required: bool = True
    deny_reason: str | None = None


class TraceEvent(EvidenceBackedRecord):
    trace_id: str
    input_id: str
    brain_path: str
    capsule_routes: list[dict[str, Any]] = Field(default_factory=list)
    memory_operations: list[dict[str, Any]] = Field(default_factory=list)
    tool_attempts: list[dict[str, Any]] = Field(default_factory=list)
    security_decisions: list[dict[str, Any]] = Field(default_factory=list)
    critique_events: list[dict[str, Any]] = Field(default_factory=list)
    eval_labels: list[str] = Field(default_factory=list)


class EvalScenario(EvidenceBackedRecord):
    scenario_id: str
    category: str
    measurable_signal: str
    trace_labels: list[str] = Field(default_factory=list)


class EBTScore(EvidenceBackedRecord):
    score_id: str
    confidence: float = Field(ge=0.0, le=1.0)
    risk: float = Field(ge=0.0, le=1.0)
    capsule_choice: str
    memory_influence: str
    fallback_reason: str | None = None
    critique_result: str


class NexusNetCanonRegistry:
    verified_at = "2026-04-26"

    def __init__(self, *, live_teacher_registry_path: Path | None = None, persistence_path: Path | str | None = None):
        self.live_teacher_registry_path = live_teacher_registry_path or (
            Path(__file__).resolve().parents[1] / "teachers" / "teacher_registry_v2026_live.yaml"
        )
        self.persistence_path = Path(persistence_path) if persistence_path else None
        self._candidate_overrides: dict[str, dict[str, Any]] = {}
        self._audit_events: list[dict[str, Any]] = []
        self._live_teacher_payload = self._load_live_teacher_payload()
        self._load_persisted_registry()

    def validate(self) -> dict[str, Any]:
        locked_decisions = [decision for decision in self.locked_decisions() if decision.status == "locked"]
        unresolved = self.unresolved_decisions()
        candidates = self.research_candidates()
        experts = self.expert_roster()
        return {
            "ok": bool(locked_decisions and unresolved and candidates and len(experts) == 19),
            "locked_decision_count": len(locked_decisions),
            "unresolved_decision_count": len(unresolved),
            "research_candidate_count": len(candidates),
            "locked_expert_count": len([expert for expert in experts if expert.status == "locked"]),
        }

    def locked_decisions(self) -> list[CanonicalDecision]:
        return [
            self._decision(
                "brain-not-wrapper",
                "NexusNet remains a neural-core brain",
                "Tools, RAG, MCP, and GUI surfaces are mediated capabilities, not the cognition authority.",
                "locked",
                ["NEXUSNET_38_CHAT_IDEA_SYNTHESIS.md", "April 2026 product sweep plan"],
            ),
            self._decision(
                "repo-split",
                "Preserve repository split",
                "nexusnet/ is the neural brain/core; nexus/ is the platform API/runtime shell.",
                "locked",
                ["MEMORY.md repo split note", "nexus.api.app:create_app"],
            ),
            self._decision(
                "scaffold-first-training",
                "Training waits behind trace/security/provenance gates",
                "No real model training or promotion begins before canon, traces, evals, memory provenance, licenses, and security are stable.",
                "locked",
                ["April 2026 research refresh", "Phase 8 plan"],
            ),
            self._decision(
                "teacher-capability-provider",
                "Teacher models are replaceable capability providers",
                "Teacher models can guide, verify, and score, but do not become permanent cognition.",
                "locked",
                ["teacher_registry_v2026_live.yaml", "Phase 2 plan"],
            ),
            self._decision(
                "security-core-architecture",
                "Security and identity are core architecture",
                "External protocol tools require signed/allowlisted definitions, identity metadata, sandboxing, consent, and audit.",
                "locked",
                ["MCP security best practices", "Phase 5 plan"],
            ),
            self._decision(
                "memory-operating-system",
                "Memory planes sit under a Memory Operating System",
                "Memory has lifecycle operations, provenance, temporal truth, and dereferenceable evidence.",
                "locked",
                ["MemOS paper", "Graphiti/Zep research anchor", "Phase 4 plan"],
            ),
        ]

    def unresolved_decisions(self) -> list[CanonicalDecision]:
        return [
            self._decision(
                "ebt-weighting-formula",
                "Exact EBT scoring weights remain unresolved",
                "EBT is locked as a pluggable traceable scoring contract, but formula weights stay unresolved until evals prove them.",
                "unresolved",
                ["Phase 3 plan", "trace-first eval requirement"],
            ),
            self._decision(
                "effective-million-context-budget",
                "One-million-token target needs measured context assembly",
                "The target is effective context through memory, summaries, indexes, and cache reuse; raw model context is not locked.",
                "unresolved",
                ["Phase 7 plan", "runtime candidate registry"],
            ),
        ]

    def research_candidates(self) -> list[ResearchCandidate]:
        rows = [
            ("graphiti-zep", "Graphiti/Zep", "memory", "https://github.com/getzep/graphiti", "Apache-2.0", "candidate", "temporal graph memory", "Optional temporal graph memory adapter candidate."),
            ("memos", "MemOS", "memory", "https://arxiv.org/abs/2505.22101", "paper", "research_only", "memory operating system design", "Research-backed memory OS design candidate."),
            ("a-mem", "A-MEM", "memory", "https://arxiv.org/search/?query=A-MEM&searchtype=all", "paper", "research_only", "adaptive memory lifecycle", "Research-only memory lifecycle candidate."),
            ("agemem", "AgeMem", "memory", "https://arxiv.org/search/?query=AgeMem&searchtype=all", "paper", "research_only", "memory aging policy", "Research-only memory aging policy candidate."),
            ("memexrl", "MemexRL", "memory-evals", "https://arxiv.org/search/?query=MemexRL&searchtype=all", "paper", "research_only", "indexed evidence memory", "Research-only indexed-evidence/reward candidate."),
            ("mcp", "Model Context Protocol", "protocol", "https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices", "specification", "candidate", "tool protocol", "Governed tool protocol, disabled until security envelope passes."),
            ("mcp-elicitation", "MCP Elicitation", "protocol", "https://modelcontextprotocol.io/specification/draft/client/elicitation", "specification", "candidate", "elicitation UX", "Accept/decline/cancel supported; secrets require URL/out-of-band flow."),
            ("a2a", "Agent2Agent", "protocol", "https://a2a-protocol.org/latest/specification/", "specification", "candidate", "agent-to-agent protocol", "Optional agent work protocol behind identity/security gates."),
            ("ag-ui", "AG-UI", "protocol", "https://github.com/ag-ui-protocol/ag-ui", "MIT", "candidate", "user-facing agent events", "Optional user-facing agent event stream candidate."),
            ("trl-v1", "TRL v1", "training", "https://huggingface.co/docs/trl/index", "Apache-2.0", "candidate", "post-training default", "Default post-training candidate after eval/security/provenance gates."),
            ("verl", "verl", "training", "https://github.com/volcengine/verl", "Apache-2.0", "candidate", "large-scale RL training", "Candidate for larger RL/tool-agent training."),
            ("skyrl", "SkyRL", "training", "https://github.com/NovaSky-AI/SkyRL", "Apache-2.0", "candidate", "large-scale RL training", "Candidate for larger RL/tool-agent training."),
            ("fara", "Fara", "evals", "https://github.com/search?q=Fara+agent+evaluation&type=repositories", "license_review_required", "research_only", "agent eval candidate", "Research-only eval candidate until source is pinned."),
            ("osworld", "OSWorld", "evals", "https://github.com/xlang-ai/OSWorld", "MIT", "candidate", "computer-use eval", "Candidate eval suite for OS/browser-like agent tasks."),
            ("ui-tars", "UI-TARS", "multimodal-agent", "https://github.com/bytedance/UI-TARS", "Apache-2.0", "candidate", "computer-use model", "Candidate multimodal UI agent, not runnable by default."),
            ("qwen3-vl", "Qwen3-VL", "multimodal-model", "https://huggingface.co/Qwen", "license_review_required", "candidate", "vision capsule teacher", "Candidate multimodal teacher/provider for vision capsule."),
            ("lfm2-5", "LFM2.5", "model", "https://www.liquid.ai/", "license_review_required", "candidate", "efficiency coach", "Candidate bounded efficiency coach, not cognition authority."),
            ("vllm", "vLLM", "runtime", "https://github.com/vllm-project/vllm", "Apache-2.0", "candidate", "GPU serving", "Candidate serving adapter."),
            ("sglang", "SGLang", "runtime", "https://github.com/sgl-project/sglang", "Apache-2.0", "candidate", "GPU serving", "Candidate serving adapter."),
            ("lmcache", "LMCache", "runtime", "https://github.com/LMCache/LMCache", "Apache-2.0", "candidate", "KV/cache reuse", "Candidate KV/cache reuse adapter."),
            ("torchao", "torchao", "runtime-optimization", "https://github.com/pytorch/ao", "BSD-style", "candidate", "quantization", "Candidate quantization/optimization adapter."),
            ("deep-eval", "DeepEval", "evals", "https://github.com/confident-ai/deepeval", "Apache-2.0", "candidate", "trace-first evals", "Candidate trace-first eval library."),
            ("openai-agent-evals", "OpenAI Agent Evals", "evals", "https://developers.openai.com/api/docs/guides/agent-evals", "documentation", "candidate", "agent eval workflow", "Reference eval approach for trace-labeled scenarios."),
            ("openrlhf", "OpenRLHF", "training", "https://github.com/OpenRLHF/OpenRLHF", "Apache-2.0", "candidate_requires_pin", "RLHF training", "README contains future-dated entries relative to 2026-04-26; pin before use."),
        ]
        candidates = [
            ResearchCandidate(
                id=row[0],
                name=row[1],
                category=row[2],
                source_url=row[3],
                verified_at=self.verified_at,
                license=row[4],
                evidence_level="source-url-recorded",
                integration_status=row[5],
                replacement_target=row[6],
                notes=row[7],
            )
            for row in rows
        ]
        return [self._apply_candidate_override(candidate) for candidate in candidates]

    def research_candidate(self, candidate_id: str) -> ResearchCandidate | None:
        return next((candidate for candidate in self.research_candidates() if candidate.id == candidate_id), None)

    def update_research_candidate(
        self,
        *,
        candidate_id: str,
        integration_status: RegistryStatus | None = None,
        maturity: str | None = None,
        notes: str | None = None,
        evidence: str | None = None,
    ) -> dict[str, Any]:
        candidate = self.research_candidate(candidate_id)
        if candidate is None:
            raise KeyError(candidate_id)

        updates: dict[str, Any] = {}
        if integration_status is not None:
            updates["integration_status"] = integration_status
        if maturity is not None:
            updates["maturity"] = maturity
        if notes is not None:
            updates["notes"] = notes
        if evidence is not None:
            updates["evidence_level"] = evidence

        self._candidate_overrides[candidate_id] = {
            **self._candidate_overrides.get(candidate_id, {}),
            **updates,
        }
        updated = self._apply_candidate_override(candidate)
        audit_event = {
            "action": "assimilation.candidate.updated",
            "candidate_id": candidate_id,
            "integration_status": updated.integration_status,
            "maturity": updated.maturity,
            "evidence": evidence,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._audit_events.append(audit_event)
        self._persist_registry()
        return {"candidate": updated.model_dump(mode="json"), "audit_event": audit_event}

    def assimilation_audit_log(self) -> list[dict[str, Any]]:
        return list(self._audit_events)

    def expert_roster(self) -> list[ExpertCapsule]:
        pairs = (self._live_teacher_payload.get("live_expert_pairs") or {})
        experts: list[ExpertCapsule] = []
        for name, details in pairs.items():
            experts.append(
                ExpertCapsule(
                    capsule_id=str(details["subject"]),
                    name=name,
                    roster_position=int(details["roster_position"]),
                    status="locked",
                    evidence=["teacher_registry_v2026_live.yaml", "38-chat synthesis locked expert roster"],
                    license="internal_canon",
                    verified_at=self.verified_at,
                    capabilities=[str(details["subject"]), "brain-mediated-routing", "traceable-critique"],
                    permissions=["memory:read-scoped", "trace:write-diagnostic"],
                    eval_coverage=list(details.get("evaluation_family") or ["trace-first-scenario"]),
                    memory_access=["working", "episodic", "evidence-dereference"],
                    teacher_policy={
                        "primary_teacher_id": details.get("primary_teacher_id"),
                        "secondary_teacher_id": details.get("secondary_teacher_id"),
                        "critique_arbiter_subject": details.get("critique_arbiter_subject"),
                        "teacher_models_are_replaceable": True,
                    },
                )
            )
        return sorted(experts, key=lambda item: item.roster_position)

    def protocol_adapters(self) -> list[ProtocolAdapter]:
        return [
            ProtocolAdapter(adapter_id="mcp", protocol="mcp", enabled_by_default=False, security_envelope_required=True, status="candidate", evidence=["MCP security best practices"], license="specification", verified_at=self.verified_at),
            ProtocolAdapter(adapter_id="a2a", protocol="a2a", enabled_by_default=False, security_envelope_required=True, status="candidate", evidence=["A2A specification"], license="specification", verified_at=self.verified_at),
            ProtocolAdapter(adapter_id="ag-ui", protocol="ag-ui", enabled_by_default=False, security_envelope_required=True, status="candidate", evidence=["AG-UI repository"], license="MIT", verified_at=self.verified_at),
        ]

    def memory_operations(self) -> list[MemoryOperation]:
        return [
            MemoryOperation(operation_id=operation, status="locked", evidence=["Phase 4 Memory Operating System plan"], license="internal_canon", verified_at=self.verified_at, allowed_states=["active", "archived"], provenance_required=True)
            for operation in ["store", "retrieve", "update", "summarize", "archive", "discard", "dereference", "provenance_lookup"]
        ]

    def status_payload(self) -> dict[str, Any]:
        validation = self.validate()
        unresolved = [decision.model_dump(mode="json") for decision in self.unresolved_decisions()]
        experts = self.expert_roster()
        return {
            "status": "locked_with_candidates",
            "repo_split": {"brain_core": "nexusnet/", "platform_shell": "nexus/"},
            "validation": validation,
            "locked_decisions": [decision.model_dump(mode="json") for decision in self.locked_decisions()],
            "unresolved_decisions": unresolved,
            "expert_roster": {
                "locked_count": len([expert for expert in experts if expert.status == "locked"]),
                "items": [expert.model_dump(mode="json") for expert in experts],
            },
            "memory_policy": {
                "status": "locked",
                "controller": "MemoryOperatingSystem",
                "operations": [operation.operation_id for operation in self.memory_operations()],
                "provenance_required": True,
            },
            "protocol_security": {
                "status": "candidate",
                "external_tools_default": "deny_until_policy_allows",
                "adapters": [adapter.model_dump(mode="json") for adapter in self.protocol_adapters()],
            },
        }

    def product_status(self) -> dict[str, Any]:
        return {
            "canon": {"status": "locked_with_candidates", "unresolved_count": len(self.unresolved_decisions())},
            "research": {"candidate_count": len(self.research_candidates()), "openrlhf_status": "candidate_requires_pin"},
            "memory": {"status": "locked", "controller": "MemoryOperatingSystem", "temporal_truth": True},
            "security": {"status": "locked_policy_candidate_protocols", "external_tools_default": "deny_until_policy_allows"},
            "runtime": {"status": "candidate_profiles", "raw_million_token_context": "unresolved"},
            "training": {"real_training_status": "gated", "default_candidate": "trl-v1"},
            "docs": {"source_of_truth": "schema_and_canon_registry", "diagram_status": "generated_from_state_where_possible"},
        }

    def _decision(
        self,
        decision_id: str,
        title: str,
        decision: str,
        status: RegistryStatus,
        evidence: list[str],
    ) -> CanonicalDecision:
        return CanonicalDecision(
            id=decision_id,
            title=title,
            decision=decision,
            status=status,
            evidence=evidence,
            license="internal_canon",
            verified_at=self.verified_at,
        )

    def _load_live_teacher_payload(self) -> dict[str, Any]:
        if not self.live_teacher_registry_path.exists():
            return {}
        with self.live_teacher_registry_path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
        return payload if isinstance(payload, dict) else {}

    def _apply_candidate_override(self, candidate: ResearchCandidate) -> ResearchCandidate:
        overrides = self._candidate_overrides.get(candidate.id)
        if not overrides:
            return candidate
        return candidate.model_copy(update=overrides)

    def _load_persisted_registry(self) -> None:
        if self.persistence_path is None or not self.persistence_path.exists():
            return
        payload = json.loads(self.persistence_path.read_text(encoding="utf-8"))
        overrides = payload.get("candidate_overrides") or {}
        self._candidate_overrides = overrides if isinstance(overrides, dict) else {}
        audit_events = payload.get("audit_events") or []
        self._audit_events = audit_events if isinstance(audit_events, list) else []

    def _persist_registry(self) -> None:
        if self.persistence_path is None:
            return
        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "candidate_overrides": self._candidate_overrides,
            "audit_events": self._audit_events,
        }
        self.persistence_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
