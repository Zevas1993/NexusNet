from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.computer_fabric.bridges import BridgeManager, JsonHttpBridgeAdapter
from nexusnet.computer_fabric import ComputerFabricService
from tests.test_nexus_phase1_foundation import make_project


class RecordingAdapter:
    def __init__(self) -> None:
        self.messages: list[dict[str, object]] = []

    def probe(self) -> dict[str, object]:
        return {"healthy": True, "detail": "ready"}

    def send(self, destination: str, payload: dict[str, object]) -> dict[str, object]:
        self.messages.append({"destination": destination, "payload": payload})
        return {"transport_id": "transport-1"}


def test_bridge_manager_redacts_approves_and_dispatches_through_registered_adapter(tmp_path: Path):
    adapter = RecordingAdapter()
    manager = BridgeManager(artifacts_dir=tmp_path, adapters={"recording": adapter})
    manager.register_bridge(
        {
            "bridge_id": "ops",
            "transport": "recording",
            "permissions": ["send"],
            "redaction_policy": "pii-secrets-local-paths",
        }
    )

    commitment = manager.prepare_outbound(
        bridge_id="ops",
        destination="alerts",
        payload={
            "text": "contact me@example.com with sk-secret123 from F:\\private\\model.gguf",
        },
    )

    assert "me@example.com" not in commitment["sanitized_payload"]["text"]
    assert "sk-secret123" not in commitment["sanitized_payload"]["text"]
    assert "F:\\private\\model.gguf" not in commitment["sanitized_payload"]["text"]
    with pytest.raises(PermissionError, match="approval"):
        manager.dispatch(commitment["commitment_id"])

    manager.approve(commitment["commitment_id"], approved_by="operator")
    receipt = manager.dispatch(commitment["commitment_id"])

    assert receipt["state"] == "dispatched"
    assert receipt["transport_receipt"] == {"transport_id": "transport-1"}
    assert adapter.messages[0]["payload"] == commitment["sanitized_payload"]
    persisted = (tmp_path / "bridges" / "receipts" / f"{commitment['commitment_id']}.json").read_text(encoding="utf-8")
    assert "sk-secret123" not in persisted


def test_bridge_manager_blocks_dispatch_when_transport_probe_is_unhealthy(tmp_path: Path):
    class UnhealthyAdapter(RecordingAdapter):
        def probe(self) -> dict[str, object]:
            return {"healthy": False, "detail": "offline"}

    manager = BridgeManager(artifacts_dir=tmp_path, adapters={"recording": UnhealthyAdapter()})
    manager.register_bridge(
        {"bridge_id": "ops", "transport": "recording", "permissions": ["send"]}
    )
    commitment = manager.prepare_outbound(bridge_id="ops", destination="alerts", payload={"text": "safe"})
    manager.approve(commitment["commitment_id"], approved_by="operator")

    with pytest.raises(RuntimeError, match="unhealthy"):
        manager.dispatch(commitment["commitment_id"])


def test_bridge_catalog_and_pending_commitment_survive_restart(tmp_path: Path):
    adapter = RecordingAdapter()
    manager = BridgeManager(artifacts_dir=tmp_path, adapters={"recording": adapter})
    manager.register_bridge(
        {"bridge_id": "durable", "transport": "recording", "permissions": ["send"]}
    )
    commitment = manager.prepare_outbound(
        bridge_id="durable",
        destination="alerts",
        payload={"text": "persist me"},
    )

    restarted = BridgeManager(artifacts_dir=tmp_path, adapters={"recording": adapter})
    summary = restarted.summary()
    assert summary["bridge_count"] == 1
    assert summary["commitment_count"] == 1
    restarted.approve(commitment["commitment_id"], approved_by="operator")
    dispatched = restarted.dispatch(commitment["commitment_id"])

    assert dispatched["state"] == "dispatched"
    assert adapter.messages[0]["payload"] == {"text": "persist me"}


def test_computer_fabric_supplies_a_working_local_artifact_bridge(tmp_path: Path):
    service = ComputerFabricService(artifacts_dir=tmp_path)
    manager = service.bridge_manager
    manager.register_bridge(
        {"bridge_id": "local-log", "transport": "local-artifact", "permissions": ["send"]}
    )
    commitment = manager.prepare_outbound(
        bridge_id="local-log",
        destination="inference-events",
        payload={"text": "inference complete"},
    )
    manager.approve(commitment["commitment_id"], approved_by="operator")

    receipt = manager.dispatch(commitment["commitment_id"])

    message_path = Path(receipt["transport_receipt"]["artifact_path"])
    assert message_path.exists()
    assert "inference complete" in message_path.read_text(encoding="utf-8")


def test_bridge_manager_api_runs_approved_local_dispatch(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))
    registered = client.post(
        "/ops/brain/bridges",
        json={"bridge_id": "local-log", "transport": "local-artifact", "permissions": ["send"]},
    )
    assert registered.status_code == 200

    prepared = client.post(
        "/ops/brain/bridges/commitments",
        json={
            "bridge_id": "local-log",
            "destination": "runtime-events",
            "payload": {"text": "ready"},
        },
    )
    assert prepared.status_code == 200
    commitment_id = prepared.json()["commitment_id"]

    approved = client.post(
        f"/ops/brain/bridges/commitments/{commitment_id}/approve",
        json={"approved_by": "operator"},
    )
    assert approved.status_code == 200
    dispatched = client.post(f"/ops/brain/bridges/commitments/{commitment_id}/dispatch")

    assert dispatched.status_code == 200
    assert dispatched.json()["state"] == "dispatched"
    assert Path(dispatched.json()["transport_receipt"]["artifact_path"]).exists()

    summary = client.get("/ops/brain/bridges")
    assert summary.status_code == 200
    assert summary.json()["bridge_count"] == 1
    assert summary.json()["commitment_count"] == 1
    assert summary.json()["raw_payload_exposed"] is False
    assert "sanitized_payload" not in summary.json()["recent_commitments"][0]


def test_json_http_bridge_adapter_probes_and_posts_sanitized_payload(tmp_path: Path):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread

    received: list[bytes] = []

    class Handler(BaseHTTPRequestHandler):
        def do_HEAD(self) -> None:
            self.send_response(200)
            self.end_headers()

        def do_POST(self) -> None:
            received.append(self.rfile.read(int(self.headers.get("Content-Length") or 0)))
            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"message_id":"remote-1"}')

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        adapter = JsonHttpBridgeAdapter(
            endpoint=f"http://127.0.0.1:{server.server_port}/hook",
            allow_private_network=True,
        )
        manager = BridgeManager(artifacts_dir=tmp_path, adapters={"webhook": adapter})
        manager.register_bridge({"bridge_id": "web", "transport": "webhook", "permissions": ["send"]})
        commitment = manager.prepare_outbound(
            bridge_id="web",
            destination="ignored-by-webhook",
            payload={"text": "email me@example.com"},
        )
        manager.approve(commitment["commitment_id"], approved_by="operator")
        receipt = manager.dispatch(commitment["commitment_id"])
    finally:
        server.shutdown()
        thread.join(timeout=5)

    assert receipt["transport_health"]["healthy"] is True
    assert receipt["transport_receipt"]["status_code"] == 202
    assert receipt["transport_receipt"]["response"] == {"message_id": "remote-1"}
    assert b"me@example.com" not in received[0]
