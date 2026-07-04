"""Canon C12 Master Blueprint Section 1.3 - Core Brain control subsystems (real behavior, not shells)."""
from __future__ import annotations

from nexusnet.hive.core_brain_control import (
    ThermalScalingUnit, VRAMConstraintManager, RecursiveDreamerGate,
    CapsuleTrustScoring, MetaReasoner,
)


# --- 1.3.1 ThermalScalingUnit ---

def test_thermal_scaling_throttles_under_heat_with_hysteresis():
    t = ThermalScalingUnit(warn_c=75, critical_c=90, min_scale=0.25)
    assert t.scale_for(60)["compute_scale"] == 1.0
    mid = t.scale_for(82)
    assert 0.25 < mid["compute_scale"] < 1.0 and mid["state"] == "throttling"
    assert t.scale_for(95)["compute_scale"] == 0.25                # critical clamps to min
    # hysteresis: still recovering just under warn, not full speed yet
    assert t.scale_for(72)["state"] == "recovering"
    assert t.scale_for(60)["compute_scale"] == 1.0                 # fully cooled -> nominal


# --- 1.3.2 VRAMConstraintManager ---

def test_vram_manager_fits_plan_to_budget():
    m = VRAMConstraintManager(vram_budget_mb=16000, base_model_mb=4000)
    plan = m.plan(want_batch=8, want_context=4096)
    assert plan["fits"] is True
    assert plan["vram_needed_mb"] <= 16000

def test_vram_manager_downgrades_then_blocks_when_too_small():
    tiny = VRAMConstraintManager(vram_budget_mb=4100, base_model_mb=4000,
                                 bytes_per_token_per_ctx=0.01)
    plan = tiny.plan(want_batch=8, want_context=8192)
    assert plan["fits"] is True and (plan["downgraded"] or plan["batch_size"] < 8 or plan["context"] < 8192)
    nofit = VRAMConstraintManager(vram_budget_mb=100, base_model_mb=4000).plan()
    assert nofit["fits"] is False


# --- 1.3.3 RecursiveDreamerGate ---

def test_dreamer_gate_only_dreams_on_safe_spare_capacity():
    g = RecursiveDreamerGate(max_temp_c=75, min_free_vram_mb=512)
    assert g.may_dream(temp_c=50, free_vram_mb=2000, serving=False)["may_dream"] is True
    busy = g.may_dream(temp_c=50, free_vram_mb=2000, serving=True)
    assert busy["may_dream"] is False and "system_busy_serving" in busy["blocked_reasons"]
    hot = g.may_dream(temp_c=88, free_vram_mb=2000, serving=False)
    assert hot["may_dream"] is False and "thermal_throttled" in hot["blocked_reasons"]
    full = g.may_dream(temp_c=50, free_vram_mb=100, serving=False)
    assert "insufficient_free_vram" in full["blocked_reasons"]


# --- Capsule Trust Scoring ---

def test_trust_scoring_rewards_success_penalizes_consequence():
    ts = CapsuleTrustScoring(alpha=0.5)
    for _ in range(5):
        ts.record("coder", success=True, confidence=0.9)
    assert ts.trust("coder") > 0.7
    for _ in range(5):
        ts.record("flaky", success=False, confidence=0.9, consequence_failure=True)
    assert ts.trust("flaky") < ts.trust("coder")
    assert ts.ranking()[0][0] == "coder"


# --- Meta Rerouter / MetaReasoner ---

def test_meta_reasoner_reroutes_to_more_trusted_capsule():
    ts = CapsuleTrustScoring(alpha=0.6)
    for _ in range(6):
        ts.record("verifier", success=True, confidence=0.95)     # very trusted
        ts.record("guesser", success=False, confidence=0.5, consequence_failure=True)  # untrusted
    meta = MetaReasoner(ts)
    # router put 'guesser' on top with a slim confidence lead, but 'verifier' is far more trusted
    res = meta.arbitrate([{"capsule": "guesser", "confidence": 0.55},
                          {"capsule": "verifier", "confidence": 0.5}])
    assert res["rerouted"] is True and res["chosen"] == "verifier"
    assert "trust_weighted_override" in res["reasons"]

def test_meta_reasoner_confirms_a_good_pick():
    ts = CapsuleTrustScoring()
    ts.record("coder", success=True, confidence=0.9)
    res = MetaReasoner(ts).arbitrate([{"capsule": "coder", "confidence": 0.9}])
    assert res["rerouted"] is False and res["chosen"] == "coder"
