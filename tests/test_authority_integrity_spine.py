import json

import pytest
from pydantic import ValidationError

from nexusnet.authority import EffectType
from nexusnet.authority.contracts import AuthorityDecisionRecord
from nexusnet.authority.spine import AuthorityIntegritySpine


def test_authority_spine_blocks_write_effect_without_sandbox_and_approval(tmp_path):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path)

    decision = spine.evaluate(
        action_id="action:file-write",
        actor_ref="agent:researcher",
        effect_type="filesystem_write",
        capability_refs=[],
        sandbox_state="none",
        operator_approved=False,
        evidence_refs=["trace:file-write-request"],
    )

    assert decision["status"] == "blocked"
    assert "write_effect_requires_sandbox" in decision["blockers"]
    assert "write_effect_requires_operator_approval" in decision["blockers"]
    assert decision["production_action_allowed"] is False


def test_authority_spine_records_readonly_receipt(tmp_path):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path)

    decision = spine.evaluate(
        action_id="action:file-read",
        actor_ref="agent:researcher",
        effect_type="filesystem_read",
        capability_refs=["cap:repo-read"],
        sandbox_state="project-readonly",
        operator_approved=False,
        evidence_refs=["trace:file-read-request"],
    )

    assert decision["status"] == "allowed-shadow"
    assert decision["observed_effect_receipt"]["declared_effect_type"] == "filesystem_read"
    assert decision["rollback_record"]["rollback_required"] is False


def test_authority_spine_returns_revalidatable_decision(tmp_path):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path)

    decision = spine.evaluate(
        action_id="action:revalidate",
        actor_ref="agent:researcher",
        effect_type="network",
        capability_refs=["cap:network-shadow"],
        sandbox_state="network-shadow",
        operator_approved=False,
        evidence_refs=["trace:network-request"],
    )

    revalidated = AuthorityDecisionRecord(**decision)

    assert revalidated.action_id == decision["action_id"]
    assert revalidated.artifact_path == decision["artifact_path"]


def test_authority_spine_exports_effect_type_contract():
    assert EffectType is not None


def test_authority_spine_summary_sees_persisted_valid_decisions_after_restart(tmp_path):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path)
    decision = spine.evaluate(
        action_id="action:persisted-read",
        actor_ref="agent:researcher",
        effect_type="filesystem_read",
        capability_refs=["cap:repo-read"],
        sandbox_state="project-readonly",
        operator_approved=False,
        evidence_refs=["trace:persisted-read"],
    )

    summary = AuthorityIntegritySpine(artifacts_dir=tmp_path).summary()

    assert summary["decision_count"] == 1
    assert summary["latest_decision"]["action_id"] == decision["action_id"]


@pytest.mark.parametrize("action_id", ["..\\escaped\\write", "../escaped/write", "nested/path/.."])
def test_authority_spine_safely_persists_unsafe_action_ids_inside_root(tmp_path, action_id):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path)

    decision = spine.evaluate(
        action_id=action_id,
        actor_ref="agent:researcher",
        effect_type="filesystem_write",
        capability_refs=["cap:file-write"],
        sandbox_state="project-write",
        operator_approved=True,
        evidence_refs=["trace:unsafe-id"],
    )

    decisions_dir = tmp_path / "authority" / "decisions"
    artifact_path = type(tmp_path)(decision["artifact_path"]).resolve()

    assert artifact_path.parent == decisions_dir.resolve()
    assert artifact_path.exists()
    assert not (decisions_dir / ".." / "escaped").exists()
    assert not (decisions_dir / "nested").exists()


def test_authority_spine_does_not_record_phantoms_after_write_failure(tmp_path, monkeypatch):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path)

    def fail_write(*args, **kwargs):
        raise OSError("simulated write failure")

    monkeypatch.setattr(type(tmp_path), "write_text", fail_write)

    with pytest.raises(OSError):
        spine.evaluate(
            action_id="action:write-failure",
            actor_ref="agent:researcher",
            effect_type="filesystem_read",
            capability_refs=["cap:repo-read"],
            sandbox_state="project-readonly",
            operator_approved=False,
            evidence_refs=["trace:write-failure"],
        )

    assert spine.summary()["decision_count"] == 0


