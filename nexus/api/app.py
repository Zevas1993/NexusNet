from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from ..schemas import ApprovalRequest, ChatRequest, RetrievalIngestRequest, RetrievalRequest
from ..services import NexusServices, build_services
from nexusnet.schemas import CurriculumAssessmentRequest, DistillationExportRequest, DreamCycleRequest, GraphIngestRequest, ModelAttachRequest


def create_app(project_root: str | None = None) -> FastAPI:
    services = build_services(project_root)
    application = FastAPI(title="Nexus API", version=services.version)
    application.state.services = services

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
            return RedirectResponse(url="/ui/")
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

    @application.get("/ops/brain/wrapper-surface")
    def ops_brain_wrapper_surface(session_id: str | None = None):
        return services.brain_ui_surface.snapshot(session_id=session_id)

    @application.get("/ops/brain/visualizer/state")
    def ops_brain_visualizer_state(session_id: str | None = None):
        return services.brain_visualizer.state(session_id=session_id)

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
        result = services.operator.execute_chat(request)
        return {
            "ok": result.status != "error",
            "status": result.status,
            "trace_id": result.trace_id,
            "session_id": result.session_id,
            "ao": result.selected_ao,
            "teacher_id": result.selected_teacher_id,
            "expert": result.selected_expert,
            "capsule": result.selected_expert,
            "model_id": result.model_id,
            "runtime": result.runtime_name,
            "backend": result.runtime_name,
            "wrapper_mode": result.wrapper_mode,
            "output": result.output,
            "reply": result.output,
            "response": result.output,
            "text": result.output,
            "citations": result.citations,
            "approval_required": result.approval_required,
            "trace": result.trace.model_dump(mode="json"),
            "critique": result.critique.model_dump(mode="json") if result.critique else None,
        }

    if services.paths.ui_dir.exists():
        application.mount("/ui", StaticFiles(directory=str(services.paths.ui_dir), html=True), name="ui")
    return application


app = create_app()
