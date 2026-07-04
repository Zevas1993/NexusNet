from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.agents.opportunity_discovery import AgentOpportunityDiscovery, AgentOpportunityRequest, WorkActivityRequest
from tests.test_nexus_phase1_foundation import make_project


def test_agent_opportunity_discovery_classifies_backstage_and_no_go_work():
    discovery = AgentOpportunityDiscovery()

    summary = discovery.discover(
        AgentOpportunityRequest(
            activities=[
                WorkActivityRequest(
                    activity_id="weekly-report",
                    title="Weekly KPI report",
                    description="Pull numbers from CRM and spreadsheets, format, and post Monday status.",
                    repetitive=True,
                    rule_based=True,
                    high_volume=True,
                    low_judgment=True,
                    hours_per_week=6.0,
                    systems=["crm", "spreadsheet", "slack"],
                    measurable_outcome="report-posted-by-monday",
                    self_contained=True,
                    error_recovery=True,
                ),
                WorkActivityRequest(
                    activity_id="hard-client-call",
                    title="Difficult customer relationship call",
                    description="Repair trust after a missed delivery.",
                    frontstage=True,
                    no_go_zone=True,
                    requires_relationship=True,
                    requires_empathy=True,
                    hours_per_week=1.0,
                    systems=["calendar"],
                ),
                WorkActivityRequest(
                    activity_id="incident-root-cause",
                    title="Safety incident root-cause prep",
                    description="Collect evidence before a high-judgment safety decision.",
                    repetitive=False,
                    rule_based=False,
                    high_volume=False,
                    low_judgment=False,
                    requires_judgment=True,
                    prep_hours_per_week=5.0,
                    judgment_hours_per_week=1.0,
                    systems=["docs", "tickets"],
                    evidence_refs=["incident::123"],
                    measurable_outcome="decision-brief-ready",
                ),
            ]
        )
    )

    assert summary["status_label"] == "LOCKED CANON"
    assert summary["opportunity_count"] == 2
    assert summary["no_go_count"] == 1
    assert summary["total_reclaimable_hours_per_week"] == 11.0

    automation = next(item for item in summary["opportunities"] if item["activity_id"] == "weekly-report")
    assert automation["aaa_layer"] == "automation"
    assert automation["agent_title"] == "Weekly KPI Report Agent"
    assert "human_review_for_external_commitments" in automation["boundaries"]
    assert "report-posted-by-monday" in automation["success_metrics"]

    augmentation = next(item for item in summary["opportunities"] if item["activity_id"] == "incident-root-cause")
    assert augmentation["aaa_layer"] == "augmentation"
    assert augmentation["human_role"] == "decision_owner"

    blocked = summary["no_go_zones"][0]
    assert blocked["activity_id"] == "hard-client-call"
    assert blocked["automation_allowed"] is False


def test_agent_opportunity_discovery_blocks_build_readiness_from_forward_radar_gate():
    discovery = AgentOpportunityDiscovery()

    summary = discovery.discover(
        {
            "activities": [
                {
                    "activity_id": "agent-router-autonomy",
                    "title": "Agent router autonomy",
                    "description": "Let an agent route and repair failed tool-use jobs without operator intervention.",
                    "repetitive": True,
                    "rule_based": True,
                    "high_volume": True,
                    "low_judgment": True,
                    "self_contained": True,
                    "error_recovery": True,
                    "hours_per_week": 7,
                    "systems": ["tools", "evals", "control-panel"],
                    "measurable_outcome": "tool-jobs-auto-recovered",
                    "metadata": {"autonomy_candidate": True},
                }
            ],
            "upstream_forward_radar_gate": {
                "promotion_allowed": False,
                "status": "blocked",
                "radar_id": "radar::blocked-harness-router",
                "blockers": ["forward_radar_blocks_harness_ledger_gate"],
            },
        }
    )

    opportunity = summary["opportunities"][0]
    assert opportunity["aaa_layer"] == "autonomy"
    assert opportunity["ready_for_agent_build"] is False
    assert opportunity["opportunity_gate_state"] == "blocked-by-forward-radar"
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_opportunity_count"] == 1
    assert "forward_radar_blocks_harness_ledger_gate" in summary["upstream_forward_radar_gate"]["blockers"]


def test_agent_opportunity_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/agent-opportunities/discover",
        json={
            "activities": [
                {
                    "activity_id": "lead-triage",
                    "title": "Inbound lead triage",
                    "description": "Score inbound leads, draft next step, and flag owner.",
                    "repetitive": True,
                    "rule_based": True,
                    "high_volume": True,
                    "low_judgment": True,
                    "hours_per_week": 8,
                    "systems": ["email", "crm", "slack"],
                    "measurable_outcome": "qualified-lead-routed",
                    "self_contained": True,
                    "error_recovery": True,
                }
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["opportunities"][0]["aaa_layer"] in {"automation", "autonomy"}

    summary = client.get("/ops/brain/agent-opportunities")
    assert summary.status_code == 200
    assert summary.json()["opportunity_count"] == 1

    scorecard = client.get("/ops/brain/canon/agent-opportunities")
    assert scorecard.status_code == 200
    assert scorecard.json()["operator_actions"]["discover"]["endpoint"] == "/ops/brain/agent-opportunities/discover"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "agent-opportunity-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["agent_opportunity_scorecard"]["surface_id"] == "agent-opportunity-discovery"

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "agent-opportunity-cockpit"}).json()
    assert blackbox["scorecard_refs"]["agent_opportunities"] == "/ops/brain/canon/agent-opportunities"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Agent Opportunity Discovery" in ui.text
    assert "agentOpportunityScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderAgentOpportunityScorecard" in app_js
    assert "/ops/brain/canon/agent-opportunities" in app_js
    opportunity_renderer = app_js[
        app_js.index("function renderAgentOpportunityScorecard"):
        app_js.index("function renderHarnessProviderScorecard")
    ]
    assert "upstream forward radar gate" in opportunity_renderer
    assert "upstream_forward_radar_gate" in opportunity_renderer
