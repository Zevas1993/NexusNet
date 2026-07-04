from __future__ import annotations

import math

from nexusnet.hive.kernel import tensor_ops as ops
from nexusnet.hive.kernel.capsule import CapsuleNeuron, squash
from nexusnet.hive.kernel.agreement_routing import route_by_agreement
from nexusnet.hive.kernel.ebt import EnergyField, deliberate


# --- B1: Capsule Neuron ---

def test_squash_length_in_unit_interval_and_direction_preserved():
    s = [3.0, 4.0]                       # ||s|| = 5
    out = squash(s)
    length = ops.norm(out)
    assert 0.0 <= length < 1.0
    # length should equal sq/(1+sq) = 25/26
    assert abs(length - (25.0 / 26.0)) < 1e-9
    # direction preserved: cosine with the input is exactly 1
    assert abs(ops.cosine(out, s) - 1.0) < 1e-9


def test_squash_short_vector_shrinks_more_than_long_vector():
    short = ops.norm(squash([0.1, 0.0]))
    long = ops.norm(squash([10.0, 0.0]))
    assert short < long < 1.0


def test_capsule_forward_emits_probability_pose_and_is_deterministic():
    cap = CapsuleNeuron(domain_index=2, d_in=8, d_hidden=12, d_out=6)
    x = [0.5, -0.2, 0.1, 0.9, -0.4, 0.3, 0.0, 0.7]
    a = cap.forward(x)
    b = cap.forward(x)
    assert a["pose"] == b["pose"]                      # deterministic / replayable
    assert len(a["pose"]) == 6
    assert 0.0 <= a["pose_length"] < 1.0
    assert abs(a["uncertainty"] - (1.0 - a["pose_length"])) < 1e-12
    assert a["production_mutation_allowed"] is False


def test_distinct_domains_occupy_distinct_phases():
    x = [0.3] * 8
    p0 = CapsuleNeuron(domain_index=0, d_in=8, d_hidden=8, d_out=6).forward(x)["pose"]
    p1 = CapsuleNeuron(domain_index=1, d_in=8, d_hidden=8, d_out=6).forward(x)["pose"]
    assert p0 != p1


# --- B2: routing-by-agreement ---

def test_coupling_rows_sum_to_one():
    lowers = [[0.4, 0.1, -0.2, 0.5], [0.2, -0.3, 0.6, 0.1], [-0.5, 0.2, 0.2, 0.3]]
    res = route_by_agreement(lowers, num_higher=2, d_higher=4, iterations=3)
    for row in res["coupling"]:
        assert abs(sum(row) - 1.0) < 1e-9
        assert all(v >= 0.0 for v in row)


def test_higher_poses_are_valid_probability_capsules():
    lowers = [[0.4, 0.1, -0.2, 0.5], [0.2, -0.3, 0.6, 0.1]]
    res = route_by_agreement(lowers, num_higher=3, d_higher=4, iterations=4)
    assert len(res["higher_poses"]) == 3
    assert all(0.0 <= L < 1.0 for L in res["higher_pose_lengths"])


def test_agreement_is_nondecreasing_over_iterations():
    lowers = [[0.6, 0.2, -0.1, 0.4], [0.5, -0.2, 0.3, 0.2], [0.55, 0.1, 0.1, 0.35]]
    res = route_by_agreement(lowers, num_higher=2, d_higher=4, iterations=5)
    hist = res["mean_agreement_per_iter"]
    # routing-by-agreement should not lower mean agreement as it iterates (converges upward)
    assert hist[-1] >= hist[0] - 1e-9


# --- B3: EBT deliberation ---

def test_energy_trajectory_is_monotonically_nonincreasing():
    res = deliberate([0.5, -0.3, 0.8, 0.1, -0.6], max_steps=20, lr=0.5)
    traj = res["energy_trajectory"]
    for earlier, later in zip(traj, traj[1:]):
        assert later <= earlier + 1e-12


def test_more_steps_reach_lower_energy():
    few = deliberate([0.5, -0.3, 0.8, 0.1, -0.6], max_steps=2, lr=0.5, tol=0.0)
    many = deliberate([0.5, -0.3, 0.8, 0.1, -0.6], max_steps=40, lr=0.5, tol=0.0)
    assert many["final_energy"] <= few["final_energy"] + 1e-12


