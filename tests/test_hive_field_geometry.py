from __future__ import annotations

import math

from nexusnet.hive.kernel.field_geometry import (
    vesica_piscis,
    torus,
    torus_point,
    flower_of_life,
    metatrons_cube,
    merkaba,
    tetrahedron_64_grid,
    plane_field_signature,
    all_field_signatures,
    PLANE_FIELD,
)
from nexusnet.hive.kernel.memory_node import PLANES
from nexusnet.hive.kernel.geometry import plane_geometry_signature

SQRT3 = math.sqrt(3.0)


# --- vesica piscis: the sqrt(3) lens ---

def test_vesica_height_to_width_is_sqrt_three():
    v = vesica_piscis(r=2.0)
    assert abs(v["height_width_ratio"] - SQRT3) < 1e-9
    assert abs(v["width"] - 2.0) < 1e-9
    assert abs(v["height"] - 2.0 * SQRT3) < 1e-9
    assert len(v["intersection_points"]) == 2


# --- torus: closed-surface invariants + implicit equation ---

def test_torus_invariants_and_points_on_surface():
    t = torus(R=3.0, r=1.0, samples=12)
    assert t["euler_characteristic"] == 0
    assert abs(t["surface_area"] - 4 * math.pi ** 2 * 3.0 * 1.0) < 1e-9
    assert abs(t["volume"] - 2 * math.pi ** 2 * 3.0 * 1.0 ** 2) < 1e-9
    assert t["max_implicit_residual"] < 1e-9          # sampled points lie on the torus


def test_torus_point_satisfies_implicit_equation():
    x, y, z = torus_point(0.7, 1.3, R=3.0, r=1.0)
    residual = (math.sqrt(x * x + y * y) - 3.0) ** 2 + z * z - 1.0
    assert abs(residual) < 1e-9


# --- flower of life: hexagonal packing distances ---

def test_flower_of_life_seed_has_seven_circles_at_radius_r():
    f = flower_of_life(r=1.5, rings=1)
    assert f["circle_count"] == 7
    assert abs(f["center_to_first_ring"] - 1.5) < 1e-9
    assert abs(f["adjacent_first_ring_distance"] - 1.5) < 1e-9   # neighbours exactly r apart


# --- metatron's cube: 13 nodes, 78 lines ---

def test_metatrons_cube_thirteen_nodes_seventy_eight_lines():
    m = metatrons_cube(s=1.0)
    assert m["node_count"] == 13
    assert m["connecting_line_count"] == 78           # C(13, 2)
    assert len(m["contains_platonic_projections"]) == 5


# --- merkaba: two interlocked regular tetrahedra ---

def test_merkaba_is_two_regular_tetrahedra():
    mk = merkaba(scale=1.0)
    assert mk["vertex_count"] == 8
    assert mk["tetra_is_regular"] is True
    assert abs(mk["tetra_edge_length"] - 2 * math.sqrt(2)) < 1e-9


# --- 64-tetrahedron grid: octave scaling ---

def test_tetra_64_grid_octave_scaling():
    g = tetrahedron_64_grid()
    assert g["tetrahedron_count"] == 64
    assert g["octave_scaling"] == [1, 8, 64]
    assert g["base_is_regular"] is True
    assert g["euler_per_tetrahedron"] == 2


# --- per-plane field mapping ---

def test_every_plane_has_a_field_shape():
    sigs = all_field_signatures()
    assert set(sigs.keys()) == set(PLANES)
    for plane in PLANES:
        sig = sigs[plane]
        assert sig["field_shape"] in {
            "vesica_piscis", "torus", "flower_of_life",
            "metatrons_cube", "merkaba", "tetrahedron_64_grid",
        }
        assert sig["rationale"]                         # a canon rationale is attached
        assert "geometry" in sig


def test_all_six_field_shapes_are_used_across_planes():
    used = {PLANE_FIELD[p][0] for p in PLANES}
    assert used == {
        "vesica_piscis", "torus", "flower_of_life",
        "metatrons_cube", "merkaba", "tetrahedron_64_grid",
    }                                                   # every shape maps to at least one plane


