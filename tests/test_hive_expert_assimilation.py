"""Canon Aspect 2: real expert assimilation + MoE fusion on the trainable substrate."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    MoECapsuleLayer, assimilate_expert, make_swiglu_expert, fuse_moe_layers,
)


def test_assimilate_expert_grows_router_and_preserves_existing():
    torch.manual_seed(0)
    layer = MoECapsuleLayer(16, 32, num_experts=4, top_k=2)
    old_gate_w = layer.gate.weight.detach().clone()
    donor = make_swiglu_expert(16, 32)
    info = assimilate_expert(layer, donor)
    assert info["num_experts"] == 5 and info["grew_from"] == 4
    assert info["existing_experts_preserved"] is True
    # router grew by one row, old rows preserved, new row neutral (zero)
    assert layer.gate.out_features == 5
    assert torch.allclose(layer.gate.weight[:4], old_gate_w)
    assert torch.allclose(layer.gate.weight[4], torch.zeros(16))
    assert layer.load_bias.numel() == 5 and layer.last_load.numel() == 5


def test_assimilated_layer_forward_and_donor_trains():
    torch.manual_seed(0)
    layer = MoECapsuleLayer(16, 32, num_experts=3, top_k=2)
    donor = make_swiglu_expert(16, 32)
    assimilate_expert(layer, donor)
    x = torch.randn(8, 16)
    out = layer(x)
    assert out.shape == (8, 16)
    out.sum().backward()
    # donor expert is part of the graph and trainable
    assert any(p.grad is not None and p.grad.abs().sum() >= 0 for p in donor.parameters())
    assert all(p.requires_grad for p in donor.parameters())


def test_neutral_gate_means_new_expert_does_not_hijack_routing():
    torch.manual_seed(0)
    layer = MoECapsuleLayer(16, 32, num_experts=4, top_k=2)
    x = torch.randn(20, 16)
    layer.eval()
    with torch.no_grad():
        before = layer(x)
    assimilate_expert(layer, make_swiglu_expert(16, 32), gate_init=0.0)
    with torch.no_grad():
        after = layer(x)
    # with a neutral (zero) gate row, routing is minimally disturbed for most tokens
    assert after.shape == before.shape
    assert (after - before).abs().mean() < before.abs().mean()   # not a wholesale takeover


def test_fuse_moe_layers_unions_experts_under_one_router():
    torch.manual_seed(0)
    a = MoECapsuleLayer(16, 32, num_experts=3, top_k=2)
    b = MoECapsuleLayer(16, 32, num_experts=2, top_k=1)
    fused = fuse_moe_layers(a, b, top_k=2)
    assert fused.num_experts == 5 and fused.top_k == 2
    assert len(fused.experts) == 5
    # both donors' expert objects are transplanted (same modules, weights intact)
    assert fused.experts[0] is a.experts[0] and fused.experts[3] is b.experts[0]
    assert torch.allclose(fused.gate.weight[:3], a.gate.weight)
    assert torch.allclose(fused.gate.weight[3:], b.gate.weight)
    out = fused(torch.randn(6, 16))
    assert out.shape == (6, 16)
    out.sum().backward()


def test_fuse_requires_matching_d_model():
    a = MoECapsuleLayer(16, 32, num_experts=2, top_k=1)
    b = MoECapsuleLayer(24, 32, num_experts=2, top_k=1)
    with pytest.raises(ValueError):
        fuse_moe_layers(a, b)
