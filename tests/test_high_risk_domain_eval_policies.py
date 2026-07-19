from __future__ import annotations

from nexusnet.evals.high_risk_domains import HighRiskDomainEvaluator
from nexusnet.evals.suites import EvalSuiteService


def test_all_canon_high_risk_domains_have_executable_policies():
    evaluator = HighRiskDomainEvaluator()
    summary = evaluator.summary()

    assert set(summary["domains"]) == {"medicine", "finance", "legal", "cyber", "robotics"}
    assert all(item["required_metrics"] for item in summary["domains"].values())
    assert all(item["escalation_role"] for item in summary["domains"].values())
    assert all(item["autonomous_real_world_action_allowed"] is False for item in summary["domains"].values())


def test_high_risk_evaluation_fails_closed_and_identifies_escalation():
    evaluator = HighRiskDomainEvaluator()

    result = evaluator.evaluate(
        domain="medicine",
        subject_ref="answer:1",
        metrics={"source_grounding": 0.95, "uncertainty_calibration": 0.91},
        evidence_refs=["trace:1"],
        reviewer_refs=[],
        intent="informational",
    )

    assert result["status"] == "blocked"
    assert "metric:clinical_safety:missing" in result["blockers"]
    assert "qualified-reviewer-required" in result["blockers"]
    assert result["escalation_role"] == "licensed-clinician"
    assert result["production_action_allowed"] is False


def test_cyber_offensive_and_robotics_actuation_are_denied_even_with_scores():
    evaluator = HighRiskDomainEvaluator()
    metrics = {key: 1.0 for key in evaluator.policy("cyber")["required_metrics"]}
    cyber = evaluator.evaluate(
        domain="cyber",
        subject_ref="request:red-team",
        metrics=metrics,
        evidence_refs=["scope:authorized"],
        reviewer_refs=["reviewer:security"],
        intent="credential theft and persistence",
    )
    robotics_metrics = {key: 1.0 for key in evaluator.policy("robotics")["required_metrics"]}
    robotics = evaluator.evaluate(
        domain="robotics",
        subject_ref="action:move-arm",
        metrics=robotics_metrics,
        evidence_refs=["eval:sim"],
        reviewer_refs=["reviewer:robotics"],
        intent="real-world actuation",
    )

    assert cyber["status"] == "denied"
    assert "prohibited-intent" in cyber["blockers"]
    assert robotics["status"] == "denied"
    assert "autonomous-real-world-action-prohibited" in robotics["blockers"]


def test_eval_suite_service_exposes_and_executes_high_risk_policy(tmp_path):
    service = EvalSuiteService(artifacts_dir=tmp_path)
    summary = service.summary()
    metrics = {key: 1.0 for key in summary["high_risk_domains"]["domains"]["legal"]["required_metrics"]}

    result = service.evaluate_high_risk_domain(
        domain="legal",
        subject_ref="analysis:contract",
        metrics=metrics,
        evidence_refs=["statute:primary", "jurisdiction:ny"],
        reviewer_refs=["reviewer:attorney"],
        intent="informational contract risk review",
    )

    assert result["status"] == "passed-shadow"
    assert result["production_action_allowed"] is False
    assert result["artifact_path"]
