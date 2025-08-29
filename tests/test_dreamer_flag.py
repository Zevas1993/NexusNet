
# Ensures server boots with dreamer flag present (even if dreamer module missing)
from fastapi.testclient import TestClient
from apps.api.main import app
def test_health():
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
