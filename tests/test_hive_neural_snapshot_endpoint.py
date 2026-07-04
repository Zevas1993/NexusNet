from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_hive_neural_snapshot_endpoint_serves_gated_evidence(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))

    response = client.get("/ops/brain/canon/hive-neural-snapshot")
    assert response.status_code == 200
    payload = response.json()

    assert payload["surface_id"] == "hive-evidence-snapshot"
    assert set(payload["layers"].keys()) == {
        "neural_core", "collective", "memory", "regulation", "dreaming", "fabric"
    }
    # the connected-organism fabric is part of the live read-only evidence
    assert payload["layers"]["fabric"]["connectivity"]["fully_connected"] is True
    # Read-only / shadow guarantees must hold over the wire.
    assert payload["all_layers_shadow_gated"] is True
    assert payload["production_mutation_allowed"] is False
    assert payload["native_weight_training"] is False
    # The real forward produced a finite output and dreaming stays observe-only.
    assert payload["layers"]["neural_core"]["forward"]["output_finite"] is True
    assert payload["layers"]["dreaming"]["observe_only"] is True


def test_visualizer_wires_the_hive_neural_snapshot():
    """The canonical visualizer (not a second control plane) fetches & renders the live hive compute."""
    app_js = Path("ui/visualizer/app.js").read_text(encoding="utf-8")
    index_html = Path("ui/visualizer/index.html").read_text(encoding="utf-8")
    # it fetches the read-only endpoint
    assert "/ops/brain/canon/hive-neural-snapshot" in app_js
    # it has a dedicated loader and renders into a card element present in the DOM
    assert "async function loadHiveNeural" in app_js
    assert 'id="hiveNeuralCard"' in index_html
    # the loader is actually invoked (init flow + refresh), not dead code
    assert app_js.count("loadHiveNeural(") >= 3


def test_endpoint_serves_sacred_geometry_for_the_visualizer(tmp_path: Path):
    project_root = make_project(tmp_path)
    client = TestClient(create_app(str(project_root)))
    fab = client.get("/ops/brain/canon/hive-neural-snapshot").json()["layers"]["fabric"]
    # the fabric layer carries the data the visualizer draws (Flower-of-Life positions + Metatron chords)
    assert "node_positions" in fab and len(fab["node_positions"]) > 0
    assert "lateral_chords" in fab and len(fab["lateral_chords"]) > 0
    assert fab["sacred_geometry"]["route_geometry_signature"] == "flower-field-to-metatron-chord-sparse-selection"


def test_visualizer_renders_the_sacred_geometry():
    app_js = Path("ui/visualizer/app.js").read_text(encoding="utf-8")
    # the visualizer builds the Flower-of-Life / Metatron-chord SVG and invokes it in the hive card
    assert "function buildSacredGeometrySvg" in app_js
    assert "buildSacredGeometrySvg(snap.layers && snap.layers.fabric)" in app_js
    assert "Metatron" in app_js  # documented in the render
