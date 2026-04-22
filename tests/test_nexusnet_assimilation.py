from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from nexus.schemas import MemoryRecord
from tests.test_nexus_phase1_foundation import make_project


def test_canonical_teacher_payload_and_runtime_spine_load(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    metadata = services.brain_teachers.metadata()
    assert metadata["schema_version"] == 2
    assert "mixtral-8x7b" in metadata["core_mentor_ensemble"]
    assert metadata["default_registry_layer"] == "v2026_live"
    assert len(services.brain_teachers.list_assignments()) >= 20

    runtime_summary = services.brain_runtime_registry.summary()
    runtime_names = {card["runtime_name"] for card in runtime_summary["capability_cards"]}
    assert "llama.cpp" in runtime_names
    assert "vllm" in runtime_names
    assert "onnx-genai" in runtime_names
    assert runtime_summary["dream_seed"]["seed_kind"] == "runtime-qes-shadow"


def test_memory_reconciliation_projection_and_migration(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    metadata = services.brain_memory_planes.metadata()
    assert metadata["schema_version"] == 1
    assert sorted(metadata["projection_names"]) == ["episodic", "semantic", "temporal"]

    migrated = services.brain_memory_planes.migrate_record(
        MemoryRecord(session_id="s1", plane="dream", content={"text": "shadow replay"})
    )
    assert migrated.plane == "imaginal"
    assert any(tag.startswith("migrated-from:") for tag in migrated.tags)


def test_api_surfaces_graph_agents_foundry_and_federation(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    agents = client.get("/ops/brain/agents")
    assert agents.status_code == 200
    assert any(cap["agent_id"] == "openclaw-agent" for cap in agents.json()["capabilities"])

    chat = client.post(
        "/chat",
        json={
            "session_id": "assimilation-session",
            "message": "Route this through the OpenClaw surface and explain why provenance matters.",
            "wrapper_mode": "openclaw",
            "teacher_id": "mixtral-8x7b",
            "rag": False,
        },
    )
    assert chat.status_code == 200
    assert chat.json()["trace"]["selected_agent"] == "openclaw-agent"

    session_agents = client.get("/ops/brain/agents", params={"session_id": "assimilation-session"})
    assert session_agents.status_code == 200
    assert session_agents.json()["session_provenance"]["active_agent_id"] == "openclaw-agent"

    ingest = client.post(
        "/ops/brain/graph/ingest",
        json={
            "source": "assimilation-spec",
            "text": "NexusNet preserves graph provenance. Graph retrieval feeds dream replay and critique.",
            "session_id": "assimilation-session",
            "plane_hint": "dream",
            "metadata": {"doc_id": "doc-1"},
        },
    )
    assert ingest.status_code == 200
    assert ingest.json()["nodes_added"] >= 1

    query = client.post(
        "/ops/brain/graph/query",
        json={"query": "graph provenance critique", "top_k": 5, "plane_tags": ["imaginal"]},
    )
    assert query.status_code == 200
    assert query.json()["hits"]
    assert "imaginal" in query.json()["evaluation"]["plane_coverage"]

    benchmark = client.post("/ops/brain/backends/benchmark")
    assert benchmark.status_code == 200
    assert Path(benchmark.json()["artifact_path"]).exists()

    distill = client.post(
        "/ops/brain/distill-dataset",
        json={"name": "assimilation-dataset", "trace_limit": 20, "include_dreams": True, "include_curriculum": True},
    )
    assert distill.status_code == 200
    artifact_path = distill.json()["artifact_path"]
    assert Path(artifact_path).exists()

    federation = client.post(
        "/ops/brain/federation/simulate",
        json={
            "candidate_kind": "adapter-update",
            "artifact_path": artifact_path,
            "lineage": "dream-derived",
            "metrics": {"win_rate": 0.62},
            "provenance": {"source": "distillation-export"},
        },
    )
    assert federation.status_code == 200
    payload = federation.json()
    assert payload["simulation"]["submission"]["packet"]["lineage"] == "dream-derived"
    assert payload["review"]["candidate_id"]
    assert payload["rollout"]["rollback_ready"] is True

    foundry = client.get("/ops/brain/foundry/status")
    assert foundry.status_code == 200
    assert foundry.json()["teacher_retirement"]
