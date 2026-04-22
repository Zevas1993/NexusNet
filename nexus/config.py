from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

VERSION = "0.6.0-phase1"


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class NexusPaths:
    project_root: Path
    runtime_dir: Path
    config_dir: Path
    state_dir: Path
    artifacts_dir: Path
    logs_dir: Path
    data_dir: Path
    ui_dir: Path
    database_path: Path
    legacy_sessions_dir: Path


def build_paths(project_root: str | Path | None = None) -> NexusPaths:
    root = Path(project_root) if project_root else _project_root()
    runtime_dir = root / "runtime"
    state_dir = runtime_dir / "state"
    artifacts_dir = runtime_dir / "artifacts"
    logs_dir = runtime_dir / "logs"
    config_dir = runtime_dir / "config"
    data_dir = root / "data"
    ui_dir = root / "ui"
    database_path = state_dir / "nexus.db"
    return NexusPaths(
        project_root=root,
        runtime_dir=runtime_dir,
        config_dir=config_dir,
        state_dir=state_dir,
        artifacts_dir=artifacts_dir,
        logs_dir=logs_dir,
        data_dir=data_dir,
        ui_dir=ui_dir,
        database_path=database_path,
        legacy_sessions_dir=data_dir / "sessions",
    )


def ensure_paths(paths: NexusPaths) -> NexusPaths:
    for directory in (
        paths.runtime_dir,
        paths.config_dir,
        paths.state_dir,
        paths.artifacts_dir,
        paths.logs_dir,
        paths.data_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return paths


def load_yaml_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if data is not None else default


def save_yaml_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False)


def load_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_runtime_configs(paths: NexusPaths) -> dict[str, Any]:
    root_planes_path = paths.project_root / "config" / "planes.yaml"
    return {
        "inference": load_yaml_file(paths.config_dir / "inference.yaml", {}),
        "engines": load_yaml_file(paths.config_dir / "engines.yaml", {}),
        "experts": load_yaml_file(paths.config_dir / "experts.yaml", {}),
        "teachers": load_yaml_file(paths.config_dir / "teachers.yaml", {}),
        "router": load_yaml_file(paths.config_dir / "router.yaml", {}),
        "rag": load_yaml_file(paths.config_dir / "rag.yaml", {}),
        "retrieval": load_yaml_file(
            paths.config_dir / "retrieval.yaml",
            load_yaml_file(_project_root() / "runtime" / "config" / "retrieval.yaml", {}),
        ),
        "vision_edge": load_yaml_file(
            paths.config_dir / "vision_edge.yaml",
            load_yaml_file(_project_root() / "runtime" / "config" / "vision_edge.yaml", {}),
        ),
        "providers": load_yaml_file(paths.config_dir / "providers.yaml", {}),
        "quant_profile": load_yaml_file(paths.config_dir / "quant_profile.yaml", {}),
        "qes": load_yaml_file(paths.config_dir / "qes_policy.yaml", {}),
        "aitune": load_yaml_file(
            paths.config_dir / "aitune.yaml",
            load_yaml_file(_project_root() / "runtime" / "config" / "aitune.yaml", {}),
        ),
        "openjarvis_lane": load_yaml_file(
            paths.config_dir / "openjarvis_lane.yaml",
            load_yaml_file(_project_root() / "runtime" / "config" / "openjarvis_lane.yaml", {}),
        ),
        "goose_lane": load_yaml_file(
            paths.config_dir / "goose_lane.yaml",
            load_yaml_file(_project_root() / "runtime" / "config" / "goose_lane.yaml", {}),
        ),
        "planes": load_yaml_file(
            root_planes_path,
            load_yaml_file(
                paths.config_dir / "planes.yaml",
                load_yaml_file(_project_root() / "runtime" / "config" / "planes.yaml", {}),
            ),
        ),
        "federated": load_yaml_file(paths.config_dir / "federated.yaml", {}),
        "features": load_yaml_file(paths.config_dir / "features.yaml", {}),
        "schema_versions": load_yaml_file(paths.config_dir / "schema_versions.yaml", load_yaml_file(_project_root() / "runtime" / "config" / "schema_versions.yaml", {})),
        "settings": load_yaml_file(paths.config_dir / "settings.yaml", {}),
        "terms": load_yaml_file(paths.config_dir / "terms_of_use.yaml", {}),
        "overrides": load_user_settings(paths),
    }


def env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_user_settings(paths: NexusPaths) -> dict[str, Any]:
    home = Path.home()
    layers = [
        home / ".nexus.json",
        home / ".config" / "nexus" / "settings.json",
        paths.project_root / ".nexus.json",
        paths.project_root / ".nexus" / "settings.json",
        paths.project_root / ".nexus" / "settings.local.json",
    ]
    merged: dict[str, Any] = {}
    for layer in layers:
        merged = _deep_merge(merged, load_json_file(layer, {}))
    return merged
