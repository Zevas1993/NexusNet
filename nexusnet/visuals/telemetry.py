from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .performance import VisualPerformanceAdvisor


@dataclass(slots=True)
class VisualTelemetryContext:
    scene: Any
    snapshot: dict[str, Any]
    traces: list[dict[str, Any]]
    session_id: str | None
    store: Any
    paths: Any


class TraceStoreTelemetryProvider:
    provider_id = "trace-store"

    def collect(self, context: VisualTelemetryContext) -> dict[str, Any]:
        return {
            "trace_records": context.traces,
            "trace_count": len(context.traces),
            "_provider_state": {
                "kind": "runtime-trace-store",
                "signal_count": len(context.traces),
                "latest_trace_id": context.traces[0].get("trace_id") if context.traces else None,
            },
            "bound": bool(context.traces),
        }


class WrapperSnapshotTelemetryProvider:
    provider_id = "wrapper-snapshot"

    def collect(self, context: VisualTelemetryContext) -> dict[str, Any]:
        snapshot = context.snapshot
        teachers = snapshot.get("teachers") or {}
        visibility = teachers.get("visibility") or {}
        runtime_summary = snapshot.get("runtime") or {}
        return {
            "recent_trace": snapshot.get("recent_trace") or {},
            "teacher_visibility": visibility,
            "recent_teacher_traces": visibility.get("recent_teacher_traces") or [],
            "runtime_summary": runtime_summary,
            "device_profile": runtime_summary.get("device_profile") or {},
            "runtime_candidates": runtime_summary.get("candidates") or [],
            "promotions": snapshot.get("promotions") or {},
            "foundry": snapshot.get("foundry") or {},
            "_provider_state": {
                "kind": "wrapper-snapshot",
                "registry_layer": ((snapshot.get("recent_trace") or {}).get("teacher_provenance") or {}).get("registry_layer"),
                "recent_trace_id": (snapshot.get("recent_trace") or {}).get("trace_id"),
                "promotion_count": len((snapshot.get("promotions") or {}).get("items", [])),
                "native_takeover_count": len((snapshot.get("foundry") or {}).get("native_takeover", [])),
            },
            "bound": True,
        }


class BrainLogTelemetryProvider:
    provider_id = "brain-telemetry-logs"

    def collect(self, context: VisualTelemetryContext) -> dict[str, Any]:
        logs_dir = Path(context.paths.logs_dir)
        channels: dict[str, Any] = {}
        for filename, channel in {
            "inference.log": "inference",
            "benchmark.log": "benchmark",
            "model_load.log": "model_load",
            "startup.log": "startup",
        }.items():
            path = logs_dir / filename
            records = self._read_tail_jsonl(path, limit=12)
            channels[channel] = {
                "path": str(path),
                "count": len(records),
                "latest_timestamp": records[0].get("timestamp") if records else None,
                "latest_trace_id": records[0].get("trace_id") if records else None,
                "bound": bool(records),
            }
        return {
            "log_channels": channels,
            "_provider_state": {
                "kind": "telemetry-logs",
                "signal_count": sum(int(channel_data.get("count", 0)) for channel_data in channels.values()),
                "bound_channels": [name for name, channel_data in channels.items() if channel_data.get("bound")],
            },
            "bound": any(channel.get("bound", False) for channel in channels.values()),
        }

    def _read_tail_jsonl(self, path: Path, *, limit: int) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return []
        records: list[dict[str, Any]] = []
        for line in reversed(lines[-limit:]):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                records.append(payload)
        return records


class SimulatedTelemetryProvider:
    provider_id = "simulated-fallback"

    def collect(self, context: VisualTelemetryContext) -> dict[str, Any]:
        recent_trace = context.snapshot.get("recent_trace") or {}
        provenance = recent_trace.get("teacher_provenance") or {}
        subject = (provenance.get("routing_decision") or {}).get("subject") or recent_trace.get("selected_expert") or provenance.get("expert")
        synthetic_records: list[dict[str, Any]] = []
        if subject:
            synthetic_records.append(
                {
                    "trace_id": f"synthetic::{subject}",
                    "session_id": context.session_id,
                    "selected_expert": subject,
                    "teacher_provenance": {
                        "expert": subject,
                        "arbitration_result": provenance.get("arbitration_result"),
                        "dream_lineage": provenance.get("dream_lineage") or "live-derived",
                    },
                    "metrics": {
                        "graph_contribution_count": (recent_trace.get("metrics") or {}).get("graph_contribution_count", 0),
                        "fallback_used": (recent_trace.get("metrics") or {}).get("fallback_used", False),
                    },
                    "promotion_references": recent_trace.get("promotion_references") or [],
                }
            )
        return {
            "simulated_trace_records": synthetic_records,
            "_provider_state": {
                "kind": "synthetic-fallback",
                "signal_count": len(synthetic_records),
                "reason": "No bound runtime traces available for the current session."
                if not context.traces
                else "Supplemental degraded fallback.",
            },
            "bound": bool(synthetic_records),
        }


