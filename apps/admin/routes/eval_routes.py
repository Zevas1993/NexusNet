
from fastapi import APIRouter
from pydantic import BaseModel
from benchmarks.math import gsm8k_eval
from benchmarks.reasoning import mmlu_eval
router = APIRouter(prefix="/eval", tags=["eval"])
class Body(BaseModel): model: str
@router.post("/gsm8k")
def gsm8k(body: Body): return gsm8k_eval.run(body.model, data_path="data/benchmarks/gsm8k.jsonl", limit=10)
@router.post("/mmlu")
def mmlu(body: Body): return mmlu_eval.run(body.model)
