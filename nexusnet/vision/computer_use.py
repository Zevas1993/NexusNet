from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import utcnow
from nexusnet.policy import PolicyKernel
from nexusnet.runtime.edge_router import EdgeWorkloadRequest, EdgeWorkloadRouter


InputModality = Literal["text", "screenshot", "screen", "image", "document", "audio", "browser_page", "video"]
ComputerUseTask = Literal[
    "screen_agent",
    "ocr",
    "vlm_route",
    "document_understanding",
    "asr",
    "tts",
    "browser_control",
    "os_control",
    "trace_replay",
]
PermissionScope = Literal["none", "public-demo", "operator-approved-local", "automation-approved"]
SandboxMode = Literal["none", "read_only", "shadow", "operator_confirmed"]


class ComputerUsePlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    session_id: str = ""
    user_goal: str
    input_modalities: list[InputModality] = Field(default_factory=list)
    requested_tasks: list[ComputerUseTask] = Field(default_factory=list)
    contains_private_data: bool = False
    permission_scope: PermissionScope = "none"
    sandbox_mode: SandboxMode = "shadow"
    local_only: bool = True
    allow_cloud: bool = False
    evidence_refs: list[str] = Field(default_factory=list)
    hardware_snapshot: dict[str, Any] = Field(default_factory=dict)
    upstream_aitune_gate: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MultimodalComputerUseController:
    def __init__(
        self,
        *,
        artifacts_dir: Path | None = None,
        edge_router: EdgeWorkloadRouter | None = None,
    ) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.plans_dir = self.artifacts_dir / "vision" / "computer-use" / "plans" if self.artifacts_dir else None
        if self.plans_dir is not None:
            self.plans_dir.mkdir(parents=True, exist_ok=True)
        self._memory_plans: list[dict[str, Any]] = []
        self.policy_kernel = PolicyKernel.default()
        self.edge_router = edge_router or EdgeWorkloadRouter(artifacts_dir=artifacts_dir)

    def plan(self, request: ComputerUsePlanRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, ComputerUsePlanRequest) else ComputerUsePlanRequest.model_validate(request)
        lanes = _lanes_for(normalized)
        safety_findings = _safety_findings(normalized)
        upstream_aitune_gate = _upstream_aitune_gate(normalized.upstream_aitune_gate)
        upstream_aitune_blocked = _upstream_aitune_gate_blocked(upstream_aitune_gate)
        if upstream_aitune_blocked:
            safety_findings.append(
                {
                    "rule_id": "computer_use_blocks_upstream_aitune_gate",
                    "severity": "hard_fail",
                    "message": "Computer-use plans cannot execute or claim readiness while upstream AITune/QES runtime evidence is blocked.",
                }
            )
        route_decision = self.edge_router.route(_edge_request(normalized))
        policy_scan = self.policy_kernel.scan(_policy_targets(normalized, upstream_aitune_gate))
        blocked = bool(safety_findings) or policy_scan.summary.active_hard_fail_count > 0 or upstream_aitune_blocked
        status = "blocked-upstream-gate" if upstream_aitune_blocked else ("blocked" if blocked else _status(normalized))
        created_at = utcnow().isoformat()
        plan = {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "multimodal-computer-use",
            "plan_id": normalized.plan_id,
            "session_id": normalized.session_id,
            "user_goal": normalized.user_goal,
            "status": status,
            "runtime_state": "degraded" if blocked else "live-bound",
            "created_at": created_at,
            "input_modalities": normalized.input_modalities,
            "requested_tasks": normalized.requested_tasks,
            "contains_private_data": normalized.contains_private_data,
            "permission_scope": normalized.permission_scope,
            "sandbox_mode": normalized.sandbox_mode,
            "local_only": normalized.local_only,
            "allow_cloud": normalized.allow_cloud,
            "evidence_refs": normalized.evidence_refs,
            "lanes": lanes,
            "route_decision": route_decision,
            "safety_findings": safety_findings,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "upstream_aitune_gate": upstream_aitune_gate,
            "required_controls": _required_controls(),
            "execution_boundary": "observe-first-act-only-with-policy-human-confirmation",
            "locality_boundary": "local-first-no-cloud-export-for-private-screen-audio-docs",
            "trace_contract": {
                "capture": ["input_modalities", "requested_tasks", "route_decision", "policy_scan", "safety_findings"],
                "replay": "redacted-screen-audio-document-action-timeline",
                "promotion_rule": "computer-use actions remain shadow or read-only until operator confirmation and sandbox evidence exist",
            },
            "operator_actions": _operator_actions(),
            "metadata": normalized.metadata,
        }
        self._persist(plan)
        return plan

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        plans = self._list_plans(limit=limit)
        latest = plans[0] if plans else None
        runtime_state = "static-canon"
        if latest:
            runtime_state = "degraded" if str(latest.get("status") or "").startswith("blocked") else "live-bound"
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "multimodal-computer-use",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "plan_count": len(plans),
            "blocked_count": sum(1 for plan in plans if str(plan.get("status") or "").startswith("blocked")),
            "shadow_count": sum(1 for plan in plans if plan.get("status") == "planned-shadow"),
            "observe_ready_count": sum(1 for plan in plans if plan.get("status") == "observe-ready"),
            "latest_plan": latest,
            "plans": plans,
            "required_controls": _required_controls(),
            "research_lanes": _research_lanes(),
            "operator_actions": _operator_actions(),
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        return {
            **summary,
            "source_documents": [
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md#multimodal-computer-use",
                "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
                "docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md",
            ],
            "assimilation_pattern": "screen-audio-document-browser-actions-through-observe-first-local-policy-gated-plans",
            "execution_boundary": "observe-first-act-only-with-policy-human-confirmation",
            "promotion_boundary": "OS-and-browser-actions-require-operator-approval-sandbox-redaction-route-proof-and-trace-replay",
        }

    def safety_cases(self) -> dict[str, Any]:
        plans = self._list_plans(limit=50)
        cases = _safety_cases()
        return {
            "status_label": "LOCKED CANON",
            "authority": "NexusBrain",
            "surface_id": "multimodal-computer-use",
            "case_count": len(cases),
            "safety_cases": cases,
            "latest_plan": plans[0] if plans else None,
            "blocked_plan_count": sum(1 for plan in plans if plan.get("status") == "blocked"),
            "shadow_plan_count": sum(1 for plan in plans if plan.get("status") == "planned-shadow"),
            "execution_boundary": "observe-first-act-only-with-policy-human-confirmation",
            "locality_boundary": "local-first-no-cloud-export-for-private-screen-audio-docs",
            "operator_actions": _operator_actions(),
        }

    def _persist(self, plan: dict[str, Any]) -> None:
        self._memory_plans.insert(0, plan)
        self._memory_plans = self._memory_plans[:50]
        if self.plans_dir is not None:
            safe_id = plan["plan_id"].replace(":", "_").replace("/", "_")
            path = self.plans_dir / f"{safe_id}.json"
            plan["artifact_path"] = str(path)
            path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    def _list_plans(self, *, limit: int) -> list[dict[str, Any]]:
        plans = list(self._memory_plans)
        seen = {plan.get("plan_id") for plan in plans}
        if self.plans_dir is not None:
            for path in self.plans_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                if payload.get("plan_id") not in seen:
                    plans.append(payload)
        plans.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return plans[:limit]


