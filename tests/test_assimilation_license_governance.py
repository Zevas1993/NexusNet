from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_research_candidate_license_reviews_are_audited_and_persisted(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    review = client.post(
        "/ops/brain/research-candidates/qwen3-vl/license-review",
        json={
            "license_status": "blocked",
            "reviewer": "license-gate-test",
            "rationale": "Vision model candidate requires commercial-use confirmation before adoption.",
            "evidence": "operator license review",
        },
    )
    assert review.status_code == 200
    payload = review.json()
    assert payload["candidate"]["id"] == "qwen3-vl"
    assert payload["candidate"]["license_review"]["license_status"] == "blocked"
    assert payload["candidate"]["integration_status"] == "disabled"
    assert payload["audit_event"]["action"] == "assimilation.license.reviewed"

    second_client = TestClient(create_app(str(project_root)))
    candidate = second_client.get("/ops/brain/research-candidates/qwen3-vl")
    assert candidate.status_code == 200
    assert candidate.json()["candidate"]["license_review"]["rationale"].startswith("Vision model candidate")

    registry = second_client.get("/ops/brain/research-candidates")
    assert registry.status_code == 200
    assert registry.json()["license_summary"]["blocked"] >= 1
