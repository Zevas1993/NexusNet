from __future__ import annotations

from typing import Any


SOURCE_DOCUMENT = "NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md"

STATE_TAXONOMY = [
    "live-bound",
    "degraded",
    "static-canon",
    "research-candidate",
    "shadow-only",
]

REQUIRED_SURFACES: dict[str, str] = {
    "overview": "Brain authority, lock state, live/degraded/static state, and promotion posture.",
    "input-ingestion": "User commands, files, project notes, code snippets, transcripts, APIs, webhooks, streams, source permissions, and freshness.",
    "live-flow-trace": "Route, model, memory, tool, policy, eval, and output trace correlation.",
    "neural-core": "NexusBrain routes, lock state, expert routing, policy decisions, and fallback paths.",
    "ao-hive": "AO roles, active work, context shards, model/tool permissions, and collaboration state.",
    "experts-hive": "Domain-specialized expert mini-brains, expert routing, evidence response, veto escalation, and memory feedback.",
    "context-memory": "Memory quality, source-to-claim maps, graph health, stale memory, and privacy controls.",
    "governance-observability": "Policies, GenAI trace mapping, redaction, audit trails, and export readiness.",
    "connections-protocols": "MCP, A2A, AG-UI, ACP, identities, consent, trust envelopes, and revocation.",
    "communication-integration": "Webhooks, message buses, event streams, real-time sync, external services, notifications, and collaboration channels.",
    "tools-execution": "Tool registry, sandboxing, approvals, failures, runtime isolation, and replay traces.",
    "runtime-lab": "Quantization formats, backend eligibility, cache economics, speculative decoding, and runtime scorecards.",
    "eval-center": "GAIA, tau-bench, OSWorld, SWE-bench, BrowserGym/WebArena, RAG, private evals, and promotion blockers.",
    "artifact-trust": "Model provenance, signatures, AI-BOM, unsafe serialization, scanner results, and license review.",
    "hardware-matrix": "Browser, desktop, mobile, NPU, GPU, CPU, server, and edge deployment lanes.",
    "visualops": "Screen, browser, document, audio, OS control, computer-use safety, and task traces.",
    "dreaming-evolution": "Self-review, autonomous update proposals, shadow simulations, promotion provenance, and rollback.",
    "self-improvement-layer": "Experience capture, event schema, triage, provenance, eval generation, improvement queue, policies, and regression gates.",
    "outputs-deliverables": "Architecture diagrams, implementation plans, source code, documentation, roadmaps, reports, working artifacts, exports, packages, and memory feedback.",
    "forward-radar": "Living watchlist for quantization, protocols, evals, memory, supply chain, edge runtimes, and computer use.",
}

SURFACE_COMPLIANCE_CONTROLS: dict[str, list[str]] = {
    "overview": [
        "current_activity",
        "brain_authority",
        "active_command",
        "state_taxonomy",
        "operator_trace",
    ],
    "input-ingestion": [
        "user_commands",
        "uploaded_files",
        "project_notes",
        "code_snippets",
        "meeting_transcripts",
        "external_apis",
        "webhooks_events",
        "realtime_streams",
        "source_permissions",
        "freshness",
    ],
    "live-flow-trace": [
        "route_correlation",
        "model_route",
        "memory_route",
        "tool_route",
        "policy_decision",
        "eval_evidence",
        "output_trace",
    ],
    "neural-core": [
        "brain_authority",
        "route_lock_state",
        "expert_routing",
        "policy_decision",
        "fallback_path",
        "memory_controller",
        "learning_controller",
        "self_check",
    ],
    "ao-hive": [
        "role_registry",
        "delegation_status",
        "per_ao_context",
        "model_tool_permissions",
        "governance_constraints",
        "collaboration_state",
    ],
    "experts-hive": [
        "domain_roster",
        "mini_nexusnet_per_expert",
        "expert_routing",
        "evidence_response",
        "model_tool_permissions",
        "consensus_signal",
        "veto_escalation",
        "memory_feedback",
    ],
    "governance-observability": [
        "policy_id",
        "decision_state",
        "allowed_denied_reason",
        "audit_event",
        "redaction_state",
    ],
    "runtime-lab": [
        "formats",
        "methods",
        "cache_economics",
        "backend_compatibility",
        "eval_deltas",
        "hardware_fit",
    ],
    "connections-protocols": [
        "identity",
        "permissions",
        "consent",
        "trust_envelopes",
        "revocation",
    ],
    "communication-integration": [
        "webhooks",
        "message_bus",
        "event_streams",
        "real_time_sync",
        "external_integrations",
        "notifications",
        "chat_collaboration",
        "protocol_trust",
    ],
    "tools-execution": [
        "tool_registry",
        "sandbox_state",
        "approval_path",
        "failure_capture",
        "runtime_isolation",
        "replay_trace",
    ],
    "eval-center": [
        "held_out_tasks",
        "regression_gates",
        "promotion_blockers",
        "pass_fail_trends",
        "autonomy_confidence",
    ],
    "context-memory": [
        "retrieval_quality",
        "source_to_claim_maps",
        "provenance",
        "stale_memory_queue",
        "privacy_controls",
    ],
    "artifact-trust": [
        "provenance",
        "signatures",
        "unsafe_serialization",
        "scanner_status",
        "license_state",
    ],
    "hardware-matrix": [
        "deployment_lane",
        "backend_runtime",
        "hardware_fit",
        "driver_stack",
        "fallback_path",
        "certification_state",
    ],
    "visualops": [
        "screen_context",
        "ocr",
        "vlm_routing",
        "action_permissions",
        "trace_replay",
        "human_approval",
    ],
    "dreaming-evolution": [
        "candidate_state",
        "shadow_simulation",
        "promotion_provenance",
        "rollback_evidence",
        "operator_approval",
    ],
    "self-improvement-layer": [
        "experience_capture",
        "improvement_event_schema",
        "data_triage",
        "provenance_tracking",
        "evaluation_generation",
        "improvement_queue",
        "memory_prompt_policy",
        "training_candidate_review",
        "regression_gates",
    ],
    "outputs-deliverables": [
        "architecture_diagrams",
        "implementation_plans",
        "source_code",
        "documentation",
        "roadmaps",
        "reports_analytics",
        "working_artifacts",
        "exports_packages",
        "memory_feedback",
    ],
}

DEFAULT_EXPERT_HIVE_ROSTER: list[dict[str, Any]] = [
    {"subject": "coder", "display_name": "Coder Expert", "role_hint": "Code synthesis, repair, and validation."},
    {"subject": "strategist", "display_name": "Strategist Expert", "role_hint": "Long-horizon planning and objective decomposition."},
    {"subject": "analyst", "display_name": "Analyst Expert", "role_hint": "Evidence weighting and structured comparison."},
    {"subject": "researcher", "display_name": "Researcher Expert", "role_hint": "Multi-source synthesis and contradiction handling."},
    {"subject": "critique", "display_name": "Critique Expert", "role_hint": "Arbitration, challenge, and safety critique."},
    {"subject": "conversationalist", "display_name": "Conversationalist Expert", "role_hint": "Tone, continuity, and dialog shaping."},
    {"subject": "toolsmith", "display_name": "Toolsmith Expert", "role_hint": "Tool schema discipline and chain recovery."},
    {"subject": "security", "display_name": "Security Expert", "role_hint": "Misuse analysis and secure patching."},
    {"subject": "memory-weaver", "display_name": "Memory Weaver Expert", "role_hint": "Multi-plane memory weaving and budgeting."},
    {"subject": "meta-reasoner", "display_name": "Meta Reasoner Expert", "role_hint": "Multi-expert synthesis and reflective oversight."},
    {"subject": "router", "display_name": "Router Expert", "role_hint": "Budget, routing, and fallback policy."},
    {"subject": "linguist", "display_name": "Linguist Expert", "role_hint": "Multilingual generation and register control."},
    {"subject": "vision", "display_name": "Vision Expert", "role_hint": "OCR, layout, and image grounding."},
    {"subject": "audio", "display_name": "Audio Expert", "role_hint": "ASR, spoken instruction grounding, and timing."},
    {"subject": "simulation", "display_name": "Simulation Expert", "role_hint": "Rollouts, counterfactuals, and dream scenarios."},
    {"subject": "builder", "display_name": "Builder Expert", "role_hint": "Feature assembly and artifact validation."},
    {"subject": "instructor", "display_name": "Instructor Expert", "role_hint": "Scaffolding, questioning, and mastery checks."},
    {"subject": "intent-mapper", "display_name": "Intent Mapper Expert", "role_hint": "Intent classification and ambiguity reduction."},
    {"subject": "critic-historian", "display_name": "Critic Historian Expert", "role_hint": "Chronology repair and evidence-weighted historical critique."},
]

BOOK_GATE_SPECS: list[dict[str, Any]] = [
    {
        "gate_id": "input-ingestion-permission-freshness",
        "label": "Input pages expose commands, files, notes, snippets, transcripts, APIs, webhooks, streams, permissions, and freshness before routing.",
        "surface_id": "input-ingestion",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["input-ingestion"],
    },
    {
        "gate_id": "live-flow-route-correlation",
        "label": "Live Flow pages correlate route, model, memory, tool, policy, eval, and output trace evidence.",
        "surface_id": "live-flow-trace",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["live-flow-trace"],
    },
    {
        "gate_id": "neural-core-orchestrator-authority",
        "label": "Neural Core pages expose NexusBrain authority, route lock state, expert routing, policy decisions, fallbacks, memory, learning, and self-check.",
        "surface_id": "neural-core",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["neural-core"],
    },
    {
        "gate_id": "experts-hive-mini-brain-governance",
        "label": "Experts Hive pages expose domain mini-brains, expert routing, evidence response, consensus/veto signals, and memory feedback.",
        "surface_id": "experts-hive",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["experts-hive"],
    },
    {
        "gate_id": "runtime-quantization-scorecard",
        "label": "Quantization/runtime pages cover formats, methods, cache economics, backend compatibility, eval deltas, and hardware fit.",
        "surface_id": "runtime-lab",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["runtime-lab"],
    },
    {
        "gate_id": "protocol-trust-envelope",
        "label": "Agent protocol pages cover identity, permissions, consent, trust envelopes, and revocation.",
        "surface_id": "connections-protocols",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["connections-protocols"],
    },
    {
        "gate_id": "communication-integration-governance",
        "label": "Communication pages cover webhooks, buses, events, sync, external services, notifications, collaboration, and protocol trust.",
        "surface_id": "communication-integration",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["communication-integration"],
    },
    {
        "gate_id": "tool-execution-sandbox-replay",
        "label": "Tool execution pages cover registry, sandbox state, approval path, failure capture, runtime isolation, and replay traces.",
        "surface_id": "tools-execution",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["tools-execution"],
    },
    {
        "gate_id": "held-out-eval-regression",
        "label": "Eval pages show held-out evals and regression gates, not only aggregate scores.",
        "surface_id": "eval-center",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["eval-center"],
    },
    {
        "gate_id": "memory-quality-provenance",
        "label": "Memory pages show quality and provenance, not only counts.",
        "surface_id": "context-memory",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["context-memory"],
    },
    {
        "gate_id": "artifact-supply-chain-trust",
        "label": "Artifact pages show provenance, signatures, unsafe serialization, scanner status, and license state.",
        "surface_id": "artifact-trust",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["artifact-trust"],
    },
    {
        "gate_id": "hardware-deployment-matrix",
        "label": "Hardware pages map browser, desktop, mobile, NPU, GPU, CPU, server, and edge deployment lanes.",
        "surface_id": "hardware-matrix",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["hardware-matrix"],
    },
    {
        "gate_id": "visualops-computer-use-safety",
        "label": "VisualOps pages map screen, browser, document, audio, OS control, safety, and replay traces.",
        "surface_id": "visualops",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["visualops"],
    },
    {
        "gate_id": "evolution-promotion-boundary",
        "label": "Evolution pages keep autonomous updates in candidate or shadow state until promotion gates pass.",
        "surface_id": "dreaming-evolution",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["dreaming-evolution"],
    },
    {
        "gate_id": "self-improvement-governed-loop",
        "label": "Self-improvement pages expose experience capture, triage, provenance, queue, policies, review, and regression gates before behavior changes.",
        "surface_id": "self-improvement-layer",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["self-improvement-layer"],
    },
    {
        "gate_id": "output-delivery-proof-loop",
        "label": "Output pages cover deliverables, artifacts, reports, exports, packages, and memory feedback with replayable proof.",
        "surface_id": "outputs-deliverables",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["outputs-deliverables"],
    },
]

ENDPOINT_REUSE_LEDGER: dict[str, dict[str, Any]] = {
    "product_sweep": {
        "state": "static-canon",
        "endpoint_refs": [],
        "doc_refs": ["docs/NEXUSNET_FULL_PRODUCT_SWEEP_ROADMAP.md"],
        "reason": "Product sweep is currently represented as roadmap/canon material rather than a live endpoint.",
    },
    "protocol": {
        "state": "live-bound",
        "endpoint_refs": ["/ops/brain/acp", "/ops/brain/extensions", "/ops/brain/gateway"],
        "doc_refs": [],
        "reason": "Protocol, ACP, extension, and gateway surfaces already exist and remain subordinate to NexusBrain.",
    },
    "training": {
        "state": "live-bound",
        "endpoint_refs": ["/ops/brain/curriculum", "/ops/brain/distill-dataset", "/ops/brain/dream"],
        "doc_refs": [],
        "reason": "Curriculum, distillation, and recursive dream routes are reused for training/evolution visibility.",
    },
    "license_review": {
        "state": "live-bound",
        "endpoint_refs": ["/ops/brain/extensions/certifications", "/ops/brain/extensions/policy-sets"],
        "doc_refs": [],
        "reason": "Extension certification and policy-set endpoints are reused for artifact and license/trust posture.",
    },
    "replacement_readiness": {
        "state": "live-bound",
        "endpoint_refs": ["/ops/brain/visualizer/replacement-readiness/compare", "/ops/brain/teachers/evidence", "/ops/brain/promotions"],
        "doc_refs": [],
        "reason": "Teacher evidence, promotion, and visualizer comparison endpoints are reused for replacement-readiness inspection.",
    },
    "operator": {
        "state": "live-bound",
        "endpoint_refs": ["/chat", "/ops/brain/core", "/ops/brain/operations"],
        "doc_refs": [],
        "reason": "Operator chat, core summary, and NexusBrain operations are reused as the command authority path.",
    },
}


def build_canon_realization(
    *,
    session_id: str | None,
    pages: list[dict[str, Any]],
    research_lanes: list[dict[str, Any]],
    build_gates: list[dict[str, Any]],
    cockpit: dict[str, Any],
    operations_summary: dict[str, Any],
) -> dict[str, Any]:
    page_map = {page.get("page_id"): page for page in pages}
    surfaces = {
        surface_id: _surface_record(surface_id=surface_id, requirement=requirement, page=page_map.get(surface_id))
        for surface_id, requirement in REQUIRED_SURFACES.items()
    }
    coverage = _coverage(surfaces)
    book_gates = _book_gates(surfaces)
    latest_command = operations_summary.get("latest_command") or None
    active_command_id = latest_command.get("command_id") if latest_command else None
    payload = {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "session_id": session_id,
        "state_taxonomy": STATE_TAXONOMY,
        "required_surface_ids": list(REQUIRED_SURFACES.keys()),
        "coverage": coverage,
        "endpoint_reuse_ledger": ENDPOINT_REUSE_LEDGER,
        "live_bindings": {
            "active_command_id": active_command_id,
            "operation_state": operations_summary.get("state", "standby"),
            "cockpit_surface_id": cockpit.get("surface_id"),
            "command_authority": ((cockpit.get("command_bar") or {}).get("authority")) or "NexusBrain",
            "operations_endpoint": "/ops/brain/operations",
            "command_endpoint": "/ops/brain/operations/commands",
            "visualizer_state_endpoint": "/ops/brain/visualizer/state",
        },
        "surfaces": surfaces,
        "book_gates": book_gates,
        "book_gate_coverage": _book_gate_coverage(book_gates),
        "operator_questions": _operator_questions(
            surfaces=surfaces,
            active_command_id=active_command_id,
            operations_summary=operations_summary,
        ),
        "research_lanes": [
            {
                "lane_id": lane.get("lane_id"),
                "label": lane.get("label"),
                "status": lane.get("status"),
                "promotion_gate": lane.get("promotion_gate"),
            }
            for lane in research_lanes
        ],
        "blocking_items": [
            {
                "surface_id": surface_id,
                "state": record["state"],
                "next_action": record["next_action"],
                "promotion_gate": record["promotion_gate"],
            }
            for surface_id, record in surfaces.items()
            if record["state"] != "live-bound"
        ],
        "build_gates": build_gates,
    }
    payload["completion_assessment"] = completion_assessment(payload)
    return payload


