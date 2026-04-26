from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_product_sweep_gatekeeper_exposes_all_phase_gates_and_blocks_training(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/product-sweep/gates")
    assert response.status_code == 200
    payload = response.json()
    assert payload["phase_count"] == 10
    assert payload["ready_for_real_training"] is False
    assert payload["safe_to_promote_checkpoint"] is False

    gates = {gate["phase_id"]: gate for gate in payload["phase_gates"]}
    assert set(gates) == {f"phase-{index}" for index in range(10)}
    assert gates["phase-5"]["status"] == "implemented_gated"
    assert "/ops/brain/security/protocol/*" in gates["phase-5"]["operator_surfaces"]
    assert gates["phase-8"]["status"] == "gated"
    assert {
        "eval_report_required",
        "approved_license_required",
        "security_gate_pass_required",
    } <= set(gates["phase-8"]["blocked_by"])


def test_product_sweep_status_aggregates_live_surfaces_without_overclaiming(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/product-sweep/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "active_gated_buildout"
    assert payload["product_status"]["training"]["real_training_status"] == "gated"
    assert payload["gate_summary"]["ready_for_real_training"] is False
    assert payload["status_surfaces"]["memory_os"]["persistent"] is True
    assert payload["status_surfaces"]["runtime"]["raw_million_token_context"] == "unresolved"
    assert payload["status_surfaces"]["evals"]["scenario_count"] >= 5
    assert payload["status_surfaces"]["canon"]["unresolved_count"] > 0


def test_expert_council_and_shadow_simulation_remain_advisory_and_non_mutating(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    council = client.post(
        "/ops/brain/expert-council/deliberate",
        json={
            "prompt": "Should NexusNet promote external tools yet?",
            "selected_experts": ["security-guardian", "memory-weaver", "systems-architect"],
        },
    )
    assert council.status_code == 200
    council_payload = council.json()
    assert council_payload["status"] == "shadow_only"
    assert council_payload["decision_authority"] == "NexusBrain"
    assert council_payload["can_mutate_production"] is False
    assert council_payload["policy_bypass_allowed"] is False
    assert {proposal["authority"] for proposal in council_payload["proposals"]} == {"advisory_only"}

    simulation = client.post(
        "/ops/brain/product-sweep/shadow-simulation",
        json={"name": "protocol-risk-dream", "target": "external-tool-promotion"},
    )
    assert simulation.status_code == 200
    simulation_payload = simulation.json()
    assert simulation_payload["status"] == "shadow_only"
    assert simulation_payload["can_mutate_memory"] is False
    assert simulation_payload["can_mutate_models"] is False
    assert simulation_payload["promotion_allowed"] is False
