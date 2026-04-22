from __future__ import annotations

from pathlib import Path
from typing import Iterable

from nexus.config import load_yaml_file, save_yaml_file
from nexus.schemas import MemoryRecord

from ..schemas import MemoryPlaneConfig, MemoryProjectionAdapter, MemoryProjectionView, MemorySchemaVersion


DEFAULT_STATUS_LABEL = "UNRESOLVED CONFLICT"
DEFAULT_SCHEMA_VERSION = 1
DEFAULT_MIGRATION_NOTES = [
    "8-plane memory remains the conceptual canon.",
    "11-plane MemoryNode is the configurable operational structure.",
    "3-plane episodic/semantic/temporal views remain compatibility projections, not the source model.",
    "Legacy runtime planes such as dream, curriculum, benchmark, architecture, and optimization are preserved through alias mapping.",
]


def _default_plane_payload() -> dict:
    return {
        "schema_version": DEFAULT_SCHEMA_VERSION,
        "status_label": DEFAULT_STATUS_LABEL,
        "migration_notes": DEFAULT_MIGRATION_NOTES,
        "legacy_plane_map": {
            "working": "metacognitive",
            "episodic": "temporal",
            "semantic": "conceptual",
            "procedural": "procedural",
            "benchmark": "metacognitive",
            "dream": "imaginal",
            "curriculum": "goal",
            "architecture": "metacognitive",
            "optimization": "predictive",
        },
        "planes": [
            {
                "plane_name": "conceptual",
                "conceptual_plane": "conceptual",
                "description": "Concepts, abstractions, schemas, and distilled facts.",
                "aliases": ["semantic"],
                "projection_roles": ["semantic"],
                "token_budget_ratio": 0.10,
            },
            {
                "plane_name": "temporal",
                "conceptual_plane": "temporal",
                "description": "Event ordering, episodic sequence, and time-aware recall.",
                "aliases": ["episodic"],
                "projection_roles": ["episodic", "temporal"],
                "token_budget_ratio": 0.08,
            },
            {
                "plane_name": "emotional",
                "conceptual_plane": "emotional",
                "description": "Affective signals and user-state interpretations.",
                "aliases": [],
                "projection_roles": ["episodic"],
                "token_budget_ratio": 0.05,
            },
            {
                "plane_name": "procedural",
                "conceptual_plane": "procedural",
                "description": "Reusable routines, procedures, and playbooks.",
                "aliases": ["procedural"],
                "projection_roles": ["semantic"],
                "token_budget_ratio": 0.10,
            },
            {
                "plane_name": "imaginal",
                "conceptual_plane": "imaginal",
                "description": "Dreaming, simulation, and hypothesis-space memory.",
                "aliases": ["dream"],
                "projection_roles": ["episodic", "temporal"],
                "token_budget_ratio": 0.05,
            },
            {
                "plane_name": "social",
                "conceptual_plane": "social",
                "description": "Persona, relationship, and interaction-pattern memory.",
                "aliases": [],
                "projection_roles": ["semantic"],
                "token_budget_ratio": 0.07,
            },
            {
                "plane_name": "ethical",
                "conceptual_plane": "ethical",
                "description": "Norms, policy boundaries, and governance-relevant memory.",
                "aliases": [],
                "projection_roles": ["semantic"],
                "token_budget_ratio": 0.05,
            },
            {
                "plane_name": "metacognitive",
                "conceptual_plane": "metacognitive",
                "description": "Self-monitoring, benchmark reflection, and architecture introspection.",
                "aliases": ["working", "benchmark", "architecture"],
                "projection_roles": ["semantic", "temporal"],
                "token_budget_ratio": 0.10,
            },
            {
                "plane_name": "goal",
                "conceptual_plane": "metacognitive",
                "description": "Goal state, curriculum progression, and directed intent memory.",
                "aliases": ["curriculum"],
                "projection_roles": ["semantic", "temporal"],
                "token_budget_ratio": 0.15,
            },
            {
                "plane_name": "spatial",
                "conceptual_plane": "conceptual",
                "description": "Spatial structures, environment models, and layout memory.",
                "aliases": [],
                "projection_roles": ["semantic"],
                "token_budget_ratio": 0.10,
            },
            {
                "plane_name": "predictive",
                "conceptual_plane": "metacognitive",
                "description": "Runtime optimization, forecast signals, and consequence anticipation.",
                "aliases": ["optimization"],
                "projection_roles": ["semantic", "temporal"],
                "token_budget_ratio": 0.15,
            },
        ],
    }


