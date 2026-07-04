"""PB-2026-06-03-094 - Harness Contract & Identity Preflight: non-mutating evidence + decision."""
from __future__ import annotations

from pathlib import Path

from nexusnet.agents.harnesses.contract import (
    HarnessContractLedger, HarnessContractRequest, IdentityClaim,
)


def _req(**kw):
    base = dict(run_id="r1", harness_id="h1", required_artifacts=["skill.a", "prompt.b"],
                loaded_artifacts=["skill.a", "prompt.b"], trajectory_followed=["skill.a", "prompt.b"])
    base.update(kw)
    return HarnessContractRequest(**base)


def test_clean_run_is_allowed():
    led = HarnessContractLedger()
    rec = led.preflight(_req())
    assert rec["decision"] == "allow"
    assert rec["activation_ok"] and rec["adherence_ok"]
    assert rec["skill_load_rate"] == 1.0 and rec["adherence_rate"] == 1.0
    assert rec["mutates_production"] is False


def test_missing_required_artifact_blocks():
    led = HarnessContractLedger()
    rec = led.preflight(_req(loaded_artifacts=["skill.a"], trajectory_followed=["skill.a"]))
    assert rec["decision"] == "block"
    assert rec["missing_artifacts"] == ["prompt.b"]
    assert any("required_artifacts_not_loaded" in r for r in rec["reasons"])


def test_loaded_but_ignored_is_review_required():
    led = HarnessContractLedger()
    # both loaded, but the trajectory only followed one -> "loaded the harness but ignored it"
    rec = led.preflight(_req(trajectory_followed=["skill.a"]))
    assert rec["decision"] == "review_required"
    assert rec["activation_ok"] is True and rec["adherence_ok"] is False
    assert rec["adherence_rate"] == 0.5
    assert "self_improvement_candidate" in rec and rec["self_improvement_candidate"]["shadow_only"]


def test_raw_secret_in_context_blocks_and_is_redacted():
    led = HarnessContractLedger()
    rec = led.preflight(_req(raw_secret_field_names=["api_key"]))
    assert rec["decision"] == "block"
    assert rec["raw_secret_violation"] is True
    assert rec["redacted_secret_field_names"] == ["api_key"]   # NAME only, never a value


def test_identity_required_but_absent_blocks():
    led = HarnessContractLedger()
    rec = led.preflight(_req(requested_scopes=["repo:write"], identity=None))
    assert rec["decision"] == "block"
    assert "identity_required_but_absent" in rec["identity_violations"]


def test_requested_scopes_exceed_available_blocks():
    led = HarnessContractLedger()
    ident = IdentityClaim(account_id="acct1", owner_bound=True, available_scopes=["repo:read"])
    rec = led.preflight(_req(requested_scopes=["repo:write"], identity=ident))
    assert rec["decision"] == "block"
    assert rec["missing_scopes"] == ["repo:write"]


def test_high_risk_requires_owner_bound():
    led = HarnessContractLedger()
    claimed = IdentityClaim(account_id="acct1", owner_bound=False, claimed=True,
                            available_scopes=["api:call"])
    rec = led.preflight(_req(requested_scopes=["api:call"], high_risk_action=True, identity=claimed))
    assert rec["decision"] == "block"
    assert "high_risk_requires_owner_bound" in rec["identity_violations"]


def test_owner_bound_with_scopes_allows():
    led = HarnessContractLedger()
    ident = IdentityClaim(account_id="acct1", owner_bound=True, available_scopes=["api:call", "x"])
    rec = led.preflight(_req(requested_scopes=["api:call"], high_risk_action=True, identity=ident))
    assert rec["decision"] == "allow" and rec["identity_ok"] is True


def test_metrics_aggregate_across_runs():
    led = HarnessContractLedger()
    led.preflight(_req(run_id="ok"))
    led.preflight(_req(run_id="ignored", trajectory_followed=["skill.a"]))     # review
    led.preflight(_req(run_id="secret", raw_secret_field_names=["tok"]))       # block
    m = led.metrics()
    assert m["runs"] == 3 and m["allow"] == 1 and m["review_required"] == 1 and m["block"] == 1
    assert m["raw_secret_violations"] == 1
    assert 0.0 <= m["loaded_pass_rate"] <= 1.0


def test_records_persist_to_disk(tmp_path: Path):
    led = HarnessContractLedger(artifacts_dir=tmp_path)
    led.preflight(_req(run_id="persisted"))
    assert (tmp_path / "agents" / "harness-contract-ledger" / "persisted.json").exists()
    assert (tmp_path / "agents" / "harness-contract-ledger" / "index.jsonl").exists()
