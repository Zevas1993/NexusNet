from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.protocols.trust import ProtocolAdapterRequest, ProtocolTrustRegistry
from tests.test_nexus_phase1_foundation import make_project


def test_protocol_trust_registry_accepts_adapter_with_complete_trust_envelope():
    registry = ProtocolTrustRegistry()

    record = registry.register(
        ProtocolAdapterRequest(
            adapter_id="protocol::mcp-local-files",
            protocol="MCP",
            endpoint="stdio://local-filesystem",
            enabled=True,
            identity_ref="identity::local-operator",
            consent_ref="consent::project-workspace",
            permissions=["read:workspace", "list:resources"],
            revocation_ref="revocation::disable-mcp-local-files",
            sandboxed=True,
        )
    )

    assert record["status_label"] == "LOCKED CANON"
    assert record["authority"] == "NexusBrain"
    assert record["status"] == "trusted-shadow"
    assert record["trust_envelope"]["complete"] is True
    assert record["policy_scan"]["summary"]["allow_merge"] is True


def test_protocol_trust_registry_blocks_enabled_adapter_without_identity_consent_or_revocation():
    registry = ProtocolTrustRegistry()

    record = registry.register(
        {
            "adapter_id": "protocol::a2a-unknown",
            "protocol": "A2A",
            "endpoint": "https://agents.example.invalid/a2a",
            "enabled": True,
            "identity_ref": "",
            "consent_ref": "",
            "permissions": [],
            "revocation_ref": "",
            "sandboxed": False,
        }
    )

    assert record["status"] == "blocked"
    assert record["trust_envelope"]["complete"] is False
    assert {
        "protocol_adapter_requires_identity",
        "protocol_adapter_requires_consent",
        "protocol_adapter_requires_permissions",
        "protocol_adapter_requires_revocation",
    }.issubset({finding["rule_id"] for finding in record["trust_findings"]})
    assert "protocol_adapter_requires_trust_envelope" in {
        finding["rule_id"] for finding in record["policy_scan"]["findings"]
    }

    scorecard = registry.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["blocked_count"] == 1
    assert scorecard["latest_adapter"]["status"] == "blocked"


def test_protocol_trust_registry_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/protocol-trust/adapters",
        json={
            "adapter_id": "protocol::ag-ui-control-panel",
            "protocol": "AG-UI",
            "endpoint": "http://127.0.0.1:8765/ui/control-panel/events",
            "enabled": True,
            "identity_ref": "identity::control-panel",
            "consent_ref": "consent::operator-session",
            "permissions": ["emit:events", "read:state"],
            "revocation_ref": "revocation::disable-ag-ui-control-panel",
            "sandboxed": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "trusted-shadow"

    summary = client.get("/ops/brain/protocol-trust")
    assert summary.status_code == 200
    assert summary.json()["adapter_count"] == 1

    scorecard = client.get("/ops/brain/canon/protocol-trust-registry")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert "mcp_a2a_acp_agui_adapters" in scorecard_payload["required_controls"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "protocol-trust-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["protocol_trust_registry_scorecard"]["adapter_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "protocol-trust-cockpit"}).json()
    assert blackbox["scorecard_refs"]["protocol_trust_registry"] == "/ops/brain/canon/protocol-trust-registry"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Protocol Trust Registry" in ui.text
    assert "protocolTrustRegistryScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderProtocolTrustRegistryScorecard" in app_js
    assert "/ops/brain/canon/protocol-trust-registry" in app_js
