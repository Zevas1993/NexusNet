from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_live_runtime_selection_falls_back_through_brain_and_records_retrieval_policy(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    client.post(
        "/retrieval/ingest",
        json={
            "documents": [
                {
                    "source": "runtime-spec",
                    "title": "Runtime Promotion",
                    "text": "Graph provenance and retrieval policy are part of the live NexusNet brain path.",
                }
            ]
        },
    )
    client.post(
        "/ops/brain/graph/ingest",
        json={
            "source": "graph-runtime-spec",
            "text": "Graph provenance contributes to retrieval policy decisions and dream replay.",
            "session_id": "promotion-session",
            "plane_hint": "conceptual",
            "metadata": {"doc_id": "graph-doc-1"},
        },
    )

    response = client.post(
        "/chat",
        json={
            "session_id": "promotion-session",
            "message": "Explain graph provenance and retrieval policy in the live brain path.",
            "model_hint": "ollama/llama3.1",
            "rag": True,
            "metadata": {"retrieval_policy": "lexical+graph-merged"},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    trace = payload["trace"]
    assert trace["runtime_selection"]["selected_runtime_name"] == "onnx-genai"
    assert trace["runtime_name"] != trace["runtime_selection"]["selected_runtime_name"]
    assert trace["runtime_name"] in trace["runtime_selection"]["fallback_runtime_names"] + ["mock"]
    assert trace["metrics"]["fallback_used"] is True
    assert trace["retrieval_policy"] == "lexical+graph-merged"
    assert trace["metrics"]["graph_contribution_count"] >= 1
    assert any(ref.startswith("runtime-profile::") for ref in trace["promotion_references"])
    assert any(ref.startswith("retrieval-policy::") for ref in trace["promotion_references"])


def test_runtime_promotion_requires_evaluation_before_approval(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    benchmark = client.post("/ops/brain/backends/benchmark")
    assert benchmark.status_code == 200
    candidate = benchmark.json()["promotion_candidates"][0]

    blocked = client.post(
        "/ops/brain/promotions/decide",
        json={
            "candidate_id": candidate["candidate_id"],
            "approver": "Architect",
            "requested_decision": "approved",
        },
    )
    assert blocked.status_code == 200
    assert blocked.json()["decision"] == "shadow"

    evaluated = client.post(
        "/ops/brain/promotions/evaluate",
        json={
            "candidate_id": candidate["candidate_id"],
            "scenario_set": ["runtime-shadow-suite"],
        },
    )
    assert evaluated.status_code == 200
    assert evaluated.json()["candidate_id"] == candidate["candidate_id"]

    promotions = client.get("/ops/brain/promotions")
    assert promotions.status_code == 200
    assert any(item["candidate"]["candidate_id"] == candidate["candidate_id"] for item in promotions.json()["items"])


def test_federated_and_foundry_candidates_are_persisted_and_visible(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    distill = client.post(
        "/ops/brain/distill-dataset",
        json={"name": "promotion-dataset", "trace_limit": 20, "include_dreams": True, "include_curriculum": True},
    )
    assert distill.status_code == 200
    distill_payload = distill.json()
    native_candidate = distill_payload["native_takeover_candidate"]
    assert native_candidate["review_status"] == "shadow"

    foundry = client.get("/ops/brain/foundry/status")
    assert foundry.status_code == 200
    assert any(item["candidate"]["candidate_id"] == native_candidate["candidate_id"] for item in foundry.json()["native_takeover"])

    federation = client.post(
        "/ops/brain/federation/simulate",
        json={
            "candidate_kind": "adapter-update",
            "artifact_path": distill_payload["artifact_path"],
            "lineage": "dream-derived",
            "metrics": {"win_rate": 0.61},
            "provenance": {"source": "distillation-export"},
        },
    )
    assert federation.status_code == 200
    federation_payload = federation.json()
    assert federation_payload["promotion_candidate"]["candidate_id"]
    assert federation_payload["simulation"]["submission"]["packet"]["lineage"] == "dream-derived"
    assert federation_payload["review"]["candidate_id"] == federation_payload["promotion_candidate"]["candidate_id"]
    assert federation_payload["rollout"]["rollback_ready"] is True

    wrapper = client.get("/ops/brain/wrapper-surface", params={"session_id": "promotion-session"})
    assert wrapper.status_code == 200
    wrapper_payload = wrapper.json()
    assert "promotions" in wrapper_payload
    assert "federation" in wrapper_payload
    assert "foundry" in wrapper_payload
