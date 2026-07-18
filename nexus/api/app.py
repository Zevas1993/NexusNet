from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
import time
from typing import Any

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from ..config import save_yaml_file
from ..schemas import ApprovalRequest, ChatRequest, ModelRuntimePlanRequest, RetrievalIngestRequest, RetrievalRequest
from ..services import NexusServices, build_services
from nexusnet.core import AutonomousUpdateRequest, CompatibilityStatus, RuntimeUnavailableError, SelfReviewRequest
from nexusnet.core.ebt import EBTScoreRequest
from nexusnet.protocols import ProtocolAdapterPolicyRequest, ProtocolConsentRequest, ProtocolServerDefinition, ToolAttempt
from nexusnet.schemas import CoreModelAttachRequest, CurriculumAssessmentRequest, DistillationExportRequest, DreamCycleRequest, GraphIngestRequest, ModelAttachRequest
from nexusnet.adapters.dataset_forge import DatasetForgeRequest
from nexusnet.adapters.decision_gate import FineTuneDecisionRequest
from nexusnet.adapters.forge import AdapterRecordRequest
from nexusnet.adapters.training_planner import AdapterTrainingPlanRequest
from nexusnet.agents import AgentOpportunityRequest, SandboxAgentFactoryRunRequest
from nexusnet.agents.harnesses import HarnessLedgerEntryRequest, HarnessRouteRequest
from nexusnet.browser import BrowserContextIngestRequest, BrowserContextQueryRequest, BrowserProfilePolicyRequest
from nexusnet.evals import EvalSuiteRequest, ShadowEvalRunRequest, VerifierSearchRequest
from nexusnet.growth import GrowthCycleRequest
from nexusnet.hive.hive_snapshot import hive_evidence_snapshot
from nexusnet.hive.self_improvement_engine import default_engine as _self_improvement_engine
from nexusnet.hive.continuous_assimilation import ContinuousAssimilationLoop
from nexusnet.hive.multi_user_growth import MultiUserGrowthCoordinator
from nexusnet.providers.model_providers import default_provider_registry as _default_provider_registry
from nexusnet.release_health_heartbeat_supervisor_repair import (
    build_completed_release_health_heartbeat_subsystem_repair_envelopes,
    build_release_health_heartbeat_supervisor_repair_run_plan,
)
from nexusnet.release_wrapper import ReleaseWrapperRuntime, release_native_hive_heartbeat_history_evidence
from nexusnet.knowledge import KnowledgeCompileRequest, KnowledgeRequestContract
from nexusnet.research import ForwardRadarCandidateRequest
from nexusnet.retrieval import RetrievalPlanRequest
from nexusnet.runtime.cache_ledger import CacheLedgerEntryRequest
from nexusnet.runtime.workload_scorecards import RuntimeWorkloadScorecardRequest
from nexusnet.canon.realization import (
    ao_hive_scorecard,
    answer_operator_question,
    artifact_trust_scorecard,
    autonomous_evolution_dossier,
    blackbox_recorder,
    completion_assessment,
    communication_integration_scorecard,
    eval_suite_scorecard,
    experts_hive_scorecard,
    hardware_matrix_scorecard,
    hive_consensus_scorecard,
    input_ingestion_scorecard,
    live_flow_scorecard,
    memory_provenance_scorecard,
    neural_core_scorecard,
    observability_scorecard,
    output_delivery_scorecard,
    protocol_trust_scorecard,
    researcher_swarm_scorecard,
    runtime_quantization_scorecard,
    security_governance_scorecard,
    self_improvement_scorecard,
    surface_drilldown,
    tool_execution_scorecard,
    visualops_scorecard,
)
from nexusnet.core.self_improvement import (
    ExperienceCapture,
    ImprovementEvent,
    ImprovementEvaluator,
    ImprovementQueue,
    LineageCandidateRequest,
    MemoryUpdatePolicy,
    PromptUpdatePolicy,
    ProvenanceTracker,
    RegressionGate,
    TrainingCandidateBuilder,
    triage_improvement_event,
)
from nexusnet.agents.pipelines import AgenticPipelineRequest
from nexusnet.operations import CodegraphRunManifestRequest
from nexusnet.hive import (
    HiveActiveReleaseRequest,
    HiveAssimilationCandidateRequest,
    HiveCheckpointRewindRequest,
    HiveForwardPassRequest,
    HiveGlobalFederationReviewRequest,
    HiveProductionizationRequest,
    HiveRollbackRequest,
    HiveRecursiveDreamRequest,
    HiveShadowReleaseRequest,
)
from nexusnet.policy import PolicyKernel, PolicyScanRequest
from nexusnet.protocols import ProtocolAdapterRequest
from nexusnet.runtime.edge_router import EdgeWorkloadRequest
from nexusnet.runtime.inference_economy_router import InferenceRouteRequest
from nexusnet.runtime.inference_architecture import InferenceArchitectureRequest
from nexusnet.runtime.evolutionary_inference import (
    CapacityGate,
    RuntimeModelMetadata,
    RuntimeObservation,
    SLOProfile,
    WorkloadProfile,
)
from nexusnet.runtime.model_passport import CertificationRunRequest, ModelPassportRequest
from nexusnet.runtime.quantization.catalog import QuantizationRecommendationRequest
from nexusnet.security import ArtifactScanRequest
from nexusnet.telemetry import ConceptTelemetryRequest, GenAITraceEventRequest, SAEExperimentRequest
from nexusnet.memory import EngramLookupRequest, EngramRecordRequest, SourceClaimRequest
from nexusnet.vision import ComputerUsePlanRequest, OperatorEventRequest
from nexusnet.training import TrainingDataExportRecord


