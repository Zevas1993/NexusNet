
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ..core.rag import TemporalGraphRAG

router = APIRouter()
graph_rag = TemporalGraphRAG()

class IngestDoc(BaseModel):
    doc_id: str
    text: str
    timestamp: Optional[str] = None
    domain: Optional[str] = "default"

class QueryRequest(BaseModel):
    query: str
    time_from: Optional[str] = None
    time_to: Optional[str] = None
    k: int = 5
    domain: Optional[str] = "default"

@router.post("/ingest")
def ingest(docs: List[IngestDoc]):
    try:
        count = graph_rag.ingest([d.dict() for d in docs])
        return {"ingested": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
def query(req: QueryRequest):
    try:
        results = graph_rag.query(req.query, req.time_from, req.time_to, req.k, domain=req.domain)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
