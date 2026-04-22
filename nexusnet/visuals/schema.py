from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from nexusnet.schemas import StatusLabel


class VisualMode(BaseModel):
    mode_id: str
    label: str
    description: str
    status_label: StatusLabel = "LOCKED CANON"
    palette: dict[str, str] = Field(default_factory=dict)
    animation_profile: dict[str, float | bool | str] = Field(default_factory=dict)
    preferred_renderer: Literal["svg-canvas", "threejs-enhanced"] = "svg-canvas"
    allow_threejs_enhancement: bool = False
    label_density: Literal["high", "medium", "low"] = "medium"


class ExpertTopology(BaseModel):
    subject: str
    display_name: str
    topology_id: str
    canon_status: StatusLabel = "LOCKED CANON"
    auxiliary: bool = False
    authoritative_core_roster: bool = True
    geometry_kind: str
    palette_key: str
    layer_count: int = 3
    neural_node_budget: int = 18
    motif_labels: list[str] = Field(default_factory=list)
    role_hint: str = ""
    description: str = ""
    inspect: dict[str, Any] = Field(default_factory=dict)


class SceneNode(BaseModel):
    node_id: str
    node_type: Literal["core", "capsule", "subnode", "overlay-anchor"]
    label: str
    x: float
    y: float
    z: float = 0.0
    radius: float = 0.0
    status_label: StatusLabel = "LOCKED CANON"
    subject: str | None = None
    topology_id: str | None = None
    layer_index: int = 0
    internal_nodes: list[dict[str, Any]] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)


class SceneLink(BaseModel):
    link_id: str
    source_id: str
    target_id: str
    link_type: Literal["core", "collaboration", "critique", "dream", "consequence", "physiology"]
    strength: float = 1.0
    animated: bool = True
    status_label: StatusLabel = "LOCKED CANON"
    meta: dict[str, Any] = Field(default_factory=dict)


class SceneLoop(BaseModel):
    loop_id: str
    loop_type: Literal["dream", "critique", "consequence"]
    label: str
    orbit_radius: float
    target_subjects: list[str] = Field(default_factory=list)
    status_label: StatusLabel = "LOCKED CANON"
    meta: dict[str, Any] = Field(default_factory=dict)


class OverlayBinding(BaseModel):
    binding_id: str
    label: str
    target_id: str
    channel: str
    source_ref: str
    status_label: StatusLabel = "LOCKED CANON"
    active: bool = True
    meta: dict[str, Any] = Field(default_factory=dict)


class VisualManifest(BaseModel):
    schema_version: str
    status_label: StatusLabel = "LOCKED CANON"
    visualizer_id: str
    title: str
    description: str
    default_mode_id: str
    default_renderer: Literal["svg-canvas", "threejs-enhanced"] = "svg-canvas"
    core: dict[str, Any] = Field(default_factory=dict)
    capsules: dict[str, Any] = Field(default_factory=dict)
    layout: dict[str, Any] = Field(default_factory=dict)
    collaboration_groups: list[dict[str, Any]] = Field(default_factory=list)
    loop_definitions: list[dict[str, Any]] = Field(default_factory=list)
    overlay_channels: list[dict[str, Any]] = Field(default_factory=list)
    safe_mode_channels: list[str] = Field(default_factory=list)
    render_policy: dict[str, Any] = Field(default_factory=dict)
    legend: dict[str, Any] = Field(default_factory=dict)


class SceneBundle(BaseModel):
    status_label: StatusLabel = "LOCKED CANON"
    scene_version: str
    default_mode_id: str
    manifest: dict[str, Any]
    modes: list[dict[str, Any]] = Field(default_factory=list)
    topologies: list[dict[str, Any]] = Field(default_factory=list)
    nodes: list[SceneNode] = Field(default_factory=list)
    links: list[SceneLink] = Field(default_factory=list)
    loops: list[SceneLoop] = Field(default_factory=list)
    overlay_bindings: list[OverlayBinding] = Field(default_factory=list)
    legend: dict[str, Any] = Field(default_factory=dict)


class VisualizerOverlayState(BaseModel):
    status_label: StatusLabel = "LOCKED CANON"
    scene_version: str
    active_session_id: str | None = None
    active_registry_layer: str | None = None
    selected_teachers: dict[str, str | None] = Field(default_factory=dict)
    active_subjects: list[str] = Field(default_factory=list)
    arbitration_result: str | None = None
    benchmark_refs: list[str] = Field(default_factory=list)
    threshold_refs: list[str] = Field(default_factory=list)
    route_activity: dict[str, Any] = Field(default_factory=dict)
    dream_activity: dict[str, Any] = Field(default_factory=dict)
    promotion_cues: dict[str, Any] = Field(default_factory=dict)
    takeover_cues: dict[str, Any] = Field(default_factory=dict)
    runtime_posture: dict[str, Any] = Field(default_factory=dict)
    safe_mode_physiology: dict[str, Any] = Field(default_factory=dict)
    link_activity: dict[str, Any] = Field(default_factory=dict)
    loop_activity: dict[str, Any] = Field(default_factory=dict)
    evidence_activity: dict[str, Any] = Field(default_factory=dict)
    physiology_activity: dict[str, Any] = Field(default_factory=dict)
    telemetry_window: dict[str, Any] = Field(default_factory=dict)
    telemetry_sources: dict[str, Any] = Field(default_factory=dict)
    teacher_evidence_refs: dict[str, list[str]] = Field(default_factory=dict)
    foundry_evidence_refs: dict[str, list[str]] = Field(default_factory=dict)
    inspection_controls: dict[str, Any] = Field(default_factory=dict)
    filter_catalog: dict[str, Any] = Field(default_factory=dict)
    diff_catalog: dict[str, Any] = Field(default_factory=dict)
    replay_catalog: dict[str, Any] = Field(default_factory=dict)
    performance_profile: dict[str, Any] = Field(default_factory=dict)
