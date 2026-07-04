"""Real /chat usage feeds the continuous-assimilation birth loop; growth is visible via the API."""
from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from nexus.api.app import create_app
from tests.test_nexus_phase1_foundation import make_project


def test_chat_feeds_continuous_assimilation_and_growth_is_visible(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))

    # before any user chat usage, startup health learning may exist but the routed
    # chat expert has not captured this user's interaction yet.
    g0 = client.get("/ops/brain/canon/continuous-assimilation").json()
    assert g0["surface_id"] == "continuous-assimilation"
    assert "expert.coder" not in g0["nodes"]

    # a real chat turn flows through the wrapper
    r = client.post("/chat", json={"message": "def add(a, b): return a + b", "rag": False})
    assert r.status_code == 200
    body = r.json()
    expert = body.get("expert") or body.get("capsule")
    assert expert  # the turn routed to an expert

    # the conversation was assimilated into that expert node, provenance-tagged, privacy-safe
    g1 = client.get("/ops/brain/canon/continuous-assimilation").json()
    assert g1["nodes"], "chat usage did not feed the assimilation loop"
    node_key = f"expert.{expert}"
    assert node_key in g1["nodes"]
    assert g1["nodes"][node_key]["captures"] >= 1
    # provenance carries the source model name only - no raw prompt/output content anywhere
    prov = g1["provenance"][node_key]
    assert prov and "source_model" in prov[0]
    import json as _json
    assert "def add" not in _json.dumps(g1)            # privacy: no raw conversation content leaked


def test_growth_surface_is_read_only_and_privacy_safe(tmp_path: Path):
    client = TestClient(create_app(str(make_project(tmp_path))))
    for _ in range(3):
        client.post("/chat", json={"message": "explain recursion briefly", "rag": False})
    g = client.get("/ops/brain/canon/continuous-assimilation").json()
    assert g["continuous"] is True and g["mutates_production"] is False
    assert "no-raw-content" in g["claim_boundary"]