def _lanes_for(request: ComputerUsePlanRequest) -> list[dict[str, str]]:
    configured = {
        "screen_agent": ("screen-agents", "Observe screen state, segment UI, and plan next actions."),
        "ocr": ("OCR", "Extract text from screenshots, browser pages, PDFs, and documents."),
        "vlm_route": ("VLM-routing", "Route visual tasks to local or remote vision-language models with confidence proof."),
        "document_understanding": ("document-understanding", "Parse layout, tables, forms, citations, and source evidence."),
        "asr": ("ASR-TTS", "Transcribe spoken input and keep audio evidence scoped to consent."),
        "tts": ("ASR-TTS", "Generate spoken output only from approved redacted content."),
        "browser_control": ("OS-browser-control", "Browser action planning and execution with sandbox and operator gates."),
        "os_control": ("OS-browser-control", "Operating-system action planning and execution with sandbox and operator gates."),
        "trace_replay": ("trace-replay", "Replay screen, audio, document, route, policy, and action evidence."),
    }
    lanes: dict[str, dict[str, str]] = {}
    for task in request.requested_tasks:
        lane_id, label = configured[task]
        state = "shadow-only" if task in {"browser_control", "os_control"} else "mapped"
        if task in {"browser_control", "os_control"} and request.sandbox_mode == "operator_confirmed":
            state = "approval-ready"
        lanes[lane_id] = {"lane_id": lane_id, "label": label, "state": state}
    if not lanes:
        lanes["screen-agents"] = {
            "lane_id": "screen-agents",
            "label": "Default observe-only screen context lane.",
            "state": "mapped",
        }
    return list(lanes.values())


