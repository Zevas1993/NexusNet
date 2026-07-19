from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.operations.assimilation_catalog import AssimilationTargetCatalog
from tests.test_nexus_phase1_foundation import make_project


def test_catalog_parses_all_144_numbered_specs():
    catalog = AssimilationTargetCatalog()
    summary = catalog.summary()

    assert summary["surface_id"] == "assimilation-target-catalog"
    assert summary["online_target_count"] == 134
    assert summary["video_target_count"] == 10
    assert summary["target_count"] == 144
    # Every target starts as a gated research candidate; none auto-promoted.
    assert summary["started_count"] == 144
    assert summary["promoted_count"] == 0
    assert all(target["lifecycle_state"] == "started-research-candidate" for target in summary["targets"])
    assert all(target["production_promotion_allowed"] is False for target in summary["targets"])


def test_catalog_target_carries_parsed_spec_fields():
    catalog = AssimilationTargetCatalog()

    target = catalog.get("09-mcp-security-dynamic-red-team-spec")
    assert target is not None
    assert target["priority"] == "P0"
    assert target["source_kind"] == "online"
    assert "zero-trust MCP" in target["assimilation_target"]
    assert target["proposed_components"]  # parsed component list is non-empty
    assert target["promotion_gates"]      # parsed promotion gates non-empty
    assert target["source_urls"]          # at least one source URL captured
    assert target["spec_sha256"].startswith("sha256:")


def test_every_catalog_target_is_bound_to_the_live_governed_assimilation_spine():
    catalog = AssimilationTargetCatalog()
    targets = catalog.summary()["targets"]

    assert len(targets) == 144
    for target in targets:
        contract = target["implementation_contract"]
        assert contract["authority"] == "NexusBrain"
        assert contract["execution_mode"] == "evidence-only"
        assert contract["production_mutation_allowed"] is False
        assert contract["promotion_requires_target_evidence"] is True
        assert contract["source_integrity_ref"] == target["spec_sha256"]
        assert contract["target_spec_ref"] == target["spec_path"]
        assert {
            "/ops/brain/canon/developmental-cortex",
            "/ops/brain/canon/authority-spine",
            "/ops/brain/canon/evidence-store",
            "/ops/brain/canon/tool-action-harness",
            "/ops/brain/canon/runtime-decision-ledger",
        } == set(contract["governed_surfaces"])


def test_catalog_priority_breakdown_matches_specs():
    catalog = AssimilationTargetCatalog()
    breakdown = catalog.summary()["priority_counts"]

    # From a header survey of the 134 online specs.
    assert breakdown["P0"] == 7
    assert breakdown["P1"] == 85
    assert breakdown["P2"] == 38
    assert breakdown["P3"] == 4
    # Video specs are tracked as candidate priority.
    assert breakdown["candidate"] == 10


def test_catalog_endpoint_and_control_panel_surface(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/canon/assimilation-target-catalog")
    assert response.status_code == 200
    payload = response.json()
    assert payload["target_count"] == 144
    assert payload["promoted_count"] == 0

    detail = client.get("/ops/brain/assimilation-target-catalog/25-browsergym-web-agent-harness-spec")
    assert detail.status_code == 200
    assert detail.json()["priority"] == "P1"

    control_panel = client.get(
        "/ops/brain/visualizer/state", params={"session_id": "catalog"}
    ).json()["overlay_state"]["control_panel"]
    scorecard = control_panel["assimilation_target_catalog_scorecard"]
    assert scorecard["target_count"] == 144
    assert scorecard["started_count"] == 144
