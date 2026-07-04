from __future__ import annotations

from nexusnet.hive.fabric import (
    NeuralBus,
    NeuralBusMessage,
    HiveBlackboard,
    HiveNode,
    HiveMindFabric,
    NODE_TYPES,
    EDGE_TYPES,
)

INP = [0.6, -0.3, 0.8, 0.1, -0.4, 0.5, 0.2, -0.1]


# --- Neural Bus: bandwidth-efficient pose/summary passing ---

def test_neural_bus_passes_summaries_not_full_state():
    bus = NeuralBus()
    bus.register("a")
    bus.register("b")
    bus.publish(NeuralBusMessage(source_id="a", target_id="b", summary_embedding=[0.1] * 8, uncertainty=0.2))
    msgs = bus.deliver("b")
    assert len(msgs) == 1 and msgs[0].source_id == "a"
    assert bus.deliver("b") == []                       # queue drained
    eff = bus.efficiency(full_state_dim=64)
    assert 0.0 < eff["bandwidth_saving_ratio"] < 1.0    # summaries far cheaper than full state


def test_neural_bus_broadcast_skips_source():
    bus = NeuralBus()
    for n in ("a", "b", "c"):
        bus.register(n)
    bus.publish(NeuralBusMessage(source_id="a", target_id=None, summary_embedding=[1.0, 0.0]))
    assert len(bus.deliver("b")) == 1 and len(bus.deliver("c")) == 1
    assert bus.deliver("a") == []                       # never delivered back to the source


# --- HiveBlackboard: stigmergic coordination with mandatory decay ---

def test_blackboard_trails_accumulate_then_decay():
    bb = HiveBlackboard(evaporation_rate=0.5)
    bb.post(topic="route.x", node_id="n1", salience=1.0)
    s0 = bb.strength("route.x")
    assert s0 > 0
    for _ in range(20):
        bb.tick()
    assert bb.strength("route.x") < 1e-4                # stale coordination fades (auditable)


def test_blackboard_read_top_orders_by_strength():
    bb = HiveBlackboard(evaporation_rate=0.1)
    bb.post(topic="hi", node_id="n", salience=3.0)
    bb.post(topic="lo", node_id="n", salience=1.0)
    top = bb.read_top(2)
    assert top[0]["topic"] == "hi" and top[0]["strength"] > top[1]["strength"]


# --- HiveNode: typed edges ---

def test_hive_node_typed_edges():
    node = HiveNode(node_id="x", node_type="expert", d_pose=8)
    node.connect("y", edge_type="aligned_with")
    assert node.edges["y"] == "aligned_with"
    import pytest
    with pytest.raises(ValueError):
        node.connect("z", edge_type="bogus")


# --- the FABRIC as one organism ---

def _fabric():
    return HiveMindFabric(num_orchestrators=2, aos_per_orchestrator=2, experts_per_ao=3, d_pose=8)


def test_fabric_is_a_fully_connected_fractal_hierarchy():
    f = _fabric()
    c = f.connectivity()
    assert c["by_type"] == {"core": 1, "orchestrator": 2, "assistant_orchestrator": 4, "expert": 12}
    assert c["total_nodes"] == 19
    assert c["fully_connected"] is True                 # every node reachable from the core


def test_fabric_propagates_core_to_experts():
    r = _fabric().process(input_vector=INP)
    assert r["reached_experts"] is True
    assert set(r["propagation_reached_types"]) == {"core", "orchestrator", "assistant_orchestrator", "expert"}


def test_fabric_activation_is_sparse():
    r = _fabric().process(input_vector=INP)
    assert r["sparse_activation"] is True
    assert r["active_count"] < r["connectivity"]["total_nodes"]
    active_experts = [n for n in r["active_nodes"] if n.startswith("expert")]
    assert 0 < len(active_experts) < 12                 # a routed subset of experts, not all


def test_fabric_neural_bus_is_bandwidth_efficient():
    r = _fabric().process(input_vector=INP)
    assert r["neural_bus"]["messages"] > 0
    assert r["neural_bus"]["bandwidth_saving_ratio"] > 0.5   # summaries, not full hidden state


def test_fabric_is_deterministic_and_gated():
    f = _fabric()
    a = f.process(input_vector=INP)
    b = f.process(input_vector=INP)
    assert a["active_nodes"] == b["active_nodes"]
    assert a["neural_bus"]["messages"] == b["neural_bus"]["messages"]
    assert a["production_mutation_allowed"] is False
    assert a["native_weight_training"] is False
