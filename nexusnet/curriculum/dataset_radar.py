from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


DATASET_SOURCE_STATES = (
    "approved_train",
    "approved_teacher_context",
    "approved_eval_only",
    "sealed_eval_only",
    "pending_license_review",
    "pending_provenance_review",
    "blocked_private_or_personal",
    "blocked_anti_distillation",
    "blocked_unknown_license",
    "blocked_tos_risk",
)

DatasetSourceState = Literal[
    "approved_train",
    "approved_teacher_context",
    "approved_eval_only",
    "sealed_eval_only",
    "pending_license_review",
    "pending_provenance_review",
    "blocked_private_or_personal",
    "blocked_anti_distillation",
    "blocked_unknown_license",
    "blocked_tos_risk",
]

TRAIN_ALLOWED_STATES = {"approved_train"}
TEACHER_CONTEXT_ALLOWED_STATES = {"approved_train", "approved_teacher_context"}
EVAL_ALLOWED_STATES = {"approved_train", "approved_eval_only", "sealed_eval_only"}
SEALED_EVAL_STATES = {"sealed_eval_only"}
BLOCKED_STATES = {
    "blocked_private_or_personal",
    "blocked_anti_distillation",
    "blocked_unknown_license",
    "blocked_tos_risk",
}

FRESHNESS_CADENCE_DAYS = {
    "daily": 1,
    "weekly": 7,
    "monthly": 31,
    "quarterly": 93,
    "annual": 366,
}

DATASET_RADAR_REFRESH_PRESETS: tuple[dict[str, Any], ...] = (
    {
        "preset_id": "coder-expert",
        "label": "Coder Expert",
        "query": "open code agent dataset swe-bench stack tool use",
        "default_sort": "trendingScore",
        "target_nodes": ["Coder Expert", "Toolsmith Expert", "Execution O"],
        "student_targets": ["coder", "toolsmith", "execution"],
        "source_family": "code_agent",
        "seed_lineage_source_ids": ["the-stack-v2", "stack-edu", "codesearchnet", "context7", "swe-bench", "swe-gym"],
    },
    {
        "preset_id": "math-reasoning",
        "label": "Math Reasoning",
        "query": "open math reasoning proof dataset olympiad instruct",
        "default_sort": "trendingScore",
        "target_nodes": ["Math Expert", "Reasoning O", "Verifier Expert"],
        "student_targets": ["math", "reasoning", "verifier"],
        "source_family": "math_reasoning",
        "seed_lineage_source_ids": ["openmathreasoning", "openmathinstruct-2", "numinamath", "openr1-math", "proof-pile-2", "minif2f"],
    },
    {
        "preset_id": "research-open",
        "label": "Research Open",
        "query": "open research papers metadata arxiv openalex scientific reasoning dataset",
        "default_sort": "lastModified",
        "target_nodes": ["Research O", "Researcher Expert", "Citation Verifier"],
        "student_targets": ["research", "citation", "open-science"],
        "source_family": "science_research",
        "seed_lineage_source_ids": ["openalex", "s2orc", "semantic-scholar-metadata", "arxiv-bulk", "pmc-oa", "papers-with-code"],
    },
    {
        "preset_id": "multimodal-perception",
        "label": "Multimodal Perception",
        "query": "open vision audio video document OCR multimodal dataset",
        "default_sort": "lastModified",
        "target_nodes": ["Multimodal Perception O", "Vision Expert", "Audio Expert"],
        "student_targets": ["multimodal", "vision", "audio", "document"],
        "source_family": "multimodal_audio_video",
        "seed_lineage_source_ids": ["common-voice", "librispeech", "yodas", "relaion-5b", "datacomp-image-text", "chartqa", "docvqa"],
    },
    {
        "preset_id": "instruction-preference",
        "label": "Instruction Preference",
        "query": "open instruction preference alignment dataset helpsteer tulu smoltalk",
        "default_sort": "trendingScore",
        "target_nodes": ["Instruction AO", "Critique Expert", "Governance O"],
        "student_targets": ["instruction", "preference", "critique"],
        "source_family": "instruction_preference",
        "seed_lineage_source_ids": ["tulu-3", "oasst1", "smoltalk", "dolly-15k", "flan-v2", "helpsteer2"],
    },
    {
        "preset_id": "foundation-web",
        "label": "Foundation Web",
        "query": "open web corpus deduplicated high quality pretraining dataset",
        "default_sort": "downloads",
        "target_nodes": ["Root NexusBrain", "Memory Context O", "Language Expert"],
        "student_targets": ["foundation", "language", "memory"],
        "source_family": "foundation_web",
        "seed_lineage_source_ids": ["common-crawl", "fineweb", "fineweb-edu", "fineweb-2", "dclm", "dolma", "redpajama-v2"],
    },
    {
        "preset_id": "cybersecurity-defensive",
        "label": "Cybersecurity Defensive",
        "query": "open cybersecurity defensive vuln secure code ctf dataset",
        "default_sort": "lastModified",
        "target_nodes": ["Security Expert", "Red Team AO", "Governance O"],
        "student_targets": ["security", "red-team", "defensive-cyber"],
        "source_family": "cybersecurity_defensive",
        "seed_lineage_source_ids": ["cybersecurity-fenrir"],
    },
    {
        "preset_id": "patent-legal",
        "label": "Patent Legal",
        "query": "open patent legal public data uspto google patents dataset",
        "default_sort": "lastModified",
        "target_nodes": ["Patent Expert", "Legal Expert", "Research O"],
        "student_targets": ["patent", "legal", "researcher"],
        "source_family": "patents_legal",
        "seed_lineage_source_ids": ["google-patents-public-data", "uspto-bulk"],
    },
    {
        "preset_id": "biomedical-genomics",
        "label": "Biomedical Genomics",
        "query": "open biomedical genomics pubmed genbank dataset",
        "default_sort": "lastModified",
        "target_nodes": ["Biomedical Expert", "Genomics Expert", "Research O"],
        "student_targets": ["biomed", "genomics", "researcher"],
        "source_family": "biomedical_genomics",
        "seed_lineage_source_ids": ["pmc-open-access", "pubmed-baseline", "ncbi-genbank-complete"],
    },
    {
        "preset_id": "engineering-cad",
        "label": "Engineering CAD",
        "query": "open engineering cad geometry design dataset",
        "default_sort": "lastModified",
        "target_nodes": ["Engineering Expert", "CAD Expert", "Spatial Reasoning Expert"],
        "student_targets": ["engineering", "cad", "geometry"],
        "source_family": "engineering_cad",
        "seed_lineage_source_ids": ["zero-to-cad-1m"],
    },
)


class DatasetFreshness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tracking: Literal["last_modified", "release_page", "bulk_snapshot", "manual_review"] = "manual_review"
    last_checked: str
    cadence: str = "monthly"


class DatasetRadarSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str
    label: str
    source_family: str
    source_url: str
    license_state: DatasetSourceState
    provenance_state: str
    allowed_uses: list[str] = Field(default_factory=list)
    student_targets: list[str] = Field(default_factory=list)
    target_nodes: list[str] = Field(default_factory=list)
    quality_signals: list[str] = Field(default_factory=list)
    freshness: DatasetFreshness
    blocked_reason: str = ""
    privacy_risk: str = "unknown"


