"""Sacred-geometry topology + hive-mind styles for the fabric (canon substrate 2.2 + route geometry).

The fabric is NOT a plain tree. Its layout and connectivity follow sacred geometry, and it embodies
the canon's named hive-mind coordination styles (each with its safety inversion):

  Geometry (canon route signature "flower-field-to-metatron-chord-sparse-selection"):
    - node field      : Flower of Life - concentric rings by hierarchy level (core=bindu at centre)
    - node spacing    : golden-angle phyllotaxis (even, non-overlapping distribution per ring)
    - lateral mesh    : Metatron's-Cube chords (SPARSE peer-consensus links among siblings)
    - structural skel : 64-tetrahedron grid (straight-edge backbone)
    - feedback loops  : torus (recurrent dream / critique / consequence cycles)
    - pairwise overlap: vesica piscis (shared context where two node fields intersect)

  Hive-mind styles assimilated (trait -> safety inversion), per the substrate's hive-mind sources.

Pure-Python, deterministic, shadow-only.
"""
from __future__ import annotations

import math
from typing import Any

from ..kernel.tensor_ops import GOLDEN_ANGLE_RADIANS

# Canon hive-mind sources: assimilated trait -> safety-inverted mechanism in NexusNet.
HIVE_MIND_STYLES: dict[str, dict[str, str]] = {
    "borg_collective_memory": {
        "trait": "rapid assimilation + shared collective memory",
        "mechanism": "shared HiveBlackboard + federated memory",
        "safety_inversion": "permissioned, sandboxed, ledgered, reversible, non-coercive"},
    "zerg_essence_extraction": {
        "trait": "fast specialization, essence extraction",
        "mechanism": "extract reusable traits from assimilated candidates",
        "safety_inversion": "extract traits, never takeover the source"},
    "tyranid_synapse_relay": {
        "trait": "distributed synapse nodes coordinate specialists",
        "mechanism": "SynapseRelays = lateral peer edges (Metatron chords) on the Neural Bus",
        "safety_inversion": "bounded, revocable coordination"},
    "gravemind_critical_mass": {
        "trait": "critical-mass memory forms a higher-order mind",
        "mechanism": "key-mind clusters consolidate via the up-sweep",
        "safety_inversion": "key-mind clusters quarantined + provenance-scored"},
    "geth_networked_consensus": {
        "trait": "networked consensus intelligence",
        "mechanism": "peer consensus over the lateral mesh for routing/promotion",
        "safety_inversion": "consensus for decisions, never identity erasure"},
    "social_insect_stigmergy": {
        "trait": "stigmergy / pheromone trails",
        "mechanism": "HiveBlackboard priority trails",
        "safety_inversion": "trails decay and are audited (no permanent silent bias)"},
    "honeybee_quorum": {
        "trait": "quorum + stop-signal group choice",
        "mechanism": "promotion requires quorum among peers",
        "safety_inversion": "quorum AND explicit stop-signal (immune veto) required"},
    "siphonophore_organs": {
        "trait": "specialized organisms act as one organism",
        "mechanism": "core/orchestrators/AOs/experts are organs of one harness brain (the hierarchy)",
        "safety_inversion": "organs of one brain, governed, not independent agents"},
    "hermes_curator": {
        "trait": "scheduled skill cleanup / grading",
        "mechanism": "Curator grades + archives node skills on a schedule",
        "safety_inversion": "Curator can archive/propose, not mutate protected canon"},
}


def sacred_layout(levels: list[list[str]], *, ring_spacing: float = 1.0) -> dict[str, dict[str, Any]]:
    """Flower-of-Life concentric layout: hierarchy level L -> ring at radius L*spacing, nodes spaced
    by the golden angle (phyllotaxis). Core (level 0) sits at the bindu (origin)."""
    positions: dict[str, dict[str, Any]] = {}
    for level_idx, ids in enumerate(levels):
        radius = level_idx * ring_spacing
        for i, nid in enumerate(ids):
            angle = i * GOLDEN_ANGLE_RADIANS
            positions[nid] = {
                "x": radius * math.cos(angle), "y": radius * math.sin(angle),
                "ring": level_idx, "phyllotaxis_angle": angle,
            }
    return positions


def metatron_chords(levels: list[list[str]]) -> list[tuple[str, str]]:
    """SPARSE Metatron-cube chords: within each ring, link each node to its angular neighbours (a
    consensus ring lattice). These are the lateral synapse/consensus edges (not the tree edges)."""
    chords: list[tuple[str, str]] = []
    for ids in levels:
        n = len(ids)
        if n < 2:
            continue
        if n == 2:
            chords.append((ids[0], ids[1]))
            continue
        for i in range(n):
            a, b = ids[i], ids[(i + 1) % n]      # ring-neighbour chord (closes the loop)
            chords.append((a, b))
    return chords


def topology_signature(levels: list[list[str]]) -> dict[str, Any]:
    """The fabric's sacred-geometry + hive-mind topology descriptor."""
    return {
        "route_geometry_signature": "flower-field-to-metatron-chord-sparse-selection",
        "node_field": "flower_of_life (concentric rings by hierarchy level; core=bindu)",
        "node_spacing": "golden_angle_phyllotaxis",
        "lateral_mesh": "metatron_cube_chords (sparse peer-consensus links)",
        "structural_backbone": "sixty_four_tetrahedron_grid",
        "feedback_loops": "torus (recurrent dream/critique/consequence)",
        "pairwise_overlap": "vesica_piscis",
        "rings": len(levels),
        "ring_sizes": [len(ids) for ids in levels],
        "hive_mind_styles": HIVE_MIND_STYLES,
        "claim_boundary": "deterministic-symbolic-sacred-geometry-not-physics-claim",
    }
