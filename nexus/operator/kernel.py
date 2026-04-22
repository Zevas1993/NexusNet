from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..agents import AgentRegistry
from ..ao import AORegistry
from ..critique import CritiqueEngine
from ..experiments import ExperimentService
from ..governance import GovernanceService
from ..memory import MemoryService
from ..models import ModelRegistry
from ..retrieval import RetrievalService
from ..runtimes import RuntimeRegistry
from ..schemas import (
    ChatRequest,
    ExecutionTrace,
    Message,
    OperatorRequest,
    OperatorResult,
    RetrievalRequest,
    TraceStep,
)
from ..storage import NexusStore
from .routing import ExpertSelector
from nexusnet.core import NexusBrain
from nexusnet.schemas import SessionContext


def _now() -> datetime:
    return datetime.now(timezone.utc)


class OperatorKernel:
    def __init__(
        self,
        *,
        store: NexusStore,
        ao_registry: AORegistry,
        agent_registry: AgentRegistry,
        model_registry: ModelRegistry,
        runtime_registry: RuntimeRegistry,
        memory: MemoryService,
        retrieval: RetrievalService,
        critique: CritiqueEngine,
        governance: GovernanceService,
        experiments: ExperimentService,
        expert_selector: ExpertSelector,
        brain: NexusBrain,
        teacher_registry: Any | None = None,
        brain_aos: Any | None = None,
        brain_agent_registry: Any | None = None,
        brain_runtime_registry: Any | None = None,
        brain_gateway: Any | None = None,
        brain_promotions: Any | None = None,
    ):
        self.store = store
        self.ao_registry = ao_registry
        self.agent_registry = agent_registry
        self.model_registry = model_registry
        self.runtime_registry = runtime_registry
        self.memory = memory
        self.retrieval = retrieval
        self.critique = critique
        self.governance = governance
        self.experiments = experiments
        self.expert_selector = expert_selector
        self.brain = brain
        self.teacher_registry = teacher_registry
        self.brain_aos = brain_aos
        self.brain_agent_registry = brain_agent_registry
        self.brain_runtime_registry = brain_runtime_registry
        self.brain_gateway = brain_gateway
        self.brain_promotions = brain_promotions

    def execute_chat(self, request: ChatRequest) -> OperatorResult:
        operator_request = OperatorRequest(
            session_id=request.session_id,
            prompt=request.prompt or request.message,
            messages=request.messages,
            model_hint=request.model_hint,
            use_retrieval=request.use_retrieval if request.rag is None else request.rag,
            retrieval_top_k=request.retrieval_top_k,
            require_approval=request.require_approval,
            success_conditions=request.success_conditions,
            metadata={
                **request.metadata,
                "teacher_id": request.teacher_id,
                "wrapper_mode": request.wrapper_mode,
            },
        )

        initial_prompt = request.prompt or request.message
        messages = request.messages or ([Message(role="user", content=initial_prompt)] if initial_prompt else [])
        raw_text = initial_prompt or (messages[-1].content if messages else "")
        use_retrieval = request.use_retrieval if request.rag is None else request.rag
        wrapper_mode = request.wrapper_mode or request.metadata.get("wrapper_mode") or "standard-chat"
        expert = self.expert_selector.select(raw_text, use_retrieval=use_retrieval)
        if self.brain_aos is not None:
            ao_plan = self.brain_aos.select_request(operator_request, expert=expert, wrapper_mode=wrapper_mode)
            selected_ao = ao_plan.ao_name
        else:
            ao_descriptor = self.ao_registry.select(operator_request)
            selected_ao = ao_descriptor.name
            ao_plan = None

        selected_teacher_id = None
        teacher_provenance: dict[str, Any] = {}
        gateway_resolution: dict[str, Any] | None = None
        if self.teacher_registry is not None:
            attached_teacher, arbitration = self.teacher_registry.resolve_for_task(
                brain=self.brain,
                task_type="chat",
                expert=expert,
                requested_teacher_id=request.teacher_id,
                model_hint=request.model_hint,
                routing_metadata=request.metadata,
            )
            selected_teacher_id = attached_teacher.teacher_id
            teacher_provenance = {
                **attached_teacher.provenance,
                "arbitration": arbitration.model_dump(mode="json"),
            }
            selected_model = self.model_registry.resolve_model(attached_teacher.model_id)
        else:
            selected_model = self.model_registry.resolve_model(request.model_hint, expert)
        steps = [TraceStep(name="classify_request", detail={"ao": selected_ao, "expert": expert, "wrapper_mode": wrapper_mode})]
        if ao_plan is not None:
            steps.append(TraceStep(name="ao_plan", detail=ao_plan.model_dump(mode="json")))
        if self.brain_gateway is not None and self.brain_agent_registry is not None:
            requested_tools = list(request.metadata.get("requested_tools", []))
            gateway_agent = self.brain_agent_registry.select_for_mode(wrapper_mode)
            gateway_resolution = self.brain_gateway.resolve(
                agent_id=gateway_agent.agent_id,
                workspace_id=str(request.metadata.get("workspace_id", "default")),
                requested_tools=requested_tools,
                require_user_approval=request.require_approval,
            )
            if requested_tools or wrapper_mode in {"openclaw", "hermes-agent"}:
                steps.append(TraceStep(name="gateway_resolution", detail=gateway_resolution))
        if teacher_provenance:
            steps.append(
                TraceStep(
                    name="select_teacher",
                    detail={
                        "teacher_id": selected_teacher_id,
                        "model_id": selected_model.model_id,
                        "status_label": teacher_provenance.get("status_label"),
                        "lineage": teacher_provenance.get("lineage"),
                    },
                )
            )

        runtime_decision = self.brain_runtime_registry.selector.select(selected_model.model_id) if self.brain_runtime_registry else None
        selected_runtime_name = runtime_decision.selected_runtime_name if runtime_decision is not None else selected_model.runtime_name
        if selected_runtime_name in self.runtime_registry.adapters:
            runtime = self.runtime_registry.get_adapter(selected_runtime_name)
            runtime_profile = runtime.profile()
        else:
            runtime = self.runtime_registry.choose(selected_model.runtime_name)
            runtime_profile = runtime.profile().model_copy(update={"available": False})
        steps.append(
            TraceStep(
                name="select_runtime",
                detail={
                    "runtime": selected_runtime_name,
                    "available": runtime_profile.available,
                    "fallback_chain": runtime_decision.fallback_runtime_names if runtime_decision is not None else [],
                },
            )
        )
        if runtime_decision is not None:
            steps.append(TraceStep(name="brain_runtime_decision", detail=runtime_decision.model_dump(mode="json")))

        brain_result = self.brain.generate(
            session_context=SessionContext(
                session_id=request.session_id,
                trace_id=operator_request.trace_id,
                ao=selected_ao,
                expert=expert,
                task_type="chat",
                use_retrieval=use_retrieval,
                memory_budget=6,
                metadata={
                    "use_pgvector": bool(request.metadata.get("use_pgvector")),
                    "retrieval_top_k": request.retrieval_top_k,
                    "retrieval_policy": request.metadata.get("retrieval_policy", "lexical+graph-merged"),
                    "graph_plane_tags": request.metadata.get("graph_plane_tags"),
                    "teacher_id": selected_teacher_id,
                    "teacher_registry_layer": (teacher_provenance.get("arbitration", {}) or {}).get("registry_layer"),
                    "teacher_lineage": teacher_provenance.get("lineage"),
                    **request.metadata,
                },
            ),
            prompt=raw_text,
            messages=messages,
            model_hint=selected_model.model_id,
            success_conditions=request.success_conditions,
            runtime_override=selected_runtime_name,
            fallback_chain=runtime_decision.fallback_runtime_names if runtime_decision is not None else [],
            runtime_selection=runtime_decision.model_dump(mode="json") if runtime_decision is not None else None,
        )
        output = brain_result.output
        runtime = self.runtime_registry.get_adapter(brain_result.runtime_name)
        selected_model = self.model_registry.resolve_model(brain_result.model_id)
        critique = brain_result.critique or self.critique.assess(
            trace_id=operator_request.trace_id,
            request=operator_request,
            output=output,
            runtime_name=runtime.runtime_name,
            retrieval_hits=brain_result.retrieval_hits,
        )
        retrieval_hits = brain_result.retrieval_hits
        status = "warning" if critique.status == "warning" else "ok"
        if brain_result.inference_trace.compression:
            steps.append(
                TraceStep(
                    name="compress_context",
                    detail=brain_result.inference_trace.compression.model_dump(mode="json"),
                )
            )
        if retrieval_hits:
            steps.append(
                TraceStep(
                    name="retrieve_context",
                    detail={
                        "hits": len(retrieval_hits),
                        "policy": brain_result.retrieval_policy_decision.get("policy_mode"),
                        "effective_policy": brain_result.retrieval_policy_decision.get("effective_policy_mode"),
                        "graph_contribution_count": brain_result.retrieval_policy_decision.get("graph_contribution_count", 0),
                        "memory_contribution_count": brain_result.retrieval_policy_decision.get("memory_contribution_count", 0),
                        "temporal_contribution_count": brain_result.retrieval_policy_decision.get("temporal_contribution_count", 0),
                        "plane_tags": brain_result.retrieval_policy_decision.get("plane_tags", []),
                        "candidate_source_counts": brain_result.retrieval_policy_decision.get("candidate_source_counts", {}),
                    },
                )
            )
        reranker = brain_result.retrieval_policy_decision.get("reranker") or {}
        if reranker.get("applied"):
            steps.append(
                TraceStep(
                    name="rerank_retrieval",
                    detail={
                        "provider": reranker.get("provider"),
                        "top_k_before_rerank": brain_result.retrieval_policy_decision.get("top_k_before_rerank", 0),
                        "top_k_after_rerank": brain_result.retrieval_policy_decision.get("top_k_after_rerank", 0),
                        "latency_delta_ms": reranker.get("latency_delta_ms", 0),
                        "relevance_delta": reranker.get("relevance_delta", 0.0),
                        "groundedness_delta": reranker.get("groundedness_delta", 0.0),
                        "provenance_delta": reranker.get("provenance_delta", 0.0),
                        "candidate_list_before_rerank": brain_result.retrieval_policy_decision.get("candidate_list_before_rerank", []),
                        "candidate_list_after_rerank": brain_result.retrieval_policy_decision.get("candidate_list_after_rerank", []),
                    },
                )
            )
        core_execution = brain_result.inference_trace.metrics.get("core_execution", {})
        core_policy = core_execution.get("execution_policy") or {}
        if core_policy:
            steps.append(
                TraceStep(
                    name="brain_execution_policy",
                    detail={
                        "policy_id": core_policy.get("policy_id"),
                        "execution_mode": core_policy.get("execution_mode"),
                        "selected_internal_experts": core_policy.get("selected_internal_experts", []),
                        "decision_reasons": core_policy.get("decision_reasons", []),
                    },
                )
            )
        native_execution = core_execution.get("native_execution") or {}
        if native_execution:
            steps.append(
                TraceStep(
                    name="internal_expert_runtime",
                    detail={
                        "execution_id": native_execution.get("execution_id"),
                        "enabled": native_execution.get("enabled"),
                        "output_count": native_execution.get("output_count", 0),
                        "disagreement_count": native_execution.get("disagreement_count", 0),
                        "teacher_fallback_path": native_execution.get("teacher_fallback_path"),
                    },
                )
            )
        steps.append(
            TraceStep(
                name="generate_output",
                detail={
                    "runtime": runtime.runtime_name,
                    "output_chars": len(output),
                    "adapter_id": brain_result.adapter_id,
                    "memory_records_written": brain_result.inference_trace.memory_records_written,
                    "fallback_used": brain_result.inference_trace.metrics.get("fallback_used", False),
                },
            )
        )
        steps.append(TraceStep(name="critique", status=critique.status, detail={"issues": critique.issues}))

        brain_agent_record = None
        if self.brain_agent_registry is not None:
            brain_agent_record = self.brain_agent_registry.record_execution(
                session_id=request.session_id,
                trace_id=operator_request.trace_id,
                wrapper_mode=wrapper_mode,
                selected_ao=selected_ao,
                selected_runtime=runtime.runtime_name,
                selected_backend=runtime.runtime_name,
                metadata={
                    "selected_teacher_id": selected_teacher_id,
                    "selected_expert": expert,
                    "teacher_provenance": teacher_provenance,
                    "gateway_resolution": gateway_resolution,
                },
            )
            steps.append(TraceStep(name="select_agent_surface", detail=brain_agent_record.model_dump(mode="json")))

        if self.brain_promotions is not None and brain_result.retrieval_policy_decision.get("policy_mode") not in {None, "lexical-baseline"}:
            self.brain_promotions.create_candidate(
                candidate_kind="retrieval-policy",
                subject_id=f"retrieval-policy::{brain_result.retrieval_policy_decision['policy_mode']}",
                baseline_reference="retrieval-policy::lexical-baseline",
                challenger_reference=brain_result.retrieval_policy_decision["policy_mode"],
                lineage="blended-derived" if brain_result.retrieval_policy_decision.get("graph_contribution_count", 0) else "live-derived",
                traceability={
                    "trace_id": operator_request.trace_id,
                    "session_id": request.session_id,
                    "policy_mode": brain_result.retrieval_policy_decision.get("policy_mode"),
                    "effective_policy_mode": brain_result.retrieval_policy_decision.get("effective_policy_mode"),
                    "graph_contribution_count": brain_result.retrieval_policy_decision.get("graph_contribution_count", 0),
                    "graph_store_health": brain_result.retrieval_policy_decision.get("graph_store_health", {}),
                    "plane_tags": brain_result.retrieval_policy_decision.get("plane_tags", []),
                    "candidate_source_counts": brain_result.retrieval_policy_decision.get("candidate_source_counts", {}),
                    "top_k_before_rerank": brain_result.retrieval_policy_decision.get("top_k_before_rerank", 0),
                    "top_k_after_rerank": brain_result.retrieval_policy_decision.get("top_k_after_rerank", 0),
                    "candidate_list_before_rerank": brain_result.retrieval_policy_decision.get("candidate_list_before_rerank", []),
                    "candidate_list_after_rerank": brain_result.retrieval_policy_decision.get("candidate_list_after_rerank", []),
                    "reranker": brain_result.retrieval_policy_decision.get("reranker", {}),
                },
            )

        safety_agent = self.agent_registry.get("SafetyAuditorAgent")
        safety_result = safety_agent.run(output=output) if safety_agent else None
        if safety_result and safety_result.detail.get("issues"):
            steps.append(TraceStep(name="safety_audit", status=safety_result.status, detail=safety_result.detail))

        trace = ExecutionTrace(
            trace_id=operator_request.trace_id,
            session_id=request.session_id,
            request=operator_request,
            status="warning" if critique.status == "warning" or status == "warning" else status,
            selected_ao=selected_ao,
            selected_teacher_id=selected_teacher_id,
            selected_agent=brain_agent_record.agent_id if brain_agent_record else ("RetrievalRankerAgent" if retrieval_hits else "ModelProfilerAgent"),
            selected_expert=expert,
            model_id=selected_model.model_id,
            runtime_name=runtime.runtime_name,
            wrapper_mode=wrapper_mode,
            started_at=operator_request.created_at,
            completed_at=_now(),
            steps=steps,
            metrics={
                "retrieval_hits": len(retrieval_hits),
                "brain_trace_id": brain_result.inference_trace.trace_id,
                "brain_latency_ms": brain_result.inference_trace.latency_ms,
                "brain_memory_records_written": brain_result.inference_trace.memory_records_written,
                "core_execution": brain_result.inference_trace.metrics.get("core_execution", {}),
                "graph_contribution_count": brain_result.retrieval_policy_decision.get("graph_contribution_count", 0),
                "memory_contribution_count": brain_result.retrieval_policy_decision.get("memory_contribution_count", 0),
                "temporal_contribution_count": brain_result.retrieval_policy_decision.get("temporal_contribution_count", 0),
                "fallback_used": brain_result.inference_trace.metrics.get("fallback_used", False),
                "rerank_provider": reranker.get("provider"),
                "top_k_before_rerank": brain_result.retrieval_policy_decision.get("top_k_before_rerank", 0),
                "top_k_after_rerank": brain_result.retrieval_policy_decision.get("top_k_after_rerank", 0),
                "rerank_latency_delta_ms": reranker.get("latency_delta_ms", 0),
                "rerank_relevance_delta": reranker.get("relevance_delta", 0.0),
                "rerank_groundedness_delta": reranker.get("groundedness_delta", 0.0),
                "rerank_provenance_delta": reranker.get("provenance_delta", 0.0),
                "gateway_decision": (gateway_resolution or {}).get("policy", {}).get("decision"),
            },
            teacher_provenance=teacher_provenance,
            retrieval_policy=brain_result.retrieval_policy_decision.get("policy_mode"),
            runtime_selection=brain_result.runtime_selection,
            promotion_references=brain_result.promotion_references,
            retrieval_hits=retrieval_hits,
            critique_id=critique.critique_id,
            output_preview=output[:240],
        )
        self.store.save_trace(trace.trace_id, trace.session_id, trace.status, trace.model_dump(mode="json"), operator_request.created_at.isoformat())

        approval_required = self.governance.approval_required(selected_model.model_id, request.require_approval)
        self.governance.record_event(
            "chat.executed",
            {
                "trace_id": trace.trace_id,
                "session_id": request.session_id,
                "runtime": runtime.runtime_name,
                "model_id": selected_model.model_id,
                "expert": expert,
                "teacher_id": selected_teacher_id,
                "wrapper_mode": wrapper_mode,
                "approval_required": approval_required,
            },
        )

        citations = [
            {"doc_id": hit.doc_id, "chunk_id": hit.chunk_id, "source": hit.source, "score": hit.score}
            for hit in retrieval_hits
        ]
        return OperatorResult(
            trace_id=trace.trace_id,
            session_id=request.session_id,
            status=trace.status,
            output=output,
            selected_ao=selected_ao,
            selected_teacher_id=selected_teacher_id,
            selected_expert=expert,
            model_id=selected_model.model_id,
            runtime_name=runtime.runtime_name,
            wrapper_mode=wrapper_mode,
            citations=citations,
            critique=critique,
            approval_required=approval_required,
            trace=trace,
        )

    def _assemble_prompt(self, prompt: str, expert: str, recent_memory: list[Message], retrieval_hits: list) -> str:
        parts = [f"Expert capsule: {expert}"]
        if recent_memory:
            parts.append("Recent memory:")
            for message in recent_memory[-6:]:
                parts.append(f"- {message.role}: {message.content[:180]}")
        if retrieval_hits:
            parts.append("Retrieved context:")
            for hit in retrieval_hits[:5]:
                parts.append(f"- ({hit.source}) {hit.content[:220]}")
        parts.append(f"User request: {prompt}")
        return "\n".join(parts)
