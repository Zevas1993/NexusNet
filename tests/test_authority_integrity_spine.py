from __future__ import annotations

import pytest

from nexusnet.authority.spine import AuthorityIntegritySpine


def test_capability_tokens_are_signed_scoped_and_effects_are_observed(tmp_path):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path, signing_key=b"test-signing-key")
    grant = spine.issue_grant(
        grant_id="grant:1",
        subject_ref="agent:worker",
        resource_patterns=["workspace/*"],
        allowed_effects=["read", "write"],
        evidence_refs=["approval:1"],
        expires_at="2099-01-01T00:00:00+00:00",
    )

    assert spine.verify_token(grant["token"])["valid"] is True
    receipt = spine.observe_effect(
        token=grant["token"],
        effect="write",
        resource_ref="workspace/result.json",
        before_ref="sha256:before",
        after_ref="sha256:after",
        rollback_ref="rollback:1",
    )
    assert receipt["decision"] == "allowed"
    assert receipt["receipt_sha256"].startswith("sha256:")
    with pytest.raises(PermissionError):
        spine.observe_effect(
            token=grant["token"],
            effect="network",
            resource_ref="https://example.com",
            before_ref=None,
            after_ref="sha256:response",
            rollback_ref=None,
        )


def test_reversible_transaction_restores_actual_state(tmp_path):
    spine = AuthorityIntegritySpine(artifacts_dir=tmp_path, signing_key=b"test-signing-key")
    state = {"route": "baseline", "enabled": False}
    transaction = spine.apply_transaction(
        transaction_id="tx:1",
        state=state,
        changes={"route": "candidate", "enabled": True},
        evidence_refs=["eval:pass"],
        approval_ref="approval:shadow",
    )
    assert state == {"route": "candidate", "enabled": True}
    assert transaction["status"] == "applied"

    rollback = spine.rollback_transaction("tx:1", state=state, reason_ref="monitor:regression")
    assert rollback["status"] == "rolled-back"
    assert state == {"route": "baseline", "enabled": False}


def test_capability_and_transaction_state_survive_restart(tmp_path):
    first = AuthorityIntegritySpine(artifacts_dir=tmp_path, signing_key=b"test-signing-key")
    grant = first.issue_grant(
        grant_id="grant:restart",
        subject_ref="agent:worker",
        resource_patterns=["workspace/*"],
        allowed_effects=["read"],
        evidence_refs=["approval:restart"],
        expires_at="2099-01-01T00:00:00+00:00",
    )
    state = {"enabled": False}
    first.apply_transaction(
        transaction_id="tx:restart",
        state=state,
        changes={"enabled": True},
        evidence_refs=["eval:restart"],
        approval_ref="approval:restart",
    )

    restarted = AuthorityIntegritySpine(artifacts_dir=tmp_path, signing_key=b"test-signing-key")
    assert restarted.verify_token(grant["token"])["valid"] is True
    restarted.rollback_transaction("tx:restart", state=state, reason_ref="monitor:restart")
    assert state == {"enabled": False}
