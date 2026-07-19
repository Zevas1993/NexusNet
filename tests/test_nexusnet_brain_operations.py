from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_brain_operations_command_lifecycle_records_hive_signals(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "ops-session",
            "command_text": "Coordinate the AO hive and expert hive to build the real command cockpit.",
            "priority": "high",
            "target_surface": "mission-control-cockpit",
            "context": {"source": "canon-book"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    command = payload["command"]
    assert payload["status_label"] == "LOCKED CANON"
    assert command["command_id"].startswith("braincmd::ops-session::")
    assert command["authority"] == "NexusBrain"
    assert command["lifecycle_state"] == "issued"
    assert command["target_surface"] == "mission-control-cockpit"
    assert payload["canon_binding"]["source_document"] == "NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md"
    assert payload["canon_binding"]["state_taxonomy"] == [
        "live_state",
        "simulated_state",
        "roadmap_state",
        "research_candidate_state",
    ]
    assert payload["signal_contract"] == [
        "receives_orders",
        "local_reasoning",
        "evidence_response",
        "veto_escalation",
        "consensus_contribution",
        "execution_status",
    ]
    assert payload["consensus"]["state"] == "pending-consensus"
    assert payload["consensus"]["veto_state"] == "clear"
    assert payload["ao_signals"]
    assert payload["ao_signals"][0]["reports_to"] == "NexusBrain"
    assert payload["ao_signals"][0]["signal_type"] == "receives_orders"
    assert payload["expert_signals"]
    assert payload["expert_signals"][0]["role"] == "Expert mini-brain"
    assert {
        "command_issued",
        "ao_signal",
        "expert_signal",
        "consensus_state",
    }.issubset({event["event_type"] for event in payload["timeline"]})

    summary = client.get("/ops/brain/operations", params={"session_id": "ops-session"})
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload["latest_command"]["command_id"] == command["command_id"]
    assert summary_payload["command_count"] == 1
    assert any(event["event_type"] == "ao_signal" for event in summary_payload["timeline"])


def test_control_panel_cockpit_surfaces_live_brain_operations(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "cockpit-session",
            "command_text": "Build the NexusNet Neural Network Hive Mind control panel.",
            "priority": "critical",
            "target_surface": "mission-control-cockpit",
        },
    ).json()["command"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "cockpit-session"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    cockpit = control_panel["cockpit"]
    live_operations = cockpit["live_operations"]
    assert live_operations["state"] == "live-bound"
    assert live_operations["latest_command"]["command_id"] == command["command_id"]
    assert cockpit["command_bar"]["active_command_id"] == command["command_id"]
    assert cockpit["operations_board"]["live_columns"]
    assert any(column["signal_type"] == "ao_signal" for column in cockpit["operations_board"]["live_columns"])
    assert any(event["event_type"] == "command_issued" for event in cockpit["timeline"]["events"])
    assert control_panel["pages"][0]["metrics"]["active_command_id"] == command["command_id"]


def test_canon_realization_ledger_maps_book_requirements_to_control_surfaces(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/canon/realization", params={"session_id": "canon-session"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["source_document"] == "NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md"
    assert payload["state_taxonomy"] == [
        "live-bound",
        "degraded",
        "static-canon",
        "research-candidate",
        "shadow-only",
    ]
    required_ids = set(payload["required_surface_ids"])
    assert {
        "overview",
        "live-flow-trace",
        "neural-core",
        "ao-hive",
        "context-memory",
        "governance-observability",
        "connections-protocols",
        "tools-execution",
        "runtime-lab",
        "eval-center",
        "artifact-trust",
        "hardware-matrix",
        "visualops",
        "dreaming-evolution",
        "forward-radar",
    }.issubset(required_ids)
    assert payload["coverage"]["missing_required_surface_count"] == 0
    assert payload["coverage"]["required_surface_count"] == len(payload["required_surface_ids"])
    assert payload["surfaces"]["runtime-lab"]["research_lanes"] == ["inference-architecture"]
    assert payload["surfaces"]["forward-radar"]["state"] == "research-candidate"
    assert payload["surfaces"]["eval-center"]["canon_requirement"]
    assert payload["operator_questions"]["route_provenance"]["prompt"] == "Which brain, expert, tool, and memory route produced this action?"
    assert payload["operator_questions"]["runtime_path"]["answer_state"] in {
        "live-bound",
        "degraded",
        "static-canon",
        "research-candidate",
    }


def test_canon_realization_tracks_live_command_and_ui_command_controls(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "canon-command-session",
            "command_text": "Realize the Canon Book as the live NexusNet command system.",
            "priority": "critical",
            "target_surface": "mission-control-cockpit",
        },
    ).json()["command"]

    realization = client.get("/ops/brain/canon/realization", params={"session_id": "canon-command-session"}).json()
    assert realization["live_bindings"]["active_command_id"] == command["command_id"]
    assert realization["operator_questions"]["route_provenance"]["answer_state"] == "live-bound"
    assert realization["surfaces"]["overview"]["metrics"]["active_command_id"] == command["command_id"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "canon-command-session"}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    assert control_panel["canon_realization"]["live_bindings"]["active_command_id"] == command["command_id"]
    assert control_panel["canon_realization"]["coverage"]["missing_required_surface_count"] == 0

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Issue NexusBrain Command" in ui.text
    assert "Canon Realization Ledger" in ui.text
    assert "canonCommandInput" in ui.text


def test_brain_operation_events_advance_lifecycle_and_surface_veto_state(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "event-session",
            "command_text": "Route a risky tool action through governance before execution.",
            "priority": "high",
            "target_surface": "mission-control-cockpit",
        },
    ).json()["command"]

    event_response = client.post(
        f"/ops/brain/operations/commands/{command['command_id']}/events",
        json={
            "session_id": "event-session",
            "event_type": "veto_escalation",
            "actor": "GovernanceAO",
            "detail": "Security review required before tool execution.",
            "lifecycle_state": "blocked",
            "metadata": {"gate": "security-review"},
        },
    )

    assert event_response.status_code == 200
    event_payload = event_response.json()
    assert event_payload["command"]["lifecycle_state"] == "blocked"
    assert event_payload["event"]["event_type"] == "veto_escalation"
    assert event_payload["event"]["consensus"]["veto_state"] == "active"

    summary = client.get("/ops/brain/operations", params={"session_id": "event-session"}).json()
    assert summary["latest_command"]["lifecycle_state"] == "blocked"
    assert any(event["event_type"] == "veto_escalation" for event in summary["timeline"])

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "event-session"}).json()
    columns = visualizer["overlay_state"]["control_panel"]["cockpit"]["operations_board"]["live_columns"]
    veto_column = next(column for column in columns if column["signal_type"] == "veto_escalation")
    assert veto_column["state"] == "live-bound"
    assert "Security review required" in veto_column["detail"]


