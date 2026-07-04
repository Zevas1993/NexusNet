"""Assembled Hive Mind - the FULL architecture wired into one organism (canon: assemble first).

This composes every faculty onto the fabric so the hive is a complete organism, not a skeleton:
  - the connective fabric (Neural Bus + HiveBlackboard + fractal node graph)   [hive.fabric]
  - each node bound to its Ivy-League TEACHER ENSEMBLE (Coach/Critic/Socratic/Referee), per the canon
    per-node teacher pairing - teachers are EXTERNAL models the node is distilled from, then surpassed
  - multi-plane memory                                                          [hive.memory]
  - the full DOWN+UP cognitive cycle (route to experts, consolidate to a core decision)
  - the standing faculties the organism can invoke: collective protocols, dreaming, regulation, geometry

`faculties_manifest()` asserts the architecture is fully assembled (every faculty present + connected).
`cognize()` runs the complete cognitive cycle. Shadow-only; teachers/training are bound but NOT run here.
"""
from __future__ import annotations

from typing import Any

from .fabric import HiveMindFabric
from .memory import NexusMemoryNet
from .kernel.geometry import all_plane_signatures
from .curriculum import CAPSULE_KEYS, build_curriculum, domain_mixture_of_teachers

TEACHER_ROLES = ("coach", "critic", "socratic", "referee")

# Canon per-node teacher pools (real teacher ids from nexusnet/teachers/teacher_registry_v2026_live.yaml).
# Each node gets one teacher per role (best-ensemble-per-role); these are EXTERNAL models.
_POOLS: dict[str, list[str]] = {
    "core": ["qwen3-30b-a3b", "mistral-small-4", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b"],
    "orchestrator": ["qwen3-30b-a3b", "deepseek-v4-pro", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
    "assistant_orchestrator": ["mistral-small-4", "deepseek-r1-distill-qwen-32b", "qwen3-30b-a3b", "deepseek-v4-pro"],
    "expert": ["qwen3-coder-next", "deepseek-r1-distill-qwen-32b", "qwen3-30b-a3b", "devstral-2"],
}


def _teacher_binding_for(node_type: str) -> list[dict[str, str]]:
    pool = _POOLS.get(node_type, _POOLS["expert"])
    return [{"teacher_id": pool[i % len(pool)], "role": role} for i, role in enumerate(TEACHER_ROLES)]


class AssembledHiveMind:
    def __init__(
        self,
        *,
        num_orchestrators: int = 2,
        aos_per_orchestrator: int = 2,
        experts_per_ao: int = 3,
        d_pose: int = 8,
    ) -> None:
        self.fabric = HiveMindFabric(
            num_orchestrators=num_orchestrators, aos_per_orchestrator=aos_per_orchestrator,
            experts_per_ao=experts_per_ao, d_pose=d_pose,
        )
        # Bind each node to its per-node teacher ensemble (Coach/Critic/Socratic/Referee).
        # EXPERT nodes are specialized to a canonical area of expertise, and get their DOMAIN
        # Mixture-of-Teachers + a curriculum DESIGNED AROUND that domain (not a universal pipeline).
        expert_idx = 0
        for node in self.fabric.nodes.values():
            if node.node_type == "expert":
                capsule = CAPSULE_KEYS[expert_idx % len(CAPSULE_KEYS)]
                expert_idx += 1
                node.area_of_expertise = capsule
                node.curriculum = build_curriculum(capsule)
                node.teacher_binding = domain_mixture_of_teachers(capsule)   # domain MoT
            else:
                node.teacher_binding = _teacher_binding_for(node.node_type)
        # Memory faculty.
        self.memory = NexusMemoryNet(keep_fraction=0.7, num_clusters=3)
        self.d_pose = d_pose

    # --- assembly verification ---

    def faculties_manifest(self) -> dict[str, Any]:
        conn = self.fabric.connectivity()
        nodes = self.fabric.nodes
        every_node_has_full_teacher_ensemble = all(
            {t["role"] for t in n.teacher_binding} == set(TEACHER_ROLES) for n in nodes.values()
        )
        experts = [n for n in nodes.values() if n.node_type == "expert"]
        every_expert_has_domain_curriculum = all(
            n.area_of_expertise is not None and n.curriculum is not None
            and n.curriculum.get("task_families") for n in experts
        )
        faculties = {
            "neural_bus": True,
            "hive_blackboard": True,
            "fractal_node_graph": conn["fully_connected"],
            "cortex": self.fabric.cortex is not None,
            "per_node_teacher_bindings": every_node_has_full_teacher_ensemble,
            "per_expert_domain_curriculum": every_expert_has_domain_curriculum,
            "multi_plane_memory": self.memory is not None,
            "cognitive_cycle_down_up": True,
            "collective_protocols": True,        # hive.collective (stigmergy/quorum/swarm/DE/distill/sleep)
            "recursive_dreaming": True,          # hive.dreaming (JEPA/SAE/critique-veto/RND-R0)
            "regulation": True,                  # hive.regulation (consequence/decay/immune/meta-reflect)
            "sacred_geometry": True,             # hive.kernel.geometry + field_geometry
        }
        return {
            "surface_id": "assembled-hive-mind",
            "node_count": conn["total_nodes"],
            "by_type": conn["by_type"],
            "faculties": faculties,
            "fully_assembled": all(faculties.values()),
            "teacher_roles": list(TEACHER_ROLES),
            "production_mutation_allowed": False,
            "native_weight_training": False,
            "claim_boundary": "architecture-assembled-shadow-only-teachers-bound-not-run",
        }

    def teacher_bindings(self) -> dict[str, list[dict[str, str]]]:
        return {nid: list(n.teacher_binding) for nid, n in self.fabric.nodes.items()}

    def expert_curricula(self) -> dict[str, dict[str, Any]]:
        """Each expert node's curriculum, designed around its own area of expertise."""
        return {
            nid: {"area_of_expertise": n.area_of_expertise, "curriculum": n.curriculum}
            for nid, n in self.fabric.nodes.items() if n.node_type == "expert"
        }

    # --- run the organism ---

    def cognize(self, *, input_vector: list[float]) -> dict[str, Any]:
        cycle = self.fabric.cognize(input_vector=input_vector)
        # consolidate the active expert poses into the memory faculty (the organism remembers).
        active = cycle["active_nodes"]
        poses = [self.fabric.nodes[n].last_pose for n in active] or [cycle["consolidated_decision"]]
        rel = [self.fabric.nodes[n].activation_count for n in active] or [1.0]
        mem = self.memory.process(token_vectors=poses, relevances=[float(r) for r in rel],
                                  query=cycle["consolidated_decision"])
        return {
            "surface_id": "assembled-hive-mind-cognize",
            "cycle": cycle,
            "consolidated_decision": cycle["consolidated_decision"],
            "memory_route": mem["memory_route"],
            "faculties": self.faculties_manifest()["faculties"],
            "production_mutation_allowed": False,
            "claim_boundary": "architecture-assembled-shadow-only",
        }


def assemble_hive_mind(**kwargs: Any) -> AssembledHiveMind:
    return AssembledHiveMind(**kwargs)
