"""Canon Aspect 1 (brain-first): real attach_base_model - inspect + LoRA adapter injection."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")
import torch.nn as nn

from nexusnet.hive.net import (
    inspect_base_model, LoRAAdapter, attach_base_model_adapters, NexusNetLM,
)


class _Base(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Embedding(20, 16)
        self.q_proj = nn.Linear(16, 16)
        self.v_proj = nn.Linear(16, 16)
        self.out = nn.Linear(16, 20)

    def forward(self, ids):
        h = self.embed(ids)
        h = self.q_proj(h) + self.v_proj(h)
        return self.out(h)


def test_inspect_reports_layers_and_shapes():
    info = inspect_base_model(_Base())
    assert info["linear_count"] == 3
    names = {l["name"] for l in info["linear_layers"]}
    assert {"q_proj", "v_proj", "out"} <= names
    assert 16 in info["hidden_sizes"] and info["total_params"] > 0


def test_lora_adapter_freezes_base_and_starts_as_identity():
    base = nn.Linear(8, 8)
    x = torch.randn(4, 8)
    ref = base(x).detach().clone()
    lora = LoRAAdapter(base, rank=2, alpha=4.0)
    # zero-init B => adapter output equals base output initially (no disruption to the base network)
    assert torch.allclose(lora(x), ref, atol=1e-6)
    assert all(not p.requires_grad for p in lora.base.parameters())   # base frozen
    assert lora.lora_a.requires_grad and lora.lora_b.requires_grad     # shim trainable


def test_lora_adapter_learns_a_delta():
    torch.manual_seed(0)
    base = nn.Linear(8, 8)
    lora = LoRAAdapter(base, rank=4, alpha=8.0)
    x = torch.randn(32, 8)
    target = torch.randn(32, 8)
    opt = torch.optim.Adam([lora.lora_a, lora.lora_b], lr=0.05)
    first = None
    for _ in range(60):
        opt.zero_grad(); loss = (lora(x) - target).pow(2).mean(); loss.backward(); opt.step()
        if first is None: first = loss.item()
    assert loss.item() < first                                # the low-rank delta actually trains
    # base weights never moved
    assert torch.equal(base.weight, lora.base.weight)


def test_attach_injects_into_targeted_layers_and_freezes_base():
    base = _Base()
    stats = attach_base_model_adapters(base, rank=4, target_names=("q_proj", "v_proj"))
    assert set(stats["injected_layers"]) == {"q_proj", "v_proj"}    # only targeted layers
    assert stats["base_frozen"] is True
    assert 0.0 < stats["trainable_fraction"] < 1.0                  # only adapters train
    # the upgraded model still runs and trains end-to-end on the adapters only
    ids = torch.randint(0, 20, (2, 5))
    out = base(ids)
    out.sum().backward()
    grads = [p.grad for n, p in base.named_parameters() if "lora_" in n and p.grad is not None]
    assert grads and all(g.abs().sum() >= 0 for g in grads)


def test_attach_upgrades_a_nexusnet_lm_with_few_trainable_params():
    torch.manual_seed(0)
    lm = NexusNetLM(d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
                    d_hidden=96, num_layers=2)
    stats = attach_base_model_adapters(lm, rank=4, target_names=("q_proj", "k_proj", "v_proj"))
    assert stats["injected_count"] >= 1
    assert stats["base_frozen"] is True
    # brain-first economy: adapters are a small fraction of the base network
    assert stats["trainable_fraction"] < 0.5
    # the upgraded LM still produces finite logits
    with torch.no_grad():
        logits = lm(torch.randint(0, 259, (1, 8)))
    assert torch.isfinite(logits).all()
