from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_protocol_adapters_are_visible_disabled_and_policy_gated(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    defaults = client.get("/ops/brain/protocol/adapters")
    assert defaults.status_code == 200
    payload = defaults.json()
    assert payload["external_execution_default"] == "deny_until_user_consent"
    adapters = {item["adapter_id"]: item for item in payload["adapters"]}
    assert set(adapters) == {"mcp", "a2a", "ag-ui"}
    assert adapters["mcp"]["status"] == "disabled"
    assert adapters["mcp"]["execution_enabled"] is False
    assert adapters["mcp"]["security_envelope_required"] is True

    unsafe = client.post(
        "/ops/brain/protocol/adapters/mcp/policy",
        json={
            "enable_requested": True,
            "server_id": "browsermcp",
            "identity_required": True,
            "sandbox_required": False,
            "permissions": ["read"],
            "approval_required": True,
            "elicitation_modes": ["accept", "decline", "cancel"],
        },
    )
    assert unsafe.status_code == 200
    assert unsafe.json()["adapter"]["status"] == "denied"
    assert unsafe.json()["adapter"]["execution_enabled"] is False
    assert unsafe.json()["adapter"]["deny_reason"] == "sandbox_required"

    client.post(
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
    safe = client.post(
        "/ops/brain/protocol/adapters/mcp/policy",
        json={
            "enable_requested": True,
            "server_id": "browsermcp",
            "identity_required": True,
            "sandbox_required": True,
            "permissions": ["read"],
            "approval_required": True,
            "elicitation_modes": ["accept", "decline", "cancel"],
        },
    )
    assert safe.status_code == 200
    safe_payload = safe.json()
    assert safe_payload["adapter"]["status"] == "enabled_gated"
    assert safe_payload["adapter"]["execution_enabled"] is False
    assert safe_payload["adapter"]["reason"] == "enabled_but_requires_user_consent_per_attempt"
    assert safe_payload["adapter"]["policy"]["tool_id"] == "mcp::*"

    detail = client.get("/ops/brain/protocol/adapters/mcp")
    assert detail.status_code == 200
    assert detail.json()["adapter"]["status"] == "enabled_gated"
    assert detail.json()["adapter"]["policy"]["approval_required"] is True
