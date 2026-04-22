from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_aitune_supported_lane_can_simulate_and_persist_live_validation_artifacts(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    model = services.model_registry.resolve_model("transformers/TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    payload = services.brain_runtime_registry.aitune_provider.validate(model, simulate=True)

    assert payload["execution_mode"] in {"simulate", "live"}
    assert Path(payload["artifact_path"]).exists()
    assert Path(payload["runner_artifact_path"]).exists()
    assert Path(payload["health_artifact_path"]).exists()
    assert Path(payload["execution_plan_artifact_path"]).exists()
    if payload["execution_mode"] == "simulate":
        assert payload["current_status"] == "simulated-supported-lane"
        assert payload["benchmark_evidence"]["mode"] == "simulated-supported-lane"

    summary = services.brain_runtime_registry.summary(model.model_id)["aitune"]
    assert summary["latest_validation"]["payload"]["current_status"] == payload["current_status"]
    assert summary["latest_health_report"]["payload"]["execution_mode"] == payload["execution_mode"]


def test_retrieval_promotion_evidence_surfaces_review_reports_and_eval_artifacts(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/chat",
        json={
            "session_id": "live-validation-rerank",
            "message": "Explain retrieval rerank provenance and the stage-two candidate review path.",
            "rag": True,
            "metadata": {"retrieval_policy": "lexical+graph-memory-temporal-rerank"},
        },
    )
    assert chat.status_code == 200

    promotions = client.get("/ops/brain/promotions")
    retrieval_candidate = next(item for item in promotions.json()["items"] if item["candidate"]["candidate_kind"] == "retrieval-policy")

    evidence = client.get("/ops/brain/retrieval/promotion-evidence")
    assert evidence.status_code == 200
    first = evidence.json()["items"][0]
    assert first["review_report_id"]
    assert Path(first["review_artifacts"]["payload"]).exists()
    assert Path(first["review_artifacts"]["markdown"]).exists()

    evaluation = client.post(
        "/ops/brain/promotions/evaluate",
        json={
            "candidate_id": retrieval_candidate["candidate"]["candidate_id"],
            "scenario_set": ["retrieval-shadow-suite"],
        },
    )
    assert evaluation.status_code == 200
    artifacts = evaluation.json()["artifacts"]
    assert Path(artifacts["retrieval_rerank_review"]).exists()
    assert Path(artifacts["retrieval_rerank_review_md"]).exists()

    wrapper = client.get("/ops/brain/wrapper-surface", params={"session_id": "live-validation-rerank"})
    assert wrapper.status_code == 200
    wrapper_item = wrapper.json()["retrieval"]["promotion_evidence"][0]
    assert wrapper_item["review_report_id"] == first["review_report_id"]
    assert "retrieval_rerank_review" in wrapper_item["evaluation_artifacts"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "live-validation-rerank"})
    assert visualizer.status_code == 200
    overlay = visualizer.json()["overlay_state"]
    assert overlay["route_activity"]["rerank_review_report_id"] == first["review_report_id"]
    assert overlay["route_activity"]["rerank_threshold_set_id"] == first["threshold_set_id"]


def test_triattention_comparative_baselines_include_repo_refs_and_surface_latest_summary(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    benchmark = client.get("/ops/brain/attention-providers/benchmark")
    assert benchmark.status_code == 200
    payload = benchmark.json()
    assert payload["baseline_registry"]
    assert payload["baseline_registry"][0]["source_refs"]
    assert Path(payload["artifacts"]["comparative_summary"]).exists()
    assert payload["summary"]["head_to_head"]["accepted-dense-kv"]["case_count"] >= 1

    wrapper = client.get("/ops/brain/wrapper-surface")
    assert wrapper.status_code == 200
    attention = wrapper.json()["assimilation"]["attention_benchmarks"]
    assert attention["latest_comparative_summary"]["baseline_registry"][0]["source_refs"]

    visualizer = client.get("/ops/brain/visualizer/state")
    assert visualizer.status_code == 200
    overlay = visualizer.json()["overlay_state"]
    assert overlay["runtime_posture"]["triattention_latest_report_id"] == payload["scorecard"]["report_id"]
