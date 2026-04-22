from __future__ import annotations

from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_critique_arbitration_path_is_exercised_for_security_teacher_disagreements(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    attached, record = services.brain_teachers.resolve_for_task(
        brain=services.brain,
        task_type="chat",
        expert="security",
        routing_metadata={
            "budget_class": "DEEP",
            "output_form": "CODE_PATCH",
            "risk_tier": "high",
            "benchmark_family": "secure patching",
        },
    )

    assert record.selected_teacher_id == "code-llama-secure"
    assert record.selected_roles["critique"] == "deepseek-r1-distill-qwen-32b"
    assert record.selected_roles["efficiency"] == "lfm2"
    assert record.local_vs_remote == "local"
    assert record.arbitration_result == "PATCH_DOMAIN_WITH_LFM2_EDITS_THEN_VERIFY"
    assert attached.provenance["arbitration"]["benchmark_family"] == "secure patching"