# --- plane signature now carries BOTH the Platonic solid AND the field shape ---

def test_plane_geometry_signature_includes_solid_and_field():
    sig = plane_geometry_signature("temporal")
    assert sig["platonic_solid"] == "hexahedron"        # round-robin solid (index 1)
    assert sig["euler_characteristic"] == 2
    assert sig["field_shape"] == "torus"                # temporal -> toroidal time
    assert sig["field_geometry"]["euler_characteristic"] == 0


# ===== additional sacred-geometry shapes (computed) =====

from nexusnet.hive.kernel.field_geometry import (
    golden_spiral, vector_equilibrium, seed_of_life, hexagram, pentagram,
    sri_yantra, tree_of_life, enneagram, FIELD_SHAPES, FIELD_DOMAINS,
)

PHI = (1 + math.sqrt(5)) / 2


def test_golden_spiral_grows_by_phi_per_quarter_turn():
    g = golden_spiral(turns=3.0, points=128)
    assert abs(g["quarter_turn_growth_ratio"] - PHI) < 1e-6
    assert len(g["points"]) == 128


def test_vector_equilibrium_edge_equals_radius():
    ve = vector_equilibrium()
    assert ve["vertex_count"] == 12
    assert ve["edge_count"] == 24
    assert ve["edge_equals_radius"] is True            # the defining property of the VE
    assert abs(ve["edge_length"] - math.sqrt(2)) < 1e-9
    assert ve["euler_characteristic"] == 2


def test_seed_of_life_is_seven_circles():
    s = seed_of_life(r=1.0)
    assert s["shape"] == "seed_of_life"
    assert s["circle_count"] == 7


def test_hexagram_two_equilateral_triangles_six_points():
    h = hexagram()
    assert h["point_count"] == 6
    assert h["triangles_equilateral"] is True


def test_pentagram_diagonal_to_side_is_phi():
    p = pentagram()
    assert abs(p["diagonal_side_ratio"] - PHI) < 1e-9


def test_sri_yantra_nine_triangles_form_forty_three():
    y = sri_yantra()
    assert y["primary_triangle_count"] == 9
    assert y["upward_triangles"] + y["downward_triangles"] == 9
    assert y["derived_triangle_count"] == 43


def test_tree_of_life_ten_nodes_twenty_two_paths():
    t = tree_of_life()
    assert t["node_count"] == 10
    assert t["path_count"] == 22
    assert len(set(t["paths"])) == 22                  # no duplicate paths


def test_enneagram_nine_points_with_369_triangle():
    e = enneagram()
    assert e["point_count"] == 9
    assert e["inner_triangle"] == [3, 6, 9]


def test_registry_has_fourteen_computed_shapes_all_callable():
    assert len(FIELD_SHAPES) == 14
    for name, fn in FIELD_SHAPES.items():
        out = fn()
        assert out["shape"] == name                    # every shape is really computed
    # the extra shapes each declare the broader field they serve
    for name in ["golden_spiral", "vector_equilibrium", "sri_yantra", "tree_of_life"]:
        assert name in FIELD_DOMAINS


def test_sri_yantra_construction_is_real_geometry():
    y = sri_yantra()
    # nine triangles as actual coordinates, correct orientation split
    assert len(y["triangles"]) == 9
    assert y["upward_triangles"] == 4 and y["downward_triangles"] == 5
    assert y["edge_count"] == 27                       # 9 triangles x 3 edges
    # edge intersections (marma points) computed from the geometry, not asserted
    assert y["intersection_count"] > 50
    # the whole figure is symmetric about the vertical axis and centred on the bindu
    assert y["axis_symmetric"] is True
    assert abs(y["bindu"][0]) < 1e-6                   # bindu on the x=0 axis
    assert abs(y["bindu"][1]) < 0.2                    # near the centre
