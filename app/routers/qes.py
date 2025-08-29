
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..core.qes import QES, apply_qes_to_inference

router = APIRouter()
qes = QES()

class TelemetryEvent(BaseModel):
    event: str
    payload: dict

@router.post("/telemetry")
def telemetry(evt: TelemetryEvent):
    qes.record(evt.event, evt.payload)
    return {"ok": True}

@router.post("/evolve")
def evolve():
    proposal = qes.propose()
    apply_qes_to_inference(proposal)
    return {"proposal_applied": proposal}
