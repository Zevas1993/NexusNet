"""Closed loops: recursive dreaming -> gated training (PB-034) + governed FedAvg (PB-024..040)."""
from __future__ import annotations

import copy

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    NexusNetLM, domain_corpus_for_capsule, make_corpus_windows, split_windows,
    train_language_model, measure_language_model,
    recursive_dream_train, recursive_dream_cycles,
    sanitized_update_packet, verify_packet, governed_federated_round,
)


def _lm_and_data(seed=0):
    torch.manual_seed(seed)
    corpus = domain_corpus_for_capsule("physicist", n_sentences=200, seed=seed, rich=True)
    x, y = make_corpus_windows(corpus, seq_len=20)
    x_tr, y_tr, x_val, y_val = split_windows(x, y, val_fraction=0.25, seed=seed)
    lm = NexusNetLM(d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
                    d_hidden=96, num_layers=2)
    return lm, x_tr, y_tr, x_val, y_val


# --- Loop 1: recursive dreaming -> gated training feedback ---

def test_recursive_dream_train_is_failure_conditioned_and_gated():
    lm, x_tr, y_tr, x_val, y_val = _lm_and_data(0)
    train_language_model(lm, x_tr, y_tr, epochs=15)            # a partially-trained model with failures
    before = measure_language_model(lm, x_val, y_val)["val_loss"]
    rec = recursive_dream_train(lm, x_tr, y_tr, x_val, y_val, dream_steps=20, shadow_epochs=15, seed=1)
    assert rec["failure_count"] >= 1                          # conditioned on real failures
    assert "dream" in rec and rec["production_mutation_allowed"] is False
    after = measure_language_model(lm, x_val, y_val)["val_loss"]
    if rec["applied"]:
        assert after <= before + 1e-6                        # applied only because it improved
    else:
        assert after == pytest.approx(before, abs=1e-6)      # rolled back -> weights unchanged


def test_recursive_dream_respects_veto():
    lm, x_tr, y_tr, x_val, y_val = _lm_and_data(2)
    # impossible veto thresholds -> the critic must veto, no weight change
    # snapshot learnable PARAMETERS (buffers like last_load change on any forward pass and are not weights)
    snapshot = {k: v.detach().clone() for k, v in lm.named_parameters()}
    rec = recursive_dream_train(lm, x_tr, y_tr, x_val, y_val, dream_steps=10,
                                veto_pred_err=-1.0, veto_gauss_dev=-1.0, seed=3)
    assert rec["vetoed"] is True and rec["applied"] is False
    for k, v in lm.named_parameters():
        assert torch.equal(v, snapshot[k])                   # vetoed dream never trained the weights


def test_recursive_dream_cycles_report_outcomes():
    lm, x_tr, y_tr, x_val, y_val = _lm_and_data(0)
    train_language_model(lm, x_tr, y_tr, epochs=10)
    out = recursive_dream_cycles(lm, x_tr, y_tr, x_val, y_val, cycles=3, dream_steps=12,
                                 shadow_epochs=10, seed=0)
    assert out["cycles"] == 3
    assert out["applied"] + out["vetoed"] + out["rolled_back"] == 3
    assert "final_val_loss" in out


# --- Loop 2: governed federated round (sanitized, signed, scanned, regression-gated) ---

def _cfg():
    return dict(vocab_size=259, d_model=48, n_heads=4, n_kv_heads=2, num_experts=4, top_k=2,
                d_hidden=96, num_layers=2)


def test_sanitized_packet_blocks_private_metadata():
    torch.manual_seed(0)
    base = NexusNetLM(**_cfg()); client = NexusNetLM(**_cfg())
    pkt = sanitized_update_packet("c1", client.state_dict(), base.state_dict(), eval_score=0.6,
                                  sample_count=100, metadata={"prompt": "secret stuff", "eval": 0.6})
    assert pkt["sanitized"] is False and "prompt" in pkt["privacy_violations"]
    assert verify_packet(pkt) is False                       # privacy failure fails verification


def test_signed_envelope_detects_tampering():
    torch.manual_seed(0)
    base = NexusNetLM(**_cfg()); client = NexusNetLM(**_cfg())
    pkt = sanitized_update_packet("c1", client.state_dict(), base.state_dict(), eval_score=0.6,
                                  sample_count=100, metadata={"route_geometry": "flower"})
    assert verify_packet(pkt) is True
    k = next(iter(pkt["delta"]))
    pkt["delta"][k] = pkt["delta"][k] + 1.0                   # tamper with the delta
    assert verify_packet(pkt) is False                       # integrity digest catches it


def test_governed_round_promotes_only_without_regression():
    torch.manual_seed(0)
    make = lambda: NexusNetLM(**_cfg())
    corpus = domain_corpus_for_capsule("coder", n_sentences=160, seed=0, rich=True)
    x, y = make_corpus_windows(corpus, seq_len=18)
    x_tr, y_tr, x_val, y_val = split_windows(x, y, val_fraction=0.3, seed=0)

    base = make(); global_state = {k: v.clone() for k, v in base.state_dict().items()}
    packets = []
    for i in range(3):
        client = make(); client.load_state_dict(global_state)
        train_language_model(client, x_tr, y_tr, epochs=20, lr=3e-3)   # real local improvement
        packets.append(sanitized_update_packet(
            f"c{i}", client.state_dict(), global_state, eval_score=0.5, sample_count=x_tr.shape[0],
            metadata={"route_geometry": "flower", "node_role": "expert"}))

    res = governed_federated_round(make, global_state, packets, x_val, y_val)
    assert res["decision"] in ("promoted", "shadow")
    assert set(res["kept_clients"]) and res["secure_aggregation_exact"] is True
    assert res["production_mutation_allowed"] is False
    # the gate is real: promotion implies no held-out regression
    if res["promoted"]:
        assert res["candidate_loss"] <= res["base_loss"] + 1e-3
    else:
        assert res["global_state"] is global_state           # shadow -> global unchanged


def test_governed_round_drops_unverified_packets():
    torch.manual_seed(0)
    make = lambda: NexusNetLM(**_cfg())
    base = make(); global_state = base.state_dict()
    client = make()
    good = sanitized_update_packet("ok", client.state_dict(), global_state, eval_score=0.5,
                                   sample_count=50, metadata={"route_geometry": "flower"})
    bad = sanitized_update_packet("leak", client.state_dict(), global_state, eval_score=0.5,
                                  sample_count=50, metadata={"raw_output": "leak"})
    x = torch.randint(0, 259, (4, 12));
    res = governed_federated_round(make, global_state, [good, bad], x, x)
    assert "leak" in res["rejected_clients"] and "ok" in res["verified_clients"]
