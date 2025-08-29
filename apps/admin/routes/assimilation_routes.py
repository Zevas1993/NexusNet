
from fastapi import APIRouter
from pydantic import BaseModel
from training.assimilation.ingest_rzero import ingest_curated
from training.assimilation.build_dataset import build
router = APIRouter(prefix="/assimilation", tags=["assimilation"])
class Ingest(BaseModel): path: str
@router.post("/ingest")
def ingest(body: Ingest):
    dst = ingest_curated(body.path); ds = build()
    return {"ingested": dst, "dataset": ds}
