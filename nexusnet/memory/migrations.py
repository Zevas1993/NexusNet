from __future__ import annotations

from nexus.schemas import MemoryRecord

from .planes import MemoryPlaneRegistry


class MemoryMigrationService:
    def __init__(self, plane_registry: MemoryPlaneRegistry):
        self.plane_registry = plane_registry

    def migrate_records(self, records: list[MemoryRecord]) -> list[MemoryRecord]:
        return [self.plane_registry.migrate_record(record) for record in records]

    def migration_report(self) -> dict:
        metadata = self.plane_registry.metadata()
        return {
            "status_label": "UNRESOLVED CONFLICT",
            "schema_version": metadata["schema_version"],
            "migration_notes": metadata["migration_notes"],
            "legacy_plane_map": metadata["legacy_plane_map"],
        }
