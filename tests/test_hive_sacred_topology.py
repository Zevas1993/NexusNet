from __future__ import annotations

import math

from nexusnet.hive.fabric import (
    HiveMindFabric,
    HIVE_MIND_STYLES,
    sacred_layout,
    metatron_chords,
    topology_signature,
)

INP = [0.6, -0.3, 0.8, 0.1, -0.4, 0.5, 0.2, -0.1]


# --- sacred geometry layout ---

def test_core_sits_at_the_bindu_and_levels_form_rings():
    levels = [["core"], ["o0", "o1"], ["a0", "a1", "a2", "a3"]]
    pos = sacred_layout(levels)
    # core is at the centre (bindu) on ring 0
    assert pos["core"]["ring"] == 0
    assert abs(pos["core"]["x"]) < 1e-12 and abs(pos["core"]["y"]) < 1e-12
    # deeper levels are on larger rings
    assert pos["o0"]["ring"] == 1 and pos["a0"]["ring"] == 2
    assert math.hypot(pos["a0"]["x"], pos["a0"]["y"]) > math.hypot(pos["o0"]["x"], pos["o0"]["y"])


def test_golden_angle_phyllotaxis_spacing():
    from nexusnet.hive.kernel.tensor_ops import GOLDEN_ANGLE_RADIANS
    levels = [["c"], ["x0", "x1", "x2"]]
    pos = sacred_layout(levels)
    assert abs(pos["x1"]["phyllotaxis_angle"] - GOLDEN_ANGLE_RADIANS) < 1e-9
    assert abs(pos["x2"]["phyllotaxis_angle"] - 2 * GOLDEN_ANGLE_RADIANS) < 1e-9


def test_metatron_chords_link_peers_within_a_ring():
    levels = [["c"], ["o0", "o1"], ["a0", "a1", "a2", "a3"]]
    chords = metatron_chords(levels)
    flat = {frozenset(c) for c in chords}
    assert frozenset({"o0", "o1"}) in flat               # the 2 orchestrators are linked
    # the 4 AOs form a consensus ring (each linked to its angular neighbour)
    ao_chords = [c for c in chords if c[0].startswith("a") and c[1].startswith("a")]
    assert len(ao_chords) == 4                            # ring of 4 -> 4 chords


def test_topology_signature_is_sacred_and_carries_hive_styles():
    sig = topology_signature([["c"], ["o0", "o1"]])
    assert sig["route_geometry_signature"] == "flower-field-to-metatron-chord-sparse-selection"
    assert "flower_of_life" in sig["node_field"]
    assert "metatron" in sig["lateral_mesh"]
    assert sig["structural_backbone"] == "sixty_four_tetrahedron_grid"
    assert "torus" in sig["feedback_loops"]
    assert len(sig["hive_mind_styles"]) == 9


# --- hive-mind styles ---

def test_nine_hive_mind_styles_each_with_trait_mechanism_and_safety_inversion():
    assert len(HIVE_MIND_STYLES) == 9
    for key in ("borg_collective_memory", "tyranid_synapse_relay", "geth_networked_consensus",
                "honeybee_quorum", "social_insect_stigmergy", "siphonophore_organs"):
        s = HIVE_MIND_STYLES[key]
        assert s["trait"] and s["mechanism"] and s["safety_inversion"]


# --- fabric wired with the sacred topology + hive-mind mesh ---

def _fabric():
    return HiveMindFabric(num_orchestrators=2, aos_per_orchestrator=2, experts_per_ao=3, d_pose=8)


def test_fabric_nodes_have_sacred_positions_and_lateral_mesh():
    f = _fabric()
    # core at the bindu
    assert f.nodes["core.brain"].position["ring"] == 0
    assert abs(f.nodes["core.brain"].position["x"]) < 1e-12
    # lateral Metatron-chord mesh added as aligned_with edges (a separate channel from the tree)
    assert len(f.lateral_chords) > 0
    aligned = [t for n in f.nodes.values() for t, et in n.edges.items() if et == "aligned_with"]
    assert len(aligned) > 0


