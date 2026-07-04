from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.memory.quality_ledger import MemoryQualityLedger, SourceClaimRequest
from tests.test_nexus_phase1_foundation import make_project


def test_memory_quality_ledger_verifies_source_backed_claim_with_graph_and_retrieval_evidence():
    ledger = MemoryQualityLedger()

    claim = ledger.record_claim(
        SourceClaimRequest(
            claim_id="claim::runtime-cache-economics",
            answer_id="answer::runtime-plan",
            claim_text="Long-context agentic workloads should use prefix caching and KV reuse when benchmark evidence supports it.",
            answerability_status="source_backed",
            source_refs=["docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md#inference-architecture"],
            memory_refs=["memory::runtime-architecture"],
            retrieval_refs=["retrieval::lmcache-notes"],
            graph_refs=["graph::runtime-cache-node"],
            evaluator_refs=["RAGChecker", "source-to-claim-verifier"],
            confidence=0.91,
        )
    )

    assert claim["status_label"] == "LOCKED CANON"
    assert claim["authority"] == "NexusBrain"
    assert claim["status"] == "verified"
    assert claim["answerability_gate"] == "source-backed"
    assert claim["quality_state"] == "claim-grounded"
    assert claim["policy_scan"]["summary"]["allow_merge"] is True
    assert claim["quality_findings"] == []
    assert {
        "source_to_claim_maps",
        "retrieval_quality",
        "answerability_gate",
        "staleness_check",
        "privacy_consent",
        "contradiction_check",
        "ragchecker_metrics",
    }.issubset(set(claim["required_controls"]))


def test_memory_quality_ledger_blocks_unsupported_private_or_conflicting_claims():
    ledger = MemoryQualityLedger()

    claim = ledger.record_claim(
        {
            "claim_id": "claim::unsafe-memory",
            "answer_id": "answer::unsupported",
            "claim_text": "The user's private note confirms this unreferenced conclusion.",
            "answerability_status": "unsupported",
            "source_refs": [],
            "memory_refs": ["memory::private-note"],
            "retrieval_refs": [],
            "graph_refs": [],
            "contains_private_data": True,
            "consent_ref": "",
            "contradiction_refs": ["memory::conflicting-note"],
            "evaluator_refs": [],
            "confidence": 0.42,
        }
    )

    assert claim["status"] == "blocked"
    assert claim["answerability_gate"] == "unsupported"
    assert claim["quality_state"] == "blocked-by-memory-quality"
    assert {
        "memory_claim_requires_source_to_claim_refs",
        "memory_claim_unsupported_answerability",
        "memory_claim_private_data_requires_consent",
        "memory_claim_conflict_requires_resolution",
        "memory_claim_low_confidence",
    }.issubset({finding["rule_id"] for finding in claim["quality_findings"]})
    assert claim["policy_scan"]["summary"]["allow_merge"] is False

    summary = ledger.scorecard()
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_count"] == 1
    assert summary["latest_claim"]["status"] == "blocked"


def test_memory_quality_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/memory-quality/claims",
        json={
            "claim_id": "claim::api-source-backed",
            "answer_id": "answer::api",
            "claim_text": "Every promoted NexusNet answer needs a source-to-claim map or an explicit unknown.",
            "answerability_status": "source_backed",
            "source_refs": ["docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md#memory-rag-and-knowledge-graphs"],
            "memory_refs": ["memory::source-claim-policy"],
            "retrieval_refs": ["retrieval::ragchecker"],
            "graph_refs": ["graph::memory-quality"],
            "evaluator_refs": ["RAGChecker"],
            "confidence": 0.88,
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "verified"

    summary = client.get("/ops/brain/memory-quality")
    assert summary.status_code == 200
    assert summary.json()["claim_count"] == 1

    scorecard = client.get("/ops/brain/canon/memory-quality")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["record_claim"]["endpoint"] == "/ops/brain/memory-quality/claims"
    assert "source_to_claim_maps" in scorecard_payload["required_controls"]
    assert {"GraphRAG", "LightRAG", "HippoRAG", "RAGChecker"}.issubset(
        {lane["lane_id"] for lane in scorecard_payload["research_lanes"]}
    )

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "memory-quality-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["memory_quality_scorecard"]["claim_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "memory-quality-cockpit"}).json()
    assert blackbox["scorecard_refs"]["memory_quality"] == "/ops/brain/canon/memory-quality"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Memory Quality Ledger" in ui.text
    assert "memoryQualityScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderMemoryQualityScorecard" in app_js
    assert "/ops/brain/canon/memory-quality" in app_js
