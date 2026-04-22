from __future__ import annotations

from pydantic import BaseModel, Field


class GroundingBox(BaseModel):
    label: str
    score: float
    bbox: list[float] = Field(default_factory=list)
    normalized: bool = True


class GroundingResponse(BaseModel):
    image_id: str
    boxes: list[GroundingBox] = Field(default_factory=list)
    schema_version: str = "bbox-v1"
