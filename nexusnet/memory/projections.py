from __future__ import annotations

from nexus.schemas import MemoryRecord

from ..schemas import MemoryProjectionAdapter, MemoryProjectionView
from .planes import MemoryPlaneRegistry


class MemoryProjectionService:
    def __init__(self, plane_registry: MemoryPlaneRegistry):
        self.plane_registry = plane_registry

    def adapters(self) -> list[MemoryProjectionAdapter]:
        return self.plane_registry.projection_adapters()

    def build(self, projection_name: str, records: list[MemoryRecord]) -> MemoryProjectionView:
        return self.plane_registry.project(projection_name, records)
