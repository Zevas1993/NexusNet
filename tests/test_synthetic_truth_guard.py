from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.memory.quality_ledger import MemoryQualityLedger, SourceClaimRequest
from tests.test_nexus_phase1_foundation import make_project


def test_synthetic_truth_guard_blocks_transcript_only_promotion():
    ledger = MemoryQualityLedger()

    claim = ledger.record_claim(
        SourceClaimRequest(
            claim_id="claim::video-only",
            answer_id="answer::assimilation",
            claim_text="The demo proves production-safe self-modification.",
            answerability_status="source_backed",
            source_status="transcript_only",
            source_refs=["video::demo-transcript"],
            confidence=0.91,
            promotion_state="canon_candidate",
        )
    )

    assert claim["status"] == "blocked"
    assert claim["source_status"] == "transcript_only"
    assert "claim_source_status_blocks_promotion" in {finding["rule_id"] for finding in claim["quality_findings"]}
    assert claim["abstention_reward"] == 0.0


def test_synthetic_truth_guard_rewards_explicit_unknown():
    ledger = MemoryQualityLedger()

    claim = ledger.record_claim(
        {
            "claim_id": "claim::unknown",
            "answer_id": "answer::assimilation",
            "claim_text": "No primary source was verified for this claim.",
            "answerability_status": "explicit_unknown",
            "source_status": "unverified",
            "confidence": 0.0,
            "promotion_state": "blocked",
            "uncertainty_label": "not_verified",
        }
    )

    assert claim["status"] == "verified"
    assert claim["abstention_reward"] == 1.0
    assert claim["answerability_gate"] == "explicit-unknown"


def test_synthetic_truth_guard_api_exposes_source_status(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/memory-quality/claims",
        json={
            "claim_id": "claim::api-contradiction",
            "answer_id": "answer::api",
            "claim_text": "Conflicting source claim.",
            "answerability_status": "conflicting",
            "source_status": "contradicted",
            "source_refs": ["source::a"],
            "contradiction_refs": ["source::b"],
            "confidence": 0.5,
            "promotion_state": "canon_candidate",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked"
    assert payload["source_status"] == "contradicted"
    assert payload["promotion_state"] == "canon_candidate"
