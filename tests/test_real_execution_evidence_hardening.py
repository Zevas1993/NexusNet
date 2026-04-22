from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_aitune_simulated_validation_writes_benchmark_and_tuned_artifacts_and_surfaces_execution_plan(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    model = services.model_registry.resolve_model("transformers/TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    payload = services.brain_runtime_registry.aitune_provider.validate(model, simulate=True)

    assert Path(payload["execution_plan_artifact_path"]).exists()
    assert Path(payload["benchmark_artifact_path"]).exists()
    assert payload["tuned_artifact_path"] is not None
    assert Path(payload["tuned_artifact_path"]).exists()

    summary = services.brain_runtime_registry.summary(model.model_id)["aitune"]
    assert summary["latest_execution_plan"]["artifact_kind"] == "execution-plan"
    assert summary["latest_benchmark"]["artifact_kind"] == "benchmark"
    assert summary["latest_tuned_artifact"]["artifact_kind"] == "tuned-artifact"

    client = TestClient(create_app(str(project_root)))
    plan = client.get("/ops/brain/aitune/execution-plan", params={"model_hint": model.model_id})
    assert plan.status_code == 200
    assert plan.json()["latest_execution_plan"]["artifact_kind"] == "execution-plan"


def test_retrieval_promotion_reviews_endpoint_uses_stable_review_ids_and_eval_artifacts(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/chat",
        json={
            "session_id": "real-execution-rerank",
            "message": "Explain rerank review evidence and candidate promotion reporting.",
            "rag": True,
            "metadata": {"retrieval_policy": "lexical+graph-memory-temporal-rerank"},
        },
    )
    assert chat.status_code == 200

    reviews = client.get("/ops/brain/retrieval/promotion-reviews")
    assert reviews.status_code == 200
    review = reviews.json()["items"][0]
    assert review["review_report_id"].startswith("retrievalreview-")
    assert review["review_headline"]

    promotions = client.get("/ops/brain/promotions")
    candidate = next(item for item in promotions.json()["items"] if item["candidate"]["candidate_kind"] == "retrieval-policy")
    evaluation = client.post(
        "/ops/brain/promotions/evaluate",
        json={"candidate_id": candidate["candidate"]["candidate_id"], "scenario_set": ["retrieval-shadow-suite"]},
    )
    assert evaluation.status_code == 200
    review_payload = json.loads(Path(evaluation.json()["artifacts"]["retrieval_rerank_review"]).read_text(encoding="utf-8"))
    assert review_payload["report_id"] == review["review_report_id"]

    wrapper = client.get("/ops/brain/wrapper-surface", params={"session_id": "real-execution-rerank"})
    assert wrapper.status_code == 200
    assert wrapper.json()["retrieval"]["compare_refs"]["promotion_reviews"] == "/ops/brain/retrieval/promotion-reviews"


def test_triattention_runtime_anchors_surface_in_summary_wrapper_and_visualizer(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    benchmark = client.get("/ops/brain/attention-providers/benchmark")
    assert benchmark.status_code == 200
    payload = benchmark.json()
    assert payload["runtime_anchor_registry"]
    assert payload["summary"]["runtime_anchor_summary"]
    assert Path(payload["artifacts"]["comparative_summary"]).exists()

    summary = client.get("/ops/brain/attention-providers/comparative-summary")
    assert summary.status_code == 200
    assert summary.json()["summary"]["runtime_anchor_registry"]

    wrapper = client.get("/ops/brain/wrapper-surface")
    assert wrapper.status_code == 200
    assert wrapper.json()["assimilation"]["compare_refs"]["attention_comparative_summary"] == "/ops/brain/attention-providers/comparative-summary"

    visualizer = client.get("/ops/brain/visualizer/state")
    assert visualizer.status_code == 200
    overlay = visualizer.json()["overlay_state"]
    assert overlay["runtime_posture"]["triattention_runtime_anchor_count"] >= 1
