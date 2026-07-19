from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def _teacher_candidate(candidate_id: str, role: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "model_or_tool_id": f"internal/{candidate_id}",
        "provider": "nexusnet-test-provider",
        "source_url": f"https://example.invalid/{candidate_id}",
        "candidate_status": "shadow",
        "teacher_roles": [role],
        "license_gate": "approved",
        "privacy_gate": "approved",
        "hardware_gate": "approved",
        "cost_gate": "approved",
        "eval_family": ["high-risk-research-birth"],
        "domain_scope": ["research"],
        "risk_scope": ["high"],
        "source_refs": [f"teacher-source::{candidate_id}"],
        "benchmark_refs": [f"teacher-benchmark::{candidate_id}"],
    }


def test_layer13_teacher_candidates_gate_and_replay_high_risk_temporary_expert_birth(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    blocked = client.post(
        "/ops/brain/genesis-node-contracts/temporary-children",
        json={
            "child_id": "high-risk-research-child-blocked",
            "parent_contract_ref": "expert-contract::researcher",
            "domain": "research",
            "risk_tier": "high",
            "teacher_ids": [],
            "capability_refs": ["research-analysis"],
            "source_refs": ["research-source::birth-request"],
        },
    )
    assert blocked.status_code == 400

    blocked_summary = client.get("/ops/brain/genesis-teacher-governance").json()
    assert blocked_summary["birth_verification_count"] == 1
    assert blocked_summary["blocked_birth_count"] == 1
    assert blocked_summary["latest_birth_verification"]["status"] == "blocked-teacher-birth-verification"
    assert "teacher_pairing_below_minimum" in blocked_summary["latest_birth_verification"]["findings"]

    generator = client.post(
        "/ops/brain/genesis-teacher-governance/candidates",
        json=_teacher_candidate("research-generator-cleared", "generator"),
    )
    reviewer = client.post(
        "/ops/brain/genesis-teacher-governance/candidates",
        json=_teacher_candidate("research-verifier-cleared", "verifier"),
    )
    assert generator.status_code == 200
    assert reviewer.status_code == 200
    assert generator.json()["teacher_capability_passport"]["promotion_allowed"] is True
    assert reviewer.json()["teacher_capability_passport"]["promotion_allowed"] is True

    accepted = client.post(
        "/ops/brain/genesis-node-contracts/temporary-children",
        json={
            "child_id": "high-risk-research-child-verified",
            "parent_contract_ref": "expert-contract::researcher",
            "domain": "research",
            "risk_tier": "high",
            "teacher_ids": ["research-generator-cleared", "research-verifier-cleared"],
            "capability_refs": ["research-analysis", "high-risk-review"],
            "source_refs": ["research-source::verified-birth-request"],
        },
    )
    assert accepted.status_code == 200
    child = accepted.json()
    verification = child["teacher_birth_verification"]
    assert verification["status"] == "teacher-birth-verified-shadow-only"
    assert verification["passed"] is True
    assert verification["distinct_teacher_count"] == 2
    assert verification["high_risk_domain_gate"]["passed"] is True
    assert verification["role_diversity_gate"]["generator_present"] is True
    assert verification["role_diversity_gate"]["reviewer_present"] is True
    assert len(verification["teacher_capability_passports"]) == 2
    assert child["expert_domain_passport"]["required_teacher_count"] == 2
    assert child["permanent_birth_allowed"] is False
    assert child["production_route_allowed"] is False

    summary = client.get("/ops/brain/genesis-teacher-governance").json()
    assert summary["persisted_candidate_intake_count"] == 2
    assert summary["birth_verification_count"] == 2
    assert summary["verified_birth_count"] == 1
    assert summary["blocked_birth_count"] == 1
    assert summary["latest_birth_verification"]["verification_id"] == verification["verification_id"]

    visualizer = client.get("/ops/brain/visualizer/state").json()
    ao_hive = next(
        page
        for page in visualizer["overlay_state"]["control_panel"]["pages"]
        if page["page_id"] == "ao-hive"
    )
    assert ao_hive["metrics"]["teacher_governance_status"] == "live-evidence"
    assert ao_hive["metrics"]["teacher_candidate_intake_count"] == 2
    assert ao_hive["metrics"]["verified_teacher_birth_count"] == 1
    assert ao_hive["metrics"]["blocked_teacher_birth_count"] == 1
    assert "/ops/brain/genesis-teacher-governance" in ao_hive["evidence_refs"]

    replay = TestClient(create_app(str(project_root))).get("/ops/brain/genesis-teacher-governance").json()
    assert replay["persisted_candidate_intake_count"] == 2
    assert replay["birth_verification_count"] == 2
    assert replay["verified_birth_count"] == 1
    assert replay["latest_birth_verification"]["verification_id"] == verification["verification_id"]

    serialized = json.dumps({"child": child, "summary": summary, "replay": replay})
    assert str(project_root) not in serialized
    assert "raw_prompt" not in serialized
    assert "raw_output" not in serialized
