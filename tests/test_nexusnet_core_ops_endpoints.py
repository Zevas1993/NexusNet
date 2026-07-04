from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def _client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(str(make_project(tmp_path))))


def test_core_wake_endpoint_returns_state_and_trace(tmp_path: Path):
    client = _client(tmp_path)

    response = client.post("/ops/brain/core/wake")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["awake"] is True
    assert payload["hardware_profile"]["cpu_count"] >= 1
    assert payload["adaptive_config"]["local_first"] is True
    assert payload["trace"]["event"] == "core.wake"

    trace = client.get("/ops/brain/core/trace")
    assert trace.status_code == 200
    assert any(event["event"] == "core.wake" for event in trace.json()["events"])


def test_core_attach_rejects_mock_without_explicit_allowance(tmp_path: Path):
    client = _client(tmp_path)

    response = client.post(
        "/ops/brain/core/attach",
        json={
            "mode": "mock",
            "model_ref": "mock/default",
            "allow_mock": False,
            "metadata": {"model_name": "mock/default"},
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["error"] == "mock-attach-disabled"
    assert detail["attached"] is False


def test_core_attach_allows_mock_but_trace_hides_it_by_default(tmp_path: Path):
    client = _client(tmp_path)

    response = client.post(
        "/ops/brain/core/attach",
        json={
            "mode": "mock",
            "model_ref": "mock/default",
            "allow_mock": True,
            "metadata": {"model_name": "mock/default", "hidden_size": 64, "vocab_size": 321},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["attached"] is True
    assert payload["attachment"]["mode"] == "mock"
    assert payload["attachment"]["product_evidence"] is False

    default_trace = client.get("/ops/brain/core/trace")
    assert all((event.get("metadata") or {}).get("mode") != "mock" for event in default_trace.json()["events"])

    audit_trace = client.get("/ops/brain/core/trace", params={"include_mock_traces": True})
    assert any((event.get("metadata") or {}).get("mode") == "mock" for event in audit_trace.json()["events"])


def test_core_product_attach_validates_equal_and_mismatched_dims(tmp_path: Path):
    client = _client(tmp_path)

    equal = client.post(
        "/ops/brain/core/attach",
        json={
            "mode": "product",
            "model_ref": "local/llama",
            "metadata": {"model_name": "local/llama", "model_family": "llama", "vocab_size": 32000},
            "router_hidden_dim": 4096,
            "expert_hidden_dim": 4096,
            "strict_product_mode": True,
        },
    )
    assert equal.status_code == 200
    assert equal.json()["compatibility_plan"]["status"] == "COMPATIBLE"
    assert equal.json()["attachment"]["product_evidence"] is True

    mismatch = client.post(
        "/ops/brain/core/attach",
        json={
            "mode": "product",
            "model_ref": "local/devstral",
            "metadata": {"model_name": "local/devstral", "model_family": "devstral", "vocab_size": 32000},
            "router_hidden_dim": 4096,
            "expert_hidden_dim": 6144,
            "strict_product_mode": True,
        },
    )
    assert mismatch.status_code == 200
    assert mismatch.json()["compatibility_plan"]["status"] == "ADAPTER_REQUIRED"
    assert mismatch.json()["compatibility_plan"]["adapter_recommendation"]["adapter_type"] == "projection"


def test_core_product_attach_blocks_unverified_and_plan_only_does_not_mutate(tmp_path: Path):
    client = _client(tmp_path)
    services = client.app.state.services

    plan_only = client.post(
        "/ops/brain/core/attach",
        json={
            "mode": "product",
            "model_ref": "local/qwen",
            "metadata": {"model_name": "local/qwen", "model_family": "qwen", "vocab_size": 151936},
            "router_hidden_dim": 3584,
            "expert_hidden_dim": 3584,
            "plan_only": True,
            "strict_product_mode": True,
        },
    )
    assert plan_only.status_code == 200
    assert plan_only.json()["attached"] is False
    assert plan_only.json()["compatibility_plan"]["status"] == "COMPATIBLE"
    assert services.nexusnet_core.base_model_handle is None

    blocked = client.post(
        "/ops/brain/core/attach",
        json={
            "mode": "product",
            "model_ref": "local/missing-metadata",
            "metadata": {"model_name": "local/missing-metadata"},
            "strict_product_mode": True,
        },
    )
    assert blocked.status_code == 400
    detail = blocked.json()["detail"]
    assert detail["attached"] is False
    assert detail["compatibility_plan"]["status"] == "UNVERIFIED"
    assert services.nexusnet_core.base_model_handle is None