def completion_assessment(realization: dict[str, Any]) -> dict[str, Any]:
    surfaces = realization.get("surfaces") or {}
    coverage = realization.get("coverage") or {}
    book_gate_coverage = realization.get("book_gate_coverage") or {}
    operator_questions = realization.get("operator_questions") or {}
    live_bindings = realization.get("live_bindings") or {}
    endpoint_reuse = realization.get("endpoint_reuse_ledger") or {}
    research_lanes = realization.get("research_lanes") or []

    required_surface_count = int(coverage.get("required_surface_count") or len(REQUIRED_SURFACES))
    implemented_surface_count = int(coverage.get("implemented_surface_count") or 0)
    operator_question_count = len(operator_questions)
    required_gate_count = int(book_gate_coverage.get("required_gate_count") or len(BOOK_GATE_SPECS))
    mapped_gate_count = int(book_gate_coverage.get("mapped_gate_count") or 0)
    live_endpoint_categories = int(coverage.get("reused_endpoint_category_count") or 0)
    total_endpoint_categories = max(len(endpoint_reuse), 1)

    runtime_surface = surfaces.get("runtime-lab") or {}
    protocol_surface = surfaces.get("connections-protocols") or {}
    eval_surface = surfaces.get("eval-center") or {}
    memory_surface = surfaces.get("context-memory") or {}
    artifact_surface = surfaces.get("artifact-trust") or {}
    hardware_surface = surfaces.get("hardware-matrix") or {}
    visualops_surface = surfaces.get("visualops") or {}
    evolution_surface = surfaces.get("dreaming-evolution") or {}
    radar_surface = surfaces.get("forward-radar") or {}
    cockpit_surface = surfaces.get("overview") or {}

    gates = [
        _completion_gate(
            gate_id="required-surface-coverage",
            label="All Canon Book control surfaces exist in the Control Panel.",
            state="satisfied" if required_surface_count and implemented_surface_count == required_surface_count else "blocked",
            metric=f"{implemented_surface_count}/{required_surface_count}",
            evidence_refs=["/ops/brain/canon/realization", "/ops/brain/visualizer/state"],
            blockers=[] if implemented_surface_count == required_surface_count else ["Missing required Canon control surfaces."],
        ),
        _completion_gate(
            gate_id="operator-answer-matrix",
            label="The cockpit answers every final operator question from the Canon Book.",
            state="satisfied" if operator_question_count >= 10 else "blocked",
            metric=f"{operator_question_count}/10",
            evidence_refs=["/ops/brain/canon/realization", "/ops/brain/canon/answers/{question_id}"],
            blockers=[] if operator_question_count >= 10 else ["Operator answer matrix is incomplete."],
        ),
        _completion_gate(
            gate_id="book-gate-mapping",
            label="Research refresh build gates are mapped to concrete control surfaces.",
            state="satisfied" if required_gate_count and mapped_gate_count == required_gate_count else "blocked",
            metric=f"{mapped_gate_count}/{required_gate_count}",
            evidence_refs=["/ops/brain/canon/realization"],
            blockers=[] if mapped_gate_count == required_gate_count else ["One or more book gates lacks a mapped control surface."],
        ),
        _completion_gate(
            gate_id="endpoint-reuse",
            label="The canon control plane reuses existing NexusBrain operational endpoints.",
            state="satisfied" if live_endpoint_categories >= 5 else "degraded",
            metric=f"{live_endpoint_categories}/{total_endpoint_categories}",
            evidence_refs=_flatten_endpoint_refs(endpoint_reuse),
            blockers=[] if live_endpoint_categories >= 5 else ["Not enough operational endpoint categories are live-bound."],
        ),
        _surface_completion_gate(
            gate_id="runtime-quantization",
            label="Runtime Lab tracks quantization methods, model formats, cache economics, backend fit, eval deltas, and hardware fit.",
            surface=runtime_surface,
            evidence_refs=[
                "/ops/brain/backends",
                "TurboQuant",
                "GGUF",
                "GPTQ",
                "AWQ",
                "EXL2",
                "KV-cache quantization",
                "LMCache",
            ],
        ),
        _surface_completion_gate(
            gate_id="protocol-trust",
            label="Protocol governance covers identity, permissions, consent, trust envelopes, and revocation.",
            surface=protocol_surface,
            evidence_refs=["/ops/brain/acp", "/ops/brain/extensions", "/ops/brain/gateway", "MCP", "A2A", "ACP", "AG-UI"],
        ),
        _surface_completion_gate(
            gate_id="eval-regression",
            label="Eval Center tracks held-out tasks, regression gates, promotion blockers, trends, and autonomy confidence.",
            surface=eval_surface,
            evidence_refs=["/ops/brain/promotions", "/ops/brain/eval-report", "GAIA", "tau-bench", "OSWorld", "SWE-bench"],
        ),
        _surface_completion_gate(
            gate_id="memory-provenance",
            label="Context and memory pages expose quality, source-to-claim maps, provenance, stale queues, and privacy controls.",
            surface=memory_surface,
            evidence_refs=["/ops/brain/memory/planes", "/ops/brain/graph/status", "GraphRAG", "LightRAG", "RAGChecker"],
        ),
        _surface_completion_gate(
            gate_id="artifact-trust",
            label="Artifact Trust tracks provenance, signatures, unsafe serialization, scanner state, and license posture.",
            surface=artifact_surface,
            evidence_refs=["/ops/brain/teachers", "/ops/brain/extensions/certifications", "safetensors", "Sigstore", "AI-BOM"],
        ),
        _surface_completion_gate(
            gate_id="hardware-matrix",
            label="Hardware Matrix maps browser, desktop, mobile, NPU, GPU, CPU, server, and edge deployment lanes.",
            surface=hardware_surface,
            evidence_refs=["WebNN", "WebGPU", "Apple MLX", "Qualcomm QAIRT", "LiteRT-LM", "ExecuTorch", "OpenVINO", "Windows NPU"],
        ),
        _surface_completion_gate(
            gate_id="visualops",
            label="VisualOps maps screen agents, OCR, VLM routing, document understanding, audio, and OS/browser control safety.",
            surface=visualops_surface,
            evidence_refs=["OSWorld", "screen agents", "OCR", "VLM routing", "ASR", "TTS", "browser control"],
        ),
        _completion_gate(
            gate_id="autonomous-evolution",
            label="Autonomous updates remain in candidate or shadow state until eval, rollback, provenance, and operator approval gates pass.",
            state="guarded" if evolution_surface.get("surface_id") and evolution_surface.get("compliance_controls") else "blocked",
            metric=evolution_surface.get("state") or "missing",
            surface_id=evolution_surface.get("surface_id"),
            evidence_refs=[
                "/ops/brain/promotions",
                "/ops/brain/foundry/status",
                "multi-agent researcher",
                "self-review",
                "shadow simulation",
                "rollback",
            ],
            blockers=[
                "shadow-only promotion boundary remains active until rollback evidence, eval delta, and operator approval pass."
            ],
        ),
        _completion_gate(
            gate_id="forward-radar",
            label="Forward Radar keeps future-facing research watchlists visible without silently promoting candidates.",
            state="research-candidate" if radar_surface.get("state") == "research-candidate" else "blocked",
            metric=f"{len(research_lanes)} lanes",
            surface_id=radar_surface.get("surface_id"),
            evidence_refs=[
                "docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md",
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
            ],
            blockers=[] if radar_surface.get("state") == "research-candidate" else ["Forward Radar surface is not in candidate state."],
        ),
        _completion_gate(
            gate_id="cockpit-command-loop",
            label="Human cockpit can issue NexusBrain commands, inspect live bindings, and queue canon realization work.",
            state="satisfied" if cockpit_surface and live_bindings.get("command_endpoint") else "blocked",
            metric=live_bindings.get("operation_state") or "standby",
            surface_id=cockpit_surface.get("surface_id"),
            evidence_refs=[
                live_bindings.get("command_endpoint") or "/ops/brain/operations/commands",
                live_bindings.get("operations_endpoint") or "/ops/brain/operations",
                "/ops/brain/canon/realize-next",
            ],
            blockers=[] if cockpit_surface and live_bindings.get("command_endpoint") else ["Cockpit command loop is not bound to NexusBrain operations."],
        ),
    ]
    completed_gate_count = sum(1 for gate in gates if gate["control_plane_complete"])
    live_surface_count = int(coverage.get("live_bound_surface_count") or 0)
    non_live_surface_count = max(required_surface_count - live_surface_count, 0)
    completion_percent = round((completed_gate_count / max(len(gates), 1)) * 100)
    ready_for_operator_use = all(
        gate["gate_id"] in {
            "required-surface-coverage",
            "operator-answer-matrix",
            "book-gate-mapping",
            "endpoint-reuse",
            "cockpit-command-loop",
        }
        and gate["control_plane_complete"]
        or gate["gate_id"] not in {
            "required-surface-coverage",
            "operator-answer-matrix",
            "book-gate-mapping",
            "endpoint-reuse",
            "cockpit-command-loop",
        }
        for gate in gates
    )
    full_product_finished = non_live_surface_count == 0 and not any(gate["blockers"] for gate in gates)
    return {
        "status_label": "LOCKED CANON",
        "source_document": realization.get("source_document") or SOURCE_DOCUMENT,
        "session_id": realization.get("session_id"),
        "claim_scope": "canon-control-plane",
        "ready_for_operator_use": bool(ready_for_operator_use),
        "full_product_finished": bool(full_product_finished),
        "completion_percent": completion_percent,
        "completed_gate_count": completed_gate_count,
        "required_gate_count": len(gates),
        "live_bound_surface_count": live_surface_count,
        "non_live_surface_count": non_live_surface_count,
        "next_action_queue_endpoint": "/ops/brain/canon/realize-next",
        "gates": gates,
        "blocking_items": [
            {
                "gate_id": gate["gate_id"],
                "label": gate["label"],
                "blockers": gate["blockers"],
            }
            for gate in gates
            if gate["blockers"]
        ],
    }


