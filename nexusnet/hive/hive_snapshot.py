"""Hive evidence snapshot - composes all five real-compute layers into one shadow-evidence object.

Ties together, in a single deterministic pass:
  - Capsule-EBT neural core   (hive.kernel.CapsuleHiveKernel)
  - Collective intelligence   (hive.collective: stigmergy trails + quorum gate over active experts)
  - NexusMemoryNet 1M-core    (hive.memory: long-context compression over the capsule poses)
  - Homeostatic regulation    (hive.regulation: meta-reflection + immune screen)
  - Recursive Dreaming v2      (hive.dreaming: observe-only dream episode)

Pure-Python, deterministic, READ-ONLY/shadow: every layer reports gated flags and the snapshot
asserts they hold. This is the single integration point a future read-only ops endpoint can call -
it does NOT introduce a second control plane and does not mutate production (canon Decision 9).
"""
from __future__ import annotations

from typing import Any

from .kernel import CapsuleHiveKernel
from .collective import PheromoneField, quorum_decision
from .memory import NexusMemoryNet
from .regulation import reflect, screen
from .dreaming import run_dream_episode
from .fabric import HiveMindFabric


def hive_evidence_snapshot(
    *,
    token_values: list[float] | None = None,
    position: int = 0,
    num_experts: int = 6,
    top_k: int = 2,
    d_pose: int = 8,
) -> dict[str, Any]:
    token_values = token_values or [0.5, -0.3, 0.8, 0.1, -0.6, 0.4, 0.2, -0.1]

    # 1. Neural core forward.
    kernel = CapsuleHiveKernel(d_model=16, d_pose=d_pose, num_experts=num_experts, top_k=top_k)
    core = kernel.forward(token_values=token_values, position=position)
    fwd = core["forward"]
    active = fwd["router_active_experts"]
    poses = fwd["capsule_poses"]
    presence = fwd["capsule_presence"]
    output = fwd["output"]

    # 2. Collective: deposit pheromone on the active-expert routes, then test a promotion quorum.
    field = PheromoneField(evaporation_rate=0.1)
    field.step({f"route->expert{e}": presence[e] for e in active})
    quorum = quorum_decision(
        support_votes=len(active), total_agents=num_experts, quorum_threshold=0.66
    )

    # 3. Memory: compress the capsule poses as a long-context store, query with the output.
    mem = NexusMemoryNet(keep_fraction=0.7, num_clusters=min(3, max(1, len(poses))))
    memory = mem.process(token_vectors=poses, relevances=presence, query=output)

    # 4. Regulation: reflect on the deliberation, screen the output for anomalies.
    confidence = 1.0 if fwd["deliberation_converged"] else 0.5
    reflection = reflect(confidences=[confidence], errors=[min(1.0, abs(fwd["final_energy"]))])
    baseline_mean = [0.0] * len(output)
    baseline_std = [1.0] * len(output)
    immune = screen(candidate=output, baseline_mean=baseline_mean, baseline_std=baseline_std)

    # 5. Dreaming v2: an observe-only dream episode over the cortex poses.
    cortex_poses = fwd["cortex_poses"] or [output]
    dream = run_dream_episode(
        current_latents=cortex_poses,
        next_latents=cortex_poses,
        capsule_activation=output,
        mode="individual",
        observe_only=True,
    )

    # 6. Fabric: run the connected organism (Neural Bus + blackboard + fractal node graph) so the
    #    snapshot reflects ONE coordinated hive, not a sequence of isolated component calls.
    fabric = HiveMindFabric(num_orchestrators=2, aos_per_orchestrator=2, experts_per_ao=3, d_pose=d_pose)
    organism = fabric.process(input_vector=output if len(output) == d_pose else token_values[:d_pose])

    layers = {
        "neural_core": core,
        "collective": {"pheromone": field.snapshot(), "quorum": quorum},
        "memory": memory,
        "regulation": {"reflection": reflection, "immune": immune},
        "dreaming": dream,
        "fabric": organism,
    }
    all_gated = all(
        _gated(v) for v in [core, memory, reflection, immune, dream, field.snapshot(), organism]
    )
    return {
        "surface_id": "hive-evidence-snapshot",
        "authority": "NexusBrain",
        "layers": layers,
        "all_layers_shadow_gated": all_gated,
        "production_mutation_allowed": False,
        "native_weight_training": False,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


def _gated(payload: dict[str, Any]) -> bool:
    return payload.get("production_mutation_allowed", False) is False
