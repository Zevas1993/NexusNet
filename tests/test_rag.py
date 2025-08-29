
from app.core.rag import TemporalGraphRAG
def test_rag_ingest_query():
    rag = TemporalGraphRAG()
    rag.ingest([{"doc_id":"d1","text":"Alpha beta. Beta gamma.","timestamp":"2020-01-01 00:00:00"}])
    res = rag.query("beta", None, None, 1)
    assert len(res) >= 1
