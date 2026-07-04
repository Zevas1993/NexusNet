"""Wave-6: inference runtime, hardware/safe-mode, neurosymbolic, EBT-in-forward, born-model serving."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    NexusNetLM,
    NexusNetTransformer,
    speculative_decode, PrefixCache, ContinuousBatcher, kv_cache_report,
    HardwareProfile, AdaptiveRuntimePolicy, SafeModeGuard, safe_forward,
    Rule, SymbolicRuleEngine, NeuroSymbolicReasoner,
    BornModelRunner,
    export_birthed_model,
)


def _lm(seed=0, **kw):
    torch.manual_seed(seed)
    cfg = dict(vocab_size=40, d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
               d_hidden=96, num_layers=2)
    cfg.update(kw)
    return NexusNetLM(**cfg)


# --- inference runtime ---

def test_speculative_decoding_matches_target_greedy():
    target = _lm(seed=0)
    draft = _lm(seed=0)                                   # identical draft => high acceptance
    prompt = [1, 2, 3, 4]
    spec = speculative_decode(target, draft, prompt, max_new_tokens=8, gamma=4)
    ref = target.generate(prompt, max_new_tokens=8, greedy=True, context=64)
    assert spec["ids"] == ref                            # greedy speculative == target greedy
    assert spec["acceptance_rate"] == 1.0                # identical draft accepts everything
    assert spec["target_forwards"] < 8                   # fewer target steps than tokens produced


def test_prefix_cache_reuses_computation():
    m = _lm(seed=1)
    cache = PrefixCache()
    ids = [3, 1, 4, 1, 5]
    a = cache.next_logits(m, ids)
    b = cache.next_logits(m, ids)                         # same prefix -> hit
    assert torch.allclose(a, b)
    assert cache.hits == 1 and cache.misses == 1 and cache.hit_rate == 0.5


def test_continuous_batching_runs_all_requests():
    m = _lm(seed=2)
    batcher = ContinuousBatcher(m, pad_id=0)
    batcher.admit("a", [1, 2, 3], max_new=4)
    batcher.admit("b", [5, 6], max_new=4)
    out = batcher.run(max_steps=10)
    assert len(out["a"]) == 3 + 4 and len(out["b"]) == 2 + 4   # each produced its tokens


def test_kv_cache_report_shows_mla_compression():
    rep = kv_cache_report(n_layers=4, n_kv_heads=2, head_dim=16, seq_len=1024, mla_latent_dim=8)
    assert rep["full_kv_bytes"] > rep["mla_kv_bytes"]
    assert rep["compression_ratio"] < 1.0


# --- hardware-aware runtime + safe mode ---

def test_adaptive_policy_plans_for_hardware():
    policy = AdaptiveRuntimePolicy()
    gpu = policy.plan(HardwareProfile(True, 16.0, "cuda", "RTX 5070 Ti"), param_count=10_000_000)
    cpu = policy.plan(HardwareProfile(False, 0.0, "cpu"), param_count=10_000_000)
    assert gpu.device == "cuda" and gpu.max_context >= cpu.max_context
    assert cpu.device == "cpu" and cpu.quantize is True
    assert HardwareProfile.detect().device in ("cpu", "cuda")


def test_safe_mode_throttles_and_pauses():
    guard = SafeModeGuard(vram_limit_gb=16.0, base_batch=8, base_context=8192)
    nominal = guard.assess(vram_used_gb=4.0, temp_c=60.0)
    throttled = guard.assess(vram_used_gb=14.0, temp_c=60.0)
    paused = guard.assess(vram_used_gb=15.9, temp_c=70.0)
    assert nominal.action == "proceed"
    assert throttled.action == "throttle" and throttled.batch_size < 8
    assert paused.action == "pause" and paused.safe is False


def test_safe_forward_gates_the_real_forward():
    m = _lm(seed=3)
    guard = SafeModeGuard(vram_limit_gb=16.0, base_batch=8)
    x = torch.randint(0, 40, (8, 6))
    paused = safe_forward(m, x, guard, vram_used_gb=15.9, temp_c=95.0)
    assert paused["ran"] is False and paused["output"] is None
    throttled = safe_forward(m, x, guard, vram_used_gb=14.0, temp_c=60.0)
    assert throttled["ran"] is True and throttled["output"].shape[0] <= 4   # batch trimmed


# --- neurosymbolic reasoning ---

def test_rule_engine_forward_chains_to_closure():
    eng = SymbolicRuleEngine([Rule(("a", "b"), "c"), Rule(("c",), "d")])
    assert eng.infer({"a", "b"}) == {"a", "b", "c", "d"}
    assert eng.infer({"a"}) == {"a"}                     # antecedents incomplete -> no firing


def test_neurosymbolic_forbids_and_boosts():
    eng = SymbolicRuleEngine([Rule(("danger",), "forbid_2")])
    reasoner = NeuroSymbolicReasoner(
        num_classes=3,
        forbid_fn=lambda facts: {2} if "forbid_2" in facts else set(),
        entail_fn=lambda facts: {0} if "prefer_0" in facts else set(),
        boost=5.0,
    )
    logits = torch.zeros(1, 3)
    out = reasoner.reason(logits, {"danger", "prefer_0"}, eng)
    assert out[0, 2] == float("-inf")                    # hard constraint applied
    assert out[0, 0] == 5.0                              # entailment boost applied
    assert int(out.argmax()) == 0


# --- EBT participates in the trainable forward ---

def test_ebt_is_in_the_trainable_forward():
    m = NexusNetTransformer(vocab_size=24, num_classes=3, d_model=32, n_heads=4, n_kv_heads=2,
                            num_experts=4, top_k=2, d_hidden=64, max_steps=1, ebt_steps=2)
    x = torch.randint(0, 24, (2, 6))
    out = m(x)
    out.sum().backward()
    # the EBT energy network received gradient => it is part of the live forward/backward graph
    assert any(p.grad is not None and p.grad.abs().sum() > 0 for p in m.ebt.parameters())


# --- standalone born-model serving (substrate-free) ---

def test_born_model_serves_independently(tmp_path):
    cfg = dict(vocab_size=40, d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
               d_hidden=96, num_layers=2)
    born = _lm(seed=7, **{k: v for k, v in cfg.items() if k != "vocab_size"})
    report = export_birthed_model(born, str(tmp_path / "exp"), config=cfg, formats=("safetensors",))
    assert "safetensors" in report["written"]
    runner = BornModelRunner.from_export_dir(str(tmp_path / "exp"), config=cfg)
    indep = runner.is_independent()
    assert indep["inference_only"] and indep["standalone"]
    out = runner.generate([1, 2, 3], max_new_tokens=5)
    assert len(out) == 3 + 5
    # the reloaded standalone model reproduces the birthed model's greedy output
    assert out == born.generate([1, 2, 3], max_new_tokens=5, greedy=True)
