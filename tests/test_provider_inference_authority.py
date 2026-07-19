"""Non-native model inference must use a scoped authority lease."""
from __future__ import annotations

import importlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.execution_authority.service import ExecutionAuthorityService
from nexusnet.genesis.event_spine import GenesisEventSpineService
from nexusnet.providers.model_providers import ProviderRegistry
from tests.test_nexus_phase1_foundation import make_project


nexus_api_app = importlib.import_module("nexus.api.app")


class _RecordedCloudProvider:
    provider_id = "authority-test-cloud"
    is_local = False

    def __init__(self) -> None:
        self.call_count = 0

    def complete(self, messages: list[dict[str, str]]) -> dict[str, object]:
        self.call_count += 1
        return {
            "ok": True,
            "text": "governed provider response",
            "model": "authority-test-model",
            "local": False,
            "tokens": 3,
        }


def _provider_scope() -> dict[str, object]:
    return {
        "provider_id": _RecordedCloudProvider.provider_id,
        "provider_local": False,
        "operation": "chat_completion",
    }


def _authorized_provider_lease(client: TestClient) -> str:
    response = client.post(
        "/ops/brain/execution-authority/leases/request",
        json={
            "capability": "model_inference",
            "scope": _provider_scope(),
            "expires_at": "2099-01-01T00:00:00+00:00",
            "budget": {"max_usd": 1.0, "max_minutes": 1},
            "rollback_plan": {"strategy": "stop-dispatch-and-use-native-fallback"},
            "approval_id": "approval::provider-inference",
            "approval_decision": "approved",
            "gateway_decision": "allow",
            "product_sweep_gate_ids": ["provider-inference"],
            "product_sweep_decision": "passed",
            "requested_execution": True,
            "requested_mutation": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["lease"]["status"] == "granted"
    return response.json()["lease"]["lease_id"]


def _governed_client(monkeypatch, project_root: Path) -> tuple[TestClient, _RecordedCloudProvider]:
    provider = _RecordedCloudProvider()
    registry = ProviderRegistry()
    registry.register(provider)
    monkeypatch.setattr(nexus_api_app, "_default_provider_registry", lambda **_: registry)
    return TestClient(create_app(str(project_root))), provider


def test_non_native_provider_is_blocked_without_authority_lease_and_emits_sanitized_event(
    monkeypatch, tmp_path: Path
):
    project_root = make_project(tmp_path)
    client, provider = _governed_client(monkeypatch, project_root)
    session_id = "provider-authority-blocked-session-SECRET"
    prompt_secret = "provider-authority-blocked-prompt-SECRET"

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": provider.provider_id,
            "messages": [{"role": "user", "content": prompt_secret}],
            "user": session_id,
        },
    )

    assert response.status_code == 403
    assert provider.call_count == 0
    authority = response.json()["detail"]["provider_authority"]
    assert authority["status"] == "blocked-authority"
    assert authority["reason"] == "execution_authority_lease_required"
    event = authority["shared_event_spine"]
    assert event["event_type"] == "genesis.execution_authority.provider_inference.blocked"

    replay = client.get("/ops/brain/genesis-event-spine", params={"session_id": session_id}).json()
    assert any(item["event_ref"] == event["event_ref"] for item in replay["events"])
    serialized = json.dumps({"authority": authority, "replay": replay}, sort_keys=True)
    assert session_id not in serialized
    assert prompt_secret not in serialized
    assert str(project_root) not in serialized

