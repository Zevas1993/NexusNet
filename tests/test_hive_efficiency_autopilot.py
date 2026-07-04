"""Autonomous efficiency self-improvement: search bit-models/quants, adopt efficiency wins (gated)."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    NexusNetLM, layer_quant_sensitivity, optimize_bit_allocation, EfficiencyAutopilot,
)


def _model(seed=0):
    torch.manual_seed(seed)
    return NexusNetLM(vocab_size=128, d_model=64, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
                      d_hidden=128, num_layers=2)


def test_sensitivity_is_monotonic_in_bits():
    sens = layer_quant_sensitivity(_model())
    assert sens
    for name, by_bits in sens.items():
        # fewer bits -> >= error (coarser quantization never reduces error)
        assert by_bits[2] >= by_bits[4] - 1e-6 >= 0
        assert by_bits[4] >= by_bits[8] - 1e-6 >= 0


def test_optimize_bit_allocation_is_a_mixed_precision_bit_model():
    alloc = optimize_bit_allocation(_model(), error_budget=0.06)
    assert alloc["layers"] >= 1
    assert all(b in (2, 4, 8) for b in alloc["bit_profile"].values())
    assert alloc["avg_bits_per_param"] < 16          # genuinely compresses vs fp16
    assert alloc["compression_vs_fp16"] > 1.0
    assert alloc["max_layer_error"] <= 0.06          # respected the quality budget


def test_tighter_budget_uses_more_bits():
    loose = optimize_bit_allocation(_model(), error_budget=0.2)
    tight = optimize_bit_allocation(_model(), error_budget=0.01)
    # a stricter quality budget forces higher precision -> more bits / less compression
    assert tight["avg_bits_per_param"] >= loose["avg_bits_per_param"]


def test_autopilot_adopts_efficiency_win_within_quality_gate():
    auto = EfficiencyAutopilot(error_budget=0.08)
    rec = auto.improvement_cycle(_model())
    assert rec["adopted"] is True
    assert rec["best_compression"] > 1.0             # found a real compression over fp16
    assert auto.best["max_error"] <= 0.08            # the adopted bit-model passes the quality gate
    assert rec["mutates_production"] is False


def test_autopilot_efficiency_is_monotonic_over_cycles():
    auto = EfficiencyAutopilot(error_budget=0.08)
    out = auto.run(_model(), cycles=4)
    assert out["cycles"] == 4
    assert out["efficiency_monotonic"] is True       # never regresses adopted efficiency
    assert out["final_compression_vs_fp16"] > 1.0
    assert out["final_est_speedup"] > 1.0
    assert out["best_bit_model"]["max_error"] <= 0.08


def test_quality_gate_can_reject_overaggressive_quants():
    # an impossibly tight budget -> the only eligible candidate is fp16 (no lossy quant passes)
    auto = EfficiencyAutopilot(error_budget=0.0)
    rec = auto.improvement_cycle(_model())
    assert auto.best["name"] == "fp16-baseline"
    assert "uniform-4bit" in rec["rejected_quality_gate"]