def _safety_findings(request: ComputerUsePlanRequest) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    needs_permission = bool(
        request.contains_private_data
        or {"screenshot", "screen", "audio", "document", "browser_page"} & set(request.input_modalities)
        or {"screen_agent", "browser_control", "os_control"} & set(request.requested_tasks)
    )
    if needs_permission and request.permission_scope not in {"operator-approved-local", "automation-approved", "public-demo"}:
        findings.append(
            {
                "rule_id": "computer_use_requires_operator_permission",
                "severity": "hard_fail",
                "message": "Screen, browser, audio, document, or private computer-use context requires explicit operator permission.",
            }
        )
    if {"browser_control", "os_control"} & set(request.requested_tasks) and request.sandbox_mode == "none":
        findings.append(
            {
                "rule_id": "computer_use_control_requires_sandbox",
                "severity": "hard_fail",
                "message": "OS and browser control require a read-only, shadow, or operator-confirmed sandbox boundary.",
            }
        )
    if request.contains_private_data and not request.local_only:
        findings.append(
            {
                "rule_id": "private_multimodal_context_requires_local_only",
                "severity": "hard_fail",
                "message": "Private screen, document, browser, or audio context must remain local-only.",
            }
        )
    if request.contains_private_data and request.allow_cloud:
        findings.append(
            {
                "rule_id": "private_multimodal_context_blocks_cloud_export",
                "severity": "hard_fail",
                "message": "Private multimodal computer-use context cannot be exported to cloud routes by default.",
            }
        )
    if request.permission_scope in {"operator-approved-local", "automation-approved"} and not request.evidence_refs:
        findings.append(
            {
                "rule_id": "computer_use_permission_requires_evidence_ref",
                "severity": "warning",
                "message": "Operator or automation approval should carry a consent or runbook evidence reference.",
            }
        )
    return findings


def _policy_targets(request: ComputerUsePlanRequest, upstream_aitune_gate: dict[str, Any]) -> list[dict[str, Any]]:
    control_requested = bool({"browser_control", "os_control"} & set(request.requested_tasks))
    write_enabled = control_requested and request.sandbox_mode in {"none", "operator_confirmed"}
    targets = [
        {
            "target_id": f"computer-use::{request.plan_id}",
            "target_type": "tool_execution",
            "metadata": {
                "write_enabled": write_enabled,
                "sandboxed": request.sandbox_mode != "none",
                "tool_scope": ",".join(request.requested_tasks),
            },
        }
    ]
    if _upstream_aitune_gate_blocked(upstream_aitune_gate):
        targets.append(
            {
                "target_id": f"computer-use-upstream-runtime::{request.plan_id}",
                "target_type": "tool_execution",
                "metadata": {
                    "write_enabled": True,
                    "sandboxed": False,
                    "upstream_aitune_gate": upstream_aitune_gate,
                },
            }
        )
    return targets


def _edge_request(request: ComputerUsePlanRequest) -> EdgeWorkloadRequest:
    return EdgeWorkloadRequest(
        workload_id=request.plan_id,
        workload_type=_workload_type(request),
        input_modalities=list(request.input_modalities),
        data_sensitivity="private" if request.contains_private_data else "internal",
        offline_required=request.local_only or request.contains_private_data or not request.allow_cloud,
        quality_priority="balanced",
        hardware_snapshot=request.hardware_snapshot,
        upstream_aitune_gate=request.upstream_aitune_gate,
        metadata={"source": "multimodal-computer-use", "session_id": request.session_id},
    )


def _workload_type(request: ComputerUsePlanRequest) -> str:
    tasks = set(request.requested_tasks)
    if "asr" in tasks:
        return "transcription"
    if "document_understanding" in tasks:
        return "document_processing"
    if tasks & {"screen_agent", "ocr", "vlm_route"}:
        return "vision"
    return "chat"


