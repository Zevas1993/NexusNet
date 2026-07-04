from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.vision.computer_use import ComputerUsePlanRequest, MultimodalComputerUseController
from tests.test_nexus_phase1_foundation import make_project


def test_multimodal_computer_use_plans_private_screen_document_audio_as_shadow_local_work():
    controller = MultimodalComputerUseController()

    plan = controller.plan(
        ComputerUsePlanRequest(
            plan_id="computer-use::operator-cockpit",
            session_id="session::cockpit",
            user_goal="Read the current browser page, extract document facts, transcribe the audio note, then propose safe next steps.",
            input_modalities=["screenshot", "document", "audio"],
            requested_tasks=["screen_agent", "ocr", "vlm_route", "document_understanding", "asr"],
            contains_private_data=True,
            permission_scope="operator-approved-local",
            sandbox_mode="shadow",
            local_only=True,
            allow_cloud=False,
            evidence_refs=["operator-consent::session::cockpit"],
            hardware_snapshot={
                "local_cpu": True,
                "local_gpu": True,
                "local_gpu_vram_gb": 24,
                "browser_webgpu": True,
            },
        )
    )

    assert plan["status_label"] == "LOCKED CANON"
    assert plan["authority"] == "NexusBrain"
    assert plan["surface_id"] == "multimodal-computer-use"
    assert plan["status"] == "planned-shadow"
    assert plan["execution_boundary"] == "observe-first-act-only-with-policy-human-confirmation"
    assert plan["route_decision"]["selected_lane_id"] in {"local-gpu", "browser-webgpu-webnn", "local-cpu"}
    assert plan["policy_scan"]["summary"]["allow_merge"] is True
    assert {
        "screen_capture_consent",
        "ocr_vlm_grounding",
        "asr_tts_boundary",
        "document_understanding",
        "os_browser_control_sandbox",
        "privacy_redaction",
        "trace_replay",
    }.issubset(set(plan["required_controls"]))
    assert {"screen-agents", "OCR", "VLM-routing", "document-understanding", "ASR-TTS"}.issubset(
        {lane["lane_id"] for lane in plan["lanes"]}
    )


def test_multimodal_computer_use_blocks_control_without_consent_or_sandbox():
    controller = MultimodalComputerUseController()

    plan = controller.plan(
        {
            "plan_id": "computer-use::unsafe-control",
            "session_id": "session::unsafe",
            "user_goal": "Click through the browser and change system settings.",
            "input_modalities": ["screenshot", "browser_page"],
            "requested_tasks": ["screen_agent", "browser_control", "os_control"],
            "contains_private_data": True,
            "permission_scope": "none",
            "sandbox_mode": "none",
            "local_only": False,
            "allow_cloud": True,
            "evidence_refs": [],
            "hardware_snapshot": {"local_cpu": True},
        }
    )

    assert plan["status"] == "blocked"
    assert plan["policy_scan"]["summary"]["allow_merge"] is False
    assert {
        "computer_use_requires_operator_permission",
        "computer_use_control_requires_sandbox",
        "private_multimodal_context_requires_local_only",
        "private_multimodal_context_blocks_cloud_export",
    }.issubset({finding["rule_id"] for finding in plan["safety_findings"]})


def test_multimodal_computer_use_blocks_plan_from_upstream_aitune_gate():
    controller = MultimodalComputerUseController()

    plan = controller.plan(
        ComputerUsePlanRequest(
            plan_id="computer-use::upstream-runtime-blocked",
            session_id="session::upstream-blocked",
            user_goal="Inspect a screenshot locally only when runtime evidence is validated.",
            input_modalities=["screenshot"],
            requested_tasks=["screen_agent", "vlm_route"],
            contains_private_data=False,
            permission_scope="public-demo",
            sandbox_mode="shadow",
            local_only=True,
            allow_cloud=False,
            hardware_snapshot={"local_cpu": True, "browser_webgpu": True},
            upstream_aitune_gate={
                "status": "blocked-upstream-gate",
                "can_execute_here": False,
                "readiness_blockers": ["computer_use_runtime_not_validated"],
            },
        )
    )

    assert plan["status"] == "blocked-upstream-gate"
    assert plan["runtime_state"] == "degraded"
    assert plan["upstream_aitune_gate"]["blockers"] == ["computer_use_runtime_not_validated"]
    assert plan["route_decision"]["status"] == "blocked-upstream-gate"
    assert "upstream_aitune_gate_blocked" in plan["route_decision"]["reason_codes"]
    assert plan["policy_scan"]["summary"]["allow_merge"] is False

    summary = controller.summary()
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_count"] == 1


