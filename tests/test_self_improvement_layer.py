from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nexus.api.app import create_app
from nexusnet.core.self_improvement.event_schema import (
    ContextSource,
    ImprovementEvent,
    LearningSignal,
    Outcome,
    SafetyClassification,
)
from nexusnet.core.self_improvement.evaluator import ImprovementEvaluator
from nexusnet.core.self_improvement.experience_capture import ExperienceCapture
from nexusnet.core.self_improvement.improvement_queue import ImprovementQueue
from nexusnet.core.self_improvement.memory_update_policy import MemoryUpdatePolicy
from nexusnet.core.self_improvement.prompt_update_policy import PromptUpdatePolicy
from nexusnet.core.self_improvement.provenance import ProvenanceTracker
from nexusnet.core.self_improvement.regression_gate import RegressionGate
from nexusnet.core.self_improvement.training_candidate_builder import TrainingCandidateBuilder
from nexusnet.core.self_improvement.triage import triage_improvement_event
from tests.test_nexus_phase1_foundation import make_project


def make_event(**overrides) -> ImprovementEvent:
    payload = {
        "session_id": "self-improve-session",
        "input_modalities": ["text", "file", "tool_output"],
        "user_goal": "Assimilate a multimodal self-improvement survey into NexusNet.",
        "agent_task_type": "architecture",
        "context_sources": [
            ContextSource(
                source_type="web",
                source_id="arxiv:2510.02665",
                provenance="Self-Improvement in Multimodal Large Language Models: A Survey",
            ),
            ContextSource(
                source_type="tool",
                source_id="pytest",
                provenance="Regression evidence from local test run.",
            ),
        ],
        "agent_plan": "Capture event, triage it, and queue only safe improvements.",
        "actions_taken": ["verified source", "mapped taxonomy", "created tests"],
        "final_output_summary": "Self-improvement MVP spine proposed with no direct model training.",
        "outcome": Outcome(
            status="partial",
            user_feedback="neutral",
            failure_modes=["missing_context"],
        ),
        "learning_signal": LearningSignal(
            should_store_memory=True,
            should_create_eval=True,
            should_create_training_example=True,
            confidence=0.72,
            review_required=True,
        ),
        "safety": SafetyClassification(
            contains_private_data=False,
            contains_secrets=False,
            retention_policy="project",
        ),
        "evidence_refs": ["https://arxiv.org/abs/2510.02665"],
    }
    payload.update(overrides)
    return ImprovementEvent(**payload)


def test_improvement_event_schema_defaults_source_contract_and_serialization():
    event = make_event()

    assert event.project == "NexusNet Neural Core AI Brain"
    assert event.event_id.startswith("improve::")
    assert event.timestamp.tzinfo is not None
    assert event.input_modalities == ["text", "file", "tool_output"]
    assert event.learning_signal.confidence == 0.72
    assert event.source_document_refs == [
        "arXiv:2510.02665",
        "arXiv:2411.17760",
        "docs/SELF_IMPROVEMENT_LAYER.md",
    ]

    exported = event.model_dump(mode="json")
    assert exported["outcome"]["failure_modes"] == ["missing_context"]
    assert exported["safety"]["retention_policy"] == "project"
    assert exported["context_sources"][0]["source_id"] == "arxiv:2510.02665"


def test_triage_prefers_memory_eval_and_reviewed_training_candidates_without_direct_self_training():
    event = make_event()

    decision = triage_improvement_event(event)

    assert decision.event_id == event.event_id
    assert decision.queue_required is True
    assert decision.review_required is True
    assert {
        "store_as_project_memory",
        "create_eval_case",
        "create_training_candidate",
        "human_review_required",
    }.issubset(set(decision.labels))
    assert "direct_model_training" not in decision.safe_optimization_modes
    assert decision.model_update_boundary == "no-weight-update-without-human-review-external-verification-and-regression-gates"


