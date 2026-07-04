"""Full Platonic-solid mathematics (real coordinates + closed-form metric properties).

Beyond (V, E, F) and Euler: exact vertex coordinates (golden-ratio-based for the dodecahedron and
icosahedron), edge length, circumradius / inradius / midradius, dihedral angle, surface area, and
volume - the genuine closed-form formulas, cross-checked against the coordinates. Deterministic-
symbolic math (no physics/consciousness claim).

Closed forms (edge length a):
  tetrahedron   R=a*sqrt6/4   r=a*sqrt6/12   rho=a/sqrt8    dih=acos(1/3)
                SA=sqrt3*a^2  V=a^3/(6*sqrt2)
  cube          R=a*sqrt3/2   r=a/2          rho=a/sqrt2    dih=pi/2
                SA=6a^2       V=a^3
  octahedron    R=a/sqrt2     r=a/sqrt6      rho=a/2        dih=acos(-1/3)
                SA=2*sqrt3*a^2 V=sqrt2/3*a^3
  dodecahedron  R=a*sqrt3*phi/2  dih=acos(-1/sqrt5)
                SA=3*sqrt(25+10*sqrt5)*a^2   V=(15+7*sqrt5)/4*a^3
  icosahedron   R=a*sqrt(phi^2+1)/2  dih=acos(-sqrt5/3)
                SA=5*sqrt3*a^2   V=5*(3+sqrt5)/12*a^3
"""
from __future__ import annotations

import math
from typing import Any

from .tensor_ops import PHI

Point3 = tuple[float, float, float]


def _dist(a: Point3, b: Point3) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _scaled(pts: list[Point3], s: float) -> list[Point3]:
    return [(s * x, s * y, s * z) for (x, y, z) in pts]


def _signs(base, pattern) -> list[Point3]:
    """Expand a coordinate with the given +/- sign pattern over the nonzero slots."""
    out = []
    nz = [i for i, v in enumerate(base) if v != 0]
    for mask in range(2 ** len(nz)):
        p = list(base)
        for bit, idx in enumerate(nz):
            if (mask >> bit) & 1:
                p[idx] = -p[idx]
        out.append(tuple(p))
    return out


def _even_perms_signs(a: float, b: float, c: float) -> list[Point3]:
    """The three even cyclic permutations of (a,b,c), each with all sign combinations on nonzero
    coordinates. Used for the icosahedron/dodecahedron golden-ratio coordinate sets."""
    seen: set[Point3] = set()
    for base in [(a, b, c), (b, c, a), (c, a, b)]:
        for p in _signs(base, None):
            seen.add(p)
    return sorted(seen)


