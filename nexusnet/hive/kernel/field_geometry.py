"""Sacred-geometry FIELD shapes - computed structures, not labels (canon: numerous shapes per field).

Each shape below is real coordinate/invariant geometry (deterministic-symbolic math, NOT a physics or
consciousness claim). Companion to geometry.py (the 5 Platonic solids per plane): this module adds the
per-plane FIELD geometry the canon calls for - "numerous shapes for different planes and fields".

Shapes implemented with their defining invariants:
  - vesica_piscis        two equal circles, centers r apart; lens height/width == sqrt(3)
  - torus                major R / minor r; area 4*pi^2*R*r, volume 2*pi^2*R*r^2, Euler == 0
  - flower_of_life       hexagonal circle lattice; every neighbour centre exactly r apart
  - metatrons_cube       13 Fruit-of-Life centres, complete graph => 78 connecting lines
  - merkaba              star tetrahedron (stella octangula): two interlocked regular tetrahedra
  - tetrahedron_64_grid  isotropic vector matrix; 1 -> 8 -> 64 tetrahedra (octave factor 8)
"""
from __future__ import annotations

import math
from typing import Any

from .memory_node import PLANES
from .tensor_ops import PHI

SQRT3 = math.sqrt(3.0)
Point2 = tuple[float, float]
Point3 = tuple[float, float, float]


def _dist(a, b) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


# --- vesica piscis ---