def test_triage_discards_secret_or_unsafe_retention_events():
    event = make_event(
        learning_signal=LearningSignal(
            should_store_memory=True,
            should_create_eval=True,
            should_create_training_example=True,
            confidence=0.95,
            review_required=False,
        ),
        safety=SafetyClassification(
            contains_private_data=True,
            contains_secrets=True,
            retention_policy="long_term",
        ),
    )

    decision = triage_improvement_event(event)

    assert decision.queue_required is False
    assert decision.review_required is True
    assert decision.labels == ["discard", "human_review_required"]
    assert decision.blocked_reason == "contains-secrets"


def test_improvement_queue_persists_lifecycle_and_rejects_invalid_transitions(tmp_path: Path):
    queue_path = tmp_path / "improvement_queue.json"
    event = make_event()
    decision = triage_improvement_event(event)
    queue = ImprovementQueue(queue_path)

    item = queue.propose(event, decision=decision, actor="ResearchAO", reason="source-verified assimilation candidate")
    assert item.status == "proposed"
    assert item.decision.labels[0] in {
        "store_as_project_memory",
        "create_eval_case",
        "create_training_candidate",
        "human_review_required",
    }

    for status in ["validated", "approved", "deployed", "monitored"]:
        item = queue.transition(item.queue_id, status, actor="NexusBrain", reason=f"{status} gate passed")
        assert item.status == status

    reloaded = ImprovementQueue(queue_path)
    loaded = reloaded.get(item.queue_id)
    assert loaded.status == "monitored"
    assert len(loaded.history) == 5

    reverted = reloaded.transition(item.queue_id, "reverted", actor="GovernanceAO", reason="rollback test")
    assert reverted.status == "reverted"

    with pytest.raises(ValueError, match="Invalid improvement queue transition"):
        reloaded.transition(item.queue_id, "deployed", actor="NexusBrain", reason="should fail")


def test_improvement_queue_rejects_non_queueable_events_with_audit_record(tmp_path: Path):
    event = make_event(
        safety=SafetyClassification(
            contains_private_data=False,
            contains_secrets=True,
            retention_policy="discard",
        )
    )
    decision = triage_improvement_event(event)
    queue = ImprovementQueue(tmp_path / "queue.json")

    item = queue.propose(event, decision=decision, actor="SafetyAO", reason="secret found")

    assert item.status == "rejected"
    assert item.decision.blocked_reason == "contains-secrets"
    assert item.history[0].to_status == "rejected"


