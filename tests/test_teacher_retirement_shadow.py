from __future__ import annotations

from nexus.services import build_services
from nexusnet.schemas import IndependenceMetrics
from tests.test_nexus_phase1_foundation import make_project


def test_teacher_retirement_shadow_path_keeps_historical_and_live_entries_intact(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    before_profiles = {profile.teacher_id for profile in services.brain_teachers.list_profiles()}
    decisions = services.brain_teachers.retirement_decisions(
        IndependenceMetrics(
            dependency_ratio=0.05,
            native_generation=0.95,
            teacher_replacement_ready=True,
        )
    )
    after_profiles = {profile.teacher_id for profile in services.brain_teachers.list_profiles()}

    assert before_profiles == after_profiles
    assert any(decision.decision == "shadow" for decision in decisions)
    assert all(decision.decision != "retire" for decision in decisions)
    assert services.brain_teachers.assignment_for("coder", "historical") is not None
    assert services.brain_teachers.assignment_for("coder", "v2026_live") is not None
