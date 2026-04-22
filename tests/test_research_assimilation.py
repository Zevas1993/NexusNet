from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexus.schemas import Message, RetrievalDocumentInput, RetrievalIngestRequest
from nexus.services import build_services
from nexusnet.tools.policy import GatewayPolicyEngine
from tests.test_nexus_phase1_foundation import make_project


def test_retrieval_rerank_benchmark_persists_two_stage_metrics(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    services.retrieval.ingest(
        RetrievalIngestRequest(
            documents=[
                RetrievalDocumentInput(
                    source="lexical-spec",
                    title="Reranking",
                    text="Cross-encoder reranking preserves grounded retrieval and records provenance.",
                ),
                RetrievalDocumentInput(
                    source="runtime-spec",
                    title="Gateway",
                    text="Gateway approvals and read-only policy visibility remain local-first.",
                ),
            ]
        )
    )
    services.memory.append_messages(
        "assimilation-rerank",
        [Message(role="user", content="Grounded retrieval and gateway approvals matter for NexusNet.")],
    )

    report = services.brain_retrieval_rerank_bench.run(
        query="grounded retrieval gateway approvals",
        session_id="assimilation-rerank",
        top_k=4,
    )

    assert report["metrics"]["with_rerank"]["top_k_before_rerank"] >= 1
    assert report["metrics"]["with_rerank"]["top_k_after_rerank"] >= 1
    assert report["metrics"]["with_rerank"]["reranker_provider"] is not None
    assert Path(report["artifacts"]["metrics"]).exists()
    assert Path(report["artifacts"]["report"]).exists()


def test_wrapper_surface_exposes_gateway_edge_lane_and_assimilation_status(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    chat = client.post(
        "/chat",
        json={
            "session_id": "assimilation-wrapper",
            "message": "Route this through the OpenClaw surface and inspect retrieval provenance.",
            "wrapper_mode": "openclaw",
            "teacher_id": "mixtral-8x7b",
            "rag": True,
            "metadata": {
                "requested_tools": ["filesystem.readonly", "retrieval.query"],
                "retrieval_policy": "lexical+graph-memory-temporal-rerank",
            },
        },
    )
    assert chat.status_code == 200

    wrapper = client.get("/ops/brain/wrapper-surface", params={"session_id": "assimilation-wrapper"})
    assert wrapper.status_code == 200
    payload = wrapper.json()
    assert payload["gateway"]["gateway_pattern"] == "local-control-plane"
    assert payload["vision_edge"]["default_provider"] == "lfm2.5-vl-450m"
    assert payload["vision_edge"]["teacher_candidates"][0]["subject"] == "vision"
    assert payload["assimilation"]["attention_research"]["providers"][0]["enabled"] is False
    assert payload["retrieval"]["recent_traces"]


def test_gateway_and_assimilation_endpoints_are_read_only_and_traceable(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    gateway = client.get(
        "/ops/brain/gateway",
        params={
            "agent_id": "openclaw-agent",
            "workspace_id": "default",
            "requested_tools": "filesystem.readonly,unknown.tool",
        },
    )
    assert gateway.status_code == 200
    gateway_payload = gateway.json()
    assert gateway_payload["policy"]["decision"] == "deny"
    assert "unknown.tool" in gateway_payload["policy"]["denied_tools"]

    vision = client.get("/ops/brain/vision/edge-lane")
    assert vision.status_code == 200
    assert vision.json()["providers"]["lfm2.5-vl-450m"]["function_calling"] is True

    assimilation = client.get("/ops/brain/assimilation/status")
    assert assimilation.status_code == 200
    assimilation_payload = assimilation.json()
    assert assimilation_payload["gateway"]["gateway_pattern"] == "local-control-plane"
    assert assimilation_payload["attention_research"]["providers"][0]["provider_name"] == "triattention"


def test_gateway_policy_denies_ambiguous_binding_and_requires_approval(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    gated = services.brain_gateway.resolve(
        agent_id="openclaw-agent",
        workspace_id="default",
        requested_tools=["governance.audit"],
    )
    assert gated["policy"]["decision"] == "allow-if-approved"
    assert "policy-approval-gate" in gated["policy"]["matched_skill_ids"]

    engine = GatewayPolicyEngine()
    ambiguous = engine.evaluate(
        agent_id="openclaw-agent",
        workspace_id="default",
        requested_tools=["ambiguous.tool"],
        visible_packages=[
            {
                "skill_id": "ambiguous-a",
                "precedence": 50,
                "allowed_tools": ["ambiguous.tool"],
                "approval_behavior": "allow",
            },
            {
                "skill_id": "ambiguous-b",
                "precedence": 50,
                "allowed_tools": ["ambiguous.tool"],
                "approval_behavior": "allow",
            },
        ],
    )
    assert ambiguous["decision"] == "deny"
    assert ambiguous["ambiguous_tools"] == ["ambiguous.tool"]
    assert ambiguous["deny_by_default_on_ambiguity"] is True


def test_edge_vision_and_aitune_summaries_expose_explicit_provider_metadata(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    edge_summary = services.brain_edge_vision.summary()
    provider = edge_summary["providers"]["lfm2.5-vl-450m"]
    assert edge_summary["default_provider"] == "lfm2.5-vl-450m"
    assert provider["provider_name"] == "lfm2.5-vl-450m"
    assert "compact edge-first design" in provider["design_lessons"]
    assert provider["function_calling"] is True
    assert "en" in provider["languages"]

    aitune_summary = services.brain_runtime_registry.summary()["aitune"]
    assert "edge-vision-lane" in aitune_summary["target_registry_ids"]
    assert any(item["lane"] == "Windows + Python 3.13 default dev flow" for item in aitune_summary["repo_audit"]["avoid"])


def test_attention_registry_defaults_off_and_skill_evolution_stays_governed(tmp_path: Path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    attention = services.brain_attention_registry.summary()
    assert attention["providers"][0]["provider_name"] == "triattention"
    assert attention["providers"][0]["enabled"] is False
    assert attention["providers"][0]["default_on"] is False

    repository = services.brain_skill_repository.summary()
    evolution = services.brain_skill_evolution.summarize_trajectories(
        [
            {"trajectory_id": "traj-1", "tool_sequence": ["filesystem.readonly", "retrieval.query"]},
            {"trajectory_id": "traj-2", "tool_sequence": ["filesystem.readonly", "retrieval.query"]},
        ]
    )
    proposal = services.brain_skill_refinement.propose(recurring_patterns=evolution["recurring_patterns"])
    assert repository["repository_kind"] == "governed-shared-skills"
    assert repository["items"][0]["rollback_ready"] is True
    assert evolution["status_label"] == "EXPLORATORY / PROTOTYPE"
    assert proposal["review_required"] is True
