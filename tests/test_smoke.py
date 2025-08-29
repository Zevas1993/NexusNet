
from fastapi.testclient import TestClient
from apps.api.main import app

def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    j = r.json()
    assert isinstance(j, dict)
    assert j.get("ok") is True
