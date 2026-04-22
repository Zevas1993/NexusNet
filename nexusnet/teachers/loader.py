from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nexus.config import load_yaml_file

from ..schemas import TeacherAssignment, TeacherProfile
from .capability_cards import build_teacher_capability_card


@dataclass(frozen=True)
class TeacherCatalogPayload:
    schema_version: int
    status_label: str
    migration_notes: list[str]
    default_registry_layer: str
    core_mentor_ensemble: list[str]
    expert_roster: list[dict[str, Any]]
    profiles: list[TeacherProfile]
    assignments: list[TeacherAssignment]
    regimens: dict[str, Any]
    routing_policy: dict[str, Any]
    registry_layers: dict[str, Any]


class TeacherCatalogLoader:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.project_root = config_dir.parents[1]
        self.repo_root = Path(__file__).resolve().parents[2]
        self.package_dir = Path(__file__).resolve().parent
        self.path = config_dir / "teachers.yaml"
        self.fallback_path = self.repo_root / "runtime" / "config" / "teachers.yaml"

    def load(self) -> TeacherCatalogPayload:
        manifest = load_yaml_file(self.path, {})
        if not manifest:
            manifest = load_yaml_file(self.fallback_path, {})

        historical = load_yaml_file(self._resolve_registry_path(manifest, "historical"), {})
        live = load_yaml_file(self._resolve_registry_path(manifest, "live"), {})
        regimens = load_yaml_file(self._resolve_registry_path(manifest, "regimens"), {})
        routing_policy = load_yaml_file(self._resolve_registry_path(manifest, "routing_policy"), {})

        profiles = self._profiles(historical, live)
        assignments = self._assignments(historical, live, regimens)
        return TeacherCatalogPayload(
            schema_version=int(manifest.get("schema_version", 2)),
            status_label=manifest.get("status_label", "LOCKED CANON"),
            migration_notes=list(manifest.get("migration_notes", [])),
            default_registry_layer=manifest.get("default_registry_layer", live.get("registry_layer", "v2026_live")),
            core_mentor_ensemble=list(historical.get("central_brain_mentor_ensemble", {}).get("teacher_ids", [])),
            expert_roster=self._expert_roster(live),
            profiles=profiles,
            assignments=assignments,
            regimens=regimens,
            routing_policy=routing_policy,
            registry_layers={
                "historical": {
                    "registry_layer": historical.get("registry_layer", "historical"),
                    "canon_status": historical.get("canon_status", "LOCKED CANON"),
                    "path": str(self._resolve_registry_path(manifest, "historical")),
                    "central_brain_mentor_ensemble": historical.get("central_brain_mentor_ensemble", {}),
                    "historical_principles": historical.get("historical_principles", {}),
                },
                "v2026_live": {
                    "registry_layer": live.get("registry_layer", "v2026_live"),
                    "canon_status": live.get("canon_status", "LOCKED CANON"),
                    "path": str(self._resolve_registry_path(manifest, "live")),
                    "global_live_pools": live.get("global_live_pools", {}),
                    "auxiliary_paths": live.get("auxiliary_paths", {}),
                },
            },
        )

    def _resolve_registry_path(self, manifest: dict[str, Any], key: str) -> Path:
        refs = manifest.get("registry_files", {})
        ref = refs.get(key)
        if not ref:
            defaults = {
                "historical": "nexusnet/teachers/teacher_registry_historical.yaml",
                "live": "nexusnet/teachers/teacher_registry_v2026_live.yaml",
                "regimens": "nexusnet/teachers/expert_training_regimens.yaml",
                "routing_policy": "nexusnet/teachers/teacher_routing_policy.yaml",
            }
            ref = defaults[key]
        candidate = Path(ref)
        if candidate.is_absolute() and candidate.exists():
            return candidate
        candidates = [
            self.config_dir / candidate.name,
            self.project_root / ref,
            self.repo_root / ref,
            self.package_dir / candidate.name,
        ]
        for path in candidates:
            if path.exists():
                return path
        return self.package_dir / candidate.name

    def _profiles(self, historical: dict[str, Any], live: dict[str, Any]) -> list[TeacherProfile]:
        merged: dict[str, dict[str, Any]] = {}
        role_tags = self._teacher_role_tags(historical, live)

        for layer_name, payload in (("historical", historical), ("v2026_live", live)):
            for teacher_id, raw in payload.get("teacher_profiles", {}).items():
                entry = merged.setdefault(
                    teacher_id,
                    {
                        "canonical_name": raw["canonical_name"],
                        "model_hints": [],
                        "modalities": [],
                        "notes": [],
                        "reasoning_modes": [],
                        "registry_layers": [],
                        "locality": raw.get("locality"),
                    },
                )
                entry["canonical_name"] = raw["canonical_name"]
                entry["model_hints"] = _dedupe(entry["model_hints"] + list(raw.get("model_hints", [])))
                entry["modalities"] = _dedupe(entry["modalities"] + list(raw.get("modalities", [])))
                entry["reasoning_modes"] = _dedupe(entry["reasoning_modes"] + list(raw.get("reasoning_modes", [])))
                entry["notes"] = _dedupe(entry["notes"] + list(raw.get("notes", [])))
                entry["registry_layers"] = _dedupe(entry["registry_layers"] + [layer_name])
                entry["locality"] = raw.get("locality", entry.get("locality"))
                for field in ("supports_tools", "supports_structured_output", "budget_class", "risk_tier", "context_window"):
                    if raw.get(field) is not None:
                        entry[field] = raw.get(field)

        profiles = []
        for teacher_id, raw in merged.items():
            tags = role_tags.get(teacher_id, [])
            capability_card = build_teacher_capability_card(teacher_id=teacher_id, payload=raw, role_tags=tags)
            profiles.append(
                TeacherProfile(
                    teacher_id=teacher_id,
                    canonical_name=raw["canonical_name"],
                    role=tags[0] if len(tags) == 1 else ("multi-role" if tags else "core-brain"),
                    role_tags=tags,
                    lineage=self._lineage(raw["registry_layers"]),
                    status_label=self._profile_status(raw["registry_layers"]),
                    registry_layers=raw["registry_layers"],
                    model_hints=raw["model_hints"],
                    specialties=capability_card.best_for,
                    capability_card=capability_card,
                    mentor=teacher_id in historical.get("central_brain_mentor_ensemble", {}).get("teacher_ids", []),
                    arbitration_weight=1.0,
                    retirement={
                        "replacement_gate": "foundry-review",
                        "minimum_native_takeover_score": 0.85,
                        "registry_layers": raw["registry_layers"],
                    },
                    notes=raw["notes"],
                )
            )
        return sorted(profiles, key=lambda profile: profile.teacher_id)

    def _assignments(self, historical: dict[str, Any], live: dict[str, Any], regimens: dict[str, Any]) -> list[TeacherAssignment]:
        regimens_by_subject = {
            payload.get("subject"): payload for payload in regimens.get("expert_regimens", {}).values() if payload.get("subject")
        }
        assignments: list[TeacherAssignment] = []

        assignments.append(
            TeacherAssignment(
                subject="core-brain",
                subject_display_name="Core Brain Historical Mentor Ensemble",
                registry_layer="historical",
                teacher_ids=list(historical.get("central_brain_mentor_ensemble", {}).get("teacher_ids", [])),
                arbitration_policy="best-ensemble-per-role",
                routing_mode="best-ensemble-per-role",
                status_label=historical.get("canon_status", "LOCKED CANON"),
            )
        )
        for display_name, payload in historical.get("expert_role_ensembles", {}).items():
            subject = payload["subject"]
            assignments.append(
                TeacherAssignment(
                    subject=subject,
                    subject_display_name=display_name,
                    registry_layer="historical",
                    teacher_ids=list(payload.get("teacher_ids", [])),
                    arbitration_policy="best-ensemble-per-role",
                    routing_mode="best-ensemble-per-role",
                    benchmark_families=list(regimens_by_subject.get(subject, {}).get("benchmark_families", [])),
                    status_label=historical.get("canon_status", "LOCKED CANON"),
                )
            )

        live_core = live.get("live_core_brain_routing", {})
        core_pool_name = live_core.get("default_pool")
        core_pool = live.get("global_live_pools", {}).get(core_pool_name, {})
        assignments.append(
            TeacherAssignment(
                subject="core-brain",
                subject_display_name=live_core.get("subject_display_name", "NexusNet Core Brain"),
                registry_layer="v2026_live",
                teacher_ids=list(core_pool.get("teacher_ids", [])),
                arbitration_policy="live-core-brain-routing",
                routing_mode="live-primary-secondary",
                primary_teacher_id=(core_pool.get("teacher_ids") or [None])[0],
                secondary_teacher_id=(core_pool.get("teacher_ids") or [None, None])[1] if len(core_pool.get("teacher_ids", [])) > 1 else None,
                critique_arbiter_subject=live_core.get("critique_arbiter_subject"),
                locality_preference=live_core.get("locality_preference"),
                fallback_teacher_ids=list(live.get("global_live_pools", {}).get(live_core.get("low_hardware_pool"), {}).get("teacher_ids", []))
                + list(live.get("global_live_pools", {}).get(live_core.get("remote_escalation_pool"), {}).get("teacher_ids", [])),
                status_label=live_core.get("canon_status", "LOCKED CANON"),
            )
        )

        for display_name, payload in live.get("live_expert_pairs", {}).items():
            subject = payload["subject"]
            assignments.append(
                TeacherAssignment(
                    subject=subject,
                    subject_display_name=display_name,
                    registry_layer="v2026_live",
                    teacher_ids=_dedupe(
                        [
                            payload.get("primary_teacher_id"),
                            payload.get("secondary_teacher_id"),
                            payload.get("optional_efficiency_coach_id"),
                        ]
                    ),
                    arbitration_policy="live-primary-secondary",
                    routing_mode="live-primary-secondary",
                    primary_teacher_id=payload.get("primary_teacher_id"),
                    secondary_teacher_id=payload.get("secondary_teacher_id"),
                    critique_arbiter_subject=payload.get("critique_arbiter_subject"),
                    optional_efficiency_coach_id=payload.get("optional_efficiency_coach_id"),
                    locality_preference=payload.get("locality_preference"),
                    historical_anchor_ref=payload.get("historical_anchor_ref"),
                    evaluation_family=list(payload.get("evaluation_family", [])),
                    benchmark_families=list(regimens_by_subject.get(subject, {}).get("benchmark_families", [])),
                    roster_position=payload.get("roster_position"),
                    status_label=payload.get("canon_status", "LOCKED CANON"),
                )
            )

        for display_name, payload in live.get("auxiliary_paths", {}).items():
            subject = payload["subject"]
            assignments.append(
                TeacherAssignment(
                    subject=subject,
                    subject_display_name=display_name,
                    registry_layer="v2026_live",
                    teacher_ids=_dedupe(
                        [
                            payload.get("primary_teacher_id"),
                            payload.get("secondary_teacher_id"),
                            payload.get("optional_efficiency_coach_id"),
                        ]
                    ),
                    arbitration_policy="live-primary-secondary",
                    routing_mode="live-primary-secondary",
                    primary_teacher_id=payload.get("primary_teacher_id"),
                    secondary_teacher_id=payload.get("secondary_teacher_id"),
                    critique_arbiter_subject=payload.get("critique_arbiter_subject"),
                    optional_efficiency_coach_id=payload.get("optional_efficiency_coach_id"),
                    locality_preference=payload.get("locality_preference"),
                    benchmark_families=list(regimens_by_subject.get(subject, {}).get("benchmark_families", [])),
                    auxiliary=True,
                    status_label=payload.get("canon_status", "STRONG ACCEPTED DIRECTION"),
                )
            )

        return sorted(assignments, key=lambda assignment: (assignment.subject, assignment.registry_layer, assignment.subject_display_name or ""))

    def _teacher_role_tags(self, historical: dict[str, Any], live: dict[str, Any]) -> dict[str, list[str]]:
        tags: dict[str, list[str]] = {}
        for teacher_id in historical.get("central_brain_mentor_ensemble", {}).get("teacher_ids", []):
            tags.setdefault(teacher_id, []).append("core-brain")
        for payload in historical.get("expert_role_ensembles", {}).values():
            for teacher_id in payload.get("teacher_ids", []):
                tags.setdefault(teacher_id, []).append(payload["subject"])
        for pool in live.get("global_live_pools", {}).values():
            for teacher_id in pool.get("teacher_ids", []):
                tags.setdefault(teacher_id, []).append("live-pool")
        for payload in live.get("live_expert_pairs", {}).values():
            if payload.get("primary_teacher_id"):
                tags.setdefault(payload["primary_teacher_id"], []).append(payload["subject"])
            if payload.get("secondary_teacher_id"):
                tags.setdefault(payload["secondary_teacher_id"], []).append(payload["subject"])
            if payload.get("optional_efficiency_coach_id"):
                tags.setdefault(payload["optional_efficiency_coach_id"], []).append("efficiency-coach")
        for payload in live.get("auxiliary_paths", {}).values():
            if payload.get("primary_teacher_id"):
                tags.setdefault(payload["primary_teacher_id"], []).append(payload["subject"])
            if payload.get("secondary_teacher_id"):
                tags.setdefault(payload["secondary_teacher_id"], []).append(payload["subject"])
        return {teacher_id: _dedupe(values) for teacher_id, values in tags.items()}

    def _expert_roster(self, live: dict[str, Any]) -> list[dict[str, Any]]:
        roster = []
        for display_name, payload in live.get("live_expert_pairs", {}).items():
            roster.append(
                {
                    "role_id": payload["subject"],
                    "canonical_name": display_name,
                    "status_label": payload.get("canon_status", "LOCKED CANON"),
                    "roster_position": payload.get("roster_position"),
                    "auxiliary": False,
                }
            )
        for display_name, payload in live.get("auxiliary_paths", {}).items():
            roster.append(
                {
                    "role_id": payload["subject"],
                    "canonical_name": display_name,
                    "status_label": payload.get("canon_status", "STRONG ACCEPTED DIRECTION"),
                    "roster_position": None,
                    "auxiliary": True,
                }
            )
        return sorted(roster, key=lambda item: (item["auxiliary"], item["roster_position"] or 999, item["canonical_name"]))

    def _lineage(self, registry_layers: list[str]) -> str:
        if set(registry_layers) == {"historical", "v2026_live"}:
            return "Historical teacher canon preserved alongside live v2026 operational routing."
        if "historical" in registry_layers:
            return "Historical teacher canon registry."
        return "Live v2026 operational teacher registry."

    def _profile_status(self, registry_layers: list[str]) -> str:
        return "LOCKED CANON" if "historical" in registry_layers else "STRONG ACCEPTED DIRECTION"


def _dedupe(values: list[Any]) -> list[Any]:
    seen = []
    for value in values:
        if value is None or value in seen:
            continue
        seen.append(value)
    return seen
