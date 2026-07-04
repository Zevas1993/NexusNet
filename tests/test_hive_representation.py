"""Wave-4: multimodal encoders + fusion, byte-level BPE tokenizer, quantization-aware + export."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    TextEncoder, VisionEncoder, AudioEncoder, VideoEncoder, TableEncoder,
    MultimodalFusion, MODALITIES,
    BPETokenizer,
    FakeQuantize, quantization_error, quantize_dynamic_int8, export_birthed_model,
    NexusNetTransformer,
)


# --- multimodal encoders + fusion ---

def test_each_encoder_maps_its_modality_into_d_model():
    d = 32
    text = TextEncoder(50, d)(torch.randint(0, 50, (2, 7)))
    vision = VisionEncoder(d, in_channels=3, patch=4)(torch.randn(2, 3, 8, 8))
    audio = AudioEncoder(d, n_mels=16)(torch.randn(2, 20, 16))
    video = VideoEncoder(d, in_channels=3, patch=4)(torch.randn(2, 5, 3, 8, 8))
    table = TableEncoder(d, n_features=9)(torch.randn(2, 9))
    for t in (text, vision, audio, video, table):
        assert t.shape[0] == 2 and t.shape[-1] == d and t.dim() == 3


def test_multimodal_fusion_unifies_streams_and_is_differentiable():
    d = 32
    text_enc = TextEncoder(50, d)
    vis_enc = VisionEncoder(d, patch=4)
    tab_enc = TableEncoder(d, n_features=4)
    fusion = MultimodalFusion(d, n_heads=2)
    streams = {
        "text": text_enc(torch.randint(0, 50, (2, 5))),
        "vision": vis_enc(torch.randn(2, 3, 8, 8)),
        "table": tab_enc(torch.randn(2, 4)),
    }
    unified = fusion(streams)
    total_T = sum(s.shape[1] for s in streams.values())
    assert unified.shape == (2, total_T, d)
    unified.sum().backward()
    # gradients reach the fusion AND each modality encoder (truly end-to-end fused)
    assert fusion.modality_embed.grad is not None and fusion.modality_embed.grad.abs().sum() > 0
    assert text_enc.embed.weight.grad is not None and text_enc.embed.weight.grad.abs().sum() > 0
    assert vis_enc.proj.weight.grad is not None and vis_enc.proj.weight.grad.abs().sum() > 0
    assert set(MODALITIES) >= {"text", "vision", "audio", "video", "table", "code"}


def test_fusion_rejects_unknown_modality():
    with pytest.raises(ValueError):
        MultimodalFusion(16)({"smell": torch.randn(1, 2, 16)})


# --- byte-level BPE tokenizer ---

def test_bpe_trains_merges_and_round_trips():
    text = "the cortex routes the tokens. " * 50
    tok = BPETokenizer().train(text, vocab_size=320)
    assert tok.vocab_size > 256 and len(tok.merges) > 0       # learned merges beyond byte base
    ids = tok.encode("the cortex routes the tokens.")
    assert tok.decode(ids) == "the cortex routes the tokens."  # lossless round-trip


def test_bpe_compresses_vs_raw_bytes():
    text = "abcabcabc " * 100
    tok = BPETokenizer().train(text, vocab_size=300)
    ids = tok.encode("abcabcabc ")
    raw = list("abcabcabc ".encode("utf-8"))
    assert len(ids) < len(raw)                                 # merges shorten frequent sequences


def test_bpe_save_load_roundtrip(tmp_path):
    tok = BPETokenizer().train("hello hive mind hello hive", vocab_size=300)
    p = tok.save(str(tmp_path / "bpe.json"))
    reloaded = BPETokenizer.load(p)
    s = "hello hive"
    assert reloaded.encode(s) == tok.encode(s)
    assert reloaded.decode(reloaded.encode(s)) == s


def test_bpe_handles_unicode():
    tok = BPETokenizer().train("café résumé café résumé", vocab_size=290)
    assert tok.decode(tok.encode("café")) == "café"


# --- quantization-aware + export ---

def test_fake_quantize_is_straight_through_and_simulates_int8():
    fq = FakeQuantize(num_bits=8)
    x = torch.randn(64, requires_grad=True)
    q = fq(x)
    assert torch.allclose(q.abs().max(), x.detach().abs().max(), atol=x.abs().max().item() / 127 + 1e-4)
    q.sum().backward()
    assert x.grad is not None and torch.allclose(x.grad, torch.ones_like(x))  # STE passes grad


def test_quantization_error_is_small_for_int8():
    m = NexusNetTransformer(vocab_size=24, num_classes=3, d_model=32, n_heads=4, n_kv_heads=2,
                            num_experts=4, top_k=2, d_hidden=64, max_steps=1, ebt_steps=1)
    err = quantization_error(m)
    assert 0.0 <= err["relative_l2_error"] < 0.2 and err["bits"] == 8


def test_dynamic_int8_quantization_runs():
    # Dynamic int8 targets feed-forward Linear stacks (inference compression); use the MoE classifier
    # core (no EBT inner-gradient descent, which is intentionally incompatible with quantized linears).
    from nexusnet.hive.net import NexusNetModel
    m = NexusNetModel(in_dim=8, d_model=32, d_hidden=64, num_experts=4, top_k=2,
                      num_classes=3, num_layers=2)
    q = quantize_dynamic_int8(m)
    with torch.no_grad():
        out = q(torch.randn(2, 8))
    assert out.shape == (2, 3) and torch.isfinite(out).all()


def test_export_writes_real_artifacts(tmp_path):
    m = NexusNetTransformer(vocab_size=24, num_classes=3, d_model=32, n_heads=4, n_kv_heads=2,
                            num_experts=4, top_k=2, d_hidden=64, max_steps=1, ebt_steps=1)
    example = torch.randint(0, 24, (1, 8))
    report = export_birthed_model(m, str(tmp_path / "export"), example_input=example,
                                  config={"d_model": 32}, formats=("safetensors", "gguf"))
    assert "safetensors" in report["written"]                  # state dict always written
    assert report["formats"]["gguf"]["status"] == "conversion_manifest"   # honest GGUF boundary
    import os
    assert os.path.exists(report["formats"]["safetensors"]["path"])
    assert os.path.exists(report["formats"]["gguf"]["path"])
