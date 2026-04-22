from __future__ import annotations

import platform
import time
from datetime import datetime, timezone
from typing import Any

from nexus.config import NexusPaths
from nexus.critique import CritiqueEngine
from nexus.memory import MemoryService
from nexus.models import ModelRegistry
from nexus.retrieval import RetrievalService
from nexus.runtimes import RuntimeRegistry
from nexus.schemas import Message, OperatorRequest, RetrievalRequest
from nexus.storage import NexusStore

from ..adapters import BaseModelAdapter
from ..benchmarks import BenchmarkHarness
from ..experts import InternalExpertExecutionService
from ..memory import MemoryNode, NeuralMemoryCortex
from ..moe import MoEFusionScaffoldService
from ..schemas import BrainGenerateResult, BrainGenerateRequest, InferenceTrace, SessionContext
from ..telemetry import BrainTelemetryLogger
from .execution_policy import CoreExecutionPolicyEngine
from .execution_trace import CoreExecutionTraceRecorder, build_lineage_tags, persist_core_execution_artifact
from .model_ingestion import ModelIngestionService
from .native_execution import NativeExecutionPlanner


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class NexusBrain:
    def __init__(
        self,
        *,
        paths: NexusPaths,
        store: NexusStore,
        runtime_registry: RuntimeRegistry,
        model_registry: ModelRegistry,
        memory: MemoryService,
        retrieval: RetrievalService,
        critique: CritiqueEngine,
        brain_runtime_registry: Any | None = None,
        teacher_registry: Any | None = None,
        memory_node: MemoryNode | None = None,
        moe_fusion: MoEFusionScaffoldService | None = None,
        evidence_bridge: Any | None = None,
        execution_policy_engine: CoreExecutionPolicyEngine | None = None,
        native_execution_planner: NativeExecutionPlanner | None = None,
        internal_expert_execution: InternalExpertExecutionService | None = None,
    ):
        self.paths = paths
        self.store = store
        self.runtime_registry = runtime_registry
        self.model_registry = model_registry
        self.memory = NeuralMemoryCortex(memory, store)
        self.retrieval = retrieval
        self.critique = critique
        self.brain_runtime_registry = brain_runtime_registry
        self.teacher_registry = teacher_registry
        self.memory_node = memory_node
        self.moe_fusion = moe_fusion or MoEFusionScaffoldService()
        self.evidence_bridge = evidence_bridge
        self.execution_policy_engine = execution_policy_engine or CoreExecutionPolicyEngine()
        self.native_execution_planner = native_execution_planner or NativeExecutionPlanner()
        self.internal_expert_execution = internal_expert_execution or InternalExpertExecutionService()
        self.telemetry = BrainTelemetryLogger(paths)
        self.adapters: dict[str, BaseModelAdapter] = {}
        self.attachment_records: dict[str, dict] = {}
        self.benchmarks = BenchmarkHarness(telemetry=self.telemetry, memory=self.memory, artifact_writer=self.store.write_artifact)
        self.model_ingestion = ModelIngestionService(
            model_registry=model_registry,
            runtime_registry=runtime_registry,
            telemetry=self.telemetry,
            adapter_cache=self.adapters,
            attachment_cache=self.attachment_records,
        )
        self.lifecycle_trace = CoreExecutionTraceRecorder(trace_name="nexusnet-brain")
        self._wake_state: dict | None = None

    def wake(self) -> dict:
        profiles = [profile.model_dump(mode="json") for profile in self.runtime_registry.list_profiles()]
        hardware_profile = (
            self.brain_runtime_registry.system_profiler.device_profile().model_dump(mode="json")
            if self.brain_runtime_registry is not None
            else {}
        )
        memory_node_summary = self.memory_node.summary() if self.memory_node is not None else {}
        payload = {
            "event": "nexusnet.wake",
            "brain_first": True,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "runtime_count": len(profiles),
            "available_runtimes": [profile["runtime_name"] for profile in profiles if profile.get("available")],
            "hardware_profile": hardware_profile,
            "memory_plane_count": memory_node_summary.get("plane_count", 0),
        }
        log_path = self.telemetry.log_startup(payload)
        payload["log_path"] = log_path
        self._wake_state = payload
        self.lifecycle_trace.record("brain-start", payload)
        return payload

    def bootstrap_from_registry(self) -> list[str]:
        attached = []
        for registration in self.model_registry.list_models():
            if not registration.available:
                continue
            self.attach_base_model(registration.model_id, role="teacher")
            attached.append(registration.model_id)
        return attached

    def attach_base_model(self, model_hint: str | None = None, *, role: str = "teacher", runtime_override: str | None = None) -> BaseModelAdapter:
        adapter, _ = self._attach_base_model(
            model_hint=model_hint,
            role=role,
            runtime_override=runtime_override,
        )
        return adapter

    def list_attached_models(self) -> list[str]:
        return sorted({adapter.model_id for adapter in self.adapters.values()})

    def core_summary(
        self,
        *,
        model_hint: str | None = None,
        expert: str | None = None,
        session_id: str | None = None,
        trace_id: str | None = None,
    ) -> dict:
        if self._wake_state is None:
            self.wake()
        latest_core_execution = self._latest_core_execution(session_id=session_id, trace_id=trace_id)
        execution_plan = (
            self.brain_runtime_registry.core_execution_plan(model_hint=model_hint, requested_runtime=None)
            if self.brain_runtime_registry is not None
            else {}
        )
        memory_context = self.memory_node.execution_context(task_type="summary", requested_plane_tags=None) if self.memory_node is not None else {}
        fusion_scaffold = self.moe_fusion.execution_plan(
            selected_expert=expert,
            memory_node_context=memory_context,
            hardware_profile=execution_plan.get("hardware_profile", {}),
        )
        execution_context = self._execution_context(
            trace_id=trace_id or f"core-summary::{session_id or expert or model_hint or 'default'}",
            session_id=session_id or "summary",
            task_type="summary",
            selected_expert=expert,
            requested_model_id=model_hint or "mock/default",
            teacher_id=None,
            teacher_registry_layer=None,
            runtime_execution_plan=execution_plan,
            memory_node_context=memory_context,
            fusion_scaffold=fusion_scaffold,
        )
        native_execution_preview = self.internal_expert_execution.preview(
            native_execution_plan=execution_context["native_execution_plan"],
            selected_expert=expert,
        )
        promotion_linkage_preview = self.native_execution_planner.promotion_linkage(
            selected_expert=expert,
            execution_policy=execution_context["execution_policy"],
            native_execution_plan=execution_context["native_execution_plan"],
            native_execution_result=native_execution_preview,
            evidence_feeds=execution_context["evidence_feeds"],
        )
        return {
            "status_label": "IMPLEMENTATION BRANCH",
            "brain_first_execution": True,
            "canonical_attach_seam": "nexusnet.core.attach_base_model.attach_base_model",
            "startup": self._wake_state,
            "attached_models": self.list_attached_models(),
            "attachment_records": self.model_ingestion.attachments(),
            "memory_node": self.memory_node.summary() if self.memory_node is not None else {},
            "runtime_execution_plan": execution_plan,
            "fusion_scaffold": fusion_scaffold,
            "evidence_feeds": execution_context["evidence_feeds"],
            "execution_policy": execution_context["execution_policy"],
            "native_execution_preview": native_execution_preview,
            "promotion_linkage_preview": promotion_linkage_preview,
            "lifecycle_trace": self.lifecycle_trace.snapshot(),
            "traceability": {
                "trace_detail_template": "/ops/traces/{trace_id}",
                "core_summary_ref": "/ops/brain/core",
                "latest_trace_id": latest_core_execution.get("trace_id"),
                "latest_artifact_id": latest_core_execution.get("artifact_id"),
                "latest_artifact_path": latest_core_execution.get("artifact_path"),
            },
            "wrapper_to_native_growth_visible": True,
            "graph_intelligence_visible": True,
        }

    def generate(
        self,
        *,
        session_context: SessionContext,
        prompt: str | None = None,
        messages: list[Message] | None = None,
        model_hint: str | None = None,
        success_conditions: list[str] | None = None,
        runtime_override: str | None = None,
        fallback_chain: list[str] | None = None,
        runtime_selection: dict | None = None,
    ) -> BrainGenerateResult:
        if self._wake_state is None:
            self.wake()
        request = BrainGenerateRequest(
            session_context=session_context,
            prompt=prompt,
            messages=messages or [],
            model_hint=model_hint,
            success_conditions=success_conditions or [],
        )
        registration = self.model_registry.resolve_model(request.model_hint or model_hint or "mock/default")
        execution_recorder = CoreExecutionTraceRecorder(trace_name=session_context.trace_id)
        execution_recorder.record(
            "brain-execution-start",
            {
                "trace_id": session_context.trace_id,
                "session_id": session_context.session_id,
                "task_type": session_context.task_type,
                "requested_model_hint": request.model_hint or model_hint,
            },
        )
        core_execution_plan = (
            self.brain_runtime_registry.core_execution_plan(
                model_hint=registration.model_id,
                requested_runtime=runtime_override,
            )
            if self.brain_runtime_registry is not None
            else {}
        )
        memory_node_context = (
            self.memory_node.execution_context(
                task_type=session_context.task_type,
                requested_plane_tags=session_context.metadata.get("graph_plane_tags"),
            )
            if self.memory_node is not None
            else {}
        )
        fusion_scaffold = self.moe_fusion.execution_plan(
            selected_expert=session_context.expert,
            memory_node_context=memory_node_context,
            hardware_profile=core_execution_plan.get("hardware_profile", {}),
        )
        execution_context = self._execution_context(
            trace_id=session_context.trace_id,
            session_id=session_context.session_id,
            task_type=session_context.task_type,
            selected_expert=session_context.expert,
            requested_model_id=registration.model_id,
            teacher_id=session_context.metadata.get("teacher_id"),
            teacher_registry_layer=session_context.metadata.get("teacher_registry_layer"),
            runtime_execution_plan=core_execution_plan,
            memory_node_context=memory_node_context,
            fusion_scaffold=fusion_scaffold,
        )
        evidence_feeds = execution_context["evidence_feeds"]
        execution_policy = execution_context["execution_policy"]
        native_execution_plan = execution_context["native_execution_plan"]
        execution_recorder.record(
            "plan-execution",
            {
                "selected_runtime_name": core_execution_plan.get("selected_runtime_name"),
                "safe_mode_fallback": core_execution_plan.get("safe_mode_fallback"),
                "plane_count": memory_node_context.get("plane_count"),
            },
        )
        execution_recorder.record(
            "evidence-driven-policy",
            {
                "policy_id": execution_policy.get("policy_id"),
                "execution_mode": execution_policy.get("execution_mode"),
                "legacy_execution_mode": execution_policy.get("legacy_execution_mode"),
                "shadow_vs_live_path": execution_policy.get("shadow_vs_live_path"),
                "selected_internal_experts": execution_policy.get("selected_internal_experts", []),
                "evidence_ref_count": execution_policy.get("evidence_ref_count"),
                "fallback_triggers": execution_policy.get("fallback_triggers", []),
            },
        )
        execution_recorder.record(
            "moe-fusion-plan",
            {
                "backbone": fusion_scaffold.get("backbone"),
                "router": fusion_scaffold.get("router"),
                "projection_required_count": ((fusion_scaffold.get("alignment") or {}).get("projection_required_count")),
            },
        )

        raw_prompt = request.prompt or self._prompt_from_messages(request.messages)
        recent_memory = self.memory.recent_messages(session_context.session_id, limit=session_context.memory_budget)
        retrieval_hits = []
        retrieval_policy_decision: dict[str, object] = {
            "policy_mode": "lexical-baseline",
            "effective_policy_mode": "lexical-baseline",
            "graph_store_health": {},
            "graph_contribution_count": 0,
            "memory_contribution_count": 0,
            "temporal_contribution_count": 0,
            "plane_tags": [],
            "graph_provenance": [],
            "candidate_source_counts": {},
            "top_k_before_rerank": 0,
            "top_k_after_rerank": 0,
            "reranker": {"provider": None, "applied": False, "latency_delta_ms": 0, "relevance_delta": 0.0, "groundedness_delta": 0.0},
        }
        if session_context.use_retrieval and raw_prompt.strip():
            retrieval_policy_decision = self.retrieval.query_with_policy(
                RetrievalRequest(
                    query=raw_prompt,
                    top_k=int(session_context.metadata.get("retrieval_top_k", 5)),
                    session_id=session_context.session_id,
                    use_pgvector=bool(session_context.metadata.get("use_pgvector")),
                ),
                policy_mode=str(session_context.metadata.get("retrieval_policy", "lexical+graph-merged")),
                plane_tags=session_context.metadata.get("graph_plane_tags"),
            )
            retrieval_hits = retrieval_policy_decision["hits"]

        native_execution = self.internal_expert_execution.execute(
            prompt=raw_prompt,
            selected_expert=session_context.expert,
            native_execution_plan=native_execution_plan,
            execution_policy=execution_policy,
            evidence_feeds=evidence_feeds,
        )
        execution_recorder.record(
            "internal-expert-harness",
            {
                "execution_id": native_execution.get("execution_id"),
                "enabled": native_execution.get("enabled"),
                "output_count": native_execution.get("output_count", 0),
                "disagreement_count": native_execution.get("disagreement_count", 0),
                "fallback_triggered": native_execution.get("fallback_triggered", False),
                "guarded_live_allowed": native_execution.get("guarded_live_allowed", False),
                "recommended_execution_mode": native_execution.get("recommended_execution_mode"),
                "teacher_comparison_verdict": (((native_execution.get("teacher_comparison") or {}).get("verdict"))),
                "alignment_hold_required": native_execution.get("alignment_hold_required", False),
            },
        )
        execution_recorder.record(
            "native-candidate-activation",
            {
                "candidate_id": (((native_execution.get("native_candidate") or {}).get("candidate_id"))),
                "activation_mode": (((native_execution.get("native_candidate") or {}).get("activation_mode"))),
                "activation_allowed": (((native_execution.get("native_candidate") or {}).get("activation_allowed"))),
                "confidence": (((native_execution.get("native_candidate") or {}).get("confidence"))),
            },
        )
        promotion_linkage = self.native_execution_planner.promotion_linkage(
            selected_expert=session_context.expert,
            execution_policy=execution_policy,
            native_execution_plan=native_execution_plan,
            native_execution_result=native_execution,
            evidence_feeds=evidence_feeds,
        )
        execution_recorder.record(
            "native-promotion-linkage",
            {
                "decision_id": promotion_linkage.get("decision_id"),
                "governed_action": promotion_linkage.get("governed_action"),
                "execution_action": promotion_linkage.get("execution_action"),
                "candidate_id": promotion_linkage.get("candidate_id"),
                "teacher_fallback_triggered": promotion_linkage.get("teacher_fallback_triggered", False),
            },
        )
        enriched_prompt = self._build_prompt(
            raw_prompt=raw_prompt,
            session_context=session_context,
            recent_memory=recent_memory,
            retrieval_hits=retrieval_hits,
            execution_policy=execution_policy,
            native_execution=native_execution,
            promotion_linkage=promotion_linkage,
        )
        execution_prompt, compression = self.memory.compress_prompt(
            enriched_prompt,
            target_tokens=session_context.compression_target_tokens,
        )

        started_at = _utcnow()
        start_time = time.perf_counter()
        status = "ok"
        error = None
        adapter = None
        attachment_record: dict | None = None
        attempted_runtimes: list[str] = []
        fallback_used = False
        planned_runtimes = self._planned_runtimes(
            registration.runtime_name,
            runtime_override=runtime_override,
            fallback_chain=fallback_chain,
        )
        for runtime_name in planned_runtimes:
            attempted_runtimes.append(runtime_name)
            try:
                runtime_backend = self.runtime_registry.get_adapter(runtime_name)
            except Exception:
                continue
            profile = runtime_backend.profile()
            if not profile.available and runtime_name != "mock":
                continue
            try:
                adapter, attachment_record = self._attach_base_model(
                    model_hint=registration.model_id,
                    role="teacher",
                    runtime_override=runtime_name,
                    runtime_decision=core_execution_plan,
                    session_context=session_context,
                    execution_policy=execution_policy,
                    native_execution=native_execution,
                    promotion_linkage=promotion_linkage,
                )
                execution_recorder.record(
                    "attach-base-model",
                    {
                        "model_id": attachment_record.get("model_id"),
                        "runtime_name": attachment_record.get("runtime_name"),
                        "adapter_id": attachment_record.get("adapter_id"),
                    },
                )
                execution_recorder.record(
                    "runtime-generate",
                    {
                        "runtime_name": runtime_name,
                        "fallback_candidate": runtime_name != (runtime_override or registration.runtime_name),
                    },
                )
                output = adapter.generate(
                    session_context=session_context,
                    prompt=execution_prompt,
                    messages=request.messages or [Message(role="user", content=raw_prompt)],
                )
                fallback_used = runtime_name != (runtime_override or registration.runtime_name)
                break
            except Exception as exc:
                status = "warning"
                error = str(exc)
                adapter = None
        if adapter is None:
            adapter, attachment_record = self._attach_base_model(
                model_hint="mock/default",
                role="teacher",
                runtime_override="mock",
                runtime_decision=core_execution_plan,
                session_context=session_context,
                execution_policy=execution_policy,
                native_execution=native_execution,
                promotion_linkage=promotion_linkage,
            )
            execution_recorder.record(
                "attach-base-model",
                {
                    "model_id": attachment_record.get("model_id"),
                    "runtime_name": attachment_record.get("runtime_name"),
                    "adapter_id": attachment_record.get("adapter_id"),
                    "fallback": True,
                },
            )
            output = adapter.generate(
                session_context=session_context,
                prompt=execution_prompt,
                messages=request.messages or [Message(role="user", content=raw_prompt)],
            )
            fallback_used = True
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        critique = self.critique.assess(
            trace_id=session_context.trace_id,
            request=OperatorRequest(
                session_id=session_context.session_id,
                prompt=raw_prompt,
                messages=request.messages,
                use_retrieval=session_context.use_retrieval,
                success_conditions=request.success_conditions,
                metadata=session_context.metadata,
            ),
            output=output,
            runtime_name=adapter.runtime_backend.runtime_name,
            retrieval_hits=retrieval_hits,
        )
        if critique.status == "warning":
            status = "warning"
        if critique.status == "error":
            status = "error"
        execution_recorder.record(
            "critique",
            {
                "critique_id": critique.critique_id,
                "status": critique.status,
            },
        )

        trace = InferenceTrace(
            trace_id=session_context.trace_id,
            session_id=session_context.session_id,
            model_id=adapter.model_id,
            runtime_name=adapter.runtime_backend.runtime_name,
            adapter_id=adapter.adapter_id,
            adapter_role=adapter.adapter_role,
            started_at=started_at,
            completed_at=_utcnow(),
            latency_ms=latency_ms,
            input_preview=raw_prompt[:240],
            output_preview=output[:240],
            retrieval_hit_count=len(retrieval_hits),
            compression=compression,
            critique_id=critique.critique_id,
            status=status,
            error=error,
            metrics={
                "memory_budget": session_context.memory_budget,
                "compression_applied": compression is not None,
                "retrieval_enabled": session_context.use_retrieval,
                "runtime_selection": runtime_selection or {
                    "selected_runtime_name": runtime_override or registration.runtime_name,
                    "fallback_runtime_names": fallback_chain or [],
                },
                "attempted_runtimes": attempted_runtimes,
                "fallback_used": fallback_used,
                "retrieval_policy": retrieval_policy_decision["policy_mode"],
                "retrieval_effective_policy": retrieval_policy_decision.get("effective_policy_mode"),
                "graph_store_health": retrieval_policy_decision["graph_store_health"],
                "graph_contribution_count": retrieval_policy_decision["graph_contribution_count"],
                "memory_contribution_count": retrieval_policy_decision.get("memory_contribution_count", 0),
                "temporal_contribution_count": retrieval_policy_decision.get("temporal_contribution_count", 0),
                "graph_plane_tags": retrieval_policy_decision["plane_tags"],
                "candidate_source_counts": retrieval_policy_decision.get("candidate_source_counts", {}),
                "top_k_before_rerank": retrieval_policy_decision.get("top_k_before_rerank", 0),
                "top_k_after_rerank": retrieval_policy_decision.get("top_k_after_rerank", 0),
                "reranker": retrieval_policy_decision.get("reranker", {}),
                "core_execution": {
                    "canonical_attach_seam": "nexusnet.core.attach_base_model.attach_base_model",
                    "brain_started_first": True,
                    "startup_log_path": (self._wake_state or {}).get("log_path"),
                    "hardware_profile": core_execution_plan.get("hardware_profile", {}),
                    "memory_node": memory_node_context,
                    "fusion_scaffold": fusion_scaffold,
                    "evidence_feeds": evidence_feeds,
                    "execution_policy": execution_policy,
                    "native_execution": native_execution,
                    "promotion_linkage": promotion_linkage,
                    "qes_execution_plan": core_execution_plan,
                    "model_attachment": attachment_record or {},
                    "teacher_registry_layer": session_context.metadata.get("teacher_registry_layer"),
                    "teacher_id": session_context.metadata.get("teacher_id"),
                    "lineage_tags": build_lineage_tags(
                        teacher_registry_layer=session_context.metadata.get("teacher_registry_layer"),
                        teacher_id=session_context.metadata.get("teacher_id"),
                        attached_role=(attachment_record or {}).get("requested_role"),
                        task_type=session_context.task_type,
                        dream_lineage=session_context.metadata.get("teacher_lineage"),
                    ),
                    "stage_names": execution_recorder.stage_names(),
                    "stages": execution_recorder.snapshot(),
                    "brain_lifecycle": self.lifecycle_trace.snapshot(),
                },
                "graph_dream_seed": {
                    "seed_kind": "graph-retrieval-contribution",
                    "graph_provenance": retrieval_policy_decision["graph_provenance"],
                }
                if retrieval_policy_decision["graph_contribution_count"]
                else None,
            },
        )
        core_execution_artifact = persist_core_execution_artifact(
            store=self.store,
            trace_id=trace.trace_id,
            session_id=trace.session_id,
            payload=dict(trace.metrics.get("core_execution", {})),
        )
        trace.metrics["core_execution"] = {
            **dict(trace.metrics.get("core_execution", {})),
            **core_execution_artifact,
        }
        trace.memory_records_written = self.memory.record_inference(
            session_context=session_context,
            prompt=raw_prompt,
            output=output,
            trace=trace,
            retrieval_hits=len(retrieval_hits),
        )
        if retrieval_hits:
            self.memory.memory.record_semantic(
                session_context.session_id,
                fact=retrieval_hits[0].content[:240],
                source=retrieval_hits[0].source,
            )
            trace.memory_records_written += 1
        self.store.save_trace(
            trace.trace_id,
            trace.session_id,
            trace.status,
            {
                "trace_id": trace.trace_id,
                "session_id": trace.session_id,
                "status": trace.status,
                "request": {
                    "prompt": raw_prompt,
                    "use_retrieval": session_context.use_retrieval,
                    "metadata": session_context.metadata,
                },
                "selected_expert": session_context.expert,
                "model_id": trace.model_id,
                "runtime_name": trace.runtime_name,
                "metrics": trace.metrics,
                "retrieval_policy": retrieval_policy_decision["policy_mode"],
                "retrieval_policy_decision": retrieval_policy_decision,
                "promotion_references": [
                    f"runtime-profile::{trace.runtime_name}",
                    f"retrieval-policy::{retrieval_policy_decision['policy_mode']}",
                    *[
                        ref
                        for ref in [
                            (promotion_linkage.get("decision_id") and f"native-promotion::{promotion_linkage.get('decision_id')}"),
                            (promotion_linkage.get("replacement_readiness_report_id") and f"replacement-readiness::{promotion_linkage.get('replacement_readiness_report_id')}"),
                            (promotion_linkage.get("candidate_id") and f"native-takeover::{promotion_linkage.get('candidate_id')}"),
                        ]
                        if ref
                    ],
                ],
                "retrieval_hits": len(retrieval_hits),
                "critique_id": trace.critique_id,
                "output_preview": trace.output_preview,
                "adapter_id": trace.adapter_id,
                "adapter_role": trace.adapter_role,
                "inference_trace": trace.model_dump(mode="json"),
            },
            trace.started_at.isoformat(),
        )
        trace.log_path = self.telemetry.log_inference(trace.model_dump(mode="json"))
        citations = [
            {"doc_id": hit.doc_id, "chunk_id": hit.chunk_id, "source": hit.source, "score": hit.score}
            for hit in retrieval_hits
        ]
        return BrainGenerateResult(
            trace_id=trace.trace_id,
            session_id=trace.session_id,
            model_id=trace.model_id,
            runtime_name=trace.runtime_name,
            adapter_id=trace.adapter_id,
            output=output,
            retrieval_hits=retrieval_hits,
            critique=critique,
            inference_trace=trace,
            citations=citations,
            compression=compression,
            used_memory_count=len(recent_memory),
            attached_role=adapter.adapter_role,
            runtime_selection=trace.metrics.get("runtime_selection", {}),
            retrieval_policy_decision={
                "policy_mode": retrieval_policy_decision["policy_mode"],
                "effective_policy_mode": retrieval_policy_decision.get("effective_policy_mode"),
                "graph_store_health": retrieval_policy_decision["graph_store_health"],
                "graph_contribution_count": retrieval_policy_decision["graph_contribution_count"],
                "memory_contribution_count": retrieval_policy_decision.get("memory_contribution_count", 0),
                "temporal_contribution_count": retrieval_policy_decision.get("temporal_contribution_count", 0),
                "plane_tags": retrieval_policy_decision["plane_tags"],
                "candidate_source_counts": retrieval_policy_decision.get("candidate_source_counts", {}),
                "top_k_before_rerank": retrieval_policy_decision.get("top_k_before_rerank", 0),
                "top_k_after_rerank": retrieval_policy_decision.get("top_k_after_rerank", 0),
                "candidate_list_before_rerank": retrieval_policy_decision.get("candidate_list_before_rerank", []),
                "candidate_list_after_rerank": retrieval_policy_decision.get("candidate_list_after_rerank", []),
                "reranker": retrieval_policy_decision.get("reranker", {}),
            },
            promotion_references=[
                f"runtime-profile::{trace.runtime_name}",
                f"retrieval-policy::{retrieval_policy_decision['policy_mode']}",
                *[
                    ref
                    for ref in [
                        ((execution_policy.get("evidence_refs") or {}).get("teacher_bundle_id") and f"teacher-bundle::{(execution_policy.get('evidence_refs') or {}).get('teacher_bundle_id')}"),
                        ((execution_policy.get("evidence_refs") or {}).get("distillation_artifact_id") and f"distillation::{(execution_policy.get('evidence_refs') or {}).get('distillation_artifact_id')}"),
                        ((execution_policy.get("evidence_refs") or {}).get("native_takeover_candidate_id") and f"native-takeover::{(execution_policy.get('evidence_refs') or {}).get('native_takeover_candidate_id')}"),
                        (promotion_linkage.get("decision_id") and f"native-promotion::{promotion_linkage.get('decision_id')}"),
                        (promotion_linkage.get("replacement_readiness_report_id") and f"replacement-readiness::{promotion_linkage.get('replacement_readiness_report_id')}"),
                    ]
                    if ref
                ],
            ],
        )

    def run_benchmark(self, *, suite_name: str, cases, model_hint: str | None = None):
        return self.benchmarks.run(suite_name=suite_name, brain=self, cases=cases, model_hint=model_hint)

    def _build_prompt(
        self,
        *,
        raw_prompt: str,
        session_context: SessionContext,
        recent_memory: list[Message],
        retrieval_hits: list,
        execution_policy: dict[str, Any] | None = None,
        native_execution: dict[str, Any] | None = None,
        promotion_linkage: dict[str, Any] | None = None,
    ) -> str:
        parts = [
            "NexusNet wrapper context:",
            f"- expert={session_context.expert or 'general'}",
            f"- task_type={session_context.task_type}",
            f"- use_retrieval={session_context.use_retrieval}",
        ]
        if execution_policy:
            parts.append("Core execution policy:")
            parts.append(f"- mode={execution_policy.get('execution_mode')}")
            if execution_policy.get("proposed_execution_mode"):
                parts.append(f"- proposed_mode={execution_policy.get('proposed_execution_mode')}")
            if execution_policy.get("legacy_execution_mode"):
                parts.append(f"- legacy_mode={execution_policy.get('legacy_execution_mode')}")
            parts.append(f"- shadow_vs_live={execution_policy.get('shadow_vs_live_path')}")
            if execution_policy.get("governed_action"):
                parts.append(f"- governed_action={execution_policy.get('governed_action')}")
            for reason in execution_policy.get("decision_reasons", [])[:3]:
                parts.append(f"- reason: {reason}")
            for trigger in execution_policy.get("fallback_triggers", [])[:3]:
                parts.append(f"- fallback_trigger: {trigger}")
        allow_native_guidance = (
            not promotion_linkage
            or promotion_linkage.get("effective_execution_mode") in {
                "native_shadow",
                "native_challenger_shadow",
                "native_planner_live",
                "native_live_guarded",
            }
            or promotion_linkage.get("governed_action")
            in {"allow_native_shadow", "allow_native_challenger_shadow", "allow_native_live_guarded", "hold_for_alignment"}
        )
        if native_execution and native_execution.get("enabled") and allow_native_guidance:
            parts.append("Native expert guidance:")
            for line in native_execution.get("prompt_guidance", [])[:3]:
                parts.append(f"- {line}")
            if (native_execution.get("teacher_comparison") or {}).get("verdict"):
                parts.append(f"- teacher_verdict={((native_execution.get('teacher_comparison') or {}).get('verdict'))}")
            if native_execution.get("recommended_execution_mode"):
                parts.append(f"- native_recommended_mode={native_execution.get('recommended_execution_mode')}")
            if (native_execution.get("native_candidate") or {}).get("candidate_id"):
                parts.append("Native candidate:")
                parts.append(f"- candidate_id={((native_execution.get('native_candidate') or {}).get('candidate_id'))}")
                parts.append(f"- activation_mode={((native_execution.get('native_candidate') or {}).get('activation_mode'))}")
                parts.append(f"- activation_allowed={((native_execution.get('native_candidate') or {}).get('activation_allowed'))}")
                parts.append(f"- candidate_confidence={((native_execution.get('native_candidate') or {}).get('confidence'))}")
                parts.append(f"- draft: {((native_execution.get('native_candidate') or {}).get('content'))}")
        if promotion_linkage:
            parts.append("Promotion linkage:")
            parts.append(f"- governed_action={promotion_linkage.get('governed_action')}")
            parts.append(f"- action={promotion_linkage.get('execution_action')}")
            if promotion_linkage.get("effective_execution_mode"):
                parts.append(f"- effective_mode={promotion_linkage.get('effective_execution_mode')}")
            if promotion_linkage.get("alignment_hold_required"):
                parts.append("- alignment_hold_required=true")
            if ((promotion_linkage.get("behavior_loop") or {}).get("next_step")):
                parts.append(f"- next_step={((promotion_linkage.get('behavior_loop') or {}).get('next_step'))}")
            if promotion_linkage.get("decision_id"):
                parts.append(f"- decision_id={promotion_linkage.get('decision_id')}")
            if promotion_linkage.get("rollback_reference"):
                parts.append(f"- rollback_reference={promotion_linkage.get('rollback_reference')}")
            if not allow_native_guidance:
                parts.append("- native_guidance_suppressed_by_governance=true")
        if recent_memory:
            parts.append("Memory:")
            for message in recent_memory[-session_context.memory_budget :]:
                parts.append(f"- {message.role}: {message.content[:180]}")
        if retrieval_hits:
            parts.append("Retrieved context:")
            for hit in retrieval_hits[:5]:
                parts.append(f"- ({hit.source}) {hit.content[:220]}")
        parts.append(f"User request: {raw_prompt}")
        return "\n".join(parts)

    def _prompt_from_messages(self, messages: list[Message]) -> str:
        return "\n".join(f"{message.role.upper()}: {message.content}" for message in messages)

    def _adapter_key(self, model_id: str, role: str, runtime_name: str) -> str:
        return f"{role}:{model_id}@{runtime_name}"

    def _attach_base_model(
        self,
        *,
        model_hint: str | None,
        role: str,
        runtime_override: str | None,
        runtime_decision: dict | None = None,
        session_context: SessionContext | None = None,
        execution_policy: dict[str, Any] | None = None,
        native_execution: dict[str, Any] | None = None,
        promotion_linkage: dict[str, Any] | None = None,
    ) -> tuple[BaseModelAdapter, dict]:
        if self._wake_state is None:
            self.wake()
        adapter, attachment_record = self.model_ingestion.attach(
            model_hint=model_hint,
            role=role,
            runtime_name=runtime_override,
            hardware_profile=(runtime_decision or {}).get("hardware_profile", {}),
            runtime_decision=runtime_decision,
            teacher_registry_layer=(session_context.metadata.get("teacher_registry_layer") if session_context else None),
            teacher_id=(session_context.metadata.get("teacher_id") if session_context else None),
            lineage_tags=build_lineage_tags(
                teacher_registry_layer=(session_context.metadata.get("teacher_registry_layer") if session_context else None),
                teacher_id=(session_context.metadata.get("teacher_id") if session_context else None),
                attached_role=role,
                task_type=(session_context.task_type if session_context else None),
                dream_lineage=(session_context.metadata.get("teacher_lineage") if session_context else None),
            ),
            evidence_refs=((execution_policy or {}).get("evidence_refs")),
            execution_mode=(
                ((promotion_linkage or {}).get("effective_execution_mode"))
                or ((execution_policy or {}).get("execution_mode"))
            ),
            proposed_execution_mode=((execution_policy or {}).get("proposed_execution_mode")),
            execution_policy_id=((execution_policy or {}).get("policy_id")),
            legacy_execution_mode=(
                ((promotion_linkage or {}).get("legacy_effective_execution_mode"))
                or ((execution_policy or {}).get("legacy_execution_mode"))
            ),
            governed_action=((promotion_linkage or {}).get("governed_action") or ((execution_policy or {}).get("governed_action"))),
            native_execution_verdict=(((native_execution or {}).get("teacher_comparison")) or {}).get("verdict"),
            alignment_hold_required=(
                ((promotion_linkage or {}).get("alignment_hold_required"))
                if (promotion_linkage or {}).get("alignment_hold_required") is not None
                else (((execution_policy or {}).get("alignment_summary")) or {}).get("alignment_hold_required")
            ),
            native_candidate_id=(((native_execution or {}).get("native_candidate")) or {}).get("candidate_id"),
            native_activation_mode=(((native_execution or {}).get("native_candidate")) or {}).get("activation_mode"),
            native_candidate_confidence=(((native_execution or {}).get("native_candidate")) or {}).get("confidence"),
            promotion_action=((promotion_linkage or {}).get("execution_action")),
            promotion_decision_id=((promotion_linkage or {}).get("decision_id")),
            startup_log_path=(self._wake_state or {}).get("log_path"),
        )
        self.lifecycle_trace.record(
            "attach-base-model",
            {
                "model_id": attachment_record.get("model_id"),
                "runtime_name": attachment_record.get("runtime_name"),
                "adapter_id": attachment_record.get("adapter_id"),
            },
        )
        return adapter, attachment_record

    def _planned_runtimes(self, registration_runtime: str, *, runtime_override: str | None, fallback_chain: list[str] | None) -> list[str]:
        planned = [runtime_override or registration_runtime, *(fallback_chain or []), registration_runtime, "mock"]
        ordered: list[str] = []
        for runtime_name in planned:
            if runtime_name and runtime_name not in ordered:
                ordered.append(runtime_name)
        return ordered

    def _latest_core_execution(self, *, session_id: str | None = None, trace_id: str | None = None) -> dict[str, Any]:
        traces = self.store.list_traces(limit=200)
        if trace_id:
            traces = [trace for trace in traces if trace.get("trace_id") == trace_id]
        elif session_id:
            traces = [trace for trace in traces if trace.get("session_id") == session_id]
        for trace in traces:
            core_execution = ((trace.get("metrics") or {}).get("core_execution")) or {}
            if core_execution.get("artifact_id") or core_execution.get("artifact_path"):
                return {
                    "trace_id": trace.get("trace_id"),
                    "artifact_id": core_execution.get("artifact_id"),
                    "artifact_path": core_execution.get("artifact_path"),
                }
        return {}

    def _execution_context(
        self,
        *,
        trace_id: str,
        session_id: str,
        task_type: str,
        selected_expert: str | None,
        requested_model_id: str,
        teacher_id: str | None,
        teacher_registry_layer: str | None,
        runtime_execution_plan: dict[str, Any],
        memory_node_context: dict[str, Any],
        fusion_scaffold: dict[str, Any],
    ) -> dict[str, Any]:
        evidence_feeds = (
            self.evidence_bridge.snapshot(
                trace_id=trace_id,
                session_id=session_id,
                subject=selected_expert,
                teacher_id=teacher_id,
            )
            if self.evidence_bridge is not None
            else {}
        )
        execution_policy = self.execution_policy_engine.decide(
            trace_id=trace_id,
            session_id=session_id,
            task_type=task_type,
            selected_expert=selected_expert,
            requested_model_id=requested_model_id,
            runtime_execution_plan=runtime_execution_plan,
            memory_node_context=memory_node_context,
            fusion_scaffold=fusion_scaffold,
            evidence_feeds=evidence_feeds,
            teacher_registry_layer=teacher_registry_layer,
            teacher_id=teacher_id,
        )
        native_execution_plan = self.native_execution_planner.plan(
            trace_id=trace_id,
            selected_expert=selected_expert,
            execution_policy=execution_policy,
            fusion_scaffold=fusion_scaffold,
            memory_node_context=memory_node_context,
            evidence_feeds=evidence_feeds,
        )
        return {
            "evidence_feeds": evidence_feeds,
            "execution_policy": execution_policy,
            "native_execution_plan": native_execution_plan,
        }
