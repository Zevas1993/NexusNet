from __future__ import annotations

from nexus.schemas import MemoryRecord

from ..schemas import GraphProvenanceRecord
from .planes import MemoryPlaneRegistry


class MemoryGraphBridge:
    def __init__(self, plane_registry: MemoryPlaneRegistry):
        self.plane_registry = plane_registry

    def plane_tags(self, plane_name: str | None) -> list[str]:
        if not plane_name:
            return []
        config = self.plane_registry.canonical_plane_for(plane_name)
        if config is None:
            return [plane_name]
        return sorted({config.plane_name, config.conceptual_plane, *config.aliases})

    def provenance_for_memory(self, record: MemoryRecord) -> GraphProvenanceRecord:
        return GraphProvenanceRecord(
            source="memory-bridge",
            session_id=record.session_id,
            plane_tags=self.plane_tags(record.plane),
            provenance_id=record.memory_id,
        )
