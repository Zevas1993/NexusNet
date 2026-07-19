"""Genesis Layer 2 authority decisions must enter the shared event spine."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def _execution_scope(*, project_root: Path, target: str) -> dict[str, str]:
    return {
        "tool_ref": "fs",
        "action_type": "read",
        "target": target,
        "sandbox_root_digest": hashlib.sha256(
            str(project_root.resolve()).encode("utf-8")
        ).hexdigest(),
    }


def _authorized_lease(client: TestClient, *, project_root: Path, target: str) -> str:
    response = client.post(
        "/ops/brain/execution-authority/leases/request",
        json={
            "capability": "deterministic_tool_boundary",
            "scope": _execution_scope(project_root=project_root, target=target),
            "expires_at": "2099-01-01T00:00:00+00:00",
            "budget": {"max_usd": 0.0, "max_minutes": 1},
            "rollback_plan": {"strategy": "no-mutation-readonly"},
            "approval_id": "approval::tool-event-spine",
            "approval_decision": "approved",
            "gateway_decision": "allow",
            "product_sweep_gate_ids": ["tool-event-spine"],
            "product_sweep_decision": "passed",
            "requested_execution": True,
            "requested_mutation": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["lease"]["status"] == "granted"
    return response.json()["lease"]["lease_id"]


def test_authorized_tool_execution_publishes_replayable_genesis_event(tmp_path: Path):
    project_root = make_project(tmp_path)
    target = "authority-event-source.txt"
    (project_root / target).write_text("tool event raw secret", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))
    session_id = "authority-event-session-SECRET"
    lease_id = _authorized_lease(client, project_root=project_root, target=target)

    execution = client.post(
        "/ops/brain/tools/actions/execute",
        json={
            "action_id": "authority-event-allow",
            "tool_ref": "fs",
            "action_type": "read",
            "target": target,
            "evidence_refs": ["evidence::authority-event-secret"],
            "lease_id": lease_id,
            "capability": "deterministic_tool_boundary",
            "session_id": session_id,
        },
    )

    assert execution.status_code == 200
    payload = execution.json()
    assert payload["status"] == "executed-readonly"
    event = payload["shared_event_spine"]
    assert event["event_type"] == "genesis.execution_authority.tool_action.executed"
    assert event["event_ref"].startswith("genesis-event::")
    assert event["raw_content_included"] is False

    replay = client.get("/ops/brain/genesis-event-spine", params={"session_id": session_id}).json()
    replay_event = next(item for item in replay["events"] if item["event_ref"] == event["event_ref"])
    assert replay_event["correlation_ref"] == payload["execution_id"]
    assert replay_event["event_type"] == event["event_type"]
    assert replay["blackboard_snapshot_count"] == replay["event_count"]
    assert replay["plane_trace_count"] == replay["event_count"]
    serialized = json.dumps({"event": event, "replay": replay}, sort_keys=True)
    assert session_id not in serialized
    assert "authority-event-secret" not in serialized
    assert "tool event raw secret" not in serialized
    assert str(project_root) not in serialized


def test_blocked_tool_execution_publishes_replayable_genesis_event(tmp_path: Path):
    project_root = make_project(tmp_path)
    target = "authority-event-source.txt"
    (project_root / target).write_text("blocked tool event raw secret", encoding="utf-8")
    client = TestClient(create_app(str(project_root)))
    session_id = "authority-event-blocked-session-SECRET"

    execution = client.post(
        "/ops/brain/tools/actions/execute",
        json={
            "action_id": "authority-event-blocked",
            "tool_ref": "fs",
            "action_type": "read",
            "target": target,
            "evidence_refs": ["evidence::authority-event-blocked-secret"],
            "capability": "deterministic_tool_boundary",
            "session_id": session_id,
        },
    )

    assert execution.status_code == 200
    payload = execution.json()
    assert payload["status"] == "blocked-authority"
    event = payload["shared_event_spine"]
    assert event["event_type"] == "genesis.execution_authority.tool_action.blocked"
    assert event["event_ref"].startswith("genesis-event::")

    replay = client.get("/ops/brain/genesis-event-spine", params={"session_id": session_id}).json()
    assert any(item["event_ref"] == event["event_ref"] for item in replay["events"])
    serialized = json.dumps({"event": event, "replay": replay}, sort_keys=True)
    assert session_id not in serialized
    assert "authority-event-blocked-secret" not in serialized
    assert "blocked tool event raw secret" not in serialized
    assert str(project_root) not in serialized
