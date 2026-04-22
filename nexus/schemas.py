from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class Message(BaseModel):
    role: str = "user"
    content: str


class TraceStep(BaseModel):
    name: str
    status: Literal["ok", "warning", "error"] = "ok"
    detail: dict[str, Any] = Field(default_factory=dict)


class OperatorRequest(BaseModel):
    session_id: str = Field(default_factory=lambda: new_id("session"))
    prompt: str | None = None
    messages: list[Message] = Field(default_factory=list)
    model_hint: str | None = None
    use_retrieval: bool = True
    retrieval_top_k: int = 5
    require_approval: bool = False
    success_conditions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    trace_id: str = Field(default_factory=lambda: new_id("trace"))
    created_at: datetime = Field(default_factory=utcnow)


class AgentDescriptor(BaseModel):
    name: str
    role: str
    description: str
    tags: list[str] = Field(default_factory=list)


class AgentResult(BaseModel):
    agent: str
    status: Literal["ok", "warning", "error"] = "ok"
    summary: str
    detail: dict[str, Any] = Field(default_factory=dict)


class AODescriptor(BaseModel):
    name: str
    description: str
    responsibilities: list[str] = Field(default_factory=list)


class CapabilityCard(BaseModel):
    model_id: str
    model_family: str
    runtime_name: str
    modalities: list[str] = Field(default_factory=lambda: ["text"])
    context_window: int = 4096
    prompt_dialect: str = "chat"
    supports_tools: bool = False
    supports_structured_output: bool = False
    quantization: list[str] = Field(default_factory=list)
    preferred_tasks: list[str] = Field(default_factory=list)
    known_weaknesses: list[str] = Field(default_factory=list)
    benchmark_history: list[dict[str, Any]] = Field(default_factory=list)


class ModelRegistration(BaseModel):
    model_id: str
    runtime_name: str
    display_name: str
    default_expert: str | None = None
    available: bool = True
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    capability_card: CapabilityCard
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class RuntimeProfile(BaseModel):
    runtime_name: str
    backend_type: str
    available: bool = True
    health: dict[str, Any] = Field(default_factory=dict)
    capabilities: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=utcnow)


class ToolManifest(BaseModel):
    tool_name: str
    permission_class: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = 30
    sandbox_policy: str = "restricted"
    healthcheck: dict[str, Any] = Field(default_factory=dict)


class ToolRequest(BaseModel):
    tool_name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    trace_id: str | None = None


class ToolResult(BaseModel):
    tool_name: str
    ok: bool
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    duration_ms: int = 0


class MemoryScore(BaseModel):
    relevance: float = 0.0
    freshness: float = 0.0
    importance: float = 0.0
    recurrence: float = 0.0
    success_history: float = 0.0


class MemoryRecord(BaseModel):
    memory_id: str = Field(default_factory=lambda: new_id("mem"))
    session_id: str
    plane: str
    role: str | None = None
    content: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    score: MemoryScore = Field(default_factory=MemoryScore)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class MemoryQuery(BaseModel):
    session_id: str
    plane: str | None = None
    limit: int = 50


class RetrievalRequest(BaseModel):
    query: str
    top_k: int = 5
    session_id: str | None = None
    include_sources: bool = True
    use_pgvector: bool = False


class RetrievalHit(BaseModel):
    chunk_id: str
    doc_id: str
    source: str
    content: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class CritiqueReport(BaseModel):
    critique_id: str = Field(default_factory=lambda: new_id("crit"))
    trace_id: str
    status: Literal["ok", "warning", "error"] = "ok"
    critic_score: float = 0.0
    groundedness: float = 0.0
    hallucination_risk: float = 0.0
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class ExecutionTrace(BaseModel):
    trace_id: str
    session_id: str
    request: OperatorRequest
    status: Literal["ok", "warning", "error"] = "ok"
    selected_ao: str
    selected_teacher_id: str | None = None
    selected_agent: str | None = None
    selected_expert: str | None = None
    model_id: str
    runtime_name: str
    wrapper_mode: str | None = None
    started_at: datetime = Field(default_factory=utcnow)
    completed_at: datetime | None = None
    steps: list[TraceStep] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    teacher_provenance: dict[str, Any] = Field(default_factory=dict)
    retrieval_policy: str | None = None
    runtime_selection: dict[str, Any] = Field(default_factory=dict)
    promotion_references: list[str] = Field(default_factory=list)
    retrieval_hits: list[RetrievalHit] = Field(default_factory=list)
    critique_id: str | None = None
    output_preview: str = ""


class OperatorResult(BaseModel):
    trace_id: str
    session_id: str
    status: Literal["ok", "warning", "error"] = "ok"
    output: str
    selected_ao: str
    selected_teacher_id: str | None = None
    selected_expert: str | None = None
    model_id: str
    runtime_name: str
    wrapper_mode: str | None = None
    citations: list[dict[str, Any]] = Field(default_factory=list)
    critique: CritiqueReport | None = None
    approval_required: bool = False
    trace: ExecutionTrace


class ExperimentRecord(BaseModel):
    experiment_id: str = Field(default_factory=lambda: new_id("exp"))
    kind: str
    name: str
    status: str = "shadow"
    lineage: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class PromotionDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: new_id("appr"))
    subject: str
    decision: Literal["approved", "rejected", "shadow"]
    approver: str
    rationale: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class RollbackRecord(BaseModel):
    rollback_id: str = Field(default_factory=lambda: new_id("rb"))
    subject: str
    status: Literal["prepared", "executed", "aborted"] = "prepared"
    target_version: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class RetrievalDocumentInput(BaseModel):
    source: str
    title: str | None = None
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalIngestRequest(BaseModel):
    documents: list[RetrievalDocumentInput]


class ApprovalRequest(BaseModel):
    subject: str
    decision: Literal["approved", "rejected", "shadow"]
    approver: str
    rationale: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    session_id: str = Field(default_factory=lambda: new_id("session"))
    messages: list[Message] = Field(default_factory=list)
    prompt: str | None = None
    message: str | None = None
    model_hint: str | None = None
    teacher_id: str | None = None
    wrapper_mode: str | None = None
    use_retrieval: bool = True
    rag: bool | None = None
    retrieval_top_k: int = 5
    require_approval: bool = False
    success_conditions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
