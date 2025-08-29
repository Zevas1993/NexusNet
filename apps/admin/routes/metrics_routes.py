
from fastapi import APIRouter
import os
router = APIRouter(prefix="/metrics", tags=["metrics"])
@router.get("/rzero/{experiment}")
def tail_metrics(experiment: str):
    path = f"data/rzero/metrics-{experiment}.jsonl"
    if not os.path.exists(path): return {"exists": False, "path": path}
    return {"path": path, "last": open(path, 'r', encoding='utf-8').read().splitlines()[-200:]}