def create_app(project_root: str | None = None) -> FastAPI:
    services = build_services(project_root)
    application = FastAPI(title="Nexus API", version=services.version)
    application.state.services = services
    # Continuous Ivy-League assimilation: real /chat usage feeds the birth loop (canon C39M0238).
    # Privacy-safe: captures a content HASH + provenance, never raw prompts/outputs.
    continuous_assimilation = ContinuousAssimilationLoop()
    application.state.continuous_assimilation = continuous_assimilation
    global_growth = MultiUserGrowthCoordinator()
    application.state.global_growth = global_growth
    services.brain_hive_substrate.global_growth = global_growth
    application.state.global_growth_rehydration = services.brain_hive_substrate.hydrate_runtime_growth_from_artifacts()
    self_improvement_queue = ImprovementQueue(services.paths.state_dir / "self_improvement_queue.json")
    application.state.self_improvement_queue = self_improvement_queue
    # The wrapper's pool of wrapped models (offline echo + canon cloud/local providers).
    import os as _os
    provider_registry = _default_provider_registry(
        openrouter_key=_os.environ.get("OPENROUTER_API_KEY", ""),
        requesty_key=_os.environ.get("REQUESTY_API_KEY", ""))
    application.state.provider_registry = provider_registry
    release_wrapper_runtime = ReleaseWrapperRuntime(
        artifacts_dir=services.paths.artifacts_dir,
        continuous_assimilation=continuous_assimilation,
        global_growth=global_growth,
        hive_substrate=services.brain_hive_substrate,
        autonomous_updates=services.brain_autonomous_updates,
        production_spine=services.brain_production_spine,
        brain=services.brain,
        improvement_queue=self_improvement_queue,
        eval_registry=services.brain_eval_registry,
        cache_ledger=services.brain_cache_ledger,
        ao_registry=services.brain_aos,
        provider_registry=provider_registry,
        teacher_registry=services.brain_teachers,
        teacher_evidence_service=services.brain_teacher_evidence,
        developmental_cortex=services.brain_developmental_cortex,
        growth_engine=services.brain_growth_engine,
        promotion_service=services.brain_promotions,
        foundry_benchmarks=services.brain_foundry_benchmarks,
        authority_spine=services.brain_authority_spine,
        evidence_store=services.brain_evidence_store,
        eval_federation=services.brain_eval_federation,
        tool_action_harness=services.brain_tool_action_harness,
        runtime_decision_ledger=services.brain_runtime_decision_ledger,
        quantization_catalog=services.brain_quantization_catalog,
    )
    application.state.release_wrapper_runtime = release_wrapper_runtime
    services.brain.native_runtime_growth_review_bridge = release_wrapper_runtime.queue_native_runtime_growth_review
    services.brain_ui_surface.release_runtime_status_provider = release_wrapper_runtime.summary
    services.brain_ui_surface.release_readiness_provider = release_wrapper_runtime.release_readiness_manifest
    services.brain_ui_surface.release_session_lifecycle_provider = release_wrapper_runtime.session_lifecycle
    application.state.release_wrapper_startup_supervision = (
        release_wrapper_runtime.record_automatic_release_health_heartbeat_loop(
            session_id=None,
            trigger="startup-auto",
            base_url="http://127.0.0.1:0",
            host="127.0.0.1",
            port=0,
            pid=0,
        )
    )
    application.state.release_health_heartbeat_supervisor = (
        release_wrapper_runtime.configure_release_health_heartbeat_supervisor(
            session_id=None,
            enabled=True,
            interval_seconds=60,
            max_pulses_per_tick=1,
            schedule_immediately=False,
            configured_by="startup",
        )
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def _latest_trace_ids(session_id: str | None, limit: int = 3) -> list[str]:
        if not session_id:
            return []
        return [
            trace.get("trace_id")
            for trace in services.store.list_traces(limit=200)
            if trace.get("session_id") == session_id and trace.get("trace_id")
        ][:limit]

    def _rough_message_tokens(messages: list[Any]) -> int:
        total = 0
        for message in messages:
            if isinstance(message, dict):
                total += len(str(message.get("content") or "").split())
            else:
                total += len(str(getattr(message, "content", "") or "").split())
        return total

    def _privacy_compat_digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]

    production_spine_lifecycle_approval_subject = "release-wrapper-production-spine-release-lifecycle"

    def _production_spine_lifecycle_admin_approval_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
        approval_ref = str(
            payload.get("approval_decision_id")
            or payload.get("admin_approval_ref")
            or payload.get("approval_ref")
            or ""
        ).strip()
        if not approval_ref:
            raise HTTPException(
                status_code=400,
                detail="Admin approval decision_id is required before running the production-spine release lifecycle.",
            )

        approvals = services.store.list_approvals(limit=500)
        approval = next(
            (
                item
                for item in approvals
                if str(item.get("decision_id") or "") == approval_ref
            ),
            None,
        )
        if approval is None:
            raise HTTPException(
                status_code=400,
                detail="Admin approval decision_id was not found in the governance approval store.",
            )
        if approval.get("subject") != production_spine_lifecycle_approval_subject:
            raise HTTPException(
                status_code=400,
                detail="Admin approval subject does not match the production-spine release lifecycle.",
            )
        if approval.get("decision") != "approved":
            raise HTTPException(
                status_code=400,
                detail="Admin approval decision must be approved before the production-spine release lifecycle can run.",
            )

        metadata = approval.get("metadata") if isinstance(approval.get("metadata"), dict) else {}
        return {
            "schema_version": "nexusnet-release-wrapper-production-spine-lifecycle-approval-v1",
            "surface_id": "release-wrapper-production-spine-lifecycle-approval",
            "approval_ref": approval_ref,
            "approval_subject": production_spine_lifecycle_approval_subject,
            "decision": "approved",
            "approver_digest": f"sha256:{_privacy_compat_digest(str(approval.get('approver') or ''))}",
            "rationale_digest": f"sha256:{_privacy_compat_digest(str(approval.get('rationale') or ''))}",
            "metadata_digest": f"sha256:{_privacy_compat_digest(json.dumps(metadata, sort_keys=True, default=str))}",
            "metadata_key_count": len(metadata),
            "created_at": str(approval.get("created_at") or ""),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
        }

    def _recipe_requested_tools(item: dict[str, Any]) -> list[str]:
        requested: set[str] = set(item.get("approved_tools", []) or [])
        for step in item.get("steps", []) or []:
            for tool in step.get("approved_tools", []) or []:
                requested.add(tool)
        return sorted(requested)

    def _recipe_requested_extensions(item: dict[str, Any]) -> list[str]:
        requested: set[str] = set(item.get("requested_extensions", []) or [])
        for step in item.get("steps", []) or []:
            for extension_id in step.get("requested_extensions", []) or []:
                requested.add(extension_id)
        return sorted(requested)

    def _parse_optional_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def _recipe_allowed_tools(item: dict[str, Any]) -> list[str]:
        recipes_config = ((services.runtime_configs.get("goose_lane") or {}).get("recipes") or {})
        approved_tool_sets = recipes_config.get("approved_tool_sets") or {}
        allowed: set[str] = set(item.get("approved_tools", []) or [])
        for tool_set_id in item.get("approved_tool_sets", []) or []:
            allowed.update(approved_tool_sets.get(tool_set_id, []) or [])
        return sorted(allowed)

    def _recipe_agent_id(item: dict[str, Any], agent_id: str | None = None) -> str:
        return agent_id or ((item.get("ao_targets") or [None])[0]) or "standard-wrapper-agent"

    def _scheduled_workflow_id(*, trigger_source: str | None, schedule_id: str | None) -> str | None:
        if schedule_id:
            return schedule_id
        if not trigger_source:
            return None
        normalized = str(trigger_source)
        for prefix in ("schedule:", "scheduled:"):
            if normalized.startswith(prefix):
                workflow_id = normalized.removeprefix(prefix).strip()
                return workflow_id or None
        return None

    def _self_improvement_queue() -> ImprovementQueue:
        return ImprovementQueue(services.paths.state_dir / "self_improvement_queue.json")

    def _self_improvement_queue_summary() -> dict[str, Any]:
        queue = _self_improvement_queue()
        items = queue.list_items()
        status_counts: dict[str, int] = {}
        for item in items:
            status_counts[item.status] = status_counts.get(item.status, 0) + 1
        return {
            "status_label": "LOCKED CANON",
            "item_count": len(items),
            "status_counts": status_counts,
            "items": [item.model_dump(mode="json") for item in items],
        }

    def _autonomous_update_proposal(update_id: str) -> dict[str, Any] | None:
        proposals = services.brain_autonomous_updates.summary(limit=500).get("proposals") or []
        return next((proposal for proposal in proposals if str(proposal.get("update_id") or "") == update_id), None)

    def _linked_improvement_queue_id(update_id: str) -> str | None:
        proposal = _autonomous_update_proposal(update_id)
        metadata = proposal.get("metadata") if isinstance((proposal or {}).get("metadata"), dict) else {}
        queue_id = str(metadata.get("improvement_queue_id") or "")
        return queue_id or None

    def _improvement_queue_transition_plan(current_status: str, target_status: str) -> list[str]:
        if current_status in {"rejected", "reverted"} or current_status == target_status:
            return []
        forward = ["proposed", "validated", "approved", "deployed", "monitored"]
        if target_status == "reverted":
            if current_status == "monitored":
                return ["reverted"]
            if current_status == "deployed":
                return ["reverted"]
            if current_status == "approved":
                return ["reverted"]
            if current_status in forward:
                current_index = forward.index(current_status)
                approved_index = forward.index("approved")
                return [*forward[current_index + 1 : approved_index + 1], "reverted"]
            return []
        if current_status not in forward or target_status not in forward:
            return []
        current_index = forward.index(current_status)
        target_index = forward.index(target_status)
        if target_index <= current_index:
            return []
        return forward[current_index + 1 : target_index + 1]

    def _sync_linked_improvement_queue(
        update_id: str,
        *,
        target_status: str,
        actor: str,
        reason: str,
    ) -> dict[str, Any]:
        queue_id = _linked_improvement_queue_id(update_id)
        if queue_id is None:
            return {
                "status": "not-linked",
                "update_id": update_id,
                "queue_id": None,
                "target_status": target_status,
            }
        queue = _self_improvement_queue()
        try:
            item = queue.get(queue_id)
        except KeyError:
            return {
                "status": "missing-queue-item",
                "update_id": update_id,
                "queue_id": queue_id,
                "target_status": target_status,
            }
        from_status = item.status
        transition_path = _improvement_queue_transition_plan(str(item.status), target_status)
        for status in transition_path:
            item = queue.transition(
                queue_id,
                status,  # type: ignore[arg-type]
                actor=actor,
                reason=f"{reason}; autonomous_update={update_id}",
            )
        return {
            "status": "transitioned" if item.status != from_status else "unchanged",
            "update_id": update_id,
            "queue_id": queue_id,
            "from_status": from_status,
            "queue_status": item.status,
            "target_status": target_status,
            "transition_path": transition_path,
        }

    def _run_linked_eval_replay(update_id: str) -> dict[str, Any]:
        proposal = _autonomous_update_proposal(update_id)
        if proposal is None:
            return {"status": "not-linked", "update_id": update_id, "reason": "proposal-not-found"}
        eval_refs = [str(ref) for ref in (proposal.get("eval_refs") or [])]
        proposal_metadata = proposal.get("metadata") if isinstance(proposal.get("metadata"), dict) else {}
        safe_payload = (
            proposal_metadata.get("safe_payload") if isinstance(proposal_metadata.get("safe_payload"), dict) else {}
        )
        federated_import_shadow = bool(
            proposal_metadata.get("federated_import_shadow")
            or proposal_metadata.get("federated_packet_import_id")
            or safe_payload.get("federated_packet_import_id")
        )
        dream_research_queue = bool(
            proposal_metadata.get("dream_research_queue")
            or proposal_metadata.get("improvement_queue_id")
        )
        suite_prefixes = (
            (
                "eval::release-wrapper-federated-import::",
                "eval::release-wrapper-dream-research::",
                "eval::release-wrapper-runtime::",
            )
            if federated_import_shadow
            else
            (
                "eval::release-wrapper-dream-research::",
                "eval::release-wrapper-federated-import::",
                "eval::release-wrapper-runtime::",
            )
            if dream_research_queue
            else (
                "eval::release-wrapper-federated-import::",
                "eval::release-wrapper-runtime::",
                "eval::release-wrapper-dream-research::",
            )
        )
        suite_id = next((ref for prefix in suite_prefixes for ref in eval_refs if ref.startswith(prefix)), None)
        if suite_id is None:
            return {"status": "not-linked", "update_id": update_id, "reason": "no-release-wrapper-eval-suite-ref"}
        registry = services.brain_eval_registry.summary(limit=500)
        suite = next((item for item in registry.get("suites", []) if item.get("suite_id") == suite_id), None)
        if suite is None:
            return {"status": "missing-eval-suite", "update_id": update_id, "suite_id": suite_id}
        metadata = suite.get("metadata") if isinstance(suite.get("metadata"), dict) else {}
        replay_template = metadata.get("replay_template") if isinstance(metadata.get("replay_template"), dict) else {}
        replay_payload = dict(replay_template.get("payload") or {})
        if not replay_payload:
            return {"status": "missing-replay-template", "update_id": update_id, "suite_id": suite_id}
        artifact_gate_refs = [
            ref
            for ref in eval_refs
            if ref.startswith("evals-ao-artifact::")
        ]
        for value in (
            proposal_metadata.get("evals_ao_artifact_gate_ref"),
            safe_payload.get("evals_ao_artifact_gate_ref"),
            metadata.get("gate_id"),
        ):
            gate_ref = str(value or "")
            if gate_ref.startswith("evals-ao-artifact::") and gate_ref not in artifact_gate_refs:
                artifact_gate_refs.append(gate_ref)
        evidence_refs = [str(ref) for ref in (replay_payload.get("evidence_refs") or []) if str(ref or "")]
        evaluator_refs = [str(ref) for ref in (replay_payload.get("evaluator_refs") or []) if str(ref or "")]
        for gate_ref in artifact_gate_refs:
            if gate_ref not in evidence_refs:
                evidence_refs.append(gate_ref)
            if gate_ref not in evaluator_refs:
                evaluator_refs.append(gate_ref)
        if artifact_gate_refs and "ao::EvalsAO" not in evaluator_refs:
            evaluator_refs.append("ao::EvalsAO")
        replay_payload["evidence_refs"] = evidence_refs
        replay_payload["evaluator_refs"] = evaluator_refs
        replay_payload["operator_approved"] = True
        replay_metadata = replay_payload.get("metadata") if isinstance(replay_payload.get("metadata"), dict) else {}
        replay_payload["metadata"] = {
            **replay_metadata,
            "admin_approved_update_id": update_id,
            "approval_trigger": "autonomous-update-admin-approval",
            "evals_ao_artifact_gate_ref": artifact_gate_refs[0] if artifact_gate_refs else None,
            "evals_ao_artifact_gate_refs": artifact_gate_refs,
            "proposal_eval_refs": eval_refs,
        }
        run = services.brain_eval_registry.run_shadow(suite_id, replay_payload)
        return services.brain_autonomous_updates.attach_eval_replay(update_id, run)

    def _self_improvement_review_payload(queue_id: str, *, operator_approved: bool = False) -> dict[str, Any]:
        try:
            item = _self_improvement_queue().get(queue_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown self-improvement queue item: {queue_id}") from exc
        provenance = ProvenanceTracker().record(
            item.event,
            verifier_refs=[f"/ops/brain/self-improvement/queue/{queue_id}/review"],
        )
        evaluation = ImprovementEvaluator().evaluate(item.event, item.decision, provenance)
        memory_candidate = MemoryUpdatePolicy().build_candidate(item.event, item.decision, provenance)
        prompt_candidate = PromptUpdatePolicy().build_candidate(item.event, item.decision)
        training_candidate = TrainingCandidateBuilder().build_candidate(item.event, item.decision, provenance)
        regression_gate = RegressionGate().evaluate(
            item,
            evaluation,
            test_results=[],
            operator_approved=operator_approved,
        )
        policy_targets = [
            {
                "target_id": f"training::{training_candidate.event_id}",
                "target_type": "training_candidate",
                "metadata": {
                    "contains_private_data": item.event.safety.contains_private_data,
                    "uses_user_data": bool(item.event.input_modalities or item.event.context_sources),
                    "operator_approved": operator_approved,
                    "promotion_requested": training_candidate.export_ready,
                    "eval_refs": item.event.evidence_refs,
                },
            },
            {
                "target_id": f"memory::{memory_candidate.event_id}",
                "target_type": "memory_update",
                "metadata": {
                    "provenance_refs": provenance.evidence_refs,
                    "retention_policy": memory_candidate.retention_policy,
                    "requires_review": memory_candidate.requires_review,
                },
            },
            {
                "target_id": f"prompt::{prompt_candidate.event_id}",
                "target_type": "autonomous_update",
                "metadata": {
                    "rollback_plan_ref": "self-improvement-regression-gate",
                    "requires_review": prompt_candidate.requires_review,
                    "policy_scope": prompt_candidate.policy_scope,
                },
            },
        ]
        if item.event.agent_task_type in {"coding", "debugging"}:
            policy_targets.append(
                {
                    "target_id": f"code::{item.event.event_id}",
                    "target_type": "code_change",
                    "metadata": {
                        "tests_provided": bool(item.event.metrics.get("tests_run") or item.event.evidence_refs),
                    },
                }
            )
        policy_scan = _policy_kernel().scan(policy_targets)
        return {
            "status_label": "LOCKED CANON",
            "queue_item": item.model_dump(mode="json"),
            "provenance": provenance.model_dump(mode="json"),
            "evaluation": evaluation.model_dump(mode="json"),
            "memory_candidate": memory_candidate.model_dump(mode="json"),
            "prompt_candidate": prompt_candidate.model_dump(mode="json"),
            "training_candidate": training_candidate.model_dump(mode="json"),
            "regression_gate": regression_gate.model_dump(mode="json"),
            "policy_scan": policy_scan.model_dump(mode="json"),
        }

    def _policy_kernel() -> PolicyKernel:
        return PolicyKernel.default()

    def _build_goose_execution_context(
        *,
        item: dict[str, Any],
        session_id: str | None,
        agent_id: str,
        workspace_id: str,
        trigger_source: str,
        linked_trace_ids: list[str],
        policy_path: list[dict[str, Any]],
        approval_path: dict[str, Any],
        requested_tools: list[str] | None = None,
        requested_extensions: list[str] | None = None,
    ) -> dict[str, Any]:
        resolved_requested_tools = sorted(set([*_recipe_requested_tools(item), *(requested_tools or [])]))
        resolved_requested_extensions = sorted(set([*_recipe_requested_extensions(item), *(requested_extensions or [])]))
        require_user_approval = (item.get("gateway_policy") in {"ask", "allow-if-approved"})
        merged_trace_ids = list(dict.fromkeys([*linked_trace_ids, *_latest_trace_ids(session_id)]))
        gateway_resolution = (
            services.brain_gateway.resolve(
                agent_id=agent_id,
                workspace_id=workspace_id,
                requested_tools=resolved_requested_tools,
                requested_extensions=resolved_requested_extensions,
                require_user_approval=require_user_approval,
                trigger_source=trigger_source,
                linked_trace_ids=merged_trace_ids,
                record_gateway_flow=True,
            )
            if resolved_requested_tools or resolved_requested_extensions
            else None
        )
        gateway_execution = (gateway_resolution or {}).get("execution_history") or {}
        gateway_execution_report = gateway_execution.get("report") or {}
        gateway_extension_provenance = list((gateway_resolution or {}).get("extension_provenance", []) or [])
        gateway_policy_set_ids = sorted(
            {item.get("policy_set_id") for item in gateway_extension_provenance if item.get("policy_set_id")}
        )
        gateway_bundle_families = sorted(
            {item.get("bundle_family") for item in gateway_extension_provenance if item.get("bundle_family")}
        )
        effective_policy_path = list(policy_path or ((gateway_resolution or {}).get("policy_path") or []))
        effective_approval_path = {
            **(((gateway_resolution or {}).get("approval_path")) or {}),
            **approval_path,
        }
        adversary_review = (gateway_resolution or {}).get("adversary_review") or {}
        adversary_report_ids = [
            report_id
            for report_id in [
                (((adversary_review.get("report") or {}).get("report_id")) if isinstance(adversary_review, dict) else None),
            ]
            if report_id
        ]
        gateway_decision_path = (
            [
                {
                    "resolution_id": gateway_resolution.get("resolution_id"),
                    "execution_id": gateway_execution.get("execution_id"),
                    "report_id": gateway_execution_report.get("report_id"),
                    "decision": ((gateway_resolution.get("policy") or {}).get("decision")),
                    "fallback_reason": gateway_resolution.get("fallback_reason"),
                    "requested_tools": resolved_requested_tools,
                    "requested_extensions": resolved_requested_extensions,
                    "extension_bundle_ids": gateway_resolution.get("extension_bundle_ids", []),
                    "policy_set_ids": gateway_policy_set_ids,
                    "permission_decision": ((gateway_resolution.get("permission_review") or {}).get("decision")),
                }
            ]
            if gateway_resolution is not None
            else []
        )
        approval_fallback_chain = [
            {
                "stage": "policy",
                "decision": ((gateway_resolution or {}).get("policy") or {}).get("decision"),
                "fallback_reason": (gateway_resolution or {}).get("fallback_reason"),
            },
            {
                "stage": "approval",
                "decision": effective_approval_path.get("decision"),
                "require_user_approval": effective_approval_path.get("require_user_approval", require_user_approval),
            },
            {
                "stage": "permission",
                "decision": (((gateway_resolution or {}).get("permission_review") or {}).get("decision")),
                "risk_level": (((gateway_resolution or {}).get("permission_review") or {}).get("risk_level")),
            },
            {
                "stage": "adversary-review",
                "decision": adversary_review.get("decision") if isinstance(adversary_review, dict) else None,
                "report_id": (((adversary_review.get("report") or {}).get("report_id")) if isinstance(adversary_review, dict) else None),
            },
        ]
        linked_report_ids = sorted(
            {
                *[report_id for report_id in adversary_report_ids if report_id],
                *[
                    report_id
                    for report_id in ((gateway_resolution or {}).get("linked_report_ids") or [])
                    if report_id
                ],
                *([gateway_execution_report.get("report_id")] if gateway_execution_report.get("report_id") else []),
            }
        )
        artifacts_produced = sorted(
            {
                artifact
                for artifact in [
                    (gateway_resolution or {}).get("artifact_path"),
                    gateway_execution.get("artifact_path"),
                    gateway_execution_report.get("payload_path"),
                    gateway_execution_report.get("markdown_path"),
                ]
                if artifact
            }
        )
        return {
            "requested_tools": resolved_requested_tools,
            "requested_extensions": resolved_requested_extensions,
            "require_user_approval": require_user_approval,
            "gateway_resolution": gateway_resolution,
            "linked_trace_ids": merged_trace_ids,
            "policy_path": effective_policy_path,
            "approval_path": effective_approval_path,
            "gateway_decision_path": gateway_decision_path,
            "execution_path": (gateway_resolution or {}).get("execution_path", []),
            "approval_fallback_chain": approval_fallback_chain,
            "adversary_review_report_ids": adversary_report_ids,
            "linked_report_ids": linked_report_ids,
            "extension_bundle_ids": (gateway_resolution or {}).get("extension_bundle_ids", []),
            "extension_policy_set_ids": gateway_policy_set_ids,
            "extension_bundle_families": gateway_bundle_families,
            "extension_provenance": gateway_extension_provenance,
            "gateway_execution_id": gateway_execution.get("execution_id"),
            "gateway_report_id": gateway_execution_report.get("report_id"),
            "artifacts_produced": artifacts_produced,
            "metadata": {
                "gateway_resolution_id": (gateway_resolution or {}).get("resolution_id"),
                "gateway_execution_id": gateway_execution.get("execution_id"),
                "gateway_report_id": gateway_execution_report.get("report_id"),
                "gateway_decision": (((gateway_resolution or {}).get("policy") or {}).get("decision")),
                "gateway_fallback_reason": (gateway_resolution or {}).get("fallback_reason"),
                "extension_bundle_ids": (gateway_resolution or {}).get("extension_bundle_ids", []),
                "extension_policy_set_ids": gateway_policy_set_ids,
                "extension_bundle_families": gateway_bundle_families,
                "requested_extensions": resolved_requested_extensions,
                "trigger_source": trigger_source,
            },
        }

    @application.get("/")
    def root():
        if services.paths.ui_dir.exists():
            return RedirectResponse(url="/ui/wrapper/")
        return {"ok": True, "status": "ok", "version": services.version}

    @application.get("/health")
    def health():
        return {"ok": True, "status": "ok", "version": services.version}

    @application.get("/status")
    def status():
        runtimes = [profile.model_dump(mode="json") for profile in services.runtime_registry.list_profiles()]
        return {
            "ok": True,
            "status": "ok",
            "version": services.version,
            "engines": runtimes,
            "runtimes": runtimes,
            "models": [model.model_dump(mode="json") for model in services.model_registry.list_models()],
        }

    @application.get("/version")
    def version():
        return {"version": services.version}

    @application.get("/ops/doctor")
    def ops_doctor():
        return services.doctor_report()

    @application.get("/ops/manifest", response_class=PlainTextResponse)
    def ops_manifest():
        return services.workspace_manifest()

    @application.get("/ops/brain")
    def ops_brain():
        return {
            "attached_models": services.brain.list_attached_models(),
            "core_execution": services.brain.core_summary(),
            "wrapper_surface": services.brain_ui_surface.state().model_dump(mode="json"),
            "promotions": services.brain_promotions.summary(),
            "logs": {
                "startup": str(services.paths.logs_dir / "startup.log"),
                "model_load": str(services.paths.logs_dir / "model_load.log"),
                "inference": str(services.paths.logs_dir / "inference.log"),
                "benchmark": str(services.paths.logs_dir / "benchmark.log"),
            },
        }

    @application.get("/ops/brain/canon")
    def ops_brain_canon():
        return services.brain_canon.status_payload()

    @application.get("/ops/brain/research-candidates")
    def ops_brain_research_candidates():
        return {
            "status": "registry_backed",
            "candidates": [candidate.model_dump(mode="json") for candidate in services.brain_canon.research_candidates()],
            "audit_log": services.brain_canon.assimilation_audit_log(),
            "license_summary": services.brain_canon.license_summary(),
        }

    @application.post("/ops/brain/research-candidates/{candidate_id}/status")
    def ops_brain_research_candidate_status(candidate_id: str, payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_canon.update_research_candidate(
                candidate_id=candidate_id,
                integration_status=payload.get("integration_status"),
                maturity=payload.get("maturity"),
                notes=payload.get("notes"),
                evidence=payload.get("evidence"),
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="research candidate not found") from exc

    @application.post("/ops/brain/research-candidates/{candidate_id}/license-review")
    def ops_brain_research_candidate_license_review(candidate_id: str, payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_canon.review_candidate_license(
                candidate_id=candidate_id,
                license_status=str(payload.get("license_status") or "requires_review"),
                reviewer=str(payload.get("reviewer") or "operator"),
                rationale=str(payload.get("rationale") or ""),
                evidence=str(payload.get("evidence") or ""),
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="research candidate not found") from exc

    @application.get("/ops/brain/research-candidates/{candidate_id}")
    def ops_brain_research_candidate(candidate_id: str):
        candidate = services.brain_canon.research_candidate(candidate_id)
        if candidate is None:
            raise HTTPException(status_code=404, detail="research candidate not found")
        return {"candidate": candidate.model_dump(mode="json")}

    @application.get("/ops/brain/product-status")
    def ops_brain_product_status():
        return {
            **services.brain_canon.product_status(),
            "ebt": services.brain_ebt.contract(),
            "evals": services.brain_trace_evals.summary(),
            "runtime": services.brain_product_runtime_profiles.summary(),
            "protocol_security": services.brain_protocol_security.summary(),
        }

    @application.get("/ops/brain/product-sweep/gates")
    def ops_brain_product_sweep_gates():
        return services.brain_product_sweep_gatekeeper.gate_payload()

    @application.get("/ops/brain/product-sweep/status")
    def ops_brain_product_sweep_status():
        payload = services.brain_product_sweep_gatekeeper.status_payload()
        payload["status_surfaces"]["archon_pi_assimilation"] = {
            "workflows": services.brain_workflows.summary(),
            "parallel_runs": services.brain_parallel_runs.summary(),
            "package_candidates": services.brain_package_candidates.summary(),
            "plan_reviews": services.brain_plan_review.summary(),
            "lifecycle_events": services.brain_lifecycle_events.summary(limit=50),
            "promotion_allowed": False,
            "external_package_execution_allowed": False,
        }
        payload["status_surfaces"]["assimilation_candidates"] = services.brain_assimilation.summary(limit=24)
        payload["status_surfaces"]["normalized_telemetry"] = services.brain_normalized_telemetry.compact_summary()
        payload["status_surfaces"]["eval_suites"] = services.brain_eval_suites.compact_summary()
        payload["status_surfaces"]["runtime_scorecards"] = services.brain_runtime_scorecards.compact_summary()
        payload["status_surfaces"]["adaptive_capabilities"] = services.brain_adaptive_capabilities.compact_summary()
        payload["status_surfaces"]["research_scout"] = services.brain_research_scout.compact_summary()
        payload["status_surfaces"]["self_improvement"] = services.brain_self_improvement.compact_summary()
        payload["status_surfaces"]["tier5_cloud_fallback"] = services.brain_tier5_fallback.compact_summary()
        payload["status_surfaces"]["context_graph"] = services.brain_context_graph.compact_summary()
        payload["status_surfaces"]["factory_orchestration"] = services.brain_factory_orchestration.compact_summary()
        payload["status_surfaces"]["execution_authority"] = services.brain_execution_authority.compact_summary()
        payload["status_surfaces"]["harness_engineering"] = services.brain_harness_engineering.compact_summary()
        payload["status_surfaces"]["autonomous_growth"] = services.brain_autonomous_growth.compact_summary()
        payload["status_surfaces"]["space_agent_assimilation"] = services.brain_assimilation.space_agent_compact_summary()
        payload["status_surfaces"]["protocol_capabilities"] = services.brain_protocol_capabilities.compact_summary()
        payload["status_surfaces"]["memory_governance"] = services.brain_memory_governance.summary()
        payload["status_surfaces"]["security_red_team"] = {
            "owasp_genai_top_10": "encoded_as_product_sweep_security_gate_family",
            "nist_ai_rmf_genai_profile": "encoded_as_product_sweep_security_gate_family",
            "red_team_pack_sources": ["garak", "promptfoo", "PyRIT", "NeMo Guardrails"],
            "runtime_provider_gate_required": True,
            "package_candidate_gate_required": True,
            "memory_write_gate_required": True,
            "autonomous_code_agent_gate_required": True,
            "execution_allowed": False,
            "mutation_allowed": False,
        }
        return payload

    @application.get("/ops/brain/protocol/adapters")
    def ops_brain_protocol_adapters():
        return services.brain_protocol_adapters.list_adapters()

    @application.get("/ops/brain/protocol/adapters/{adapter_id}")
    def ops_brain_protocol_adapter(adapter_id: str):
        adapter = services.brain_protocol_adapters.get_adapter(adapter_id)
        if adapter is None:
            raise HTTPException(status_code=404, detail="protocol adapter not found")
        return {"adapter": adapter.model_dump(mode="json")}

    @application.post("/ops/brain/protocol/adapters/{adapter_id}/policy")
    def ops_brain_protocol_adapter_policy(adapter_id: str, request: ProtocolAdapterPolicyRequest):
        if services.brain_protocol_adapters.get_adapter(adapter_id) is None:
            raise HTTPException(status_code=404, detail="protocol adapter not found")
        return services.brain_protocol_adapters.apply_policy(adapter_id, request)

    @application.get("/ops/brain/protocol/capabilities")
    def ops_brain_protocol_capabilities():
        return services.brain_protocol_capabilities.summary()

    @application.post("/ops/brain/product-sweep/shadow-simulation")
    def ops_brain_product_sweep_shadow_simulation(payload: dict[str, Any] = Body(...)):
        return services.brain_product_sweep_gatekeeper.shadow_simulation(
            name=str(payload.get("name") or "shadow-simulation"),
            target=str(payload.get("target") or "product-sweep"),
        )

    @application.get("/ops/brain/workflows")
    def ops_brain_workflows():
        return services.brain_workflows.summary()

    @application.get("/ops/brain/events")
    def ops_brain_events(event_type: str | None = None, subject_prefix: str | None = None, limit: int = 50):
        return services.brain_lifecycle_events.summary(event_type=event_type, subject_prefix=subject_prefix, limit=limit)

    @application.get("/ops/brain/telemetry/normalized")
    def ops_brain_telemetry_normalized(limit: int = 200):
        return services.brain_normalized_telemetry.summary(limit=limit)

    @application.get("/ops/brain/execution-authority")
    def ops_brain_execution_authority(limit: int = 100):
        return services.brain_execution_authority.summary(limit=limit)

    @application.get("/ops/brain/harness-engineering")
    def ops_brain_harness_engineering(limit: int = 100):
        return services.brain_harness_engineering.summary(limit=limit)

    @application.get("/ops/brain/growth-control")
    def ops_brain_growth_control(limit: int = 100):
        return services.brain_autonomous_growth.summary(limit=limit)

    @application.post("/ops/brain/growth-control/activate")
    def ops_brain_growth_control_activate(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_autonomous_growth.activate(
                wave_ids=[str(item) for item in (payload.get("wave_ids") or [])] or None,
                operator_goal=str(payload.get("operator_goal") or ""),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/growth-control/sandbox-manifests")
    def ops_brain_growth_control_sandbox_manifests(payload: dict[str, Any] = Body(...)):
        return services.brain_autonomous_growth.record_sandbox_manifest(
            workspace_ref=str(payload.get("workspace_ref") or "workspace"),
            manifest=dict(payload.get("manifest") or {}),
            sandbox_providers=[str(item) for item in (payload.get("sandbox_providers") or [])],
            requested_capabilities=[str(item) for item in (payload.get("requested_capabilities") or [])],
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/growth-control/security-boundaries/derive")
    def ops_brain_growth_control_security_boundaries_derive(payload: dict[str, Any] = Body(...)):
        return services.brain_autonomous_growth.derive_security_boundary(
            objective=str(payload.get("objective") or ""),
            tool_requests=[dict(item) for item in (payload.get("tool_requests") or [])],
            content_channels=[str(item) for item in (payload.get("content_channels") or [])],
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/growth-control/telemetry/export-plan")
    def ops_brain_growth_control_telemetry_export_plan(payload: dict[str, Any] = Body(...)):
        return services.brain_autonomous_growth.plan_trace_export(
            trace_ids=[str(item) for item in (payload.get("trace_ids") or [])],
            destination=str(payload.get("destination") or "local"),
            formats=[str(item) for item in (payload.get("formats") or [])],
            redaction_policy=dict(payload.get("redaction_policy") or {}),
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/growth-control/optimizer/shadow-run")
    def ops_brain_growth_control_optimizer_shadow_run(payload: dict[str, Any] = Body(...)):
        return services.brain_autonomous_growth.propose_shadow_optimizer(
            target_subsystem=str(payload.get("target_subsystem") or "workflows"),
            raw_trace_ids=[str(item) for item in (payload.get("raw_trace_ids") or [])],
            summary_trace_ids=[str(item) for item in (payload.get("summary_trace_ids") or [])],
            candidate_change=str(payload.get("candidate_change") or ""),
            transfer_models=[str(item) for item in (payload.get("transfer_models") or [])],
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/growth-control/evals/paired")
    def ops_brain_growth_control_evals_paired(payload: dict[str, Any] = Body(...)):
        return services.brain_autonomous_growth.record_paired_eval(
            subject=str(payload.get("subject") or "unknown-subject"),
            baseline=dict(payload.get("baseline") or {}),
            variant=dict(payload.get("variant") or {}),
            acceptance_criteria=dict(payload.get("acceptance_criteria") or {}),
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/growth-control/runtime-pack-certifications")
    def ops_brain_growth_control_runtime_pack_certifications(payload: dict[str, Any] = Body(...)):
        return services.brain_autonomous_growth.certify_runtime_pack(
            runtime_id=str(payload.get("runtime_id") or "unknown-runtime"),
            hardware_tier=str(payload.get("hardware_tier") or "tier_2_mainstream_local"),
            model_formats=[str(item) for item in (payload.get("model_formats") or [])],
            accelerators=[str(item) for item in (payload.get("accelerators") or [])],
            measurements=dict(payload.get("measurements") or {}),
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/growth-control/serving-scorecards")
    def ops_brain_growth_control_serving_scorecards(payload: dict[str, Any] = Body(...)):
        return services.brain_autonomous_growth.record_serving_scorecard(
            provider_id=str(payload.get("provider_id") or "unknown-provider"),
            features=dict(payload.get("features") or {}),
            measurements=dict(payload.get("measurements") or {}),
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/growth-control/protocol-trust/record")
    def ops_brain_growth_control_protocol_trust_record(payload: dict[str, Any] = Body(...)):
        return services.brain_autonomous_growth.record_protocol_trust(
            protocol_id=str(payload.get("protocol_id") or "unknown-protocol"),
            server_ref=str(payload.get("server_ref") or "unknown-server"),
            auth=dict(payload.get("auth") or {}),
            capability_manifest=dict(payload.get("capability_manifest") or {}),
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/growth-control/memory-hierarchy/record")
    def ops_brain_growth_control_memory_hierarchy_record(payload: dict[str, Any] = Body(...)):
        return services.brain_autonomous_growth.record_memory_hierarchy(
            agent_ref=str(payload.get("agent_ref") or "unknown-agent"),
            core_blocks=[dict(item) for item in (payload.get("core_blocks") or [])],
            archival_refs=[str(item) for item in (payload.get("archival_refs") or [])],
            shared_blocks=[dict(item) for item in (payload.get("shared_blocks") or [])],
            contradictions=[dict(item) for item in (payload.get("contradictions") or [])],
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/growth-control/research-evidence/ingest")
    def ops_brain_growth_control_research_evidence_ingest(payload: dict[str, Any] = Body(...)):
        return services.brain_autonomous_growth.ingest_research_evidence(
            source_name=str(payload.get("source_name") or "unknown-source"),
            source_url=str(payload.get("source_url") or ""),
            claim=str(payload.get("claim") or ""),
            citations=[dict(item) for item in (payload.get("citations") or [])],
            credibility=dict(payload.get("credibility") or {}),
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/harness-engineering/specs/register")
    def ops_brain_harness_engineering_specs_register(payload: dict[str, Any] = Body(...)):
        return services.brain_harness_engineering.register_spec(
            source=dict(payload.get("source") or {}),
            harness_name=str(payload.get("harness_name") or "nexus-harness"),
            target_subsystem=str(payload.get("target_subsystem") or "workflows"),
            layers=dict(payload.get("layers") or {}),
            execution_contracts=[dict(item) for item in (payload.get("execution_contracts") or [])],
            durable_state_paths=[str(item) for item in (payload.get("durable_state_paths") or [])],
            delegation_topology=str(payload.get("delegation_topology") or "orchestrator_workers"),
            module_inventory=[str(item) for item in (payload.get("module_inventory") or [])],
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/harness-engineering/ablations/record")
    def ops_brain_harness_engineering_ablations_record(payload: dict[str, Any] = Body(...)):
        return services.brain_harness_engineering.record_ablation(
            harness_id=str(payload.get("harness_id") or "unknown-harness"),
            benchmark=str(payload.get("benchmark") or "unknown-benchmark"),
            baseline=dict(payload.get("baseline") or {}),
            variant=dict(payload.get("variant") or {}),
            module_findings=[dict(item) for item in (payload.get("module_findings") or [])],
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/harness-engineering/optimization/propose")
    def ops_brain_harness_engineering_optimization_propose(payload: dict[str, Any] = Body(...)):
        return services.brain_harness_engineering.propose_optimization(
            source=dict(payload.get("source") or {}),
            target_harness_id=str(payload.get("target_harness_id") or "unknown-harness"),
            failure_trace_ids=[str(item) for item in (payload.get("failure_trace_ids") or [])],
            summary_trace_ids=[str(item) for item in (payload.get("summary_trace_ids") or [])],
            proposed_change_summary=str(payload.get("proposed_change_summary") or ""),
            candidate_changes=[str(item) for item in (payload.get("candidate_changes") or [])],
            transfer_eval_models=[str(item) for item in (payload.get("transfer_eval_models") or [])],
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/harness-engineering/safety-rules/record")
    def ops_brain_harness_engineering_safety_rules_record(payload: dict[str, Any] = Body(...)):
        return services.brain_harness_engineering.record_safety_rule(
            source=dict(payload.get("source") or {}),
            rule_id=str(payload.get("rule_id") or "unnamed-rule"),
            phase=str(payload.get("phase") or "action_execution"),
            trigger=str(payload.get("trigger") or "tool.requested"),
            predicate=str(payload.get("predicate") or "false"),
            enforcement=str(payload.get("enforcement") or "deny"),
            defense_layers=[str(item) for item in (payload.get("defense_layers") or [])],
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/execution-authority/leases/request")
    def ops_brain_execution_authority_leases_request(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_execution_authority.request_lease(
                capability=str(payload["capability"]),
                scope=dict(payload.get("scope") or {}),
                expires_at=payload.get("expires_at"),
                budget=dict(payload.get("budget") or {}),
                rollback_plan=dict(payload.get("rollback_plan") or {}),
                approval_id=payload.get("approval_id"),
                approval_decision=str(payload.get("approval_decision") or "not_requested"),
                gateway_decision=str(payload.get("gateway_decision") or "hold"),
                product_sweep_gate_ids=[str(item) for item in (payload.get("product_sweep_gate_ids") or [])],
                product_sweep_decision=str(payload.get("product_sweep_decision") or "not_evaluated"),
                evidence=dict(payload.get("evidence") or {}),
                requested_execution=bool(payload.get("requested_execution", True)),
                requested_mutation=bool(payload.get("requested_mutation", False)),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/execution-authority/evaluate")
    def ops_brain_execution_authority_evaluate(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_execution_authority.evaluate(
                lease_id=str(payload["lease_id"]),
                capability=str(payload["capability"]),
                scope=dict(payload.get("scope") or {}),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="execution lease not found") from exc

    @application.get("/ops/brain/context-graph")
    def ops_brain_context_graph(limit: int = 100):
        return services.brain_context_graph.summary(limit=limit)

    @application.post("/ops/brain/context-graph/index-plan")
    def ops_brain_context_graph_index_plan(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_context_graph.plan_index(
                source=dict(payload.get("source") or {}),
                corpus_root=str(payload.get("corpus_root") or services.paths.project_root),
                content_kinds=[str(item) for item in (payload.get("content_kinds") or ["code", "docs"])],
                assistant_platforms=[str(item) for item in (payload.get("assistant_platforms") or ["codex"])],
                graph_ignore_patterns=[str(item) for item in (payload.get("graph_ignore_patterns") or [])],
                changed_files=[str(item) for item in (payload.get("changed_files") or [])],
                update_mode=str(payload.get("update_mode") or "full"),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/context-graph/query")
    def ops_brain_context_graph_query(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_context_graph.query(
                graph_record_id=str(payload["graph_record_id"]),
                question=str(payload["question"]),
                mode=str(payload.get("mode") or "query"),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=f"missing required field: {exc.args[0]}") from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.get("/ops/brain/factory-orchestration")
    def ops_brain_factory_orchestration(limit: int = 100):
        return services.brain_factory_orchestration.summary(limit=limit)

    @application.post("/ops/brain/factory-orchestration/triage")
    def ops_brain_factory_orchestration_triage(payload: dict[str, Any] = Body(...)):
        return services.brain_factory_orchestration.triage_batch(
            source=dict(payload.get("source") or {}),
            issues=[dict(item) for item in (payload.get("issues") or [])],
            cadence=str(payload.get("cadence") or "scheduled_batch"),
            max_parallel=int(payload.get("max_parallel") or 1),
            priority_rules=dict(payload.get("priority_rules") or {}),
            protected_paths=[str(item) for item in (payload.get("protected_paths") or [])],
            token_budget=dict(payload.get("token_budget") or {}),
            linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
        )

    @application.post("/ops/brain/factory-orchestration/reproduction-check")
    def ops_brain_factory_orchestration_reproduction_check(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_factory_orchestration.reproduction_check(
                issue_ref=str(payload["issue_ref"]),
                reproduction_surface=str(payload.get("reproduction_surface") or "cli"),
                required_tools=[str(item) for item in (payload.get("required_tools") or [])],
                comment_policy=str(payload.get("comment_policy") or "draft_evidence_only"),
                e2e_required=bool(payload.get("e2e_required", True)),
                static_analysis_only=bool(payload.get("static_analysis_only", False)),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=f"missing required field: {exc.args[0]}") from exc

    @application.post("/ops/brain/factory-orchestration/pr-validation")
    def ops_brain_factory_orchestration_pr_validation(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_factory_orchestration.pr_validation(
                pr_ref=str(payload["pr_ref"]),
                required_validation_profiles=[str(item) for item in (payload.get("required_validation_profiles") or [])],
                browser_validation_required=bool(payload.get("browser_validation_required", False)),
                start_service_status=str(payload.get("start_service_status") or "not_started"),
                deployment_target=payload.get("deployment_target"),
                merge_policy=payload.get("merge_policy"),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=f"missing required field: {exc.args[0]}") from exc

    @application.get("/ops/brain/adaptive-capabilities")
    def ops_brain_adaptive_capabilities():
        return services.brain_adaptive_capabilities.summary()

    @application.post("/ops/brain/adaptive-capabilities/profile")
    def ops_brain_adaptive_capabilities_profile(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_adaptive_capabilities.profile(
                capability_family=str(payload.get("capability_family") or "inference"),
                source=dict(payload.get("source") or {}),
                hardware_profile=dict(payload.get("hardware_profile") or {}),
                target_subsystem=payload.get("target_subsystem"),
                requested_tier=payload.get("requested_tier"),
                privacy_posture=payload.get("privacy_posture"),
                cost_posture=payload.get("cost_posture"),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.get("/ops/brain/adaptive-capabilities/scorecards")
    def ops_brain_adaptive_capabilities_scorecards():
        return services.brain_adaptive_capabilities.scorecards()

    @application.post("/ops/brain/adaptive-capabilities/route")
    def ops_brain_adaptive_capabilities_route(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_adaptive_capabilities.route(
                capability_family=str(payload.get("capability_family") or "inference"),
                source=dict(payload.get("source") or {}),
                hardware_profile=dict(payload.get("hardware_profile") or {}),
                target_subsystem=payload.get("target_subsystem"),
                allow_cloud_fallback=bool(payload.get("allow_cloud_fallback", False)),
                local_satisfies_policy=bool(payload.get("local_satisfies_policy", True)),
                fallback_reason=payload.get("fallback_reason"),
                privacy_posture=payload.get("privacy_posture"),
                cost_posture=payload.get("cost_posture"),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.get("/ops/brain/research-scout/candidates")
    def ops_brain_research_scout_candidates():
        return services.brain_research_scout.summary()

    @application.post("/ops/brain/research-scout/ingest")
    def ops_brain_research_scout_ingest(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_research_scout.ingest(
                source_type=str(payload["source_type"]),
                source_name=str(payload["source_name"]),
                source_url=str(payload["source_url"]),
                claimed_capability=str(payload.get("claimed_capability") or ""),
                capability_family=str(payload.get("capability_family") or "research"),
                hardware_tier_fit=[str(item) for item in (payload.get("hardware_tier_fit") or [])] or None,
                license_posture=str(payload.get("license_posture") or "requires_review"),
                risk_flags=[str(item) for item in (payload.get("risk_flags") or [])],
                dependency_posture=str(payload.get("dependency_posture") or "candidate_only"),
                confidence=float(payload.get("confidence", 0.5)),
                required_eval_suite=str(payload.get("required_eval_suite") or "regression_behavior"),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/research-scout/run")
    def ops_brain_research_scout_run(payload: dict[str, Any] = Body(default={})):
        try:
            return services.brain_research_scout.run(
                query=str(payload.get("query") or "capability updates"),
                source_types=[str(item) for item in (payload.get("source_types") or [])] or None,
                live_fetch=bool(payload.get("live_fetch", False)),
                max_candidates_per_source=int(payload.get("max_candidates_per_source") or 3),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.get("/ops/brain/self-improvement/proposals")
    def ops_brain_self_improvement_proposals():
        return services.brain_self_improvement.summary()

    @application.post("/ops/brain/self-improvement/propose")
    def ops_brain_self_improvement_propose(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_self_improvement.propose(
                category=str(payload["category"]),
                target_subsystem=str(payload.get("target_subsystem") or "workflow"),
                proposed_change_summary=str(payload.get("proposed_change_summary") or ""),
                evidence_links=[str(item) for item in (payload.get("evidence_links") or [])],
                eval_suite_id=str(payload.get("eval_suite_id") or "regression_behavior"),
                rollback_requirement=str(payload.get("rollback_requirement") or "restore_previous_governed_artifact"),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/self-improvement/validate")
    def ops_brain_self_improvement_validate(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_self_improvement.validate(
                proposal_id=str(payload["proposal_id"]),
                eval_status=str(payload.get("eval_status") or "blocked"),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="self-improvement proposal not found") from exc

    @application.post("/ops/brain/self-improvement/mine")
    def ops_brain_self_improvement_mine(payload: dict[str, Any] = Body(default={})):
        return services.brain_self_improvement.mine(
            source_limit=int(payload.get("source_limit") or 100),
            max_proposals=int(payload.get("max_proposals") or 8),
            include_product_sweep=bool(payload.get("include_product_sweep", True)),
        )

    @application.post("/ops/brain/tier5/fallback/evaluate")
    def ops_brain_tier5_fallback_evaluate(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_tier5_fallback.evaluate(
                provider_id=str(payload.get("provider_id") or "tier5-cloud-router"),
                fallback_reason=str(payload.get("fallback_reason") or ""),
                privacy_posture=payload.get("privacy_posture"),
                cost_posture=payload.get("cost_posture"),
                approval_decision=str(payload.get("approval_decision") or "not_requested"),
                gateway_decision=str(payload.get("gateway_decision") or "hold"),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/workflows/execute")
    def ops_brain_workflows_execute(
        workflow_id: str = Body(...),
        trigger_source: str = Body(default="manual"),
        workspace_id: str = Body(default="default"),
        agent_id: str = Body(default="standard-wrapper-agent"),
        parameter_set: dict | None = Body(default=None),
        linked_trace_ids: list[str] | None = Body(default=None),
        requested_tools: list[str] | None = Body(default=None),
        requested_extensions: list[str] | None = Body(default=None),
        approval_path: dict | None = Body(default=None),
        status: str | None = Body(default=None),
    ):
        try:
            return services.brain_workflows.execute(
                workflow_id=workflow_id,
                trigger_source=trigger_source,
                workspace_id=workspace_id,
                agent_id=agent_id,
                parameter_set=parameter_set or {},
                linked_trace_ids=linked_trace_ids or [],
                requested_tools=requested_tools or [],
                requested_extensions=requested_extensions or [],
                approval_path=approval_path or {},
                status=status,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="workflow not found") from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.get("/ops/brain/workflows/history")
    def ops_brain_workflows_history(
        workflow_id: str | None = None,
        trigger_source: str | None = None,
        status: str | None = None,
        limit: int = 20,
    ):
        return services.brain_workflows.history(
            workflow_id=workflow_id,
            trigger_source=trigger_source,
            status=status,
            limit=limit,
        )

    @application.get("/ops/brain/parallel-runs")
    def ops_brain_parallel_runs(source_type: str | None = None, status: str | None = None, limit: int = 50):
        return services.brain_parallel_runs.summary(source_type=source_type, status=status, limit=limit)

    @application.post("/ops/brain/parallel-runs/prepare")
    def ops_brain_parallel_runs_prepare(
        source_type: str = Body(...),
        source_ref: str = Body(...),
        base_branch: str = Body(default="main"),
        workspace_id: str = Body(default="default"),
        agent_id: str = Body(default="standard-wrapper-agent"),
        database_mode: str = Body(default="none"),
        requested_tools: list[str] | None = Body(default=None),
        requested_extensions: list[str] | None = Body(default=None),
        validation_profile: str = Body(default="python-fast"),
        linked_trace_ids: list[str] | None = Body(default=None),
    ):
        try:
            return services.brain_parallel_runs.prepare(
                source_type=source_type,
                source_ref=source_ref,
                base_branch=base_branch,
                workspace_id=workspace_id,
                agent_id=agent_id,
                database_mode=database_mode,
                requested_tools=requested_tools or [],
                requested_extensions=requested_extensions or [],
                validation_profile=validation_profile,
                linked_trace_ids=linked_trace_ids or [],
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.get("/ops/brain/parallel-runs/history")
    def ops_brain_parallel_runs_history(source_type: str | None = None, status: str | None = None, limit: int = 50):
        return services.brain_parallel_runs.history(source_type=source_type, status=status, limit=limit)

    @application.post("/ops/brain/parallel-runs/{run_id}/review")
    def ops_brain_parallel_runs_review(
        run_id: str,
        lane: str = Body(...),
        decision: str = Body(...),
        reviewer: str = Body(default="operator"),
        findings: list[dict] | None = Body(default=None),
        linked_trace_ids: list[str] | None = Body(default=None),
    ):
        try:
            return services.brain_parallel_runs.review(
                run_id=run_id,
                lane=lane,
                decision=decision,
                reviewer=reviewer,
                findings=findings or [],
                linked_trace_ids=linked_trace_ids or [],
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="parallel run not found") from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/parallel-runs/{run_id}/self-healing-report")
    def ops_brain_parallel_runs_self_healing_report(
        run_id: str,
        signals: list[dict] = Body(...),
        linked_trace_ids: list[str] | None = Body(default=None),
    ):
        try:
            return services.brain_parallel_runs.self_healing_report(
                run_id=run_id,
                signals=signals,
                linked_trace_ids=linked_trace_ids or [],
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="parallel run not found") from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.get("/ops/brain/package-candidates")
    def ops_brain_package_candidates(workspace_id: str | None = None, limit: int = 50):
        return services.brain_package_candidates.summary(workspace_id=workspace_id, limit=limit)

    @application.post("/ops/brain/package-candidates/ingest")
    def ops_brain_package_candidates_ingest(
        source_type: str = Body(...),
        source_ref: str = Body(...),
        workspace_id: str = Body(default="default"),
        manifest: dict | None = Body(default=None),
        metadata: dict | None = Body(default=None),
    ):
        return services.brain_package_candidates.ingest(
            source_type=source_type,
            source_ref=source_ref,
            workspace_id=workspace_id,
            manifest=manifest or {},
            metadata=metadata or {},
        )

    @application.get("/ops/brain/plans")
    def ops_brain_plans(limit: int = 50):
        return services.brain_plan_review.summary(limit=limit)

    @application.post("/ops/brain/plans/review")
    def ops_brain_plans_review(
        title: str = Body(...),
        content: str = Body(...),
        decision: str = Body(...),
        plan_id: str | None = Body(default=None),
        reviewer: str = Body(default="operator"),
        annotations: list[dict] | None = Body(default=None),
        linked_workflow_id: str | None = Body(default=None),
    ):
        return services.brain_plan_review.review(
            plan_id=plan_id,
            title=title,
            content=content,
            decision=decision,
            reviewer=reviewer,
            annotations=annotations or [],
            linked_workflow_id=linked_workflow_id,
        )

    @application.get("/ops/brain/memory-os")
    def ops_brain_memory_os():
        return services.brain_memory_os.summarize()

    @application.post("/ops/brain/memory-os/proposals")
    def ops_brain_memory_os_proposals(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_memory_governance.propose(
                fact_id=str(payload["fact_id"]),
                content=str(payload["content"]),
                source=str(payload["source"]),
                operation=str(payload.get("operation") or "store"),
                evidence=dict(payload.get("evidence") or {}),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/memory-os/store")
    def ops_brain_memory_os_store(payload: dict[str, Any] = Body(...)):
        record = services.brain_memory_os.store(
            fact_id=str(payload["fact_id"]),
            content=str(payload["content"]),
            source=str(payload["source"]),
            evidence=dict(payload.get("evidence") or {}),
            effective_at=_parse_optional_datetime(payload.get("effective_at")),
        )
        return record.model_dump(mode="json")

    @application.post("/ops/brain/memory-os/update")
    def ops_brain_memory_os_update(payload: dict[str, Any] = Body(...)):
        record = services.brain_memory_os.update(
            fact_id=str(payload["fact_id"]),
            content=str(payload["content"]),
            source=str(payload["source"]),
            evidence=dict(payload.get("evidence") or {}),
            effective_at=_parse_optional_datetime(payload.get("effective_at")),
        )
        return record.model_dump(mode="json")

    @application.get("/ops/brain/memory-os/retrieve/{fact_id}")
    def ops_brain_memory_os_retrieve(
        fact_id: str,
        as_of: str | None = None,
        include_archived: bool = False,
        include_discarded: bool = False,
    ):
        record = services.brain_memory_os.retrieve(
            fact_id,
            as_of=_parse_optional_datetime(as_of),
            include_archived=include_archived,
            include_discarded=include_discarded,
        )
        if record is None:
            raise HTTPException(status_code=404, detail="memory fact not found")
        return record.model_dump(mode="json")

    @application.post("/ops/brain/memory-os/archive/{fact_id}")
    def ops_brain_memory_os_archive(fact_id: str):
        record = services.brain_memory_os.archive(fact_id)
        if record is None:
            raise HTTPException(status_code=404, detail="memory fact not found")
        return record.model_dump(mode="json")

    @application.post("/ops/brain/memory-os/discard/{fact_id}")
    def ops_brain_memory_os_discard(fact_id: str):
        record = services.brain_memory_os.discard(fact_id)
        if record is None:
            raise HTTPException(status_code=404, detail="memory fact not found")
        return record.model_dump(mode="json")

    @application.get("/ops/brain/memory-os/dereference/{memory_id}")
    def ops_brain_memory_os_dereference(memory_id: str):
        try:
            return services.brain_memory_os.dereference(memory_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="memory record not found") from exc

    @application.get("/ops/brain/memory-os/provenance/{fact_id}")
    def ops_brain_memory_os_provenance(fact_id: str):
        return services.brain_memory_os.provenance_lookup(fact_id)

    @application.post("/ops/brain/security/protocol/evaluate")
    def ops_brain_security_protocol_evaluate(attempt: ToolAttempt):
        decision = services.brain_protocol_security.evaluate(attempt)
        return decision.model_dump(mode="json")

    @application.post("/ops/brain/security/protocol/servers")
    def ops_brain_security_protocol_register_server(definition: ProtocolServerDefinition):
        return services.brain_protocol_security.register_server(definition)

    @application.get("/ops/brain/security/protocol/servers")
    def ops_brain_security_protocol_servers():
        return {
            "servers": services.brain_protocol_security.servers(),
            "summary": services.brain_protocol_security.summary(),
        }

    @application.post("/ops/brain/security/protocol/consent")
    def ops_brain_security_protocol_consent(request: ProtocolConsentRequest):
        decision = services.brain_protocol_security.consent(request)
        return decision.model_dump(mode="json")

    @application.get("/ops/brain/security/protocol/audit")
    def ops_brain_security_protocol_audit():
        events = services.brain_protocol_security.audit_log()
        return {
            "audit_event_count": len(events),
            "events": events,
            "summary": services.brain_protocol_security.summary(),
        }

    @application.get("/ops/brain/ebt/contract")
    def ops_brain_ebt_contract():
        return services.brain_ebt.contract()

    @application.post("/ops/brain/ebt/score")
    def ops_brain_ebt_score(request: EBTScoreRequest):
        return services.brain_ebt.score(request)

    @application.get("/ops/brain/evals/scenarios")
    def ops_brain_eval_scenarios():
        return services.brain_trace_evals.summary()

    @application.get("/ops/brain/evals/suites")
    def ops_brain_eval_suites():
        return services.brain_eval_suites.summary()

    @application.post("/ops/brain/evals/run")
    def ops_brain_eval_run(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_eval_suites.run(
                suite_type=str(payload["suite_type"]),
                subject=str(payload.get("subject") or "operator-request"),
                linked_trace_ids=[str(item) for item in (payload.get("linked_trace_ids") or [])],
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/expert-council/deliberate")
    def ops_brain_expert_council_deliberate(payload: dict[str, Any] = Body(...)):
        decision = services.brain_expert_council.deliberate(
            prompt=str(payload.get("prompt") or ""),
            selected_experts=[str(expert) for expert in payload.get("selected_experts", [])],
        )
        return decision.model_dump(mode="json")

    @application.post("/ops/brain/runtime/context-assembly")
    def ops_brain_runtime_context_assembly(payload: dict[str, Any] = Body(...)):
        return services.brain_product_runtime_profiles.assemble_context(
            profile=str(payload.get("profile") or "local"),
            target_tokens=int(payload.get("target_tokens") or 8192),
            requested_adapter=payload.get("requested_adapter"),
            task_type=str(payload.get("task_type") or "general"),
        )

    @application.get("/ops/brain/runtime/scorecards")
    def ops_brain_runtime_scorecards():
        return services.brain_runtime_scorecards.summary()

    @application.post("/ops/brain/runtime/scorecards/evaluate")
    def ops_brain_runtime_scorecards_evaluate(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_runtime_scorecards.evaluate(
                provider_id=str(payload["provider_id"]),
                endpoint_url=payload.get("endpoint_url"),
                model_hint=payload.get("model_hint"),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/training/export-record")
    def ops_brain_training_export_record(record: TrainingDataExportRecord):
        payload = record.export_payload()
        return {
            **payload,
            "real_training_status": "gated",
            "promotion_gate": "canon_traces_evals_memory_provenance_licenses_security",
        }

    @application.post("/ops/brain/training/export-dataset")
    def ops_brain_training_export_dataset(payload: dict[str, Any] = Body(...)):
        records = [TrainingDataExportRecord.model_validate(record) for record in payload.get("records", [])]
        return services.brain_training_exporter.export_dataset(
            name=str(payload.get("name") or "training-dataset"),
            records=records,
        )

    @application.post("/ops/brain/training/reward-spec")
    def ops_brain_training_reward_spec(payload: dict[str, Any] = Body(...)):
        return services.brain_training_exporter.export_reward_spec(
            name=str(payload.get("name") or "reward-spec"),
            objectives=[str(item) for item in payload.get("objectives", [])],
            metrics=dict(payload.get("metrics") or {}),
            safety_constraints=[str(item) for item in payload.get("safety_constraints", [])],
            provenance=[dict(item) for item in payload.get("provenance", [])],
        )

    @application.post("/ops/brain/training/eval-report")
    def ops_brain_training_eval_report(payload: dict[str, Any] = Body(...)):
        return services.brain_training_exporter.export_eval_report(
            name=str(payload.get("name") or "eval-report"),
            dataset_artifact_path=str(payload.get("dataset_artifact_path") or ""),
            reward_spec_path=payload.get("reward_spec_path"),
            scenario_ids=[str(item) for item in payload.get("scenario_ids", [])],
            results=dict(payload.get("results") or {}),
            license_status=str(payload.get("license_status") or "not_reviewed"),
            security_gate_status=str(payload.get("security_gate_status") or "not_run"),
        )

    @application.get("/ops/brain/training/artifacts")
    def ops_brain_training_artifacts():
        return services.brain_training_exporter.list_artifacts()

    @application.get("/ops/brain/core")
    def ops_brain_core(
        model_hint: str | None = None,
        expert: str | None = None,
        session_id: str | None = None,
        trace_id: str | None = None,
    ):
        return services.brain.core_summary(
            model_hint=model_hint,
            expert=expert,
            session_id=session_id,
            trace_id=trace_id,
        )

    @application.post("/ops/brain/core/wake")
    def ops_brain_core_wake():
        state = services.nexusnet_core.wake()
        return {
            "status": "ok",
            "awake": bool(state.get("awake")),
            "core_state": state,
            "hardware_profile": state.get("hardware_scan", {}),
            "adaptive_config": state.get("adaptive_runtime_config", {}),
            "trace": state.get("trace_event", {}),
        }

    @application.post("/ops/brain/core/attach")
    def ops_brain_core_attach(request: CoreModelAttachRequest):
        metadata = {
            **dict(request.metadata or {}),
            **({"model_ref": request.model_ref} if request.model_ref else {}),
            **({"tokenizer_ref": request.tokenizer_ref} if request.tokenizer_ref else {}),
        }
        if request.model_ref and not metadata.get("model_id"):
            metadata["model_id"] = request.model_ref
        if request.mode == "mock" and not request.allow_mock:
            trace = services.nexusnet_core.trace_logger.write(
                event="base_model.attach.blocked",
                component="NexusNetCore",
                status="error",
                metadata={
                    "mode": "mock",
                    "is_mock": True,
                    "product_evidence": False,
                    "model_id": metadata.get("model_id") or request.model_ref,
                    "blocked_reason": "mock-attach-disabled",
                },
                error="Mock attach requires allow_mock=true.",
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "mock-attach-disabled",
                    "message": "Mock core attach requires allow_mock=true.",
                    "attached": False,
                    "trace": trace,
                },
            )

        compatibility_plan = None
        should_plan = (
            request.mode == "product"
            or request.plan_only
            or request.router_hidden_dim is not None
            or request.expert_hidden_dim is not None
        )
        if should_plan:
            compatibility_plan = services.nexusnet_core.compatibility_planner.plan(
                metadata=metadata,
                router_hidden_dim=request.router_hidden_dim,
                expert_hidden_dim=request.expert_hidden_dim,
                strict_product_mode=request.strict_product_mode and request.mode == "product",
            )
        plan_payload = compatibility_plan.model_dump(mode="json") if compatibility_plan is not None else {}

        if request.plan_only:
            trace = services.nexusnet_core.trace_logger.write(
                event="base_model.attach.plan",
                component="NexusNetCore",
                status="ok",
                metadata={
                    "mode": request.mode,
                    "is_mock": request.mode == "mock",
                    "product_evidence": False,
                    "model_id": metadata.get("model_id") or request.model_ref,
                    "compatibility_status": plan_payload.get("status"),
                    "compatibility_plan_id": plan_payload.get("compatibility_plan_id"),
                },
            )
            return {
                "status": "ok",
                "attached": False,
                "mode": request.mode,
                "plan_only": True,
                "attachment": None,
                "compatibility_plan": plan_payload,
                "trace": trace,
            }

        if (
            request.mode == "product"
            and request.strict_product_mode
            and compatibility_plan is not None
            and compatibility_plan.status not in {CompatibilityStatus.COMPATIBLE, CompatibilityStatus.ADAPTER_REQUIRED}
        ):
            trace = services.nexusnet_core.trace_logger.write(
                event="base_model.attach.blocked",
                component="NexusNetCore",
                status="error",
                metadata={
                    "mode": "product",
                    "is_mock": False,
                    "product_evidence": False,
                    "model_id": metadata.get("model_id") or request.model_ref,
                    "compatibility_status": plan_payload.get("status"),
                    "compatibility_plan_id": plan_payload.get("compatibility_plan_id"),
                    "blocked_reason": "product-compatibility-validation-failed",
                },
                error="Product-mode attach failed compatibility validation.",
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "product-compatibility-validation-failed",
                    "message": "Product-mode base-model attachment requires COMPATIBLE or ADAPTER_REQUIRED compatibility status.",
                    "attached": False,
                    "compatibility_plan": plan_payload,
                    "trace": trace,
                },
            )

        attachment = services.nexusnet_core.attach_base_model(
            metadata=metadata,
            model_hint=None,
            role=request.role,
            mode=request.mode,
            compatibility_plan=compatibility_plan,
            product_evidence=(
                request.mode == "product"
                and compatibility_plan is not None
                and compatibility_plan.status in {CompatibilityStatus.COMPATIBLE, CompatibilityStatus.ADAPTER_REQUIRED}
            ),
        )
        return {
            "status": "ok",
            "attached": True,
            "mode": request.mode,
            "attachment": attachment,
            "compatibility_plan": plan_payload,
            "trace": attachment.get("trace_event", {}),
        }

    @application.get("/ops/brain/core/trace")
    def ops_brain_core_trace(
        limit: int = 50,
        component: str | None = None,
        event: str | None = None,
        status: str | None = None,
        include_mock_traces: bool = False,
    ):
        events = services.nexusnet_core.trace_logger.read(
            limit=limit,
            component=component,
            event=event,
            status=status,
            include_mock_traces=include_mock_traces,
        )
        return {
            "status": "ok",
            "count": len(events),
            "events": events,
        }

    @application.get("/ops/brain/wrapper-surface")
    def ops_brain_wrapper_surface(session_id: str | None = None):
        return services.brain_ui_surface.snapshot(session_id=session_id)

    @application.get("/ops/brain/visualizer/state")
    def ops_brain_visualizer_state(session_id: str | None = None):
        return services.brain_visualizer.state(session_id=session_id)

    @application.get("/ops/brain/operations")
    def ops_brain_operations(session_id: str | None = None, limit: int = 25):
        return services.brain_operations.summary(session_id=session_id, limit=limit)

    @application.post("/ops/brain/operations/commands")
    def ops_brain_operations_commands(
        command_text: str = Body(...),
        session_id: str | None = Body(default=None),
        priority: str = Body(default="normal"),
        target_surface: str = Body(default="mission-control-cockpit"),
        context: dict[str, Any] | None = Body(default=None),
    ):
        return services.brain_operations.issue_command(
            session_id=session_id,
            command_text=command_text,
            priority=priority,
            target_surface=target_surface,
            context=context,
        )

    @application.post("/ops/brain/operations/commands/{command_id}/events")
    def ops_brain_operations_command_events(
        command_id: str,
        event_type: str = Body(...),
        actor: str = Body(...),
        detail: str = Body(...),
        session_id: str | None = Body(default=None),
        lifecycle_state: str | None = Body(default=None),
        signal_type: str | None = Body(default=None),
        state: str = Body(default="live_state"),
        metadata: dict[str, Any] | None = Body(default=None),
    ):
        try:
            return services.brain_operations.record_event(
                command_id=command_id,
                session_id=session_id,
                event_type=event_type,
                actor=actor,
                detail=detail,
                lifecycle_state=lifecycle_state,
                signal_type=signal_type,
                state=state,
                metadata=metadata,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown brain operation command: {command_id}") from exc

    @application.get("/ops/brain/canon/realization")
    def ops_brain_canon_realization(session_id: str | None = None):
        return services.brain_visualizer.canon_realization(session_id=session_id)

    @application.get("/ops/brain/canon/completion")
    def ops_brain_canon_completion(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return completion_assessment(realization)

    @application.get("/ops/brain/canon/runtime-scorecard")
    def ops_brain_canon_runtime_scorecard(session_id: str | None = None, model_hint: str | None = None):
        control_panel = services.brain_visualizer.state(session_id=session_id)["overlay_state"]["control_panel"]
        return runtime_quantization_scorecard(
            control_panel=control_panel,
            backend_summary=services.brain_runtime_registry.summary(model_hint),
        )

    @application.get("/ops/brain/canon/evolution-dossier")
    def ops_brain_canon_evolution_dossier(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return autonomous_evolution_dossier(realization)

    @application.post("/ops/brain/self-improvement/events")
    def ops_brain_self_improvement_events(payload: dict[str, Any] = Body(...)):
        event = ImprovementEvent.model_validate(payload)
        decision = triage_improvement_event(event)
        item = _self_improvement_queue().propose(
            event,
            decision=decision,
            actor="NexusBrain",
            reason="self-improvement event accepted through NexusBrain API",
        )
        return {
            "status_label": "LOCKED CANON",
            "event": event.model_dump(mode="json"),
            "decision": decision.model_dump(mode="json"),
            "queue_item": item.model_dump(mode="json"),
        }

    @application.post("/ops/brain/self-improvement/capture")
    def ops_brain_self_improvement_capture(payload: dict[str, Any] = Body(...)):
        event = ExperienceCapture().capture(**payload)
        decision = triage_improvement_event(event)
        item = _self_improvement_queue().propose(
            event,
            decision=decision,
            actor="NexusBrain",
            reason="raw interaction trace captured through NexusBrain API",
        )
        return {
            "status_label": "LOCKED CANON",
            "event": event.model_dump(mode="json"),
            "decision": decision.model_dump(mode="json"),
            "queue_item": item.model_dump(mode="json"),
            "review": _self_improvement_review_payload(item.queue_id),
        }

    @application.get("/ops/brain/self-improvement/queue")
    def ops_brain_self_improvement_queue(status: str | None = None):
        summary = _self_improvement_queue_summary()
        if status:
            summary["items"] = [item for item in summary["items"] if item.get("status") == status]
            summary["item_count"] = len(summary["items"])
            summary["status_counts"] = {status: summary["item_count"]} if summary["item_count"] else {}
        return summary

    @application.get("/ops/brain/self-improvement/queue/{queue_id}/review")
    def ops_brain_self_improvement_queue_review(queue_id: str, operator_approved: bool = False):
        return _self_improvement_review_payload(queue_id, operator_approved=operator_approved)

    @application.get("/ops/brain/canon/self-improvement")
    def ops_brain_canon_self_improvement(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return self_improvement_scorecard(realization, queue_summary=_self_improvement_queue_summary())

    @application.get("/ops/brain/canon/developmental-cortex")
    def ops_brain_canon_developmental_cortex():
        return services.brain_developmental_cortex.scorecard()

    @application.post("/ops/brain/developmental-cortex/assess")
    def ops_brain_developmental_cortex_assess(payload: dict[str, Any] = Body(...)):
        return services.brain_developmental_cortex.assess(payload)

    @application.get("/ops/brain/canon/authority-spine")
    def ops_brain_canon_authority_spine():
        return services.brain_authority_spine.summary()

    @application.post("/ops/brain/authority-spine/decisions")
    def ops_brain_authority_spine_decisions(payload: dict[str, Any] = Body(...)):
        return services.brain_authority_spine.evaluate(
            action_id=str(payload["action_id"]),
            actor_ref=str(payload.get("actor_ref") or "operator"),
            effect_type=str(payload["effect_type"]),
            capability_refs=list(payload.get("capability_refs") or []),
            sandbox_state=str(payload.get("sandbox_state") or "none"),
            operator_approved=bool(payload.get("operator_approved")),
            evidence_refs=list(payload.get("evidence_refs") or []),
        )

    @application.get("/ops/brain/canon/evidence-store")
    def ops_brain_canon_evidence_store():
        return services.brain_evidence_store.projection()

    @application.get("/ops/brain/canon/eval-federation")
    def ops_brain_canon_eval_federation():
        return services.brain_eval_federation.summary()

    @application.get("/ops/brain/canon/tool-action-harness")
    def ops_brain_canon_tool_action_harness():
        return services.brain_tool_action_harness.summary()

    @application.get("/ops/brain/canon/runtime-decision-ledger")
    def ops_brain_canon_runtime_decision_ledger():
        return services.brain_runtime_decision_ledger.summary()

    @application.get("/ops/brain/canon/assimilation-target-catalog")
    def ops_brain_canon_assimilation_target_catalog():
        return services.brain_assimilation_catalog.summary()

    @application.get("/ops/brain/canon/hive-neural-snapshot")
    def ops_brain_canon_hive_neural_snapshot():
        """Read-only shadow evidence: one composed pass through the real capsule-EBT hive layers
        (neural core + collective + memory + regulation + dreaming). No second control plane; no
        production mutation (canon Decision 9)."""
        return hive_evidence_snapshot()

    @application.get("/ops/brain/canon/self-improvement-coverage")
    def ops_brain_canon_self_improvement_coverage():
        """Read-only: the unified self-improvement engine's coverage - every improvable aspect of
        NexusNet and whether a real improvement lane exists for it. Makes the compute-layer
        self-improvement surface reachable from the running service (torch-free; runs no lanes)."""
        cov = _self_improvement_engine().coverage()
        evolution_coverage = services.brain_evolution.evolvable_units()["coverage"]
        return {
            "surface_id": "self-improvement-coverage",
            "authority": "NexusBrain",
            "every_aspect_covered": cov["fully_covered"],
            **cov,
            **evolution_coverage,
        }

    @application.get("/ops/brain/evolution/everything-state")
    def ops_brain_evolution_everything_state():
        return services.brain_evolution.everything_state()

    @application.get("/ops/brain/evolution/evolvable-units")
    def ops_brain_evolution_evolvable_units():
        return services.brain_evolution.evolvable_units()

    @application.get("/ops/brain/evolution/growth-pressure")
    def ops_brain_evolution_growth_pressure():
        return services.brain_evolution.growth_pressure()

    @application.get("/ops/brain/evolution/status")
    def ops_brain_evolution_status():
        return services.brain_evolution.status()

    @application.get("/ops/wrapper/providers")
    def ops_wrapper_providers():
        """The wrapper's pool of wrapped models the end user can select (canon C39 model selector).
        Lists offline + cloud (OpenRouter/Requesty) + local (LM Studio/vLLM) providers, each tagged
        local vs cloud. Cloud activates with an API key; local activates when its endpoint is reachable."""
        return {
            "surface_id": "wrapper-providers",
            "authority": "NexusBrain",
            "providers": provider_registry.list(),
            "local": provider_registry.local_providers(),
            "cloud": provider_registry.cloud_providers(),
            "provider_readiness": provider_registry.readiness(),
            "note": "cloud providers require an API key; local providers require a reachable endpoint",
        }

    @application.get("/ops/brain/canon/continuous-assimilation")
    def ops_brain_canon_continuous_assimilation():
        """Read-only: the wrapper-to-native GROWTH surface - how real /chat usage is assimilating the
        wrapped models into expert nodes (provenance-tagged), and which nodes are now training-ready.
        Privacy-safe: source-model names + counts only, never raw prompts/outputs."""
        status = continuous_assimilation.status()
        return {
            "surface_id": "continuous-assimilation",
            "authority": "NexusBrain",
            **status,
            "provenance": {n: continuous_assimilation.provenance(n) for n in status["nodes"]},
            "claim_boundary": "wrapper-to-native-growth-signal-from-real-usage-no-raw-content",
        }

    @application.get("/ops/wrapper/release-runtime")
    def ops_wrapper_release_runtime(session_id: str | None = None):
        return release_wrapper_runtime.summary(session_id=session_id)

    @application.get("/ops/wrapper/release-readiness")
    def ops_wrapper_release_readiness(session_id: str | None = None):
        return release_wrapper_runtime.release_readiness_manifest(session_id=session_id)

    @application.get("/ops/wrapper/status-card")
    def ops_wrapper_status_card(session_id: str | None = None):
        card = dict(release_wrapper_runtime.status_card(session_id=session_id))
        card["evolution"] = services.brain_evolution.status()
        return card

    @application.get("/ops/wrapper/privacy-consent")
    def ops_wrapper_privacy_consent(session_id: str | None = None):
        return release_wrapper_runtime.privacy_consent(session_id=session_id)

    @application.post("/ops/wrapper/privacy-consent")
    def ops_wrapper_privacy_consent_update(payload: dict[str, Any] = Body(...)):
        result = release_wrapper_runtime.record_privacy_consent_decision(
            session_id=str(payload.get("session_id") or "") or None,
            decision=str(payload.get("decision") or ""),
            personal_data_training_opt_in=(
                bool(payload["personal_data_training_opt_in"])
                if "personal_data_training_opt_in" in payload
                else None
            ),
            personal_data_federation_allowed=(
                bool(payload["personal_data_federation_allowed"])
                if "personal_data_federation_allowed" in payload
                else None
            ),
            personal_data_dream_training_allowed=(
                bool(payload["personal_data_dream_training_allowed"])
                if "personal_data_dream_training_allowed" in payload
                else None
            ),
            approved_by=str(payload.get("approved_by") or "admin"),
            approval_ref=str(payload.get("approval_ref") or ""),
        )
        if str(result.get("status") or "").startswith("blocked"):
            raise HTTPException(status_code=400, detail=result)
        return result

    @application.post("/ops/wrapper/boot-supervisor/run")
    def ops_wrapper_boot_supervisor_run(payload: dict[str, Any] = Body(...)):
        return release_wrapper_runtime.run_boot_supervisor_manifest(
            session_id=str(payload.get("session_id") or "") or None,
            base_url=str(payload.get("base_url") or "http://127.0.0.1:0"),
            host=str(payload.get("host") or "127.0.0.1"),
            port=int(payload.get("port") or 0),
            pid=int(payload.get("pid") or 0),
            readiness_command=str(payload.get("readiness_command") or ""),
        )

    @application.post("/ops/wrapper/release-health-heartbeat/run")
    def ops_wrapper_release_health_heartbeat_run(payload: dict[str, Any] | None = Body(default=None)):
        payload = payload or {}
        return release_wrapper_runtime.run_release_health_heartbeat_loop(
            session_id=str(payload.get("session_id") or "") or None,
            trigger=str(payload.get("trigger") or "operator-request"),
            max_cycles=int(payload.get("max_cycles") or 1),
            interval_seconds=int(payload.get("interval_seconds") or 60),
            max_retry_attempts=int(payload.get("max_retry_attempts") or 3),
            retry_backoff_seconds=int(payload.get("retry_backoff_seconds") or 5),
            base_url=str(payload.get("base_url") or "http://127.0.0.1:0"),
            host=str(payload.get("host") or "127.0.0.1"),
            port=int(payload.get("port") or 0),
            pid=int(payload.get("pid") or 0),
        )

    @application.post("/ops/wrapper/release-health-heartbeat/supervisor/configure")
    def ops_wrapper_release_health_heartbeat_supervisor_configure(
        payload: dict[str, Any] | None = Body(default=None),
    ):
        payload = payload or {}
        return release_wrapper_runtime.configure_release_health_heartbeat_supervisor(
            session_id=str(payload.get("session_id") or "") or None,
            enabled=bool(payload.get("enabled")),
            interval_seconds=int(payload.get("interval_seconds") or 60),
            max_pulses_per_tick=int(payload.get("max_pulses_per_tick") or 1),
            schedule_immediately=bool(payload.get("schedule_immediately")),
            configured_by=str(payload.get("configured_by") or "admin"),
        )

    @application.post("/ops/wrapper/release-health-heartbeat/supervisor/repair-run")
    def ops_wrapper_release_health_heartbeat_supervisor_repair_run(
        payload: dict[str, Any] | None = Body(default=None),
    ):
        payload = payload or {}
        session_id = str(payload.get("session_id") or "release-health-heartbeat-supervisor")
        runtime = ops_wrapper_release_runtime(session_id=session_id)
        supervisor = (
            runtime.get("release_health_heartbeat_supervisor")
            if isinstance(runtime.get("release_health_heartbeat_supervisor"), dict)
            else {}
        )
        latest_pulse = supervisor.get("latest_pulse") if isinstance(supervisor.get("latest_pulse"), dict) else {}
        loop = latest_pulse.get("loop") if isinstance(latest_pulse.get("loop"), dict) else {}
        repair_queue = loop.get("repair_queue") if isinstance(loop.get("repair_queue"), dict) else {}
        update_id = str(payload.get("update_id") or repair_queue.get("latest_update_id") or "")
        repair_context: dict[str, Any] = {}
        if update_id:
            supervisor_update_id = str(repair_queue.get("latest_update_id") or "")
            supervisor_safe_update_id = (
                supervisor_update_id.replace(":", "_").replace("/", "_").replace("\\", "_")
            )
            needs_pending_context = (
                not loop
                or not supervisor_update_id
                or update_id not in {supervisor_update_id, supervisor_safe_update_id}
            )
            if needs_pending_context and hasattr(
                release_wrapper_runtime,
                "release_health_heartbeat_supervisor_repair_context",
            ):
                repair_context = release_wrapper_runtime.release_health_heartbeat_supervisor_repair_context(
                    update_id=update_id,
                    session_id=session_id,
                    persist_pulse=True,
                )
                if repair_context.get("status") == "found":
                    update_id = str(repair_context.get("update_id") or update_id)
                    supervisor = (
                        repair_context.get("supervisor")
                        if isinstance(repair_context.get("supervisor"), dict)
                        else supervisor
                    )
                    latest_pulse = (
                        supervisor.get("latest_pulse")
                        if isinstance(supervisor.get("latest_pulse"), dict)
                        else {}
                    )
                    loop = latest_pulse.get("loop") if isinstance(latest_pulse.get("loop"), dict) else {}
                    repair_queue = loop.get("repair_queue") if isinstance(loop.get("repair_queue"), dict) else {}
        if not update_id:
            raise HTTPException(
                status_code=400,
                detail="heartbeat supervisor repair requires a pulse repair proposal update_id",
            )

        proposal = _autonomous_update_proposal(update_id)
        if proposal is None:
            raise HTTPException(status_code=404, detail=f"Unknown autonomous update: {update_id}")

        registry = services.brain_eval_registry.summary(limit=500)
        registered_suite_ids = {
            str(item.get("suite_id") or "")
            for item in registry.get("suites", [])
            if isinstance(item, dict) and str(item.get("suite_id") or "")
        }
        repair_plan = build_release_health_heartbeat_supervisor_repair_run_plan(
            payload=payload,
            supervisor=supervisor,
            proposal=proposal,
            registered_suite_ids=registered_suite_ids,
            default_command=(
                "pytest tests/test_release_wrapper_runtime.py::"
                "test_release_wrapper_health_heartbeat_loop_runs_bounded_self_checks_with_backoff_and_repair_queue -q"
            ),
            digest=_privacy_compat_digest,
        )
        if repair_plan.get("status") != "planned":
            raise HTTPException(
                status_code=int(repair_plan.get("http_status") or 400),
                detail=str(repair_plan.get("detail") or "heartbeat supervisor repair plan was blocked"),
            )

        if repair_plan["register_eval_suite"]:
            services.brain_eval_registry.register(
                EvalSuiteRequest.model_validate(repair_plan["eval_suite_request"])
            )

        command = str(repair_plan["command"])
        actions: dict[str, dict[str, Any]] = {}
        actions["admin_approval"] = ops_brain_autonomous_updates_admin_approval(
            update_id,
            repair_plan["admin_approval_payload"],
        )
        linked_eval_replay = actions["admin_approval"].get("linked_eval_replay")
        actions["shadow_eval_replay"] = (
            linked_eval_replay if isinstance(linked_eval_replay, dict) else {"status": "not-linked"}
        )
        actions["sandbox_tests"] = ops_brain_autonomous_updates_sandbox_tests(
            update_id,
            repair_plan["sandbox_tests_payload"],
        )
        if actions["sandbox_tests"].get("passed") is not True:
            subsystem_repair_envelopes = build_completed_release_health_heartbeat_subsystem_repair_envelopes(
                repair_plan.get("subsystem_repair_envelopes")
                if isinstance(repair_plan.get("subsystem_repair_envelopes"), list)
                else [],
                actions=actions,
            )
            readiness_run = release_wrapper_runtime.record_release_readiness_evidence_run(
                session_id=session_id,
                update_id=update_id,
                command=command,
                actions=actions,
                status="blocked-heartbeat-supervisor-repair-sandbox",
                subsystem_repair_envelopes=subsystem_repair_envelopes,
            )
            return {
                "surface_id": "release-health-heartbeat-supervisor-repair-run",
                "status": "blocked-sandbox-failed",
                "update_id": update_id,
                "source_pulse_id": repair_plan.get("source_pulse_id"),
                "source_loop_id": repair_plan.get("source_loop_id"),
                "repair_context_source": repair_context.get("source") or "supervisor-pulse",
                "subsystem_repair_envelopes": subsystem_repair_envelopes,
                "subsystem_repair_envelope_count": len(subsystem_repair_envelopes),
                "actions": actions,
                "readiness_evidence_run": readiness_run,
                "active_production_mutated": bool(readiness_run.get("active_production_mutated")),
                "raw_content_included": False,
            }
        evidence_ref = str(actions["sandbox_tests"].get("evidence_ref") or "")
        actions["apply"] = ops_brain_autonomous_updates_apply(
            update_id,
            {
                "test_refs": [command],
                "test_evidence_refs": [evidence_ref] if evidence_ref else [],
            },
        )
        actions["rollback"] = ops_brain_autonomous_updates_rollback(
            update_id,
            {"reason": "heartbeat-supervisor-repair-run-rollback-verification"},
        )
        subsystem_repair_envelopes = build_completed_release_health_heartbeat_subsystem_repair_envelopes(
            repair_plan.get("subsystem_repair_envelopes")
            if isinstance(repair_plan.get("subsystem_repair_envelopes"), list)
            else [],
            actions=actions,
        )
        readiness_run = release_wrapper_runtime.record_release_readiness_evidence_run(
            session_id=session_id,
            update_id=update_id,
            command=command,
            actions=actions,
            status="completed-heartbeat-supervisor-repair",
            subsystem_repair_envelopes=subsystem_repair_envelopes,
        )
        return {
            "schema_version": "nexusnet-release-health-heartbeat-supervisor-repair-run-v1",
            "surface_id": "release-health-heartbeat-supervisor-repair-run",
            "status": "completed",
            "update_id": update_id,
            "source_pulse_id": repair_plan.get("source_pulse_id"),
            "source_loop_id": repair_plan.get("source_loop_id"),
            "source_heartbeat_id": repair_plan.get("source_heartbeat_id"),
            "repair_context_source": repair_context.get("source") or "supervisor-pulse",
            "subsystem_repair_envelopes": subsystem_repair_envelopes,
            "subsystem_repair_envelope_count": len(subsystem_repair_envelopes),
            "actions": actions,
            "readiness_evidence_run": readiness_run,
            "active_production_mutated": bool(readiness_run.get("active_production_mutated")),
            "raw_content_included": False,
            "mutation_boundary": "admin-approved-shadow-eval-sandbox-safe-file-apply-rollback-only",
            "privacy_boundary": "sanitized-heartbeat-repair-statuses-and-refs-only-no-prompts-outputs-session-ids",
        }

    @application.post("/ops/wrapper/domain-expert-growth/admin-replay")
    def ops_wrapper_domain_expert_growth_admin_replay(payload: dict[str, Any] = Body(...)):
        result = release_wrapper_runtime.approve_domain_expert_growth_admin_replay(
            session_id=str(payload.get("session_id") or "") or None,
            domain_ao=str(payload.get("domain_ao") or "") or None,
            handoff_id=str(payload.get("handoff_id") or "") or None,
            approved_by=str(payload.get("approved_by") or "admin"),
            approval_ref=str(payload.get("approval_ref") or "") or None,
            requested_decision=str(payload.get("requested_decision") or "approved"),
        )
        if str(result.get("status") or "").startswith("blocked-missing"):
            raise HTTPException(status_code=404, detail=result)
        if str(result.get("status") or "").startswith("blocked"):
            raise HTTPException(status_code=400, detail=result)
        return result

    @application.get("/ops/wrapper/federated-packets")
    def ops_wrapper_federated_packets(session_id: str | None = None):
        return release_wrapper_runtime.federated_packet_outbox(session_id=session_id)

    @application.post("/ops/wrapper/federated-packets/import")
    def ops_wrapper_import_federated_packet(payload: dict[str, Any] = Body(...)):
        packet = payload.get("packet") if isinstance(payload.get("packet"), dict) else payload
        return release_wrapper_runtime.import_federated_packet(
            packet=packet,
            session_id=payload.get("session_id") if isinstance(payload, dict) else None,
            peer_node_id=payload.get("peer_node_id") if isinstance(payload, dict) else None,
        )

    @application.get("/ops/wrapper/federated-packets/imports")
    def ops_wrapper_federated_packet_imports(session_id: str | None = None):
        return release_wrapper_runtime.federated_packet_inbox(session_id=session_id)

    @application.get("/ops/wrapper/session-lifecycle")
    def ops_wrapper_session_lifecycle(session_id: str | None = None):
        return release_wrapper_runtime.session_lifecycle(session_id=session_id)

    @application.get("/ops/wrapper/first-run-readiness")
    def ops_wrapper_first_run_readiness(session_id: str | None = None):
        return release_wrapper_runtime.first_run_readiness(session_id=session_id)

    @application.post("/ops/wrapper/first-run-readiness/run")
    def ops_wrapper_first_run_readiness_run(payload: dict[str, Any] | None = Body(default=None)):
        payload = payload or {}
        session_id = str(payload.get("session_id") or "") or None
        overrides = payload.get("request_overrides") if isinstance(payload.get("request_overrides"), dict) else {}
        return release_wrapper_runtime.record_first_run_readiness_run(
            session_id=session_id,
            request_overrides=overrides,
        )

    @application.get("/ops/wrapper/production-spine-release-lifecycle")
    def ops_wrapper_production_spine_release_lifecycle(session_id: str | None = None):
        return release_wrapper_runtime.production_spine_release_lifecycle(session_id=session_id)

    @application.post("/ops/wrapper/production-spine-release-lifecycle/run")
    def ops_wrapper_production_spine_release_lifecycle_run(payload: dict[str, Any] | None = Body(default=None)):
        payload = payload or {}
        session_id = str(payload.get("session_id") or "") or None
        overrides = payload.get("request_overrides") if isinstance(payload.get("request_overrides"), dict) else {}
        admin_approval = _production_spine_lifecycle_admin_approval_from_payload(payload)
        return release_wrapper_runtime.record_production_spine_release_lifecycle_run(
            session_id=session_id,
            operator_approved=bool(payload.get("operator_approved")),
            human_approved=bool(payload.get("human_approved")),
            admin_approval=admin_approval,
            request_overrides=overrides,
        )

    @application.post("/ops/wrapper/production-spine-release-lifecycle/{run_id}/rollback")
    def ops_wrapper_production_spine_release_lifecycle_rollback(
        run_id: str,
        payload: dict[str, Any] | None = Body(default=None),
    ):
        payload = payload or {}
        session_id = str(payload.get("session_id") or "") or None
        reason = str(payload.get("reason") or "operator-requested-lifecycle-rollback")
        rollback = release_wrapper_runtime.rollback_production_spine_release_lifecycle_run(
            run_id=run_id,
            session_id=session_id,
            reason=reason,
        )
        if rollback.get("status") == "blocked-run-not-found":
            raise HTTPException(status_code=404, detail="production-spine release lifecycle run was not found")
        return rollback

    @application.get("/ops/brain/assimilation-target-catalog/{target_id}")
    def ops_brain_assimilation_target_catalog_detail(target_id: str):
        target = services.brain_assimilation_catalog.get(target_id)
        if target is not None:
            return target
        raise HTTPException(status_code=404, detail=f"Unknown assimilation target: {target_id}")

    @application.get("/ops/brain/self-improvement/lineage")
    def ops_brain_self_improvement_lineage():
        return services.brain_self_improvement_lineage.summary()

    @application.post("/ops/brain/self-improvement/lineage/candidates")
    def ops_brain_self_improvement_lineage_candidates(payload: dict[str, Any] = Body(...)):
        return services.brain_self_improvement_lineage.record_candidate(LineageCandidateRequest.model_validate(payload))

    @application.get("/ops/brain/verifier-search")
    def ops_brain_verifier_search():
        return services.brain_verifier_search.summary()

    @application.post("/ops/brain/verifier-search/runs")
    def ops_brain_verifier_search_runs(payload: dict[str, Any] = Body(...)):
        return services.brain_verifier_search.record_search(VerifierSearchRequest.model_validate(payload))

    @application.get("/ops/brain/policy/rules")
    def ops_brain_policy_rules():
        return _policy_kernel().rules_payload()

    @application.post("/ops/brain/policy/scan")
    def ops_brain_policy_scan(payload: dict[str, Any] = Body(...)):
        request = PolicyScanRequest.model_validate(payload)
        return _policy_kernel().scan(request.targets, waivers=request.waivers).model_dump(mode="json")

    @application.get("/ops/brain/canon/policy-kernel")
    def ops_brain_canon_policy_kernel():
        return _policy_kernel().scorecard()

    @application.get("/ops/brain/agentic-pipelines")
    def ops_brain_agentic_pipelines(session_id: str | None = None, limit: int = 20):
        return services.brain_agentic_pipelines.summary(session_id=session_id, limit=limit)

    @application.post("/ops/brain/agentic-pipelines/runs")
    def ops_brain_agentic_pipeline_runs(payload: dict[str, Any] = Body(...)):
        request = AgenticPipelineRequest.model_validate(payload)
        return services.brain_agentic_pipelines.start(request)

    @application.get("/ops/brain/canon/agentic-pipelines")
    def ops_brain_canon_agentic_pipelines(session_id: str | None = None):
        return services.brain_agentic_pipelines.scorecard(session_id=session_id)

    @application.get("/ops/brain/sandbox-agent-factory")
    def ops_brain_sandbox_agent_factory(session_id: str | None = None, limit: int = 20):
        return services.brain_sandbox_agent_factory.summary(session_id=session_id, limit=limit)

    @application.post("/ops/brain/sandbox-agent-factory/runs")
    def ops_brain_sandbox_agent_factory_runs(payload: dict[str, Any] = Body(...)):
        request = SandboxAgentFactoryRunRequest.model_validate(payload)
        return services.brain_sandbox_agent_factory.start(request)

    @application.get("/ops/brain/canon/sandbox-agent-factory")
    def ops_brain_canon_sandbox_agent_factory(session_id: str | None = None):
        return services.brain_sandbox_agent_factory.scorecard(session_id=session_id)

    @application.get("/ops/brain/assimilation-targets")
    def ops_brain_assimilation_targets(session_id: str | None = None):
        return services.brain_assimilation_targets.summary(session_id=session_id)

    @application.get("/ops/brain/assimilation-targets/{target_id}")
    def ops_brain_assimilation_target(target_id: str):
        target = services.brain_assimilation_targets.target(target_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Assimilation target not found.")
        return target

    @application.get("/ops/brain/video-assimilation-targets")
    def ops_brain_video_assimilation_targets(session_id: str | None = None):
        return services.brain_assimilation_targets.video_scorecard(session_id=session_id)

    @application.get("/ops/brain/video-assimilation-targets/{target_id}")
    def ops_brain_video_assimilation_target(target_id: str):
        payload = services.brain_assimilation_targets.video_target(target_id)
        if payload is None:
            raise HTTPException(status_code=404, detail="video assimilation target not found")
        return payload

    @application.post("/ops/brain/skill-systems/compose")
    def ops_brain_skill_systems_compose(payload: dict[str, Any] = Body(...)):
        return services.brain_assimilation_targets.compose_skill_system(payload)

    @application.get("/ops/brain/canon/assimilation-targets")
    def ops_brain_canon_assimilation_targets(session_id: str | None = None):
        return services.brain_assimilation_targets.scorecard(session_id=session_id)

    @application.get("/ops/brain/canon/video-assimilation-targets")
    def ops_brain_canon_video_assimilation_targets(session_id: str | None = None):
        return services.brain_assimilation_targets.video_scorecard(session_id=session_id)

    @application.get("/ops/brain/codegraph-gate")
    def ops_brain_codegraph_gate():
        return services.brain_codegraph_gate.summary()

    @application.post("/ops/brain/codegraph-gate/manifests")
    def ops_brain_codegraph_gate_manifests(payload: dict[str, Any] = Body(...)):
        return services.brain_codegraph_gate.evaluate(CodegraphRunManifestRequest.model_validate(payload))

    @application.get("/ops/brain/hive-substrate")
    def ops_brain_hive_substrate(session_id: str | None = None):
        return services.brain_hive_substrate.summary(session_id=session_id)

    @application.post("/ops/brain/hive-substrate/forward-pass")
    def ops_brain_hive_substrate_forward_pass(payload: dict[str, Any] = Body(...)):
        request = HiveForwardPassRequest.model_validate(payload)
        result = services.brain_hive_substrate.run_forward_pass(request)
        result["runtime_growth_dream_research"] = release_wrapper_runtime.queue_native_runtime_growth_review(
            session_id=request.session_id,
            hive_result=result,
        )
        return result

    @application.post("/ops/brain/hive-substrate/assimilate")
    def ops_brain_hive_substrate_assimilate(payload: dict[str, Any] = Body(...)):
        request = HiveAssimilationCandidateRequest.model_validate(payload)
        return services.brain_hive_substrate.assimilate_candidate(request)

    @application.post("/ops/brain/hive-substrate/dream")
    def ops_brain_hive_substrate_dream(payload: dict[str, Any] = Body(...)):
        request = HiveRecursiveDreamRequest.model_validate(payload)
        return services.brain_hive_substrate.run_recursive_dream(request)

    @application.post("/ops/brain/hive-substrate/productionize")
    def ops_brain_hive_substrate_productionize(payload: dict[str, Any] = Body(...)):
        request = HiveProductionizationRequest.model_validate(payload)
        return services.brain_hive_substrate.run_productionization_cycle(request)

    @application.post("/ops/brain/hive-substrate/shadow-release")
    def ops_brain_hive_substrate_shadow_release(payload: dict[str, Any] = Body(...)):
        request = HiveShadowReleaseRequest.model_validate(payload)
        return services.brain_hive_substrate.activate_shadow_release(request)

    @application.post("/ops/brain/hive-substrate/active-release")
    def ops_brain_hive_substrate_active_release(payload: dict[str, Any] = Body(...)):
        request = HiveActiveReleaseRequest.model_validate(payload)
        return services.brain_hive_substrate.promote_active_release(request)

    @application.post("/ops/brain/hive-substrate/rollback")
    def ops_brain_hive_substrate_rollback(payload: dict[str, Any] = Body(...)):
        request = HiveRollbackRequest.model_validate(payload)
        return services.brain_hive_substrate.rollback_shadow_release(request)

    @application.post("/ops/brain/hive-substrate/rewind")
    def ops_brain_hive_substrate_rewind(payload: dict[str, Any] = Body(...)):
        request = HiveCheckpointRewindRequest.model_validate(payload)
        return services.brain_hive_substrate.rewind_checkpoint(request)

    @application.post("/ops/brain/hive-substrate/global-federation/review")
    def ops_brain_hive_substrate_global_federation_review(payload: dict[str, Any] = Body(...)):
        request = HiveGlobalFederationReviewRequest.model_validate(payload)
        return services.brain_hive_substrate.review_global_federation_promotion(request)

    @application.post("/ops/brain/hive-substrate/route-candidates/{evaluation_id}/approve")
    def ops_brain_hive_substrate_route_candidate_approve(
        evaluation_id: str,
        payload: dict[str, Any] = Body(...),
    ):
        request = dict(payload or {})
        request["evaluation_id"] = evaluation_id
        return services.brain_hive_substrate.approve_governed_route_candidate(
            request,
            eval_registry=services.brain_eval_registry,
        )

    @application.post("/ops/brain/hive-substrate/route-candidates/{approval_id}/rollback")
    def ops_brain_hive_substrate_route_candidate_rollback(
        approval_id: str,
        payload: dict[str, Any] = Body(...),
    ):
        request = dict(payload or {})
        request["approval_id"] = approval_id
        return services.brain_hive_substrate.rollback_governed_route_candidate(request)

    @application.get("/ops/brain/hive-substrate/health")
    def ops_brain_hive_substrate_health(session_id: str | None = None):
        return services.brain_hive_substrate.health(session_id=session_id)

    @application.get("/ops/brain/hive-substrate/replay")
    def ops_brain_hive_substrate_replay(session_id: str | None = None, run_id: str | None = None):
        return services.brain_hive_substrate.replay(session_id=session_id, run_id=run_id)

    @application.get("/ops/brain/hive-substrate/curator")
    def ops_brain_hive_substrate_curator(session_id: str | None = None):
        return services.brain_hive_substrate.curate(session_id=session_id)

    @application.get("/ops/brain/canon/hive-substrate")
    def ops_brain_canon_hive_substrate(session_id: str | None = None):
        return services.brain_hive_substrate.scorecard(session_id=session_id)

    @application.get("/ops/brain/harness-providers")
    def ops_brain_harness_providers():
        return services.brain_harness_providers.summary()

    @application.post("/ops/brain/harness-providers/recommend")
    def ops_brain_harness_providers_recommend(payload: dict[str, Any] = Body(...)):
        return services.brain_harness_providers.recommend(payload)

    @application.get("/ops/brain/canon/harness-providers")
    def ops_brain_canon_harness_providers():
        return services.brain_harness_providers.scorecard()

    @application.get("/ops/brain/harness-routing")
    def ops_brain_harness_routing():
        return services.brain_harness_router.summary()

    @application.post("/ops/brain/harness-routing/recommend")
    def ops_brain_harness_routing_recommend(payload: dict[str, Any] = Body(...)):
        request = HarnessRouteRequest.model_validate(payload)
        return services.brain_harness_router.recommend(request)

    @application.get("/ops/brain/canon/harness-routing")
    def ops_brain_canon_harness_routing():
        return services.brain_harness_router.scorecard()

    @application.get("/ops/brain/evolution/harness-ledger")
    def ops_brain_evolution_harness_ledger(limit: int = 50):
        return services.brain_harness_improvement_ledger.summary(limit=limit)

    @application.post("/ops/brain/evolution/harness-ledger/entries")
    def ops_brain_evolution_harness_ledger_entries(payload: dict[str, Any] = Body(...)):
        request = HarnessLedgerEntryRequest.model_validate(payload)
        return services.brain_harness_improvement_ledger.record(request)

    @application.get("/ops/brain/canon/harness-ledger")
    def ops_brain_canon_harness_ledger():
        return services.brain_harness_improvement_ledger.scorecard()

    @application.get("/ops/brain/agent-opportunities")
    def ops_brain_agent_opportunities():
        return services.brain_agent_opportunities.summary()

    @application.post("/ops/brain/agent-opportunities/discover")
    def ops_brain_agent_opportunities_discover(payload: dict[str, Any] = Body(...)):
        request = AgentOpportunityRequest.model_validate(payload)
        return services.brain_agent_opportunities.discover(request)

    @application.get("/ops/brain/canon/agent-opportunities")
    def ops_brain_canon_agent_opportunities():
        return services.brain_agent_opportunities.scorecard()

    @application.get("/ops/brain/edge-workload-router")
    def ops_brain_edge_workload_router(limit: int = 20):
        return services.brain_edge_workload_router.summary(limit=limit)

    @application.post("/ops/brain/edge-workload-router/route")
    def ops_brain_edge_workload_router_route(payload: dict[str, Any] = Body(...)):
        request = EdgeWorkloadRequest.model_validate(payload)
        return services.brain_edge_workload_router.route(request)

    @application.get("/ops/brain/canon/edge-workload-router")
    def ops_brain_canon_edge_workload_router():
        return services.brain_edge_workload_router.scorecard()

    @application.get("/ops/brain/inference-economy-router")
    def ops_brain_inference_economy_router(limit: int = 50):
        return services.brain_inference_economy_router.summary(limit=limit)

    @application.post("/ops/brain/inference-economy-router/route")
    def ops_brain_inference_economy_router_route(payload: dict[str, Any] = Body(...)):
        request = InferenceRouteRequest.model_validate(payload)
        return services.brain_inference_economy_router.route(request)

    @application.get("/ops/brain/canon/inference-economy-router")
    def ops_brain_canon_inference_economy_router():
        return services.brain_inference_economy_router.scorecard()

    @application.get("/ops/brain/inference-architecture")
    def ops_brain_inference_architecture(limit: int = 50):
        return services.brain_inference_architecture.summary(limit=limit)

    @application.post("/ops/brain/inference-architecture/plan")
    def ops_brain_inference_architecture_plan(payload: dict[str, Any] = Body(...)):
        request = InferenceArchitectureRequest.model_validate(payload)
        return services.brain_inference_architecture.plan(request)

    @application.get("/ops/brain/canon/inference-architecture")
    def ops_brain_canon_inference_architecture():
        return services.brain_inference_architecture.scorecard()

    @application.get("/ops/brain/inference-evolution")
    def ops_brain_inference_evolution():
        return services.brain_inference_architecture.evolutionary_system.status()

    @application.post("/ops/brain/inference-evolution/model")
    def ops_brain_inference_evolution_model(metadata: RuntimeModelMetadata = Body(...)):
        return services.brain_inference_architecture.evolutionary_system.attach_model(metadata).model_dump(mode="json")

    @application.post("/ops/brain/inference-evolution/select")
    def ops_brain_inference_evolution_select(payload: dict[str, Any] = Body(...)):
        workload = WorkloadProfile.model_validate(payload.get("workload", {}))
        slo = SLOProfile.model_validate(payload.get("slo", {}))
        return services.brain_inference_architecture.evolutionary_system.select_plan(workload, slo).model_dump(mode="json")

    @application.post("/ops/brain/inference-evolution/dream")
    def ops_brain_inference_evolution_dream(gate: CapacityGate = Body(...)):
        return services.brain_inference_architecture.evolutionary_system.run_dream_cycle(gate).model_dump(mode="json")

    @application.post("/ops/brain/inference-evolution/observe")
    def ops_brain_inference_evolution_observe(observation: RuntimeObservation = Body(...)):
        return {"outcome": services.brain_inference_architecture.evolutionary_system.observe(observation)}

    @application.post("/ops/brain/inference-evolution/rollback")
    def ops_brain_inference_evolution_rollback(payload: dict[str, Any] = Body(default={})):
        reason = str(payload.get("reason") or "operator-request")
        return {"outcome": services.brain_inference_architecture.evolutionary_system.rollback(reason)}

    @application.get("/ops/brain/cache-ledger")
    def ops_brain_cache_ledger(limit: int = 50):
        return services.brain_cache_ledger.summary(limit=limit)

    @application.get("/ops/brain/runtime/effective-context")
    def ops_brain_runtime_effective_context(limit: int = 50):
        return services.brain_cache_ledger.summary(limit=limit)

    @application.post("/ops/brain/cache-ledger/entries")
    def ops_brain_cache_ledger_entries(payload: dict[str, Any] = Body(...)):
        request = CacheLedgerEntryRequest.model_validate(payload)
        return services.brain_cache_ledger.record(request)

    @application.get("/ops/brain/canon/cache-ledger")
    def ops_brain_canon_cache_ledger():
        return services.brain_cache_ledger.scorecard()

    @application.get("/ops/brain/runtime-scorecards")
    def ops_brain_runtime_scorecards(limit: int = 50):
        return services.brain_runtime_workload_scorecards.summary(limit=limit)

    @application.post("/ops/brain/runtime-scorecards/records")
    def ops_brain_runtime_scorecards_records(payload: dict[str, Any] = Body(...)):
        request = RuntimeWorkloadScorecardRequest.model_validate(payload)
        return services.brain_runtime_workload_scorecards.record(request)

    @application.get("/ops/brain/canon/runtime-scorecards")
    def ops_brain_canon_runtime_scorecards():
        return services.brain_runtime_workload_scorecards.scorecard()

    @application.get("/ops/brain/quantization-catalog")
    def ops_brain_quantization_catalog(limit: int = 50):
        return services.brain_quantization_catalog.summary(limit=limit)

    @application.post("/ops/brain/quantization-catalog/recommend")
    def ops_brain_quantization_catalog_recommend(payload: dict[str, Any] = Body(...)):
        request = QuantizationRecommendationRequest.model_validate(payload)
        return services.brain_quantization_catalog.recommend(request)

    @application.get("/ops/brain/canon/quantization-catalog")
    def ops_brain_canon_quantization_catalog():
        return services.brain_quantization_catalog.scorecard()

    @application.get("/ops/brain/model-passports")
    def ops_brain_model_passports():
        return services.brain_edge_model_certification.summary()

    @application.post("/ops/brain/model-passports")
    def ops_brain_model_passports_register(payload: dict[str, Any] = Body(...)):
        return services.brain_edge_model_certification.register_passport(ModelPassportRequest.model_validate(payload))

    @application.post("/ops/brain/model-certifications")
    def ops_brain_model_certifications(payload: dict[str, Any] = Body(...)):
        return services.brain_edge_model_certification.certify(CertificationRunRequest.model_validate(payload))

    @application.get("/ops/brain/protocol-trust")
    def ops_brain_protocol_trust_registry(limit: int = 50):
        return services.brain_protocol_trust_registry.summary(limit=limit)

    @application.post("/ops/brain/protocol-trust/adapters")
    def ops_brain_protocol_trust_registry_adapters(payload: dict[str, Any] = Body(...)):
        request = ProtocolAdapterRequest.model_validate(payload)
        return services.brain_protocol_trust_registry.register(request)

    @application.get("/ops/brain/canon/protocol-trust-registry")
    def ops_brain_canon_protocol_trust_registry():
        return services.brain_protocol_trust_registry.scorecard()

    @application.get("/ops/brain/browser-context")
    def ops_brain_browser_context(limit: int = 50):
        return services.brain_browser_context.summary(limit=limit)

    @application.post("/ops/brain/browser-context/ingest")
    def ops_brain_browser_context_ingest(payload: dict[str, Any] = Body(...)):
        request = BrowserContextIngestRequest.model_validate(payload)
        return services.brain_browser_context.ingest(request)

    @application.post("/ops/brain/browser-context/query")
    def ops_brain_browser_context_query(payload: dict[str, Any] = Body(...)):
        request = BrowserContextQueryRequest.model_validate(payload)
        return services.brain_browser_context.query(request)

    @application.get("/ops/brain/canon/browser-context")
    def ops_brain_canon_browser_context():
        return services.brain_browser_context.scorecard()

    @application.get("/ops/brain/browser/profile-policy")
    def ops_brain_browser_profile_policy():
        return services.brain_browser_profile_policy.summary()

    @application.post("/ops/brain/browser/profile-policy")
    def ops_brain_browser_profile_policy_evaluate(payload: dict[str, Any] = Body(...)):
        return services.brain_browser_profile_policy.evaluate(BrowserProfilePolicyRequest.model_validate(payload))

    @application.get("/ops/brain/dataset-radar")
    def ops_brain_dataset_radar(limit: int = 50):
        return services.brain_dataset_radar.summary(limit=limit)

    @application.get("/ops/brain/dataset-radar/sources")
    def ops_brain_dataset_radar_sources(
        target_node: str | None = None,
        allowed_use: str | None = None,
        limit: int = 200,
    ):
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "living-dataset-radar",
            "sources": services.brain_dataset_radar.list_sources(
                target_node=target_node,
                allowed_use=allowed_use,
                limit=limit,
            ),
        }

    @application.get("/ops/brain/dataset-radar/sources/{source_id:path}")
    def ops_brain_dataset_radar_source_detail(source_id: str):
        detail = services.brain_dataset_radar.source_detail(source_id)
        if detail is None:
            raise HTTPException(status_code=404, detail=f"Dataset Radar source not found: {source_id}")
        return detail

    @application.post("/ops/brain/dataset-radar/refresh")
    def ops_brain_dataset_radar_refresh(payload: dict[str, Any] = Body(default_factory=dict)):
        return services.brain_dataset_radar.refresh(payload)

    @application.post("/ops/brain/dataset-radar/refresh-batch")
    def ops_brain_dataset_radar_refresh_batch(payload: dict[str, Any] = Body(default_factory=dict)):
        return services.brain_dataset_radar.refresh_batch_run(payload)

    @application.post("/ops/brain/dataset-radar/gate-preview")
    def ops_brain_dataset_radar_gate_preview(payload: dict[str, Any] = Body(default_factory=dict)):
        return services.brain_dataset_radar.gate_preview(payload)

    @application.post("/ops/brain/dataset-radar/material-request")
    def ops_brain_dataset_radar_material_request(payload: dict[str, Any] = Body(default_factory=dict)):
        return services.brain_dataset_radar.material_request(payload)

    @application.post("/ops/brain/dataset-radar/candidate-review")
    def ops_brain_dataset_radar_candidate_review(payload: dict[str, Any] = Body(default_factory=dict)):
        return services.brain_dataset_radar.candidate_review(payload)

    @application.get("/ops/brain/dataset-radar/refresh-presets")
    def ops_brain_dataset_radar_refresh_presets():
        return {
            "surface_id": "living-dataset-radar",
            "presets": services.brain_dataset_radar.refresh_presets(),
        }

    @application.get("/ops/brain/dataset-radar/refresh-runs")
    def ops_brain_dataset_radar_refresh_runs(limit: int = 50):
        return {
            "surface_id": "living-dataset-radar",
            "runs": services.brain_dataset_radar.refresh_runs(limit=limit),
        }

    @application.get("/ops/brain/dataset-radar/refresh-runs/{refresh_run_id}")
    def ops_brain_dataset_radar_refresh_run(refresh_run_id: str):
        run = services.brain_dataset_radar.refresh_run(refresh_run_id)
        if run is None:
            raise HTTPException(status_code=404, detail=f"Dataset Radar refresh run not found: {refresh_run_id}")
        return run

    @application.get("/ops/brain/dataset-radar/refresh-batches")
    def ops_brain_dataset_radar_refresh_batches(limit: int = 50):
        return {
            "surface_id": "living-dataset-radar",
            "batches": services.brain_dataset_radar.refresh_batches(limit=limit),
        }

    @application.get("/ops/brain/dataset-radar/refresh-batches/{batch_id}")
    def ops_brain_dataset_radar_refresh_batch_replay(batch_id: str):
        batch = services.brain_dataset_radar.refresh_batch(batch_id)
        if batch is None:
            raise HTTPException(status_code=404, detail=f"Dataset Radar refresh batch not found: {batch_id}")
        return batch

    @application.get("/ops/brain/dataset-radar/material-requests")
    def ops_brain_dataset_radar_material_requests(limit: int = 50):
        return {
            "surface_id": "living-dataset-radar",
            "requests": services.brain_dataset_radar.material_requests(limit=limit),
        }

    @application.get("/ops/brain/dataset-radar/material-requests/{material_request_id}")
    def ops_brain_dataset_radar_material_request_replay(material_request_id: str):
        request = services.brain_dataset_radar.material_request_record(material_request_id)
        if request is None:
            raise HTTPException(status_code=404, detail=f"Dataset Radar material request not found: {material_request_id}")
        return request

    @application.get("/ops/brain/dataset-radar/candidate-reviews")
    def ops_brain_dataset_radar_candidate_reviews(limit: int = 50):
        return {
            "surface_id": "living-dataset-radar",
            "reviews": services.brain_dataset_radar.candidate_reviews(limit=limit),
        }

    @application.get("/ops/brain/dataset-radar/candidate-reviews/{candidate_review_id}")
    def ops_brain_dataset_radar_candidate_review_replay(candidate_review_id: str):
        review = services.brain_dataset_radar.candidate_review_record(candidate_review_id)
        if review is None:
            raise HTTPException(status_code=404, detail=f"Dataset Radar candidate review not found: {candidate_review_id}")
        return review

    @application.get("/ops/brain/canon/dataset-radar")
    def ops_brain_canon_dataset_radar():
        return services.brain_dataset_radar.scorecard()

    @application.get("/ops/brain/dataset-forge")
    def ops_brain_dataset_forge(limit: int = 50):
        return services.brain_dataset_forge.summary(limit=limit)

    @application.post("/ops/brain/dataset-forge/manifests")
    def ops_brain_dataset_forge_manifests(payload: dict[str, Any] = Body(...)):
        request = DatasetForgeRequest.model_validate(payload)
        return services.brain_dataset_forge.build(request)

    @application.get("/ops/brain/canon/dataset-forge")
    def ops_brain_canon_dataset_forge():
        return services.brain_dataset_forge.scorecard()

    @application.get("/ops/brain/knowledge-artifacts")
    def ops_brain_knowledge_artifacts(limit: int = 50, task_family: str | None = None):
        artifacts = services.brain_knowledge_artifacts.artifacts(limit=limit, task_family=task_family)
        summary = services.brain_knowledge_artifacts.summary(limit=limit)
        return {
            **summary,
            "artifact_count": len(artifacts),
            "artifacts": artifacts,
            "latest_artifact": artifacts[0] if artifacts else None,
        }

    @application.post("/ops/brain/knowledge-artifacts/compile")
    def ops_brain_knowledge_artifacts_compile(payload: dict[str, Any] = Body(...)):
        request = KnowledgeCompileRequest.model_validate(payload)
        return services.brain_knowledge_artifacts.compile(request)

    @application.post("/ops/brain/knowledge-artifacts/query")
    def ops_brain_knowledge_artifacts_query(payload: dict[str, Any] = Body(...)):
        request = KnowledgeRequestContract.model_validate(payload)
        return services.brain_knowledge_artifacts.query(request)

    @application.get("/ops/brain/knowledge-artifacts/query-events")
    def ops_brain_knowledge_artifacts_query_events(limit: int = 50):
        return services.brain_knowledge_artifacts.query_events(limit=limit)

    @application.post("/ops/brain/knowledge-artifacts/freshness")
    def ops_brain_knowledge_artifacts_freshness(payload: dict[str, Any] = Body(...)):
        artifact_id = str(payload.get("artifact_id") or "")
        if not artifact_id:
            raise HTTPException(status_code=400, detail="artifact_id is required")
        sources = payload.get("sources") or []
        return services.brain_knowledge_artifacts.refresh_freshness(artifact_id, sources)

    @application.get("/ops/brain/canon/knowledge-artifacts")
    def ops_brain_canon_knowledge_artifacts():
        return services.brain_knowledge_artifacts.scorecard()

    @application.get("/ops/brain/knowledge-artifacts/{artifact_id:path}")
    def ops_brain_knowledge_artifact_detail(artifact_id: str):
        artifact = services.brain_knowledge_artifacts.artifact(artifact_id)
        if artifact is None:
            raise HTTPException(status_code=404, detail=f"Knowledge artifact not found: {artifact_id}")
        return artifact

    @application.get("/ops/brain/adapter-registry")
    def ops_brain_adapter_registry(limit: int = 50):
        return services.brain_adapter_registry.summary(limit=limit)

    @application.post("/ops/brain/adapter-registry/candidates")
    def ops_brain_adapter_registry_candidates(payload: dict[str, Any] = Body(...)):
        request = AdapterRecordRequest.model_validate(payload)
        return services.brain_adapter_registry.register(request)

    @application.get("/ops/brain/canon/adapter-registry")
    def ops_brain_canon_adapter_registry():
        return services.brain_adapter_registry.scorecard()

    @application.get("/ops/brain/fine-tune-decision-gate")
    def ops_brain_fine_tune_decision_gate(limit: int = 50):
        return services.brain_fine_tune_decision_gate.summary(limit=limit)

    @application.post("/ops/brain/fine-tune-decision-gate/decisions")
    def ops_brain_fine_tune_decision_gate_decisions(payload: dict[str, Any] = Body(...)):
        request = FineTuneDecisionRequest.model_validate(payload)
        return services.brain_fine_tune_decision_gate.decide(request)

    @application.get("/ops/brain/canon/fine-tune-decision-gate")
    def ops_brain_canon_fine_tune_decision_gate():
        return services.brain_fine_tune_decision_gate.scorecard()

    @application.get("/ops/brain/adapter-training")
    def ops_brain_adapter_training(limit: int = 50):
        return services.brain_adapter_training.summary(limit=limit)

    @application.post("/ops/brain/adapter-training/plans")
    def ops_brain_adapter_training_plans(payload: dict[str, Any] = Body(...)):
        request = AdapterTrainingPlanRequest.model_validate(payload)
        return services.brain_adapter_training.plan(request)

    @application.get("/ops/brain/canon/adapter-training")
    def ops_brain_canon_adapter_training():
        return services.brain_adapter_training.scorecard()

    @application.get("/ops/brain/growth-engine")
    def ops_brain_growth_engine(limit: int = 50):
        return services.brain_growth_engine.summary(limit=limit)

    @application.post("/ops/brain/growth-engine/cycles")
    def ops_brain_growth_engine_cycles(payload: dict[str, Any] = Body(...)):
        request = GrowthCycleRequest.model_validate(payload)
        return services.brain_growth_engine.start_dry_run(request)

    @application.get("/ops/brain/growth-engine/cycles/{cycle_id}")
    def ops_brain_growth_engine_cycle(cycle_id: str):
        replay = services.brain_growth_engine.replay_cycle(cycle_id)
        if replay is not None:
            return replay
        raise HTTPException(status_code=404, detail=f"Unknown growth cycle: {cycle_id}")

    @application.get("/ops/brain/canon/growth-engine")
    def ops_brain_canon_growth_engine():
        return services.brain_growth_engine.scorecard()

    @application.get("/ops/brain/production-spine")
    def ops_brain_production_spine(limit: int = 50):
        return services.brain_production_spine.summary(limit=limit)

    @application.post("/ops/brain/production-spine/cycles")
    def ops_brain_production_spine_cycles(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.run_completion_cycle(payload)

    @application.post("/ops/brain/production-spine/growth-lifecycles")
    def ops_brain_production_spine_growth_lifecycles(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.run_growth_lifecycle(payload)

    @application.post("/ops/brain/production-spine/reviewer-windows")
    def ops_brain_production_spine_reviewer_windows(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.record_reviewer_window_advancement(payload)

    @application.post("/ops/brain/production-spine/training-runs")
    def ops_brain_production_spine_training_runs(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.run_sandbox_training_proof(payload)

    @application.post("/ops/brain/production-spine/real-training-gates")
    def ops_brain_production_spine_real_training_gates(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.assess_real_training_execution_gate(payload)

    @application.post("/ops/brain/production-spine/training-backend-plans")
    def ops_brain_production_spine_training_backend_plans(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.plan_training_backend(payload)

    @application.post("/ops/brain/production-spine/child-executions")
    def ops_brain_production_spine_child_executions(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.execute_child_node(payload)

    @application.post("/ops/brain/production-spine/hive-moe-routes")
    def ops_brain_production_spine_hive_moe_routes(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.run_hive_moe_shadow_route(payload)

    @application.post("/ops/brain/production-spine/tensor-programs")
    def ops_brain_production_spine_tensor_programs(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.execute_tensor_program(payload)

    @application.post("/ops/brain/production-spine/teacher-council-reviews")
    def ops_brain_production_spine_teacher_council_reviews(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.run_teacher_council_review(payload)

    @application.post("/ops/brain/production-spine/eval-gauntlets")
    def ops_brain_production_spine_eval_gauntlets(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.run_sealed_eval_review(payload)

    @application.post("/ops/brain/production-spine/node-registry-decisions")
    def ops_brain_production_spine_node_registry_decisions(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.apply_node_registry_decision(payload)

    @application.post("/ops/brain/production-spine/node-registry-snapshot")
    def ops_brain_production_spine_node_registry_snapshot(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.node_registry_snapshot(payload)

    @application.post("/ops/brain/production-spine/federated-packets")
    def ops_brain_production_spine_federated_packets(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.submit_federated_influence_packet(payload)

    @application.post("/ops/brain/production-spine/dream-cycles")
    def ops_brain_production_spine_dream_cycles(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.run_recursive_dream_cycle(payload)

    @application.post("/ops/brain/production-spine/runtime-benchmarks")
    def ops_brain_production_spine_runtime_benchmarks(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.run_runtime_quantization_benchmark(payload)

    @application.post("/ops/brain/production-spine/deep-replay")
    def ops_brain_production_spine_deep_replay(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.build_deep_replay_bundle(payload)

    @application.post("/ops/brain/production-spine/signed-replay-artifact-trust-rescans")
    def ops_brain_production_spine_signed_replay_artifact_trust_rescans(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.run_signed_replay_artifact_trust_rescan(payload)

    @application.post("/ops/brain/production-spine/signing-keys/project-local")
    def ops_brain_production_spine_project_local_signing_key(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.create_project_local_signing_key(payload)

    @application.post("/ops/brain/production-spine/productization-readiness")
    def ops_brain_production_spine_productization_readiness(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.assess_productization_readiness(payload)

    @application.post("/ops/brain/production-spine/support-bundles")
    def ops_brain_production_spine_support_bundles(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.build_support_bundle_manifest(payload)

    @application.post("/ops/brain/production-spine/first-run-readiness")
    def ops_brain_production_spine_first_run_readiness(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.build_first_run_readiness_manifest(payload)

    @application.post("/ops/brain/production-spine/crash-diagnostics")
    def ops_brain_production_spine_crash_diagnostics(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.build_crash_diagnostics_manifest(payload)

    @application.post("/ops/brain/production-spine/release-packages")
    def ops_brain_production_spine_release_packages(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.build_release_package_manifest(payload)

    @application.post("/ops/brain/production-spine/release-go-no-go")
    def ops_brain_production_spine_release_go_no_go(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.build_release_go_no_go_manifest(payload)

    @application.post("/ops/brain/production-spine/runtime-health-monitors")
    def ops_brain_production_spine_runtime_health_monitors(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.build_runtime_health_monitor_manifest(payload)

    @application.post("/ops/brain/production-spine/teacher-ejection-reviews")
    def ops_brain_production_spine_teacher_ejection_reviews(payload: dict[str, Any] = Body(...)):
        return services.brain_production_spine.build_teacher_ejection_review_manifest(payload)

    @application.get("/ops/brain/production-spine/manifest-previews")
    def ops_brain_production_spine_manifest_previews(cycle_id: str | None = None):
        return services.brain_production_spine.list_manifest_previews(cycle_id)

    @application.get("/ops/brain/canon/production-spine")
    def ops_brain_canon_production_spine():
        return services.brain_production_spine.scorecard()

    @application.get("/ops/brain/eval-registry")
    def ops_brain_eval_registry(limit: int = 50):
        return services.brain_eval_registry.summary(limit=limit)

    @application.get("/ops/brain/eval-suites")
    def ops_brain_eval_suites(limit: int = 50):
        return services.brain_eval_registry.summary(limit=limit)

    @application.post("/ops/brain/eval-registry/suites")
    def ops_brain_eval_registry_suites(payload: dict[str, Any] = Body(...)):
        request = EvalSuiteRequest.model_validate(payload)
        return services.brain_eval_registry.register(request)

    @application.post("/ops/brain/eval-suites/{suite_id}/run-shadow")
    def ops_brain_eval_suites_run_shadow(suite_id: str, payload: dict[str, Any] = Body(...)):
        request = ShadowEvalRunRequest.model_validate(payload)
        return services.brain_eval_registry.run_shadow(suite_id, request)

    @application.get("/ops/brain/canon/eval-registry")
    def ops_brain_canon_eval_registry():
        return services.brain_eval_registry.scorecard()

    @application.get("/ops/brain/artifact-trust")
    def ops_brain_artifact_trust_registry(limit: int = 50):
        return services.brain_artifact_trust_registry.summary(limit=limit)

    @application.post("/ops/brain/artifact-trust/scans")
    def ops_brain_artifact_trust_registry_scans(payload: dict[str, Any] = Body(...)):
        request = ArtifactScanRequest.model_validate(payload)
        return services.brain_artifact_trust_registry.scan(request)

    @application.post("/ops/brain/artifact-trust/knowledge-artifacts/scan")
    def ops_brain_artifact_trust_knowledge_artifact_scan(payload: dict[str, Any] = Body(...)):
        artifact_id = str(payload.get("artifact_id") or "")
        if not artifact_id:
            raise HTTPException(status_code=400, detail="artifact_id is required")
        artifact = services.brain_knowledge_artifacts.artifact(artifact_id)
        if artifact is None:
            raise HTTPException(status_code=404, detail=f"Knowledge artifact not found: {artifact_id}")
        return services.brain_artifact_trust_registry.scan_knowledge_artifact(artifact)

    @application.get("/ops/brain/canon/artifact-trust-registry")
    def ops_brain_canon_artifact_trust_registry():
        return services.brain_artifact_trust_registry.scorecard()

    @application.get("/ops/brain/autonomous-updates")
    def ops_brain_autonomous_updates(limit: int = 50):
        return services.brain_autonomous_updates.summary(limit=limit)

    @application.post("/ops/brain/autonomous-updates/proposals")
    def ops_brain_autonomous_updates_proposals(payload: dict[str, Any] = Body(...)):
        request = AutonomousUpdateRequest.model_validate(payload)
        return services.brain_autonomous_updates.propose(request)

    def _release_wrapper_ao_guard_or_400(update_id: str, action: str, endpoint_ref: str) -> dict[str, Any]:
        guard = release_wrapper_runtime.guard_self_repair_action(
            update_id=update_id,
            action=action,
            endpoint_ref=endpoint_ref,
        )
        if guard.get("passed") is True:
            return guard
        missing = ", ".join(str(item) for item in guard.get("missing_aos") or []) or "unknown"
        if action == "apply":
            detail = f"AO guard receipts required before safe apply; missing AOs: {missing}"
        else:
            detail = f"AO guard receipts required before admin self-repair action; missing AOs: {missing}"
        raise HTTPException(status_code=400, detail=detail)

    def _release_wrapper_privacy_consent_gate_or_400(
        update_id: str,
        action: str,
        endpoint_ref: str,
    ) -> dict[str, Any]:
        gate = release_wrapper_runtime.guard_privacy_consent_for_autonomous_update(
            update_id=update_id,
            action=action,
            endpoint_ref=endpoint_ref,
        )
        if gate.get("passed") is True:
            return gate
        raise HTTPException(status_code=400, detail=gate)

    @application.post("/ops/brain/autonomous-updates/{update_id}/admin-approval")
    def ops_brain_autonomous_updates_admin_approval(update_id: str, payload: dict[str, Any] = Body(...)):
        try:
            endpoint_ref = f"/ops/brain/autonomous-updates/{update_id}/admin-approval"
            privacy_gate = _release_wrapper_privacy_consent_gate_or_400(
                update_id,
                "admin_approval",
                endpoint_ref,
            )
            guard = _release_wrapper_ao_guard_or_400(update_id, "admin_approval", endpoint_ref)
            approval = services.brain_autonomous_updates.approve(
                update_id,
                approved_by=str(payload.get("approved_by") or "admin"),
                approval_ref=str(payload.get("approval_ref") or ""),
            )
            approval["linked_improvement_queue"] = _sync_linked_improvement_queue(
                update_id,
                target_status="validated",
                actor="AutonomousUpdateController",
                reason="linked autonomous update received admin approval",
            )
            approval["linked_eval_replay"] = _run_linked_eval_replay(update_id)
            approval["release_wrapper_privacy_consent_gate"] = privacy_gate
            approval["release_wrapper_ao_guard"] = guard
            approval["release_wrapper_self_repair"] = release_wrapper_runtime.record_self_repair_action(
                update_id=update_id,
                action="admin_approval",
                result=approval,
                endpoint_ref=endpoint_ref,
            )
            return approval
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @application.post("/ops/brain/autonomous-updates/{update_id}/apply")
    def ops_brain_autonomous_updates_apply(update_id: str, payload: dict[str, Any] = Body(...)):
        try:
            endpoint_ref = f"/ops/brain/autonomous-updates/{update_id}/apply"
            privacy_gate = _release_wrapper_privacy_consent_gate_or_400(update_id, "apply", endpoint_ref)
            guard = _release_wrapper_ao_guard_or_400(update_id, "apply", endpoint_ref)
            applied = services.brain_autonomous_updates.apply_safe(
                update_id,
                test_refs=[str(item) for item in (payload.get("test_refs") or [])],
                test_results=[dict(item) for item in (payload.get("test_results") or []) if isinstance(item, dict)],
                test_evidence_refs=[str(item) for item in (payload.get("test_evidence_refs") or [])],
                ao_guard=guard,
            )
            applied["linked_improvement_queue"] = _sync_linked_improvement_queue(
                update_id,
                target_status="deployed",
                actor="AutonomousUpdateController",
                reason="linked autonomous update applied as shadow safe file",
            )
            applied["release_wrapper_privacy_consent_gate"] = privacy_gate
            applied["release_wrapper_ao_guard"] = guard
            applied["release_wrapper_self_repair"] = release_wrapper_runtime.record_self_repair_action(
                update_id=update_id,
                action="apply",
                result=applied,
                endpoint_ref=endpoint_ref,
            )
            return applied
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/autonomous-updates/{update_id}/sandbox-tests")
    def ops_brain_autonomous_updates_sandbox_tests(update_id: str, payload: dict[str, Any] = Body(...)):
        try:
            endpoint_ref = f"/ops/brain/autonomous-updates/{update_id}/sandbox-tests"
            privacy_gate = _release_wrapper_privacy_consent_gate_or_400(
                update_id,
                "sandbox_tests",
                endpoint_ref,
            )
            guard = _release_wrapper_ao_guard_or_400(update_id, "sandbox_tests", endpoint_ref)
            evidence = services.brain_autonomous_updates.run_sandbox_tests(
                update_id,
                command=str(payload.get("command") or ""),
                project_root=services.paths.project_root,
                timeout_seconds=int(payload.get("timeout_seconds") or 60),
            )
            if evidence.get("passed") is True:
                evidence["linked_improvement_queue"] = _sync_linked_improvement_queue(
                    update_id,
                    target_status="approved",
                    actor="AutonomousUpdateController",
                    reason="linked autonomous update passed isolated sandbox tests",
                )
            else:
                evidence["linked_improvement_queue"] = {
                    "status": "unchanged",
                    "update_id": update_id,
                    "target_status": "approved",
                    "reason": "sandbox evidence did not pass",
                }
            evidence["release_wrapper_privacy_consent_gate"] = privacy_gate
            evidence["release_wrapper_ao_guard"] = guard
            evidence["release_wrapper_self_repair"] = release_wrapper_runtime.record_self_repair_action(
                update_id=update_id,
                action="sandbox_tests",
                result=evidence,
                endpoint_ref=endpoint_ref,
            )
            return evidence
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/autonomous-updates/{update_id}/rollback")
    def ops_brain_autonomous_updates_rollback(update_id: str, payload: dict[str, Any] = Body(...)):
        try:
            endpoint_ref = f"/ops/brain/autonomous-updates/{update_id}/rollback"
            guard = _release_wrapper_ao_guard_or_400(update_id, "rollback", endpoint_ref)
            rollback = services.brain_autonomous_updates.rollback(
                update_id,
                reason=str(payload.get("reason") or "operator-requested-rollback"),
            )
            rollback["linked_improvement_queue"] = _sync_linked_improvement_queue(
                update_id,
                target_status="reverted",
                actor="AutonomousUpdateController",
                reason="linked autonomous update rollback restored previous safe file",
            )
            rollback["release_wrapper_ao_guard"] = guard
            rollback["release_wrapper_self_repair"] = release_wrapper_runtime.record_self_repair_action(
                update_id=update_id,
                action="rollback",
                result=rollback,
                endpoint_ref=endpoint_ref,
            )
            return rollback
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @application.post("/ops/wrapper/release-readiness/run")
    def ops_wrapper_release_readiness_run(payload: dict[str, Any] = Body(...)):
        session_id = str(payload.get("session_id") or "")
        status_card = release_wrapper_runtime.status_card(session_id=session_id or None)
        lane = (
            status_card.get("operator_action_lane")
            if isinstance(status_card.get("operator_action_lane"), dict)
            else {}
        )
        update_id = str(lane.get("proposal_update_id") or payload.get("update_id") or "")
        if not update_id:
            raise HTTPException(status_code=400, detail="release wrapper proposal is required before readiness runner")
        command = str(payload.get("command") or payload.get("sandbox_command") or lane.get("default_sandbox_command") or "")
        timeout_seconds = int(payload.get("timeout_seconds") or 60)
        approved_by = str(payload.get("approved_by") or "admin")
        approval_ref = str(payload.get("approval_ref") or "operator-review::release-readiness-runner")
        actions: dict[str, dict[str, Any]] = {}
        actions["admin_approval"] = ops_brain_autonomous_updates_admin_approval(
            update_id,
            {
                "approved_by": approved_by,
                "approval_ref": approval_ref,
            },
        )
        actions["sandbox_tests"] = ops_brain_autonomous_updates_sandbox_tests(
            update_id,
            {
                "command": command,
                "timeout_seconds": timeout_seconds,
            },
        )
        if actions["sandbox_tests"].get("passed") is not True:
            return release_wrapper_runtime.record_release_readiness_evidence_run(
                session_id=session_id,
                update_id=update_id,
                command=command,
                actions=actions,
                status="blocked-sandbox-failed",
            )
        evidence_ref = str(actions["sandbox_tests"].get("evidence_ref") or "")
        actions["apply"] = ops_brain_autonomous_updates_apply(
            update_id,
            {
                "test_refs": [command],
                "test_evidence_refs": [evidence_ref] if evidence_ref else [],
            },
        )
        actions["rollback"] = ops_brain_autonomous_updates_rollback(
            update_id,
            {"reason": "release-readiness-runner-rollback-verification"},
        )
        return release_wrapper_runtime.record_release_readiness_evidence_run(
            session_id=session_id,
            update_id=update_id,
            command=command,
            actions=actions,
            status="completed",
        )

    @application.post("/ops/wrapper/initial-release-supervisor/run")
    def ops_wrapper_initial_release_supervisor_run(payload: dict[str, Any] = Body(...)):
        session_id = str(payload.get("session_id") or "initial-release-supervisor")
        approved_by = str(payload.get("approved_by") or "admin")
        approval_ref = str(payload.get("approval_ref") or "operator-review::initial-release-supervisor")
        readiness_command = str(
            payload.get("command")
            or payload.get("sandbox_command")
            or payload.get("readiness_command")
            or "pytest tests/test_release_wrapper_runtime.py::test_root_boots_to_release_wrapper_entrypoint -q"
        )
        timeout_seconds = int(payload.get("timeout_seconds") or 60)
        prompts = payload.get("prompts") if isinstance(payload.get("prompts"), list) else []
        if not prompts:
            prompts = [
                "Implement a safe code repair through the NexusNet wrapper release path.",
                "Research assimilation targets and route the learning into the expert system.",
                "Exercise federated packet handling and peer-shadow growth evidence.",
            ]

        heartbeat_supervisor_config = ops_wrapper_release_health_heartbeat_supervisor_configure(
            {
                "session_id": session_id,
                "enabled": True,
                "interval_seconds": 1,
                "max_pulses_per_tick": 1,
                "schedule_immediately": True,
                "configured_by": "initial-release-supervisor",
            }
        )
        chat_refs: list[str] = []
        chat_attempt_count = len(prompts[:3])
        for index, prompt in enumerate(prompts[:3]):
            chat_payload = {
                "session_id": session_id,
                "model": str(payload.get("model") or "nexusnet-offline"),
                "messages": [{"role": "user", "content": str(prompt)}],
                "metadata": {"initial_release_supervisor_step": index + 1},
            }
            chat_result = openai_compatible_chat_completions(chat_payload)
            nexusnet_payload = chat_result.get("nexusnet") if isinstance(chat_result, dict) else {}
            trace_id = nexusnet_payload.get("trace_id") if isinstance(nexusnet_payload, dict) else None
            if trace_id:
                chat_refs.append(f"trace::{trace_id}")

        runtime_after_chats = ops_wrapper_release_runtime(session_id=session_id)
        status_after_chats = ops_wrapper_status_card(session_id=session_id)
        lane = (
            status_after_chats.get("operator_action_lane")
            if isinstance(status_after_chats.get("operator_action_lane"), dict)
            else {}
        )
        update_id = str(lane.get("proposal_update_id") or payload.get("update_id") or "")
        fallback_proposal: dict[str, Any] | None = None
        if not update_id:
            update_id = f"update::initial-release-supervisor::{_privacy_compat_digest(session_id)}"
            fallback_proposal = ops_brain_autonomous_updates_proposals(
                {
                    "update_id": update_id,
                    "update_type": "prompt_policy",
                    "target_ref": "safe-artifact::initial-release-supervisor",
                    "requested_state": "proposal",
                    "eval_refs": [*chat_refs, "initial-release-supervisor::live-wrapper-path"],
                    "artifact_trust_refs": [
                        str((runtime_after_chats.get("latest_federated_packet") or {}).get("packet_signature") or "wrapper-packet")
                    ],
                    "rollback_plan": "restore-previous-initial-release-supervisor-safe-file",
                    "monitoring_plan": readiness_command,
                    "operator_approved": False,
                    "sandbox_ref": "initial-release-supervisor",
                    "metadata": {
                        "source": "release-wrapper-initial-release-supervisor",
                        "session_ref_digest": f"sha256:{_privacy_compat_digest(session_id)}",
                        "safe_payload": {
                            "surface_id": "release-wrapper-initial-release-supervisor",
                            "chat_ref_count": len(chat_refs),
                        },
                        "safe_file_scope": ["artifacts/autonomous-updates/safe-files"],
                        "active_production_mutation_allowed": False,
                    },
                }
            )

        try:
            heartbeat_repair_run = ops_wrapper_release_health_heartbeat_supervisor_repair_run(
                {
                    "session_id": session_id,
                    "command": readiness_command,
                    "timeout_seconds": timeout_seconds,
                    "approved_by": approved_by,
                    "approval_ref": f"{approval_ref}::heartbeat-supervisor-repair",
                }
            )
        except HTTPException as exc:
            if (
                int(exc.status_code) != 400
                or str(exc.detail) != "heartbeat supervisor repair requires a pulse repair proposal update_id"
            ):
                raise
            heartbeat_repair_run = {
                "surface_id": "release-health-heartbeat-supervisor-repair-run",
                "status": "not-required",
                "detail": "heartbeat supervisor had no pulse repair proposal for this product-smoke pass",
                "session_ref_digest": f"sha256:{_privacy_compat_digest(session_id)}",
                "actions": {},
                "readiness_evidence_run": {
                    "surface_id": "release-wrapper-readiness-evidence-run",
                    "status": "not-required",
                    "raw_content_included": False,
                    "active_production_mutation_allowed": False,
                    "active_production_mutated": False,
                },
                "subsystem_repair_envelopes": [],
                "subsystem_repair_envelope_count": 0,
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
                "active_production_mutated": False,
            }
        packet = runtime_after_chats.get("latest_federated_packet")
        if not isinstance(packet, dict) or not packet:
            raise HTTPException(status_code=400, detail="initial release supervisor requires a real wrapper federated packet")
        imported_packet = ops_wrapper_import_federated_packet(
            {
                "session_id": session_id,
                "peer_node_id": str(payload.get("peer_node_id") or "initial-release-supervisor-peer"),
                "packet": packet,
            }
        )
        domain_replay = ops_wrapper_domain_expert_growth_admin_replay(
            {
                "session_id": session_id,
                "domain_ao": str(payload.get("domain_ao") or "FederationAO"),
                "approved_by": approved_by,
                "approval_ref": f"{approval_ref}::domain-expert-growth",
                "requested_decision": "approved",
            }
        )
        readiness_run = ops_wrapper_release_readiness_run(
            {
                "session_id": session_id,
                "update_id": update_id,
                "command": readiness_command,
                "timeout_seconds": timeout_seconds,
                "approved_by": approved_by,
                "approval_ref": approval_ref,
            }
        )
        lifecycle_approval = ops_approvals(
            ApprovalRequest.model_validate(
                {
                    "subject": production_spine_lifecycle_approval_subject,
                    "decision": "approved",
                    "approver": approved_by,
                    "rationale": "Initial release supervisor whole-system shadow lifecycle approval.",
                    "metadata": {
                        "session_ref_digest": f"sha256:{_privacy_compat_digest(session_id)}",
                        "surface_id": "release-wrapper-initial-release-supervisor",
                    },
                }
            )
        )
        production_lifecycle = ops_wrapper_production_spine_release_lifecycle_run(
            {
                "session_id": session_id,
                "approval_decision_id": lifecycle_approval["decision_id"],
                "operator_approved": True,
                "human_approved": True,
            }
        )
        production_rollback = ops_wrapper_production_spine_release_lifecycle_rollback(
            str(production_lifecycle.get("run_id") or ""),
            {"session_id": session_id, "reason": "initial-release-supervisor-rollback-verification"},
        )
        boot_supervisor = ops_wrapper_boot_supervisor_run(
            {
                "session_id": session_id,
                "base_url": str(payload.get("base_url") or "http://127.0.0.1:0"),
                "host": str(payload.get("host") or "127.0.0.1"),
                "port": int(payload.get("port") or 0),
                "pid": int(payload.get("pid") or 0),
                "readiness_command": readiness_command,
            }
        )
        release_readiness = ops_wrapper_release_readiness(session_id=session_id)
        runtime_after_release = ops_wrapper_release_runtime(session_id=session_id)
        release_health_heartbeat_supervisor = (
            runtime_after_release.get("release_health_heartbeat_supervisor")
            if isinstance(runtime_after_release.get("release_health_heartbeat_supervisor"), dict)
            else {}
        )
        native_hive_heartbeat_history = release_native_hive_heartbeat_history_evidence(
            runtime_after_release.get("native_hive_heartbeat")
            if isinstance(runtime_after_release.get("native_hive_heartbeat"), dict)
            else {}
        )
        heartbeat_repair_actions = (
            heartbeat_repair_run.get("actions") if isinstance(heartbeat_repair_run.get("actions"), dict) else {}
        )
        heartbeat_repair_action_statuses = {
            "admin_approval": str(
                (heartbeat_repair_actions.get("admin_approval") or {}).get("status") or "not-approved"
            ),
            "shadow_eval_replay": str(
                (heartbeat_repair_actions.get("shadow_eval_replay") or {}).get("status") or "not-run"
            ),
            "sandbox_tests": str(
                (heartbeat_repair_actions.get("sandbox_tests") or {}).get("status") or "not-run"
            ),
            "apply": str((heartbeat_repair_actions.get("apply") or {}).get("status") or "not-applied"),
            "rollback": str((heartbeat_repair_actions.get("rollback") or {}).get("status") or "not-rolled-back"),
        }
        heartbeat_repair_evidence_run = (
            heartbeat_repair_run.get("readiness_evidence_run")
            if isinstance(heartbeat_repair_run.get("readiness_evidence_run"), dict)
            else {}
        )
        generated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        action_statuses = {
            "wrapper_interactions": "recorded" if chat_attempt_count else "not-recorded",
            "native_hive_heartbeat_history": str(native_hive_heartbeat_history.get("status") or "stale-or-missing"),
            "release_health_heartbeat_supervisor": str(
                release_health_heartbeat_supervisor.get("status")
                or heartbeat_supervisor_config.get("status")
                or "disabled"
            ),
            "release_health_heartbeat_supervisor_repair": str(heartbeat_repair_run.get("status") or "not-run"),
            "federated_packet_import": str(imported_packet.get("status") or "not-recorded"),
            "domain_expert_growth_admin_replay": str(domain_replay.get("status") or "not-recorded"),
            "release_readiness_runner": str(readiness_run.get("status") or "not-run"),
            "production_spine_release_lifecycle": str(production_lifecycle.get("status") or "not-run"),
            "production_spine_release_lifecycle_rollback": str(production_rollback.get("status") or "not-rolled-back"),
            "boot_supervisor": str(boot_supervisor.get("status") or "not-run"),
        }
        heartbeat_repair_status = str(heartbeat_repair_run.get("status") or "not-run")
        heartbeat_repair_ok = heartbeat_repair_status in {"completed", "not-required"}
        status = (
            "initial-release-go"
            if release_readiness.get("go_no_go") == "go"
            and boot_supervisor.get("status") == "boot-smoke-passed"
            and native_hive_heartbeat_history.get("status") == "fresh"
            and native_hive_heartbeat_history.get("latest_fresh") is True
            and release_health_heartbeat_supervisor.get("status") == "enabled"
            and int(release_health_heartbeat_supervisor.get("pulse_count") or 0) > 0
            and heartbeat_repair_ok
            and production_lifecycle.get("status") == "approved-shadow-release-lifecycle"
            and production_rollback.get("status") == "rolled-back"
            else "initial-release-blocked"
        )
        artifact_path = release_wrapper_runtime.runtime_dir / "initial-release-supervisor.json"
        manifest = {
            "schema_version": "nexusnet-release-wrapper-initial-release-supervisor-v1",
            "surface_id": "release-wrapper-initial-release-supervisor",
            "manifest_id": f"initial-release-supervisor::{_privacy_compat_digest(generated_at + session_id)}",
            "generated_at": generated_at,
            "authority": "NexusBrain",
            "status_label": "LOCKED CANON",
            "status": status,
            "honest_status_label": status,
            "product_surface": "wrapper",
            "product_scope": "whole-system",
            "session_ref_digest": f"sha256:{_privacy_compat_digest(session_id)}",
            "actions": {
                "wrapper_interactions": {
                    "status": action_statuses["wrapper_interactions"],
                    "interaction_count": chat_attempt_count,
                    "trace_refs": chat_refs,
                    "raw_content_included": False,
                },
                "native_hive_heartbeat_history": native_hive_heartbeat_history,
                "release_health_heartbeat_supervisor": {
                    "status": action_statuses["release_health_heartbeat_supervisor"],
                    "pulse_count": int(release_health_heartbeat_supervisor.get("pulse_count") or 0),
                    "latest_pulse_id": release_health_heartbeat_supervisor.get("latest_pulse_id"),
                    "latest_loop_id": release_health_heartbeat_supervisor.get("latest_loop_id"),
                    "next_due_status": release_health_heartbeat_supervisor.get("next_due_status"),
                    "raw_content_included": False,
                    "active_production_mutation_allowed": False,
                },
                "release_health_heartbeat_supervisor_repair": {
                    "status": action_statuses["release_health_heartbeat_supervisor_repair"],
                    "update_id": heartbeat_repair_run.get("update_id"),
                    "source_pulse_id": heartbeat_repair_run.get("source_pulse_id"),
                    "source_loop_id": heartbeat_repair_run.get("source_loop_id"),
                    "source_heartbeat_id": heartbeat_repair_run.get("source_heartbeat_id"),
                    "readiness_run_id": heartbeat_repair_evidence_run.get("run_id"),
                    "readiness_evidence_status": heartbeat_repair_evidence_run.get("status"),
                    "action_statuses": heartbeat_repair_action_statuses,
                    "active_production_mutated": bool(heartbeat_repair_run.get("active_production_mutated")),
                    "raw_content_included": False,
                    "active_production_mutation_allowed": False,
                },
                "autonomous_update_proposal": {
                    "status": str((fallback_proposal or {}).get("status") or "existing-proposal-used"),
                    "update_id": update_id,
                    "raw_content_included": False,
                    "active_production_mutation_allowed": False,
                },
                "federated_packet_import": {
                    "status": action_statuses["federated_packet_import"],
                    "import_id": imported_packet.get("import_id"),
                    "raw_content_included": False,
                    "active_production_mutation_allowed": False,
                },
                "domain_expert_growth_admin_replay": {
                    "status": action_statuses["domain_expert_growth_admin_replay"],
                    "run_id": domain_replay.get("run_id"),
                    "promotion_decision": domain_replay.get("promotion_decision"),
                    "raw_content_included": False,
                    "active_production_mutation_allowed": False,
                },
                "release_readiness_runner": {
                    "status": action_statuses["release_readiness_runner"],
                    "run_id": readiness_run.get("run_id"),
                    "readiness_after": readiness_run.get("readiness_after"),
                    "active_production_mutated": bool(readiness_run.get("active_production_mutated")),
                    "raw_content_included": False,
                },
                "production_spine_release_lifecycle": {
                    "status": action_statuses["production_spine_release_lifecycle"],
                    "run_id": production_lifecycle.get("run_id"),
                    "step_counts": production_lifecycle.get("step_counts") or {},
                    "governance_status": (
                        (production_lifecycle.get("authority_evidence_tool_governance") or {}).get("status")
                        if isinstance(production_lifecycle.get("authority_evidence_tool_governance"), dict)
                        else None
                    ),
                    "release_manifest_status": (
                        (production_lifecycle.get("release_manifest_status_rollup") or {}).get("status")
                        if isinstance(production_lifecycle.get("release_manifest_status_rollup"), dict)
                        else None
                    ),
                    "raw_content_included": False,
                    "active_production_mutation_allowed": False,
                },
                "production_spine_release_lifecycle_rollback": {
                    "status": action_statuses["production_spine_release_lifecycle_rollback"],
                    "rollback_id": production_rollback.get("rollback_id"),
                    "rollback_restored": bool(production_rollback.get("rollback_restored")),
                    "raw_content_included": False,
                    "active_production_mutation_allowed": False,
                },
                "boot_supervisor": {
                    "status": action_statuses["boot_supervisor"],
                    "manifest_id": boot_supervisor.get("manifest_id"),
                    "pass_count": boot_supervisor.get("pass_count"),
                    "failed_count": boot_supervisor.get("failed_count"),
                    "raw_content_included": False,
                    "active_production_mutation_allowed": False,
                },
            },
            "action_statuses": action_statuses,
            "release_readiness": {
                "surface_id": release_readiness.get("surface_id"),
                "go_no_go": release_readiness.get("go_no_go"),
                "passed_check_count": release_readiness.get("passed_check_count"),
                "blocked_check_count": release_readiness.get("blocked_check_count"),
                "blockers": release_readiness.get("blockers") or [],
            },
            "boot_supervisor": {
                "surface_id": boot_supervisor.get("surface_id"),
                "status": boot_supervisor.get("status"),
                "manifest_id": boot_supervisor.get("manifest_id"),
                "pass_count": boot_supervisor.get("pass_count"),
                "failed_count": boot_supervisor.get("failed_count"),
            },
            "endpoint_refs": {
                "initial_release_supervisor_run": "/ops/wrapper/initial-release-supervisor/run",
                "release_runtime": "/ops/wrapper/release-runtime",
                "release_readiness": "/ops/wrapper/release-readiness",
                "release_readiness_runner": "/ops/wrapper/release-readiness/run",
                "release_health_heartbeat_supervisor_configure": (
                    "/ops/wrapper/release-health-heartbeat/supervisor/configure"
                ),
                "release_health_heartbeat_supervisor_repair_run": (
                    "/ops/wrapper/release-health-heartbeat/supervisor/repair-run"
                ),
                "production_spine_release_lifecycle_run": "/ops/wrapper/production-spine-release-lifecycle/run",
                "boot_supervisor_run": "/ops/wrapper/boot-supervisor/run",
            },
            "artifact_path": str(artifact_path),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": bool(readiness_run.get("active_production_mutated")),
            "privacy_boundary": "sanitized-status-ids-counts-digests-only-no-raw-prompts-outputs-session-ids",
            "mutation_boundary": "admin-approved-shadow-safe-file-production-spine-and-boot-evidence-only",
        }
        artifact_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        return manifest

    @application.post("/ops/wrapper/release-product-smoke/run")
    def ops_wrapper_release_product_smoke_run(payload: dict[str, Any] | None = Body(default=None)):
        payload = payload or {}
        session_id = str(payload.get("session_id") or "release-product-smoke")
        readiness_command = str(
            payload.get("command")
            or payload.get("sandbox_command")
            or payload.get("readiness_command")
            or "pytest tests/test_release_wrapper_runtime.py::test_root_boots_to_release_wrapper_entrypoint -q"
        )
        base_url = str(payload.get("base_url") or "http://127.0.0.1:0")
        host = str(payload.get("host") or "127.0.0.1")
        port = int(payload.get("port") or 0)
        pid = int(payload.get("pid") or 0)
        payload_prompts = [str(prompt) for prompt in payload.get("prompts", [])] if isinstance(payload.get("prompts"), list) else []
        smoke_prompts = [
            *(payload_prompts[:1] or ["Exercise the NexusNet release product smoke path."]),
            "Research assimilation targets and route the learning into the expert system.",
            "Exercise federated packet handling and peer-shadow growth evidence.",
        ]
        initial_release = ops_wrapper_initial_release_supervisor_run(
            {
                "session_id": session_id,
                "base_url": base_url,
                "host": host,
                "port": port,
                "pid": pid,
                "readiness_command": readiness_command,
                "timeout_seconds": int(payload.get("timeout_seconds") or 60),
                "approved_by": str(payload.get("approved_by") or "admin"),
                "approval_ref": str(payload.get("approval_ref") or "operator-review::release-product-smoke"),
                "prompts": smoke_prompts,
                "model": str(payload.get("model") or "nexusnet-offline"),
                "peer_node_id": str(payload.get("peer_node_id") or "release-product-smoke-peer"),
                "domain_ao": str(payload.get("domain_ao") or "FederationAO"),
                "update_id": str(payload.get("update_id") or ""),
            }
        )
        runtime = ops_wrapper_release_runtime(session_id=session_id)
        readiness = ops_wrapper_release_readiness(session_id=session_id)
        status_card = ops_wrapper_status_card(session_id=session_id)
        session_lifecycle = ops_wrapper_session_lifecycle(session_id=session_id)
        visualizer = ops_brain_visualizer_state(session_id=session_id)
        overlay = visualizer.get("overlay_state") if isinstance(visualizer, dict) else {}
        control_panel = overlay.get("control_panel") if isinstance(overlay, dict) else {}
        if not isinstance(control_panel, dict):
            control_panel = {}
        return release_wrapper_runtime.record_release_product_smoke_run(
            session_id=session_id,
            base_url=base_url,
            host=host,
            port=port,
            pid=pid,
            readiness_command=readiness_command,
            initial_release_supervisor=initial_release,
            runtime=runtime,
            readiness=readiness,
            status_card=status_card,
            session_lifecycle=session_lifecycle,
            control_panel=control_panel,
        )

    @application.get("/ops/brain/canon/autonomous-updates")
    def ops_brain_canon_autonomous_updates():
        return services.brain_autonomous_updates.scorecard()

    @application.get("/ops/brain/genai-observability")
    def ops_brain_genai_observability(limit: int = 50):
        return services.brain_genai_observability.summary(limit=limit)

    @application.post("/ops/brain/genai-observability/traces")
    def ops_brain_genai_observability_traces(payload: dict[str, Any] = Body(...)):
        request = GenAITraceEventRequest.model_validate(payload)
        return services.brain_genai_observability.record(request)

    @application.get("/ops/brain/trace-schema")
    def ops_brain_trace_schema():
        return services.brain_genai_observability.trace_schema()

    @application.get("/ops/brain/trace-schema/otel-projection/{trace_id}")
    def ops_brain_trace_schema_otel_projection(trace_id: str):
        projection = services.brain_genai_observability.otel_projection(trace_id)
        if projection is None:
            raise HTTPException(status_code=404, detail=f"Trace not found: {trace_id}")
        return projection

    @application.get("/ops/brain/canon/genai-observability")
    def ops_brain_canon_genai_observability():
        return services.brain_genai_observability.scorecard()

    @application.get("/ops/brain/concept-telemetry")
    def ops_brain_concept_telemetry():
        return services.brain_concept_telemetry.summary()

    @application.post("/ops/brain/concept-telemetry/concepts")
    def ops_brain_concept_telemetry_concepts(payload: dict[str, Any] = Body(...)):
        return services.brain_concept_telemetry.record_concept(ConceptTelemetryRequest.model_validate(payload))

    @application.post("/ops/brain/concept-telemetry/sae-experiments")
    def ops_brain_concept_telemetry_sae(payload: dict[str, Any] = Body(...)):
        return services.brain_concept_telemetry.record_sae_experiment(SAEExperimentRequest.model_validate(payload))

    @application.get("/ops/brain/forward-radar")
    def ops_brain_forward_radar(limit: int = 50):
        return services.brain_forward_radar.summary(limit=limit)

    @application.get("/ops/brain/forward-radar/{radar_id}")
    def ops_brain_forward_radar_candidate(radar_id: str):
        candidate = services.brain_forward_radar.get(radar_id)
        if candidate is None:
            raise HTTPException(status_code=404, detail=f"Forward Radar candidate not found: {radar_id}")
        return candidate

    @application.post("/ops/brain/forward-radar/{radar_id}/review")
    def ops_brain_forward_radar_review(radar_id: str, payload: dict[str, Any] = Body(...)):
        request = ForwardRadarCandidateRequest.model_validate(payload)
        return services.brain_forward_radar.review(radar_id, request)

    @application.get("/ops/brain/canon/forward-radar")
    def ops_brain_canon_forward_radar():
        return services.brain_forward_radar.scorecard()

    @application.get("/ops/brain/self-review")
    def ops_brain_self_review(limit: int = 50):
        return services.brain_self_review.summary(limit=limit)

    @application.post("/ops/brain/self-review/reviews")
    def ops_brain_self_review_reviews(payload: dict[str, Any] = Body(...)):
        request = SelfReviewRequest.model_validate(payload)
        return services.brain_self_review.review(request)

    @application.get("/ops/brain/canon/self-review")
    def ops_brain_canon_self_review():
        return services.brain_self_review.scorecard()

    @application.get("/ops/brain/memory-quality")
    def ops_brain_memory_quality(limit: int = 50):
        return services.brain_memory_quality.summary(limit=limit)

    @application.post("/ops/brain/memory-quality/claims")
    def ops_brain_memory_quality_claims(payload: dict[str, Any] = Body(...)):
        request = SourceClaimRequest.model_validate(payload)
        return services.brain_memory_quality.record_claim(request)

    @application.get("/ops/brain/canon/memory-quality")
    def ops_brain_canon_memory_quality():
        return services.brain_memory_quality.scorecard()

    @application.get("/ops/brain/memory/engram")
    def ops_brain_memory_engram():
        return services.brain_engram_memory.summary()

    @application.post("/ops/brain/memory/engram/records")
    def ops_brain_memory_engram_records(payload: dict[str, Any] = Body(...)):
        request = EngramRecordRequest.model_validate(payload)
        return services.brain_engram_memory.store(request)

    @application.post("/ops/brain/memory/engram/lookup")
    def ops_brain_memory_engram_lookup(payload: dict[str, Any] = Body(...)):
        request = EngramLookupRequest.model_validate(payload)
        return services.brain_engram_memory.lookup(request)

    @application.get("/ops/brain/canon/engram-memory")
    def ops_brain_canon_engram_memory():
        return services.brain_engram_memory.scorecard()

    @application.get("/ops/brain/canon/protocol-trust")
    def ops_brain_canon_protocol_trust(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return protocol_trust_scorecard(realization)

    @application.get("/ops/brain/canon/communication-integration")
    def ops_brain_canon_communication_integration(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return communication_integration_scorecard(realization)

    @application.get("/ops/brain/canon/eval-suite")
    def ops_brain_canon_eval_suite(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return eval_suite_scorecard(realization)

    @application.get("/ops/brain/canon/memory-provenance")
    def ops_brain_canon_memory_provenance(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return memory_provenance_scorecard(realization)

    @application.get("/ops/brain/canon/artifact-trust")
    def ops_brain_canon_artifact_trust(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return artifact_trust_scorecard(realization)

    @application.get("/ops/brain/canon/hardware-matrix")
    def ops_brain_canon_hardware_matrix(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return hardware_matrix_scorecard(realization)

    @application.get("/ops/brain/hardware-matrix")
    def ops_brain_hardware_matrix(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return hardware_matrix_scorecard(realization)

    @application.get("/ops/brain/canon/visualops")
    def ops_brain_canon_visualops(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return visualops_scorecard(realization)

    @application.get("/ops/brain/canon/input-ingestion")
    def ops_brain_canon_input_ingestion(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        operations_summary = services.brain_operations.summary(session_id=session_id)
        return input_ingestion_scorecard(realization, operations_summary=operations_summary)

    @application.get("/ops/brain/canon/live-flow")
    def ops_brain_canon_live_flow(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        operations_summary = services.brain_operations.summary(session_id=session_id)
        return live_flow_scorecard(realization, operations_summary=operations_summary)

    @application.get("/ops/brain/canon/neural-core")
    def ops_brain_canon_neural_core(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        operations_summary = services.brain_operations.summary(session_id=session_id)
        return neural_core_scorecard(realization, operations_summary=operations_summary)

    @application.get("/ops/brain/canon/tool-execution")
    def ops_brain_canon_tool_execution(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return tool_execution_scorecard(realization)

    @application.get("/ops/brain/canon/output-delivery")
    def ops_brain_canon_output_delivery(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return output_delivery_scorecard(realization)

    @application.get("/ops/brain/canon/ao-hive")
    def ops_brain_canon_ao_hive(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        operations_summary = services.brain_operations.summary(session_id=session_id)
        return ao_hive_scorecard(
            realization,
            ao_snapshot=services.brain_aos.snapshot().model_dump(mode="json"),
            operations_summary=operations_summary,
        )

    @application.get("/ops/brain/canon/experts-hive")
    def ops_brain_canon_experts_hive(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        operations_summary = services.brain_operations.summary(session_id=session_id)
        return experts_hive_scorecard(
            realization,
            operations_summary=operations_summary,
        )

    @application.get("/ops/brain/canon/observability")
    def ops_brain_canon_observability(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return observability_scorecard(realization)

    @application.get("/ops/brain/canon/security-governance")
    def ops_brain_canon_security_governance(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return security_governance_scorecard(realization)

    @application.get("/ops/brain/canon/blackbox")
    def ops_brain_canon_blackbox(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        payload = blackbox_recorder(realization)
        payload.setdefault("scorecard_refs", {})["growth_engine"] = "/ops/brain/canon/growth-engine"
        payload.setdefault("scorecard_refs", {})["knowledge_artifacts"] = "/ops/brain/canon/knowledge-artifacts"
        return payload

    @application.get("/ops/brain/canon/hive-consensus")
    def ops_brain_canon_hive_consensus(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        operations_summary = services.brain_operations.summary(session_id=session_id)
        control_panel = services.brain_visualizer.state(session_id=session_id)["overlay_state"]["control_panel"]
        return hive_consensus_scorecard(
            realization,
            operations_summary=operations_summary,
            hive_mind=control_panel.get("hive_mind") or {},
        )

    @application.get("/ops/brain/canon/researcher-swarm")
    def ops_brain_canon_researcher_swarm(session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        return researcher_swarm_scorecard(realization)

    @application.get("/ops/brain/canon/answers/{question_id}")
    def ops_brain_canon_answers(question_id: str, session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        answer = answer_operator_question(realization, question_id)
        if answer is None:
            raise HTTPException(status_code=404, detail=f"Unknown canon operator question: {question_id}")
        return answer

    @application.post("/ops/brain/canon/answers/{question_id}/events")
    def ops_brain_canon_answer_events(
        question_id: str,
        actor: str = Body(...),
        detail: str = Body(...),
        session_id: str | None = Body(default=None),
        command_id: str | None = Body(default=None),
        metadata: dict[str, Any] | None = Body(default=None),
    ):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        answer = answer_operator_question(realization, question_id)
        if answer is None:
            raise HTTPException(status_code=404, detail=f"Unknown canon operator question: {question_id}")
        selected_command_id = command_id or answer.get("active_command_id") or (
            (realization.get("live_bindings") or {}).get("active_command_id")
        )
        if not selected_command_id:
            raise HTTPException(status_code=409, detail="No active NexusBrain command is available for this answer event.")
        event_payload = services.brain_operations.record_event(
            command_id=selected_command_id,
            session_id=session_id,
            event_type=question_id,
            actor=actor,
            detail=detail,
            metadata={
                **(metadata or {}),
                "canon_question_id": question_id,
                "surface_id": answer.get("surface_id"),
            },
        )
        updated_realization = services.brain_visualizer.canon_realization(session_id=session_id)
        updated_answer = answer_operator_question(updated_realization, question_id)
        return {
            "status_label": "LOCKED CANON",
            "event": event_payload["event"],
            "command": event_payload["command"],
            "answer": updated_answer,
        }

    @application.get("/ops/brain/canon/surfaces/{surface_id}")
    def ops_brain_canon_surfaces(surface_id: str, session_id: str | None = None):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        drilldown = surface_drilldown(realization, surface_id)
        if drilldown is None:
            raise HTTPException(status_code=404, detail=f"Unknown canon surface: {surface_id}")
        return drilldown

    @application.post("/ops/brain/canon/realize-next")
    def ops_brain_canon_realize_next(
        session_id: str | None = Body(default=None),
        surface_id: str | None = Body(default=None),
    ):
        realization = services.brain_visualizer.canon_realization(session_id=session_id)
        surfaces = realization.get("surfaces") or {}
        target = None
        if surface_id:
            target = surfaces.get(surface_id)
            if not target:
                raise HTTPException(status_code=404, detail=f"Unknown canon surface: {surface_id}")
        else:
            for item in realization.get("blocking_items") or []:
                target = surfaces.get(item.get("surface_id"))
                if target:
                    break
        if not target:
            raise HTTPException(status_code=409, detail="No canon realization gap is available to command.")
        command_text = (
            f"Realize Canon surface {target.get('label')}: {target.get('next_action')} "
            f"Requirement: {target.get('canon_requirement')} "
            f"Promotion gate: {target.get('promotion_gate')}"
        )
        issued = services.brain_operations.issue_command(
            session_id=session_id,
            command_text=command_text,
            priority="high",
            target_surface="mission-control-cockpit",
            context={
                "source": "canon-realization",
                "surface_id": target.get("surface_id"),
                "surface_state": target.get("state"),
                "canon_requirement": target.get("canon_requirement"),
            },
        )
        return {
            "status_label": "LOCKED CANON",
            "target_surface": target,
            "command": issued["command"],
            "signal_contract": issued["signal_contract"],
            "canon_binding": issued["canon_binding"],
        }

    @application.get("/ops/brain/visualizer/replay")
    def ops_brain_visualizer_replay(session_id: str | None = None, limit: int = 12):
        return services.brain_visualizer.replay(session_id=session_id, limit=limit)

    @application.get("/ops/brain/visualizer/disagreements/compare")
    def ops_brain_visualizer_disagreement_compare(left_artifact_id: str, right_artifact_id: str):
        return services.brain_visualizer.compare_disagreements(left_artifact_id, right_artifact_id)

    @application.get("/ops/brain/visualizer/replacement-readiness/compare")
    def ops_brain_visualizer_replacement_compare(left_report_id: str, right_report_id: str):
        return services.brain_visualizer.compare_replacement_readiness(left_report_id, right_report_id)

    @application.get("/ops/brain/visualizer/route-activity/compare")
    def ops_brain_visualizer_route_compare(session_id: str | None = None, left_window: int = 6, right_window: int = 24):
        return services.brain_visualizer.compare_route_activity(
            session_id=session_id,
            left_window=left_window,
            right_window=right_window,
        )

    @application.get("/ops/brain/teachers")
    def ops_brain_teachers():
        return {
            "status_label": "LOCKED CANON",
            "profiles": [profile.model_dump(mode="json") for profile in services.brain_teachers.list_profiles()],
            "attached": [teacher.model_dump(mode="json") for teacher in services.brain_teachers.list_attached()],
            "assignments": [assignment.model_dump(mode="json") for assignment in services.brain_teachers.list_assignments()],
            "active_teacher": services.brain_teachers.active_teacher().model_dump(mode="json") if services.brain_teachers.active_teacher() else None,
            "metadata": services.brain_teachers.metadata(),
            "routing_policy": services.brain_teachers.routing_policy,
            "regimens": services.brain_teachers.regimens,
            "schema_registry": services.brain_teachers.schema_registry.metadata(),
            "schema_manifest_path": services.brain_teachers.schema_manifest_path,
            "retirement": [decision.model_dump(mode="json") for decision in services.brain_teachers.retirement_decisions()],
            "evidence_bundles": services.brain_teacher_evidence.list_bundles(limit=50),
            "disagreement_artifacts": services.store.list_teacher_disagreement_artifacts(limit=50),
            "scorecards": services.store.list_teacher_scorecards(limit=50),
            "trend_scorecards": services.store.list_teacher_trend_scorecards(limit=50),
            "takeover_trends": services.store.list_takeover_trend_reports(limit=50),
            "fleet_summaries": services.store.list_teacher_benchmark_fleet_summaries(limit=50),
            "cohort_scorecards": services.store.list_teacher_cohort_scorecards(limit=50),
            "replacement_readiness_reports": services.store.list_replacement_readiness_reports(limit=50),
            "retirement_shadow_log": services.store.list_retirement_shadow_records(limit=50),
        }

    @application.get("/ops/brain/teachers/schema")
    def ops_brain_teacher_schema():
        return {
            "status_label": "LOCKED CANON",
            "schema_registry": services.brain_teachers.schema_registry.metadata(),
            "schema_manifest_path": services.brain_teachers.schema_manifest_path,
        }

    @application.get("/ops/brain/teachers/evidence")
    def ops_brain_teacher_evidence(subject: str | None = None, limit: int = 50):
        return {
            "status_label": "LOCKED CANON",
            "items": services.brain_teacher_evidence.list_bundles(subject=subject, limit=limit),
        }

    @application.get("/ops/brain/teachers/disagreements")
    def ops_brain_teacher_disagreements(subject: str | None = None, limit: int = 50):
        return {
            "status_label": "LOCKED CANON",
            "items": services.store.list_teacher_disagreement_artifacts(subject=subject, limit=limit),
        }

    @application.get("/ops/brain/teachers/trends")
    def ops_brain_teacher_trends(subject: str | None = None, benchmark_family_id: str | None = None, limit: int = 50):
        return {
            "status_label": "LOCKED CANON",
            "teacher_trends": services.store.list_teacher_trend_scorecards(
                subject=subject,
                benchmark_family_id=benchmark_family_id,
                limit=limit,
            ),
            "takeover_trends": services.store.list_takeover_trend_reports(subject=subject, limit=limit),
        }

    @application.get("/ops/brain/teachers/fleets")
    def ops_brain_teacher_fleets(
        fleet_id: str | None = None,
        subject: str | None = None,
        window_id: str = "medium",
        teacher_pair_id: str | None = None,
        budget_class: str | None = None,
        output_form: str | None = None,
        risk_tier: str | None = None,
        locality: str | None = None,
        hardware_class: str | None = None,
        lineage: str | None = None,
        limit: int = 50,
    ):
        if fleet_id:
            summary = services.brain_teacher_fleets.build(
                fleet_id=fleet_id,
                window_id=window_id,
                subject=subject,
                teacher_pair_id=teacher_pair_id,
                budget_class=budget_class,
                output_form=output_form,
                risk_tier=risk_tier,
                locality=locality,
                hardware_class=hardware_class,
                lineage=lineage,
            )
            items = [summary.model_dump(mode="json")]
        else:
            items = services.store.list_teacher_benchmark_fleet_summaries(fleet_id=fleet_id, subject=subject, limit=limit)
        return {
            "status_label": "LOCKED CANON",
            "registry": services.brain_teachers.fleet_registry.metadata(),
            "windows": services.brain_teachers.fleet_window_registry.metadata(),
            "items": items,
        }

    @application.get("/ops/brain/teachers/cohorts")
    def ops_brain_teacher_cohorts(
        fleet_id: str,
        subject: str | None = None,
        window_id: str = "medium",
        teacher_pair_id: str | None = None,
        budget_class: str | None = None,
        output_form: str | None = None,
        risk_tier: str | None = None,
        locality: str | None = None,
        hardware_class: str | None = None,
        lineage: str | None = None,
        native_takeover_candidate_id: str | None = None,
        limit: int = 50,
    ):
        cohort = services.brain_teacher_cohorts.build(
            fleet_id=fleet_id,
            window_id=window_id,
            subject=subject,
            teacher_pair_id=teacher_pair_id,
            budget_class=budget_class,
            output_form=output_form,
            risk_tier=risk_tier,
            locality=locality,
            hardware_class=hardware_class,
            lineage=lineage,
            native_takeover_candidate_id=native_takeover_candidate_id,
        )
        return {
            "status_label": "LOCKED CANON",
            "thresholds": services.brain_teachers.cohort_threshold_registry.metadata(),
            "items": [cohort.model_dump(mode="json")] + services.store.list_teacher_cohort_scorecards(fleet_id=fleet_id, subject=subject, limit=limit - 1),
        }

    @application.get("/ops/brain/teachers/evidence/diff")
    def ops_brain_teacher_evidence_diff(left_bundle_id: str, right_bundle_id: str):
        left = services.brain_teacher_evidence.bundle_payload(left_bundle_id)
        right = services.brain_teacher_evidence.bundle_payload(right_bundle_id)
        return {
            "status_label": "LOCKED CANON",
            "left": left,
            "right": right,
            "scene_delta": services.brain_visualizer.telemetry.evidence_scene_delta(left=left, right=right),
            "diff": {
                "subjects": [left.get("subject"), right.get("subject")],
                "registry_layers": [left.get("registry_layer"), right.get("registry_layer")],
                "benchmark_families": {
                    "left_only": sorted(set(left.get("benchmark_families", [])) - set(right.get("benchmark_families", []))),
                    "right_only": sorted(set(right.get("benchmark_families", [])) - set(left.get("benchmark_families", []))),
                    "shared": sorted(set(left.get("benchmark_families", [])) & set(right.get("benchmark_families", []))),
                },
                "threshold_sets": [left.get("threshold_set_id"), right.get("threshold_set_id")],
                "trend_refs": [left.get("trend_scorecards", []), right.get("trend_scorecards", [])],
            },
        }

    @application.get("/ops/brain/teachers/cohorts/compare")
    def ops_brain_teacher_cohort_compare(fleet_id: str, subject: str | None = None, left_window: str = "short", right_window: str = "long"):
        left = services.brain_teacher_cohorts.build(fleet_id=fleet_id, window_id=left_window, subject=subject)
        right = services.brain_teacher_cohorts.build(fleet_id=fleet_id, window_id=right_window, subject=subject)
        return {
            "status_label": "LOCKED CANON",
            "left": left.model_dump(mode="json"),
            "right": right.model_dump(mode="json"),
            "scene_delta": services.brain_visualizer.telemetry.cohort_scene_delta(
                left=left.model_dump(mode="json"),
                right=right.model_dump(mode="json"),
            ),
            "diff": {
                "stability_score_delta": round(right.stability_score - left.stability_score, 3),
                "variance_delta": round(right.variance - left.variance, 4),
                "outperformance_delta": round(right.outperformance_consistency - left.outperformance_consistency, 3),
            },
        }

    @application.post("/ops/brain/teachers/attach")
    def ops_brain_teachers_attach(request: ModelAttachRequest):
        attached = services.brain_teachers.attach(services.brain, request)
        return attached.model_dump(mode="json")

    @application.post("/ops/brain/teachers/select")
    def ops_brain_teachers_select(request: ModelAttachRequest):
        if request.teacher_id and services.brain_teachers.set_active(request.teacher_id):
            return services.brain_teachers.active_teacher().model_dump(mode="json")
        attached = services.brain_teachers.attach(services.brain, request)
        return attached.model_dump(mode="json")

    @application.get("/ops/brain/aos")
    def ops_brain_aos():
        return services.brain_aos.snapshot().model_dump(mode="json")

    @application.get("/ops/brain/agents")
    def ops_brain_agents(session_id: str | None = None):
        return {
            "status_label": "LOCKED CANON",
            "capabilities": [capability.model_dump(mode="json") for capability in services.brain_agent_registry.list_capabilities()],
            "session_provenance": services.brain_agent_registry.session_provenance(session_id).model_dump(mode="json") if session_id else None,
        }

    @application.get("/ops/brain/gateway")
    def ops_brain_gateway(
        session_id: str | None = None,
        agent_id: str = "standard-wrapper-agent",
        workspace_id: str = "default",
        requested_tools: str | None = None,
        requested_extensions: str | None = None,
        require_user_approval: bool = False,
        trigger_source: str = "gateway:direct",
    ):
        requested_tool_list = [tool.strip() for tool in (requested_tools or "").split(",") if tool.strip()]
        requested_extension_list = [bundle.strip() for bundle in (requested_extensions or "").split(",") if bundle.strip()]
        if requested_tool_list or requested_extension_list:
            return services.brain_gateway.resolve(
                agent_id=agent_id,
                workspace_id=workspace_id,
                requested_tools=requested_tool_list,
                requested_extensions=requested_extension_list,
                require_user_approval=require_user_approval,
                trigger_source=trigger_source,
                linked_trace_ids=_latest_trace_ids(session_id),
                record_gateway_flow=True,
            )
        return services.brain_gateway.summary(session_id=session_id, agent_id=agent_id, workspace_id=workspace_id)

    @application.get("/ops/brain/gateway/history")
    def ops_brain_gateway_history(
        agent_id: str | None = None,
        workspace_id: str | None = None,
        trigger_source: str | None = None,
        status: str | None = None,
        limit: int = 12,
    ):
        return services.brain_gateway.history_summary(
            agent_id=agent_id,
            workspace_id=workspace_id,
            trigger_source=trigger_source,
            status=status,
            limit=limit,
        )

    @application.get("/ops/brain/gateway/history/compare")
    def ops_brain_gateway_history_compare(left_execution_id: str, right_execution_id: str):
        comparison = services.brain_gateway.compare_history(left_execution_id, right_execution_id)
        if comparison is None:
            raise HTTPException(status_code=404, detail="gateway execution comparison unavailable")
        return comparison

    @application.get("/ops/brain/gateway/history/{execution_id}")
    def ops_brain_gateway_history_detail(execution_id: str):
        detail = services.brain_gateway.history_detail(execution_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="gateway execution not found")
        return detail

    @application.get("/ops/brain/runtime/init")
    def ops_brain_runtime_init(use_case: str | None = None):
        if use_case:
            return {
                "status_label": "STRONG ACCEPTED DIRECTION",
                "recommendation": services.brain_runtime_init.recommend(use_case=use_case),
                "summary": services.brain_runtime_init.summary(),
            }
        return services.brain_runtime_init.summary()

    @application.get("/ops/brain/runtime/doctor")
    def ops_brain_runtime_doctor():
        return services.brain_runtime_doctor.summary()

    @application.get("/ops/brain/memory/planes")
    def ops_brain_memory_planes():
        return {
            "metadata": services.brain_memory_planes.metadata(),
            "configs": [config.model_dump(mode="json") for config in services.brain_memory_planes.list_configs()],
            "projection_adapters": [adapter.model_dump(mode="json") for adapter in services.brain_memory_planes.projection_adapters()],
        }

    @application.get("/ops/brain/memory/projections/{projection_name}")
    def ops_brain_memory_projection(projection_name: str, session_id: str):
        return services.brain_ui_surface.projection(session_id, projection_name)

    @application.get("/ops/brain/runtime-profile")
    def ops_brain_runtime_profile(model_hint: str | None = None):
        return {
            **services.brain_runtime_optimizer.summary(model_hint),
            "brain_runtime": services.brain_runtime_registry.summary(model_hint),
            "edge_vision_lane": services.brain_edge_vision.summary(),
        }

    @application.get("/ops/brain/vision/edge-lane")
    def ops_brain_vision_edge_lane():
        return services.brain_edge_vision.summary()

    @application.get("/ops/brain/vision/edge-benchmark")
    def ops_brain_vision_edge_benchmark(provider_id: str | None = None):
        return services.brain_edge_vision.benchmark(provider_id=provider_id)

    @application.get("/ops/brain/multimodal-computer-use")
    def ops_brain_multimodal_computer_use(limit: int = 50):
        return services.brain_multimodal_computer_use.summary(limit=limit)

    @application.get("/ops/brain/operator-events")
    def ops_brain_operator_events():
        return services.brain_operator_events.summary()

    @application.post("/ops/brain/operator-events")
    def ops_brain_operator_events_record(payload: dict[str, Any] = Body(...)):
        return services.brain_operator_events.record(OperatorEventRequest.model_validate(payload))

    @application.post("/ops/brain/multimodal-computer-use/plans")
    def ops_brain_multimodal_computer_use_plans(payload: dict[str, Any] = Body(...)):
        request = ComputerUsePlanRequest.model_validate(payload)
        return services.brain_multimodal_computer_use.plan(request)

    @application.get("/ops/brain/computer-use/safety-cases")
    def ops_brain_computer_use_safety_cases():
        return services.brain_multimodal_computer_use.safety_cases()

    @application.get("/ops/brain/canon/multimodal-computer-use")
    def ops_brain_canon_multimodal_computer_use():
        return services.brain_multimodal_computer_use.scorecard()

    @application.get("/ops/brain/recipes")
    def ops_brain_recipes():
        return services.brain_recipe_catalog.summary()

    @application.get("/ops/brain/recipes/history")
    def ops_brain_recipe_history(
        recipe_id: str | None = None,
        schedule_id: str | None = None,
        trigger_source: str | None = None,
        status: str | None = None,
        limit: int = 12,
    ):
        return services.brain_recipe_history.summary(
            execution_kind="recipe",
            recipe_id=recipe_id,
            schedule_id=schedule_id,
            trigger_source=trigger_source,
            status=status,
            limit=limit,
        )

    @application.get("/ops/brain/recipes/history/compare")
    def ops_brain_recipe_history_compare(left_execution_id: str, right_execution_id: str):
        comparison = services.brain_recipe_history.compare(left_execution_id, right_execution_id)
        if comparison is None:
            raise HTTPException(status_code=404, detail="recipe execution comparison unavailable")
        return comparison

    @application.get("/ops/brain/recipes/history/{execution_id}")
    def ops_brain_recipe_history_detail(execution_id: str):
        detail = services.brain_recipe_history.detail(execution_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="recipe execution not found")
        return detail

    @application.post("/ops/brain/recipes/execute")
    def ops_brain_recipe_execute(
        recipe_id: str = Body(...),
        trigger_source: str = Body(default="manual"),
        session_id: str | None = Body(default=None),
        workspace_id: str = Body(default="default"),
        agent_id: str | None = Body(default=None),
        parameter_set: dict | None = Body(default=None),
        linked_trace_ids: list[str] | None = Body(default=None),
        linked_subagent_ids: list[str] | None = Body(default=None),
        policy_path: list[dict] | None = Body(default=None),
        approval_path: dict | None = Body(default=None),
        artifacts_produced: list[str] | None = Body(default=None),
        status: str = Body(default="success"),
        schedule_id: str | None = Body(default=None),
        metadata: dict | None = Body(default=None),
    ):
        item = services.brain_recipe_catalog.get(recipe_id)
        if item is None or item.get("kind") != "recipe":
            raise HTTPException(status_code=404, detail="recipe not found")
        execution_context = _build_goose_execution_context(
            item=item,
            session_id=session_id,
            agent_id=_recipe_agent_id(item, agent_id),
            workspace_id=workspace_id,
            trigger_source=trigger_source,
            linked_trace_ids=linked_trace_ids or [],
            policy_path=policy_path or [],
            approval_path=approval_path or {},
        )
        execution = services.brain_recipe_history.execute(
            recipe_id=recipe_id,
            trigger_source=trigger_source,
            parameter_set=parameter_set or {},
            linked_trace_ids=execution_context["linked_trace_ids"],
            linked_subagent_ids=linked_subagent_ids or [],
            policy_path=execution_context["policy_path"],
            approval_path=execution_context["approval_path"],
            gateway_decision_path=execution_context["gateway_decision_path"],
            gateway_execution_id=execution_context["gateway_execution_id"],
            gateway_report_id=execution_context["gateway_report_id"],
            execution_path=execution_context["execution_path"],
            approval_fallback_chain=execution_context["approval_fallback_chain"],
            adversary_review_report_ids=execution_context["adversary_review_report_ids"],
            linked_report_ids=execution_context["linked_report_ids"],
            extension_bundle_ids=execution_context["extension_bundle_ids"],
            extension_policy_set_ids=execution_context["extension_policy_set_ids"],
            extension_bundle_families=execution_context["extension_bundle_families"],
            extension_provenance=execution_context["extension_provenance"],
            artifacts_produced=sorted(set([*(artifacts_produced or []), *execution_context["artifacts_produced"]])),
            status=status,
            schedule_id=schedule_id,
            metadata={**execution_context["metadata"], **(metadata or {})},
        )
        workflow_id = _scheduled_workflow_id(trigger_source=trigger_source, schedule_id=schedule_id)
        if workflow_id:
            scheduled_artifact = services.brain_scheduled_agents.record_execution(workflow_id=workflow_id, execution=execution)
            if scheduled_artifact is not None:
                execution["scheduled_artifact"] = scheduled_artifact
        return execution

    @application.get("/ops/brain/runbooks")
    def ops_brain_runbooks():
        summary = services.brain_recipe_catalog.summary()
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "runbook_count": summary.get("runbook_count", 0),
            "items": [item for item in summary.get("items", []) if item.get("kind") == "runbook"],
        }

    @application.get("/ops/brain/runbooks/history")
    def ops_brain_runbook_history(
        recipe_id: str | None = None,
        schedule_id: str | None = None,
        trigger_source: str | None = None,
        status: str | None = None,
        limit: int = 12,
    ):
        return services.brain_runbook_history.summary(
            recipe_id=recipe_id,
            schedule_id=schedule_id,
            trigger_source=trigger_source,
            status=status,
            limit=limit,
        )

    @application.get("/ops/brain/runbooks/history/compare")
    def ops_brain_runbook_history_compare(left_execution_id: str, right_execution_id: str):
        comparison = services.brain_runbook_history.compare(left_execution_id, right_execution_id)
        if comparison is None:
            raise HTTPException(status_code=404, detail="runbook execution comparison unavailable")
        return comparison

    @application.get("/ops/brain/runbooks/history/{execution_id}")
    def ops_brain_runbook_history_detail(execution_id: str):
        detail = services.brain_runbook_history.detail(execution_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="runbook execution not found")
        return detail

    @application.post("/ops/brain/runbooks/execute")
    def ops_brain_runbook_execute(
        recipe_id: str = Body(...),
        trigger_source: str = Body(default="manual"),
        session_id: str | None = Body(default=None),
        workspace_id: str = Body(default="default"),
        agent_id: str | None = Body(default=None),
        parameter_set: dict | None = Body(default=None),
        linked_trace_ids: list[str] | None = Body(default=None),
        linked_subagent_ids: list[str] | None = Body(default=None),
        policy_path: list[dict] | None = Body(default=None),
        approval_path: dict | None = Body(default=None),
        artifacts_produced: list[str] | None = Body(default=None),
        status: str = Body(default="success"),
        schedule_id: str | None = Body(default=None),
        metadata: dict | None = Body(default=None),
    ):
        item = services.brain_recipe_catalog.get(recipe_id)
        if item is None or item.get("kind") != "runbook":
            raise HTTPException(status_code=404, detail="runbook not found")
        execution_context = _build_goose_execution_context(
            item=item,
            session_id=session_id,
            agent_id=_recipe_agent_id(item, agent_id),
            workspace_id=workspace_id,
            trigger_source=trigger_source,
            linked_trace_ids=linked_trace_ids or [],
            policy_path=policy_path or [],
            approval_path=approval_path or {},
        )
        execution = services.brain_runbook_history.execute(
            recipe_id=recipe_id,
            trigger_source=trigger_source,
            parameter_set=parameter_set or {},
            linked_trace_ids=execution_context["linked_trace_ids"],
            linked_subagent_ids=linked_subagent_ids or [],
            policy_path=execution_context["policy_path"],
            approval_path=execution_context["approval_path"],
            gateway_decision_path=execution_context["gateway_decision_path"],
            gateway_execution_id=execution_context["gateway_execution_id"],
            gateway_report_id=execution_context["gateway_report_id"],
            execution_path=execution_context["execution_path"],
            approval_fallback_chain=execution_context["approval_fallback_chain"],
            adversary_review_report_ids=execution_context["adversary_review_report_ids"],
            linked_report_ids=execution_context["linked_report_ids"],
            extension_bundle_ids=execution_context["extension_bundle_ids"],
            extension_policy_set_ids=execution_context["extension_policy_set_ids"],
            extension_bundle_families=execution_context["extension_bundle_families"],
            extension_provenance=execution_context["extension_provenance"],
            artifacts_produced=sorted(set([*(artifacts_produced or []), *execution_context["artifacts_produced"]])),
            status=status,
            schedule_id=schedule_id,
            metadata={**execution_context["metadata"], **(metadata or {})},
        )
        workflow_id = _scheduled_workflow_id(trigger_source=trigger_source, schedule_id=schedule_id)
        if workflow_id:
            scheduled_artifact = services.brain_scheduled_agents.record_execution(workflow_id=workflow_id, execution=execution)
            if scheduled_artifact is not None:
                execution["scheduled_artifact"] = scheduled_artifact
        return execution

    @application.get("/ops/brain/skills/catalog")
    def ops_brain_skills_catalog(source_id: str | None = None, category: str | None = None):
        if source_id:
            return {
                "status_label": "STRONG ACCEPTED DIRECTION",
                "sync_plan": services.brain_skill_catalog.sync_plan(source_id=source_id, category=category),
                "summary": services.brain_skill_catalog.summary(),
            }
        return services.brain_skill_catalog.summary()

    @application.get("/ops/brain/extensions")
    def ops_brain_extensions(workspace_id: str = "default"):
        return services.brain_extension_catalog.summary(workspace_id=workspace_id)

    @application.get("/ops/brain/extensions/policy-sets")
    def ops_brain_extension_policy_sets(workspace_id: str = "default"):
        return services.brain_extension_catalog.policy_set_summary(workspace_id=workspace_id)

    @application.get("/ops/brain/extensions/policy-sets/{policy_set_id}")
    def ops_brain_extension_policy_set_detail(policy_set_id: str, workspace_id: str = "default", version: str | None = None):
        detail = services.brain_extension_catalog.policy_set_detail(policy_set_id=policy_set_id, version=version, workspace_id=workspace_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="extension policy set not found")
        return detail

    @application.get("/ops/brain/extensions/policy-history")
    def ops_brain_extension_policy_history(workspace_id: str = "default"):
        return services.brain_extension_catalog.policy_history_summary(workspace_id=workspace_id)

    @application.get("/ops/brain/extensions/policy-history/compare")
    def ops_brain_extension_policy_history_compare(
        left_policy_set_id: str,
        right_policy_set_id: str,
        workspace_id: str = "default",
        left_version: str | None = None,
        right_version: str | None = None,
    ):
        comparison = services.brain_extension_catalog.compare_policy_history(
            left_policy_set_id=left_policy_set_id,
            right_policy_set_id=right_policy_set_id,
            left_version=left_version,
            right_version=right_version,
            workspace_id=workspace_id,
        )
        if comparison is None:
            raise HTTPException(status_code=404, detail="extension policy comparison unavailable")
        return comparison

    @application.get("/ops/brain/extensions/policy-history/{policy_set_id}")
    def ops_brain_extension_policy_history_detail(policy_set_id: str, workspace_id: str = "default", version: str | None = None):
        detail = services.brain_extension_catalog.policy_history_detail(policy_set_id=policy_set_id, version=version, workspace_id=workspace_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="extension policy history not found")
        return detail

    @application.get("/ops/brain/extensions/policy-rollouts")
    def ops_brain_extension_policy_rollouts():
        return services.brain_extension_catalog.policy_rollout_summary()

    @application.get("/ops/brain/extensions/certifications")
    def ops_brain_extension_certifications(workspace_id: str = "default"):
        return services.brain_extension_catalog.certification_summary(workspace_id=workspace_id)

    @application.get("/ops/brain/extensions/certifications/compare")
    def ops_brain_extension_certification_compare(left_artifact_id: str, right_artifact_id: str):
        comparison = services.brain_extension_catalog.compare_certifications(
            left_artifact_id=left_artifact_id,
            right_artifact_id=right_artifact_id,
        )
        if comparison is None:
            raise HTTPException(status_code=404, detail="extension certification comparison unavailable")
        return comparison

    @application.get("/ops/brain/extensions/certifications/{artifact_id}")
    def ops_brain_extension_certification_detail(artifact_id: str):
        detail = services.brain_extension_catalog.certification_detail(artifact_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="extension certification not found")
        return detail

    @application.get("/ops/brain/extensions/{bundle_id}")
    def ops_brain_extension_detail(bundle_id: str, workspace_id: str = "default"):
        detail = services.brain_extension_catalog.detail(bundle_id=bundle_id, workspace_id=workspace_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="extension bundle not found")
        return detail

    @application.get("/ops/brain/acp")
    def ops_brain_acp():
        return services.brain_acp_bridge.summary()

    @application.get("/ops/brain/acp/health")
    def ops_brain_acp_health():
        return services.brain_acp_bridge.health_summary()

    @application.get("/ops/brain/acp/providers/compare")
    def ops_brain_acp_provider_compare(left_provider_id: str, right_provider_id: str):
        comparison = services.brain_acp_bridge.compare_providers(left_provider_id, right_provider_id)
        if comparison is None:
            raise HTTPException(status_code=404, detail="acp provider comparison unavailable")
        return comparison

    @application.get("/ops/brain/acp/providers/{provider_id}")
    def ops_brain_acp_provider_detail(provider_id: str):
        detail = services.brain_acp_bridge.provider_detail(provider_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="acp provider not found")
        return detail

    @application.post("/ops/brain/acp/compatibility")
    def ops_brain_acp_compatibility(
        requested_tools: list[str] | None = Body(default=None),
        requested_extensions: list[str] | None = Body(default=None),
        subagent_mode: str | None = Body(default=None),
    ):
        return services.brain_acp_bridge.compatibility_summary(
            requested_tools=requested_tools or [],
            requested_extensions=requested_extensions or [],
            subagent_mode=subagent_mode,
        )

    @application.get("/ops/brain/subagents")
    def ops_brain_subagents():
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "subagents": services.brain_subagents.summary(),
            "delegation": services.brain_delegation.summary(),
            "parallel": services.brain_parallel.summary(),
        }

    @application.post("/ops/brain/subagents/plan")
    def ops_brain_subagents_plan(
        recipe_id: str = Body(...),
        parent_task: str = Body(...),
        mode: str = Body(default="sequential"),
        session_id: str | None = Body(default=None),
        workspace_id: str = Body(default="default"),
        agent_id: str | None = Body(default=None),
        trigger_source: str | None = Body(default=None),
        schedule_id: str | None = Body(default=None),
        linked_trace_ids: list[str] | None = Body(default=None),
        policy_path: list[dict] | None = Body(default=None),
        approval_path: dict | None = Body(default=None),
    ):
        recipe = services.brain_recipe_catalog.get(recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="recipe not found")
        plan = services.brain_delegation.plan(recipe_id=recipe_id, parent_task=parent_task)
        effective_trigger_source = trigger_source or f"subagent-plan:{mode}"
        plan_requested_tools = sorted({tool for worker in plan.get("workers", []) for tool in worker.get("requested_tools", []) if tool})
        plan_requested_extensions = sorted({ext for worker in plan.get("workers", []) for ext in worker.get("requested_extensions", []) if ext})
        execution_context = _build_goose_execution_context(
            item=recipe,
            session_id=session_id,
            agent_id=_recipe_agent_id(recipe, agent_id),
            workspace_id=workspace_id,
            trigger_source=effective_trigger_source,
            linked_trace_ids=linked_trace_ids or [],
            policy_path=policy_path or [],
            approval_path=approval_path or {},
            requested_tools=plan_requested_tools,
            requested_extensions=plan_requested_extensions,
        )
        execution = services.brain_subagents.execute(
            recipe_id=recipe_id,
            parent_task=parent_task,
            workers=plan.get("workers", []),
            mode=mode,
            trigger_source=effective_trigger_source,
            inherited_tools=_recipe_allowed_tools(recipe),
            inherited_extensions=[ext for item in plan.get("workers", []) for ext in item.get("requested_extensions", [])],
            linked_trace_ids=execution_context["linked_trace_ids"],
            policy_path=execution_context["policy_path"],
            approval_path=execution_context["approval_path"],
            gateway_resolution=execution_context["gateway_resolution"],
            approval_fallback_chain=execution_context["approval_fallback_chain"],
            adversary_review_report_ids=execution_context["adversary_review_report_ids"],
            linked_report_ids=execution_context["linked_report_ids"],
        )
        privilege_requested_tools = sorted({tool for worker in execution.get("workers", []) for tool in worker.get("requested_tools", [])})
        privilege_allowed_tools = sorted({tool for worker in execution.get("workers", []) for tool in worker.get("allowed_tools", [])})
        privilege_requested_extensions = sorted({ext for worker in execution.get("workers", []) for ext in worker.get("requested_extensions", [])})
        privilege_allowed_extensions = sorted({ext for worker in execution.get("workers", []) for ext in worker.get("allowed_extensions", [])})
        privilege_review = None
        if (
            privilege_requested_tools != privilege_allowed_tools
            or privilege_requested_extensions != privilege_allowed_extensions
        ):
            privilege_review = services.brain_adversary_review.review(
                subject=f"subagents::{execution.get('run_id')}",
                requested_tools=privilege_requested_tools,
                risk_level="high",
                reviewer_status="available",
                summary="Subagent privilege confusion requires bounded review.",
                policy_path=execution_context["policy_path"],
                multi_step=len(execution.get("workers", [])) > 1,
                approval_requested=bool(execution_context["approval_path"].get("require_user_approval")),
                approval_required=execution_context["approval_path"].get("decision") in {"ask", "allow-if-approved"},
                allowed_tools=privilege_allowed_tools,
                requested_extensions=privilege_requested_extensions,
                allowed_extensions=privilege_allowed_extensions,
                trigger_source=effective_trigger_source,
            )
        execution["gateway_resolution"] = execution_context["gateway_resolution"]
        execution["gateway_execution_history"] = ((execution_context.get("gateway_resolution") or {}).get("execution_history"))
        execution["privilege_review"] = privilege_review
        execution["linked_trace_ids"] = execution_context["linked_trace_ids"]
        if execution.get("artifact_path"):
            Path(execution["artifact_path"]).write_text(json.dumps(execution, indent=2), encoding="utf-8")
        history_service = services.brain_runbook_history if recipe.get("kind") == "runbook" else services.brain_recipe_history
        adversary_report_ids = list(execution_context["adversary_review_report_ids"])
        if privilege_review and ((privilege_review.get("report") or {}).get("report_id")):
            adversary_report_ids.append((privilege_review.get("report") or {}).get("report_id"))
        linked_report_ids = list(execution_context["linked_report_ids"])
        if privilege_review and ((privilege_review.get("report") or {}).get("report_id")):
            linked_report_ids.append((privilege_review.get("report") or {}).get("report_id"))
        execution_history = history_service.execute(
            recipe_id=recipe_id,
            trigger_source=effective_trigger_source,
            parameter_set={"parent_task": parent_task, "mode": mode},
            linked_trace_ids=execution_context["linked_trace_ids"],
            linked_subagent_ids=[worker.get("subagent_id") for worker in execution.get("workers", []) if worker.get("subagent_id")],
            policy_path=execution_context["policy_path"]
            + [
                {
                    "policy": "restricted-inheritance",
                    "reason": "goose-bounded-subagent-plan",
                    "requested_tool_count": len(worker.get("requested_tools", [])),
                }
                for worker in plan.get("workers", [])
            ],
            approval_path={
                **execution_context["approval_path"],
                "decision": "bounded-subagent-plan",
                "governance_mutation_allowed": execution.get("governance_mutation_allowed", False),
            },
            gateway_decision_path=execution_context["gateway_decision_path"],
            gateway_execution_id=execution_context["gateway_execution_id"],
            gateway_report_id=execution_context["gateway_report_id"],
            execution_path=execution_context["execution_path"],
            approval_fallback_chain=execution_context["approval_fallback_chain"],
            adversary_review_report_ids=sorted(set(adversary_report_ids)),
            linked_report_ids=sorted(set(linked_report_ids)),
            extension_bundle_ids=execution_context["extension_bundle_ids"],
            extension_policy_set_ids=execution_context["extension_policy_set_ids"],
            extension_bundle_families=execution_context["extension_bundle_families"],
            extension_provenance=execution_context["extension_provenance"],
            artifacts_produced=sorted(
                set(
                    [
                        *execution_context["artifacts_produced"],
                        *([execution.get("artifact_path")] if execution.get("artifact_path") else []),
                    ]
                )
            ),
            status="success",
            metadata={
                "worker_count": len(execution.get("workers", [])),
                "plan_status": plan.get("status_label"),
                **execution_context["metadata"],
                "privilege_review_id": privilege_review.get("review_id") if privilege_review else None,
            },
        )
        workflow_id = _scheduled_workflow_id(trigger_source=effective_trigger_source, schedule_id=schedule_id)
        scheduled_artifact = (
            services.brain_scheduled_agents.record_execution(workflow_id=workflow_id, execution=execution_history)
            if workflow_id
            else None
        )
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "plan": plan,
            "execution": execution,
            "gateway_resolution": execution_context["gateway_resolution"],
            "privilege_review": privilege_review,
            "execution_history": execution_history,
            "scheduled_artifact": scheduled_artifact,
            "parallel": services.brain_parallel.summary(),
        }

    @application.get("/ops/brain/agents/scheduled")
    def ops_brain_agents_scheduled():
        return services.brain_scheduled_agents.summary()

    @application.get("/ops/brain/agents/scheduled/history")
    def ops_brain_agents_scheduled_history(workflow_id: str | None = None, limit: int = 10):
        summary = services.brain_scheduled_agents.summary()
        history = summary.get("history") or {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "workflow_count": 0,
            "history_count": 0,
            "latest_artifact": None,
            "captured_this_summary": [],
            "items": [],
        }
        if workflow_id:
            history["items"] = [item for item in history.get("items", []) if item.get("workflow_id") == workflow_id][:limit]
        else:
            history["items"] = history.get("items", [])[:limit]
        history["history_count"] = len(history["items"])
        history["latest_artifact"] = history["items"][0] if history["items"] else None
        latest_artifact = history["latest_artifact"] or {}
        history["latest_report_id"] = ((latest_artifact.get("report") or {}).get("report_id"))
        history["latest_linked_trace_ids"] = latest_artifact.get("linked_trace_ids", [])
        history["latest_linked_report_ids"] = latest_artifact.get("linked_report_ids", [])
        return history

    @application.get("/ops/brain/agents/scheduled/history/{artifact_id}")
    def ops_brain_agents_scheduled_history_detail(artifact_id: str):
        detail = services.brain_scheduled_agents.history_detail(artifact_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="scheduled artifact not found")
        return detail

    @application.get("/ops/brain/security/permissions")
    def ops_brain_security_permissions():
        return services.brain_permissions.summary()

    @application.get("/ops/brain/security/sandbox")
    def ops_brain_security_sandbox():
        return services.brain_sandbox.summary()

    @application.get("/ops/brain/security/guardrails")
    def ops_brain_security_guardrails():
        return services.brain_persistent_guardrails.summary()

    @application.post("/ops/brain/security/adversary-review")
    def ops_brain_security_adversary_review(
        subject: str = Body(...),
        requested_tools: list[str] = Body(default=[]),
        requested_extensions: list[str] | None = Body(default=None),
        allowed_extensions: list[str] | None = Body(default=None),
        allowed_tools: list[str] | None = Body(default=None),
        risk_level: str = Body(default="medium"),
        reviewer_status: str = Body(default="available"),
        summary: str | None = Body(default=None),
        fallback_reason: str | None = Body(default=None),
        policy_path: list[dict] | None = Body(default=None),
        multi_step: bool | None = Body(default=None),
        trigger_source: str | None = Body(default=None),
        approval_requested: bool | None = Body(default=None),
        approval_required: bool | None = Body(default=None),
    ):
        return services.brain_adversary_review.review(
            subject=subject,
            requested_tools=requested_tools,
            risk_level=risk_level,
            reviewer_status=reviewer_status,
            summary=summary,
            fallback_reason=fallback_reason,
            policy_path=policy_path or [],
            multi_step=multi_step,
            allowed_tools=allowed_tools,
            requested_extensions=requested_extensions or [],
            allowed_extensions=allowed_extensions or [],
            trigger_source=trigger_source,
            approval_requested=approval_requested,
            approval_required=approval_required,
        )

    @application.get("/ops/brain/security/adversary-reviews")
    def ops_brain_security_adversary_reviews(limit: int = 10):
        summary = services.brain_adversary_review.summary()
        summary["recent_reviews"] = (summary.get("recent_reviews") or [])[:limit]
        return summary

    @application.get("/ops/brain/security/adversary-reviews/compare")
    def ops_brain_security_adversary_review_compare(left_review_id: str, right_review_id: str):
        comparison = services.brain_adversary_review.compare(left_review_id, right_review_id)
        if comparison is None:
            raise HTTPException(status_code=404, detail="adversary review comparison unavailable")
        return comparison

    @application.get("/ops/brain/security/adversary-reviews/{review_id}")
    def ops_brain_security_adversary_review_detail(review_id: str):
        detail = services.brain_adversary_review.detail(review_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="adversary review not found")
        return detail

    @application.get("/ops/brain/security/adversary-reviews/{review_id}/audit-export")
    def ops_brain_security_adversary_review_audit_export(review_id: str):
        detail = services.brain_adversary_review.audit_export_detail(review_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="adversary audit export not found")
        return detail

    @application.get("/ops/brain/evals/cost-energy")
    def ops_brain_evals_cost_energy():
        return services.brain_cost_energy.summarize(services.store.list_traces(limit=100))

    @application.get("/ops/brain/skill-evolution")
    def ops_brain_skill_evolution():
        return {
            "catalog": services.brain_skill_catalog.summary(),
            "repository": services.brain_skill_repository.summary(),
            "evolution": services.brain_skill_evolution.summarize_trajectories([]),
            "refinement": services.brain_skill_refinement.propose(recurring_patterns=[]),
        }

    @application.post("/ops/brain/skill-evolution/proposals")
    def ops_brain_skill_evolution_proposals(trajectories: list[dict] = Body(default=[])):
        summary = services.brain_skill_evolution.summarize_trajectories(trajectories)
        proposals = services.brain_skill_evolution.build_proposals(trajectories)
        services.brain_skill_repository.record_proposals(proposals)
        refinement = services.brain_skill_refinement.propose(recurring_patterns=summary["recurring_patterns"])
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "summary": summary,
            "proposals": proposals,
            "refinement": refinement,
            "repository": services.brain_skill_repository.summary(),
        }

    @application.get("/ops/brain/agent-harness")
    def ops_brain_agent_harness():
        return {
            "harness": services.brain_agent_harness.summary(),
            "teams": services.brain_agent_teams.summary(),
        }

    @application.get("/ops/brain/attention-providers")
    def ops_brain_attention_providers():
        return {
            "registry": services.brain_attention_registry.summary(),
            "benchmarks": services.brain_attention_benchmarks.summary(),
        }

    @application.get("/ops/brain/attention-providers/benchmark")
    def ops_brain_attention_providers_benchmark(provider_name: str = "triattention"):
        return services.brain_attention_benchmarks.run(provider_name=provider_name)

    @application.get("/ops/brain/attention-providers/comparative-summary")
    def ops_brain_attention_providers_comparative_summary():
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "summary": services.brain_attention_benchmarks.summary().get("latest_comparative_summary"),
            "scorecard": services.brain_attention_benchmarks.summary().get("latest_comparative_scorecard"),
        }

    @application.get("/ops/brain/research/guardrail-analysis")
    def ops_brain_research_guardrail_analysis():
        return services.brain_guardrail_analysis.summary()

    @application.post("/ops/brain/research/guardrail-analysis")
    def ops_brain_research_guardrail_analysis_run(payload: dict = Body(default={})):
        return services.brain_guardrail_analysis.analyze(
            before=payload.get("before"),
            after=payload.get("after"),
            stress_tests=payload.get("stress_tests"),
        )

    @application.get("/ops/brain/research/refusal-circuit-review")
    def ops_brain_research_refusal_circuit_review():
        return {
            "review": services.brain_red_team_review.summary(),
            "evaluator": services.brain_red_team_evaluator.summary(),
        }

    @application.post("/ops/brain/research/refusal-circuit-review")
    def ops_brain_research_refusal_circuit_review_run(payload: dict = Body(default={})):
        review = services.brain_red_team_review.review(before=payload.get("before"), after=payload.get("after"))
        return {
            "review": review,
            "evaluator": services.brain_red_team_evaluator.summary(),
        }

    @application.get("/ops/brain/assimilation/status")
    def ops_brain_assimilation_status():
        return {
            "assimilation_candidates": services.brain_assimilation.summary(),
            "normalized_telemetry": services.brain_normalized_telemetry.compact_summary(),
            "eval_suites": services.brain_eval_suites.compact_summary(),
            "runtime_scorecards": services.brain_runtime_scorecards.compact_summary(),
            "adaptive_capabilities": services.brain_adaptive_capabilities.compact_summary(),
            "research_scout": services.brain_research_scout.compact_summary(),
            "self_improvement": services.brain_self_improvement.compact_summary(),
            "tier5_cloud_fallback": services.brain_tier5_fallback.compact_summary(),
            "context_graph": services.brain_context_graph.compact_summary(),
            "factory_orchestration": services.brain_factory_orchestration.compact_summary(),
            "execution_authority": services.brain_execution_authority.compact_summary(),
            "harness_engineering": services.brain_harness_engineering.compact_summary(),
            "autonomous_growth": services.brain_autonomous_growth.compact_summary(),
            "space_agent_assimilation": services.brain_assimilation.space_agent_summary(),
            "protocol_capabilities": services.brain_protocol_capabilities.compact_summary(),
            "memory_governance": services.brain_memory_governance.summary(),
            "retrieval": {
                "benchmark": services.brain_retrieval_rerank_bench.run(
                    query="retrieval provenance",
                    top_k=4,
                    policy_mode="lexical+graph-memory-temporal-rerank",
                ),
                "scorecard": services.brain_retrieval_rerank_ops.summary(),
                "promotion_evidence": services.brain_promotions.summary().get("retrieval_policy_evidence", []),
                "promotion_reviews": [
                    {
                        "candidate_id": item.get("candidate_id"),
                        "review_report_id": item.get("review_report_id"),
                        "review_headline": item.get("review_headline"),
                        "review_artifacts": item.get("review_artifacts", {}),
                    }
                    for item in services.brain_promotions.summary().get("retrieval_policy_evidence", [])
                ],
            },
            "gateway": services.brain_gateway.summary(),
            "openjarvis_runtime": {
                "init": services.brain_runtime_init.summary(),
                "doctor": services.brain_runtime_doctor.summary(),
                "skills": services.brain_skill_catalog.summary(),
                "scheduled_agents": services.brain_scheduled_agents.summary(),
                "cost_energy": services.brain_cost_energy.summarize(services.store.list_traces(limit=100)),
            },
            "vision_edge": services.brain_edge_vision.summary(),
            "aitune": services.brain_runtime_registry.aitune_provider.summary(),
            "skill_evolution": services.brain_skill_repository.summary(),
            "agent_harness": services.brain_agent_harness.summary(),
            "attention_research": services.brain_attention_registry.summary(),
            "attention_benchmarks": services.brain_attention_benchmarks.summary(),
            "obliteratus_safe_boundary": {
                "guardrail_analysis": services.brain_guardrail_analysis.summary(),
                "red_team_review": services.brain_red_team_review.summary(),
                "red_team_evaluator": services.brain_red_team_evaluator.summary(),
            },
        }

    @application.get("/ops/brain/retrieval/planner")
    def ops_brain_retrieval_planner():
        return services.brain_retrieval_planner.summary()

    @application.post("/ops/brain/retrieval/plans")
    def ops_brain_retrieval_plans(payload: dict[str, Any] = Body(...)):
        return services.brain_retrieval_planner.plan(RetrievalPlanRequest.model_validate(payload))

    @application.get("/ops/brain/canon/retrieval-planner")
    def ops_brain_canon_retrieval_planner():
        return services.brain_retrieval_planner.summary()

    @application.post("/ops/brain/assimilation/candidates/ingest")
    def ops_brain_assimilation_candidates_ingest(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_assimilation.ingest(
                category=str(payload["category"]),
                source_name=str(payload["source_name"]),
                source_url=str(payload["source_url"]),
                license_posture=str(payload.get("license_posture") or "requires_review"),
                target_subsystem=payload.get("target_subsystem"),
                governance_status=str(payload.get("governance_status") or "gated"),
                provenance=dict(payload.get("provenance") or {}),
                scorecard=dict(payload.get("scorecard") or {}),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.post("/ops/brain/assimilation/space-agent/review")
    def ops_brain_assimilation_space_agent_review(payload: dict[str, Any] = Body(...)):
        try:
            return services.brain_assimilation.review_space_agent(
                source_url=str(payload["source_url"]),
                commit_sha=str(payload.get("commit_sha") or ""),
                license_posture=str(payload.get("license_posture") or "requires_review"),
                observed_patterns=[str(item) for item in (payload.get("observed_patterns") or [])],
                evidence=dict(payload.get("evidence") or {}),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @application.get("/ops/brain/retrieval/rerank-benchmark")
    def ops_brain_retrieval_rerank_benchmark(
        query: str,
        session_id: str | None = None,
        top_k: int = 6,
        policy_mode: str = "lexical+graph-memory-temporal-rerank",
    ):
        return services.brain_retrieval_rerank_bench.run(
            query=query,
            session_id=session_id,
            top_k=top_k,
            policy_mode=policy_mode,
        )

    @application.get("/ops/brain/retrieval/rerank-scorecard")
    def ops_brain_retrieval_rerank_scorecard(
        session_id: str | None = None,
        top_k: int | None = None,
        policy_mode: str | None = None,
    ):
        return services.brain_retrieval_rerank_ops.run(
            session_id=session_id,
            top_k=top_k,
            policy_mode=policy_mode,
        )

    @application.get("/ops/brain/retrieval/promotion-evidence")
    def ops_brain_retrieval_promotion_evidence():
        promotions = services.brain_promotions.summary()
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "items": promotions.get("retrieval_policy_evidence", []),
        }

    @application.get("/ops/brain/retrieval/promotion-reviews")
    def ops_brain_retrieval_promotion_reviews():
        promotions = services.brain_promotions.summary()
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "items": [
                {
                    "candidate_id": item.get("candidate_id"),
                    "subject_id": item.get("subject_id"),
                    "review_report_id": item.get("review_report_id"),
                    "review_headline": item.get("review_headline"),
                    "review_summary": item.get("review_summary", []),
                    "human_summary": item.get("human_summary"),
                    "review_badges": item.get("review_badges", {}),
                    "candidate_shift_count": item.get("candidate_shift_count", 0),
                    "candidate_shift_summary": item.get("candidate_shift_summary", {}),
                    "top_shift_preview": item.get("top_shift_preview"),
                    "delta_summary": item.get("delta_summary", {}),
                    "threshold_summary": item.get("threshold_summary", {}),
                    "evaluator_artifact_summary": item.get("evaluator_artifact_summary", {}),
                    "review_artifacts": item.get("review_artifacts", {}),
                    "scorecard_id": item.get("scorecard_id"),
                    "threshold_set_id": item.get("threshold_set_id"),
                    "benchmark_family_id": item.get("benchmark_family_id"),
                    "evaluation_artifacts": item.get("evaluation_artifacts", {}),
                }
                for item in promotions.get("retrieval_policy_evidence", [])
            ],
        }

    @application.get("/ops/brain/retrieval/promotion-reviews/{review_report_id}")
    def ops_brain_retrieval_promotion_review_detail(review_report_id: str):
        promotions = services.brain_promotions.summary()
        item = next(
            (
                candidate
                for candidate in promotions.get("retrieval_policy_evidence", [])
                if candidate.get("review_report_id") == review_report_id
            ),
            None,
        )
        if item is None:
            raise HTTPException(status_code=404, detail="Retrieval promotion review not found.")
        payload_path = (item.get("review_artifacts") or {}).get("payload")
        markdown_path = (item.get("review_artifacts") or {}).get("markdown")
        payload = None
        markdown = None
        if payload_path:
            try:
                payload = json.loads(Path(payload_path).read_text(encoding="utf-8"))
            except Exception:
                payload = None
        if markdown_path:
            try:
                markdown = Path(markdown_path).read_text(encoding="utf-8")
            except Exception:
                markdown = None
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "item": item,
            "summary": {
                "review_report_id": item.get("review_report_id"),
                "human_summary": item.get("human_summary"),
                "review_badges": item.get("review_badges", {}),
                "candidate_shift_count": item.get("candidate_shift_count", 0),
                "evaluator_artifact_summary": item.get("evaluator_artifact_summary", {}),
            },
            "payload": payload,
            "markdown": markdown,
        }

    @application.get("/ops/brain/backends")
    def ops_brain_backends(model_hint: str | None = None):
        return services.brain_runtime_registry.summary(model_hint)

    @application.get("/ops/brain/runtimes/capabilities")
    def ops_brain_runtimes_capabilities():
        return services.model_runtime_planner.capabilities()

    @application.post("/ops/brain/models/plan")
    def ops_brain_models_plan(request: ModelRuntimePlanRequest):
        return services.model_runtime_planner.plan(request)

    @application.post("/ops/brain/models/validate")
    def ops_brain_models_validate(request: ModelRuntimePlanRequest):
        return services.model_runtime_planner.validate(request)

    @application.get("/ops/brain/aitune/validation")
    def ops_brain_aitune_validation(model_hint: str | None = None, simulate: bool = False):
        model = services.model_registry.resolve_model(model_hint) if model_hint else None
        return services.brain_runtime_registry.aitune_provider.validate(model, simulate=simulate)

    @application.get("/ops/brain/aitune/execution-plan")
    def ops_brain_aitune_execution_plan(model_hint: str | None = None):
        model = services.model_registry.resolve_model(model_hint) if model_hint else None
        summary = services.brain_runtime_registry.aitune_provider.summary(model)
        return {
            "status_label": "EXPLORATORY / PROTOTYPE",
            "supported_lane_readiness": summary.get("supported_lane_readiness"),
            "latest_execution_plan": summary.get("latest_execution_plan"),
            "latest_execution_plan_markdown_path": summary.get("latest_execution_plan_markdown_path"),
            "latest_runner_report": summary.get("latest_runner_report"),
            "latest_validation": summary.get("latest_validation"),
            "latest_benchmark": summary.get("latest_benchmark"),
            "latest_tuned_artifact": summary.get("latest_tuned_artifact"),
        }

    @application.post("/ops/brain/backends/benchmark")
    def ops_brain_backends_benchmark(model_hint: str | None = None):
        benchmark = services.brain_runtime_registry.benchmark(model_hint)
        candidates = []
        for record in benchmark["records"]:
            benchmark_metrics = record.get("metrics", {})
            candidate = services.brain_promotions.create_candidate(
                candidate_kind="runtime-profile",
                subject_id=f"runtime-profile::{record['runtime_name']}::{record['model_id']}",
                baseline_reference=f"runtime-profile::{record['model_id']}::baseline",
                challenger_reference=benchmark["artifact_path"],
                lineage=record.get("lineage", "live-derived"),
                rollback_reference=benchmark_metrics.get("rollback_reference"),
                traceability={
                    "benchmark_record": record,
                    "benchmark_artifact": benchmark["artifact_path"],
                    "qes_provider": benchmark_metrics.get("qes_provider"),
                    "runtime_artifact": benchmark_metrics.get("tuned_artifact_path") or benchmark_metrics.get("benchmark_artifact_path"),
                    "hardware_profile": benchmark_metrics.get("hardware_profile", {}),
                    "environment_compatibility": benchmark_metrics.get("environment_compatibility", {}),
                },
            )
            candidates.append(candidate.model_dump(mode="json"))
        benchmark["promotion_candidates"] = candidates
        return benchmark

    @application.get("/ops/brain/evals/report")
    def ops_brain_eval_report(limit: int = 25):
        return services.brain_evaluator.run_recent(limit=limit)

    @application.get("/ops/brain/promotions")
    def ops_brain_promotions():
        return services.brain_promotions.summary()

    @application.post("/ops/brain/promotions/evaluate")
    def ops_brain_promotions_evaluate(
        candidate_id: str = Body(...),
        scenario_set: list[str] | None = Body(default=None),
        candidate_metrics: dict | None = Body(default=None),
        limit: int = Body(default=25),
    ):
        evaluation = services.brain_promotions.evaluate_candidate(
            candidate_id=candidate_id,
            scenario_set=scenario_set,
            candidate_metrics=candidate_metrics,
            limit=limit,
        )
        return evaluation.model_dump(mode="json")

    @application.post("/ops/brain/promotions/decide")
    def ops_brain_promotions_decide(
        candidate_id: str = Body(...),
        approver: str = Body(...),
        requested_decision: str = Body(default="approved"),
        rationale: str | None = Body(default=None),
    ):
        decision = services.brain_promotions.decide_candidate(
            candidate_id=candidate_id,
            approver=approver,
            requested_decision=requested_decision,
            rationale=rationale,
        )
        return decision.model_dump(mode="json")

    @application.get("/ops/brain/reflection")
    def ops_brain_reflection(limit: int = 25):
        return services.brain_reflection.summarize(limit=limit).model_dump(mode="json")

    @application.post("/ops/brain/dream")
    def ops_brain_dream(request: DreamCycleRequest | None = Body(default=None)):
        episode = services.brain_dreaming.run_cycle(brain=services.brain, request=request or DreamCycleRequest())
        return episode.model_dump(mode="json")

    @application.get("/ops/brain/curriculum")
    def ops_brain_curriculum(subject: str | None = None, limit: int = 200):
        return {"transcript": services.brain_curriculum.transcript(subject=subject, limit=limit)}

    @application.post("/ops/brain/curriculum/assess")
    def ops_brain_curriculum_assess(request: CurriculumAssessmentRequest):
        assessment = services.brain_curriculum.assess(brain=services.brain, request=request)
        return assessment.model_dump(mode="json")

    @application.post("/ops/brain/distill-dataset")
    def ops_brain_distill_dataset(request: DistillationExportRequest):
        result = services.brain_distillation.export(request)
        artifact_path = result.artifact_path
        teacher_evidence = result.metadata.get("teacher_evidence", {})
        artifact = services.brain_foundry_refinery.record_distillation_artifact(
            name=request.name,
            artifact_path=artifact_path,
            source_kinds=result.metadata.get("source_kinds", []),
            sample_count=result.sample_count,
            lineage=result.metadata.get("lineage", "blended-derived"),
            metadata={
                "teacher_evidence": teacher_evidence,
                "dream_derived_included": request.include_dreams,
                "curriculum_included": request.include_curriculum,
            },
        )
        benchmark = services.brain_foundry_benchmarks.evaluate(artifact=artifact)
        retirement_decisions = services.brain_teachers.retirement_decisions()
        replacement_teacher_id = (
            teacher_evidence.get("teacher_replacement_candidate")
            or (teacher_evidence.get("selected_teacher_roles") or {}).get("primary")
            or (teacher_evidence.get("selected_teachers") or [None])[0]
        )
        teacher_replacement = next(
            (decision for decision in retirement_decisions if decision.teacher_id == replacement_teacher_id),
            retirement_decisions[0],
        )
        takeover = services.brain_foundry_retirement.takeover_candidate(
            teacher_replacement,
            benchmark_summary=benchmark,
            teacher_evidence=teacher_evidence,
        )
        candidate = services.brain_promotions.create_candidate(
            candidate_kind="native-takeover",
            subject_id=f"native-takeover::{artifact.artifact_id}",
            baseline_reference=f"teacher::{teacher_replacement.teacher_id}",
            challenger_reference=artifact.artifact_path,
            lineage=artifact.lineage,
            traceability={
                "distillation_artifact": artifact.model_dump(mode="json"),
                "benchmark": benchmark,
                "teacher_replacement": teacher_replacement.model_dump(mode="json"),
                "takeover": takeover.model_dump(mode="json"),
                "teacher_evidence": teacher_evidence,
                "teacher_evidence_bundle_id": teacher_evidence.get("bundle_id"),
                "threshold_set_id": teacher_evidence.get("threshold_set_id") or benchmark.get("threshold_set_id"),
                "takeover_scorecard": benchmark.get("takeover_scorecard"),
            },
        )
        payload = result.model_dump(mode="json")
        payload["native_takeover_candidate"] = candidate.model_dump(mode="json")
        payload["benchmark"] = benchmark
        payload["teacher_replacement"] = teacher_replacement.model_dump(mode="json")
        payload["takeover"] = takeover.model_dump(mode="json")
        payload["teacher_evidence"] = teacher_evidence
        return payload

    @application.get("/ops/brain/graph/status")
    def ops_brain_graph_status():
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "store": services.brain_ui_surface.graph_service.status(),
        }

    @application.post("/ops/brain/graph/ingest")
    def ops_brain_graph_ingest(request: GraphIngestRequest):
        return services.brain_graph_ingestion.ingest(request)

    @application.post("/ops/brain/graph/query")
    def ops_brain_graph_query(query: str = Body(...), top_k: int = Body(default=5), plane_tags: list[str] | None = Body(default=None)):
        hits = services.brain_graph_retriever.query(query=query, top_k=top_k, plane_tags=plane_tags)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "hits": hits,
            "evaluation": services.brain_graph_evaluator.evaluate(query=query, hits=hits),
        }

    @application.get("/ops/brain/foundry/status")
    def ops_brain_foundry_status():
        native_candidates = services.brain_promotions.list_candidates(candidate_kind="native-takeover")
        retirement = services.brain_teachers.retirement_decisions()
        benchmark = services.brain_foundry_benchmarks.evaluate(
            artifact=services.brain_foundry_refinery.record_distillation_artifact(
                name="status-snapshot",
                artifact_path=str(services.paths.artifacts_dir / "foundry" / "status-snapshot.jsonl"),
                source_kinds=["trace"],
                sample_count=len(services.store.list_traces(limit=100)),
                lineage="live-derived",
                metadata={},
            )
        )
        return {
            "status_label": "LOCKED CANON",
            "teacher_retirement": [decision.model_dump(mode="json") for decision in retirement],
            "benchmark": benchmark,
            "takeover_scorecards": services.store.list_takeover_scorecards(limit=50),
            "takeover_trends": services.store.list_takeover_trend_reports(limit=50),
            "fleet_summaries": services.store.list_teacher_benchmark_fleet_summaries(limit=50),
            "cohort_scorecards": services.store.list_teacher_cohort_scorecards(limit=50),
            "replacement_readiness_reports": services.store.list_replacement_readiness_reports(limit=50),
            "retirement_shadow_log": services.store.list_retirement_shadow_records(limit=50),
            "native_takeover": [
                {
                    "candidate": candidate.model_dump(mode="json"),
                    "latest_decision": services.store.latest_promotion_decision(candidate.candidate_id),
                    "teacher_evidence_bundle_id": candidate.teacher_evidence_bundle_id,
                    "threshold_set_id": candidate.threshold_set_id,
                    "teacher_evidence": candidate.traceability.get("teacher_evidence", {}),
                    "takeover_scorecard": candidate.traceability.get("takeover_scorecard"),
                    "takeover_trend_report": candidate.traceability.get("benchmark", {}).get("takeover_trend_report"),
                    "fleet_summaries": candidate.traceability.get("benchmark", {}).get("fleet_summaries", []),
                    "cohort_scorecards": candidate.traceability.get("benchmark", {}).get("cohort_scorecards", []),
                    "replacement_readiness": candidate.traceability.get("benchmark", {}).get("replacement_readiness"),
                }
                for candidate in native_candidates
            ],
        }

    @application.get("/ops/brain/federation/status")
    def ops_brain_federation_status():
        return services.brain_federation_coordinator.status()

    @application.post("/ops/brain/federation/simulate")
    def ops_brain_federation_simulate(
        candidate_kind: str = Body(...),
        artifact_path: str = Body(...),
        lineage: str = Body(default="live-derived"),
        metrics: dict | None = Body(default=None),
        provenance: dict | None = Body(default=None),
    ):
        simulation = services.brain_federation_simulation.run(
            candidate_kind=candidate_kind,
            artifact_path=artifact_path,
            lineage=lineage,
            metrics=metrics,
            provenance=provenance,
        )
        promotion_candidate = simulation["submission"].get("promotion_candidate")
        candidate_id = promotion_candidate["candidate_id"] if promotion_candidate else simulation["submission"]["candidate"]["candidate_id"]
        evaluation = services.brain_promotions.evaluate_candidate(
            candidate_id=candidate_id,
            scenario_set=["federated-shadow-rollout"],
            candidate_metrics=metrics or {},
            limit=25,
        )
        review = services.brain_federation_review_gate.decide(
            candidate_id=candidate_id,
            evaluator_decision=evaluation.decision,
        )
        rollout = services.brain_global_rollout.decide(
            candidate_id=candidate_id,
            review_decision=review.decision,
            evaluator_decision=evaluation.decision,
        )
        decision = services.brain_promotions.decide_candidate(
            candidate_id=candidate_id,
            approver="FederatedReviewBoard",
            requested_decision="approved" if rollout.decision == "rollout" else "shadow",
            rationale=rollout.rationale,
        )
        return {
            "status_label": "LOCKED CANON",
            "simulation": simulation,
            "promotion_candidate": promotion_candidate,
            "evaluation": evaluation.model_dump(mode="json"),
            "review": review.model_dump(mode="json"),
            "rollout": rollout.model_dump(mode="json"),
            "decision": decision.model_dump(mode="json"),
        }

    @application.get("/ops/models")
    def ops_models():
        return {"models": [model.model_dump(mode="json") for model in services.model_registry.list_models()]}

    @application.get("/ops/runtimes")
    def ops_runtimes():
        return {"runtimes": [profile.model_dump(mode="json") for profile in services.runtime_registry.list_profiles()]}

    @application.get("/ops/runtime-acceleration")
    @application.get("/api/runtime-packs/status")
    def ops_runtime_acceleration():
        return services.runtime_registry.accelerator_status()

    @application.get("/ops/runtime-acceleration/certification")
    @application.get("/api/runtime-packs/certification")
    def ops_runtime_acceleration_certification():
        return services.runtime_registry.accelerator_status()["certification"]

    @application.put("/ops/runtime-acceleration/mode")
    @application.put("/api/runtime-packs/mode")
    def set_ops_runtime_acceleration_mode(payload: dict[str, Any] = Body(...)):
        try:
            return services.runtime_registry.set_execution_mode(payload.get("mode"))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @application.get("/ops/tools")
    def ops_tools():
        entries = []
        for manifest in services.tool_registry.list():
            authorization = services.permission_context.authorize(manifest)
            payload = manifest.model_dump(mode="json")
            payload["authorization"] = authorization
            entries.append(payload)
        return {"permission_mode": services.permission_context.mode, "tools": entries}

    @application.get("/ops/traces/{trace_id}")
    def ops_trace(trace_id: str):
        trace = services.store.get_trace(trace_id)
        if trace is None:
            raise HTTPException(status_code=404, detail="trace not found")
        return trace

    @application.get("/ops/memory/{session_id}")
    def ops_memory(session_id: str):
        return services.memory.session_view(session_id)

    @application.get("/ops/experiments")
    def ops_experiments():
        return {"experiments": [record.model_dump(mode="json") for record in services.experiments.list()]}

    @application.get("/ops/audit")
    def ops_audit(limit: int = 200):
        return {"events": services.governance.list_audit(limit=limit)}

    @application.get("/admin/config")
    def admin_config():
        return {
            "inference": services.runtime_configs.get("inference", {}),
            "experts": services.runtime_configs.get("experts", {}),
            "router": services.runtime_configs.get("router", {}),
            "rag": services.runtime_configs.get("rag", {}),
            "retrieval": services.runtime_configs.get("retrieval", {}),
            "qes": services.runtime_configs.get("qes", {}),
            "goose_lane": services.runtime_configs.get("goose_lane", {}),
            "planes": services.runtime_configs.get("planes", {}),
        }

    @application.post("/first-run/save")
    def first_run_save(payload: dict[str, Any] = Body(...)):
        env_payload = payload.get("env") or {}
        rag_payload = payload.get("rag") or {}
        allowed_env_keys = {
            "OLLAMA_BASE_URL",
            "OLLAMA_MODEL",
            "VLLM_BASE_URL",
            "VLLM_MODEL",
            "TGI_BASE_URL",
            "LIVE_ENGINES",
            "OPENAI_COMPAT_BASE_URL",
            "OPENAI_COMPAT_API_KEY",
        }
        env_updates = {
            key: str(value)
            for key, value in env_payload.items()
            if key in allowed_env_keys and value is not None and str(value) != ""
        }
        env_path = services.paths.project_root / ".env"
        existing_lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
        seen_keys: set[str] = set()
        next_lines: list[str] = []
        for line in existing_lines:
            key = line.split("=", 1)[0].strip() if "=" in line and not line.lstrip().startswith("#") else None
            if key in env_updates:
                next_lines.append(f"{key}={env_updates[key]}")
                seen_keys.add(key)
            else:
                next_lines.append(line)
        for key in sorted(set(env_updates) - seen_keys):
            next_lines.append(f"{key}={env_updates[key]}")
        env_path.write_text("\n".join(next_lines).rstrip() + ("\n" if next_lines else ""), encoding="utf-8")

        inference = dict(services.runtime_configs.get("inference", {}) or {})
        if env_updates.get("OLLAMA_BASE_URL") or env_updates.get("OLLAMA_MODEL"):
            inference["ollama"] = {
                **dict(inference.get("ollama") or {}),
                "base_url": env_updates.get("OLLAMA_BASE_URL") or (inference.get("ollama") or {}).get("base_url"),
                "model": env_updates.get("OLLAMA_MODEL") or (inference.get("ollama") or {}).get("model", "llama3.1"),
            }
        if env_updates.get("VLLM_BASE_URL") or env_updates.get("VLLM_MODEL"):
            inference["vllm"] = {
                **dict(inference.get("vllm") or {}),
                "endpoint": env_updates.get("VLLM_BASE_URL") or (inference.get("vllm") or {}).get("endpoint"),
                "model": env_updates.get("VLLM_MODEL") or (inference.get("vllm") or {}).get("model", "default"),
            }
        if env_updates.get("TGI_BASE_URL"):
            inference["tgi"] = {
                **dict(inference.get("tgi") or {}),
                "endpoint": env_updates["TGI_BASE_URL"],
            }
        if "LIVE_ENGINES" in env_updates:
            inference.setdefault("policy", dict(inference.get("policy") or {}))
            inference["policy"]["live_engines"] = env_updates["LIVE_ENGINES"] in {"1", "true", "TRUE", "yes", "on"}
        save_yaml_file(services.paths.config_dir / "inference.yaml", inference)

        rag = dict(services.runtime_configs.get("rag", {}) or {})
        for key in ("enabled", "top_k", "corpus_dir"):
            if key in rag_payload:
                rag[key] = rag_payload[key]
        save_yaml_file(services.paths.config_dir / "rag.yaml", rag)

        services.runtime_configs["inference"] = inference
        services.runtime_configs["rag"] = rag
        return {
            "ok": True,
            "paths": {
                "env": str(env_path),
                "inference": str(services.paths.config_dir / "inference.yaml"),
                "rag": str(services.paths.config_dir / "rag.yaml"),
            },
        }

    @application.post("/ops/approvals")
    def ops_approvals(request: ApprovalRequest):
        decision = services.governance.record_approval(request)
        return decision.model_dump(mode="json")

    @application.post("/retrieval/ingest")
    def retrieval_ingest(request: RetrievalIngestRequest):
        doc_ids = services.retrieval.ingest(request)
        return {"ok": True, "doc_ids": doc_ids, "count": len(doc_ids)}

    @application.post("/retrieval/query")
    def retrieval_query(request: RetrievalRequest):
        hits = services.retrieval.query(request)
        return {"hits": [hit.model_dump(mode="json") for hit in hits]}

    @application.post("/rag/ingest")
    def rag_ingest(payload: list[str] | None = Body(default=None)):
        documents = RetrievalIngestRequest(documents=[
            {"source": "legacy-rag", "text": text, "metadata": {"compat": True}} for text in (payload or [])
        ])
        doc_ids = services.retrieval.ingest(documents)
        return {"ok": True, "added": len(doc_ids), "doc_ids": doc_ids}

    @application.post("/chat")
    def chat(request: ChatRequest):
        try:
            result = services.operator.execute_chat(request)
        except RuntimeUnavailableError as exc:
            raise HTTPException(status_code=503, detail=exc.detail) from exc
        # Feed the release wrapper runtime: real use updates assimilation, global growth,
        # sanitized federation packets, and shadow-only autonomous update proposals.
        try:
            release_wrapper_runtime.record_chat_turn(request=request, result=result)
        except Exception:
            pass
        runtime_selection = result.runtime_selection or result.trace.runtime_selection or {}
        requested_model_id = runtime_selection.get("requested_model_id") or result.model_id
        requested_runtime = runtime_selection.get("requested_runtime_name")
        served_model_id = runtime_selection.get("served_model_id") or result.model_id
        served_runtime = runtime_selection.get("served_runtime_name") or result.runtime_name
        runtime_lane = runtime_selection.get("runtime_lane") or served_runtime
        return {
            "ok": result.status != "error",
            "status": result.status,
            "trace_id": result.trace_id,
            "session_id": result.session_id,
            "ao": result.selected_ao,
            "teacher_id": result.selected_teacher_id,
            "expert": result.selected_expert,
            "capsule": result.selected_expert,
            "requested_model_id": requested_model_id,
            "requested_runtime": requested_runtime,
            "served_model_id": served_model_id,
            "served_runtime": served_runtime,
            "runtime_lane": runtime_lane,
            "fallback_used": bool(runtime_selection.get("fallback_used", False)),
            "fallback_reason": runtime_selection.get("fallback_reason"),
            "compatibility_plan_id": runtime_selection.get("compatibility_plan_id"),
            "compatibility_status": runtime_selection.get("compatibility_status"),
            "attachment_mode": runtime_selection.get("attachment_mode"),
            "product_evidence": runtime_selection.get("product_evidence"),
            "model_id": served_model_id,
            "runtime": served_runtime,
            "backend": served_runtime,
            "wrapper_mode": result.wrapper_mode,
            "output": result.output,
            "reply": result.output,
            "response": result.output,
            "text": result.output,
            "citations": result.citations,
            "approval_required": result.approval_required,
            "trace": result.trace.model_dump(mode="json"),
            "runtime_selection": runtime_selection,
            "critique": result.critique.model_dump(mode="json") if result.critique else None,
        }

    @application.post("/v1/chat/completions")
    def openai_compatible_chat_completions(payload: dict[str, Any] = Body(...)):
        stream = bool(payload.get("stream"))
        messages = payload.get("messages") or []
        if not isinstance(messages, list) or not messages:
            raise HTTPException(status_code=400, detail="messages must be a non-empty list")
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        session_id = str(payload.get("user") or metadata.get("session_id") or payload.get("session_id") or "")
        requested_model = str(payload.get("model") or "")
        provider = provider_registry.get(requested_model) if requested_model else None
        if provider is not None:
            if not session_id:
                session_id = f"openai-compatible-{_privacy_compat_digest(str(messages))}"
            provider_result = provider_registry.complete(requested_model, messages)
            if not provider_result.get("ok"):
                release_wrapper_runtime.record_provider_turn(
                    session_id=session_id,
                    provider_id=requested_model,
                    model_id=str(provider_result.get("model") or requested_model),
                    messages=messages,
                    output=str(provider_result.get("text") or provider_result.get("error") or ""),
                    ok=False,
                    wrapper_mode="openai-compatible",
                )
                raise HTTPException(status_code=502, detail=str(provider_result.get("error") or "provider unavailable"))
            release_wrapper_runtime.record_provider_turn(
                session_id=session_id,
                provider_id=requested_model,
                model_id=str(provider_result.get("model") or requested_model),
                messages=messages,
                output=str(provider_result.get("text") or ""),
                ok=True,
                wrapper_mode="openai-compatible",
            )
            prompt_tokens = _rough_message_tokens(messages)
            completion_tokens = int(provider_result.get("tokens") or len(str(provider_result.get("text") or "").split()))
            response_payload = {
                "id": f"chatcmpl-provider-{_privacy_compat_digest(session_id + requested_model)}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": str(provider_result.get("model") or requested_model),
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": str(provider_result.get("text") or "")},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
                "nexusnet": {
                    "session_id": session_id,
                    "status": "ok",
                    "provider_id": requested_model,
                    "provider_local": bool(provider.is_local),
                    "runtime": f"provider:{requested_model}",
                    "wrapper_mode": "openai-compatible",
                    "release_runtime_ref": "/ops/wrapper/release-runtime",
                },
            }
            return _stream_chat_completion_response(response_payload) if stream else response_payload
        request_payload: dict[str, Any] = {
            "messages": messages,
            "model_hint": requested_model or None,
            "wrapper_mode": "openai-compatible",
            "rag": bool(payload.get("rag")) if "rag" in payload else False,
            "metadata": {
                **metadata,
                "openai_compatible_surface": True,
                "temperature": payload.get("temperature"),
                "top_p": payload.get("top_p"),
                "max_tokens": payload.get("max_tokens"),
            },
        }
        if session_id:
            request_payload["session_id"] = session_id
        request = ChatRequest.model_validate(request_payload)
        result = services.operator.execute_chat(request)
        try:
            release_wrapper_runtime.record_chat_turn(request=request, result=result)
        except Exception:
            pass
        prompt_tokens = _rough_message_tokens(messages)
        completion_tokens = len(str(result.output or "").split())
        response_payload = {
            "id": f"chatcmpl-{result.trace_id}",
            "object": "chat.completion",
            "created": int(result.trace.started_at.timestamp()),
            "model": result.model_id,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": result.output},
                    "finish_reason": "stop" if result.status != "error" else "error",
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            "nexusnet": {
                "trace_id": result.trace_id,
                "session_id": result.session_id,
                "status": result.status,
                "ao": result.selected_ao,
                "expert": result.selected_expert,
                "runtime": result.runtime_name,
                "wrapper_mode": result.wrapper_mode,
                "release_runtime_ref": "/ops/wrapper/release-runtime",
            },
        }
        return _stream_chat_completion_response(response_payload) if stream else response_payload

    def _stream_chat_completion_response(completion: dict[str, Any]) -> StreamingResponse:
        choice = (completion.get("choices") or [{}])[0]
        message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
        content = str(message.get("content") or "")
        finish_reason = str(choice.get("finish_reason") or "stop")

        def event(payload: dict[str, Any]) -> str:
            return f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"

        def events():
            base = {
                "id": completion.get("id"),
                "object": "chat.completion.chunk",
                "created": completion.get("created"),
                "model": completion.get("model"),
            }
            yield event({**base, "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]})
            if content:
                yield event({**base, "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": None}]})
            yield event({**base, "choices": [{"index": 0, "delta": {}, "finish_reason": finish_reason}]})
            yield "data: [DONE]\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    @application.get("/v1/models")
    def v1_models():
        data: list[dict[str, Any]] = []
        for model in services.model_registry.list_models():
            data.append(
                {
                    "id": model.model_id,
                    "object": "model",
                    "created": 0,
                    "owned_by": "NexusBrain",
                    "nexusnet": {
                        "source": "model-registry",
                        "runtime": model.runtime_name,
                        "available": model.available,
                    },
                }
            )
        for provider in provider_registry.list():
            data.append(
                {
                    "id": provider["provider_id"],
                    "object": "model",
                    "created": 0,
                    "owned_by": "NexusBrain",
                    "nexusnet": {
                        "source": "wrapper-provider",
                        "runtime": f"provider:{provider['provider_id']}",
                        "local": bool(provider.get("local")),
                    },
                }
            )
        return {"object": "list", "data": data}

    @application.post("/v1/chat")
    def native_v1_chat(payload: dict[str, Any] = Body(...)):
        compat = openai_compatible_chat_completions({**payload, "stream": False})
        choice = (compat.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        nexusnet_payload = compat.get("nexusnet") or {}
        return {
            "ok": nexusnet_payload.get("status") == "ok",
            "reply": message.get("content") or "",
            "model": compat.get("model"),
            "choices": compat.get("choices") or [],
            "usage": compat.get("usage") or {},
            "nexusnet": nexusnet_payload,
        }

    @application.get("/ui", include_in_schema=False)
    @application.get("/ui/", include_in_schema=False)
    def ui_root():
        return RedirectResponse(url="/ui/control-panel/")

    @application.get("/ui/wrapper", include_in_schema=False)
    @application.get("/ui/wrapper/", include_in_schema=False)
    def ui_wrapper():
        wrapper_index = services.paths.ui_dir / "wrapper" / "index.html"
        if not wrapper_index.exists():
            wrapper_index = services.paths.ui_dir / "index.html"
        if not wrapper_index.exists():
            raise HTTPException(status_code=404, detail="Wrapper surface is not available.")
        return FileResponse(wrapper_index)

    if services.paths.ui_dir.exists():
        application.mount("/ui", StaticFiles(directory=str(services.paths.ui_dir), html=True), name="ui")
    return application


app = create_app(os.environ.get("NEXUSNET_PROJECT_ROOT") or None)
