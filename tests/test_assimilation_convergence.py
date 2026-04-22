from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_retrieval_policy_candidates_carry_rerank_promotion_evidence_and_eval_artifacts(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/chat",
        json={
            "session_id": "convergence-rerank",
            "message": "Explain retrieval provenance and graph contribution traceability in NexusNet.",
            "rag": True,
            "metadata": {"retrieval_policy": "lexical+graph-memory-temporal-rerank"},
        },
    )
    assert chat.status_code == 200

    promotions = client.get("/ops/brain/promotions")
    assert promotions.status_code == 200
    items = promotions.json()["items"]
    retrieval_candidate = next(item for item in items if item["candidate"]["candidate_kind"] == "retrieval-policy")
    evidence = retrieval_candidate["candidate"]["traceability"]["retrieval_rerank_evidence"]
    assert evidence["bundle_id"]
    assert evidence["scorecard_id"]
    assert evidence["benchmark_family_id"] == "retrieval-rerank-operational"
    assert evidence["threshold_set_id"] == "retrieval-rerank-v2026-r1"
    assert Path(evidence["artifact_path"]).exists()

    promotion_evidence = client.get("/ops/brain/retrieval/promotion-evidence")
    assert promotion_evidence.status_code == 200
    assert promotion_evidence.json()["items"][0]["bundle_id"] == evidence["bundle_id"]

    evaluation = client.post(
        "/ops/brain/promotions/evaluate",
        json={
            "candidate_id": retrieval_candidate["candidate"]["candidate_id"],
            "scenario_set": ["retrieval-shadow-suite"],
        },
    )
    assert evaluation.status_code == 200
    eval_payload = evaluation.json()
    assert Path(eval_payload["artifacts"]["retrieval_rerank_evidence"]).exists()
    assert Path(eval_payload["artifacts"]["assimilation_artifacts"]).exists()
    assert Path(eval_payload["artifacts"]["assimilation_scorecards"]).exists()

    wrapper = client.get("/ops/brain/wrapper-surface", params={"session_id": "convergence-rerank"})
    assert wrapper.status_code == 200
    assert wrapper.json()["retrieval"]["promotion_evidence"][0]["bundle_id"] == evidence["bundle_id"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "convergence-rerank"})
    assert visualizer.status_code == 200
    overlay = visualizer.json()["overlay_state"]
    assert overlay["route_activity"]["rerank_promotion_evidence_ref"] == evidence["bundle_id"]


def test_aitune_validation_exposes_supported_lane_runner_and_artifacts_without_breaking_unsupported_envs(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    model = services.model_registry.resolve_model("transformers/TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    payload = services.brain_runtime_registry.aitune_provider.validate(model)

    assert payload["current_status"] == "skipped"
    assert payload["supported_lane"]["status"] in {"ready-on-supported-host", "ready-to-run-here"}
    assert "docs/aitune_supported_lane.md" in payload["supported_lane"]["docs"]
    assert Path(payload["artifact_path"]).exists()
    assert Path(payload["runner_artifact_path"]).exists()

    summary = services.brain_runtime_registry.summary(model.model_id)["aitune"]
    assert summary["supported_lane_readiness"]["runner_command"].startswith("python -m nexusnet.runtime.qes.aitune_runner")


def test_triattention_benchmark_records_comparative_baselines_and_surfaces_in_wrapper_and_visualizer(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    benchmark = client.get("/ops/brain/attention-providers/benchmark")
    assert benchmark.status_code == 200
    payload = benchmark.json()
    assert payload["baseline_providers"] == ["accepted-dense-kv", "accepted-windowed-hybrid"]
    assert "avg_kv_memory_ratio" in payload["summary"]
    assert payload["scorecard"]["threshold_set_id"] == "triattention-v2026-r1"
    assert Path(payload["artifacts"]["scorecard"]).exists()

    wrapper = client.get("/ops/brain/wrapper-surface")
    assert wrapper.status_code == 200
    attention_summary = wrapper.json()["assimilation"]["attention_benchmarks"]
    assert attention_summary["latest_comparative_scorecard"]["scorecard_id"] == payload["scorecard"]["scorecard_id"]

    visualizer = client.get("/ops/brain/visualizer/state")
    assert visualizer.status_code == 200
    overlay = visualizer.json()["overlay_state"]
    assert overlay["runtime_posture"]["triattention_latest_scorecard_id"] == payload["scorecard"]["scorecard_id"]


def test_assimilation_status_reports_retrieval_evidence_aitune_readiness_and_attention_benchmarks(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/chat",
        json={
            "session_id": "assimilation-status",
            "message": "Summarize gateway approvals and retrieval provenance.",
            "rag": True,
            "metadata": {"retrieval_policy": "lexical+graph-memory-temporal-rerank"},
        },
    )
    client.get("/ops/brain/attention-providers/benchmark")

    status = client.get("/ops/brain/assimilation/status")
    assert status.status_code == 200
    payload = status.json()
    assert payload["retrieval"]["promotion_evidence"]
    assert payload["aitune"]["supported_lane_readiness"]["status"] in {"ready-on-supported-host", "ready-to-run-here"}
    assert payload["attention_benchmarks"]["latest_comparative_scorecard"]["provider_name"] == "triattention"
