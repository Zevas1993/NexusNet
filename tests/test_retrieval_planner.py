from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.retrieval.planner import RetrievalPlanner, RetrievalPlanRequest
from tests.test_nexus_phase1_foundation import make_project


def test_retrieval_planner_requires_evidence_threshold_and_modes():
    planner = RetrievalPlanner()

    plan = planner.plan(
        RetrievalPlanRequest(
            plan_id="retrieval-plan::complex",
            user_goal="Explain whether the Jarvis repo is safe to assimilate.",
            source_classes=["repo", "video_transcript", "primary_source"],
            query_decomposition=["verify license", "map high-authority actions", "extract safe NexusNet transfers"],
            retrieval_modes=["lexical", "semantic", "graph", "temporal", "rerank"],
            evidence_threshold=0.8,
            cost_budget_ms=2500,
        )
    )

    assert plan["status_label"] == "LOCKED CANON"
    assert plan["surface_id"] == "retrieval-planner"
    assert plan["status"] == "planned"
    assert plan["claim_ledger_contract"]["requires_source_status"] is True
    assert {"lexical", "semantic", "graph", "temporal", "rerank"} == set(plan["retrieval_modes"])
    assert "critic_loop" in plan["required_controls"]


def test_retrieval_planner_blocks_low_threshold_deep_retrieval():
    planner = RetrievalPlanner()

    plan = planner.plan(
        {
            "plan_id": "retrieval-plan::unsafe",
            "user_goal": "Make a canon claim from one weak source.",
            "source_classes": ["video_transcript"],
            "query_decomposition": [],
            "retrieval_modes": ["semantic"],
            "evidence_threshold": 0.25,
            "cost_budget_ms": 0,
        }
    )

    assert plan["status"] == "blocked"
    assert "retrieval_plan_requires_decomposition" in {finding["rule_id"] for finding in plan["planner_findings"]}
    assert "retrieval_plan_requires_evidence_threshold" in {finding["rule_id"] for finding in plan["planner_findings"]}


def test_retrieval_planner_api(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/retrieval/plans",
        json={
            "plan_id": "retrieval-plan::api",
            "user_goal": "Answer with source-backed claims only.",
            "source_classes": ["primary_source", "repo"],
            "query_decomposition": ["find primary source", "check contradiction"],
            "retrieval_modes": ["lexical", "rerank"],
            "evidence_threshold": 0.7,
            "cost_budget_ms": 1500,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "planned"
    summary = client.get("/ops/brain/retrieval/planner")
    assert summary.status_code == 200
    assert summary.json()["plan_count"] == 1
