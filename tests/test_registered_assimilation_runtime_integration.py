from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.operations.assimilation_targets import (
    ASSIMILATION_TARGETS,
    AssimilationTargetRegistry,
    _canon_ledger_entry,
)
from tests.test_nexus_phase1_foundation import make_project


CANON_LEDGER_FIELDS = {
    "entry_id",
    "date_added",
    "status",
    "source_refs",
    "original_book_status",
    "delta_type",
    "affected_lanes",
    "canon_effect",
    "implementation_refs",
    "validation_refs",
    "security_or_policy_gates",
    "rollback_or_sidebar_rule",
}


def test_every_registered_assimilation_target_has_a_complete_book_canon_ledger_entry():
    registry = AssimilationTargetRegistry()
    targets = [*registry.scorecard()["targets"], *registry.video_scorecard()["targets"]]

    assert len(targets) == 22
    for target in targets:
        ledger = target["canon_ledger"]
        assert CANON_LEDGER_FIELDS == set(ledger)
        assert ledger["entry_id"] == f"ASML-{target['target_id']}"
        assert ledger["source_refs"] == target["source_ids"]
        assert ledger["implementation_refs"] == target["implementation_refs"]
        assert ledger["affected_lanes"]
        assert ledger["validation_refs"]
        assert ledger["security_or_policy_gates"]
        assert "promotion" in ledger["rollback_or_sidebar_rule"].lower()


def test_canon_ledger_rejects_a_future_target_without_required_provenance():
    incomplete_target = deepcopy(ASSIMILATION_TARGETS[0])
    incomplete_target.pop("implementation_refs")

    with pytest.raises(ValueError, match="missing Canon ledger inputs: implementation_refs"):
        _canon_ledger_entry(incomplete_target)


def test_every_registered_assimilation_target_has_a_live_governed_operational_surface(tmp_path):
    client = TestClient(create_app(str(make_project(tmp_path))))
    registry = AssimilationTargetRegistry()
    targets = [*registry.scorecard()["targets"], *registry.video_scorecard()["targets"]]

    assert len(targets) == 22
    for target in targets:
        target_id = target["target_id"]
        binding = target["runtime_binding"]
        assert binding["evidence_endpoint"].startswith("/ops/brain/")
        assert binding["policy_endpoint"].startswith("/ops/brain/")
        assert binding["verification_test"].startswith("tests/")
        for endpoint in {
            binding["operational_endpoint"],
            binding["evidence_endpoint"],
            binding["policy_endpoint"],
        }:
            response = client.get(endpoint)
            assert response.status_code == 200, f"{target_id}: {endpoint}"
            assert response.json(), f"{target_id}: {endpoint}"

    evolution = client.get("/ops/brain/inference-evolution").json()
    assert evolution["moe_architecture_intake"]["implementation_state"] == "available"
    assert evolution["moe_architecture_intake"]["policy_mutation_allowed"] is False
