from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_package_candidate_ingest_is_metadata_only_and_fail_closed(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/package-candidates/ingest",
        json={
            "source_type": "npm",
            "source_ref": "@plannotator/pi-extension@0.19.1",
            "workspace_id": "default",
            "manifest": {
                "name": "@plannotator/pi-extension",
                "version": "0.19.1",
                "license": "MIT OR Apache-2.0",
                "nexusnet_package": {
                    "tools": ["plan.review"],
                    "skills": ["plannotator-compound"],
                    "prompts": ["plan-review"],
                    "themes": ["review-status-widget"],
                    "providers": ["browser-plan-review"],
                    "workflow_templates": ["nexus-plan-review-loop"],
                    "plan_review_plugins": ["visual-annotation"],
                    "permissions": ["filesystem.write", "network.external"],
                },
            },
            "metadata": {
                "repository": "https://github.com/backnotprop/plannotator",
                "dist": {"provenance": True},
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["source_type"] == "npm"
    assert payload["source_ref"] == "@plannotator/pi-extension@0.19.1"
    assert payload["candidate_state"] == "candidate_only"
    assert payload["execution_allowed"] is False
    assert payload["enablement_state"] == "disabled_until_certified"
    assert payload["sandbox_posture"] == "deny_execution_until_review"
    assert payload["license_review"]["status"] == "requires_review"
    assert {"filesystem.write", "network.external"} <= set(payload["requested_permissions"])
    assert payload["classification"]["resource_types"]["plan_review_plugins"] == ["visual-annotation"]
    assert payload["policy"]["mutation_requires_policy_grant"] is True
    assert Path(payload["artifact_path"]).exists()

    candidates = client.get("/ops/brain/package-candidates")
    assert candidates.status_code == 200
    candidates_json = candidates.json()
    assert candidates_json["candidate_count"] == 1
    assert candidates_json["latest_candidate"]["candidate_id"] == payload["candidate_id"]
    assert candidates_json["event_log"]["event_type_counts"]["package_candidate.ingested"] == 1


def test_package_candidate_rejects_unknown_source_and_surfaces_denial(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/package-candidates/ingest",
        json={
            "source_type": "curl-pipe",
            "source_ref": "https://example.invalid/install.sh",
            "manifest": {"name": "unsafe-installer", "nexusnet_package": {"tools": ["shell.exec"]}},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["candidate_state"] == "rejected"
    assert payload["execution_allowed"] is False
    assert payload["policy"]["decision"] == "deny"
    assert "unsupported-source-type" in payload["risk_flags"]
    assert "shell-exec-risk" in payload["risk_flags"]
    assert payload["enablement_state"] == "disabled"
