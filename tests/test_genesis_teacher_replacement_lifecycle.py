from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_layer13_distillation_records_shadow_teacher_replacement_recommendation_and_replays(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    curriculum = client.post(
        "/ops/brain/curriculum/assess",
        json={"phase": "graduate", "subject": "toolsmith", "model_hint": "mock/default"},
    )
    assert curriculum.status_code == 200

    distill = client.post(
        "/ops/brain/distill-dataset",
        json={
            "name": "layer13-replacement-lifecycle",
            "trace_limit": 20,
            "include_dreams": True,
            "include_curriculum": True,
        },
    )
    assert distill.status_code == 200
    recommendation = distill.json()["teacher_replacement_recommendation"]
    assert recommendation["status"] == "replacement-recommended-shadow"
    assert recommendation["archive_not_delete"] is True
    assert recommendation["rollback_required"] is True
    assert recommendation["admin_approval_required"] is True
    assert recommendation["active_teacher_retired"] is False
    assert recommendation["raw_content_included"] is False

    governance = client.get("/ops/brain/genesis-teacher-governance").json()
    assert governance["teacher_replacement_recommendation_count"] == 1
    assert governance["latest_teacher_replacement_recommendation"]["recommendation_id"] == recommendation["recommendation_id"]

    visualizer = client.get("/ops/brain/visualizer/state").json()
    ao_hive = next(
        page
        for page in visualizer["overlay_state"]["control_panel"]["pages"]
        if page["page_id"] == "ao-hive"
    )
    assert ao_hive["metrics"]["teacher_replacement_recommendation_count"] == 1

    replay = TestClient(create_app(str(project_root))).get("/ops/brain/genesis-teacher-governance").json()
    assert replay["teacher_replacement_recommendation_count"] == 1
    assert replay["latest_teacher_replacement_recommendation"]["archive_not_delete"] is True
