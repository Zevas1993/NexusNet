from __future__ import annotations

from nexusnet.hive.curriculum import (
    EXPERT_CAPSULES,
    CAPSULE_KEYS,
    build_curriculum,
    domain_mixture_of_teachers,
    all_curricula,
    ROLES,
)
from nexusnet.hive.assembly import assemble_hive_mind


CANONICAL_19 = {
    "vision", "auditory", "linguist", "librarian", "mathematician", "coder", "scientist", "engineer",
    "medical", "legal", "financial", "strategist", "simulator", "robotics", "creative_artist",
    "psychologist", "verifier", "ethicist", "guardian",
}
FRONTIER = {
    "philosopher", "physicist", "chemist", "biologist", "neuroscientist", "cosmologist", "logician",
    "economist", "historian", "cryptographer", "quantum_information", "materials_scientist",
}


def test_capsule_roster_covers_canonical_and_frontier_domains():
    keys = set(CAPSULE_KEYS)
    assert CANONICAL_19 <= keys                        # the canonical 19
    assert FRONTIER <= keys                            # expandable frontier / edge-case experts
    assert len(CAPSULE_KEYS) >= 31
    for key, spec in EXPERT_CAPSULES.items():
        assert spec["area_of_expertise"]
        assert spec["task_families"]
        assert len(spec["teachers"]) >= 4              # enough for a 4-role MoT
        assert spec["eval_gates"]


def test_frontier_experts_have_distinct_domains():
    for key in ("philosopher", "physicist", "quantum_information", "logician"):
        cur = build_curriculum(key)
        assert cur["area_of_expertise"]
        assert cur["task_families"]
        assert {t["role"] for t in cur["teacher_mixture"]} == set(ROLES)


def test_curriculum_is_designed_around_the_experts_domain():
    coder = build_curriculum("coder")
    vision = build_curriculum("vision")
    # the coder curriculum is coding tasks taught by coding teachers
    assert "code_generation" in coder["task_families"]
    assert any(t["teacher_id"] == "qwen3-coder-next" for t in coder["teacher_mixture"])
    assert "humaneval" in coder["eval_gates"]
    # the vision curriculum is a DIFFERENT, vision-specific curriculum
    assert "image_classification" in vision["task_families"]
    assert any(t["teacher_id"] == "qwen3-vl" for t in vision["teacher_mixture"])
    assert coder["task_families"] != vision["task_families"]
    assert coder["eval_gates"] != vision["eval_gates"]


def test_curriculum_has_domain_difficulty_ladder_and_full_mot():
    cur = build_curriculum("mathematician", difficulty_levels=5)
    assert len(cur["difficulty_ladder"]) == 5
    # the Challenger escalates difficulty within the domain's own task families
    assert cur["difficulty_ladder"][0]["challenger_difficulty"] < cur["difficulty_ladder"][-1]["challenger_difficulty"]
    assert all(level["families"] == cur["task_families"] for level in cur["difficulty_ladder"])
    assert {t["role"] for t in cur["teacher_mixture"]} == set(ROLES)


def test_all_curricula_are_distinct_per_domain():
    cur = all_curricula()
    assert len(cur) == len(CAPSULE_KEYS)
    families = [tuple(c["task_families"]) for c in cur.values()]
    assert len(set(families)) == len(cur)              # every domain has its own task set


def test_domain_mixture_of_teachers_has_four_roles():
    mot = domain_mixture_of_teachers("coder")
    assert {t["role"] for t in mot} == set(ROLES)
    assert all(t["teacher_id"] for t in mot)


# --- assembly: experts are domain-specialized with domain curricula ---

def test_assembled_experts_are_domain_specialized():
    hm = assemble_hive_mind(num_orchestrators=3, aos_per_orchestrator=3, experts_per_ao=2, d_pose=8)
    man = hm.faculties_manifest()
    assert man["faculties"]["per_expert_domain_curriculum"] is True
    cur = hm.expert_curricula()
    # every expert has a designed area of expertise and a domain curriculum
    for nid, entry in cur.items():
        assert entry["area_of_expertise"] in CAPSULE_KEYS
        assert entry["curriculum"]["task_families"]
        assert entry["curriculum"]["area_of_expertise"]
    # distinct experts cover distinct domains (first 18 of the 19 here)
    domains = [e["area_of_expertise"] for e in cur.values()]
    assert len(set(domains)) == len(domains)


def test_expert_teacher_binding_matches_its_domain():
    hm = assemble_hive_mind(num_orchestrators=2, aos_per_orchestrator=2, experts_per_ao=3, d_pose=8)
    cur = hm.expert_curricula()
    tb = hm.teacher_bindings()
    # the vision expert (first) is taught by vision teachers, not generic ones
    vision_node = next(nid for nid, e in cur.items() if e["area_of_expertise"] == "vision")
    assert any(t["teacher_id"] == "qwen3-vl" for t in tb[vision_node])


def test_domain_specialist_teacher_models_are_assigned():
    """Researched real domain-specialist teacher models drive the per-field Mixture-of-Teachers."""
    from nexusnet.hive.curriculum import DOMAIN_SPECIALIST_PROFILES, DOMAIN_SPECIALIST_TEACHERS
    expectations = {
        "mathematician": "deepseek-math-v2",
        "chemist": "chemdfm-v1.5-8b",
        "biologist": "biomistral-7b",
        "medical": "medgemma-27b",
        "legal": "saullm-141b",
        "financial": "fingpt",
        "physicist": "sciglm-32b",
        "materials_scientist": "mattergen",
        # validated-pass specialist swaps
        "auditory": "voxtral-transcribe-2",
        "psychologist": "psycollm",
        "climate_scientist": "climategpt-70b",
        "geologist": "jiuzhou",
    }
    for capsule, expected_teacher in expectations.items():
        ids = {t["teacher_id"] for t in build_curriculum(capsule)["teacher_mixture"]}
        assert expected_teacher in ids, (capsule, expected_teacher, ids)
    # every specialist teacher id used is documented with a source
    for capsule, teachers in DOMAIN_SPECIALIST_TEACHERS.items():
        for tid in teachers:
            if tid in DOMAIN_SPECIALIST_PROFILES:
                assert DOMAIN_SPECIALIST_PROFILES[tid]["source"].startswith("http")
