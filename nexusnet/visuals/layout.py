from __future__ import annotations

from collections import defaultdict
import hashlib
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
from nexusnet.agents import AgentOpportunityDiscovery
from nexusnet.agents.harnesses import HarnessImprovementLedger, HarnessModelRouter, HarnessProviderRegistry
from nexusnet.agents.pipelines import AgenticPipelineRuntime
from nexusnet.adapters.dataset_forge import DatasetForge
from nexusnet.adapters.decision_gate import FineTuneDecisionGate
from nexusnet.adapters.forge import AdapterForgeRegistry
from nexusnet.adapters.training_planner import AdapterTrainingPlanner
from nexusnet.browser import BrowserContextMemory, BrowserProfilePolicy
from nexusnet.core import AutonomousUpdateController, SelfReviewGate
from nexusnet.core.self_improvement import ImprovementQueue, SelfImprovementLineageRegistry
from nexusnet.curriculum import DatasetRadar
from nexusnet.evals import EvalRegistry, VerifierSearchRegistry
from nexusnet.growth import HiveModelGrowthEngine, NexusNetProductionSpine
from nexusnet.knowledge import KnowledgeArtifactCompiler
from nexusnet.memory import MemoryQualityLedger, NexusEngramIndex
from nexusnet.authority import AuthorityIntegritySpine
from nexusnet.developmental import DevelopmentalCortexService
from nexusnet.evals.federation import EvalFederationRegistry
from nexusnet.evidence import EvidenceStore
from nexusnet.operations import AssimilationTargetCatalog, AssimilationTargetRegistry, CodegraphGate
from nexusnet.runtime.decision_ledger import RuntimeDecisionLedger
from nexusnet.tools.action_harness import ToolActionHarness
from nexusnet.policy import PolicyKernel
from nexusnet.protocols import ProtocolTrustRegistry
from nexusnet.research import ForwardRadarRegistry
from nexusnet.retrieval import RetrievalPlanner
from nexusnet.runtime.cache_ledger import EffectiveContextCacheLedger
from nexusnet.runtime.edge_router import EdgeWorkloadRouter
from nexusnet.runtime.inference_economy_router import InferenceEconomyRouter
from nexusnet.runtime.inference_architecture import InferenceArchitectureRegistry
from nexusnet.runtime.model_passport import EdgeModelCertificationRegistry
from nexusnet.runtime.quantization.catalog import QuantizationCatalog
from nexusnet.runtime.workload_scorecards import RuntimeWorkloadScorecardRegistry
from nexusnet.security import ArtifactTrustRegistry
from nexusnet.telemetry import ConceptTelemetryRegistry, GenAITraceRegistry
from nexusnet.vision import MultimodalComputerUseController, OperatorEventRegistry
from nexusnet.canon import (
    ao_hive_scorecard,
    autonomous_evolution_dossier,
    artifact_trust_scorecard,
    blackbox_recorder,
    build_canon_realization,
    communication_integration_scorecard,
    eval_suite_scorecard,
    experts_hive_scorecard,
    hardware_matrix_scorecard,
    hive_consensus_scorecard,
    input_ingestion_scorecard,
    live_flow_scorecard,
    memory_provenance_scorecard,
    neural_core_scorecard,
    observability_scorecard,
    output_delivery_scorecard,
    protocol_trust_scorecard,
    researcher_swarm_scorecard,
    runtime_quantization_scorecard,
    security_governance_scorecard,
    self_improvement_scorecard,
    tool_execution_scorecard,
    visualops_scorecard,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _dataset_forge_flow_lineage(dataset_forge: dict[str, Any]) -> dict[str, Any]:
    manifests = list(dataset_forge.get("manifests") or [])
    canonical_train_lineage: list[dict[str, Any]] = []
    candidate_material_lineage: list[dict[str, Any]] = []
    blocked_lineage: list[dict[str, Any]] = []
    review_blocked_lineage: list[dict[str, Any]] = []
    lineage_split_policy: dict[str, Any] = {}
    train_blocked_source_ids: list[str] = []
    sealed_eval_visibility: dict[str, Any] = {
        "visible_to_training": False,
        "visible_to_teacher_council": False,
        "source_ids": [],
    }
    for manifest in manifests[:20]:
        manifest_id = manifest.get("dataset_manifest_id")
        if not lineage_split_policy and manifest.get("dataset_radar_lineage_split_policy"):
            lineage_split_policy = dict(manifest.get("dataset_radar_lineage_split_policy") or {})
        splits = manifest.get("splits") or {}
        train_split = splits.get("train") or {}
        for source_id in train_split.get("blocked_source_ids") or []:
            if source_id not in train_blocked_source_ids:
                train_blocked_source_ids.append(source_id)
        hidden_split = splits.get("teacher_free_hidden") or {}
        if hidden_split:
            hidden_source_ids = list(hidden_split.get("source_ids") or [])
            sealed_eval_visibility = {
                "visible_to_training": bool(hidden_split.get("visible_to_training")),
                "visible_to_teacher_council": bool(hidden_split.get("visible_to_teacher_council")),
                "source_ids": hidden_source_ids,
            }
        review_packets = _manifest_review_packets_by_source(manifest)
        for gate in manifest.get("dataset_radar_gates") or []:
            review_packet = (
                review_packets.get(gate.get("source_id"))
                or review_packets.get(gate.get("request_source_id"))
                or {}
            )
            review_blocking_fields = list(review_packet.get("blocking_fields") or [])
            training_promotion_allowed = (
                bool(review_packet.get("training_promotion_allowed"))
                if review_packet
                else bool(gate.get("training_eligible"))
            )
            row = {
                "dataset_manifest_id": manifest_id,
                "source_id": gate.get("source_id"),
                "request_source_id": gate.get("request_source_id"),
                "source_kind": gate.get("source_kind"),
                "requested_split": gate.get("requested_split") or gate.get("split"),
                "allowed": bool(gate.get("allowed")),
                "candidate_material": bool(gate.get("candidate_material")),
                "training_eligible": bool(gate.get("training_eligible")),
                "material_request_ref": gate.get("material_request_ref"),
                "latest_candidate_review_id": gate.get("latest_candidate_review_id"),
                "reason": gate.get("reason"),
                "source_review_packet_id": review_packet.get("packet_id"),
                "source_review_state": review_packet.get("review_state") or "not_recorded",
                "training_promotion_allowed": training_promotion_allowed,
                "review_blocking_fields": review_blocking_fields,
            }
            if row["candidate_material"]:
                candidate_material_lineage.append(row)
            elif row["training_eligible"]:
                canonical_train_lineage.append(row)
            elif not row["allowed"]:
                blocked_lineage.append(row)
            if review_packet and (not training_promotion_allowed or review_blocking_fields):
                review_blocked_lineage.append(row)
    return {
        "manifest_count": dataset_forge.get("manifest_count", 0),
        "ready_count": dataset_forge.get("ready_count", 0),
        "blocked_count": dataset_forge.get("blocked_count", 0),
        "latest_manifest_id": (dataset_forge.get("latest_manifest") or {}).get("dataset_manifest_id"),
        "required_controls": dataset_forge.get("required_controls", []),
        "canonical_train_lineage": canonical_train_lineage[:12],
        "candidate_material_lineage": candidate_material_lineage[:12],
        "blocked_lineage": blocked_lineage[:12],
        "review_blocked_lineage": review_blocked_lineage[:12],
        "lineage_split_policy": lineage_split_policy,
        "train_blocked_source_ids": train_blocked_source_ids,
        "sealed_eval_visibility": sealed_eval_visibility,
    }


def _manifest_review_packets_by_source(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    packets: dict[str, dict[str, Any]] = {}
    for wrapper in manifest.get("dataset_radar_review_packets") or []:
        review_packet = wrapper.get("review_required_packet") or {}
        for source_key in (
            wrapper.get("dataset_radar_source_id"),
            wrapper.get("source_id"),
            review_packet.get("dataset_id"),
        ):
            if source_key:
                packets[str(source_key)] = review_packet
    return packets


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

    def bundled_control_panel_dir(self) -> Path:
        return _repo_root() / "ui" / "control-panel"

    def bundled_wrapper_index(self) -> Path:
        return _repo_root() / "ui" / "wrapper" / "index.html"

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
    def __init__(
        self,
        *,
        paths,
        teacher_registry,
        wrapper_surface,
        store,
        dataset_radar: DatasetRadar | None = None,
        harness_provider_registry: HarnessProviderRegistry | None = None,
        harness_model_router: HarnessModelRouter | None = None,
        assimilation_targets: AssimilationTargetRegistry | None = None,
        retrieval_planner: RetrievalPlanner | None = None,
        self_improvement_lineage: SelfImprovementLineageRegistry | None = None,
        verifier_search: VerifierSearchRegistry | None = None,
        browser_profile_policy: BrowserProfilePolicy | None = None,
        operator_events: OperatorEventRegistry | None = None,
        edge_model_certification: EdgeModelCertificationRegistry | None = None,
        concept_telemetry: ConceptTelemetryRegistry | None = None,
        codegraph_gate: CodegraphGate | None = None,
        developmental_cortex=None,
        authority_spine=None,
        evidence_store=None,
        eval_federation=None,
        tool_action_harness=None,
        runtime_decision_ledger=None,
        assimilation_catalog=None,
    ):
        self.paths = paths
        self.teacher_registry = teacher_registry
        self.wrapper_surface = wrapper_surface
        self.store = store
        self.dataset_radar = dataset_radar or DatasetRadar(artifacts_dir=paths.artifacts_dir)
        self.harness_provider_registry = harness_provider_registry or HarnessProviderRegistry.default()
        self.harness_model_router = harness_model_router or HarnessModelRouter.default()
        self.assimilation_targets = assimilation_targets or AssimilationTargetRegistry(artifacts_dir=paths.artifacts_dir)
        self.retrieval_planner = retrieval_planner or RetrievalPlanner(artifacts_dir=paths.artifacts_dir)
        self.self_improvement_lineage = self_improvement_lineage or SelfImprovementLineageRegistry(artifacts_dir=paths.artifacts_dir)
        self.verifier_search = verifier_search or VerifierSearchRegistry(artifacts_dir=paths.artifacts_dir)
        self.browser_profile_policy = browser_profile_policy or BrowserProfilePolicy(artifacts_dir=paths.artifacts_dir)
        self.operator_events = operator_events or OperatorEventRegistry(artifacts_dir=paths.artifacts_dir)
        self.edge_model_certification = edge_model_certification or EdgeModelCertificationRegistry(artifacts_dir=paths.artifacts_dir)
        self.concept_telemetry = concept_telemetry or ConceptTelemetryRegistry(artifacts_dir=paths.artifacts_dir)
        self.codegraph_gate = codegraph_gate or CodegraphGate(artifacts_dir=paths.artifacts_dir)
        self.developmental_cortex = developmental_cortex or DevelopmentalCortexService(artifacts_dir=paths.artifacts_dir)
        self.authority_spine = authority_spine or AuthorityIntegritySpine(artifacts_dir=paths.artifacts_dir)
        self.evidence_store = evidence_store or EvidenceStore(artifacts_dir=paths.artifacts_dir)
        self.eval_federation = eval_federation or EvalFederationRegistry(artifacts_dir=paths.artifacts_dir)
        self.tool_action_harness = tool_action_harness or ToolActionHarness(artifacts_dir=paths.artifacts_dir)
        self.runtime_decision_ledger = runtime_decision_ledger or RuntimeDecisionLedger(artifacts_dir=paths.artifacts_dir)
        self.assimilation_catalog = assimilation_catalog or AssimilationTargetCatalog()
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
        source_control_panel = self.compiler.bundled_control_panel_dir()
        target_control_panel = self.paths.ui_dir / "control-panel"
        if source_control_panel.exists() and source_control_panel.resolve() != target_control_panel.resolve():
            shutil.copytree(source_control_panel, target_control_panel, dirs_exist_ok=True)
        source_wrapper = self.compiler.bundled_wrapper_index()
        target_wrapper = self.paths.ui_dir / "wrapper" / "index.html"
        if source_wrapper.exists() and source_wrapper.resolve() != target_wrapper.resolve():
            target_wrapper.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_wrapper, target_wrapper)

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

    def canon_realization(self, session_id: str | None = None) -> dict[str, Any]:
        return self.state(session_id=session_id)["overlay_state"]["control_panel"]["canon_realization"]

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
        control_panel = self._build_control_panel(
            session_id=session_id,
            snapshot=snapshot,
            recent_trace=recent_trace,
            teacher_visibility=teacher_visibility,
            filter_catalog=filter_catalog,
            diff_catalog=diff_catalog,
            performance_profile=performance_profile,
            replay_catalog=replay_catalog,
            telemetry_window=telemetry_window,
            safe_mode_physiology=safe_mode_physiology,
        )

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
            control_panel=control_panel,
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

    def _brain_operations_summary(self, *, session_id: str | None) -> dict[str, Any]:
        commands = self.store.list_brain_operation_commands(session_id=session_id, limit=5)
        events = self.store.list_brain_operation_events(session_id=session_id, limit=30)
        latest_command = commands[0] if commands else None
        active_command_id = latest_command.get("command_id") if latest_command else None
        active_events = [event for event in events if not active_command_id or event.get("command_id") == active_command_id]
        return {
            "status_label": "LOCKED CANON",
            "state": "live-bound" if latest_command else "standby",
            "session_id": session_id,
            "command_count": len(commands),
            "latest_command": latest_command,
            "commands": commands,
            "timeline": list(reversed(active_events or events)),
            "signal_contract": [
                "receives_orders",
                "local_reasoning",
                "evidence_response",
                "veto_escalation",
                "consensus_contribution",
                "execution_status",
            ],
            "canon_binding": {
                "source_document": "NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
                "state_taxonomy": [
                    "live_state",
                    "simulated_state",
                    "roadmap_state",
                    "research_candidate_state",
                ],
            },
        }

    def _brain_operations_columns(self, operations_summary: dict[str, Any]) -> list[dict[str, Any]]:
        latest_command = operations_summary.get("latest_command") or {}
        events = operations_summary.get("timeline") or []
        event_by_type = {event.get("event_type"): event for event in events}
        veto_event = event_by_type.get("veto_escalation") or event_by_type.get("consensus_state")
        execution_event = event_by_type.get("execution_status")
        return [
            {
                "label": "NexusBrain orders",
                "signal_type": "command_issued",
                "state": "live-bound" if latest_command else "standby",
                "actor": "NexusBrain",
                "detail": latest_command.get("command_text") or "No active command issued.",
            },
            {
                "label": "AO local reasoning",
                "signal_type": "ao_signal",
                "state": "live-bound" if event_by_type.get("ao_signal") else "standby",
                "actor": (event_by_type.get("ao_signal") or {}).get("actor") or "AO Hive",
                "detail": (event_by_type.get("ao_signal") or {}).get("detail") or "AO mini-brains waiting for orders.",
            },
            {
                "label": "Expert evidence",
                "signal_type": "expert_signal",
                "state": "live-bound" if event_by_type.get("expert_signal") else "standby",
                "actor": (event_by_type.get("expert_signal") or {}).get("actor") or "Experts Hive",
                "detail": (event_by_type.get("expert_signal") or {}).get("detail") or "Expert mini-brains waiting for evidence requests.",
            },
            {
                "label": "Veto / escalation",
                "signal_type": (veto_event or {}).get("event_type") or "consensus_state",
                "state": "live-bound" if veto_event else "standby",
                "actor": (veto_event or {}).get("actor") or "Governance / Safety / NexusBrain",
                "detail": (veto_event or {}).get("detail")
                or ((veto_event or {}).get("consensus") or {}).get("veto_state")
                or "No active veto state.",
            },
            {
                "label": "Execution status",
                "signal_type": "execution_status",
                "state": (execution_event or {}).get("state") or latest_command.get("lifecycle_state") or "standby",
                "actor": (execution_event or {}).get("actor") or latest_command.get("target_surface") or "Tools / Outputs",
                "detail": (execution_event or {}).get("detail")
                or "Command lifecycle is tracked through command, AO, expert, consensus, and audit events.",
            },
        ]

    def _build_control_panel(
        self,
        *,
        session_id: str | None,
        snapshot: dict[str, Any],
        recent_trace: dict[str, Any],
        teacher_visibility: dict[str, Any],
        filter_catalog: dict[str, Any],
        diff_catalog: dict[str, Any],
        performance_profile: dict[str, Any],
        replay_catalog: dict[str, Any],
        telemetry_window: dict[str, Any],
        safe_mode_physiology: dict[str, Any],
    ) -> dict[str, Any]:
        assimilation = snapshot.get("assimilation") or {}
        compare_refs = assimilation.get("compare_refs") or {}
        goose = assimilation.get("goose") or {}
        goose_security = (goose.get("security") or {})
        goose_extensions = (goose.get("extensions") or {})
        goose_acp = (goose.get("acp") or {})
        goose_recipes = (goose.get("recipes") or {})
        runtime_summary = snapshot.get("runtime") or {}
        brain_runtime_summary = snapshot.get("brain_runtime") or {}
        memory_planes = snapshot.get("memory_planes") or {}
        graph_summary = snapshot.get("graph") or {}
        retrieval_summary = snapshot.get("retrieval") or {}
        promotions = snapshot.get("promotions") or {}
        aos = snapshot.get("aos") or {}
        agents = snapshot.get("agents") or {}
        core_execution = snapshot.get("core_execution") or {}
        release_wrapper_runtime = snapshot.get("release_runtime") or {}
        project_heartbeat = release_wrapper_runtime.get("project_heartbeat") or {
            "schema_version": "nexusnet-project-heartbeat-v1",
            "surface_id": "nexusnet-project-heartbeat",
            "status": "not-run",
            "runtime_state": "not-run",
            "honest_status_label": "core-substrate-heartbeat-not-observed",
            "trigger": "hive-forward-pass",
            "heartbeat_id": None,
            "session_ref_digest": self._session_ref_digest(session_id),
            "lane_count": 0,
            "alive_lane_count": 0,
            "degraded_lane_count": 0,
            "lanes": [],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": (
                "sanitized-project-heartbeat-status-counts-and-refs-only-no-prompts-outputs-session-ids-or-local-paths"
            ),
            "mutation_boundary": "heartbeat-status-and-artifact-refs-only-no-active-production-mutation",
        }
        release_wrapper_privacy_consent = release_wrapper_runtime.get("privacy_consent") or {
            "schema_version": "nexusnet-release-wrapper-privacy-consent-ledger-v1",
            "surface_id": "release-wrapper-privacy-consent-ledger",
            "status_label": "LOCKED CANON",
            "status": "no-live-consent-record-yet-personal-data-default-off",
            "session_ref_digest": self._session_ref_digest(session_id),
            "record_count": 0,
            "latest_record_id": None,
            "personal_data_training_opt_in": False,
            "personal_data_federation_allowed": False,
            "personal_data_dream_training_allowed": False,
            "sanitized_metadata_federation_allowed": True,
            "sanitized_dream_research_allowed": True,
            "raw_content_included": False,
            "contains_personal_data": False,
            "active_production_mutation_allowed": False,
            "privacy_boundary": "hashed-session-consent-state-config-refs-and-retention-policy-only-no-prompts-outputs-session-ids-or-local-paths",
        }
        release_wrapper_privacy_consent_enforcement = (
            release_wrapper_runtime.get("privacy_consent_enforcement")
            or release_wrapper_privacy_consent.get("queue_enforcement")
            or {
                "schema_version": "nexusnet-release-wrapper-privacy-consent-enforcement-ledger-v1",
                "surface_id": "release-wrapper-privacy-consent-enforcement",
                "status_label": "LOCKED CANON",
                "status": "no-revocation-enforcement-recorded",
                "session_ref_digest": self._session_ref_digest(session_id),
                "record_count": 0,
                "latest_record_id": None,
                "blocked_capabilities": [],
                "revoked_personal_data_queue_count": 0,
                "revoked_federated_packet_count": 0,
                "revoked_federated_import_count": 0,
                "active_personal_data_training_allowed": False,
                "active_production_mutation_allowed": False,
                "raw_content_included": False,
                "contains_personal_data": False,
                "privacy_boundary": "sanitized-queue-packet-import-ids-and-consent-record-refs-only-no-prompts-outputs-session-ids-or-local-paths",
            }
        )
        release_wrapper_privacy_retention_enforcement = (
            release_wrapper_runtime.get("privacy_retention_enforcement")
            or release_wrapper_privacy_consent.get("retention_cleanup")
            or release_wrapper_privacy_consent_enforcement.get("retention_enforcement")
            or {
                "schema_version": "nexusnet-release-wrapper-privacy-retention-enforcement-ledger-v1",
                "surface_id": "release-wrapper-privacy-retention-enforcement",
                "status_label": "LOCKED CANON",
                "status": "no-retention-enforcement-recorded",
                "session_ref_digest": self._session_ref_digest(session_id),
                "record_count": 0,
                "latest_record_id": None,
                "expired_queue_count": 0,
                "passivated_global_growth_count": 0,
                "global_growth_passivation_mode": "not-recorded",
                "active_personal_data_training_allowed": False,
                "active_production_mutation_allowed": False,
                "raw_content_included": False,
                "contains_personal_data": False,
                "privacy_boundary": "sanitized-retention-counts-queue-refs-and-growth-passivation-refs-only-no-prompts-outputs-session-ids-or-local-paths",
            }
        )
        project_heartbeat_replay = release_wrapper_runtime.get("project_heartbeat_replay") or {}
        native_project_heartbeat_replay_status = {
            "surface_id": "project-heartbeat-native-replay-control-status",
            "status": (
                "covered"
                if project_heartbeat.get("native_replay_ref")
                and project_heartbeat.get("native_replay_record_id")
                else "degraded"
            ),
            "runtime_state": (
                "live-bound"
                if project_heartbeat.get("native_replay_ref")
                and project_heartbeat.get("native_replay_record_id")
                else "degraded"
            ),
            "session_ref_digest": self._session_ref_digest(session_id),
            "native_replay_ref": project_heartbeat.get("native_replay_ref"),
            "native_replay_record_id": project_heartbeat.get("native_replay_record_id"),
            "wrapper_replay_ref": (
                project_heartbeat.get("wrapper_replay_ref")
                or project_heartbeat_replay.get("artifact_ref")
            ),
            "wrapper_replay_record_id": (
                project_heartbeat.get("wrapper_replay_record_id")
                or project_heartbeat_replay.get("latest_record_id")
            ),
            "evidence_refs": [
                ref
                for ref in [
                    project_heartbeat.get("native_replay_ref"),
                    project_heartbeat.get("native_replay_record_id"),
                    project_heartbeat_replay.get("artifact_ref"),
                    project_heartbeat_replay.get("latest_record_id"),
                ]
                if ref
            ],
            "honest_status_label": (
                "native-project-heartbeat-replay-covered"
                if project_heartbeat.get("native_replay_ref")
                and project_heartbeat.get("native_replay_record_id")
                else "native-project-heartbeat-replay-missing"
            ),
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": "sanitized-native-heartbeat-replay-refs-only-no-prompts-outputs-session-ids-or-local-paths",
            "mutation_boundary": "control-panel-status-only-no-active-production-mutation",
        }
        release_wrapper_telemetry = release_wrapper_runtime.get("live_wrapper_telemetry") or {
            "surface_id": "release-wrapper-live-telemetry",
            "runtime_state": "static-canon",
            "event_count": 0,
            "recent_events": [],
            "privacy_boundary": "sanitized-digests-refs-counts-and-status-only-no-raw-prompts-outputs-session-ids",
        }
        release_wrapper_self_repair_ledger = release_wrapper_runtime.get("self_repair_ledger") or {
            "surface_id": "release-wrapper-self-repair-ledger",
            "scope": "session" if session_id else "global",
            "session_ref_digest": None,
            "repair_count": 0,
            "global_repair_count": 0,
            "latest_action": None,
            "latest_status": None,
            "actions": [],
            "ao_guard_required": True,
            "ao_guard_passed_count": 0,
            "latest_ao_guard": None,
            "active_production_mutated": False,
            "raw_content_included": False,
            "mutation_boundary": "admin-approved-shadow-safe-file-only-no-active-production-mutation",
            "privacy_boundary": "sanitized-update-session-digests-and-evidence-refs-only-no-raw-prompts-outputs-session-ids",
        }
        release_wrapper_boot_supervisor = release_wrapper_runtime.get("boot_supervisor") or {
            "surface_id": "release-wrapper-boot-supervisor",
            "runtime_state": "not-run",
            "latest_status": "not-run",
            "manifest_ref": "artifacts/release-wrapper-runtime/boot-manifest.json",
            "check_count": 0,
            "pass_count": 0,
            "failed_count": 0,
            "raw_content_included": False,
            "privacy_boundary": "sanitized-boot-refs-status-counts-digests-only-no-raw-prompts-outputs-session-ids",
        }
        release_wrapper_initial_release_supervisor = release_wrapper_runtime.get("initial_release_supervisor") or {
            "surface_id": "release-wrapper-initial-release-supervisor",
            "runtime_state": "not-run",
            "latest_status": "not-run",
            "manifest_ref": "artifacts/release-wrapper-runtime/initial-release-supervisor.json",
            "product_scope": "whole-system",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "privacy_boundary": "sanitized-status-ids-counts-digests-only-no-raw-prompts-outputs-session-ids",
        }
        release_wrapper_release_product_smoke = release_wrapper_runtime.get("release_product_smoke") or {
            "surface_id": "release-wrapper-product-smoke",
            "runtime_state": "not-run",
            "latest_status": "not-run",
            "manifest_ref": "artifacts/release-wrapper-runtime/release-product-smoke.json",
            "product_scope": "whole-system",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": "sanitized-release-product-smoke-status-counts-digests-and-endpoint-refs-only-no-prompts-outputs-session-ids-or-local-paths",
        }
        release_wrapper_release_run_history = release_wrapper_runtime.get("release_run_history") or {
            "surface_id": "release-wrapper-release-run-history",
            "runtime_state": "not-run",
            "latest_status": "not-run",
            "manifest_ref": "artifacts/release-wrapper-runtime/release-run-history.jsonl",
            "product_scope": "whole-system",
            "run_count": 0,
            "global_run_count": 0,
            "latest_run": None,
            "runs": [],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": "sanitized-release-run-history-status-counts-digests-and-endpoint-refs-only-no-prompts-outputs-admin-identities-session-ids-or-local-paths",
        }
        release_wrapper_native_hive_heartbeat_watchdog = release_wrapper_runtime.get(
            "native_hive_heartbeat_watchdog"
        ) or {
            "schema_version": "nexusnet-release-wrapper-native-hive-heartbeat-watchdog-v1",
            "surface_id": "release-wrapper-native-hive-heartbeat-watchdog",
            "status": "blocked",
            "runtime_state": "not-run",
            "latest_fresh": False,
            "freshness_status": "not-run",
            "heartbeat_count": 0,
            "latest_heartbeat_id": None,
            "artifact_ref": "release-wrapper-runtime/native-hive-heartbeats.jsonl",
            "watchdog_ref": "release-wrapper-runtime/native-hive-heartbeat-watchdog.json",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": "sanitized-native-hive-watchdog-status-ids-counts-and-artifact-refs-only-no-prompts-outputs-session-ids-or-local-paths",
        }
        release_wrapper_release_health_heartbeat = release_wrapper_runtime.get("release_health_heartbeat") or {
            "schema_version": "nexusnet-release-wrapper-health-heartbeat-v1",
            "surface_id": "release-wrapper-health-heartbeat",
            "status": "not-run",
            "runtime_state": "not-run",
            "trigger": "not-run",
            "product_surface": "wrapper",
            "heartbeat_count": 0,
            "latest_heartbeat_id": None,
            "artifact_ref": "release-wrapper-runtime/release-health-heartbeat.jsonl",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": "sanitized-release-health-status-counts-and-refs-only-no-prompts-outputs-session-ids-or-local-paths",
        }
        release_wrapper_release_health_heartbeat_loop = release_wrapper_runtime.get("release_health_heartbeat_loop") or {
            "schema_version": "nexusnet-release-wrapper-health-heartbeat-loop-v1",
            "surface_id": "release-wrapper-health-heartbeat-loop",
            "status": "not-run",
            "runtime_state": "not-run",
            "trigger": "not-run",
            "product_surface": "wrapper",
            "loop_count": 0,
            "global_loop_count": 0,
            "latest_loop_id": None,
            "latest_heartbeat_id": None,
            "artifact_ref": "release-wrapper-runtime/release-health-heartbeat-loop.jsonl",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": "sanitized-release-health-loop-status-counts-timers-and-refs-only-no-prompts-outputs-session-ids-or-local-paths",
        }
        release_wrapper_release_health_heartbeat_supervisor = release_wrapper_runtime.get(
            "release_health_heartbeat_supervisor"
        ) or {
            "schema_version": "nexusnet-release-wrapper-health-heartbeat-supervisor-v1",
            "surface_id": "release-wrapper-health-heartbeat-supervisor",
            "status": "disabled",
            "runtime_state": "disabled",
            "pulse_count": 0,
            "global_pulse_count": 0,
            "latest_pulse_id": None,
            "latest_loop_id": None,
            "artifact_ref": "release-wrapper-runtime/release-health-heartbeat-supervisor.jsonl",
            "state_ref": "release-wrapper-runtime/release-health-heartbeat-supervisor.json",
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": "sanitized-release-health-supervisor-timers-status-counts-and-refs-only-no-prompts-outputs-session-ids-or-local-paths",
        }
        release_wrapper_canon_contract_ledger = release_wrapper_runtime.get("canon_contract_ledger") or {
            "surface_id": "whole-project-canon-contract-ledger",
            "schema_version": "nexusnet-whole-project-canon-contract-ledger-v1",
            "status_label": "LOCKED CANON",
            "product_scope": "whole-system",
            "coverage_status": "missing",
            "contract_count": 0,
            "evidence_present_count": 0,
            "partial_count": 0,
            "missing_count": 0,
            "source_manifest": {
                "surface_id": "whole-project-canon-source-manifest",
                "source_refs": [],
                "source_count": 0,
                "ingested_source_count": 0,
                "missing_source_count": 0,
                "sources": [],
                "raw_content_included": False,
            },
            "contracts": [],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "active_production_mutated": False,
            "privacy_boundary": "sanitized-canon-source-refs-hashes-counts-headings-keyword-counts-and-runtime-evidence-refs-only-no-raw-canon-text-prompts-outputs-session-ids-or-local-paths",
        }
        release_wrapper_canon_contract_receipts = release_wrapper_runtime.get("canon_contract_receipts") or {
            "schema_version": "nexusnet-whole-project-canon-contract-receipts-v1",
            "surface_id": "whole-project-canon-contract-receipts",
            "status_label": "LOCKED CANON",
            "runtime_state": "static-canon",
            "receipt_count": 0,
            "covered_receipt_count": 0,
            "partial_receipt_count": 0,
            "missing_receipt_count": 0,
            "latest_status": "not-run",
            "latest_receipt": None,
            "receipts": [],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "privacy_boundary": "sanitized-canon-contract-receipt-ids-counts-statuses-and-evidence-refs-only-no-raw-canon-text-prompts-outputs-session-ids-or-local-paths",
        }
        release_wrapper_developmental_release_contract = release_wrapper_runtime.get("developmental_release_contract") or {
            "surface_id": "developmental-release-contract",
            "runtime_state": "static-canon",
            "latest_status": "not-recorded",
            "canonical_output_names": [
                "body_schema_snapshot",
                "reference_frame_updates",
                "dream_request",
                "causal_test_request",
                "growth_archive_candidate",
                "promotion_tribunal_case",
            ],
            "canonical_output_count": 6,
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "privacy_boundary": "canonical-developmental-ids-statuses-counts-and-digested-refs-only-no-prompts-outputs-session-ids-or-local-paths",
        }
        release_wrapper_forward_pass_enforcement_matrix = release_wrapper_runtime.get(
            "whole_system_forward_pass_enforcement_matrix"
        ) or {
            "surface_id": "whole-system-forward-pass-enforcement-matrix",
            "runtime_state": "static-canon",
            "coverage_status": "partial",
            "required_capability_columns": [
                "continuous_assimilation",
                "global_growth",
                "federated_packet",
                "production_spine",
                "ao_eval_tool_governance",
                "developmental_release_contract",
                "cache_context_truth",
                "rollback_safe_updates",
            ],
            "entrypoint_count": 0,
            "covered_entrypoint_count": 0,
            "missing_entrypoint_count": 0,
            "entrypoints": [],
            "raw_content_included": False,
            "active_production_mutation_allowed": False,
            "privacy_boundary": "sanitized-entrypoint-statuses-capability-columns-and-evidence-refs-only-no-prompts-outputs-session-ids-or-local-paths",
        }
        release_wrapper_session_lifecycle = snapshot.get("release_session_lifecycle") or {
            "surface_id": "release-wrapper-session-lifecycle",
            "runtime_state": release_wrapper_runtime.get("entrypoint", {}).get("runtime_state") or "static-canon",
            "lifecycle_steps": [],
            "step_counts": {"total": 0, "passed": 0, "blocked": 0},
            "session_history": release_wrapper_runtime.get("session_history") or {},
            "readiness": snapshot.get("release_readiness") or {},
            "release_manifest_status_rollup": release_wrapper_runtime.get("release_manifest_status_rollup") or {},
            "privacy_boundary": "sanitized-session-lifecycle-digests-refs-status-only-no-raw-prompts-outputs-session-ids",
        }
        native_runtime_growth_governance = (
            release_wrapper_runtime.get("native_runtime_growth_governance")
            if isinstance(release_wrapper_runtime.get("native_runtime_growth_governance"), dict)
            else release_wrapper_session_lifecycle.get("native_runtime_growth_governance")
            if isinstance(release_wrapper_session_lifecycle.get("native_runtime_growth_governance"), dict)
            else {}
        )
        direct_nexusbrain_native_growth_governance = {
            "surface_id": "direct-nexusbrain-native-growth-governance",
            "status_label": "LOCKED CANON",
            "status": (
                native_runtime_growth_governance.get("status")
                if native_runtime_growth_governance.get("direct_nexusbrain_generate") is True
                else "not-triggered"
            ),
            "honest_status_label": (
                "direct-nexusbrain-native-growth-governance-replayed"
                if native_runtime_growth_governance.get("direct_nexusbrain_generate") is True
                and native_runtime_growth_governance.get("latest_runner_run_id")
                else "direct-nexusbrain-native-growth-governance-not-observed"
            ),
            "runtime_state": (
                "replayed-history"
                if native_runtime_growth_governance.get("direct_nexusbrain_generate") is True
                and native_runtime_growth_governance.get("latest_runner_run_id")
                else "static-canon"
            ),
            "direct_nexusbrain_generate": bool(
                native_runtime_growth_governance.get("direct_nexusbrain_generate")
            ),
            "runtime_growth_receipt_id": native_runtime_growth_governance.get("runtime_growth_receipt_id"),
            "proposal_update_id": native_runtime_growth_governance.get("proposal_update_id"),
            "latest_runner_run_id": native_runtime_growth_governance.get("latest_runner_run_id"),
            "latest_action_statuses": native_runtime_growth_governance.get("latest_action_statuses") or {},
            "active_production_mutated": bool(
                native_runtime_growth_governance.get("active_production_mutated")
            ),
            "active_production_mutation_allowed": False,
            "raw_content_included": False,
            "privacy_boundary": (
                "direct-nexusbrain-native-growth-visualizer-status-uses-receipt-run-status-refs-only-no-prompts-outputs-session-ids"
            ),
            "mutation_boundary": "visualizer-status-only-no-active-production-mutation",
        }
        operations_summary = self._brain_operations_summary(session_id=session_id)
        latest_operation_command = operations_summary.get("latest_command") or {}
        active_command_id = latest_operation_command.get("command_id")
        live_operation_events = operations_summary.get("timeline") or []

        def count(value: Any) -> int:
            return len(value) if isinstance(value, list) else 0

        def map_state(condition: Any, fallback: str = "static-canon") -> str:
            return "live-bound" if condition else fallback

        def status_counts(values: list[str]) -> dict[str, int]:
            counts: dict[str, int] = {}
            for value in values:
                counts[value] = counts.get(value, 0) + 1
            return counts

        def page(
            page_id: str,
            label: str,
            *,
            state: str,
            summary: str,
            metrics: dict[str, Any],
            refs: list[str],
            required: list[str],
            research: list[str] | None = None,
        ) -> dict[str, Any]:
            return {
                "page_id": page_id,
                "label": label,
                "state": state,
                "summary": summary,
                "metrics": metrics,
                "evidence_refs": [ref for ref in refs if ref],
                "required_surfaces": required,
                "research_lanes": research or [],
            }

        runtime_candidates = runtime_summary.get("candidates") or []
        teacher_profiles = ((snapshot.get("teachers") or {}).get("profiles") or [])
        memory_configs = memory_planes.get("configs") or []
        ao_records = aos.get("orchestrators") or aos.get("aos") or aos.get("items") or []
        agent_capabilities = agents.get("capabilities") or []
        promotion_items = promotions.get("items") or []
        extension_summary = goose_extensions if isinstance(goose_extensions, dict) else {}
        acp_summary = goose_acp if isinstance(goose_acp, dict) else {}
        recipes_summary = goose_recipes if isinstance(goose_recipes, dict) else {}
        assimilation_target_scorecard = assimilation.get("assimilation_targets") or self.assimilation_targets.scorecard(
            session_id=session_id,
        )
        video_assimilation_scorecard = self.assimilation_targets.video_scorecard(session_id=session_id)

        research_lanes = [
            {
                "lane_id": "inference-architecture",
                "label": "Inference Architecture Beyond Quantization",
                "status": "candidate",
                "watch_items": ["speculative decoding", "disaggregated prefill/decode", "prefix caching", "KV reuse", "LMCache", "continuous batching"],
                "promotion_gate": "RuntimeWorkloadScorecard plus KVCacheLedger evidence required.",
            },
            {
                "lane_id": "agent-observability",
                "label": "Agent Observability Standards",
                "status": "candidate",
                "watch_items": ["OpenTelemetry GenAI", "trace schema registry", "redaction", "export readiness"],
                "promotion_gate": "TraceSchemaRegistry and TracePrivacyGate must be populated.",
            },
            {
                "lane_id": "agent-protocols",
                "label": "Agent Protocol Future",
                "status": "candidate",
                "watch_items": ["MCP", "A2A", "AG-UI", "ACP", "agent identity", "permission scopes"],
                "promotion_gate": "GovernedProtocolAdapterRegistry and ProtocolTrustEnvelope required.",
            },
            {
                "lane_id": "agent-evals",
                "label": "Agent Eval Suite",
                "status": "candidate",
                "watch_items": ["GAIA", "tau-bench", "OSWorld", "SWE-bench", "BrowserGym", "WebArena", "NexusNet held-out evals"],
                "promotion_gate": "EvalSuiteRegistry and held-out regression evidence required.",
            },
            {
                "lane_id": "memory-rag-kg",
                "label": "Memory, RAG, And Knowledge Graphs",
                "status": "candidate",
                "watch_items": ["GraphRAG", "LightRAG", "HippoRAG", "RAGChecker", "RAGAS", "source-to-claim maps"],
                "promotion_gate": "MemoryQualityLedger and SourceClaimMap evidence required.",
            },
            {
                "lane_id": "ai-supply-chain",
                "label": "AI Supply Chain Security",
                "status": "candidate",
                "watch_items": ["Sigstore", "ML-BOM", "AI-BOM", "safetensors", "pickle scanning", "artifact provenance"],
                "promotion_gate": "ArtifactTrustLedger and unsafe-artifact gate required.",
            },
            {
                "lane_id": "edge-local-hardware",
                "label": "Edge, Browser, And Local Hardware Roadmap",
                "status": "candidate",
                "watch_items": ["WebNN", "WebGPU", "MLX", "QAIRT", "LiteRT-LM", "ExecuTorch", "OpenVINO", "Ryzen AI"],
                "promotion_gate": "EdgeHardwareMatrix and DeviceCertificationGate required.",
            },
            {
                "lane_id": "multimodal-computer-use",
                "label": "Multimodal Computer Use",
                "status": "candidate",
                "watch_items": ["screen agents", "OCR", "VLM routing", "OmniParser", "ASR", "TTS", "OS/browser control"],
                "promotion_gate": "ComputerUseSafetyCase and action permission gates required.",
            },
            {
                "lane_id": "autonomous-updates",
                "label": "Autonomous Updates And Self-Review",
                "status": "shadow-only",
                "watch_items": ["multi-agent researcher", "self-review", "harness diffing", "shadow simulation", "rollback"],
                "promotion_gate": "PromotionProvenanceGate and rollback readiness required.",
            },
        ]

        quantization_catalog = {
            "method_families": [
                "GGUF",
                "GPTQ",
                "AWQ",
                "EXL2",
                "MXFP4",
                "NVFP4",
                "FP4",
                "FP8",
                "NF4",
                "INT8",
                "INT4",
                "SmoothQuant",
                "SpinQuant",
                "QuaRot",
                "HQQ",
                "AQLM",
                "KV-cache quantization",
                "TurboQuant",
            ],
            "formats": ["safetensors", "GGUF", "ONNX", "MLX", "MNN", "ExecuTorch", "LiteRT", "OpenVINO IR", "TensorRT-LLM"],
            "required_fields": [
                "backend_support",
                "hardware_fit",
                "eval_delta",
                "cache_impact",
                "license",
                "provenance",
                "rollback_path",
            ],
        }
        dataset_radar = self.dataset_radar.scorecard()
        dataset_forge = DatasetForge(artifacts_dir=self.paths.artifacts_dir, dataset_radar=self.dataset_radar).scorecard()
        knowledge_artifacts = KnowledgeArtifactCompiler(artifacts_dir=self.paths.artifacts_dir).scorecard()
        latest_knowledge_artifact = knowledge_artifacts.get("latest_artifact") or {}
        knowledge_artifact_runtime_gate_coverage = knowledge_artifacts.get("downstream_runtime_gate_coverage") or {}
        dataset_flow_view = {
            "view_id": "dataset-flow-view",
            "label": "Dataset Flow View",
            "stage_views": [
                "Macro Hive",
                "Neural Substrate",
                "Transformer/MoE Path",
                "Growth Flow",
                "Dataset Curriculum",
                "Replay Mode",
            ],
            "flow_label": "dataset -> license/privacy gate -> teacher council -> curriculum stage -> student -> eval -> promotion",
            "runtime_state": dataset_radar.get("runtime_state", "static-canon"),
            "source_count": dataset_radar.get("source_count", 0),
            "blocked_count": dataset_radar.get("blocked_count", 0),
            "candidate_gate_blocked_count": dataset_radar.get("candidate_gate_blocked_count", 0),
            "state_counts": dataset_radar.get("state_counts", {}),
            "coder_expert_lineage": dataset_radar.get("coder_expert_lineage", []),
            "coder_expert_lineage_split_policy": dataset_radar.get("coder_expert_lineage_split_policy", {}),
            "candidate_gate_previews": dataset_radar.get("candidate_gate_previews", []),
            "candidate_review_history": dataset_radar.get("candidate_review_history", []),
            "material_request_history": dataset_radar.get("material_request_history", []),
            "refresh_batch_history": dataset_radar.get("refresh_batch_history", []),
            "dataset_forge_lineage": _dataset_forge_flow_lineage(dataset_forge),
            "node_fields": [
                "source_url",
                "freshness",
                "license_state",
                "allowed_uses",
                "target_nodes",
                "blocked_reason",
                "source_kind",
                "candidate_material",
                "training_eligible",
                "material_request_ref",
                "replay",
            ],
            "gate_sequence": [
                "dataset",
                "license/privacy gate",
                "candidate review",
                "material request",
                "teacher council",
                "curriculum stage",
                "student",
                "eval",
                "promotion",
            ],
        }
        hive_mind = {
            "operating_model_id": "commanded-collective-hive",
            "label": "Commanded Collective Hive",
            "summary": (
                "NexusBrain centrally orchestrates goals, priorities, constraints, and orders while AO and Expert "
                "mini-brains contribute local reasoning, evidence, veto/escalation signals, and execution status."
            ),
            "central_orchestrator": {
                "authority": "NexusBrain",
                "role": "central neural command and arbitration layer",
                "command_chain": [
                    "NexusBrain",
                    "AO Hive",
                    "Experts Hive",
                    "Tools / Outputs",
                    "Memory Feedback",
                    "NexusBrain",
                ],
                "responsibilities": [
                    "issue mission intent",
                    "set priorities",
                    "route work",
                    "enforce policy",
                    "arbitrate conflict",
                    "promote verified outcomes",
                ],
            },
            "hybrid_traits": {
                "collective_intelligence": [
                    "proposal/evidence consensus",
                    "local specialist reasoning",
                    "veto/downvote escalation",
                    "shared memory contribution",
                ],
                "unified_command": [
                    "central command pressure",
                    "shared mission state",
                    "synchronized execution",
                    "organization-wide awareness",
                ],
                "business_organization": [
                    "executive command",
                    "AO departments",
                    "expert teams",
                    "tool/operator workforce",
                ],
            },
            "mini_brain_signal_contract": [
                "receives_orders",
                "local_reasoning",
                "evidence_response",
                "veto_escalation",
                "consensus_contribution",
                "execution_status",
            ],
            "mini_brain_nodes": [
                {
                    "node_id": "ao-hive",
                    "role": "AO mini-brain",
                    "scope": "department-level orchestration across NexusNet brain regions",
                    "reports_to": "NexusBrain",
                    "state": map_state(ao_records, "static-canon"),
                    "signals": ["receives_orders", "local_reasoning", "veto_escalation", "consensus_contribution"],
                },
                {
                    "node_id": "experts-hive",
                    "role": "Expert mini-brain",
                    "scope": "specialized knowledge, tools, and local evidence for each domain",
                    "reports_to": "AO Hive",
                    "state": map_state(teacher_profiles, "static-canon"),
                    "signals": ["receives_orders", "evidence_response", "execution_status", "consensus_contribution"],
                },
                {
                    "node_id": "tools-outputs",
                    "role": "Execution workforce",
                    "scope": "tool calls, build actions, artifacts, outputs, and operator-visible results",
                    "reports_to": "Experts Hive",
                    "state": map_state(recipes_summary or agent_capabilities, "static-canon"),
                    "signals": ["receives_orders", "execution_status", "evidence_response"],
                },
                {
                    "node_id": "memory-feedback",
                    "role": "Memory feedback loop",
                    "scope": "shared memory updates, source-to-claim maps, continuity, and learning feedback",
                    "reports_to": "NexusBrain",
                    "state": map_state(memory_configs or graph_summary or retrieval_summary, "static-canon"),
                    "signals": ["evidence_response", "consensus_contribution", "execution_status"],
                },
            ],
        }
        cockpit = {
            "surface_id": "mission-control-cockpit",
            "label": "NexusNet Mission Control",
            "primary_mode": "Command",
            "modes": [
                "Command",
                "Brain Map",
                "AOs",
                "Experts",
                "Security",
                "Runtime",
                "Memory",
                "Forward Radar",
            ],
            "command_chain": [
                "NexusBrain",
                "AO Hive",
                "Experts",
                "Tools/Outputs",
                "Memory Feedback",
                "NexusBrain",
            ],
            "command_bar": {
                "label": "Pilot Command Deck",
                "authority": "NexusBrain",
                "state": "live-bound" if active_command_id else "standby",
                "active_surface": "Command",
                "session_trace": recent_trace.get("trace_id") or "standby",
                "active_command_id": active_command_id,
                "primary_order": latest_operation_command.get("command_text")
                or "orchestrate NexusNet brain, AO hive, expert hive, tools, outputs, and memory feedback",
            },
            "command_rail": {
                "label": "Command Rail",
                "actions": [
                    "Refresh live state",
                    "Open wrapper",
                    "Open visualizer",
                    "Inspect selected brain surface",
                    "Review promotion gates",
                ],
            },
            "operations_board": {
                "label": "AO / Expert Operations Board",
                "columns": [
                    "NexusBrain orders",
                    "AO local reasoning",
                    "Expert evidence",
                    "Veto / escalation",
                    "Execution status",
                ],
                "live_columns": self._brain_operations_columns(operations_summary),
            },
            "alert_rail": {
                "label": "Alert Rail",
                "channels": [
                    "security posture",
                    "governance gates",
                    "runtime health",
                    "eval blockers",
                    "protocol permissions",
                ],
            },
            "timeline": {
                "label": "Operations Timeline",
                "lanes": [
                    "flow trace",
                    "decisions",
                    "tool runs",
                    "memory writes",
                    "autonomous update proposals",
                ],
                "events": live_operation_events,
            },
            "brain_map_deck": {
                "label": "Brain Map Deck",
                "role": "secondary cockpit deck for architecture inspection after the live command viewport",
            },
            "live_operations": operations_summary,
        }

        expert_topologies = [
            topology.model_dump(mode="json")
            for topology in self.compiler.topologies.values()
            if topology.authoritative_core_roster and not topology.auxiliary
        ]
        improvement_queue_items = ImprovementQueue(self.paths.state_dir / "self_improvement_queue.json").list_items()
        improvement_queue_summary = {
            "item_count": len(improvement_queue_items),
            "status_counts": status_counts([item.status for item in improvement_queue_items]),
        }

        pages = [
            page(
                "overview",
                "Overview",
                state="live-bound",
                summary="Brain authority, layer posture, live/degraded/static state, and promotion posture.",
                metrics={
                    "trace_count": telemetry_window.get("trace_count", 0),
                    "registry_layer": ((recent_trace.get("teacher_provenance") or {}).get("registry_layer")),
                    "promotion_candidate_count": count(promotion_items),
                    "recommended_render_tier": performance_profile.get("recommended_tier"),
                    "active_command_id": active_command_id,
                },
                refs=["/ops/brain/visualizer/state", "/ops/brain/wrapper-surface"],
                required=["brain authority", "12-layer posture", "state truthfulness", "promotion posture"],
            ),
            page(
                "input-ingestion",
                "Input Ingestion",
                state=map_state(active_command_id or retrieval_summary or acp_summary, "static-canon"),
                summary="User commands, files, project notes, code snippets, transcripts, external APIs, webhooks, events, streams, source permissions, and freshness.",
                metrics={
                    "active_command_id": active_command_id,
                    "command_count": operations_summary.get("command_count", 0),
                    "retrieval_scorecard": (((retrieval_summary.get("scorecards") or {}).get("latest_scorecard") or {}).get("scorecard_id")),
                    "permission_surface": "/ops/brain/security/permissions",
                },
                refs=["/ops/brain/canon/input-ingestion", "/ops/brain/operations", "/retrieval/ingest", "/ops/brain/security/permissions"],
                required=["user commands", "uploaded files", "project notes", "code snippets", "transcripts", "external APIs", "events", "streams", "source permissions", "freshness"],
                research=["agent-observability", "memory-rag-kg", "agent-protocols"],
            ),
            page(
                "live-flow-trace",
                "Live Flow Trace",
                state=map_state(recent_trace, "degraded"),
                summary="Route, model, memory, tool, policy, eval, and output trace correlation.",
                metrics={
                    "latest_trace_id": recent_trace.get("trace_id"),
                    "selected_ao": recent_trace.get("selected_ao"),
                    "selected_expert": recent_trace.get("selected_expert"),
                    "replay_frames": replay_catalog.get("frame_count", 0),
                },
                refs=["/ops/brain/visualizer/replay", "/ops/traces/{trace_id}"],
                required=["route trace", "memory trace", "tool trace", "policy trace", "eval link"],
                research=["agent-observability"],
            ),
            page(
                "neural-core",
                "Neural Core Orchestrator",
                state=map_state(core_execution.get("latest_trace_id"), "static-canon"),
                summary="NexusBrain routes, lock state, expert routing, policy decisions, and fallback paths.",
                metrics={
                    "brain_first_execution": core_execution.get("brain_first_execution"),
                    "execution_mode": core_execution.get("execution_mode"),
                    "selected_runtime_name": core_execution.get("selected_runtime_name"),
                    "latest_artifact_id": core_execution.get("latest_artifact_id"),
                },
                refs=["/ops/brain/core", "/ops/brain/wrapper-surface"],
                required=["NexusBrain authority", "fallback path", "policy decision", "artifact trace"],
            ),
            page(
                "ao-hive",
                "AO Hive",
                state=map_state(ao_records, "static-canon"),
                summary="AO roles, active work, context shards, model/tool permissions, and collaboration state.",
                metrics={
                    "ao_count": count(ao_records),
                    "agent_capability_count": count(agent_capabilities),
                    "active_agent_id": (agents.get("session_provenance") or {}).get("active_agent_id"),
                },
                refs=["/ops/brain/subagents", "/ops/brain/agents/scheduled"],
                required=["AO roles", "delegation state", "context ownership", "tool permissions"],
                research=["agent-protocols", "autonomous-updates"],
            ),
            page(
                "experts-hive",
                "Experts Hive",
                state=map_state(expert_topologies, "static-canon"),
                summary="Domain-specialized expert mini-brains with local reasoning, evidence response, consensus signals, veto escalation, and memory feedback.",
                metrics={
                    "expert_count": count(expert_topologies),
                    "selected_expert": recent_trace.get("selected_expert"),
                    "expert_signal_count": sum(len(event.get("signals") or []) for event in operations_summary.get("timeline", []) if event.get("event_type") == "expert_signal"),
                    "mini_nexusnet_per_expert": True,
                },
                refs=["/ops/brain/canon/experts-hive", "/ops/brain/core", "/ops/brain/operations", "nexusnet/visuals/expert_topologies.yaml"],
                required=["domain roster", "mini NexusNet per expert", "expert routing", "evidence response", "veto escalation", "memory feedback"],
                research=["agent-protocols", "agent-evals", "memory-rag-kg"],
            ),
            page(
                "hive-organization",
                "Hive Organization",
                state="static-canon",
                summary="Commanded collective hive structure: NexusBrain executive command, AO departments, Expert teams, tools, outputs, and memory feedback.",
                metrics={
                    "operating_model": hive_mind["operating_model_id"],
                    "command_chain_length": len(hive_mind["central_orchestrator"]["command_chain"]),
                    "mini_brain_count": len(hive_mind["mini_brain_nodes"]),
                    "signal_contract_count": len(hive_mind["mini_brain_signal_contract"]),
                },
                refs=["overlay.control_panel.hive_mind", "/ops/brain/visualizer/state"],
                required=["central orchestration", "AO departments", "expert mini-brains", "command chain", "feedback loop"],
                research=["agent-protocols", "agent-observability", "autonomous-updates"],
            ),
            page(
                "context-memory",
                "Context And Memory",
                state=map_state(memory_configs or graph_summary or retrieval_summary, "static-canon"),
                summary="Memory quality, source-to-claim maps, graph health, stale memory, and privacy controls.",
                metrics={
                    "memory_plane_count": count(memory_configs),
                    "projection_adapter_count": count(memory_planes.get("projection_adapters") or []),
                    "graph_status": graph_summary.get("status") or graph_summary.get("state"),
                    "retrieval_scorecard": (((retrieval_summary.get("scorecards") or {}).get("latest_scorecard") or {}).get("scorecard_id")),
                },
                refs=["/ops/memory/{session_id}", compare_refs.get("attention_comparative_summary")],
                required=["MemoryQualityLedger", "SourceClaimMap", "graph health", "staleness queue"],
                research=["memory-rag-kg"],
            ),
            page(
                "governance-observability",
                "Governance And Observability",
                state=map_state(telemetry_window.get("trace_count"), "degraded"),
                summary="Policies, GenAI trace mapping, redaction, audit trails, and export readiness.",
                metrics={
                    "trace_count": telemetry_window.get("trace_count", 0),
                    "source_status": telemetry_window.get("source_status", {}),
                    "safe_mode": safe_mode_physiology.get("safe_mode"),
                    "compare_ref_count": len(compare_refs),
                },
                refs=["/ops/brain/visualizer/state", "/ops/brain/security/adversary-reviews", "/ops/brain/security/permissions"],
                required=["TraceSchemaRegistry", "GenAISpanMapper", "TracePrivacyGate", "audit export"],
                research=["agent-observability", "ai-supply-chain"],
            ),
            page(
                "connections-protocols",
                "Connections And Protocols",
                state=map_state(acp_summary or extension_summary, "research-candidate"),
                summary="MCP, A2A, AG-UI, ACP, webhooks, buses, identities, consent, and trust envelopes.",
                metrics={
                    "acp_provider_count": acp_summary.get("provider_count", 0),
                    "acp_enabled": acp_summary.get("enabled", False),
                    "extension_count": extension_summary.get("extension_count", 0),
                    "approval_required_count": extension_summary.get("approval_required_count", 0),
                },
                refs=[compare_refs.get("goose_acp"), compare_refs.get("goose_extensions"), compare_refs.get("goose_extension_policy_sets")],
                required=["GovernedProtocolAdapterRegistry", "ProtocolTrustEnvelope", "identity ledger", "revocation controls"],
                research=["agent-protocols"],
            ),
            page(
                "communication-integration",
                "Communication And Integration",
                state=map_state(acp_summary or extension_summary or recipes_summary, "static-canon"),
                summary="Webhooks, message buses, event streams, sync, external integrations, notifications, and chat/collaboration channels.",
                metrics={
                    "acp_provider_count": acp_summary.get("provider_count", 0),
                    "extension_count": extension_summary.get("extension_count", 0),
                    "recipe_count": recipes_summary.get("recipe_count", 0),
                    "trust_adapter_state": "nexusbrain-governed",
                },
                refs=["/ops/brain/canon/communication-integration", "/ops/brain/canon/protocol-trust", "/ops/brain/gateway", "/ops/brain/extensions"],
                required=["webhooks", "message bus", "event streams", "real-time sync", "external services", "notifications", "chat collaboration"],
                research=["agent-protocols", "agent-observability"],
            ),
            page(
                "tools-execution",
                "Tools And Execution",
                state=map_state(recipes_summary or goose_security, "static-canon"),
                summary="Tool registry, sandboxing, approvals, failures, runtime isolation, and replay traces.",
                metrics={
                    "recipe_count": recipes_summary.get("recipe_count", 0),
                    "runbook_count": recipes_summary.get("runbook_count", 0),
                    "permission_mode": (((goose_security.get("permissions") or {}).get("active_mode") or {}).get("mode_id")),
                    "sandbox_profile": (((goose_security.get("sandbox") or {}).get("active_profile") or {}).get("profile_id")),
                },
                refs=[compare_refs.get("goose_recipes"), compare_refs.get("goose_runbooks"), compare_refs.get("goose_security_permissions"), compare_refs.get("goose_security_sandbox")],
                required=["tool registry", "sandbox state", "approval path", "execution replay"],
                research=["agent-protocols", "ai-supply-chain"],
            ),
            page(
                "claude-code-assimilation",
                "Claude Code Assimilation",
                state=assimilation_target_scorecard.get("runtime_state", "live-bound"),
                summary="Assimilated Claude-code-style harness targets: tool registry, rewind ledger, task graph, provider resilience, prompt overlays, plan jail, skill systems, bridges, and monitors.",
                metrics={
                    "target_count": assimilation_target_scorecard.get("target_count", 0),
                    "covered_target_count": len((assimilation_target_scorecard.get("coverage_summary") or {}).get("covered_target_ids") or []),
                    "skill_system_model": (assimilation_target_scorecard.get("coverage_summary") or {}).get("skill_system_model"),
                    "latest_skill_system": ((assimilation_target_scorecard.get("latest_skill_system") or {}).get("system_id")),
                },
                refs=["/ops/brain/canon/assimilation-targets", "/ops/brain/skill-systems/compose"],
                required=["ToolDef metadata", "checkpoint rewind", "task graph", "provider circuit breaker", "prompt overlays", "plan-mode jail", "skill-system orchestrator", "bridge catalog", "research monitor"],
                research=["agent-protocols", "agent-observability", "autonomous-updates"],
            ),
            page(
                "outputs-deliverables",
                "Outputs And Deliverables",
                state=map_state(recent_trace or replay_catalog or promotion_items, "static-canon"),
                summary="Architecture diagrams, implementation plans, source code, documentation, reports, working artifacts, exports, packages, and memory feedback.",
                metrics={
                    "latest_trace_id": recent_trace.get("trace_id"),
                    "replay_frame_count": replay_catalog.get("frame_count", 0),
                    "promotion_candidate_count": count(promotion_items),
                    "blackbox_ref": "/ops/brain/canon/blackbox",
                },
                refs=["/ops/brain/canon/output-delivery", "/ops/brain/canon/artifact-trust", "/ops/brain/canon/blackbox", "/ops/brain/canon/completion"],
                required=["architecture diagrams", "implementation plans", "source code", "documentation", "reports", "working artifacts", "exports", "memory feedback"],
                research=["agent-observability", "memory-rag-kg", "ai-supply-chain"],
            ),
            page(
                "runtime-lab",
                "Runtime Lab",
                state=map_state(runtime_candidates or brain_runtime_summary, "static-canon"),
                summary="Quantization formats, backend eligibility, cache economics, speculative decoding, and runtime scorecards.",
                metrics={
                    "runtime_candidate_count": count(runtime_candidates),
                    "selected_runtime_name": (recent_trace.get("runtime_selection") or {}).get("selected_runtime_name"),
                    "quantization_default": (brain_runtime_summary.get("quantization") or {}).get("default"),
                    "aitune_status": ((brain_runtime_summary.get("aitune") or {}).get("supported_lane_readiness") or {}).get("status"),
                },
                refs=["/ops/brain/backends", compare_refs.get("runtime_doctor"), compare_refs.get("aitune_execution_plan")],
                required=["RuntimeWorkloadScorecard", "KVCacheLedger", "cache economics", "backend eligibility"],
                research=["inference-architecture"],
            ),
            page(
                "eval-center",
                "Eval Center",
                state=map_state(promotions or retrieval_summary or teacher_visibility.get("scorecards"), "static-canon"),
                summary="GAIA, tau-bench, OSWorld, SWE-bench, BrowserGym/WebArena, RAG, private NexusNet evals, and promotion blockers.",
                metrics={
                    "promotion_candidate_count": count(promotion_items),
                    "teacher_scorecard_count": count(teacher_visibility.get("scorecards") or []),
                    "retrieval_review_count": count(retrieval_summary.get("promotion_reviews") or []),
                    "held_out_eval_state": "required",
                },
                refs=["/ops/brain/promotions", "/ops/brain/promotions/evaluate", compare_refs.get("cost_energy")],
                required=["EvalSuiteRegistry", "HeldOutTaskLedger", "TraceReplayEvalHarness", "regression gates"],
                research=["agent-evals", "memory-rag-kg"],
            ),
            page(
                "artifact-trust",
                "Artifact Trust",
                state=map_state(extension_summary or teacher_profiles, "research-candidate"),
                summary="Model provenance, signatures, AI-BOM, unsafe serialization, scanner results, and license review.",
                metrics={
                    "teacher_profile_count": count(teacher_profiles),
                    "extension_count": extension_summary.get("extension_count", 0),
                    "certification_count": (goose.get("extension_certifications") or {}).get("artifact_count", 0),
                    "unsafe_serialization_gate": "required",
                },
                refs=[compare_refs.get("goose_extension_certifications"), compare_refs.get("goose_extension_certification_compare")],
                required=["ArtifactTrustLedger", "AIBillOfMaterials", "UnsafeArtifactGate", "LicenseReviewRollup"],
                research=["ai-supply-chain"],
            ),
            page(
                "hardware-matrix",
                "Hardware Matrix",
                state=map_state(runtime_summary.get("device_profile"), "static-canon"),
                summary="Browser, desktop, mobile, NPU, GPU, CPU, server, and edge deployment lanes.",
                metrics={
                    "device_profile": runtime_summary.get("device_profile") or {},
                    "hardware_classes": filter_catalog.get("hardware_classes", []),
                    "recommended_render_tier": performance_profile.get("recommended_tier"),
                    "edge_lane_state": "required",
                },
                refs=[compare_refs.get("runtime_init"), compare_refs.get("runtime_doctor"), "/ops/brain/vision/edge-lane"],
                required=["EdgeHardwareMatrix", "BackendEligibilityReport", "RuntimeCompatibilityLedger", "DeviceCertificationGate"],
                research=["edge-local-hardware"],
            ),
            page(
                "visualops",
                "VisualOps",
                state="live-bound",
                summary="Multimodal computer-use traces, OCR/VLM state, screen actions, and safety gates.",
                metrics={
                    "scene_version": self.scene.scene_version,
                    "replay_available": replay_catalog.get("available", False),
                    "replay_frame_count": replay_catalog.get("frame_count", 0),
                    "depth_renderer_allowed": performance_profile.get("allow_depth_enhancement"),
                },
                refs=["/ui/visualizer/", "/ops/brain/visualizer/state", "/ops/brain/visualizer/replay"],
                required=["ComputerUseSafetyCase", "VisualParseTrace", "ActionPermissionGate", "ScreenAgentEvalReport"],
                research=["multimodal-computer-use"],
            ),
            page(
                "dreaming-evolution",
                "Dreaming And Evolution",
                state=map_state(promotion_items or snapshot.get("dream_activity"), "static-canon"),
                summary="Research candidates, self-review, autonomous update proposals, shadow simulations, and rollback.",
                metrics={
                    "promotion_candidate_count": count(promotion_items),
                    "dream_derived_trace_count": sum(
                        1
                        for trace in self.store.list_traces(limit=40)
                        if (trace.get("teacher_provenance") or {}).get("dream_lineage") == "dream-derived"
                    ),
                    "rollback_readiness": "required",
                },
                refs=["/ops/brain/promotions", "/ops/brain/foundry/status", compare_refs.get("scheduled_agents")],
                required=["HarnessImprovementLedger", "ResearchCandidateRegistry", "PromotionProvenanceGate", "RollbackReadinessRecord"],
                research=["autonomous-updates", "agent-evals"],
            ),
            page(
                "self-improvement-layer",
                "Self-Improvement Layer",
                state=map_state(improvement_queue_items or snapshot.get("dream_activity"), "static-canon"),
                summary="Experience capture, ImprovementEvent schema, data triage, provenance tracking, eval generation, improvement queue, update policies, and regression gates.",
                metrics={
                    "queue_item_count": improvement_queue_summary["item_count"],
                    "queued_status_counts": improvement_queue_summary["status_counts"],
                    "model_update_boundary": "human-review-external-verification-regression-gates",
                    "direct_training_enabled": False,
                },
                refs=["/ops/brain/canon/self-improvement", "/ops/brain/self-improvement/queue", "docs/SELF_IMPROVEMENT_LAYER.md"],
                required=["experience capture", "event schema", "triage", "provenance", "eval generation", "queue", "memory/prompt policy", "training review", "regression gates"],
                research=["autonomous-updates", "agent-evals", "memory-rag-kg", "multimodal-computer-use"],
            ),
            page(
                "forward-radar",
                "Forward Radar",
                state="research-candidate",
                summary="Living watchlist for quantization, protocols, evals, memory, supply chain, edge runtimes, and computer use.",
                metrics={
                    "lane_count": len(research_lanes),
                    "candidate_lane_count": sum(1 for lane in research_lanes if lane["status"] == "candidate"),
                    "shadow_lane_count": sum(1 for lane in research_lanes if lane["status"] == "shadow-only"),
                    "source_date": "2026-04-28",
                },
                refs=["docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md", "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md"],
                required=["freshness", "evidence", "maturity", "impact", "promotion gates"],
                research=[lane["lane_id"] for lane in research_lanes],
            ),
        ]
        pages.append(
            page(
                "dataset-radar",
                "Dataset Radar",
                state=dataset_radar.get("runtime_state", "live-bound"),
                summary="Living dataset discovery, source-state gating, teacher context routing, sealed eval separation, and student lineage.",
                metrics={
                    "source_count": dataset_radar.get("source_count", 0),
                    "approved_train_count": dataset_radar.get("approved_train_count", 0),
                    "blocked_count": dataset_radar.get("blocked_count", 0),
                    "candidate_count": dataset_radar.get("candidate_count", 0),
                },
                refs=["/ops/brain/dataset-radar", "/ops/brain/dataset-radar/sources", "/ops/brain/canon/dataset-radar"],
                required=["source freshness", "license state", "privacy gate", "teacher context gate", "sealed eval split", "student targets"],
                research=["memory-rag-kg", "agent-evals", "ai-supply-chain"],
            )
        )
        pages.append(
            page(
                "knowledge-artifacts",
                "Knowledge Artifacts",
                state=knowledge_artifacts.get("runtime_state", "static-canon"),
                summary="Compiled task-specific context artifacts with field-level citations, source digests, conflict objects, freshness invalidation, permission filters, and raw retrieval fallback.",
                metrics={
                    "artifact_count": knowledge_artifacts.get("artifact_count", 0),
                    "stale_count": knowledge_artifacts.get("stale_count", 0),
                    "query_event_count": knowledge_artifacts.get("query_event_count", 0),
                    "conflict_count": latest_knowledge_artifact.get("conflict_count", 0),
                    "excluded_source_count": latest_knowledge_artifact.get("excluded_source_count", 0),
                    "blocked_source_ref_count": (
                        latest_knowledge_artifact.get("source_ref_security_gate") or {}
                    ).get("blocked_count", 0),
                    "artifact_trust_preview_status": (
                        latest_knowledge_artifact.get("artifact_trust_preview") or {}
                    ).get("status", "not_scanned"),
                    "active_runtime_blocker_count": len(knowledge_artifacts.get("active_runtime_blockers") or []),
                    "downstream_runtime_gate_gated_count": knowledge_artifact_runtime_gate_coverage.get("gated_consumer_count", 0),
                    "downstream_runtime_gate_enforced_count": knowledge_artifact_runtime_gate_coverage.get(
                        "enforced_consumer_count",
                        0,
                    ),
                    "downstream_runtime_gate_required_count": knowledge_artifact_runtime_gate_coverage.get(
                        "required_consumer_count",
                        0,
                    ),
                    "downstream_runtime_gate_all_gated": knowledge_artifact_runtime_gate_coverage.get(
                        "all_runtime_consumers_gated",
                        False,
                    ),
                    "downstream_runtime_gate_proof_ref_count": knowledge_artifact_runtime_gate_coverage.get(
                        "proof_ref_count",
                        0,
                    ),
                },
                refs=[
                    "/ops/brain/knowledge-artifacts",
                    "/ops/brain/knowledge-artifacts/compile",
                    "/ops/brain/knowledge-artifacts/query",
                    "/ops/brain/knowledge-artifacts/query-events",
                    "/ops/brain/canon/knowledge-artifacts",
                    "/ops/brain/artifact-trust/knowledge-artifacts/scan",
                    *knowledge_artifact_runtime_gate_coverage.get("proof_refs", [])[:8],
                ],
                required=[
                    "field citations",
                    "source digests",
                    "freshness",
                    "RBAC/privacy filter",
                    "conflict objects",
                    "raw retrieval fallback",
                    "source-ref security gate",
                    "artifact trust preview",
                    "runtime gate proof refs",
                ],
                research=["memory-rag-kg", "agent-evals", "ai-supply-chain"],
            )
        )

        build_gates = [
            {
                "gate_id": "canon-book-updated",
                "label": "Complete chat canon book carries 2026 research refresh.",
                "state": "satisfied",
                "evidence_ref": "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md#2026-research-refresh-integration-addendum",
            },
            {
                "gate_id": "truthful-live-state",
                "label": "Live cards must be backed by endpoints or shown as degraded/static/research.",
                "state": "enforced",
                "evidence_ref": "/ops/brain/visualizer/state",
            },
            {
                "gate_id": "brain-authority",
                "label": "Protocol adapters, tools, and autonomous updates remain subordinate to NexusBrain governance.",
                "state": "enforced",
                "evidence_ref": "/ops/brain/core",
            },
            {
                "gate_id": "research-candidate-boundary",
                "label": "Forward-looking items stay candidate/shadow-only until promotion gates pass.",
                "state": "enforced",
                "evidence_ref": "overlay.control_panel.research_lanes",
            },
        ]
        canon_realization = build_canon_realization(
            session_id=session_id,
            pages=pages,
            research_lanes=research_lanes,
            build_gates=build_gates,
            cockpit=cockpit,
            operations_summary=operations_summary,
        )
        runtime_scorecard = runtime_quantization_scorecard(
            control_panel={
                "quantization_catalog": quantization_catalog,
                "canon_realization": canon_realization,
            },
        )
        evolution_dossier = autonomous_evolution_dossier(canon_realization)
        self_improvement = self_improvement_scorecard(canon_realization, queue_summary=improvement_queue_summary)
        protocol_trust = protocol_trust_scorecard(canon_realization)
        communication_integration = communication_integration_scorecard(canon_realization)
        eval_suite = eval_suite_scorecard(canon_realization)
        memory_provenance = memory_provenance_scorecard(canon_realization)
        artifact_trust = artifact_trust_scorecard(canon_realization)
        hardware_matrix = hardware_matrix_scorecard(canon_realization)
        visualops = visualops_scorecard(canon_realization)
        input_ingestion = input_ingestion_scorecard(canon_realization, operations_summary=operations_summary)
        live_flow = live_flow_scorecard(canon_realization, operations_summary=operations_summary)
        neural_core = neural_core_scorecard(canon_realization, operations_summary=operations_summary)
        tool_execution = tool_execution_scorecard(canon_realization)
        output_delivery = output_delivery_scorecard(canon_realization)
        ao_hive = ao_hive_scorecard(
            canon_realization,
            ao_snapshot=aos,
            operations_summary=operations_summary,
        )
        experts_hive = experts_hive_scorecard(
            canon_realization,
            operations_summary=operations_summary,
            expert_topologies=expert_topologies,
        )
        observability = observability_scorecard(canon_realization)
        security_governance = security_governance_scorecard(canon_realization)
        policy_kernel = PolicyKernel.default().scorecard()
        agentic_pipeline = AgenticPipelineRuntime(artifacts_dir=self.paths.artifacts_dir).scorecard(session_id=session_id)
        agent_opportunities = AgentOpportunityDiscovery(artifacts_dir=self.paths.artifacts_dir).scorecard()
        harness_provider = self.harness_provider_registry.scorecard()
        harness_routing = self.harness_model_router.scorecard()
        harness_improvement_ledger = HarnessImprovementLedger(artifacts_dir=self.paths.artifacts_dir).scorecard()
        edge_workload_router = EdgeWorkloadRouter(artifacts_dir=self.paths.artifacts_dir).scorecard()
        multimodal_computer_use = MultimodalComputerUseController(artifacts_dir=self.paths.artifacts_dir).scorecard()
        inference_economy_router = InferenceEconomyRouter(artifacts_dir=self.paths.artifacts_dir).scorecard()
        inference_architecture = InferenceArchitectureRegistry(artifacts_dir=self.paths.artifacts_dir).scorecard()
        cache_ledger = EffectiveContextCacheLedger(artifacts_dir=self.paths.artifacts_dir).scorecard()
        runtime_workload_scorecards = RuntimeWorkloadScorecardRegistry(artifacts_dir=self.paths.artifacts_dir).scorecard()
        quantization_catalog_scorecard = QuantizationCatalog.default(artifacts_dir=self.paths.artifacts_dir).scorecard()
        protocol_trust_registry = ProtocolTrustRegistry(artifacts_dir=self.paths.artifacts_dir).scorecard()
        browser_context = BrowserContextMemory(artifacts_dir=self.paths.artifacts_dir).scorecard()
        adapter_registry = AdapterForgeRegistry(artifacts_dir=self.paths.artifacts_dir).scorecard()
        fine_tune_decision_gate = FineTuneDecisionGate(artifacts_dir=self.paths.artifacts_dir).scorecard()
        adapter_training = AdapterTrainingPlanner(artifacts_dir=self.paths.artifacts_dir).scorecard()
        growth_engine = HiveModelGrowthEngine(artifacts_dir=self.paths.artifacts_dir).scorecard()
        production_spine = NexusNetProductionSpine(artifacts_dir=self.paths.artifacts_dir).scorecard()
        eval_registry = EvalRegistry.default(artifacts_dir=self.paths.artifacts_dir).scorecard()
        artifact_trust_registry = ArtifactTrustRegistry(artifacts_dir=self.paths.artifacts_dir).scorecard()
        autonomous_updates = AutonomousUpdateController(artifacts_dir=self.paths.artifacts_dir).scorecard()
        genai_observability = GenAITraceRegistry(artifacts_dir=self.paths.artifacts_dir).scorecard()
        self_review = SelfReviewGate(artifacts_dir=self.paths.artifacts_dir).scorecard()
        forward_radar = ForwardRadarRegistry(artifacts_dir=self.paths.artifacts_dir).scorecard()
        memory_quality = MemoryQualityLedger(artifacts_dir=self.paths.artifacts_dir).scorecard()
        engram_memory = NexusEngramIndex(artifacts_dir=self.paths.artifacts_dir).scorecard()
        retrieval_planner = self.retrieval_planner.summary()
        self_improvement_lineage = self.self_improvement_lineage.summary()
        verifier_search = self.verifier_search.summary()
        browser_profile_policy = self.browser_profile_policy.summary()
        operator_events = self.operator_events.summary()
        edge_model_certification = self.edge_model_certification.summary()
        concept_telemetry = self.concept_telemetry.summary()
        codegraph_gate = self.codegraph_gate.summary()
        blackbox = blackbox_recorder(canon_realization)
        hive_consensus = hive_consensus_scorecard(
            canon_realization,
            operations_summary=operations_summary,
            hive_mind=hive_mind,
        )
        researcher_swarm = researcher_swarm_scorecard(canon_realization)

        control_panel = {
            "title": "NexusNet Control Panel",
            "state_model": ["live-bound", "degraded", "static-canon", "research-candidate", "shadow-only"],
            "source_documents": [
                "docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md",
                "docs/NEXUSNET_COMPLETE_CANON_RESEARCH_REFRESH_DIFF_2026-04-28.md",
                "docs/NEXUSNET_OPEN_FIRST_RESEARCH_EXPANSION_2026-04-28.md",
                "docs/NEXUSNET_QUANTIZATION_AGENTIC_RESEARCH_EXPANSION_2026-04-28.md",
                "docs/NEXUSNET_FORWARD_RESEARCH_RADAR_2026-04-28.md",
                "docs/NEXUSNET_FORWARD_RESEARCH_DEEP_DIVE_2026-04-28.md",
                "docs/NEXUSNET_RESEARCH_CANDIDATE_DOSSIER_2026-04-28.md",
            ],
            "pages": pages,
            "page_count": len(pages),
            "research_lanes": research_lanes,
            "quantization_catalog": quantization_catalog,
            "hive_mind": hive_mind,
            "cockpit": cockpit,
            "canon_realization": canon_realization,
            "completion_assessment": canon_realization["completion_assessment"],
            "runtime_scorecard": runtime_scorecard,
            "evolution_dossier": evolution_dossier,
            "developmental_cortex_scorecard": self.developmental_cortex.scorecard(),
            "authority_spine_scorecard": self.authority_spine.summary(),
            "evidence_store_scorecard": self.evidence_store.projection(),
            "eval_federation_scorecard": self.eval_federation.summary(),
            "tool_action_harness_scorecard": self.tool_action_harness.summary(),
            "runtime_decision_ledger_scorecard": self.runtime_decision_ledger.summary(),
            "assimilation_target_catalog_scorecard": self.assimilation_catalog.scorecard(),
            "self_improvement_scorecard": self_improvement,
            "protocol_trust_scorecard": protocol_trust,
            "communication_integration_scorecard": communication_integration,
            "eval_suite_scorecard": eval_suite,
            "memory_provenance_scorecard": memory_provenance,
            "artifact_trust_scorecard": artifact_trust,
            "hardware_matrix_scorecard": hardware_matrix,
            "visualops_scorecard": visualops,
            "input_ingestion_scorecard": input_ingestion,
            "live_flow_scorecard": live_flow,
            "neural_core_scorecard": neural_core,
            "tool_execution_scorecard": tool_execution,
            "assimilation_target_scorecard": assimilation_target_scorecard,
            "video_assimilation_scorecard": video_assimilation_scorecard,
            "retrieval_planner_scorecard": retrieval_planner,
            "self_improvement_lineage_scorecard": self_improvement_lineage,
            "verifier_search_scorecard": verifier_search,
            "browser_profile_policy_scorecard": browser_profile_policy,
            "operator_events_scorecard": operator_events,
            "edge_model_certification_scorecard": edge_model_certification,
            "concept_telemetry_scorecard": concept_telemetry,
            "codegraph_gate_scorecard": codegraph_gate,
            "output_delivery_scorecard": output_delivery,
            "ao_hive_scorecard": ao_hive,
            "experts_hive_scorecard": experts_hive,
            "observability_scorecard": observability,
            "security_governance_scorecard": security_governance,
            "policy_kernel_scorecard": policy_kernel,
            "agentic_pipeline_scorecard": agentic_pipeline,
            "agent_opportunity_scorecard": agent_opportunities,
            "harness_provider_scorecard": harness_provider,
            "harness_routing_scorecard": harness_routing,
            "harness_improvement_ledger": harness_improvement_ledger,
            "edge_workload_router_scorecard": edge_workload_router,
            "multimodal_computer_use_scorecard": multimodal_computer_use,
            "inference_economy_router_scorecard": inference_economy_router,
            "inference_architecture_scorecard": inference_architecture,
            "cache_ledger_scorecard": cache_ledger,
            "runtime_workload_scorecards": runtime_workload_scorecards,
            "quantization_catalog_scorecard": quantization_catalog_scorecard,
            "protocol_trust_registry_scorecard": protocol_trust_registry,
            "browser_context_scorecard": browser_context,
            "dataset_radar_scorecard": dataset_radar,
            "dataset_flow_view": dataset_flow_view,
            "dataset_forge_scorecard": dataset_forge,
            "knowledge_artifacts_scorecard": knowledge_artifacts,
            "adapter_registry_scorecard": adapter_registry,
            "fine_tune_decision_gate_scorecard": fine_tune_decision_gate,
            "adapter_training_scorecard": adapter_training,
            "growth_engine_scorecard": growth_engine,
            "production_spine_scorecard": production_spine,
            "eval_registry_scorecard": eval_registry,
            "artifact_trust_registry_scorecard": artifact_trust_registry,
            "autonomous_update_scorecard": autonomous_updates,
            "release_wrapper_runtime": release_wrapper_runtime,
            "release_wrapper_privacy_consent": release_wrapper_privacy_consent,
            "release_wrapper_privacy_consent_enforcement": release_wrapper_privacy_consent_enforcement,
            "release_wrapper_privacy_retention_enforcement": release_wrapper_privacy_retention_enforcement,
            "project_heartbeat": project_heartbeat,
            "project_heartbeat_native_replay_status": native_project_heartbeat_replay_status,
            "release_wrapper_telemetry": release_wrapper_telemetry,
            "release_wrapper_self_repair_ledger": release_wrapper_self_repair_ledger,
            "release_wrapper_boot_supervisor": release_wrapper_boot_supervisor,
            "release_wrapper_initial_release_supervisor": release_wrapper_initial_release_supervisor,
            "release_wrapper_release_product_smoke": release_wrapper_release_product_smoke,
            "release_wrapper_release_run_history": release_wrapper_release_run_history,
            "release_wrapper_native_hive_heartbeat_watchdog": release_wrapper_native_hive_heartbeat_watchdog,
            "release_wrapper_release_health_heartbeat": release_wrapper_release_health_heartbeat,
            "release_wrapper_release_health_heartbeat_loop": release_wrapper_release_health_heartbeat_loop,
            "release_wrapper_release_health_heartbeat_supervisor": release_wrapper_release_health_heartbeat_supervisor,
            "release_wrapper_canon_contract_ledger": release_wrapper_canon_contract_ledger,
            "release_wrapper_canon_contract_receipts": release_wrapper_canon_contract_receipts,
            "release_wrapper_developmental_release_contract": release_wrapper_developmental_release_contract,
            "release_wrapper_forward_pass_enforcement_matrix": release_wrapper_forward_pass_enforcement_matrix,
            "release_wrapper_session_lifecycle": release_wrapper_session_lifecycle,
            "direct_nexusbrain_native_growth_governance": direct_nexusbrain_native_growth_governance,
            "release_wrapper_readiness": snapshot.get("release_readiness"),
            "genai_observability_scorecard": genai_observability,
            "self_review_scorecard": self_review,
            "forward_radar_scorecard": forward_radar,
            "memory_quality_scorecard": memory_quality,
            "engram_memory_scorecard": engram_memory,
            "blackbox_recorder": blackbox,
            "hive_consensus_scorecard": hive_consensus,
            "researcher_swarm_scorecard": researcher_swarm,
            "book_gate_summary": canon_realization["book_gate_coverage"],
            "build_gates": build_gates,
            "live_refs": {
                "visualizer_state": "/ops/brain/visualizer/state",
                "wrapper_surface": "/ops/brain/wrapper-surface",
                "replay": "/ops/brain/visualizer/replay",
                "compare_refs": compare_refs,
                "diff_catalog": diff_catalog,
                "dataset_radar": "/ops/brain/dataset-radar",
                "dataset_flow_view": "overlay.control_panel.dataset_flow_view",
                "knowledge_artifacts": "/ops/brain/knowledge-artifacts",
                "project_heartbeat": "overlay.control_panel.project_heartbeat",
                "project_heartbeat_native_replay_status": (
                    "overlay.control_panel.project_heartbeat_native_replay_status"
                ),
                "release_wrapper_telemetry": "overlay.control_panel.release_wrapper_telemetry",
                "release_wrapper_privacy_consent": "overlay.control_panel.release_wrapper_privacy_consent",
                "release_wrapper_privacy_consent_enforcement": (
                    "overlay.control_panel.release_wrapper_privacy_consent_enforcement"
                ),
                "release_wrapper_privacy_retention_enforcement": (
                    "overlay.control_panel.release_wrapper_privacy_retention_enforcement"
                ),
                "release_wrapper_self_repair_ledger": "overlay.control_panel.release_wrapper_self_repair_ledger",
                "direct_nexusbrain_native_growth_governance": (
                    "overlay.control_panel.direct_nexusbrain_native_growth_governance"
                ),
            },
        }
        return self._sanitize_control_panel_session_ids(control_panel, session_id=session_id)

    def _sanitize_control_panel_session_ids(self, value: Any, *, session_id: str | None) -> Any:
        session_ref_digest = self._session_ref_digest(session_id)
        if isinstance(value, dict):
            sanitized: dict[str, Any] = {}
            for key, item in value.items():
                if key == "session_id":
                    if session_ref_digest:
                        sanitized["session_ref_digest"] = session_ref_digest
                    sanitized["raw_session_id_included"] = False
                    continue
                sanitized[key] = self._sanitize_control_panel_session_ids(item, session_id=session_id)
            return sanitized
        if isinstance(value, list):
            return [self._sanitize_control_panel_session_ids(item, session_id=session_id) for item in value]
        return value

    def _session_ref_digest(self, session_id: str | None) -> str | None:
        if session_id is None or str(session_id).strip() == "":
            return None
        return hashlib.sha256(str(session_id).encode("utf-8")).hexdigest()[:16]

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