def runtime_quantization_scorecard(
    *,
    control_panel: dict[str, Any],
    backend_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    catalog = control_panel.get("quantization_catalog") or {}
    realization = control_panel.get("canon_realization") or {}
    surface = ((realization.get("surfaces") or {}).get("runtime-lab")) or {}
    controls = set(surface.get("compliance_controls") or [])
    backend_summary = backend_summary or {}
    inference_lanes = [
        {
            "lane_id": "speculative-decoding",
            "label": "Speculative Decoding",
            "state": "research-candidate",
            "operator_value": "Reduce decode latency only after task-quality eval deltas remain acceptable.",
            "promotion_gate": "latency-quality-regression",
        },
        {
            "lane_id": "disaggregated-prefill-decode",
            "label": "Disaggregated Prefill/Decode",
            "state": "research-candidate",
            "operator_value": "Separate expensive prefill from token decode so runtime pages can reason about queue economics.",
            "promotion_gate": "serving-topology-capacity-model",
        },
        {
            "lane_id": "prefix-caching",
            "label": "Prefix Caching",
            "state": "mapped",
            "operator_value": "Track repeated system/project prefixes and reuse cache when policy and privacy allow it.",
            "promotion_gate": "cache-privacy-and-correctness",
        },
        {
            "lane_id": "kv-reuse",
            "label": "KV Reuse",
            "state": "mapped",
            "operator_value": "Expose when KV cache is reused, evicted, quantized, or invalidated.",
            "promotion_gate": "kv-lineage-and-staleness",
        },
        {
            "lane_id": "LMCache",
            "label": "LMCache",
            "state": "research-candidate",
            "operator_value": "Watch external KV-cache orchestration for server and multi-agent runtime economics.",
            "promotion_gate": "cache-security-eval-and-runtime-fit",
        },
        {
            "lane_id": "continuous-batching",
            "label": "Continuous Batching",
            "state": "research-candidate",
            "operator_value": "Model queueing efficiency separately from model quality and artifact trust.",
            "promotion_gate": "multi-session-fairness-and-latency",
        },
        {
            "lane_id": "cache-economics",
            "label": "Cache Economics",
            "state": "mapped",
            "operator_value": "Score latency, memory pressure, hit rate, privacy scope, and stale-cache risk together.",
            "promotion_gate": "runtime-scorecard-eval-delta",
        },
    ]
    hardware_lanes = [
        "CPU",
        "NVIDIA GPU",
        "AMD GPU",
        "Apple MLX",
        "Qualcomm QAIRT",
        "WebNN",
        "WebGPU",
        "LiteRT-LM",
        "ExecuTorch",
        "OpenVINO",
        "Ryzen AI",
        "Windows NPU",
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "runtime-lab",
        "surface_state": surface.get("state") or "missing",
        "method_families": catalog.get("method_families") or [],
        "formats": catalog.get("formats") or [],
        "required_fields": catalog.get("required_fields") or [],
        "required_controls": {
            "formats": _runtime_control("formats", controls, bool(catalog.get("formats")), evidence_refs=["GGUF", "safetensors", "ONNX"]),
            "methods": _runtime_control("methods", controls, bool(catalog.get("method_families")), evidence_refs=["TurboQuant", "AWQ", "GPTQ", "EXL2"]),
            "cache_economics": _runtime_control(
                "cache_economics",
                controls,
                True,
                evidence_refs=["prefix-caching", "kv-reuse", "LMCache", "continuous-batching"],
                promotion_gate="runtime-scorecard-eval-delta",
            ),
            "backend_compatibility": _runtime_control(
                "backend_compatibility",
                controls,
                True,
                endpoint="/ops/brain/backends",
                evidence_refs=["backend registry", "runtime eligibility"],
            ),
            "eval_deltas": _runtime_control(
                "eval_deltas",
                controls,
                True,
                endpoint="/ops/brain/promotions",
                evidence_refs=["held-out evals", "regression gates"],
                promotion_gate="held-out-eval-regression",
            ),
            "hardware_fit": _runtime_control(
                "hardware_fit",
                controls,
                True,
                evidence_refs=hardware_lanes,
                promotion_gate="hardware-fit-certification",
            ),
        },
        "inference_architecture_lanes": inference_lanes,
        "hardware_lanes": hardware_lanes,
        "backend_compatibility": {
            "endpoint": "/ops/brain/backends",
            "summary": backend_summary,
        },
        "operator_actions": {
            "inspect_backends": {"method": "GET", "endpoint": "/ops/brain/backends"},
            "run_benchmark": {"method": "POST", "endpoint": "/ops/brain/backends/benchmark"},
            "inspect_runtime_profile": {"method": "GET", "endpoint": "/ops/brain/runtime-profile"},
        },
        "promotion_boundary": "candidate-or-shadow-until-eval-runtime-security-license-and-governance-pass",
        "evidence_refs": [
            "/ops/brain/backends",
            "/ops/brain/runtime-profile",
            "/ops/brain/promotions",
            "docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md",
            "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
        ],
    }


def autonomous_evolution_dossier(realization: dict[str, Any]) -> dict[str, Any]:
    surfaces = realization.get("surfaces") or {}
    surface = surfaces.get("dreaming-evolution") or {}
    live_bindings = realization.get("live_bindings") or {}
    active_command_id = live_bindings.get("active_command_id")
    pipeline = [
        _evolution_stage(
            "observe",
            "Observe and collect runtime traces, operator goals, failures, and forward-radar signals.",
            "NexusBrain",
            "live-bound" if active_command_id else "static-canon",
            ["/ops/brain/operations", "/ops/brain/visualizer/state"],
        ),
        _evolution_stage(
            "multi-agent-research",
            "Dispatch research AOs to compare options, source evidence, and produce candidate dossiers.",
            "ResearchAO",
            "research-candidate",
            [
                "docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md",
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
            ],
        ),
        _evolution_stage(
            "propose-patch",
            "Convert approved research into a bounded patch proposal with ownership, blast radius, and rollback notes.",
            "ImplementationAO",
            "shadow-only",
            ["/ops/brain/canon/realize-next"],
        ),
        _evolution_stage(
            "self-review",
            "Run self-review before any operator sees a promotion recommendation.",
            "SelfReviewAO",
            "shadow-only",
            ["/ops/brain/reflection", "/ops/brain/operations"],
        ),
        _evolution_stage(
            "regression-generation",
            "Generate or select held-out regression tasks covering behavior, policy, memory, runtime, and UI surfaces.",
            "EvalAO",
            "shadow-only",
            ["/ops/brain/promotions", "/ops/brain/eval-report"],
        ),
        _evolution_stage(
            "shadow-run",
            "Run the proposed behavior in shadow mode without replacing the live path.",
            "EvolutionAO",
            "shadow-only",
            ["/ops/brain/dream", "/ops/brain/foundry/status"],
        ),
        _evolution_stage(
            "eval-delta",
            "Compare candidate outputs against baseline quality, latency, safety, cost, and memory provenance.",
            "EvalAO",
            "blocked-until-proof",
            ["/ops/brain/promotions"],
        ),
        _evolution_stage(
            "rollback-plan",
            "Require a rollback path before candidate promotion can be considered.",
            "GovernanceAO",
            "blocked-until-proof",
            ["/ops/brain/promotions"],
        ),
        _evolution_stage(
            "operator-approval",
            "Ask the human operator to approve or deny the candidate promotion with visible evidence.",
            "Operator",
            "blocked-until-approval",
            ["/ops/approvals"],
        ),
        _evolution_stage(
            "promotion",
            "Promote only after eval delta, rollback evidence, artifact trust, and operator approval pass.",
            "NexusBrain",
            "blocked-until-proof",
            ["/ops/brain/promotions"],
        ),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "dreaming-evolution",
        "surface_state": surface.get("state") or "missing",
        "operating_mode": "shadow-governed-autonomous-updates",
        "active_command_id": active_command_id,
        "promotion_boundary": "no-autonomous-live-promotion-without-operator-approval",
        "pipeline": pipeline,
        "required_promotion_evidence": [
            "eval_delta",
            "rollback_evidence",
            "artifact_provenance",
            "security_review",
            "license_review",
            "memory_provenance",
            "operator_approval",
        ],
        "operator_actions": {
            "queue_candidate": {"method": "POST", "endpoint": "/ops/brain/canon/realize-next"},
            "inspect_promotions": {"method": "GET", "endpoint": "/ops/brain/promotions"},
            "inspect_dream_loop": {"method": "GET", "endpoint": "/ops/brain/dream"},
            "record_proof": {"method": "POST", "endpoint": "/ops/brain/canon/answers/update_candidate/events"},
        },
        "evidence_refs": [
            "/ops/brain/operations",
            "/ops/brain/dream",
            "/ops/brain/promotions",
            "/ops/brain/foundry/status",
            "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md#autonomous-update-canon",
        ],
        "blockers": [
            "No autonomous live promotion is allowed until eval_delta, rollback_evidence, artifact_provenance, security_review, license_review, memory_provenance, and operator_approval are present."
        ],
    }


def self_improvement_scorecard(
    realization: dict[str, Any],
    *,
    queue_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("self-improvement-layer")) or {}
    queue = queue_summary or {}
    stages = [
        _improvement_stage("experience-capture", "Capture structured interaction, multimodal, tool, failure, metric, and feedback signals.", "live-bound"),
        _improvement_stage("improvement-event-schema", "Normalize raw traces into ImprovementEvent records with safety and source fields.", "live-bound"),
        _improvement_stage("data-triage", "Classify events into memory, eval, training-candidate, discard, or review lanes.", "live-bound"),
        _improvement_stage("provenance-tracking", "Keep source evidence, context sources, and verification refs attached to every candidate.", "live-bound"),
        _improvement_stage("evaluation-generation", "Prefer eval-case creation from failures before changing behavior.", "live-bound"),
        _improvement_stage("improvement-queue", "Hold proposed improvements behind validation, approval, deployment, monitoring, and rollback transitions.", "live-bound"),
        _improvement_stage("memory-prompt-policy", "Allow memory, prompt, policy, and routing updates before model-weight changes.", "live-bound"),
        _improvement_stage("training-candidate-review", "Training examples stay human-reviewable candidates and never auto-train.", "live-bound"),
        _improvement_stage("regression-gates", "Require continuity, factuality, tool-use, safety, privacy, multimodal, cost, and latency checks.", "live-bound"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "self-improvement-layer",
        "surface_state": surface.get("state") or "missing",
        "authority": "NexusBrain",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["self-improvement-layer"],
        "pipeline_stages": stages,
        "queue_summary": {
            "item_count": queue.get("item_count", 0),
            "status_counts": queue.get("status_counts", {}),
            "queue_endpoint": "/ops/brain/self-improvement/queue",
        },
        "optimization_sequence": [
            "memory_rag_update",
            "prompt_policy_candidate",
            "routing_policy_candidate",
            "eval_case_expansion",
            "human_reviewed_training_candidate",
        ],
        "model_update_boundary": "no-weight-update-without-human-review-external-verification-and-regression-gates",
        "operator_actions": {
            "capture_event": {"method": "POST", "endpoint": "/ops/brain/self-improvement/capture"},
            "queue_event": {"method": "POST", "endpoint": "/ops/brain/self-improvement/events"},
            "inspect_queue": {"method": "GET", "endpoint": "/ops/brain/self-improvement/queue"},
            "review_queue_item": {"method": "GET", "endpoint_template": "/ops/brain/self-improvement/queue/{queue_id}/review"},
            "inspect_evals": {"method": "GET", "endpoint": "/ops/brain/canon/eval-suite"},
            "inspect_memory": {"method": "GET", "endpoint": "/ops/brain/canon/memory-provenance"},
            "inspect_evolution": {"method": "GET", "endpoint": "/ops/brain/canon/evolution-dossier"},
        },
        "evidence_refs": [
            "docs/SELF_IMPROVEMENT_LAYER.md",
            "/ops/brain/self-improvement/queue",
            "/ops/brain/canon/eval-suite",
            "/ops/brain/canon/memory-provenance",
        ],
    }


def protocol_trust_scorecard(realization: dict[str, Any]) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("connections-protocols")) or {}
    protocols = [
        _protocol_record("MCP", "Tool and resource protocol", ["tools", "resources", "permissions"]),
        _protocol_record("A2A", "Agent-to-agent task delegation protocol", ["delegation", "identity", "task state"]),
        _protocol_record("ACP", "Agent communication/control protocol", ["agent control", "workspace context", "audit"]),
        _protocol_record("AG-UI", "Agent-to-UI event and interaction protocol", ["events", "human approval", "state sync"]),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "connections-protocols",
        "surface_state": surface.get("state") or "missing",
        "authority": "NexusBrain",
        "protocols": protocols,
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["connections-protocols"],
        "trust_envelope": {
            "decision_authority": "NexusBrain",
            "identity_endpoint": "/ops/brain/acp",
            "permission_endpoint": "/ops/brain/security/permissions",
            "consent_endpoint": "/ops/approvals",
            "trust_envelope_endpoint": "/ops/brain/extensions",
            "revocation_endpoint": "/ops/brain/gateway",
        },
        "promotion_boundary": "protocols-remain-adapters-not-brain-authority",
        "evidence_refs": [
            "/ops/brain/acp",
            "/ops/brain/extensions",
            "/ops/brain/gateway",
            "/ops/brain/security/permissions",
        ],
    }


def communication_integration_scorecard(realization: dict[str, Any]) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("communication-integration")) or {}
    lanes = [
        _integration_lane("webhooks", "Inbound and outbound webhook triggers remain permissioned, traceable, and revocable.", "mapped"),
        _integration_lane("message-bus", "Message bus traffic carries identity, consent, correlation id, and replay evidence.", "research-candidate"),
        _integration_lane("event-streams", "Event streams publish typed updates from NexusBrain, AOs, tools, memory, and outputs.", "mapped"),
        _integration_lane("real-time-sync", "Real-time operator and wrapper state sync cannot bypass NexusBrain authority.", "mapped"),
        _integration_lane("external-integrations", "Third-party services are adapter-governed with scoped trust envelopes.", "research-candidate"),
        _integration_lane("email-notifications", "Notifications ship only with redaction, consent, and audit metadata.", "static-canon"),
        _integration_lane("chat-collaboration", "Human and agent collaboration channels bind messages to command, policy, and memory context.", "mapped"),
        _integration_lane("mcp-a2a-acp-agui", "MCP, A2A, ACP, and AG-UI remain protocol adapters under NexusBrain trust review.", "mapped"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "communication-integration",
        "surface_state": surface.get("state") or "missing",
        "authority": "NexusBrain",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["communication-integration"],
        "integration_lanes": lanes,
        "integration_rule": "external-communications-remain-consent-permission-trust-envelope-and-revocation-gated",
        "operator_actions": {
            "inspect_protocols": {"method": "GET", "endpoint": "/ops/brain/canon/protocol-trust"},
            "inspect_gateway": {"method": "GET", "endpoint": "/ops/brain/gateway"},
            "inspect_extensions": {"method": "GET", "endpoint": "/ops/brain/extensions"},
            "inspect_permissions": {"method": "GET", "endpoint": "/ops/brain/security/permissions"},
            "record_communication_proof": {"method": "POST", "endpoint": "/ops/brain/canon/answers/trusted_protocol/events"},
        },
        "evidence_refs": [
            "/ops/brain/canon/protocol-trust",
            "/ops/brain/gateway",
            "/ops/brain/extensions",
            "/ops/brain/security/permissions",
            "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md#agent-protocol-future",
        ],
    }


def eval_suite_scorecard(realization: dict[str, Any]) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("eval-center")) or {}
    eval_families = [
        _eval_family("GAIA", "General assistant reasoning and tool-use tasks", "research-candidate"),
        _eval_family("tau-bench", "Task-agent behavior and policy-following evals", "research-candidate"),
        _eval_family("OSWorld", "Computer-use and operating-system task evals", "research-candidate"),
        _eval_family("SWE-bench", "Software engineering issue-resolution evals", "research-candidate"),
        _eval_family("BrowserGym-WebArena", "Browser control, web task, and UI navigation evals", "research-candidate"),
        _eval_family("RAGChecker", "Retrieval quality and source-grounding evals", "research-candidate"),
        _eval_family("NexusNet-held-out", "Private regression tasks from NexusNet traces and canon gates", "mapped"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "eval-center",
        "surface_state": surface.get("state") or "missing",
        "eval_families": eval_families,
        "promotion_gates": SURFACE_COMPLIANCE_CONTROLS["eval-center"],
        "operator_actions": {
            "inspect_promotions": {"method": "GET", "endpoint": "/ops/brain/promotions"},
            "inspect_eval_report": {"method": "GET", "endpoint": "/ops/brain/eval-report"},
            "record_eval_proof": {"method": "POST", "endpoint": "/ops/brain/canon/answers/eval_evidence/events"},
        },
        "autonomous_update_rule": "no-update-without-held-out-regression-and-rollback",
        "evidence_refs": [
            "/ops/brain/promotions",
            "/ops/brain/eval-report",
            "/ops/brain/canon/evolution-dossier",
        ],
    }


def memory_provenance_scorecard(realization: dict[str, Any]) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("context-memory")) or {}
    memory_lanes = [
        _canon_lane("GraphRAG", "Graph-grounded retrieval and relationship-aware source traversal.", "research-candidate"),
        _canon_lane("LightRAG", "Low-overhead graph/RAG indexing pattern for local and edge contexts.", "research-candidate"),
        _canon_lane("HippoRAG", "Long-memory inspired retrieval and consolidation watch lane.", "research-candidate"),
        _canon_lane("RAGChecker", "Retrieval answerability, grounding, and source quality evaluation.", "mapped"),
        _canon_lane("source-to-claim", "Every important answer claim can point back to a memory, source, trace, or explicit unknown.", "mapped"),
        _canon_lane("memory-consolidation", "Stale, duplicate, private, and contradictory memory items move through a governed consolidation queue.", "mapped"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "context-memory",
        "surface_state": surface.get("state") or "missing",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["context-memory"],
        "memory_lanes": memory_lanes,
        "quality_model": {
            "answerability_gate": "source-backed-or-explicitly-unknown",
            "provenance_policy": "claim-level-source-map-required-for-promoted-answers",
            "staleness_policy": "stale-memory-queues-before-reuse",
            "privacy_policy": "private-memory-never-promotes-without-consent-and-redaction",
        },
        "operator_actions": {
            "inspect_memory_planes": {"method": "GET", "endpoint": "/ops/brain/memory/planes"},
            "inspect_graph": {"method": "GET", "endpoint": "/ops/brain/graph/status"},
            "record_memory_proof": {"method": "POST", "endpoint": "/ops/brain/canon/answers/memory_support/events"},
        },
        "evidence_refs": [
            "/ops/brain/memory/planes",
            "/ops/brain/graph/status",
            "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md#memory-rag-and-knowledge-graphs",
        ],
    }


def artifact_trust_scorecard(realization: dict[str, Any]) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("artifact-trust")) or {}
    controls = [
        _supply_chain_control("safetensors", "Prefer safe tensor formats and block unsafe pickle loading unless explicitly reviewed.", "mapped"),
        _supply_chain_control("pickle-risk", "Surface serialization risk and scanner results before model/artifact use.", "mapped"),
        _supply_chain_control("Sigstore", "Watch model signing and transparency logs for artifact provenance.", "research-candidate"),
        _supply_chain_control("AI-BOM", "Track model, dataset, dependency, license, and tool lineage as a bill of materials.", "research-candidate"),
        _supply_chain_control("model-signing", "Require signature or trusted provenance for promoted model artifacts.", "mapped"),
        _supply_chain_control("license-review", "Expose license and redistribution posture before artifact promotion.", "mapped"),
        _supply_chain_control("malicious-model-scan", "Scan for unsafe serialization, suspicious files, and plugin/runtime risk.", "mapped"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "artifact-trust",
        "surface_state": surface.get("state") or "missing",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["artifact-trust"],
        "supply_chain_controls": controls,
        "trust_rule": "no-unsafe-artifact-without-scanner-provenance-license-and-rollback",
        "operator_actions": {
            "inspect_teachers": {"method": "GET", "endpoint": "/ops/brain/teachers"},
            "inspect_certifications": {"method": "GET", "endpoint": "/ops/brain/extensions/certifications"},
            "inspect_backends": {"method": "GET", "endpoint": "/ops/brain/backends"},
            "record_artifact_proof": {"method": "POST", "endpoint": "/ops/brain/canon/answers/artifact_model/events"},
        },
        "evidence_refs": [
            "/ops/brain/teachers",
            "/ops/brain/extensions/certifications",
            "/ops/brain/backends",
            "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md#ai-supply-chain-security",
        ],
    }


def hardware_matrix_scorecard(realization: dict[str, Any]) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("hardware-matrix")) or {}
    deployment_lanes = [
        _deployment_lane("WebNN", "Browser NPU/GPU/CPU acceleration path.", "research-candidate"),
        _deployment_lane("WebGPU", "Browser GPU compute lane for local UI-adjacent inference.", "research-candidate"),
        _deployment_lane("Apple MLX", "Apple Silicon local inference and training lane.", "research-candidate"),
        _deployment_lane("Qualcomm QAIRT", "Qualcomm mobile/edge NPU deployment lane.", "research-candidate"),
        _deployment_lane("LiteRT-LM", "Android and edge LiteRT GenAI lane.", "research-candidate"),
        _deployment_lane("ExecuTorch", "PyTorch edge/mobile execution lane.", "research-candidate"),
        _deployment_lane("OpenVINO", "Intel CPU/GPU/NPU optimized inference lane.", "research-candidate"),
        _deployment_lane("Ryzen AI", "AMD NPU deployment lane.", "research-candidate"),
        _deployment_lane("Windows NPU", "Windows local NPU path for cockpit and wrapper deployment.", "research-candidate"),
        _deployment_lane("CPU", "Universal safe fallback lane.", "mapped"),
        _deployment_lane("Server GPU", "High-throughput hosted inference lane when local hardware is insufficient.", "mapped"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "hardware-matrix",
        "surface_state": surface.get("state") or "missing",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["hardware-matrix"],
        "deployment_lanes": deployment_lanes,
        "fallback_rule": "prefer-local-accelerator-when-certified-else-safe-cpu-or-server-lane",
        "operator_actions": {
            "inspect": {"method": "GET", "endpoint": "/ops/brain/hardware-matrix"},
            "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/hardware-matrix"},
            "inspect_runtime_profile": {"method": "GET", "endpoint": "/ops/brain/runtime-profile"},
            "inspect_backends": {"method": "GET", "endpoint": "/ops/brain/backends"},
            "run_benchmark": {"method": "POST", "endpoint": "/ops/brain/backends/benchmark"},
        },
        "evidence_refs": [
            "/ops/brain/runtime-profile",
            "/ops/brain/backends",
            "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md#edge-browser-and-local-hardware-roadmap",
        ],
    }


