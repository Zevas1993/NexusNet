"""Wave-1 canon core-compute: SelectiveSSM, MLA, YaRN, hybrid core. Real torch, differentiable."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    SelectiveSSM,
    MLAttention,
    HybridSSMAttentionBlock,
    build_rope_yarn,
    build_rope,
    NexusNetTransformer,
    make_sequence_dataset,
    train_model,
)


# --- SelectiveSSM (Mamba2-style) ---

def test_selective_ssm_shapes_and_grad():
    ssm = SelectiveSSM(d_model=16, d_state=8, expand=2)
    x = torch.randn(2, 7, 16, requires_grad=True)
    out = ssm(x)
    assert out.shape == (2, 7, 16)
    out.sum().backward()
    assert x.grad.abs().sum() > 0
    # A must stay negative (stable diagonal recurrence): A = -exp(A_log)
    assert (-torch.exp(ssm.A_log) < 0).all()


def test_selective_ssm_is_causal_in_time():
    """SSM is a left-to-right scan: changing a later token must not change an earlier output."""
    torch.manual_seed(0)
    ssm = SelectiveSSM(d_model=12, d_state=6)
    ssm.eval()
    x = torch.randn(1, 6, 12)
    with torch.no_grad():
        y0 = ssm(x)
        x2 = x.clone()
        x2[:, 5] += 5.0                       # perturb only the last position
        y1 = ssm(x2)
    assert torch.allclose(y0[:, :5], y1[:, :5], atol=1e-5)   # earlier outputs unchanged
    assert not torch.allclose(y0[:, 5], y1[:, 5])            # last output changed


# --- MLA (Multi-head Latent Attention) ---

def test_mla_shapes_grad_and_compression():
    mla = MLAttention(d_model=32, n_heads=4, kv_latent_dim=8)
    cos, sin = build_rope(6, 8)
    x = torch.randn(2, 6, 32, requires_grad=True)
    out, latent = mla(x, cos, sin, return_latent=True)
    assert out.shape == (2, 6, 32)
    assert latent.shape == (2, 6, 8)          # the cached latent is small
    assert mla.kv_cache_ratio() < 1.0         # compresses vs full KV
    out.sum().backward()
    assert x.grad.abs().sum() > 0


def test_mla_causal_masks_future():
    mla = MLAttention(d_model=16, n_heads=2, kv_latent_dim=4, causal=True)
    cos, sin = build_rope(5, 8)
    mla.eval()
    x = torch.randn(1, 5, 16)
    with torch.no_grad():
        y0 = mla(x, cos, sin)
        x2 = x.clone(); x2[:, 4] += 9.0       # change last token only
        y1 = mla(x, cos, sin)                 # same input -> deterministic
        y2 = mla(x2, cos, sin)
    assert torch.allclose(y0, y1)
    assert torch.allclose(y0[:, :4], y2[:, :4], atol=1e-5)   # causal: earlier rows unaffected


# --- YaRN long-context scaling ---

def test_yarn_reduces_to_rope_at_scale_one():
    cos_y, sin_y, mscale = build_rope_yarn(8, 16, scale=1.0, harmonic=True)
    cos_r, sin_r = build_rope(8, 16, harmonic=True)
    assert mscale == 1.0
    assert torch.allclose(cos_y, cos_r, atol=1e-5)
    assert torch.allclose(sin_y, sin_r, atol=1e-5)


def test_yarn_scales_and_sets_attention_temperature():
    cos1, _, m1 = build_rope_yarn(8, 16, scale=1.0)
    cos8, _, m8 = build_rope_yarn(8, 16, scale=8.0, original_max_pos=4)
    assert m8 > 1.0                            # YaRN raises attention temperature when extending
    assert not torch.allclose(cos1, cos8)      # low-frequency dims are interpolated


# --- hybrid core block + integrated model ---

def test_hybrid_block_forward_and_grad_for_both_attn_kinds():
    for attn_kind in ("gqa", "mla"):
        blk = HybridSSMAttentionBlock(
            16, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2, d_hidden=32,
            d_state=8, attn_kind=attn_kind, kv_latent_dim=6,
        )
        cos, sin = build_rope(5, 4)
        x = torch.randn(2, 5, 16, requires_grad=True)
        out = blk(x, cos, sin)
        assert out.shape == (2, 5, 16)
        out.sum().backward()
        assert x.grad.abs().sum() > 0


def test_hybrid_mla_yarn_model_learns():
    torch.manual_seed(0)
    m = NexusNetTransformer(
        vocab_size=24, num_classes=3, d_model=48, n_heads=4, n_kv_heads=2,
        num_experts=6, top_k=2, d_hidden=96, max_steps=2, num_planes=11, ebt_steps=1,
        core_kind="hybrid", attn_kind="mla", d_state=8, kv_latent_dim=12,
        rope_scale=4.0, rope_original_max=8,
    )
    from nexusnet.hive.net.advanced_layers import SelectiveSSM as _SSM, MLAttention as _MLA
    assert isinstance(m.recurrent.block, HybridSSMAttentionBlock)
    assert isinstance(m.recurrent.block.ssm, _SSM)
    assert isinstance(m.recurrent.block.attn, _MLA)
    X, y = make_sequence_dataset(n=300, seq_len=12, vocab_size=24, num_classes=3, seed=0)
    metrics = train_model(m, X, y, epochs=60, lr=3e-3)
    assert metrics["gradients_flowed"] is True
    assert metrics["final_loss"] < metrics["initial_loss"]
    assert m.rope_mscale > 1.0                  # YaRN temperature actually applied during forward


def test_default_transformer_still_gqa_and_unscaled():
    m = NexusNetTransformer(vocab_size=16, num_classes=3, d_model=32, n_heads=4, n_kv_heads=2,
                            num_experts=4, top_k=2, d_hidden=64)
    from nexusnet.hive.net import TransformerBlock, GQAttention
    assert isinstance(m.recurrent.block, TransformerBlock)
    assert isinstance(m.recurrent.block.attn, GQAttention)
    assert m.rope_scale == 1.0
