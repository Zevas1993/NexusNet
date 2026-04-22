from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from nexusnet.schemas import ModelAttachRequest, SessionContext
from tests.test_nexus_phase1_foundation import make_project


def test_teacher_registry_and_memory_plane_projection(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    attached = services.brain_teachers.attach(
        services.brain,
        ModelAttachRequest(teacher_id="mixtral-8x7b", set_active=True),
    )
    assert attached.teacher_id == "mixtral-8x7b"
    assert services.brain_teachers.active_teacher() is not None

    result = services.brain.generate(
        session_context=SessionContext(session_id="surface-session", expert="researcher", use_retrieval=False),
        prompt="Explain why NexusNet keeps teacher provenance visible.",
        model_hint=attached.model_id,
    )
    assert result.output

    projection = services.brain_ui_surface.projection("surface-session", "temporal")
    assert projection["projection_name"] == "temporal"
    assert projection["grouped_records"]

    planes = services.brain_memory_planes.metadata()
    assert planes["status_label"] == "UNRESOLVED CONFLICT"
    assert "legacy_plane_map" in planes


def test_wrapper_surface_and_brain_api_endpoints(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    attach = client.post("/ops/brain/teachers/attach", json={"teacher_id": "mixtral-8x7b", "set_active": True})
    assert attach.status_code == 200
    attached = attach.json()
    assert attached["teacher_id"] == "mixtral-8x7b"

    wrapper = client.get("/ops/brain/wrapper-surface", params={"session_id": "api-surface"})
    assert wrapper.status_code == 200
    wrapper_payload = wrapper.json()
    assert wrapper_payload["state"]["active_teacher_id"] == "mixtral-8x7b"
    assert any(mode["mode_id"] == "openclaw" for mode in wrapper_payload["state"]["modes"])

    aos = client.get("/ops/brain/aos")
    assert aos.status_code == 200
    assert any(ao["name"] == "DreamAO" for ao in aos.json()["active_aos"])

    memory_planes = client.get("/ops/brain/memory/planes")
    assert memory_planes.status_code == 200
    assert memory_planes.json()["metadata"]["status_label"] == "UNRESOLVED CONFLICT"

    runtime = client.get("/ops/brain/runtime-profile")
    assert runtime.status_code == 200
    runtime_payload = runtime.json()
    assert "device_profile" in runtime_payload
    assert runtime_payload["token_budget_profile"]["summary_fraction"] == 0.5

    chat = client.post(
        "/chat",
        json={
            "session_id": "api-surface",
            "message": "Use the wrapper surface to explain why teacher traces matter.",
            "teacher_id": "mixtral-8x7b",
            "wrapper_mode": "openclaw",
            "rag": False,
        },
    )
    assert chat.status_code == 200
    payload = chat.json()
    assert payload["teacher_id"] == "mixtral-8x7b"
    assert payload["wrapper_mode"] == "openclaw"
    assert payload["trace"]["selected_teacher_id"] == "mixtral-8x7b"

    projection = client.get("/ops/brain/memory/projections/temporal", params={"session_id": "api-surface"})
    assert projection.status_code == 200
    assert projection.json()["grouped_records"]

    eval_report = client.get("/ops/brain/evals/report")
    assert eval_report.status_code == 200
    report_payload = eval_report.json()
    assert Path(report_payload["artifacts"]["report"]).exists()
