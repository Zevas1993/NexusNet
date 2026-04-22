from __future__ import annotations

import json
from pathlib import Path

from ...schemas import BenchmarkMatrixRecord


class QESBenchmarkMatrix:
    def __init__(self, artifacts_dir: Path):
        self.artifacts_dir = artifacts_dir

    def write(self, records: list[BenchmarkMatrixRecord]) -> str:
        destination = self.artifacts_dir / "runtime" / "qes-benchmark-matrix.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps([record.model_dump(mode="json") for record in records], indent=2),
            encoding="utf-8",
        )
        return str(destination)