class DatasetRadar:
    def __init__(
        self,
        *,
        artifacts_dir: Path | str | None = None,
        registry_path: Path | str | None = None,
    ):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.registry_path = Path(registry_path) if registry_path else Path(__file__).with_name("dataset_source_registry.yaml")
        self.radar_dir = self.artifacts_dir / "curriculum" / "dataset-radar" if self.artifacts_dir is not None else None
        if self.radar_dir is not None:
            self.radar_dir.mkdir(parents=True, exist_ok=True)
        self._seed_sources = self._load_seed_sources()

    def list_sources(
        self,
        *,
        target_node: str | None = None,
        allowed_use: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        sources = [source.model_dump(mode="json") for source in self._seed_sources]
        if target_node:
            normalized_target = target_node.lower()
            sources = [
                source
                for source in sources
                if normalized_target in [str(target).lower() for target in source.get("target_nodes", [])]
                or normalized_target in [str(target).lower() for target in source.get("student_targets", [])]
            ]
        if allowed_use:
            sources = [source for source in sources if allowed_use in source.get("allowed_uses", [])]
        sources.sort(key=lambda source: (source.get("source_family", ""), source.get("dataset_id", "")))
        return sources[:limit] if limit else sources

    def source_for(self, dataset_id: str) -> dict[str, Any] | None:
        for source in self._seed_sources:
            if source.dataset_id == dataset_id:
                return source.model_dump(mode="json")
        return None

    def source_detail(self, dataset_id: str) -> dict[str, Any] | None:
        normalized_id = str(dataset_id or "").strip()
        canonical_source = self.source_for(normalized_id)
        candidate_source = self._candidate_for(normalized_id)
        if canonical_source is None and candidate_source is None:
            return None
        gate_preview = self.gate_preview({"dataset_id": normalized_id})
        review_history = [
            review
            for review in self._list_candidate_reviews(limit=500)
            if review.get("dataset_id") == normalized_id
        ]
        material_usage = _source_material_request_usage(
            dataset_id=normalized_id,
            material_requests=self._list_material_requests(limit=500),
        )
        latest_review = review_history[0] if review_history else None
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "living-dataset-radar",
            "dataset_id": normalized_id,
            "source_kind": gate_preview.get("source_kind"),
            "canonical_source": canonical_source,
            "candidate_source": candidate_source,
            "latest_candidate_review": latest_review,
            "candidate_review_history": review_history,
            "gate_preview": gate_preview,
            "material_request_usage": material_usage,
            "review_required_packet": _source_review_required_packet(
                dataset_id=normalized_id,
                source_kind=str(gate_preview.get("source_kind") or "unknown"),
                source=canonical_source or candidate_source or {},
                gate_preview=gate_preview,
                latest_candidate_review=latest_review,
            ),
            "training_approval_allowed": False if candidate_source else "canonical-gated-by-source-state",
            "operator_actions": {
                "candidate_review": {"method": "POST", "endpoint": "/ops/brain/dataset-radar/candidate-review"},
                "material_request": {"method": "POST", "endpoint": "/ops/brain/dataset-radar/material-request"},
                "gate_preview": {"method": "POST", "endpoint": "/ops/brain/dataset-radar/gate-preview"},
                "source_detail": {
                    "method": "GET",
                    "endpoint_template": "/ops/brain/dataset-radar/sources/{dataset_id}",
                },
            },
        }

    def summary(self, *, limit: int = 50) -> dict[str, Any]:
        sources = self.list_sources()
        state_counts = Counter(source["license_state"] for source in sources)
        family_counts = Counter(source["source_family"] for source in sources)
        candidates = self._list_candidates(limit=limit)
        refresh_history = self._list_refresh_runs(limit=limit)
        refresh_batch_history = self._list_refresh_batches(limit=limit)
        material_request_history = self._list_material_requests(limit=limit)
        candidate_review_history = self._list_candidate_reviews(limit=limit)
        freshness_rollup = _freshness_rollup(sources=sources, refresh_history=refresh_history)
        refresh_presets = self.refresh_presets()
        refresh_recommendations = _refresh_recommendations(
            due_sources=freshness_rollup["due_sources"],
            presets=refresh_presets,
        )
        coder_lineage_source_ids = ["the-stack-v2", "stack-edu", "codesearchnet", "context7", "swe-bench", "swe-gym"]
        coder_lineage_sources = [
            source
            for source in (self.source_for(source_id) for source_id in coder_lineage_source_ids)
            if source is not None
        ]
        candidate_gate_previews = [self.gate_preview({"dataset_id": candidate["dataset_id"]}) for candidate in candidates[: min(limit, 8)]]
        candidate_gate_blocked_count = sum(
            1
            for preview in candidate_gate_previews
            if preview.get("source_kind") == "candidate"
            and preview.get("gates")
            and not any(gate.get("allowed") for gate in preview.get("gates") or [])
        )
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "living-dataset-radar",
            "authority": "NexusBrain",
            "runtime_state": "degraded" if candidate_gate_blocked_count else "live-bound",
            "source_count": len(sources),
            "state_catalog": list(DATASET_SOURCE_STATES),
            "state_counts": dict(state_counts),
            "source_family_counts": dict(family_counts),
            "approved_train_count": state_counts.get("approved_train", 0),
            "blocked_count": sum(state_counts.get(state, 0) for state in BLOCKED_STATES),
            "candidate_count": len(candidates),
            "candidate_gate_blocked_count": candidate_gate_blocked_count,
            "refresh_run_count": len(refresh_history),
            "refresh_batch_count": len(refresh_batch_history),
            "material_request_count": len(material_request_history),
            "candidate_review_count": len(candidate_review_history),
            "latest_refresh_run": refresh_history[0] if refresh_history else None,
            "latest_refresh_batch": refresh_batch_history[0] if refresh_batch_history else None,
            "latest_material_request": material_request_history[0] if material_request_history else None,
            "latest_candidate_review": candidate_review_history[0] if candidate_review_history else None,
            "refresh_history": refresh_history,
            "refresh_batch_history": refresh_batch_history,
            "material_request_history": material_request_history,
            "candidate_review_history": candidate_review_history,
            "refresh_presets": refresh_presets,
            "refresh_recommendations": refresh_recommendations,
            "coder_expert_lineage_split_policy": _lineage_split_policy(coder_lineage_sources),
            "candidate_gate_previews": candidate_gate_previews,
            "latest_candidates": candidates[:limit],
            "top_sources": sources[:limit],
            "freshness_summary": freshness_rollup["summary"],
            "refresh_due_sources": freshness_rollup["due_sources"][:limit],
            "source_freshness_warnings": freshness_rollup["warnings"][:limit],
            "refresh_run_freshness": freshness_rollup["refresh_run_freshness"],
            "refresh_warning_count": freshness_rollup["warning_count"],
            "required_fields": [
                "source_url",
                "freshness",
                "license_state",
                "provenance_state",
                "allowed_uses",
                "student_targets",
                "target_nodes",
                "quality_signals",
                "blocked_reason",
            ],
            "required_gates": [
                "license_state",
                "provenance_state",
                "privacy_risk",
                "allowed_use_for_split",
                "sealed_eval_visibility",
                "synthetic_generator_rights",
            ],
            "refresh_plan": self._refresh_plan(),
            "operator_actions": {
                "inspect": {"method": "GET", "endpoint": "/ops/brain/dataset-radar"},
                "list_sources": {"method": "GET", "endpoint": "/ops/brain/dataset-radar/sources"},
                "source_detail": {
                    "method": "GET",
                    "endpoint_template": "/ops/brain/dataset-radar/sources/{dataset_id}",
                },
                "refresh": {"method": "POST", "endpoint": "/ops/brain/dataset-radar/refresh"},
                "refresh_batch": {"method": "POST", "endpoint": "/ops/brain/dataset-radar/refresh-batch"},
                "gate_preview": {"method": "POST", "endpoint": "/ops/brain/dataset-radar/gate-preview"},
                "candidate_review": {"method": "POST", "endpoint": "/ops/brain/dataset-radar/candidate-review"},
                "material_request": {"method": "POST", "endpoint": "/ops/brain/dataset-radar/material-request"},
                "list_refresh_presets": {"method": "GET", "endpoint": "/ops/brain/dataset-radar/refresh-presets"},
                "list_refresh_runs": {"method": "GET", "endpoint": "/ops/brain/dataset-radar/refresh-runs"},
                "list_refresh_batches": {"method": "GET", "endpoint": "/ops/brain/dataset-radar/refresh-batches"},
                "list_material_requests": {"method": "GET", "endpoint": "/ops/brain/dataset-radar/material-requests"},
                "list_candidate_reviews": {"method": "GET", "endpoint": "/ops/brain/dataset-radar/candidate-reviews"},
                "replay_refresh_run": {
                    "method": "GET",
                    "endpoint_template": "/ops/brain/dataset-radar/refresh-runs/{refresh_run_id}",
                },
                "replay_refresh_batch": {
                    "method": "GET",
                    "endpoint_template": "/ops/brain/dataset-radar/refresh-batches/{batch_id}",
                },
                "replay_material_request": {
                    "method": "GET",
                    "endpoint_template": "/ops/brain/dataset-radar/material-requests/{material_request_id}",
                },
                "replay_candidate_review": {
                    "method": "GET",
                    "endpoint_template": "/ops/brain/dataset-radar/candidate-reviews/{candidate_review_id}",
                },
                "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/dataset-radar"},
            },
        }

    def scorecard(self) -> dict[str, Any]:
        summary = self.summary()
        coder_lineage_source_ids = ["the-stack-v2", "stack-edu", "codesearchnet", "context7", "swe-bench", "swe-gym"]
        coder_lineage = self.lineage_for_student(
            "coder",
            source_ids=coder_lineage_source_ids,
        )
        coder_lineage_sources = [
            source
            for source in (self.source_for(source_id) for source_id in coder_lineage_source_ids)
            if source is not None
        ]
        return {
            **summary,
            "scorecard_id": "living-dataset-radar.v0.1",
            "boundary": "read-only-discover-score-gate-display-no-download-no-training",
            "teacher_access_rule": "teacher councils request material through Dataset Radar only",
            "dataset_forge_rule": "DatasetForge must validate split eligibility before manifest readiness",
            "synthetic_dataset_rule": (
                "Synthetic or teacher-generated cases must record generator model, source license, allowed "
                "distillation state, and contamination risk."
            ),
            "coder_expert_lineage": coder_lineage,
            "coder_expert_lineage_split_policy": _lineage_split_policy(coder_lineage_sources),
        }

    def refresh_runs(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return self._list_refresh_runs(limit=limit)

    def refresh_batches(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return self._list_refresh_batches(limit=limit)

    def material_requests(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return self._list_material_requests(limit=limit)

    def candidate_reviews(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return self._list_candidate_reviews(limit=limit)

    def refresh_presets(self) -> list[dict[str, Any]]:
        return [_hydrate_preset(preset, self) for preset in DATASET_RADAR_REFRESH_PRESETS]

    def refresh_preset(self, preset_id: str | None) -> dict[str, Any] | None:
        if not preset_id:
            return None
        normalized = str(preset_id).strip().lower()
        for preset in self.refresh_presets():
            if preset["preset_id"] == normalized:
                return preset
        return None

    def refresh_run(self, refresh_run_id: str) -> dict[str, Any] | None:
        if self.radar_dir is None:
            return None
        path = self.radar_dir / "refresh-runs" / f"{refresh_run_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def refresh_batch(self, batch_id: str) -> dict[str, Any] | None:
        if self.radar_dir is None:
            return None
        path = self.radar_dir / "refresh-batches" / f"{batch_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def material_request_record(self, material_request_id: str) -> dict[str, Any] | None:
        if self.radar_dir is None:
            return None
        path = self.radar_dir / "material-requests" / f"{material_request_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def candidate_review_record(self, candidate_review_id: str) -> dict[str, Any] | None:
        if self.radar_dir is None:
            return None
        path = self.radar_dir / "candidate-reviews" / f"{candidate_review_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def lineage_for_student(self, student_ref: str, *, source_ids: list[str] | None = None) -> list[dict[str, Any]]:
        normalized_student = student_ref.lower()
        sources = self.list_sources()
        if source_ids is not None:
            source_ids_set = set(source_ids)
            sources = [source for source in sources if source["dataset_id"] in source_ids_set]
        else:
            sources = [
                source
                for source in sources
                if normalized_student in [str(target).lower() for target in source.get("student_targets", [])]
                or normalized_student in [str(target).lower() for target in source.get("target_nodes", [])]
            ]
        return [
            {
                "dataset_id": source["dataset_id"],
                "label": source["label"],
                "source_url": source["source_url"],
                "license_state": source["license_state"],
                "allowed_uses": source["allowed_uses"],
                "target_nodes": source["target_nodes"],
                "blocked_reason": source.get("blocked_reason", ""),
                "freshness": source["freshness"],
            }
            for source in sources
        ]

    def validate_source_for_split(self, dataset_id: str, split: str) -> dict[str, Any]:
        source = self.source_for(dataset_id)
        if source is None:
            return {
                "source_id": dataset_id,
                "split": split,
                "allowed": False,
                "license_state": "blocked_unknown_license",
                "reason": "Dataset Radar has no canonical source entry for this dataset.",
            }
        license_state = source["license_state"]
        allowed_uses = set(source.get("allowed_uses", []))
        normalized_split = _normalize_split(split)
        state_allowed = False
        if normalized_split == "train":
            state_allowed = license_state in TRAIN_ALLOWED_STATES and "train" in allowed_uses
        elif normalized_split == "teacher_context":
            state_allowed = license_state in TEACHER_CONTEXT_ALLOWED_STATES and "teacher_context" in allowed_uses
        elif normalized_split == "teacher_free_hidden":
            state_allowed = license_state in SEALED_EVAL_STATES and "teacher_free_hidden" in allowed_uses
        elif normalized_split in {"validation", "heldout", "adversarial", "test", "regression"}:
            state_allowed = license_state in EVAL_ALLOWED_STATES and bool(
                allowed_uses.intersection({normalized_split, "validation", "heldout", "regression"})
            )
        reason = "allowed" if state_allowed else source.get("blocked_reason") or f"{license_state} is not allowed for {normalized_split}."
        return {
            "source_id": dataset_id,
            "label": source["label"],
            "source_url": source["source_url"],
            "split": normalized_split,
            "allowed": state_allowed,
            "license_state": license_state,
            "allowed_uses": sorted(allowed_uses),
            "provenance_state": source["provenance_state"],
            "privacy_risk": source.get("privacy_risk"),
            "freshness": source["freshness"],
            "reason": reason,
        }

    def gate_preview(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = payload or {}
        dataset_id = str(normalized.get("dataset_id") or normalized.get("source_id") or "").strip()
        splits = [str(split) for split in normalized.get("splits") or ["train", "teacher_context", "validation", "teacher_free_hidden"]]
        source = self.source_for(dataset_id)
        if source is not None:
            gates = [self.validate_source_for_split(dataset_id, split) for split in splits]
            return {
                "status_label": "LOCKED CANON",
                "surface_id": "living-dataset-radar",
                "dataset_id": dataset_id,
                "source_kind": "canonical_source",
                "label": source["label"],
                "source_url": source["source_url"],
                "license_state": source["license_state"],
                "provenance_state": source["provenance_state"],
                "privacy_risk": source.get("privacy_risk"),
                "auto_approval_allowed": False,
                "gates": gates,
            }
        candidate = self._candidate_for(dataset_id)
        if candidate is None:
            return {
                "status_label": "LOCKED CANON",
                "surface_id": "living-dataset-radar",
                "dataset_id": dataset_id,
                "source_kind": "unknown",
                "label": dataset_id or "unknown",
                "source_url": "",
                "license_state": "blocked_unknown_license",
                "provenance_state": "unknown",
                "privacy_risk": "unknown",
                "auto_approval_allowed": False,
                "gates": [
                    {
                        "source_id": dataset_id,
                        "split": _normalize_split(split),
                        "allowed": False,
                        "license_state": "blocked_unknown_license",
                        "reason": "Dataset Radar has no canonical source entry or candidate discovery for this dataset.",
                    }
                    for split in splits
                ],
            }
        latest_review = self._latest_candidate_review(dataset_id)
        state = str((latest_review or {}).get("applied_state") or candidate.get("license_state") or "blocked_unknown_license")
        allowed_uses = list((latest_review or {}).get("allowed_uses") or [])
        blocked_reason = str(
            (latest_review or {}).get("reason")
            or candidate.get("blocked_reason")
            or "Candidate has not passed license/provenance/privacy review."
        )
        reason_prefix = "candidate review allows limited use" if latest_review and not state.startswith("blocked_") else (
            "candidate remains blocked" if state.startswith("blocked_") else "candidate remains pending"
        )
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "living-dataset-radar",
            "dataset_id": dataset_id,
            "source_kind": "candidate",
            "label": candidate.get("label") or dataset_id,
            "source_url": candidate.get("source_url") or f"https://hf.co/datasets/{dataset_id}",
            "license_state": state,
            "provenance_state": "candidate_discovery_only",
            "privacy_risk": "unreviewed",
            "auto_approval_allowed": False,
            "latest_candidate_review": latest_review,
            "gates": [
                _candidate_gate(
                    dataset_id=dataset_id,
                    split=split,
                    state=state,
                    allowed_uses=allowed_uses,
                    freshness=candidate.get("freshness") or {},
                    reason=f"{reason_prefix}: {blocked_reason}",
                )
                for split in splits
            ],
        }

    def candidate_review(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = payload or {}
        reviewed_at = _utcnow()
        dataset_id = str(normalized.get("dataset_id") or normalized.get("source_id") or "").strip()
        requested_state = str(normalized.get("review_state") or normalized.get("state") or "pending_license_review").strip()
        if requested_state not in DATASET_SOURCE_STATES:
            requested_state = "blocked_unknown_license"
        candidate = self._candidate_for(dataset_id)
        candidate_review_id = str(
            normalized.get("candidate_review_id") or f"dataset-radar-review-{_compact_timestamp(reviewed_at)}"
        )
        if requested_state == "approved_train":
            applied_state = "pending_license_review"
            decision = "blocked_training_approval"
            applied_reason = "Candidate review cannot approve training use; DatasetForge/governance/human gates are required."
        else:
            applied_state = requested_state
            decision = "recorded"
            applied_reason = str(normalized.get("reason") or "Candidate review recorded.")
        allowed_uses = _candidate_review_allowed_uses(applied_state)
        review = {
            "status_label": "LOCKED CANON",
            "surface_id": "living-dataset-radar",
            "candidate_review_id": candidate_review_id,
            "dataset_id": dataset_id,
            "source_kind": "candidate",
            "candidate_found": candidate is not None,
            "requested_state": requested_state,
            "applied_state": applied_state,
            "decision": decision,
            "reason": applied_reason,
            "reviewer": normalized.get("reviewer") or normalized.get("operator_actor") or "unknown",
            "reviewed_at": reviewed_at,
            "allowed_uses": allowed_uses,
            "training_approval_allowed": False,
            "auto_download_allowed": False,
            "candidate_ref": (candidate or {}).get("refresh_run_id"),
            "operator_context": {
                "session_id": normalized.get("session_id"),
                "operator_actor": normalized.get("operator_actor") or normalized.get("actor") or normalized.get("reviewer") or "unknown",
                "source": normalized.get("source") or "dataset-radar-candidate-review",
            },
        }
        self._persist_candidate_review(review)
        return review

    def material_request(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = payload or {}
        requested_at = _utcnow()
        material_request_id = str(normalized.get("material_request_id") or f"dataset-radar-material-{_compact_timestamp(requested_at)}")
        target_node = str(normalized.get("target_node") or "").strip() or None
        requested_split = _normalize_split(str(normalized.get("requested_split") or normalized.get("split") or "teacher_context"))
        allowed_use = str(normalized.get("allowed_use") or requested_split).strip() or None
        limit = int(normalized.get("limit") or 12)
        sources = self.list_sources(target_node=target_node, allowed_use=allowed_use, limit=limit)
        source_gate_previews = [
            self.gate_preview({"dataset_id": source["dataset_id"], "splits": [requested_split]})
            for source in sources
        ]
        if requested_split != "train":
            known_source_ids = {preview["dataset_id"] for preview in source_gate_previews}
            for candidate in self._list_candidates(limit=500):
                dataset_id = str(candidate.get("dataset_id") or "")
                if not dataset_id or dataset_id in known_source_ids:
                    continue
                preview = self.gate_preview({"dataset_id": dataset_id, "splits": [requested_split]})
                if preview.get("gates") and preview["gates"][0].get("allowed"):
                    source_gate_previews.append(preview)
                    known_source_ids.add(dataset_id)
        approved_source_ids = [
            preview["dataset_id"]
            for preview in source_gate_previews
            if preview.get("gates") and preview["gates"][0].get("allowed")
        ]
        blocked_source_ids = [
            preview["dataset_id"]
            for preview in source_gate_previews
            if not (preview.get("gates") and preview["gates"][0].get("allowed"))
        ]
        request = {
            "status_label": "LOCKED CANON",
            "surface_id": "living-dataset-radar",
            "material_request_id": material_request_id,
            "teacher_ref": normalized.get("teacher_ref") or "teacher:unknown",
            "target_node": target_node,
            "requested_split": requested_split,
            "allowed_use": allowed_use,
            "requested_at": requested_at,
            "source_count": len(source_gate_previews),
            "approved_source_ids": approved_source_ids,
            "blocked_source_ids": blocked_source_ids,
            "source_gate_previews": source_gate_previews,
            "auto_download_allowed": False,
            "teacher_access_rule": "teacher councils request material through Dataset Radar only",
            "dataset_forge_handoff": _dataset_forge_handoff(
                material_request_id=material_request_id,
                teacher_ref=str(normalized.get("teacher_ref") or "teacher:unknown"),
                target_node=target_node,
                requested_split=requested_split,
                source_gate_previews=source_gate_previews,
            ),
            "operator_context": {
                "session_id": normalized.get("session_id"),
                "operator_actor": normalized.get("operator_actor") or normalized.get("actor") or "unknown",
                "source": normalized.get("source") or "dataset-radar-material-request",
            },
        }
        self._persist_material_request(request)
        return request

    def refresh(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = payload or {}
        preset = self.refresh_preset(normalized.get("preset_id"))
        if preset is not None:
            normalized = {
                **normalized,
                "query": normalized.get("query") or preset["query"],
                "sort": normalized.get("sort") or normalized.get("sort_by") or preset["default_sort"],
                "target_nodes": normalized.get("target_nodes") or preset["target_nodes"],
                "seed_lineage_source_ids": normalized.get("seed_lineage_source_ids") or preset["seed_lineage_source_ids"],
                "source_family": normalized.get("source_family") or preset["source_family"],
            }
        hf_results = list(normalized.get("hf_results") or [])
        fetch_error = None
        discovery_fetch_mode = "provided_results" if hf_results else "not_requested"
        if not hf_results and normalized.get("query"):
            discovery_fetch_mode = "live_huggingface_api"
            try:
                hf_results = self._fetch_huggingface_results(
                    query=str(normalized.get("query") or ""),
                    sort=str(normalized.get("sort") or normalized.get("sort_by") or "lastModified"),
                    limit=int(normalized.get("limit") or 25),
                )
            except OSError as exc:
                fetch_error = str(exc)
                discovery_fetch_mode = "live_huggingface_api_failed"
        raw_candidate_count = len(hf_results)
        discovery_filters = _discovery_filters(normalized)
        hf_results = [result for result in hf_results if _passes_discovery_filters(result, discovery_filters)]
        candidates = [self._candidate_from_hf(result, normalized) for result in hf_results]
        candidates.sort(key=lambda item: float(item.get("review_score") or 0.0), reverse=True)
        refreshed_at = _utcnow()
        refresh_run_id = f"dataset-radar-refresh-{_compact_timestamp(refreshed_at)}"
        refresh = {
            "status_label": "LOCKED CANON",
            "surface_id": "living-dataset-radar",
            "refresh_run_id": refresh_run_id,
            "batch_id": normalized.get("batch_id"),
            "discovery_source": "huggingface",
            "preset_id": preset["preset_id"] if preset else None,
            "preset": preset,
            "query": normalized.get("query"),
            "sort": normalized.get("sort") or normalized.get("sort_by"),
            "target_nodes": normalized.get("target_nodes") or [],
            "seed_lineage_source_ids": normalized.get("seed_lineage_source_ids") or [],
            "source_family": normalized.get("source_family"),
            "refreshed_at": refreshed_at,
            "candidate_count": len(candidates),
            "raw_candidate_count": raw_candidate_count,
            "filtered_out_count": max(raw_candidate_count - len(candidates), 0),
            "discovery_filters": discovery_filters,
            "fetch_error": fetch_error,
            "discovery_fetch_mode": discovery_fetch_mode,
            "auto_approval_allowed": False,
            "operator_context": {
                "session_id": normalized.get("session_id"),
                "operator_actor": normalized.get("operator_actor") or normalized.get("actor") or "unknown",
                "source": normalized.get("source") or "dataset-radar-refresh",
            },
            "candidates": candidates,
            "blocked_rule": "HF discoveries are candidates only; license/provenance/privacy gates decide use.",
        }
        for candidate in refresh["candidates"]:
            candidate["refresh_run_id"] = refresh_run_id
            candidate["batch_id"] = refresh["batch_id"]
        self._persist_refresh(refresh)
        return refresh

    def refresh_batch_run(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = payload or {}
        preset_ids = [str(preset_id).strip().lower() for preset_id in normalized.get("preset_ids") or [] if str(preset_id).strip()]
        if not preset_ids:
            preset_ids = [preset["preset_id"] for preset in self.refresh_presets()]
        refreshed_at = _utcnow()
        batch_id = str(normalized.get("batch_id") or f"dataset-radar-batch-{_compact_timestamp(refreshed_at)}")
        hf_results_by_preset = normalized.get("hf_results_by_preset") or {}
        query_by_preset = normalized.get("query_by_preset") or {}
        sort_by_preset = normalized.get("sort_by_preset") or {}
        runs: list[dict[str, Any]] = []
        for preset_id in preset_ids:
            run_payload = {
                "batch_id": batch_id,
                "session_id": normalized.get("session_id"),
                "operator_actor": normalized.get("operator_actor") or normalized.get("actor") or "unknown",
                "source": normalized.get("source") or "dataset-radar-refresh-batch",
                "preset_id": preset_id,
                "limit": normalized.get("limit"),
                "required_tags": normalized.get("required_tags"),
                "blocked_tags": normalized.get("blocked_tags"),
                "authors": normalized.get("authors"),
                "source_families": normalized.get("source_families"),
            }
            if preset_id in hf_results_by_preset:
                run_payload["hf_results"] = hf_results_by_preset[preset_id]
            if preset_id in query_by_preset:
                run_payload["query"] = query_by_preset[preset_id]
            if preset_id in sort_by_preset:
                run_payload["sort"] = sort_by_preset[preset_id]
            runs.append(self.refresh(run_payload))
        batch = {
            "status_label": "LOCKED CANON",
            "surface_id": "living-dataset-radar",
            "batch_id": batch_id,
            "refreshed_at": refreshed_at,
            "preset_ids": preset_ids,
            "preset_count": len(preset_ids),
            "refresh_run_ids": [run["refresh_run_id"] for run in runs],
            "candidate_count": sum(int(run.get("candidate_count") or 0) for run in runs),
            "operator_context": {
                "session_id": normalized.get("session_id"),
                "operator_actor": normalized.get("operator_actor") or normalized.get("actor") or "unknown",
                "source": normalized.get("source") or "dataset-radar-refresh-batch",
            },
            "auto_approval_allowed": False,
            "runs": runs,
            "blocked_rule": "Batch discoveries are candidates only; license/provenance/privacy gates decide use.",
        }
        self._persist_refresh_batch(batch)
        return batch

    def _fetch_huggingface_results(self, *, query: str, sort: str, limit: int) -> list[dict[str, Any]]:
        params = urllib.parse.urlencode({"search": query, "sort": sort, "limit": max(1, min(limit, 100)), "full": "true"})
        url = f"https://huggingface.co/api/datasets?{params}"
        request = urllib.request.Request(url, headers={"User-Agent": "NexusNet-DatasetRadar/0.1"})
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload if isinstance(payload, list) else []

    def _load_seed_sources(self) -> list[DatasetRadarSource]:
        payload = yaml.safe_load(self.registry_path.read_text(encoding="utf-8")) or {}
        return [DatasetRadarSource.model_validate(item) for item in payload.get("sources", [])]

    def _candidate_from_hf(self, result: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
        dataset_id = str(result.get("id") or result.get("dataset_id") or result.get("name") or "unknown")
        tags = [str(tag).lower() for tag in result.get("tags", []) or []]
        license_tags = [tag for tag in tags if tag.startswith("license:")]
        lowered = " ".join([dataset_id.lower(), *tags])
        if any(term in lowered for term in ("openai", "claude", "anthropic", "gemini")):
            license_state = "blocked_anti_distillation"
            blocked_reason = "Candidate mentions a blocked frontier/API teacher source."
        elif any(term in lowered for term in ("private", "personal", "chat-dump", "user-chat")):
            license_state = "blocked_private_or_personal"
            blocked_reason = "Candidate appears to contain private or personal conversation data."
        elif not license_tags:
            license_state = "blocked_unknown_license"
            blocked_reason = "No license tag was present in discovery metadata."
        else:
            license_state = "pending_provenance_review"
            blocked_reason = "License tag exists, but source card/provenance review has not approved training."
        scoring = _candidate_review_scoring(
            result=result,
            request=request,
            dataset_id=dataset_id,
            tags=tags,
            license_state=license_state,
        )
        return {
            "dataset_id": dataset_id,
            "label": str(result.get("label") or dataset_id),
            "source_family": _infer_family(tags, dataset_id),
            "source_url": f"https://hf.co/datasets/{dataset_id}",
            "discovery_source": "huggingface",
            "query": request.get("query"),
            "sort": request.get("sort") or request.get("sort_by"),
            "license_state": license_state,
            "auto_approved": False,
            "blocked_reason": blocked_reason,
            "author": result.get("author"),
            "tags": result.get("tags", []) or [],
            "quality_signals": {
                "downloads": result.get("downloads"),
                "lastModified": result.get("lastModified") or result.get("last_modified"),
                "trendingScore": result.get("trendingScore") or result.get("trending_score"),
                **scoring["quality_signals"],
            },
            "review_score": scoring["review_score"],
            "ranking_reason": "candidate-ranked-for-review-only",
            "freshness": {
                "tracking": "last_modified",
                "last_checked": _today(),
                "last_modified": result.get("lastModified") or result.get("last_modified"),
                "cadence": "manual",
            },
            "required_next_review": ["license", "provenance", "privacy", "target-node-fit"],
        }

    def _persist_refresh(self, refresh: dict[str, Any]) -> None:
        if self.radar_dir is None:
            return
        run_dir = self.radar_dir / "refresh-runs"
        run_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = run_dir / f"{refresh['refresh_run_id']}.json"
        event_log_path = self.radar_dir / "refresh_runs.jsonl"
        refresh["replay"] = {
            "artifact_ref": _project_relative_artifact_ref(self.artifacts_dir, artifact_path),
            "event_log_ref": _project_relative_artifact_ref(self.artifacts_dir, event_log_path),
            "candidate_log_ref": _project_relative_artifact_ref(self.artifacts_dir, self.radar_dir / "candidates.jsonl"),
        }
        path = self.radar_dir / "candidates.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            for candidate in refresh.get("candidates", []):
                handle.write(json.dumps({"refreshed_at": refresh["refreshed_at"], **candidate}, sort_keys=True) + "\n")
        event = {
            "refresh_run_id": refresh["refresh_run_id"],
            "batch_id": refresh.get("batch_id"),
            "surface_id": refresh["surface_id"],
            "refreshed_at": refresh["refreshed_at"],
            "query": refresh.get("query"),
            "sort": refresh.get("sort"),
            "preset_id": refresh.get("preset_id"),
            "target_nodes": refresh.get("target_nodes") or [],
            "seed_lineage_source_ids": refresh.get("seed_lineage_source_ids") or [],
            "candidate_count": refresh.get("candidate_count", 0),
            "fetch_error": refresh.get("fetch_error"),
            "auto_approval_allowed": False,
            "operator_context": refresh.get("operator_context") or {},
            "replay": refresh["replay"],
            "blocked_rule": refresh["blocked_rule"],
        }
        with event_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        artifact_path.write_text(json.dumps(refresh, indent=2, sort_keys=True), encoding="utf-8")
        latest_path = self.radar_dir / "latest_refresh.json"
        latest_path.write_text(json.dumps(refresh, indent=2, sort_keys=True), encoding="utf-8")

    def _persist_refresh_batch(self, batch: dict[str, Any]) -> None:
        if self.radar_dir is None:
            return
        batch_dir = self.radar_dir / "refresh-batches"
        batch_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = batch_dir / f"{batch['batch_id']}.json"
        event_log_path = self.radar_dir / "refresh_batches.jsonl"
        batch["replay"] = {
            "artifact_ref": _project_relative_artifact_ref(self.artifacts_dir, artifact_path),
            "event_log_ref": _project_relative_artifact_ref(self.artifacts_dir, event_log_path),
        }
        event = {
            "batch_id": batch["batch_id"],
            "surface_id": batch["surface_id"],
            "refreshed_at": batch["refreshed_at"],
            "preset_ids": batch["preset_ids"],
            "preset_count": batch["preset_count"],
            "refresh_run_ids": batch["refresh_run_ids"],
            "candidate_count": batch["candidate_count"],
            "auto_approval_allowed": False,
            "operator_context": batch.get("operator_context") or {},
            "replay": batch["replay"],
            "blocked_rule": batch["blocked_rule"],
        }
        with event_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        artifact_path.write_text(json.dumps(batch, indent=2, sort_keys=True), encoding="utf-8")
        latest_path = self.radar_dir / "latest_refresh_batch.json"
        latest_path.write_text(json.dumps(batch, indent=2, sort_keys=True), encoding="utf-8")

    def _persist_material_request(self, request: dict[str, Any]) -> None:
        if self.radar_dir is None:
            return
        request_dir = self.radar_dir / "material-requests"
        request_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = request_dir / f"{request['material_request_id']}.json"
        event_log_path = self.radar_dir / "material_requests.jsonl"
        request["replay"] = {
            "artifact_ref": _project_relative_artifact_ref(self.artifacts_dir, artifact_path),
            "event_log_ref": _project_relative_artifact_ref(self.artifacts_dir, event_log_path),
        }
        event = {
            "material_request_id": request["material_request_id"],
            "surface_id": request["surface_id"],
            "teacher_ref": request["teacher_ref"],
            "target_node": request["target_node"],
            "requested_split": request["requested_split"],
            "allowed_use": request["allowed_use"],
            "requested_at": request["requested_at"],
            "source_count": request["source_count"],
            "approved_source_ids": request["approved_source_ids"],
            "blocked_source_ids": request["blocked_source_ids"],
            "auto_download_allowed": False,
            "dataset_forge_handoff": request.get("dataset_forge_handoff") or {},
            "operator_context": request.get("operator_context") or {},
            "replay": request["replay"],
        }
        with event_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        artifact_path.write_text(json.dumps(request, indent=2, sort_keys=True), encoding="utf-8")
        latest_path = self.radar_dir / "latest_material_request.json"
        latest_path.write_text(json.dumps(request, indent=2, sort_keys=True), encoding="utf-8")

    def _persist_candidate_review(self, review: dict[str, Any]) -> None:
        if self.radar_dir is None:
            return
        review_dir = self.radar_dir / "candidate-reviews"
        review_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = review_dir / f"{review['candidate_review_id']}.json"
        event_log_path = self.radar_dir / "candidate_reviews.jsonl"
        review["replay"] = {
            "artifact_ref": _project_relative_artifact_ref(self.artifacts_dir, artifact_path),
            "event_log_ref": _project_relative_artifact_ref(self.artifacts_dir, event_log_path),
        }
        event = {
            "candidate_review_id": review["candidate_review_id"],
            "surface_id": review["surface_id"],
            "dataset_id": review["dataset_id"],
            "requested_state": review["requested_state"],
            "applied_state": review["applied_state"],
            "decision": review["decision"],
            "reviewer": review["reviewer"],
            "reviewed_at": review["reviewed_at"],
            "allowed_uses": review["allowed_uses"],
            "training_approval_allowed": False,
            "operator_context": review.get("operator_context") or {},
            "replay": review["replay"],
        }
        with event_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        artifact_path.write_text(json.dumps(review, indent=2, sort_keys=True), encoding="utf-8")
        latest_path = self.radar_dir / "latest_candidate_review.json"
        latest_path.write_text(json.dumps(review, indent=2, sort_keys=True), encoding="utf-8")

    def _list_refresh_runs(self, *, limit: int = 50) -> list[dict[str, Any]]:
        if self.radar_dir is None:
            return []
        path = self.radar_dir / "refresh_runs.jsonl"
        if not path.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        events.sort(key=lambda item: item.get("refreshed_at") or "", reverse=True)
        return events[:limit]

    def _list_refresh_batches(self, *, limit: int = 50) -> list[dict[str, Any]]:
        if self.radar_dir is None:
            return []
        path = self.radar_dir / "refresh_batches.jsonl"
        if not path.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        events.sort(key=lambda item: item.get("refreshed_at") or "", reverse=True)
        return events[:limit]

    def _list_material_requests(self, *, limit: int = 50) -> list[dict[str, Any]]:
        if self.radar_dir is None:
            return []
        path = self.radar_dir / "material_requests.jsonl"
        if not path.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        events.sort(key=lambda item: item.get("requested_at") or "", reverse=True)
        return events[:limit]

    def _list_candidate_reviews(self, *, limit: int = 50) -> list[dict[str, Any]]:
        if self.radar_dir is None:
            return []
        path = self.radar_dir / "candidate_reviews.jsonl"
        if not path.exists():
            return []
        events: list[dict[str, Any]] = []
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                event["_event_index"] = index
                events.append(event)
            except json.JSONDecodeError:
                continue
        events.sort(key=lambda item: (item.get("reviewed_at") or "", int(item.get("_event_index") or 0)), reverse=True)
        selected = events[:limit]
        for event in selected:
            event.pop("_event_index", None)
        return selected

    def _list_candidates(self, *, limit: int = 50) -> list[dict[str, Any]]:
        if self.radar_dir is None:
            return []
        path = self.radar_dir / "candidates.jsonl"
        if not path.exists():
            return []
        candidates: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                candidates.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        candidates.sort(
            key=lambda item: (
                float(item.get("review_score") or 0.0),
                str(item.get("refreshed_at") or ""),
            ),
            reverse=True,
        )
        return candidates[:limit]

    def _candidate_for(self, dataset_id: str) -> dict[str, Any] | None:
        if not dataset_id:
            return None
        normalized = dataset_id.strip().lower()
        for candidate in self._list_candidates(limit=500):
            if str(candidate.get("dataset_id") or "").strip().lower() == normalized:
                return candidate
        return None

    def _latest_candidate_review(self, dataset_id: str) -> dict[str, Any] | None:
        if not dataset_id:
            return None
        normalized = dataset_id.strip().lower()
        for review in self._list_candidate_reviews(limit=500):
            if str(review.get("dataset_id") or "").strip().lower() == normalized:
                return review
        return None

    def _refresh_plan(self) -> dict[str, Any]:
        return {
            "huggingface": {
                "sorts": ["trendingScore", "lastModified", "downloads"],
                "tracked_filters": ["tags", "authors", "source families", "target nodes"],
                "approval_policy": "discoveries_never_auto_approve",
            },
            "official_non_hf": [
                "Common Crawl",
                "Software Heritage",
                "OpenAlex",
                "PMC Open Access",
                "arXiv bulk",
                "Google Patents",
                "Wikimedia",
                "Stack Exchange",
                "GitHub Archive",
                "DataComp",
                "LAION/Re-LAION",
            ],
        }


def _source_material_request_usage(*, dataset_id: str, material_requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    usages: list[dict[str, Any]] = []
    for request in material_requests:
        approved = dataset_id in set(request.get("approved_source_ids") or [])
        blocked = dataset_id in set(request.get("blocked_source_ids") or [])
        if not approved and not blocked:
            continue
        usages.append(
            {
                "material_request_id": request.get("material_request_id"),
                "teacher_ref": request.get("teacher_ref"),
                "target_node": request.get("target_node"),
                "requested_split": request.get("requested_split"),
                "allowed_use": request.get("allowed_use"),
                "usage_state": "approved" if approved else "blocked",
                "replay": request.get("replay") or {},
                "dataset_forge_handoff": request.get("dataset_forge_handoff") or {},
            }
        )
    return usages


def _source_review_required_packet(
    *,
    dataset_id: str,
    source_kind: str,
    source: dict[str, Any],
    gate_preview: dict[str, Any],
    latest_candidate_review: dict[str, Any] | None,
) -> dict[str, Any]:
    license_state = str(gate_preview.get("license_state") or source.get("license_state") or "blocked_unknown_license")
    provenance_state = str(gate_preview.get("provenance_state") or source.get("provenance_state") or "unknown")
    privacy_risk = str(gate_preview.get("privacy_risk") or source.get("privacy_risk") or "unknown")
    gates = gate_preview.get("gates") or []
    train_gate = next((gate for gate in gates if gate.get("split") == "train"), {})
    teacher_gate = next((gate for gate in gates if gate.get("split") == "teacher_context"), {})
    validation_gate = next((gate for gate in gates if gate.get("split") == "validation"), {})
    candidate_training_blocked = source_kind == "candidate"
    license_status = _review_status_for_license(license_state)
    provenance_status = _review_status_for_provenance(provenance_state)
    privacy_status = _review_status_for_privacy(privacy_risk, license_state)
    attribution_status = _review_status_for_attribution(source)
    pre_training_blocking_fields = [
        field
        for field, status in {
            "license_evidence": license_status,
            "provenance_evidence": provenance_status,
            "privacy_evidence": privacy_status,
            "attribution_evidence": attribution_status,
        }.items()
        if status in {"required", "blocked"}
    ]
    training_promotion_allowed = bool(train_gate.get("allowed")) and not candidate_training_blocked and not pre_training_blocking_fields
    training_status = "satisfied" if training_promotion_allowed else ("blocked" if candidate_training_blocked else "required")
    fields = [
        _review_field(
            field="license_evidence",
            status=license_status,
            current_value=license_state,
            reason=_review_reason_for_license(license_state),
            accepted_evidence=[
                "license file or source card URL",
                "allowed training/distillation terms",
                "dataset version or commit hash",
            ],
        ),
        _review_field(
            field="provenance_evidence",
            status=provenance_status,
            current_value=provenance_state,
            reason=_review_reason_for_provenance(provenance_state),
            accepted_evidence=[
                "official source card or project page",
                "source lineage and generation method",
                "deduplication/contamination notes when available",
            ],
        ),
        _review_field(
            field="privacy_evidence",
            status=privacy_status,
            current_value=privacy_risk,
            reason=_review_reason_for_privacy(privacy_risk, license_state),
            accepted_evidence=[
                "PII/user-content risk assessment",
                "redaction or consent policy",
                "domain policy gate for biomedical/legal/security sources",
            ],
        ),
        _review_field(
            field="attribution_evidence",
            status=attribution_status,
            current_value=source.get("source_url") or gate_preview.get("source_url") or "",
            reason=_review_reason_for_attribution(source),
            accepted_evidence=[
                "source URL",
                "citation/attribution requirement",
                "redistribution notice when required",
            ],
        ),
        _review_field(
            field="training_eligibility",
            status=training_status,
            current_value=train_gate.get("reason") or "no train gate found",
            reason=(
                "Candidate discoveries cannot be promoted to training directly from review."
                if candidate_training_blocked
                else (
                    "Required review evidence must be satisfied before training promotion."
                    if pre_training_blocking_fields
                    else train_gate.get("reason") or "Training gate has not passed."
                )
            ),
            accepted_evidence=[
                "approved_train license state",
                "train split allowed by Dataset Radar gate",
                "operator/human approval before downstream training execution",
            ],
        ),
    ]
    blocking_fields = [
        field["field"]
        for field in fields
        if field["status"] in {"required", "blocked"}
    ]
    return {
        "packet_id": f"review-required:{dataset_id}",
        "dataset_id": dataset_id,
        "source_kind": source_kind,
        "review_state": "complete" if not blocking_fields else "review_required",
        "latest_candidate_review_id": (latest_candidate_review or {}).get("candidate_review_id"),
        "training_promotion_allowed": training_promotion_allowed,
        "teacher_context_allowed": bool(teacher_gate.get("allowed")),
        "validation_allowed": bool(validation_gate.get("allowed")),
        "blocking_fields": blocking_fields,
        "fields": fields,
        "next_operator_action": (
            "source is eligible for training material only after downstream DatasetForge/eval gates"
            if training_promotion_allowed
            else "collect missing evidence, keep source restricted to allowed non-training splits, then rerun candidate/source review"
        ),
    }


def _review_field(
    *,
    field: str,
    status: str,
    current_value: Any,
    reason: str,
    accepted_evidence: list[str],
) -> dict[str, Any]:
    return {
        "field": field,
        "status": status,
        "current_value": current_value,
        "reason": reason,
        "accepted_evidence": accepted_evidence,
    }


def _review_status_for_license(license_state: str) -> str:
    if license_state == "approved_train":
        return "satisfied"
    if license_state in {"approved_teacher_context", "approved_eval_only", "sealed_eval_only"}:
        return "required"
    if license_state.startswith("blocked_"):
        return "blocked"
    return "required"


def _review_reason_for_license(license_state: str) -> str:
    if license_state == "approved_train":
        return "License state allows training after Dataset Radar and DatasetForge gates pass."
    if license_state in {"approved_teacher_context", "approved_eval_only", "sealed_eval_only"}:
        return f"{license_state} is not a training approval."
    if license_state.startswith("blocked_"):
        return f"{license_state} blocks training and may block all material use."
    return "License remains pending and cannot enter training."


def _review_status_for_provenance(provenance_state: str) -> str:
    normalized = provenance_state.lower()
    if any(token in normalized for token in ("source_card_available", "official", "open_policy", "official_dump")):
        return "satisfied"
    if any(token in normalized for token in ("ambiguous", "unknown", "candidate_discovery_only", "needs_exact", "pending")):
        return "required"
    return "required"


def _review_reason_for_provenance(provenance_state: str) -> str:
    if _review_status_for_provenance(provenance_state) == "satisfied":
        return "Provenance has an official or source-card-backed reference."
    return "Provenance must be pinned before promotion beyond the currently allowed split."


def _review_status_for_privacy(privacy_risk: str, license_state: str) -> str:
    normalized = privacy_risk.lower()
    if license_state == "blocked_private_or_personal" or "high" in normalized or "private" in normalized or "personal" in normalized:
        return "blocked"
    if normalized in {"low", "low_with_attribution", "eval_contamination_risk"}:
        return "satisfied"
    if "review" in normalized or "risk" in normalized or normalized in {"unknown", "unreviewed"}:
        return "required"
    return "required"


def _review_reason_for_privacy(privacy_risk: str, license_state: str) -> str:
    status = _review_status_for_privacy(privacy_risk, license_state)
    if status == "satisfied":
        return "Privacy risk is low or bounded to eval contamination controls."
    if status == "blocked":
        return "Privacy risk blocks training until legal/privacy review explicitly clears use."
    return "Privacy and personal-data review is required before broader use."


def _review_status_for_attribution(source: dict[str, Any]) -> str:
    source_url = str(source.get("source_url") or "")
    privacy_risk = str(source.get("privacy_risk") or "").lower()
    quality_signals = " ".join(str(value).lower() for value in source.get("quality_signals") or [])
    if not source_url:
        return "required"
    if "attribution" in privacy_risk or "attribution" in quality_signals:
        return "required"
    return "satisfied"


def _review_reason_for_attribution(source: dict[str, Any]) -> str:
    if _review_status_for_attribution(source) == "satisfied":
        return "Source URL exists and no explicit attribution flag is present."
    return "Attribution terms or source URL must be recorded before promotion."


def _dataset_forge_handoff(
    *,
    material_request_id: str,
    teacher_ref: str,
    target_node: str | None,
    requested_split: str,
    source_gate_previews: list[dict[str, Any]],
) -> dict[str, Any]:
    approved_previews = [
        preview
        for preview in source_gate_previews
        if preview.get("gates") and any(gate.get("allowed") for gate in preview.get("gates") or [])
    ]
    sources = [
        _dataset_forge_source_template(
            preview=preview,
            material_request_id=material_request_id,
            requested_split=requested_split,
        )
        for preview in approved_previews
    ]
    return {
        "method": "POST",
        "endpoint": "/ops/brain/dataset-forge/manifests",
        "auto_execute_allowed": False,
        "build_allowed": False,
        "handoff_rule": "operator-reviewed excerpts are required before DatasetForge build execution",
        "request_body_template": {
            "dataset_manifest_id": f"dataset-radar-{material_request_id}",
            "purpose": f"Dataset Radar {requested_split} handoff for {target_node or 'target node'}",
            "material_request_ref": material_request_id,
            "task_type": "tool_use",
            "operator_approved": False,
            "metadata": {
                "source": "dataset-radar-material-request",
                "teacher_ref": teacher_ref,
                "target_node": target_node,
                "requested_split": requested_split,
                "candidate_training_allowed": False,
            },
            "sources": sources,
        },
    }


def _dataset_forge_source_template(
    *,
    preview: dict[str, Any],
    material_request_id: str,
    requested_split: str,
) -> dict[str, Any]:
    dataset_id = str(preview.get("dataset_id") or preview.get("source_id") or "unknown")
    source_kind = str(preview.get("source_kind") or "unknown")
    license_state = str(preview.get("license_state") or "blocked_unknown_license")
    training_eligible = source_kind == "canonical_source" and requested_split == "train" and license_state == "approved_train"
    return {
        "source_id": dataset_id,
        "source_type": "web",
        "text": f"Operator-reviewed excerpt placeholder for Dataset Radar source {dataset_id}.",
        "license_status": _forge_license_status(license_state),
        "contains_private_data": False,
        "provenance_ref": f"dataset-radar:{material_request_id}:{dataset_id}",
        "dataset_radar_source_id": dataset_id,
        "allowed_distillation_state": "not_applicable",
        "contamination_risk": "unknown",
        "metadata": {
            "material_request_ref": material_request_id,
            "intended_split": requested_split,
            "source_kind": source_kind,
            "license_state": license_state,
            "training_eligible": training_eligible,
            "requires_operator_excerpt": True,
        },
    }


def _forge_license_status(license_state: str) -> str:
    if license_state.startswith("blocked_"):
        return "blocked"
    if license_state.startswith("approved_") or license_state == "sealed_eval_only":
        return "approved"
    return "needs_review"


def _candidate_review_scoring(
    *,
    result: dict[str, Any],
    request: dict[str, Any],
    dataset_id: str,
    tags: list[str],
    license_state: str,
) -> dict[str, Any]:
    downloads = _safe_float(result.get("downloads"))
    trending = _safe_float(result.get("trendingScore") or result.get("trending_score"))
    last_modified = result.get("lastModified") or result.get("last_modified")
    license_signal = 0.55 if license_state == "pending_provenance_review" else 0.0
    popularity_signal = min(math.log10(max(downloads, 0.0) + 1.0) / 6.0, 1.0)
    trending_signal = min(max(trending, 0.0) / 100.0, 1.0)
    freshness_signal = _freshness_signal(last_modified)
    target_fit_signal = _target_fit_signal(dataset_id=dataset_id, tags=tags, request=request)
    blocked_penalty = 0.55 if license_state.startswith("blocked_") else 0.0
    review_score = max(
        0.0,
        min(
            1.0,
            (license_signal * 0.35)
            + (popularity_signal * 0.20)
            + (trending_signal * 0.20)
            + (freshness_signal * 0.15)
            + (target_fit_signal * 0.10)
            - blocked_penalty,
        ),
    )
    return {
        "review_score": round(review_score, 4),
        "quality_signals": {
            "license_signal": round(license_signal, 4),
            "popularity_signal": round(popularity_signal, 4),
            "trending_signal": round(trending_signal, 4),
            "freshness_signal": round(freshness_signal, 4),
            "target_fit_signal": round(target_fit_signal, 4),
            "review_priority": _review_priority(review_score),
        },
    }


def _safe_float(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _freshness_signal(value: Any) -> float:
    if not value:
        return 0.0
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return 0.0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    age_days = max((datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).days, 0)
    if age_days <= 30:
        return 1.0
    if age_days <= 180:
        return 0.75
    if age_days <= 365:
        return 0.5
    if age_days <= 730:
        return 0.25
    return 0.0


def _freshness_rollup(*, sources: list[dict[str, Any]], refresh_history: list[dict[str, Any]]) -> dict[str, Any]:
    source_statuses = [_source_freshness_status(source) for source in sources]
    due_sources = [status for status in source_statuses if status["refresh_due"]]
    stale_sources = [status for status in due_sources if status["freshness_status"] == "stale"]
    manual_sources = [status for status in due_sources if status["freshness_status"] == "manual_review"]
    invalid_sources = [status for status in due_sources if status["freshness_status"] == "invalid"]
    refresh_run_freshness = _refresh_run_freshness(refresh_history)
    warnings = [
        {
            "warning_id": f"source-refresh-due:{status['dataset_id']}",
            "severity": status["severity"],
            "dataset_id": status["dataset_id"],
            "label": status["label"],
            "source_family": status["source_family"],
            "cadence": status["cadence"],
            "last_checked": status["last_checked"],
            "age_days": status["age_days"],
            "days_overdue": status["days_overdue"],
            "reason": status["reason"],
        }
        for status in due_sources
    ]
    if refresh_run_freshness["refresh_due"]:
        warnings.insert(
            0,
            {
                "warning_id": "radar-refresh-run-due",
                "severity": refresh_run_freshness["severity"],
                "dataset_id": "dataset-radar-refresh",
                "label": "Dataset Radar refresh run",
                "source_family": "radar_runtime",
                "cadence": refresh_run_freshness["cadence"],
                "last_checked": refresh_run_freshness["last_refreshed_at"],
                "age_days": refresh_run_freshness["age_days"],
                "days_overdue": refresh_run_freshness["days_overdue"],
                "reason": refresh_run_freshness["reason"],
            },
        )
    warnings.sort(key=lambda item: _freshness_severity_rank(str(item.get("severity") or "")), reverse=True)
    due_sources.sort(
        key=lambda item: (
            _freshness_severity_rank(item["severity"]),
            int(item.get("days_overdue") or 0),
            item["dataset_id"],
        ),
        reverse=True,
    )
    return {
        "summary": {
            "source_count": len(sources),
            "current_count": len([status for status in source_statuses if status["freshness_status"] == "current"]),
            "refresh_due_count": len(due_sources),
            "stale_count": len(stale_sources),
            "manual_review_count": len(manual_sources),
            "invalid_count": len(invalid_sources),
            "latest_refresh_due": refresh_run_freshness["refresh_due"],
            "policy": {
                "cadence_days": FRESHNESS_CADENCE_DAYS,
                "manual_cadence_rule": "manual sources require explicit operator review before use",
                "refresh_run_cadence": "daily",
            },
        },
        "due_sources": due_sources,
        "warnings": warnings,
        "refresh_run_freshness": refresh_run_freshness,
        "warning_count": len(warnings),
    }


def _refresh_recommendations(*, due_sources: list[dict[str, Any]], presets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_family: dict[str, list[dict[str, Any]]] = {}
    for source in due_sources:
        family = str(source.get("source_family") or "unknown")
        by_family.setdefault(family, []).append(source)
    recommendations: list[dict[str, Any]] = []
    for family, family_sources in sorted(by_family.items()):
        matching_presets = [preset for preset in presets if preset.get("source_family") == family]
        due_source_ids = sorted(str(source.get("dataset_id")) for source in family_sources if source.get("dataset_id"))
        target_nodes = sorted(
            {
                str(target)
                for source in family_sources
                for target in (source.get("target_nodes") or [])
                if str(target).strip()
            }
        )
        if matching_presets:
            preset_ids = [str(preset["preset_id"]) for preset in matching_presets]
            endpoint = "/ops/brain/dataset-radar/refresh-batch"
            refresh_payload: dict[str, Any] = {
                "preset_ids": preset_ids,
                "source_families": [family],
                "limit": 25,
                "source": "dataset-radar-freshness-recommendation",
            }
        else:
            preset_ids = []
            endpoint = "/ops/brain/dataset-radar/refresh"
            query_terms = " ".join(family.replace("_", " ").split())
            refresh_payload = {
                "query": f"open {query_terms} dataset",
                "source_families": [family],
                "target_nodes": target_nodes,
                "limit": 25,
                "source": "dataset-radar-freshness-recommendation",
            }
        recommendations.append(
            {
                "recommendation_id": f"refresh-family:{family}",
                "source_family": family,
                "due_count": len(due_source_ids),
                "due_source_ids": due_source_ids,
                "preset_ids": preset_ids,
                "target_nodes": target_nodes,
                "method": "POST",
                "endpoint": endpoint,
                "refresh_payload": refresh_payload,
                "auto_execute_allowed": False,
                "reason": "Source freshness is due; operator must run an explicit refresh and review candidates.",
            }
        )
    recommendations.sort(key=lambda item: (item["due_count"], item["source_family"]), reverse=True)
    return recommendations


def _source_freshness_status(source: dict[str, Any]) -> dict[str, Any]:
    freshness = source.get("freshness") or {}
    cadence = str(freshness.get("cadence") or "manual").strip().lower()
    last_checked = str(freshness.get("last_checked") or "")
    age_days = _age_days(last_checked)
    max_age_days = FRESHNESS_CADENCE_DAYS.get(cadence)
    if cadence == "manual":
        return _source_freshness_payload(
            source=source,
            freshness_status="manual_review",
            refresh_due=True,
            severity="medium",
            age_days=age_days,
            days_overdue=0,
            reason="Manual cadence requires explicit operator review before use.",
        )
    if age_days is None:
        return _source_freshness_payload(
            source=source,
            freshness_status="invalid",
            refresh_due=True,
            severity="high",
            age_days=None,
            days_overdue=0,
            reason="Source freshness has an invalid or missing last_checked date.",
        )
    if max_age_days is None:
        return _source_freshness_payload(
            source=source,
            freshness_status="manual_review",
            refresh_due=True,
            severity="medium",
            age_days=age_days,
            days_overdue=0,
            reason=f"Unknown cadence '{cadence}' requires operator review.",
        )
    days_overdue = max(age_days - max_age_days, 0)
    if days_overdue > 0:
        return _source_freshness_payload(
            source=source,
            freshness_status="stale",
            refresh_due=True,
            severity="high" if days_overdue > max_age_days else "medium",
            age_days=age_days,
            days_overdue=days_overdue,
            reason=f"Last checked {age_days} days ago; {cadence} cadence allows {max_age_days} days.",
        )
    return _source_freshness_payload(
        source=source,
        freshness_status="current",
        refresh_due=False,
        severity="none",
        age_days=age_days,
        days_overdue=0,
        reason=f"Current for {cadence} cadence.",
    )


def _source_freshness_payload(
    *,
    source: dict[str, Any],
    freshness_status: str,
    refresh_due: bool,
    severity: str,
    age_days: int | None,
    days_overdue: int,
    reason: str,
) -> dict[str, Any]:
    freshness = source.get("freshness") or {}
    return {
        "dataset_id": source.get("dataset_id"),
        "label": source.get("label"),
        "source_family": source.get("source_family"),
        "license_state": source.get("license_state"),
        "target_nodes": source.get("target_nodes") or [],
        "freshness_status": freshness_status,
        "refresh_due": refresh_due,
        "severity": severity,
        "tracking": freshness.get("tracking"),
        "cadence": freshness.get("cadence"),
        "last_checked": freshness.get("last_checked"),
        "age_days": age_days,
        "days_overdue": days_overdue,
        "reason": reason,
    }


def _refresh_run_freshness(refresh_history: list[dict[str, Any]]) -> dict[str, Any]:
    latest = refresh_history[0] if refresh_history else None
    if latest is None:
        return {
            "cadence": "daily",
            "last_refreshed_at": None,
            "age_hours": None,
            "age_days": None,
            "days_overdue": 1,
            "refresh_due": True,
            "severity": "medium",
            "reason": "No Dataset Radar refresh run has been recorded in this artifact store.",
        }
    refreshed_at = str(latest.get("refreshed_at") or "")
    age_hours = _age_hours(refreshed_at)
    if age_hours is None:
        return {
            "cadence": "daily",
            "last_refreshed_at": refreshed_at,
            "age_hours": None,
            "age_days": None,
            "days_overdue": 1,
            "refresh_due": True,
            "severity": "high",
            "reason": "Latest Dataset Radar refresh timestamp is invalid.",
        }
    refresh_due = age_hours > 24
    return {
        "cadence": "daily",
        "last_refreshed_at": refreshed_at,
        "age_hours": age_hours,
        "age_days": math.floor(age_hours / 24),
        "days_overdue": max(math.floor((age_hours - 24) / 24) + 1, 0) if refresh_due else 0,
        "refresh_due": refresh_due,
        "severity": "medium" if refresh_due else "none",
        "reason": "Latest Dataset Radar refresh is older than 24 hours." if refresh_due else "Latest Dataset Radar refresh is current.",
    }


def _age_days(value: str) -> int | None:
    parsed = _parse_datetime(value)
    if parsed is None:
        return None
    return max((datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).days, 0)


def _age_hours(value: str) -> int | None:
    parsed = _parse_datetime(value)
    if parsed is None:
        return None
    return max(math.floor((datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).total_seconds() / 3600), 0)


def _parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = datetime.fromisoformat(f"{value}T00:00:00+00:00")
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _freshness_severity_rank(severity: str) -> int:
    return {"high": 3, "medium": 2, "low": 1, "none": 0}.get(severity, 1)


def _target_fit_signal(*, dataset_id: str, tags: list[str], request: dict[str, Any]) -> float:
    target_tokens = {
        token
        for value in [
            request.get("query"),
            request.get("source_family"),
            " ".join(str(node) for node in request.get("target_nodes", []) or []),
        ]
        for token in str(value or "").lower().replace("-", " ").replace("_", " ").split()
        if len(token) > 2
    }
    candidate_tokens = {
        token
        for token in " ".join([dataset_id.lower().replace("-", " ").replace("_", " "), *tags]).split()
        if len(token) > 2
    }
    if not target_tokens:
        return 0.0
    overlap = target_tokens.intersection(candidate_tokens)
    return min(len(overlap) / max(len(target_tokens), 1), 1.0)


def _review_priority(score: float) -> str:
    if score >= 0.55:
        return "high"
    if score >= 0.30:
        return "medium"
    return "low"


def _candidate_review_allowed_uses(state: str) -> list[str]:
    if state == "approved_teacher_context":
        return ["teacher_context"]
    if state == "approved_eval_only":
        return ["validation", "heldout", "adversarial"]
    if state == "sealed_eval_only":
        return ["teacher_free_hidden"]
    return []


def _candidate_gate(
    *,
    dataset_id: str,
    split: str,
    state: str,
    allowed_uses: list[str],
    freshness: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    normalized_split = _normalize_split(split)
    allowed = False
    if normalized_split == "teacher_context":
        allowed = state in TEACHER_CONTEXT_ALLOWED_STATES and "teacher_context" in allowed_uses
    elif normalized_split in {"validation", "heldout", "adversarial"}:
        allowed = state in EVAL_ALLOWED_STATES and normalized_split in allowed_uses
    elif normalized_split == "teacher_free_hidden":
        allowed = state in SEALED_EVAL_STATES and "teacher_free_hidden" in allowed_uses
    return {
        "source_id": dataset_id,
        "split": normalized_split,
        "allowed": allowed,
        "license_state": state,
        "allowed_uses": allowed_uses,
        "provenance_state": "candidate_reviewed" if allowed else "candidate_discovery_only",
        "privacy_risk": "unreviewed",
        "freshness": freshness,
        "reason": "allowed by candidate review for non-training use" if allowed else reason,
    }


def _discovery_filters(request: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "required_tags": _string_list(request.get("required_tags") or request.get("tags") or []),
        "blocked_tags": _string_list(request.get("blocked_tags") or []),
        "authors": _string_list(request.get("authors") or request.get("author") or []),
        "source_families": _string_list(request.get("source_families") or request.get("source_family_filter") or []),
    }


def _string_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        raw_items = value.replace(",", " ").split()
    elif isinstance(value, (list, tuple, set)):
        raw_items = [str(item) for item in value]
    else:
        raw_items = [str(value)]
    return [item.strip().lower() for item in raw_items if item and item.strip()]


def _passes_discovery_filters(result: dict[str, Any], filters: dict[str, list[str]]) -> bool:
    tags = [str(tag).lower() for tag in result.get("tags", []) or []]
    dataset_id = str(result.get("id") or result.get("dataset_id") or result.get("name") or "").lower()
    author = str(result.get("author") or "").lower()
    source_family = _infer_family(tags, dataset_id)
    searchable = " ".join([dataset_id, author, *tags]).replace("-", " ").replace("_", " ")

    required_tags = filters.get("required_tags") or []
    if required_tags and not all(_filter_token_present(token, tags, searchable) for token in required_tags):
        return False

    blocked_tags = filters.get("blocked_tags") or []
    if blocked_tags and any(_filter_token_present(token, tags, searchable) for token in blocked_tags):
        return False

    authors = set(filters.get("authors") or [])
    if authors and author not in authors:
        return False

    source_families = set(filters.get("source_families") or [])
    if source_families and source_family not in source_families:
        return False

    return True


def _filter_token_present(token: str, tags: list[str], searchable: str) -> bool:
    normalized = str(token).strip().lower()
    if not normalized:
        return False
    return normalized in tags or normalized in searchable


def _infer_family(tags: list[str], dataset_id: str) -> str:
    lowered = " ".join([dataset_id.lower(), *tags])
    if any(value in lowered for value in ("cyber", "security", "vulnerability", "vuln", "malware", "ctf", "owasp")):
        return "cybersecurity_defensive"
    if any(value in lowered for value in ("patent", "uspto", "legal", "court", "law", "statute", "case-law")):
        return "patents_legal"
    if any(value in lowered for value in ("biomed", "biomedical", "pubmed", "pmc", "genbank", "genomics", "genome", "protein", "clinical")):
        return "biomedical_genomics"
    if any(value in lowered for value in ("cad", "engineering", "geometry", "mechanical", "mesh", "3d-model", "3d")):
        return "engineering_cad"
    if any(value in lowered for value in ("arxiv", "openalex", "semantic", "scholar", "paper", "papers", "science", "research", "citation")):
        return "science_research"
    if any(value in lowered for value in ("gutenberg", "wikimedia", "wikidata", "books", "book", "corpus", "public-domain", "cc-by-sa")):
        return "open_legal_text"
    if any(value in lowered for value in ("code", "agent", "tool", "swe")):
        return "code_agent"
    if any(value in lowered for value in ("math", "proof", "reasoning")):
        return "math_reasoning"
    if any(value in lowered for value in ("audio", "speech", "vision", "image", "video", "ocr")):
        return "multimodal_audio_video"
    if any(value in lowered for value in ("preference", "instruction", "chat")):
        return "instruction_preference"
    return "foundation_web"


def _normalize_split(split: str) -> str:
    normalized = str(split).strip().lower().replace("-", "_")
    if normalized in {"sealed_eval", "hidden_eval", "teacher_free_eval"}:
        return "teacher_free_hidden"
    if normalized == "teacher":
        return "teacher_context"
    if normalized == "eval":
        return "validation"
    return normalized


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _lineage_split_policy(sources: list[dict[str, Any]]) -> dict[str, Any]:
    train_source_ids: list[str] = []
    teacher_context_only_source_ids: list[str] = []
    sealed_eval_source_ids: list[str] = []
    eval_only_source_ids: list[str] = []
    for source in sources:
        source_id = str(source.get("dataset_id") or "")
        if not source_id:
            continue
        allowed_uses = set(source.get("allowed_uses") or [])
        license_state = str(source.get("license_state") or "")
        if license_state == "approved_train" and "train" in allowed_uses:
            train_source_ids.append(source_id)
        if "teacher_context" in allowed_uses and "train" not in allowed_uses:
            teacher_context_only_source_ids.append(source_id)
        if license_state == "sealed_eval_only" or "teacher_free_hidden" in allowed_uses:
            sealed_eval_source_ids.append(source_id)
        elif {"validation", "heldout", "regression"} & allowed_uses and "train" not in allowed_uses:
            eval_only_source_ids.append(source_id)
    return {
        "train_source_ids": train_source_ids,
        "teacher_context_only_source_ids": teacher_context_only_source_ids,
        "sealed_eval_source_ids": sealed_eval_source_ids,
        "eval_only_source_ids": eval_only_source_ids,
        "split_rule": "training sources cannot be reused as sealed teacher-free eval sources",
    }


def _hydrate_preset(preset: dict[str, Any], radar: DatasetRadar) -> dict[str, Any]:
    source_ids = list(preset.get("seed_lineage_source_ids") or [])
    sources = [radar.source_for(source_id) for source_id in source_ids]
    present_sources = [source for source in sources if source is not None]
    split_policy = _lineage_split_policy(present_sources)
    return {
        **preset,
        "seed_lineage_labels": [source["label"] for source in present_sources],
        "seed_lineage_states": {source["dataset_id"]: source["license_state"] for source in present_sources},
        "seed_lineage_train_source_ids": split_policy["train_source_ids"],
        "seed_lineage_teacher_context_only_source_ids": split_policy["teacher_context_only_source_ids"],
        "seed_lineage_sealed_eval_source_ids": split_policy["sealed_eval_source_ids"],
        "seed_lineage_eval_only_source_ids": split_policy["eval_only_source_ids"],
        "seed_lineage_split_rule": split_policy["split_rule"],
    }


def _compact_timestamp(value: str) -> str:
    return (
        value.replace("+00:00", "Z")
        .replace(":", "")
        .replace("-", "")
        .replace(".", "")
        .replace("T", "T")
        .replace("Z", "Z")
    )


def _project_relative_artifact_ref(artifacts_dir: Path | None, path: Path) -> str:
    if artifacts_dir is None:
        return path.as_posix()
    try:
        return path.relative_to(artifacts_dir.parent.parent).as_posix()
    except ValueError:
        pass
    try:
        return path.relative_to(artifacts_dir.parent).as_posix()
    except ValueError:
        return path.as_posix()
