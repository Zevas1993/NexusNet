
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from ..core.config import settings, save_yaml, CONFIG_ROOT
from ..core.router import ExpertRouter

router = APIRouter()
ex_router = ExpertRouter()

class ToggleRequest(BaseModel):
    expert: str
    enabled: bool

@router.get("/experts")
def list_experts():
    cfg = settings.experts
    return cfg

@router.post("/toggle")
def toggle_expert(req: ToggleRequest):
    # Update config and persist
    ex_router.toggle_expert(req.expert, req.enabled)
    return {"ok": True, "expert": req.expert, "enabled": req.enabled}

@router.get("/config")
def get_config():
    return {
        "inference": settings.inference,
        "experts": settings.experts,
        "planes": settings.planes,
        "router": settings.router,
        "rag": settings.rag,
        "qes": settings.qes,
        "federated": settings.federated,
    }
