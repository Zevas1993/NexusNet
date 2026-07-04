from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_plan_review_records_denial_resubmission_and_approval_without_execution(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    denial = client.post(
        "/ops/brain/plans/review",
        json={
            "plan_id": "archon-pi-assimilation-plan",
            "title": "Archon Pi Assimilation",
            "content": "# Plan\n\n- install arbitrary npm packages\n- run them in core",
            "decision": "denied",
            "reviewer": "operator",
            "annotations": [
                {
                    "line": 3,
                    "severity": "blocker",
                    "message": "Package execution must stay candidate-only until certified.",
                }
            ],
            "linked_workflow_id": "nexus-package-candidate-review",
        },
    )
    assert denial.status_code == 200
    denial_json = denial.json()
    assert denial_json["status"] == "changes_requested"
    assert denial_json["execution_allowed"] is False
    assert denial_json["latest_review"]["decision"] == "denied"
    assert denial_json["analytics"]["denied_count"] == 1
    assert denial_json["versions"][0]["version"] == 1
    assert Path(denial_json["artifact_path"]).exists()

    approval = client.post(
        "/ops/brain/plans/review",
        json={
            "plan_id": "archon-pi-assimilation-plan",
            "title": "Archon Pi Assimilation",
            "content": "# Plan\n\n- ingest packages as metadata-only candidates\n- require gateway and certification before use",
            "decision": "approved",
            "reviewer": "operator",
            "annotations": [{"line": 3, "severity": "info", "message": "Bounded candidate intake accepted."}],
            "linked_workflow_id": "nexus-package-candidate-review",
        },
    )
    assert approval.status_code == 200
    approval_json = approval.json()
    assert approval_json["status"] == "approved_for_validation"
    assert approval_json["execution_allowed"] is False
    assert approval_json["gateway_required"] is True
    assert approval_json["latest_review"]["decision"] == "approved"
    assert approval_json["versions"][-1]["version"] == 2
    assert approval_json["diff_from_previous"]["changed"] is True
    assert approval_json["analytics"]["approved_count"] == 1
    assert approval_json["analytics"]["denied_count"] == 1

    plans = client.get("/ops/brain/plans")
    assert plans.status_code == 200
    plans_json = plans.json()
    assert plans_json["plan_count"] == 1
    assert plans_json["latest_plan"]["plan_id"] == "archon-pi-assimilation-plan"
    assert plans_json["denial_analytics"]["common_blockers"]["Package execution must stay candidate-only until certified."] == 1
    assert plans_json["event_log"]["event_type_counts"]["plan.reviewed"] == 2


def test_plan_review_denies_execution_approval_language(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/plans/review",
        json={
            "title": "Unsafe Approval",
            "content": "Approval grants live execution and bypasses policy.",
            "decision": "approved",
            "reviewer": "operator",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "approved_for_validation"
    assert payload["execution_allowed"] is False
    assert payload["gateway_required"] is True
    assert "approval-is-not-execution-authority" in payload["risk_flags"]