def visualops_scorecard(realization: dict[str, Any]) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("visualops")) or {}
    lanes = [
        _computer_use_lane("screen-agents", "Screen state observation, segmentation, and task planning.", "research-candidate"),
        _computer_use_lane("OCR", "Text extraction from screenshots, PDFs, documents, and app surfaces.", "mapped"),
        _computer_use_lane("VLM-routing", "Route visual tasks to vision-language models with explicit confidence and fallback.", "research-candidate"),
        _computer_use_lane("document-understanding", "Document layout, table, form, and source extraction.", "mapped"),
        _computer_use_lane("ASR-TTS", "Audio input/output lanes for operator and meeting workflows.", "research-candidate"),
        _computer_use_lane("OS-browser-control", "Browser and operating-system actions gated by policy and human approval.", "shadow-only"),
        _computer_use_lane("trace-replay", "Replay computer-use actions with screenshots, decisions, and rollback notes.", "mapped"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "visualops",
        "surface_state": surface.get("state") or "missing",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["visualops"],
        "computer_use_lanes": lanes,
        "safety_rule": "observe-first-act-only-with-policy-and-human-approval",
        "operator_actions": {
            "inspect_visualizer": {"method": "GET", "endpoint": "/ops/brain/visualizer/state"},
            "inspect_replay": {"method": "GET", "endpoint": "/ops/brain/visualizer/replay"},
            "record_visualops_proof": {"method": "POST", "endpoint": "/ops/brain/canon/answers/current_activity/events"},
        },
        "evidence_refs": [
            "/ops/brain/visualizer/state",
            "/ops/brain/visualizer/replay",
            "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md#multimodal-computer-use",
        ],
    }


def input_ingestion_scorecard(
    realization: dict[str, Any],
    *,
    operations_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("input-ingestion")) or {}
    operations = operations_summary or {}
    latest_command = operations.get("latest_command") or {}
    active_command_id = ((realization.get("live_bindings") or {}).get("active_command_id")) or latest_command.get("command_id")
    lanes = [
        _input_lane("user-commands", "Operator commands become NexusBrain commands with priority, surface, context, and correlation id.", "live-bound" if active_command_id else "static-canon"),
        _input_lane("uploaded-files", "Uploaded files require provenance, unsafe-artifact checks, source permissions, and memory routing.", "static-canon"),
        _input_lane("project-notes", "Project notes enter as source-bound memory candidates with freshness and contradiction checks.", "mapped"),
        _input_lane("code-snippets", "Code snippets are treated as executable-risk inputs until sandbox and policy context is known.", "mapped"),
        _input_lane("meeting-transcripts", "Transcripts require speaker/time metadata, redaction, and source-to-claim extraction.", "research-candidate"),
        _input_lane("external-apis", "External API inputs are governed through protocol trust, consent, and revocation.", "mapped"),
        _input_lane("webhooks-events", "Webhook and event inputs must carry identity, timestamp, source, and replay metadata.", "mapped"),
        _input_lane("realtime-streams", "Real-time streams stay degraded or shadow-only until freshness, rate, and privacy gates pass.", "research-candidate"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "input-ingestion",
        "surface_state": surface.get("state") or "missing",
        "authority": "NexusBrain",
        "session_id": realization.get("session_id") or operations.get("session_id"),
        "active_command_id": active_command_id,
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["input-ingestion"],
        "input_lanes": lanes,
        "intake_rule": "inputs-enter-only-through-source-permission-freshness-redaction-and-command-correlation",
        "freshness_model": {
            "command_correlation": active_command_id,
            "freshness_policy": "stale-or-unknown-source-state-must-be-labeled-before-routing",
            "permission_policy": "private-or-external-inputs-require-consent-and-source-permission-before-memory-or-tool-use",
            "redaction_policy": "operator-private-inputs-are-redacted-before-export-or-protocol-egress",
        },
        "operator_actions": {
            "inspect_operations": {"method": "GET", "endpoint": "/ops/brain/operations"},
            "inspect_memory": {"method": "GET", "endpoint": "/ops/brain/canon/memory-provenance"},
            "inspect_communication": {"method": "GET", "endpoint": "/ops/brain/canon/communication-integration"},
            "inspect_permissions": {"method": "GET", "endpoint": "/ops/brain/security/permissions"},
            "ingest_retrieval": {"method": "POST", "endpoint": "/retrieval/ingest"},
            "record_input_proof": {"method": "POST", "endpoint": "/ops/brain/canon/answers/current_activity/events"},
        },
        "evidence_refs": [
            "/ops/brain/operations",
            "/retrieval/ingest",
            "/ops/brain/canon/memory-provenance",
            "/ops/brain/canon/communication-integration",
            "/ops/brain/security/permissions",
        ],
    }


def live_flow_scorecard(
    realization: dict[str, Any],
    *,
    operations_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("live-flow-trace")) or {}
    operations = operations_summary or {}
    live_bindings = realization.get("live_bindings") or {}
    latest_command = operations.get("latest_command") or {}
    active_command_id = live_bindings.get("active_command_id") or latest_command.get("command_id")
    questions = {
        question_id: answer_operator_question(realization, question_id) or {}
        for question_id in [
            "current_activity",
            "route_provenance",
            "policy_decision",
            "runtime_path",
            "memory_support",
            "artifact_model",
            "eval_evidence",
        ]
    }
    trace_segments = [
        _flow_segment(
            "command",
            "NexusBrain command intake",
            "live-bound" if active_command_id else surface.get("state") or "static-canon",
            ["/ops/brain/operations", "/ops/brain/visualizer/state"],
            latest_command.get("command_text") or questions["current_activity"].get("answer"),
        ),
        _flow_segment("brain-route", "Brain, AO, expert, tool, and memory route", questions["route_provenance"].get("answer_state"), questions["route_provenance"].get("evidence_refs"), questions["route_provenance"].get("answer")),
        _flow_segment("model", "Model, expert, and artifact route", questions["artifact_model"].get("answer_state"), questions["artifact_model"].get("evidence_refs"), questions["artifact_model"].get("answer")),
        _flow_segment("memory", "Memory source and source-to-claim route", questions["memory_support"].get("answer_state"), questions["memory_support"].get("evidence_refs"), questions["memory_support"].get("answer")),
        _flow_segment("tools", "Tool execution and replay route", ((realization.get("surfaces") or {}).get("tools-execution") or {}).get("state"), ["/ops/brain/canon/tool-execution", "/ops/brain/extensions", "/ops/brain/visualizer/replay"], "Tool route must remain policy-gated, sandboxed, isolated, and replayable."),
        _flow_segment("policy", "Policy allow/deny decision and redaction route", questions["policy_decision"].get("answer_state"), questions["policy_decision"].get("evidence_refs"), questions["policy_decision"].get("answer")),
        _flow_segment("eval", "Eval evidence and promotion blocker route", questions["eval_evidence"].get("answer_state"), questions["eval_evidence"].get("evidence_refs"), questions["eval_evidence"].get("answer")),
        _flow_segment("output", "Output artifact and operator-visible proof route", "live-bound" if active_command_id else surface.get("state") or "static-canon", ["/ops/brain/canon/blackbox", "/ops/brain/canon/completion"], "Output proof is exported through the black-box recorder and canon completion matrix."),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "live-flow-trace",
        "surface_state": surface.get("state") or "missing",
        "active_command_id": active_command_id,
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["live-flow-trace"],
        "correlation_model": {
            "correlation_id": active_command_id,
            "authority": "NexusBrain",
            "trace_rule": "route-model-memory-tool-policy-eval-output-must-share-command-correlation",
            "redaction_state": "redacted-operator-safe",
        },
        "trace_segments": trace_segments,
        "operator_actions": {
            "inspect_operations": {"method": "GET", "endpoint": "/ops/brain/operations"},
            "inspect_visualizer": {"method": "GET", "endpoint": "/ops/brain/visualizer/state"},
            "inspect_blackbox": {"method": "GET", "endpoint": "/ops/brain/canon/blackbox"},
            "record_policy_proof": {"method": "POST", "endpoint": "/ops/brain/canon/answers/policy_decision/events"},
        },
        "evidence_refs": [
            "/ops/brain/operations",
            "/ops/brain/visualizer/state",
            "/ops/brain/canon/blackbox",
            "/ops/brain/canon/answers/route_provenance",
        ],
    }


def neural_core_scorecard(
    realization: dict[str, Any],
    *,
    operations_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("neural-core")) or {}
    operations = operations_summary or {}
    live_bindings = realization.get("live_bindings") or {}
    latest_command = operations.get("latest_command") or {}
    active_command_id = live_bindings.get("active_command_id") or latest_command.get("command_id")
    units = [
        _orchestrator_unit("intent-router", "Routes operator intent into NexusBrain command state.", "live-bound" if active_command_id else surface.get("state")),
        _orchestrator_unit("context-retriever", "Retrieves memory, source maps, and current session context.", ((realization.get("surfaces") or {}).get("context-memory") or {}).get("state")),
        _orchestrator_unit("planning-engine", "Plans task decomposition under NexusBrain authority.", surface.get("state")),
        _orchestrator_unit("reasoning-engine", "Runs reasoning and expert arbitration inside the brain envelope.", surface.get("state")),
        _orchestrator_unit("task-decomposer", "Splits work for AOs, experts, tools, and outputs.", ((realization.get("surfaces") or {}).get("tools-execution") or {}).get("state")),
        _orchestrator_unit("decision-manager", "Records policy decisions, gates, and fallback state.", ((realization.get("surfaces") or {}).get("governance-observability") or {}).get("state")),
        _orchestrator_unit("goal-manager", "Maintains mission state, update candidates, and promotion boundaries.", ((realization.get("surfaces") or {}).get("dreaming-evolution") or {}).get("state")),
        _orchestrator_unit("memory-controller", "Controls memory writes, source-to-claim maps, and consolidation.", ((realization.get("surfaces") or {}).get("context-memory") or {}).get("state")),
        _orchestrator_unit("learning-controller", "Keeps learning and autonomous updates shadow-gated until promotion evidence passes.", ((realization.get("surfaces") or {}).get("dreaming-evolution") or {}).get("state")),
        _orchestrator_unit("self-check", "Requires eval, critique, and black-box proof before operator claims are treated as complete.", ((realization.get("surfaces") or {}).get("eval-center") or {}).get("state")),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "neural-core",
        "surface_state": surface.get("state") or "missing",
        "authority": "NexusBrain",
        "active_command_id": active_command_id,
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["neural-core"],
        "orchestrator_units": units,
        "fallback_model": {
            "fallback_rule": "degrade-to-safe-static-canon-or-shadow-state-before-bypassing-nexusbrain",
            "lock_state": "locked-to-nexusbrain",
            "no_bypass_rule": "adapters-tools-protocols-and-update-loops-remain-subordinate-to-nexusbrain",
        },
        "operator_actions": {
            "inspect_core": {"method": "GET", "endpoint": "/ops/brain/core"},
            "inspect_live_flow": {"method": "GET", "endpoint": "/ops/brain/canon/live-flow"},
            "inspect_ao_hive": {"method": "GET", "endpoint": "/ops/brain/canon/ao-hive"},
            "inspect_policy": {"method": "GET", "endpoint": "/ops/brain/canon/observability"},
            "inspect_blackbox": {"method": "GET", "endpoint": "/ops/brain/canon/blackbox"},
        },
        "evidence_refs": [
            "/ops/brain/core",
            "/ops/brain/canon/live-flow",
            "/ops/brain/canon/ao-hive",
            "/ops/brain/canon/blackbox",
        ],
    }


def tool_execution_scorecard(realization: dict[str, Any]) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("tools-execution")) or {}
    lanes = [
        _execution_lane("tool-registry", "Registered tools, extensions, recipes, and execution surfaces.", "mapped"),
        _execution_lane("sandbox-policy", "Execution must declare sandbox, approval, and isolation posture before use.", "mapped"),
        _execution_lane("approval-chain", "Risky tools require explicit policy and operator approval paths.", "live-bound"),
        _execution_lane("failure-replay", "Failures must leave replayable trace, actor, command, and rollback evidence.", "mapped"),
        _execution_lane("runtime-isolation", "Tool/runtime lanes must not bypass NexusBrain authority or protocol trust.", "mapped"),
        _execution_lane("extension-permissions", "Extensions carry permissions, trust state, and certification posture.", "live-bound"),
        _execution_lane("recipe-runbooks", "Reusable execution recipes are inspected through bounded runbooks and history.", "live-bound"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "tools-execution",
        "surface_state": surface.get("state") or "missing",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["tools-execution"],
        "execution_lanes": lanes,
        "safe_execution_rule": "tools-execute-only-through-nexusbrain-policy-approval-sandbox-and-replay",
        "operator_actions": {
            "inspect_tools": {"method": "GET", "endpoint": "/ops/brain/extensions"},
            "inspect_gateway": {"method": "GET", "endpoint": "/ops/brain/gateway"},
            "inspect_recipes": {"method": "GET", "endpoint": "/ops/brain/recipes"},
            "inspect_policy_sets": {"method": "GET", "endpoint": "/ops/brain/extensions/policy-sets"},
            "inspect_replay": {"method": "GET", "endpoint": "/ops/brain/visualizer/replay"},
            "record_execution_status": {"method": "POST", "endpoint": "/ops/brain/operations/commands/{command_id}/events"},
        },
        "evidence_refs": [
            "/ops/brain/extensions",
            "/ops/brain/gateway",
            "/ops/brain/recipes",
            "/ops/brain/extensions/policy-sets",
            "/ops/brain/visualizer/replay",
        ],
    }


def output_delivery_scorecard(realization: dict[str, Any]) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("outputs-deliverables")) or {}
    live_bindings = realization.get("live_bindings") or {}
    active_command_id = live_bindings.get("active_command_id")
    lanes = [
        _delivery_lane("architecture-diagrams", "Architecture diagrams must reflect the current NexusBrain control plane and source refs.", "mapped"),
        _delivery_lane("implementation-plans", "Plans require owner, scope, gate, rollback, and proof references before execution.", "mapped"),
        _delivery_lane("source-code", "Generated source code must be tied to command, test, policy, and artifact-trust evidence.", "live-bound" if active_command_id else "mapped"),
        _delivery_lane("documentation", "Docs carry source-to-claim and research freshness boundaries.", "mapped"),
        _delivery_lane("roadmaps", "Roadmaps separate locked canon, research candidates, shadow-only items, and demotions.", "mapped"),
        _delivery_lane("reports-analytics", "Reports and analytics expose method, inputs, metrics, and replay references.", "static-canon"),
        _delivery_lane("working-artifacts", "Working artifacts require provenance, scanner posture, and operator-visible validation.", "mapped"),
        _delivery_lane("exports-packages", "Exports and packages must pass artifact trust, privacy redaction, and rollback proof.", "mapped"),
        _delivery_lane("memory-feedback", "Delivered outputs feed memory only through source-backed consolidation and privacy controls.", "mapped"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "outputs-deliverables",
        "surface_state": surface.get("state") or "missing",
        "authority": "NexusBrain",
        "active_command_id": active_command_id,
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["outputs-deliverables"],
        "delivery_lanes": lanes,
        "delivery_rule": "outputs-ship-only-with-source-evidence-artifact-trust-memory-feedback-and-replayable-proof",
        "operator_actions": {
            "inspect_artifacts": {"method": "GET", "endpoint": "/ops/brain/canon/artifact-trust"},
            "inspect_blackbox": {"method": "GET", "endpoint": "/ops/brain/canon/blackbox"},
            "inspect_completion": {"method": "GET", "endpoint": "/ops/brain/canon/completion"},
            "inspect_memory": {"method": "GET", "endpoint": "/ops/brain/canon/memory-provenance"},
            "record_output_proof": {"method": "POST", "endpoint": "/ops/brain/canon/answers/current_activity/events"},
        },
        "evidence_refs": [
            "/ops/brain/canon/artifact-trust",
            "/ops/brain/canon/blackbox",
            "/ops/brain/canon/completion",
            "/ops/brain/canon/memory-provenance",
            "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md#outputs-and-deliverables",
        ],
    }


def observability_scorecard(realization: dict[str, Any]) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("governance-observability")) or {}
    trace_standards = [
        _canon_lane("OpenTelemetry-GenAI", "Map LLM, tool, prompt, response, token, and agent events to GenAI telemetry fields.", "mapped"),
        _canon_lane("OpenInference", "Keep an interoperability lane for tracing prompts, tools, retrieval, and model calls.", "research-candidate"),
        _canon_lane("NexusNet-command-timeline", "Bind NexusBrain commands, AO signals, expert work, policy decisions, and proof events.", "live-bound"),
        _canon_lane("audit-redaction-export", "Export only redacted audit frames with evidence references and no raw private inputs.", "mapped"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "governance-observability",
        "surface_state": surface.get("state") or "missing",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["governance-observability"],
        "trace_standards": trace_standards,
        "audit_model": {
            "authority": "NexusBrain",
            "event_contract": [
                "command_id",
                "surface_id",
                "actor",
                "policy_id",
                "decision_state",
                "allowed_denied_reason",
                "evidence_refs",
                "redaction_state",
            ],
            "redaction_rule": "redact-private-inputs-before-export",
            "retention_rule": "retain-redacted-proof-frames-and-evidence-refs",
            "export_format": "canonical-json-audit-frame",
        },
        "operator_actions": {
            "inspect_permissions": {"method": "GET", "endpoint": "/ops/brain/security/permissions"},
            "inspect_guardrails": {"method": "GET", "endpoint": "/ops/brain/security/guardrails"},
            "record_policy_proof": {"method": "POST", "endpoint": "/ops/brain/canon/answers/policy_decision/events"},
            "export_audit": {"method": "GET", "endpoint": "/ops/brain/canon/blackbox"},
        },
        "evidence_refs": [
            "/ops/brain/security/permissions",
            "/ops/brain/security/guardrails",
            "/ops/brain/operations",
            "/ops/brain/canon/answers/policy_decision",
            "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md#agent-observability-standards",
        ],
    }


def security_governance_scorecard(realization: dict[str, Any]) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("governance-observability")) or {}
    lanes = [
        _security_lane("security-rules", "Security rules must be explicit, versioned, and bound to NexusBrain decisions.", "mapped"),
        _security_lane("permissions", "Tool, extension, protocol, memory, and runtime permissions are inspectable before execution.", "live-bound"),
        _security_lane("sandbox", "Execution context must report sandbox and isolation posture.", "live-bound"),
        _security_lane("guardrails", "Persistent guardrails shape allowed actions and escalation behavior.", "live-bound"),
        _security_lane("audit-trail", "Security-sensitive actions must write audit events and redacted export frames.", "mapped"),
        _security_lane("compliance", "Policy, consent, license, and artifact trust states remain visible to operators.", "mapped"),
        _security_lane("privacy-controls", "Private inputs, memory, and trace exports require redaction and consent gates.", "mapped"),
        _security_lane("rollback-readiness", "Promotions, tool changes, and autonomous updates require rollback evidence.", "mapped"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "governance-observability",
        "surface_state": surface.get("state") or "missing",
        "authority": "NexusBrain",
        "required_controls": [
            "security_rules",
            "permissions",
            "guardrails",
            "audit_trail",
            "compliance",
            "privacy_controls",
            "rollback_policy",
        ],
        "security_lanes": lanes,
        "security_rule": "no-security-sensitive-action-without-policy-permission-audit-redaction-and-rollback",
        "operator_actions": {
            "inspect_permissions": {"method": "GET", "endpoint": "/ops/brain/security/permissions"},
            "inspect_sandbox": {"method": "GET", "endpoint": "/ops/brain/security/sandbox"},
            "inspect_guardrails": {"method": "GET", "endpoint": "/ops/brain/security/guardrails"},
            "inspect_audit": {"method": "GET", "endpoint": "/ops/audit"},
            "record_approval": {"method": "POST", "endpoint": "/ops/approvals"},
            "inspect_blackbox": {"method": "GET", "endpoint": "/ops/brain/canon/blackbox"},
        },
        "evidence_refs": [
            "/ops/brain/security/permissions",
            "/ops/brain/security/sandbox",
            "/ops/brain/security/guardrails",
            "/ops/audit",
            "/ops/approvals",
        ],
    }


def blackbox_recorder(realization: dict[str, Any]) -> dict[str, Any]:
    live_bindings = realization.get("live_bindings") or {}
    questions = {
        question_id: answer_operator_question(realization, question_id) or {}
        for question_id in [
            "current_activity",
            "route_provenance",
            "policy_decision",
            "runtime_path",
            "memory_support",
            "artifact_model",
            "eval_evidence",
            "trusted_protocol",
            "update_candidate",
            "research_watch",
        ]
    }
    frames = [
        _recorder_frame("command", "Active NexusBrain command", questions["current_activity"]),
        {
            "frame_id": "input-ingestion",
            "label": "Commands, files, notes, snippets, transcripts, APIs, events, streams, permissions, and freshness",
            "state": "live-bound" if live_bindings.get("active_command_id") else ((realization.get("surfaces") or {}).get("input-ingestion") or {}).get("state") or "static-canon",
            "answer": "Inputs enter NexusNet only through source permission, freshness, redaction, and command-correlation gates before routing into memory, tools, protocols, or outputs.",
            "surface_id": "input-ingestion",
            "evidence_refs": [
                "/ops/brain/canon/input-ingestion",
                "/ops/brain/operations",
                "/retrieval/ingest",
                "/ops/brain/canon/memory-provenance",
            ],
            "compliance_controls": SURFACE_COMPLIANCE_CONTROLS["input-ingestion"],
        },
        _recorder_frame("route", "Brain, AO, expert, tool, and memory route", questions["route_provenance"]),
        {
            "frame_id": "live-flow",
            "label": "Route, model, memory, tool, policy, eval, and output correlation",
            "state": "live-bound" if live_bindings.get("active_command_id") else ((realization.get("surfaces") or {}).get("live-flow-trace") or {}).get("state") or "static-canon",
            "answer": "Live flow correlation uses the NexusBrain command id to bind route, model, memory, tool, policy, eval, and output proof.",
            "surface_id": "live-flow-trace",
            "evidence_refs": [
                "/ops/brain/canon/live-flow",
                "/ops/brain/operations",
                "/ops/brain/visualizer/state",
            ],
            "compliance_controls": SURFACE_COMPLIANCE_CONTROLS["live-flow-trace"],
        },
        {
            "frame_id": "neural-core",
            "label": "NexusBrain orchestrator authority, routing, policy, fallback, learning, and self-check",
            "state": "live-bound" if live_bindings.get("active_command_id") else ((realization.get("surfaces") or {}).get("neural-core") or {}).get("state") or "static-canon",
            "answer": "The neural core remains the central authority; every adapter, AO, expert, tool, memory path, and update loop stays subordinate to NexusBrain.",
            "surface_id": "neural-core",
            "evidence_refs": [
                "/ops/brain/canon/neural-core",
                "/ops/brain/core",
                "/ops/brain/canon/live-flow",
            ],
            "compliance_controls": SURFACE_COMPLIANCE_CONTROLS["neural-core"],
        },
        {
            "frame_id": "security-governance",
            "label": "Security rules, permissions, guardrails, audit, privacy, compliance, and rollback posture",
            "state": ((realization.get("surfaces") or {}).get("governance-observability") or {}).get("state") or "static-canon",
            "answer": "Security-sensitive actions require policy, permissions, guardrails, audit, privacy redaction, compliance evidence, and rollback posture.",
            "surface_id": "governance-observability",
            "evidence_refs": [
                "/ops/brain/canon/security-governance",
                "/ops/brain/security/permissions",
                "/ops/brain/security/guardrails",
                "/ops/audit",
            ],
            "compliance_controls": [
                "security_rules",
                "permissions",
                "guardrails",
                "audit_trail",
                "compliance",
                "privacy_controls",
                "rollback_policy",
            ],
        },
        {
            "frame_id": "communication-integration",
            "label": "Webhooks, buses, events, external services, notifications, and collaboration channels",
            "state": ((realization.get("surfaces") or {}).get("communication-integration") or {}).get("state") or "static-canon",
            "answer": "Communication channels are governed as adapters: identity, consent, permission, trust envelope, revocation, and audit stay visible before external exchange.",
            "surface_id": "communication-integration",
            "evidence_refs": [
                "/ops/brain/canon/communication-integration",
                "/ops/brain/canon/protocol-trust",
                "/ops/brain/gateway",
                "/ops/brain/extensions",
            ],
            "compliance_controls": SURFACE_COMPLIANCE_CONTROLS["communication-integration"],
        },
        {
            "frame_id": "self-improvement-layer",
            "label": "Experience capture, triage, provenance, queue, review, and regression gates",
            "state": ((realization.get("surfaces") or {}).get("self-improvement-layer") or {}).get("state") or "static-canon",
            "answer": "Self-improvement candidates are captured and queued, but behavior cannot change without review, external verification, regression gates, and rollback readiness.",
            "surface_id": "self-improvement-layer",
            "evidence_refs": [
                "/ops/brain/canon/self-improvement",
                "/ops/brain/self-improvement/queue",
                "docs/SELF_IMPROVEMENT_LAYER.md",
            ],
            "compliance_controls": SURFACE_COMPLIANCE_CONTROLS["self-improvement-layer"],
        },
        {
            "frame_id": "dataset-radar",
            "label": "Dataset discovery, license gates, refresh runs, and curriculum lineage",
            "state": "live-bound",
            "answer": "Dataset Radar refreshes are persisted as candidate-only replay artifacts; teacher councils and DatasetForge must consume the gated source lineage instead of raw discoveries.",
            "surface_id": "dataset-radar",
            "evidence_refs": [
                "/ops/brain/canon/dataset-radar",
                "/ops/brain/dataset-radar",
                "/ops/brain/dataset-radar/refresh-runs",
                "/ops/brain/dataset-radar/refresh-batches",
                "/ops/brain/dataset-radar/material-requests",
                "/ops/brain/dataset-radar/candidate-reviews",
                "/ops/brain/dataset-radar/gate-preview",
                "/ops/brain/dataset-radar/sources",
                "/ops/brain/dataset-radar/sources/{dataset_id}",
            ],
            "replay_refs": [
                "/ops/brain/dataset-radar/refresh-runs/{refresh_run_id}",
                "/ops/brain/dataset-radar/refresh-batches/{batch_id}",
                "/ops/brain/dataset-radar/material-requests/{material_request_id}",
                "/ops/brain/dataset-radar/candidate-reviews/{candidate_review_id}",
                "/ops/brain/dataset-radar/sources/{dataset_id}",
            ],
            "compliance_controls": [
                "license_state",
                "provenance_state",
                "privacy_risk",
                "candidate_only_discovery",
                "refresh_run_replay",
                "refresh_batch_replay",
                "material_request_replay",
                "candidate_review_replay",
                "source_detail_replay",
                "candidate_gate_preview",
                "sealed_eval_visibility",
            ],
        },
        {
            "frame_id": "dataset-forge",
            "label": "Dataset manifest forging, split isolation, material lineage, and sealed eval boundaries",
            "state": "live-bound",
            "answer": "DatasetForge converts approved Dataset Radar material requests into replayable manifests with train, validation, heldout, adversarial, and sealed teacher-free eval separation.",
            "surface_id": "dataset-forge",
            "evidence_refs": [
                "/ops/brain/canon/dataset-forge",
                "/ops/brain/dataset-forge",
                "/ops/brain/dataset-forge/manifests",
                "/ops/brain/dataset-radar/material-requests",
            ],
            "replay_refs": [
                "/ops/brain/dataset-forge",
                "/ops/brain/canon/dataset-forge",
                "/ops/brain/dataset-radar/material-requests/{material_request_id}",
            ],
            "compliance_controls": [
                "privacy_license_filters",
                "dataset_radar_gate",
                "dataset_radar_material_request_gate",
                "split_isolation",
                "sealed_teacher_free_eval_split",
                "manifest_replay",
            ],
        },
        {
            "frame_id": "knowledge-artifacts",
            "label": "Compiled knowledge artifacts, citations, freshness, conflicts, and raw retrieval fallback",
            "state": "live-bound",
            "answer": "Knowledge Artifact Compiler turns approved source material into typed, cited, versioned task artifacts while preserving raw retrieval as a fallback lane.",
            "surface_id": "context-memory",
            "evidence_refs": [
                "/ops/brain/canon/knowledge-artifacts",
                "/ops/brain/knowledge-artifacts",
                "/ops/brain/knowledge-artifacts/compile",
                "/ops/brain/knowledge-artifacts/query",
                "/ops/brain/knowledge-artifacts/query-events",
                "/ops/brain/knowledge-artifacts/freshness",
            ],
            "replay_refs": [
                "/ops/brain/knowledge-artifacts/{artifact_id}",
                "/ops/brain/canon/knowledge-artifacts",
                "/ops/brain/artifact-trust/knowledge-artifacts/scan",
            ],
            "compliance_controls": [
                "field_level_citations",
                "source_digests",
                "freshness_invalidation",
                "rbac_privacy_filter",
                "conflict_objects",
                "raw_retrieval_fallback",
                "raw_retrieval_recall_only_boundary",
                "query_mutation_boundary",
                "source_ref_security_gate",
                "blocked_source_ref_replay",
                "artifact_trust_preview",
                "artifact_trust_scan",
                "downstream_krc_runtime_gate_coverage",
                "candidate_ledger_gate",
            ],
        },
        {
            "frame_id": "growth-engine",
            "label": "Shadow student birth, model genome, eval gauntlet, and teacher ejection boundary",
            "state": "live-bound",
            "answer": "Hive Model Growth Engine births temporary shadow students from gated datasets, writes model genomes, blocks weight mutation in dry-run mode, and keeps teacher ejection locked behind reviewer consistency windows.",
            "surface_id": "growth-engine",
            "evidence_refs": [
                "/ops/brain/canon/growth-engine",
                "/ops/brain/growth-engine",
                "/ops/brain/growth-engine/cycles",
                "/ops/brain/canon/dataset-forge",
                "/ops/brain/canon/dataset-radar",
            ],
            "replay_refs": [
                "/ops/brain/growth-engine/cycles/{cycle_id}",
                "/ops/brain/canon/growth-engine",
                "/ops/brain/canon/dataset-forge",
            ],
            "compliance_controls": [
                "growth_cycle",
                "model_genome",
                "shadow_student_only",
                "sandbox_eval_gate",
                "teacher_surpass_review",
                "teacher_ejection_block",
                "dataset_radar_source_review_gate",
                "hidden_eval_attestation_gate",
                "sealed_eval_teacher_visibility_gate",
                "actual_weight_mutation_block",
                "actual_weight_mutation_blocked_until",
                "training_prerequisite_blockers",
                "teacher_council_evidence_replay",
                "dataset_split_replay",
                "dataset_radar_lineage_replay",
                "student_birth_record_replay",
                "model_genome_replay",
                "training_loss_trace_replay",
                "training_checkpoint_replay",
                "training_output_artifact_replay",
                "eval_scorecard_replay",
                "eval_comparison_matrix_replay",
                "eval_case_results_replay",
                "rollback_snapshot",
            ],
        },
        _recorder_frame("policy", "Policy allow, deny, redaction, and audit decision", questions["policy_decision"]),
        _recorder_frame("runtime", "Runtime, quantization, backend, and cache path", questions["runtime_path"]),
        _recorder_frame("memory", "Memory source, source-to-claim map, and stale-memory status", questions["memory_support"]),
        _recorder_frame("artifact", "Model, tool, artifact, scanner, and license posture", questions["artifact_model"]),
        _recorder_frame("eval", "Held-out eval, regression gate, and promotion blocker evidence", questions["eval_evidence"]),
        _recorder_frame("protocol", "Protocol identity, permission, trust envelope, and revocation state", questions["trusted_protocol"]),
        _recorder_frame("evolution", "Autonomous update candidate, shadow run, rollback, and approval state", questions["update_candidate"]),
        _recorder_frame("research", "Forward radar watch item and promotion boundary", questions["research_watch"]),
        {
            "frame_id": "hive-consensus",
            "label": "Central command, AO consensus, expert evidence, veto, and memory feedback",
            "state": "live-bound" if live_bindings.get("active_command_id") else "static-canon",
            "answer": "The commanded collective hive is governed through NexusBrain orders, AO local reasoning, expert evidence, veto escalation, and memory feedback.",
            "surface_id": "ao-hive",
            "evidence_refs": [
                "/ops/brain/canon/hive-consensus",
                "/ops/brain/operations",
                "/ops/brain/visualizer/state",
            ],
            "compliance_controls": [
                "receives_orders",
                "local_reasoning",
                "evidence_response",
                "veto_escalation",
                "consensus_contribution",
                "execution_status",
            ],
        },
        {
            "frame_id": "ao-hive",
            "label": "AO roles, delegation, context scopes, permissions, and governance constraints",
            "state": ((realization.get("surfaces") or {}).get("ao-hive") or {}).get("state") or "static-canon",
            "answer": "AOs are department-level mini-brains that receive NexusBrain orders and return evidence, vetoes, and execution status.",
            "surface_id": "ao-hive",
            "evidence_refs": [
                "/ops/brain/canon/ao-hive",
                "/ops/brain/aos",
                "/ops/brain/operations",
            ],
            "compliance_controls": SURFACE_COMPLIANCE_CONTROLS["ao-hive"],
        },
        {
            "frame_id": "experts-hive",
            "label": "Domain expert mini-brains, evidence response, consensus, veto, and memory feedback",
            "state": ((realization.get("surfaces") or {}).get("experts-hive") or {}).get("state") or "static-canon",
            "answer": "Experts are domain-specialized mini NexusNet brains that reason locally, return evidence and constraints, and remain governed by NexusBrain authority.",
            "surface_id": "experts-hive",
            "evidence_refs": [
                "/ops/brain/canon/experts-hive",
                "/ops/brain/core",
                "/ops/brain/operations",
                "/ops/brain/canon/hive-consensus",
            ],
            "compliance_controls": SURFACE_COMPLIANCE_CONTROLS["experts-hive"],
        },
        {
            "frame_id": "tool-execution",
            "label": "Tool registry, sandbox, approval, runtime isolation, failure, and replay proof",
            "state": ((realization.get("surfaces") or {}).get("tools-execution") or {}).get("state") or "static-canon",
            "answer": "Tools are valid only when routed through NexusBrain policy, approval, sandbox, isolation, and replay controls.",
            "surface_id": "tools-execution",
            "evidence_refs": [
                "/ops/brain/canon/tool-execution",
                "/ops/brain/extensions",
                "/ops/brain/gateway",
                "/ops/brain/visualizer/replay",
            ],
            "compliance_controls": SURFACE_COMPLIANCE_CONTROLS["tools-execution"],
        },
        {
            "frame_id": "output-delivery",
            "label": "Deliverables, working artifacts, exports, packages, reports, and memory feedback",
            "state": ((realization.get("surfaces") or {}).get("outputs-deliverables") or {}).get("state") or "static-canon",
            "answer": "Outputs ship only when they carry source evidence, artifact trust, memory feedback posture, redaction, and replayable proof.",
            "surface_id": "outputs-deliverables",
            "evidence_refs": [
                "/ops/brain/canon/output-delivery",
                "/ops/brain/canon/artifact-trust",
                "/ops/brain/canon/blackbox",
                "/ops/brain/canon/completion",
            ],
            "compliance_controls": SURFACE_COMPLIANCE_CONTROLS["outputs-deliverables"],
        },
        {
            "frame_id": "operator-proof",
            "label": "Operator-facing proof bundle",
            "state": "live-bound" if live_bindings.get("active_command_id") else "static-canon",
            "answer": "Control Panel binds all cockpit scorecards to NexusBrain state and redacted evidence references.",
            "surface_id": "overview",
            "evidence_refs": [
                "/ops/brain/canon/realization",
                "/ops/brain/canon/completion",
                "/ops/brain/visualizer/state",
                "/ops/brain/canon/observability",
            ],
            "compliance_controls": [
                "current_activity",
                "operator_trace",
                "audit_event",
                "redaction_state",
            ],
        },
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "recorder_id": "nexusnet-blackbox-recorder",
        "authority": live_bindings.get("command_authority") or "NexusBrain",
        "session_id": realization.get("session_id"),
        "active_command_id": live_bindings.get("active_command_id"),
        "frames": frames,
        "scorecard_refs": {
            "input_ingestion": "/ops/brain/canon/input-ingestion",
            "live_flow": "/ops/brain/canon/live-flow",
            "neural_core": "/ops/brain/canon/neural-core",
            "security_governance": "/ops/brain/canon/security-governance",
            "policy_kernel": "/ops/brain/canon/policy-kernel",
            "agentic_pipelines": "/ops/brain/canon/agentic-pipelines",
            "agent_opportunities": "/ops/brain/canon/agent-opportunities",
            "harness_providers": "/ops/brain/canon/harness-providers",
            "harness_routing": "/ops/brain/canon/harness-routing",
            "harness_improvement_ledger": "/ops/brain/canon/harness-ledger",
            "edge_workload_router": "/ops/brain/canon/edge-workload-router",
            "multimodal_computer_use": "/ops/brain/canon/multimodal-computer-use",
            "inference_economy_router": "/ops/brain/canon/inference-economy-router",
            "inference_architecture": "/ops/brain/canon/inference-architecture",
            "cache_ledger": "/ops/brain/canon/cache-ledger",
            "runtime_workload_scorecards": "/ops/brain/canon/runtime-scorecards",
            "quantization_catalog": "/ops/brain/canon/quantization-catalog",
            "protocol_trust_registry": "/ops/brain/canon/protocol-trust-registry",
            "browser_context": "/ops/brain/canon/browser-context",
            "dataset_radar": "/ops/brain/canon/dataset-radar",
            "dataset_forge": "/ops/brain/canon/dataset-forge",
            "knowledge_artifacts": "/ops/brain/canon/knowledge-artifacts",
            "growth_engine": "/ops/brain/canon/growth-engine",
            "adapter_registry": "/ops/brain/canon/adapter-registry",
            "fine_tune_decision_gate": "/ops/brain/canon/fine-tune-decision-gate",
            "adapter_training": "/ops/brain/canon/adapter-training",
            "eval_registry": "/ops/brain/canon/eval-registry",
            "artifact_trust_registry": "/ops/brain/canon/artifact-trust-registry",
            "autonomous_updates": "/ops/brain/canon/autonomous-updates",
            "genai_observability": "/ops/brain/canon/genai-observability",
            "self_review": "/ops/brain/canon/self-review",
            "forward_radar": "/ops/brain/canon/forward-radar",
            "memory_quality": "/ops/brain/canon/memory-quality",
            "engram_memory": "/ops/brain/canon/engram-memory",
            "communication_integration": "/ops/brain/canon/communication-integration",
            "self_improvement": "/ops/brain/canon/self-improvement",
            "ao_hive": "/ops/brain/canon/ao-hive",
            "experts_hive": "/ops/brain/canon/experts-hive",
            "hive": "/ops/brain/canon/hive-consensus",
            "tool_execution": "/ops/brain/canon/tool-execution",
            "output_delivery": "/ops/brain/canon/output-delivery",
            "runtime": "/ops/brain/canon/runtime-scorecard",
            "evolution": "/ops/brain/canon/evolution-dossier",
            "protocol": "/ops/brain/canon/protocol-trust",
            "eval": "/ops/brain/canon/eval-suite",
            "memory": "/ops/brain/canon/memory-provenance",
            "artifact": "/ops/brain/canon/artifact-trust",
            "hardware": "/ops/brain/canon/hardware-matrix",
            "visualops": "/ops/brain/canon/visualops",
            "observability": "/ops/brain/canon/observability",
        },
        "export_contract": {
            "format": "redacted-canonical-json",
            "standard_mappings": ["OpenTelemetry-GenAI", "OpenInference", "NexusNet-command-timeline"],
            "redaction_rule": "redact-private-inputs-before-export",
            "proof_rule": "every-operator-claim-must-carry-state-evidence-and-promotion-boundary",
        },
    }


def hive_consensus_scorecard(
    realization: dict[str, Any],
    *,
    operations_summary: dict[str, Any] | None = None,
    hive_mind: dict[str, Any] | None = None,
) -> dict[str, Any]:
    operations = operations_summary or {}
    hive = hive_mind or {}
    live_bindings = realization.get("live_bindings") or {}
    latest_command = operations.get("latest_command") or {}
    active_command_id = live_bindings.get("active_command_id") or latest_command.get("command_id")
    central_orchestrator = hive.get("central_orchestrator") or {}
    command_chain = central_orchestrator.get("command_chain") or [
        "NexusBrain",
        "AO Hive",
        "Experts Hive",
        "Tools / Outputs",
        "Memory Feedback",
        "NexusBrain",
    ]
    mini_brain_groups = hive.get("mini_brain_nodes") or [
        {
            "node_id": "ao-hive",
            "role": "AO mini-brain",
            "reports_to": "NexusBrain",
            "state": ((realization.get("surfaces") or {}).get("ao-hive") or {}).get("state") or "static-canon",
            "signals": ["receives_orders", "local_reasoning", "veto_escalation", "consensus_contribution"],
        },
        {
            "node_id": "experts-hive",
            "role": "Expert mini-brain",
            "reports_to": "AO Hive",
            "state": "static-canon",
            "signals": ["receives_orders", "evidence_response", "execution_status", "consensus_contribution"],
        },
        {
            "node_id": "tools-outputs",
            "role": "Execution workforce",
            "reports_to": "Experts Hive",
            "state": ((realization.get("surfaces") or {}).get("tools-execution") or {}).get("state") or "static-canon",
            "signals": ["receives_orders", "execution_status", "evidence_response"],
        },
        {
            "node_id": "memory-feedback",
            "role": "Memory feedback loop",
            "reports_to": "NexusBrain",
            "state": ((realization.get("surfaces") or {}).get("context-memory") or {}).get("state") or "static-canon",
            "signals": ["evidence_response", "consensus_contribution", "execution_status"],
        },
    ]
    event_types = [
        ("command_issued", "NexusBrain issued mission command"),
        ("ao_signal", "AO hive received orders and opened local reasoning"),
        ("expert_signal", "Expert mini-brains prepared evidence response"),
        ("consensus_state", "Consensus and veto window opened"),
        ("veto_escalation", "Security or governance veto/downvote escalated"),
        ("execution_status", "Execution status returned to NexusBrain"),
        ("memory_feedback", "Memory feedback loop updated shared context"),
    ]
    signal_frames = [
        _hive_signal_frame(frame_id, label, _latest_timeline_event(operations, frame_id), active_command_id=active_command_id)
        for frame_id, label in event_types
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "operating_model_id": hive.get("operating_model_id") or "commanded-collective-hive",
        "authority": central_orchestrator.get("authority") or "NexusBrain",
        "session_id": realization.get("session_id") or operations.get("session_id"),
        "active_command_id": active_command_id,
        "command_text": latest_command.get("command_text"),
        "lifecycle_state": latest_command.get("lifecycle_state") or ("issued" if active_command_id else "standby"),
        "command_chain": command_chain,
        "consensus_rules": [
            _consensus_rule("central-command", "NexusBrain sets mission intent, priorities, constraints, and final arbitration."),
            _consensus_rule("local-reasoning", "AO departments and expert mini-brains reason locally under the command envelope."),
            _consensus_rule("evidence-consensus", "Responses must return evidence, uncertainty, and execution constraints before promotion."),
            _consensus_rule("veto-escalation", "Security, governance, or quality vetoes can pause execution until NexusBrain clears the gate."),
            _consensus_rule("memory-feedback", "Approved outcomes feed shared memory, source maps, and future command context."),
        ],
        "mini_brain_groups": mini_brain_groups,
        "signal_contract": operations.get("signal_contract")
        or hive.get("mini_brain_signal_contract")
        or [
            "receives_orders",
            "local_reasoning",
            "evidence_response",
            "veto_escalation",
            "consensus_contribution",
            "execution_status",
        ],
        "signal_frames": signal_frames,
        "operator_actions": {
            "issue_command": {"method": "POST", "endpoint": "/ops/brain/operations/commands"},
            "record_veto": {"method": "POST", "endpoint": f"/ops/brain/operations/commands/{active_command_id or '{command_id}'}/events"},
            "record_policy_proof": {"method": "POST", "endpoint": "/ops/brain/canon/answers/policy_decision/events"},
            "inspect_blackbox": {"method": "GET", "endpoint": "/ops/brain/canon/blackbox"},
        },
        "evidence_refs": [
            "/ops/brain/operations",
            "/ops/brain/visualizer/state",
            "/ops/brain/canon/blackbox",
        ],
    }


def researcher_swarm_scorecard(realization: dict[str, Any]) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("forward-radar")) or {}
    active_research_watch = answer_operator_question(realization, "research_watch") or {}
    research_roles = [
        _research_role("horizon-scout", "Scans open-first models, quantization, protocols, evals, memory, supply chain, edge, and computer-use lanes."),
        _research_role("source-verifier", "Checks primary sources, licenses, recency, and reproducibility before a candidate can move forward."),
        _research_role("benchmarker", "Maps candidates to held-out evals, runtime benchmarks, cache economics, and hardware fit."),
        _research_role("security-reviewer", "Reviews provenance, unsafe serialization, permissions, protocol identity, and trust envelopes."),
        _research_role("integration-planner", "Turns verified research into bounded NexusBrain implementation commands and rollback plans."),
        _research_role("self-reviewer", "Runs critique, contradiction checks, autonomous update gates, and operator approval readiness."),
    ]
    promotion_loop = [
        _promotion_stage("discover", "Find candidates and attach source, license, and use-case metadata.", "research-candidate"),
        _promotion_stage("verify", "Confirm source quality, evidence freshness, implementation status, and artifact trust.", "research-candidate"),
        _promotion_stage("simulate", "Run shadow-only integration, policy, runtime, memory, and UI impact checks.", "shadow-only"),
        _promotion_stage("score", "Attach eval, benchmark, regression, and operator-readiness evidence.", "shadow-only"),
        _promotion_stage("propose", "Queue a bounded NexusBrain command with rollback and proof requirements.", "static-canon"),
        _promotion_stage("operator-approval", "Require explicit human/operator approval before live promotion.", "static-canon"),
        _promotion_stage("promote-or-rollback", "Promote only when gates pass; otherwise retain watchlist or rollback.", "static-canon"),
    ]
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "forward-radar",
        "surface_state": surface.get("state") or "missing",
        "authority": "NexusBrain",
        "active_research_watch": active_research_watch,
        "research_roles": research_roles,
        "promotion_loop": promotion_loop,
        "candidate_registry": realization.get("research_lanes") or [],
        "autonomy_rule": "researchers-can-discover-and-propose-but-not-promote-without-evals-security-rollback-and-operator-approval",
        "operator_actions": {
            "queue_candidate": {"method": "POST", "endpoint": "/ops/brain/canon/realize-next"},
            "record_research_proof": {"method": "POST", "endpoint": "/ops/brain/canon/answers/research_watch/events"},
            "inspect_evals": {"method": "GET", "endpoint": "/ops/brain/canon/eval-suite"},
            "inspect_artifact_trust": {"method": "GET", "endpoint": "/ops/brain/canon/artifact-trust"},
            "inspect_hive": {"method": "GET", "endpoint": "/ops/brain/canon/hive-consensus"},
        },
        "evidence_refs": [
            "docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md",
            "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
            "/ops/brain/canon/answers/research_watch",
            "/ops/brain/canon/realize-next",
        ],
    }


