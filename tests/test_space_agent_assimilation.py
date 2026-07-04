from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


SPACE_AGENT_URL = "https://github.com/agent0ai/space-agent"
SPACE_AGENT_COMMIT = "1289793bab727a46e62365992a65ffb3476c4091"


def test_space_agent_review_records_clean_room_assimilation_targets(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/assimilation/space-agent/review",
        json={
            "source_url": SPACE_AGENT_URL,
            "commit_sha": SPACE_AGENT_COMMIT,
            "license_posture": "declared:MIT",
            "observed_patterns": [
                "registered_browser_surfaces",
                "hierarchical_agents_skills",
                "workspace_spaces_widgets",
                "customware_layers",
                "git_backed_time_travel",
                "browser_local_inference",
                "plain_text_javascript_actions",
            ],
            "evidence": {
                "readme": "browser-first runtime with skills and runtime UI",
                "docs": "registered browser surfaces, layered customware, spaces/widgets, time travel",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    review = payload["review"]
    candidate = payload["assimilation_candidate"]

    assert review["review_id"].startswith("spaceagent_")
    assert review["status"] == "reviewed_metadata_only"
    assert review["source"]["source_url"] == SPACE_AGENT_URL
    assert review["source"]["commit_sha"] == SPACE_AGENT_COMMIT
    assert review["direct_code_adoption_allowed"] is False
    assert review["copy_source_assets_prompts_allowed"] is False
    assert review["execution_allowed"] is False
    assert review["mutation_allowed"] is False
    assert review["policy_path"][0]["decision"] == "hold"
    assert review["approval_path"]["decision"] == "not_requested"
    assert Path(review["artifact_path"]).exists()

    targets = {item["nexusnet_target"] for item in review["recommended_assimilations"]}
    assert {
        "ui_surface.browser_surface_registry",
        "tools.context_gated_skill_catalog",
        "ui_surface.workspace_widget_runtime",
        "package_candidates.layered_workspace_overlay",
        "memory_governance.layered_time_travel",
        "runtime.browser_local_inference_scorecards",
    } <= targets

    script_action = next(item for item in review["recommended_assimilations"] if item["pattern"] == "plain_text_javascript_actions")
    assert script_action["governance_posture"] == "deny_by_default_script_execution"
    assert "browser_surface_data_egress" in review["risk_flags"]
    assert "operator-surface-truthfulness" in review["product_sweep_gate_ids"]
    assert "extension-provenance-gate" in review["product_sweep_gate_ids"]

    assert candidate["category"] == "operator_ux"
    assert candidate["source_name"] == "Space Agent"
    assert candidate["target_subsystem"] == "ui_surface"
    assert candidate["scorecard"]["source_assimilated_as_pattern"] is True
    assert candidate["scorecard"]["execution_allowed"] is False
    assert candidate["scorecard"]["mutation_allowed"] is False

    status = client.get("/ops/brain/assimilation/status")
    assert status.status_code == 200
    status_json = status.json()
    assert "space_agent_assimilation" in status_json
    assert status_json["space_agent_assimilation"]["review_count"] == 1
    assert status_json["space_agent_assimilation"]["latest_review"]["source"]["source_url"] == SPACE_AGENT_URL

    product = client.get("/ops/brain/product-sweep/status")
    assert product.status_code == 200
    surface = product.json()["status_surfaces"]["space_agent_assimilation"]
    assert surface["review_count"] == 1
    assert surface["direct_code_adoption_allowed"] is False
    assert surface["mutation_allowed"] is False

    events = client.get("/ops/brain/events", params={"subject_prefix": "assimilation:space-agent", "limit": 10})
    assert events.status_code == 200
    assert events.json()["event_type_counts"]["assimilation.space_agent_reviewed"] >= 1
