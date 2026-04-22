from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_aitune_supported_host_summary_surfaces_runner_and_markdown_artifacts(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    model = services.model_registry.resolve_model("transformers/TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    payload = services.brain_runtime_registry.aitune_provider.validate(model, simulate=True)

    assert Path(payload["execution_plan_markdown_path"]).exists()
    summary = services.brain_runtime_registry.summary(model.model_id)["aitune"]
    assert summary["latest_runner_report"]["artifact_kind"] == "runner"
    assert summary["latest_execution_plan_markdown_path"]
    assert Path(summary["latest_execution_plan_markdown_path"]).exists()

    client = TestClient(create_app(str(project_root)))
    response = client.get("/ops/brain/aitune/execution-plan", params={"model_hint": model.model_id})
    assert response.status_code == 200
    body = response.json()
    assert body["latest_runner_report"]["artifact_kind"] == "runner"
    assert Path(body["latest_execution_plan_markdown_path"]).exists()
    assert body["supported_lane_readiness"]["status"] in {"ready-on-supported-host", "ready-to-run-here"}


def test_retrieval_promotion_review_detail_surfaces_human_summary_and_eval_linkage(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/chat",
        json={
            "session_id": "supported-host-rerank",
            "message": "Explain retrieval rerank evidence and why the review summary should be readable.",
            "rag": True,
            "metadata": {"retrieval_policy": "lexical+graph-memory-temporal-rerank"},
        },
    )
    assert chat.status_code == 200

    promotions = client.get("/ops/brain/promotions")
    assert promotions.status_code == 200
    candidate = next(item for item in promotions.json()["items"] if item["candidate"]["candidate_kind"] == "retrieval-policy")

    evaluation = client.post(
        "/ops/brain/promotions/evaluate",
        json={"candidate_id": candidate["candidate"]["candidate_id"], "scenario_set": ["retrieval-shadow-suite"]},
    )
    assert evaluation.status_code == 200
    artifacts = evaluation.json()["artifacts"]
    assimilation_artifacts = json.loads(Path(artifacts["assimilation_artifacts"]).read_text(encoding="utf-8"))
    assimilation_scorecards = json.loads(Path(artifacts["assimilation_scorecards"]).read_text(encoding="utf-8"))
    assert assimilation_artifacts["retrieval_rerank_review"]["human_summary"]
    assert assimilation_scorecards["retrieval_rerank"]["human_summary"]

    reviews = client.get("/ops/brain/retrieval/promotion-reviews")
    assert reviews.status_code == 200
    review = reviews.json()["items"][0]
    assert review["human_summary"]
    assert review["evaluator_artifact_summary"]["artifact_count"] >= 1
    assert review["candidate_shift_summary"]["changed_count"] >= 0

    detail = client.get(f"/ops/brain/retrieval/promotion-reviews/{review['review_report_id']}")
    assert detail.status_code == 200
    detail_payload = detail.json()
    assert detail_payload["summary"]["human_summary"] == review["human_summary"]
    assert "Candidate Shift Summary" in (detail_payload["markdown"] or "")

    wrapper = client.get("/ops/brain/wrapper-surface", params={"session_id": "supported-host-rerank"})
    assert wrapper.status_code == 200
    compare_refs = wrapper.json()["retrieval"]["compare_refs"]
    assert compare_refs["promotion_review_detail_template"].endswith("{review_report_id}")
    wrapper_review = wrapper.json()["retrieval"]["promotion_evidence"][0]
    assert wrapper_review["evaluator_artifact_summary"]["artifact_count"] >= 1


def test_triattention_comparative_summary_surfaces_runtime_anchor_quality_metadata(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    benchmark = client.get("/ops/brain/attention-providers/benchmark")
    assert benchmark.status_code == 200
    payload = benchmark.json()
    assert payload["summary"]["runtime_anchor_quality_summary"]["anchor_count"] >= 1
    assert payload["summary"]["runtime_anchor_quality_summary"]["measurement_modes"]
    assert payload["summary"]["runtime_anchor_summary"]

    summary = client.get("/ops/brain/attention-providers/comparative-summary")
    assert summary.status_code == 200
    comparative = summary.json()["summary"]
    assert comparative["runtime_anchor_quality_summary"]["anchor_count"] >= 1

    visualizer = client.get("/ops/brain/visualizer/state")
    assert visualizer.status_code == 200
    overlay = visualizer.json()["overlay_state"]
    assert overlay["runtime_posture"]["triattention_runtime_anchor_count"] >= 1
    assert overlay["runtime_posture"]["triattention_runtime_anchor_measurement_modes"]
