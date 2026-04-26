from __future__ import annotations

from nexusnet.foundry.replacement_governance import ReplacementGovernanceAdvisor
from nexusnet.foundry.replacement_readiness import ReplacementReadinessAdvisor
from nexusnet.foundry.teacher_replacement import TeacherReplacementAdvisor
from nexusnet.schemas import ReplacementReadinessReport


def _all_gate_readiness(**evidence_refs) -> ReplacementReadinessReport:
    return ReplacementReadinessReport(
        subject="toolsmith",
        teacher_id="devstral-2",
        threshold_set_id="teacher-v2026-r1",
        threshold_version=1,
        subject_trend_ready=True,
        fleet_gate_ready=True,
        cohort_gate_ready=True,
        external_evaluation_passed=True,
        rollback_ready=True,
        governance_signed_off=True,
        ready=True,
        replacement_mode="replace",
        metrics={"quality": 0.96},
        evidence_refs=evidence_refs,
    )


def test_replacement_readiness_requires_authoritative_promotion_provenance_gate():
    advisor = ReplacementReadinessAdvisor()

    report = advisor.decide(
        subject="toolsmith",
        teacher_id="devstral-2",
        threshold_set_id="teacher-v2026-r1",
        threshold_version=1,
        subject_trend_ready=True,
        fleet_gate_ready=True,
        cohort_gate_ready=True,
        external_evaluation_passed=True,
        rollback_ready=True,
        governance_signed_off=True,
        metrics={"quality": 0.96},
        evidence_refs={"takeover_scorecard_id": "scorecard-1"},
    )

    assert report.ready is False
    assert report.replacement_mode == "shadow"
    authority = report.evidence_refs["readiness_authority"]
    assert authority["authoritative_readiness"] is False
    assert authority["readiness_authority"] == "promotion-provenance-gate"
    assert "takeover_eligible" in authority["missing_authority"]


def test_replacement_readiness_can_only_become_ready_with_explicit_authority():
    advisor = ReplacementReadinessAdvisor()

    report = advisor.decide(
        subject="toolsmith",
        teacher_id="devstral-2",
        threshold_set_id="teacher-v2026-r1",
        threshold_version=1,
        subject_trend_ready=True,
        fleet_gate_ready=True,
        cohort_gate_ready=True,
        external_evaluation_passed=True,
        rollback_ready=True,
        governance_signed_off=True,
        metrics={"quality": 0.96},
        evidence_refs={
            "takeover_scorecard_id": "scorecard-1",
            "takeover_eligible": True,
            "readiness_status": "eligible",
            "readiness_authority": "promotion-provenance-gate",
            "authoritative_readiness": True,
        },
    )

    assert report.ready is True
    assert report.replacement_mode == "replace"
    assert report.evidence_refs["readiness_authority"]["authoritative_readiness"] is True


def test_replacement_decision_advisors_fail_closed_on_legacy_ready_reports_without_authority():
    readiness = _all_gate_readiness(takeover_scorecard_id="scorecard-legacy")

    governance = ReplacementGovernanceAdvisor().decide(
        teacher_id="devstral-2",
        replacement_target="native::devstral-2",
        readiness=readiness,
    )
    teacher = TeacherReplacementAdvisor().decide(
        teacher_id="devstral-2",
        replacement_target="native::devstral-2",
        readiness=readiness,
    )

    assert governance.decision == "shadow"
    assert teacher.decision == "shadow"
    assert governance.evidence["readiness_authority"]["authoritative_readiness"] is False
    assert teacher.evidence["readiness_authority"]["authoritative_readiness"] is False
    assert "promotion-provenance-gate" in governance.rationale
