
from fastapi.testclient import TestClient
from apps.api.main import app
def test_expert_routing_basic():
    c = TestClient(app)
    prompt = "def add(a,b): return a+b"
    r = c.post("/chat", json={"message": prompt, "rag": False})
    assert r.status_code == 200
    j = r.json()
    assert "capsule" in j  # heuristic routes to 'code' or 'generalist'
