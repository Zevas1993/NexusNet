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
from nexusnet.core.compatibility_provenance import normalize_compatibility_provenance
from nexusnet.schemas import SessionContext
from nexusnet.runtime.evolutionary_inference import SLOProfile, WorkloadProfile


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
        model_runtime_planner: Any | None = None,
        nexusnet_core: Any | None = None,
        evolutionary_inference: Any | None = None,
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
        self.model_runtime_planner = model_runtime_planner
        self.nexusnet_core = nexusnet_core
        self.evolutionary_inference = evolutionary_inference

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

        compatibility_plan = (
            self.model_runtime_planner.plan(
                {
                    "model_id": selected_model.model_id,
                    "context_tokens": selected_model.capability_card.context_window,
                    "modality": (selected_model.capability_card.modalities or ["text"])[0],
                    "quantization": (selected_model.capability_card.quantization or [None])[0],
                }
            )
            if self.model_runtime_planner is not None
            else {}
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
        if compatibility_plan:
            steps.append(TraceStep(name="model_runtime_plan", detail=compatibility_plan))

        runtime_selection_payload = runtime_decision.model_dump(mode="json") if runtime_decision is not None else {}
        if compatibility_plan:
            runtime_selection_payload = {
                **runtime_selection_payload,
                "runtime_compatibility_plan_id": compatibility_plan.get("compatibility_plan_id"),
                "runtime_compatibility_plan": compatibility_plan,
                "compatibility_plan_id": compatibility_plan.get("compatibility_plan_id"),
                "compatibility_plan": compatibility_plan,
            }
        core_attach_provenance = self._core_attachment_provenance()
        if core_attach_provenance:
            runtime_selection_payload = {
                **runtime_selection_payload,
                "core_attachment_provenance": core_attach_provenance,
                "compatibility_plan_id": core_attach_provenance.get(
                    "compatibility_plan_id",
                    runtime_selection_payload.get("compatibility_plan_id"),
                ),
                "compatibility_status": core_attach_provenance.get("compatibility_status"),
                "attachment_mode": core_attach_provenance.get("attachment_mode"),
                "product_evidence": core_attach_provenance.get("product_evidence"),
                "compatibility_provenance": core_attach_provenance,
            }

        evolutionary_selection: dict[str, Any] | None = None
        if self.evolutionary_inference is not None:
            input_tokens = sum(max(1, len(message.content.split())) for message in messages)
            objective = str(request.metadata.get("inference_objective", "balanced"))
            if objective not in {"latency", "throughput", "memory", "balanced"}:
                objective = "balanced"
            workload_profile = WorkloadProfile(
                prompt_tokens=input_tokens,
                max_new_tokens=max(1, int(request.metadata.get("max_new_tokens", 256))),
                batch_size=max(1, int(request.metadata.get("batch_size", 1))),
                concurrent_requests=max(1, int(request.metadata.get("concurrent_requests", 1))),
            )
            selected_execution_plan = self.evolutionary_inference.select_plan(
                workload_profile,
                SLOProfile(
                    objective=objective,
                    max_latency_ms=request.metadata.get("max_inference_latency_ms"),
                    max_peak_ram_bytes=request.metadata.get("max_peak_ram_bytes"),
                    max_peak_vram_bytes=request.metadata.get("max_peak_vram_bytes"),
                ),
            )
            evolution_status = self.evolutionary_inference.status()
            plan_verified = selected_execution_plan.plan_id in evolution_status.get("verified_plan_ids", [])
            raw_required_controls = request.metadata.get("required_runtime_controls", [])
            required_controls = (
                sorted({str(control) for control in raw_required_controls if str(control)})
                if isinstance(raw_required_controls, (list, tuple, set))
                else []
            )
            execution_fit_receipts: dict[str, dict[str, Any]] = {}
            if plan_verified and evolution_status.get("model_fingerprint_id"):
                for capability_profile in self.runtime_registry.runtime_capability_profiles():
                    fit_receipt = self.evolutionary_inference.fit_plan(
                        selected_execution_plan,
                        workload_profile,
                        capability_profile,
                        required_controls=required_controls,
                    )
                    execution_fit_receipts[capability_profile.runtime_name] = fit_receipt.model_dump(
                        mode="json"
                    )
            selected_fit_receipt = execution_fit_receipts.get(selected_runtime_name)
            if selected_fit_receipt is None:
                selected_fit_receipt = execution_fit_receipts.get(runtime.runtime_name)
            evolutionary_selection = {
                "plan_id": selected_execution_plan.plan_id,
                "primitive_ids": selected_execution_plan.primitive_ids,
                "parameters": selected_execution_plan.parameters,
                "fallback_plan_id": selected_execution_plan.fallback_plan_id,
                "model_fingerprint_id": evolution_status.get("model_fingerprint_id"),
                "verified": plan_verified,
                "fit_required": bool(execution_fit_receipts),
                "execution_fit_receipt": selected_fit_receipt,
                "execution_fit_receipts": execution_fit_receipts,
                "required_controls": required_controls,
                "quality_semantics": selected_execution_plan.quality_semantics,
                "raw_content_included": False,
            }
            runtime_selection_payload = {
                **runtime_selection_payload,
                "evolutionary_inference": evolutionary_selection,
            }
            steps.append(TraceStep(name="evolutionary_inference_plan", detail=evolutionary_selection))

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
                    "evolutionary_inference": evolutionary_selection,
                },
            ),
            prompt=raw_text,
            messages=messages,
            model_hint=selected_model.model_id,
            success_conditions=request.success_conditions,
            runtime_override=selected_runtime_name,
            fallback_chain=runtime_decision.fallback_runtime_names if runtime_decision is not None else [],
            runtime_selection=runtime_selection_payload,
        )
        output = brain_result.output
        runtime = self.runtime_registry.get_adapter(brain_result.runtime_name)
        runtime_control_receipt = runtime.control_binding_status()
        served_evolutionary_selection = dict(
            (brain_result.runtime_selection or {}).get("evolutionary_inference") or {}
        )
        served_fit_receipts = served_evolutionary_selection.get("execution_fit_receipts") or {}
        if isinstance(served_fit_receipts, dict) and runtime.runtime_name in served_fit_receipts:
            served_evolutionary_selection["execution_fit_receipt"] = served_fit_receipts[
                runtime.runtime_name
            ]
        runtime_selection_payload = {
            **brain_result.runtime_selection,
            "evolutionary_inference": served_evolutionary_selection,
        }
        if runtime_control_receipt is not None:
            runtime_selection_payload["runtime_control_receipt"] = runtime_control_receipt.model_dump(
                mode="json"
            )
            steps.append(
                TraceStep(
                    name="evolutionary_inference_execution",
                    status="warning" if runtime_control_receipt.decision == "degraded" else "ok",
                    detail={
                        "runtime_name": runtime_control_receipt.runtime_name,
                        "plan_id": runtime_control_receipt.plan_id,
                        "binding_id": runtime_control_receipt.binding_id,
                        "decision": runtime_control_receipt.decision,
                        "reason_codes": runtime_control_receipt.reason_codes,
                        "raw_content_included": False,
                    },
                )
            )
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
                    "compatibility_provenance": normalize_compatibility_provenance(runtime_selection_payload),
                    "runtime_selection": runtime_selection_payload,
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

        ao_execution_receipt = None
        if ao_plan is not None and self.brain_aos is not None and hasattr(self.brain_aos, "record_execution"):
            ao_execution_receipt = self.brain_aos.record_execution(
                session_id=request.session_id,
                trace_id=operator_request.trace_id,
                plan=ao_plan,
                selected_expert=expert,
                selected_teacher_id=selected_teacher_id,
                wrapper_mode=wrapper_mode,
            )
            steps.append(
                TraceStep(
                    name="ao_execution_receipt",
                    detail={
                        "execution_id": ao_execution_receipt.get("execution_id"),
                        "ao_name": ao_execution_receipt.get("ao_name"),
                        "trace_ref": ao_execution_receipt.get("trace_ref"),
                        "input_contract": ao_execution_receipt.get("input_contract"),
                        "raw_content_included": False,
                    },
                )
            )

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
            runtime_selection=runtime_selection_payload,
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
            runtime_selection=runtime_selection_payload,
        )

    def _core_attachment_provenance(self) -> dict[str, Any]:
        if self.nexusnet_core is None or not hasattr(self.nexusnet_core, "attachment_provenance"):
            return {}
        try:
            return normalize_compatibility_provenance(self.nexusnet_core.attachment_provenance())
        except Exception:
            return {}

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