def ao_hive_scorecard(
    realization: dict[str, Any],
    *,
    ao_snapshot: dict[str, Any] | None = None,
    operations_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("ao-hive")) or {}
    operations = operations_summary or {}
    latest_command = operations.get("latest_command") or {}
    active_command_id = ((realization.get("live_bindings") or {}).get("active_command_id")) or latest_command.get("command_id")
    roster = []
    for record in (ao_snapshot or {}).get("active_aos", []) or []:
        roster.append(
            {
                "ao_name": record.get("name") or record.get("ao_name"),
                "description": record.get("description"),
                "risk_tier": record.get("risk_tier") or "medium",
                "status_label": record.get("status_label") or "LOCKED CANON",
                "responsibilities": record.get("responsibilities") or [],
                "reports_to": "NexusBrain",
                "context_scope": _ao_context_scope(record),
                "model_tool_permissions": _ao_permissions(record),
                "governance_constraints": _ao_governance_constraints(record),
                "collaboration_state": "active-route" if _ao_is_selected(record, operations) else "available",
            }
        )
    selected_ao = _selected_ao_name(operations)
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "ao-hive",
        "surface_state": surface.get("state") or "missing",
        "authority": "NexusBrain",
        "session_id": realization.get("session_id") or operations.get("session_id"),
        "active_command_id": active_command_id,
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["ao-hive"],
        "ao_roster": roster,
        "delegation_model": {
            "selected_ao": selected_ao,
            "command_authority": "NexusBrain",
            "delegation_rule": "AOs receive orders, reason locally, return evidence, and escalate vetoes without bypassing NexusBrain.",
            "active_command_text": latest_command.get("command_text"),
        },
        "operator_actions": {
            "inspect_aos": {"method": "GET", "endpoint": "/ops/brain/aos"},
            "issue_command": {"method": "POST", "endpoint": "/ops/brain/operations/commands"},
            "record_ao_signal": {"method": "POST", "endpoint": f"/ops/brain/operations/commands/{active_command_id or '{command_id}'}/events"},
            "inspect_hive_consensus": {"method": "GET", "endpoint": "/ops/brain/canon/hive-consensus"},
            "inspect_blackbox": {"method": "GET", "endpoint": "/ops/brain/canon/blackbox"},
        },
        "evidence_refs": [
            "/ops/brain/aos",
            "/ops/brain/operations",
            "/ops/brain/canon/hive-consensus",
            "/ops/brain/canon/blackbox",
        ],
    }


