from __future__ import annotations

import pytest

from nexusnet.memory.evolution import MemoryEvolutionRegistry


def _ready_fields(**overrides):
    fields = {
        "passport_id": "memory-change-1",
        "operation": "store",
        "fact_id": "fact:gpu-offload",
        "content": "Pinned host buffers reduce repeated pageable-memory staging.",
        "source_refs": ["paper:offload-1"],
        "privacy_class": "internal",
        "consent_status": "granted",
        "confidence": 0.91,
        "contradiction_refs": [],
        "eval_refs": ["eval:retrieval-1"],
        "eval_passed": True,
        "reviewer_refs": ["review:memory-ao", "review:nexusbrain"],
        "rollback_plan": {"mode": "snapshot-restore"},
        "promotion_state": "shadow",
    }
    fields.update(overrides)
    return fields


def test_memory_evolution_passport_is_fail_closed_and_contains_no_raw_content(tmp_path):
    registry = MemoryEvolutionRegistry(artifacts_dir=tmp_path)

    passport = registry.propose(**_ready_fields(eval_refs=[], eval_passed=False, reviewer_refs=[]))

    assert passport["status"] == "blocked"
    assert "eval-pass-required" in passport["blockers"]
    assert "reviewer-pair-required" in passport["blockers"]
    assert "content" not in passport
    assert passport["content_ref"].startswith("sha256:")
    with pytest.raises(PermissionError):
        registry.apply(passport["passport_id"], content="wrong")


def test_memory_evolution_apply_restart_and_rollback_restore_prior_state(tmp_path):
    registry = MemoryEvolutionRegistry(artifacts_dir=tmp_path)
    created = registry.propose(**_ready_fields())
    applied = registry.apply(created["passport_id"], content=_ready_fields()["content"])

    assert applied["status"] == "applied"
    assert "snapshot" not in applied
    assert "Pinned host buffers" not in (tmp_path / "memory" / "evolution-passports.json").read_text(encoding="utf-8")
    assert registry.memory.retrieve("fact:gpu-offload").content.startswith("Pinned host buffers")

    restarted = MemoryEvolutionRegistry(artifacts_dir=tmp_path)
    assert restarted.get("memory-change-1")["status"] == "applied"
    assert restarted.memory.retrieve("fact:gpu-offload") is not None

    rolled_back = restarted.rollback("memory-change-1", reason_ref="operator:revert")
    assert rolled_back["status"] == "rolled-back"
    assert restarted.memory.retrieve("fact:gpu-offload", include_archived=True, include_discarded=True) is None


def test_forgetting_redacts_content_but_preserves_audit_and_can_rollback(tmp_path):
    registry = MemoryEvolutionRegistry(artifacts_dir=tmp_path)
    initial = registry.propose(**_ready_fields())
    registry.apply(initial["passport_id"], content=_ready_fields()["content"])
    forget = registry.propose(
        **_ready_fields(
            passport_id="memory-forget-1",
            operation="forget",
            content=None,
            promotion_state="active",
        )
    )

    registry.apply(forget["passport_id"])
    forgotten = registry.memory.retrieve(
        "fact:gpu-offload", include_archived=True, include_discarded=True
    )
    assert forgotten.discarded is True
    assert forgotten.content.startswith("[forgotten:sha256:")
    assert "Pinned host buffers" not in (tmp_path / "memory" / "state.json").read_text(encoding="utf-8")

    registry.rollback("memory-forget-1", reason_ref="privacy-review:restore")
    restored = registry.memory.retrieve("fact:gpu-offload")
    assert restored.content.startswith("Pinned host buffers")