def test_self_improvement_event_api_triages_and_queues_without_direct_training(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    event = make_event(session_id="self-improvement-api")

    response = client.post(
        "/ops/brain/self-improvement/events",
        json=event.model_dump(mode="json"),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["decision"]["queue_required"] is True
    assert "direct_model_training" not in payload["decision"]["safe_optimization_modes"]
    assert payload["queue_item"]["status"] == "proposed"

    queue = client.get("/ops/brain/self-improvement/queue")
    assert queue.status_code == 200
    queue_payload = queue.json()
    assert queue_payload["item_count"] == 1
    assert queue_payload["status_counts"]["proposed"] == 1


def test_self_improvement_canon_scorecard_and_control_panel_surface(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/canon/self-improvement", params={"session_id": "self-improvement-surface"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["surface_id"] == "self-improvement-layer"
    assert payload["authority"] == "NexusBrain"
    assert payload["required_controls"] == [
        "experience_capture",
        "improvement_event_schema",
        "data_triage",
        "provenance_tracking",
        "evaluation_generation",
        "improvement_queue",
        "memory_prompt_policy",
        "training_candidate_review",
        "regression_gates",
    ]
    assert {"experience-capture", "data-triage", "improvement-queue", "regression-gates"}.issubset(
        {stage["stage_id"] for stage in payload["pipeline_stages"]}
    )
    stage_states = {stage["stage_id"]: stage["state"] for stage in payload["pipeline_stages"]}
    assert stage_states["experience-capture"] == "live-bound"
    assert stage_states["provenance-tracking"] == "live-bound"
    assert stage_states["regression-gates"] == "live-bound"
    assert payload["model_update_boundary"] == "no-weight-update-without-human-review-external-verification-and-regression-gates"
    assert payload["operator_actions"]["queue_event"]["endpoint"] == "/ops/brain/self-improvement/events"
    assert payload["operator_actions"]["capture_event"]["endpoint"] == "/ops/brain/self-improvement/capture"
    assert payload["operator_actions"]["inspect_queue"]["endpoint"] == "/ops/brain/self-improvement/queue"
    assert (
        payload["operator_actions"]["review_queue_item"]["endpoint_template"]
        == "/ops/brain/self-improvement/queue/{queue_id}/review"
    )

    blackbox = client.get(
        "/ops/brain/canon/blackbox",
        params={"session_id": "self-improvement-surface"},
    ).json()
    assert "self-improvement-layer" in {frame["frame_id"] for frame in blackbox["frames"]}
    assert blackbox["scorecard_refs"]["self_improvement"] == "/ops/brain/canon/self-improvement"

    ui = client.get("/ui/control-panel/")
    assert ui.status_code == 200
    assert "Self-Improvement Layer" in ui.text
    assert "selfImprovementScorecard" in ui.text

    app_js = (project_root / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")
    assert "renderSelfImprovementScorecard" in app_js
    assert "/ops/brain/canon/self-improvement" in app_js


def test_experience_capture_normalizes_raw_interaction_into_event():
    capture = ExperienceCapture(project="NexusNet Neural Core AI Brain")

    event = capture.capture(
        session_id="capture-session",
        user_goal="Turn a failed tool run into an eval case.",
        input_modalities=["text", "tool_output"],
        agent_task_type="debugging",
        context_sources=[
            {"source_type": "tool", "source_id": "pytest", "provenance": "local regression run"},
            ContextSource(source_type="web", source_id="arxiv:2510.02665", provenance="self-improvement taxonomy"),
        ],
        agent_plan="Capture the failure, keep provenance, and route through review.",
        actions_taken=["ran focused test", "captured failure"],
        final_output_summary="Failure became a reviewed improvement candidate.",
        outcome={"status": "failed", "user_feedback": "neutral", "failure_modes": ["tool_error"]},
        learning_signal={"should_create_eval": True, "confidence": 0.64, "review_required": True},
        safety={"retention_policy": "project"},
        evidence_refs=["tests/test_self_improvement_layer.py::test_experience_capture_normalizes_raw_interaction_into_event"],
    )

    assert event.session_id == "capture-session"
    assert event.agent_task_type == "debugging"
    assert event.context_sources[0].source_id == "pytest"
    assert event.outcome.failure_modes == ["tool_error"]
    assert event.learning_signal.should_create_eval is True
    assert event.metadata["capture_method"] == "ExperienceCapture.capture"


def test_provenance_evaluator_policies_and_regression_gate_keep_updates_governed(tmp_path: Path):
    event = make_event()
    decision = triage_improvement_event(event)
    provenance = ProvenanceTracker().record(event, verifier_refs=["pytest::tests/test_self_improvement_layer.py"])

    assert provenance.source_count == 2
    assert provenance.evidence_count == 2
    assert provenance.verifier_count == 1
    assert provenance.trust_level == "reviewable"
    assert provenance.unsupported_source_ids == []

    evaluation = ImprovementEvaluator().evaluate(event, decision, provenance)
    checks = {check.check_id: check for check in evaluation.checks}
    assert evaluation.status == "needs_review"
    assert checks["source-coverage"].status == "pass"
    assert checks["direct-training-block"].status == "pass"
    assert checks["human-review"].status == "warn"

    memory_candidate = MemoryUpdatePolicy().build_candidate(event, decision, provenance)
    assert memory_candidate.allowed is True
    assert memory_candidate.requires_review is True
    assert memory_candidate.retention_policy == "project"
    assert memory_candidate.evidence_refs == event.evidence_refs

    prompt_candidate = PromptUpdatePolicy().build_candidate(event, decision)
    assert prompt_candidate.allowed is True
    assert prompt_candidate.policy_scope == "architecture-routing"
    assert "missing_context" in prompt_candidate.failure_modes

    training_candidate = TrainingCandidateBuilder().build_candidate(event, decision, provenance)
    assert training_candidate.allowed is True
    assert training_candidate.status == "review_required"
    assert training_candidate.export_ready is False
    assert training_candidate.provenance_id == provenance.provenance_id

    queue = ImprovementQueue(tmp_path / "queue.json")
    queued = queue.propose(event, decision=decision)
    gate_report = RegressionGate().evaluate(
        queued,
        evaluation,
        test_results=[
            {"check_id": "project-continuity", "status": "pass", "evidence_ref": "pytest continuity"},
            {"check_id": "factuality", "status": "pass", "evidence_ref": "source coverage"},
            {"check_id": "tool-use", "status": "pass", "evidence_ref": "tool trace"},
            {"check_id": "safety-privacy", "status": "pass", "evidence_ref": "privacy scan"},
        ],
        operator_approved=False,
    )

    assert gate_report.can_promote is False
    assert gate_report.status == "blocked"
    assert "operator-approval-required" in gate_report.blockers
    assert gate_report.required_check_ids == ["project-continuity", "factuality", "tool-use", "safety-privacy"]

    approved_report = RegressionGate().evaluate(
        queued,
        evaluation,
        test_results=[
            {"check_id": "project-continuity", "status": "pass", "evidence_ref": "pytest continuity"},
            {"check_id": "factuality", "status": "pass", "evidence_ref": "source coverage"},
            {"check_id": "tool-use", "status": "pass", "evidence_ref": "tool trace"},
            {"check_id": "safety-privacy", "status": "pass", "evidence_ref": "privacy scan"},
        ],
        operator_approved=True,
    )

    assert approved_report.status == "pass"
    assert approved_report.can_promote is True


def test_self_improvement_review_api_returns_governed_candidates(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    event = make_event(session_id="self-improvement-review-api")

    queued = client.post("/ops/brain/self-improvement/events", json=event.model_dump(mode="json")).json()
    response = client.get(f"/ops/brain/self-improvement/queue/{queued['queue_item']['queue_id']}/review")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["evaluation"]["status"] == "needs_review"
    assert payload["memory_candidate"]["allowed"] is True
    assert payload["prompt_candidate"]["allowed"] is True
    assert payload["training_candidate"]["status"] == "review_required"
    assert payload["regression_gate"]["can_promote"] is False
    assert "operator-approval-required" in payload["regression_gate"]["blockers"]
    assert payload["policy_scan"]["summary"]["allow_merge"] is False
    assert payload["policy_scan"]["summary"]["active_hard_fail_count"] == 1
    assert payload["policy_scan"]["findings"][0]["rule_id"] == "training_candidate_requires_operator_approval"

    approved_response = client.get(
        f"/ops/brain/self-improvement/queue/{queued['queue_item']['queue_id']}/review",
        params={"operator_approved": True},
    )
    approved_payload = approved_response.json()
    assert approved_payload["policy_scan"]["summary"]["allow_merge"] is True
    assert approved_payload["policy_scan"]["summary"]["active_hard_fail_count"] == 0


def test_self_improvement_capture_api_normalizes_raw_trace_and_returns_review(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.post(
        "/ops/brain/self-improvement/capture",
        json={
            "session_id": "self-improvement-capture-api",
            "user_goal": "Capture raw operator trace.",
            "input_modalities": ["text", "tool_output"],
            "agent_task_type": "debugging",
            "context_sources": [
                {"source_type": "tool", "source_id": "pytest", "provenance": "focused regression"},
            ],
            "agent_plan": "Capture and review.",
            "actions_taken": ["ran test"],
            "final_output_summary": "Raw trace became a governed candidate.",
            "outcome": {"status": "failed", "user_feedback": "neutral", "failure_modes": ["tool_error"]},
            "learning_signal": {"should_create_eval": True, "confidence": 0.66, "review_required": True},
            "safety": {"contains_private_data": False, "contains_secrets": False, "retention_policy": "project"},
            "evidence_refs": ["pytest::self_improvement_capture_api"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status_label"] == "LOCKED CANON"
    assert payload["event"]["metadata"]["capture_method"] == "ExperienceCapture.capture"
    assert payload["queue_item"]["status"] == "proposed"
    assert payload["review"]["evaluation"]["status"] == "needs_review"
    assert payload["review"]["provenance"]["trust_level"] == "reviewable"
