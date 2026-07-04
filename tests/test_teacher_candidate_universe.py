from __future__ import annotations

import pytest

from nexusnet.teachers.candidate_universe import TeacherCandidate, build_default_teacher_candidate_universe


def test_candidate_universe_bootstraps_watchlist_without_active_promotion():
    universe = build_default_teacher_candidate_universe()

    leanstral = universe.get("leanstral-1-5")
    assert leanstral is not None
    assert leanstral.candidate_status == "watchlist"
    assert "verifier" in leanstral.teacher_roles
    assert "formal_methods" in leanstral.domain_scope
    assert universe.promotion_blockers("leanstral-1-5") == [
        "candidate_status_not_shadow_or_canary",
        "license_gate_not_approved",
        "privacy_gate_not_approved",
        "hardware_gate_not_approved",
        "cost_gate_not_approved",
        "benchmark_refs_missing",
    ]


def test_quarantined_unlicensed_candidate_is_blocked_from_promotion():
    universe = build_default_teacher_candidate_universe()
    candidate = TeacherCandidate(
        candidate_id="frontier-remote-council",
        model_or_tool_id="remote/frontier-council",
        provider="remote",
        source_url="https://example.invalid/frontier",
        candidate_status="quarantined",
        teacher_roles=["critic", "judge"],
        license_gate="needs_review",
        privacy_gate="blocked",
        hardware_gate="not_required",
        cost_gate="needs_review",
        eval_family=["agentic-reasoning"],
        domain_scope=["orchestration"],
        risk_scope=["high"],
        source_refs=["model-card::frontier-council"],
    )
    universe.register(candidate)

    assert universe.get("frontier-remote-council") == candidate
    assert universe.promotion_allowed("frontier-remote-council") is False
    assert "privacy_gate_blocked" in universe.promotion_blockers("frontier-remote-council")


def test_evidenced_shadow_candidate_can_be_promotion_ready():
    universe = build_default_teacher_candidate_universe()
    universe.register(
        {
            "candidate_id": "qwen3-coder-next-shadow",
            "model_or_tool_id": "Qwen/Qwen3-Coder-Next",
            "provider": "huggingface",
            "source_url": "https://huggingface.co/Qwen/Qwen3-Coder-Next",
            "candidate_status": "shadow",
            "teacher_roles": ["generator", "critic"],
            "license_gate": "approved",
            "privacy_gate": "approved",
            "hardware_gate": "approved",
            "cost_gate": "approved",
            "eval_family": ["coding", "agentic-software"],
            "domain_scope": ["software", "coding"],
            "risk_scope": ["medium"],
            "source_refs": ["hf::Qwen/Qwen3-Coder-Next"],
            "benchmark_refs": ["eval::swebench-shadow"],
            "replacement_candidates": ["devstral-2"],
        }
    )

    assert universe.promotion_allowed("qwen3-coder-next-shadow") is True
    summary = universe.summary()
    assert summary["candidate_count"] >= 4
    assert summary["promotion_ready_count"] == 1
    assert "qwen3-coder-next-shadow" in summary["promotion_ready_candidate_ids"]


def test_register_rejects_duplicate_candidate_ids_by_default_without_replacing_original():
    universe = build_default_teacher_candidate_universe()
    original = universe.get("qwen3-coder-next")
    assert original is not None
    replacement = original.model_copy(update={"candidate_status": "active"})

    with pytest.raises(ValueError, match="already registered"):
        universe.register(replacement)

    assert universe.get("qwen3-coder-next") == original
    assert universe.register(replacement, replace=True) == replacement
    assert universe.get("qwen3-coder-next") == replacement
