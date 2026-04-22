from __future__ import annotations

from pathlib import Path

from ..distillation.dataset_lineage import DistillationLineageWriter
from ..schemas import DistillationArtifactRecord


class FoundryRefinery:
    def __init__(self, artifacts_dir: Path):
        self.lineage_writer = DistillationLineageWriter(artifacts_dir)

    def record_distillation_artifact(
        self,
        *,
        name: str,
        artifact_path: str,
        source_kinds: list[str],
        sample_count: int,
        lineage: str,
        metadata: dict | None = None,
    ) -> DistillationArtifactRecord:
        record = DistillationArtifactRecord(
            name=name,
            artifact_path=artifact_path,
            source_kinds=source_kinds,
            sample_count=sample_count,
            lineage=lineage,
            metadata=metadata or {},
        )
        self.lineage_writer.write(record)
        return record