class VisualizerTelemetryAdapter:
    def __init__(
        self,
        *,
        scene,
        store,
        paths,
        allow_depth_enhancement: bool,
        source_providers: list[object] | None = None,
    ):
        self.scene = scene
        self.store = store
        self.paths = paths
        self.performance = VisualPerformanceAdvisor(allow_depth_enhancement=allow_depth_enhancement)
        self.source_providers = source_providers or [
            TraceStoreTelemetryProvider(),
            WrapperSnapshotTelemetryProvider(),
            BrainLogTelemetryProvider(),
            SimulatedTelemetryProvider(),
        ]

    def collect_sources(
        self,
        *,
        snapshot: dict[str, Any],
        traces: list[dict[str, Any]],
        session_id: str | None,
    ) -> dict[str, Any]:
        context = VisualTelemetryContext(
            scene=self.scene,
            snapshot=snapshot,
            traces=traces,
            session_id=session_id,
            store=self.store,
            paths=self.paths,
        )
        merged: dict[str, Any] = {}
        provider_states: list[dict[str, Any]] = []
        for provider in self.source_providers:
            payload = provider.collect(context)  # type: ignore[attr-defined]
            bound = bool(payload.pop("bound", False))
            provider_state = payload.pop("_provider_state", {})
            provider_states.append({"provider_id": provider.provider_id, "bound": bound, **provider_state})  # type: ignore[attr-defined]
            merged.update(payload)
        bound_count = sum(1 for state in provider_states if state["bound"])
        merged["source_status"] = {
            "providers": provider_states,
            "bound_ratio": round(bound_count / len(provider_states), 3) if provider_states else 0.0,
        }
        return merged

    def safe_mode_physiology(self, *, recent_trace: dict[str, Any], traces: list[dict[str, Any]], sources: dict[str, Any]) -> dict[str, Any]:
        runtime_candidates = sources.get("runtime_candidates") or []
        device_profile = sources.get("device_profile") or {}
        safe_mode = any(candidate.get("source") == "qes-shadow" and candidate.get("estimated_power", 1) <= 0.3 for candidate in runtime_candidates)
        thermal_mode = str(device_profile.get("thermal_mode", "unknown") or "unknown")
        fallback_used = bool((recent_trace.get("metrics") or {}).get("fallback_used", False))
        retry_burst = sum(1 for trace in traces[:8] if (trace.get("metrics") or {}).get("fallback_used", False))
        vram_pressure = str(device_profile.get("vram_pressure", "unreported") or "unreported")
        ram_pressure = str(device_profile.get("ram_pressure", "unreported") or "unreported")
        return {
            "safe_mode": safe_mode,
            "thermal_mode": thermal_mode,
            "vram_pressure": vram_pressure,
            "ram_pressure": ram_pressure,
            "retry_state": "fallback-path-active" if fallback_used else ("retry-burst" if retry_burst >= 2 else "stable"),
            "channel_activity": {
                "safe_mode": safe_mode,
                "thermal_mode": thermal_mode != "unknown",
                "vram_pressure": vram_pressure not in {"", "unreported", "unknown"},
                "ram_pressure": ram_pressure not in {"", "unreported", "unknown"},
                "retry_state": fallback_used or retry_burst >= 2,
            },
        }

    def link_activity(self, *, traces: list[dict[str, Any]], snapshot: dict[str, Any], sources: dict[str, Any]) -> dict[str, Any]:
        records = self._route_records(traces=traces, sources=sources)
        edge_scores: dict[str, float] = defaultdict(float)
        edge_counts: dict[str, int] = defaultdict(int)
        edge_refs: dict[str, list[str]] = defaultdict(list)
        core_scores: dict[str, float] = defaultdict(float)
        core_counts: dict[str, int] = defaultdict(int)
        core_refs: dict[str, list[str]] = defaultdict(list)
        group_scores: dict[str, float] = defaultdict(float)
        group_counts: dict[str, int] = defaultdict(int)
        group_refs: dict[str, list[str]] = defaultdict(list)

        group_members = {group.get("group_id"): list(group.get("subjects", [])) for group in self.scene.manifest.get("collaboration_groups", [])}
        group_edges: dict[str, list[str]] = defaultdict(list)
        for link in self.scene.links:
            group_id = (link.meta or {}).get("group_id")
            if group_id:
                group_edges[group_id].append(link.link_id)

        for index, trace in enumerate(records):
            weight = self._trace_weight(index)
            trace_id = trace.get("trace_id", f"trace:{index}")
            provenance = trace.get("teacher_provenance") or {}
            subject = (provenance.get("routing_decision") or {}).get("subject") or trace.get("selected_expert") or provenance.get("expert")
            graph_count = int((trace.get("metrics") or {}).get("graph_contribution_count", 0) or 0)
            if subject:
                core_scores[subject] += weight
                core_counts[subject] += 1
                self._append_ref(core_refs[subject], trace_id)
                edge_id = f"core::{subject}"
                edge_scores[edge_id] += weight
                edge_counts[edge_id] += 1
                self._append_ref(edge_refs[edge_id], trace_id)
                collaboration_boost = weight * (0.42 + min(graph_count, 5) * 0.08)
                for group_id, subjects in group_members.items():
                    if subject not in subjects:
                        continue
                    group_scores[group_id] += collaboration_boost
                    group_counts[group_id] += 1
                    self._append_ref(group_refs[group_id], trace_id)
                    for grouped_edge_id in group_edges.get(group_id, []):
                        edge_scores[grouped_edge_id] += collaboration_boost
                        edge_counts[grouped_edge_id] += 1
                        self._append_ref(edge_refs[grouped_edge_id], trace_id)
            if provenance.get("arbitration_result") and subject and subject != "critique":
                critique_edge = f"critique::{subject}"
                edge_scores[critique_edge] += weight * 0.92
                edge_counts[critique_edge] += 1
                self._append_ref(edge_refs[critique_edge], trace_id)
            if trace.get("promotion_references"):
                consequence_subject = subject or "router"
                consequence_edge = f"consequence-loop::{consequence_subject}"
                edge_scores[consequence_edge] += weight * 0.55
                edge_counts[consequence_edge] += 1
                self._append_ref(edge_refs[consequence_edge], trace_id)
            if provenance.get("dream_lineage") == "dream-derived" or provenance.get("dream_derived"):
                dream_subject = subject or "simulation"
                dream_edge = f"dream-loop::{dream_subject}"
                edge_scores[dream_edge] += weight * 0.6
                edge_counts[dream_edge] += 1
                self._append_ref(edge_refs[dream_edge], trace_id)

        return {
            "status": "bound" if traces else ("degraded" if records else "unbound"),
            "provider_chain": self._provider_chain(sources),
            "decay": {"smoothing": "weighted-recent", "persistence_floor": 0.18, "half_life_steps": 4},
            "core_to_capsule": {
                subject: {
                    "intensity": self._cap(core_scores.get(subject, 0.0), ceiling=1.8),
                    "trace_count": core_counts.get(subject, 0),
                    "source_refs": core_refs.get(subject, []),
                    "link_id": f"core::{subject}",
                }
                for subject in self._capsule_subjects()
            },
            "collaboration_groups": {
                group_id: {
                    "intensity": self._cap(group_scores.get(group_id, 0.0), ceiling=1.6),
                    "trace_count": group_counts.get(group_id, 0),
                    "source_refs": group_refs.get(group_id, []),
                    "edge_ids": group_edges.get(group_id, []),
                    "subjects": subjects,
                }
                for group_id, subjects in group_members.items()
            },
            "edges": {
                link.link_id: {
                    "intensity": self._cap(edge_scores.get(link.link_id, 0.0), ceiling=2.4),
                    "trace_count": edge_counts.get(link.link_id, 0),
                    "source_refs": edge_refs.get(link.link_id, []),
                    "link_type": link.link_type,
                    "meta": link.meta,
                }
                for link in self.scene.links
            },
        }

    def loop_activity(self, *, traces: list[dict[str, Any]], snapshot: dict[str, Any], sources: dict[str, Any]) -> dict[str, Any]:
        records = self._route_records(traces=traces, sources=sources)
        scores: dict[str, float] = defaultdict(float)
        counts: dict[str, int] = defaultdict(int)
        refs: dict[str, list[str]] = defaultdict(list)
        for index, trace in enumerate(records):
            weight = self._trace_weight(index)
            trace_id = trace.get("trace_id", f"trace:{index}")
            provenance = trace.get("teacher_provenance") or {}
            if provenance.get("dream_lineage") == "dream-derived" or provenance.get("dream_derived"):
                scores["dream"] += weight
                counts["dream"] += 1
                self._append_ref(refs["dream"], trace_id)
            if provenance.get("arbitration_result"):
                scores["critique"] += weight
                counts["critique"] += 1
                self._append_ref(refs["critique"], trace_id)
            if trace.get("promotion_references") or provenance.get("native_takeover_candidate_id") or (trace.get("metrics") or {}).get("fallback_used", False):
                scores["consequence"] += weight
                counts["consequence"] += 1
                self._append_ref(refs["consequence"], trace_id)

        foundry = snapshot.get("foundry") or {}
        promotions = snapshot.get("promotions") or {}
        if foundry.get("native_takeover"):
            scores["consequence"] += min(1.0, len(foundry.get("native_takeover", [])) * 0.18)
        if promotions.get("items"):
            scores["consequence"] += min(1.0, len(promotions.get("items", [])) * 0.08)

        return {
            loop_type: {
                "intensity": self._cap(scores.get(loop_type, 0.0), ceiling=2.0),
                "count": counts.get(loop_type, 0),
                "active_refs": refs.get(loop_type, []),
                "smoothing_window": len(records),
            }
            for loop_type in ["dream", "critique", "consequence"]
        }

    def evidence_activity(self, *, snapshot: dict[str, Any], traces: list[dict[str, Any]], teacher_visibility: dict[str, Any]) -> dict[str, Any]:
        disagreement_ids = [item.get("artifact_id") for item in teacher_visibility.get("disagreement_artifacts", []) if item.get("artifact_id")]
        bundle_ids = [item.get("bundle_id") for item in teacher_visibility.get("evidence_bundles", []) if item.get("bundle_id")]
        promotions = snapshot.get("promotions") or {}
        foundry = snapshot.get("foundry") or {}
        return {
            "teacher": {
                "intensity": self._cap(len(bundle_ids), ceiling=6.0),
                "refs": bundle_ids[:8],
            },
            "promotion": {
                "intensity": self._cap(len(promotions.get("items", [])), ceiling=6.0),
                "refs": [
                    item.get("candidate", {}).get("candidate_id")
                    for item in promotions.get("items", [])[:8]
                    if item.get("candidate", {}).get("candidate_id")
                ],
            },
            "takeover": {
                "intensity": self._cap(len(foundry.get("native_takeover", [])), ceiling=5.0),
                "refs": [
                    item.get("candidate", {}).get("candidate_id")
                    for item in foundry.get("native_takeover", [])[:8]
                    if item.get("candidate", {}).get("candidate_id")
                ],
            },
            "disagreement": {
                "intensity": self._cap(len(disagreement_ids), ceiling=6.0),
                "refs": disagreement_ids[:8],
                "recent_trace_count": len(traces),
            },
        }

    def physiology_activity(self, *, safe_mode_physiology: dict[str, Any], traces: list[dict[str, Any]]) -> dict[str, Any]:
        thermal_mode = str(safe_mode_physiology.get("thermal_mode", "unknown"))
        thermal_intensity = 0.0
        thermal_label = "unbound"
        if thermal_mode == "unknown":
            thermal_label = "unbound"
        elif thermal_mode.lower() in {"cool", "nominal"}:
            thermal_intensity = 0.2
            thermal_label = "nominal"
        elif thermal_mode.lower() in {"warm", "elevated"}:
            thermal_intensity = 0.5
            thermal_label = "elevated"
        else:
            thermal_intensity = 0.82
            thermal_label = "stressed"
        retry_count = sum(1 for trace in traces[:8] if (trace.get("metrics") or {}).get("fallback_used", False))
        vram_pressure = str(safe_mode_physiology.get("vram_pressure", "unreported"))
        ram_pressure = str(safe_mode_physiology.get("ram_pressure", "unreported"))
        return {
            "safe_mode": {
                "state": "contracted" if safe_mode_physiology.get("safe_mode") else "nominal",
                "intensity": 0.78 if safe_mode_physiology.get("safe_mode") else 0.12,
                "bound": True,
            },
            "thermal": {
                "state": thermal_label,
                "intensity": thermal_intensity,
                "bound": thermal_mode != "unknown",
            },
            "vram": {
                "state": vram_pressure,
                "intensity": 0.0 if vram_pressure in {"unreported", "unknown", ""} else 0.65,
                "bound": vram_pressure not in {"unreported", "unknown", ""},
            },
            "ram": {
                "state": ram_pressure,
                "intensity": 0.0 if ram_pressure in {"unreported", "unknown", ""} else 0.46,
                "bound": ram_pressure not in {"unreported", "unknown", ""},
            },
            "retry": {
                "state": safe_mode_physiology.get("retry_state", "stable"),
                "intensity": self._cap(retry_count or (1 if safe_mode_physiology.get("retry_state") != "stable" else 0), ceiling=3.0),
                "bound": True,
            },
            "degraded_channels": [
                channel
                for channel in ["safe_mode", "thermal_mode", "vram_pressure", "ram_pressure", "retry_state"]
                if not safe_mode_physiology.get("channel_activity", {}).get(channel, False)
            ],
        }

    def telemetry_window(self, *, traces: list[dict[str, Any]], session_id: str | None, sources: dict[str, Any]) -> dict[str, Any]:
        log_channels = sources.get("log_channels") or {}
        recent_trace_ids = [trace.get("trace_id") for trace in traces[:12] if trace.get("trace_id")]
        if not recent_trace_ids:
            recent_trace_ids = [trace.get("trace_id") for trace in sources.get("recent_teacher_traces", [])[:12] if trace.get("trace_id")]
        return {
            "trace_count": len(traces),
            "horizon": f"recent-{len(traces)}",
            "scope": "session" if session_id else "global",
            "fully_bound": bool(traces),
            "recent_trace_ids": recent_trace_ids,
            "log_channels": log_channels,
            "source_status": sources.get("source_status", {}),
        }

    def teacher_evidence_refs(self, teacher_visibility: dict[str, Any]) -> dict[str, list[str]]:
        return {
            "bundle_ids": [item.get("bundle_id") for item in teacher_visibility.get("evidence_bundles", [])[:12] if item.get("bundle_id")],
            "disagreement_ids": [item.get("artifact_id") for item in teacher_visibility.get("disagreement_artifacts", [])[:12] if item.get("artifact_id")],
            "scorecard_ids": [item.get("scorecard_id") for item in teacher_visibility.get("scorecards", [])[:12] if item.get("scorecard_id")],
            "trend_ids": [item.get("trend_id") for item in teacher_visibility.get("trend_scorecards", [])[:12] if item.get("trend_id")],
        }

    def foundry_evidence_refs(self, teacher_visibility: dict[str, Any]) -> dict[str, list[str]]:
        return {
            "fleet_summary_ids": [item.get("summary_id") for item in teacher_visibility.get("fleet_summaries", [])[:12] if item.get("summary_id")],
            "cohort_ids": [item.get("cohort_id") for item in teacher_visibility.get("cohort_scorecards", [])[:12] if item.get("cohort_id")],
            "retirement_shadow_ids": [item.get("record_id") for item in teacher_visibility.get("retirement_shadow_log", [])[:12] if item.get("record_id")],
        }

    def inspection_controls(self, teacher_visibility: dict[str, Any]) -> dict[str, Any]:
        controls = teacher_visibility.get("inspection_controls", {})
        compare_refs = dict(controls.get("compare_refs", {}))
        compare_refs.update(
            {
                "disagreement_compare": "/ops/brain/visualizer/disagreements/compare",
                "replacement_compare": "/ops/brain/visualizer/replacement-readiness/compare",
                "route_compare": "/ops/brain/visualizer/route-activity/compare",
                "visualizer_replay": "/ops/brain/visualizer/replay",
            }
        )
        return {
            "registry_layers": controls.get("registry_layers", []),
            "available_subjects": controls.get("available_subjects", []),
            "available_teacher_pairs": controls.get("available_teacher_pairs", []),
            "available_fleets": controls.get("available_fleets", []),
            "available_windows": controls.get("available_windows", []),
            "compare_refs": compare_refs,
        }

    def filter_catalog(
        self,
        *,
        snapshot: dict[str, Any],
        teacher_visibility: dict[str, Any],
        recent_trace: dict[str, Any],
        safe_mode_physiology: dict[str, Any],
    ) -> dict[str, Any]:
        bundle_ids = [item.get("bundle_id") for item in teacher_visibility.get("evidence_bundles", []) if item.get("bundle_id")]
        disagreement_ids = [item.get("artifact_id") for item in teacher_visibility.get("disagreement_artifacts", []) if item.get("artifact_id")]
        replacement_ids = [item.get("report_id") for item in teacher_visibility.get("replacement_readiness_reports", []) if item.get("report_id")]
        scorecards = teacher_visibility.get("scorecards", [])
        trends = teacher_visibility.get("trend_scorecards", [])
        takeover_trends = teacher_visibility.get("takeover_trends", [])
        promotions = snapshot.get("promotions") or {}
        foundry = snapshot.get("foundry") or {}
        benchmark_families = sorted(
            {
                value
                for value in [
                    *[item.get("benchmark_family_id") for item in scorecards],
                    *[item.get("benchmark_family_id") for item in trends],
                    *[item.get("benchmark_family") for item in teacher_visibility.get("disagreement_artifacts", [])],
                    (recent_trace.get("teacher_provenance") or {}).get("benchmark_family"),
                ]
                if value
            }
        )
        hardware_classes = sorted(
            {
                value
                for value in [
                    *[item.get("hardware_class") for item in teacher_visibility.get("fleet_summaries", [])],
                    *[item.get("hardware_class") for item in teacher_visibility.get("cohort_scorecards", [])],
                ]
                if value
            }
        )
        takeover_statuses = sorted(
            {
                value
                for value in [
                    safe_mode_physiology.get("retry_state"),
                    *[item.get("decision") for item in teacher_visibility.get("retirement_shadow_log", [])],
                    *[item.get("replacement_mode") for item in teacher_visibility.get("replacement_readiness_reports", [])],
                ]
                if value
            }
        )
        return {
            "registry_layers": teacher_visibility.get("inspection_controls", {}).get("registry_layers", []),
            "expert_capsules": teacher_visibility.get("inspection_controls", {}).get("available_subjects", []),
            "teacher_pairs": teacher_visibility.get("inspection_controls", {}).get("available_teacher_pairs", []),
            "promotion_kinds": sorted(
                {
                    item.get("candidate", {}).get("candidate_kind")
                    for item in promotions.get("items", [])
                    if item.get("candidate", {}).get("candidate_kind")
                }
            ),
            "takeover_statuses": takeover_statuses,
            "benchmark_families": benchmark_families,
            "threshold_sets": teacher_visibility.get("threshold_metadata", {}).get("threshold_sets", []),
            "evidence_bundle_ids": bundle_ids[:24],
            "disagreement_artifact_ids": disagreement_ids[:24],
            "replacement_readiness_ids": replacement_ids[:24],
            "fleet_summary_ids": [item.get("summary_id") for item in teacher_visibility.get("fleet_summaries", [])[:24] if item.get("summary_id")],
            "cohort_ids": [item.get("cohort_id") for item in teacher_visibility.get("cohort_scorecards", [])[:24] if item.get("cohort_id")],
            "takeover_trend_ids": [item.get("trend_id") for item in takeover_trends[:24] if item.get("trend_id")],
            "lineages": ["live-derived", "dream-derived", "blended-derived"],
            "recent_trace_windows": [6, 12, 24, 48],
            "safe_mode_postures": ["stable", "fallback-path-active", "retry-burst", "contracted", "thermal-elevated", "vram-unbound"],
            "hardware_classes": hardware_classes,
            "defaults": {
                "registry_layer": (recent_trace.get("teacher_provenance") or {}).get("registry_layer"),
                "expert_capsule": recent_trace.get("selected_expert"),
                "trace_window": 24,
                "safe_mode_posture": "contracted" if safe_mode_physiology.get("safe_mode") else safe_mode_physiology.get("retry_state", "stable"),
            },
            "foundry_counts": {
                "native_takeover": len(foundry.get("native_takeover", [])),
                "replacement_readiness": len(replacement_ids),
            },
        }

    def diff_catalog(self, *, teacher_visibility: dict[str, Any], filter_catalog: dict[str, Any]) -> dict[str, Any]:
        return {
            "bundle_diff_endpoint": "/ops/brain/teachers/evidence/diff",
            "cohort_compare_endpoint": "/ops/brain/teachers/cohorts/compare",
            "disagreement_compare_endpoint": "/ops/brain/visualizer/disagreements/compare",
            "replacement_compare_endpoint": "/ops/brain/visualizer/replacement-readiness/compare",
            "route_compare_endpoint": "/ops/brain/visualizer/route-activity/compare",
            "available_bundle_ids": filter_catalog.get("evidence_bundle_ids", []),
            "available_disagreement_ids": filter_catalog.get("disagreement_artifact_ids", []),
            "available_replacement_readiness_ids": filter_catalog.get("replacement_readiness_ids", []),
            "available_windows": teacher_visibility.get("inspection_controls", {}).get("available_windows", []),
        }

    def replay_catalog(self, *, replay_frames: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "endpoint": "/ops/brain/visualizer/replay",
            "available": bool(replay_frames),
            "frame_count": len(replay_frames),
            "latest_frame_id": replay_frames[0]["frame_id"] if replay_frames else None,
            "available_windows": [6, 12, 24],
        }

    def performance_profile(
        self,
        *,
        snapshot: dict[str, Any],
        safe_mode_physiology: dict[str, Any],
        telemetry_window: dict[str, Any],
        sources: dict[str, Any],
    ) -> dict[str, Any]:
        return self.performance.build_profile(
            snapshot=snapshot,
            safe_mode_physiology=safe_mode_physiology,
            telemetry_window=telemetry_window,
            source_status=sources.get("source_status", {}),
        )

    def replay_frames(
        self,
        *,
        snapshot: dict[str, Any],
        traces: list[dict[str, Any]],
        session_id: str | None,
        limit: int,
        sources: dict[str, Any],
    ) -> list[dict[str, Any]]:
        runtime_summary = sources.get("runtime_summary") or snapshot.get("runtime") or {}
        frames: list[dict[str, Any]] = []
        for index, trace in enumerate(self._route_records(traces=traces, sources=sources)[:limit]):
            provenance = trace.get("teacher_provenance") or {}
            subject = (provenance.get("routing_decision") or {}).get("subject") or trace.get("selected_expert") or provenance.get("expert")
            physiology = self.safe_mode_physiology(recent_trace=trace, traces=traces[index:index + 6], sources=sources)
            frame_link = self.link_activity(traces=[trace], snapshot=snapshot, sources=sources)
            frame_loop = self.loop_activity(traces=[trace], snapshot=snapshot, sources=sources)
            frame_evidence = {
                "teacher": {"intensity": self._cap(1 if provenance else 0, ceiling=1.0), "refs": [value for value in [provenance.get("bundle_id")] if value]},
                "promotion": {"intensity": self._cap(len(trace.get("promotion_references") or []), ceiling=2.0), "refs": trace.get("promotion_references") or []},
                "takeover": {"intensity": self._cap(1 if provenance.get("native_takeover_candidate_id") else 0, ceiling=1.0), "refs": [value for value in [provenance.get("native_takeover_candidate_id")] if value]},
                "disagreement": {"intensity": self._cap(1 if provenance.get("arbitration_result") else 0, ceiling=1.0), "refs": [value for value in [provenance.get("arbitration_result")] if value]},
            }
            frames.append(
                {
                    "frame_id": f"replay::{trace.get('trace_id', index)}",
                    "trace_id": trace.get("trace_id"),
                    "session_id": trace.get("session_id", session_id),
                    "created_at": trace.get("created_at") or trace.get("started_at"),
                    "selected_expert": subject,
                    "lineage": provenance.get("dream_lineage") or ("dream-derived" if provenance.get("dream_derived") else "live-derived"),
                    "source_ref": {
                        "provider_chain": self._provider_chain(sources),
                        "runtime_name": trace.get("runtime_name") or (runtime_summary.get("quantization_decision") or {}).get("model_id"),
                    },
                    "refs": {
                        "promotion_references": trace.get("promotion_references") or [],
                        "native_takeover_candidate_id": provenance.get("native_takeover_candidate_id"),
                    },
                    "overlay": {
                        "active_subjects": [subject] if subject else [],
                        "route_activity": {
                            "trace_id": trace.get("trace_id"),
                            "selected_ao": trace.get("selected_ao"),
                            "selected_agent": trace.get("selected_agent"),
                            "selected_expert": trace.get("selected_expert"),
                            "graph_contribution_count": (trace.get("metrics") or {}).get("graph_contribution_count", 0),
                        },
                        "link_activity": frame_link,
                        "loop_activity": frame_loop,
                        "evidence_activity": frame_evidence,
                        "physiology_activity": self.physiology_activity(safe_mode_physiology=physiology, traces=[trace]),
                    },
                }
            )
        return frames

    def route_window_summary(self, *, traces: list[dict[str, Any]], window: int, sources: dict[str, Any]) -> dict[str, Any]:
        loop_activity = self.loop_activity(traces=traces, snapshot={}, sources=sources)
        link_activity = self.link_activity(traces=traces, snapshot={}, sources=sources)
        physiology = self.physiology_activity(
            safe_mode_physiology=self.safe_mode_physiology(
                recent_trace=traces[0] if traces else {},
                traces=traces,
                sources=sources,
            ),
            traces=traces,
        )
        active_subjects = sorted(
            {
                (trace.get("teacher_provenance") or {}).get("expert")
                or (trace.get("teacher_provenance") or {}).get("routing_decision", {}).get("subject")
                or trace.get("selected_expert")
                for trace in traces
                if (
                    (trace.get("teacher_provenance") or {}).get("expert")
                    or (trace.get("teacher_provenance") or {}).get("routing_decision", {}).get("subject")
                    or trace.get("selected_expert")
                )
            }
        )
        return {
            "window": window,
            "trace_count": len(traces),
            "active_subjects": active_subjects,
            "link_activity": link_activity,
            "loop_activity": loop_activity,
            "physiology_activity": physiology,
        }

    def scene_delta(self, *, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        left_subjects = left.get("link_activity", {}).get("core_to_capsule", {})
        right_subjects = right.get("link_activity", {}).get("core_to_capsule", {})
        all_subjects = sorted({*left_subjects.keys(), *right_subjects.keys()})
        subject_delta = []
        for subject in all_subjects:
            delta = round(float(right_subjects.get(subject, {}).get("intensity", 0.0)) - float(left_subjects.get(subject, {}).get("intensity", 0.0)), 3)
            if delta != 0:
                subject_delta.append({"subject": subject, "delta": delta})
        subject_delta.sort(key=lambda item: abs(item["delta"]), reverse=True)

        left_edges = left.get("link_activity", {}).get("edges", {})
        right_edges = right.get("link_activity", {}).get("edges", {})
        edge_delta = []
        for edge_id in sorted({*left_edges.keys(), *right_edges.keys()}):
            delta = round(float(right_edges.get(edge_id, {}).get("intensity", 0.0)) - float(left_edges.get(edge_id, {}).get("intensity", 0.0)), 3)
            if delta != 0:
                edge_delta.append({"link_id": edge_id, "delta": delta})
        edge_delta.sort(key=lambda item: abs(item["delta"]), reverse=True)
        return {
            "hot_subjects": subject_delta[:12],
            "hot_links": edge_delta[:16],
            "left_active_subjects": left.get("active_subjects", []),
            "right_active_subjects": right.get("active_subjects", []),
        }

    def evidence_scene_delta(self, *, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        subject_candidates = [left.get("subject"), right.get("subject")]
        subjects = [subject for subject in subject_candidates if subject]
        hot_links = []
        for index, subject in enumerate(subjects):
            signed_delta = 1.0 if index == 1 else -1.0
            hot_links.append({"link_id": f"core::{subject}", "delta": signed_delta})
            if left.get("arbitration_result") or right.get("arbitration_result"):
                hot_links.append({"link_id": f"critique::{subject}", "delta": round(signed_delta * 0.72, 3)})
        return {
            "hot_subjects": [{"subject": subject, "delta": 1.0 if index == 1 else -1.0} for index, subject in enumerate(subjects)],
            "hot_links": hot_links[:12],
            "refs": {
                "left": left.get("bundle_id") or left.get("artifact_id") or left.get("report_id"),
                "right": right.get("bundle_id") or right.get("artifact_id") or right.get("report_id"),
            },
        }

    def cohort_scene_delta(self, *, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        subject = right.get("subject") or left.get("subject")
        if not subject:
            return {
                "hot_subjects": [],
                "hot_links": [],
                "refs": {
                    "left": left.get("cohort_id"),
                    "right": right.get("cohort_id"),
                },
            }
        stability_delta = round(float(right.get("stability_score", 0.0)) - float(left.get("stability_score", 0.0)), 3)
        outperformance_delta = round(
            float(right.get("outperformance_consistency", 0.0)) - float(left.get("outperformance_consistency", 0.0)),
            3,
        )
        primary_delta = outperformance_delta if outperformance_delta != 0 else stability_delta
        hot_links = [{"link_id": f"core::{subject}", "delta": primary_delta}]
        hot_links.extend(self._collaboration_delta_links(subject=subject, delta=round(primary_delta * 0.58, 3)))
        return {
            "hot_subjects": [{"subject": subject, "delta": primary_delta}],
            "hot_links": hot_links[:12],
            "refs": {
                "left": left.get("cohort_id"),
                "right": right.get("cohort_id"),
                "fleet_id": right.get("fleet_id") or left.get("fleet_id"),
            },
        }

    def provider_catalog(self, sources: dict[str, Any]) -> dict[str, Any]:
        providers = sources.get("source_status", {}).get("providers", [])
        bound_count = sum(1 for provider in providers if provider.get("bound"))
        degraded_count = sum(1 for provider in providers if not provider.get("bound"))
        signal_count = sum(int(provider.get("signal_count", 0) or 0) for provider in providers)
        return {
            "providers": providers,
            "log_channels": sources.get("log_channels", {}),
            "summary": {
                "provider_count": len(providers),
                "bound_count": bound_count,
                "degraded_count": degraded_count,
                "signal_count": signal_count,
                "bound_ratio": sources.get("source_status", {}).get("bound_ratio", 0.0),
                "health": "healthy" if providers and bound_count == len(providers) else ("degraded" if bound_count else "unbound"),
                "kinds": [provider.get("kind") for provider in providers if provider.get("kind")],
                "latest_trace_id": next((provider.get("latest_trace_id") for provider in providers if provider.get("latest_trace_id")), None),
            },
        }

    def _route_records(self, *, traces: list[dict[str, Any]], sources: dict[str, Any]) -> list[dict[str, Any]]:
        if traces:
            return traces
        recent_teacher_traces = sources.get("recent_teacher_traces") or []
        if recent_teacher_traces:
            return [
                {
                    "trace_id": record.get("trace_id"),
                    "session_id": record.get("session_id"),
                    "selected_expert": record.get("selected_expert") or record.get("subject"),
                    "teacher_provenance": {
                        "registry_layer": record.get("registry_layer"),
                        "selected_teacher_roles": record.get("selected_teacher_roles", {}),
                        "arbitration_result": record.get("arbitration_result"),
                        "benchmark_family": record.get("benchmark_family"),
                        "threshold_set_id": record.get("threshold_set_id"),
                        "native_takeover_candidate_id": record.get("native_takeover_candidate_id"),
                    },
                    "promotion_references": [],
                    "metrics": {"graph_contribution_count": 0, "fallback_used": False},
                }
                for record in recent_teacher_traces
            ]
        return sources.get("simulated_trace_records") or []

    def _capsule_subjects(self) -> list[str]:
        return [node.subject for node in self.scene.nodes if node.node_type == "capsule" and node.subject]

    def _trace_weight(self, index: int) -> float:
        return max(0.18, round(1.0 - (index * 0.07), 3))

    def _cap(self, value: float | int, *, ceiling: float) -> float:
        if ceiling <= 0:
            return 0.0
        return round(min(1.0, float(value) / ceiling), 3)

    def _append_ref(self, refs: list[str], value: str | None) -> None:
        if value and value not in refs and len(refs) < 8:
            refs.append(value)

    def _provider_chain(self, sources: dict[str, Any]) -> list[str]:
        return [provider["provider_id"] for provider in sources.get("source_status", {}).get("providers", []) if provider.get("bound")]

    def _collaboration_delta_links(self, *, subject: str, delta: float) -> list[dict[str, Any]]:
        if delta == 0:
            return []
        link_ids: list[dict[str, Any]] = []
        for group in self.scene.manifest.get("collaboration_groups", []):
            if subject not in (group.get("subjects") or []):
                continue
            group_id = group.get("group_id")
            for link in self.scene.links:
                if (link.meta or {}).get("group_id") == group_id:
                    link_ids.append({"link_id": link.link_id, "delta": delta})
        return link_ids[:8]
