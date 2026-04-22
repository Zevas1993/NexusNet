from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_retrieval_rerank_scorecard_and_wrapper_visibility(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    scorecard = client.get("/ops/brain/retrieval/rerank-scorecard")
    assert scorecard.status_code == 200
    payload = scorecard.json()
    assert payload["scorecard"]["summary"]["case_count"] >= 3
    assert Path(payload["artifacts"]["scorecard"]).exists()

    wrapper = client.get("/ops/brain/wrapper-surface")
    assert wrapper.status_code == 200
    retrieval = wrapper.json()["retrieval"]
    assert retrieval["scorecards"]["latest_scorecard"]["scorecard_id"] == payload["scorecard"]["scorecard_id"]
    assert retrieval["compare_refs"]["rerank_scorecard"] == "/ops/brain/retrieval/rerank-scorecard"


def test_gateway_provenance_history_is_read_only_and_traceable(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    denied = client.get(
        "/ops/brain/gateway",
        params={
            "agent_id": "openclaw-agent",
            "workspace_id": "default",
            "requested_tools": "filesystem.readonly,unknown.tool",
        },
    )
    assert denied.status_code == 200
    denied_payload = denied.json()
    assert denied_payload["fallback_reason"] == "tool-outside-allowlist"
    assert denied_payload["policy"]["policy_path"]
    assert denied_payload["selected_skill_packages"]

    gated = client.get(
        "/ops/brain/gateway",
        params={
            "agent_id": "openclaw-agent",
            "workspace_id": "default",
            "requested_tools": "governance.audit",
        },
    )
    assert gated.status_code == 200
    assert gated.json()["policy"]["decision"] == "allow-if-approved"

    wrapper = client.get("/ops/brain/wrapper-surface", params={"session_id": "gateway-session"})
    assert wrapper.status_code == 200
    recent = wrapper.json()["gateway"]["recent_resolutions"]
    assert recent
    assert recent[0]["policy"]["decision"] in {"deny", "allow-if-approved"}


def test_edge_vision_benchmark_and_aitune_validation_are_inspectable(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    edge = client.get("/ops/brain/vision/edge-benchmark")
    assert edge.status_code == 200
    edge_payload = edge.json()
    assert edge_payload["summary"]["case_count"] >= 3
    assert Path(edge_payload["artifacts"]["metrics"]).exists()

    vision = client.get("/ops/brain/vision/edge-lane")
    assert vision.status_code == 200
    assert vision.json()["benchmark_summary"]["latest_benchmark"]["case_count"] >= 3

    aitune = client.get("/ops/brain/aitune/validation")
    assert aitune.status_code == 200
    aitune_payload = aitune.json()
    assert aitune_payload["current_status"] == "skipped"
    assert aitune_payload["matrix"]["scenarios"]
    assert Path(aitune_payload["artifact_path"]).exists()


def test_evalsao_persists_retrieval_scorecard_artifact(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))
    services.brain_retrieval_rerank_ops.run()

    report = services.brain_evaluator.run_recent(limit=10)
    assert "retrieval_rerank_scorecard" in report["artifacts"]
    assert Path(report["artifacts"]["retrieval_rerank_scorecard"]).exists()


def test_skill_evolution_proposals_and_attention_benchmark_are_governed_and_read_only(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    proposals = client.post(
        "/ops/brain/skill-evolution/proposals",
        json=[
            {"trajectory_id": "t1", "tool_sequence": ["filesystem.readonly", "retrieval.query"]},
            {"trajectory_id": "t2", "tool_sequence": ["filesystem.readonly", "retrieval.query"]},
            {"trajectory_id": "t3", "tool_sequence": ["governance.audit"]},
        ],
    )
    assert proposals.status_code == 200
    proposal_payload = proposals.json()
    assert proposal_payload["proposals"]
    assert proposal_payload["proposals"][0]["status"] == "shadow"
    assert proposal_payload["repository"]["proposal_count"] >= 2

    attention = client.get("/ops/brain/attention-providers/benchmark")
    assert attention.status_code == 200
    attention_payload = attention.json()
    assert attention_payload["summary"]["case_count"] >= 4
    assert Path(attention_payload["artifacts"]["metrics"]).exists()
