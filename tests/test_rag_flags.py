
from fastapi.testclient import TestClient
from apps.api.main import app
def test_ingest_and_chat_rag_flag():
    c = TestClient(app)
    r = c.post("/rag/ingest", json=["NexusNet has a RAG module with AIS and temporal."])
    assert r.status_code == 200
    r2 = c.post("/chat", json={"message":"What does NexusNet's RAG do?", "rag": True})
    assert r2.status_code == 200
    j = r2.json(); assert "response" in j
