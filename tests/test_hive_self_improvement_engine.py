"""Unified self-improvement: every aspect enumerated + tracked; real lanes run + gated; honest gaps."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.self_improvement_engine import (
    SelfImprovementEngine, default_engine, IMPROVABLE_ASPECTS,
)
from nexusnet.hive.net import (
    NexusNetLM, domain_corpus_for_capsule, make_corpus_windows, split_windows,
)


def _ctx(seed=0):
    torch.manual_seed(seed)
    corpus = domain_corpus_for_capsule("coder", n_sentences=120, seed=seed, rich=True)
    x, y = make_corpus_windows(corpus, seq_len=16)
    x_tr, y_tr, x_val, y_val = split_windows(x, y, val_fraction=0.25, seed=seed)
    model = NexusNetLM(vocab_size=259, d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
                       d_hidden=96, num_layers=2, full_features=True)
    return {"model": model, "x_tr": x_tr, "y_tr": y_tr, "x_val": x_val, "y_val": y_val, "seed": seed}


def test_taxonomy_enumerates_many_aspects():
    # self-improvement must span every aspect - the taxonomy is broad and unique
    assert len(IMPROVABLE_ASPECTS) >= 20
    assert len(set(IMPROVABLE_ASPECTS)) == len(IMPROVABLE_ASPECTS)
    for key in ("efficiency_quant", "architecture", "dreaming", "teacher_replacement",
                "tokenizer", "federation", "regulation_safety", "wrapper_absorption"):
        assert key in IMPROVABLE_ASPECTS


def test_every_aspect_has_a_real_improvement_lane():
    eng = default_engine()
    cov = eng.coverage()
    assert cov["total_aspects"] == len(IMPROVABLE_ASPECTS)
    # self-improvement spans EVERY aspect - the taxonomy is fully covered by real lanes
    assert cov["fully_covered"] is True
    assert cov["covered_count"] == len(IMPROVABLE_ASPECTS)
    assert cov["uncovered"] == []
    assert set(cov["covered"]) == set(IMPROVABLE_ASPECTS)


def test_register_rejects_unknown_aspect():
    eng = SelfImprovementEngine()
    with pytest.raises(ValueError):
        eng.register("teleportation", lambda ctx: {"improved": False})


def test_run_cycle_runs_real_lanes_and_improves_some():
    eng = default_engine()
    rec = eng.run_cycle(_ctx(0))
    # every registered lane produced a result keyed by its aspect
    assert set(rec["results"]) == set(eng.lanes)
    for aspect, r in rec["results"].items():
        assert r["aspect"] == aspect
        assert "improved" in r
    # at least one aspect genuinely improved this cycle (weights and/or efficiency)
    assert rec["improved_count"] >= 1
    assert "efficiency_quant" in rec["results"]
    assert rec["results"]["efficiency_quant"]["improved"] is True   # bit-model search always finds a win
    assert len(eng.history) == 1


def test_lane_failure_is_recorded_not_raised():
    eng = SelfImprovementEngine()
    eng.register("tokenizer", lambda ctx: 1 / 0)          # a broken lane
    rec = eng.run_cycle({})
    assert rec["results"]["tokenizer"]["skipped"] is True
    assert "error" in rec["results"]["tokenizer"]["reason"]


def test_lanes_skip_cleanly_without_required_context():
    eng = default_engine()
    rec = eng.run_cycle({})                               # no model/data
    # nothing crashes; data-needing lanes skip
    assert rec["results"]["dreaming"]["skipped"] is True
    assert rec["results"]["weights_capability"]["skipped"] is True


def test_efficiency_and_absorption_lanes_work_on_full_feature_model():
    eng = default_engine()
    ctx = _ctx(1)
    eff = eng.improve("efficiency_quant", ctx)
    assert eff["improved"] is True and eff["metric_after"] > 1.0
    absorb = eng.improve("wrapper_absorption", ctx)
    assert absorb["improved"] is True                    # full-feature model fully absorbs the wrapper
