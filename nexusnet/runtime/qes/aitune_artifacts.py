from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from nexus.schemas import new_id, utcnow


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-").lower() or "artifact"


class AITuneArtifactStore:
    def __init__(self, artifacts_dir: Path):
        self.artifacts_dir = artifacts_dir

    def write_compatibility_report(self, *, model_id: str, payload: dict[str, Any]) -> str:
        return self._write(kind="compatibility", model_id=model_id, payload=payload)

    def write_benchmark_report(self, *, model_id: str, payload: dict[str, Any]) -> str:
        return self._write(kind="benchmark", model_id=model_id, payload=payload)

    def write_tuned_artifact_metadata(self, *, model_id: str, payload: dict[str, Any]) -> str:
        return self._write(kind="tuned-artifact", model_id=model_id, payload=payload)

    def write_validation_report(self, *, model_id: str, payload: dict[str, Any]) -> str:
        return self._write(kind="validation", model_id=model_id, payload=payload)

    def write_runner_report(self, *, model_id: str, payload: dict[str, Any]) -> str:
        return self._write(kind="runner", model_id=model_id, payload=payload)

    def write_health_report(self, *, model_id: str, payload: dict[str, Any]) -> str:
        return self._write(kind="health", model_id=model_id, payload=payload)

    def write_execution_plan(self, *, model_id: str, payload: dict[str, Any]) -> str:
        return self._write(kind="execution-plan", model_id=model_id, payload=payload)

    def write_execution_plan_markdown(self, *, model_id: str, markdown: str) -> str:
        relative = Path("runtime") / "aitune" / _slug(model_id) / f"{new_id('aitune-execution-plan-md')}.md"
        destination = self.artifacts_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(markdown, encoding="utf-8")
        return str(destination)

    def latest_validation_report(self, *, model_id: str | None = None) -> dict[str, Any] | None:
        return self._latest(kind="validation", model_id=model_id)

    def latest_health_report(self, *, model_id: str | None = None) -> dict[str, Any] | None:
        return self._latest(kind="health", model_id=model_id)

    def latest_execution_plan(self, *, model_id: str | None = None) -> dict[str, Any] | None:
        return self._latest(kind="execution-plan", model_id=model_id)

    def latest_benchmark_report(self, *, model_id: str | None = None) -> dict[str, Any] | None:
        return self._latest(kind="benchmark", model_id=model_id)

    def latest_tuned_artifact_metadata(self, *, model_id: str | None = None) -> dict[str, Any] | None:
        return self._latest(kind="tuned-artifact", model_id=model_id)

    def latest_runner_report(self, *, model_id: str | None = None) -> dict[str, Any] | None:
        return self._latest(kind="runner", model_id=model_id)

    def latest_execution_plan_markdown_path(self, *, model_id: str | None = None) -> str | None:
        base = self.artifacts_dir / "runtime" / "aitune"
        if not base.exists():
            return None
        pattern = "*.md" if model_id is None else str(Path(_slug(model_id)) / "*.md")
        candidates = sorted(base.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
        for candidate in candidates:
            if "execution-plan" not in candidate.name:
                continue
            return str(candidate)
        return None

    def _write(self, *, kind: str, model_id: str, payload: dict[str, Any]) -> str:
        artifact_id = new_id(f"aitune-{kind}")
        relative = Path("runtime") / "aitune" / _slug(model_id) / f"{artifact_id}.json"
        destination = self.artifacts_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        envelope = {
            "artifact_id": artifact_id,
            "artifact_kind": kind,
            "model_id": model_id,
            "created_at": utcnow().isoformat(),
            "payload": payload,
        }
        destination.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
        return str(destination)

    def _latest(self, *, kind: str, model_id: str | None = None) -> dict[str, Any] | None:
        base = self.artifacts_dir / "runtime" / "aitune"
        if not base.exists():
            return None
        pattern = "*.json" if model_id is None else str(Path(_slug(model_id)) / "*.json")
        candidates = sorted(base.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
        for candidate in candidates:
            try:
                envelope = json.loads(candidate.read_text(encoding="utf-8"))
            except Exception:
                continue
            if envelope.get("artifact_kind") != kind:
                continue
            if model_id is not None and envelope.get("model_id") != model_id:
                continue
            return {
                "artifact_id": envelope.get("artifact_id"),
                "artifact_kind": envelope.get("artifact_kind"),
                "model_id": envelope.get("model_id"),
                "path": str(candidate),
                "payload": envelope.get("payload", {}),
            }
        return None
