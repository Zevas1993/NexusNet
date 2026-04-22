from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from nexusnet.schemas import CurriculumAssessmentRequest
from tests.test_nexus_phase1_foundation import make_project


def test_curriculum_stage_execution_uses_teacher_regimen_and_records_disagreement(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    assessment = services.brain_curriculum.assess(
        brain=services.brain,
        request=CurriculumAssessmentRequest(phase="graduate", subject="toolsmith", model_hint="mock/default"),
    )

    assert assessment.total_courses == 4
    assert assessment.teacher_flow["mode"] == "teacher-regimen"
    assert assessment.teacher_flow["selected_teachers"] == [
        "deepseek-r1-distill-qwen-32b",
        "devstral-2",
        "lfm2",
        "qwen3-coder-next",
    ]
    assert assessment.teacher_flow["disagreement_artifacts"]
    assert any(record["detail"].get("dream_episode") for record in assessment.records)


def test_native_takeover_candidate_and_foundry_status_carry_teacher_evidence(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    curriculum = client.post(
        "/ops/brain/curriculum/assess",
        json={"phase": "graduate", "subject": "toolsmith", "model_hint": "mock/default"},
    )
    assert curriculum.status_code == 200

    distill = client.post(
        "/ops/brain/distill-dataset",
        json={"name": "teacher-aware-native", "trace_limit": 20, "include_dreams": True, "include_curriculum": True},
    )
    assert distill.status_code == 200
    payload = distill.json()
    teacher_evidence = payload["teacher_evidence"]
    assert teacher_evidence["selected_teachers"]
    assert teacher_evidence["benchmark_families"]
    assert "teacher_evidence" in payload["native_takeover_candidate"]["traceability"]

    foundry = client.get("/ops/brain/foundry/status")
    assert foundry.status_code == 200
    assert any(item["teacher_evidence"] for item in foundry.json()["native_takeover"])


def test_teacher_aware_eval_scenarios_and_wrapper_visibility_are_exposed(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    curriculum = client.post(
        "/ops/brain/curriculum/assess",
        json={"phase": "graduate", "subject": "toolsmith", "model_hint": "mock/default"},
    )
    assert curriculum.status_code == 200

    distill = client.post(
        "/ops/brain/distill-dataset",
        json={"name": "teacher-aware-eval", "trace_limit": 20, "include_dreams": True, "include_curriculum": True},
    )
    assert distill.status_code == 200
    candidate = distill.json()["native_takeover_candidate"]

    evaluation = client.post(
        "/ops/brain/promotions/evaluate",
        json={
            "candidate_id": candidate["candidate_id"],
            "scenario_set": [
                "primary-vs-secondary-disagreement",
                "critique-arbitration-validation",
                "lfm2-bounded-lane-enforcement",
                "native-takeover-vs-teacher-fallback",
                "dream-derived-trace-contamination",
            ],
        },
    )
    assert evaluation.status_code == 200
    scenario_ids = {item["scenario_id"] for item in evaluation.json()["metrics"]["scenario_results"]}
    assert {
        "primary-vs-secondary-disagreement",
        "critique-arbitration-validation",
        "lfm2-bounded-lane-enforcement",
        "native-takeover-vs-teacher-fallback",
        "dream-derived-trace-contamination",
    }.issubset(scenario_ids)

    wrapper = client.get("/ops/brain/wrapper-surface")
    assert wrapper.status_code == 200
    wrapper_payload = wrapper.json()
    assert wrapper_payload["teachers"]["visibility"]["teacher_evidence"]["selected_teachers"]
    assert wrapper_payload["teachers"]["visibility"]["recent_teacher_traces"]
    assert wrapper_payload["promotions"]["teacher_evidence"]