def experts_hive_scorecard(
    realization: dict[str, Any],
    *,
    operations_summary: dict[str, Any] | None = None,
    expert_topologies: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    surface = ((realization.get("surfaces") or {}).get("experts-hive")) or {}
    operations = operations_summary or {}
    latest_command = operations.get("latest_command") or {}
    active_command_id = ((realization.get("live_bindings") or {}).get("active_command_id")) or latest_command.get("command_id")
    expert_signals = _latest_expert_signals(operations)
    domain_experts = [
        _expert_hive_record(record, operations)
        for record in (expert_topologies or DEFAULT_EXPERT_HIVE_ROSTER)
        if not record.get("auxiliary") and record.get("authoritative_core_roster", True)
    ]
    selected_signal = expert_signals[0] if expert_signals else {}
    return {
        "status_label": "LOCKED CANON",
        "source_document": SOURCE_DOCUMENT,
        "surface_id": "experts-hive",
        "surface_state": surface.get("state") or "missing",
        "authority": "NexusBrain",
        "session_id": realization.get("session_id") or operations.get("session_id"),
        "active_command_id": active_command_id,
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["experts-hive"],
        "domain_experts": domain_experts,
        "expert_signals": expert_signals,
        "mini_brain_model": {
            "topology_rule": "each-expert-is-a-mini-nexusnet-under-nexusbrain-authority",
            "local_reasoning": "domain experts reason locally but cannot promote, execute, or communicate externally outside NexusBrain governance.",
            "shared_memory_rule": "expert outputs feed memory only through source-to-claim, privacy, and consolidation gates.",
            "veto_rule": "domain uncertainty, security risk, or evidence gaps can escalate a veto to NexusBrain or GovernanceAO.",
        },
        "routing_model": {
            "selected_signal_count": len(expert_signals),
            "selected_expert": selected_signal.get("actor") or selected_signal.get("subject"),
            "selected_subject": selected_signal.get("subject"),
            "route_rule": "NexusBrain selects expert capsules, requests evidence, receives constraints, and arbitrates consensus.",
            "active_command_text": latest_command.get("command_text"),
        },
        "operator_actions": {
            "inspect_core": {"method": "GET", "endpoint": "/ops/brain/core"},
            "inspect_operations": {"method": "GET", "endpoint": "/ops/brain/operations"},
            "record_expert_signal": {"method": "POST", "endpoint": f"/ops/brain/operations/commands/{active_command_id or '{command_id}'}/events"},
            "inspect_hive_consensus": {"method": "GET", "endpoint": "/ops/brain/canon/hive-consensus"},
            "inspect_blackbox": {"method": "GET", "endpoint": "/ops/brain/canon/blackbox"},
        },
        "evidence_refs": [
            "/ops/brain/core",
            "/ops/brain/operations",
            "/ops/brain/canon/hive-consensus",
            "/ops/brain/canon/blackbox",
            "nexusnet/visuals/expert_topologies.yaml",
        ],
    }


def answer_operator_question(realization: dict[str, Any], question_id: str) -> dict[str, Any] | None:
    questions = realization.get("operator_questions") or {}
    question = questions.get(question_id)
    if not question:
        return None
    question_surface = question.get("surface_id") or {
        "current_activity": "overview",
        "route_provenance": "live-flow-trace",
        "policy_decision": "governance-observability",
        "eval_evidence": "eval-center",
        "artifact_model": "artifact-trust",
        "runtime_path": "runtime-lab",
        "trusted_protocol": "connections-protocols",
        "memory_support": "context-memory",
        "update_candidate": "dreaming-evolution",
        "research_watch": "forward-radar",
    }.get(question_id, "overview")
    surface = (realization.get("surfaces") or {}).get(question_surface, {})
    active_command_id = ((realization.get("live_bindings") or {}).get("active_command_id"))
    evidence_refs = list(question.get("evidence_refs") or [])
    evidence_ref = question.get("evidence_ref")
    if not evidence_refs and evidence_ref:
        evidence_refs = [evidence_ref]
    return {
        "status_label": "LOCKED CANON",
        "question_id": question_id,
        "prompt": question.get("prompt"),
        "answer_state": question.get("answer_state"),
        "surface_id": question_surface,
        "surface_state": surface.get("state"),
        "active_command_id": active_command_id,
        "answer": question.get("current_answer")
        or _surface_answer(question_id=question_id, surface=surface),
        "evidence_refs": evidence_refs or surface.get("evidence_refs", []),
        "compliance_controls": surface.get("compliance_controls") or [],
        "promotion_gate": surface.get("promotion_gate"),
        "next_action": surface.get("next_action"),
    }


def surface_drilldown(realization: dict[str, Any], surface_id: str) -> dict[str, Any] | None:
    surfaces = realization.get("surfaces") or {}
    surface = surfaces.get(surface_id)
    if not surface:
        return None
    session_id = realization.get("session_id")
    query = f"?session_id={session_id}" if session_id else ""
    answer_links = [
        {
            "question_id": question_id,
            "prompt": question.get("prompt"),
            "href": f"/ops/brain/canon/answers/{question_id}{query}",
            "answer_state": question.get("answer_state"),
        }
        for question_id, question in (realization.get("operator_questions") or {}).items()
        if question.get("surface_id") == surface_id
    ]
    book_gates = [
        gate
        for gate in realization.get("book_gates") or []
        if gate.get("surface_id") == surface_id
    ]
    blocking_item = next(
        (
            item
            for item in realization.get("blocking_items") or []
            if item.get("surface_id") == surface_id
        ),
        None,
    )
    return {
        "status_label": "LOCKED CANON",
        "source_document": realization.get("source_document") or SOURCE_DOCUMENT,
        "session_id": session_id,
        "surface": surface,
        "book_gates": book_gates,
        "answer_links": answer_links,
        "research_lanes": surface.get("research_lanes") or [],
        "evidence_refs": surface.get("evidence_refs") or [],
        "blocking_item": blocking_item,
        "realize_next": {
            "method": "POST",
            "endpoint": "/ops/brain/canon/realize-next",
            "body": {
                "session_id": session_id,
                "surface_id": surface_id,
            },
            "label": "Queue Next Canon Action",
        },
    }


def _completion_gate(
    *,
    gate_id: str,
    label: str,
    state: str,
    metric: str,
    evidence_refs: list[str],
    blockers: list[str],
    surface_id: str | None = None,
) -> dict[str, Any]:
    control_plane_complete = state in {"satisfied", "mapped", "live-bound", "guarded", "research-candidate"}
    return {
        "gate_id": gate_id,
        "label": label,
        "state": state,
        "metric": metric,
        "surface_id": surface_id,
        "evidence_refs": [ref for ref in evidence_refs if ref],
        "blockers": blockers,
        "control_plane_complete": control_plane_complete,
    }


def _surface_completion_gate(
    *,
    gate_id: str,
    label: str,
    surface: dict[str, Any],
    evidence_refs: list[str],
) -> dict[str, Any]:
    surface_state = surface.get("state") or "missing"
    controls = surface.get("compliance_controls") or []
    complete = surface_state != "missing" and bool(controls)
    state = "mapped" if complete else "blocked"
    return _completion_gate(
        gate_id=gate_id,
        label=label,
        state=state,
        metric=f"{len(controls)} controls",
        surface_id=surface.get("surface_id"),
        evidence_refs=[*(surface.get("evidence_refs") or []), *evidence_refs],
        blockers=[] if complete else [f"{surface.get('surface_id') or gate_id} is missing required controls."],
    )


def _runtime_control(
    control_id: str,
    controls: set[str],
    condition: bool,
    *,
    endpoint: str | None = None,
    evidence_refs: list[str] | None = None,
    promotion_gate: str | None = None,
) -> dict[str, Any]:
    mapped = control_id in controls and condition
    return {
        "control_id": control_id,
        "state": "mapped" if mapped else "missing",
        "endpoint": endpoint,
        "evidence_refs": evidence_refs or [],
        "promotion_gate": promotion_gate,
    }


def _evolution_stage(
    stage_id: str,
    label: str,
    actor: str,
    state: str,
    evidence_refs: list[str],
) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "label": label,
        "actor": actor,
        "state": state,
        "evidence_refs": evidence_refs,
    }


