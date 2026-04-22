from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.config import NexusPaths
from nexus.schemas import utcnow


class BrainTelemetryLogger:
    def __init__(self, paths: NexusPaths):
        self.paths = paths
        self.paths.logs_dir.mkdir(parents=True, exist_ok=True)

    def log_startup(self, payload: dict[str, Any]) -> str:
        return self._append("startup.log", payload)

    def log_model_attach(self, payload: dict[str, Any]) -> str:
        return self._append("model_load.log", payload)

    def log_inference(self, payload: dict[str, Any]) -> str:
        return self._append("inference.log", payload)

    def log_benchmark(self, payload: dict[str, Any]) -> str:
        return self._append("benchmark.log", payload)

    def _append(self, filename: str, payload: dict[str, Any]) -> str:
        destination = self.paths.logs_dir / filename
        line = {"timestamp": utcnow().isoformat(), **payload}
        with destination.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(line, ensure_ascii=True, default=str) + "\n")
        return str(destination)
