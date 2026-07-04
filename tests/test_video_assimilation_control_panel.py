from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_video_assimilation_surfaces_are_visible_in_control_panel(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Video Assimilation" in ui.text
    assert "videoAssimilationScorecard" in ui.text
    assert "retrievalPlannerScorecard" in ui.text
    assert "operatorEventsScorecard" in ui.text
    assert "conceptTelemetryScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "/ops/brain/canon/video-assimilation-targets" in app_js
    assert "/ops/brain/retrieval/planner" in app_js
    assert "/ops/brain/operator-events" in app_js
    assert "/ops/brain/concept-telemetry" in app_js
    assert "renderVideoAssimilationScorecard" in app_js


def test_visualizer_overlay_contains_new_assimilation_scorecards(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "video-assimilation-ui"})

    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert "video_assimilation_scorecard" in control_panel
    assert "retrieval_planner_scorecard" in control_panel
    assert "codegraph_gate_scorecard" in control_panel
