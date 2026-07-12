from pathlib import Path

from fastapi.testclient import TestClient

from nexus import services as services_module
from nexus.api.app import create_app
from nexusnet.evolution import FoundationVerifier
from tests.test_nexus_phase1_foundation import make_project


def test_evolution_endpoints_are_nexusbrain_owned_and_read_only(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))
    state = client.get("/ops/brain/evolution/everything-state")
    units = client.get("/ops/brain/evolution/evolvable-units")
    pressure = client.get("/ops/brain/evolution/growth-pressure")
    status = client.get("/ops/brain/evolution/status")
    assert [response.status_code for response in (state, units, pressure, status)] == [
        200,
        200,
        200,
        200,
    ]
    assert state.json()["authority"] == "NexusBrain"
    assert units.json()["coverage"]["legacy_taxonomy_fully_covered"] is True
    assert units.json()["coverage"]["universal_coverage_complete"] is False
    assert pressure.json()["items"] == []
    assert status.json()["mutation_boundary"] == (
        "read-only-no-protected-state-mutation"
    )
    prerequisite_checks = {
        check["foundation_id"].removeprefix("foundation:"): check
        for check in state.json()["prerequisite_checks"]
    }
    assert prerequisite_checks["neural_bus"]["status"] == "unverified"
    assert prerequisite_checks["hive_blackboard"]["status"] == "unverified"
    assert status.json()["missing_or_unverified_prerequisites"] == [
        "hive_blackboard",
        "neural_bus",
    ]
    expected_interfaces = {
        "checkpoint": "rewind_checkpoint",
        "rollback": "rollback_governed_route_candidate",
    }
    substrate = client.app.state.services.brain_hive_substrate
    for prerequisite, interface_name in expected_interfaces.items():
        check = prerequisite_checks[prerequisite]
        assert check["status"] == "verified"
        assert check["evidence_ref"] == (
            f"service:HiveNeuralSubstrate:{interface_name}"
        )
        assert callable(getattr(substrate, interface_name, None))
    evidence_refs = {
        check["evidence_ref"]
        for check in prerequisite_checks.values()
        if check["evidence_ref"] is not None
    }
    assert "service:HiveNeuralSubstrate:checkpoint" not in evidence_refs
    assert "service:HiveNeuralSubstrate:rollback" not in evidence_refs


def test_wrapper_status_projects_sanitized_evolution_without_session_identifier(
    tmp_path: Path,
):
    client = TestClient(create_app(str(make_project(tmp_path))))
    card = client.get(
        "/ops/wrapper/status-card", params={"session_id": "private-user-123"}
    ).json()
    assert card["evolution"]["authority"] == "NexusBrain"
    assert card["evolution"]["coverage"]["universal_coverage_complete"] is False
    assert "private-user-123" not in str(card["evolution"])


def test_optional_hive_prerequisites_remain_unverified_without_callable_interfaces():
    class IncompleteHiveSubstrate:
        rewind_checkpoint = None
        replay = "not-callable"

    evidence = services_module._universal_evolution_prerequisite_evidence(
        IncompleteHiveSubstrate()
    )
    checks = {
        check.prerequisite: check
        for check in FoundationVerifier(evidence).verify()
    }

    for prerequisite in ("checkpoint", "replay", "rollback"):
        assert prerequisite not in evidence
        assert checks[prerequisite].status == "unverified"
        assert checks[prerequisite].evidence_ref is None
