from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def _client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(str(make_project(tmp_path))))


def test_authority_spine_endpoint_and_decision(tmp_path: Path):
    client = _client(tmp_path)

    decision = client.post(
        "/ops/brain/authority-spine/decisions",
        json={
            "action_id": "action:cp-write",
            "effect_type": "filesystem_write",
            "sandbox_state": "none",
            "operator_approved": False,
            "evidence_refs": ["trace:cp"],
        },
    ).json()
    assert decision["status"] == "blocked"
    assert "write_effect_requires_sandbox" in decision["blockers"]

    summary = client.get("/ops/brain/canon/authority-spine").json()
    assert summary["surface_id"] == "authority-integrity-spine"
    assert summary["decision_count"] >= 1


def test_evidence_eval_tool_runtime_endpoints_serve(tmp_path: Path):
    client = _client(tmp_path)

    assert client.get("/ops/brain/canon/evidence-store").json()["surface_id"] == "content-addressed-evidence-store"
    assert client.get("/ops/brain/canon/eval-federation").json()["surface_id"] == "eval-federation"
    assert client.get("/ops/brain/canon/tool-action-harness").json()["surface_id"] == "tool-action-harness"
    assert client.get("/ops/brain/canon/runtime-decision-ledger").json()["surface_id"] == "runtime-decision-ledger"


def test_control_panel_exposes_developmental_support_scorecards(tmp_path: Path):
    client = _client(tmp_path)

    control_panel = client.get(
        "/ops/brain/visualizer/state", params={"session_id": "dev-support"}
    ).json()["overlay_state"]["control_panel"]

    for key, surface_id in [
        ("authority_spine_scorecard", "authority-integrity-spine"),
        ("evidence_store_scorecard", "content-addressed-evidence-store"),
        ("eval_federation_scorecard", "eval-federation"),
        ("tool_action_harness_scorecard", "tool-action-harness"),
        ("runtime_decision_ledger_scorecard", "runtime-decision-ledger"),
    ]:
        assert control_panel[key]["surface_id"] == surface_id