def test_multimodal_computer_use_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/multimodal-computer-use/plans",
        json={
            "plan_id": "computer-use::api-safe-shadow",
            "session_id": "session::api-shadow",
            "user_goal": "Inspect a screenshot and document locally before proposing a browser action.",
            "input_modalities": ["screenshot", "document"],
            "requested_tasks": ["screen_agent", "ocr", "document_understanding", "browser_control"],
            "contains_private_data": True,
            "permission_scope": "operator-approved-local",
            "sandbox_mode": "shadow",
            "local_only": True,
            "allow_cloud": False,
            "evidence_refs": ["operator-consent::api-shadow"],
            "hardware_snapshot": {"local_cpu": True, "browser_webgpu": True},
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "planned-shadow"

    summary = client.get("/ops/brain/multimodal-computer-use")
    assert summary.status_code == 200
    assert summary.json()["plan_count"] == 1

    scorecard = client.get("/ops/brain/canon/multimodal-computer-use")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["plan"]["endpoint"] == "/ops/brain/multimodal-computer-use/plans"
    assert {"OSWorld", "BrowserGym-WebArena", "screen-agents", "local-browser-agent"}.issubset(
        {lane["lane_id"] for lane in scorecard_payload["research_lanes"]}
    )

    blocked = client.post(
        "/ops/brain/multimodal-computer-use/plans",
        json={
            "plan_id": "computer-use::api-upstream-runtime-blocked",
            "session_id": "session::api-upstream-blocked",
            "user_goal": "Inspect a screenshot locally only after runtime validation.",
            "input_modalities": ["screenshot"],
            "requested_tasks": ["screen_agent", "vlm_route"],
            "contains_private_data": False,
            "permission_scope": "public-demo",
            "sandbox_mode": "shadow",
            "local_only": True,
            "allow_cloud": False,
            "hardware_snapshot": {"local_cpu": True, "browser_webgpu": True},
            "upstream_aitune_gate": {
                "status": "blocked-upstream-gate",
                "can_execute_here": False,
                "readiness_blockers": ["computer_use_runtime_not_validated"],
            },
        },
    )
    assert blocked.status_code == 200
    assert blocked.json()["status"] == "blocked-upstream-gate"

    degraded_scorecard = client.get("/ops/brain/canon/multimodal-computer-use")
    assert degraded_scorecard.status_code == 200
    degraded_payload = degraded_scorecard.json()
    assert degraded_payload["runtime_state"] == "degraded"
    assert degraded_payload["blocked_count"] == 1
    assert degraded_payload["latest_plan"]["status"] == "blocked-upstream-gate"

    safety_cases = client.get("/ops/brain/computer-use/safety-cases")
    assert safety_cases.status_code == 200
    safety_payload = safety_cases.json()
    assert safety_payload["surface_id"] == "multimodal-computer-use"
    assert safety_payload["case_count"] >= 5
    assert "screen_capture_consent" in {case["case_id"] for case in safety_payload["safety_cases"]}
    assert "private_cloud_export_block" in {case["case_id"] for case in safety_payload["safety_cases"]}
    assert safety_payload["operator_actions"]["plan"]["endpoint"] == "/ops/brain/multimodal-computer-use/plans"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "computer-use-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["multimodal_computer_use_scorecard"]["runtime_state"] == "degraded"
    assert control_panel["multimodal_computer_use_scorecard"]["plan_count"] == 2

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "computer-use-cockpit"}).json()
    assert blackbox["scorecard_refs"]["multimodal_computer_use"] == "/ops/brain/canon/multimodal-computer-use"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Multimodal Computer Use" in ui.text
    assert "multimodalComputerUseScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderMultimodalComputerUseScorecard" in app_js
    assert "/ops/brain/canon/multimodal-computer-use" in app_js
