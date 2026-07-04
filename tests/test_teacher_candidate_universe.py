from __future__ import annotations

import pytest

from nexusnet.teachers.candidate_universe import (
    TeacherCandidate,
    TeacherCandidateUniverse,
    build_default_teacher_candidate_universe,
)


def test_candidate_universe_bootstraps_watchlist_without_active_promotion():
    universe = build_default_teacher_candidate_universe()

    leanstral = universe.get("leanstral-1-5")
    assert leanstral is not None
    assert leanstral.provider == "huggingface"
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


def test_not_required_gates_do_not_block_evidenced_shadow_candidate():
    universe = build_default_teacher_candidate_universe()
    universe.register(
        {
            "candidate_id": "not-required-shadow",
            "model_or_tool_id": "local/not-required-shadow",
            "provider": "local",
            "source_url": "https://example.invalid/not-required-shadow",
            "candidate_status": "shadow",
            "teacher_roles": ["verifier"],
            "license_gate": "not_required",
            "privacy_gate": "not_required",
            "hardware_gate": "not_required",
            "cost_gate": "not_required",
            "source_refs": ["source::not-required-shadow"],
            "benchmark_refs": ["benchmark::not-required-shadow"],
        }
    )

    assert universe.promotion_blockers("not-required-shadow") == []
    assert universe.promotion_allowed("not-required-shadow") is True


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


def test_candidate_accepts_research_and_retirement_fields_and_reason_blocks_promotion():
    candidate = TeacherCandidate(
        candidate_id="retired-by-reason",
        model_or_tool_id="local/retired-by-reason",
        provider="local",
        source_url="https://example.invalid/retired-by-reason",
        candidate_status="shadow",
        teacher_roles=["critic"],
        license_gate="approved",
        privacy_gate="approved",
        hardware_gate="approved",
        cost_gate="approved",
        source_refs=["source::retired-by-reason"],
        benchmark_refs=["benchmark::retired-by-reason"],
        last_researched_at="2026-07-04",
        retirement_reason="superseded-by-better-candidate",
    )
    universe = TeacherCandidateUniverse([candidate])

    assert candidate.last_researched_at == "2026-07-04"
    assert candidate.retirement_reason == "superseded-by-better-candidate"
    assert universe.promotion_blockers("retired-by-reason") == ["candidate_retired"]
    assert universe.promotion_allowed("retired-by-reason") is False


def test_package_level_candidate_universe_exports_are_importable():
    from nexusnet.teachers import TeacherCandidateUniverse, build_default_teacher_candidate_universe

    universe = build_default_teacher_candidate_universe()

    assert isinstance(universe, TeacherCandidateUniverse)
    assert universe.summary()["candidate_count"] == 3


def test_registry_get_returns_copy_so_stored_candidate_cannot_be_mutated_without_register():
    universe = build_default_teacher_candidate_universe()
    original = universe.get("leanstral-1-5")
    assert original is not None

    original.candidate_status = "shadow"
    original.license_gate = "approved"
    original.privacy_gate = "approved"
    original.hardware_gate = "approved"
    original.cost_gate = "approved"
    original.benchmark_refs.append("benchmark::mutated")

    assert universe.promotion_allowed("leanstral-1-5") is False
    assert universe.get("leanstral-1-5").candidate_status == "watchlist"


def test_register_copies_input_and_returned_candidate_to_isolate_stored_state():
    universe = TeacherCandidateUniverse()
    candidate = TeacherCandidate(
        candidate_id="mutable-registration",
        model_or_tool_id="local/mutable-registration",
        provider="local",
        source_url="https://example.invalid/mutable-registration",
        candidate_status="watchlist",
        teacher_roles=["critic"],
        source_refs=["source::mutable-registration"],
    )

    registered = universe.register(candidate)
    candidate.candidate_status = "shadow"
    candidate.license_gate = "approved"
    candidate.privacy_gate = "approved"
    candidate.hardware_gate = "approved"
    candidate.cost_gate = "approved"
    candidate.benchmark_refs.append("benchmark::input-mutated")
    registered.candidate_status = "canary"
    registered.license_gate = "approved"
    registered.privacy_gate = "approved"
    registered.hardware_gate = "approved"
    registered.cost_gate = "approved"
    registered.benchmark_refs.append("benchmark::return-mutated")

    stored = universe.get("mutable-registration")
    assert stored is not None
    assert stored.candidate_status == "watchlist"
    assert stored.license_gate == "needs_review"
    assert stored.benchmark_refs == []
    assert universe.promotion_allowed("mutable-registration") is False


def test_planned_list_candidate_filter_names_and_summary_contract_work():
    universe = build_default_teacher_candidate_universe()

    assert [candidate.candidate_id for candidate in universe.list_candidates(status="watchlist")] == [
        "leanstral-1-5",
        "qwen3-coder-next",
    ]
    assert [candidate.candidate_id for candidate in universe.list_candidates(role="critic", domain="coding")] == [
        "leanstral-1-5",
        "qwen3-coder-next",
    ]

    summary = universe.summary()
    assert summary["surface_id"] == "teacher-candidate-universe"
    assert (
        summary["autonomy_rule"]
        == "new-teacher-candidates-start-watchlist-or-quarantined-and-require-source-license-privacy-hardware-cost-benchmark-gates-before-promotion"
    )


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
