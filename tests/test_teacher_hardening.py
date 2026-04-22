from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from nexusnet.schemas import CurriculumAssessmentRequest
from tests.test_nexus_phase1_foundation import make_project


def test_teacher_benchmark_families_and_thresholds_load_for_core_and_auxiliary_subjects(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    families = services.brain_teachers.benchmark_registry.families_for_subject("toolsmith")
    assert {item["name"] for item in families} == {
        "strict JSON / tool schemas",
        "tool chain recovery",
        "sandbox-safe execution",
        "API/tool invocation discipline",
    }

    threshold = services.brain_teachers.threshold_registry.resolve(
        subject="security",
        benchmark_family="safe tool use",
    )
    assert threshold.threshold_set_id == "teacher-v2026-r1"
    assert threshold.version == 1
    assert threshold.metric_rules["safety"]["value"] == 0.90

    auxiliary = services.brain_teachers.benchmark_registry.subject_catalog("curriculum-architect")
    assert auxiliary["auxiliary"] is True
    assert auxiliary["canon_status"] == "STRONG ACCEPTED DIRECTION"


def test_curriculum_persists_teacher_scorecards_disagreements_and_bundles(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    assessment = services.brain_curriculum.assess(
        brain=services.brain,
        request=CurriculumAssessmentRequest(phase="graduate", subject="toolsmith", model_hint="mock/default"),
    )

    assert assessment.teacher_flow["bundle_ids"]
    assert assessment.teacher_flow["scorecards"]
    assert assessment.teacher_flow["threshold_set_id"] == "teacher-v2026-r1"

    bundles = services.store.list_teacher_evidence_bundles(subject="toolsmith", limit=50)
    disagreements = services.store.list_teacher_disagreement_artifacts(subject="toolsmith", limit=50)
    scorecards = services.store.list_teacher_scorecards(subject="toolsmith", limit=50)

    assert bundles
    assert disagreements
    assert scorecards
    assert bundles[0]["threshold_set_id"] == "teacher-v2026-r1"
    assert disagreements[0]["lfm2_lane"] == "toolsmith"
    assert scorecards[0]["weight_profile"]


def test_native_takeover_and_promotion_link_to_teacher_evidence_and_scorecards(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    curriculum = client.post(
        "/ops/brain/curriculum/assess",
        json={"phase": "graduate", "subject": "toolsmith", "model_hint": "mock/default"},
    )
    assert curriculum.status_code == 200

    distill = client.post(
        "/ops/brain/distill-dataset",
        json={"name": "teacher-hardening-native", "trace_limit": 20, "include_dreams": True, "include_curriculum": True},
    )
    assert distill.status_code == 200
    payload = distill.json()
    candidate = payload["native_takeover_candidate"]
    assert candidate["teacher_evidence_bundle_id"]
    assert candidate["threshold_set_id"] == "teacher-v2026-r1"
    assert candidate["traceability"]["takeover_scorecard"]["scorecard_id"]
    assert payload["benchmark"]["takeover_scorecard"]["passed"] in {True, False}

    evaluation = client.post(
        "/ops/brain/promotions/evaluate",
        json={"candidate_id": candidate["candidate_id"], "scenario_set": ["teacher-backed-output-quality"]},
    )
    assert evaluation.status_code == 200
    metrics = evaluation.json()["metrics"]
    assert metrics["scorecard_summary"]["scorecard_count"] >= 1
    assert Path(evaluation.json()["artifacts"]["scorecard"]).exists()
    assert Path(evaluation.json()["artifacts"]["teacher_eval_report"]).exists()

    foundry = client.get("/ops/brain/foundry/status")
    assert foundry.status_code == 200
    foundry_payload = foundry.json()
    assert foundry_payload["takeover_scorecards"]
    assert foundry_payload["retirement_shadow_log"]


def test_wrapper_and_ops_surface_expose_teacher_hardening_fields(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/ops/brain/curriculum/assess",
        json={"phase": "graduate", "subject": "toolsmith", "model_hint": "mock/default"},
    )
    distill = client.post(
        "/ops/brain/distill-dataset",
        json={"name": "teacher-hardening-wrapper", "trace_limit": 20, "include_dreams": True, "include_curriculum": True},
    )
    assert distill.status_code == 200

    wrapper = client.get("/ops/brain/wrapper-surface")
    assert wrapper.status_code == 200
    visibility = wrapper.json()["teachers"]["visibility"]
    assert visibility["benchmark_metadata"]["default_threshold_set_id"] == "teacher-v2026-r1"
    assert visibility["threshold_metadata"]["threshold_sets"] == ["teacher-v2026-r1"]
    assert visibility["evidence_bundles"]
    assert visibility["disagreement_artifacts"]
    assert visibility["scorecards"]
    assert visibility["retirement_shadow_log"]

    evidence = client.get("/ops/brain/teachers/evidence")
    assert evidence.status_code == 200
    assert evidence.json()["items"]

    disagreements = client.get("/ops/brain/teachers/disagreements")
    assert disagreements.status_code == 200
    assert disagreements.json()["items"]
