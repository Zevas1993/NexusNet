from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.agents.harnesses import HarnessModelRouter, HarnessRouteRequest
from tests.test_nexus_phase1_foundation import make_project


def test_harness_model_router_prefers_cheap_proxy_only_for_public_low_risk_work():
    router = HarnessModelRouter.default()

    decision = router.recommend(
        HarnessRouteRequest(
            task_type="unit_tests",
            data_sensitivity="public",
            requires_tool_use=True,
            cost_priority=True,
        )
    )

    assert decision["status_label"] == "LOCKED CANON"
    assert decision["decision"] == "allow"
    assert decision["selected_route"]["route_id"] == "cheap-tool-coding-proxy"
    assert "deepseek-anthropic-api" in decision["selected_route"]["backend_candidates"]
    assert "no_raw_logging" in decision["required_controls"]
    assert "credential_vault_boundary" in decision["required_controls"]
    assert decision["security_findings"] == []


def test_harness_model_router_keeps_private_or_ui_authority_out_of_cheap_proxy():
    router = HarnessModelRouter.default()

    confidential = router.recommend(
        {
            "task_type": "backend_coding",
            "data_sensitivity": "confidential",
            "requires_tool_use": True,
            "cost_priority": True,
        }
    )
    assert confidential["decision"] == "allow"
    assert confidential["selected_route"]["route_id"] == "local-nexus-code-harness"
    assert confidential["selected_route"]["privacy_posture"] == "local-first"
    assert "external_proxy_data_boundary" in confidential["security_findings"]

    design = router.recommend(
        {
            "task_type": "ui_design",
            "data_sensitivity": "public",
            "requires_ui_taste": True,
            "cost_priority": True,
        }
    )
    assert design["selected_route"]["role"] == "design_authority"
    assert "cheap_model_style_extension_only" in design["caveats"]
    assert design["selected_route"]["route_id"] != "cheap-tool-coding-proxy"


def test_harness_model_router_blocks_recommendation_from_upstream_aitune_gate():
    router = HarnessModelRouter.default()

    decision = router.recommend(
        HarnessRouteRequest(
            task_type="unit_tests",
            data_sensitivity="public",
            requires_tool_use=True,
            cost_priority=True,
            upstream_aitune_gate={
                "status": "blocked-upstream-gate",
                "can_execute_here": False,
                "readiness_blockers": ["harness_runtime_not_validated"],
            },
        )
    )

    assert decision["selected_route"]["route_id"] == "cheap-tool-coding-proxy"
    assert decision["decision"] == "blocked"
    assert decision["runtime_state"] == "degraded"
    assert decision["upstream_aitune_gate"]["blockers"] == ["harness_runtime_not_validated"]
    assert "upstream_aitune_gate_blocked" in decision["reason_codes"]
    assert "router_alignment_blocks_upstream_aitune_gate" in decision["blocked_reasons"]
    assert decision["policy_scan"]["summary"]["allow_merge"] is False


def test_harness_routing_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    summary = client.get("/ops/brain/harness-routing")
    assert summary.status_code == 200
    summary_payload = summary.json()
    assert summary_payload["route_count"] >= 4
    assert "dangerously_skip_permissions_blocked" in summary_payload["security_rules"]

    recommendation = client.post(
        "/ops/brain/harness-routing/recommend",
        json={
            "task_type": "code_review",
            "data_sensitivity": "internal",
            "requires_code_review": True,
        },
    )
    assert recommendation.status_code == 200
    assert recommendation.json()["selected_route"]["role"] == "independent_reviewer"

    blocked = client.post(
        "/ops/brain/harness-routing/recommend",
        json={
            "task_type": "backend_coding",
            "data_sensitivity": "public",
            "dangerously_skip_permissions": True,
        },
    )
    assert blocked.status_code == 200
    assert blocked.json()["decision"] == "blocked"
    assert "dangerously_skip_permissions_blocked" in blocked.json()["blocked_reasons"]

    scorecard = client.get("/ops/brain/canon/harness-routing")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "degraded"
    assert scorecard_payload["blocked_count"] == 1
    assert scorecard_payload["latest_recommendation"]["decision"] == "blocked"
    assert scorecard_payload["operator_actions"]["recommend"]["endpoint"] == "/ops/brain/harness-routing/recommend"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "harness-routing-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["harness_routing_scorecard"]["route_count"] >= 4
    assert control_panel["harness_routing_scorecard"]["runtime_state"] == "degraded"

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "harness-routing-cockpit"}).json()
    assert blackbox["scorecard_refs"]["harness_routing"] == "/ops/brain/canon/harness-routing"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Harness Model Router" in ui.text
    assert "harnessRoutingScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderHarnessRoutingScorecard" in app_js
    assert "/ops/brain/canon/harness-routing" in app_js
