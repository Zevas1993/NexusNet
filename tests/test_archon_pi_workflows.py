from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_workflow_catalog_loads_starter_dags_and_rejects_invalid_shapes(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    summary = services.brain_workflows.summary()
    workflow_ids = {item["workflow_id"] for item in summary["items"]}
    assert {
        "nexus-idea-to-validation",
        "nexus-package-candidate-review",
        "nexus-plan-review-loop",
    } <= workflow_ids
    assert summary["validation"]["ok"] is True
    assert summary["workflow_count"] >= 3

    valid = services.brain_workflows.validate_payload(
        {
            "workflow_id": "valid-inline",
            "label": "Valid Inline",
            "nodes": [
                {"id": "plan", "kind": "prompt", "prompt": "Draft the plan."},
                {"id": "approve", "kind": "approval", "depends_on": ["plan"], "approval": {"mode": "human"}},
                {"id": "validate", "kind": "validation", "depends_on": ["approve"], "validation": {"commands": ["pytest --collect-only -q"]}},
            ],
        }
    )
    assert valid["ok"] is True
    assert valid["topological_order"] == ["plan", "approve", "validate"]

    invalid = services.brain_workflows.validate_payload(
        {
            "workflow_id": "unsafe-inline",
            "label": "Unsafe Inline",
            "nodes": [
                {"id": "plan", "kind": "prompt", "depends_on": ["missing"], "prompt": "Draft the plan."},
                {"id": "plan", "kind": "bash", "bash": "rm -rf ."},
                {"id": "mystery", "kind": "external-exec"},
            ],
        }
    )
    reasons = {error["reason"] for error in invalid["errors"]}
    assert invalid["ok"] is False
    assert {"duplicate-node-id", "missing-dependency", "unsupported-node-kind", "unsafe-bash-command"} <= reasons

    cyclic = services.brain_workflows.validate_payload(
        {
            "workflow_id": "cyclic-inline",
            "label": "Cyclic Inline",
            "nodes": [
                {"id": "a", "kind": "prompt", "depends_on": ["b"], "prompt": "A"},
                {"id": "b", "kind": "prompt", "depends_on": ["a"], "prompt": "B"},
            ],
        }
    )
    assert cyclic["ok"] is False
    assert any(error["reason"] == "cycle-detected" for error in cyclic["errors"])


def test_workflow_execution_records_gated_path_gateway_and_events(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/workflows/execute",
        json={
            "workflow_id": "nexus-package-candidate-review",
            "trigger_source": "manual:test",
            "workspace_id": "default",
            "parameter_set": {"source_type": "npm", "source_ref": "@plannotator/pi-extension"},
            "requested_tools": ["filesystem.readonly", "network.external"],
            "requested_extensions": ["mcp-filesystem"],
            "approval_path": {"decision": "ask"},
            "linked_trace_ids": ["trace-workflow-001"],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["workflow_id"] == "nexus-package-candidate-review"
    assert payload["status"] in {"approval_required", "validation_pending", "gated"}
    assert Path(payload["artifact_path"]).exists()
    assert payload["report"]["report_id"]
    assert payload["execution_history"]["execution_kind"] == "workflow"
    assert payload["execution_history"]["recipe_id"] == "nexus-package-candidate-review"
    assert payload["execution_history"]["gateway_decision_path"]
    assert payload["execution_history"]["extension_provenance"]
    assert "workflow-dag" in payload["execution_history"]["flow_families"]

    node_states = {node["node_id"]: node for node in payload["node_states"]}
    assert node_states["ingest-candidate"]["status"] == "recorded"
    assert node_states["operator-approval"]["status"] == "approval_required"
    assert node_states["certification-review"]["status"] == "validation_pending"
    assert payload["execution_allowed"] is False
    assert payload["mutation_allowed"] is False

    history = client.get("/ops/brain/workflows/history", params={"workflow_id": "nexus-package-candidate-review"})
    assert history.status_code == 200
    history_json = history.json()
    assert history_json["execution_count"] >= 1
    assert history_json["latest_execution"]["execution_id"] == payload["execution_history"]["execution_id"]
    assert "workflow.start" in history_json["event_type_counts"]
    assert "workflow.node.end" in history_json["event_type_counts"]

    summary = client.get("/ops/brain/workflows")
    assert summary.status_code == 200
    summary_json = summary.json()
    assert summary_json["history"]["latest_execution_id"] == payload["execution_history"]["execution_id"]
    assert summary_json["event_log"]["latest_event"]["event_type"] in {"workflow.end", "workflow.node.end"}
