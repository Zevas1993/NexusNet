from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    NexusNetModel,
    MoECapsuleLayer,
    squash,
    make_nonlinear_dataset,
    train_model,
)


def test_model_has_real_learnable_parameters():
    model = NexusNetModel(in_dim=8, num_classes=3)
    n = model.num_parameters()
    assert n > 1000
    assert all(p.requires_grad for p in model.parameters())


def test_squash_length_in_unit_interval_and_direction_preserved():
    x = torch.tensor([[3.0, 4.0]])
    out = squash(x)
    length = out.norm(dim=-1).item()
    assert 0.0 <= length < 1.0
    assert abs(length - 25.0 / 26.0) < 1e-5
    cos = torch.cosine_similarity(out, x, dim=-1).item()
    assert abs(cos - 1.0) < 1e-5


def test_moe_router_is_sparse_and_differentiable():
    layer = MoECapsuleLayer(d_model=16, d_hidden=32, num_experts=6, top_k=2)
    x = torch.randn(10, 16, requires_grad=True)
    out = layer(x)
    out.sum().backward()
    assert x.grad is not None and x.grad.abs().sum() > 0      # gradients flow through routing
    # each token's used-expert load can't exceed top_k tokens-per-expert bound
    assert int(layer.last_load.sum().item()) <= 10 * layer.top_k


def test_network_actually_learns_loss_decreases():
    torch.manual_seed(0)
    X, y = make_nonlinear_dataset(n=600, in_dim=8, num_classes=3, seed=0)
    model = NexusNetModel(in_dim=8, d_model=32, d_hidden=64, num_experts=6, top_k=2, num_classes=3)
    metrics = train_model(model, X, y, epochs=250, lr=5e-3)
    assert metrics["gradients_flowed"] is True
    # real learning: loss drops a lot and accuracy rises well above chance (1/3)
    assert metrics["final_loss"] < 0.5 * metrics["initial_loss"]
    assert metrics["final_accuracy"] > 0.85
    assert metrics["initial_accuracy"] < metrics["final_accuracy"]


def test_network_generalizes_to_held_out_data():
    torch.manual_seed(1)
    X, y = make_nonlinear_dataset(n=900, in_dim=8, num_classes=3, seed=1)
    X_tr, y_tr = X[:700], y[:700]
    X_te, y_te = X[700:], y[700:]
    model = NexusNetModel(in_dim=8, d_model=32, d_hidden=64, num_experts=6, top_k=2, num_classes=3)
    train_model(model, X_tr, y_tr, epochs=250, lr=5e-3)
    model.eval()
    with torch.no_grad():
        test_acc = (model(X_te).argmax(dim=-1) == y_te).float().mean().item()
    assert test_acc > 0.55                                    # well above 1/3 chance => generalizes


def test_weights_actually_change_after_training():
    torch.manual_seed(2)
    X, y = make_nonlinear_dataset(n=300, in_dim=8, num_classes=3, seed=2)
    model = NexusNetModel(in_dim=8, num_classes=3)
    before = model.head.weight.detach().clone()
    train_model(model, X, y, epochs=30, lr=5e-3)
    after = model.head.weight.detach()
    assert (after - before).abs().sum() > 0                   # weights were updated by training
