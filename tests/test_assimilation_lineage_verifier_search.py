from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.core.self_improvement import LineageCandidateRequest, SelfImprovementLineageRegistry
from nexusnet.evals import VerifierSearchRegistry, VerifierSearchRequest
from tests.test_nexus_phase1_foundation import make_project


def test_lineage_candidate_stays_shadow_and_records_anti_cheat_receipts():
    registry = SelfImprovementLineageRegistry()

    candidate = registry.record_candidate(
        LineageCandidateRequest(
            candidate_id="candidate::dgm-shadow",
            parent_ids=["candidate::root"],
            mutation_prompt="Improve retrieval plan scoring.",
            touched_files=["nexusnet/retrieval/planner.py"],
            eval_suite_refs=["eval::nexus-held-out"],
            command_receipts=[
                {"command": "pytest tests/test_retrieval_planner.py -q", "exit_code": 0, "artifact_hash": "sha256:abc"}
            ],
            scores={"pass_rate": 0.9, "safety": 0.95},
            transfer_results={"alternate_model": "passed"},
            safety_flags=[],
            reviewer_decision="shadow-passed",
        )
    )

    assert candidate["status"] == "shadow-passed"
    assert candidate["promotion_allowed"] is False
    assert candidate["anti_cheat_gate"]["real_receipts_present"] is True
    assert candidate["lineage"]["parent_ids"] == ["candidate::root"]


def test_lineage_blocks_fake_receipts_and_reward_hacking():
    registry = SelfImprovementLineageRegistry()

    candidate = registry.record_candidate(
        {
            "candidate_id": "candidate::unsafe",
            "parent_ids": [],
            "mutation_prompt": "Maximize benchmark by hiding failures.",
            "touched_files": ["nexusnet/evals/registry.py"],
            "eval_suite_refs": [],
            "command_receipts": [{"command": "pytest", "exit_code": 0}],
            "scores": {"pass_rate": 0.99, "safety": 0.4},
            "transfer_results": {},
            "safety_flags": ["reward_hacking_probe_failed"],
            "reviewer_decision": "safety-blocked",
        }
    )

    assert candidate["status"] == "safety-blocked"
    assert candidate["promotion_allowed"] is False
    assert "lineage_candidate_requires_hashable_command_receipts" in {
        finding["rule_id"] for finding in candidate["findings"]
    }
    assert "reward_hacking_probe_failed" in candidate["safety_flags"]


def test_verifier_search_records_multi_objective_candidate_database():
    registry = VerifierSearchRegistry()

    result = registry.record_search(
        VerifierSearchRequest(
            search_id="verifier-search::retrieval-policy",
            objective="Improve retrieval source faithfulness without increasing latency.",
            scorer_ref="scorer::source-faithfulness-v1",
            candidates=[
                {
                    "candidate_id": "candidate::fast",
                    "scores": {"quality": 0.72, "latency": 0.95, "safety": 0.9, "source_faithfulness": 0.6},
                },
                {
                    "candidate_id": "candidate::faithful",
                    "scores": {"quality": 0.86, "latency": 0.74, "safety": 0.94, "source_faithfulness": 0.91},
                },
            ],
            constraints={"minimum_source_faithfulness": 0.8, "minimum_safety": 0.85},
            evidence_refs=["eval::source-faithfulness-v1"],
        )
    )

    assert result["status_label"] == "LOCKED CANON"
    assert result["selected"]["candidate_id"] == "candidate::faithful"
    assert result["blocked_candidates"][0]["candidate_id"] == "candidate::fast"
    assert result["promotion_boundary"] == "verifier-search-results-remain-shadow-until-human-review"


def test_lineage_and_verifier_search_api(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    lineage = client.post(
        "/ops/brain/self-improvement/lineage/candidates",
        json={
            "candidate_id": "candidate::api",
            "parent_ids": ["candidate::root"],
            "mutation_prompt": "Create a retrieval planner.",
            "touched_files": ["nexusnet/retrieval/planner.py"],
            "eval_suite_refs": ["eval::api"],
            "command_receipts": [
                {"command": "pytest tests/test_retrieval_planner.py -q", "exit_code": 0, "artifact_hash": "sha256:def"}
            ],
            "scores": {"pass_rate": 0.88, "safety": 0.94},
            "transfer_results": {"alternate_model": "passed"},
            "safety_flags": [],
            "reviewer_decision": "teacher-approved",
        },
    )
    assert lineage.status_code == 200
    assert lineage.json()["status"] == "teacher-approved"

    search = client.post(
        "/ops/brain/verifier-search/runs",
        json={
            "search_id": "verifier-search::api",
            "objective": "Choose the safest retrieval planner candidate.",
            "scorer_ref": "scorer::api",
            "candidates": [
                {
                    "candidate_id": "candidate::api",
                    "scores": {"quality": 0.9, "latency": 0.8, "safety": 0.93, "source_faithfulness": 0.9},
                }
            ],
            "constraints": {"minimum_source_faithfulness": 0.8},
            "evidence_refs": ["eval::api"],
        },
    )
    assert search.status_code == 200
    assert search.json()["selected"]["candidate_id"] == "candidate::api"