def test_canon_realize_next_creates_a_brain_command_for_book_gap(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/canon/realize-next",
        json={
            "session_id": "realize-next-session",
            "surface_id": "runtime-lab",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["target_surface"]["surface_id"] == "runtime-lab"
    assert "Runtime Lab" in payload["command"]["command_text"]
    assert payload["command"]["authority"] == "NexusBrain"
    assert payload["command"]["context"]["source"] == "canon-realization"
    assert payload["command"]["context"]["surface_id"] == "runtime-lab"

    summary = client.get("/ops/brain/operations", params={"session_id": "realize-next-session"}).json()
    assert summary["latest_command"]["command_id"] == payload["command"]["command_id"]


def test_canon_realization_enforces_book_build_gates_and_surface_controls(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    realization = client.get("/ops/brain/canon/realization", params={"session_id": "gate-session"}).json()

    gate_ids = {gate["gate_id"] for gate in realization["book_gates"]}
    assert {
        "runtime-quantization-scorecard",
        "protocol-trust-envelope",
        "held-out-eval-regression",
        "memory-quality-provenance",
        "artifact-supply-chain-trust",
        "evolution-promotion-boundary",
    }.issubset(gate_ids)
    runtime_gate = next(gate for gate in realization["book_gates"] if gate["gate_id"] == "runtime-quantization-scorecard")
    assert runtime_gate["required_controls"] == [
        "formats",
        "methods",
        "cache_economics",
        "backend_compatibility",
        "eval_deltas",
        "hardware_fit",
    ]
    protocol_gate = next(gate for gate in realization["book_gates"] if gate["gate_id"] == "protocol-trust-envelope")
    assert protocol_gate["required_controls"] == [
        "identity",
        "permissions",
        "consent",
        "trust_envelopes",
        "revocation",
    ]
    assert realization["surfaces"]["runtime-lab"]["compliance_controls"] == runtime_gate["required_controls"]
    assert "held_out_tasks" in realization["surfaces"]["eval-center"]["compliance_controls"]
    assert "source_to_claim_maps" in realization["surfaces"]["context-memory"]["compliance_controls"]
    assert "unsafe_serialization" in realization["surfaces"]["artifact-trust"]["compliance_controls"]
    assert realization["book_gate_coverage"]["missing_gate_count"] == 0

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "gate-session"}).json()
    control_panel = visualizer["overlay_state"]["control_panel"]
    assert control_panel["canon_realization"]["book_gate_coverage"]["required_gate_count"] >= 6
    assert control_panel["book_gate_summary"]["missing_gate_count"] == 0

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Book Compliance" in ui.text
    assert "complianceList" in ui.text
    assert "Operator Answer Links" in ui.text
    assert "answerLinkGrid" in ui.text


def test_canon_operator_answer_endpoint_answers_book_questions_with_evidence(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "answer-session",
            "command_text": "Answer the final console questions from the Canon Book.",
            "priority": "high",
            "target_surface": "mission-control-cockpit",
        },
    ).json()["command"]

    route = client.get(
        "/ops/brain/canon/answers/route_provenance",
        params={"session_id": "answer-session"},
    )
    assert route.status_code == 200
    route_payload = route.json()
    assert route_payload["question_id"] == "route_provenance"
    assert route_payload["answer_state"] == "live-bound"
    assert route_payload["active_command_id"] == command["command_id"]
    assert route_payload["evidence_refs"] == ["/ops/brain/operations"]
    assert "Answer the final console questions" in route_payload["answer"]

    runtime = client.get(
        "/ops/brain/canon/answers/runtime_path",
        params={"session_id": "answer-session"},
    ).json()
    assert runtime["question_id"] == "runtime_path"
    assert runtime["surface_id"] == "runtime-lab"
    assert "formats" in runtime["compliance_controls"]
    assert "/ops/brain/backends" in runtime["evidence_refs"]

    unknown = client.get("/ops/brain/canon/answers/not-a-question")
    assert unknown.status_code == 404


def test_canon_operator_question_matrix_covers_all_final_console_questions(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "ten-question-session",
            "command_text": "Show the operator exactly what NexusNet is doing now.",
            "priority": "critical",
            "target_surface": "mission-control-cockpit",
        },
    ).json()["command"]

    realization = client.get(
        "/ops/brain/canon/realization",
        params={"session_id": "ten-question-session"},
    ).json()

    assert list(realization["operator_questions"]) == [
        "current_activity",
        "route_provenance",
        "policy_decision",
        "eval_evidence",
        "artifact_model",
        "runtime_path",
        "trusted_protocol",
        "memory_support",
        "update_candidate",
        "research_watch",
    ]
    assert realization["operator_questions"]["current_activity"]["answer_state"] == "live-bound"
    assert realization["operator_questions"]["current_activity"]["current_answer"] == (
        f"NexusBrain is holding command {command['command_id']}: Show the operator exactly what NexusNet is doing now."
    )
    assert realization["operator_questions"]["policy_decision"]["surface_id"] == "governance-observability"
    assert "/ops/brain/security/permissions" in realization["operator_questions"]["policy_decision"]["evidence_refs"]
    assert realization["operator_questions"]["artifact_model"]["surface_id"] == "artifact-trust"
    assert "/ops/brain/extensions/certifications" in realization["operator_questions"]["artifact_model"]["evidence_refs"]
    assert realization["operator_questions"]["update_candidate"]["surface_id"] == "dreaming-evolution"
    assert realization["operator_questions"]["research_watch"]["surface_id"] == "forward-radar"


def test_missing_canon_answer_endpoints_return_surface_specific_evidence(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "missing-answer-session",
            "command_text": "Route policy, artifact, update, and research answers into the cockpit.",
            "priority": "high",
            "target_surface": "mission-control-cockpit",
        },
    ).json()["command"]

    current = client.get(
        "/ops/brain/canon/answers/current_activity",
        params={"session_id": "missing-answer-session"},
    )
    assert current.status_code == 200
    current_payload = current.json()
    assert current_payload["answer_state"] == "live-bound"
    assert current_payload["active_command_id"] == command["command_id"]
    assert current_payload["surface_id"] == "overview"
    assert current_payload["evidence_refs"] == ["/ops/brain/operations", "/ops/brain/visualizer/state"]

    policy = client.get(
        "/ops/brain/canon/answers/policy_decision",
        params={"session_id": "missing-answer-session"},
    ).json()
    assert policy["surface_id"] == "governance-observability"
    assert policy["evidence_refs"] == [
        "/ops/brain/security/permissions",
        "/ops/brain/security/guardrails",
        "/ops/brain/operations",
    ]
    assert "allowed or denied" in policy["answer"]

    artifact = client.get(
        "/ops/brain/canon/answers/artifact_model",
        params={"session_id": "missing-answer-session"},
    ).json()
    assert artifact["surface_id"] == "artifact-trust"
    assert {"provenance", "unsafe_serialization", "license_state"}.issubset(set(artifact["compliance_controls"]))
    assert "/ops/brain/teachers" in artifact["evidence_refs"]

    update = client.get(
        "/ops/brain/canon/answers/update_candidate",
        params={"session_id": "missing-answer-session"},
    ).json()
    assert update["surface_id"] == "dreaming-evolution"
    assert "candidate" in update["answer"]

    research = client.get(
        "/ops/brain/canon/answers/research_watch",
        params={"session_id": "missing-answer-session"},
    ).json()
    assert research["surface_id"] == "forward-radar"
    assert "research" in research["answer"].lower()


