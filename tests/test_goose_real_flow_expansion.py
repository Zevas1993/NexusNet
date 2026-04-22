from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_goose_scheduled_recipe_execution_persists_execution_linkage(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/chat",
        json={
            "session_id": "goose-scheduled-recipe",
            "message": "Track a scheduled Goose recipe execution.",
            "wrapper_mode": "scheduled-monitor",
            "rag": False,
        },
    )
    assert chat.status_code == 200
    trace_id = chat.json()["trace_id"]

    response = client.post(
        "/ops/brain/recipes/execute",
        json={
            "recipe_id": "ao-deep-research",
            "trigger_source": "schedule:scheduled-monitor",
            "schedule_id": "scheduled-monitor",
            "session_id": "goose-scheduled-recipe",
            "parameter_set": {"topic": "Scheduled recipe linkage"},
            "status": "success",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    scheduled_artifact = payload["scheduled_artifact"]
    assert scheduled_artifact["artifact_kind"] == "scheduled-execution"
    assert payload["execution_id"] in scheduled_artifact["linked_execution_ids"]
    assert payload["report"]["report_id"] in scheduled_artifact["linked_report_ids"]
    assert trace_id in scheduled_artifact["linked_trace_ids"]

    filtered_history = client.get("/ops/brain/agents/scheduled/history", params={"workflow_id": "scheduled-monitor"})
    assert filtered_history.status_code == 200
    filtered_json = filtered_history.json()
    assert filtered_json["latest_artifact"]["artifact_id"] == scheduled_artifact["artifact_id"]
    assert filtered_json["latest_linked_trace_ids"][0] == trace_id

    wrapper = client.get("/ops/brain/wrapper-surface").json()
    scheduled = wrapper["goose"]["scheduled"]["history"]
    assert scheduled["latest_artifacts_by_workflow"]["scheduled-monitor"]["artifact_id"] == scheduled_artifact["artifact_id"]
    assert payload["report"]["report_id"] in scheduled["latest_artifacts_by_workflow"]["scheduled-monitor"]["linked_report_ids"]

    visualizer = client.get("/ops/brain/visualizer/state").json()
    runtime_posture = visualizer["overlay_state"]["runtime_posture"]
    assert runtime_posture["goose_latest_scheduled_execution_id"] == payload["execution_id"]
    assert runtime_posture["goose_latest_scheduled_linked_trace_id"] == trace_id
    assert runtime_posture["goose_latest_scheduled_linked_report_id"] == payload["report"]["report_id"]


def test_goose_scheduled_subagent_plan_records_scheduled_artifact(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/subagents/plan",
        json={
            "recipe_id": "ao-deep-research",
            "parent_task": "Expand a scheduled monitoring worker plan.",
            "mode": "parallel",
            "trigger_source": "schedule:scheduled-monitor",
            "schedule_id": "scheduled-monitor",
            "linked_trace_ids": ["trace-scheduled-plan"],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["execution"]["trigger_source"] == "schedule:scheduled-monitor"
    assert payload["scheduled_artifact"] is not None
    assert payload["execution_history"]["execution_id"] in payload["scheduled_artifact"]["linked_execution_ids"]
    assert "trace-scheduled-plan" in payload["scheduled_artifact"]["linked_trace_ids"]


def test_goose_acp_operator_diagnostics_expose_readiness_and_extension_compatibility(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    health = client.get("/ops/brain/acp/health")
    assert health.status_code == 200
    health_json = health.json()
    assert "misconfigured_count" in health_json
    assert "version_mismatch_count" in health_json
    assert "feature_incompatible_count" in health_json
    assert "failure_pattern_counts" in health_json

    provider = client.get("/ops/brain/acp/providers/acp-local-coder")
    assert provider.status_code == 200
    provider_json = provider.json()
    assert provider_json["operator_summary"]["headline"]
    assert provider_json["operator_summary"]["recommended_action"]
    assert provider_json["compatibility_example"]["requested_extensions"] == ["acp-coding-lane"]
    assert provider_json["compatibility_example"]["supported_extensions"]
    assert provider_json["compatibility_example"]["compatible"] is False

    compatibility = client.post(
        "/ops/brain/acp/compatibility",
        json={
            "requested_tools": ["filesystem.write"],
            "requested_extensions": ["acp-coding-lane"],
            "subagent_mode": "parallel",
        },
    )
    assert compatibility.status_code == 200
    compatibility_json = compatibility.json()
    item = next(entry for entry in compatibility_json["items"] if entry["provider_id"] == "acp-local-coder")
    assert item["requested_extensions"] == ["acp-coding-lane"]
    assert item["supported_extensions"] == ["acp-coding-lane", "mcp-filesystem"]
    assert item["compatible"] is False
    assert item["readiness_summary"]


def test_goose_adversary_review_flags_extension_acp_privilege_confusion(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    review = client.post(
        "/ops/brain/security/adversary-review",
        json={
            "subject": "subagents::acp-privilege-confusion",
            "requested_tools": ["provider.acp"],
            "requested_extensions": ["acp-coding-lane"],
            "allowed_tools": ["retrieval.query"],
            "allowed_extensions": ["local-retrieval-pack"],
            "risk_level": "high",
            "reviewer_status": "available",
            "trigger_source": "subagent-plan:parallel",
            "approval_requested": True,
            "approval_required": True,
        },
    )
    assert review.status_code == 200
    review_json = review.json()
    assert review_json["decision"] == "escalate"
    assert "extension-acp-privilege-inheritance-confusion-risk" in review_json["risk_families"]
    assert review_json["fail_open_allowed"] is False

    detail = client.get(f"/ops/brain/security/adversary-reviews/{review_json['review_id']}")
    assert detail.status_code == 200
    detail_json = detail.json()
    assert "acp-coding-lane" in detail_json["report_payload"]["requested_extensions"]
    assert "local-retrieval-pack" in detail_json["report_payload"]["allowed_extensions"]
