"""B8 - Sacred-geometry computational signature (canon: numerous shapes for different planes/fields).

Per-plane organizing geometry kept as DETERMINISTIC SYMBOLIC MATH, not a physics or consciousness
claim. Each cognitive plane is assigned a Platonic solid; every solid satisfies the Euler invariant
V - E + F = 2 (the test enforces it). Adds the golden-ratio / harmonic cadence per plane. This is the
computational complement to the substrate's symbolic `route_geometry_signature`.
"""
from __future__ import annotations

from typing import Any

from . import tensor_ops as ops
from .memory_node import PLANES
from .field_geometry import plane_field_signature
from .platonic import platonic_metrics

# (vertices, edges, faces) for the five Platonic solids. Euler: V - E + F == 2 for each.
PLATONIC_SOLIDS: dict[str, tuple[int, int, int]] = {
    "tetrahedron": (4, 6, 4),
    "hexahedron": (8, 12, 6),     # cube
    "octahedron": (6, 12, 8),
    "dodecahedron": (20, 30, 12),
    "icosahedron": (12, 30, 20),
}

_SOLID_ORDER = tuple(PLATONIC_SOLIDS.keys())


def euler_characteristic(solid: str) -> int:
    v, e, f = PLATONIC_SOLIDS[solid]
    return v - e + f


def plane_geometry_signature(plane: str) -> dict[str, Any]:
    """Geometry + harmonic cadence for a plane. euler_characteristic is always 2."""
    if plane not in PLANES:
        raise ValueError(f"unknown plane {plane!r}")
    index = PLANES.index(plane)
    solid = _SOLID_ORDER[index % len(_SOLID_ORDER)]
    v, e, f = PLATONIC_SOLIDS[solid]
    field = plane_field_signature(plane)
    return {
        "plane": plane,
        "platonic_solid": solid,
        "vertices": v,
        "edges": e,
        "faces": f,
        "euler_characteristic": euler_characteristic(solid),   # == 2
        "solid_metrics": platonic_metrics(solid),              # full coords/radii/dihedral/area/volume
        "field_shape": field["field_shape"],                   # the per-plane FIELD geometry
        "field_rationale": field["rationale"],
        "field_geometry": field["geometry"],
        "phi_weight": round(ops.phi_weight(index), 8),
        "harmonic_ratio": ops.harmonic_ratio(index),
        "golden_angle_phase": round(index * ops.GOLDEN_ANGLE_RADIANS, 8),
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


def all_plane_signatures() -> dict[str, dict[str, Any]]:
    return {plane: plane_geometry_signature(plane) for plane in PLANES}