def test_canon_surface_drilldown_maps_surface_gates_answers_and_realization_command(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    runtime = client.get(
        "/ops/brain/canon/surfaces/runtime-lab",
        params={"session_id": "surface-session"},
    )
    assert runtime.status_code == 200
    payload = runtime.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface"]["surface_id"] == "runtime-lab"
    assert payload["surface"]["canon_requirement"].startswith("Quantization formats")
    assert {gate["gate_id"] for gate in payload["book_gates"]} == {"runtime-quantization-scorecard"}
    assert payload["answer_links"] == [
        {
            "question_id": "runtime_path",
            "prompt": "Which runtime and quantization path is active?",
            "href": "/ops/brain/canon/answers/runtime_path",
            "answer_state": payload["surface"]["state"],
        }
    ]
    assert payload["realize_next"]["endpoint"] == "/ops/brain/canon/realize-next"
    assert payload["realize_next"]["body"]["surface_id"] == "runtime-lab"
    assert payload["realize_next"]["body"]["session_id"] is None
    assert "surface-session" not in str(payload)
    assert payload["realize_next"]["method"] == "POST"

    missing = client.get("/ops/brain/canon/surfaces/not-a-surface")
    assert missing.status_code == 404


def test_control_panel_ui_can_queue_selected_canon_surface(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Queue Next Canon Action" in ui.text
    assert "realizeSurfaceButton" in ui.text
    assert "surfaceDrilldownList" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "realizeSelectedSurface" in app_js
    assert "/ops/brain/canon/surfaces/" in app_js
    assert "/ops/brain/canon/realize-next" in app_js


def test_control_panel_ui_can_record_operator_answer_proof(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Record Answer Proof" in ui.text
    assert "canonProofForm" in ui.text
    assert "canonProofQuestion" in ui.text
    assert "canonProofDetail" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "recordAnswerProof" in app_js
    assert "/ops/brain/canon/answers/" in app_js
    assert "/events" in app_js


def test_canon_answers_promote_to_live_when_brain_timeline_records_decisions(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "live-answer-session",
            "command_text": "Execute the live operator answer proof path.",
            "priority": "critical",
            "target_surface": "mission-control-cockpit",
        },
    ).json()["command"]
    live_events = [
        (
            "policy_decision",
            "SecurityAO",
            "Policy TOOL-RISK-001 allowed the read-only inspection and denied destructive execution.",
            {"policy_id": "TOOL-RISK-001", "decision": "allow-read-deny-write"},
        ),
        (
            "artifact_model",
            "RuntimeAO",
            "Model qwen2.5-3b-mnn is selected with artifact cert-001 pending signature verification.",
            {"model_id": "qwen2.5-3b-mnn", "artifact_id": "cert-001"},
        ),
        (
            "update_candidate",
            "EvolutionAO",
            "Candidate native-takeover-2026 is waiting in shadow-only promotion state.",
            {"candidate_id": "native-takeover-2026", "promotion_state": "shadow-only"},
        ),
        (
            "research_watch",
            "ResearchAO",
            "Forward radar is watching TurboQuant, LMCache, A2A, AG-UI, and OSWorld.",
            {"lane_id": "forward-radar", "watch_items": ["TurboQuant", "LMCache", "A2A", "AG-UI", "OSWorld"]},
        ),
    ]
    for event_type, actor, detail, metadata in live_events:
        response = client.post(
            f"/ops/brain/operations/commands/{command['command_id']}/events",
            json={
                "session_id": "live-answer-session",
                "event_type": event_type,
                "actor": actor,
                "detail": detail,
                "metadata": metadata,
            },
        )
        assert response.status_code == 200

    realization = client.get(
        "/ops/brain/canon/realization",
        params={"session_id": "live-answer-session"},
    ).json()
    assert realization["operator_questions"]["policy_decision"]["answer_state"] == "live-bound"
    assert realization["operator_questions"]["policy_decision"]["current_answer"].startswith("Policy TOOL-RISK-001")
    assert realization["operator_questions"]["artifact_model"]["answer_state"] == "live-bound"
    assert "qwen2.5-3b-mnn" in realization["operator_questions"]["artifact_model"]["current_answer"]
    assert realization["operator_questions"]["update_candidate"]["answer_state"] == "live-bound"
    assert "native-takeover-2026" in realization["operator_questions"]["update_candidate"]["current_answer"]
    assert realization["operator_questions"]["research_watch"]["answer_state"] == "live-bound"
    assert "TurboQuant" in realization["operator_questions"]["research_watch"]["current_answer"]

    policy = client.get(
        "/ops/brain/canon/answers/policy_decision",
        params={"session_id": "live-answer-session"},
    ).json()
    assert policy["answer_state"] == "live-bound"
    assert policy["answer"].startswith("Policy TOOL-RISK-001")


def test_canon_answer_event_endpoint_records_live_proof_against_active_command(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "answer-event-session",
            "command_text": "Record policy proof without exposing raw event plumbing.",
            "priority": "high",
            "target_surface": "mission-control-cockpit",
        },
    ).json()["command"]

    event_response = client.post(
        "/ops/brain/canon/answers/policy_decision/events",
        json={
            "session_id": "answer-event-session",
            "actor": "SecurityAO",
            "detail": "Policy CONNECTOR-READ-001 allowed connector inventory and denied external mutation.",
            "metadata": {"policy_id": "CONNECTOR-READ-001", "decision": "allow-read"},
        },
    )

    assert event_response.status_code == 200
    payload = event_response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["event"]["command_id"] == command["command_id"]
    assert payload["event"]["event_type"] == "policy_decision"
    assert payload["answer"]["answer_state"] == "live-bound"
    assert payload["answer"]["surface_id"] == "governance-observability"
    assert payload["answer"]["answer"].startswith("Policy CONNECTOR-READ-001")

    missing = client.post(
        "/ops/brain/canon/answers/not-a-question/events",
        json={
            "session_id": "answer-event-session",
            "actor": "SecurityAO",
            "detail": "No question exists.",
        },
    )
    assert missing.status_code == 404


def test_canon_realization_reuses_existing_operational_endpoints(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    realization = client.get("/ops/brain/canon/realization", params={"session_id": "reuse-session"}).json()

    reuse = realization["endpoint_reuse_ledger"]
    assert reuse["protocol"]["state"] == "live-bound"
    assert {"/ops/brain/acp", "/ops/brain/extensions", "/ops/brain/gateway"}.issubset(set(reuse["protocol"]["endpoint_refs"]))
    assert reuse["training"]["state"] == "live-bound"
    assert {"/ops/brain/curriculum", "/ops/brain/distill-dataset", "/ops/brain/dream"}.issubset(set(reuse["training"]["endpoint_refs"]))
    assert reuse["license_review"]["state"] == "live-bound"
    assert "/ops/brain/extensions/certifications" in reuse["license_review"]["endpoint_refs"]
    assert reuse["replacement_readiness"]["state"] == "live-bound"
    assert "/ops/brain/visualizer/replacement-readiness/compare" in reuse["replacement_readiness"]["endpoint_refs"]
    assert reuse["operator"]["state"] == "live-bound"
    assert {"/chat", "/ops/brain/core", "/ops/brain/operations"}.issubset(set(reuse["operator"]["endpoint_refs"]))
    assert realization["coverage"]["reused_endpoint_category_count"] >= 5


def test_canon_completion_endpoint_scores_operational_readiness_from_book_gates(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get(
        "/ops/brain/canon/completion",
        params={"session_id": "completion-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["claim_scope"] == "canon-control-plane"
    assert payload["ready_for_operator_use"] is True
    assert payload["full_product_finished"] is False
    assert payload["completion_percent"] >= 80
    assert payload["next_action_queue_endpoint"] == "/ops/brain/canon/realize-next"

    gates = {gate["gate_id"]: gate for gate in payload["gates"]}
    assert {
        "required-surface-coverage",
        "operator-answer-matrix",
        "book-gate-mapping",
            "endpoint-reuse",
            "runtime-quantization",
            "protocol-trust",
            "eval-regression",
            "memory-provenance",
            "artifact-trust",
            "autonomous-evolution",
            "forward-radar",
            "cockpit-command-loop",
        }.issubset(gates)
    assert gates["required-surface-coverage"]["metric"] == "20/20"
    assert gates["operator-answer-matrix"]["metric"] == "10/10"
    assert gates["book-gate-mapping"]["state"] == "satisfied"
    assert gates["runtime-quantization"]["surface_id"] == "runtime-lab"
    assert "TurboQuant" in gates["runtime-quantization"]["evidence_refs"]
    assert gates["autonomous-evolution"]["state"] == "guarded"
    assert "shadow-only" in gates["autonomous-evolution"]["blockers"][0]

    realization = client.get(
        "/ops/brain/canon/realization",
        params={"session_id": "completion-session"},
    ).json()
    assert realization["completion_assessment"]["completion_percent"] == payload["completion_percent"]
    assert realization["completion_assessment"]["ready_for_operator_use"] is True


def test_control_panel_ui_renders_canon_completion_matrix(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Canon Completion Matrix" in ui.text
    assert "canonCompletionMatrix" in ui.text
    assert "completionPercent" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderCanonCompletion" in app_js
    assert "completion_assessment" in app_js
    assert "/ops/brain/canon/completion" in app_js


def test_runtime_quantization_scorecard_tracks_formats_methods_and_cache_economics(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get(
        "/ops/brain/canon/runtime-scorecard",
        params={"session_id": "runtime-scorecard-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "runtime-lab"
    assert payload["source_document"] == "NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md"
    assert "TurboQuant" in payload["method_families"]
    assert {"GGUF", "safetensors", "ONNX", "MLX", "MNN", "ExecuTorch"}.issubset(set(payload["formats"]))
    assert {
        "speculative-decoding",
        "disaggregated-prefill-decode",
        "prefix-caching",
        "kv-reuse",
        "LMCache",
        "continuous-batching",
        "cache-economics",
    }.issubset({lane["lane_id"] for lane in payload["inference_architecture_lanes"]})
    assert payload["required_controls"]["cache_economics"]["state"] == "mapped"
    assert payload["required_controls"]["backend_compatibility"]["endpoint"] == "/ops/brain/backends"
    assert payload["required_controls"]["eval_deltas"]["promotion_gate"] == "held-out-eval-regression"
    assert "Windows NPU" in payload["hardware_lanes"]
    assert payload["operator_actions"]["run_benchmark"]["endpoint"] == "/ops/brain/backends/benchmark"
    assert payload["promotion_boundary"] == "candidate-or-shadow-until-eval-runtime-security-license-and-governance-pass"


def test_control_panel_ui_renders_runtime_scorecard(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Runtime Scorecard" in ui.text
    assert "runtimeScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderRuntimeScorecard" in app_js
    assert "/ops/brain/canon/runtime-scorecard" in app_js
    assert "inference_architecture_lanes" in app_js


def test_autonomous_evolution_dossier_keeps_updates_shadow_governed(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "evolution-dossier-session",
            "command_text": "Evaluate a self-review update candidate without auto-promoting it.",
            "priority": "critical",
            "target_surface": "mission-control-cockpit",
        },
    ).json()["command"]

    response = client.get(
        "/ops/brain/canon/evolution-dossier",
        params={"session_id": "evolution-dossier-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "dreaming-evolution"
    assert payload["operating_mode"] == "shadow-governed-autonomous-updates"
    assert payload["active_command_id"] == command["command_id"]
    assert payload["promotion_boundary"] == "no-autonomous-live-promotion-without-operator-approval"
    assert [stage["stage_id"] for stage in payload["pipeline"]] == [
        "observe",
        "multi-agent-research",
        "propose-patch",
        "self-review",
        "regression-generation",
        "shadow-run",
        "eval-delta",
        "rollback-plan",
        "operator-approval",
        "promotion",
    ]
    assert payload["pipeline"][1]["actor"] == "ResearchAO"
    assert payload["pipeline"][3]["actor"] == "SelfReviewAO"
    assert payload["pipeline"][5]["state"] == "shadow-only"
    assert {"eval_delta", "rollback_evidence", "operator_approval"}.issubset(set(payload["required_promotion_evidence"]))
    assert "/ops/brain/promotions" in payload["evidence_refs"]
    assert payload["operator_actions"]["queue_candidate"]["endpoint"] == "/ops/brain/canon/realize-next"


def test_control_panel_ui_renders_autonomous_evolution_dossier(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Autonomous Evolution Dossier" in ui.text
    assert "evolutionDossier" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderEvolutionDossier" in app_js
    assert "/ops/brain/canon/evolution-dossier" in app_js
    assert "shadow-governed-autonomous-updates" in app_js


def test_protocol_trust_scorecard_maps_agent_protocol_governance(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get(
        "/ops/brain/canon/protocol-trust",
        params={"session_id": "protocol-trust-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "connections-protocols"
    assert payload["authority"] == "NexusBrain"
    assert {item["protocol_id"] for item in payload["protocols"]} == {"MCP", "A2A", "ACP", "AG-UI"}
    assert payload["required_controls"] == [
        "identity",
        "permissions",
        "consent",
        "trust_envelopes",
        "revocation",
    ]
    assert payload["trust_envelope"]["decision_authority"] == "NexusBrain"
    assert payload["trust_envelope"]["revocation_endpoint"] == "/ops/brain/gateway"
    assert "/ops/brain/acp" in payload["evidence_refs"]
    assert payload["promotion_boundary"] == "protocols-remain-adapters-not-brain-authority"


def test_eval_suite_scorecard_maps_autonomous_promotion_evidence(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get(
        "/ops/brain/canon/eval-suite",
        params={"session_id": "eval-suite-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "eval-center"
    assert {item["eval_id"] for item in payload["eval_families"]}.issuperset(
        {"GAIA", "tau-bench", "OSWorld", "SWE-bench", "BrowserGym-WebArena", "RAGChecker"}
    )
    assert payload["promotion_gates"] == [
        "held_out_tasks",
        "regression_gates",
        "promotion_blockers",
        "pass_fail_trends",
        "autonomy_confidence",
    ]
    assert payload["operator_actions"]["inspect_promotions"]["endpoint"] == "/ops/brain/promotions"
    assert payload["autonomous_update_rule"] == "no-update-without-held-out-regression-and-rollback"


def test_control_panel_ui_renders_protocol_and_eval_scorecards(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Protocol Trust" in ui.text
    assert "protocolTrustScorecard" in ui.text
    assert "Eval Suite" in ui.text
    assert "evalSuiteScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderProtocolTrustScorecard" in app_js
    assert "renderEvalSuiteScorecard" in app_js
    assert "/ops/brain/canon/protocol-trust" in app_js
    assert "/ops/brain/canon/eval-suite" in app_js


def test_memory_provenance_scorecard_maps_rag_quality_and_source_to_claim_controls(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get(
        "/ops/brain/canon/memory-provenance",
        params={"session_id": "memory-provenance-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "context-memory"
    assert payload["required_controls"] == [
        "retrieval_quality",
        "source_to_claim_maps",
        "provenance",
        "stale_memory_queue",
        "privacy_controls",
    ]
    assert {lane["lane_id"] for lane in payload["memory_lanes"]}.issuperset(
        {"GraphRAG", "LightRAG", "HippoRAG", "RAGChecker", "source-to-claim"}
    )
    assert payload["quality_model"]["answerability_gate"] == "source-backed-or-explicitly-unknown"
    assert payload["operator_actions"]["inspect_memory_planes"]["endpoint"] == "/ops/brain/memory/planes"
    assert payload["operator_actions"]["inspect_graph"]["endpoint"] == "/ops/brain/graph/status"


def test_artifact_trust_scorecard_maps_supply_chain_security_controls(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get(
        "/ops/brain/canon/artifact-trust",
        params={"session_id": "artifact-trust-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "artifact-trust"
    assert payload["required_controls"] == [
        "provenance",
        "signatures",
        "unsafe_serialization",
        "scanner_status",
        "license_state",
    ]
    assert {item["control_id"] for item in payload["supply_chain_controls"]}.issuperset(
        {"safetensors", "pickle-risk", "Sigstore", "AI-BOM", "model-signing", "license-review"}
    )
    assert payload["trust_rule"] == "no-unsafe-artifact-without-scanner-provenance-license-and-rollback"
    assert payload["operator_actions"]["inspect_certifications"]["endpoint"] == "/ops/brain/extensions/certifications"


def test_hardware_and_visualops_scorecards_map_edge_and_computer_use_controls(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    hardware = client.get(
        "/ops/brain/canon/hardware-matrix",
        params={"session_id": "hardware-visualops-session"},
    )
    visualops = client.get(
        "/ops/brain/canon/visualops",
        params={"session_id": "hardware-visualops-session"},
    )

    assert hardware.status_code == 200
    hardware_payload = hardware.json()
    assert hardware_payload["surface_id"] == "hardware-matrix"
    assert {"WebNN", "WebGPU", "Apple MLX", "Qualcomm QAIRT", "LiteRT-LM", "ExecuTorch", "OpenVINO", "Windows NPU"}.issubset(
        {lane["lane_id"] for lane in hardware_payload["deployment_lanes"]}
    )
    assert hardware_payload["fallback_rule"] == "prefer-local-accelerator-when-certified-else-safe-cpu-or-server-lane"

    assert visualops.status_code == 200
    visualops_payload = visualops.json()
    assert visualops_payload["surface_id"] == "visualops"
    assert {lane["lane_id"] for lane in visualops_payload["computer_use_lanes"]}.issuperset(
        {"screen-agents", "OCR", "VLM-routing", "document-understanding", "ASR-TTS", "OS-browser-control"}
    )
    assert visualops_payload["safety_rule"] == "observe-first-act-only-with-policy-and-human-approval"
    assert visualops_payload["operator_actions"]["record_visualops_proof"]["endpoint"] == "/ops/brain/canon/answers/current_activity/events"


def test_control_panel_ui_renders_memory_artifact_hardware_and_visualops_scorecards(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Memory Provenance" in ui.text
    assert "memoryProvenanceScorecard" in ui.text
    assert "Artifact Trust" in ui.text
    assert "artifactTrustScorecard" in ui.text
    assert "Hardware Matrix" in ui.text
    assert "hardwareMatrixScorecard" in ui.text
    assert "VisualOps" in ui.text
    assert "visualOpsScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderMemoryProvenanceScorecard" in app_js
    assert "renderArtifactTrustScorecard" in app_js
    assert "renderHardwareMatrixScorecard" in app_js
    assert "renderVisualOpsScorecard" in app_js
    assert "/ops/brain/canon/memory-provenance" in app_js
    assert "/ops/brain/canon/artifact-trust" in app_js
    assert "/ops/brain/canon/hardware-matrix" in app_js
    assert "/ops/brain/canon/visualops" in app_js


def test_governance_observability_scorecard_maps_trace_standards_and_audit_controls(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get(
        "/ops/brain/canon/observability",
        params={"session_id": "observability-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "governance-observability"
    assert payload["required_controls"] == [
        "policy_id",
        "decision_state",
        "allowed_denied_reason",
        "audit_event",
        "redaction_state",
    ]
    assert {"OpenTelemetry-GenAI", "OpenInference", "NexusNet-command-timeline"}.issubset(
        {item["lane_id"] for item in payload["trace_standards"]}
    )
    assert payload["audit_model"]["redaction_rule"] == "redact-private-inputs-before-export"
    assert payload["operator_actions"]["export_audit"]["endpoint"] == "/ops/brain/canon/blackbox"
    assert "/ops/brain/security/permissions" in payload["evidence_refs"]


def test_blackbox_recorder_collects_command_route_policy_memory_eval_artifact_and_scorecards(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "blackbox-session",
            "command_text": "Route a cockpit command through NexusBrain with policy and memory proof.",
            "priority": "critical",
            "target_surface": "mission-control-cockpit",
        },
    ).json()["command"]
    event_response = client.post(
        "/ops/brain/canon/answers/policy_decision/events",
        json={
            "session_id": "blackbox-session",
            "actor": "SecurityAO",
            "detail": "Policy COCKPIT-TRACE-001 allowed cockpit readout and denied raw secret export.",
            "metadata": {"policy_id": "COCKPIT-TRACE-001", "decision": "allow-redacted"},
        },
    )
    assert event_response.status_code == 200

    response = client.get(
        "/ops/brain/canon/blackbox",
        params={"session_id": "blackbox-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["recorder_id"] == "nexusnet-blackbox-recorder"
    assert payload["authority"] == "NexusBrain"
    assert payload["active_command_id"] == command["command_id"]
    frame_ids = {frame["frame_id"] for frame in payload["frames"]}
    assert {
        "command",
        "route",
        "policy",
        "runtime",
        "memory",
        "artifact",
        "eval",
        "protocol",
        "evolution",
        "research",
        "operator-proof",
    }.issubset(frame_ids)
    policy_frame = next(frame for frame in payload["frames"] if frame["frame_id"] == "policy")
    assert policy_frame["state"] == "live-bound"
    assert "/ops/brain/security/permissions" in policy_frame["evidence_refs"]
    assert {"OpenTelemetry-GenAI", "OpenInference"}.issubset(payload["export_contract"]["standard_mappings"])
    assert payload["scorecard_refs"]["runtime"] == "/ops/brain/canon/runtime-scorecard"


def test_control_panel_ui_renders_observability_and_blackbox_recorder(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Governance Observability" in ui.text
    assert "observabilityScorecard" in ui.text
    assert "Black Box Recorder" in ui.text
    assert "blackBoxRecorder" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderObservabilityScorecard" in app_js
    assert "renderBlackBoxRecorder" in app_js
    assert "/ops/brain/canon/observability" in app_js
    assert "/ops/brain/canon/blackbox" in app_js


def test_hive_consensus_scorecard_tracks_central_command_local_reasoning_veto_and_feedback(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "hive-consensus-session",
            "command_text": "Coordinate AO departments and expert mini-brains under NexusBrain command.",
            "priority": "critical",
            "target_surface": "hive-organization",
        },
    ).json()["command"]
    veto = client.post(
        f"/ops/brain/operations/commands/{command['command_id']}/events",
        json={
            "session_id": "hive-consensus-session",
            "event_type": "veto_escalation",
            "actor": "SecurityAO",
            "detail": "Security review required before external tool execution.",
            "lifecycle_state": "blocked",
        },
    )
    assert veto.status_code == 200

    response = client.get(
        "/ops/brain/canon/hive-consensus",
        params={"session_id": "hive-consensus-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["operating_model_id"] == "commanded-collective-hive"
    assert payload["authority"] == "NexusBrain"
    assert payload["active_command_id"] == command["command_id"]
    assert payload["command_chain"][0] == "NexusBrain"
    assert payload["command_chain"][-1] == "NexusBrain"
    assert {"central-command", "local-reasoning", "evidence-consensus", "veto-escalation", "memory-feedback"}.issubset(
        {rule["rule_id"] for rule in payload["consensus_rules"]}
    )
    assert {"ao-hive", "experts-hive", "tools-outputs", "memory-feedback"}.issubset(
        {group["node_id"] for group in payload["mini_brain_groups"]}
    )
    frame_ids = {frame["frame_id"] for frame in payload["signal_frames"]}
    assert {"command_issued", "ao_signal", "expert_signal", "consensus_state", "veto_escalation"}.issubset(frame_ids)
    veto_frame = next(frame for frame in payload["signal_frames"] if frame["frame_id"] == "veto_escalation")
    assert veto_frame["state"] == "live-bound"
    assert veto_frame["consensus_state"] == "escalated"
    assert payload["operator_actions"]["record_veto"]["endpoint"] == f"/ops/brain/operations/commands/{command['command_id']}/events"


def test_control_panel_ui_renders_hive_consensus_scorecard(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Hive Consensus" in ui.text
    assert "hiveConsensusScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderHiveConsensusScorecard" in app_js
    assert "/ops/brain/canon/hive-consensus" in app_js


def test_researcher_swarm_scorecard_maps_multi_agent_research_self_review_and_promotion_loop(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "researcher-swarm-session",
            "command_text": "Research forward-radar candidates and prepare promotion evidence.",
            "priority": "high",
            "target_surface": "forward-radar",
        },
    )
    event_response = client.post(
        "/ops/brain/canon/answers/research_watch/events",
        json={
            "session_id": "researcher-swarm-session",
            "actor": "ResearcherSwarm",
            "detail": "TurboQuant and LMCache remain forward-radar candidates pending benchmark and artifact trust review.",
            "metadata": {"candidate": "TurboQuant", "review_state": "needs-benchmark"},
        },
    )
    assert event_response.status_code == 200

    response = client.get(
        "/ops/brain/canon/researcher-swarm",
        params={"session_id": "researcher-swarm-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "forward-radar"
    assert payload["authority"] == "NexusBrain"
    assert {"horizon-scout", "source-verifier", "benchmarker", "security-reviewer", "integration-planner", "self-reviewer"}.issubset(
        {role["role_id"] for role in payload["research_roles"]}
    )
    assert [stage["stage_id"] for stage in payload["promotion_loop"]] == [
        "discover",
        "verify",
        "simulate",
        "score",
        "propose",
        "operator-approval",
        "promote-or-rollback",
    ]
    assert payload["active_research_watch"]["answer_state"] == "live-bound"
    assert payload["operator_actions"]["queue_candidate"]["endpoint"] == "/ops/brain/canon/realize-next"
    assert payload["operator_actions"]["record_research_proof"]["endpoint"] == "/ops/brain/canon/answers/research_watch/events"


def test_control_panel_ui_renders_researcher_swarm_scorecard(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Researcher Swarm" in ui.text
    assert "researcherSwarmScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderResearcherSwarmScorecard" in app_js
    assert "/ops/brain/canon/researcher-swarm" in app_js


def test_tool_execution_scorecard_maps_registry_sandbox_approval_isolation_and_replay(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get(
        "/ops/brain/canon/tool-execution",
        params={"session_id": "tool-execution-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "tools-execution"
    assert payload["required_controls"] == [
        "tool_registry",
        "sandbox_state",
        "approval_path",
        "failure_capture",
        "runtime_isolation",
        "replay_trace",
    ]
    assert {"tool-registry", "sandbox-policy", "approval-chain", "failure-replay", "runtime-isolation", "extension-permissions"}.issubset(
        {lane["lane_id"] for lane in payload["execution_lanes"]}
    )
    assert payload["safe_execution_rule"] == "tools-execute-only-through-nexusbrain-policy-approval-sandbox-and-replay"
    assert payload["operator_actions"]["inspect_tools"]["endpoint"] == "/ops/brain/extensions"
    assert payload["operator_actions"]["inspect_replay"]["endpoint"] == "/ops/brain/visualizer/replay"

    blackbox = client.get(
        "/ops/brain/canon/blackbox",
        params={"session_id": "tool-execution-session"},
    ).json()
    assert "tool-execution" in {frame["frame_id"] for frame in blackbox["frames"]}
    assert blackbox["scorecard_refs"]["tool_execution"] == "/ops/brain/canon/tool-execution"


def test_control_panel_ui_renders_tool_execution_scorecard(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Tool Execution" in ui.text
    assert "toolExecutionScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderToolExecutionScorecard" in app_js
    assert "/ops/brain/canon/tool-execution" in app_js


def test_ao_hive_scorecard_maps_roles_delegation_context_permissions_and_governance(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "ao-hive-session",
            "command_text": "Have GovernanceAO and CodingAO coordinate an implementation with audit proof.",
            "priority": "critical",
            "target_surface": "ao-hive",
            "context": {"ao": "GovernanceAO"},
        },
    ).json()["command"]

    response = client.get(
        "/ops/brain/canon/ao-hive",
        params={"session_id": "ao-hive-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "ao-hive"
    assert payload["authority"] == "NexusBrain"
    assert payload["active_command_id"] == command["command_id"]
    assert payload["required_controls"] == [
        "role_registry",
        "delegation_status",
        "per_ao_context",
        "model_tool_permissions",
        "governance_constraints",
        "collaboration_state",
    ]
    assert {"PlanningAO", "GovernanceAO", "CodingAO", "RuntimeAO", "EvalsAO"}.issubset(
        {ao["ao_name"] for ao in payload["ao_roster"]}
    )
    governance = next(ao for ao in payload["ao_roster"] if ao["ao_name"] == "GovernanceAO")
    assert governance["risk_tier"] == "high"
    assert governance["reports_to"] == "NexusBrain"
    assert payload["delegation_model"]["selected_ao"] == "GovernanceAO"
    assert payload["operator_actions"]["inspect_aos"]["endpoint"] == "/ops/brain/aos"
    assert payload["operator_actions"]["inspect_hive_consensus"]["endpoint"] == "/ops/brain/canon/hive-consensus"

    blackbox = client.get(
        "/ops/brain/canon/blackbox",
        params={"session_id": "ao-hive-session"},
    ).json()
    assert "ao-hive" in {frame["frame_id"] for frame in blackbox["frames"]}
    assert blackbox["scorecard_refs"]["ao_hive"] == "/ops/brain/canon/ao-hive"


def test_control_panel_ui_renders_ao_hive_scorecard(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "AO Hive Command" in ui.text
    assert "aoHiveScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderAoHiveScorecard" in app_js
    assert "/ops/brain/canon/ao-hive" in app_js


def test_experts_hive_scorecard_maps_domain_mini_brains_signals_routing_and_veto(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "experts-hive-session",
            "command_text": "Route domain experts as mini NexusNet brains under NexusBrain command.",
            "priority": "critical",
            "target_surface": "experts-hive",
        },
    ).json()["command"]

    response = client.get(
        "/ops/brain/canon/experts-hive",
        params={"session_id": "experts-hive-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "experts-hive"
    assert payload["authority"] == "NexusBrain"
    assert payload["active_command_id"] == command["command_id"]
    assert payload["required_controls"] == [
        "domain_roster",
        "mini_nexusnet_per_expert",
        "expert_routing",
        "evidence_response",
        "model_tool_permissions",
        "consensus_signal",
        "veto_escalation",
        "memory_feedback",
    ]
    assert {"Coder Expert", "Security Expert", "Researcher Expert", "Vision Expert"}.issubset(
        {expert["display_name"] for expert in payload["domain_experts"]}
    )
    assert payload["mini_brain_model"]["topology_rule"] == "each-expert-is-a-mini-nexusnet-under-nexusbrain-authority"
    assert payload["routing_model"]["selected_signal_count"] >= 4
    assert payload["operator_actions"]["inspect_core"]["endpoint"] == "/ops/brain/core"
    assert payload["operator_actions"]["inspect_operations"]["endpoint"] == "/ops/brain/operations"
    assert payload["operator_actions"]["inspect_hive_consensus"]["endpoint"] == "/ops/brain/canon/hive-consensus"

    blackbox = client.get(
        "/ops/brain/canon/blackbox",
        params={"session_id": "experts-hive-session"},
    ).json()
    assert "experts-hive" in {frame["frame_id"] for frame in blackbox["frames"]}
    assert blackbox["scorecard_refs"]["experts_hive"] == "/ops/brain/canon/experts-hive"


def test_control_panel_ui_renders_experts_hive_scorecard(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Experts Hive Command" in ui.text
    assert "expertsHiveScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderExpertsHiveScorecard" in app_js
    assert "/ops/brain/canon/experts-hive" in app_js


def test_live_flow_scorecard_correlates_route_model_memory_tool_policy_eval_and_output(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "live-flow-session",
            "command_text": "Trace a full NexusBrain route from command through output proof.",
            "priority": "critical",
            "target_surface": "live-flow-trace",
        },
    ).json()["command"]
    policy = client.post(
        "/ops/brain/canon/answers/policy_decision/events",
        json={
            "session_id": "live-flow-session",
            "actor": "GovernanceAO",
            "detail": "Policy FLOW-TRACE-001 allowed redacted route inspection.",
            "metadata": {"policy_id": "FLOW-TRACE-001", "decision": "allow-read"},
        },
    )
    assert policy.status_code == 200

    response = client.get(
        "/ops/brain/canon/live-flow",
        params={"session_id": "live-flow-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "live-flow-trace"
    assert payload["active_command_id"] == command["command_id"]
    assert payload["required_controls"] == [
        "route_correlation",
        "model_route",
        "memory_route",
        "tool_route",
        "policy_decision",
        "eval_evidence",
        "output_trace",
    ]
    assert {"command", "brain-route", "model", "memory", "tools", "policy", "eval", "output"}.issubset(
        {segment["segment_id"] for segment in payload["trace_segments"]}
    )
    policy_segment = next(segment for segment in payload["trace_segments"] if segment["segment_id"] == "policy")
    assert policy_segment["state"] == "live-bound"
    assert payload["correlation_model"]["correlation_id"] == command["command_id"]
    assert payload["operator_actions"]["inspect_operations"]["endpoint"] == "/ops/brain/operations"
    assert payload["operator_actions"]["inspect_blackbox"]["endpoint"] == "/ops/brain/canon/blackbox"

    blackbox = client.get(
        "/ops/brain/canon/blackbox",
        params={"session_id": "live-flow-session"},
    ).json()
    assert "live-flow" in {frame["frame_id"] for frame in blackbox["frames"]}
    assert blackbox["scorecard_refs"]["live_flow"] == "/ops/brain/canon/live-flow"


def test_neural_core_scorecard_maps_orchestrator_units_authority_policy_and_fallbacks(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "neural-core-session",
            "command_text": "Coordinate the neural core orchestrator and self-check the route.",
            "priority": "critical",
            "target_surface": "neural-core",
        },
    ).json()["command"]

    response = client.get(
        "/ops/brain/canon/neural-core",
        params={"session_id": "neural-core-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "neural-core"
    assert payload["authority"] == "NexusBrain"
    assert payload["active_command_id"] == command["command_id"]
    assert payload["required_controls"] == [
        "brain_authority",
        "route_lock_state",
        "expert_routing",
        "policy_decision",
        "fallback_path",
        "memory_controller",
        "learning_controller",
        "self_check",
    ]
    assert {"intent-router", "context-retriever", "planning-engine", "reasoning-engine", "task-decomposer", "decision-manager", "goal-manager", "memory-controller", "learning-controller", "self-check"}.issubset(
        {unit["unit_id"] for unit in payload["orchestrator_units"]}
    )
    assert payload["fallback_model"]["fallback_rule"] == "degrade-to-safe-static-canon-or-shadow-state-before-bypassing-nexusbrain"
    assert payload["operator_actions"]["inspect_core"]["endpoint"] == "/ops/brain/core"
    assert payload["operator_actions"]["inspect_live_flow"]["endpoint"] == "/ops/brain/canon/live-flow"


def test_control_panel_ui_renders_live_flow_and_neural_core_scorecards(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Flow Correlation" in ui.text
    assert "liveFlowScorecard" in ui.text
    assert "Neural Core Control" in ui.text
    assert "neuralCoreScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderLiveFlowScorecard" in app_js
    assert "renderNeuralCoreScorecard" in app_js
    assert "/ops/brain/canon/live-flow" in app_js
    assert "/ops/brain/canon/neural-core" in app_js


def test_input_ingestion_scorecard_maps_commands_files_notes_snippets_streams_permissions_and_freshness(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    command = client.post(
        "/ops/brain/operations/commands",
        json={
            "session_id": "input-ingestion-session",
            "command_text": "Ingest commands, files, notes, snippets, transcripts, APIs, webhooks, and live streams safely.",
            "priority": "high",
            "target_surface": "input-ingestion",
        },
    ).json()["command"]

    response = client.get(
        "/ops/brain/canon/input-ingestion",
        params={"session_id": "input-ingestion-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "input-ingestion"
    assert payload["authority"] == "NexusBrain"
    assert payload["active_command_id"] == command["command_id"]
    assert payload["required_controls"] == [
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
    ]
    assert {
        "user-commands",
        "uploaded-files",
        "project-notes",
        "code-snippets",
        "meeting-transcripts",
        "external-apis",
        "webhooks-events",
        "realtime-streams",
    }.issubset({lane["lane_id"] for lane in payload["input_lanes"]})
    assert payload["intake_rule"] == "inputs-enter-only-through-source-permission-freshness-redaction-and-command-correlation"
    assert payload["operator_actions"]["inspect_operations"]["endpoint"] == "/ops/brain/operations"
    assert payload["operator_actions"]["inspect_memory"]["endpoint"] == "/ops/brain/canon/memory-provenance"
    assert payload["operator_actions"]["inspect_communication"]["endpoint"] == "/ops/brain/canon/communication-integration"

    blackbox = client.get(
        "/ops/brain/canon/blackbox",
        params={"session_id": "input-ingestion-session"},
    ).json()
    assert "input-ingestion" in {frame["frame_id"] for frame in blackbox["frames"]}
    assert blackbox["scorecard_refs"]["input_ingestion"] == "/ops/brain/canon/input-ingestion"


def test_control_panel_ui_renders_input_ingestion_scorecard(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Input Ingestion" in ui.text
    assert "inputIngestionScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderInputIngestionScorecard" in app_js
    assert "/ops/brain/canon/input-ingestion" in app_js


def test_security_governance_scorecard_maps_permissions_guardrails_audit_privacy_and_rollback(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get(
        "/ops/brain/canon/security-governance",
        params={"session_id": "security-governance-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "governance-observability"
    assert payload["authority"] == "NexusBrain"
    assert payload["required_controls"] == [
        "security_rules",
        "permissions",
        "guardrails",
        "audit_trail",
        "compliance",
        "privacy_controls",
        "rollback_policy",
    ]
    assert {"security-rules", "permissions", "sandbox", "guardrails", "audit-trail", "compliance", "privacy-controls", "rollback-readiness"}.issubset(
        {lane["lane_id"] for lane in payload["security_lanes"]}
    )
    assert payload["security_rule"] == "no-security-sensitive-action-without-policy-permission-audit-redaction-and-rollback"
    assert payload["operator_actions"]["inspect_permissions"]["endpoint"] == "/ops/brain/security/permissions"
    assert payload["operator_actions"]["inspect_guardrails"]["endpoint"] == "/ops/brain/security/guardrails"
    assert payload["operator_actions"]["inspect_audit"]["endpoint"] == "/ops/audit"

    blackbox = client.get(
        "/ops/brain/canon/blackbox",
        params={"session_id": "security-governance-session"},
    ).json()
    assert "security-governance" in {frame["frame_id"] for frame in blackbox["frames"]}
    assert blackbox["scorecard_refs"]["security_governance"] == "/ops/brain/canon/security-governance"


def test_control_panel_ui_renders_security_governance_scorecard(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Security Governance" in ui.text
    assert "securityGovernanceScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderSecurityGovernanceScorecard" in app_js
    assert "/ops/brain/canon/security-governance" in app_js


def test_communication_integration_scorecard_maps_webhooks_bus_events_external_services_and_collab(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get(
        "/ops/brain/canon/communication-integration",
        params={"session_id": "communication-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "communication-integration"
    assert payload["authority"] == "NexusBrain"
    assert payload["required_controls"] == [
        "webhooks",
        "message_bus",
        "event_streams",
        "real_time_sync",
        "external_integrations",
        "notifications",
        "chat_collaboration",
        "protocol_trust",
    ]
    assert {
        "webhooks",
        "message-bus",
        "event-streams",
        "real-time-sync",
        "external-integrations",
        "email-notifications",
        "chat-collaboration",
        "mcp-a2a-acp-agui",
    }.issubset({lane["lane_id"] for lane in payload["integration_lanes"]})
    assert payload["integration_rule"] == "external-communications-remain-consent-permission-trust-envelope-and-revocation-gated"
    assert payload["operator_actions"]["inspect_protocols"]["endpoint"] == "/ops/brain/canon/protocol-trust"
    assert payload["operator_actions"]["inspect_gateway"]["endpoint"] == "/ops/brain/gateway"
    assert payload["operator_actions"]["inspect_extensions"]["endpoint"] == "/ops/brain/extensions"

    blackbox = client.get(
        "/ops/brain/canon/blackbox",
        params={"session_id": "communication-session"},
    ).json()
    assert "communication-integration" in {frame["frame_id"] for frame in blackbox["frames"]}
    assert blackbox["scorecard_refs"]["communication_integration"] == "/ops/brain/canon/communication-integration"


def test_output_delivery_scorecard_maps_deliverables_artifacts_reports_exports_and_feedback(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get(
        "/ops/brain/canon/output-delivery",
        params={"session_id": "output-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "outputs-deliverables"
    assert payload["authority"] == "NexusBrain"
    assert payload["required_controls"] == [
        "architecture_diagrams",
        "implementation_plans",
        "source_code",
        "documentation",
        "roadmaps",
        "reports_analytics",
        "working_artifacts",
        "exports_packages",
        "memory_feedback",
    ]
    assert {
        "architecture-diagrams",
        "implementation-plans",
        "source-code",
        "documentation",
        "roadmaps",
        "reports-analytics",
        "working-artifacts",
        "exports-packages",
        "memory-feedback",
    }.issubset({lane["lane_id"] for lane in payload["delivery_lanes"]})
    assert payload["delivery_rule"] == "outputs-ship-only-with-source-evidence-artifact-trust-memory-feedback-and-replayable-proof"
    assert payload["operator_actions"]["inspect_artifacts"]["endpoint"] == "/ops/brain/canon/artifact-trust"
    assert payload["operator_actions"]["inspect_blackbox"]["endpoint"] == "/ops/brain/canon/blackbox"
    assert payload["operator_actions"]["inspect_completion"]["endpoint"] == "/ops/brain/canon/completion"

    blackbox = client.get(
        "/ops/brain/canon/blackbox",
        params={"session_id": "output-session"},
    ).json()
    assert "output-delivery" in {frame["frame_id"] for frame in blackbox["frames"]}
    assert blackbox["scorecard_refs"]["output_delivery"] == "/ops/brain/canon/output-delivery"


def test_control_panel_ui_renders_communication_and_output_delivery_scorecards(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")

    assert ui.status_code == 200
    assert "Communication Integration" in ui.text
    assert "communicationIntegrationScorecard" in ui.text
    assert "Output Delivery" in ui.text
    assert "outputDeliveryScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderCommunicationIntegrationScorecard" in app_js
    assert "renderOutputDeliveryScorecard" in app_js
    assert "/ops/brain/canon/communication-integration" in app_js
    assert "/ops/brain/canon/output-delivery" in app_js
