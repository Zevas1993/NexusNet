"""Wave-2: Governed Sparse Routing (fabric governs the learned MoE router) + Mini-NexusNet experts."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from nexusnet.hive.net import (
    MoECapsuleLayer,
    MiniNexusNetExpert,
    SwiGLUExpert,
    GovernedSparseRouter,
    fabric_expert_governance,
    NexusNetTransformer,
    make_sequence_dataset,
    train_model,
)


# --- Mini-NexusNet experts (each expert is a real internal network) ---

def test_mini_expert_is_a_real_internal_network():
    exp = MiniNexusNetExpert(d_model=16, d_hidden=32, depth=3)
    assert len(exp.ffns) == 3 and len(exp.norms) == 3      # genuine internal depth
    x = torch.randn(4, 16, requires_grad=True)
    out = exp(x)
    assert out.shape == (4, 16)
    pose = exp.pose(x)
    assert pose.shape == (4, 16)
    assert (pose.norm(dim=-1) < 1.0 + 1e-4).all()          # squashed capsule presence in [0,1)
    out.sum().backward()
    assert x.grad.abs().sum() > 0


def test_moe_uses_mini_experts_when_requested():
    moe = MoECapsuleLayer(16, 32, num_experts=4, top_k=2, expert_kind="mini")
    assert all(isinstance(e, MiniNexusNetExpert) for e in moe.experts)
    default = MoECapsuleLayer(16, 32, num_experts=4, top_k=2)
    assert all(isinstance(e, SwiGLUExpert) for e in default.experts)


# --- Governed Sparse Routing ---

def test_governance_bias_hard_forbids_and_prioritizes():
    router = GovernedSparseRouter(num_experts=6, hard=True)
    bias = router.governance_bias([0, 1, 2, 3], priorities=[9, 1, 1, 1, 1, 1], top_k=2)
    assert bias[4] == float("-inf") and bias[5] == float("-inf")   # not eligible -> forbidden
    assert torch.isfinite(bias[0])                                  # eligible -> finite
    assert bias[0] > bias[1]                                        # higher priority ranks higher


def test_governance_degrades_to_advisory_when_too_few_eligible():
    router = GovernedSparseRouter(num_experts=6, hard=True, soft_penalty=10.0)
    bias = router.governance_bias([0], top_k=2)        # only 1 eligible but top_k=2 -> cannot hard-gate
    assert torch.isfinite(bias).all()                  # no -inf (would make top-k impossible)
    assert bias[0] == 0.0 and bias[1] == -10.0         # advisory penalty instead


def test_governed_router_routes_only_to_allowed_experts():
    torch.manual_seed(0)
    moe = MoECapsuleLayer(16, 32, num_experts=6, top_k=2)
    router = GovernedSparseRouter(num_experts=6, hard=True)
    moe.set_governance(router.governance_bias([0, 1, 2], top_k=2))
    x = torch.randn(20, 16)
    moe(x)
    # forbidden experts (3,4,5) must carry zero load; allowed must carry all of it
    assert moe.last_load[3:].sum() == 0
    assert moe.last_load[:3].sum() > 0


def test_govern_and_release_across_whole_model():
    torch.manual_seed(0)
    m = NexusNetTransformer(vocab_size=20, num_classes=3, d_model=32, n_heads=4, n_kv_heads=2,
                            num_experts=6, top_k=2, d_hidden=64, max_steps=2, ebt_steps=1)
    router = GovernedSparseRouter(num_experts=6)
    router.govern(m, allowed=[0, 1, 2, 3])
    moe_layers = [mod for mod in m.modules() if isinstance(mod, MoECapsuleLayer)]
    assert moe_layers and all(layer.governance is not None for layer in moe_layers)
    router.release(m)
    assert all(layer.governance is None for layer in moe_layers)


def test_fabric_process_translates_to_governance():
    process = {
        "active_node_set": ["expert.coder", "expert.vision"],
        "node_positions": {"expert.coder": [0.0, 0.0], "expert.vision": [1.0, 0.0],
                            "expert.physicist": [2.0, 0.0]},
    }
    expert_ids = ["expert.coder", "expert.vision", "expert.physicist"]
    allowed, priorities = fabric_expert_governance(process, expert_ids)
    assert allowed == [0, 1]                            # only active nodes are eligible
    assert priorities[0] > priorities[1] > priorities[2]   # centrality: closer to bindu = higher


def test_governed_model_still_trains():
    torch.manual_seed(0)
    m = NexusNetTransformer(vocab_size=24, num_classes=3, d_model=48, n_heads=4, n_kv_heads=2,
                            num_experts=6, top_k=2, d_hidden=96, max_steps=2, ebt_steps=1,
                            expert_kind="mini")
    GovernedSparseRouter(num_experts=6).govern(m, allowed=[0, 1, 2, 3, 4])  # govern + mini experts
    X, y = make_sequence_dataset(n=300, seq_len=12, vocab_size=24, num_classes=3, seed=0)
    metrics = train_model(m, X, y, epochs=50, lr=3e-3)
    assert metrics["gradients_flowed"] is True
    assert metrics["final_loss"] < metrics["initial_loss"]