def _vertices(solid: str) -> list[Point3]:
    inv = 1.0 / PHI
    if solid == "tetrahedron":
        return [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    if solid == "hexahedron":  # cube
        return _signs((1, 1, 1), None)
    if solid == "octahedron":
        return [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    if solid == "icosahedron":
        return _even_perms_signs(0.0, 1.0, PHI)
    if solid == "dodecahedron":
        cube = _signs((1, 1, 1), None)
        rect = _even_perms_signs(0.0, inv, PHI)
        return cube + rect
    raise ValueError(f"unknown solid {solid!r}")


_FACE_COUNT = {"tetrahedron": 4, "hexahedron": 6, "octahedron": 8, "dodecahedron": 12, "icosahedron": 20}


def _min_edge(verts: list[Point3]) -> float:
    return min(_dist(verts[i], verts[j]) for i in range(len(verts)) for j in range(i + 1, len(verts)))


def _count_edges(verts: list[Point3], edge: float) -> int:
    return sum(
        1 for i in range(len(verts)) for j in range(i + 1, len(verts))
        if abs(_dist(verts[i], verts[j]) - edge) < 1e-9
    )


def _midradius_from_coords(verts: list[Point3], edge: float) -> float:
    """Distance from the centre to the midpoint of an edge (equal for all edges of a Platonic solid)."""
    best = None
    for i in range(len(verts)):
        for j in range(i + 1, len(verts)):
            if abs(_dist(verts[i], verts[j]) - edge) < 1e-9:
                mid = tuple((verts[i][d] + verts[j][d]) / 2 for d in range(3))
                best = _dist((0, 0, 0), mid)
                break
        if best is not None:
            break
    return best


# Closed-form metric coefficients as multiples of the EDGE length a.
def _closed_form(solid: str, a: float) -> dict[str, float]:
    s5 = math.sqrt(5.0)
    if solid == "tetrahedron":
        return dict(circumradius=a * math.sqrt(6) / 4, inradius=a * math.sqrt(6) / 12,
                    midradius=a / math.sqrt(8), dihedral=math.acos(1 / 3),
                    surface_area=math.sqrt(3) * a * a, volume=a ** 3 / (6 * math.sqrt(2)))
    if solid == "hexahedron":
        return dict(circumradius=a * math.sqrt(3) / 2, inradius=a / 2, midradius=a / math.sqrt(2),
                    dihedral=math.pi / 2, surface_area=6 * a * a, volume=a ** 3)
    if solid == "octahedron":
        return dict(circumradius=a / math.sqrt(2), inradius=a / math.sqrt(6), midradius=a / 2,
                    dihedral=math.acos(-1 / 3), surface_area=2 * math.sqrt(3) * a * a,
                    volume=math.sqrt(2) / 3 * a ** 3)
    if solid == "dodecahedron":
        return dict(circumradius=a * math.sqrt(3) * PHI / 2,
                    inradius=a / 2 * math.sqrt((25 + 11 * s5) / 10),
                    midradius=a * PHI ** 2 / 2, dihedral=math.acos(-1 / s5),
                    surface_area=3 * math.sqrt(25 + 10 * s5) * a * a,
                    volume=(15 + 7 * s5) / 4 * a ** 3)
    if solid == "icosahedron":
        return dict(circumradius=a * math.sqrt(PHI ** 2 + 1) / 2,
                    inradius=a * PHI ** 2 / (2 * math.sqrt(3)),
                    midradius=a * PHI / 2, dihedral=math.acos(-s5 / 3),
                    surface_area=5 * math.sqrt(3) * a * a, volume=5 * (3 + s5) / 12 * a ** 3)
    raise ValueError(f"unknown solid {solid!r}")


def platonic_metrics(solid: str, *, edge: float | None = None) -> dict[str, Any]:
    """Full metric data for a Platonic solid. `edge` rescales the canonical coordinates.

    circumradius_from_coords is computed from the actual vertices and matches the closed form.
    """
    verts = _vertices(solid)
    native_edge = _min_edge(verts)
    scale = 1.0 if edge is None else edge / native_edge
    verts = _scaled(verts, scale)
    a = native_edge * scale
    cf = _closed_form(solid, a)
    circum_from_coords = max(_dist((0, 0, 0), v) for v in verts)
    edges_from_coords = _count_edges(verts, a)
    faces = _FACE_COUNT[solid]
    euler_from_coords = len(verts) - edges_from_coords + faces   # V - E + F, E & V from geometry
    return {
        "solid": solid,
        "edge_length": a,
        "vertices": verts,
        "edge_count_from_coords": edges_from_coords,         # E derived from the coordinates
        "face_count": faces,
        "euler_from_coords": euler_from_coords,              # == 2, derived not asserted
        "circumradius": cf["circumradius"],
        "circumradius_from_coords": circum_from_coords,     # == circumradius (cross-check)
        "inradius": cf["inradius"],
        "midradius": cf["midradius"],
        "midradius_from_coords": _midradius_from_coords(verts, a),   # == midradius (cross-check)
        "dihedral_angle_radians": cf["dihedral"],
        "dihedral_angle_degrees": math.degrees(cf["dihedral"]),
        "surface_area": cf["surface_area"],
        "volume": cf["volume"],
        "uses_golden_ratio": solid in ("dodecahedron", "icosahedron"),
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }
