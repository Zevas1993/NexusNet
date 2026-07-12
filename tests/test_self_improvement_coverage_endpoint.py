"""The unified self-improvement coverage is reachable from the running service (live API)."""
from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_self_improvement_coverage_endpoint_serves_every_aspect(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))
    resp = client.get("/ops/brain/canon/self-improvement-coverage")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["surface_id"] == "self-improvement-coverage"
    # the compute-layer self-improvement is reachable and spans every aspect
    assert payload["every_aspect_covered"] is True
    assert payload["total_aspects"] >= 20
    assert payload["covered_count"] == payload["total_aspects"]
    assert payload["uncovered"] == []
    assert "efficiency_quant" in payload["covered"] and "wrapper_absorption" in payload["covered"]
    assert payload["legacy_taxonomy_fully_covered"] is True
    assert payload["universal_coverage_complete"] is False
    assert payload["claim_boundary"] == (
        "legacy-lane-coverage-is-not-universal-organism-coverage"
    )
