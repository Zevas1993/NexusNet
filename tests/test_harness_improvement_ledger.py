from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.agents.harnesses.ledger import HarnessImprovementLedger, HarnessLedgerEntryRequest
from tests.test_nexus_phase1_foundation import make_project


def test_harness_improvement_ledger_records_shadow_validated_harness_diff():
    ledger = HarnessImprovementLedger()

    entry = ledger.record(
        HarnessLedgerEntryRequest(
            entry_id="harness-ledger::context-router-v2",
            harness_id="harness::nexusnet-agent-loop",
            change_type="context_management",
            proposer="ResearcherSwarm",
            diff_summary="Route repeated canon prompts through project-local prefix cache and source-aware context packs.",
            source_refs=["docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md"],
            shadow_run_refs=["shadow::context-router-v2"],
            optimization_eval_refs=["eval::dev-routing"],
            heldout_eval_refs=["eval::heldout-agent-loop"],
            baseline_score=0.71,
            candidate_score=0.82,
            regression_failures=[],
            security_review_passed=True,
            rollback_plan="restore-context-router-v1",
            operator_approved=True,
        )
    )

    assert entry["status_label"] == "LOCKED CANON"
    assert entry["authority"] == "NexusBrain"
    assert entry["surface_id"] == "harness-improvement-ledger"
    assert entry["status"] == "shadow-validated"
    assert entry["promotion_allowed"] is True
    assert entry["score_delta"] == 0.11
    assert entry["policy_scan"]["summary"]["allow_merge"] is True


def test_harness_improvement_ledger_blocks_heldout_leak_or_missing_gates():
    ledger = HarnessImprovementLedger()

    entry = ledger.record(
        {
            "entry_id": "harness-ledger::unsafe-self-tune",
            "harness_id": "harness::agent-loop",
            "change_type": "planner",
            "proposer": "autonomous-update",
            "diff_summary": "Tune harness directly against the public heldout suite.",
            "source_refs": [],
            "shadow_run_refs": [],
            "optimization_eval_refs": ["eval::heldout-agent-loop"],
            "heldout_eval_refs": ["eval::heldout-agent-loop"],
            "baseline_score": 0.8,
            "candidate_score": 0.79,
            "regression_failures": ["tool-routing-regression"],
            "security_review_passed": False,
            "rollback_plan": "",
            "operator_approved": False,
        }
    )

    assert entry["status"] == "blocked"
    assert entry["promotion_allowed"] is False
    assert entry["runtime_state"] == "degraded"
    assert {
        "harness_ledger_requires_source_refs",
        "harness_ledger_requires_shadow_runs",
        "harness_ledger_blocks_heldout_overlap",
        "harness_ledger_requires_positive_score_delta",
        "harness_ledger_requires_security_review",
        "harness_ledger_requires_rollback_plan",
        "harness_ledger_requires_operator_approval",
    }.issubset({finding["rule_id"] for finding in entry["ledger_findings"]})


def test_harness_improvement_ledger_blocks_upstream_self_review_gate():
    ledger = HarnessImprovementLedger()

    entry = ledger.record(
        {
            "entry_id": "harness-ledger::blocked-review-router",
            "harness_id": "harness::agent-loop",
            "change_type": "tool_routing",
            "proposer": "autonomous-update",
            "diff_summary": "Route harness planner through a newly generated tool arbitration policy.",
            "source_refs": ["docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md"],
            "shadow_run_refs": ["shadow::blocked-review-router"],
            "optimization_eval_refs": ["eval::tool-routing-dev"],
            "heldout_eval_refs": ["eval::tool-routing-heldout"],
            "baseline_score": 0.72,
            "candidate_score": 0.84,
            "regression_failures": [],
            "security_review_passed": True,
            "rollback_plan": "restore-tool-router-v1",
            "operator_approved": True,
            "upstream_self_review_gate": {
                "status": "blocked",
                "review_state": "blocked-by-review",
                "review_id": "review::blocked-eval-adapter",
                "upstream_eval_gate": {
                    "promotion_allowed": False,
                    "blockers": ["self_review_blocks_eval_promotion_gate"],
                    "upstream_lifecycle_gate": {
                        "lifecycle_status": "closed_loop_blocked",
                        "blockers": ["growth_engine_adapter_training_gate_blocked"],
                    },
                },
            },
        }
    )

    assert entry["status"] == "blocked"
    assert entry["promotion_allowed"] is False
    assert entry["upstream_self_review_gate"]["review_state"] == "blocked-by-review"
    assert "growth_engine_adapter_training_gate_blocked" in entry["upstream_self_review_gate"]["blockers"]
    assert {
        "harness_ledger_blocks_self_review_gate",
        "harness_ledger_blocks_upstream_eval_gate",
    }.issubset({finding["rule_id"] for finding in entry["ledger_findings"]})

    scorecard = ledger.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["blocked_count"] == 1
    assert scorecard["latest_entry"]["status"] == "blocked"


def test_harness_ledger_api_visualizer_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/evolution/harness-ledger/entries",
        json={
            "entry_id": "harness-ledger::api-tool-router",
            "harness_id": "harness::api-agent-loop",
            "change_type": "tool_routing",
            "proposer": "NexusBrain",
            "diff_summary": "Add a deterministic tool preflight gate before autonomous tool execution.",
            "source_refs": ["docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md"],
            "shadow_run_refs": ["shadow::api-tool-router"],
            "optimization_eval_refs": ["eval::tool-routing-dev"],
            "heldout_eval_refs": ["eval::tool-routing-heldout"],
            "baseline_score": 0.73,
            "candidate_score": 0.81,
            "regression_failures": [],
            "security_review_passed": True,
            "rollback_plan": "restore-tool-router-v1",
            "operator_approved": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "shadow-validated"

    summary = client.get("/ops/brain/evolution/harness-ledger")
    assert summary.status_code == 200
    assert summary.json()["entry_count"] == 1

    scorecard = client.get("/ops/brain/canon/harness-ledger")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["record"]["endpoint"] == "/ops/brain/evolution/harness-ledger/entries"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "harness-ledger-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["harness_improvement_ledger"]["entry_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "harness-ledger-cockpit"}).json()
    assert blackbox["scorecard_refs"]["harness_improvement_ledger"] == "/ops/brain/canon/harness-ledger"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Harness Improvement Ledger" in ui.text
    assert "harnessImprovementLedger" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderHarnessImprovementLedger" in app_js
    assert "/ops/brain/canon/harness-ledger" in app_js
    harness_renderer = app_js[
        app_js.index("function renderHarnessImprovementLedger"):
        app_js.index("function renderEdgeWorkloadRouterScorecard")
    ]
    assert "upstream self-review gate" in harness_renderer
    assert "upstream_self_review_gate" in harness_renderer
