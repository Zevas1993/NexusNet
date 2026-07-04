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
