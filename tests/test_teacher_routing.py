from __future__ import annotations

from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_live_teacher_routing_selects_expected_primary_secondary_and_bounded_lfm2(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    _, record = services.brain_teachers.resolve_for_task(
        brain=services.brain,
        task_type="chat",
        expert="router",
        routing_metadata={
            "budget_class": "FASTPATH",
            "output_form": "TOOL_CALL_STRICT_JSON",
            "risk_tier": "low",
        },
    )
    assert record.registry_layer == "v2026_live"
    assert record.selected_teacher_id == "deepseek-v2-lite"
    assert record.selected_roles["secondary"] == "qwen3-30b-a3b"
    assert record.selected_roles["efficiency"] == "lfm2"
    assert record.arbitration_result == "PATCH_DOMAIN_WITH_LFM2_EDITS_THEN_VERIFY"


def test_historical_teacher_routing_stays_best_ensemble_and_strategist_does_not_pick_lfm2(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    _, historical = services.brain_teachers.resolve_for_task(
        brain=services.brain,
        task_type="chat",
        expert="coder",
        routing_metadata={"teacher_registry_layer": "historical"},
    )
    assert historical.registry_layer == "historical"
    assert historical.selected_teacher_id == "codestral"
    assert historical.selected_roles == {"primary": "codestral"}

    _, strategist = services.brain_teachers.resolve_for_task(
        brain=services.brain,
        task_type="chat",
        expert="strategist",
        routing_metadata={
            "budget_class": "DEEP",
            "output_form": "LONGFORM",
            "risk_tier": "medium",
        },
    )
    assert strategist.registry_layer == "v2026_live"
    assert strategist.selected_teacher_id == "qwen3-30b-a3b"
    assert "efficiency" not in strategist.selected_roles
