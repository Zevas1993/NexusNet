"""Waves 7-10: trainable JEPA dreaming, modern Hopfield, real FedAvg, end-to-end integration."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    JEPAWorldModel, sigreg, train_world_model,
    ModernHopfield, HopfieldAssociativeStore, HopfieldLayer, hopfield_retrieve,
    fedavg, divergence_guard, secure_aggregate, federated_train_round,
    MultimodalNexusNet, birth_expert,
    NexusNetLM, make_sequence_dataset,
)


# --- Wave 7: trainable JEPA world-model + SIGReg ---

def test_jepa_learns_to_predict_latents():
    torch.manual_seed(0)
    jepa = JEPAWorldModel(d_model=24, hidden=48, ema=0.9)
    # structured sequences (latents with temporal correlation) so prediction is learnable
    base = torch.randn(16, 1, 24)
    seq = base + 0.1 * torch.randn(16, 10, 24) + torch.linspace(0, 1, 10).reshape(1, 10, 1)
    res = train_world_model(jepa, seq, steps=60, lr=3e-3)
    assert res["world_model_learned"] is True
    assert res["final_pred_err"] < res["initial_pred_err"]


def test_jepa_target_encoder_is_ema_no_grad():
    jepa = JEPAWorldModel(d_model=16)
    assert all(not p.requires_grad for p in jepa.target_encoder.parameters())
    before = [p.detach().clone() for p in jepa.target_encoder.parameters()]
    opt = torch.optim.Adam((p for p in jepa.parameters() if p.requires_grad), lr=1e-2)
    from nexusnet.hive.net import dream_step
    dream_step(jepa, torch.randn(8, 6, 16), opt)
    after = list(jepa.target_encoder.parameters())
    assert any(not torch.equal(b, a) for b, a in zip(before, after))   # EMA moved it
    assert all(p.grad is None for p in jepa.target_encoder.parameters())  # but via EMA, not backprop


def test_sigreg_detects_anisotropy():
    iso = torch.randn(512, 16)
    aniso = iso.clone(); aniso[:, 0] *= 8.0; aniso[:, 1] = aniso[:, 0]   # scaled + correlated
    assert float(sigreg(aniso)["gauss_dev"]) > float(sigreg(iso)["gauss_dev"])


# --- Wave 8: modern Hopfield associative memory ---

def test_hopfield_recalls_clean_pattern_from_noisy_cue():
    torch.manual_seed(0)
    patterns = torch.randn(5, 32)
    store = HopfieldAssociativeStore(32, beta=8.0, steps=4)
    store.write(patterns)
    target = patterns[2]
    cue = target + 0.3 * torch.randn(32)
    recalled = store.recall(cue.unsqueeze(0))[0]
    # recalled is closer to the true stored pattern than the noisy cue was
    assert (recalled - target).norm() < (cue - target).norm()
    # and pattern 2 is the nearest stored pattern to the recall
    dists = (patterns - recalled).norm(dim=-1)
    assert int(dists.argmin()) == 2


def test_hopfield_beta_sharpens_retrieval():
    patterns = torch.randn(6, 16)
    cue = patterns[0].unsqueeze(0)
    sharp = ModernHopfield(beta=20.0).retrieval_weights(cue, patterns)
    soft = ModernHopfield(beta=0.2).retrieval_weights(cue, patterns)
    assert sharp.max() > soft.max()                          # higher beta -> peakier attention


def test_hopfield_layer_is_differentiable():
    layer = HopfieldLayer(16, beta=1.0, steps=2)
    state = torch.randn(3, 16, requires_grad=True)
    memory = torch.randn(8, 16)
    out = layer(state, memory)
    assert out.shape == (3, 16)
    out.sum().backward()
    assert state.grad.abs().sum() > 0 and layer.q.weight.grad is not None


# --- Wave 9: real federated aggregation ---

def test_fedavg_is_sample_weighted_mean():
    a = {"w": torch.zeros(4)}
    b = {"w": torch.ones(4)}
    avg = fedavg([a, b], [1.0, 3.0])                         # 3:1 weight toward b
    assert torch.allclose(avg["w"], torch.full((4,), 0.75))


def test_divergence_guard_flags_outlier():
    base = {"w": torch.zeros(20)}
    states = [dict(base), dict(base), {"w": torch.zeros(20)}, {"w": torch.full((20,), 50.0)}]
    guard = divergence_guard(states, tolerance=2.0)
    assert 3 in guard["flagged"] and 0 in guard["kept"]


def test_secure_aggregate_hides_individuals_preserves_mean():
    updates = [torch.randn(10) for _ in range(4)]
    res = secure_aggregate(updates, seed=0)
    assert torch.allclose(res["true_mean"], res["masked_mean"], atol=1e-5)   # mean exact
    assert not torch.allclose(res["masked"][0], updates[0])                  # individual hidden


def test_federated_round_improves_global_model():
    torch.manual_seed(0)
    cfg = dict(vocab_size=24, d_model=32, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
               d_hidden=64, num_layers=2)
    make = lambda: NexusNetLM(**cfg)
    global_state = make().state_dict()
    shards = [make_sequence_dataset(n=60, seq_len=10, vocab_size=24, num_classes=24, seed=s)
              for s in range(3)]
    # sequence dataset returns class labels; reuse tokens as next-token targets for a quick LM shard
    client_shards = [(x, x) for x, _ in shards]
    res = federated_train_round(make, global_state, client_shards, local_steps=15, lr=3e-3,
                                use_guard=True)
    assert res["clients"] == 3
    assert res["improved"] is True                           # FedAvg global beats the starting global


# --- Wave 10: end-to-end integration ---

def test_multimodal_nexusnet_fuses_and_classifies():
    torch.manual_seed(0)
    m = MultimodalNexusNet(num_classes=3, d_model=48, num_layers=2, text_vocab=40,
                           audio_mels=16, table_features=6)
    inputs = {
        "text": torch.randint(0, 40, (2, 5)),
        "vision": torch.randn(2, 3, 8, 8),
        "audio": torch.randn(2, 18, 16),
        "table": torch.randn(2, 6),
    }
    out = m(inputs)
    assert out.shape == (2, 3)
    out.sum().backward()
    assert any(p.grad is not None and p.grad.abs().sum() > 0 for p in m.parameters())


def test_birth_expert_runs_domain_pipeline_with_gates():
    res = birth_expert("philosopher", epochs=40, seq_len=20, n_sentences=160, seed=0)
    assert res["capsule"] == "philosopher"
    assert res["metrics"]["final_loss"] < res["metrics"]["initial_loss"]
    assert res["eval_gates"]["gates_total"] >= 1
    assert "birth_ready" in res["milestones"]
    assert res["distilled"] is False and res["governed"] is False


def test_birth_expert_with_distillation_and_governance():
    torch.manual_seed(0)
    from nexusnet.hive.net import VOCAB_SIZE
    # teacher must share the student's (byte) vocabulary so soft targets align
    teacher = NexusNetLM(vocab_size=VOCAB_SIZE, d_model=64, n_heads=4, n_kv_heads=2, num_experts=6,
                         top_k=2, d_hidden=128, num_layers=2)
    res = birth_expert("coder", teacher=teacher, epochs=15, seq_len=20, n_sentences=120, seed=0,
                       govern_allowed=[0, 1, 2, 3])
    assert res["distilled"] is True and res["governed"] is True
    assert "distillation" in res["metrics"]
