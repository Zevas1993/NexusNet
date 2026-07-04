from __future__ import annotations

import math

import pytest

from nexusnet.hive.kernel.platonic import platonic_metrics
from nexusnet.hive.kernel.field_geometry import (
    torus,
    torus_gaussian_curvature,
    torus_mean_curvature,
    torus_principal_curvatures,
    torus_implicit_residual,
    golden_spiral,
)

PHI = (1 + math.sqrt(5)) / 2
SOLIDS = ["tetrahedron", "hexahedron", "octahedron", "dodecahedron", "icosahedron"]
VCOUNT = {"tetrahedron": 4, "hexahedron": 8, "octahedron": 6, "dodecahedron": 20, "icosahedron": 12}
# Known exact dihedral angles (degrees).
DIHEDRAL = {
    "tetrahedron": 70.5287793655,
    "hexahedron": 90.0,
    "octahedron": 109.4712206344,
    "dodecahedron": 116.5650511771,
    "icosahedron": 138.1896851042,
}


@pytest.mark.parametrize("solid", SOLIDS)
def test_platonic_vertex_count_and_circumradius_cross_check(solid):
    m = platonic_metrics(solid)
    assert len(m["vertices"]) == VCOUNT[solid]
    # circumradius computed from the actual coordinates must equal the closed-form circumradius
    assert abs(m["circumradius"] - m["circumradius_from_coords"]) < 1e-9


@pytest.mark.parametrize("solid", SOLIDS)
def test_platonic_dihedral_angles_match_known_values(solid):
    m = platonic_metrics(solid)
    assert abs(m["dihedral_angle_degrees"] - DIHEDRAL[solid]) < 1e-6


def test_platonic_golden_ratio_used_for_icosa_and_dodeca():
    assert platonic_metrics("icosahedron")["uses_golden_ratio"] is True
    assert platonic_metrics("dodecahedron")["uses_golden_ratio"] is True
    assert platonic_metrics("cube" if False else "hexahedron")["uses_golden_ratio"] is False


def test_unit_edge_volume_matches_closed_form():
    # Regular tetrahedron with edge 1 has volume 1/(6*sqrt(2)).
    m = platonic_metrics("tetrahedron", edge=1.0)
    assert abs(m["edge_length"] - 1.0) < 1e-9
    assert abs(m["volume"] - 1.0 / (6 * math.sqrt(2))) < 1e-9
    # Unit cube.
    c = platonic_metrics("hexahedron", edge=1.0)
    assert abs(c["volume"] - 1.0) < 1e-9
    assert abs(c["surface_area"] - 6.0) < 1e-9


def test_icosahedron_circumradius_closed_form():
    # R = (a/4) * sqrt(10 + 2 sqrt5) for edge a.
    m = platonic_metrics("icosahedron", edge=2.0)
    expected = (2.0 / 4) * math.sqrt(10 + 2 * math.sqrt(5))
    assert abs(m["circumradius"] - expected) < 1e-9


# --- torus differential geometry ---

def test_torus_implicit_quartic_holds_on_surface():
    from nexusnet.hive.kernel.field_geometry import torus_point
    x, y, z = torus_point(0.9, 2.1, R=3.0, r=1.0)
    assert abs(torus_implicit_residual(x, y, z, R=3.0, r=1.0)) < 1e-9


def test_torus_gaussian_curvature_sign_pattern():
    # Outer equator (phi=0): K > 0; top (phi=pi/2): K = 0; inner (phi=pi): K < 0.
    assert torus_gaussian_curvature(0.0, R=3.0, r=1.0) > 0
    assert abs(torus_gaussian_curvature(math.pi / 2, R=3.0, r=1.0)) < 1e-12
    assert torus_gaussian_curvature(math.pi, R=3.0, r=1.0) < 0


def test_torus_gauss_bonnet_total_curvature_is_zero():
    t = torus(R=3.0, r=1.0)
    # integral of K dA over a torus == 2*pi*chi == 0
    assert abs(t["gauss_bonnet_total_curvature"]) < 1e-6
    assert t["euler_characteristic"] == 0


def test_torus_principal_and_mean_curvature_relation():
    phi, R, r = 0.7, 3.0, 1.0
    k1, k2 = torus_principal_curvatures(phi, R=R, r=r)
    H = torus_mean_curvature(phi, R=R, r=r)
    assert abs(H - 0.5 * (k1 + k2)) < 1e-9          # H = (k1 + k2)/2
    K = torus_gaussian_curvature(phi, R=R, r=r)
    assert abs(K - k1 * k2) < 1e-9                  # K = k1 * k2


# --- true logarithmic golden spiral ---

def test_golden_spiral_quarter_and_full_turn_growth():
    g = golden_spiral(turns=2.0, points=64)
    assert abs(g["quarter_turn_growth_ratio"] - PHI) < 1e-9
    assert abs(g["per_turn_growth_ratio"] - PHI ** 4) < 1e-9     # full turn => phi^4
    assert g["pitch_angle_radians"] > 0                          # equiangular spiral


# --- Euler relation and midradius DERIVED from coordinates (not asserted) ---

EDGES = {"tetrahedron": 6, "hexahedron": 12, "octahedron": 12, "dodecahedron": 30, "icosahedron": 30}


@pytest.mark.parametrize("solid", SOLIDS)
def test_edges_and_euler_derived_from_coordinates(solid):
    m = platonic_metrics(solid)
    assert m["edge_count_from_coords"] == EDGES[solid]          # E counted from the vertices
    assert m["euler_from_coords"] == 2                          # V - E + F == 2 from geometry


@pytest.mark.parametrize("solid", SOLIDS)
def test_midradius_from_coords_matches_closed_form(solid):
    m = platonic_metrics(solid)
    assert abs(m["midradius"] - m["midradius_from_coords"]) < 1e-9
