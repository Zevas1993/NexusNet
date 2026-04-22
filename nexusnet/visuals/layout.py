from __future__ import annotations

from collections import defaultdict
import json
import math
import shutil
from pathlib import Path
from typing import Any

import yaml

from .schema import (
    ExpertTopology,
    OverlayBinding,
    SceneBundle,
    SceneLink,
    SceneLoop,
    SceneNode,
    VisualManifest,
    VisualMode,
    VisualizerOverlayState,
)
from .telemetry import VisualizerTelemetryAdapter


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


class NexusVisualizerCompiler:
    def __init__(self, config_dir: Path | None = None):
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).resolve().parent
        self.manifest = VisualManifest.model_validate(self._load_yaml("visual_manifest.yaml"))
        modes_payload = self._load_yaml("modes.yaml")
        topologies_payload = self._load_yaml("expert_topologies.yaml")
        self.modes = [VisualMode.model_validate(item) for item in modes_payload.get("modes", [])]
        self.topologies = {
            subject: ExpertTopology.model_validate({"subject": subject, **payload})
            for subject, payload in topologies_payload.get("experts", {}).items()
        }

    def _load_yaml(self, name: str) -> dict[str, Any]:
        with (self.config_dir / name).open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
        return payload if payload is not None else {}

    def compile_scene(self) -> SceneBundle:
        nodes: list[SceneNode] = []
        links: list[SceneLink] = []
        loops: list[SceneLoop] = []
        overlay_bindings: list[OverlayBinding] = []

        core_cfg = self.manifest.core
        layout_cfg = self.manifest.layout
        roster = self.manifest.capsules.get("authoritative_core_roster", [])
        capsule_radius = float(layout_cfg.get("capsule_radius", 96))
        radius_x = float(layout_cfg.get("capsule_orbit_radius_x", 760))
        radius_y = float(layout_cfg.get("capsule_orbit_radius_y", 510))

        core_node = SceneNode(
            node_id=core_cfg.get("node_id", "nexus-core"),
            node_type="core",
            label=core_cfg.get("label", "NexusNet Core"),
            x=float(layout_cfg.get("center", [0, 0])[0]),
            y=float(layout_cfg.get("center", [0, 0])[1]),
            radius=float(core_cfg.get("ring_radii", [88, 148, 214])[-1]),
            internal_nodes=self._core_internal_nodes(core_cfg),
            meta={
                "neural_layer_labels": core_cfg.get("neural_layer_labels", []),
                "ring_radii": core_cfg.get("ring_radii", []),
                "neural_bus_count": core_cfg.get("neural_bus_count", 6),
                "sculpture_density": core_cfg.get("sculpture_density", 48),
            },
        )
        nodes.append(core_node)

        capsule_nodes: dict[str, SceneNode] = {}
        for index, subject in enumerate(roster):
            topology = self.topologies[subject]
            x, y, z = self._capsule_position(index=index, total=len(roster), radius_x=radius_x, radius_y=radius_y)
            node = SceneNode(
                node_id=f"capsule:{subject}",
                node_type="capsule",
                label=topology.display_name,
                subject=subject,
                topology_id=topology.topology_id,
                x=x,
                y=y,
                z=z,
                radius=capsule_radius,
                layer_index=index,
                status_label=topology.canon_status,
                internal_nodes=self._topology_internal_nodes(topology),
                meta={
                    "palette_key": topology.palette_key,
                    "geometry_kind": topology.geometry_kind,
                    "motif_labels": topology.motif_labels,
                    "description": topology.description,
                    "role_hint": topology.role_hint,
                    "auxiliary": topology.auxiliary,
                    "authoritative_core_roster": topology.authoritative_core_roster,
                    "inspect": topology.inspect,
                },
            )
            nodes.append(node)
            capsule_nodes[subject] = node
            links.append(
                SceneLink(
                    link_id=f"core::{subject}",
                    source_id=core_node.node_id,
                    target_id=node.node_id,
                    link_type="core",
                    strength=1.0,
                    meta={"subject": subject},
                )
            )

        critique_subject = layout_cfg.get("critique_broadcast_subject", "critique")
        for subject in roster:
            if subject == critique_subject:
                continue
            links.append(
                SceneLink(
                    link_id=f"critique::{subject}",
                    source_id=f"capsule:{critique_subject}",
                    target_id=f"capsule:{subject}",
                    link_type="critique",
                    strength=0.82,
                    meta={"broadcast": True},
                )
            )

        for group in self.manifest.collaboration_groups:
            subjects = [subject for subject in group.get("subjects", []) if subject in capsule_nodes]
            for left, right in zip(subjects, subjects[1:]):
                links.append(
                    SceneLink(
                        link_id=f"{group['group_id']}::{left}::{right}",
                        source_id=f"capsule:{left}",
                        target_id=f"capsule:{right}",
                        link_type="collaboration",
                        strength=0.74,
                        meta={"group_id": group["group_id"]},
                    )
                )

        for loop_cfg in self.manifest.loop_definitions:
            loops.append(SceneLoop.model_validate(loop_cfg))
            for subject in loop_cfg.get("target_subjects", []):
                if subject not in capsule_nodes:
                    continue
                links.append(
                    SceneLink(
                        link_id=f"{loop_cfg['loop_id']}::{subject}",
                        source_id=core_node.node_id,
                        target_id=f"capsule:{subject}",
                        link_type=loop_cfg["loop_type"],
                        strength=0.55,
                        meta={"loop_id": loop_cfg["loop_id"]},
                    )
                )

        for binding in self.manifest.overlay_channels:
            overlay_bindings.append(OverlayBinding.model_validate(binding))

        return SceneBundle(
            scene_version=self.manifest.schema_version,
            default_mode_id=self.manifest.default_mode_id,
            manifest=self.manifest.model_dump(mode="json"),
            modes=[mode.model_dump(mode="json") for mode in self.modes],
            topologies=[topology.model_dump(mode="json") for topology in self.topologies.values()],
            nodes=nodes,
            links=links,
            loops=loops,
            overlay_bindings=overlay_bindings,
            legend=self.manifest.legend,
        )

    def export_bundle(self, output_dir: Path) -> dict[str, str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        scene = self.compile_scene()
        paths = {
            "scene": output_dir / "scene.json",
            "modes": output_dir / "modes.json",
            "topologies": output_dir / "topologies.json",
            "legend": output_dir / "legend.json",
        }
        paths["scene"].write_text(json.dumps(scene.model_dump(mode="json"), indent=2), encoding="utf-8")
        paths["modes"].write_text(json.dumps([mode.model_dump(mode="json") for mode in self.modes], indent=2), encoding="utf-8")
        paths["topologies"].write_text(
            json.dumps({subject: topology.model_dump(mode="json") for subject, topology in self.topologies.items()}, indent=2),
            encoding="utf-8",
        )
        paths["legend"].write_text(json.dumps(self.manifest.legend, indent=2), encoding="utf-8")
        return {name: str(path) for name, path in paths.items()}

    def bundled_ui_dir(self) -> Path:
        return _repo_root() / "ui" / "visualizer"

    def bundled_legacy_3d_dir(self) -> Path:
        return _repo_root() / "ui" / "3d"

    def _capsule_position(self, *, index: int, total: int, radius_x: float, radius_y: float) -> tuple[float, float, float]:
        angle = ((math.pi * 2) / total) * index - math.pi / 2
        x = math.cos(angle) * radius_x
        y = math.sin(angle) * radius_y
        z = math.sin(angle * 2) * 28
        return (round(x, 3), round(y, 3), round(z, 3))

    def _core_internal_nodes(self, core_cfg: dict[str, Any]) -> list[dict[str, Any]]:
        ring_radii = core_cfg.get("ring_radii", [88, 148, 214])
        internal: list[dict[str, Any]] = []
        for layer_index, radius in enumerate(ring_radii):
            points = 8 + layer_index * 6
            for point_index in range(points):
                angle = ((math.pi * 2) / points) * point_index
                internal.append(
                    {
                        "id": f"core-layer-{layer_index}-{point_index}",
                        "x": round(math.cos(angle) * radius * 0.58, 3),
                        "y": round(math.sin(angle) * radius * 0.58, 3),
                        "kind": "core-neuron",
                        "layer_index": layer_index,
                    }
                )
        return internal

    def _topology_internal_nodes(self, topology: ExpertTopology) -> list[dict[str, Any]]:
        kind = topology.geometry_kind
        budget = topology.neural_node_budget
        if kind == "lattice":
            return self._grid_nodes(topology, cols=5, rows=4, budget=budget)
        if kind == "branching-tree":
            return self._tree_nodes(topology, budget=budget)
        if kind == "comparator":
            return self._dual_lobes(topology, budget=budget, bridge=True)
        if kind == "citation-web":
            return self._ring_web(topology, budget=budget, rings=3)
        if kind == "dual-hemisphere":
            return self._dual_lobes(topology, budget=budget, bridge=False)
        if kind == "braid":
            return self._braid_nodes(topology, budget=budget)
        if kind == "switchboard":
            return self._grid_nodes(topology, cols=4, rows=4, budget=budget, stagger=True)
        if kind == "shield-mesh":
            return self._shield_nodes(topology, budget=budget)
        if kind == "archive-braid":
            return self._braid_nodes(topology, budget=budget, bands=3)
        if kind == "supervisory-halo":
            return self._halo_nodes(topology, budget=budget)
        if kind == "router-fabric":
            return self._hub_spoke_nodes(topology, budget=budget)
        if kind == "syntax-helix":
            return self._helix_nodes(topology, budget=budget)
        if kind == "feature-pyramid":
            return self._pyramid_nodes(topology, budget=budget)
        if kind == "waveform-spiral":
            return self._spiral_nodes(topology, budget=budget)
        if kind == "rollout-orbits":
            return self._orbit_nodes(topology, budget=budget)
        if kind == "scaffold-lattice":
            return self._grid_nodes(topology, cols=4, rows=5, budget=budget)
        if kind == "ladder-checkpoints":
            return self._ladder_nodes(topology, budget=budget)
        if kind == "funnel-cones":
            return self._funnel_nodes(topology, budget=budget)
        if kind == "chronology-rings":
            return self._ring_web(topology, budget=budget, rings=4)
        if kind == "synthesis-grid":
            return self._grid_nodes(topology, cols=4, rows=4, budget=budget)
        return self._ring_web(topology, budget=budget, rings=max(2, topology.layer_count))

    def _grid_nodes(self, topology: ExpertTopology, *, cols: int, rows: int, budget: int, stagger: bool = False) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        count = 0
        for row in range(rows):
            for col in range(cols):
                if count >= budget:
                    return nodes
                x = -52 + col * (104 / max(cols - 1, 1))
                if stagger and row % 2:
                    x += 10
                y = -42 + row * (84 / max(rows - 1, 1))
                nodes.append({"id": f"{topology.subject}-{count}", "x": round(x, 3), "y": round(y, 3), "kind": topology.geometry_kind})
                count += 1
        return nodes

    def _tree_nodes(self, topology: ExpertTopology, *, budget: int) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        levels = [[(0, -54)], [(-34, -12), (34, -12)], [(-52, 24), (0, 18), (52, 24)], [(-62, 58), (-20, 52), (20, 52), (62, 58)]]
        for count, (x, y) in enumerate(point for level in levels for point in level):
            if count >= budget:
                break
            nodes.append({"id": f"{topology.subject}-{count}", "x": x, "y": y, "kind": topology.geometry_kind})
        return nodes

    def _dual_lobes(self, topology: ExpertTopology, *, budget: int, bridge: bool) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        half = max(4, budget // 2)
        for side, x_bias in enumerate((-28, 28)):
            for index in range(half):
                if len(nodes) >= budget:
                    break
                angle = ((math.pi * 2) / half) * index
                x = x_bias + math.cos(angle) * 22
                y = math.sin(angle) * 34
                nodes.append({"id": f"{topology.subject}-{len(nodes)}", "x": round(x, 3), "y": round(y, 3), "kind": topology.geometry_kind, "side": side})
        if bridge and len(nodes) < budget:
            nodes.append({"id": f"{topology.subject}-{len(nodes)}", "x": 0, "y": 0, "kind": "bridge"})
        return nodes

    def _ring_web(self, topology: ExpertTopology, *, budget: int, rings: int) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        used = 0
        for ring_index in range(rings):
            count = max(4, budget // rings)
            radius = 18 + ring_index * 18
            for point_index in range(count):
                if used >= budget:
                    return nodes
                angle = ((math.pi * 2) / count) * point_index
                nodes.append(
                    {
                        "id": f"{topology.subject}-{used}",
                        "x": round(math.cos(angle) * radius, 3),
                        "y": round(math.sin(angle) * radius, 3),
                        "kind": topology.geometry_kind,
                        "ring_index": ring_index,
                    }
                )
                used += 1
        return nodes

    def _braid_nodes(self, topology: ExpertTopology, *, budget: int, bands: int = 2) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        for index in range(budget):
            t = index / max(budget - 1, 1)
            band = index % bands
            x = math.sin(t * math.pi * 2 + band * math.pi / bands) * (28 + band * 8)
            y = -54 + t * 108
            nodes.append({"id": f"{topology.subject}-{index}", "x": round(x, 3), "y": round(y, 3), "kind": topology.geometry_kind, "band": band})
        return nodes

    def _shield_nodes(self, topology: ExpertTopology, *, budget: int) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        shell = [(-42, -8), (-28, -42), (0, -54), (28, -42), (42, -8), (24, 40), (0, 54), (-24, 40)]
        for index, (x, y) in enumerate(shell):
            if len(nodes) >= budget:
                break
            nodes.append({"id": f"{topology.subject}-{index}", "x": x, "y": y, "kind": "shield"})
        while len(nodes) < budget:
            offset = len(nodes) - len(shell)
            nodes.append({"id": f"{topology.subject}-{len(nodes)}", "x": (offset % 3 - 1) * 18, "y": -6 + (offset // 3) * 18, "kind": topology.geometry_kind})
        return nodes

    def _halo_nodes(self, topology: ExpertTopology, *, budget: int) -> list[dict[str, Any]]:
        nodes = self._dual_lobes(topology, budget=max(10, budget - 6), bridge=True)
        halo_count = budget - len(nodes)
        for index in range(max(0, halo_count)):
            angle = ((math.pi * 2) / max(halo_count, 1)) * index
            nodes.append({"id": f"{topology.subject}-halo-{index}", "x": round(math.cos(angle) * 58, 3), "y": round(math.sin(angle) * 58, 3), "kind": "halo"})
        return nodes

    def _hub_spoke_nodes(self, topology: ExpertTopology, *, budget: int) -> list[dict[str, Any]]:
        nodes = [{"id": f"{topology.subject}-hub", "x": 0, "y": 0, "kind": "hub"}]
        for index in range(1, budget):
            angle = ((math.pi * 2) / max(budget - 1, 1)) * (index - 1)
            radius = 42 if index % 2 else 58
            nodes.append({"id": f"{topology.subject}-{index}", "x": round(math.cos(angle) * radius, 3), "y": round(math.sin(angle) * radius, 3), "kind": topology.geometry_kind})
        return nodes

    def _helix_nodes(self, topology: ExpertTopology, *, budget: int) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        for index in range(budget):
            t = index / max(budget - 1, 1)
            angle = t * math.pi * 4
            x = math.cos(angle) * 26
            y = -52 + t * 104
            nodes.append({"id": f"{topology.subject}-{index}", "x": round(x, 3), "y": round(y, 3), "kind": topology.geometry_kind})
        return nodes

    def _pyramid_nodes(self, topology: ExpertTopology, *, budget: int) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        levels = [1, 2, 3, 4]
        for level_index, count in enumerate(levels):
            y = -50 + level_index * 32
            span = 16 + level_index * 18
            for point_index in range(count):
                if len(nodes) >= budget:
                    return nodes
                x = 0 if count == 1 else -span + point_index * ((span * 2) / (count - 1))
                nodes.append({"id": f"{topology.subject}-{len(nodes)}", "x": round(x, 3), "y": y, "kind": topology.geometry_kind})
        return nodes

    def _spiral_nodes(self, topology: ExpertTopology, *, budget: int) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        for index in range(budget):
            t = index / max(budget - 1, 1)
            angle = t * math.pi * 5
            radius = 10 + t * 42
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            nodes.append({"id": f"{topology.subject}-{index}", "x": round(x, 3), "y": round(y, 3), "kind": topology.geometry_kind})
        return nodes

    def _orbit_nodes(self, topology: ExpertTopology, *, budget: int) -> list[dict[str, Any]]:
        nodes = [{"id": f"{topology.subject}-core", "x": 0, "y": 0, "kind": "sim-core"}]
        remaining = max(0, budget - 1)
        for index in range(remaining):
            angle = ((math.pi * 2) / max(remaining, 1)) * index
            radius = 22 + (index % 3) * 14
            nodes.append({"id": f"{topology.subject}-{index}", "x": round(math.cos(angle) * radius, 3), "y": round(math.sin(angle) * radius, 3), "kind": topology.geometry_kind})
        return nodes

    def _ladder_nodes(self, topology: ExpertTopology, *, budget: int) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        rungs = max(4, budget // 2)
        for rung in range(rungs):
            if len(nodes) >= budget:
                break
            y = -48 + rung * (96 / max(rungs - 1, 1))
            nodes.append({"id": f"{topology.subject}-{len(nodes)}", "x": -22, "y": round(y, 3), "kind": "rail"})
            if len(nodes) >= budget:
                break
            nodes.append({"id": f"{topology.subject}-{len(nodes)}", "x": 22, "y": round(y, 3), "kind": topology.geometry_kind})
        return nodes

    def _funnel_nodes(self, topology: ExpertTopology, *, budget: int) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        levels = [4, 3, 2, 1]
        for level_index, count in enumerate(levels):
            y = -52 + level_index * 34
            span = 46 - level_index * 12
            for point_index in range(count):
                if len(nodes) >= budget:
                    return nodes
                x = 0 if count == 1 else -span + point_index * ((span * 2) / (count - 1))
                nodes.append({"id": f"{topology.subject}-{len(nodes)}", "x": round(x, 3), "y": y, "kind": topology.geometry_kind})
        return nodes


class NexusVisualizerService:
    def __init__(self, *, paths, teacher_registry, wrapper_surface, store):
        self.paths = paths
        self.teacher_registry = teacher_registry
        self.wrapper_surface = wrapper_surface
        self.store = store
        self.compiler = NexusVisualizerCompiler()
        self.scene = self.compiler.compile_scene()
        self.telemetry = VisualizerTelemetryAdapter(
            scene=self.scene,
            store=store,
            paths=paths,
            allow_depth_enhancement=any(mode.allow_threejs_enhancement for mode in self.compiler.modes),
        )
        self.ensure_ui_assets()

    def ensure_ui_assets(self) -> None:
        target_visualizer = self.paths.ui_dir / "visualizer"
        target_visualizer.parent.mkdir(parents=True, exist_ok=True)
        source_visualizer = self.compiler.bundled_ui_dir()
        if source_visualizer.exists() and source_visualizer.resolve() != target_visualizer.resolve():
            shutil.copytree(source_visualizer, target_visualizer, dirs_exist_ok=True)
        source_legacy = self.compiler.bundled_legacy_3d_dir()
        target_legacy = self.paths.ui_dir / "3d"
        if source_legacy.exists() and source_legacy.resolve() != target_legacy.resolve():
            shutil.copytree(source_legacy, target_legacy, dirs_exist_ok=True)

    def scene_payload(self) -> dict[str, Any]:
        return self.scene.model_dump(mode="json")

    def state(self, session_id: str | None = None) -> dict[str, Any]:
        snapshot = self.wrapper_surface.snapshot(session_id=session_id)
        traces = self._recent_traces(session_id=session_id, limit=24)
        sources = self.telemetry.collect_sources(snapshot=snapshot, traces=traces, session_id=session_id)
        replay_frames = self._build_replay_frames(snapshot=snapshot, traces=traces, session_id=session_id, limit=12, sources=sources)
        overlay = self._build_overlay(snapshot=snapshot, traces=traces, session_id=session_id, replay_frames=replay_frames, sources=sources)
        return {
            "status_label": "LOCKED CANON",
            "scene_version": self.scene.scene_version,
            "static_assets": {
                "scene": "/ui/visualizer/data/scene.json",
                "modes": "/ui/visualizer/data/modes.json",
                "topologies": "/ui/visualizer/data/topologies.json",
                "legend": "/ui/visualizer/data/legend.json",
            },
            "manifest": {
                "visualizer_id": self.scene.manifest["visualizer_id"],
                "title": self.scene.manifest["title"],
                "default_mode_id": self.scene.default_mode_id,
                "default_renderer": self.scene.manifest["default_renderer"],
                "render_policy": self.scene.manifest["render_policy"],
            },
            "overlay_state": overlay.model_dump(mode="json"),
        }

    def replay(self, session_id: str | None = None, limit: int = 12) -> dict[str, Any]:
        snapshot = self.wrapper_surface.snapshot(session_id=session_id)
        traces = self._recent_traces(session_id=session_id, limit=max(limit, 1))
        sources = self.telemetry.collect_sources(snapshot=snapshot, traces=traces, session_id=session_id)
        frames = self._build_replay_frames(snapshot=snapshot, traces=traces, session_id=session_id, limit=limit, sources=sources)
        return {
            "status_label": "LOCKED CANON",
            "scene_version": self.scene.scene_version,
            "session_id": session_id,
            "frame_count": len(frames),
            "frames": frames,
        }

    def compare_disagreements(self, left_artifact_id: str, right_artifact_id: str) -> dict[str, Any]:
        left = self._artifact_by_id(self.store.list_teacher_disagreement_artifacts(limit=500), "artifact_id", left_artifact_id)
        right = self._artifact_by_id(self.store.list_teacher_disagreement_artifacts(limit=500), "artifact_id", right_artifact_id)
        return {
            "status_label": "LOCKED CANON",
            "left": left,
            "right": right,
            "scene_delta": self.telemetry.evidence_scene_delta(left=left, right=right),
            "diff": {
                "subjects": [left.get("subject"), right.get("subject")],
                "registry_layers": [left.get("registry_layer"), right.get("registry_layer")],
                "severity_delta": round(float(right.get("disagreement_severity", 0.0)) - float(left.get("disagreement_severity", 0.0)), 3),
                "arbitration_results": [left.get("arbitration_result"), right.get("arbitration_result")],
                "benchmark_families": [left.get("benchmark_family"), right.get("benchmark_family")],
                "lfm2_lanes": [left.get("lfm2_lane"), right.get("lfm2_lane")],
                "lfm2_bounded": [left.get("lfm2_bounded_ok", True), right.get("lfm2_bounded_ok", True)],
            },
        }

    def compare_replacement_readiness(self, left_report_id: str, right_report_id: str) -> dict[str, Any]:
        left = self._artifact_by_id(self.store.list_replacement_readiness_reports(limit=500), "report_id", left_report_id)
        right = self._artifact_by_id(self.store.list_replacement_readiness_reports(limit=500), "report_id", right_report_id)
        return {
            "status_label": "LOCKED CANON",
            "left": left,
            "right": right,
            "scene_delta": self.telemetry.evidence_scene_delta(left=left, right=right),
            "diff": {
                "subjects": [left.get("subject"), right.get("subject")],
                "teachers": [left.get("teacher_id"), right.get("teacher_id")],
                "replacement_modes": [left.get("replacement_mode"), right.get("replacement_mode")],
                "ready_delta": [left.get("ready", False), right.get("ready", False)],
                "metric_delta": self._metric_delta(left.get("metrics", {}), right.get("metrics", {})),
            },
        }

    def compare_route_activity(self, *, session_id: str | None = None, left_window: int = 6, right_window: int = 24) -> dict[str, Any]:
        limit = max(left_window, right_window, 1)
        traces = self._recent_traces(session_id=session_id, limit=limit)
        sources = self.telemetry.collect_sources(snapshot=self.wrapper_surface.snapshot(session_id=session_id), traces=traces, session_id=session_id)
        left = self._route_window_summary(traces[:left_window], window=left_window, sources=sources)
        right = self._route_window_summary(traces[:right_window], window=right_window, sources=sources)
        return {
            "status_label": "LOCKED CANON",
            "session_id": session_id,
            "left": left,
            "right": right,
            "scene_delta": self.telemetry.scene_delta(left=left, right=right),
            "diff": {
                "active_subject_count_delta": len(right.get("active_subjects", [])) - len(left.get("active_subjects", [])),
                "dream_intensity_delta": round(float(right.get("loop_activity", {}).get("dream", {}).get("intensity", 0.0)) - float(left.get("loop_activity", {}).get("dream", {}).get("intensity", 0.0)), 3),
                "critique_intensity_delta": round(float(right.get("loop_activity", {}).get("critique", {}).get("intensity", 0.0)) - float(left.get("loop_activity", {}).get("critique", {}).get("intensity", 0.0)), 3),
                "retry_intensity_delta": round(float(right.get("physiology_activity", {}).get("retry", {}).get("intensity", 0.0)) - float(left.get("physiology_activity", {}).get("retry", {}).get("intensity", 0.0)), 3),
            },
        }

    def _build_overlay(
        self,
        *,
        snapshot: dict[str, Any],
        traces: list[dict[str, Any]],
        session_id: str | None,
        replay_frames: list[dict[str, Any]],
        sources: dict[str, Any],
    ) -> VisualizerOverlayState:
        recent_trace = snapshot.get("recent_trace") or {}
        teacher_provenance = recent_trace.get("teacher_provenance") or {}
        teacher_visibility = ((snapshot.get("teachers") or {}).get("visibility") or {})
        teacher_roles = teacher_provenance.get("selected_teacher_roles") or {}
        runtime_summary = snapshot.get("runtime") or {}
        brain_runtime_summary = snapshot.get("brain_runtime") or {}
        edge_vision_summary = snapshot.get("vision_edge") or {}
        device_profile = runtime_summary.get("device_profile") or {}
        runtime_selection = recent_trace.get("runtime_selection") or {}
        foundry = snapshot.get("foundry") or {}
        promotions = snapshot.get("promotions") or {}
        active_subjects = sorted(
            {
                subject
                for subject in [recent_trace.get("selected_expert"), teacher_provenance.get("expert")]
                if subject
            }
        )
        safe_mode_physiology = self._safe_mode_physiology(
            runtime_summary=runtime_summary,
            recent_trace=recent_trace,
            device_profile=device_profile,
            traces=traces,
            sources=sources,
        )
        link_activity = self._build_link_activity(traces=traces, snapshot=snapshot, sources=sources)
        loop_activity = self._build_loop_activity(traces=traces, snapshot=snapshot, sources=sources)
        evidence_activity = self._build_evidence_activity(snapshot=snapshot, traces=traces, teacher_visibility=teacher_visibility)
        physiology_activity = self._build_physiology_activity(safe_mode_physiology=safe_mode_physiology, traces=traces)
        telemetry_window = self._build_telemetry_window(traces=traces, session_id=session_id, sources=sources)
        teacher_evidence_refs = self._teacher_evidence_refs(teacher_visibility)
        foundry_evidence_refs = self._foundry_evidence_refs(teacher_visibility)
        inspection_controls = self._inspection_controls(teacher_visibility)
        filter_catalog = self._build_filter_catalog(
            snapshot=snapshot,
            teacher_visibility=teacher_visibility,
            recent_trace=recent_trace,
            safe_mode_physiology=safe_mode_physiology,
        )
        diff_catalog = self._build_diff_catalog(teacher_visibility=teacher_visibility, filter_catalog=filter_catalog)
        performance_profile = self._build_performance_profile(
            snapshot=snapshot,
            safe_mode_physiology=safe_mode_physiology,
            telemetry_window=telemetry_window,
            sources=sources,
        )
        replay_catalog = self._build_replay_catalog(replay_frames=replay_frames)
        latest_retrieval_review = (((snapshot.get("retrieval") or {}).get("promotion_evidence") or [{}])[0]) or {}
        latest_aitune_summary = brain_runtime_summary.get("aitune") or {}
        latest_triattention_summary = ((snapshot.get("assimilation") or {}).get("attention_benchmarks") or {})
        goose_summary = ((snapshot.get("assimilation") or {}).get("goose") or {})
        goose_recipes = (goose_summary.get("recipes") or {})
        goose_recipe_history = (goose_recipes.get("history") or {})
        goose_runbook_history = (goose_recipes.get("runbook_history") or {})
        goose_gateway = (goose_summary.get("gateway") or {})
        goose_gateway_history = (goose_gateway.get("history") or {})
        goose_scheduled = (goose_summary.get("scheduled") or {})
        goose_scheduled_history = (goose_scheduled.get("history") or {})
        goose_scheduled_monitor_artifact = (
            ((goose_scheduled_history.get("latest_artifacts_by_workflow") or {}).get("scheduled-monitor"))
            or (goose_scheduled_history.get("latest_artifact") or {})
        )
        goose_extensions = (goose_summary.get("extensions") or {})
        goose_extension_policy_sets = (goose_summary.get("extension_policy_sets") or {})
        goose_extension_policy_history = (goose_summary.get("extension_policy_history") or {})
        goose_extension_policy_rollouts = (goose_summary.get("extension_policy_rollouts") or {})
        goose_extension_certifications = (goose_summary.get("extension_certifications") or {})
        goose_subagents = (goose_summary.get("subagents") or {})
        goose_acp = (goose_summary.get("acp") or {})
        goose_acp_health = (goose_acp.get("health") or {})
        goose_security = (goose_summary.get("security") or {})
        goose_permissions = (goose_security.get("permissions") or {})
        goose_sandbox = (goose_security.get("sandbox") or {})
        goose_guardrails = (goose_security.get("persistent_guardrails") or {})
        goose_adversary = (goose_security.get("adversary_review") or {})
        goose_compare_controls = self._goose_compare_controls(
            goose_gateway_history=goose_gateway_history,
            goose_extension_policy_history=goose_extension_policy_history,
            goose_extension_certifications=goose_extension_certifications,
            goose_adversary=goose_adversary,
            goose_acp_health=goose_acp_health,
        )
        inspection_controls["goose_compare"] = goose_compare_controls
        diff_catalog["goose_compare"] = self._goose_compare_catalog(goose_compare_controls)

        return VisualizerOverlayState(
            scene_version=self.scene.scene_version,
            active_session_id=session_id,
            active_registry_layer=teacher_provenance.get("registry_layer")
            or ((snapshot.get("teachers") or {}).get("metadata") or {}).get("default_registry_layer"),
            selected_teachers={
                "primary": teacher_roles.get("primary"),
                "secondary": teacher_roles.get("secondary"),
                "critique": teacher_roles.get("critique"),
                "efficiency": teacher_roles.get("efficiency"),
            },
            active_subjects=active_subjects,
            arbitration_result=teacher_provenance.get("arbitration_result"),
            benchmark_refs=[value for value in [teacher_provenance.get("benchmark_family")] if value],
            threshold_refs=[value for value in [teacher_provenance.get("threshold_set_id")] if value],
            route_activity={
                "trace_id": recent_trace.get("trace_id"),
                "selected_ao": recent_trace.get("selected_ao"),
                "selected_agent": recent_trace.get("selected_agent"),
                "selected_expert": recent_trace.get("selected_expert"),
                "retrieval_policy": recent_trace.get("retrieval_policy"),
                "gateway_decision": (recent_trace.get("metrics") or {}).get("gateway_decision"),
                "graph_contribution_count": (recent_trace.get("metrics") or {}).get("graph_contribution_count", 0),
                "rerank_scorecard_ref": (((snapshot.get("retrieval") or {}).get("scorecards") or {}).get("latest_scorecard") or {}).get("scorecard_id"),
                "rerank_promotion_evidence_ref": latest_retrieval_review.get("bundle_id"),
                "rerank_review_report_id": latest_retrieval_review.get("review_report_id"),
                "rerank_review_headline": latest_retrieval_review.get("review_headline"),
                "rerank_review_human_summary": latest_retrieval_review.get("human_summary"),
                "rerank_review_artifact_ref": ((latest_retrieval_review.get("review_artifacts") or {}).get("payload")),
                "rerank_threshold_set_id": latest_retrieval_review.get("threshold_set_id"),
                "rerank_scorecard_passed": latest_retrieval_review.get("scorecard_passed"),
                "rerank_candidate_shift_count": latest_retrieval_review.get("candidate_shift_count", 0),
                "rerank_top_shift_chunk_id": ((latest_retrieval_review.get("top_shift_preview") or {}).get("chunk_id")),
                "rerank_top_shift_delta": ((latest_retrieval_review.get("top_shift_preview") or {}).get("rank_delta")),
                "rerank_provider_badge": ((latest_retrieval_review.get("review_badges") or {}).get("provider")),
                "rerank_evaluator_artifact_count": ((latest_retrieval_review.get("evaluator_artifact_summary") or {}).get("artifact_count", 0)),
                "promotion_references": recent_trace.get("promotion_references") or [],
                "link_activity_ref": "overlay.link_activity",
                "telemetry_window_ref": "overlay.telemetry_window",
            },
            dream_activity={
                "dream_lineage": teacher_provenance.get("dream_lineage"),
                "recent_dream_derived_count": sum(
                    1
                    for trace in self.store.list_traces(limit=40)
                    if (trace.get("teacher_provenance") or {}).get("dream_lineage") == "dream-derived"
                ),
                "loop_activity_ref": "overlay.loop_activity.dream",
            },
            promotion_cues={
                "candidate_count": len(promotions.get("items", [])),
                "candidate_ids": [
                    item.get("candidate", {}).get("candidate_id")
                    for item in promotions.get("items", [])[:12]
                    if item.get("candidate", {}).get("candidate_id")
                ],
                "teacher_evidence_bundle_ids": [
                    item.get("teacher_evidence_bundle_id")
                    for item in promotions.get("teacher_evidence", [])
                    if item.get("teacher_evidence_bundle_id")
                ],
            },
            takeover_cues={
                "native_takeover_count": len(foundry.get("native_takeover", [])),
                "replacement_readiness_ids": [
                    item.get("report_id")
                    for item in teacher_visibility.get("replacement_readiness_reports", [])[:12]
                    if item.get("report_id")
                ],
                "takeover_trend_ids": [
                    item.get("trend_id")
                    for item in teacher_visibility.get("takeover_trends", [])[:12]
                    if item.get("trend_id")
                ],
            },
            runtime_posture={
                "selected_runtime_name": runtime_selection.get("selected_runtime_name")
                or snapshot.get("state", {}).get("selected_runtime_name"),
                "selected_backend_name": snapshot.get("state", {}).get("selected_backend_name"),
                "fallback_runtime_names": runtime_selection.get("fallback_runtime_names") or [],
                "fallback_used": (recent_trace.get("metrics") or {}).get("fallback_used", False),
                "device_profile": device_profile,
                "aitune_provider_health": (((latest_aitune_summary.get("capability") or {}).get("provider_health"))),
                "aitune_supported_lane_status": (((latest_aitune_summary.get("supported_lane_readiness") or {}).get("status"))),
                "aitune_latest_validation_status": ((((latest_aitune_summary.get("latest_validation") or {}).get("payload") or {}).get("current_status"))),
                "aitune_latest_validation_artifact_id": (((latest_aitune_summary.get("latest_validation") or {}).get("artifact_id"))),
                "aitune_skip_reason": ((((latest_aitune_summary.get("latest_validation") or {}).get("payload") or {}).get("skip_reason"))),
                "aitune_latest_execution_plan_id": (((latest_aitune_summary.get("latest_execution_plan") or {}).get("artifact_id"))),
                "aitune_latest_execution_plan_markdown_path": latest_aitune_summary.get("latest_execution_plan_markdown_path"),
                "aitune_latest_runner_artifact_id": (((latest_aitune_summary.get("latest_runner_report") or {}).get("artifact_id"))),
                "aitune_latest_runner_status": ((((latest_aitune_summary.get("latest_runner_report") or {}).get("payload") or {}).get("supported_lane") or {}).get("status")),
                "aitune_latest_benchmark_id": (((latest_aitune_summary.get("latest_benchmark") or {}).get("artifact_id"))),
                "aitune_latest_tuned_artifact_id": (((latest_aitune_summary.get("latest_tuned_artifact") or {}).get("artifact_id"))),
                "edge_vision_default_provider": edge_vision_summary.get("default_provider"),
                "edge_vision_benchmark_case_count": (((edge_vision_summary.get("benchmark_summary") or {}).get("latest_benchmark") or {}).get("case_count")),
                "openjarvis_recommended_preset": ((((snapshot.get("runtime_doctor") or {}).get("recommended_preset")) or {}).get("preset_id")),
                "openjarvis_recommended_runtime": ((((snapshot.get("runtime_doctor") or {}).get("recommended_preset")) or {}).get("recommended_runtime")),
                "openjarvis_skill_catalog_count": ((((snapshot.get("assimilation") or {}).get("openjarvis_runtime") or {}).get("skill_catalog")) or {}).get("package_count"),
                "openjarvis_scheduled_workflow_count": ((((snapshot.get("assimilation") or {}).get("openjarvis_runtime") or {}).get("scheduled_agents")) or {}).get("workflow_count"),
                "openjarvis_cost_energy_wh": (((((snapshot.get("assimilation") or {}).get("openjarvis_runtime") or {}).get("cost_energy")) or {}).get("summary") or {}).get("energy_wh"),
                "goose_recipe_count": goose_recipes.get("recipe_count", 0),
                "goose_runbook_count": goose_recipes.get("runbook_count", 0),
                "goose_schedule_compatible_count": len(goose_recipes.get("schedule_compatible_ids", []) or []),
                "goose_recipe_execution_count": goose_recipe_history.get("execution_count", 0),
                "goose_recipe_flow_family_counts": goose_recipe_history.get("flow_family_counts", {}),
                "goose_latest_recipe_execution_id": (((goose_recipe_history.get("latest_execution") or {}).get("execution_id"))),
                "goose_latest_recipe_report_id": goose_recipe_history.get("latest_report_id"),
                "goose_latest_recipe_gateway_resolution_id": goose_recipe_history.get("latest_gateway_resolution_id"),
                "goose_latest_recipe_gateway_execution_id": goose_recipe_history.get("latest_gateway_execution_id"),
                "goose_latest_recipe_gateway_report_id": goose_recipe_history.get("latest_gateway_report_id"),
                "goose_latest_recipe_adversary_report_id": (((goose_recipe_history.get("latest_adversary_report_ids") or [None])[0])),
                "goose_latest_recipe_linked_trace_id": (((goose_recipe_history.get("latest_linked_trace_ids") or [None])[0])),
                "goose_latest_recipe_linked_report_id": next(
                    (
                        report_id
                        for report_id in (goose_recipe_history.get("latest_linked_report_ids") or [])
                        if str(report_id).startswith("recipereport_")
                    ),
                    ((goose_recipe_history.get("latest_linked_report_ids") or [None])[0]),
                ),
                "goose_runbook_execution_count": goose_runbook_history.get("execution_count", 0),
                "goose_runbook_flow_family_counts": goose_runbook_history.get("flow_family_counts", {}),
                "goose_latest_runbook_execution_id": (((goose_runbook_history.get("latest_execution") or {}).get("execution_id"))),
                "goose_latest_runbook_report_id": goose_runbook_history.get("latest_report_id"),
                "goose_latest_runbook_gateway_resolution_id": goose_runbook_history.get("latest_gateway_resolution_id"),
                "goose_latest_runbook_gateway_execution_id": goose_runbook_history.get("latest_gateway_execution_id"),
                "goose_latest_runbook_gateway_report_id": goose_runbook_history.get("latest_gateway_report_id"),
                "goose_latest_runbook_adversary_report_id": (((goose_runbook_history.get("latest_adversary_report_ids") or [None])[0])),
                "goose_latest_runbook_linked_trace_id": (((goose_runbook_history.get("latest_linked_trace_ids") or [None])[0])),
                "goose_latest_runbook_linked_report_id": next(
                    (
                        report_id
                        for report_id in (goose_runbook_history.get("latest_linked_report_ids") or [])
                        if str(report_id).startswith("recipereport_")
                    ),
                    ((goose_runbook_history.get("latest_linked_report_ids") or [None])[0]),
                ),
                "goose_gateway_execution_count": goose_gateway_history.get("execution_count", 0),
                "goose_gateway_flow_family_counts": goose_gateway_history.get("flow_family_counts", {}),
                "goose_latest_gateway_execution_id": (((goose_gateway_history.get("latest_execution") or {}).get("execution_id"))),
                "goose_latest_gateway_report_id": goose_gateway_history.get("latest_report_id"),
                "goose_latest_gateway_resolution_id": goose_gateway_history.get("latest_resolution_id"),
                "goose_latest_gateway_flow_families": goose_gateway_history.get("latest_flow_families", []),
                "goose_latest_gateway_extension_bundle_id": (((goose_gateway_history.get("latest_extension_bundle_ids") or [None])[0])),
                "goose_latest_gateway_policy_set_id": (((goose_gateway_history.get("latest_extension_policy_set_ids") or [None])[0])),
                "goose_latest_gateway_bundle_family": (((goose_gateway_history.get("latest_extension_bundle_families") or [None])[0])),
                "goose_latest_gateway_trace_id": (((goose_gateway_history.get("latest_linked_trace_ids") or [None])[0])),
                "goose_latest_gateway_linked_report_id": (((goose_gateway_history.get("latest_linked_report_ids") or [None])[0])),
                "goose_latest_gateway_adversary_report_id": (((goose_gateway_history.get("latest_adversary_report_ids") or [None])[0])),
                "goose_scheduled_history_count": goose_scheduled_history.get("history_count", 0),
                "goose_latest_scheduled_artifact_id": goose_scheduled_monitor_artifact.get("artifact_id"),
                "goose_latest_scheduled_report_id": (((goose_scheduled_monitor_artifact.get("report") or {}).get("report_id"))),
                "goose_latest_scheduled_execution_id": ((goose_scheduled_monitor_artifact.get("linked_execution_ids") or [None])[0]),
                "goose_latest_scheduled_linked_trace_id": (((goose_scheduled_monitor_artifact.get("linked_trace_ids")) or [None])[0]),
                "goose_latest_scheduled_linked_report_id": (
                    goose_scheduled_monitor_artifact.get("source_report_id")
                    or next(
                        (
                            report_id
                            for report_id in (goose_scheduled_monitor_artifact.get("linked_report_ids") or [])
                            if str(report_id).startswith("recipereport_")
                        ),
                        (((goose_scheduled_monitor_artifact.get("linked_report_ids")) or [None])[0]),
                    )
                ),
                "goose_latest_scheduled_gateway_resolution_id": (((goose_scheduled_monitor_artifact.get("gateway_resolution_ids")) or [None])[0]),
                "goose_extension_count": goose_extensions.get("extension_count", 0),
                "goose_enabled_extension_count": goose_extensions.get("enabled_count", 0),
                "goose_extension_approval_required_count": goose_extensions.get("approval_required_count", 0),
                "goose_extension_high_risk_count": goose_extensions.get("high_risk_bundle_count", 0),
                "goose_extension_policy_set_count": goose_extensions.get("policy_set_count", 0),
                "goose_extension_bundle_family_count": goose_extensions.get("bundle_family_count", 0),
                "goose_latest_extension_bundle_id": goose_extensions.get("latest_bundle_id"),
                "goose_latest_extension_bundle_artifact_id": goose_extensions.get("latest_bundle_artifact_id"),
                "goose_latest_extension_bundle_report_id": goose_extensions.get("latest_bundle_report_id"),
                "goose_latest_extension_policy_set_id": goose_extensions.get("latest_policy_set_id"),
                "goose_latest_extension_policy_set_version": goose_extensions.get("latest_policy_set_version"),
                "goose_latest_extension_bundle_family": goose_extensions.get("latest_bundle_family"),
                "goose_latest_policy_status": goose_extensions.get("latest_policy_status"),
                "goose_latest_policy_history_artifact_id": goose_extensions.get("latest_policy_history_artifact_id"),
                "goose_latest_policy_history_report_id": goose_extensions.get("latest_policy_history_report_id"),
                "goose_policy_history_count": goose_extension_policy_history.get("artifact_count", 0),
                "goose_policy_rollout_family_count": goose_extensions.get("policy_rollout_family_count", 0),
                "goose_policy_rollout_status_counts": goose_extensions.get("policy_rollout_status_counts", {}),
                "goose_latest_certification_artifact_id": goose_extensions.get("latest_certification_artifact_id"),
                "goose_latest_certification_report_id": goose_extensions.get("latest_certification_report_id"),
                "goose_latest_certification_status": goose_extensions.get("latest_certification_status"),
                "goose_certification_artifact_count": goose_extension_certifications.get("artifact_count", 0),
                "goose_subagent_run_count": goose_subagents.get("recent_run_count", 0),
                "goose_latest_subagent_run_id": (((goose_subagents.get("latest_run") or {}).get("run_id"))),
                "goose_latest_subagent_gateway_resolution_id": ((((goose_subagents.get("latest_run") or {}).get("gateway_resolution")) or {}).get("resolution_id")),
                "goose_latest_subagent_privilege_review_id": ((((goose_subagents.get("latest_run") or {}).get("privilege_review")) or {}).get("review_id")),
                "goose_acp_provider_count": goose_acp.get("provider_count", 0),
                "goose_acp_enabled": goose_acp.get("enabled", False),
                "goose_acp_ready_count": goose_acp_health.get("ready_count", 0),
                "goose_acp_status_counts": goose_acp_health.get("status_counts", {}),
                "goose_acp_probe_mode_counts": goose_acp_health.get("probe_mode_counts", {}),
                "goose_acp_probe_status_counts": goose_acp_health.get("probe_status_counts", {}),
                "goose_acp_probe_readiness_state_counts": goose_acp_health.get("probe_readiness_state_counts", {}),
                "goose_acp_misconfigured_count": goose_acp_health.get("misconfigured_count", 0),
                "goose_acp_version_mismatch_count": goose_acp_health.get("version_mismatch_count", 0),
                "goose_acp_live_probe_capable_count": goose_acp_health.get("live_probe_capable_count", 0),
                "goose_acp_live_probe_active_count": goose_acp_health.get("live_probe_active_count", 0),
                "goose_acp_simulated_probe_count": goose_acp_health.get("simulated_probe_count", 0),
                "goose_acp_provider_gated_count": goose_acp_health.get("provider_gated_count", 0),
                "goose_acp_blocked_probe_count": goose_acp_health.get("blocked_probe_count", 0),
                "goose_acp_version_compatible_count": goose_acp_health.get("version_compatible_count", 0),
                "goose_acp_feature_compatible_count": goose_acp_health.get("feature_compatible_count", 0),
                "goose_acp_feature_incompatible_count": goose_acp_health.get("feature_incompatible_count", 0),
                "goose_acp_remediation_action_counts": goose_acp_health.get("remediation_action_counts", {}),
                "goose_acp_recommended_action_counts": goose_acp_health.get("recommended_action_counts", {}),
                "goose_acp_config_gap_counts": goose_acp_health.get("config_gap_counts", {}),
                "goose_acp_live_probe_blocker_counts": goose_acp_health.get("live_probe_blocker_counts", {}),
                "goose_acp_compatibility_fixture_count": goose_acp_health.get("compatibility_fixture_count", 0),
                "goose_acp_live_probe_example_count": goose_acp_health.get("live_probe_example_count", 0),
                "goose_permission_mode": (((goose_permissions.get("active_mode") or {}).get("mode_id"))),
                "goose_sandbox_profile": (((goose_sandbox.get("active_profile") or {}).get("profile_id"))),
                "goose_guardrail_count": goose_guardrails.get("enabled_guardrail_count", 0),
                "goose_latest_adversary_review_id": (((goose_adversary.get("latest_review") or {}).get("review_id"))),
                "goose_latest_adversary_decision": (((goose_adversary.get("latest_review") or {}).get("decision"))),
                "goose_latest_adversary_report_id": goose_adversary.get("latest_report_id"),
                "goose_latest_adversary_audit_export_id": goose_adversary.get("latest_audit_export_id"),
                "goose_latest_adversary_trigger_source": (((goose_adversary.get("latest_review") or {}).get("trigger_source"))),
                "goose_adversary_family_counts": goose_adversary.get("family_counts", {}),
                "goose_extension_policy_catalog_count": goose_extension_policy_sets.get("policy_set_count", 0),
                "goose_gateway_compare_ref": (((snapshot.get("assimilation") or {}).get("compare_refs") or {}).get("goose_gateway_history_compare")),
                "goose_policy_history_compare_ref": (((snapshot.get("assimilation") or {}).get("compare_refs") or {}).get("goose_extension_policy_history_compare")),
                "goose_certification_compare_ref": (((snapshot.get("assimilation") or {}).get("compare_refs") or {}).get("goose_extension_certification_compare")),
                "goose_acp_compare_ref": (((snapshot.get("assimilation") or {}).get("compare_refs") or {}).get("goose_acp_provider_compare")),
                "goose_adversary_compare_ref": (((snapshot.get("assimilation") or {}).get("compare_refs") or {}).get("goose_security_adversary_review_compare")),
                "triattention_latest_scorecard_id": ((latest_triattention_summary.get("latest_comparative_scorecard") or {}).get("scorecard_id")),
                "triattention_latest_report_id": ((latest_triattention_summary.get("latest_comparative_scorecard") or {}).get("report_id")),
                "triattention_baseline_count": len(((latest_triattention_summary.get("latest_comparative_scorecard") or {}).get("baseline_providers", []) or [])),
                "triattention_runtime_anchor_count": len(((latest_triattention_summary.get("latest_comparative_summary") or {}).get("runtime_anchor_registry", []) or [])),
                "triattention_runtime_anchor_live_count": (((latest_triattention_summary.get("latest_comparative_summary") or {}).get("runtime_anchor_quality_summary") or {}).get("available_count", 0)),
                "triattention_runtime_anchor_latency_anchored_count": (((latest_triattention_summary.get("latest_comparative_summary") or {}).get("runtime_anchor_quality_summary") or {}).get("latency_anchored_count", 0)),
                "triattention_runtime_anchor_measurement_modes": (((latest_triattention_summary.get("latest_comparative_summary") or {}).get("runtime_anchor_quality_summary") or {}).get("measurement_modes", {})),
                "obliteratus_latest_review_id": (((((snapshot.get("assimilation") or {}).get("obliteratus_safe_boundary") or {}).get("red_team_review")) or {}).get("latest_review") or {}).get("review_id"),
                "obliteratus_quarantine_required": ((((snapshot.get("assimilation") or {}).get("obliteratus_safe_boundary") or {}).get("red_team_review")) or {}).get("quarantine_required"),
                "recommended_render_tier": performance_profile.get("recommended_tier"),
            },
            safe_mode_physiology=safe_mode_physiology,
            link_activity=link_activity,
            loop_activity=loop_activity,
            evidence_activity=evidence_activity,
            physiology_activity=physiology_activity,
            telemetry_window=telemetry_window,
            telemetry_sources=self.telemetry.provider_catalog(sources),
            teacher_evidence_refs=teacher_evidence_refs,
            foundry_evidence_refs=foundry_evidence_refs,
            inspection_controls=inspection_controls,
            filter_catalog=filter_catalog,
            diff_catalog=diff_catalog,
            replay_catalog=replay_catalog,
            performance_profile=performance_profile,
        )

    def _recent_traces(self, *, session_id: str | None, limit: int) -> list[dict[str, Any]]:
        traces = self.store.list_traces(limit=max(limit * 4, limit))
        if session_id:
            scoped = [trace for trace in traces if trace.get("session_id") == session_id]
            if scoped:
                return scoped[:limit]
        return traces[:limit]

    def _safe_mode_physiology(
        self,
        *,
        runtime_summary: dict[str, Any],
        recent_trace: dict[str, Any],
        device_profile: dict[str, Any],
        traces: list[dict[str, Any]],
        sources: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.telemetry.safe_mode_physiology(
            recent_trace=recent_trace,
            traces=traces,
            sources=sources
            or {
                "runtime_summary": runtime_summary,
                "device_profile": device_profile,
                "runtime_candidates": runtime_summary.get("candidates") or [],
            },
        )

    def _build_link_activity(self, *, traces: list[dict[str, Any]], snapshot: dict[str, Any], sources: dict[str, Any] | None = None) -> dict[str, Any]:
        active_sources = sources or self.telemetry.collect_sources(snapshot=snapshot, traces=traces, session_id=None)
        return self.telemetry.link_activity(traces=traces, snapshot=snapshot, sources=active_sources)

    def _build_loop_activity(self, *, traces: list[dict[str, Any]], snapshot: dict[str, Any], sources: dict[str, Any] | None = None) -> dict[str, Any]:
        active_sources = sources or self.telemetry.collect_sources(snapshot=snapshot, traces=traces, session_id=None)
        return self.telemetry.loop_activity(traces=traces, snapshot=snapshot, sources=active_sources)

    def _build_evidence_activity(self, *, snapshot: dict[str, Any], traces: list[dict[str, Any]], teacher_visibility: dict[str, Any]) -> dict[str, Any]:
        return self.telemetry.evidence_activity(snapshot=snapshot, traces=traces, teacher_visibility=teacher_visibility)

    def _build_physiology_activity(self, *, safe_mode_physiology: dict[str, Any], traces: list[dict[str, Any]]) -> dict[str, Any]:
        return self.telemetry.physiology_activity(safe_mode_physiology=safe_mode_physiology, traces=traces)

    def _build_telemetry_window(self, *, traces: list[dict[str, Any]], session_id: str | None, sources: dict[str, Any] | None = None) -> dict[str, Any]:
        active_sources = sources or self.telemetry.collect_sources(snapshot={}, traces=traces, session_id=session_id)
        return self.telemetry.telemetry_window(traces=traces, session_id=session_id, sources=active_sources)

    def _teacher_evidence_refs(self, teacher_visibility: dict[str, Any]) -> dict[str, list[str]]:
        return self.telemetry.teacher_evidence_refs(teacher_visibility)

    def _foundry_evidence_refs(self, teacher_visibility: dict[str, Any]) -> dict[str, list[str]]:
        return self.telemetry.foundry_evidence_refs(teacher_visibility)

    def _inspection_controls(self, teacher_visibility: dict[str, Any]) -> dict[str, Any]:
        return self.telemetry.inspection_controls(teacher_visibility)

    def _build_filter_catalog(
        self,
        *,
        snapshot: dict[str, Any],
        teacher_visibility: dict[str, Any],
        recent_trace: dict[str, Any],
        safe_mode_physiology: dict[str, Any],
    ) -> dict[str, Any]:
        return self.telemetry.filter_catalog(
            snapshot=snapshot,
            teacher_visibility=teacher_visibility,
            recent_trace=recent_trace,
            safe_mode_physiology=safe_mode_physiology,
        )

    def _build_diff_catalog(self, *, teacher_visibility: dict[str, Any], filter_catalog: dict[str, Any]) -> dict[str, Any]:
        return self.telemetry.diff_catalog(teacher_visibility=teacher_visibility, filter_catalog=filter_catalog)

    def _goose_compare_controls(
        self,
        *,
        goose_gateway_history: dict[str, Any],
        goose_extension_policy_history: dict[str, Any],
        goose_extension_certifications: dict[str, Any],
        goose_adversary: dict[str, Any],
        goose_acp_health: dict[str, Any],
    ) -> dict[str, Any]:
        group_filters = [
            {
                "value": "policy-lifecycle",
                "label": "Policy Lifecycle",
                "description": "status, version, rollback, and lineage deltas",
            },
            {
                "value": "certification-state",
                "label": "Certification State",
                "description": "certification, restoration, and lineage state changes",
            },
            {
                "value": "permission-deltas",
                "label": "Permission Deltas",
                "description": "allowed-tool, permission, and privilege drift",
            },
            {
                "value": "approval-fallback",
                "label": "Approval And Fallback",
                "description": "approval posture and fallback-chain changes",
            },
            {
                "value": "acp-readiness",
                "label": "ACP Readiness",
                "description": "probe, capability, version, and remediation deltas",
            },
            {
                "value": "adversary-outcome",
                "label": "Adversary Outcome",
                "description": "risk-family and decision-path changes",
            },
            {
                "value": "gateway-execution-path",
                "label": "Gateway Execution Path",
                "description": "trigger, flow-family, extension, and traceability changes",
            },
            {
                "value": "trace-and-artifacts",
                "label": "Trace And Artifacts",
                "description": "trace, report, and produced-artifact drift",
            },
        ]
        return {
            "gateway_executions": [
                {
                    "value": item.get("execution_id"),
                    "label": (
                        f"{item.get('execution_id')} | "
                        f"{item.get('trigger_source') or 'unknown-trigger'} | "
                        f"{item.get('status') or 'unknown-status'}"
                    ),
                }
                for item in goose_gateway_history.get("items", [])
                if item.get("execution_id")
            ],
            "policy_versions": [
                {
                    "value": f"{item.get('policy_set_id')}@@{item.get('version')}",
                    "label": (
                        f"{item.get('policy_set_id')}@{item.get('version')} | "
                        f"{item.get('status') or 'unknown-status'} | "
                        f"{item.get('bundle_family') or 'unknown-family'}"
                    ),
                }
                for item in goose_extension_policy_history.get("items", [])
                if item.get("policy_set_id") and item.get("version")
            ],
            "certifications": [
                {
                    "value": item.get("artifact_id"),
                    "label": (
                        f"{item.get('artifact_id')} | "
                        f"{item.get('bundle_id') or 'unknown-bundle'} | "
                        f"{item.get('certification_status') or 'unknown-status'}"
                    ),
                }
                for item in goose_extension_certifications.get("items", [])
                if item.get("artifact_id")
            ],
            "adversary_reviews": [
                {
                    "value": item.get("review_id"),
                    "label": (
                        f"{item.get('review_id')} | "
                        f"{item.get('decision') or 'unknown-decision'} | "
                        f"{item.get('trigger_source') or 'unknown-trigger'}"
                    ),
                }
                for item in goose_adversary.get("recent_reviews", [])
                if item.get("review_id")
            ],
            "acp_providers": [
                {
                    "value": item.get("provider_id"),
                    "label": (
                        f"{item.get('provider_id')} | "
                        f"{((item.get('diagnostic') or {}).get('probe_mode')) or 'unknown-probe'} | "
                        f"{((item.get('diagnostic') or {}).get('probe_status')) or 'unknown-status'}"
                    ),
                }
                for item in goose_acp_health.get("providers", [])
                if item.get("provider_id")
            ],
            "group_filters": group_filters,
            "default_expanded_groups": [
                "policy-lifecycle",
                "certification-state",
                "acp-readiness",
            ],
            "collapse_actions": [
                "expand-all",
                "collapse-all",
                "default-expanded",
            ],
        }

    def _goose_compare_catalog(self, controls: dict[str, Any]) -> dict[str, Any]:
        return {
            "gateway_compare_endpoint": "/ops/brain/gateway/history/compare",
            "policy_compare_endpoint": "/ops/brain/extensions/policy-history/compare",
            "certification_compare_endpoint": "/ops/brain/extensions/certifications/compare",
            "adversary_compare_endpoint": "/ops/brain/security/adversary-reviews/compare",
            "acp_compare_endpoint": "/ops/brain/acp/providers/compare",
            "group_names": [
                "policy-lifecycle",
                "certification-state",
                "permission-deltas",
                "approval-fallback",
                "acp-readiness",
                "adversary-outcome",
                "gateway-execution-path",
                "trace-and-artifacts",
            ],
            "group_descriptions": {
                "policy-lifecycle": "status, version, rollback, and lineage deltas",
                "certification-state": "certification, restoration, and lineage state changes",
                "permission-deltas": "allowed-tool, permission, and privilege drift",
                "approval-fallback": "approval posture and fallback-chain changes",
                "acp-readiness": "probe, capability, version, and remediation deltas",
                "adversary-outcome": "risk-family and decision-path changes",
                "gateway-execution-path": "trigger, flow-family, extension, and traceability changes",
                "trace-and-artifacts": "trace, report, and produced-artifact drift",
            },
            "default_expanded_groups": controls.get("default_expanded_groups", []),
            "gateway_execution_count": len(controls.get("gateway_executions", [])),
            "policy_version_count": len(controls.get("policy_versions", [])),
            "certification_count": len(controls.get("certifications", [])),
            "adversary_review_count": len(controls.get("adversary_reviews", [])),
            "acp_provider_count": len(controls.get("acp_providers", [])),
        }

    def _build_replay_catalog(self, *, replay_frames: list[dict[str, Any]]) -> dict[str, Any]:
        return self.telemetry.replay_catalog(replay_frames=replay_frames)

    def _build_performance_profile(
        self,
        *,
        snapshot: dict[str, Any],
        safe_mode_physiology: dict[str, Any],
        telemetry_window: dict[str, Any],
        sources: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        active_sources = sources or self.telemetry.collect_sources(snapshot=snapshot, traces=[], session_id=None)
        return self.telemetry.performance_profile(
            snapshot=snapshot,
            safe_mode_physiology=safe_mode_physiology,
            telemetry_window=telemetry_window,
            sources=active_sources,
        )

    def _build_replay_frames(
        self,
        *,
        snapshot: dict[str, Any],
        traces: list[dict[str, Any]],
        session_id: str | None,
        limit: int,
        sources: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        active_sources = sources or self.telemetry.collect_sources(snapshot=snapshot, traces=traces, session_id=session_id)
        return self.telemetry.replay_frames(
            snapshot=snapshot,
            traces=traces,
            session_id=session_id,
            limit=limit,
            sources=active_sources,
        )

    def _route_window_summary(self, traces: list[dict[str, Any]], *, window: int, sources: dict[str, Any] | None = None) -> dict[str, Any]:
        active_sources = sources or self.telemetry.collect_sources(snapshot={}, traces=traces, session_id=None)
        return self.telemetry.route_window_summary(traces=traces, window=window, sources=active_sources)

    def _capsule_subjects(self) -> list[str]:
        return [node.subject for node in self.scene.nodes if node.node_type == "capsule" and node.subject]

    def _trace_weight(self, index: int) -> float:
        return max(0.18, round(1.0 - (index * 0.07), 3))

    def _cap(self, value: float | int, *, ceiling: float) -> float:
        if ceiling <= 0:
            return 0.0
        return round(min(1.0, float(value) / ceiling), 3)

    def _append_ref(self, refs: list[str], value: str) -> None:
        if value not in refs and len(refs) < 8:
            refs.append(value)

    def _artifact_by_id(self, items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
        for item in items:
            if item.get(key) == value:
                return item
        return {"missing": True, key: value}

    def _metric_delta(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, float]:
        keys = sorted({*left.keys(), *right.keys()})
        deltas: dict[str, float] = {}
        for key in keys:
            left_value = left.get(key)
            right_value = right.get(key)
            if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                deltas[key] = round(float(right_value) - float(left_value), 3)
        return deltas
