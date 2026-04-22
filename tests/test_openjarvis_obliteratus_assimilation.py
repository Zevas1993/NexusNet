from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_openjarvis_runtime_doctor_and_skill_catalog_are_read_only_and_local_first(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    init_payload = client.get("/ops/brain/runtime/init")
    assert init_payload.status_code == 200
    init_json = init_payload.json()
    assert init_json["local_first_default"] is True
    assert len(init_json["preset_catalog"]) >= 4
    assert init_json["recommended_preset"]["preset_id"]

    doctor = client.get("/ops/brain/runtime/doctor")
    assert doctor.status_code == 200
    doctor_json = doctor.json()
    assert doctor_json["recommended_preset"]["cloud_only_when_necessary"] is True
    assert doctor_json["recommendation_matrix"]

    skills = client.get("/ops/brain/skills/catalog", params={"source_id": "hermes", "category": "research"})
    assert skills.status_code == 200
    skills_json = skills.json()
    assert skills_json["sync_plan"]["read_only"] is True
    assert skills_json["summary"]["package_count"] >= 4
    assert skills_json["summary"]["benchmark_summary"]["benchmark_mode"] == "local-trace-history"

    scheduled = client.get("/ops/brain/agents/scheduled")
    assert scheduled.status_code == 200
    assert scheduled.json()["workflow_count"] >= 2

    wrapper = client.get("/ops/brain/wrapper-surface")
    assert wrapper.status_code == 200
    openjarvis_runtime = wrapper.json()["assimilation"]["openjarvis_runtime"]
    assert openjarvis_runtime["doctor"]["recommended_preset"]["preset_id"]
    assert openjarvis_runtime["skill_catalog"]["package_count"] >= 4
    assert openjarvis_runtime["scheduled_agents"]["workflow_count"] >= 2


def test_cost_energy_metrics_are_persisted_in_external_eval_reports(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    report = services.brain_evaluator.run_recent(limit=10)

    assert "cost_energy" in report["metrics"]
    assert "cost_energy" in report["artifacts"]
    assert Path(report["artifacts"]["cost_energy"]).exists()


def test_obliteratus_safe_boundary_stays_quarantined_and_surfaces_in_visualizer(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    review = client.post(
        "/ops/brain/research/refusal-circuit-review",
        json={
            "before": {"refusal_rate": 0.14, "stability": 0.95, "circuit_weight": 0.5},
            "after": {"refusal_rate": 0.13, "stability": 0.93, "circuit_weight": 0.46},
        },
    )
    assert review.status_code == 200
    review_json = review.json()
    assert review_json["review"]["research_only"] is True
    assert review_json["review"]["non_promotion_default"] is True
    assert review_json["review"]["guardrail_ablation_allowed"] is False
    assert Path(review_json["review"]["artifact_path"]).exists()

    analysis = client.get("/ops/brain/research/guardrail-analysis")
    assert analysis.status_code == 200
    assert analysis.json()["latest_analysis"]["analysis_id"] == review_json["review"]["analysis_ref"]

    wrapper = client.get("/ops/brain/wrapper-surface")
    assert wrapper.status_code == 200
    safe_boundary = wrapper.json()["assimilation"]["obliteratus_safe_boundary"]
    assert safe_boundary["red_team_eval"]["promotion_blocked_by_default"] is True

    visualizer = client.get("/ops/brain/visualizer/state")
    assert visualizer.status_code == 200
    overlay = visualizer.json()["overlay_state"]
    assert overlay["runtime_posture"]["obliteratus_quarantine_required"] is True
    assert overlay["runtime_posture"]["obliteratus_latest_review_id"] == review_json["review"]["review_id"]