def test_deliberation_converges_to_energy_fixed_point():
    res = deliberate([0.5, -0.3, 0.8, 0.1, -0.6], max_steps=200, lr=0.5, tol=1e-10)
    field = EnergyField([0.5, -0.3, 0.8, 0.1, -0.6])
    star = field.fixed_point()
    for zi, si in zip(res["candidate"], star):
        assert abs(zi - si) < 1e-4
    assert res["converged"] is True


def test_exit_schedule_is_a_valid_distribution():
    res = deliberate([0.4, 0.2, -0.5], max_steps=10, lr=0.5, tol=0.0)
    sched = res["exit_schedule"]
    total = sum(sched["exit_probabilities"]) + sched["final_survival"]
    assert abs(total - 1.0) < 1e-9


# --- B4: capsule router + forward ---

def _fwd():
    from nexusnet.hive.kernel.capsule_forward import CapsuleForward
    k = CapsuleForward(d_model=16, d_pose=8, num_experts=6, top_k=2, deliberation_steps=12)
    return k.forward(token_values=[0.5, -0.3, 0.8, 0.1, -0.6, 0.4, 0.2, -0.1], position=5)


def test_forward_is_sparse_and_finite():
    r = _fwd()
    assert len(r["router_active_experts"]) <= 2          # sparse top-k activation
    assert r["output_finite"] is True
    assert all(__import__("math").isfinite(x) for x in r["output"])


def test_forward_attention_and_coupling_normalized():
    r = _fwd()
    assert abs(sum(r["attention"]) - 1.0) < 1e-9
    for row in r["routing_coupling"]:
        assert abs(sum(row) - 1.0) < 1e-9


def test_forward_is_deterministic_and_gated():
    from nexusnet.hive.kernel.capsule_forward import CapsuleForward
    k = CapsuleForward(d_model=16, d_pose=8, num_experts=6, top_k=2)
    args = dict(token_values=[0.2, 0.4, -0.1, 0.3, 0.5, -0.2, 0.1, 0.0], position=3)
    assert k.forward(**args)["output"] == k.forward(**args)["output"]
    assert _fwd()["production_mutation_allowed"] is False


# --- B5: MemoryNode ---

def _planes(seed=0.0):
    from nexusnet.hive.kernel.memory_node import PLANES
    return {p: [seed + i * 0.1 + j * 0.01 for j in range(4)] for i, p in enumerate(PLANES)}


def test_memory_node_requires_all_planes_and_uniform_dims():
    from nexusnet.hive.kernel.memory_node import MemoryNode, PLANES
    node = MemoryNode(node_id="m1", planes=_planes())
    assert node.d_plane == 4
    assert len(PLANES) == 11


def test_cross_plane_attention_sums_to_one():
    from nexusnet.hive.kernel.memory_node import MemoryNode
    node = MemoryNode(node_id="m1", planes=_planes())
    res = node.cross_plane_attention("imaginal")
    assert abs(sum(res["attention_vector"]) - 1.0) < 1e-9
    assert len(res["mixed"]) == 4


def test_hyperedges_typed_and_validated():
    from nexusnet.hive.kernel.memory_node import MemoryNode
    node = MemoryNode(node_id="m1", planes=_planes())
    node.add_edge(edge_type="predicts", target_node_id="m2")
    assert node.edges == [{"type": "predicts", "target": "m2"}]
    import pytest
    with pytest.raises(ValueError):
        node.add_edge(edge_type="bogus", target_node_id="m3")


def test_hopfield_recall_returns_nearest_pattern():
    from nexusnet.hive.kernel.memory_node import HopfieldStore
    store = HopfieldStore()
    store.store([1.0, 0.0, 0.0])
    store.store([0.0, 1.0, 0.0])
    store.store([0.0, 0.0, 1.0])
    res = store.recall([0.9, 0.1, 0.0], beta=12.0)
    assert res["nearest_index"] == 0
    assert res["retrieved"][0] > res["retrieved"][1]


# --- B6: Cortex dream-director ---

def test_only_top_salience_signals_ignite():
    from nexusnet.hive.kernel.cortex import Cortex
    cx = Cortex(ignition_ratio=0.5)
    res = cx.ignite(saliences=[0.9, 0.1, 0.85, 0.05], poses=[[1.0, 0.0]] * 4)
    assert res["ignited_experts"] == [0, 2]
    assert set(res["suppressed_experts"]) == {1, 3}