class MemoryPlaneRegistry:
    def __init__(self, config_dir: Path | None = None, *, config_path: Path | None = None, fallback_path: Path | None = None):
        self.path = config_path or (Path(config_dir) / "planes.yaml")
        fallback_payload = load_yaml_file(fallback_path, _default_plane_payload()) if fallback_path else _default_plane_payload()
        if not self.path.exists():
            save_yaml_file(self.path, fallback_payload)
        payload = self._normalize_payload(load_yaml_file(self.path, fallback_payload))
        self.schema = MemorySchemaVersion(
            version=int(payload.get("schema_version", DEFAULT_SCHEMA_VERSION)),
            migration_notes=list(payload.get("migration_notes", DEFAULT_MIGRATION_NOTES)),
        )
        self.status_label = payload.get("status_label", DEFAULT_STATUS_LABEL)
        self.migration_notes = payload.get("migration_notes", DEFAULT_MIGRATION_NOTES)
        self.legacy_plane_map = payload.get("legacy_plane_map", {})
        self._configs = [MemoryPlaneConfig.model_validate(item) for item in payload.get("planes", [])]
        self._by_name = {config.plane_name: config for config in self._configs}
        self._projection_adapters = [
            MemoryProjectionAdapter(
                projection_name="episodic",
                source_planes=[config.plane_name for config in self._configs if "episodic" in config.projection_roles],
                description="Compatibility projection for episodic-style retrieval over the multi-plane source model.",
            ),
            MemoryProjectionAdapter(
                projection_name="semantic",
                source_planes=[config.plane_name for config in self._configs if "semantic" in config.projection_roles],
                description="Compatibility projection for semantic abstraction over the multi-plane source model.",
            ),
            MemoryProjectionAdapter(
                projection_name="temporal",
                source_planes=[config.plane_name for config in self._configs if "temporal" in config.projection_roles],
                description="Compatibility projection for temporal sequence over the multi-plane source model.",
            ),
        ]

    def list_configs(self) -> list[MemoryPlaneConfig]:
        return list(self._configs)

    def projection_adapters(self) -> list[MemoryProjectionAdapter]:
        return list(self._projection_adapters)

    def metadata(self) -> dict:
        return {
            "status_label": self.status_label,
            "schema_version": self.schema.version,
            "migration_notes": self.migration_notes,
            "config_path": str(self.path),
            "plane_count": len(self._configs),
            "projection_names": [adapter.projection_name for adapter in self._projection_adapters],
            "legacy_plane_map": self.legacy_plane_map,
        }

    def canonical_plane_for(self, plane_name: str) -> MemoryPlaneConfig | None:
        if plane_name in self._by_name:
            return self._by_name[plane_name]
        mapped = self.legacy_plane_map.get(plane_name, plane_name)
        if mapped in self._by_name:
            return self._by_name[mapped]
        for config in self._configs:
            if plane_name in config.aliases:
                return config
        return None

    def canonical_groups(self, records: Iterable[MemoryRecord]) -> dict[str, list[dict]]:
        grouped: dict[str, list[dict]] = {config.plane_name: [] for config in self._configs}
        for record in records:
            config = self.canonical_plane_for(record.plane)
            key = config.plane_name if config else record.plane
            grouped.setdefault(key, []).append(record.model_dump(mode="json"))
        return grouped

    def project(self, projection_name: str, records: Iterable[MemoryRecord]) -> MemoryProjectionView:
        grouped: dict[str, list[dict]] = {}
        for record in records:
            config = self.canonical_plane_for(record.plane)
            if config is None or projection_name not in config.projection_roles:
                continue
            grouped.setdefault(config.plane_name, []).append(record.model_dump(mode="json"))
        return MemoryProjectionView(
            projection_name=projection_name,
            source_planes=sorted(grouped.keys()),
            grouped_records=grouped,
        )

    def migrate_record(self, record: MemoryRecord) -> MemoryRecord:
        config = self.canonical_plane_for(record.plane)
        if config is None or record.plane == config.plane_name:
            return record
        updated_tags = sorted(set(record.tags + [f"migrated-from:{record.plane}"]))
        return record.model_copy(update={"plane": config.plane_name, "tags": updated_tags})

    def _normalize_payload(self, payload: dict) -> dict:
        if not payload:
            return _default_plane_payload()
        if payload.get("schema_version") and payload.get("status_label") and payload.get("legacy_plane_map"):
            return payload

        defaults = _default_plane_payload()
        normalized_planes = []
        for item in payload.get("planes", []):
            if "plane_name" in item:
                normalized_planes.append(item)
                continue
            name = item.get("name")
            if not name:
                continue
            lookup_name = "goal" if name == "goal_intent" else name
            default = next((plane for plane in defaults["planes"] if plane["plane_name"] == lookup_name), None)
            if default is None:
                normalized_planes.append(
                    {
                        "plane_name": lookup_name,
                        "conceptual_plane": lookup_name,
                        "description": f"Normalized plane '{lookup_name}' from legacy config.",
                        "aliases": [name] if name != lookup_name else [],
                        "projection_roles": ["semantic"],
                        "token_budget_ratio": item.get("token_budget_ratio"),
                    }
                )
                continue
            merged = dict(default)
            if name != lookup_name:
                merged["aliases"] = sorted(set(default.get("aliases", []) + [name]))
            if "token_budget_ratio" in item:
                merged["token_budget_ratio"] = item["token_budget_ratio"]
            normalized_planes.append(merged)

        return {
            "schema_version": payload.get("schema_version", defaults["schema_version"]),
            "status_label": payload.get("status_label", defaults["status_label"]),
            "migration_notes": payload.get("migration_notes", defaults["migration_notes"]),
            "legacy_plane_map": payload.get("legacy_plane_map", defaults["legacy_plane_map"]),
            "planes": normalized_planes or defaults["planes"],
        }
