from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.research.forward_radar import ForwardRadarCandidateRequest, ForwardRadarRegistry
from tests.test_nexus_phase1_foundation import make_project


def test_forward_radar_registry_promotes_candidate_only_after_all_evidence_gates():
    registry = ForwardRadarRegistry()

    review = registry.review(
        "radar::turboquant-kv",
        ForwardRadarCandidateRequest(
            radar_id="radar::turboquant-kv",
            title="TurboQuant KV cache candidate",
            lane="runtime-cache",
            summary="Track TurboQuant as a KV-cache compression candidate for long-context serving.",
            source_refs=["https://research.google/blog/turboquant", "docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md"],
            source_quality="primary",
            license_status="approved",
            security_review="passed",
            runtime_evidence_refs=["bench::long-context-cache"],
            eval_refs=["eval::needle-recall"],
            observability_refs=["trace::cache-ledger"],
            rollback_plan="disable-turboquant-kv-policy",
            operator_approved=True,
            open_first=True,
            local_first=True,
        ),
    )

    assert review["status_label"] == "LOCKED CANON"
    assert review["authority"] == "NexusBrain"
    assert review["surface_id"] == "forward-radar"
    assert review["radar_id"] == "radar::turboquant-kv"
    assert review["status"] == "promotion-ready"
    assert review["promotion_allowed"] is True
    assert review["gate_summary"]["passed_gate_count"] == 8
    assert review["policy_scan"]["summary"]["allow_merge"] is True


def test_forward_radar_registry_keeps_under_evidenced_candidate_on_watchlist():
    registry = ForwardRadarRegistry()

    review = registry.review(
        "radar::agent-platform-claim",
        {
            "radar_id": "radar::agent-platform-claim",
            "title": "Agent platform claim",
            "lane": "agent-harness",
            "summary": "Unverified hosted-agent feature claim.",
            "source_refs": [],
            "source_quality": "unverified",
            "license_status": "needs_review",
            "security_review": "needs_review",
            "runtime_evidence_refs": [],
            "eval_refs": [],
            "observability_refs": [],
            "rollback_plan": "",
            "operator_approved": False,
        },
    )

    assert review["status"] == "watchlist"
    assert review["promotion_allowed"] is False
    assert review["gate_summary"]["failed_gate_count"] >= 7
    assert {
        "forward_radar_requires_primary_or_verified_source",
        "forward_radar_requires_approved_license",
        "forward_radar_requires_runtime_evidence",
        "forward_radar_requires_eval_refs",
        "forward_radar_requires_rollback_plan",
        "forward_radar_requires_operator_approval",
    }.issubset({finding["rule_id"] for finding in review["review_findings"]})


def test_forward_radar_registry_blocks_candidate_with_blocked_upstream_harness_gate():
    registry = ForwardRadarRegistry()

    review = registry.review(
        "radar::blocked-harness-router",
        {
            "radar_id": "radar::blocked-harness-router",
            "title": "Blocked harness router candidate",
            "lane": "agent-harness",
            "summary": "Track a tool-routing improvement whose upstream harness evidence is blocked.",
            "source_refs": ["docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md"],
            "source_quality": "primary",
            "license_status": "approved",
            "security_review": "passed",
            "runtime_evidence_refs": ["bench::tool-router-shadow"],
            "eval_refs": ["eval::tool-router-heldout"],
            "observability_refs": ["trace::harness-ledger"],
            "rollback_plan": "restore-tool-router-v1",
            "operator_approved": True,
            "upstream_harness_ledger_gate": {
                "promotion_allowed": False,
                "status": "blocked",
                "entry_id": "harness-ledger::blocked-review-router",
                "upstream_self_review_gate": {
                    "status": "blocked",
                    "review_state": "blocked-by-review",
                    "blockers": ["harness_ledger_blocks_self_review_gate"],
                    "upstream_eval_gate": {
                        "promotion_allowed": False,
                        "blockers": ["self_review_blocks_eval_promotion_gate"],
                    },
                },
            },
        },
    )

    assert review["status"] == "blocked"
    assert review["promotion_allowed"] is False
    assert review["upstream_harness_ledger_gate"]["promotion_allowed"] is False
    assert "self_review_blocks_eval_promotion_gate" in review["upstream_harness_ledger_gate"]["blockers"]
    assert {
        "forward_radar_blocks_harness_ledger_gate",
        "forward_radar_blocks_upstream_self_review_gate",
        "forward_radar_blocks_upstream_eval_gate",
    }.issubset({finding["rule_id"] for finding in review["review_findings"]})

    scorecard = registry.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["blocked_count"] == 1
    assert scorecard["latest_candidate"]["status"] == "blocked"


def test_forward_radar_api_visualizer_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/forward-radar/radar::lmcache/review",
        json={
            "radar_id": "radar::lmcache",
            "title": "LMCache KV reuse",
            "lane": "runtime-cache",
            "summary": "Track LMCache-style KV reuse for repeated canon and AO context.",
            "source_refs": ["https://docs.lmcache.ai/developer_guide/architecture.html"],
            "source_quality": "primary",
            "license_status": "approved",
            "security_review": "passed",
            "runtime_evidence_refs": ["cache::api-vllm-prefix"],
            "eval_refs": ["eval::cache-regression"],
            "observability_refs": ["trace::api-agent"],
            "rollback_plan": "disable-lmcache-runtime-target",
            "operator_approved": True,
            "open_first": True,
            "local_first": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "promotion-ready"

    summary = client.get("/ops/brain/forward-radar")
    assert summary.status_code == 200
    assert summary.json()["candidate_count"] == 1

    item = client.get("/ops/brain/forward-radar/radar::lmcache")
    assert item.status_code == 200
    assert item.json()["title"] == "LMCache KV reuse"

    scorecard = client.get("/ops/brain/canon/forward-radar")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["review"]["endpoint"] == "/ops/brain/forward-radar/{radar_id}/review"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "forward-radar-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["forward_radar_scorecard"]["candidate_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "forward-radar-cockpit"}).json()
    assert blackbox["scorecard_refs"]["forward_radar"] == "/ops/brain/canon/forward-radar"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Forward Radar Registry" in ui.text
    assert "forwardRadarScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderForwardRadarScorecard" in app_js
    assert "/ops/brain/canon/forward-radar" in app_js
    forward_renderer = app_js[
        app_js.index("function renderForwardRadarScorecard"):
        app_js.index("function renderEvalSuiteScorecard")
    ]
    assert "upstream harness-ledger gate" in forward_renderer
    assert "upstream_harness_ledger_gate" in forward_renderer
