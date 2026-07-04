from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_developmental_cortex_endpoint_returns_live_subsurfaces(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/canon/developmental-cortex")
    assert response.status_code == 200
    payload = response.json()
    assert payload["surface_id"] == "developmental-cortex-kernel"
    assert payload["authority"] == "NexusBrain"
    assert payload["production_mutation_allowed"] is False
    # Live sub-surface summaries are present, not just static labels.
    subsurfaces = payload["subsurfaces"]
    assert subsurfaces["body_schema"]["surface_id"] == "nexus-body-schema"
    assert subsurfaces["reference_frames"]["surface_id"] == "reference-frame-store"
    assert subsurfaces["promotion_tribunal"]["surface_id"] == "promotion-tribunal"


def test_developmental_cortex_assess_records_shadow_packet(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/developmental-cortex/assess",
        json={
            "request_id": "dev:req:cp-001",
            "task_ref": "task:improve-routing",
            "trace_refs": ["trace:route-1"],
            "evidence_refs": ["eval:route-shadow"],
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "shadow-ready"
    assert result["production_mutation_allowed"] is False
    assert result["promotion_case"]["decision"] == "accepted-shadow"

    # The new packet is now visible through the live scorecard.
    scorecard = client.get("/ops/brain/canon/developmental-cortex").json()
    assert scorecard["assessment_count"] >= 1


def test_control_panel_developmental_cortex_scorecard_is_live(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    state = client.get("/ops/brain/visualizer/state", params={"session_id": "dev-cortex-live"})
    control_panel = state.json()["overlay_state"]["control_panel"]
    scorecard = control_panel["developmental_cortex_scorecard"]
    assert scorecard["surface_id"] == "developmental-cortex-kernel"
    assert scorecard["production_mutation_allowed"] is False
    assert scorecard["subsurfaces"]["body_schema"]["surface_id"] == "nexus-body-schema"
