from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
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
