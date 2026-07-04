from __future__ import annotations

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.adapters.decision_gate import FineTuneDecisionGate, FineTuneDecisionRequest
from tests.test_nexus_phase1_foundation import make_project


def test_fine_tune_decision_gate_routes_changing_knowledge_to_rag_before_training():
    gate = FineTuneDecisionGate()

    decision = gate.decide(
        FineTuneDecisionRequest(
            decision_id="decision::fresh-policy-knowledge",
            candidate_id="candidate::fresh-policy-knowledge",
            learning_target="fresh_knowledge",
            failure_modes=["stale_info"],
            prompt_attempted=True,
            rag_attempted=False,
            agent_loop_attempted=False,
            eval_refs=["eval::fresh-knowledge-heldout"],
            provenance_refs=["docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md"],
            contains_private_data=False,
            license_status="approved",
            operator_approved=True,
            dataset_manifest_id="dataset::fresh-policy-knowledge",
            adapter_plan_id="training::fresh-policy-knowledge",
        )
    )

    assert decision["status_label"] == "LOCKED CANON"
    assert decision["authority"] == "NexusBrain"
    assert decision["surface_id"] == "fine-tune-decision-gate"
    assert decision["status"] == "rag-first"
    assert decision["recommended_path"] == "rag"
    assert decision["adapter_training_allowed"] is False
    assert decision["training_boundary"] == "decision-only-no-training-job"
    assert "fine_tune_gate_changing_knowledge_stays_retrieval_first" in {
        finding["rule_id"] for finding in decision["decision_findings"]
    }


def test_fine_tune_decision_gate_allows_shadow_adapter_after_prompt_rag_agent_eval_and_rights():
    gate = FineTuneDecisionGate()

    decision = gate.decide(
        {
            "decision_id": "decision::code-ao-style",
            "candidate_id": "candidate::code-ao-style",
            "learning_target": "style_behavior",
            "failure_modes": ["style_drift", "format_inconsistency"],
            "prompt_attempted": True,
            "rag_attempted": True,
            "agent_loop_attempted": True,
            "eval_refs": ["eval::style-heldout", "eval::format-regression"],
            "provenance_refs": ["dataset::code-ao-style", "youtube-transcript::v7qMjy_RxOs"],
            "contains_private_data": False,
            "license_status": "approved",
            "operator_approved": True,
            "dataset_manifest_id": "dataset::code-ao-style",
            "adapter_plan_id": "training::code-ao-style",
        }
    )

    assert decision["status"] == "adapter-shadow-eligible"
    assert decision["runtime_state"] == "live-bound"
    assert decision["recommended_path"] == "adapter-training"
    assert decision["adapter_training_allowed"] is True
    assert decision["policy_scan"]["summary"]["allow_merge"] is True
    assert {
        "prompt-first",
        "rag-first",
        "agent-loop-first",
        "eval-provenance-required",
        "operator-approval-required",
        "adapter-shadow-only",
    }.issubset(set(decision["required_controls"]))


def test_fine_tune_decision_gate_blocks_private_or_unlicensed_training():
    gate = FineTuneDecisionGate()

    decision = gate.decide(
        {
            "decision_id": "decision::private-raw-browser-history",
            "candidate_id": "candidate::private-raw-browser-history",
            "learning_target": "style_behavior",
            "failure_modes": ["style_drift"],
            "prompt_attempted": True,
            "rag_attempted": True,
            "agent_loop_attempted": True,
            "eval_refs": [],
            "provenance_refs": [],
            "contains_private_data": True,
            "license_status": "blocked",
            "operator_approved": False,
            "dataset_manifest_id": "dataset::raw-browser-history",
            "adapter_plan_id": "training::raw-browser-history",
        }
    )

    assert decision["status"] == "blocked"
    assert decision["adapter_training_allowed"] is False
    assert decision["runtime_state"] == "degraded"
    assert decision["policy_scan"]["summary"]["allow_merge"] is False
    assert {
        "fine_tune_gate_private_data_requires_operator_approval",
        "fine_tune_gate_requires_approved_license",
        "fine_tune_gate_requires_eval_refs",
        "fine_tune_gate_requires_provenance_refs",
    }.issubset({finding["rule_id"] for finding in decision["decision_findings"]})