def test_dreams_are_per_expert_and_gated():
    from nexusnet.hive.kernel.cortex import Cortex
    cx = Cortex()
    poses = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]
    ign = cx.ignite(saliences=[0.8, 0.2, 0.6], poses=poses)
    dreams = cx.direct_dreams(poses=poses, broadcast=ign["broadcast"], mode="collaborative")
    assert len(dreams["assignments"]) == 3
    assert [a["expert"] for a in dreams["assignments"]] == [0, 1, 2]
    assert dreams["production_mutation_allowed"] is False


# --- B7: fractal scale runner ---

def test_same_kernel_runs_at_every_scale():
    from nexusnet.hive.kernel.brain_scale import FractalScaleRunner, BRAIN_SCALES
    runner = FractalScaleRunner(base_config={"d_model": 16, "d_pose": 8, "num_experts": 6, "top_k": 2})
    out = runner.run_all(token_values=[0.3, 0.1, -0.2, 0.4, 0.5, -0.1, 0.2, 0.0], position=2)
    assert list(out["results"].keys()) == list(BRAIN_SCALES)
    for scale in BRAIN_SCALES:
        assert out["results"][scale]["brain_scale"] == scale
        assert out["results"][scale]["output_finite"] is True


def test_child_scale_override_respected():
    from nexusnet.hive.kernel.brain_scale import FractalScaleRunner
    runner = FractalScaleRunner(
        base_config={"d_model": 16, "d_pose": 8, "num_experts": 6, "top_k": 2},
        scale_overrides={"expert": {"num_experts": 3, "top_k": 1}},
    )
    res = runner.run_scale("expert", token_values=[0.2] * 8, position=1)
    assert res["num_experts"] == 3
    assert len(res["router_active_experts"]) <= 1


# --- B8: geometry signature + assembled CapsuleHiveKernel ---

def test_every_platonic_solid_satisfies_euler():
    from nexusnet.hive.kernel.geometry import PLATONIC_SOLIDS, euler_characteristic
    for solid in PLATONIC_SOLIDS:
        assert euler_characteristic(solid) == 2


def test_every_plane_has_geometry_with_euler_two():
    from nexusnet.hive.kernel.geometry import all_plane_signatures
    from nexusnet.hive.kernel.memory_node import PLANES
    sigs = all_plane_signatures()
    assert set(sigs.keys()) == set(PLANES)
    for sig in sigs.values():
        assert sig["euler_characteristic"] == 2
        assert sig["platonic_solid"] in {
            "tetrahedron", "hexahedron", "octahedron", "dodecahedron", "icosahedron"
        }


def test_assembled_hive_kernel_forward():
    from nexusnet.hive.kernel import CapsuleHiveKernel
    k = CapsuleHiveKernel(d_model=16, d_pose=8, num_experts=6, top_k=2)
    out = k.forward(
        token_values=[0.5, -0.3, 0.8, 0.1, -0.6, 0.4, 0.2, -0.1],
        position=7,
        dream_mode="competitive",
    )
    assert out["computed"] is True
    assert out["euler_invariant_holds"] is True
    assert out["forward"]["output_finite"] is True
    assert len(out["cortex_dreams"]["assignments"]) == 6
    assert out["production_mutation_allowed"] is False
    assert out["native_weight_training"] is False


def test_assembled_kernel_is_deterministic():
    from nexusnet.hive.kernel import CapsuleHiveKernel
    k = CapsuleHiveKernel(num_experts=5, top_k=2)
    args = dict(token_values=[0.2, 0.4, -0.1, 0.3, 0.5, -0.2], position=4)
    assert k.forward(**args)["forward"]["output"] == k.forward(**args)["forward"]["output"]


def test_public_kernel_exports_resolve():
    import nexusnet.hive.kernel as K
    for name in [
        "CapsuleNeuron", "route_by_agreement", "deliberate", "CapsuleForward",
        "MemoryNode", "HopfieldStore", "Cortex", "FractalScaleRunner",
        "CapsuleHiveKernel", "plane_geometry_signature",
    ]:
        assert hasattr(K, name), name
