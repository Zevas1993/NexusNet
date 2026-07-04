from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_hardware_matrix_operational_endpoint_aliases_canon_scorecard(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/hardware-matrix", params={"session_id": "hardware-matrix-alias"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "hardware-matrix"
    assert {"WebNN", "WebGPU", "Windows NPU", "CPU", "Server GPU"}.issubset(
        {lane["lane_id"] for lane in payload["deployment_lanes"]}
    )
    assert payload["operator_actions"]["inspect"]["endpoint"] == "/ops/brain/hardware-matrix"
    assert payload["operator_actions"]["scorecard"]["endpoint"] == "/ops/brain/canon/hardware-matrix"
