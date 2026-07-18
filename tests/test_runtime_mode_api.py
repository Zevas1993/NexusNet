from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app


def test_runtime_mode_api_reads_and_updates_operator_toggle(tmp_path: Path) -> None:
    project_root = tmp_path / "workspace"
    client = TestClient(create_app(str(project_root)))

    initial = client.get("/api/runtime-packs/status")
    changed = client.put("/api/runtime-packs/mode", json={"mode": "GPU"})
    persisted = client.get("/api/runtime-packs/status")

    assert initial.status_code == 200
    assert initial.json()["mode"]["requested_mode"] == "Auto"
    assert changed.status_code == 200
    assert changed.json()["mode"]["requested_mode"] == "GPU"
    assert persisted.json()["mode"]["requested_mode"] == "GPU"
    assert set(persisted.json()) == {
        "status_label",
        "mode",
        "routes",
        "active_decision",
        "calibration",
        "circuits",
        "certification",
    }


def test_runtime_mode_api_rejects_invalid_mode_and_ui_exposes_all_four_choices(tmp_path: Path) -> None:
    project_root = tmp_path / "workspace"
    client = TestClient(create_app(str(project_root)))

    invalid = client.put("/api/runtime-packs/mode", json={"mode": "cuda"})
    html = (Path(__file__).parents[1] / "ui" / "control-panel" / "index.html").read_text(encoding="utf-8")
    javascript = (Path(__file__).parents[1] / "ui" / "control-panel" / "app.js").read_text(encoding="utf-8")

    assert invalid.status_code == 422
    assert 'id="runtimeAccelerationMode"' in html
    assert all(f'value="{mode}"' in html for mode in ("Auto", "CPU", "GPU", "Both"))
    assert "/api/runtime-packs/mode" in javascript
    assert "/api/runtime-packs/certification" in javascript


def test_runtime_pack_certification_api_is_sanitized(tmp_path: Path) -> None:
    client = TestClient(create_app(str(tmp_path / "workspace")))

    response = client.get("/api/runtime-packs/certification")

    assert response.status_code == 200
    assert set(response.json()) == {
        "route_count",
        "verified_route_count",
        "calibrated_route_count",
        "quarantined_route_count",
        "support_state",
        "blocker_codes",
    }
