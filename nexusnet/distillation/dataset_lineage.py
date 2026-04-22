from __future__ import annotations

import json
from pathlib import Path

from ..schemas import DistillationArtifactRecord


class DistillationLineageWriter:
    def __init__(self, artifacts_dir: Path):
        self.artifacts_dir = artifacts_dir

    def write(self, record: DistillationArtifactRecord) -> str:
        destination = self.artifacts_dir / "foundry" / "lineage" / f"{record.artifact_id}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(record.model_dump(mode="json"), indent=2), encoding="utf-8")
        return str(destination)
