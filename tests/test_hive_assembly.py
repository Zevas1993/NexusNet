from __future__ import annotations

from nexusnet.hive.assembly import assemble_hive_mind, TEACHER_ROLES

INP = [0.6, -0.3, 0.8, 0.1, -0.4, 0.5, 0.2, -0.1]


def _hm():
    return assemble_hive_mind(num_orchestrators=2, aos_per_orchestrator=2, experts_per_ao=3, d_pose=8)


def test_full_architecture_is_assembled():
    man = _hm().faculties_manifest()
    assert man["fully_assembled"] is True
    # every required faculty is present and connected
    for faculty in (
        "neural_bus", "hive_blackboard", "fractal_node_graph", "cortex",
        "per_node_teacher_bindings", "multi_plane_memory", "cognitive_cycle_down_up",
        "collective_protocols", "recursive_dreaming", "regulation", "sacred_geometry",
    ):
        assert man["faculties"][faculty] is True, faculty


def test_every_node_bound_to_full_teacher_ensemble():
    hm = _hm()
    bindings = hm.teacher_bindings()
    assert len(bindings) == 19
    for nid, ensemble in bindings.items():
        roles = {t["role"] for t in ensemble}
        assert roles == set(TEACHER_ROLES)               # Coach/Critic/Socratic/Referee, per node
        assert all(t["teacher_id"] for t in ensemble)    # real external teacher model ids


def test_teacher_pools_are_domain_specific_for_experts():
    hm = _hm()
    tb = hm.teacher_bindings()
    cur = hm.expert_curricula()
    core_ids = {t["teacher_id"] for t in tb["core.brain"]}
    # the first expert is the canonical 'vision' capsule -> taught by vision teachers, not the core pool
    assert cur["expert.0.0.0"]["area_of_expertise"] == "vision"
    expert_ids = {t["teacher_id"] for t in tb["expert.0.0.0"]}
    assert core_ids != expert_ids                        # experts get their DOMAIN pool, not the core pool
    assert "qwen3-vl" in expert_ids                      # real vision teacher id for the vision expert


def test_full_cognitive_cycle_runs_down_then_up():
    r = _hm().cognize(input_vector=INP)
    cycle = r["cycle"]
    assert cycle["cognitive_cycle_complete"] is True
    assert cycle["down_sweep_reached_experts"] is True   # input routed all the way to the experts
    assert abs(cycle["decision_norm"] - 1.0) < 1e-6      # consolidated core decision is a unit vector
    assert len(r["consolidated_decision"]) == 8
    assert r["memory_route"] in {"in_context", "external_memory"}


def test_assembly_is_deterministic_and_gated():
    hm = _hm()
    a = hm.cognize(input_vector=INP)
    b = hm.cognize(input_vector=INP)
    assert a["consolidated_decision"] == b["consolidated_decision"]
    assert a["production_mutation_allowed"] is False
    man = hm.faculties_manifest()
    assert man["native_weight_training"] is False        # teachers bound, NOT trained here