def _protocol_record(protocol_id: str, label: str, capabilities: list[str]) -> dict[str, Any]:
    return {
        "protocol_id": protocol_id,
        "label": label,
        "state": "adapter-governed",
        "capabilities": capabilities,
        "authority": "NexusBrain",
        "required_controls": SURFACE_COMPLIANCE_CONTROLS["connections-protocols"],
    }


def _eval_family(eval_id: str, label: str, state: str) -> dict[str, Any]:
    return {
        "eval_id": eval_id,
        "label": label,
        "state": state,
        "promotion_use": "block-or-approve-candidate-promotion",
    }


def _canon_lane(lane_id: str, label: str, state: str) -> dict[str, Any]:
    return {
        "lane_id": lane_id,
        "label": label,
        "state": state,
        "promotion_gate": "registry-license-security-eval-runtime-privacy-governance",
    }


def _supply_chain_control(control_id: str, label: str, state: str) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "label": label,
        "state": state,
        "promotion_gate": "scanner-provenance-license-rollback",
    }


def _deployment_lane(lane_id: str, label: str, state: str) -> dict[str, Any]:
    return {
        "lane_id": lane_id,
        "label": label,
        "state": state,
        "promotion_gate": "hardware-certification-runtime-eval",
    }


def _computer_use_lane(lane_id: str, label: str, state: str) -> dict[str, Any]:
    return {
        "lane_id": lane_id,
        "label": label,
        "state": state,
        "promotion_gate": "policy-human-approval-replay-safety",
    }


def _execution_lane(lane_id: str, label: str, state: str) -> dict[str, Any]:
    return {
        "lane_id": lane_id,
        "label": label,
        "state": state,
        "promotion_gate": "nexusbrain-policy-approval-sandbox-isolation-replay",
    }


def _integration_lane(lane_id: str, label: str, state: str) -> dict[str, Any]:
    return {
        "lane_id": lane_id,
        "label": label,
        "state": state,
        "promotion_gate": "identity-consent-permission-trust-envelope-revocation-audit",
    }


def _delivery_lane(lane_id: str, label: str, state: str) -> dict[str, Any]:
    return {
        "lane_id": lane_id,
        "label": label,
        "state": state,
        "promotion_gate": "source-evidence-artifact-trust-memory-feedback-replay-proof",
    }


def _input_lane(lane_id: str, label: str, state: str) -> dict[str, Any]:
    return {
        "lane_id": lane_id,
        "label": label,
        "state": state,
        "promotion_gate": "source-permission-freshness-redaction-command-correlation",
    }


def _flow_segment(
    segment_id: str,
    label: str,
    state: str | None,
    evidence_refs: list[str] | None,
    answer: str | None,
) -> dict[str, Any]:
    return {
        "segment_id": segment_id,
        "label": label,
        "state": state or "static-canon",
        "answer": answer or "No live proof recorded for this segment yet.",
        "evidence_refs": evidence_refs or [],
        "correlation_requirement": "command_id",
    }


def _orchestrator_unit(unit_id: str, label: str, state: str | None) -> dict[str, Any]:
    return {
        "unit_id": unit_id,
        "label": label,
        "state": state or "static-canon",
        "authority": "NexusBrain",
        "promotion_gate": "live-trace-policy-eval-fallback-proof",
    }


def _security_lane(lane_id: str, label: str, state: str) -> dict[str, Any]:
    return {
        "lane_id": lane_id,
        "label": label,
        "state": state,
        "promotion_gate": "policy-permission-guardrail-audit-privacy-rollback",
    }


def _recorder_frame(frame_id: str, label: str, answer: dict[str, Any]) -> dict[str, Any]:
    return {
        "frame_id": frame_id,
        "label": label,
        "state": answer.get("answer_state") or answer.get("surface_state") or "static-canon",
        "answer": answer.get("answer") or "No live proof has been recorded for this frame.",
        "surface_id": answer.get("surface_id"),
        "evidence_refs": answer.get("evidence_refs") or [],
        "compliance_controls": answer.get("compliance_controls") or [],
        "promotion_gate": answer.get("promotion_gate"),
    }


def _consensus_rule(rule_id: str, label: str) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "label": label,
        "state": "enforced",
        "authority": "NexusBrain",
    }


def _research_role(role_id: str, responsibility: str) -> dict[str, Any]:
    return {
        "role_id": role_id,
        "label": role_id.replace("-", " ").title(),
        "state": "research-candidate" if role_id in {"horizon-scout", "source-verifier"} else "shadow-only",
        "responsibility": responsibility,
        "reports_to": "NexusBrain",
        "promotion_gate": "source-license-security-eval-runtime-rollback-operator-approval",
    }


def _promotion_stage(stage_id: str, label: str, state: str) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "label": label,
        "state": state,
        "authority": "NexusBrain",
    }


