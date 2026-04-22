from __future__ import annotations

from nexus.services import build_services
from tests.test_nexus_phase1_foundation import make_project


def test_teacher_provenance_captures_registry_roles_and_lineage(tmp_path):
    project_root = make_project(tmp_path)
    services = build_services(str(project_root))

    attached, record = services.brain_teachers.resolve_for_task(
        brain=services.brain,
        task_type="chat",
        expert="toolsmith",
        routing_metadata={
            "budget_class": "STANDARD",
            "output_form": "TOOL_CALL_STRICT_JSON",
            "risk_tier": "medium",
            "teacher_lineage": "dream-derived",
            "benchmark_family": "strict JSON / tool schemas",
            "native_takeover_candidate_id": "nativecand_123",
        },
    )
    provenance = attached.provenance
    assert provenance["registry_layer"] == "v2026_live"
    assert provenance["selected_teacher_roles"]["primary"] == "devstral-2"
    assert provenance["selected_teacher_roles"]["secondary"] == "qwen3-coder-next"
    assert provenance["selected_teacher_roles"]["critique"] == "deepseek-r1-distill-qwen-32b"
    assert provenance["selected_teacher_roles"]["efficiency"] == "lfm2"
    assert provenance["dream_derived"] is True
    assert provenance["live_derived"] is False
    assert provenance["benchmark_family"] == "strict JSON / tool schemas"
    assert provenance["native_takeover_candidate_id"] == "nativecand_123"
    assert provenance["arbitration"]["record_id"] == record.record_id
