
from fastapi import APIRouter
from pydantic import BaseModel
from apps.admin.rzero import run_many
router = APIRouter(prefix="/rzero", tags=["rzero"])
class RunBody(BaseModel):
    model: str; seeds: str = ""; experiment: str = "default"; device: str = "cpu"; iterations: int = 1
@router.post("/run_many")
def run_many_route(body: RunBody):
    return run_many(body.model, body.seeds, body.experiment, body.device, body.iterations)