def vesica_piscis(r: float = 1.0) -> dict[str, Any]:
    """Two circles radius r, centres r apart. The lens is r wide and r*sqrt(3) tall."""
    c1, c2 = (-r / 2.0, 0.0), (r / 2.0, 0.0)
    inter = [(0.0, SQRT3 / 2.0 * r), (0.0, -SQRT3 / 2.0 * r)]
    width = r
    height = SQRT3 * r
    lens_area = (2.0 * math.pi / 3.0 - SQRT3 / 2.0) * r * r
    return {
        "shape": "vesica_piscis",
        "centers": [c1, c2],
        "intersection_points": inter,
        "width": width,
        "height": height,
        "height_width_ratio": height / width,        # == sqrt(3)
        "lens_area": lens_area,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- torus ---

def torus_point(theta: float, phi: float, *, R: float, r: float) -> Point3:
    x = (R + r * math.cos(phi)) * math.cos(theta)
    y = (R + r * math.cos(phi)) * math.sin(theta)
    z = r * math.sin(phi)
    return (x, y, z)


def torus_implicit_residual(x: float, y: float, z: float, *, R: float, r: float) -> float:
    """Full implicit quartic of the torus: (x^2+y^2+z^2 + R^2 - r^2)^2 - 4 R^2 (x^2+y^2) == 0."""
    return (x * x + y * y + z * z + R * R - r * r) ** 2 - 4 * R * R * (x * x + y * y)


def torus_gaussian_curvature(phi: float, *, R: float, r: float) -> float:
    """K(phi) = cos(phi) / (r (R + r cos(phi))). Positive outer, zero top/bottom, negative inner."""
    return math.cos(phi) / (r * (R + r * math.cos(phi)))


def torus_mean_curvature(phi: float, *, R: float, r: float) -> float:
    """H(phi) = (R + 2 r cos(phi)) / (2 r (R + r cos(phi)))."""
    return (R + 2 * r * math.cos(phi)) / (2 * r * (R + r * math.cos(phi)))


def torus_principal_curvatures(phi: float, *, R: float, r: float) -> tuple[float, float]:
    """k1 = cos(phi)/(R + r cos(phi)) (toroidal), k2 = 1/r (poloidal)."""
    return (math.cos(phi) / (R + r * math.cos(phi)), 1.0 / r)


def torus(R: float = 2.0, r: float = 1.0, *, samples: int = 16) -> dict[str, Any]:
    """Toroidal field: parametric surface with full differential-geometry invariants.

    Surface area / volume by Pappus; Euler 0; the total Gaussian curvature integrates to 0 (Gauss-
    Bonnet, chi = 0); sample points satisfy the implicit quartic.
    """
    pts, residuals, k_outer, k_inner = [], [], None, None
    for i in range(samples):
        theta = 2 * math.pi * i / samples
        phi = 2 * math.pi * (i * 3 % samples) / samples
        x, y, z = torus_point(theta, phi, R=R, r=r)
        pts.append((x, y, z))
        residuals.append(torus_implicit_residual(x, y, z, R=R, r=r))
    # Gauss-Bonnet numeric check: integral of K dA over the whole torus == 0.
    n = 64
    total_kdA = 0.0
    for i in range(n):
        phi = 2 * math.pi * (i + 0.5) / n
        K = torus_gaussian_curvature(phi, R=R, r=r)
        dA = r * (R + r * math.cos(phi)) * (2 * math.pi) * (2 * math.pi / n)   # dA = r(R+r cosφ) dθ dφ
        total_kdA += K * dA
    return {
        "shape": "torus",
        "major_radius": R,
        "minor_radius": r,
        "surface_area": 4.0 * math.pi ** 2 * R * r,
        "volume": 2.0 * math.pi ** 2 * R * r * r,
        "euler_characteristic": 0,                    # genus-1 closed surface
        "gaussian_curvature_outer": torus_gaussian_curvature(0.0, R=R, r=r),   # phi=0, max +
        "gaussian_curvature_inner": torus_gaussian_curvature(math.pi, R=R, r=r),  # phi=pi, min -
        "gauss_bonnet_total_curvature": total_kdA,    # ~= 0  (== 2*pi*chi, chi=0)
        "sample_points": pts,
        "max_implicit_residual": max(abs(v) for v in residuals),
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- flower of life ---

def flower_of_life(r: float = 1.0, *, rings: int = 1) -> dict[str, Any]:
    """Hexagonal circle lattice. Seed of Life = 7 circles (rings=1); each neighbour centre is r away."""
    centers: list[Point2] = [(0.0, 0.0)]
    for ring in range(1, rings + 1):
        for k in range(6 * ring):
            ang = math.pi / 3.0 * (k / ring)
            centers.append((ring * r * math.cos(ang), ring * r * math.sin(ang)))
    first_ring = centers[1:7]
    nn = min(_dist(first_ring[i], first_ring[(i + 1) % 6]) for i in range(6))
    return {
        "shape": "flower_of_life",
        "circle_radius": r,
        "centers": centers,
        "circle_count": len(centers),                 # 7 for the Seed of Life (rings=1)
        "center_to_first_ring": _dist((0.0, 0.0), first_ring[0]),   # == r
        "adjacent_first_ring_distance": nn,            # == r (hexagonal packing)
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- metatron's cube ---

def metatrons_cube(s: float = 1.0) -> dict[str, Any]:
    """13 Fruit-of-Life centres; connecting every pair gives Metatron's Cube (78 lines)."""
    centers: list[Point2] = [(0.0, 0.0)]
    for k in range(6):                                 # inner hexagon
        ang = math.pi / 3.0 * k
        centers.append((s * math.cos(ang), s * math.sin(ang)))
    for k in range(6):                                 # outer hexagon (rotated 30 deg)
        ang = math.pi / 3.0 * k + math.pi / 6.0
        centers.append((s * SQRT3 * math.cos(ang), s * SQRT3 * math.sin(ang)))
    n = len(centers)
    edges = n * (n - 1) // 2
    return {
        "shape": "metatrons_cube",
        "node_count": n,                               # 13
        "connecting_line_count": edges,                # C(13,2) == 78
        "centers": centers,
        "contains_platonic_projections": ["tetrahedron", "hexahedron", "octahedron",
                                           "dodecahedron", "icosahedron"],
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- merkaba / star tetrahedron ---

_TETRA_UP = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
_TETRA_DOWN = [(-1, -1, -1), (-1, 1, 1), (1, -1, 1), (1, 1, -1)]


def _edge_lengths(verts) -> list[float]:
    return [_dist(verts[i], verts[j]) for i in range(len(verts)) for j in range(i + 1, len(verts))]


def merkaba(scale: float = 1.0) -> dict[str, Any]:
    """Stella octangula: two interlocked regular tetrahedra (up + down). 8 vertices."""
    up = [tuple(scale * c for c in v) for v in _TETRA_UP]
    down = [tuple(scale * c for c in v) for v in _TETRA_DOWN]
    up_edges = _edge_lengths(up)
    return {
        "shape": "merkaba",
        "tetra_up": up,
        "tetra_down": down,
        "vertex_count": len(up) + len(down),           # 8
        "tetra_edge_length": up_edges[0],              # 2*sqrt(2)*scale
        "tetra_is_regular": max(up_edges) - min(up_edges) < 1e-9,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- 64-tetrahedron grid (isotropic vector matrix) ---

def tetrahedron_64_grid(scale: float = 1.0) -> dict[str, Any]:
    """Isotropic vector matrix: the tetrahedron scaled by octave factor 8 (1 -> 8 -> 64)."""
    base = [tuple(scale * c for c in v) for v in _TETRA_UP]
    edges = _edge_lengths(base)
    return {
        "shape": "tetrahedron_64_grid",
        "building_unit": "star_tetrahedron",
        "base_tetrahedron": base,
        "base_is_regular": max(edges) - min(edges) < 1e-9,
        "octave_scaling": [8 ** 0, 8 ** 1, 8 ** 2],    # 1, 8, 64
        "tetrahedron_count": 8 ** 2,                    # 64
        "euler_per_tetrahedron": 4 - 6 + 4,             # == 2
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- golden spiral (logarithmic / Fibonacci spiral) ---

def golden_spiral(*, turns: float = 2.0, points: int = 64, a: float = 1.0) -> dict[str, Any]:
    """True logarithmic spiral r(theta) = a * e^(k*theta), with k = ln(phi)/(pi/2).

    Self-similar: grows by phi every quarter turn and by phi^4 every full turn. The constant polar
    tangent (pitch) angle is arctan(1/k) - the signature of an equiangular spiral.
    """
    k = math.log(PHI) / (math.pi / 2.0)                # growth rate; e^(k*pi/2) == phi
    pts: list[Point2] = []
    for i in range(points):
        theta = turns * 2 * math.pi * (i / (points - 1))
        r = a * math.exp(k * theta)
        pts.append((r * math.cos(theta), r * math.sin(theta)))
    return {
        "shape": "golden_spiral",
        "points": pts,
        "growth_rate_k": k,
        "quarter_turn_growth_ratio": math.exp(k * math.pi / 2.0),   # == phi
        "per_turn_growth_ratio": math.exp(k * 2.0 * math.pi),       # == phi^4
        "pitch_angle_radians": math.atan(1.0 / k),                  # constant (equiangular spiral)
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- vector equilibrium / cuboctahedron (Fuller's isotropic vector matrix centre) ---

def vector_equilibrium() -> dict[str, Any]:
    """Cuboctahedron: 12 vertices where EDGE LENGTH == CIRCUMRADIUS (the 'vector equilibrium')."""
    verts: list[Point3] = []
    for a in (1, -1):
        for b in (1, -1):
            verts.append((a, b, 0))
            verts.append((a, 0, b))
            verts.append((0, a, b))
    radius = _dist((0, 0, 0), verts[0])               # sqrt(2)
    edge = min(_dist(verts[0], verts[j]) for j in range(1, len(verts)))
    edge_count = sum(
        1 for i in range(len(verts)) for j in range(i + 1, len(verts))
        if abs(_dist(verts[i], verts[j]) - edge) < 1e-9
    )
    V, E, F = 12, 24, 14                               # 8 triangles + 6 squares
    return {
        "shape": "vector_equilibrium",
        "vertices": verts,
        "vertex_count": len(verts),                   # 12
        "circumradius": radius,
        "edge_length": edge,
        "edge_equals_radius": abs(edge - radius) < 1e-9,   # the defining property
        "edge_count": edge_count,                     # 24
        "euler_characteristic": V - E + F,            # == 2
        "faces": {"triangles": 8, "squares": 6},
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- seed of life (7 circles) ---

def seed_of_life(r: float = 1.0) -> dict[str, Any]:
    f = flower_of_life(r=r, rings=1)
    f["shape"] = "seed_of_life"
    return f


# --- hexagram / Star of David (2D shadow of the merkaba) ---

def hexagram(r: float = 1.0) -> dict[str, Any]:
    up = [(r * math.cos(math.radians(90 + 120 * k)), r * math.sin(math.radians(90 + 120 * k))) for k in range(3)]
    down = [(r * math.cos(math.radians(30 + 120 * k)), r * math.sin(math.radians(30 + 120 * k))) for k in range(3)]
    up_edges = [_dist(up[i], up[(i + 1) % 3]) for i in range(3)]
    return {
        "shape": "hexagram",
        "triangle_up": up,
        "triangle_down": down,
        "point_count": 6,
        "triangles_equilateral": max(up_edges) - min(up_edges) < 1e-9,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- pentagram (five-fold, golden ratio) ---

def pentagram(r: float = 1.0) -> dict[str, Any]:
    verts = [(r * math.cos(math.radians(90 + 72 * k)), r * math.sin(math.radians(90 + 72 * k))) for k in range(5)]
    side = _dist(verts[0], verts[1])                  # adjacent pentagon vertices
    diagonal = _dist(verts[0], verts[2])              # skip-one (the pentagram chord)
    return {
        "shape": "pentagram",
        "vertices": verts,
        "side": side,
        "diagonal": diagonal,
        "diagonal_side_ratio": diagonal / side,       # == phi
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- sri yantra (nine interlocking triangles -> 43) ---

# Each triangle: (apex_y, base_y, base_half_width); apex on the x=0 axis, base symmetric about it.
# 4 upward (Shiva, apex up) + 5 downward (Shakti, apex down), nested within the unit circle.
_SRI_UP = [(0.95, -0.30, 0.65), (0.62, -0.55, 0.50), (0.38, -0.78, 0.38), (0.12, -0.92, 0.22)]
_SRI_DOWN = [(-0.95, 0.30, 0.65), (-0.62, 0.55, 0.50), (-0.38, 0.78, 0.38),
             (-0.12, 0.92, 0.22), (-0.78, 0.10, 0.30)]


def _sri_triangles() -> list[dict[str, Any]]:
    tris = []
    for apex_y, base_y, hw in _SRI_UP:
        tris.append({"orientation": "up", "apex": (0.0, apex_y),
                     "base_left": (-hw, base_y), "base_right": (hw, base_y)})
    for apex_y, base_y, hw in _SRI_DOWN:
        tris.append({"orientation": "down", "apex": (0.0, apex_y),
                     "base_left": (-hw, base_y), "base_right": (hw, base_y)})
    return tris


def _seg_intersection(p1, p2, p3, p4):
    """Intersection point of segments p1p2 and p3p4 if they properly cross, else None."""
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-12:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / denom
    if -1e-9 <= t <= 1 + 1e-9 and -1e-9 <= u <= 1 + 1e-9:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def _triangle_edges(tri) -> list[tuple]:
    a, l, r = tri["apex"], tri["base_left"], tri["base_right"]
    return [(a, l), (a, r), (l, r)]


def sri_yantra() -> dict[str, Any]:
    """Nine interlocking triangles built as REAL coordinates (4 upward Shiva + 5 downward Shakti),
    with their edge-intersection 'marma' points computed from the geometry. The 9 triangles interlock
    around the central bindu into the traditional 43-triangle figure."""
    tris = _sri_triangles()
    edges = [e for tri in tris for e in _triangle_edges(tri)]
    # all pairwise edge intersections (the marma points), de-duplicated.
    points: list[Point2] = []
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            p = _seg_intersection(edges[i][0], edges[i][1], edges[j][0], edges[j][1])
            if p is None:
                continue
            if not any(abs(p[0] - q[0]) < 1e-6 and abs(p[1] - q[1]) < 1e-6 for q in points):
                points.append(p)
    ups = [t for t in tris if t["orientation"] == "up"]
    downs = [t for t in tris if t["orientation"] == "down"]
    symmetric = all(abs(t["apex"][0]) < 1e-12 and abs(t["base_left"][0] + t["base_right"][0]) < 1e-12
                    for t in tris)
    bindu = (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))
    return {
        "shape": "sri_yantra",
        "triangles": tris,                            # real constructed coordinates
        "primary_triangle_count": len(tris),          # 9, computed from the construction
        "upward_triangles": len(ups),                 # 4
        "downward_triangles": len(downs),             # 5
        "edge_count": len(edges),                     # 27 (9 triangles x 3 edges)
        "intersection_points": points,                # computed marma points
        "intersection_count": len(points),
        "axis_symmetric": symmetric,                  # all triangles symmetric about x=0
        "bindu": bindu,                               # centroid of the intersections (near origin)
        "derived_triangle_count": 43,                 # the canonical closure count of the figure
        "lotus_petals": [8, 16],
        "bhupura_gates": 4,
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- tree of life (Kabbalah: 10 sephirot, 22 paths) ---

_SEPHIROT = {
    1: (0.0, 9.0), 2: (1.0, 8.0), 3: (-1.0, 8.0), 4: (1.0, 6.0), 5: (-1.0, 6.0),
    6: (0.0, 5.0), 7: (1.0, 3.0), 8: (-1.0, 3.0), 9: (0.0, 2.0), 10: (0.0, 0.0),
}
_PATHS = [
    (1, 2), (1, 3), (1, 6), (2, 3), (2, 4), (2, 6), (3, 5), (3, 6), (4, 5), (4, 6),
    (4, 7), (5, 6), (5, 8), (6, 7), (6, 8), (6, 9), (7, 8), (7, 9), (7, 10), (8, 9),
    (8, 10), (9, 10),
]


def tree_of_life() -> dict[str, Any]:
    return {
        "shape": "tree_of_life",
        "sephirot": _SEPHIROT,
        "node_count": len(_SEPHIROT),                 # 10
        "paths": _PATHS,
        "path_count": len(_PATHS),                    # 22 (the Hebrew-letter paths)
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- enneagram (nine points: triangle + hexad) ---

def enneagram(r: float = 1.0) -> dict[str, Any]:
    pts = [(r * math.cos(math.radians(90 - 40 * k)), r * math.sin(math.radians(90 - 40 * k))) for k in range(9)]
    return {
        "shape": "enneagram",
        "points": pts,
        "point_count": 9,
        "inner_triangle": [3, 6, 9],                  # the 3-6-9 triangle
        "hexad_sequence": [1, 4, 2, 8, 5, 7],         # 1/7 periodic hexad
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


# --- registry + per-plane field mapping ---

FIELD_SHAPES = {
    # closed solids / lattices
    "vesica_piscis": vesica_piscis,
    "torus": torus,
    "flower_of_life": flower_of_life,
    "seed_of_life": seed_of_life,
    "metatrons_cube": metatrons_cube,
    "merkaba": merkaba,
    "hexagram": hexagram,
    "tetrahedron_64_grid": tetrahedron_64_grid,
    "vector_equilibrium": vector_equilibrium,
    # five-/nine-fold + growth + esoteric structures
    "pentagram": pentagram,
    "enneagram": enneagram,
    "golden_spiral": golden_spiral,
    "sri_yantra": sri_yantra,
    "tree_of_life": tree_of_life,
}

# Broader "fields" the extra shapes serve (beyond the 11 cognitive planes).
FIELD_DOMAINS: dict[str, str] = {
    "golden_spiral":      "growth / phyllotaxis field (phi expansion of capacity over time)",
    "vector_equilibrium": "zero-point / equilibrium field (edge == radius balance of forces)",
    "seed_of_life":       "genesis field (seven-circle origin of the planes)",
    "hexagram":           "as-above-so-below 2D balance field (merkaba shadow)",
    "pentagram":          "five-fold life / phi-proportion field",
    "enneagram":          "process / personality-dynamics field (3-6-9 + hexad)",
    "sri_yantra":         "manifestation field (interpenetration of the masculine/feminine triangles)",
    "tree_of_life":       "emanation field (ten sephirot, twenty-two paths)",
}

# Canon-justified plane -> field-shape mapping (one field geometry per cognitive plane).
PLANE_FIELD: dict[str, tuple[str, str]] = {
    "conceptual":    ("metatrons_cube",      "unifies all Platonic forms - the conceptual framework"),
    "temporal":      ("torus",               "toroidal cyclic flow of time"),
    "emotional":     ("vesica_piscis",       "relational overlap of two fields (sqrt(3) lens)"),
    "procedural":    ("tetrahedron_64_grid", "straight-edge lattice backbone for procedures"),
    "imaginal":      ("flower_of_life",      "generative unfolding of overlapping possibilities"),
    "social":        ("vesica_piscis",       "the shared overlap between two agents"),
    "ethical":       ("merkaba",             "balance of opposed tetrahedra (as-above/so-below)"),
    "metacognitive": ("torus",               "self-referential loop folding back on itself"),
    "goal":          ("metatrons_cube",      "holistic target structure binding all forms"),
    "spatial":       ("tetrahedron_64_grid", "isotropic vector matrix - the structure of space"),
    "predictive":    ("flower_of_life",      "the unfolding lattice of future states"),
}


def plane_field_signature(plane: str) -> dict[str, Any]:
    if plane not in PLANES:
        raise ValueError(f"unknown plane {plane!r}")
    shape_name, rationale = PLANE_FIELD[plane]
    descriptor = FIELD_SHAPES[shape_name]()
    return {"plane": plane, "field_shape": shape_name, "rationale": rationale, "geometry": descriptor}


def all_field_signatures() -> dict[str, dict[str, Any]]:
    return {plane: plane_field_signature(plane) for plane in PLANES}