def test_fine_tune_decision_gate_blocks_dataset_forge_manifest_needing_review():
    gate = FineTuneDecisionGate()

    decision = gate.decide(
        {
            "decision_id": "decision::review-blocked-code-adapter",
            "candidate_id": "candidate::review-blocked-code-adapter",
            "learning_target": "style_behavior",
            "failure_modes": ["code_style_drift"],
            "prompt_attempted": True,
            "rag_attempted": True,
            "agent_loop_attempted": True,
            "eval_refs": ["eval::code-style-heldout"],
            "provenance_refs": ["dataset::review-blocked-code-adapter"],
            "contains_private_data": False,
            "license_status": "approved",
            "operator_approved": True,
            "dataset_manifest_id": "dataset::review-blocked-code-adapter",
            "dataset_manifest_status": "needs_review",
            "dataset_radar_training_review_gate": {
                "allowed": False,
                "blocked_source_ids": ["the-stack-v2"],
                "blockers": [
                    {
                        "source_id": "the-stack-v2",
                        "review_state": "review_required",
                        "blocking_fields": ["privacy_evidence", "training_eligibility"],
                    }
                ],
            },
            "adapter_plan_id": "training::review-blocked-code-adapter",
        }
    )

    assert decision["status"] == "blocked"
    assert decision["adapter_training_allowed"] is False
    assert decision["dataset_manifest_status"] == "needs_review"
    assert decision["dataset_radar_training_review_gate"]["allowed"] is False
    assert {
        "fine_tune_gate_requires_ready_dataset_manifest",
        "fine_tune_gate_dataset_radar_training_review_blocked",
    }.issubset({finding["rule_id"] for finding in decision["decision_findings"]})

    scorecard = gate.scorecard()
    assert scorecard["runtime_state"] == "degraded"
    assert scorecard["blocked_count"] == 1
    assert scorecard["latest_decision"]["status"] == "blocked"


def test_fine_tune_decision_gate_api_visualizer_blackbox_and_control_panel_surface(tmp_path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/fine-tune-decision-gate/decisions",
        json={
            "decision_id": "decision::api-code-ao-style",
            "candidate_id": "candidate::api-code-ao-style",
            "learning_target": "style_behavior",
            "failure_modes": ["style_drift"],
            "prompt_attempted": True,
            "rag_attempted": True,
            "agent_loop_attempted": True,
            "eval_refs": ["eval::api-style-heldout"],
            "provenance_refs": ["dataset::api-code-ao-style"],
            "contains_private_data": False,
            "license_status": "approved",
            "operator_approved": True,
            "dataset_manifest_id": "dataset::api-code-ao-style",
            "adapter_plan_id": "training::api-code-ao-style",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "adapter-shadow-eligible"

    summary = client.get("/ops/brain/fine-tune-decision-gate")
    assert summary.status_code == 200
    assert summary.json()["decision_count"] == 1

    scorecard = client.get("/ops/brain/canon/fine-tune-decision-gate")
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.json()
    assert scorecard_payload["runtime_state"] == "live-bound"
    assert scorecard_payload["operator_actions"]["decide"]["endpoint"] == "/ops/brain/fine-tune-decision-gate/decisions"

    visualizer = client.get("/ops/brain/visualizer/state", params={"session_id": "fine-tune-gate-cockpit"})
    assert visualizer.status_code == 200
    control_panel = visualizer.json()["overlay_state"]["control_panel"]
    assert control_panel["fine_tune_decision_gate_scorecard"]["decision_count"] == 1

    blackbox = client.get("/ops/brain/canon/blackbox", params={"session_id": "fine-tune-gate-cockpit"}).json()
    assert blackbox["scorecard_refs"]["fine_tune_decision_gate"] == "/ops/brain/canon/fine-tune-decision-gate"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Fine-Tune Decision Gate" in ui.text
    assert "fineTuneDecisionGateScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderFineTuneDecisionGateScorecard" in app_js
    assert "/ops/brain/canon/fine-tune-decision-gate" in app_js
    assert "Fine-tune DatasetForge review gate" in app_js
    assert "dataset_manifest_status" in app_js
    assert "fine_tune_gate_dataset_radar_training_review_blocked" in app_js