def _status(request: ComputerUsePlanRequest) -> str:
    if {"browser_control", "os_control"} & set(request.requested_tasks):
        return "planned-shadow" if request.sandbox_mode != "operator_confirmed" else "approval-ready"
    if request.contains_private_data or request.sandbox_mode == "shadow":
        return "planned-shadow"
    return "observe-ready"


def _upstream_aitune_gate(gate: dict[str, Any]) -> dict[str, Any]:
    blockers = list(gate.get("blockers") or gate.get("readiness_blockers") or [])
    status = str(gate.get("status") or "not_provided")
    can_execute_here = gate.get("can_execute_here")
    if can_execute_here is False and not blockers:
        blockers.append("upstream_aitune_execution_not_ready")
    if status in {"blocked", "blocked-upstream-gate"} and not blockers:
        blockers.append("upstream_aitune_gate_blocked")
    return {
        **gate,
        "status": status,
        "can_execute_here": can_execute_here,
        "blockers": blockers,
    }


def _upstream_aitune_gate_blocked(gate: dict[str, Any]) -> bool:
    return bool(
        gate.get("can_execute_here") is False
        or gate.get("status") in {"blocked", "blocked-upstream-gate"}
        or gate.get("blockers")
    )


def _required_controls() -> list[str]:
    return [
        "screen_capture_consent",
        "ocr_vlm_grounding",
        "asr_tts_boundary",
        "document_understanding",
        "os_browser_control_sandbox",
        "privacy_redaction",
        "trace_replay",
        "route_evidence",
    ]


def _safety_cases() -> list[dict[str, str]]:
    return [
        {
            "case_id": "screen_capture_consent",
            "label": "Screen, screenshot, browser page, document, and audio inputs require explicit operator permission.",
            "state": "required",
        },
        {
            "case_id": "observe_first_before_action",
            "label": "Computer-use plans observe and propose before executing browser or OS actions.",
            "state": "required",
        },
        {
            "case_id": "os_browser_control_sandbox",
            "label": "Browser and OS control require read-only, shadow, or operator-confirmed sandbox boundaries.",
            "state": "required",
        },
        {
            "case_id": "private_cloud_export_block",
            "label": "Private screen, document, browser, and audio context must not be exported to cloud routes by default.",
            "state": "required",
        },
        {
            "case_id": "trace_replay_redaction",
            "label": "Computer-use evidence must be replayable through redacted screen/audio/document/action timelines.",
            "state": "required",
        },
        {
            "case_id": "route_evidence",
            "label": "Every multimodal lane selection must carry local/cloud route evidence and hardware fit.",
            "state": "required",
        },
    ]


def _research_lanes() -> list[dict[str, str]]:
    return [
        {"lane_id": "OSWorld", "label": "Computer-use task benchmark for screen and OS control.", "state": "cataloged"},
        {"lane_id": "BrowserGym-WebArena", "label": "Browser task suite for web navigation and action grounding.", "state": "cataloged"},
        {"lane_id": "screen-agents", "label": "Screen perception, state tracking, and observe-first planning.", "state": "mapped"},
        {"lane_id": "OCR", "label": "Text extraction for screenshots, PDFs, forms, and UI state.", "state": "mapped"},
        {"lane_id": "VLM-routing", "label": "Vision-language routing with confidence, fallback, and grounding checks.", "state": "research-candidate"},
        {"lane_id": "ASR-TTS", "label": "Audio input and output under consent, redaction, and transcript provenance.", "state": "research-candidate"},
        {"lane_id": "document-understanding", "label": "Layout, table, form, and source-to-claim extraction.", "state": "mapped"},
        {"lane_id": "local-browser-agent", "label": "Local tab/page/history assistant pattern with no default cloud export.", "state": "mapped"},
    ]


def _operator_actions() -> dict[str, dict[str, str]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/multimodal-computer-use"},
        "plan": {"method": "POST", "endpoint": "/ops/brain/multimodal-computer-use/plans"},
        "safety_cases": {"method": "GET", "endpoint": "/ops/brain/computer-use/safety-cases"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/multimodal-computer-use"},
        "visualops": {"method": "GET", "endpoint": "/ops/brain/canon/visualops"},
    }
