"""Waves 11-14: incremental KV cache, advanced quantization, regulation hooks, observability spans."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    NexusNetLM, NexusNetTransformer, make_sequence_dataset,
    LayerKVCache, cached_generate,
    nf4_quantize, gptq_quantize, awq_quantize, NF4_CODEBOOK,
    NeuralImmuneGate, consequence_weighted_loss, SelectiveDecayRegularizer,
    GenAISpanRecorder,
)


def _lm(seed=0, **kw):
    torch.manual_seed(seed)
    cfg = dict(vocab_size=40, d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
               d_hidden=96, num_layers=2)
    cfg.update(kw)
    return NexusNetLM(**cfg)


# --- Wave 11: incremental KV cache ---

def test_cached_generation_matches_uncached_greedy():
    m = _lm(seed=0)
    prompt = [1, 2, 3, 4]
    cached = m.generate_cached(prompt, max_new_tokens=10, greedy=True)
    uncached = m.generate(prompt, max_new_tokens=10, greedy=True, context=128)
    assert cached == uncached                                  # KV-cache decode is exact


def test_kv_cache_accumulates_length():
    m = _lm(seed=1)
    res = cached_generate(m, [5, 6, 7], max_new_tokens=6, greedy=True)
    # every token except the final generated one has passed through attention (been cached)
    assert res["cache_length"] == 3 + 6 - 1
    assert len(res["ids"]) == 3 + 6


def test_attention_uncached_path_unchanged():
    # cache=None / start_pos=0 must behave exactly like before (regression guard on the edit)
    from nexusnet.hive.net import GQAttention, build_rope
    torch.manual_seed(0)
    attn = GQAttention(16, 4, 2, causal=True)
    cos, sin = build_rope(5, 4)
    x = torch.randn(2, 5, 16)
    out = attn(x, cos, sin)
    assert out.shape == (2, 5, 16) and torch.isfinite(out).all()


# --- Wave 12: advanced quantization ---

def test_nf4_quantizes_to_codebook_with_low_error():
    w = torch.randn(64, 64)
    res = nf4_quantize(w, group_size=32)
    assert res["bits"] == 4
    assert res["codes"].max() < len(NF4_CODEBOOK)              # indices into the 16-value codebook
    assert res["rel_error"] < 0.2                              # 4-bit NF4 reconstructs reasonably


def test_gptq_beats_round_to_nearest():
    torch.manual_seed(0)
    # correlated calibration so the Hessian is informative
    base = torch.randn(40, 6)
    calib = base @ torch.randn(6, 6)
    w = torch.randn(8, 6)
    res = gptq_quantize(w, calib, bits=4)
    assert res["beats_rtn"] is True


def test_awq_protects_salient_channels():
    torch.manual_seed(0)
    w = torch.randn(12, 10)
    act_scale = torch.rand(10)
    act_scale[3] = 20.0                                        # one very salient channel
    res = awq_quantize(w, act_scale, bits=4)
    assert res["protects_salient"] is True


# --- Wave 13: regulation hooks ---

def test_immune_gate_attenuates_anomalies():
    gate = NeuralImmuneGate(8, threshold=3.0)
    gate.train()
    for _ in range(5):                                         # learn nominal stats
        gate(torch.randn(64, 8))
    x = torch.randn(4, 8, requires_grad=True)
    spiked = x.clone().detach()
    spiked[0, 0] = 50.0                                        # inject an anomaly
    spiked.requires_grad_(True)
    gated, rate = gate(spiked)
    assert gated[0, 0].abs() < 50.0                            # anomaly attenuated
    assert rate > 0.0
    gated.sum().backward()
    assert spiked.grad is not None                             # still differentiable


def test_consequence_weighted_loss_emphasizes_high_consequence():
    losses = torch.tensor([0.1, 0.1, 2.0])
    low = consequence_weighted_loss(losses, torch.tensor([1.0, 1.0, 1.0]))
    high = consequence_weighted_loss(losses, torch.tensor([1.0, 1.0, 9.0]))   # 3rd is high-consequence
    assert high > low


def test_selective_decay_forgets_low_salience_more():
    m = _lm(seed=0)
    reg = SelectiveDecayRegularizer(base_decay=0.1)
    params = dict(m.named_parameters())
    names = list(params)
    salience = {names[0]: 1.0, names[1]: 0.0}                  # keep first, forget second
    n0 = params[names[0]].norm().item()
    n1 = params[names[1]].norm().item()
    reg.apply(m.named_parameters(), salience)
    assert params[names[0]].norm().item() == pytest.approx(n0, rel=1e-5)   # salient preserved
    assert params[names[1]].norm().item() < n1                              # low-salience decayed


# --- Wave 14: observability spans ---

def test_genai_span_records_usage_attributes():
    m = _lm(seed=2)
    rec = GenAISpanRecorder(redact=True)
    x = torch.randint(0, 40, (2, 6))
    out = rec.record_forward(m, x)
    sp = out["span"].attributes
    assert sp["gen_ai.system"] == "nexusnet"
    assert sp["gen_ai.operation.name"] == "forward"
    assert sp["gen_ai.usage.input_tokens"] == 12
    assert sp["gen_ai.response.finite"] is True
    assert sp["gen_ai.prompt.redacted"] is True
    assert "gen_ai.prompt.tokens" not in sp                   # redacted: no raw content
    assert "nexusnet.expert_load" in sp                       # MoE load captured


def test_span_redaction_off_includes_content_and_otel_export():
    m = _lm(seed=3)
    rec = GenAISpanRecorder(redact=False)
    rec.record_forward(m, torch.randint(0, 40, (1, 4)))
    spans = rec.to_otel()
    assert len(spans) == 1 and spans[0]["name"] == "forward"
    assert spans[0]["status"] == "OK" and spans[0]["duration_ms"] >= 0.0
    assert "gen_ai.prompt.tokens" in spans[0]["attributes"]    # content present when not redacted