def _improvement_stage(stage_id: str, label: str, state: str) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "label": label,
        "state": state,
        "authority": "NexusBrain",
        "promotion_gate": "human-review-external-verification-regression-rollback",
    }


def _ao_context_scope(record: dict[str, Any]) -> str:
    name = str(record.get("name") or record.get("ao_name") or "AO")
    if "Memory" in name:
        return "memory planes, source-to-claim maps, and continuity packets"
    if "Governance" in name or "Safety" in name:
        return "policy, approvals, audit trail, rollback, and veto state"
    if "Runtime" in name:
        return "runtime lanes, quantization, hardware fit, and performance evidence"
    if "Eval" in name or "Critique" in name:
        return "held-out evals, regression gates, critique, and quality evidence"
    if "Coding" in name or "Tool" in name:
        return "tool execution, code paths, sandbox, and replay traces"
    return "mission intent, local reasoning, evidence, and collaboration state"


def _ao_permissions(record: dict[str, Any]) -> list[str]:
    name = str(record.get("name") or record.get("ao_name") or "")
    if "Governance" in name or "Safety" in name:
        return ["policy-read", "audit-write", "veto-escalation", "rollback-request"]
    if "Runtime" in name:
        return ["runtime-read", "benchmark-request", "backend-profile-read"]
    if "Tool" in name or "Coding" in name:
        return ["tool-registry-read", "sandbox-request", "replay-read"]
    if "Memory" in name:
        return ["memory-read", "memory-write-candidate", "privacy-check"]
    if "Eval" in name or "Critique" in name:
        return ["eval-read", "critique-write", "promotion-blocker-write"]
    return ["command-read", "evidence-write", "consensus-contribute"]


def _ao_governance_constraints(record: dict[str, Any]) -> list[str]:
    constraints = ["reports-to-nexusbrain", "evidence-required", "audit-visible"]
    if (record.get("risk_tier") or "medium") == "high":
        constraints.extend(["explicit-approval-for-high-risk-actions", "veto-escalation-enabled"])
    return constraints


def _selected_ao_name(operations: dict[str, Any]) -> str | None:
    latest_command = operations.get("latest_command") or {}
    explicit = ((latest_command.get("context") or {}).get("ao"))
    if explicit:
        return explicit
    for event in operations.get("timeline") or []:
        if event.get("event_type") == "ao_signal":
            signals = event.get("signals") or []
            if signals:
                return signals[0].get("actor")
            return event.get("actor")
    return None


def _ao_is_selected(record: dict[str, Any], operations: dict[str, Any]) -> bool:
    selected = _selected_ao_name(operations)
    return bool(selected and selected == (record.get("name") or record.get("ao_name")))


def _latest_expert_signals(operations: dict[str, Any]) -> list[dict[str, Any]]:
    for event in operations.get("timeline") or []:
        if event.get("event_type") == "expert_signal":
            return list(event.get("signals") or [])
    return []


def _expert_hive_record(record: dict[str, Any], operations: dict[str, Any]) -> dict[str, Any]:
    subject = record.get("subject") or record.get("expert") or "expert"
    display_name = record.get("display_name") or record.get("subject_display_name") or str(subject).replace("-", " ").title()
    return {
        "subject": subject,
        "display_name": display_name,
        "role_hint": record.get("role_hint") or record.get("description") or "Domain-specialized expert mini-brain.",
        "topology_id": record.get("topology_id") or f"{subject}-mini-nexusnet",
        "geometry_kind": record.get("geometry_kind") or "domain-mini-brain",
        "neural_node_budget": record.get("neural_node_budget") or 16,
        "motif_labels": record.get("motif_labels") or [],
        "reports_to": "Experts Hive",
        "authority": "NexusBrain",
        "mini_nexusnet": True,
        "model_tool_permissions": _expert_permissions(str(subject)),
        "consensus_state": "selected-route" if _expert_is_selected(display_name, str(subject), operations) else "available",
        "memory_feedback": "source-to-claim-and-privacy-gated",
        "promotion_gate": "expert-evidence-uncertainty-policy-eval-memory-feedback",
    }


def _expert_is_selected(display_name: str, subject: str, operations: dict[str, Any]) -> bool:
    for signal in _latest_expert_signals(operations):
        if signal.get("actor") == display_name or signal.get("subject") == subject:
            return True
    return False


def _expert_permissions(subject: str) -> list[str]:
    normalized = subject.lower()
    permissions = ["domain-evidence-write", "uncertainty-report", "consensus-contribute"]
    if normalized in {"coder", "builder", "toolsmith"}:
        permissions.extend(["tool-schema-read", "code-evidence-write"])
    if normalized in {"security", "critique", "meta-reasoner"}:
        permissions.extend(["veto-escalation", "policy-risk-write"])
    if normalized in {"researcher", "analyst", "critic-historian"}:
        permissions.extend(["source-map-write", "contradiction-report"])
    if normalized in {"memory-weaver", "router", "intent-mapper"}:
        permissions.extend(["memory-context-read", "route-constraint-write"])
    if normalized in {"vision", "audio", "linguist"}:
        permissions.extend(["multimodal-evidence-write", "fallback-required"])
    return list(dict.fromkeys(permissions))


def _hive_signal_frame(
    frame_id: str,
    label: str,
    event: dict[str, Any] | None,
    *,
    active_command_id: str | None,
) -> dict[str, Any]:
    consensus = (event or {}).get("consensus") or {}
    return {
        "frame_id": frame_id,
        "label": label,
        "state": "live-bound" if event else ("standby" if active_command_id else "static-canon"),
        "event_id": (event or {}).get("event_id"),
        "actor": (event or {}).get("actor") or "NexusBrain",
        "detail": (event or {}).get("detail") or "No live signal recorded for this frame.",
        "signal_count": len((event or {}).get("signals") or []),
        "consensus_state": consensus.get("state") or ("pending-consensus" if frame_id == "consensus_state" and event else "not-open"),
        "veto_state": consensus.get("veto_state") or ("clear" if active_command_id else "unknown"),
        "evidence_refs": ["/ops/brain/operations", "/ops/brain/visualizer/state"],
    }


def _flatten_endpoint_refs(endpoint_reuse: dict[str, dict[str, Any]]) -> list[str]:
    refs: list[str] = []
    for item in endpoint_reuse.values():
        refs.extend(item.get("endpoint_refs") or [])
        refs.extend(item.get("doc_refs") or [])
    return list(dict.fromkeys(refs))


def _surface_record(surface_id: str, requirement: str, page: dict[str, Any] | None) -> dict[str, Any]:
    if not page:
        return {
            "surface_id": surface_id,
            "label": surface_id,
            "state": "missing",
            "canon_requirement": requirement,
            "metrics": {},
            "evidence_refs": [],
            "research_lanes": [],
            "compliance_controls": SURFACE_COMPLIANCE_CONTROLS.get(surface_id, []),
            "next_action": "Create the missing control surface and bind it to truthful state.",
            "promotion_gate": "Cannot promote until the required surface exists.",
        }
    state = page.get("state") or "static-canon"
    return {
        "surface_id": surface_id,
        "label": page.get("label") or surface_id,
        "state": state,
        "canon_requirement": requirement,
        "summary": page.get("summary"),
        "metrics": page.get("metrics") or {},
        "evidence_refs": page.get("evidence_refs") or [],
        "research_lanes": page.get("research_lanes") or [],
        "compliance_controls": SURFACE_COMPLIANCE_CONTROLS.get(surface_id, []),
        "next_action": _next_action(state),
        "promotion_gate": _promotion_gate(state),
    }


def _coverage(surfaces: dict[str, dict[str, Any]]) -> dict[str, int]:
    states = [record["state"] for record in surfaces.values()]
    missing_count = states.count("missing")
    return {
        "required_surface_count": len(surfaces),
        "implemented_surface_count": len(surfaces) - missing_count,
        "missing_required_surface_count": missing_count,
        "live_bound_surface_count": states.count("live-bound"),
        "degraded_surface_count": states.count("degraded"),
        "static_canon_surface_count": states.count("static-canon"),
        "research_candidate_surface_count": states.count("research-candidate"),
        "shadow_only_surface_count": states.count("shadow-only"),
        "reused_endpoint_category_count": sum(
            1
            for item in ENDPOINT_REUSE_LEDGER.values()
            if item.get("state") == "live-bound" and item.get("endpoint_refs")
        ),
    }


def _book_gates(surfaces: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    gates = []
    for spec in BOOK_GATE_SPECS:
        surface = surfaces.get(spec["surface_id"]) or {}
        available_controls = set(surface.get("compliance_controls") or [])
        required_controls = list(spec["required_controls"])
        missing_controls = [control for control in required_controls if control not in available_controls]
        surface_state = surface.get("state", "missing")
        gates.append(
            {
                **spec,
                "state": "mapped" if not missing_controls and surface_state != "missing" else "missing",
                "surface_state": surface_state,
                "missing_controls": missing_controls,
                "evidence_refs": surface.get("evidence_refs") or [],
                "next_action": surface.get("next_action") or "Create the required surface controls.",
            }
        )
    return gates


def _book_gate_coverage(book_gates: list[dict[str, Any]]) -> dict[str, int]:
    missing = [gate for gate in book_gates if gate.get("state") == "missing"]
    return {
        "required_gate_count": len(book_gates),
        "mapped_gate_count": len(book_gates) - len(missing),
        "missing_gate_count": len(missing),
    }


def _operator_questions(
    *,
    surfaces: dict[str, dict[str, Any]],
    active_command_id: str | None,
    operations_summary: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    route_state = "live-bound" if active_command_id else surfaces["live-flow-trace"]["state"]
    latest_command = operations_summary.get("latest_command") or {}
    current_state = "live-bound" if active_command_id else surfaces["overview"]["state"]
    current_answer = (
        f"NexusBrain is holding command {active_command_id}: {latest_command.get('command_text')}"
        if active_command_id
        else "No active command has been issued in this session."
    )
    policy_event = _latest_timeline_event(operations_summary, "policy_decision")
    artifact_event = _latest_timeline_event(operations_summary, "artifact_model")
    update_event = _latest_timeline_event(operations_summary, "update_candidate")
    research_event = _latest_timeline_event(operations_summary, "research_watch")
    return {
        "current_activity": {
            "prompt": "What is happening now?",
            "surface_id": "overview",
            "answer_state": current_state,
            "evidence_refs": ["/ops/brain/operations", "/ops/brain/visualizer/state"],
            "current_answer": current_answer,
        },
        "route_provenance": {
            "prompt": "Which brain, expert, tool, and memory route produced this action?",
            "surface_id": "live-flow-trace",
            "answer_state": route_state,
            "evidence_refs": ["/ops/brain/operations"],
            "current_answer": latest_command.get("command_text") if active_command_id else "No active command has been issued in this session.",
        },
        "policy_decision": {
            "prompt": "Which policy allowed or denied it?",
            "surface_id": "governance-observability",
            "answer_state": "live-bound" if policy_event else surfaces["governance-observability"]["state"],
            "evidence_refs": [
                "/ops/brain/security/permissions",
                "/ops/brain/security/guardrails",
                "/ops/brain/operations",
            ],
            "current_answer": _event_detail(policy_event),
        },
        "eval_evidence": {
            "prompt": "Which eval proves the behavior is acceptable?",
            "surface_id": "eval-center",
            "answer_state": surfaces["eval-center"]["state"],
            "evidence_refs": ["/ops/brain/promotions", "/ops/brain/eval-report"],
        },
        "artifact_model": {
            "prompt": "Which artifact or model is being used?",
            "surface_id": "artifact-trust",
            "answer_state": "live-bound" if artifact_event else surfaces["artifact-trust"]["state"],
            "evidence_refs": [
                "/ops/brain/teachers",
                "/ops/brain/backends",
                "/ops/brain/extensions/certifications",
            ],
            "current_answer": _event_detail(artifact_event),
        },
        "runtime_path": {
            "prompt": "Which runtime and quantization path is active?",
            "surface_id": "runtime-lab",
            "answer_state": surfaces["runtime-lab"]["state"],
            "evidence_refs": ["/ops/brain/backends"],
        },
        "trusted_protocol": {
            "prompt": "Which protocol or connector is trusted?",
            "surface_id": "connections-protocols",
            "answer_state": surfaces["connections-protocols"]["state"],
            "evidence_refs": ["/ops/brain/acp", "/ops/brain/extensions"],
        },
        "memory_support": {
            "prompt": "Which memory source supports the answer?",
            "surface_id": "context-memory",
            "answer_state": surfaces["context-memory"]["state"],
            "evidence_refs": ["/ops/brain/memory/planes", "/ops/brain/graph/status"],
        },
        "update_candidate": {
            "prompt": "Which update candidate is waiting?",
            "surface_id": "dreaming-evolution",
            "answer_state": "live-bound" if update_event else surfaces["dreaming-evolution"]["state"],
            "evidence_refs": ["/ops/brain/promotions", "/ops/brain/foundry/status"],
            "current_answer": _event_detail(update_event),
        },
        "research_watch": {
            "prompt": "Which future research lane is being watched?",
            "surface_id": "forward-radar",
            "answer_state": "live-bound" if research_event else surfaces["forward-radar"]["state"],
            "evidence_refs": [
                "docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md",
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
            ],
            "current_answer": _event_detail(research_event),
        },
    }


def _latest_timeline_event(operations_summary: dict[str, Any], event_type: str) -> dict[str, Any] | None:
    for event in reversed(operations_summary.get("timeline") or []):
        if event.get("event_type") == event_type:
            return event
    return None


def _event_detail(event: dict[str, Any] | None) -> str | None:
    if not event:
        return None
    return event.get("detail") or event.get("label")


def _surface_answer(*, question_id: str, surface: dict[str, Any]) -> str:
    label = surface.get("label") or surface.get("surface_id") or "selected surface"
    state = surface.get("state") or "unknown"
    controls = ", ".join(surface.get("compliance_controls") or [])
    if question_id == "current_activity":
        return f"{label} is {state}; the current activity must be read from NexusBrain operations and visualizer state."
    if question_id == "policy_decision":
        return f"{label} is {state}; allowed or denied status must come from permissions, guardrails, and the audited command event."
    if question_id == "runtime_path":
        return f"{label} is {state}; required runtime controls are {controls or 'not declared'}."
    if question_id == "eval_evidence":
        return f"{label} is {state}; eval proof must come from held-out tasks, regression gates, and promotion blockers."
    if question_id == "artifact_model":
        return f"{label} is {state}; artifact or model trust depends on provenance, signatures, unsafe serialization, scanner status, and license state."
    if question_id == "trusted_protocol":
        return f"{label} is {state}; trust depends on identity, permissions, consent, trust envelopes, and revocation."
    if question_id == "memory_support":
        return f"{label} is {state}; memory support depends on retrieval quality, source-to-claim maps, provenance, stale memory, and privacy controls."
    if question_id == "update_candidate":
        return f"{label} is {state}; update candidate promotion requires candidate state, shadow simulation, provenance, rollback evidence, and operator approval."
    if question_id == "research_watch":
        return f"{label} is {state}; research lanes remain watchlisted until registry, license, security, eval, runtime, privacy, and governance gates pass."
    return f"{label} is {state}."


def _next_action(state: str) -> str:
    if state == "live-bound":
        return "Keep live telemetry, evals, policy, and audit references fresh."
    if state == "degraded":
        return "Bind the degraded surface to a live endpoint or explain the missing telemetry source."
    if state == "research-candidate":
        return "Keep this as candidate state until registry, license, security, eval, runtime, privacy, and governance gates pass."
    if state == "shadow-only":
        return "Keep in shadow simulation and require promotion evidence before operator-facing activation."
    return "Replace static canon with live endpoint evidence where the runtime surface exists."


def _promotion_gate(state: str) -> str:
    if state == "live-bound":
        return "Runtime evidence and audit trail are present."
    if state == "research-candidate":
        return "Requires registry, license, security, eval, runtime, privacy, and governance approval."
    if state == "shadow-only":
        return "Requires shadow-run comparison, rollback evidence, and operator approval."
    if state == "degraded":
        return "Requires restored telemetry and explicit degraded-state recovery evidence."
    return "Requires live API binding or explicit static-canon acceptance."
