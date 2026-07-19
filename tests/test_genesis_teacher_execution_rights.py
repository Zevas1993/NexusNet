from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def _cleared_candidate(candidate_id: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "model_or_tool_id": f"internal/{candidate_id}",
        "provider": "nexusnet-test-provider",
        "source_url": f"https://example.invalid/{candidate_id}",
        "candidate_status": "shadow",
        "teacher_roles": ["generator", "verifier"],
        "license_gate": "approved",
        "privacy_gate": "approved",
        "hardware_gate": "approved",
        "cost_gate": "approved",
        "eval_family": ["teacher-execution-rights"],
        "domain_scope": ["research"],
        "risk_scope": ["high"],
        "source_refs": [f"teacher-source::{candidate_id}"],
        "benchmark_refs": [f"teacher-benchmark::{candidate_id}"],
    }


def test_layer13_teacher_execution_requires_persisted_rights_receipt_and_replays(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    denied = client.post(
        "/ops/brain/teachers/attach",
        json={
            "teacher_id": "teacher-execution-uncleared",
            "model_hint": "mock/default",
            "usage_intent": "teacher-or-distillation",
        },
    )
    assert denied.status_code == 403
    assert "teacher" in denied.json()["detail"].lower()

    intake = client.post(
        "/ops/brain/genesis-teacher-governance/candidates",
        json=_cleared_candidate("teacher-execution-cleared"),
    )
    assert intake.status_code == 200

    attached = client.post(
        "/ops/brain/teachers/attach",
        json={
            "teacher_id": "teacher-execution-cleared",
            "model_hint": "mock/default",
            "usage_intent": "teacher-or-distillation",
        },
    )
    assert attached.status_code == 200
    payload = attached.json()
    rights = payload["provenance"]["teacher_use_rights"]
    assert rights["status"] == "authorized-teacher-or-distillation-use"
    assert rights["teacher_or_distillation_use_authorized"] is True
    assert rights["raw_content_included"] is False
    attachment = next(
        record
        for record in client.app.state.services.brain.model_ingestion.attachments()
        if record["adapter_key"] == "teacher:mock/default@mock"
    )
    layer11 = attachment["layer11_attach_contract"]
    assert layer11["status"] == "authorized-teacher-or-distillation"
    assert layer11["model_provider_contract"]["effective_usage"] == "teacher-or-distillation"
    assert layer11["rights_gate"]["teacher_or_distillation_use_authorized"] is True

    governance = client.get("/ops/brain/genesis-teacher-governance").json()
    assert governance["teacher_use_authorization_count"] == 2
    assert governance["authorized_teacher_use_count"] == 1
    assert governance["denied_teacher_use_count"] == 1
    assert governance["latest_teacher_use_authorization"]["authorization_id"] == rights["authorization_id"]

    replay = TestClient(create_app(str(project_root))).get("/ops/brain/genesis-teacher-governance").json()
    assert replay["teacher_use_authorization_count"] == 2
    assert replay["authorized_teacher_use_count"] == 1
    assert replay["denied_teacher_use_count"] == 1
