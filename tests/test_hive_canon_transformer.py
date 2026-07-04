from __future__ import annotations

import math

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    NexusNetTransformer,
    TransformerBlock,
    MoECapsuleLayer,
    RMSNorm,
    GQAttention,
    EBTRefinement,
    RecurrentDepth,
    MultiPlaneMemory,
    CortexPool,
    build_rope,
    apply_rope,
    make_sequence_dataset,
    train_model,
)


# --- individual canon layers are real & differentiable ---

def test_rmsnorm_normalizes_and_is_learnable():
    norm = RMSNorm(8)
    x = torch.randn(4, 8, requires_grad=True)
    out = norm(x)
    rms = out.pow(2).mean(dim=-1).sqrt()
    assert torch.allclose(rms, torch.ones_like(rms), atol=1e-3)
    out.sum().backward()
    assert norm.weight.grad is not None


def test_rope_is_norm_preserving():
    cos, sin = build_rope(seq_len=5, head_dim=8, harmonic=True)
    x = torch.randn(2, 3, 5, 8)              # (B, H, T, D)
    r = apply_rope(x, cos, sin)
    assert torch.allclose(x.norm(dim=-1), r.norm(dim=-1), atol=1e-4)


def test_gqa_attention_shapes_and_grads():
    attn = GQAttention(d_model=16, n_heads=4, n_kv_heads=2)
    cos, sin = build_rope(6, 4)
    x = torch.randn(2, 6, 16, requires_grad=True)
    out = attn(x, cos, sin)
    assert out.shape == (2, 6, 16)
    out.sum().backward()
    assert x.grad.abs().sum() > 0


def test_ebt_descends_energy_and_works_under_no_grad():
    ebt = EBTRefinement(12, steps=3, lr=0.3)
    ebt.eval()
    x = torch.randn(5, 12)
    e0 = ebt.energy(x).sum().item()
    with torch.no_grad():                    # inference path must still run the energy descent
        refined = ebt(x)
    e1 = ebt.energy(refined).sum().item()
    assert e1 <= e0 + 1e-4                    # energy did not increase
    assert refined.shape == x.shape


def test_recurrent_depth_ponder_in_bounds_and_differentiable():
    block = TransformerBlock(16, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2, d_hidden=32)
    rec = RecurrentDepth(block, 16, max_steps=3)
    cos, sin = build_rope(5, 4)
    x = torch.randn(2, 5, 16, requires_grad=True)
    out = rec(x, cos, sin)
    out.sum().backward()
    assert x.grad.abs().sum() > 0
    assert 1.0 - 1e-4 <= float(rec.last_ponder) <= 3.0 + 1e-4


def test_multiplane_memory_and_cortex_pool():
    mem = MultiPlaneMemory(16, num_planes=11)
    cortex = CortexPool(16)
    x = torch.randn(2, 6, 16, requires_grad=True)
    pooled = cortex(mem(x))
    assert pooled.shape == (2, 16)
    pooled.sum().backward()
    assert x.grad.abs().sum() > 0


# --- the INTEGRATED model: all canon designs in one trainable network ---

def _build_model(seed=0):
    torch.manual_seed(seed)
    return NexusNetTransformer(
        vocab_size=24, num_classes=3, d_model=48, n_heads=4, n_kv_heads=2,
        num_experts=6, top_k=2, d_hidden=96, max_steps=3, num_planes=11, ebt_steps=2,
    )


def test_integrated_model_contains_every_canon_component():
    m = _build_model()
    assert isinstance(m.recurrent, RecurrentDepth)
    assert isinstance(m.recurrent.block, TransformerBlock)
    assert isinstance(m.recurrent.block.attn, GQAttention)
    assert isinstance(m.recurrent.block.moe, MoECapsuleLayer)
    assert m.recurrent.block.moe.num_experts == 6 and m.recurrent.block.moe.top_k == 2
    assert isinstance(m.ebt, EBTRefinement)
    assert isinstance(m.memory, MultiPlaneMemory)
    assert isinstance(m.cortex, CortexPool)
    assert isinstance(m.ebt_norm, RMSNorm)
    assert m.num_parameters() > 50_000


def test_integrated_model_actually_learns():
    m = _build_model(seed=0)
    X, y = make_sequence_dataset(n=400, seq_len=12, vocab_size=24, num_classes=3, seed=0)
    metrics = train_model(m, X, y, epochs=70, lr=3e-3)
    assert metrics["gradients_flowed"] is True
    assert metrics["final_loss"] < 0.5 * metrics["initial_loss"]
    assert metrics["final_accuracy"] > 0.80
    assert metrics["initial_accuracy"] < metrics["final_accuracy"]


def test_integrated_model_inference_under_no_grad():
    m = _build_model(seed=1)
    X, _ = make_sequence_dataset(n=20, seq_len=12, vocab_size=24, num_classes=3, seed=1)
    m.eval()
    with torch.no_grad():
        logits = m(X)
    assert logits.shape == (20, 3)
    assert torch.isfinite(logits).all()
