from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_memory_os_persists_across_service_reloads(tmp_path):
    project_root = make_project(tmp_path)
    first_client = TestClient(create_app(str(project_root)))
    stored = first_client.post(
        "/ops/brain/memory-os/store",
        json={
            "fact_id": "nexusnet.persisted",
            "content": "Durable memory facts must survive service rebuilds.",
            "source": "deepening-test",
            "evidence": {"test": "memory-os-persistence"},
            "effective_at": datetime(2026, 4, 26, tzinfo=timezone.utc).isoformat(),
        },
    )
    assert stored.status_code == 200

    second_client = TestClient(create_app(str(project_root)))
    retrieved = second_client.get("/ops/brain/memory-os/retrieve/nexusnet.persisted")
    assert retrieved.status_code == 200
    assert retrieved.json()["content"] == "Durable memory facts must survive service rebuilds."
    persistence = second_client.get("/ops/brain/memory-os")
    assert persistence.status_code == 200
    assert Path(persistence.json()["persistence_path"]).exists()


def test_assimilation_registry_updates_are_audited_and_living(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    update = client.post(
        "/ops/brain/research-candidates/lmcache/status",
        json={
            "integration_status": "candidate",
            "maturity": "prototype",
            "notes": "Validated as a KV/cache reuse candidate but not promoted.",
            "evidence": "operator-reviewed runtime profile",
        },
    )
    assert update.status_code == 200
    payload = update.json()
    assert payload["candidate"]["id"] == "lmcache"
    assert payload["candidate"]["maturity"] == "prototype"
    assert payload["audit_event"]["action"] == "assimilation.candidate.updated"

    registry = client.get("/ops/brain/research-candidates/lmcache")
    assert registry.status_code == 200
    assert registry.json()["candidate"]["notes"] == "Validated as a KV/cache reuse candidate but not promoted."


def test_protocol_server_registration_and_consent_modes_fail_closed(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    rejected = client.post(
        "/ops/brain/security/protocol/servers",
        json={
            "server_id": "unsigned-browsermcp",
            "protocol": "mcp",
            "base_url": "http://127.0.0.1:6277",
            "signed": False,
            "allowlisted": True,
            "permissions": ["read"],
        },
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "denied"

    registered = client.post(
        "/ops/brain/security/protocol/servers",
        json={
            "server_id": "browsermcp",
            "protocol": "mcp",
            "base_url": "http://127.0.0.1:6277",
            "signed": True,
            "allowlisted": True,
            "permissions": ["read"],
        },
    )
    assert registered.status_code == 200
    assert registered.json()["status"] == "registered"

    decline = client.post(
        "/ops/brain/security/protocol/consent",
        json={"server_id": "browsermcp", "tool_id": "browsermcp.navigate", "mode": "decline"},
    )
    assert decline.status_code == 200
    assert decline.json()["status"] == "denied"
    assert decline.json()["executed"] is False

    cancel = client.post(
        "/ops/brain/security/protocol/consent",
        json={"server_id": "browsermcp", "tool_id": "browsermcp.navigate", "mode": "cancel"},
    )
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "hold"
    assert cancel.json()["reason"] == "user_cancelled"


def test_runtime_context_assembly_and_training_dataset_export_are_artifact_backed(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    context = client.post(
        "/ops/brain/runtime/context-assembly",
        json={
            "profile": "cloud",
            "target_tokens": 1_000_000,
            "requested_adapter": "vllm",
            "task_type": "research",
        },
    )
    assert context.status_code == 200
    context_payload = context.json()
    assert context_payload["raw_context_claim"] == "unresolved"
    assert context_payload["effective_context_strategy"] == "memory_index_summary_cache"
    assert context_payload["segments"]["indexed_evidence"]["tokens"] > context_payload["segments"]["raw_prompt"]["tokens"]
    assert context_payload["runtime_profile"]["runnable"] is False

    export = client.post(
        "/ops/brain/training/export-dataset",
        json={
            "name": "deepening-dataset",
            "records": [
                {
                    "trace_id": "trace-deepening-1",
                    "prompt": "Explain the Memory OS.",
                    "output": "The Memory OS controls lifecycle and provenance.",
                    "provenance": [{"source": "test", "id": "trace-deepening-1"}],
                    "teacher_source": {"teacher_id": "qwen3-30b-a3b"},
                    "capsule_source": {"capsule_id": "memory-weaver", "status": "locked"},
                    "safety_labels": ["policy_checked"],
                    "eval_target": "trace-first-evals",
                    "license_metadata": {"status": "candidate_requires_review"},
                }
            ],
        },
    )
    assert export.status_code == 200
    export_payload = export.json()
    assert export_payload["sample_count"] == 1
    assert export_payload["checkpoint_promotion_ready"] is False
    assert Path(export_payload["artifact_path"]).exists()
    assert Path(export_payload["manifest_path"]).exists()
