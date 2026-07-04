from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.core.self_review import SelfReviewGate, SelfReviewRequest
from tests.test_nexus_phase1_foundation import make_project


def test_self_review_gate_accepts_candidate_with_independent_verifier_and_clean_issue_log():
    gate = SelfReviewGate()

    review = gate.review(
        SelfReviewRequest(
            review_id="review::runtime-plan",
            candidate_id="update::runtime-shadow",
            candidate_type="runtime",
            target_surface="inference-architecture",
            reviewer_refs=["ao::runtime-reviewer", "expert::performance"],
            verifier_refs=["tool::pytest", "eval::runtime-held-out"],
            eval_refs=["eval::runtime-held-out"],
            evidence_refs=["/ops/brain/inference-architecture", "/ops/brain/eval-registry"],
            issues=[],
            uncertainty=0.12,
            operator_approved=True,
        )
    )

    assert review["status_label"] == "LOCKED CANON"
    assert review["authority"] == "NexusBrain"
    assert review["status"] == "accepted-shadow"
    assert review["review_state"] == "review-passed"
    assert review["review_findings"] == []
    assert review["policy_scan"]["summary"]["allow_merge"] is True
    assert {
        "independent_reviewers",
        "external_or_tool_verifier",
        "evidence_refs",
        "issue_log",
        "uncertainty_threshold",
        "operator_approval",
    }.issubset(set(review["required_controls"]))


def test_self_review_gate_blocks_self_only_review_missing_verifier_and_open_issues():
    gate = SelfReviewGate()

    review = gate.review(
        {
            "review_id": "review::weak-output",
            "candidate_id": "output::unsupported-answer",
            "candidate_type": "output",
            "target_surface": "output-delivery",
            "reviewer_refs": ["NexusBrain"],
            "verifier_refs": [],
            "eval_refs": [],
            "evidence_refs": [],
            "issues": [{"issue_id": "gap::citation", "severity": "hard_fail", "status": "open"}],
            "uncertainty": 0.62,
            "operator_approved": False,
        }
    )

    assert review["status"] == "blocked"
    assert review["review_state"] == "blocked-by-review"
    assert {
        "self_review_requires_independent_reviewer",
        "self_review_requires_external_or_tool_verifier",
        "self_review_requires_evidence_refs",
        "self_review_requires_issue_resolution",
        "self_review_uncertainty_above_threshold",
        "self_review_requires_operator_approval_for_high_impact",
    }.issubset({finding["rule_id"] for finding in review["review_findings"]})
    assert review["policy_scan"]["summary"]["allow_merge"] is False

    summary = gate.scorecard()
    assert summary["runtime_state"] == "degraded"
    assert summary["blocked_count"] == 1
    assert summary["latest_review"]["status"] == "blocked"


def test_self_review_gate_blocks_candidate_with_blocked_upstream_eval_gate():
    gate = SelfReviewGate()

    review = gate.review(
        {
            "review_id": "review::blocked-eval-adapter",
            "candidate_id": "update::blocked-eval-shadow",
            "candidate_type": "adapter",
            "target_surface": "autonomous-updates",
            "reviewer_refs": ["ao::safety", "expert::evals"],
            "verifier_refs": ["tool::pytest", "eval::nexus-held-out"],
            "eval_refs": ["shadow-run::blocked-growth-lifecycle"],
            "evidence_refs": ["/ops/brain/canon/eval-registry", "/ops/brain/canon/autonomous-updates"],
            "issues": [],
            "uncertainty": 0.1,
            "operator_approved": True,
            "upstream_eval_gate": {
                "promotion_allowed": False,
                "blockers": ["shadow_eval_blocks_growth_engine_gate"],
                "upstream_lifecycle_gate": {
                    "lifecycle_status": "closed_loop_blocked",
                    "growth_engine_gate_allowed": False,
                    "artifact_trust_promotion_allowed": False,
                    "blockers": ["growth_engine_adapter_training_gate_blocked"],
                },
            },
        }
    )

    assert review["status"] == "blocked"
    assert review["review_state"] == "blocked-by-review"
    assert review["upstream_eval_gate"]["promotion_allowed"] is False
    assert "growth_engine_adapter_training_gate_blocked" in review["upstream_eval_gate"]["blockers"]
    assert {
        "self_review_blocks_eval_promotion_gate",
        "self_review_blocks_upstream_lifecycle_gate",
    }.issubset({finding["rule_id"] for finding in review["review_findings"]})


def test_self_review_api_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/self-review/reviews",
        json={
            "review_id": "review::api-output",
            "candidate_id": "output::api-answer",
            "candidate_type": "output",
            "target_surface": "output-delivery",
            "reviewer_refs": ["ao::qa", "expert::documentation"],
            "verifier_refs": ["tool::schema-check"],
            "eval_refs": ["eval::answer-grounding"],
            "evidence_refs": ["/ops/brain/canon/output-delivery"],
            "issues": [],
            "uncertainty": 0.18,
            "operator_approved": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted-shadow"

    summary = client.get("/ops/brain/self-review")
    assert summary.status_code == 200
    assert summary.json()["review_count"] == 1

    scorecard = client.get("/ops/brain/canon/self-review")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["record_review"]["endpoint"] == "/ops/brain/self-review/reviews"
    assert "external_or_tool_verifier" in scorecard_payload["required_controls"]

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "self-review-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["self_review_scorecard"]["review_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "self-review-cockpit"}).json()
    assert blackbox["scorecard_refs"]["self_review"] == "/ops/brain/canon/self-review"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Self-Review Gate" in ui.text
    assert "selfReviewScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderSelfReviewScorecard" in app_js
    assert "/ops/brain/canon/self-review" in app_js
    self_review_renderer = app_js[
        app_js.index("function renderSelfReviewScorecard"):
        app_js.index("function renderProtocolTrustScorecard")
    ]
    assert "upstream eval gate" in self_review_renderer
    assert "upstream_eval_gate" in self_review_renderer