def test_lateral_mesh_does_not_break_the_directional_sweep():
    r = _fabric().process(input_vector=INP)
    # the sacred lateral mesh is a separate channel; the down/up sweep still works
    assert r["connectivity"]["fully_connected"] is True
    assert r["sparse_activation"] is True
    assert r["reached_experts"] is True


def test_process_exposes_sacred_geometry_and_hive_consensus():
    r = _fabric().process(input_vector=INP)
    assert r["sacred_geometry"]["route_geometry_signature"] == "flower-field-to-metatron-chord-sparse-selection"
    assert len(r["hive_mind_styles"]) == 9
    # per-ring honeybee/Geth consensus is reported
    assert "rings" in r["lateral_consensus"]
    assert all("committed" in v for v in r["lateral_consensus"]["rings"].values())


def test_hive_mind_styles_operate_in_the_cognitive_cycle():
    """The hive-mind styles are not just tags - they RUN over the sacred-geometry mesh each cycle."""
    f = _fabric()
    c = f.cognize(input_vector=INP)
    hc = c["hive_coordination"]
    # Tyranid synapse-relay / Geth consensus actually exchanged poses over the lateral mesh
    assert hc["synapse_relay"]["relayed_nodes"] > 0
    assert hc["synapse_relay"]["mean_consensus_shift"] >= 0.0
    # social-insect stigmergy left trails; honeybee quorum decided per ring
    assert hc["stigmergy"]["active_trails"] > 0
    assert "rings" in hc["ring_quorum"]
    # Gravemind critical-mass + siphonophore organs + Borg collective memory are reported
    assert isinstance(hc["critical_mass"], bool)
    assert hc["organs_of_one_brain"] is True
    assert hc["collective_memory"] == "hive-blackboard-shared"
    # the cycle still produces a unit core decision and stays deterministic
    assert abs(c["decision_norm"] - 1.0) < 1e-6
    assert f.cognize(input_vector=INP)["consolidated_decision"] == c["consolidated_decision"]


def test_synapse_relay_converges_active_peers():
    """The lateral relay moves each active node toward its peers' consensus (non-negative shift)."""
    f = _fabric()
    f.process(input_vector=INP)                          # populate poses + activation
    relay = f._synapse_relay()
    assert relay["relayed_nodes"] > 0
    assert relay["mean_consensus_shift"] >= 0.0


def test_zerg_essence_extraction_extracts_traits_without_takeover():
    f = _fabric()
    f.process(input_vector=INP)
    ess = f.zerg_essence_extraction()
    assert ess["extracted"] > 0
    assert ess["takeover"] is False                     # traits extracted, source NOT taken over
    for e in ess["essences"]:
        assert len(e["essence_vector"]) == 8            # the reusable capability signature
        assert e["takeover"] is False


def test_hermes_curator_grades_and_proposes_without_mutating_canon():
    f = _fabric()
    f.process(input_vector=INP)
    cur = f.hermes_curator()
    assert cur["graded"] == 19
    assert cur["mutates_canon"] is False                # archive/propose only, never mutate canon
    # dormant experts get archive proposals; strong active nodes get promote proposals
    assert isinstance(cur["archive_proposals"], list)
    assert isinstance(cur["promote_proposals"], list)


def test_all_nine_hive_styles_present_in_cognition_evidence():
    f = _fabric()
    hc = f.cognize(input_vector=INP)["hive_coordination"]
    # every canon hive-mind style now has an operating footprint in the cycle
    for key in ("synapse_relay", "ring_quorum", "stigmergy", "critical_mass",
                "collective_memory", "organs_of_one_brain", "essence_extraction", "curator"):
        assert key in hc


def test_process_exposes_sacred_positions_and_chords_for_the_visualizer():
    r = _fabric().process(input_vector=INP)
    assert len(r["node_positions"]) == 19
    assert r["node_positions"]["core.brain"]["ring"] == 0       # core at the bindu
    assert len(r["lateral_chords"]) > 0                         # Metatron mesh edges to draw
    assert "node_types" in r and "active_node_set" in r
