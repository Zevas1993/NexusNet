from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_goose_recipe_and_runbook_catalogs_surface_in_wrapper_and_visualizer(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    recipes = client.get("/ops/brain/recipes")
    assert recipes.status_code == 200
    recipes_json = recipes.json()
    assert recipes_json["recipe_count"] >= 2
    assert recipes_json["runbook_count"] >= 1
    assert recipes_json["validation"]["ok"] is True

    runbooks = client.get("/ops/brain/runbooks")
    assert runbooks.status_code == 200
    assert runbooks.json()["runbook_count"] >= 1

    wrapper = client.get("/ops/brain/wrapper-surface")
    assert wrapper.status_code == 200
    goose = wrapper.json()["assimilation"]["goose"]
    assert goose["recipes"]["recipe_count"] >= 2
    assert goose["recipes"]["schedule_compatible_ids"]
    assert wrapper.json()["assimilation"]["compare_refs"]["goose_recipes"] == "/ops/brain/recipes"

    visualizer = client.get("/ops/brain/visualizer/state")
    assert visualizer.status_code == 200
    runtime_posture = visualizer.json()["overlay_state"]["runtime_posture"]
    assert runtime_posture["goose_recipe_count"] >= 2
    assert runtime_posture["goose_runbook_count"] >= 1


def test_goose_security_lane_fails_closed_or_escalates_and_surfaces_state(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    review = client.post(
        "/ops/brain/security/adversary-review",
        json={
            "subject": "high-risk-shell-path",
            "requested_tools": ["shell.exec"],
            "risk_level": "high",
            "reviewer_status": "unavailable",
        },
    )
    assert review.status_code == 200
    review_json = review.json()
    assert review_json["fail_open_allowed"] is False
    assert review_json["decision"] in {"deny", "escalate"}
    assert Path(review_json["artifact_path"]).exists()

    permissions = client.get("/ops/brain/security/permissions")
    assert permissions.status_code == 200
    assert permissions.json()["active_mode"]["mode_id"] == "workspace-write"

    sandbox = client.get("/ops/brain/security/sandbox")
    assert sandbox.status_code == 200
    assert sandbox.json()["active_profile"]["profile_id"] == "workspace-write"

    gateway = client.get("/ops/brain/gateway")
    assert gateway.status_code == 200
    gateway_json = gateway.json()
    assert gateway_json["permissions"]["active_mode"]["mode_id"] == "workspace-write"
    assert gateway_json["persistent_guardrails"]["enabled_guardrail_count"] >= 1

    visualizer = client.get("/ops/brain/visualizer/state")
    runtime_posture = visualizer.json()["overlay_state"]["runtime_posture"]
    assert runtime_posture["goose_latest_adversary_review_id"] == review_json["review_id"]
    assert runtime_posture["goose_latest_adversary_decision"] == review_json["decision"]


def test_goose_subagents_extensions_and_acp_stay_bounded_and_read_only(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    extensions = client.get("/ops/brain/extensions")
    assert extensions.status_code == 200
    extensions_json = extensions.json()
    assert extensions_json["extension_count"] >= 2
    assert extensions_json["mcp_compatible_count"] >= 1

    acp = client.get("/ops/brain/acp")
    assert acp.status_code == 200
    acp_json = acp.json()
    assert acp_json["provider_count"] >= 1
    assert acp_json["enabled"] is False

    plan = client.post(
        "/ops/brain/subagents/plan",
        json={"recipe_id": "ao-deep-research", "parent_task": "Investigate graph-aware citations", "mode": "parallel"},
    )
    assert plan.status_code == 200
    plan_json = plan.json()
    execution = plan_json["execution"]
    assert execution["temporary_lifecycle"] is True
    assert execution["governance_mutation_allowed"] is False
    assert execution["workers"]
    assert Path(execution["artifact_path"]).exists()

    wrapper = client.get("/ops/brain/wrapper-surface")
    goose = wrapper.json()["goose"]
    assert goose["extensions"]["extension_count"] >= 2
    assert goose["acp"]["provider_count"] >= 1
    assert goose["subagents"]["recent_run_count"] >= 1

    visualizer = client.get("/ops/brain/visualizer/state")
    runtime_posture = visualizer.json()["overlay_state"]["runtime_posture"]
    assert runtime_posture["goose_subagent_run_count"] >= 1
    assert runtime_posture["goose_acp_provider_count"] >= 1