def test_authority_spine_skips_invalid_disk_files_without_hiding_valid_records(tmp_path):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path)
    valid = spine.evaluate(
        action_id="action:valid-disk",
        actor_ref="agent:researcher",
        effect_type="filesystem_read",
        capability_refs=["cap:repo-read"],
        sandbox_state="project-readonly",
        operator_approved=False,
        evidence_refs=["trace:valid-disk"],
    )
    decisions_dir = tmp_path / "authority" / "decisions"
    (decisions_dir / "corrupt.json").write_text("{", encoding="utf-8")
    (decisions_dir / "non-object.json").write_text(json.dumps([]), encoding="utf-8")
    (decisions_dir / "invalid-model.json").write_text(json.dumps({"action_id": "missing-required"}), encoding="utf-8")

    summary = AuthorityIntegritySpine(artifacts_dir=tmp_path).summary()

    assert summary["decision_count"] == 1
    assert summary["latest_decision"]["action_id"] == valid["action_id"]


def test_authority_spine_dedupes_duplicate_disk_decisions_deterministically(tmp_path):
    decisions_dir = tmp_path / "authority" / "decisions"
    decisions_dir.mkdir(parents=True)
    first = AuthorityDecisionRecord(
        action_id="action:duplicate",
        actor_ref="agent:first",
        effect_type="filesystem_read",
        status="allowed-shadow",
        sandbox_state="project-readonly",
        operator_approved=False,
        observed_effect_receipt={
            "receipt_id": "effect::action:duplicate",
            "declared_effect_type": "filesystem_read",
            "observed_effect_type": "filesystem_read",
            "created_at": "2026-05-06T00:00:01+00:00",
        },
        rollback_record={
            "rollback_id": "rollback::action:duplicate",
            "rollback_required": False,
            "rollback_available": False,
        },
    ).model_dump(mode="json")
    second = AuthorityDecisionRecord(
        action_id="action:duplicate",
        actor_ref="agent:second",
        effect_type="filesystem_read",
        status="allowed-shadow",
        sandbox_state="project-readonly",
        operator_approved=False,
        observed_effect_receipt={
            "receipt_id": "effect::action:duplicate",
            "declared_effect_type": "filesystem_read",
            "observed_effect_type": "filesystem_read",
            "created_at": "2026-05-06T00:00:02+00:00",
        },
        rollback_record={
            "rollback_id": "rollback::action:duplicate",
            "rollback_required": False,
            "rollback_available": False,
        },
    ).model_dump(mode="json")
    (decisions_dir / "a.json").write_text(json.dumps(first), encoding="utf-8")
    (decisions_dir / "b.json").write_text(json.dumps(second), encoding="utf-8")

    summary = AuthorityIntegritySpine(artifacts_dir=tmp_path).summary()

    assert summary["decision_count"] == 1
    assert summary["latest_decision"]["action_id"] == "action:duplicate"
    assert summary["latest_decision"]["actor_ref"] == "agent:second"


def test_authority_spine_in_memory_record_wins_over_duplicate_disk_decision(tmp_path):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path)
    memory_decision = spine.evaluate(
        action_id="action:memory-wins",
        actor_ref="agent:memory",
        effect_type="filesystem_read",
        capability_refs=["cap:repo-read"],
        sandbox_state="project-readonly",
        operator_approved=False,
        evidence_refs=["trace:memory"],
    )
    disk_decision = AuthorityDecisionRecord(
        **{
            **memory_decision,
            "actor_ref": "agent:disk",
            "observed_effect_receipt": {
                **memory_decision["observed_effect_receipt"],
                "created_at": "2999-01-01T00:00:00+00:00",
            },
        }
    ).model_dump(mode="json")
    (tmp_path / "authority" / "decisions" / "duplicate.json").write_text(json.dumps(disk_decision), encoding="utf-8")

    summary = spine.summary()

    assert summary["decision_count"] == 1
    assert summary["latest_decision"]["actor_ref"] == "agent:memory"


def test_authority_spine_invalid_effect_type_raises_validation_error_without_persisting(tmp_path):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path)

    with pytest.raises(ValidationError):
        spine.evaluate(
            action_id="action:invalid-effect",
            actor_ref="agent:researcher",
            effect_type="invalid-effect",
            capability_refs=[],
            sandbox_state="project-readonly",
            operator_approved=False,
            evidence_refs=["trace:invalid-effect"],
        )

    assert spine.summary()["decision_count"] == 0
    assert not any((tmp_path / "authority" / "decisions").glob("*.json"))
