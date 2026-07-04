"""HiveMindFabric - the connective tissue that makes the nodes ONE organism (canon PB-017/PB-018).

Instantiates the fractal nested-brain hierarchy (primary core -> orchestrators -> assistant
orchestrators -> experts), wires every parent<->child with TYPED edges, and runs the organism: an
input enters the core, propagates DOWN the Neural Bus through the hierarchy and back UP, the
HiveBlackboard accumulates stigmergic coordination trails (and decays them), the Cortex ignites the
salient set (global-workspace bottleneck), and compute stays SPARSE while monitoring stays FULL
(hive-wide neuroplasticity: everything connected, sparsely activated, fully observed).

Pure-Python, deterministic, shadow-only. This is the fabric the kernel/collective/memory/dreaming
components plug into - not a sequence of isolated calls.
"""
from __future__ import annotations

from collections import deque
from typing import Any

from ..kernel import tensor_ops as ops
from ..kernel.cortex import Cortex
from .neural_bus import NeuralBus
from .blackboard import HiveBlackboard
from .hive_node import HiveNode, Vector
from .sacred_topology import sacred_layout, metatron_chords, topology_signature, HIVE_MIND_STYLES


class HiveMindFabric:
    def __init__(
        self,
        *,
        num_orchestrators: int = 2,
        aos_per_orchestrator: int = 2,
        experts_per_ao: int = 3,
        d_pose: int = 8,
        evaporation_rate: float = 0.2,
    ) -> None:
        self.d_pose = d_pose
        self.bus = NeuralBus()
        self.blackboard = HiveBlackboard(evaporation_rate=evaporation_rate)
        self.cortex = Cortex(ignition_ratio=0.5)
        self.nodes: dict[str, HiveNode] = {}
        self.children: dict[str, list[str]] = {}
        phase = 0

        def add(node_id: str, node_type: str) -> HiveNode:
            nonlocal phase
            node = HiveNode(node_id=node_id, node_type=node_type, d_pose=d_pose, phase_index=phase)
            phase += 1
            self.nodes[node_id] = node
            self.children[node_id] = []
            self.bus.register(node_id)
            return node

        def link(parent: str, child: str) -> None:
            # bidirectional typed edges: parent trusts child, child predicts parent.
            self.nodes[parent].connect(child, edge_type="trusts")
            self.nodes[child].connect(parent, edge_type="predicts")
            self.children[parent].append(child)

        self.core_id = "core.brain"
        add(self.core_id, "core")
        for o in range(num_orchestrators):
            oid = f"orch.{o}"
            add(oid, "orchestrator")
            link(self.core_id, oid)
            for a in range(aos_per_orchestrator):
                aid = f"ao.{o}.{a}"
                add(aid, "assistant_orchestrator")
                link(oid, aid)
                for e in range(experts_per_ao):
                    eid = f"expert.{o}.{a}.{e}"
                    add(eid, "expert")
                    link(aid, eid)

        # --- sacred-geometry topology + hive-mind lateral mesh ---
        # Flower-of-Life rings by hierarchy level (core=bindu), golden-angle phyllotaxis spacing.
        self.levels = [
            [self.core_id],
            [n for n in self.nodes if self.nodes[n].node_type == "orchestrator"],
            [n for n in self.nodes if self.nodes[n].node_type == "assistant_orchestrator"],
            [n for n in self.nodes if self.nodes[n].node_type == "expert"],
        ]
        positions = sacred_layout(self.levels)
        for nid, pos in positions.items():
            self.nodes[nid].position = pos
        # Metatron-chord lateral mesh: sparse peer-consensus edges among siblings (Tyranid synapse /
        # Geth consensus). These are `aligned_with` edges - a separate channel from the down/up tree.
        self.lateral_chords = metatron_chords(self.levels)
        for a, b in self.lateral_chords:
            self.nodes[a].connect(b, edge_type="aligned_with")
            self.nodes[b].connect(a, edge_type="aligned_with")
        self.sacred_signature = topology_signature(self.levels)

    # --- sacred geometry + hive-mind ---

    def sacred_geometry_signature(self) -> dict[str, Any]:
        return self.sacred_signature

    def hive_mind_styles(self) -> dict[str, dict[str, str]]:
        return HIVE_MIND_STYLES

    def zerg_essence_extraction(self) -> dict[str, Any]:
        """Operational Zerg essence-extraction: extract each active node's reusable TRAIT signature
        (its distilled capability 'essence' = normalized pose + domain trait tags) for reuse across the
        hive - WITHOUT taking over the source node. Canon inversion: extract traits, never takeover."""
        essences = []
        for nid, node in self.nodes.items():
            if not node.active:
                continue
            tags = (node.curriculum or {}).get("task_families", []) if node.node_type == "expert" else []
            essences.append({
                "node_id": nid, "node_type": node.node_type,
                "area_of_expertise": node.area_of_expertise,
                "essence_vector": ops.l2_normalize(node.last_pose),   # reusable capability direction
                "trait_tags": tags, "takeover": False,
            })
        return {
            "extracted": len(essences), "essences": essences, "takeover": False,
            "mechanism": "zerg-essence-extraction (reusable traits distilled, source not taken over)",
        }

    def hermes_curator(self, *, strength_promote: float = 0.7) -> dict[str, Any]:
        """Operational Hermes curator: scheduled grading of node skills (usage + pose strength).
        Proposes ARCHIVE for dormant expert skills and PROMOTE for strong active nodes - but NEVER
        mutates protected canon. Canon inversion: Curator can archive/propose, not mutate canon."""
        grades: dict[str, Any] = {}
        archive_proposals: list[str] = []
        promote_proposals: list[str] = []
        for nid, node in self.nodes.items():
            strength = ops.norm(node.last_pose)
            grades[nid] = {"active": node.active, "strength": round(strength, 4),
                           "score": round((1.0 if node.active else 0.0) + strength, 4)}
            if node.node_type == "expert" and not node.active:
                archive_proposals.append(nid)                 # dormant skill -> propose archival
            elif node.active and strength >= strength_promote:
                promote_proposals.append(nid)                 # strong skill -> propose promotion
        return {
            "graded": len(grades), "grades": grades,
            "archive_proposals": sorted(archive_proposals),
            "promote_proposals": sorted(promote_proposals),
            "mutates_canon": False,
            "mechanism": "hermes-curator (scheduled grading; archive/propose only, never mutate canon)",
        }

    def lateral_consensus(self) -> dict[str, Any]:
        """Honeybee quorum + Geth consensus across each ring of peers (over the lateral Metatron mesh):
        a ring 'commits' when a quorum of its active peers agree and no stop-signal is raised."""
        from ..collective.quorum import quorum_decision
        rings = {}
        for level_idx, ids in enumerate(self.levels):
            if not ids:
                continue
            active = [n for n in ids if self.nodes[n].active]
            decision = quorum_decision(
                support_votes=len(active), total_agents=len(ids), quorum_threshold=0.5,
            )
            rings[f"ring_{level_idx}"] = {
                "ring_size": len(ids), "active": len(active),
                "committed": decision["committed"], "reason": decision["reason"],
            }
        return {"rings": rings, "mechanism": "metatron-chord peer mesh + honeybee quorum (Geth consensus)"}

    # --- structure ---

    def _up_sweep(self) -> tuple[dict[str, list[float]], list[float]]:
        """Consolidate active node poses UP the hierarchy (expert -> AO -> orchestrator -> core).

        Each node's consolidated vector starts as its own last pose; children fold their consolidated
        pose into their parent's. The core's consolidated vector is the organism's collective decision.
        """
        consolidated = {nid: list(node.last_pose) for nid, node in self.nodes.items()}
        for level in ("expert", "assistant_orchestrator", "orchestrator"):
            for nid, node in self.nodes.items():
                if node.node_type != level or not node.active:
                    continue
                for parent_id, edge_type in node.edges.items():
                    if edge_type == "predicts":          # edge to this node's parent
                        for i in range(self.d_pose):
                            consolidated[parent_id][i] += consolidated[nid][i]
        decision = ops.l2_normalize(consolidated[self.core_id])
        return consolidated, decision

    def _synapse_relay(self, *, relay_weight: float = 0.3) -> dict[str, Any]:
        """Operational Tyranid synapse-relay / Geth consensus over the Metatron lateral mesh: active
        peers exchange poses across their `aligned_with` edges and converge toward a local consensus.
        Synchronous (snapshot then update) so it is order-independent. Returns the consensus shift."""
        snapshot = {nid: list(n.last_pose) for nid, n in self.nodes.items()}
        shifts: list[float] = []
        for nid, node in self.nodes.items():
            if not node.active:
                continue
            peers = [t for t, et in node.edges.items() if et == "aligned_with" and self.nodes[t].active]
            if not peers:
                continue
            peer_mean = [sum(snapshot[p][i] for p in peers) / len(peers) for i in range(self.d_pose)]
            blended = [snapshot[nid][i] + relay_weight * peer_mean[i] for i in range(self.d_pose)]
            refined = ops.l2_normalize(blended)
            shifts.append(1.0 - max(-1.0, min(1.0, ops.cosine(snapshot[nid], refined))))
            node.last_pose = refined
        return {
            "relayed_nodes": len(shifts),
            "mean_consensus_shift": (sum(shifts) / len(shifts)) if shifts else 0.0,
            "mechanism": "tyranid-synapse-relay + geth-consensus over the metatron lateral mesh",
        }

    def cognize(self, *, input_vector: Vector, steps: int | None = None) -> dict[str, Any]:
        """One full cognitive cycle, operating the hive-mind styles over the sacred-geometry mesh:
        DOWN sweep (route to experts) -> SYNAPSE RELAY (lateral peer consensus over the Metatron mesh)
        -> UP sweep (consolidate to a core decision) -> Cortex ignition + per-ring honeybee/Geth quorum.
        """
        down = self.process(input_vector=input_vector, steps=steps)
        synapse = self._synapse_relay()                  # lateral consensus refines poses before consolidation
        consolidated, decision = self._up_sweep()
        # Gravemind critical-mass: a higher-order mind forms once a critical fraction has ignited.
        critical_mass = down["active_count"] >= 0.5 * down["connectivity"]["total_nodes"]
        poses = [consolidated[nid] for nid in self.nodes]
        saliences = [ops.norm(p) for p in poses]
        ignition = self.cortex.ignite(saliences=saliences, poses=poses)
        ignited_ids = [list(self.nodes.keys())[i] for i in ignition["ignited_experts"]]
        return {
            **down,
            "surface_id": "hive-mind-cognitive-cycle",
            "cognitive_cycle_complete": True,
            "consolidated_decision": decision,           # the organism's collective output vector
            "decision_norm": round(ops.norm(decision), 8),
            "cortex_final_ignited": ignited_ids,
            "down_sweep_reached_experts": down["reached_experts"],
            # the hive-mind styles, OPERATING (not just tagged) over this cycle:
            "hive_coordination": {
                "synapse_relay": synapse,                                  # Tyranid / Geth lateral consensus
                "ring_quorum": self.lateral_consensus(),                   # honeybee quorum per ring
                "stigmergy": {"active_trails": len(down["blackboard"]["active_topics"])},  # social-insect
                "critical_mass": critical_mass,                           # Gravemind higher-order mind
                "collective_memory": "hive-blackboard-shared",            # Borg (permissioned/ledgered)
                "organs_of_one_brain": True,                              # siphonophore (governed hierarchy)
                "essence_extraction": self.zerg_essence_extraction(),     # Zerg (traits, not takeover)
                "curator": self.hermes_curator(),                         # Hermes (grade/archive/propose)
            },
        }

    def connectivity(self) -> dict[str, Any]:
        """BFS from the core over the edge graph: a true organism has every node reachable."""
        seen = {self.core_id}
        queue = deque([self.core_id])
        while queue:
            nid = queue.popleft()
            for target in self.nodes[nid].edges:
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        return {
            "total_nodes": len(self.nodes),
            "reachable_from_core": len(seen),
            "fully_connected": len(seen) == len(self.nodes),
            "by_type": self._counts_by_type(),
        }

    def _counts_by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for node in self.nodes.values():
            counts[node.node_type] = counts.get(node.node_type, 0) + 1
        return counts

    # --- runtime ---

    def process(self, *, input_vector: Vector, steps: int | None = None) -> dict[str, Any]:
        """Run the organism: inject input at the core, propagate through the hive for enough steps to
        reach the experts and return, igniting the salient set and decaying coordination trails."""
        depth = 4  # core -> orchestrator -> ao -> expert
        # one forward sweep down the hierarchy: the deterministic top-k routing keeps activation sparse
        # (deeper recirculation would saturate every node, which is not how a gated hive routes).
        steps = steps if steps is not None else depth
        # Reset transient runtime so every process() call is independent and reproducible.
        self.bus = NeuralBus()
        for nid in self.nodes:
            self.bus.register(nid)
        self.blackboard = HiveBlackboard(evaporation_rate=self.blackboard._field.rho)
        for node in self.nodes.values():
            node.activation_count = 0
            node.last_pose = [0.0] * self.d_pose
            node.active = False
        step_trace: list[dict[str, Any]] = []
        ever_active: set[str] = set()
        for t in range(steps):
            ext = input_vector if t == 0 else None
            # CLOCKED delivery: snapshot every node's inbox FIRST, so messages published this step are
            # only seen next step (one hierarchy level per step) - order-independent propagation.
            inboxes = {nid: self.bus.deliver(nid) for nid in self.nodes}
            active_this_step = []
            for node in self.nodes.values():
                ext_for_node = ext if node.node_id == self.core_id else None
                result = node.step(
                    bus=self.bus, blackboard=self.blackboard,
                    external_input=ext_for_node, incoming=inboxes[node.node_id],
                )
                if result["active"]:
                    active_this_step.append(node.node_id)
                    ever_active.add(node.node_id)
            self.blackboard.tick()                       # stigmergic decay each step
            step_trace.append({"step": t, "active_nodes": active_this_step})

        # Cortex global-workspace ignition over the final node poses.
        poses = [self.nodes[nid].last_pose for nid in self.nodes]
        saliences = [ops.norm(p) for p in poses]
        ignition = self.cortex.ignite(saliences=saliences, poses=poses)
        ignited_ids = [list(self.nodes.keys())[i] for i in ignition["ignited_experts"]]

        active_ids = sorted(ever_active)                 # any node that ignited during propagation
        reached_types = sorted({self.nodes[n].node_type for n in ever_active})
        return {
            "surface_id": "hive-mind-fabric",
            "authority": "NexusBrain",
            "connectivity": self.connectivity(),
            "steps": steps,
            "active_nodes": active_ids,
            "active_count": len(active_ids),
            "sparse_activation": len(active_ids) < len(self.nodes),
            "propagation_reached_types": reached_types,   # which scales the signal lit up
            "reached_experts": "expert" in reached_types,
            "cortex_ignited": ignited_ids,
            "broadcast": ignition["broadcast"],
            "neural_bus": self.bus.efficiency(full_state_dim=64),
            "blackboard": self.blackboard.snapshot(),
            "sacred_geometry": self.sacred_signature,     # flower-field + metatron chords + torus loops
            "node_positions": {nid: n.position for nid, n in self.nodes.items()},   # Flower-of-Life coords
            "lateral_chords": [list(c) for c in self.lateral_chords],               # Metatron mesh edges
            "node_types": {nid: n.node_type for nid, n in self.nodes.items()},
            "active_node_set": active_ids,
            "lateral_consensus": self.lateral_consensus(),  # honeybee quorum / Geth consensus per ring
            "hive_mind_styles": list(HIVE_MIND_STYLES),
            "step_trace": step_trace,
            "production_mutation_allowed": False,
            "native_weight_training": False,
            "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
        }
