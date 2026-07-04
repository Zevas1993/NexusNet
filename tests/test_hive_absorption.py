"""Wrapper absorption: the born model internalizes the wrapper's architecture + features (canon)."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    NexusNetTransformer, NexusNetLM, native_features, absorb_wrapper, BornNexus,
    NATIVE_WRAPPER_FEATURES, CAPABILITY_WRAPPER_FEATURES,
)


def test_full_feature_lm_absorbs_all_native_wrapper_features():
    lm = NexusNetLM(vocab_size=64, d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
                    d_hidden=96, num_layers=2, full_features=True)
    absorb = absorb_wrapper(lm)
    assert absorb["wrapper_fully_absorbed"] is True
    assert absorb["native_parity"] == 1.0
    assert absorb["native_features_missing"] == []
    assert absorb["supersedes_wrapper"] is True
    # every declared native feature is genuinely present in the model's modules
    nat = native_features(lm)
    assert all(nat[f] for f in NATIVE_WRAPPER_FEATURES)


def test_lean_lm_has_partial_parity_reported_honestly():
    # the lean LM (no full_features) genuinely LACKS some wrapper features - absorption reports it
    lm = NexusNetLM(vocab_size=64, d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
                    d_hidden=96, num_layers=2, full_features=False)
    absorb = absorb_wrapper(lm)
    assert absorb["wrapper_fully_absorbed"] is False
    assert absorb["native_parity"] < 1.0
    assert "multi_plane_memory" in absorb["native_features_missing"]
    assert "cortex_pool" in absorb["native_features_missing"]


def test_transformer_stack_has_full_parity():
    t = NexusNetTransformer(vocab_size=32, num_classes=4, d_model=48, n_heads=4, n_kv_heads=2,
                            num_experts=6, top_k=2, d_hidden=96)
    assert absorb_wrapper(t)["wrapper_fully_absorbed"] is True


def test_full_feature_lm_still_trains_and_generates():
    torch.manual_seed(0)
    lm = NexusNetLM(vocab_size=40, d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
                    d_hidden=96, num_layers=2, full_features=True)
    x = torch.randint(0, 40, (4, 12))
    y = torch.randint(0, 40, (4, 12))
    opt = torch.optim.Adam(lm.parameters(), lr=3e-3)
    import torch.nn.functional as F
    first = None
    for _ in range(20):
        opt.zero_grad(); logits = lm(x)
        loss = F.cross_entropy(logits.reshape(-1, 40), y.reshape(-1)); loss.backward(); opt.step()
        if first is None: first = loss.item()
    assert loss.item() < first                        # full-feature model learns
    assert lm.last_summary is not None                # cortex global-workspace readout produced
    out = lm.generate([1, 2, 3], max_new_tokens=5, greedy=True)
    assert len(out) == 8


def test_born_nexus_is_wrapper_successor_only_at_full_parity():
    full = BornNexus(NexusNetLM(vocab_size=40, d_model=48, n_heads=4, n_kv_heads=2, num_experts=4,
                                top_k=2, d_hidden=96, num_layers=2, full_features=True),
                     capabilities={c: 1 for c in CAPABILITY_WRAPPER_FEATURES})
    assert full.attest()["is_wrapper_successor"] is True
    assert full.attest()["ready_to_supersede"] is True
    manifest = full.feature_manifest()
    assert manifest["native_parity"] == 1.0 and not manifest["native_missing"]

    lean = BornNexus(NexusNetLM(vocab_size=40, d_model=48, n_heads=4, n_kv_heads=2, num_experts=4,
                                top_k=2, d_hidden=96, num_layers=2, full_features=False))
    assert lean.attest()["is_wrapper_successor"] is False   # honest: not a successor until full parity
