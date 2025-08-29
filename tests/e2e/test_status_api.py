
from __future__ import annotations
from fastapi.testclient import TestClient
from apps.api.main import app

def test_status():
    c = TestClient(app)
    r = c.get("/status")
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    assert "engines" in j
