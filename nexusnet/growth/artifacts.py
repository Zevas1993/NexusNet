from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


def ref_tail(ref: str) -> str:
    return ref.split(":", 1)[1] if ":" in ref else ref


def safe_name(ref: str) -> str:
    return ref_tail(ref).replace("/", "_").replace("\\", "_").replace(":", "_")


class GrowthArtifactStore:
    def __init__(self, artifacts_dir: Path | str | None = None) -> None:
        base = Path(artifacts_dir) if artifacts_dir is not None else Path("runtime") / "artifacts"
        self.root = base / "growth"
        self.cycles_dir = self.root / "cycles"
        self.registry_dir = self.root / "artifact-registry"
        self.registry_artifacts_dir = self.registry_dir / "artifacts"
        self.cycles_dir.mkdir(parents=True, exist_ok=True)
        self.registry_artifacts_dir.mkdir(parents=True, exist_ok=True)

    def cycle_dir(self, cycle_id: str) -> Path:
        path = self.cycles_dir / safe_name(cycle_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_json(self, path: Path, payload: dict[str, Any]) -> dict[str, Any]:
        path.parent.mkdir(parents=True, exist_ok=True)
        stamped = self._stamp_hash(path, payload)
        path.write_text(json.dumps(stamped, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.register_artifact(stamped, path)
        return stamped

    def write_jsonl(self, path: Path, records: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = "".join(json.dumps(record, sort_keys=True) + "\n" for record in records)
        path.write_text(text, encoding="utf-8")

    def append_jsonl(self, path: Path, record: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def write_yaml(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            import yaml

            text = yaml.safe_dump(payload, sort_keys=False)
        except Exception:
            text = json.dumps(payload, indent=2, sort_keys=True)
        path.write_text(text, encoding="utf-8")

    def register_artifact(self, payload: dict[str, Any], path: Path) -> None:
        header = payload.get("header")
        if not isinstance(header, dict):
            return
        artifact_id = header.get("artifact_id")
        if not artifact_id:
            return
        entry = {
            "schema_version": "artifact_registry_entry.v0.1",
            "artifact_id": artifact_id,
            "artifact_type": header.get("artifact_type"),
            "cycle_id": header.get("cycle_id"),
            "hash": header.get("hash"),
            "storage_path": str(path),
            "privacy_class": header.get("privacy_class"),
            "license_state": header.get("license_state"),
            "governance_state": header.get("governance_state"),
        }
        self.append_jsonl(self.registry_dir / "index.jsonl", entry)
        artifact_path = self.registry_artifacts_dir / f"{safe_name(artifact_id)}.json"
        artifact_path.write_text(json.dumps(entry, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _stamp_hash(self, path: Path, payload: dict[str, Any]) -> dict[str, Any]:
        stamped = copy.deepcopy(payload)
        header = stamped.get("header")
        if isinstance(header, dict):
            header["storage_path"] = str(path)
            header["hash"] = ""
        digest_source = copy.deepcopy(stamped)
        digest = hashlib.sha256(json.dumps(digest_source, sort_keys=True, default=str).encode("utf-8")).hexdigest()
        if isinstance(header, dict):
            header["hash"] = f"sha256:{digest}"
        return stamped