def test_authority_lease_allows_scoped_provider_inference_and_emits_sanitized_event(
    monkeypatch, tmp_path: Path
):
    project_root = make_project(tmp_path)
    client, provider = _governed_client(monkeypatch, project_root)
    lease_id = _authorized_provider_lease(client)
    session_id = "provider-authority-allowed-session-SECRET"
    prompt_secret = "provider-authority-allowed-prompt-SECRET"

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": provider.provider_id,
            "messages": [{"role": "user", "content": prompt_secret}],
            "user": session_id,
            "metadata": {"execution_authority_lease_id": lease_id},
        },
    )

    assert response.status_code == 200
    assert provider.call_count == 1
    authority = response.json()["nexusnet"]["provider_authority"]
    assert authority["surface_id"] == "provider-registry-inference-authority"
    assert authority["status"] == "allowed"
    assert authority["execution_allowed"] is True
    event = authority["shared_event_spine"]
    assert event["event_type"] == "genesis.execution_authority.provider_inference.executed"

    replay = client.get("/ops/brain/genesis-event-spine", params={"session_id": session_id}).json()
    assert any(item["event_ref"] == event["event_ref"] for item in replay["events"])
    serialized = json.dumps({"authority": authority, "replay": replay}, sort_keys=True)
    assert session_id not in serialized
    assert prompt_secret not in serialized
    assert str(project_root) not in serialized

    streamed = client.post(
        "/v1/chat/completions",
        json={
            "model": provider.provider_id,
            "messages": [{"role": "user", "content": prompt_secret}],
            "user": session_id,
            "metadata": {"execution_authority_lease_id": lease_id},
            "stream": True,
        },
    )

    assert streamed.status_code == 200
    chunks = [
        json.loads(line.removeprefix("data: "))
        for line in streamed.text.splitlines()
        if line.startswith("data: {")
    ]
    terminal_authority = chunks[-1]["nexusnet"]["provider_authority"]
    assert terminal_authority["status"] == "allowed"
    assert terminal_authority["shared_event_spine"]["event_type"] == (
        "genesis.execution_authority.provider_inference.executed"
    )


def test_provider_registry_blocks_direct_non_native_dispatch_without_lease_and_allows_matching_lease(
    tmp_path: Path,
):
    provider = _RecordedCloudProvider()
    registry = ProviderRegistry()
    registry.register(provider)
    authority = ExecutionAuthorityService(artifacts_dir=tmp_path / "artifacts")
    registry.execution_authority = authority
    event_spine = GenesisEventSpineService(
        artifacts_dir=tmp_path / "artifacts",
        project_root=tmp_path,
    )

    def observe(envelope: dict[str, object]) -> dict[str, object]:
        return event_spine.publish_event(
            event_type=str(envelope["event_type"]),
            source_surface_id=str(envelope["source_surface_id"]),
            correlation_ref=str(envelope["correlation_ref"]),
            session_ref_digest=(
                str(envelope["session_ref_digest"])
                if envelope.get("session_ref_digest")
                else None
            ),
            artifact_refs=[str(item) for item in envelope["artifact_refs"]],
            planes=[str(item) for item in envelope["planes"]],
        )

    registry.execution_observer = observe

    blocked = registry.complete(provider.provider_id, [{"role": "user", "content": "registry-secret"}])

    assert blocked["ok"] is False
    assert provider.call_count == 0
    assert blocked["provider_authority"]["reason"] == "execution_authority_lease_required"
    blocked_event = blocked["provider_authority"]["shared_event_spine"]
    assert blocked_event["event_type"] == "genesis.execution_authority.provider_inference.blocked"

    lease = authority.request_lease(
        capability="model_inference",
        scope={
            "provider_id": provider.provider_id,
            "provider_local": False,
            "operation": "chat_completion",
        },
        expires_at="2099-01-01T00:00:00+00:00",
        budget={"max_usd": 1.0, "max_minutes": 1},
        rollback_plan={"strategy": "stop-dispatch-and-use-native-fallback"},
        approval_id="approval::direct-registry",
        approval_decision="approved",
        gateway_decision="allow",
        product_sweep_gate_ids=["provider-inference"],
        product_sweep_decision="passed",
        requested_execution=True,
        requested_mutation=False,
    )["lease"]
    allowed = registry.complete(
        provider.provider_id,
        [{"role": "user", "content": "registry-secret"}],
        authority_lease_id=lease["lease_id"],
    )

    assert allowed["ok"] is True
    assert provider.call_count == 1
    assert allowed["provider_authority"]["execution_allowed"] is True
    allowed_event = allowed["provider_authority"]["shared_event_spine"]
    assert allowed_event["event_type"] == "genesis.execution_authority.provider_inference.executed"

    replay = event_spine.summary()
    assert replay["event_count"] == 2
    assert replay["blackboard_snapshot_count"] == 2
    assert replay["plane_trace_count"] == 2
    serialized = json.dumps({"events": replay["events"], "receipts": [blocked_event, allowed_event]})
    assert "registry-secret" not in serialized
    assert str(tmp_path) not in serialized
