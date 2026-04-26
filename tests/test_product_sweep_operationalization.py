from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_memory_os_api_stores_updates_retrieves_history_and_evidence(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    first_time = datetime(2026, 4, 20, tzinfo=timezone.utc)
    second_time = first_time + timedelta(days=3)

    first = client.post(
        "/ops/brain/memory-os/store",
        json={
            "fact_id": "nexusnet.identity",
            "content": "NexusNet is a neural-core brain.",
            "source": "38-chat-synthesis",
            "evidence": {"artifact": "NEXUSNET_38_CHAT_IDEA_SYNTHESIS.md"},
            "effective_at": first_time.isoformat(),
        },
    )
    assert first.status_code == 200
    first_id = first.json()["memory_id"]

    updated = client.post(
        "/ops/brain/memory-os/update",
        json={
            "fact_id": "nexusnet.identity",
            "content": "NexusNet is a neural-core brain with governed protocol tools.",
            "source": "product-sweep-refresh",
            "evidence": {"registry": "assimilation"},
            "effective_at": second_time.isoformat(),
        },
    )
    assert updated.status_code == 200

    historical = client.get(
        "/ops/brain/memory-os/retrieve/nexusnet.identity",
        params={"as_of": (first_time + timedelta(hours=1)).isoformat()},
    )
    assert historical.status_code == 200
    assert historical.json()["content"] == "NexusNet is a neural-core brain."

    current = client.get("/ops/brain/memory-os/retrieve/nexusnet.identity")
    assert current.status_code == 200
    assert "governed protocol tools" in current.json()["content"]

    evidence = client.get(f"/ops/brain/memory-os/dereference/{first_id}")
    assert evidence.status_code == 200
    assert evidence.json()["evidence"]["artifact"] == "NEXUSNET_38_CHAT_IDEA_SYNTHESIS.md"

    provenance = client.get("/ops/brain/memory-os/provenance/nexusnet.identity")
    assert provenance.status_code == 200
    assert provenance.json()["version_count"] == 2


def test_protocol_security_api_evaluates_denies_holds_and_audits(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    denied = client.post(
        "/ops/brain/security/protocol/evaluate",
        json={
            "tool_id": "browsermcp.login",
            "protocol": "mcp",
            "server_signed": True,
            "server_allowlisted": True,
            "sandboxed": True,
            "permissions": ["read"],
            "elicitation_mode": "form",
            "handles_secret": True,
            "approval_granted": True,
            "identity_metadata": {"user": "operator"},
        },
    )
    assert denied.status_code == 200
    assert denied.json()["status"] == "denied"
    assert denied.json()["executed"] is False

    held = client.post(
        "/ops/brain/security/protocol/evaluate",
        json={
            "tool_id": "browsermcp.navigate",
            "protocol": "mcp",
            "server_signed": True,
            "server_allowlisted": True,
            "sandboxed": True,
            "permissions": ["read"],
            "approval_granted": False,
            "identity_metadata": {"user": "operator"},
        },
    )
    assert held.status_code == 200
    assert held.json()["status"] == "hold"
    assert held.json()["reason"] == "user_approval_required"

    audit = client.get("/ops/brain/security/protocol/audit")
    assert audit.status_code == 200
    assert audit.json()["audit_event_count"] == 2


def test_ebt_eval_and_training_contract_apis_are_trace_first_and_gated(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    contract = client.get("/ops/brain/ebt/contract")
    assert contract.status_code == 200
    assert contract.json()["status"] == "pluggable_contract"
    assert "confidence" in contract.json()["required_fields"]

    score = client.post(
        "/ops/brain/ebt/score",
        json={
            "capsule_id": "researcher",
            "confidence": 0.82,
            "risk": 0.18,
            "memory_influence": "retrieved-provenance",
            "critique_result": "ok",
            "fallback_reason": None,
        },
    )
    assert score.status_code == 200
    score_payload = score.json()
    assert score_payload["score_id"].startswith("ebt_")
    assert score_payload["capsule_choice"] == "researcher"
    assert score_payload["route_decision"] == "use_capsule"

    scenarios = client.get("/ops/brain/evals/scenarios")
    assert scenarios.status_code == 200
    categories = {item["category"] for item in scenarios.json()["scenarios"]}
    assert {"route_choice", "tool_correctness", "memory_recall", "critique_quality", "policy_violation"} <= categories

    export = client.post(
        "/ops/brain/training/export-record",
        json={
            "trace_id": "trace-product-1",
            "prompt": "Explain NexusNet.",
            "output": "NexusNet is a neural-core brain.",
            "provenance": [{"source": "trace", "id": "trace-product-1"}],
            "teacher_source": {"teacher_id": "qwen3-30b-a3b", "registry_layer": "v2026_live"},
            "capsule_source": {"capsule_id": "researcher", "status": "locked"},
            "safety_labels": ["policy_checked"],
            "eval_target": "trace-first-evals",
            "license_metadata": {"status": "candidate_requires_review", "source": "assimilation-registry"},
        },
    )
    assert export.status_code == 200
    assert export.json()["checkpoint_promotion_ready"] is False
    assert export.json()["real_training_status"] == "gated"
