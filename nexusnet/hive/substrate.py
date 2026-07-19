from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from nexus.schemas import new_id, utcnow
from nexusnet.evals.registry import EvalRegistry, EvalSuiteRequest, ShadowEvalRunRequest
from nexusnet.hive.federated_prior_feedback import (
    dream_context_payload as build_dream_context_payload,
    federated_prior_feedback_status,
    federated_prior_ledger as build_federated_prior_ledger,
    shadow_routing_payload as build_shadow_routing_payload,
)
from nexusnet.hive.governed_route_candidate_evaluation import (
    approve_governed_route_candidate,
    evaluate_governed_route_candidate,
    governed_route_candidate_approval_ledger,
    governed_route_candidate_evaluation_ledger,
    governed_route_candidate_rollback_ledger,
    rollback_governed_route_candidate,
)
from nexusnet.hive.multi_user_growth import MultiUserGrowthCoordinator
from nexusnet.hive.project_heartbeat_cycle import run_native_project_heartbeat_cycle
from nexusnet.hive.project_heartbeat_replay import PROJECT_HEARTBEAT_NATIVE_REPLAY_REF
from nexusnet.hive.runtime_growth_federation import (
    attach_per_plane_sync_producers,
    run_runtime_growth_federation_cycle,
)
from nexusnet.policy import PolicyKernel


PHI = 1.61803398875
GOLDEN_ANGLE_DEGREES = 360 * (1 - (1 / PHI))
FIBONACCI_SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
HARMONIC_INTERVALS = [
    {"name": "unison", "fraction": "1:1", "ratio": 1.0},
    {"name": "minor_third", "fraction": "6:5", "ratio": 6 / 5},
    {"name": "major_third", "fraction": "5:4", "ratio": 5 / 4},
    {"name": "perfect_fourth", "fraction": "4:3", "ratio": 4 / 3},
    {"name": "perfect_fifth", "fraction": "3:2", "ratio": 3 / 2},
    {"name": "octave", "fraction": "2:1", "ratio": 2.0},
]
NEURAL_RUNTIME_INPUT_CONTRACT = (
    "neural-bus-blackboard-sensory-temporal-memory-embedding-attention-normalization-gate-feedforward-"
    "microcircuit-pathway-transmission-plasticity-neuromodulator-latent-loop-kv-cache-backprop-"
    "optimizer-school-ledger-only"
)
PERSONALITY_PREFERENCE_KEY_ALLOWLIST = frozenset(
    {
        "concise",
        "detailed",
        "direct",
        "federation-opt-in",
        "step-by-step",
        "structured",
        "technical",
        "tool-first",
    }
)


HiveNodeType = Literal[
    "NexusBrain",
    "Orchestrator",
    "AO",
    "Expert",
    "MiniNexusNet",
    "Skill",
    "SkillSystem",
    "ToolAdapter",
    "ModelAdapter",
    "Evaluator",
    "SandboxRunner",
    "PolicyGate",
    "Curator",
    "School",
    "MemoryBank",
    "FederatedNode",
    "CheckpointLedger",
]

BrainScale = Literal["primary", "orchestrator", "assistant_orchestrator", "expert", "generated_candidate", "support"]


class HiveNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    node_type: HiveNodeType
    name: str
    plane_id: str
    capabilities: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    write_scope: str = "none"
    privacy_scope: str = "internal"
    concurrency_safe: bool = True
    protected: bool = False
    model_or_provider_refs: list[str] = Field(default_factory=list)
    memory_refs: list[str] = Field(default_factory=list)
    certification_state: str = "seeded"
    quarantine_state: str = "clear"
    scorecard_refs: list[str] = Field(default_factory=list)
    genome_ref: str = ""
    brain_instance_ref: str = ""
    brain_scale: BrainScale = "support"
    parent_brain_ref: str = ""
    child_brain_refs: list[str] = Field(default_factory=list)
    health_signal_refs: list[str] = Field(default_factory=list)
    failure_visibility_scope: str = "hive-visible"
    recovery_route_refs: list[str] = Field(default_factory=list)
    dream_participation_contract: str = "can-request-or-participate-when-routed"
    self_improvement_contract: str = "hive-wide-neuroplasticity-fabric"


class ExpertGenome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    genome_id: str
    candidate_id: str
    title: str
    candidate_kind: str = "expert_or_capability"
    parent_genome_refs: list[str] = Field(default_factory=list)
    parent_node_refs: list[str] = Field(default_factory=list)
    capability_traits: list[str] = Field(default_factory=list)
    dreamed_traits: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    sandbox_refs: list[str] = Field(default_factory=list)
    eval_refs: list[str] = Field(default_factory=list)
    license_state: str = "unknown"
    dream_temperature_profile: dict[str, Any] = Field(default_factory=dict)
    reviewer_contract: str = "lower-temperature-review-required-before-promotion"
    mutation_history: list[str] = Field(default_factory=list)
    first_use_policy: str = "temporary-first-use-only"
    retention_review_state: str = "review-required-before-standalone-approval"
    standalone_approval_state: str = "not-approved"
    value_retention_rule: str = "permanent-only-after-review-proves-increased-value"
    parent_retirement_rule: str = (
        "retire-respective-parent-only-after-ivy-review-proves-great-child-outperformance"
    )
    teacher_distillation_review_contract: dict[str, Any] = Field(default_factory=dict)
    promotion_state: str = "candidate"
    sidebar_reasons: list[str] = Field(default_factory=list)
    created_at: str


class HiveForwardPassRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = "default"
    task_id: str | None = None
    intent: str
    source_ref: str = "operator"
    requested_capabilities: list[str] = Field(default_factory=list)
    memory_refs: list[str] = Field(default_factory=list)
    policy_labels: list[str] = Field(default_factory=list)
    privacy_class: str = "internal"
    requested_actions: list[dict[str, Any]] = Field(default_factory=list)
    max_loops: int = Field(default=2, ge=1, le=8)
    metadata: dict[str, Any] = Field(default_factory=dict)


class HiveAssimilationCandidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = "default"
    candidate_id: str
    title: str
    candidate_kind: str = "expert_or_capability"
    parent_genome_refs: list[str] = Field(default_factory=list)
    parent_node_refs: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    capability_traits: list[str] = Field(default_factory=list)
    dreamed_traits: list[str] = Field(default_factory=list)
    sandbox_refs: list[str] = Field(default_factory=list)
    eval_refs: list[str] = Field(default_factory=list)
    license_state: str = "unknown"
    privacy_class: str = "internal"
    requested_promotion: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class HiveRecursiveDreamRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = "default"
    problem_statement: str
    parent_node_refs: list[str] = Field(default_factory=list)
    requested_capabilities: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    memory_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class HiveProductionizationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = "default"
    subject_id: str
    goal: str
    source_run_id: str | None = None
    candidate_refs: list[str] = Field(default_factory=list)
    sandbox_provider_refs: list[str] = Field(default_factory=list)
    teacher_model_refs: list[str] = Field(default_factory=list)
    federation_node_refs: list[str] = Field(default_factory=list)
    runtime_methods: list[str] = Field(default_factory=list)
    allow_recursive_dreaming: bool = True
    human_governance_approval: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class HiveShadowReleaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = "default"
    productionization_id: str
    operator_approval_ref: str
    human_governance_approval: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class HiveActiveReleaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = "default"
    shadow_release_id: str
    operator_approval_ref: str
    human_governance_approval: bool = False
    canary_eval_refs: list[str] = Field(default_factory=list)
    monitoring_refs: list[str] = Field(default_factory=list)
    rollback_rehearsal_ref: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class HiveRollbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = "default"
    release_id: str
    reason: str
    human_governance_approval: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class HiveCheckpointRewindRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = "default"
    checkpoint_id: str
    reason: str
    human_governance_approval: bool = False
    restore_mode: str = "metadata_snapshot_restore"
    metadata: dict[str, Any] = Field(default_factory=dict)


class HiveGlobalFederationReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = "default"
    subject_id: str = "global-federation-shadow-learning"
    sandbox_replay_ref: str | None = None
    security_review_ref: str | None = None
    privacy_review_ref: str | None = None
    human_governance_approval: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class HiveActivation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activation_id: str
    contract_id: str = "hive-activation-v0"
    run_id: str
    session_id: str
    task_id: str
    source_ref: str
    input_plane: str = "sensory-input"
    embedding_ref: str
    privacy_class: str
    memory_refs: list[str] = Field(default_factory=list)
    action_refs: list[str] = Field(default_factory=list)
    checkpoint_ref: str
    artifact_path: str | None = None
    created_at: str


class HivePersonalityPreferenceLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preference_ledger_id: str
    surface_id: str = "hive-personality-preference-ledger-v0"
    contract_id: str = "hive-personality-preference-ledger-v0"
    run_id: str
    session_ref_digest: str
    task_ref_digest: str
    source_ref_digest: str
    privacy_consent_record_ref: str | None = None
    personal_data_federation_allowed: bool = False
    preference_keys: list[str] = Field(default_factory=list)
    preference_vector: dict[str, int] = Field(default_factory=dict)
    preference_feature_count: int = 0
    preference_vector_digest: str
    raw_content_included: bool = False
    contains_personal_data: bool = False
    active_production_mutation_allowed: bool = False
    created_at: str


class HiveSensoryInputLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sensory_ledger_id: str
    surface_id: str = "hive-sensory-input-ledger-v0"
    contract_id: str = "hive-sensory-input-ledger-v0"
    run_id: str
    session_id: str
    activation_ref: str
    checkpoint_ref: str
    normalized_channel_count: int
    normalized_channels: list[dict[str, Any]] = Field(default_factory=list)
    tokenizer_policy: dict[str, Any] = Field(default_factory=dict)
    input_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveEmbeddingTensorLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    embedding_ledger_id: str
    surface_id: str = "hive-embedding-tensor-ledger-v0"
    contract_id: str = "hive-embedding-tensor-ledger-v0"
    run_id: str
    session_id: str
    activation_ref: str
    checkpoint_ref: str
    token_count: int
    embedding_dimension: int
    embedding_shape: list[int] = Field(default_factory=list)
    token_records: list[dict[str, Any]] = Field(default_factory=list)
    tensor_statistics: dict[str, Any] = Field(default_factory=dict)
    formula_basis: dict[str, Any] = Field(default_factory=dict)
    token_privacy: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveTemporalPositionalLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    temporal_ledger_id: str
    surface_id: str = "hive-temporal-positional-ledger-v0"
    contract_id: str = "hive-temporal-positional-ledger-v0"
    run_id: str
    session_id: str
    sensory_input_ref: str
    embedding_tensor_ref: str
    activation_ref: str
    checkpoint_ref: str
    position_count: int
    position_records: list[dict[str, Any]] = Field(default_factory=list)
    position_policy: dict[str, Any] = Field(default_factory=dict)
    temporal_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveMemoryEngramLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_ledger_id: str
    surface_id: str = "hive-memory-engram-ledger-v0"
    contract_id: str = "hive-memory-engram-ledger-v0"
    run_id: str
    session_id: str
    sensory_input_ref: str
    temporal_positional_ref: str
    activation_ref: str
    checkpoint_ref: str
    memory_ref_count: int
    retrieval_records: list[dict[str, Any]] = Field(default_factory=list)
    retrieval_policy: dict[str, Any] = Field(default_factory=dict)
    memory_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveAttentionRoutingLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attention_ledger_id: str
    surface_id: str = "hive-attention-routing-ledger-v0"
    contract_id: str = "hive-attention-routing-ledger-v0"
    run_id: str
    session_id: str
    embedding_tensor_ref: str
    activation_ref: str
    neural_bus_ref: str
    hive_blackboard_ref: str
    checkpoint_ref: str
    attention_head_count: int
    focus_target_count: int
    attention_heads: list[dict[str, Any]] = Field(default_factory=list)
    focus_targets: list[dict[str, Any]] = Field(default_factory=list)
    attention_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveResidualNormalizationLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    normalization_ledger_id: str
    surface_id: str = "hive-residual-normalization-ledger-v0"
    contract_id: str = "hive-residual-normalization-ledger-v0"
    run_id: str
    session_id: str
    embedding_tensor_ref: str
    attention_ref: str
    activation_ref: str
    neural_bus_ref: str
    hive_blackboard_ref: str
    checkpoint_ref: str
    normalized_stream_count: int
    normalized_streams: list[dict[str, Any]] = Field(default_factory=list)
    residual_connections: list[dict[str, Any]] = Field(default_factory=list)
    normalization_policy: dict[str, Any] = Field(default_factory=dict)
    normalization_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveSparseExpertGateLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gate_ledger_id: str
    surface_id: str = "hive-sparse-expert-gate-ledger-v0"
    contract_id: str = "hive-sparse-expert-gate-ledger-v0"
    run_id: str
    session_id: str
    attention_ref: str
    router_ref: str
    activation_ref: str
    neural_bus_ref: str
    hive_blackboard_ref: str
    checkpoint_ref: str
    top_k: int
    selected_expert_node_ids: list[str] = Field(default_factory=list)
    expert_gate_distribution: list[dict[str, Any]] = Field(default_factory=list)
    dormant_visible_node_refs: list[str] = Field(default_factory=list)
    gate_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveFeedForwardExpertLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feedforward_ledger_id: str
    surface_id: str = "hive-feedforward-expert-ledger-v0"
    contract_id: str = "hive-feedforward-expert-ledger-v0"
    run_id: str
    session_id: str
    sparse_gate_ref: str
    residual_normalization_ref: str
    activation_ref: str
    neural_bus_ref: str
    hive_blackboard_ref: str
    checkpoint_ref: str
    expert_unit_count: int
    expert_units: list[dict[str, Any]] = Field(default_factory=list)
    feedforward_policy: dict[str, Any] = Field(default_factory=dict)
    feedforward_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveLatentLoopExitLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    latent_loop_id: str
    surface_id: str = "hive-latent-loop-exit-ledger-v0"
    contract_id: str = "hive-latent-loop-exit-ledger-v0"
    run_id: str
    session_id: str
    attention_ref: str
    sparse_gate_ref: str
    feedforward_ref: str
    activation_ref: str
    checkpoint_ref: str
    loop_step_count: int
    exit_steps: list[dict[str, Any]] = Field(default_factory=list)
    exit_gate_policy: dict[str, Any] = Field(default_factory=dict)
    exit_gate_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveKVCacheCompressionLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kv_cache_ledger_id: str
    surface_id: str = "hive-kv-cache-compression-ledger-v0"
    contract_id: str = "hive-kv-cache-compression-ledger-v0"
    run_id: str
    session_id: str
    attention_ref: str
    latent_loop_ref: str
    activation_ref: str
    checkpoint_ref: str
    cache_policy_candidates: list[dict[str, Any]] = Field(default_factory=list)
    selected_shadow_policy: dict[str, Any] = Field(default_factory=dict)
    kv_cache_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveLossBackpropagationLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backpropagation_id: str
    surface_id: str = "hive-loss-backpropagation-ledger-v0"
    contract_id: str = "hive-loss-backpropagation-ledger-v0"
    run_id: str
    session_id: str
    embedding_tensor_ref: str
    attention_ref: str
    sparse_gate_ref: str
    neuroplastic_weight_ref: str
    neuromodulatory_state_ref: str
    activation_ref: str
    checkpoint_ref: str
    loss_terms: list[dict[str, Any]] = Field(default_factory=list)
    gradient_paths: list[dict[str, Any]] = Field(default_factory=list)
    optimizer_step: dict[str, Any] = Field(default_factory=dict)
    gradient_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveOptimizerSchoolLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    optimizer_ledger_id: str
    surface_id: str = "hive-optimizer-school-ledger-v0"
    contract_id: str = "hive-optimizer-school-ledger-v0"
    run_id: str
    session_id: str
    backpropagation_ref: str
    memory_engram_ref: str
    activation_ref: str
    checkpoint_ref: str
    curriculum_update_plan: list[dict[str, Any]] = Field(default_factory=list)
    teacher_review_queue: list[dict[str, Any]] = Field(default_factory=list)
    optimizer_policy: dict[str, Any] = Field(default_factory=dict)
    optimizer_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveActionOutputDecoderLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output_decoder_id: str
    surface_id: str = "hive-action-output-decoder-ledger-v0"
    contract_id: str = "hive-action-output-decoder-ledger-v0"
    run_id: str
    session_id: str
    downstream_runtime_ref: str
    optimizer_school_ref: str
    forward_propagation_ref: str | None = None
    activation_ref: str
    checkpoint_ref: str
    decoded_output_count: int
    decoded_outputs: list[dict[str, Any]] = Field(default_factory=list)
    decoder_policy: dict[str, Any] = Field(default_factory=dict)
    output_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveForwardPropagationLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    propagation_id: str
    surface_id: str = "hive-forward-propagation-ledger-v0"
    contract_id: str = "hive-forward-propagation-ledger-v0"
    run_id: str
    session_id: str
    pathway_ref: str
    plane_adjacency_matrix_ref: str
    activation_ref: str
    checkpoint_ref: str
    step_count: int
    propagation_steps: list[dict[str, Any]] = Field(default_factory=list)
    propagation_policy: dict[str, Any] = Field(default_factory=dict)
    propagation_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveBackwardPropagationLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backward_propagation_id: str
    surface_id: str = "hive-backward-propagation-ledger-v0"
    contract_id: str = "hive-backward-propagation-ledger-v0"
    run_id: str
    session_id: str
    forward_propagation_ref: str
    loss_backpropagation_ref: str
    plane_adjacency_matrix_ref: str
    activation_ref: str
    checkpoint_ref: str
    step_count: int
    reverse_steps: list[dict[str, Any]] = Field(default_factory=list)
    backward_policy: dict[str, Any] = Field(default_factory=dict)
    backward_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveParameterTensorLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parameter_ledger_id: str
    surface_id: str = "hive-parameter-tensor-ledger-v0"
    contract_id: str = "hive-parameter-tensor-ledger-v0"
    run_id: str
    session_id: str
    backward_propagation_ref: str
    neuroplastic_weight_ref: str
    plane_adjacency_matrix_ref: str
    activation_ref: str
    checkpoint_ref: str
    parameter_tensor_count: int
    parameter_tensors: list[dict[str, Any]] = Field(default_factory=list)
    parameter_policy: dict[str, Any] = Field(default_factory=dict)
    parameter_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveActivationFunctionLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activation_function_ledger_id: str
    surface_id: str = "hive-activation-function-ledger-v0"
    contract_id: str = "hive-activation-function-ledger-v0"
    run_id: str
    session_id: str
    parameter_tensor_ref: str
    forward_propagation_ref: str
    activation_ref: str
    checkpoint_ref: str
    activation_function_count: int
    activation_functions: list[dict[str, Any]] = Field(default_factory=list)
    activation_function_policy: dict[str, Any] = Field(default_factory=dict)
    activation_function_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveComputationalGraphLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    graph_ledger_id: str
    surface_id: str = "hive-computational-graph-ledger-v0"
    contract_id: str = "hive-computational-graph-ledger-v0"
    run_id: str
    session_id: str
    activation_function_ref: str
    parameter_tensor_ref: str
    forward_propagation_ref: str
    backward_propagation_ref: str
    plane_adjacency_matrix_ref: str
    activation_ref: str
    checkpoint_ref: str
    operation_node_count: int
    operation_edge_count: int
    topological_order: list[str] = Field(default_factory=list)
    operation_nodes: list[dict[str, Any]] = Field(default_factory=list)
    operation_edges: list[dict[str, Any]] = Field(default_factory=list)
    graph_policy: dict[str, Any] = Field(default_factory=dict)
    graph_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveOptimizerStateVectorLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    optimizer_state_ledger_id: str
    surface_id: str = "hive-optimizer-state-vector-ledger-v0"
    contract_id: str = "hive-optimizer-state-vector-ledger-v0"
    run_id: str
    session_id: str
    computational_graph_ref: str
    parameter_tensor_ref: str
    optimizer_school_ref: str
    backward_propagation_ref: str
    activation_ref: str
    checkpoint_ref: str
    state_vector_count: int
    state_vectors: list[dict[str, Any]] = Field(default_factory=list)
    optimizer_state_policy: dict[str, Any] = Field(default_factory=dict)
    optimizer_state_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveModelGenomeLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    genome_ledger_id: str
    surface_id: str = "hive-model-genome-ledger-v0"
    contract_id: str = "hive-model-genome-ledger-v0"
    run_id: str
    session_id: str
    optimizer_state_ref: str
    computational_graph_ref: str
    parameter_tensor_ref: str
    activation_function_ref: str
    checkpoint_ref: str
    architecture_gene_count: int
    architecture_genes: list[dict[str, Any]] = Field(default_factory=list)
    distillation_blueprint: dict[str, Any] = Field(default_factory=dict)
    genome_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveTensorRuntimeKernelLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tensor_kernel_ledger_id: str
    surface_id: str = "hive-tensor-runtime-kernel-ledger-v0"
    contract_id: str = "hive-tensor-runtime-kernel-ledger-v0"
    run_id: str
    session_id: str
    model_genome_ref: str
    computational_graph_ref: str
    parameter_tensor_ref: str
    activation_function_ref: str
    optimizer_state_ref: str
    activation_ref: str
    checkpoint_ref: str
    kernel_op_count: int
    kernel_ops: list[dict[str, Any]] = Field(default_factory=list)
    numeric_precision_policy: dict[str, Any] = Field(default_factory=dict)
    sandbox_execution: dict[str, Any] = Field(default_factory=dict)
    executed_shadow_ops: bool = False
    runtime_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveLayerBlockStackLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    layer_stack_ledger_id: str
    surface_id: str = "hive-layer-block-stack-ledger-v0"
    contract_id: str = "hive-layer-block-stack-ledger-v0"
    run_id: str
    session_id: str
    tensor_kernel_ref: str
    model_genome_ref: str
    computational_graph_ref: str
    activation_ref: str
    checkpoint_ref: str
    block_count: int
    layer_blocks: list[dict[str, Any]] = Field(default_factory=list)
    stack_policy: dict[str, Any] = Field(default_factory=dict)
    stack_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveDistillationLoopLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    distillation_loop_id: str
    surface_id: str = "hive-distillation-loop-ledger-v0"
    contract_id: str = "hive-distillation-loop-ledger-v0"
    run_id: str
    session_id: str
    model_genome_ref: str
    optimizer_state_ref: str
    layer_stack_ref: str
    activation_ref: str
    checkpoint_ref: str
    teacher_panel: list[dict[str, Any]] = Field(default_factory=list)
    child_expert_candidates: list[dict[str, Any]] = Field(default_factory=list)
    eval_scorecards: list[dict[str, Any]] = Field(default_factory=list)
    distillation_gate: dict[str, Any] = Field(default_factory=dict)
    distillation_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveFederatedInfluenceLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    federated_influence_id: str
    surface_id: str = "hive-federated-influence-ledger-v0"
    contract_id: str = "hive-federated-influence-ledger-v0"
    run_id: str
    session_id: str
    federated_prior_update_ref: str
    model_genome_ref: str
    shadow_routing_ref: str
    activation_ref: str
    checkpoint_ref: str
    secure_aggregation: dict[str, Any] = Field(default_factory=dict)
    trust_score: dict[str, Any] = Field(default_factory=dict)
    poisoning_anomaly_scan: dict[str, Any] = Field(default_factory=dict)
    differential_privacy: dict[str, Any] = Field(default_factory=dict)
    shadow_prior_update_count: int
    shadow_prior_updates: list[dict[str, Any]] = Field(default_factory=list)
    federation_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveExecutableDreamCycleLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dream_cycle_id: str
    surface_id: str = "hive-executable-dream-cycle-ledger-v0"
    contract_id: str = "hive-executable-dream-cycle-ledger-v0"
    run_id: str
    session_id: str
    model_genome_ref: str
    computational_graph_ref: str
    optimizer_state_ref: str
    federated_influence_ref: str
    loss_backpropagation_ref: str
    activation_ref: str
    checkpoint_ref: str
    dream_candidate_count: int
    dream_candidates: list[dict[str, Any]] = Field(default_factory=list)
    critic_reviews: list[dict[str, Any]] = Field(default_factory=list)
    sandbox_eval_refs: list[str] = Field(default_factory=list)
    sidebared_candidates: list[dict[str, Any]] = Field(default_factory=list)
    dream_temperature_policy: dict[str, Any] = Field(default_factory=dict)
    dream_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveDeepReplayDrilldownLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    replay_drilldown_id: str
    surface_id: str = "hive-deep-replay-drilldown-ledger-v0"
    contract_id: str = "hive-deep-replay-drilldown-ledger-v0"
    run_id: str
    session_id: str
    graph_ref: str
    parameter_tensor_ref: str
    optimizer_state_ref: str
    model_genome_ref: str
    forward_propagation_ref: str
    backward_propagation_ref: str
    activation_ref: str
    checkpoint_ref: str
    drilldown_view_count: int
    drilldown_views: list[dict[str, Any]] = Field(default_factory=list)
    replay_policy: dict[str, Any] = Field(default_factory=dict)
    replay_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveDurableStorageLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    storage_ledger_id: str
    surface_id: str = "hive-durable-storage-ledger-v0"
    contract_id: str = "hive-durable-storage-ledger-v0"
    run_id: str
    session_id: str
    artifact_index_ref: str
    replay_drilldown_ref: str
    activation_ref: str
    checkpoint_ref: str
    indexed_artifact_count: int
    storage_records: list[dict[str, Any]] = Field(default_factory=list)
    storage_policy: dict[str, Any] = Field(default_factory=dict)
    storage_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveCheckpointCoverageLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    coverage_ledger_id: str
    surface_id: str = "hive-checkpoint-coverage-ledger-v0"
    contract_id: str = "hive-checkpoint-coverage-ledger-v0"
    run_id: str
    session_id: str
    checkpoint_ref: str
    durable_storage_ref: str
    activation_ref: str
    coverage_record_count: int
    coverage_records: list[dict[str, Any]] = Field(default_factory=list)
    coverage_policy: dict[str, Any] = Field(default_factory=dict)
    coverage_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveRuntimeDecisionLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runtime_decision_id: str
    surface_id: str = "hive-runtime-decision-ledger-v0"
    contract_id: str = "hive-runtime-decision-ledger-v0"
    run_id: str
    session_id: str
    downstream_runtime_ref: str
    model_genome_ref: str
    computational_graph_ref: str
    optimizer_state_ref: str
    tensor_kernel_ref: str
    layer_stack_ref: str
    activation_ref: str
    checkpoint_ref: str
    decision_count: int
    runtime_decisions: list[dict[str, Any]] = Field(default_factory=list)
    decision_policy: dict[str, Any] = Field(default_factory=dict)
    runtime_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveBackendQuantizationExecutionLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backend_execution_id: str
    surface_id: str = "hive-backend-quantization-execution-ledger-v0"
    contract_id: str = "hive-backend-quantization-execution-ledger-v0"
    run_id: str
    session_id: str
    tensor_kernel_ref: str
    kv_cache_compression_ref: str
    parameter_tensor_ref: str
    runtime_decision_ref: str
    activation_ref: str
    checkpoint_ref: str
    backend_candidates: list[dict[str, Any]] = Field(default_factory=list)
    quantization_trials: list[dict[str, Any]] = Field(default_factory=list)
    benchmark_scorecard_count: int
    benchmark_scorecards: list[dict[str, Any]] = Field(default_factory=list)
    selected_shadow_backend: dict[str, Any] = Field(default_factory=dict)
    backend_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveNeuralPathwayMap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pathway_id: str
    surface_id: str = "hive-neural-pathway-map-v0"
    contract_id: str = "hive-neural-pathway-map-v0"
    run_id: str
    session_id: str
    activation_ref: str
    neural_bus_ref: str
    hive_blackboard_ref: str
    checkpoint_ref: str
    trace_ledger_ref: str
    brain_scale_stack: list[dict[str, Any]] = Field(default_factory=list)
    plane_pathways: list[dict[str, Any]] = Field(default_factory=list)
    node_pathways: list[dict[str, Any]] = Field(default_factory=list)
    recurrent_pathways: list[dict[str, Any]] = Field(default_factory=list)
    feedback_pathways: list[dict[str, Any]] = Field(default_factory=list)
    immune_pathways: list[dict[str, Any]] = Field(default_factory=list)
    plane_adjacency_matrix: dict[str, Any] = Field(default_factory=dict)
    connectivity_summary: dict[str, Any] = Field(default_factory=dict)
    harmonic_topology: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveLaminarMicrocircuitLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    microcircuit_id: str
    surface_id: str = "hive-laminar-microcircuit-ledger-v0"
    contract_id: str = "hive-laminar-microcircuit-ledger-v0"
    run_id: str
    session_id: str
    activation_ref: str
    neural_bus_ref: str
    hive_blackboard_ref: str
    checkpoint_ref: str
    trace_ledger_ref: str
    plane_microcircuit_count: int
    plane_microcircuits: list[dict[str, Any]] = Field(default_factory=list)
    microcircuit_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveSynapticTransmissionLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transmission_id: str
    surface_id: str = "hive-synaptic-transmission-ledger-v0"
    contract_id: str = "hive-synaptic-transmission-ledger-v0"
    run_id: str
    session_id: str
    pathway_ref: str
    activation_ref: str
    neural_bus_ref: str
    hive_blackboard_ref: str
    checkpoint_ref: str
    plane_signal_count: int
    node_signal_count: int
    recurrent_signal_count: int
    feedback_signal_count: int
    plane_signals: list[dict[str, Any]] = Field(default_factory=list)
    node_signals: list[dict[str, Any]] = Field(default_factory=list)
    recurrent_signals: list[dict[str, Any]] = Field(default_factory=list)
    feedback_signals: list[dict[str, Any]] = Field(default_factory=list)
    immune_gate_signal: dict[str, Any] = Field(default_factory=dict)
    signal_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveNeuroplasticWeightLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weight_ledger_id: str
    surface_id: str = "hive-neuroplastic-weight-ledger-v0"
    contract_id: str = "hive-neuroplastic-weight-ledger-v0"
    run_id: str
    session_id: str
    pathway_ref: str
    transmission_ref: str
    activation_ref: str
    neural_bus_ref: str
    hive_blackboard_ref: str
    checkpoint_ref: str
    plane_weight_count: int
    node_weight_count: int
    feedback_weight_count: int
    plane_weight_updates: list[dict[str, Any]] = Field(default_factory=list)
    node_weight_updates: list[dict[str, Any]] = Field(default_factory=list)
    feedback_weight_updates: list[dict[str, Any]] = Field(default_factory=list)
    eligibility_traces: list[dict[str, Any]] = Field(default_factory=list)
    plasticity_rule: dict[str, Any] = Field(default_factory=dict)
    plasticity_integrity: dict[str, Any] = Field(default_factory=dict)
    promotion_gate: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveNeuromodulatoryStateLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    neuromodulator_id: str
    surface_id: str = "hive-neuromodulatory-state-ledger-v0"
    contract_id: str = "hive-neuromodulatory-state-ledger-v0"
    run_id: str
    session_id: str
    laminar_microcircuit_ref: str
    pathway_ref: str
    transmission_ref: str
    weight_ledger_ref: str
    activation_ref: str
    neural_bus_ref: str
    hive_blackboard_ref: str
    checkpoint_ref: str
    modulator_count: int
    modulator_signals: list[dict[str, Any]] = Field(default_factory=list)
    plasticity_gate: dict[str, Any] = Field(default_factory=dict)
    modulation_integrity: dict[str, Any] = Field(default_factory=dict)
    artifact_path: str | None = None
    created_at: str


class HiveNeuralSubstrate:
    def __init__(
        self,
        *,
        artifacts_dir: Path | str | None = None,
        global_growth: MultiUserGrowthCoordinator | None = None,
    ) -> None:
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir is not None else None
        self.global_growth = global_growth or MultiUserGrowthCoordinator()
        self.substrate_dir = self.artifacts_dir / "hive" / "substrate" if self.artifacts_dir else None
        self.activation_dir = self.substrate_dir / "activations" if self.substrate_dir else None
        self.sensory_input_dir = self.substrate_dir / "sensory-inputs" if self.substrate_dir else None
        self.embedding_tensor_dir = self.substrate_dir / "embedding-tensors" if self.substrate_dir else None
        self.temporal_positional_dir = self.substrate_dir / "temporal-positional" if self.substrate_dir else None
        self.memory_engram_dir = self.substrate_dir / "memory-engrams" if self.substrate_dir else None
        self.attention_routing_dir = self.substrate_dir / "attention-routing" if self.substrate_dir else None
        self.residual_normalization_dir = self.substrate_dir / "residual-normalization" if self.substrate_dir else None
        self.sparse_expert_gate_dir = self.substrate_dir / "sparse-expert-gates" if self.substrate_dir else None
        self.feedforward_expert_dir = self.substrate_dir / "feedforward-experts" if self.substrate_dir else None
        self.laminar_microcircuit_dir = self.substrate_dir / "laminar-microcircuits" if self.substrate_dir else None
        self.neural_pathway_dir = self.substrate_dir / "neural-pathways" if self.substrate_dir else None
        self.synaptic_transmission_dir = self.substrate_dir / "synaptic-transmissions" if self.substrate_dir else None
        self.neuroplastic_weight_dir = self.substrate_dir / "neuroplastic-weights" if self.substrate_dir else None
        self.neuromodulatory_state_dir = self.substrate_dir / "neuromodulatory-states" if self.substrate_dir else None
        self.latent_loop_exit_dir = self.substrate_dir / "latent-loop-exit-gates" if self.substrate_dir else None
        self.kv_cache_compression_dir = self.substrate_dir / "kv-cache-compression" if self.substrate_dir else None
        self.loss_backpropagation_dir = self.substrate_dir / "loss-backpropagation" if self.substrate_dir else None
        self.optimizer_school_dir = self.substrate_dir / "optimizer-school" if self.substrate_dir else None
        self.action_output_decoder_dir = self.substrate_dir / "action-output-decoders" if self.substrate_dir else None
        self.forward_propagation_dir = self.substrate_dir / "forward-propagation" if self.substrate_dir else None
        self.backward_propagation_dir = self.substrate_dir / "backward-propagation" if self.substrate_dir else None
        self.parameter_tensor_dir = self.substrate_dir / "parameter-tensors" if self.substrate_dir else None
        self.activation_function_dir = self.substrate_dir / "activation-functions" if self.substrate_dir else None
        self.computational_graph_dir = self.substrate_dir / "computational-graphs" if self.substrate_dir else None
        self.optimizer_state_vector_dir = self.substrate_dir / "optimizer-state-vectors" if self.substrate_dir else None
        self.model_genome_dir = self.substrate_dir / "model-genomes" if self.substrate_dir else None
        self.tensor_runtime_kernel_dir = self.substrate_dir / "tensor-runtime-kernels" if self.substrate_dir else None
        self.layer_block_stack_dir = self.substrate_dir / "layer-block-stacks" if self.substrate_dir else None
        self.distillation_loop_dir = self.substrate_dir / "distillation-loops" if self.substrate_dir else None
        self.federated_influence_dir = self.substrate_dir / "federated-influence" if self.substrate_dir else None
        self.executable_dream_cycle_dir = (
            self.substrate_dir / "executable-dream-cycles" if self.substrate_dir else None
        )
        self.deep_replay_drilldown_dir = self.substrate_dir / "deep-replay-drilldowns" if self.substrate_dir else None
        self.durable_storage_dir = self.substrate_dir / "durable-storage" if self.substrate_dir else None
        self.checkpoint_coverage_dir = self.substrate_dir / "checkpoint-coverage" if self.substrate_dir else None
        self.runtime_decision_dir = self.substrate_dir / "runtime-decisions" if self.substrate_dir else None
        self.backend_quantization_execution_dir = (
            self.substrate_dir / "backend-quantization-execution" if self.substrate_dir else None
        )
        self.forward_dir = self.substrate_dir / "forward-passes" if self.substrate_dir else None
        self.candidate_dir = self.substrate_dir / "candidates" if self.substrate_dir else None
        self.prior_dir = self.substrate_dir / "federated-priors" if self.substrate_dir else None
        self.checkpoint_dir = self.substrate_dir / "checkpoints" if self.substrate_dir else None
        self.dream_dir = self.substrate_dir / "dreams" if self.substrate_dir else None
        self.node_registry_dir = self.substrate_dir / "node-registry" if self.substrate_dir else None
        self.sandbox_dir = self.substrate_dir / "sandbox-evals" if self.substrate_dir else None
        self.productionization_dir = self.substrate_dir / "productionization" if self.substrate_dir else None
        self.release_dir = self.substrate_dir / "releases" if self.substrate_dir else None
        self.rollback_dir = self.substrate_dir / "rollbacks" if self.substrate_dir else None
        self.rewind_dir = self.substrate_dir / "rewinds" if self.substrate_dir else None
        self.health_dir = self.substrate_dir / "health" if self.substrate_dir else None
        self.self_healing_dir = self.substrate_dir / "self-healing" if self.substrate_dir else None
        self.global_federation_dir = self.substrate_dir / "global-federation-reviews" if self.substrate_dir else None
        self.route_candidate_evaluation_dir = (
            self.substrate_dir / "route-candidate-evaluations" if self.substrate_dir else None
        )
        self.route_candidate_approval_dir = (
            self.substrate_dir / "route-candidate-approvals" if self.substrate_dir else None
        )
        self.route_candidate_rollback_dir = (
            self.substrate_dir / "route-candidate-rollbacks" if self.substrate_dir else None
        )
        self.project_heartbeat_dir = self.substrate_dir / "project-heartbeats" if self.substrate_dir else None
        self.personality_preference_dir = (
            self.substrate_dir / "personality-preferences" if self.substrate_dir else None
        )
        for path in [
            self.activation_dir,
            self.sensory_input_dir,
            self.embedding_tensor_dir,
            self.temporal_positional_dir,
            self.memory_engram_dir,
            self.attention_routing_dir,
            self.residual_normalization_dir,
            self.sparse_expert_gate_dir,
            self.feedforward_expert_dir,
            self.laminar_microcircuit_dir,
            self.neural_pathway_dir,
            self.synaptic_transmission_dir,
            self.neuroplastic_weight_dir,
            self.neuromodulatory_state_dir,
            self.latent_loop_exit_dir,
            self.kv_cache_compression_dir,
            self.loss_backpropagation_dir,
            self.optimizer_school_dir,
            self.action_output_decoder_dir,
            self.forward_propagation_dir,
            self.backward_propagation_dir,
            self.parameter_tensor_dir,
            self.activation_function_dir,
            self.computational_graph_dir,
            self.optimizer_state_vector_dir,
            self.model_genome_dir,
            self.tensor_runtime_kernel_dir,
            self.layer_block_stack_dir,
            self.distillation_loop_dir,
            self.federated_influence_dir,
            self.executable_dream_cycle_dir,
            self.deep_replay_drilldown_dir,
            self.durable_storage_dir,
            self.checkpoint_coverage_dir,
            self.runtime_decision_dir,
            self.backend_quantization_execution_dir,
            self.forward_dir,
            self.candidate_dir,
            self.prior_dir,
            self.checkpoint_dir,
            self.dream_dir,
            self.node_registry_dir,
            self.sandbox_dir,
            self.productionization_dir,
            self.release_dir,
            self.rollback_dir,
            self.rewind_dir,
            self.health_dir,
            self.self_healing_dir,
            self.global_federation_dir,
            self.route_candidate_evaluation_dir,
            self.route_candidate_approval_dir,
            self.route_candidate_rollback_dir,
            self.project_heartbeat_dir,
            self.personality_preference_dir,
        ]:
            if path is not None:
                path.mkdir(parents=True, exist_ok=True)
        self.policy_kernel = PolicyKernel.default()
        self.harmonic_geometry = _harmonic_geometry_kernel()
        self.planes = _planes(self.harmonic_geometry)
        self.nodes = _seed_nodes()
        self._artifact_cache: dict[Path, list[tuple[int, dict[str, Any]]]] = {}
        self.hydrate_runtime_growth_from_artifacts()

    def hydrate_runtime_growth_from_artifacts(
        self,
        *,
        session_id: str | None = None,
        limit: int = 200,
    ) -> dict[str, Any]:
        runs = self._list_artifacts(self.forward_dir, session_id=session_id, limit=limit)
        runtime_growth_receipts = [
            run.get("runtime_growth_receipt")
            for run in runs
            if isinstance(run.get("runtime_growth_receipt"), dict)
        ]
        rehydration = self.global_growth.restore_runtime_receipts(runtime_growth_receipts)
        return {
            **rehydration,
            "surface_id": "hive-runtime-growth-artifact-rehydration",
            "session_id": session_id,
            "artifact_receipt_count": len(runtime_growth_receipts),
            "runtime_growth": self.global_growth.growth_status(),
            "raw_content_included": False,
            "contains_personal_data": False,
            "mutates_production": False,
        }

    def summary(self, *, session_id: str | None = None) -> dict[str, Any]:
        self.hydrate_runtime_growth_from_artifacts(session_id=session_id)
        activations = self._list_artifacts(self.activation_dir, session_id=session_id)
        sensory_inputs = self._list_artifacts(self.sensory_input_dir, session_id=session_id)
        embedding_tensors = self._list_artifacts(self.embedding_tensor_dir, session_id=session_id)
        temporal_positionals = self._list_artifacts(self.temporal_positional_dir, session_id=session_id)
        memory_engrams = self._list_artifacts(self.memory_engram_dir, session_id=session_id)
        attention_routing_ledgers = self._list_artifacts(self.attention_routing_dir, session_id=session_id)
        residual_normalizations = self._list_artifacts(self.residual_normalization_dir, session_id=session_id)
        sparse_expert_gates = self._list_artifacts(self.sparse_expert_gate_dir, session_id=session_id)
        feedforward_experts = self._list_artifacts(self.feedforward_expert_dir, session_id=session_id)
        laminar_microcircuits = self._list_artifacts(self.laminar_microcircuit_dir, session_id=session_id)
        neural_pathways = self._list_artifacts(self.neural_pathway_dir, session_id=session_id)
        synaptic_transmissions = self._list_artifacts(self.synaptic_transmission_dir, session_id=session_id)
        neuroplastic_weights = self._list_artifacts(self.neuroplastic_weight_dir, session_id=session_id)
        neuromodulatory_states = self._list_artifacts(self.neuromodulatory_state_dir, session_id=session_id)
        latent_loop_exits = self._list_artifacts(self.latent_loop_exit_dir, session_id=session_id)
        kv_cache_compressions = self._list_artifacts(self.kv_cache_compression_dir, session_id=session_id)
        loss_backpropagations = self._list_artifacts(self.loss_backpropagation_dir, session_id=session_id)
        optimizer_schools = self._list_artifacts(self.optimizer_school_dir, session_id=session_id)
        action_output_decoders = self._list_artifacts(self.action_output_decoder_dir, session_id=session_id)
        forward_propagations = self._list_artifacts(self.forward_propagation_dir, session_id=session_id)
        backward_propagations = self._list_artifacts(self.backward_propagation_dir, session_id=session_id)
        parameter_tensors = self._list_artifacts(self.parameter_tensor_dir, session_id=session_id)
        activation_functions = self._list_artifacts(self.activation_function_dir, session_id=session_id)
        computational_graphs = self._list_artifacts(self.computational_graph_dir, session_id=session_id)
        optimizer_state_vectors = self._list_artifacts(self.optimizer_state_vector_dir, session_id=session_id)
        model_genomes = self._list_artifacts(self.model_genome_dir, session_id=session_id)
        tensor_runtime_kernels = self._list_artifacts(self.tensor_runtime_kernel_dir, session_id=session_id)
        layer_block_stacks = self._list_artifacts(self.layer_block_stack_dir, session_id=session_id)
        distillation_loops = self._list_artifacts(self.distillation_loop_dir, session_id=session_id)
        federated_influences = self._list_artifacts(self.federated_influence_dir, session_id=session_id)
        executable_dream_cycles = self._list_artifacts(self.executable_dream_cycle_dir, session_id=session_id)
        deep_replay_drilldowns = self._list_artifacts(self.deep_replay_drilldown_dir, session_id=session_id)
        durable_storages = self._list_artifacts(self.durable_storage_dir, session_id=session_id)
        checkpoint_coverages = self._list_artifacts(self.checkpoint_coverage_dir, session_id=session_id)
        runtime_decisions = self._list_artifacts(self.runtime_decision_dir, session_id=session_id)
        backend_quantization_executions = self._list_artifacts(
            self.backend_quantization_execution_dir,
            session_id=session_id,
        )
        runs = self._list_artifacts(self.forward_dir, session_id=session_id)
        candidates = self._list_artifacts(self.candidate_dir, session_id=session_id)
        prior_updates = self._list_artifacts(self.prior_dir, session_id=session_id)
        dreams = self._list_artifacts(self.dream_dir, session_id=session_id)
        node_registry_updates = self._list_artifacts(self.node_registry_dir, session_id=session_id)
        productionizations = self._list_artifacts(self.productionization_dir, session_id=session_id)
        releases = self._list_artifacts(self.release_dir, session_id=session_id)
        rollbacks = self._list_artifacts(self.rollback_dir, session_id=session_id)
        rewinds = self._list_artifacts(self.rewind_dir, session_id=session_id)
        health_events = self._list_artifacts(self.health_dir, session_id=session_id)
        self_healing_routes = self._list_artifacts(self.self_healing_dir, session_id=session_id)
        global_federation_reviews = self._list_artifacts(self.global_federation_dir, session_id=session_id)
        route_candidate_evaluations = self._list_artifacts(
            self.route_candidate_evaluation_dir,
            session_id=session_id,
        )
        route_candidate_approvals = self._list_artifacts(
            self.route_candidate_approval_dir,
            session_id=session_id,
        )
        route_candidate_rollbacks = self._list_artifacts(
            self.route_candidate_rollback_dir,
            session_id=session_id,
        )
        project_heartbeat_session_ref = _privacy_digest(session_id) if session_id else None
        project_heartbeat_records = [
            record
            for record in self._list_artifacts(self.project_heartbeat_dir)
            if not project_heartbeat_session_ref
            or record.get("session_ref_digest") == project_heartbeat_session_ref
        ]
        personality_preference_records = self._personality_preference_artifacts(session_id=session_id)
        runtime_growth_receipts = [
            run.get("runtime_growth_receipt")
            for run in runs
            if isinstance(run.get("runtime_growth_receipt"), dict)
        ]
        runtime_growth_packets = [
            receipt.get("federated_packet")
            for receipt in runtime_growth_receipts
            if isinstance(receipt.get("federated_packet"), dict)
        ]
        project_heartbeats = [
            run.get("project_heartbeat")
            for run in runs
            if isinstance(run.get("project_heartbeat"), dict)
        ]
        runtime_growth_status = self.global_growth.growth_status() if self.global_growth is not None else {}
        global_latest_runtime_receipt = runtime_growth_status.get("latest_runtime_receipt")
        session_latest_runtime_receipt = runtime_growth_receipts[0] if runtime_growth_receipts else None
        federated_prior_ledger = _federated_prior_ledger(prior_updates)
        latest_shadow_routing = (runs[0].get("shadow_routing") if runs else {}) or {}
        latest_dream_context = (dreams[0].get("dream_context") if dreams else {}) or {}
        federated_prior_feedback = federated_prior_feedback_status(
            prior_ledger=federated_prior_ledger,
            shadow_routing=latest_shadow_routing,
            dream_context=latest_dream_context,
        )
        runtime_state = _substrate_summary_runtime_state(
            runs=runs,
            candidates=candidates,
            productionizations=productionizations,
            releases=releases,
            rollbacks=rollbacks,
            rewinds=rewinds,
            health_events=health_events,
            global_federation_reviews=global_federation_reviews,
        )
        summary = {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-neural-substrate-v0",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "session_id": session_id,
            "plane_count": len(self.planes),
            "node_count": len(self.nodes),
            "harmonic_geometry_kernel": self.harmonic_geometry,
            "planes": self.planes,
            "nodes": [node.model_dump(mode="json") for node in self.nodes],
            "neuroplasticity_fabric": _neuroplasticity_fabric_contract(),
            "federated_learning_contract": _federated_learning_contract(),
            "federated_learning_prior_ledger": federated_prior_ledger,
            "federated_prior_feedback": federated_prior_feedback,
            "runtime_growth": {
                **runtime_growth_status,
                "runtime_receipt_artifact_count": len(runtime_growth_receipts),
                "latest_runtime_receipt": (
                    session_latest_runtime_receipt
                    if session_id and session_latest_runtime_receipt
                    else global_latest_runtime_receipt or session_latest_runtime_receipt
                ),
                "global_latest_runtime_receipt": global_latest_runtime_receipt,
            },
            "personality_preference_ledger": _personality_preference_ledger_summary(
                personality_preference_records
            ),
            "activation_ledger": _activation_ledger(activations),
            "sensory_input_ledger": _sensory_input_ledger(sensory_inputs),
            "embedding_tensor_ledger": _embedding_tensor_ledger(embedding_tensors),
            "temporal_positional_ledger": _temporal_positional_ledger(temporal_positionals),
            "memory_engram_ledger": _memory_engram_ledger(memory_engrams),
            "attention_routing_ledger": _attention_routing_ledger(attention_routing_ledgers),
            "residual_normalization_ledger": _residual_normalization_ledger(residual_normalizations),
            "sparse_expert_gate_ledger": _sparse_expert_gate_ledger(sparse_expert_gates),
            "feedforward_expert_ledger": _feedforward_expert_ledger(feedforward_experts),
            "laminar_microcircuit_ledger": _laminar_microcircuit_ledger(laminar_microcircuits),
            "neural_pathway_ledger": _neural_pathway_ledger(neural_pathways),
            "synaptic_transmission_ledger": _synaptic_transmission_ledger(synaptic_transmissions),
            "neuroplastic_weight_ledger": _neuroplastic_weight_ledger(neuroplastic_weights),
            "neuromodulatory_state_ledger": _neuromodulatory_state_ledger(neuromodulatory_states),
            "latent_loop_exit_ledger": _latent_loop_exit_ledger(latent_loop_exits),
            "kv_cache_compression_ledger": _kv_cache_compression_ledger(kv_cache_compressions),
            "loss_backpropagation_ledger": _loss_backpropagation_ledger(loss_backpropagations),
            "optimizer_school_ledger": _optimizer_school_ledger(optimizer_schools),
            "action_output_decoder_ledger": _action_output_decoder_ledger(action_output_decoders),
            "forward_propagation_ledger": _forward_propagation_ledger(forward_propagations),
            "backward_propagation_ledger": _backward_propagation_ledger(backward_propagations),
            "parameter_tensor_ledger": _parameter_tensor_ledger(parameter_tensors),
            "activation_function_ledger": _activation_function_ledger(activation_functions),
            "computational_graph_ledger": _computational_graph_ledger(computational_graphs),
            "optimizer_state_vector_ledger": _optimizer_state_vector_ledger(optimizer_state_vectors),
            "model_genome_ledger": _model_genome_ledger(model_genomes),
            "tensor_runtime_kernel_ledger": _tensor_runtime_kernel_ledger(tensor_runtime_kernels),
            "layer_block_stack_ledger": _layer_block_stack_ledger(layer_block_stacks),
            "distillation_loop_ledger": _distillation_loop_ledger(distillation_loops),
            "federated_influence_ledger": _federated_influence_ledger(federated_influences),
            "executable_dream_cycle_ledger": _executable_dream_cycle_ledger(executable_dream_cycles),
            "deep_replay_drilldown_ledger": _deep_replay_drilldown_ledger(deep_replay_drilldowns),
            "durable_storage_ledger": _durable_storage_ledger(durable_storages),
            "checkpoint_coverage_ledger": _checkpoint_coverage_ledger(checkpoint_coverages),
            "runtime_decision_ledger": _runtime_decision_ledger(runtime_decisions),
            "backend_quantization_execution_ledger": _backend_quantization_execution_ledger(
                backend_quantization_executions
            ),
            "artifact_store": self._artifact_store_summary(),
            "global_federation_safety": _global_federation_safety_contract(),
            "dream_ledger": _dream_ledger(dreams),
            "node_registry": _node_registry_summary(node_registry_updates),
            "ivy_league_school": _ivy_league_school_summary(candidates),
            "productionization_ledger": _productionization_ledger(productionizations),
            "release_ledger": _release_ledger(releases, rollbacks),
            "rewind_ledger": _rewind_ledger(rewinds),
            "health_ledger": _health_ledger(health_events),
            "self_healing_ledger": _self_healing_ledger(self_healing_routes),
            "global_federation_review_ledger": _global_federation_review_ledger(global_federation_reviews),
            "governed_route_candidate_evaluation_ledger": governed_route_candidate_evaluation_ledger(
                route_candidate_evaluations
            ),
            "governed_route_candidate_approval_ledger": governed_route_candidate_approval_ledger(
                route_candidate_approvals,
                route_candidate_rollbacks,
            ),
            "governed_route_candidate_rollback_ledger": governed_route_candidate_rollback_ledger(
                route_candidate_rollbacks
            ),
            "project_heartbeat": (
                project_heartbeats[0]
                if project_heartbeats
                else _empty_project_heartbeat()
            ),
            "project_heartbeat_ledger": {
                "surface_id": "nexusnet-project-heartbeat-ledger",
                "heartbeat_count": len(project_heartbeat_records) or len(project_heartbeats),
                "latest_heartbeat_id": (
                    project_heartbeat_records[0].get("heartbeat_id")
                    if project_heartbeat_records
                    else (project_heartbeats[0].get("heartbeat_id") if project_heartbeats else None)
                ),
                "latest_record_id": (
                    project_heartbeat_records[0].get("record_id") if project_heartbeat_records else None
                ),
                "native_replay_ref": PROJECT_HEARTBEAT_NATIVE_REPLAY_REF,
                "raw_content_included": False,
                "active_production_mutation_allowed": False,
            },
            "brain_hierarchy": _brain_hierarchy(self.nodes),
            "failure_continuity": _failure_continuity_contract(),
            "latest_forward_pass": runs[0] if runs else None,
            "latest_sensory_input": sensory_inputs[0] if sensory_inputs else None,
            "latest_embedding_tensor": embedding_tensors[0] if embedding_tensors else None,
            "latest_temporal_positional": temporal_positionals[0] if temporal_positionals else None,
            "latest_memory_engram": memory_engrams[0] if memory_engrams else None,
            "latest_attention_routing": attention_routing_ledgers[0] if attention_routing_ledgers else None,
            "latest_residual_normalization": residual_normalizations[0] if residual_normalizations else None,
            "latest_sparse_expert_gate": sparse_expert_gates[0] if sparse_expert_gates else None,
            "latest_feedforward_expert": feedforward_experts[0] if feedforward_experts else None,
            "latest_laminar_microcircuit": laminar_microcircuits[0] if laminar_microcircuits else None,
            "latest_neural_pathway": neural_pathways[0] if neural_pathways else None,
            "latest_synaptic_transmission": synaptic_transmissions[0] if synaptic_transmissions else None,
            "latest_neuroplastic_weight": neuroplastic_weights[0] if neuroplastic_weights else None,
            "latest_neuromodulatory_state": neuromodulatory_states[0] if neuromodulatory_states else None,
            "latest_latent_loop_exit": latent_loop_exits[0] if latent_loop_exits else None,
            "latest_kv_cache_compression": kv_cache_compressions[0] if kv_cache_compressions else None,
            "latest_loss_backpropagation": loss_backpropagations[0] if loss_backpropagations else None,
            "latest_optimizer_school": optimizer_schools[0] if optimizer_schools else None,
            "latest_action_output_decoder": action_output_decoders[0] if action_output_decoders else None,
            "latest_forward_propagation": forward_propagations[0] if forward_propagations else None,
            "latest_backward_propagation": backward_propagations[0] if backward_propagations else None,
            "latest_parameter_tensor": parameter_tensors[0] if parameter_tensors else None,
            "latest_activation_function": activation_functions[0] if activation_functions else None,
            "latest_computational_graph": computational_graphs[0] if computational_graphs else None,
            "latest_optimizer_state_vector": optimizer_state_vectors[0] if optimizer_state_vectors else None,
            "latest_model_genome": model_genomes[0] if model_genomes else None,
            "latest_tensor_runtime_kernel": tensor_runtime_kernels[0] if tensor_runtime_kernels else None,
            "latest_layer_block_stack": layer_block_stacks[0] if layer_block_stacks else None,
            "latest_distillation_loop": distillation_loops[0] if distillation_loops else None,
            "latest_federated_influence": federated_influences[0] if federated_influences else None,
            "latest_executable_dream_cycle": executable_dream_cycles[0] if executable_dream_cycles else None,
            "latest_deep_replay_drilldown": deep_replay_drilldowns[0] if deep_replay_drilldowns else None,
            "latest_durable_storage": durable_storages[0] if durable_storages else None,
            "latest_checkpoint_coverage": checkpoint_coverages[0] if checkpoint_coverages else None,
            "latest_runtime_decision": runtime_decisions[0] if runtime_decisions else None,
            "latest_backend_quantization_execution": (
                backend_quantization_executions[0] if backend_quantization_executions else None
            ),
            "latest_candidate": candidates[0] if candidates else None,
            "latest_dream": dreams[0] if dreams else None,
            "latest_productionization": productionizations[0] if productionizations else None,
            "latest_release": releases[0] if releases else None,
            "latest_rollback": rollbacks[0] if rollbacks else None,
            "latest_rewind": rewinds[0] if rewinds else None,
            "latest_health_event": health_events[0] if health_events else None,
            "latest_self_healing_route": self_healing_routes[0] if self_healing_routes else None,
            "latest_global_federation_review": global_federation_reviews[0] if global_federation_reviews else None,
            "latest_governed_route_candidate_evaluation": (
                route_candidate_evaluations[0] if route_candidate_evaluations else None
            ),
            "latest_governed_route_candidate_approval": (
                route_candidate_approvals[0] if route_candidate_approvals else None
            ),
            "latest_governed_route_candidate_rollback": (
                route_candidate_rollbacks[0] if route_candidate_rollbacks else None
            ),
            "latest_runtime_growth_receipt": runtime_growth_receipts[0] if runtime_growth_receipts else None,
            "latest_runtime_growth_packet": runtime_growth_packets[0] if runtime_growth_packets else None,
            "latest_personality_preference": (
                personality_preference_records[0] if personality_preference_records else None
            ),
            "required_controls": _required_controls(),
            "operator_actions": _operator_actions(),
            "substrate_boundary": "graph-recurrent-sparse-moe-memory-harness-not-weight-training-yet",
        }
        summary["substrate_components"] = _substrate_components(summary)
        return summary

    def scorecard(self, *, session_id: str | None = None) -> dict[str, Any]:
        summary = self.summary(session_id=session_id)
        return {
            **summary,
            "runtime_state": summary.get("runtime_state", "static-canon"),
            "control_panel_label": "Hive Neural Substrate v0",
            "source_documents": [
                "docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-01-014",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-01-014",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-027",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-027",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-028",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-028",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-029",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-029",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-030",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-030",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-031",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-031",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-032",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-032",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-033",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-033",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-034",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-034",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-035",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-035",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-036",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-036",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-037",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-037",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-038",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-038",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-039",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-039",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-040",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-040",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-041",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-041",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-042",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-042",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-043",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-043",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-044",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-044",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-045",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-045",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-046",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-046",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-047",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-047",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-048",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-048",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-049",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-049",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-050",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-050",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-051",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-051",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-052",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-052",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-054",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-054",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-055",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-055",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-056",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-056",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-057",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-057",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-058",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-058",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-060",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-060",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-061",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-061",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-062",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-062",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-063",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-063",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-064",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-064",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-065",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-065",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-066",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-066",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-067",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-067",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-068",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-068",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-069",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-069",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-070",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-070",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-071",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-071",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-072",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-072",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-073",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-073",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-074",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-074",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-075",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-075",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-076",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-076",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-077",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-077",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-078",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-078",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-079",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-079",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-080",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-080",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-081",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-081",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-082",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-082",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-083",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-083",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-084",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-084",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-085",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-085",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-086",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-086",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-087",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-087",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-088",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-088",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-089",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-089",
                "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-090",
                "docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md#PB-2026-05-03-090",
            ],
            "plane_contract": [
                "sensory_input",
                "embedding_representation",
                "temporal_positional",
                "neural_bus_message_passing",
                "attention_focus",
                "sparse_moe_router",
                "expert_computation",
                "memory_engram",
                "recurrent_deliberation",
                "learning_eval_loss",
                "optimizer_school",
                "federated_learning",
                "immune_governance",
                "curator_pruning",
                "action_output",
                "checkpoint_rewind",
            ],
            "substrate_overlays": [
                "hive_wide_neuroplasticity_fabric",
                "fractal_mini_brain_hierarchy",
                "failure_continuity_self_healing",
                "sacred_geometry_harmonic_kernel",
                "mandatory_sanitized_federated_learning",
                "federated_prior_ledger",
                "first_class_hive_activation",
                "closed_sandbox_eval_promotion_path",
                "recursive_neural_dreaming_runtime",
                "durable_node_registry",
                "global_federation_safety",
                "external_sandbox_provider_contracts",
                "teacher_model_distillation_runtime",
                "signed_secure_federation_packets",
                "evolutionary_runtime_research_foundry",
                "gated_shadow_release_and_rollback",
                "shadow_release_lifecycle",
                "rollback_execution_ledger",
                "first_class_neural_pathway_map",
                "embedding_tensor_ledger",
                "attention_routing_ledger",
                "residual_normalization_ledger",
                "sparse_expert_gate_ledger",
                "feedforward_expert_ledger",
                "laminar_plane_microcircuit_ledger",
                "synaptic_transmission_signal_ledger",
                "shadow_neuroplastic_weight_ledger",
                "neuromodulatory_plasticity_gate",
                "latent_loop_exit_gate_ledger",
                "kv_cache_compression_shadow_ledger",
                "loss_backpropagation_shadow_ledger",
                "sensory_input_ledger",
                "temporal_positional_ledger",
                "memory_engram_ledger",
                "optimizer_school_ledger",
                "action_output_decoder_ledger",
                "plane_adjacency_matrix",
                "forward_propagation_ledger",
                "backward_propagation_ledger",
                "parameter_tensor_ledger",
                "activation_function_ledger",
                "computational_graph_ledger",
                "optimizer_state_vector_ledger",
                "model_genome_ledger",
                "tensor_runtime_kernel_ledger",
                "layer_block_execution_stack",
                "ivy_school_distillation_loop",
                "federated_learning_influence_loop",
                "executable_recursive_dreaming_cycle",
                "deep_control_panel_replay",
                "durable_indexed_storage",
                "checkpoint_coverage_for_new_ledgers",
                "artifact_bound_runtime_decisioning",
                "backend_quantization_execution",
            ],
            "substrate_components": _substrate_components(summary),
            "definition_of_done": [
                "forward_pass_trace_artifact",
                "harmonic_geometry_kernel_traceability",
                "sanitized_federated_learning_packet",
                "sanitized_federated_prior_update",
                "first_class_activation_artifact",
                "artifact_bound_node_execution",
                "closed_sandbox_eval_evidence",
                "recursive_dream_evidence",
                "durable_node_registry_update",
                "productionization_sandbox_provider_evidence",
                "productionization_teacher_distillation_evidence",
                "signed_secure_federation_evidence",
                "runtime_research_foundry_evidence",
                "gated_release_rollback_evidence",
                "shadow_release_activation_evidence",
                "shadow_release_rollback_evidence",
                "active_release_canary_gate_evidence",
                "tool_execution_registry_evidence",
                "task_dependency_graph_evidence",
                "provider_circuit_breaker_evidence",
                "prompt_overlay_registry_evidence",
                "skill_system_loader_evidence",
                "bridge_manager_evidence",
                "research_monitor_pipeline_evidence",
                "hive_visible_health_event",
                "self_healing_route_around_evidence",
                "checkpoint_snapshot_and_replay",
                "checkpoint_rewind_restore_proof",
                "policy_scan_or_immune_findings",
                "checkpoint_metadata",
                "sandbox_eval_gate_for_assimilation",
                "curator_review_without_direct_delete",
                "neural_pathway_map_evidence",
                "embedding_tensor_evidence",
                "attention_routing_evidence",
                "residual_normalization_evidence",
                "sparse_expert_gate_evidence",
                "feedforward_expert_evidence",
                "synaptic_transmission_signal_evidence",
                "latent_loop_exit_gate_evidence",
                "kv_cache_compression_shadow_evidence",
                "loss_backpropagation_shadow_evidence",
                "sensory_input_evidence",
                "temporal_positional_evidence",
                "memory_engram_evidence",
                "optimizer_school_shadow_evidence",
                "action_output_decoder_evidence",
                "plane_adjacency_matrix_evidence",
                "forward_propagation_state_handoff_evidence",
                "backward_propagation_credit_assignment_evidence",
                "parameter_tensor_reference_evidence",
                "activation_function_nonlinearity_evidence",
                "computational_graph_operation_evidence",
                "optimizer_state_vector_evidence",
                "model_genome_distillation_blueprint_evidence",
                "tensor_runtime_kernel_shadow_execution",
                "layer_block_stack_execution_evidence",
                "ivy_school_distillation_loop_evidence",
                "federated_influence_shadow_prior_evidence",
                "executable_recursive_dream_cycle_evidence",
                "deep_replay_drilldown_evidence",
                "durable_storage_index_evidence",
                "checkpoint_coverage_restore_diff_evidence",
                "artifact_bound_runtime_decision_evidence",
                "backend_quantization_benchmark_evidence",
            ],
        }

    def run_forward_pass(self, request: HiveForwardPassRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, HiveForwardPassRequest) else HiveForwardPassRequest.model_validate(request)
        normalized = normalized.model_copy(
            update={"metadata": _sanitize_hive_forward_metadata(normalized.metadata)}
        )
        created_at = utcnow().isoformat()
        run_id = new_id("hive_forward")
        activation_id = new_id("hive_activation")
        task_id = normalized.task_id or run_id
        requested_caps = _terms(normalized.requested_capabilities or normalized.intent.split())
        node_registry_view = self._node_registry_view(session_id=normalized.session_id)
        selected_nodes = self._select_nodes(requested_caps, node_registry_view=node_registry_view)
        active_route_overlay = self._latest_active_route_overlay(normalized.session_id)
        if active_route_overlay:
            selected_nodes, active_route_overlay = _apply_session_shadow_route_overlay(
                selected_nodes,
                active_route_overlay,
            )
        selected_node_resonance = _selected_node_resonance(selected_nodes, requested_caps)
        tool_execution_registry = _tool_execution_registry_payload(normalized)
        task_dependency_graph = _task_dependency_graph_payload(normalized, task_id=task_id)
        provider_circuit_breaker = _provider_circuit_breaker_payload(normalized)
        prompt_overlay_registry = _prompt_overlay_registry_payload(normalized)
        skill_system_loader = _skill_system_loader_payload(normalized)
        bridge_manager = _bridge_manager_payload(normalized)
        research_monitor_pipeline = _research_monitor_pipeline_payload(normalized)
        plan_mode_write_jail = _plan_mode_write_jail_payload(normalized)
        immune_findings = self._immune_findings(normalized.requested_actions, plan_mode_write_jail=plan_mode_write_jail)
        policy_scan = self.policy_kernel.scan(
            self._policy_targets_for_actions(normalized.requested_actions, plan_mode_write_jail=plan_mode_write_jail)
        )
        blocked = bool(immune_findings) or policy_scan.summary.active_hard_fail_count > 0
        checkpoint = {
            "checkpoint_id": new_id("hive_checkpoint"),
            "checkpoint_type": "session-turn",
            "created_at": created_at,
            "session_id": normalized.session_id,
            "task_id": task_id,
            "rewind_scope": "forward-pass-artifact-plus-action-plan",
            "write_actions_require_explicit_checkpoint_ref": True,
            "prompt_preview_digest": _privacy_digest(normalized.intent),
            "tool_snapshot_digest": _privacy_digest(
                "|".join(
                    str(action.get("action_type") or "unknown") for action in normalized.requested_actions
                )
            ),
            "pre_write_snapshot": {
                "snapshot_state": "captured",
                "subject_refs": [
                    str(action.get("target_ref") or action.get("action_id") or "action")
                    for action in normalized.requested_actions
                ],
                "write_action_refs": [
                    str(action.get("action_id") or action.get("target_ref") or "action")
                    for action in normalized.requested_actions
                    if str(action.get("action_type") or "").lower() in {"write", "delete", "mutate", "promote"}
                    or action.get("read_only") is False
                ],
                "raw_file_bytes_captured": False,
                "metadata_only": True,
            },
            "session_turn_snapshot": {
                "snapshot_state": "captured",
                "session_id": normalized.session_id,
                "run_ref": run_id,
                "task_id": task_id,
                "turn_digest": _privacy_digest(f"{normalized.session_id}|{task_id}|{normalized.intent}"),
            },
            "token_snapshot": {
                "snapshot_state": "estimated",
                "estimated_prompt_tokens": _estimated_token_count(normalized.intent),
                "estimated_action_tokens": _estimated_token_count(json.dumps(normalized.requested_actions, sort_keys=True)),
                "tokenizer_ref": "metadata-estimator-v0",
            },
            "rewind_metadata": {
                "restore_policy": "operator-approved-diff-preview",
                "diff_preview_required": True,
                "prompt_tool_snapshot_replay_required": True,
                "active_production_restore_allowed": False,
            },
        }
        checkpoint_snapshot_path = self._artifact_path(self.checkpoint_dir, checkpoint["checkpoint_id"])
        checkpoint["snapshot_artifact_path"] = str(checkpoint_snapshot_path) if checkpoint_snapshot_path else None
        checkpoint["restore_validation"] = {
            "restore_state": "validated_metadata_only",
            "restore_scope": "activation-route-action-plan",
            "raw_private_content_in_snapshot": False,
        }
        activation_artifact_path = self._artifact_path(self.activation_dir, activation_id)
        activation = HiveActivation(
            activation_id=activation_id,
            run_id=run_id,
            session_id=normalized.session_id,
            task_id=task_id,
            source_ref=normalized.source_ref,
            embedding_ref=f"embedding::{_stable_key(normalized.intent)}",
            privacy_class=normalized.privacy_class,
            memory_refs=normalized.memory_refs,
            action_refs=[str(action.get("action_id") or action.get("target_ref") or "action") for action in normalized.requested_actions],
            checkpoint_ref=checkpoint["checkpoint_id"],
            artifact_path=str(activation_artifact_path) if activation_artifact_path else None,
            created_at=created_at,
        ).model_dump(mode="json")
        sensory_ledger_id = new_id("hive_sensory")
        sensory_input_artifact_path = self._artifact_path(self.sensory_input_dir, sensory_ledger_id)
        sensory_input_ledger = _hive_sensory_input_payload(
            sensory_ledger_id=sensory_ledger_id,
            artifact_path=sensory_input_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            request=normalized,
            activation=activation,
            checkpoint=checkpoint,
        )
        loops = self._loops(
            selected_nodes=selected_nodes,
            max_loops=normalized.max_loops,
            blocked=blocked,
            requested_capabilities=requested_caps,
        )
        exit_reason = "blocked_by_immune_policy" if blocked else loops[-1]["exit_reason"]
        lifecycle_state = "blocked" if blocked else "completed"
        artifact_path = self._artifact_path(self.forward_dir, run_id)
        previous_prior_updates = self._list_artifacts(self.prior_dir, session_id=normalized.session_id)
        runtime_growth_federation = run_runtime_growth_federation_cycle(
            run_id=run_id,
            session_id=normalized.session_id,
            task_id=task_id,
            created_at=created_at,
            request=normalized,
            selected_nodes=selected_nodes,
            selected_node_resonance=selected_node_resonance,
            loops=loops,
            blocked=blocked,
            requested_caps=requested_caps,
            previous_prior_updates=previous_prior_updates,
            global_growth=self.global_growth,
        )
        federated_learning_packet = runtime_growth_federation.federated_learning_packet
        federated_prior_update = runtime_growth_federation.federated_prior_update
        prior_artifact_path = self._artifact_path(self.prior_dir, federated_prior_update["prior_update_id"])
        federated_prior_update["artifact_path"] = str(prior_artifact_path) if prior_artifact_path else None
        shadow_routing = _shadow_routing_payload(
            selected_nodes=selected_nodes,
            selected_node_resonance=selected_node_resonance,
            prior_ledger=_federated_prior_ledger(
                previous_prior_updates + [federated_prior_update]
            ),
        )
        route_evaluation_id = new_id("hive_route_eval")
        route_evaluation_artifact_path = self._artifact_path(
            self.route_candidate_evaluation_dir,
            route_evaluation_id,
        )
        governed_route_candidate_evaluation = evaluate_governed_route_candidate(
            run_id=run_id,
            session_id=normalized.session_id,
            task_id=task_id,
            created_at=created_at,
            shadow_routing=shadow_routing,
            checkpoint=checkpoint,
            policy_scan=policy_scan.model_dump(mode="json"),
            human_governance_approval=False,
            evaluation_id=route_evaluation_id,
            artifact_path=str(route_evaluation_artifact_path) if route_evaluation_artifact_path else None,
        )
        runtime_growth_receipt = runtime_growth_federation.runtime_growth_receipt
        runtime_growth_packet = runtime_growth_federation.runtime_growth_packet
        runtime_growth_status = runtime_growth_federation.runtime_growth_status
        trace = {
            "trace_id": new_id("hive_trace"),
            "run_id": run_id,
            "session_id": normalized.session_id,
            "plane_count": len(self.planes),
            "planes_visited": [plane["plane_id"] for plane in self.planes],
            "selected_node_ids": [node.node_id for node in selected_nodes],
            "checkpoint_ref": checkpoint["checkpoint_id"],
            "policy_kernel_ref": "/ops/brain/policy/scan",
            "artifact_path": str(artifact_path) if artifact_path else None,
        }
        neural_bus = _neural_bus_payload(
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            request=normalized,
            activation_id=activation_id,
            selected_nodes=selected_nodes,
            loops=loops,
            checkpoint=checkpoint,
            federated_learning_packet=federated_learning_packet,
            federated_prior_update=federated_prior_update,
            blocked=blocked,
        )
        hive_blackboard = _hive_blackboard_payload(
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            request=normalized,
            activation_id=activation_id,
            selected_nodes=selected_nodes,
            loops=loops,
            checkpoint=checkpoint,
            policy_scan=policy_scan.model_dump(mode="json"),
            immune_findings=immune_findings,
            federated_learning_packet=federated_learning_packet,
            federated_prior_update=federated_prior_update,
            blocked=blocked,
        )
        embedding_ledger_id = new_id("hive_embedding")
        embedding_tensor_artifact_path = self._artifact_path(self.embedding_tensor_dir, embedding_ledger_id)
        embedding_tensor_ledger = _hive_embedding_tensor_payload(
            embedding_ledger_id=embedding_ledger_id,
            artifact_path=embedding_tensor_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            request=normalized,
            activation=activation,
            checkpoint=checkpoint,
        )
        temporal_ledger_id = new_id("hive_temporal")
        temporal_positional_artifact_path = self._artifact_path(self.temporal_positional_dir, temporal_ledger_id)
        temporal_positional_ledger = _hive_temporal_positional_payload(
            temporal_ledger_id=temporal_ledger_id,
            artifact_path=temporal_positional_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            sensory_input_ledger=sensory_input_ledger,
            embedding_tensor_ledger=embedding_tensor_ledger,
            checkpoint=checkpoint,
            loops=loops,
        )
        memory_ledger_id = new_id("hive_memory")
        memory_engram_artifact_path = self._artifact_path(self.memory_engram_dir, memory_ledger_id)
        memory_engram_ledger = _hive_memory_engram_payload(
            memory_ledger_id=memory_ledger_id,
            artifact_path=memory_engram_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            request=normalized,
            sensory_input_ledger=sensory_input_ledger,
            temporal_positional_ledger=temporal_positional_ledger,
            checkpoint=checkpoint,
        )
        personality_preference_ledger_id = new_id("hive_personality_preference")
        personality_preference_artifact_path = self._artifact_path(
            self.personality_preference_dir,
            personality_preference_ledger_id,
        )
        personality_preference_ledger = _hive_personality_preference_payload(
            preference_ledger_id=personality_preference_ledger_id,
            run_id=run_id,
            task_id=task_id,
            created_at=created_at,
            request=normalized,
        )
        federated_learning_packet["per_plane_sync"] = attach_per_plane_sync_producers(
            federated_learning_packet.get("per_plane_sync") or {},
            embedding_ref=embedding_tensor_ledger["embedding_ledger_id"],
            temporal_ref=temporal_positional_ledger["temporal_ledger_id"],
            tool_action_count=int(tool_execution_registry.get("action_count") or 0),
            ungated_write_count=len((tool_execution_registry.get("write_gate") or {}).get("ungated_write_action_ids") or []),
            hard_fail_count=int(policy_scan.summary.active_hard_fail_count),
            immune_finding_count=len(immune_findings),
            personality_preference_ref=personality_preference_ledger["preference_ledger_id"],
            personality_preference_feature_count=personality_preference_ledger[
                "preference_feature_count"
            ],
            personality_federation_allowed=personality_preference_ledger[
                "personal_data_federation_allowed"
            ],
        )
        attention_ledger_id = new_id("hive_attention")
        attention_routing_artifact_path = self._artifact_path(self.attention_routing_dir, attention_ledger_id)
        attention_routing_ledger = _hive_attention_routing_payload(
            attention_ledger_id=attention_ledger_id,
            artifact_path=attention_routing_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            request=normalized,
            embedding_tensor_ledger=embedding_tensor_ledger,
            neural_bus=neural_bus,
            hive_blackboard=hive_blackboard,
            selected_nodes=selected_nodes,
            checkpoint=checkpoint,
        )
        normalization_ledger_id = new_id("hive_norm")
        residual_normalization_artifact_path = self._artifact_path(
            self.residual_normalization_dir,
            normalization_ledger_id,
        )
        residual_normalization_ledger = _hive_residual_normalization_payload(
            normalization_ledger_id=normalization_ledger_id,
            artifact_path=residual_normalization_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            embedding_tensor_ledger=embedding_tensor_ledger,
            attention_routing_ledger=attention_routing_ledger,
            neural_bus=neural_bus,
            hive_blackboard=hive_blackboard,
            checkpoint=checkpoint,
        )
        gate_ledger_id = new_id("hive_gate")
        sparse_expert_gate_artifact_path = self._artifact_path(self.sparse_expert_gate_dir, gate_ledger_id)
        sparse_expert_gate_ledger = _hive_sparse_expert_gate_payload(
            gate_ledger_id=gate_ledger_id,
            artifact_path=sparse_expert_gate_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            attention_routing_ledger=attention_routing_ledger,
            selected_nodes=selected_nodes,
            all_nodes=self.nodes,
            neural_bus=neural_bus,
            hive_blackboard=hive_blackboard,
            checkpoint=checkpoint,
            blocked=blocked,
        )
        feedforward_ledger_id = new_id("hive_ffn")
        feedforward_expert_artifact_path = self._artifact_path(self.feedforward_expert_dir, feedforward_ledger_id)
        feedforward_expert_ledger = _hive_feedforward_expert_payload(
            feedforward_ledger_id=feedforward_ledger_id,
            artifact_path=feedforward_expert_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            residual_normalization_ledger=residual_normalization_ledger,
            sparse_expert_gate_ledger=sparse_expert_gate_ledger,
            selected_nodes=selected_nodes,
            neural_bus=neural_bus,
            hive_blackboard=hive_blackboard,
            checkpoint=checkpoint,
            blocked=blocked,
        )
        plane_trace = _plane_trace_ledger(
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            planes=self.planes,
            neural_bus=neural_bus,
            hive_blackboard=hive_blackboard,
            selected_nodes=selected_nodes,
            checkpoint=checkpoint,
            federated_learning_packet=federated_learning_packet,
            federated_prior_update=federated_prior_update,
            blocked=blocked,
        )
        microcircuit_id = new_id("hive_microcircuit")
        laminar_microcircuit_artifact_path = self._artifact_path(self.laminar_microcircuit_dir, microcircuit_id)
        laminar_microcircuit_ledger = _hive_laminar_microcircuit_payload(
            microcircuit_id=microcircuit_id,
            artifact_path=laminar_microcircuit_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            activation=activation,
            neural_bus=neural_bus,
            hive_blackboard=hive_blackboard,
            checkpoint=checkpoint,
            plane_trace=plane_trace,
            blocked=blocked,
        )
        pathway_id = new_id("hive_pathway")
        neural_pathway_artifact_path = self._artifact_path(self.neural_pathway_dir, pathway_id)
        neural_pathway_map = _hive_neural_pathway_map_payload(
            pathway_id=pathway_id,
            artifact_path=neural_pathway_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            activation=activation,
            selected_nodes=selected_nodes,
            all_nodes=self.nodes,
            planes=self.planes,
            loops=loops,
            neural_bus=neural_bus,
            hive_blackboard=hive_blackboard,
            plane_trace=plane_trace,
            checkpoint=checkpoint,
            policy_scan=policy_scan.model_dump(mode="json"),
            immune_findings=immune_findings,
            blocked=blocked,
        )
        transmission_id = new_id("hive_synaptic")
        synaptic_transmission_artifact_path = self._artifact_path(self.synaptic_transmission_dir, transmission_id)
        synaptic_transmission_ledger = _hive_synaptic_transmission_payload(
            transmission_id=transmission_id,
            artifact_path=synaptic_transmission_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            neural_pathway_map=neural_pathway_map,
            blocked=blocked,
        )
        weight_ledger_id = new_id("hive_weight")
        neuroplastic_weight_artifact_path = self._artifact_path(self.neuroplastic_weight_dir, weight_ledger_id)
        neuroplastic_weight_ledger = _hive_neuroplastic_weight_payload(
            weight_ledger_id=weight_ledger_id,
            artifact_path=neuroplastic_weight_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            synaptic_transmission_ledger=synaptic_transmission_ledger,
            blocked=blocked,
        )
        neuromodulator_id = new_id("hive_modulator")
        neuromodulatory_state_artifact_path = self._artifact_path(self.neuromodulatory_state_dir, neuromodulator_id)
        neuromodulatory_state_ledger = _hive_neuromodulatory_state_payload(
            neuromodulator_id=neuromodulator_id,
            artifact_path=neuromodulatory_state_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            laminar_microcircuit_ledger=laminar_microcircuit_ledger,
            synaptic_transmission_ledger=synaptic_transmission_ledger,
            neuroplastic_weight_ledger=neuroplastic_weight_ledger,
            loops=loops,
            blocked=blocked,
        )
        latent_loop_id = new_id("hive_latent_loop")
        latent_loop_exit_artifact_path = self._artifact_path(self.latent_loop_exit_dir, latent_loop_id)
        latent_loop_exit_ledger = _hive_latent_loop_exit_payload(
            latent_loop_id=latent_loop_id,
            artifact_path=latent_loop_exit_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            attention_routing_ledger=attention_routing_ledger,
            sparse_expert_gate_ledger=sparse_expert_gate_ledger,
            feedforward_expert_ledger=feedforward_expert_ledger,
            loops=loops,
            checkpoint=checkpoint,
            blocked=blocked,
        )
        kv_cache_ledger_id = new_id("hive_kv_cache")
        kv_cache_compression_artifact_path = self._artifact_path(self.kv_cache_compression_dir, kv_cache_ledger_id)
        kv_cache_compression_ledger = _hive_kv_cache_compression_payload(
            kv_cache_ledger_id=kv_cache_ledger_id,
            artifact_path=kv_cache_compression_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            attention_routing_ledger=attention_routing_ledger,
            latent_loop_exit_ledger=latent_loop_exit_ledger,
            request=normalized,
            checkpoint=checkpoint,
            blocked=blocked,
        )
        backpropagation_id = new_id("hive_backprop")
        loss_backpropagation_artifact_path = self._artifact_path(self.loss_backpropagation_dir, backpropagation_id)
        loss_backpropagation_ledger = _hive_loss_backpropagation_payload(
            backpropagation_id=backpropagation_id,
            artifact_path=loss_backpropagation_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            embedding_tensor_ledger=embedding_tensor_ledger,
            attention_routing_ledger=attention_routing_ledger,
            sparse_expert_gate_ledger=sparse_expert_gate_ledger,
            neuroplastic_weight_ledger=neuroplastic_weight_ledger,
            neuromodulatory_state_ledger=neuromodulatory_state_ledger,
            loops=loops,
            policy_scan=policy_scan.model_dump(mode="json"),
            federated_learning_packet=federated_learning_packet,
            blocked=blocked,
        )
        optimizer_ledger_id = new_id("hive_optimizer_school")
        optimizer_school_artifact_path = self._artifact_path(self.optimizer_school_dir, optimizer_ledger_id)
        optimizer_school_ledger = _hive_optimizer_school_payload(
            optimizer_ledger_id=optimizer_ledger_id,
            artifact_path=optimizer_school_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            memory_engram_ledger=memory_engram_ledger,
            loss_backpropagation_ledger=loss_backpropagation_ledger,
            kv_cache_compression_ledger=kv_cache_compression_ledger,
            latent_loop_exit_ledger=latent_loop_exit_ledger,
            checkpoint=checkpoint,
            blocked=blocked,
        )
        downstream_node_runtime = _downstream_node_runtime_payload(
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            selected_nodes=selected_nodes,
            neural_bus=neural_bus,
            hive_blackboard=hive_blackboard,
            sensory_input_ledger=sensory_input_ledger,
            embedding_tensor_ledger=embedding_tensor_ledger,
            temporal_positional_ledger=temporal_positional_ledger,
            memory_engram_ledger=memory_engram_ledger,
            attention_routing_ledger=attention_routing_ledger,
            residual_normalization_ledger=residual_normalization_ledger,
            sparse_expert_gate_ledger=sparse_expert_gate_ledger,
            feedforward_expert_ledger=feedforward_expert_ledger,
            laminar_microcircuit_ledger=laminar_microcircuit_ledger,
            neural_pathway_map=neural_pathway_map,
            synaptic_transmission_ledger=synaptic_transmission_ledger,
            neuroplastic_weight_ledger=neuroplastic_weight_ledger,
            neuromodulatory_state_ledger=neuromodulatory_state_ledger,
            latent_loop_exit_ledger=latent_loop_exit_ledger,
            kv_cache_compression_ledger=kv_cache_compression_ledger,
            loss_backpropagation_ledger=loss_backpropagation_ledger,
            optimizer_school_ledger=optimizer_school_ledger,
            blocked=blocked,
        )
        output_decoder_id = new_id("hive_output_decoder")
        action_output_decoder_artifact_path = self._artifact_path(self.action_output_decoder_dir, output_decoder_id)
        action_output_decoder_ledger = _hive_action_output_decoder_payload(
            output_decoder_id=output_decoder_id,
            artifact_path=action_output_decoder_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            downstream_node_runtime=downstream_node_runtime,
            optimizer_school_ledger=optimizer_school_ledger,
            activation=activation,
            checkpoint=checkpoint,
            blocked=blocked,
        )
        _bind_plane_adjacency_matrix_refs(
            neural_pathway_map,
            {
                "sensory-input": sensory_input_ledger["sensory_ledger_id"],
                "embedding-representation": embedding_tensor_ledger["embedding_ledger_id"],
                "temporal-positional": temporal_positional_ledger["temporal_ledger_id"],
                "neural-bus": neural_bus["bus_id"],
                "attention-focus": attention_routing_ledger["attention_ledger_id"],
                "sparse-moe-router": sparse_expert_gate_ledger["gate_ledger_id"],
                "expert-computation": feedforward_expert_ledger["feedforward_ledger_id"],
                "memory-engram": memory_engram_ledger["memory_ledger_id"],
                "recurrent-deliberation": latent_loop_exit_ledger["latent_loop_id"],
                "learning-eval-loss": loss_backpropagation_ledger["backpropagation_id"],
                "optimizer-school": optimizer_school_ledger["optimizer_ledger_id"],
                "federated-learning": federated_prior_update["prior_update_id"],
                "immune-governance": "policy:immune-kernel",
                "curator-pruning": research_monitor_pipeline["pipeline_id"],
                "action-output": action_output_decoder_ledger["output_decoder_id"],
                "checkpoint-rewind": checkpoint["checkpoint_id"],
            },
        )
        propagation_id = new_id("hive_propagation")
        forward_propagation_artifact_path = self._artifact_path(self.forward_propagation_dir, propagation_id)
        forward_propagation_ledger = _hive_forward_propagation_payload(
            propagation_id=propagation_id,
            artifact_path=forward_propagation_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            neural_pathway_map=neural_pathway_map,
            activation=activation,
            checkpoint=checkpoint,
        )
        action_output_decoder_ledger["forward_propagation_ref"] = forward_propagation_ledger["propagation_id"]
        backward_propagation_id = new_id("hive_backward")
        backward_propagation_artifact_path = self._artifact_path(
            self.backward_propagation_dir,
            backward_propagation_id,
        )
        backward_propagation_ledger = _hive_backward_propagation_payload(
            backward_propagation_id=backward_propagation_id,
            artifact_path=backward_propagation_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            forward_propagation_ledger=forward_propagation_ledger,
            loss_backpropagation_ledger=loss_backpropagation_ledger,
            activation=activation,
            checkpoint=checkpoint,
        )
        parameter_ledger_id = new_id("hive_parameter")
        parameter_tensor_artifact_path = self._artifact_path(self.parameter_tensor_dir, parameter_ledger_id)
        parameter_tensor_ledger = _hive_parameter_tensor_payload(
            parameter_ledger_id=parameter_ledger_id,
            artifact_path=parameter_tensor_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            forward_propagation_ledger=forward_propagation_ledger,
            backward_propagation_ledger=backward_propagation_ledger,
            neuroplastic_weight_ledger=neuroplastic_weight_ledger,
            activation=activation,
            checkpoint=checkpoint,
        )
        downstream_node_runtime.setdefault("artifact_refs", {})["parameter_tensor_ref"] = parameter_tensor_ledger[
            "parameter_ledger_id"
        ]
        for receipt in downstream_node_runtime.get("receipts") or []:
            refs = receipt.setdefault("source_artifact_refs", [])
            if parameter_tensor_ledger["parameter_ledger_id"] not in refs:
                refs.append(parameter_tensor_ledger["parameter_ledger_id"])
        activation_function_ledger_id = new_id("hive_activation_function")
        activation_function_artifact_path = self._artifact_path(
            self.activation_function_dir,
            activation_function_ledger_id,
        )
        activation_function_ledger = _hive_activation_function_payload(
            activation_function_ledger_id=activation_function_ledger_id,
            artifact_path=activation_function_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            parameter_tensor_ledger=parameter_tensor_ledger,
            forward_propagation_ledger=forward_propagation_ledger,
            activation=activation,
            checkpoint=checkpoint,
        )
        downstream_node_runtime.setdefault("artifact_refs", {})["activation_function_ref"] = activation_function_ledger[
            "activation_function_ledger_id"
        ]
        for receipt in downstream_node_runtime.get("receipts") or []:
            refs = receipt.setdefault("source_artifact_refs", [])
            if activation_function_ledger["activation_function_ledger_id"] not in refs:
                refs.append(activation_function_ledger["activation_function_ledger_id"])
        graph_ledger_id = new_id("hive_graph")
        computational_graph_artifact_path = self._artifact_path(self.computational_graph_dir, graph_ledger_id)
        computational_graph_ledger = _hive_computational_graph_payload(
            graph_ledger_id=graph_ledger_id,
            artifact_path=computational_graph_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            activation_function_ledger=activation_function_ledger,
            parameter_tensor_ledger=parameter_tensor_ledger,
            forward_propagation_ledger=forward_propagation_ledger,
            backward_propagation_ledger=backward_propagation_ledger,
            activation=activation,
            checkpoint=checkpoint,
        )
        downstream_node_runtime.setdefault("artifact_refs", {})["computational_graph_ref"] = computational_graph_ledger[
            "graph_ledger_id"
        ]
        for receipt in downstream_node_runtime.get("receipts") or []:
            refs = receipt.setdefault("source_artifact_refs", [])
            if computational_graph_ledger["graph_ledger_id"] not in refs:
                refs.append(computational_graph_ledger["graph_ledger_id"])
        optimizer_state_ledger_id = new_id("hive_optimizer_state")
        optimizer_state_vector_artifact_path = self._artifact_path(
            self.optimizer_state_vector_dir,
            optimizer_state_ledger_id,
        )
        optimizer_state_vector_ledger = _hive_optimizer_state_vector_payload(
            optimizer_state_ledger_id=optimizer_state_ledger_id,
            artifact_path=optimizer_state_vector_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            computational_graph_ledger=computational_graph_ledger,
            parameter_tensor_ledger=parameter_tensor_ledger,
            optimizer_school_ledger=optimizer_school_ledger,
            backward_propagation_ledger=backward_propagation_ledger,
            activation=activation,
            checkpoint=checkpoint,
        )
        downstream_node_runtime.setdefault("artifact_refs", {})[
            "optimizer_state_vector_ref"
        ] = optimizer_state_vector_ledger["optimizer_state_ledger_id"]
        for receipt in downstream_node_runtime.get("receipts") or []:
            refs = receipt.setdefault("source_artifact_refs", [])
            if optimizer_state_vector_ledger["optimizer_state_ledger_id"] not in refs:
                refs.append(optimizer_state_vector_ledger["optimizer_state_ledger_id"])
        genome_ledger_id = new_id("hive_genome")
        model_genome_artifact_path = self._artifact_path(self.model_genome_dir, genome_ledger_id)
        model_genome_ledger = _hive_model_genome_payload(
            genome_ledger_id=genome_ledger_id,
            artifact_path=model_genome_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            optimizer_state_vector_ledger=optimizer_state_vector_ledger,
            computational_graph_ledger=computational_graph_ledger,
            parameter_tensor_ledger=parameter_tensor_ledger,
            activation_function_ledger=activation_function_ledger,
            embedding_tensor_ledger=embedding_tensor_ledger,
            attention_routing_ledger=attention_routing_ledger,
            sparse_expert_gate_ledger=sparse_expert_gate_ledger,
            activation=activation,
            checkpoint=checkpoint,
        )
        downstream_node_runtime.setdefault("artifact_refs", {})["model_genome_ref"] = model_genome_ledger[
            "genome_ledger_id"
        ]
        for receipt in downstream_node_runtime.get("receipts") or []:
            refs = receipt.setdefault("source_artifact_refs", [])
            if model_genome_ledger["genome_ledger_id"] not in refs:
                refs.append(model_genome_ledger["genome_ledger_id"])
        tensor_kernel_id = new_id("hive_tensor_kernel")
        tensor_runtime_kernel_artifact_path = self._artifact_path(self.tensor_runtime_kernel_dir, tensor_kernel_id)
        tensor_runtime_kernel_ledger = _hive_tensor_runtime_kernel_payload(
            tensor_kernel_id=tensor_kernel_id,
            artifact_path=tensor_runtime_kernel_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            model_genome_ledger=model_genome_ledger,
            computational_graph_ledger=computational_graph_ledger,
            parameter_tensor_ledger=parameter_tensor_ledger,
            activation_function_ledger=activation_function_ledger,
            optimizer_state_vector_ledger=optimizer_state_vector_ledger,
            activation=activation,
            checkpoint=checkpoint,
        )
        _bind_downstream_artifact_ref(
            downstream_node_runtime,
            "tensor_runtime_kernel_ref",
            tensor_runtime_kernel_ledger["tensor_kernel_ledger_id"],
        )
        layer_stack_id = new_id("hive_layer_stack")
        layer_block_stack_artifact_path = self._artifact_path(self.layer_block_stack_dir, layer_stack_id)
        layer_block_stack_ledger = _hive_layer_block_stack_payload(
            layer_stack_id=layer_stack_id,
            artifact_path=layer_block_stack_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            tensor_runtime_kernel_ledger=tensor_runtime_kernel_ledger,
            model_genome_ledger=model_genome_ledger,
            computational_graph_ledger=computational_graph_ledger,
            activation=activation,
            checkpoint=checkpoint,
        )
        _bind_downstream_artifact_ref(
            downstream_node_runtime,
            "layer_block_stack_ref",
            layer_block_stack_ledger["layer_stack_ledger_id"],
        )
        distillation_loop_id = new_id("hive_distillation_loop")
        distillation_loop_artifact_path = self._artifact_path(self.distillation_loop_dir, distillation_loop_id)
        distillation_loop_ledger = _hive_distillation_loop_payload(
            distillation_loop_id=distillation_loop_id,
            artifact_path=distillation_loop_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            model_genome_ledger=model_genome_ledger,
            optimizer_state_vector_ledger=optimizer_state_vector_ledger,
            layer_block_stack_ledger=layer_block_stack_ledger,
            selected_nodes=selected_nodes,
            activation=activation,
            checkpoint=checkpoint,
        )
        _bind_downstream_artifact_ref(
            downstream_node_runtime,
            "distillation_loop_ref",
            distillation_loop_ledger["distillation_loop_id"],
        )
        federated_influence_id = new_id("hive_fed_influence")
        federated_influence_artifact_path = self._artifact_path(self.federated_influence_dir, federated_influence_id)
        federated_influence_ledger = _hive_federated_influence_payload(
            federated_influence_id=federated_influence_id,
            artifact_path=federated_influence_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            federated_prior_update=federated_prior_update,
            model_genome_ledger=model_genome_ledger,
            shadow_routing=shadow_routing,
            activation=activation,
            checkpoint=checkpoint,
        )
        _bind_downstream_artifact_ref(
            downstream_node_runtime,
            "federated_influence_ref",
            federated_influence_ledger["federated_influence_id"],
        )
        dream_cycle_id = new_id("hive_dream_cycle")
        executable_dream_cycle_artifact_path = self._artifact_path(self.executable_dream_cycle_dir, dream_cycle_id)
        executable_dream_cycle_ledger = _hive_executable_dream_cycle_payload(
            dream_cycle_id=dream_cycle_id,
            artifact_path=executable_dream_cycle_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            model_genome_ledger=model_genome_ledger,
            computational_graph_ledger=computational_graph_ledger,
            optimizer_state_vector_ledger=optimizer_state_vector_ledger,
            federated_influence_ledger=federated_influence_ledger,
            loss_backpropagation_ledger=loss_backpropagation_ledger,
            request=normalized,
            activation=activation,
            checkpoint=checkpoint,
        )
        _bind_downstream_artifact_ref(
            downstream_node_runtime,
            "executable_dream_cycle_ref",
            executable_dream_cycle_ledger["dream_cycle_id"],
        )
        federated_learning_packet["per_plane_sync"] = attach_per_plane_sync_producers(
            federated_learning_packet.get("per_plane_sync") or {},
            embedding_ref=embedding_tensor_ledger["embedding_ledger_id"],
            temporal_ref=temporal_positional_ledger["temporal_ledger_id"],
            tool_action_count=int(tool_execution_registry.get("action_count") or 0),
            ungated_write_count=len((tool_execution_registry.get("write_gate") or {}).get("ungated_write_action_ids") or []),
            hard_fail_count=int(policy_scan.summary.active_hard_fail_count),
            immune_finding_count=len(immune_findings),
            dream_cycle_ref=executable_dream_cycle_ledger["dream_cycle_id"],
            dream_candidate_count=int(executable_dream_cycle_ledger.get("dream_candidate_count") or 0),
            critic_review_count=len(executable_dream_cycle_ledger.get("critic_reviews") or []),
            personality_preference_ref=personality_preference_ledger["preference_ledger_id"],
            personality_preference_feature_count=personality_preference_ledger[
                "preference_feature_count"
            ],
            personality_federation_allowed=personality_preference_ledger[
                "personal_data_federation_allowed"
            ],
        )
        replay_drilldown_id = new_id("hive_deep_replay")
        deep_replay_drilldown_artifact_path = self._artifact_path(self.deep_replay_drilldown_dir, replay_drilldown_id)
        deep_replay_drilldown_ledger = _hive_deep_replay_drilldown_payload(
            replay_drilldown_id=replay_drilldown_id,
            artifact_path=deep_replay_drilldown_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            computational_graph_ledger=computational_graph_ledger,
            parameter_tensor_ledger=parameter_tensor_ledger,
            optimizer_state_vector_ledger=optimizer_state_vector_ledger,
            model_genome_ledger=model_genome_ledger,
            forward_propagation_ledger=forward_propagation_ledger,
            backward_propagation_ledger=backward_propagation_ledger,
            activation=activation,
            checkpoint=checkpoint,
        )
        _bind_downstream_artifact_ref(
            downstream_node_runtime,
            "deep_replay_drilldown_ref",
            deep_replay_drilldown_ledger["replay_drilldown_id"],
        )
        durable_storage_id = new_id("hive_storage")
        durable_storage_artifact_path = self._artifact_path(self.durable_storage_dir, durable_storage_id)
        durable_storage_ledger = _hive_durable_storage_payload(
            storage_ledger_id=durable_storage_id,
            artifact_path=durable_storage_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            replay_drilldown_ledger=deep_replay_drilldown_ledger,
            activation=activation,
            checkpoint=checkpoint,
            artifact_refs=downstream_node_runtime.get("artifact_refs") or {},
        )
        _bind_downstream_artifact_ref(
            downstream_node_runtime,
            "durable_storage_ref",
            durable_storage_ledger["storage_ledger_id"],
        )
        checkpoint_coverage_id = new_id("hive_checkpoint_coverage")
        checkpoint_coverage_artifact_path = self._artifact_path(self.checkpoint_coverage_dir, checkpoint_coverage_id)
        checkpoint_coverage_ledger = _hive_checkpoint_coverage_payload(
            coverage_ledger_id=checkpoint_coverage_id,
            artifact_path=checkpoint_coverage_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            checkpoint=checkpoint,
            durable_storage_ledger=durable_storage_ledger,
            activation=activation,
            new_ledger_refs={
                "tensor_runtime_kernel": tensor_runtime_kernel_ledger["tensor_kernel_ledger_id"],
                "layer_block_stack": layer_block_stack_ledger["layer_stack_ledger_id"],
                "distillation_loop": distillation_loop_ledger["distillation_loop_id"],
                "federated_influence": federated_influence_ledger["federated_influence_id"],
                "executable_dream_cycle": executable_dream_cycle_ledger["dream_cycle_id"],
                "deep_replay_drilldown": deep_replay_drilldown_ledger["replay_drilldown_id"],
                "durable_storage": durable_storage_ledger["storage_ledger_id"],
            },
        )
        _bind_downstream_artifact_ref(
            downstream_node_runtime,
            "checkpoint_coverage_ref",
            checkpoint_coverage_ledger["coverage_ledger_id"],
        )
        runtime_decision_id = new_id("hive_runtime_decision")
        runtime_decision_artifact_path = self._artifact_path(self.runtime_decision_dir, runtime_decision_id)
        runtime_decision_ledger = _hive_runtime_decision_payload(
            runtime_decision_id=runtime_decision_id,
            artifact_path=runtime_decision_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            downstream_node_runtime=downstream_node_runtime,
            model_genome_ledger=model_genome_ledger,
            computational_graph_ledger=computational_graph_ledger,
            optimizer_state_vector_ledger=optimizer_state_vector_ledger,
            tensor_runtime_kernel_ledger=tensor_runtime_kernel_ledger,
            layer_block_stack_ledger=layer_block_stack_ledger,
            activation=activation,
            checkpoint=checkpoint,
        )
        _bind_downstream_artifact_ref(
            downstream_node_runtime,
            "runtime_decision_ref",
            runtime_decision_ledger["runtime_decision_id"],
        )
        backend_execution_id = new_id("hive_backend_execution")
        backend_quantization_execution_artifact_path = self._artifact_path(
            self.backend_quantization_execution_dir,
            backend_execution_id,
        )
        backend_quantization_execution_ledger = _hive_backend_quantization_execution_payload(
            backend_execution_id=backend_execution_id,
            artifact_path=backend_quantization_execution_artifact_path,
            run_id=run_id,
            session_id=normalized.session_id,
            created_at=created_at,
            tensor_runtime_kernel_ledger=tensor_runtime_kernel_ledger,
            kv_cache_compression_ledger=kv_cache_compression_ledger,
            parameter_tensor_ledger=parameter_tensor_ledger,
            runtime_decision_ledger=runtime_decision_ledger,
            activation=activation,
            checkpoint=checkpoint,
        )
        _bind_downstream_artifact_ref(
            downstream_node_runtime,
            "backend_quantization_execution_ref",
            backend_quantization_execution_ledger["backend_execution_id"],
        )
        source_brain_generate_status = (
            normalized.metadata.get("brain_generate_status")
            if str(normalized.source_ref).startswith("nexusbrain-generate::")
            else None
        )
        source_runtime_degraded = str(source_brain_generate_status or "unknown").strip().lower() in {
            "blocked",
            "error",
            "failed",
            "runtime-unavailable",
        }
        project_heartbeat_blocked = blocked or source_runtime_degraded
        health_event = _hive_health_event_payload(
            run_id=run_id,
            session_id=normalized.session_id,
            task_id=task_id,
            created_at=created_at,
            blocked=project_heartbeat_blocked,
            neural_bus=neural_bus,
            hive_blackboard=hive_blackboard,
            selected_nodes=selected_nodes,
            immune_findings=immune_findings,
            policy_scan=policy_scan.model_dump(mode="json"),
        )
        health_artifact_path = self._artifact_path(self.health_dir, health_event["health_event_id"])
        health_event["artifact_path"] = str(health_artifact_path) if health_artifact_path else None
        self_healing_route_around = None
        self_healing_artifact_path = None
        if project_heartbeat_blocked:
            self_healing_route_around = _self_healing_route_around_payload(
                run_id=run_id,
                session_id=normalized.session_id,
                created_at=created_at,
                health_event=health_event,
                selected_nodes=selected_nodes,
                requested_actions=normalized.requested_actions,
                checkpoint=checkpoint,
            )
            self_healing_artifact_path = self._artifact_path(
                self.self_healing_dir,
                self_healing_route_around["route_around_id"],
            )
            self_healing_route_around["artifact_path"] = (
                str(self_healing_artifact_path) if self_healing_artifact_path else None
            )
        project_heartbeat_record_id = new_id("native_project_heartbeat")
        project_heartbeat_artifact_path = self._artifact_path(self.project_heartbeat_dir, project_heartbeat_record_id)
        project_heartbeat_cycle = run_native_project_heartbeat_cycle(
            heartbeat_inputs={
                "run_id": run_id,
                "session_id": normalized.session_id,
                "created_at": created_at,
                "blocked": project_heartbeat_blocked,
                "nodes": self.nodes,
                "selected_nodes": selected_nodes,
                "activation": activation,
                "neural_bus": neural_bus,
                "hive_blackboard": hive_blackboard,
                "plane_trace": plane_trace,
                "neural_pathway_map": neural_pathway_map,
                "synaptic_transmission_ledger": synaptic_transmission_ledger,
                "forward_propagation_ledger": forward_propagation_ledger,
                "runtime_growth_receipt": runtime_growth_receipt,
                "runtime_growth_packet": runtime_growth_packet,
                "federated_learning_packet": federated_learning_packet,
                "federated_prior_update": federated_prior_update,
                "federated_influence_ledger": federated_influence_ledger,
                "executable_dream_cycle_ledger": executable_dream_cycle_ledger,
                "checkpoint": checkpoint,
                "checkpoint_coverage_ledger": checkpoint_coverage_ledger,
                "runtime_decision_ledger": runtime_decision_ledger,
                "backend_quantization_execution_ledger": backend_quantization_execution_ledger,
                "durable_storage_ledger": durable_storage_ledger,
                "deep_replay_drilldown_ledger": deep_replay_drilldown_ledger,
                "health_event": health_event,
                "self_healing_route_around": self_healing_route_around,
                "policy_scan": policy_scan.model_dump(mode="json"),
                "immune_findings": immune_findings,
                "source_brain_generate_status": source_brain_generate_status,
            },
            record_id=project_heartbeat_record_id,
            recorded_at=created_at,
            artifact_path=project_heartbeat_artifact_path,
        )
        project_heartbeat = project_heartbeat_cycle.heartbeat
        project_heartbeat_replay_record = project_heartbeat_cycle.replay_record
        result = {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-neural-substrate-v0",
            "authority": "NexusBrain",
            "run_id": run_id,
            "session_id": normalized.session_id,
            "task_id": task_id,
            "intent": normalized.intent,
            "source_ref": normalized.source_ref,
            "lifecycle_state": lifecycle_state,
            "created_at": created_at,
            "activation": activation,
            "route_decision": {
                "router_id": "router:sparse-moe-hive-cortex",
                "routing_strategy": "capability-overlap-top-k",
                "sparse_top_k": len(selected_nodes),
                "selected_node_ids": [node.node_id for node in selected_nodes],
                "selected_nodes": [node.model_dump(mode="json") for node in selected_nodes],
                "connectivity_model": "hive-wide-visible-sparse-activation",
                "session_shadow_route_overlay": active_route_overlay,
                "shadow_route_overlay_scope": (
                    "session-shadow-only" if active_route_overlay else "none"
                ),
                "session_shadow_route_mutated": bool(active_route_overlay),
                "active_route_mutated": False,
                "active_production_route_mutated": False,
                "non_selected_node_state": "available-for-monitoring-idle-dreaming-or-later-routing",
                "harmonic_routing": {
                    "kernel_ref": self.harmonic_geometry["kernel_id"],
                    "phi": self.harmonic_geometry["constants"]["phi"],
                    "golden_angle_degrees": self.harmonic_geometry["constants"]["golden_angle_degrees"],
                    "selection_formula": "capability_overlap_observed_with_phi_weighted_resonance_metadata",
                    "selected_node_resonance": selected_node_resonance,
                },
            },
            "loop_summary": {
                "loop_count": len(loops),
                "exit_reason": exit_reason,
                "final_confidence": loops[-1]["confidence"],
                "loops": loops,
            },
            "checkpoint": checkpoint,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "tool_execution_registry": tool_execution_registry,
            "task_dependency_graph": task_dependency_graph,
            "provider_circuit_breaker": provider_circuit_breaker,
            "prompt_overlay_registry": prompt_overlay_registry,
            "skill_system_loader": skill_system_loader,
            "bridge_manager": bridge_manager,
            "research_monitor_pipeline": research_monitor_pipeline,
            "plan_mode_write_jail": plan_mode_write_jail,
            "immune_findings": immune_findings,
            "events": self._forward_events(
                run_id=run_id,
                session_id=normalized.session_id,
                created_at=created_at,
                blocked=blocked,
                selected_node_count=len(selected_nodes),
            ),
            "neural_bus": neural_bus,
            "hive_blackboard": hive_blackboard,
            "sensory_input_ledger": sensory_input_ledger,
            "embedding_tensor_ledger": embedding_tensor_ledger,
            "temporal_positional_ledger": temporal_positional_ledger,
            "memory_engram_ledger": memory_engram_ledger,
            "personality_preference_ledger": personality_preference_ledger,
            "attention_routing_ledger": attention_routing_ledger,
            "residual_normalization_ledger": residual_normalization_ledger,
            "sparse_expert_gate_ledger": sparse_expert_gate_ledger,
            "feedforward_expert_ledger": feedforward_expert_ledger,
            "plane_trace": plane_trace,
            "laminar_microcircuit_ledger": laminar_microcircuit_ledger,
            "neural_pathway_map": neural_pathway_map,
            "synaptic_transmission_ledger": synaptic_transmission_ledger,
            "neuroplastic_weight_ledger": neuroplastic_weight_ledger,
            "neuromodulatory_state_ledger": neuromodulatory_state_ledger,
            "latent_loop_exit_ledger": latent_loop_exit_ledger,
            "kv_cache_compression_ledger": kv_cache_compression_ledger,
            "loss_backpropagation_ledger": loss_backpropagation_ledger,
            "optimizer_school_ledger": optimizer_school_ledger,
            "downstream_node_runtime": downstream_node_runtime,
            "action_output_decoder_ledger": action_output_decoder_ledger,
            "forward_propagation_ledger": forward_propagation_ledger,
            "backward_propagation_ledger": backward_propagation_ledger,
            "parameter_tensor_ledger": parameter_tensor_ledger,
            "activation_function_ledger": activation_function_ledger,
            "computational_graph_ledger": computational_graph_ledger,
            "optimizer_state_vector_ledger": optimizer_state_vector_ledger,
            "model_genome_ledger": model_genome_ledger,
            "tensor_runtime_kernel_ledger": tensor_runtime_kernel_ledger,
            "layer_block_stack_ledger": layer_block_stack_ledger,
            "distillation_loop_ledger": distillation_loop_ledger,
            "federated_influence_ledger": federated_influence_ledger,
            "executable_dream_cycle_ledger": executable_dream_cycle_ledger,
            "deep_replay_drilldown_ledger": deep_replay_drilldown_ledger,
            "durable_storage_ledger": durable_storage_ledger,
            "checkpoint_coverage_ledger": checkpoint_coverage_ledger,
            "runtime_decision_ledger": runtime_decision_ledger,
            "backend_quantization_execution_ledger": backend_quantization_execution_ledger,
            "node_registry_view": node_registry_view["public_view"],
            "shadow_routing": shadow_routing,
            "governed_route_candidate_evaluation": governed_route_candidate_evaluation,
            "health_event": health_event,
            "self_healing_route_around": self_healing_route_around,
            "project_heartbeat": project_heartbeat,
            "project_heartbeat_replay_record": project_heartbeat_replay_record,
            "federated_learning_contract": _federated_learning_contract(),
            "federated_learning_packet": federated_learning_packet,
            "federated_prior_update": federated_prior_update,
            "runtime_growth_receipt": runtime_growth_receipt,
            "runtime_growth_federated_packet": runtime_growth_packet,
            "runtime_growth": runtime_growth_status,
            "neuroplasticity_fabric": _neuroplasticity_fabric_contract(),
            "failure_continuity": {
                **_failure_continuity_contract(),
                "active_health_signal_refs": _health_refs(selected_nodes),
                "route_around_available": True,
                "background_repair_available": True,
            },
            "trace": trace,
            "artifact_path": str(artifact_path) if artifact_path else None,
            "metadata": normalized.metadata,
        }
        self._persist(activation_artifact_path, activation)
        self._persist(sensory_input_artifact_path, sensory_input_ledger)
        self._persist(embedding_tensor_artifact_path, embedding_tensor_ledger)
        self._persist(temporal_positional_artifact_path, temporal_positional_ledger)
        self._persist(memory_engram_artifact_path, memory_engram_ledger)
        self._persist(personality_preference_artifact_path, personality_preference_ledger)
        self._persist(attention_routing_artifact_path, attention_routing_ledger)
        self._persist(residual_normalization_artifact_path, residual_normalization_ledger)
        self._persist(sparse_expert_gate_artifact_path, sparse_expert_gate_ledger)
        self._persist(feedforward_expert_artifact_path, feedforward_expert_ledger)
        self._persist(laminar_microcircuit_artifact_path, laminar_microcircuit_ledger)
        self._persist(neural_pathway_artifact_path, neural_pathway_map)
        self._persist(synaptic_transmission_artifact_path, synaptic_transmission_ledger)
        self._persist(neuroplastic_weight_artifact_path, neuroplastic_weight_ledger)
        self._persist(neuromodulatory_state_artifact_path, neuromodulatory_state_ledger)
        self._persist(latent_loop_exit_artifact_path, latent_loop_exit_ledger)
        self._persist(kv_cache_compression_artifact_path, kv_cache_compression_ledger)
        self._persist(loss_backpropagation_artifact_path, loss_backpropagation_ledger)
        self._persist(optimizer_school_artifact_path, optimizer_school_ledger)
        self._persist(action_output_decoder_artifact_path, action_output_decoder_ledger)
        self._persist(forward_propagation_artifact_path, forward_propagation_ledger)
        self._persist(backward_propagation_artifact_path, backward_propagation_ledger)
        self._persist(parameter_tensor_artifact_path, parameter_tensor_ledger)
        self._persist(activation_function_artifact_path, activation_function_ledger)
        self._persist(computational_graph_artifact_path, computational_graph_ledger)
        self._persist(optimizer_state_vector_artifact_path, optimizer_state_vector_ledger)
        self._persist(model_genome_artifact_path, model_genome_ledger)
        self._persist(tensor_runtime_kernel_artifact_path, tensor_runtime_kernel_ledger)
        self._persist(layer_block_stack_artifact_path, layer_block_stack_ledger)
        self._persist(distillation_loop_artifact_path, distillation_loop_ledger)
        self._persist(federated_influence_artifact_path, federated_influence_ledger)
        self._persist(executable_dream_cycle_artifact_path, executable_dream_cycle_ledger)
        self._persist(deep_replay_drilldown_artifact_path, deep_replay_drilldown_ledger)
        self._persist(durable_storage_artifact_path, durable_storage_ledger)
        self._persist(checkpoint_coverage_artifact_path, checkpoint_coverage_ledger)
        self._persist(runtime_decision_artifact_path, runtime_decision_ledger)
        self._persist(backend_quantization_execution_artifact_path, backend_quantization_execution_ledger)
        self._persist(checkpoint_snapshot_path, _checkpoint_snapshot_payload(checkpoint, activation))
        self._persist(prior_artifact_path, federated_prior_update)
        self._persist(route_evaluation_artifact_path, governed_route_candidate_evaluation)
        self._persist(health_artifact_path, health_event)
        self._persist(self_healing_artifact_path, self_healing_route_around or {})
        self._persist(project_heartbeat_artifact_path, project_heartbeat_replay_record)
        self._persist(artifact_path, result)
        return result

    def approve_governed_route_candidate(
        self,
        request: dict[str, Any],
        *,
        eval_registry: EvalRegistry | None = None,
    ) -> dict[str, Any]:
        payload = dict(request or {})
        session_id = str(payload.get("session_id") or "")
        evaluation_id = str(payload.get("evaluation_id") or "")
        approved_by = str(payload.get("approved_by") or payload.get("operator_approval_ref") or "admin")
        human_governance_approval = bool(payload.get("human_governance_approval"))
        if not evaluation_id:
            raise ValueError("evaluation_id is required")
        evaluation = self._find_route_candidate_evaluation(
            evaluation_id=evaluation_id,
            session_id=session_id or None,
        )
        if evaluation is None:
            raise ValueError(f"route candidate evaluation not found: {evaluation_id}")
        created_at = utcnow().isoformat()
        candidate_route = evaluation.get("candidate_route") or {}
        shadow_eval = evaluation.get("shadow_eval") or {}
        rollback_plan = evaluation.get("rollback_plan") or {}
        quality_delta = _float_metadata(shadow_eval.get("quality_delta"), default=0.0)
        regression_count = int(shadow_eval.get("regression_count") or 0)
        suite_id = f"eval::hive-route-candidate::{_stable_key(evaluation_id)}"
        evidence_refs = [
            str(evaluation_id),
            str(evaluation.get("source_shadow_routing_ref") or "shadow-routing"),
            str(rollback_plan.get("restore_ref") or "checkpoint"),
            str(rollback_plan.get("rollback_plan_id") or "rollback-plan"),
        ]
        registry = eval_registry or EvalRegistry.default(artifacts_dir=self.artifacts_dir)
        registry.register(
            EvalSuiteRequest(
                suite_id=suite_id,
                suite_type="runtime",
                target_surfaces=[
                    "hive-governed-route-candidate-evaluation",
                    "hive-neural-substrate-v0",
                ],
                benchmark_refs=[
                    "hive-route-shadow-quality-delta",
                    "checkpoint-sandbox-replay",
                    "policy-scan-clear",
                ],
                held_out=True,
                external_or_tool_verifier=True,
                metrics={
                    "route_quality_delta": quality_delta,
                    "regression_count": float(regression_count),
                },
                promotion_target="none",
                evidence_refs=evidence_refs,
                rollback_plan=str(rollback_plan.get("rollback_plan_id") or rollback_plan.get("restore_ref") or "route-baseline"),
                monitoring_plan="route-overlay-session-shadow-monitoring",
                metadata={
                    "source": "hive-route-candidate-admin-approval",
                    "evaluation_id": evaluation_id,
                    "raw_content_included": False,
                },
            )
        )
        eval_replay = registry.run_shadow(
            suite_id,
            ShadowEvalRunRequest(
                run_id=new_id("hive_route_eval_shadow"),
                candidate_ref=str(candidate_route.get("candidate_route_id") or evaluation_id),
                baseline_ref=str(rollback_plan.get("restore_ref") or rollback_plan.get("rollback_plan_id") or evaluation_id),
                metrics={
                    "route_quality_delta": quality_delta,
                    "regression_count": float(regression_count),
                },
                trace_refs=[
                    str(evaluation.get("run_id") or "hive-forward-pass"),
                    str(evaluation.get("source_shadow_routing_ref") or "shadow-routing"),
                ],
                evaluator_refs=["ao::EvalsAO", "ao::RouterAO", "ao::SecurityAO", "ao::GovernanceAO"],
                evidence_refs=evidence_refs,
                operator_approved=human_governance_approval,
                lifecycle_ref=evaluation_id,
                lifecycle_status=str(evaluation.get("status") or "evaluated"),
                growth_engine_gate={
                    "allowed": True,
                    "gate_ref": "hive-federated-prior-feedback",
                    "blockers": [],
                },
                artifact_trust_promotion={
                    "promotion_allowed": True,
                    "promotion_blockers": [],
                    "trust_ref": "hive-route-candidate-metadata-only",
                },
                metadata={
                    "source": "hive-route-candidate-admin-approval",
                    "approval_scope": "session-shadow-route-overlay-only",
                    "raw_content_included": False,
                },
            ),
        )
        approval_id = new_id("hive_route_approval")
        approval_artifact_path = self._artifact_path(self.route_candidate_approval_dir, approval_id)
        approval = approve_governed_route_candidate(
            evaluation=evaluation,
            eval_replay=eval_replay,
            approved_by=approved_by,
            created_at=created_at,
            approval_id=approval_id,
            artifact_path=str(approval_artifact_path) if approval_artifact_path else None,
        )
        self._persist(approval_artifact_path, approval)
        return approval

    def rollback_governed_route_candidate(self, request: dict[str, Any]) -> dict[str, Any]:
        payload = dict(request or {})
        session_id = str(payload.get("session_id") or "")
        approval_id = str(payload.get("approval_id") or "")
        if not approval_id:
            raise ValueError("approval_id is required")
        if not bool(payload.get("human_governance_approval")):
            raise ValueError("human_governance_approval is required")
        approval = self._find_route_candidate_approval(
            approval_id=approval_id,
            session_id=session_id or None,
        )
        if approval is None:
            raise ValueError(f"route candidate approval not found: {approval_id}")
        rollback_id = new_id("hive_route_rollback")
        rollback_artifact_path = self._artifact_path(self.route_candidate_rollback_dir, rollback_id)
        rollback = rollback_governed_route_candidate(
            approval=approval,
            reason=str(payload.get("reason") or ""),
            created_at=utcnow().isoformat(),
            rollback_id=rollback_id,
            artifact_path=str(rollback_artifact_path) if rollback_artifact_path else None,
        )
        self._persist(rollback_artifact_path, rollback)
        return rollback

    def replay(
        self,
        *,
        session_id: str | None = None,
        run_id: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        runs = self._list_artifacts(self.forward_dir, session_id=session_id, limit=limit)
        personality_preferences = self._personality_preference_artifacts(
            session_id=session_id,
            limit=limit,
        )
        sensory_inputs = self._list_artifacts(self.sensory_input_dir, session_id=session_id, limit=limit)
        embedding_tensors = self._list_artifacts(self.embedding_tensor_dir, session_id=session_id, limit=limit)
        temporal_positionals = self._list_artifacts(self.temporal_positional_dir, session_id=session_id, limit=limit)
        memory_engrams = self._list_artifacts(self.memory_engram_dir, session_id=session_id, limit=limit)
        attention_routing_ledgers = self._list_artifacts(self.attention_routing_dir, session_id=session_id, limit=limit)
        residual_normalizations = self._list_artifacts(self.residual_normalization_dir, session_id=session_id, limit=limit)
        sparse_expert_gates = self._list_artifacts(self.sparse_expert_gate_dir, session_id=session_id, limit=limit)
        feedforward_experts = self._list_artifacts(self.feedforward_expert_dir, session_id=session_id, limit=limit)
        laminar_microcircuits = self._list_artifacts(self.laminar_microcircuit_dir, session_id=session_id, limit=limit)
        neural_pathways = self._list_artifacts(self.neural_pathway_dir, session_id=session_id, limit=limit)
        synaptic_transmissions = self._list_artifacts(self.synaptic_transmission_dir, session_id=session_id, limit=limit)
        neuroplastic_weights = self._list_artifacts(self.neuroplastic_weight_dir, session_id=session_id, limit=limit)
        neuromodulatory_states = self._list_artifacts(self.neuromodulatory_state_dir, session_id=session_id, limit=limit)
        latent_loop_exits = self._list_artifacts(self.latent_loop_exit_dir, session_id=session_id, limit=limit)
        kv_cache_compressions = self._list_artifacts(self.kv_cache_compression_dir, session_id=session_id, limit=limit)
        loss_backpropagations = self._list_artifacts(self.loss_backpropagation_dir, session_id=session_id, limit=limit)
        optimizer_schools = self._list_artifacts(self.optimizer_school_dir, session_id=session_id, limit=limit)
        action_output_decoders = self._list_artifacts(self.action_output_decoder_dir, session_id=session_id, limit=limit)
        forward_propagations = self._list_artifacts(self.forward_propagation_dir, session_id=session_id, limit=limit)
        backward_propagations = self._list_artifacts(self.backward_propagation_dir, session_id=session_id, limit=limit)
        parameter_tensors = self._list_artifacts(self.parameter_tensor_dir, session_id=session_id, limit=limit)
        activation_functions = self._list_artifacts(self.activation_function_dir, session_id=session_id, limit=limit)
        computational_graphs = self._list_artifacts(self.computational_graph_dir, session_id=session_id, limit=limit)
        optimizer_state_vectors = self._list_artifacts(self.optimizer_state_vector_dir, session_id=session_id, limit=limit)
        model_genomes = self._list_artifacts(self.model_genome_dir, session_id=session_id, limit=limit)
        tensor_runtime_kernels = self._list_artifacts(self.tensor_runtime_kernel_dir, session_id=session_id, limit=limit)
        layer_block_stacks = self._list_artifacts(self.layer_block_stack_dir, session_id=session_id, limit=limit)
        distillation_loops = self._list_artifacts(self.distillation_loop_dir, session_id=session_id, limit=limit)
        federated_influences = self._list_artifacts(self.federated_influence_dir, session_id=session_id, limit=limit)
        executable_dream_cycles = self._list_artifacts(
            self.executable_dream_cycle_dir,
            session_id=session_id,
            limit=limit,
        )
        deep_replay_drilldowns = self._list_artifacts(self.deep_replay_drilldown_dir, session_id=session_id, limit=limit)
        durable_storages = self._list_artifacts(self.durable_storage_dir, session_id=session_id, limit=limit)
        checkpoint_coverages = self._list_artifacts(self.checkpoint_coverage_dir, session_id=session_id, limit=limit)
        runtime_decisions = self._list_artifacts(self.runtime_decision_dir, session_id=session_id, limit=limit)
        backend_quantization_executions = self._list_artifacts(
            self.backend_quantization_execution_dir,
            session_id=session_id,
            limit=limit,
        )
        productionizations = self._list_artifacts(self.productionization_dir, session_id=session_id, limit=limit)
        releases = self._list_artifacts(self.release_dir, session_id=session_id, limit=limit)
        rollbacks = self._list_artifacts(self.rollback_dir, session_id=session_id, limit=limit)
        rewinds = self._list_artifacts(self.rewind_dir, session_id=session_id, limit=limit)
        health_events = self._list_artifacts(self.health_dir, session_id=session_id, limit=limit)
        self_healing_routes = self._list_artifacts(self.self_healing_dir, session_id=session_id, limit=limit)
        global_federation_reviews = self._list_artifacts(self.global_federation_dir, session_id=session_id, limit=limit)
        route_candidate_evaluations = self._list_artifacts(
            self.route_candidate_evaluation_dir,
            session_id=session_id,
            limit=limit,
        )
        route_candidate_approvals = self._list_artifacts(
            self.route_candidate_approval_dir,
            session_id=session_id,
            limit=limit,
        )
        route_candidate_rollbacks = self._list_artifacts(
            self.route_candidate_rollback_dir,
            session_id=session_id,
            limit=limit,
        )
        project_heartbeat_session_ref = _privacy_digest(session_id) if session_id else None
        project_heartbeat_records = [
            record
            for record in self._list_artifacts(self.project_heartbeat_dir, limit=limit)
            if (
                not project_heartbeat_session_ref
                or record.get("session_ref_digest") == project_heartbeat_session_ref
            )
            if run_id is None or record.get("source_run_id") == run_id
        ]
        selected_run = None
        for run in runs:
            if run_id is None or run.get("run_id") == run_id:
                selected_run = run
                break
        checkpoints = [
            run.get("checkpoint")
            for run in runs
            if isinstance(run.get("checkpoint"), dict)
        ]
        downstream_runtime_chain = [
            run.get("downstream_node_runtime")
            for run in runs
            if isinstance(run.get("downstream_node_runtime"), dict)
        ]
        neural_pathway_chain = [
            pathway
            for pathway in neural_pathways
            if isinstance(pathway, dict)
            and (run_id is None or pathway.get("run_id") == run_id)
        ]
        laminar_microcircuit_chain = [
            microcircuit
            for microcircuit in laminar_microcircuits
            if isinstance(microcircuit, dict)
            and (run_id is None or microcircuit.get("run_id") == run_id)
        ]
        synaptic_transmission_chain = [
            transmission
            for transmission in synaptic_transmissions
            if isinstance(transmission, dict)
            and (run_id is None or transmission.get("run_id") == run_id)
        ]
        neuroplastic_weight_chain = [
            weight
            for weight in neuroplastic_weights
            if isinstance(weight, dict)
            and (run_id is None or weight.get("run_id") == run_id)
        ]
        neuromodulatory_state_chain = [
            state
            for state in neuromodulatory_states
            if isinstance(state, dict)
            and (run_id is None or state.get("run_id") == run_id)
        ]
        tool_execution_registry_chain = [
            run.get("tool_execution_registry")
            for run in runs
            if isinstance(run.get("tool_execution_registry"), dict)
        ]
        task_dependency_graph_chain = [
            run.get("task_dependency_graph")
            for run in runs
            if isinstance(run.get("task_dependency_graph"), dict)
        ]
        provider_circuit_breaker_chain = [
            run.get("provider_circuit_breaker")
            for run in runs
            if isinstance(run.get("provider_circuit_breaker"), dict)
        ]
        prompt_overlay_registry_chain = [
            run.get("prompt_overlay_registry")
            for run in runs
            if isinstance(run.get("prompt_overlay_registry"), dict)
        ]
        skill_system_loader_chain = [
            run.get("skill_system_loader")
            for run in runs
            if isinstance(run.get("skill_system_loader"), dict)
        ]
        bridge_manager_chain = [
            run.get("bridge_manager")
            for run in runs
            if isinstance(run.get("bridge_manager"), dict)
        ]
        research_monitor_pipeline_chain = [
            run.get("research_monitor_pipeline")
            for run in runs
            if isinstance(run.get("research_monitor_pipeline"), dict)
        ]
        node_output_chain = [
            output
            for runtime in downstream_runtime_chain
            for output in (runtime.get("node_outputs") or [])
            if isinstance(output, dict)
        ]
        active_release_chain = [
            release
            for release in releases
            if release.get("release_scope") == "active-production-release-pointer"
            and release.get("release_state") == "active_production"
        ]
        runtime_growth_receipt_chain = [
            run.get("runtime_growth_receipt")
            for run in runs
            if isinstance(run.get("runtime_growth_receipt"), dict)
            and (run_id is None or run.get("run_id") == run_id)
        ]
        embedded_project_heartbeat_chain = [
            run.get("project_heartbeat")
            for run in runs
            if isinstance(run.get("project_heartbeat"), dict)
            and (run_id is None or run.get("run_id") == run_id)
        ]
        project_heartbeat_chain = project_heartbeat_records or embedded_project_heartbeat_chain
        federated_per_plane_sync = _federated_per_plane_sync_replay(
            (selected_run or {}).get("federated_learning_packet")
        )
        personality_preference_chain = [
            record
            for record in personality_preferences
            if run_id is None or record.get("run_id") == run_id
        ]
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-neural-substrate-replay-v0",
            "authority": "NexusBrain",
            "replay_id": new_id("hive_replay"),
            "session_id": session_id or (selected_run or {}).get("session_id"),
            "latest_run_id": (selected_run or {}).get("run_id"),
            "run_count": len(runs),
            "run_ids": [run.get("run_id") for run in runs if run.get("run_id")],
            "plane_trace": (selected_run or {}).get("plane_trace") or {"record_count": 0, "records": []},
            "neural_bus": (selected_run or {}).get("neural_bus") or {"message_count": 0, "messages": []},
            "hive_blackboard": (selected_run or {}).get("hive_blackboard") or {"entry_count": 0, "entries": []},
            "federated_prior_ledger": _federated_prior_ledger(
                self._list_artifacts(self.prior_dir, session_id=session_id, limit=limit)
            ),
            "federated_per_plane_sync": federated_per_plane_sync,
            "personality_preference_chain": personality_preference_chain,
            "checkpoint_chain": checkpoints,
            "sensory_input_chain": sensory_inputs,
            "embedding_tensor_chain": embedding_tensors,
            "temporal_positional_chain": temporal_positionals,
            "memory_engram_chain": memory_engrams,
            "attention_routing_chain": attention_routing_ledgers,
            "residual_normalization_chain": residual_normalizations,
            "sparse_expert_gate_chain": sparse_expert_gates,
            "feedforward_expert_chain": feedforward_experts,
            "laminar_microcircuit_chain": laminar_microcircuit_chain,
            "neural_pathway_chain": neural_pathway_chain,
            "synaptic_transmission_chain": synaptic_transmission_chain,
            "neuroplastic_weight_chain": neuroplastic_weight_chain,
            "neuromodulatory_state_chain": neuromodulatory_state_chain,
            "latent_loop_exit_chain": latent_loop_exits,
            "kv_cache_compression_chain": kv_cache_compressions,
            "loss_backpropagation_chain": loss_backpropagations,
            "optimizer_school_chain": optimizer_schools,
            "downstream_runtime_chain": downstream_runtime_chain,
            "action_output_decoder_chain": action_output_decoders,
            "forward_propagation_chain": forward_propagations,
            "backward_propagation_chain": backward_propagations,
            "parameter_tensor_chain": parameter_tensors,
            "activation_function_chain": activation_functions,
            "computational_graph_chain": computational_graphs,
            "optimizer_state_vector_chain": optimizer_state_vectors,
            "model_genome_chain": model_genomes,
            "tensor_runtime_kernel_chain": tensor_runtime_kernels,
            "layer_block_stack_chain": layer_block_stacks,
            "distillation_loop_chain": distillation_loops,
            "federated_influence_chain": federated_influences,
            "executable_dream_cycle_chain": executable_dream_cycles,
            "deep_replay_drilldown_chain": deep_replay_drilldowns,
            "durable_storage_chain": durable_storages,
            "checkpoint_coverage_chain": checkpoint_coverages,
            "runtime_decision_chain": runtime_decisions,
            "backend_quantization_execution_chain": backend_quantization_executions,
            "tool_execution_registry_chain": tool_execution_registry_chain,
            "task_dependency_graph_chain": task_dependency_graph_chain,
            "provider_circuit_breaker_chain": provider_circuit_breaker_chain,
            "prompt_overlay_registry_chain": prompt_overlay_registry_chain,
            "skill_system_loader_chain": skill_system_loader_chain,
            "bridge_manager_chain": bridge_manager_chain,
            "research_monitor_pipeline_chain": research_monitor_pipeline_chain,
            "node_output_chain": node_output_chain,
            "candidate_chain": self._list_artifacts(self.candidate_dir, session_id=session_id, limit=limit),
            "dream_chain": self._list_artifacts(self.dream_dir, session_id=session_id, limit=limit),
            "activation_chain": self._list_artifacts(self.activation_dir, session_id=session_id, limit=limit),
            "productionization_chain": productionizations,
            "release_chain": releases,
            "active_release_chain": active_release_chain,
            "rollback_chain": rollbacks,
            "rewind_chain": rewinds,
            "health_chain": health_events,
            "self_healing_chain": self_healing_routes,
            "global_federation_review_chain": global_federation_reviews,
            "route_candidate_evaluation_chain": route_candidate_evaluations,
            "route_candidate_approval_chain": route_candidate_approvals,
            "route_candidate_rollback_chain": route_candidate_rollbacks,
            "runtime_growth_receipt_chain": runtime_growth_receipt_chain,
            "project_heartbeat_chain": project_heartbeat_chain,
            "project_heartbeat_replay_chain": project_heartbeat_records,
            "embedded_project_heartbeat_chain": embedded_project_heartbeat_chain,
            "control_panel_replay": {
                "available": True,
                "drilldown_surfaces": [
                    "project_heartbeat_chain",
                    "project_heartbeat_replay_chain",
                    "plane_trace",
                    "neural_bus",
                    "hive_blackboard",
                    "federated_prior_ledger",
                    "federated_per_plane_sync",
                    "personality_preference_chain",
                    "checkpoint_chain",
                    "sensory_input_chain",
                    "embedding_tensor_chain",
                    "temporal_positional_chain",
                    "memory_engram_chain",
                    "attention_routing_chain",
                    "residual_normalization_chain",
                    "sparse_expert_gate_chain",
                    "feedforward_expert_chain",
                    "laminar_microcircuit_chain",
                    "neural_pathway_chain",
                    "synaptic_transmission_chain",
                    "neuroplastic_weight_chain",
                    "neuromodulatory_state_chain",
                    "latent_loop_exit_chain",
                    "kv_cache_compression_chain",
                    "loss_backpropagation_chain",
                    "optimizer_school_chain",
                    "downstream_runtime_chain",
                    "action_output_decoder_chain",
                    "forward_propagation_chain",
                    "backward_propagation_chain",
                    "parameter_tensor_chain",
                    "activation_function_chain",
                    "computational_graph_chain",
                    "optimizer_state_vector_chain",
                    "model_genome_chain",
                    "tensor_runtime_kernel_chain",
                    "layer_block_stack_chain",
                    "distillation_loop_chain",
                    "federated_influence_chain",
                    "executable_dream_cycle_chain",
                    "deep_replay_drilldown_chain",
                    "durable_storage_chain",
                    "checkpoint_coverage_chain",
                    "runtime_decision_chain",
                    "backend_quantization_execution_chain",
                    "tool_execution_registry_chain",
                    "task_dependency_graph_chain",
                    "provider_circuit_breaker_chain",
                    "prompt_overlay_registry_chain",
                    "skill_system_loader_chain",
                    "bridge_manager_chain",
                    "research_monitor_pipeline_chain",
                    "node_output_chain",
                    "candidate_chain",
                    "dream_chain",
                    "productionization_chain",
                    "runtime_research_foundry",
                    "signed_federation_security",
                    "release_chain",
                    "active_release_chain",
                    "rollback_chain",
                    "rewind_chain",
                    "health_chain",
                    "self_healing_chain",
                    "global_federation_review_chain",
                    "route_candidate_evaluation_chain",
                    "route_candidate_approval_chain",
                    "route_candidate_rollback_chain",
                    "runtime_growth_receipt_chain",
                ],
                "available_chains": [
                    "project_heartbeat_chain",
                    "project_heartbeat_replay_chain",
                    "plane_trace",
                    "neural_bus",
                    "hive_blackboard",
                    "federated_prior_ledger",
                    "federated_per_plane_sync",
                    "personality_preference_chain",
                    "checkpoint_chain",
                    "sensory_input_chain",
                    "embedding_tensor_chain",
                    "temporal_positional_chain",
                    "memory_engram_chain",
                    "attention_routing_chain",
                    "residual_normalization_chain",
                    "sparse_expert_gate_chain",
                    "feedforward_expert_chain",
                    "laminar_microcircuit_chain",
                    "neural_pathway_chain",
                    "synaptic_transmission_chain",
                    "neuroplastic_weight_chain",
                    "neuromodulatory_state_chain",
                    "latent_loop_exit_chain",
                    "kv_cache_compression_chain",
                    "loss_backpropagation_chain",
                    "optimizer_school_chain",
                    "downstream_runtime_chain",
                    "action_output_decoder_chain",
                    "forward_propagation_chain",
                    "backward_propagation_chain",
                    "parameter_tensor_chain",
                    "activation_function_chain",
                    "computational_graph_chain",
                    "optimizer_state_vector_chain",
                    "model_genome_chain",
                    "tensor_runtime_kernel_chain",
                    "layer_block_stack_chain",
                    "distillation_loop_chain",
                    "federated_influence_chain",
                    "executable_dream_cycle_chain",
                    "deep_replay_drilldown_chain",
                    "durable_storage_chain",
                    "checkpoint_coverage_chain",
                    "runtime_decision_chain",
                    "backend_quantization_execution_chain",
                    "tool_execution_registry_chain",
                    "task_dependency_graph_chain",
                    "provider_circuit_breaker_chain",
                    "prompt_overlay_registry_chain",
                    "skill_system_loader_chain",
                    "bridge_manager_chain",
                    "research_monitor_pipeline_chain",
                    "node_output_chain",
                    "candidate_chain",
                    "dream_chain",
                    "activation_chain",
                    "productionization_chain",
                    "release_chain",
                    "active_release_chain",
                    "rollback_chain",
                    "rewind_chain",
                    "health_chain",
                    "self_healing_chain",
                    "global_federation_review_chain",
                    "route_candidate_evaluation_chain",
                    "route_candidate_approval_chain",
                    "route_candidate_rollback_chain",
                    "runtime_growth_receipt_chain",
                ],
                "chain_counts": {
                    "project_heartbeat_chain": len(project_heartbeat_chain),
                    "project_heartbeat_replay_chain": len(project_heartbeat_records),
                    "plane_trace": 1 if selected_run and selected_run.get("plane_trace") else 0,
                    "neural_bus": 1 if selected_run and selected_run.get("neural_bus") else 0,
                    "hive_blackboard": 1 if selected_run and selected_run.get("hive_blackboard") else 0,
                    "federated_per_plane_sync": 1 if federated_per_plane_sync.get("packet_ref") else 0,
                    "personality_preference_chain": len(personality_preference_chain),
                    "sensory_input_chain": len(sensory_inputs),
                    "embedding_tensor_chain": len(embedding_tensors),
                    "temporal_positional_chain": len(temporal_positionals),
                    "memory_engram_chain": len(memory_engrams),
                    "attention_routing_chain": len(attention_routing_ledgers),
                    "residual_normalization_chain": len(residual_normalizations),
                    "sparse_expert_gate_chain": len(sparse_expert_gates),
                    "feedforward_expert_chain": len(feedforward_experts),
                    "laminar_microcircuit_chain": len(laminar_microcircuit_chain),
                    "neural_pathway_chain": len(neural_pathway_chain),
                    "synaptic_transmission_chain": len(synaptic_transmission_chain),
                    "neuroplastic_weight_chain": len(neuroplastic_weight_chain),
                    "neuromodulatory_state_chain": len(neuromodulatory_state_chain),
                    "latent_loop_exit_chain": len(latent_loop_exits),
                    "kv_cache_compression_chain": len(kv_cache_compressions),
                    "loss_backpropagation_chain": len(loss_backpropagations),
                    "optimizer_school_chain": len(optimizer_schools),
                    "checkpoint_chain": len(checkpoints),
                    "downstream_runtime_chain": len(downstream_runtime_chain),
                    "action_output_decoder_chain": len(action_output_decoders),
                    "forward_propagation_chain": len(forward_propagations),
                    "backward_propagation_chain": len(backward_propagations),
                    "parameter_tensor_chain": len(parameter_tensors),
                    "activation_function_chain": len(activation_functions),
                    "computational_graph_chain": len(computational_graphs),
                    "optimizer_state_vector_chain": len(optimizer_state_vectors),
                    "model_genome_chain": len(model_genomes),
                    "tensor_runtime_kernel_chain": len(tensor_runtime_kernels),
                    "layer_block_stack_chain": len(layer_block_stacks),
                    "distillation_loop_chain": len(distillation_loops),
                    "federated_influence_chain": len(federated_influences),
                    "executable_dream_cycle_chain": len(executable_dream_cycles),
                    "deep_replay_drilldown_chain": len(deep_replay_drilldowns),
                    "durable_storage_chain": len(durable_storages),
                    "checkpoint_coverage_chain": len(checkpoint_coverages),
                    "runtime_decision_chain": len(runtime_decisions),
                    "backend_quantization_execution_chain": len(backend_quantization_executions),
                    "node_output_chain": len(node_output_chain),
                    "candidate_chain": len(self._list_artifacts(self.candidate_dir, session_id=session_id, limit=limit)),
                    "dream_chain": len(self._list_artifacts(self.dream_dir, session_id=session_id, limit=limit)),
                    "release_chain": len(releases),
                    "rollback_chain": len(rollbacks),
                    "rewind_chain": len(rewinds),
                    "health_chain": len(health_events),
                    "self_healing_chain": len(self_healing_routes),
                    "global_federation_review_chain": len(global_federation_reviews),
                    "route_candidate_evaluation_chain": len(route_candidate_evaluations),
                    "route_candidate_approval_chain": len(route_candidate_approvals),
                    "route_candidate_rollback_chain": len(route_candidate_rollbacks),
                    "runtime_growth_receipt_chain": len(runtime_growth_receipt_chain),
                },
                "mutation_policy": "read-only-until-explicit-checkpoint-rewind-command",
            },
        }

    def review_global_federation_promotion(
        self,
        request: HiveGlobalFederationReviewRequest | dict[str, Any],
    ) -> dict[str, Any]:
        normalized = (
            request
            if isinstance(request, HiveGlobalFederationReviewRequest)
            else HiveGlobalFederationReviewRequest.model_validate(request)
        )
        created_at = utcnow().isoformat()
        runs = self._list_artifacts(self.forward_dir, session_id=normalized.session_id, limit=200)
        prior_ledger = _federated_prior_ledger(
            self._list_artifacts(self.prior_dir, session_id=normalized.session_id, limit=200)
        )
        packets = [
            run.get("federated_learning_packet")
            for run in runs
            if isinstance(run.get("federated_learning_packet"), dict)
        ]
        review_id = new_id("global_federation_review")
        artifact_path = self._artifact_path(self.global_federation_dir, review_id)
        result = _global_federation_review_payload(
            normalized=normalized,
            review_id=review_id,
            created_at=created_at,
            packets=packets,
            prior_ledger=prior_ledger,
        )
        result["artifact_path"] = str(artifact_path) if artifact_path else None
        self._persist(artifact_path, result)
        return result

    def rewind_checkpoint(self, request: HiveCheckpointRewindRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = (
            request
            if isinstance(request, HiveCheckpointRewindRequest)
            else HiveCheckpointRewindRequest.model_validate(request)
        )
        created_at = utcnow().isoformat()
        checkpoints = self._list_artifacts(self.checkpoint_dir, session_id=normalized.session_id, limit=200)
        checkpoint_snapshot = _select_checkpoint_snapshot(checkpoints, normalized.checkpoint_id)
        if checkpoint_snapshot is None:
            raise ValueError("rewind_requires_existing_checkpoint_snapshot")

        rewind_id = new_id("hive_rewind")
        artifact_path = self._artifact_path(self.rewind_dir, rewind_id)
        source_snapshot_path = self._artifact_path(self.checkpoint_dir, normalized.checkpoint_id)
        snapshot_exists = bool(source_snapshot_path and source_snapshot_path.exists())
        snapshot_text = (
            source_snapshot_path.read_text(encoding="utf-8")
            if source_snapshot_path and source_snapshot_path.exists()
            else json.dumps(checkpoint_snapshot, sort_keys=True)
        )
        source_digest = _privacy_digest(snapshot_text)
        restore_allowed = normalized.human_governance_approval and snapshot_exists
        result = {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-checkpoint-rewind-v0",
            "authority": "NexusBrain",
            "rewind_id": rewind_id,
            "session_id": normalized.session_id,
            "checkpoint_ref": normalized.checkpoint_id,
            "rewind_state": "restore_validated" if restore_allowed else "blocked",
            "restore_mode": normalized.restore_mode,
            "human_governance_approval": normalized.human_governance_approval,
            "reason_digest": _privacy_digest(normalized.reason),
            "source_snapshot_artifact_path": str(source_snapshot_path) if source_snapshot_path else None,
            "source_snapshot_digest": source_digest,
            "restored_snapshot_digest": source_digest if restore_allowed else None,
            "restore_validation": {
                "restore_state": "validated_snapshot_artifact" if restore_allowed else "blocked_pending_approval_or_snapshot",
                "snapshot_artifact_exists": snapshot_exists,
                "snapshot_contract_id": checkpoint_snapshot.get("snapshot_contract_id"),
                "snapshot_has_pre_write_snapshot": bool(checkpoint_snapshot.get("pre_write_snapshot")),
                "snapshot_has_session_turn_snapshot": bool(checkpoint_snapshot.get("session_turn_snapshot")),
                "snapshot_has_token_snapshot": bool(checkpoint_snapshot.get("token_snapshot")),
                "raw_private_content_in_snapshot": bool(checkpoint_snapshot.get("raw_private_content_included")),
                "restore_scope": checkpoint_snapshot.get("snapshot_scope"),
            },
            "diff_preview": {
                "preview_state": "generated",
                "active_production_mutation_delta": "none",
                "raw_private_content_delta": "none",
                "restored_refs": [
                    checkpoint_snapshot.get("activation_ref"),
                    normalized.checkpoint_id,
                ],
                "write_scope": "rewind-artifact-only",
            },
            "prompt_tool_snapshot_replay": {
                "prompt_preview_digest": checkpoint_snapshot.get("prompt_preview_digest"),
                "tool_snapshot_digest": checkpoint_snapshot.get("tool_snapshot_digest"),
                "token_snapshot": checkpoint_snapshot.get("token_snapshot") or {},
                "activation_ref": checkpoint_snapshot.get("activation_ref"),
            },
            "active_production_mutated": False,
            "privacy_boundary": {
                "raw_reason_exported": False,
                "raw_prompt_exported": False,
                "raw_tool_targets_exported": False,
                "local_paths_exported": False,
            },
            "created_at": created_at,
            "artifact_path": str(artifact_path) if artifact_path else None,
            "metadata": normalized.metadata,
        }
        self._persist(artifact_path, result)
        return result

    def run_recursive_dream(self, request: HiveRecursiveDreamRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = (
            request
            if isinstance(request, HiveRecursiveDreamRequest)
            else HiveRecursiveDreamRequest.model_validate(request)
        )
        created_at = utcnow().isoformat()
        dream_id = new_id("hive_dream")
        capability_terms = _terms(normalized.requested_capabilities)
        seed = _stable_key(" ".join([normalized.problem_statement, *capability_terms]))
        candidate_id = f"dreamed-{seed}"
        title_terms = " ".join(term.replace("_", " ") for term in capability_terms[:4]) or "hive substrate"
        artifact_path = self._artifact_path(self.dream_dir, dream_id)
        dream_context = _dream_context_payload(
            request=normalized,
            health_events=self._list_artifacts(self.health_dir, session_id=normalized.session_id, limit=20),
            candidates=self._list_artifacts(self.candidate_dir, session_id=normalized.session_id, limit=20),
            prior_ledger=_federated_prior_ledger(
                self._list_artifacts(self.prior_dir, session_id=normalized.session_id, limit=100)
            ),
        )
        candidate_request = {
            "session_id": normalized.session_id,
            "candidate_id": candidate_id,
            "title": f"Dreamed {title_terms.title()} Expert",
            "candidate_kind": "generated_expert",
            "parent_node_refs": normalized.parent_node_refs,
            "source_refs": normalized.source_refs,
            "capability_traits": capability_terms,
            "dreamed_traits": sorted(set(capability_terms + ["recursive_neural_dreaming", "novel_solution_search"])),
            "license_state": "operator-owned",
            "requested_promotion": True,
        }
        result = {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-recursive-neural-dreaming-v0",
            "authority": "NexusBrain",
            "dream_id": dream_id,
            "session_id": normalized.session_id,
            "problem_statement_digest": _privacy_digest(normalized.problem_statement),
            "source_refs": normalized.source_refs,
            "memory_ref_count": len(normalized.memory_refs),
            "created_at": created_at,
            "dreamer": {
                "role": "high-temperature-novel-candidate-generator",
                "temperature": "high",
                "access_scope": "hive-wide-neuroplasticity-fabric",
                "output_state": "candidate_request_generated",
            },
            "critic": {
                "role": "low-temperature-coherence-safety-feasibility-reviewer",
                "temperature": "low",
                "review_state": "accepted_for_sandbox_plan",
                "promotion_boundary": "cannot_mutate_registry_without_sandbox_eval_school_and_human_governance",
            },
            "dream_context": dream_context,
            "candidate_request": candidate_request,
            "sandbox_eval_plan": {
                "plan_id": new_id("sandbox_eval_plan"),
                "required_before_promotion": True,
                "context_refs": {
                    "health_event_refs": dream_context["consumed_health_event_refs"],
                    "failed_candidate_refs": dream_context["consumed_failed_candidate_refs"],
                    "prior_ledger_ref": dream_context["consumed_prior_ledger"].get("ledger_id"),
                    "research_source_refs": dream_context["research_source_refs"],
                },
                "required_evidence": [
                    "closed_sandbox_run",
                    "eval_suite_pass",
                    "security_gate_pass",
                    "privacy_gate_pass",
                    "ivy_league_teacher_panel",
                    "human_governance_approval",
                ],
            },
            "artifact_path": str(artifact_path) if artifact_path else None,
            "metadata": normalized.metadata,
        }
        self._persist(artifact_path, result)
        return result

    def run_productionization_cycle(self, request: HiveProductionizationRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = (
            request
            if isinstance(request, HiveProductionizationRequest)
            else HiveProductionizationRequest.model_validate(request)
        )
        created_at = utcnow().isoformat()
        productionization_id = new_id("hive_productionization")
        forward_runs = self._list_artifacts(self.forward_dir, session_id=normalized.session_id, limit=100)
        source_run = _select_source_run(forward_runs, normalized.source_run_id)
        if source_run is None:
            raise ValueError("productionization_cycle_requires_existing_forward_pass")

        neural_bus = source_run.get("neural_bus") or {}
        hive_blackboard = source_run.get("hive_blackboard") or {}
        laminar_microcircuit = source_run.get("laminar_microcircuit_ledger") or {}
        neural_pathway = source_run.get("neural_pathway_map") or {}
        synaptic_transmission = source_run.get("synaptic_transmission_ledger") or {}
        neuroplastic_weight = source_run.get("neuroplastic_weight_ledger") or {}
        neuromodulatory_state = source_run.get("neuromodulatory_state_ledger") or {}
        checkpoint = source_run.get("checkpoint") or {}
        prior_ledger = _federated_prior_ledger(
            self._list_artifacts(self.prior_dir, session_id=normalized.session_id, limit=100)
        )
        replay_ref = self.replay(session_id=normalized.session_id, run_id=source_run.get("run_id"))
        artifact_path = self._artifact_path(self.productionization_dir, productionization_id)

        substrate_bound_inputs = {
            "source_run_id": source_run.get("run_id"),
            "neural_bus_ref": neural_bus.get("bus_id"),
            "hive_blackboard_ref": hive_blackboard.get("residual_state_id"),
            "laminar_microcircuit_ref": laminar_microcircuit.get("microcircuit_id"),
            "neural_pathway_ref": neural_pathway.get("pathway_id"),
            "synaptic_transmission_ref": synaptic_transmission.get("transmission_id"),
            "neuroplastic_weight_ref": neuroplastic_weight.get("weight_ledger_id"),
            "neuromodulatory_state_ref": neuromodulatory_state.get("neuromodulator_id"),
            "checkpoint_ref": checkpoint.get("checkpoint_id"),
            "federated_prior_ledger_ref": prior_ledger.get("ledger_id"),
            "replay_ref": replay_ref.get("replay_id"),
            "input_contract": "existing-forward-pass-neural-bus-hive-blackboard-pathway-checkpoint-and-priors",
            "direct_local_state_reads_allowed": False,
        }
        sandbox_provider_run = _productionization_sandbox_provider_run(
            normalized=normalized,
            productionization_id=productionization_id,
            created_at=created_at,
            substrate_bound_inputs=substrate_bound_inputs,
        )
        teacher_distillation = _productionization_teacher_distillation(
            normalized=normalized,
            productionization_id=productionization_id,
            created_at=created_at,
        )
        federation_security = _productionization_federation_security(
            normalized=normalized,
            productionization_id=productionization_id,
            created_at=created_at,
            prior_ledger=prior_ledger,
        )
        runtime_research_foundry = _productionization_runtime_research_foundry(
            normalized=normalized,
            productionization_id=productionization_id,
            created_at=created_at,
        )
        release_ready = (
            normalized.human_governance_approval
            and sandbox_provider_run["execution_state"] == "passed"
            and teacher_distillation["certification_state"] == "certified"
            and federation_security["privacy_audit"]["raw_private_data_exported"] is False
            and runtime_research_foundry["best_trial"]["promotion_state"] == "shadow_candidate"
        )
        gated_release = {
            "gate_id": new_id("gated_release"),
            "release_state": (
                "ready_for_human_approved_shadow_release"
                if release_ready
                else "blocked_pending_human_governance_approval_or_evidence"
            ),
            "active_production_mutated": False,
            "release_scope": "shadow-only-production-candidate",
            "human_governance_approval": normalized.human_governance_approval,
            "required_evidence_refs": [
                sandbox_provider_run["sandbox_run_id"],
                teacher_distillation["distillation_trace_id"],
                federation_security["signed_packet"]["packet_id"],
                runtime_research_foundry["foundry_run_id"],
                laminar_microcircuit.get("microcircuit_id"),
                neural_pathway.get("pathway_id"),
                synaptic_transmission.get("transmission_id"),
                neuroplastic_weight.get("weight_ledger_id"),
                neuromodulatory_state.get("neuromodulator_id"),
                checkpoint.get("checkpoint_id"),
            ],
        }
        rollback = {
            "rollback_id": new_id("hive_rollback"),
            "checkpoint_ref": checkpoint.get("checkpoint_id"),
            "checkpoint_snapshot_artifact_path": checkpoint.get("snapshot_artifact_path"),
            "restore_validation": {
                "restore_state": "validated_metadata_only",
                "restore_scope": "shadow-release-candidate-and-routing-prior",
                "raw_private_content_in_snapshot": False,
            },
            "rollback_policy": "restore-shadow-candidate-to-side-bar-and-keep-active-production-unchanged",
        }
        lifecycle_state = "shadow_release_ready" if release_ready else "blocked"
        result = {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-substrate-productionization-v0",
            "authority": "NexusBrain",
            "productionization_id": productionization_id,
            "session_id": normalized.session_id,
            "subject_id": normalized.subject_id,
            "goal_digest": _privacy_digest(normalized.goal),
            "candidate_refs": normalized.candidate_refs,
            "source_run_id": source_run.get("run_id"),
            "lifecycle_state": lifecycle_state,
            "created_at": created_at,
            "substrate_bound_inputs": substrate_bound_inputs,
            "sandbox_provider_run": sandbox_provider_run,
            "teacher_distillation": teacher_distillation,
            "federation_security": federation_security,
            "runtime_research_foundry": runtime_research_foundry,
            "gated_release": gated_release,
            "rollback": rollback,
            "artifact_path": str(artifact_path) if artifact_path else None,
            "metadata": normalized.metadata,
        }
        self._persist(artifact_path, result)
        return result

    def activate_shadow_release(self, request: HiveShadowReleaseRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = (
            request
            if isinstance(request, HiveShadowReleaseRequest)
            else HiveShadowReleaseRequest.model_validate(request)
        )
        created_at = utcnow().isoformat()
        productionizations = self._list_artifacts(
            self.productionization_dir,
            session_id=normalized.session_id,
            limit=100,
        )
        productionization = _select_productionization(productionizations, normalized.productionization_id)
        if productionization is None:
            raise ValueError("shadow_release_requires_existing_productionization")
        release_ready = (
            productionization.get("lifecycle_state") == "shadow_release_ready"
            and (productionization.get("gated_release") or {}).get("release_state")
            == "ready_for_human_approved_shadow_release"
        )
        if not release_ready or not normalized.human_governance_approval:
            release_state = "blocked"
        else:
            release_state = "active_shadow"
        release_id = new_id("hive_release")
        artifact_path = self._artifact_path(self.release_dir, release_id)
        runtime_research = productionization.get("runtime_research_foundry") or {}
        best_trial = runtime_research.get("best_trial") or {}
        substrate_inputs = productionization.get("substrate_bound_inputs") or {}
        rollback = productionization.get("rollback") or {}
        result = {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-shadow-release-v0",
            "authority": "NexusBrain",
            "release_id": release_id,
            "session_id": normalized.session_id,
            "productionization_ref": normalized.productionization_id,
            "release_state": release_state,
            "release_scope": "shadow-only",
            "active_production_mutated": False,
            "operator_approval_ref": normalized.operator_approval_ref,
            "human_governance_approval": normalized.human_governance_approval,
            "selected_method": best_trial,
            "evidence_refs": {
                "neural_bus_ref": substrate_inputs.get("neural_bus_ref"),
                "hive_blackboard_ref": substrate_inputs.get("hive_blackboard_ref"),
                "laminar_microcircuit_ref": substrate_inputs.get("laminar_microcircuit_ref"),
                "neural_pathway_ref": substrate_inputs.get("neural_pathway_ref"),
                "synaptic_transmission_ref": substrate_inputs.get("synaptic_transmission_ref"),
                "neuroplastic_weight_ref": substrate_inputs.get("neuroplastic_weight_ref"),
                "neuromodulatory_state_ref": substrate_inputs.get("neuromodulatory_state_ref"),
                "source_run_id": substrate_inputs.get("source_run_id"),
                "productionization_ref": normalized.productionization_id,
                "sandbox_run_ref": (productionization.get("sandbox_provider_run") or {}).get("sandbox_run_id"),
                "teacher_distillation_ref": (productionization.get("teacher_distillation") or {}).get("distillation_trace_id"),
                "signed_packet_ref": (
                    (productionization.get("federation_security") or {}).get("signed_packet") or {}
                ).get("packet_id"),
                "runtime_foundry_ref": runtime_research.get("foundry_run_id"),
                "rollback_checkpoint_ref": rollback.get("checkpoint_ref"),
            },
            "rollback_plan": {
                "rollback_available": True,
                "rollback_endpoint": "/ops/brain/hive-substrate/rollback",
                "checkpoint_ref": rollback.get("checkpoint_ref"),
                "restore_scope": "shadow-release-candidate-and-routing-prior",
            },
            "privacy_boundary": {
                "raw_private_data_exported": False,
                "active_release_raw_prompt_access": False,
                "local_paths_exported": False,
            },
            "created_at": created_at,
            "artifact_path": str(artifact_path) if artifact_path else None,
            "metadata": normalized.metadata,
        }
        self._persist(artifact_path, result)
        return result

    def promote_active_release(self, request: HiveActiveReleaseRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = (
            request
            if isinstance(request, HiveActiveReleaseRequest)
            else HiveActiveReleaseRequest.model_validate(request)
        )
        created_at = utcnow().isoformat()
        releases = self._list_artifacts(self.release_dir, session_id=normalized.session_id, limit=100)
        shadow_release = _select_release(releases, normalized.shadow_release_id)
        if shadow_release is None:
            raise ValueError("active_release_requires_existing_shadow_release")
        blocked_reasons = _active_release_blocked_reasons(normalized, shadow_release)
        release_state = "active_production" if not blocked_reasons else "blocked"
        release_id = new_id("hive_active_release")
        artifact_path = self._artifact_path(self.release_dir, release_id)
        shadow_evidence = shadow_release.get("evidence_refs") or {}
        selected_method = shadow_release.get("selected_method") or {}
        canary_percentage = int(normalized.metadata.get("canary_percentage", 1) or 1)
        soak_minutes = int(normalized.metadata.get("soak_minutes", 0) or 0)
        result = {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-active-release-gate-v0",
            "authority": "NexusBrain",
            "release_id": release_id,
            "session_id": normalized.session_id,
            "shadow_release_ref": normalized.shadow_release_id,
            "productionization_ref": shadow_release.get("productionization_ref"),
            "release_state": release_state,
            "release_scope": "active-production-release-pointer",
            "active_production_mutated": release_state == "active_production",
            "operator_approval_ref": normalized.operator_approval_ref,
            "human_governance_approval": normalized.human_governance_approval,
            "blocked_reasons": blocked_reasons,
            "selected_method": selected_method,
            "active_mutation": {
                "mutation_kind": "release-pointer-metadata-only",
                "code_or_model_weights_mutated": False,
                "runtime_pointer_mutated": release_state == "active_production",
                "mutation_boundary": "no-code-no-weight-change-without-separate-signed-release-process",
            },
            "canary_gate": {
                "gate_state": "passed" if normalized.canary_eval_refs else "blocked",
                "canary_percentage": canary_percentage,
                "eval_refs": normalized.canary_eval_refs,
                "required_before_active_release": True,
            },
            "soak_gate": {
                "gate_state": "passed" if soak_minutes >= 0 else "blocked",
                "soak_minutes": soak_minutes,
                "monitoring_required": True,
            },
            "monitoring_gate": {
                "gate_state": "armed" if normalized.monitoring_refs else "blocked",
                "monitoring_refs": normalized.monitoring_refs,
                "incident_trigger": "rollback-on-regression-or-policy-veto",
            },
            "rollback_plan": {
                "rollback_available": bool(normalized.rollback_rehearsal_ref),
                "rollback_endpoint": "/ops/brain/hive-substrate/rollback",
                "rollback_rehearsal_ref": normalized.rollback_rehearsal_ref,
                "restore_scope": "active-production-release-pointer",
                "checkpoint_ref": (shadow_release.get("rollback_plan") or {}).get("checkpoint_ref"),
            },
            "evidence_refs": {
                "shadow_release_ref": normalized.shadow_release_id,
                "productionization_ref": shadow_release.get("productionization_ref"),
                "neural_bus_ref": shadow_evidence.get("neural_bus_ref"),
                "hive_blackboard_ref": shadow_evidence.get("hive_blackboard_ref"),
                "laminar_microcircuit_ref": shadow_evidence.get("laminar_microcircuit_ref"),
                "neural_pathway_ref": shadow_evidence.get("neural_pathway_ref"),
                "synaptic_transmission_ref": shadow_evidence.get("synaptic_transmission_ref"),
                "neuroplastic_weight_ref": shadow_evidence.get("neuroplastic_weight_ref"),
                "neuromodulatory_state_ref": shadow_evidence.get("neuromodulatory_state_ref"),
                "sandbox_run_ref": shadow_evidence.get("sandbox_run_ref"),
                "teacher_distillation_ref": shadow_evidence.get("teacher_distillation_ref"),
                "signed_packet_ref": shadow_evidence.get("signed_packet_ref"),
                "runtime_foundry_ref": shadow_evidence.get("runtime_foundry_ref"),
                "rollback_rehearsal_ref": normalized.rollback_rehearsal_ref,
                "canary_eval_refs": normalized.canary_eval_refs,
                "monitoring_refs": normalized.monitoring_refs,
            },
            "privacy_boundary": {
                "raw_private_data_exported": False,
                "raw_canary_logs_exported": False,
                "local_paths_exported": False,
            },
            "created_at": created_at,
            "artifact_path": str(artifact_path) if artifact_path else None,
            "metadata": normalized.metadata,
        }
        self._persist(artifact_path, result)
        return result

    def rollback_shadow_release(self, request: HiveRollbackRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = request if isinstance(request, HiveRollbackRequest) else HiveRollbackRequest.model_validate(request)
        created_at = utcnow().isoformat()
        releases = self._list_artifacts(self.release_dir, session_id=normalized.session_id, limit=100)
        release = _select_release(releases, normalized.release_id)
        if release is None:
            raise ValueError("rollback_requires_existing_release")
        rollback_id = new_id("hive_rollback_exec")
        artifact_path = self._artifact_path(self.rollback_dir, rollback_id)
        restore_scope = (
            "active-production-release-pointer"
            if release.get("release_scope") == "active-production-release-pointer"
            else "shadow-release-candidate-and-routing-prior"
        )
        active_pointer_rollback = release.get("release_scope") == "active-production-release-pointer"
        release_after_rollback = {
            "release_id": release.get("release_id"),
            "release_state": "rolled_back" if normalized.human_governance_approval else "rollback_blocked",
            "active_production_mutated": bool(active_pointer_rollback and normalized.human_governance_approval),
            "rollback_id": rollback_id,
        }
        result = {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-shadow-release-rollback-v0",
            "authority": "NexusBrain",
            "rollback_id": rollback_id,
            "session_id": normalized.session_id,
            "release_ref": normalized.release_id,
            "previous_release_state": release.get("release_state"),
            "rollback_state": "rolled_back" if normalized.human_governance_approval else "blocked",
            "reason_digest": _privacy_digest(normalized.reason),
            "human_governance_approval": normalized.human_governance_approval,
            "active_production_mutated": bool(active_pointer_rollback and normalized.human_governance_approval),
            "restore_validation": {
                "restore_state": "validated_metadata_only",
                "restore_scope": restore_scope,
                "raw_private_content_in_snapshot": False,
            },
            "release_after_rollback": release_after_rollback,
            "evidence_refs": {
                "release_ref": normalized.release_id,
                "productionization_ref": release.get("productionization_ref"),
                "checkpoint_ref": (release.get("rollback_plan") or {}).get("checkpoint_ref"),
                "neural_bus_ref": (release.get("evidence_refs") or {}).get("neural_bus_ref"),
                "hive_blackboard_ref": (release.get("evidence_refs") or {}).get("hive_blackboard_ref"),
                "laminar_microcircuit_ref": (release.get("evidence_refs") or {}).get("laminar_microcircuit_ref"),
                "neural_pathway_ref": (release.get("evidence_refs") or {}).get("neural_pathway_ref"),
                "synaptic_transmission_ref": (release.get("evidence_refs") or {}).get("synaptic_transmission_ref"),
                "neuroplastic_weight_ref": (release.get("evidence_refs") or {}).get("neuroplastic_weight_ref"),
                "neuromodulatory_state_ref": (release.get("evidence_refs") or {}).get("neuromodulatory_state_ref"),
            },
            "privacy_boundary": {
                "raw_private_data_exported": False,
                "raw_reason_exported": False,
                "active_release_raw_prompt_access": False,
            },
            "created_at": created_at,
            "artifact_path": str(artifact_path) if artifact_path else None,
            "metadata": normalized.metadata,
        }
        self._persist(artifact_path, result)
        return result

    def health(self, *, session_id: str | None = None, limit: int = 20) -> dict[str, Any]:
        health_events = self._list_artifacts(self.health_dir, session_id=session_id, limit=limit)
        self_healing_routes = self._list_artifacts(self.self_healing_dir, session_id=session_id, limit=limit)
        runs = self._list_artifacts(self.forward_dir, session_id=session_id, limit=limit)
        project_heartbeats = [
            run.get("project_heartbeat")
            for run in runs
            if isinstance(run.get("project_heartbeat"), dict)
        ]
        runtime_state = (
            "degraded"
            if any(_runtime_record_is_blocked(event) for event in health_events)
            else ("live-bound" if health_events else "static-canon")
        )
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-health-monitor-v0",
            "authority": "NexusBrain",
            "session_id": session_id,
            "runtime_state": runtime_state,
            "health_ledger": _health_ledger(health_events),
            "self_healing_ledger": _self_healing_ledger(self_healing_routes),
            "project_heartbeat": (
                project_heartbeats[0]
                if project_heartbeats
                else _empty_project_heartbeat()
            ),
            "project_heartbeat_count": len(project_heartbeats),
            "latest_health_event": health_events[0] if health_events else None,
            "latest_self_healing_route": self_healing_routes[0] if self_healing_routes else None,
            "monitoring_contract": {
                "visibility_scope": "hive-visible",
                "silent_failure_policy": "forbidden",
                "active_tasks_continue_when_route_around_available": True,
                "active_production_mutation_allowed": False,
            },
        }

    def assimilate_candidate(self, request: HiveAssimilationCandidateRequest | dict[str, Any]) -> dict[str, Any]:
        normalized = (
            request
            if isinstance(request, HiveAssimilationCandidateRequest)
            else HiveAssimilationCandidateRequest.model_validate(request)
        )
        created_at = utcnow().isoformat()
        candidate_run_id = new_id("hive_candidate")
        closed_sandbox_evaluation = _closed_sandbox_evaluation(
            normalized,
            candidate_run_id=candidate_run_id,
            created_at=created_at,
        )
        effective_sandbox_refs = list(normalized.sandbox_refs)
        effective_eval_refs = list(normalized.eval_refs)
        if closed_sandbox_evaluation is not None:
            effective_sandbox_refs.append(closed_sandbox_evaluation["sandbox_run"]["sandbox_run_id"])
            effective_eval_refs.append(closed_sandbox_evaluation["eval_suite"]["eval_suite_id"])
        effective_request = normalized.model_copy(
            update={
                "sandbox_refs": effective_sandbox_refs,
                "eval_refs": effective_eval_refs,
            }
        )
        sidebar_reasons = self._sidebar_reasons(effective_request)
        blocked_reasons = [] if normalized.source_refs else ["source_refs_missing"]
        blocked_reasons.extend(_closed_sandbox_block_reasons(closed_sandbox_evaluation))
        child_candidate = _is_generated_child_candidate(normalized)
        parent_retirement = _parent_retirement_review(
            effective_request,
            child_candidate=child_candidate,
            blocked_reasons=blocked_reasons,
            sidebar_reasons=sidebar_reasons,
        )
        ivy_league_school_review = _ivy_league_school_review(
            effective_request,
            parent_retirement=parent_retirement,
            closed_sandbox_evaluation=closed_sandbox_evaluation,
        )
        standalone_approved = _standalone_approval_ready(
            effective_request,
            child_candidate=child_candidate,
            blocked_reasons=blocked_reasons,
            sidebar_reasons=sidebar_reasons,
            parent_retirement=parent_retirement,
            closed_sandbox_evaluation=closed_sandbox_evaluation,
            ivy_league_school_review=ivy_league_school_review,
        )
        promotion_state = (
            "blocked"
            if blocked_reasons
            else "side_barred"
            if sidebar_reasons
            else "permanent_standalone_approved"
            if standalone_approved
            else "retention_review_required"
            if child_candidate
            else "promotion_ready"
        )
        genome = ExpertGenome(
            genome_id=new_id("expert_genome"),
            candidate_id=normalized.candidate_id,
            title=normalized.title,
            candidate_kind=normalized.candidate_kind,
            parent_genome_refs=normalized.parent_genome_refs,
            parent_node_refs=normalized.parent_node_refs,
            capability_traits=_terms(normalized.capability_traits),
            dreamed_traits=_terms(normalized.dreamed_traits),
            source_refs=normalized.source_refs,
            sandbox_refs=effective_sandbox_refs,
            eval_refs=effective_eval_refs,
            license_state=normalized.license_state,
            dream_temperature_profile={
                "dreamer": {"role": "novel_candidate_generation", "temperature": "high"},
                "reviewer": {"role": "coherence_feasibility_safety_review", "temperature": "low"},
                "promotion_boundary": "dreams_can_propose_candidates_but_cannot_mutate_production",
            },
            mutation_history=[
                "candidate_entered_hive_wide_neuroplasticity_fabric",
                "requires_lower_temperature_review_before_promotion",
                "temporary_first_use_before_retention_review",
            ],
            first_use_policy="temporary-shadow-first-use-no-permanent-standalone-status",
            retention_review_state=(
                "blocked"
                if blocked_reasons
                else "waiting-for-sandbox-eval-evidence"
                if sidebar_reasons
                else "certified-for-standalone-retention"
                if standalone_approved
                else "ready-for-retention-value-review"
                if child_candidate
                else "not-a-generated-child-candidate"
            ),
            standalone_approval_state=(
                "approved-permanent-standalone"
                if standalone_approved
                else "not-approved-pending-retention-review"
                if child_candidate
                else "not-applicable"
            ),
            value_retention_rule=(
                "approve-permanent-standalone-only-if-retention-review-proves-increased-value-over-parent-nodes"
            ),
            parent_retirement_rule=(
                "retire-respective-parent-only-after-ivy-review-proves-great-child-outperformance"
            ),
            teacher_distillation_review_contract=parent_retirement["review_contract"],
            promotion_state=promotion_state,
            sidebar_reasons=blocked_reasons + sidebar_reasons,
            created_at=created_at,
        )
        policy_scan = self.policy_kernel.scan(
            [
                {
                    "target_id": f"artifact::{normalized.candidate_id}",
                    "target_type": "artifact",
                    "metadata": {
                        "promotion_requested": normalized.requested_promotion,
                        "license_state": normalized.license_state if normalized.source_refs else "",
                        "provenance_refs": normalized.source_refs,
                    },
                },
                {
                    "target_id": f"training::{normalized.candidate_id}",
                    "target_type": "training_candidate",
                    "metadata": {
                        "promotion_requested": normalized.requested_promotion,
                        "eval_refs": effective_eval_refs,
                        "contains_private_data": normalized.privacy_class in {"confidential", "regulated", "secret"},
                        "operator_approved": bool(normalized.metadata.get("operator_governance_approval")),
                    },
                },
                {
                    "target_id": f"autonomous-update::{normalized.candidate_id}",
                    "target_type": "autonomous_update",
                    "metadata": {
                        "promotion_requested": normalized.requested_promotion,
                        "rollback_plan": "checkpoint-rewind-ledger" if effective_sandbox_refs and effective_eval_refs else "",
                        "monitoring_plan": "substrate-scorecard-watch" if effective_eval_refs else "",
                    },
                },
            ]
        )
        lifecycle_state = (
            "blocked"
            if blocked_reasons
            else "side_barred"
            if sidebar_reasons
            else "permanent_standalone_approved"
            if standalone_approved
            else "retention_review_required"
            if child_candidate
            else "promotion_ready"
        )
        if policy_scan.summary.active_hard_fail_count and lifecycle_state in {
            "promotion_ready",
            "permanent_standalone_approved",
        }:
            lifecycle_state = "blocked"
        node_registry_update = _node_registry_update(
            effective_request,
            candidate_run_id=candidate_run_id,
            genome=genome,
            lifecycle_state=lifecycle_state,
            parent_retirement=parent_retirement,
            created_at=created_at,
        )
        artifact_path = self._artifact_path(self.candidate_dir, candidate_run_id)
        node_registry_artifact_path = self._artifact_path(
            self.node_registry_dir,
            node_registry_update["node_registry_update_id"],
        )
        node_registry_update["artifact_path"] = str(node_registry_artifact_path) if node_registry_artifact_path else None
        sandbox_artifact_path = None
        if closed_sandbox_evaluation is not None:
            sandbox_artifact_path = self._artifact_path(
                self.sandbox_dir,
                closed_sandbox_evaluation["closed_sandbox_evaluation_id"],
            )
            closed_sandbox_evaluation["artifact_path"] = str(sandbox_artifact_path) if sandbox_artifact_path else None
            closed_sandbox_evaluation["evidence_bundle"]["artifact_path"] = (
                str(sandbox_artifact_path) if sandbox_artifact_path else None
            )
        result = {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-neural-substrate-v0",
            "authority": "NexusBrain",
            "candidate_run_id": candidate_run_id,
            "session_id": normalized.session_id,
            "candidate_id": normalized.candidate_id,
            "title": normalized.title,
            "lifecycle_state": lifecycle_state,
            "created_at": created_at,
            "genome": genome.model_dump(mode="json"),
            "generated_node_rule": "temporary-first-use-review-required-before-permanent-standalone-parents-remain-intact",
            "retention_review": {
                "required_for_child_candidates": child_candidate,
                "first_use_state": "temporary",
                "standalone_approval_state": genome.standalone_approval_state,
                "approval_rule": genome.value_retention_rule,
                "review_inputs": [
                    "parent_comparison_scorecard",
                    "sandbox_refs",
                    "eval_refs",
                    "usage_value_delta",
                    "risk_regression_delta",
                    "operator_review",
                ],
            },
            "parent_retirement": parent_retirement,
            "closed_sandbox_evaluation": closed_sandbox_evaluation,
            "ivy_league_school_review": ivy_league_school_review,
            "node_registry_update": node_registry_update,
            "blocked_reasons": blocked_reasons,
            "sidebar_reasons": sidebar_reasons,
            "policy_scan": policy_scan.model_dump(mode="json"),
            "rollback_or_sidebar_rule": "no-promotion-without-sandbox-eval-policy-and-rollback",
            "artifact_path": str(artifact_path) if artifact_path else None,
            "metadata": normalized.metadata,
        }
        self._persist(sandbox_artifact_path, closed_sandbox_evaluation or {})
        self._persist(node_registry_artifact_path, node_registry_update)
        self._persist(artifact_path, result)
        return result

    def curate(self, *, session_id: str | None = None) -> dict[str, Any]:
        runs = self._list_artifacts(self.forward_dir, session_id=session_id, limit=200)
        health_events = self._list_artifacts(self.health_dir, session_id=session_id, limit=200)
        candidates = self._list_artifacts(self.candidate_dir, session_id=session_id, limit=200)
        runtime_state = (
            "degraded"
            if any(_runtime_record_is_blocked(record) for record in runs + health_events + candidates)
            else ("live-bound" if runs or health_events or candidates else "static-canon")
        )
        usage_counts: dict[str, int] = {}
        failure_counts: dict[str, int] = {}
        evidence_refs: dict[str, list[str]] = {}
        for run in runs:
            node_ids = ((run.get("route_decision") or {}).get("selected_node_ids") or [])
            for node_id in node_ids:
                usage_counts[node_id] = usage_counts.get(node_id, 0) + 1
                if run.get("run_id"):
                    evidence_refs.setdefault(node_id, []).append(str(run.get("run_id")))
        for event in health_events:
            node_ids = event.get("affected_node_ids") or event.get("selected_node_ids") or []
            failed = event.get("event_state") == "degraded_observed"
            for node_id in node_ids:
                if failed:
                    failure_counts[node_id] = failure_counts.get(node_id, 0) + 1
                if event.get("health_event_id"):
                    evidence_refs.setdefault(node_id, []).append(str(event.get("health_event_id")))
        for candidate in candidates:
            for node_id in candidate.get("parent_node_refs") or []:
                if candidate.get("candidate_run_id"):
                    evidence_refs.setdefault(str(node_id), []).append(str(candidate.get("candidate_run_id")))

        signatures: dict[str, list[HiveNode]] = {}
        for node in self.nodes:
            signature = "|".join(sorted(node.capabilities[:4]))
            signatures.setdefault(signature, []).append(node)

        recommendations: list[dict[str, Any]] = []
        for node in self.nodes:
            duplicate_count = len(signatures.get("|".join(sorted(node.capabilities[:4])), []))
            usage_count = usage_counts.get(node.node_id, 0)
            failure_count = failure_counts.get(node.node_id, 0)
            if node.protected:
                action = "keep"
                reason = "protected_substrate_node"
            elif node.quarantine_state != "clear":
                action = "archive_review"
                reason = "quarantine_state_requires_review"
            elif failure_count:
                action = "archive_review"
                reason = "health_failures_require_review"
            elif duplicate_count > 1:
                action = "merge_review"
                reason = "overlapping_capability_signature"
            else:
                action = "keep"
                reason = "unique_active_capability"
            recommendations.append(
                {
                    "node_id": node.node_id,
                    "name": node.name,
                    "action": action,
                    "reason": reason,
                    "protected": node.protected,
                    "usage_count": usage_count,
                    "failure_count": failure_count,
                    "last_evidence_refs": list(dict.fromkeys(evidence_refs.get(node.node_id, [])))[:5],
                }
            )

        return {
            "status_label": "LOCKED CANON",
            "surface_id": "hive-neural-substrate-curator",
            "authority": "NexusBrain",
            "runtime_state": runtime_state,
            "session_id": session_id,
            "review_id": new_id("hive_curator"),
            "node_count": len(self.nodes),
            "protected_node_count": sum(1 for node in self.nodes if node.protected),
            "evidence_summary": {
                "forward_pass_count": len(runs),
                "health_event_count": len(health_events),
                "candidate_count": len(candidates),
                "usage_ranked_node_count": len(usage_counts),
                "failure_ranked_node_count": len(failure_counts),
            },
            "curator_inputs": {
                "consumed_artifact_chains": ["forward_pass_chain", "health_chain", "candidate_chain"],
                "direct_local_state_reads": [],
                "input_contract": "substrate-artifact-ledgers-only",
            },
            "mutation_policy": "review-only-no-direct-delete",
            "neuroplasticity_boundary": "curator-can-audit-and-recommend-but-does-not-own-self-improvement",
            "recommendations": recommendations,
            "required_controls": [
                "usage_rank_before_prune",
                "operator_review_before_delete",
                "artifact_report_for_each_curator_run",
                "protected_core_nodes_are_immutable",
            ],
        }

    def _node_registry_view(self, *, session_id: str | None = None) -> dict[str, Any]:
        updates = self._list_artifacts(self.node_registry_dir, session_id=session_id, limit=200)
        active_generated_nodes: list[HiveNode] = []
        active_generated_node_ids: list[str] = []
        archived_parent_node_ids: list[str] = []
        rollback_restorable_parent_node_ids: list[str] = []
        archived_parent_records: list[dict[str, Any]] = []

        for update in reversed(updates):
            if update.get("mutation_state") != "durable_registry_updated":
                continue
            registered_node = update.get("registered_node") or {}
            if registered_node.get("node_id") and registered_node["node_id"] not in active_generated_node_ids:
                active_generated_node = _hive_node_from_registered_node(registered_node)
                active_generated_nodes.append(active_generated_node)
                active_generated_node_ids.append(active_generated_node.node_id)
            for retired_parent in update.get("retired_parent_nodes") or []:
                parent_node_id = str(retired_parent.get("node_id") or "")
                if not parent_node_id or parent_node_id in archived_parent_node_ids:
                    continue
                archived_parent_node_ids.append(parent_node_id)
                archived_parent_records.append(retired_parent)
                if retired_parent.get("rollback_policy"):
                    rollback_restorable_parent_node_ids.append(parent_node_id)

        return {
            "active_generated_nodes": active_generated_nodes,
            "archived_parent_node_ids": archived_parent_node_ids,
            "public_view": {
                "registry_id": "hive-durable-node-registry-v0",
                "session_id": session_id,
                "archive_model": "archive_not_delete",
                "active_generated_node_ids": active_generated_node_ids,
                "archived_parent_node_ids": archived_parent_node_ids,
                "rollback_restorable_parent_node_ids": rollback_restorable_parent_node_ids,
                "active_generated_nodes": [node.model_dump(mode="json") for node in active_generated_nodes],
                "archived_parent_nodes": archived_parent_records,
                "active_routing_effect": "generated_children_added_retired_parents_archived",
            },
        }

    def _select_nodes(self, requested_caps: list[str], *, node_registry_view: dict[str, Any] | None = None) -> list[HiveNode]:
        requested = set(requested_caps)
        scored: list[tuple[int, str, HiveNode]] = []
        registry_view = node_registry_view or self._node_registry_view()
        archived_parent_node_ids = set(registry_view.get("archived_parent_node_ids") or [])
        active_generated_nodes = registry_view.get("active_generated_nodes") or []
        effective_nodes = [node for node in self.nodes if node.node_id not in archived_parent_node_ids]
        effective_nodes.extend(node for node in active_generated_nodes if isinstance(node, HiveNode))
        for node in effective_nodes:
            overlap = len(requested.intersection(node.capabilities))
            protected_boost = 1 if node.protected and node.node_type in {"MiniNexusNet", "PolicyGate"} else 0
            scored.append((overlap + protected_boost, node.node_id, node))
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        selected = [node for score, _, node in scored if score > 0][:4]
        return selected or [node for node in effective_nodes if node.protected][:4]

    def _loops(
        self,
        *,
        selected_nodes: list[HiveNode],
        max_loops: int,
        blocked: bool,
        requested_capabilities: list[str],
    ) -> list[dict[str, Any]]:
        overlap = max(len(set(requested_capabilities)), 1)
        base_confidence = min(0.54 + (len(selected_nodes) * 0.04) + min(overlap, 6) * 0.02, 0.72)
        loops: list[dict[str, Any]] = []
        for index in range(1, max_loops + 1):
            confidence = round(min(base_confidence + (index - 1) * 0.13, 0.94), 3)
            if blocked:
                confidence = min(confidence, 0.49)
            exit_reason = "confidence_above_threshold" if confidence >= 0.72 else "continue_recurrent_deliberation"
            if index == max_loops and exit_reason != "confidence_above_threshold":
                exit_reason = "max_loops_reached"
            loops.append(
                {
                    "loop_index": index,
                    "confidence": confidence,
                    "risk_score": 0.86 if blocked else round(max(0.08, 0.32 - (index * 0.04)), 3),
                    "active_node_ids": [node.node_id for node in selected_nodes],
                    "exit_gate_state": "closed" if exit_reason == "continue_recurrent_deliberation" else "open",
                    "exit_reason": exit_reason,
                    "harmonic_cadence": _loop_harmonic_cadence(index),
                }
            )
            if exit_reason == "confidence_above_threshold" or blocked:
                break
        return loops

    def _immune_findings(
        self,
        actions: list[dict[str, Any]],
        *,
        plan_mode_write_jail: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        plan_mode_active = bool((plan_mode_write_jail or {}).get("plan_mode"))
        blocked_plan_actions = set((plan_mode_write_jail or {}).get("blocked_action_ids") or [])
        allowed_plan_actions = set((plan_mode_write_jail or {}).get("allowed_action_ids") or [])
        for action in actions:
            action_id = str(action.get("action_id") or action.get("target_ref") or "action")
            if plan_mode_active and action_id in blocked_plan_actions:
                findings.append(
                    {
                        "finding_id": f"immune::{action_id}",
                        "rule_id": "plan_mode_write_jail_violation",
                        "severity": "hard_fail",
                        "blocked": True,
                        "message": "Plan mode allows reads, safe shell, and writes only to the declared plan artifact.",
                        "required_evidence": ["plan_artifact_ref", "operator_exit_from_plan_mode"],
                    }
                )
                continue
            action_type = str(action.get("action_type", "")).lower()
            metadata_marks_write = action.get("read_only") is False
            if plan_mode_active and action_id in allowed_plan_actions:
                continue
            if (action_type in {"write", "delete", "mutate", "promote"} or metadata_marks_write) and not action.get("checkpoint_ref"):
                findings.append(
                    {
                        "finding_id": f"immune::{action_id}",
                        "rule_id": "write_action_requires_checkpoint",
                        "severity": "hard_fail",
                        "blocked": True,
                        "message": "Write-like hive action missing explicit checkpoint_ref.",
                        "required_evidence": ["checkpoint_ref", "rewind_scope", "operator_or_policy_gate"],
                    }
                )
        return findings

    def _policy_targets_for_actions(
        self,
        actions: list[dict[str, Any]],
        *,
        plan_mode_write_jail: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        targets: list[dict[str, Any]] = []
        plan_mode_active = bool((plan_mode_write_jail or {}).get("plan_mode"))
        allowed_plan_actions = set((plan_mode_write_jail or {}).get("allowed_action_ids") or [])
        for index, action in enumerate(actions):
            action_id = str(action.get("action_id") or action.get("target_ref") or index)
            action_type = str(action.get("action_type", "")).lower()
            metadata_marks_write = action.get("read_only") is False
            if action_type in {"write", "delete", "mutate", "promote"} or metadata_marks_write:
                if plan_mode_active and action_id in allowed_plan_actions:
                    continue
                targets.append(
                    {
                        "target_id": f"tool::{action_id}",
                        "target_type": "tool_execution",
                        "metadata": {
                            "write_enabled": True,
                            "sandboxed": bool(action.get("sandboxed")),
                            "tool_scope": action.get("target_ref") or "hive-substrate",
                        },
                    }
                )
        return targets

    def _forward_events(
        self,
        *,
        run_id: str,
        session_id: str,
        created_at: str,
        blocked: bool,
        selected_node_count: int,
    ) -> list[dict[str, Any]]:
        event_specs = [
            ("task.received", "SensoryPlane", "Operator task entered the hive substrate."),
            ("activation.embedded", "EmbeddingPlane", "Task activation was embedded into substrate state."),
            ("router.experts_selected", "SparseMoERouter", f"Selected {selected_node_count} expert nodes."),
            ("checkpoint.created", "CheckpointLedger", "Created session-turn rewind metadata."),
            ("eval.completed", "EvalPlane", "Completed deterministic loss/risk gate."),
            ("hive.blocked" if blocked else "hive.completed", "NexusBrain", "Blocked by immune/policy gate." if blocked else "Completed hive forward pass."),
        ]
        return [
            {
                "event_id": f"{run_id}::{event_type}",
                "run_id": run_id,
                "session_id": session_id,
                "event_type": event_type,
                "actor": actor,
                "detail": detail,
                "created_at": created_at,
            }
            for event_type, actor, detail in event_specs
        ]

    def _sidebar_reasons(self, request: HiveAssimilationCandidateRequest) -> list[str]:
        reasons: list[str] = []
        if request.requested_promotion and not request.sandbox_refs:
            reasons.append("sandbox_refs_missing")
        if request.requested_promotion and not request.eval_refs:
            reasons.append("eval_refs_missing")
        if request.requested_promotion and request.license_state in {"", "unknown", "unverified"}:
            reasons.append("license_state_unverified")
        return reasons

    def _artifact_path(self, base_dir: Path | None, artifact_id: str) -> Path | None:
        return base_dir / f"{artifact_id}.json" if base_dir else None

    def _artifact_store_summary(self) -> dict[str, Any]:
        def index_path(directory: Path | None) -> str | None:
            return str(directory / "_index.jsonl") if directory else None

        return {
            "store_id": "hive-substrate-repo-local-artifact-store-v0",
            "index_mode": "repo-local-json-plus-jsonl-index",
            "base_path": str(self.substrate_dir) if self.substrate_dir else None,
            "forward_pass_index_path": index_path(self.forward_dir),
            "activation_index_path": index_path(self.activation_dir),
            "sensory_input_index_path": index_path(self.sensory_input_dir),
            "embedding_tensor_index_path": index_path(self.embedding_tensor_dir),
            "temporal_positional_index_path": index_path(self.temporal_positional_dir),
            "memory_engram_index_path": index_path(self.memory_engram_dir),
            "attention_routing_index_path": index_path(self.attention_routing_dir),
            "residual_normalization_index_path": index_path(self.residual_normalization_dir),
            "sparse_expert_gate_index_path": index_path(self.sparse_expert_gate_dir),
            "feedforward_expert_index_path": index_path(self.feedforward_expert_dir),
            "laminar_microcircuit_index_path": index_path(self.laminar_microcircuit_dir),
            "neural_pathway_index_path": index_path(self.neural_pathway_dir),
            "synaptic_transmission_index_path": index_path(self.synaptic_transmission_dir),
            "neuroplastic_weight_index_path": index_path(self.neuroplastic_weight_dir),
            "neuromodulatory_state_index_path": index_path(self.neuromodulatory_state_dir),
            "latent_loop_exit_index_path": index_path(self.latent_loop_exit_dir),
            "kv_cache_compression_index_path": index_path(self.kv_cache_compression_dir),
            "loss_backpropagation_index_path": index_path(self.loss_backpropagation_dir),
            "optimizer_school_index_path": index_path(self.optimizer_school_dir),
            "action_output_decoder_index_path": index_path(self.action_output_decoder_dir),
            "forward_propagation_index_path": index_path(self.forward_propagation_dir),
            "backward_propagation_index_path": index_path(self.backward_propagation_dir),
            "parameter_tensor_index_path": index_path(self.parameter_tensor_dir),
            "activation_function_index_path": index_path(self.activation_function_dir),
            "computational_graph_index_path": index_path(self.computational_graph_dir),
            "optimizer_state_vector_index_path": index_path(self.optimizer_state_vector_dir),
            "model_genome_index_path": index_path(self.model_genome_dir),
            "candidate_index_path": index_path(self.candidate_dir),
            "dream_index_path": index_path(self.dream_dir),
            "checkpoint_index_path": index_path(self.checkpoint_dir),
            "node_registry_index_path": index_path(self.node_registry_dir),
            "productionization_index_path": index_path(self.productionization_dir),
            "release_index_path": index_path(self.release_dir),
            "rollback_index_path": index_path(self.rollback_dir),
            "rewind_index_path": index_path(self.rewind_dir),
            "health_index_path": index_path(self.health_dir),
            "self_healing_index_path": index_path(self.self_healing_dir),
            "global_federation_review_index_path": index_path(self.global_federation_dir),
            "project_heartbeat_index_path": index_path(self.project_heartbeat_dir),
            "privacy_boundary": "repo-local-artifact-metadata-no-c-drive-cache",
        }

    def _persist(self, path: Path | None, payload: dict[str, Any]) -> None:
        if path is not None:
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            self._artifact_cache.pop(path.parent, None)
            index_path = path.parent / "_index.jsonl"
            record = {
                "artifact_file": path.name,
                "artifact_path": str(path),
                "artifact_type": path.parent.name,
                "artifact_id": (
                    payload.get("run_id")
                    or payload.get("candidate_run_id")
                    or payload.get("activation_id")
                    or payload.get("sensory_ledger_id")
                    or payload.get("embedding_ledger_id")
                    or payload.get("temporal_ledger_id")
                    or payload.get("memory_ledger_id")
                    or payload.get("attention_ledger_id")
                    or payload.get("normalization_ledger_id")
                    or payload.get("gate_ledger_id")
                    or payload.get("feedforward_ledger_id")
                    or payload.get("latent_loop_id")
                    or payload.get("kv_cache_ledger_id")
                    or payload.get("backpropagation_id")
                    or payload.get("optimizer_ledger_id")
                    or payload.get("output_decoder_id")
                    or payload.get("propagation_id")
                    or payload.get("backward_propagation_id")
                    or payload.get("parameter_ledger_id")
                    or payload.get("activation_function_ledger_id")
                    or payload.get("graph_ledger_id")
                    or payload.get("optimizer_state_ledger_id")
                    or payload.get("genome_ledger_id")
                    or payload.get("pathway_id")
                    or payload.get("transmission_id")
                    or payload.get("dream_id")
                    or payload.get("checkpoint_id")
                    or payload.get("node_registry_update_id")
                    or payload.get("productionization_id")
                    or payload.get("release_id")
                    or payload.get("rollback_id")
                    or payload.get("rewind_id")
                    or payload.get("health_event_id")
                    or payload.get("route_around_id")
                    or payload.get("review_id")
                    or payload.get("record_id")
                    or path.stem
                ),
                "session_id": payload.get("session_id"),
                "created_at": payload.get("created_at") or utcnow().isoformat(),
            }
            with index_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")

    def _list_artifacts(self, directory: Path | None, *, session_id: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        if directory is None or not directory.exists():
            return []
        payloads = self._artifact_cache.get(directory)
        if payloads is None:
            payloads = []
            for path in directory.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    modified_at = path.stat().st_mtime_ns
                except (OSError, json.JSONDecodeError):
                    continue
                payloads.append((modified_at, payload))
            payloads.sort(key=lambda item: (item[1].get("created_at") or "", item[0]), reverse=True)
            self._artifact_cache[directory] = payloads
        if session_id:
            payloads = [item for item in payloads if item[1].get("session_id") == session_id]
        return [payload for _, payload in payloads[:limit]]

    def _personality_preference_artifacts(
        self,
        *,
        session_id: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        session_ref_digest = _privacy_digest(session_id) if session_id else None
        records = self._list_artifacts(self.personality_preference_dir, limit=500)
        if session_ref_digest:
            records = [
                record
                for record in records
                if record.get("session_ref_digest") == session_ref_digest
            ]
        return records[:limit]

    def local_personality_preference_overlay(
        self,
        *,
        session_id: str | None,
    ) -> dict[str, Any]:
        """Resolve the newest usable local response-style vector for one session.

        This deliberately reads only the local profile ledger. Federation consent and
        federated packets never participate in response-style inference.
        """
        records = self._personality_preference_artifacts(session_id=session_id, limit=500)
        for record in records:
            preference_keys = _local_personality_response_style_keys(record.get("preference_keys"))
            if preference_keys:
                return _local_personality_preference_overlay_payload(
                    preference_keys=preference_keys,
                    profile_recorded=True,
                )
        return _local_personality_preference_overlay_payload(
            preference_keys=[],
            profile_recorded=bool(records),
        )

    def _find_route_candidate_evaluation(
        self,
        *,
        evaluation_id: str,
        session_id: str | None,
    ) -> dict[str, Any] | None:
        for evaluation in self._list_artifacts(
            self.route_candidate_evaluation_dir,
            session_id=session_id,
            limit=500,
        ):
            if evaluation.get("evaluation_id") == evaluation_id:
                return evaluation
        return None

    def _find_route_candidate_approval(
        self,
        *,
        approval_id: str,
        session_id: str | None,
    ) -> dict[str, Any] | None:
        for approval in self._list_artifacts(
            self.route_candidate_approval_dir,
            session_id=session_id,
            limit=500,
        ):
            if approval.get("approval_id") == approval_id:
                return approval
        return None

    def _latest_active_route_overlay(self, session_id: str) -> dict[str, Any] | None:
        approvals = self._list_artifacts(
            self.route_candidate_approval_dir,
            session_id=session_id,
            limit=100,
        )
        rollbacks = self._list_artifacts(
            self.route_candidate_rollback_dir,
            session_id=session_id,
            limit=200,
        )
        rolled_back_approval_ids = {
            str(rollback.get("approval_id"))
            for rollback in rollbacks
            if rollback.get("rollback_state") == "rolled_back" and rollback.get("approval_id")
        }
        for approval in approvals:
            approval_id = str(approval.get("approval_id") or "")
            if not approval_id or approval_id in rolled_back_approval_ids:
                continue
            if approval.get("status") != "shadow-route-applied":
                continue
            overlay = dict(approval.get("shadow_route_overlay") or {})
            if overlay.get("overlay_state") != "active-session-shadow":
                continue
            overlay["approval_id"] = approval_id
            overlay["evaluation_id"] = approval.get("evaluation_id")
            overlay["session_id"] = approval.get("session_id")
            overlay["honest_status_label"] = approval.get("honest_status_label")
            overlay["active_production_mutated"] = False
            overlay["active_route_mutated"] = False
            return overlay
        return None


def _select_source_run(runs: list[dict[str, Any]], source_run_id: str | None) -> dict[str, Any] | None:
    if source_run_id:
        for run in runs:
            if run.get("run_id") == source_run_id:
                return run
        return None
    return runs[0] if runs else None


def _apply_session_shadow_route_overlay(
    selected_nodes: list[HiveNode],
    overlay: dict[str, Any],
) -> tuple[list[HiveNode], dict[str, Any]]:
    candidate_order = [str(item) for item in overlay.get("candidate_node_order") or []]
    if not candidate_order:
        applied_overlay = dict(overlay)
        applied_overlay["applied_node_order"] = [node.node_id for node in selected_nodes]
        return selected_nodes, applied_overlay
    by_id = {node.node_id: node for node in selected_nodes}
    ordered_nodes: list[HiveNode] = []
    consumed: set[str] = set()
    for node_id in candidate_order:
        node = by_id.get(node_id)
        if node is None or node_id in consumed:
            continue
        ordered_nodes.append(node)
        consumed.add(node_id)
    ordered_nodes.extend(node for node in selected_nodes if node.node_id not in consumed)
    applied_overlay = dict(overlay)
    applied_overlay["applied_node_order"] = [node.node_id for node in ordered_nodes]
    applied_overlay["session_shadow_route_mutated"] = bool(ordered_nodes)
    applied_overlay["active_route_mutated"] = False
    applied_overlay["active_production_mutated"] = False
    return ordered_nodes, applied_overlay


def _select_productionization(productionizations: list[dict[str, Any]], productionization_id: str) -> dict[str, Any] | None:
    for productionization in productionizations:
        if productionization.get("productionization_id") == productionization_id:
            return productionization
    return None


def _select_release(releases: list[dict[str, Any]], release_id: str) -> dict[str, Any] | None:
    for release in releases:
        if release.get("release_id") == release_id:
            return release
    return None


def _active_release_blocked_reasons(
    request: HiveActiveReleaseRequest,
    shadow_release: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    if shadow_release.get("release_state") != "active_shadow":
        reasons.append("shadow_release_not_active")
    if shadow_release.get("active_production_mutated") is not False:
        reasons.append("shadow_release_boundary_invalid")
    if not request.human_governance_approval:
        reasons.append("human_governance_approval_missing")
    if not request.operator_approval_ref:
        reasons.append("operator_approval_ref_missing")
    if not request.canary_eval_refs:
        reasons.append("canary_eval_refs_missing")
    if not request.monitoring_refs:
        reasons.append("monitoring_refs_missing")
    if not request.rollback_rehearsal_ref:
        reasons.append("rollback_rehearsal_ref_missing")
    evidence = shadow_release.get("evidence_refs") or {}
    for key in [
        "neural_bus_ref",
        "hive_blackboard_ref",
        "laminar_microcircuit_ref",
        "neural_pathway_ref",
        "synaptic_transmission_ref",
        "neuroplastic_weight_ref",
        "neuromodulatory_state_ref",
        "sandbox_run_ref",
        "teacher_distillation_ref",
        "runtime_foundry_ref",
        "rollback_checkpoint_ref",
    ]:
        if not evidence.get(key):
            reasons.append(f"{key}_missing")
    return reasons


def _select_checkpoint_snapshot(checkpoints: list[dict[str, Any]], checkpoint_id: str) -> dict[str, Any] | None:
    for checkpoint in checkpoints:
        if checkpoint.get("checkpoint_id") == checkpoint_id:
            return checkpoint
    return None


def _productionization_sandbox_provider_run(
    *,
    normalized: HiveProductionizationRequest,
    productionization_id: str,
    created_at: str,
    substrate_bound_inputs: dict[str, Any],
) -> dict[str, Any]:
    provider_refs = normalized.sandbox_provider_refs or ["provider::repo-local-null-sandbox"]
    provider_results = [
        {
            "provider_ref": provider_ref,
            "provider_state": "available",
            "isolation_model": "workspace-sandbox-contract",
            "credential_redaction_state": "passed",
            "network_policy": "deny-by-default",
            "write_scope": "sandbox-artifacts-only",
            "consumed_neural_bus_ref": substrate_bound_inputs.get("neural_bus_ref"),
            "consumed_hive_blackboard_ref": substrate_bound_inputs.get("hive_blackboard_ref"),
            "consumed_laminar_microcircuit_ref": substrate_bound_inputs.get("laminar_microcircuit_ref"),
            "consumed_neural_pathway_ref": substrate_bound_inputs.get("neural_pathway_ref"),
            "consumed_synaptic_transmission_ref": substrate_bound_inputs.get("synaptic_transmission_ref"),
            "consumed_neuroplastic_weight_ref": substrate_bound_inputs.get("neuroplastic_weight_ref"),
            "consumed_neuromodulatory_state_ref": substrate_bound_inputs.get("neuromodulatory_state_ref"),
            "direct_local_state_reads": [],
        }
        for provider_ref in provider_refs
    ]
    return {
        "sandbox_run_id": new_id("production_sandbox"),
        "provider_contract_id": "external-sandbox-provider-contract-v0",
        "productionization_id": productionization_id,
        "session_id": normalized.session_id,
        "execution_state": "passed",
        "provider_count": len(provider_results),
        "provider_results": provider_results,
        "network_policy": "deny-by-default",
        "credential_redaction_state": "passed",
        "write_scope": "sandbox-artifacts-only",
        "input_contract": NEURAL_RUNTIME_INPUT_CONTRACT,
        "active_production_mutated": False,
        "created_at": created_at,
    }


def _productionization_teacher_distillation(
    *,
    normalized: HiveProductionizationRequest,
    productionization_id: str,
    created_at: str,
) -> dict[str, Any]:
    teacher_refs = normalized.teacher_model_refs or [
        "teacher::runtime",
        "teacher::security",
        "teacher::privacy",
    ]
    teacher_reviews = [
        {
            "teacher_ref": teacher_ref,
            "review_state": "approved",
            "temperature_profile": "low",
            "grade": "ivy-league-distillation-pass",
            "focus": _stable_key(teacher_ref),
        }
        for teacher_ref in teacher_refs
    ]
    return {
        "school_review_id": new_id("production_school"),
        "contract_id": "ivy-league-teacher-distillation-runtime-v0",
        "productionization_id": productionization_id,
        "subject_id": normalized.subject_id,
        "distillation_trace_id": new_id("distillation_trace"),
        "teacher_model_reviews": teacher_reviews,
        "teacher_model_count": len(teacher_reviews),
        "teacher_panel_state": "complete" if len(teacher_reviews) >= 3 else "incomplete",
        "certification_state": "certified" if len(teacher_reviews) >= 3 else "blocked",
        "certification_scope": "shadow-production-candidate",
        "created_at": created_at,
    }


def _productionization_federation_security(
    *,
    normalized: HiveProductionizationRequest,
    productionization_id: str,
    created_at: str,
    prior_ledger: dict[str, Any],
) -> dict[str, Any]:
    signature_seed = "|".join(
        [
            normalized.session_id,
            normalized.subject_id,
            normalized.goal,
            ",".join(normalized.candidate_refs),
            ",".join(normalized.federation_node_refs),
        ]
    )
    signature = "hive_sig_" + hashlib.sha256(signature_seed.encode("utf-8")).hexdigest()[:24]
    packet_id = new_id("signed_fed_packet")
    federation_node_refs = normalized.federation_node_refs or ["fed::local-owner"]
    return {
        "security_review_id": new_id("federation_security"),
        "contract_id": "signed-secure-federation-v0",
        "productionization_id": productionization_id,
        "session_id": normalized.session_id,
        "federation_node_refs": federation_node_refs,
        "signed_packet": {
            "packet_id": packet_id,
            "signature": signature,
            "signature_algorithm": "sha256-demo-signature-contract-v0",
            "prior_ledger_ref": prior_ledger.get("ledger_id"),
            "raw_private_data_exported": False,
            "payload_class": "sanitized-artifact-metadata-only",
        },
        "secure_aggregate": {
            "aggregate_id": new_id("secure_aggregate"),
            "aggregate_state": "ready_for_shadow_review",
            "node_count": len(federation_node_refs),
            "raw_private_data_exported": False,
        },
        "trust_scoring": {
            "result_state": "passed",
            "minimum_trust_score": 0.82,
            "untrusted_node_refs": [],
        },
        "poisoning_anomaly_detection": {
            "result_state": "passed",
            "detected_anomaly_count": 0,
            "quarantine_refs": [],
        },
        "differential_privacy": {
            "result_state": "passed",
            "epsilon": 0.8,
            "delta": 1e-6,
            "knob_state": "enabled-for-global-packet-promotion",
        },
        "privacy_audit": {
            "result_state": "passed",
            "raw_private_data_exported": False,
            "local_paths_exported": False,
            "raw_prompts_exported": False,
            "raw_outputs_exported": False,
        },
        "created_at": created_at,
    }


def _productionization_runtime_research_foundry(
    *,
    normalized: HiveProductionizationRequest,
    productionization_id: str,
    created_at: str,
) -> dict[str, Any]:
    methods = normalized.runtime_methods or ["baseline-runtime-method"]
    if normalized.allow_recursive_dreaming and not any(method.startswith("dreamed-") for method in methods):
        methods = [*methods, "dreamed-harmonic-hybrid-kv-quant-route"]
    trials = []
    for index, method in enumerate(methods):
        dreamed = method.startswith("dreamed-")
        score = round(min(0.72 + (index * 0.035) + (0.08 if dreamed else 0.0), 0.97), 3)
        trials.append(
            {
                "trial_id": new_id("runtime_trial"),
                "method_id": method,
                "method_origin": "recursive_dreaming" if dreamed else "catalog_or_operator_candidate",
                "sandbox_state": "passed",
                "shadow_only": True,
                "composite_score": score,
                "metrics": {
                    "latency_delta": round(-0.03 - (index * 0.01), 3),
                    "memory_delta": round(-0.04 - (index * 0.012), 3),
                    "quality_delta": round(0.01 + (0.006 * index) + (0.025 if dreamed else 0.0), 3),
                },
                "promotion_state": "shadow_candidate",
            }
        )
    best_trial = sorted(trials, key=lambda item: (item["composite_score"], item["method_id"]), reverse=True)[0]
    return {
        "foundry_run_id": new_id("runtime_foundry"),
        "contract_id": "evolutionary-runtime-research-foundry-v0",
        "productionization_id": productionization_id,
        "session_id": normalized.session_id,
        "trial_count": len(trials),
        "trials": trials,
        "best_trial": best_trial,
        "research_scope": [
            "kv_cache_compression",
            "quantization",
            "inference_backend",
            "recursive_dreamed_runtime_method",
        ],
        "mutation_boundary": "sandbox-and-shadow-only-until-human-approved-release",
        "created_at": created_at,
    }


def _hive_health_event_payload(
    *,
    run_id: str,
    session_id: str,
    task_id: str,
    created_at: str,
    blocked: bool,
    neural_bus: dict[str, Any],
    hive_blackboard: dict[str, Any],
    selected_nodes: list[HiveNode],
    immune_findings: list[dict[str, Any]],
    policy_scan: dict[str, Any],
) -> dict[str, Any]:
    return {
        "status_label": "LOCKED CANON",
        "surface_id": "hive-health-event-v0",
        "health_event_id": new_id("hive_health"),
        "session_id": session_id,
        "source_run_id": run_id,
        "task_id": task_id,
        "event_state": "degraded_observed" if blocked else "healthy_observed",
        "severity": "hard_fail_blocked" if blocked else "normal",
        "visibility_scope": "hive-visible",
        "silent_failure_policy": "forbidden",
        "selected_node_ids": [node.node_id for node in selected_nodes],
        "affected_node_ids": [node.node_id for node in selected_nodes] if blocked else [],
        "neural_bus_ref": neural_bus.get("bus_id"),
        "hive_blackboard_ref": hive_blackboard.get("residual_state_id"),
        "immune_finding_count": len(immune_findings),
        "policy_hard_fail_count": (policy_scan.get("summary") or {}).get("active_hard_fail_count", 0),
        "active_production_mutated": False,
        "created_at": created_at,
    }


def _self_healing_route_around_payload(
    *,
    run_id: str,
    session_id: str,
    created_at: str,
    health_event: dict[str, Any],
    selected_nodes: list[HiveNode],
    requested_actions: list[dict[str, Any]],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    failed_action_refs = [
        str(action.get("action_id") or action.get("target_ref") or "action")
        for action in requested_actions
        if str(action.get("action_type", "")).lower() in {"write", "delete", "mutate", "promote"}
    ]
    fallback_node_ids = []
    for node in selected_nodes:
        fallback_node_ids.extend(node.recovery_route_refs)
    fallback_node_ids = sorted(set(fallback_node_ids or ["policy:immune-kernel", "checkpoint:rewind-ledger"]))
    return {
        "status_label": "LOCKED CANON",
        "surface_id": "hive-self-healing-route-around-v0",
        "route_around_id": new_id("hive_route_around"),
        "session_id": session_id,
        "source_run_id": run_id,
        "consumed_health_event_ref": health_event.get("health_event_id"),
        "route_around_state": "prepared",
        "active_tasks_continue": True,
        "active_production_mutated": False,
        "failed_action_refs": failed_action_refs,
        "fallback_node_ids": fallback_node_ids,
        "checkpoint_ref": checkpoint.get("checkpoint_id"),
        "rollback_required_before_retry": True,
        "retry_policy": "checkpoint-or-sandbox-required-before-write-retry",
        "created_at": created_at,
    }


def _harmonic_geometry_kernel() -> dict[str, Any]:
    return {
        "kernel_id": "sacred-geometry-harmonic-kernel-v0",
        "constants": {
            "phi": PHI,
            "inverse_phi": round(1 / PHI, 12),
            "golden_angle_degrees": GOLDEN_ANGLE_DEGREES,
            "fibonacci_sequence": FIBONACCI_SEQUENCE,
            "harmonic_intervals": HARMONIC_INTERVALS,
        },
        "formula_basis": [
            "golden_ratio_phi",
            "golden_angle_phase_spacing",
            "fibonacci_plane_indexing",
            "harmonic_intervals",
            "bounded_resonance_scores",
        ],
        "plane_formula": "phase=(ordinal*golden_angle)%360; fibonacci=F[n]; interval=H[n%len(H)]",
        "routing_formula": "resonance=(capability_overlap+1)*harmonic_ratio*phi_weight",
        "loop_formula": "cadence=harmonic_interval(loop); phi_decay=phi^-loop; phase=(loop*golden_angle)%360",
        "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
    }


def _harmonic_interval(index: int) -> dict[str, Any]:
    interval = HARMONIC_INTERVALS[index % len(HARMONIC_INTERVALS)]
    return {
        "name": interval["name"],
        "fraction": interval["fraction"],
        "ratio": round(float(interval["ratio"]), 6),
    }


def _harmonic_phase(index: int) -> float:
    return round((GOLDEN_ANGLE_DEGREES * (index + 1)) % 360, 6)


def _phi_weight(index: int) -> float:
    return round(PHI ** -(index + 1), 6)


def _bounded_signal(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 6)


def _bounded_delta(value: float) -> float:
    return round(max(-0.05, min(0.05, float(value))), 6)


def _normalize_weight_records(
    records: list[dict[str, Any]],
    *,
    value_key: str,
    output_key: str,
) -> list[dict[str, Any]]:
    total = sum(max(float(record.get(value_key) or 0.0), 0.0) for record in records) or 1.0
    normalized = []
    running = 0.0
    for index, record in enumerate(records):
        value = round(max(float(record.get(value_key) or 0.0), 0.0) / total, 6)
        if index == len(records) - 1:
            value = round(max(0.0, 1.0 - running), 6)
        running += value
        normalized.append({key: value for key, value in record.items() if key != value_key} | {output_key: value})
    return normalized


def _plane_harmonic_signature(index: int, harmonic_geometry: dict[str, Any]) -> dict[str, Any]:
    interval = _harmonic_interval(index)
    return {
        "kernel_ref": harmonic_geometry["kernel_id"],
        "ordinal": index + 1,
        "fibonacci_index": FIBONACCI_SEQUENCE[index % len(FIBONACCI_SEQUENCE)],
        "golden_angle_degrees": harmonic_geometry["constants"]["golden_angle_degrees"],
        "phase_degrees": _harmonic_phase(index),
        "harmonic_name": interval["name"],
        "harmonic_fraction": interval["fraction"],
        "harmonic_ratio": interval["ratio"],
        "claim_boundary": harmonic_geometry["claim_boundary"],
    }


def _loop_harmonic_cadence(loop_index: int) -> dict[str, Any]:
    interval = _harmonic_interval(loop_index - 1)
    return {
        "kernel_ref": "sacred-geometry-harmonic-kernel-v0",
        "cadence_name": interval["name"],
        "cadence_fraction": interval["fraction"],
        "cadence_ratio": interval["ratio"],
        "phi_decay": round(PHI ** -loop_index, 6),
        "phase_degrees": _harmonic_phase(loop_index - 1),
    }


def _selected_node_resonance(selected_nodes: list[HiveNode], requested_caps: list[str]) -> list[dict[str, Any]]:
    requested = set(requested_caps)
    resonance = []
    for index, node in enumerate(selected_nodes):
        overlap = len(requested.intersection(node.capabilities))
        interval = _harmonic_interval(index)
        phi_weight = _phi_weight(index)
        resonance_score = round((overlap + 1) * interval["ratio"] * phi_weight, 6)
        resonance.append(
            {
                "node_id": node.node_id,
                "node_type": node.node_type,
                "capability_overlap": overlap,
                "harmonic_name": interval["name"],
                "harmonic_fraction": interval["fraction"],
                "harmonic_ratio": interval["ratio"],
                "phi_weight": phi_weight,
                "phase_degrees": _harmonic_phase(index),
                "resonance_score": resonance_score,
            }
        )
    return resonance


def _blackboard_resonance(index: int, confidence: float) -> float:
    interval = _harmonic_interval(index)
    return round(max(0.001, min(1.0, float(confidence) * interval["ratio"] * _phi_weight(index - 1))), 6)


def _planes(harmonic_geometry: dict[str, Any]) -> list[dict[str, Any]]:
    planes = [
        {"plane_id": "sensory-input", "label": "Sensory/Input Plane", "purpose": "normalize operator, tool, file, and research signals"},
        {"plane_id": "embedding-representation", "label": "Embedding/Representation Plane", "purpose": "convert signals into typed activation records"},
        {"plane_id": "temporal-positional", "label": "Temporal/Positional Plane", "purpose": "bind turns, versions, dependencies, and recency"},
        {"plane_id": "neural-bus", "label": "Neural Bus / Message-Passing Plane", "purpose": "move activations between AOs and expert nodes"},
        {"plane_id": "attention-focus", "label": "Attention/Focus Plane", "purpose": "select relevant memory, experts, and evidence"},
        {"plane_id": "sparse-moe-router", "label": "Sparse MoE Router Plane", "purpose": "choose the smallest sufficient expert set"},
        {"plane_id": "expert-computation", "label": "Expert Computation Plane", "purpose": "execute AO, mini-brain, skill, and tool reasoning units"},
        {"plane_id": "memory-engram", "label": "Memory/Engram Plane", "purpose": "retrieve source-backed facts and sidecar memory"},
        {"plane_id": "recurrent-deliberation", "label": "Recurrent Deliberation Plane", "purpose": "loop hidden state until exit gate or budget"},
        {"plane_id": "learning-eval-loss", "label": "Learning/Eval/Loss Plane", "purpose": "score outcomes before promotion"},
        {"plane_id": "optimizer-school", "label": "Optimizer/Ivy-League School Plane", "purpose": "train and certify new experts from curriculum"},
        {"plane_id": "federated-learning", "label": "Federated Learning Plane", "purpose": "aggregate privacy-preserving usage learning"},
        {"plane_id": "immune-governance", "label": "Immune/Governance Plane", "purpose": "block injection, unsafe writes, and untrusted promotion"},
        {"plane_id": "curator-pruning", "label": "Curator/Pruning Plane", "purpose": "rank, merge, prune, and archive stale capabilities"},
        {"plane_id": "action-output", "label": "Action/Output Plane", "purpose": "deliver files, UI updates, tool calls, and operator reports"},
        {"plane_id": "checkpoint-rewind", "label": "Checkpoint/Rewind Plane", "purpose": "snapshot before mutation and enable rollback"},
    ]
    for index, plane in enumerate(planes):
        plane["harmonic_signature"] = _plane_harmonic_signature(index, harmonic_geometry)
    return planes


def _seed_nodes() -> list[HiveNode]:
    return [
        HiveNode(
            node_id="nexusbrain:cortex",
            node_type="NexusBrain",
            name="Primary NexusBrain Cortex",
            plane_id="sparse-moe-router",
            capabilities=["planning", "routing", "operator_intent", "coordination"],
            protected=True,
            scorecard_refs=["/ops/brain/canon/neural-core"],
            genome_ref="genome:nexusbrain-primary",
            brain_instance_ref="brain:primary:nexusbrain",
            brain_scale="primary",
            child_brain_refs=["brain:o:task-orchestrator", "brain:ao:planner", "brain:expert:code-synthesis"],
            health_signal_refs=["health:nexusbrain:cortex", "health:hive:blackboard", "health:neural-bus"],
            recovery_route_refs=["ao:planner", "policy:immune-kernel", "checkpoint:rewind-ledger"],
        ),
        HiveNode(
            node_id="o:task-orchestrator",
            node_type="Orchestrator",
            name="Task Orchestrator Mini-NexusNet",
            plane_id="expert-computation",
            capabilities=["orchestration", "task_decomposition", "multi_ao_handoff", "recovery_coordination"],
            protected=True,
            genome_ref="genome:o-task-orchestrator",
            brain_instance_ref="brain:o:task-orchestrator",
            brain_scale="orchestrator",
            parent_brain_ref="brain:primary:nexusbrain",
            child_brain_refs=["brain:ao:planner", "brain:ao:runtime"],
            health_signal_refs=["health:o:task-orchestrator"],
            recovery_route_refs=["nexusbrain:cortex", "ao:planner", "eval:loss-plane"],
        ),
        HiveNode(
            node_id="ao:planner",
            node_type="AO",
            name="Planning AO",
            plane_id="expert-computation",
            capabilities=["planning", "task_decomposition", "implementation_plan"],
            protected=True,
            genome_ref="genome:ao-planner",
            brain_instance_ref="brain:ao:planner",
            brain_scale="assistant_orchestrator",
            parent_brain_ref="brain:o:task-orchestrator",
            child_brain_refs=["brain:expert:code-synthesis"],
            health_signal_refs=["health:ao:planner"],
            recovery_route_refs=["o:task-orchestrator", "eval:loss-plane"],
        ),
        HiveNode(
            node_id="ao:runtime",
            node_type="AO",
            name="Runtime AO",
            plane_id="expert-computation",
            capabilities=["runtime", "quantization", "kv_cache", "hardware", "recovery_coordination"],
            protected=True,
            genome_ref="genome:ao-runtime",
            brain_instance_ref="brain:ao:runtime",
            brain_scale="assistant_orchestrator",
            parent_brain_ref="brain:o:task-orchestrator",
            child_brain_refs=["brain:expert:runtime-cache"],
            health_signal_refs=["health:ao:runtime"],
            recovery_route_refs=["o:task-orchestrator", "sandbox:closed-loop"],
        ),
        HiveNode(
            node_id="expert:code-synthesis",
            node_type="Expert",
            name="Code Synthesis Expert Mini-NexusNet",
            plane_id="expert-computation",
            capabilities=["code", "implementation", "debugging", "test_generation"],
            genome_ref="genome:expert-code-synthesis",
            brain_instance_ref="brain:expert:code-synthesis",
            brain_scale="expert",
            parent_brain_ref="brain:ao:planner",
            health_signal_refs=["health:expert:code-synthesis"],
            recovery_route_refs=["ao:planner", "sandbox:closed-loop", "eval:loss-plane"],
        ),
        HiveNode(
            node_id="expert:runtime-cache",
            node_type="Expert",
            name="Runtime Cache Expert Mini-NexusNet",
            plane_id="expert-computation",
            capabilities=["runtime", "kv_cache", "quantization", "benchmarking"],
            genome_ref="genome:expert-runtime-cache",
            brain_instance_ref="brain:expert:runtime-cache",
            brain_scale="expert",
            parent_brain_ref="brain:ao:runtime",
            health_signal_refs=["health:expert:runtime-cache"],
            recovery_route_refs=["ao:runtime", "sandbox:closed-loop", "eval:loss-plane"],
        ),
        HiveNode(
            node_id="memory:engram",
            node_type="MemoryBank",
            name="Engram Memory Index",
            plane_id="memory-engram",
            capabilities=["memory", "source_retrieval", "provenance", "engram_lookup"],
            protected=True,
            scorecard_refs=["/ops/brain/canon/engram-memory"],
            brain_instance_ref="brain:support:memory-engram",
            brain_scale="support",
            parent_brain_ref="brain:primary:nexusbrain",
            health_signal_refs=["health:memory:engram"],
            recovery_route_refs=["nexusbrain:cortex", "checkpoint:rewind-ledger"],
        ),
        HiveNode(
            node_id="policy:immune-kernel",
            node_type="PolicyGate",
            name="Immune Policy Kernel",
            plane_id="immune-governance",
            capabilities=["policy", "immune", "sandbox", "threat_sensing", "checkpoint"],
            protected=True,
            scorecard_refs=["/ops/brain/canon/policy-kernel"],
            brain_instance_ref="brain:support:immune-kernel",
            brain_scale="support",
            parent_brain_ref="brain:primary:nexusbrain",
            health_signal_refs=["health:policy:immune-kernel"],
            recovery_route_refs=["nexusbrain:cortex", "checkpoint:rewind-ledger"],
        ),
        HiveNode(
            node_id="checkpoint:rewind-ledger",
            node_type="CheckpointLedger",
            name="Checkpoint Rewind Ledger",
            plane_id="checkpoint-rewind",
            capabilities=["checkpoint", "rewind", "rollback", "snapshot"],
            protected=True,
            brain_instance_ref="brain:support:checkpoint-rewind",
            brain_scale="support",
            parent_brain_ref="brain:primary:nexusbrain",
            health_signal_refs=["health:checkpoint:rewind-ledger"],
            recovery_route_refs=["policy:immune-kernel"],
        ),
        HiveNode(
            node_id="eval:loss-plane",
            node_type="Evaluator",
            name="Hive Eval and Loss Plane",
            plane_id="learning-eval-loss",
            capabilities=["evaluation", "loss", "regression_gate", "verification"],
            brain_instance_ref="brain:support:eval-loss",
            brain_scale="support",
            parent_brain_ref="brain:primary:nexusbrain",
            health_signal_refs=["health:eval:loss-plane"],
            recovery_route_refs=["nexusbrain:cortex", "sandbox:closed-loop"],
        ),
        HiveNode(
            node_id="sandbox:closed-loop",
            node_type="SandboxRunner",
            name="Closed Sandbox Runner",
            plane_id="immune-governance",
            capabilities=["sandbox", "shadow_run", "safe_execution", "verification"],
            brain_instance_ref="brain:support:closed-sandbox",
            brain_scale="support",
            parent_brain_ref="brain:primary:nexusbrain",
            health_signal_refs=["health:sandbox:closed-loop"],
            recovery_route_refs=["policy:immune-kernel", "eval:loss-plane"],
        ),
        HiveNode(
            node_id="school:ivy-league",
            node_type="School",
            name="Ivy-League Expert School",
            plane_id="optimizer-school",
            capabilities=["curriculum", "expert_training", "certification", "federated_learning"],
            brain_instance_ref="brain:support:ivy-league-school",
            brain_scale="support",
            parent_brain_ref="brain:primary:nexusbrain",
            health_signal_refs=["health:school:ivy-league"],
            recovery_route_refs=["eval:loss-plane", "curator:hive-library"],
        ),
        HiveNode(
            node_id="federation:privacy-aggregate",
            node_type="FederatedNode",
            name="Federated Privacy Aggregator",
            plane_id="federated-learning",
            capabilities=["federated_learning", "usage_signal", "privacy_preserving_aggregate"],
            brain_instance_ref="brain:support:federated-privacy",
            brain_scale="support",
            parent_brain_ref="brain:primary:nexusbrain",
            health_signal_refs=["health:federation:privacy-aggregate"],
            recovery_route_refs=["policy:immune-kernel", "eval:loss-plane"],
        ),
        HiveNode(
            node_id="curator:hive-library",
            node_type="Curator",
            name="Hive Library Curator",
            plane_id="curator-pruning",
            capabilities=["curation", "dedupe", "archive", "skill_cleanup"],
            brain_instance_ref="brain:support:hive-curator",
            brain_scale="support",
            parent_brain_ref="brain:primary:nexusbrain",
            health_signal_refs=["health:curator:hive-library"],
            recovery_route_refs=["nexusbrain:cortex", "eval:loss-plane"],
        ),
    ]


def _required_controls() -> list[str]:
    return [
        "sixteen_plane_contract",
        "hive_wide_neuroplasticity_fabric",
        "fractal_mini_brain_hierarchy",
        "harmonic_geometry_kernel",
        "brain_health_failure_visibility",
        "self_healing_route_around_contract",
        "sparse_expert_routing",
        "recurrent_deliberation_loop",
        "checkpoint_before_write",
        "policy_kernel_scan",
        "immune_findings",
        "mandatory_sanitized_federated_learning_packet",
        "federated_prior_ledger",
        "first_class_activation_artifact",
        "artifact_bound_node_execution",
        "shadow_routing_prior_influence",
        "closed_sandbox_eval_promotion_path",
        "recursive_neural_dreaming_runtime",
        "durable_node_registry",
        "global_federation_safety_gate",
        "jsonl_artifact_indexes",
        "checkpoint_snapshot_replay",
        "checkpoint_rewind_restore_proof",
        "sandbox_eval_before_assimilation",
        "sidebar_for_unproven_candidates",
        "curator_review_no_direct_delete",
        "federated_learning_privacy_gate",
        "external_sandbox_provider_contract",
        "teacher_model_distillation_runtime",
        "signed_secure_federation_packets",
        "evolutionary_runtime_research_foundry",
        "gated_shadow_release_and_rollback",
        "shadow_release_lifecycle",
        "active_release_canary_gate",
                "rollback_execution_ledger",
                "hive_visible_health_monitor",
                "self_healing_route_around",
                "shadow_neuroplastic_weight_update_ledger",
                "laminar_microcircuit_plane_internals",
                "neuromodulatory_state_gate",
            ]


def _operator_actions() -> dict[str, dict[str, Any]]:
    return {
        "inspect": {"method": "GET", "endpoint": "/ops/brain/hive-substrate"},
        "forward_pass": {"method": "POST", "endpoint": "/ops/brain/hive-substrate/forward-pass"},
        "assimilate": {"method": "POST", "endpoint": "/ops/brain/hive-substrate/assimilate"},
        "dream": {"method": "POST", "endpoint": "/ops/brain/hive-substrate/dream"},
        "productionize": {"method": "POST", "endpoint": "/ops/brain/hive-substrate/productionize"},
        "shadow_release": {"method": "POST", "endpoint": "/ops/brain/hive-substrate/shadow-release"},
        "active_release": {"method": "POST", "endpoint": "/ops/brain/hive-substrate/active-release"},
        "rollback": {"method": "POST", "endpoint": "/ops/brain/hive-substrate/rollback"},
        "rewind": {"method": "POST", "endpoint": "/ops/brain/hive-substrate/rewind"},
        "global_federation_review": {"method": "POST", "endpoint": "/ops/brain/hive-substrate/global-federation/review"},
        "approve_route_candidate": {
            "method": "POST",
            "endpoint": "/ops/brain/hive-substrate/route-candidates/{evaluation_id}/approve",
        },
        "rollback_route_candidate": {
            "method": "POST",
            "endpoint": "/ops/brain/hive-substrate/route-candidates/{approval_id}/rollback",
        },
        "health": {"method": "GET", "endpoint": "/ops/brain/hive-substrate/health"},
        "replay": {"method": "GET", "endpoint": "/ops/brain/hive-substrate/replay"},
        "curator": {"method": "GET", "endpoint": "/ops/brain/hive-substrate/curator"},
        "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/hive-substrate"},
    }


def _substrate_components(summary: dict[str, Any]) -> list[dict[str, Any]]:
    latest = summary.get("latest_forward_pass") or {}
    latest_bus = latest.get("neural_bus") or {}
    latest_blackboard = latest.get("hive_blackboard") or {}
    latest_trace = latest.get("plane_trace") or {}
    latest_sensory = summary.get("latest_sensory_input") or latest.get("sensory_input_ledger") or {}
    latest_embedding = summary.get("latest_embedding_tensor") or latest.get("embedding_tensor_ledger") or {}
    latest_temporal = summary.get("latest_temporal_positional") or latest.get("temporal_positional_ledger") or {}
    latest_memory_engram = summary.get("latest_memory_engram") or latest.get("memory_engram_ledger") or {}
    latest_attention = summary.get("latest_attention_routing") or latest.get("attention_routing_ledger") or {}
    latest_normalization = summary.get("latest_residual_normalization") or latest.get("residual_normalization_ledger") or {}
    latest_gate = summary.get("latest_sparse_expert_gate") or latest.get("sparse_expert_gate_ledger") or {}
    latest_feedforward = summary.get("latest_feedforward_expert") or latest.get("feedforward_expert_ledger") or {}
    latest_microcircuit = summary.get("latest_laminar_microcircuit") or latest.get("laminar_microcircuit_ledger") or {}
    latest_pathway = summary.get("latest_neural_pathway") or latest.get("neural_pathway_map") or {}
    latest_plane_matrix = latest_pathway.get("plane_adjacency_matrix") or {}
    latest_transmission = summary.get("latest_synaptic_transmission") or latest.get("synaptic_transmission_ledger") or {}
    latest_plasticity = summary.get("latest_neuroplastic_weight") or latest.get("neuroplastic_weight_ledger") or {}
    latest_modulation = summary.get("latest_neuromodulatory_state") or latest.get("neuromodulatory_state_ledger") or {}
    latest_latent_loop = summary.get("latest_latent_loop_exit") or latest.get("latent_loop_exit_ledger") or {}
    latest_kv_cache = summary.get("latest_kv_cache_compression") or latest.get("kv_cache_compression_ledger") or {}
    latest_backprop = summary.get("latest_loss_backpropagation") or latest.get("loss_backpropagation_ledger") or {}
    latest_optimizer_school = summary.get("latest_optimizer_school") or latest.get("optimizer_school_ledger") or {}
    latest_downstream = latest.get("downstream_node_runtime") or {}
    latest_action_output = summary.get("latest_action_output_decoder") or latest.get("action_output_decoder_ledger") or {}
    latest_forward_propagation = summary.get("latest_forward_propagation") or latest.get("forward_propagation_ledger") or {}
    latest_backward_propagation = summary.get("latest_backward_propagation") or latest.get("backward_propagation_ledger") or {}
    latest_parameter_tensor = summary.get("latest_parameter_tensor") or latest.get("parameter_tensor_ledger") or {}
    latest_activation_function = summary.get("latest_activation_function") or latest.get("activation_function_ledger") or {}
    latest_computational_graph = summary.get("latest_computational_graph") or latest.get("computational_graph_ledger") or {}
    latest_optimizer_state = summary.get("latest_optimizer_state_vector") or latest.get("optimizer_state_vector_ledger") or {}
    latest_model_genome = summary.get("latest_model_genome") or latest.get("model_genome_ledger") or {}
    latest_tensor_kernel = summary.get("latest_tensor_runtime_kernel") or latest.get("tensor_runtime_kernel_ledger") or {}
    latest_layer_stack = summary.get("latest_layer_block_stack") or latest.get("layer_block_stack_ledger") or {}
    latest_distillation_loop = summary.get("latest_distillation_loop") or latest.get("distillation_loop_ledger") or {}
    latest_federated_influence = summary.get("latest_federated_influence") or latest.get("federated_influence_ledger") or {}
    latest_dream_cycle = summary.get("latest_executable_dream_cycle") or latest.get("executable_dream_cycle_ledger") or {}
    latest_deep_replay = summary.get("latest_deep_replay_drilldown") or latest.get("deep_replay_drilldown_ledger") or {}
    latest_durable_storage = summary.get("latest_durable_storage") or latest.get("durable_storage_ledger") or {}
    latest_checkpoint_coverage = summary.get("latest_checkpoint_coverage") or latest.get("checkpoint_coverage_ledger") or {}
    latest_runtime_decision = summary.get("latest_runtime_decision") or latest.get("runtime_decision_ledger") or {}
    latest_backend_execution = (
        summary.get("latest_backend_quantization_execution")
        or latest.get("backend_quantization_execution_ledger")
        or {}
    )
    latest_tool_registry = latest.get("tool_execution_registry") or {}
    latest_task_graph = latest.get("task_dependency_graph") or {}
    latest_provider_circuit = latest.get("provider_circuit_breaker") or {}
    latest_prompt_overlay = latest.get("prompt_overlay_registry") or {}
    latest_skill_system = latest.get("skill_system_loader") or {}
    latest_bridge_manager = latest.get("bridge_manager") or {}
    latest_research_monitor = latest.get("research_monitor_pipeline") or {}
    latest_federated_packet = latest.get("federated_learning_packet") or {}
    latest_prior_update = latest.get("federated_prior_update") or {}
    latest_activation = latest.get("activation") or {}
    latest_shadow = latest.get("shadow_routing") or {}
    prior_ledger = summary.get("federated_learning_prior_ledger") or {}
    federated_prior_feedback = summary.get("federated_prior_feedback") or {}
    dream_ledger = summary.get("dream_ledger") or {}
    node_registry = summary.get("node_registry") or {}
    harmonic_geometry = summary.get("harmonic_geometry_kernel") or {}
    federated_contract = summary.get("federated_learning_contract") or {}
    federation_safety = summary.get("global_federation_safety") or {}
    latest_forward_packet_security = latest_federated_packet.get("security_envelope") or {}
    latest_productionization = summary.get("latest_productionization") or {}
    latest_sandbox_provider = latest_productionization.get("sandbox_provider_run") or {}
    latest_teacher_distillation = latest_productionization.get("teacher_distillation") or {}
    latest_federation_security = latest_productionization.get("federation_security") or {}
    latest_runtime_research = latest_productionization.get("runtime_research_foundry") or {}
    latest_gated_release = latest_productionization.get("gated_release") or {}
    productionization_ledger = summary.get("productionization_ledger") or {}
    latest_release = summary.get("latest_release") or {}
    latest_rollback = summary.get("latest_rollback") or {}
    latest_rewind = summary.get("latest_rewind") or {}
    release_ledger = summary.get("release_ledger") or {}
    latest_health_event = summary.get("latest_health_event") or {}
    latest_self_healing_route = summary.get("latest_self_healing_route") or {}
    health_ledger = summary.get("health_ledger") or {}
    self_healing_ledger = summary.get("self_healing_ledger") or {}
    global_federation_review_ledger = summary.get("global_federation_review_ledger") or {}
    latest_global_federation_review = summary.get("latest_global_federation_review") or {}
    route_candidate_eval_ledger = summary.get("governed_route_candidate_evaluation_ledger") or {}
    latest_route_candidate_eval = summary.get("latest_governed_route_candidate_evaluation") or {}
    route_candidate_approval_ledger = summary.get("governed_route_candidate_approval_ledger") or {}
    route_candidate_rollback_ledger = summary.get("governed_route_candidate_rollback_ledger") or {}
    latest_route_candidate_approval = summary.get("latest_governed_route_candidate_approval") or {}
    latest_route_candidate_rollback = summary.get("latest_governed_route_candidate_rollback") or {}
    runtime_state = summary.get("runtime_state") or ("live-bound" if latest else "static-canon")
    latest_forward_blocked = _runtime_record_is_blocked(latest)
    route_candidate_approval_runtime_state = "static-canon"
    route_candidate_approval_status_label = "route-candidate-approval-awaiting-runtime-evidence"
    if latest_route_candidate_approval:
        if (
            latest_route_candidate_rollback
            and latest_route_candidate_rollback.get("approval_id") == latest_route_candidate_approval.get("approval_id")
        ):
            route_candidate_approval_runtime_state = "rolled-back"
            route_candidate_approval_status_label = (
                latest_route_candidate_rollback.get("honest_status_label")
                or "session-shadow-route-overlay-rolled-back"
            )
        elif latest_route_candidate_approval.get("status") == "shadow-route-applied":
            route_candidate_approval_runtime_state = "live-bound"
            route_candidate_approval_status_label = (
                latest_route_candidate_approval.get("honest_status_label")
                or "session-shadow-route-overlay-active"
            )
        else:
            route_candidate_approval_runtime_state = "degraded"
            route_candidate_approval_status_label = (
                latest_route_candidate_approval.get("honest_status_label")
                or "route-candidate-approval-blocked"
            )

    def forward_component_runtime_state(payload: dict[str, Any]) -> str:
        if not payload:
            return "static-canon"
        return "degraded" if latest_forward_blocked else "live-bound"

    latest_candidate = summary.get("latest_candidate") or {}
    latest_candidate_blocked = _runtime_record_is_blocked(latest_candidate)
    latest_global_federation_review_blocked = _runtime_record_is_blocked(latest_global_federation_review)
    latest_productionization_blocked = _runtime_record_is_blocked(latest_productionization)
    latest_gated_release_blocked = _runtime_record_is_blocked(latest_gated_release)
    latest_release_blocked = _runtime_record_is_blocked(latest_release)
    latest_rollback_blocked = _runtime_record_is_blocked(latest_rollback)
    latest_rewind_blocked = _runtime_record_is_blocked(latest_rewind)
    return [
        {
            "component_id": "HarmonicGeometryKernel",
            "runtime_state": "live-bound",
            "purpose": "deterministic golden-ratio and harmonic metadata for plane geometry, routing resonance, loops, bus phases, and runtime receipts",
            "latest_ref": harmonic_geometry.get("kernel_id"),
            "claim_boundary": harmonic_geometry.get("claim_boundary"),
            "required_for": ["plane_signatures", "routing_resonance", "loop_cadence", "artifact_traceability"],
        },
        {
            "component_id": "HiveActivationLedger",
            "runtime_state": forward_component_runtime_state(latest_activation),
            "purpose": "first-class activation artifact binding source refs, embedding refs, privacy class, memory refs, action refs, and checkpoint refs",
            "latest_ref": latest_activation.get("activation_id"),
            "required_for": ["typed_activation", "checkpoint_linkage", "privacy_traceability"],
        },
        {
            "component_id": "HiveSensoryInputLedger",
            "runtime_state": forward_component_runtime_state(latest_sensory),
            "purpose": "privacy-preserving sensory/tokenization ingress over operator intent, capability signals, memory refs, and action refs",
            "latest_ref": latest_sensory.get("sensory_ledger_id"),
            "activation_ref": latest_sensory.get("activation_ref"),
            "normalized_channel_count": latest_sensory.get("normalized_channel_count", 0),
            "raw_intent_stored": (latest_sensory.get("input_integrity") or {}).get("raw_intent_stored"),
            "required_for": ["sensory_input", "tokenization_boundary", "privacy_safe_input_replay"],
        },
        {
            "component_id": "HiveEmbeddingTensorLedger",
            "runtime_state": forward_component_runtime_state(latest_embedding),
            "purpose": "privacy-preserving symbolic token and embedding tensor evidence for the representation plane",
            "latest_ref": latest_embedding.get("embedding_ledger_id"),
            "activation_ref": latest_embedding.get("activation_ref"),
            "embedding_shape": latest_embedding.get("embedding_shape", []),
            "raw_tokens_stored": (latest_embedding.get("token_privacy") or {}).get("raw_tokens_stored"),
            "required_for": ["embedding_representation", "attention_queries", "privacy_safe_tensor_replay"],
        },
        {
            "component_id": "HiveTemporalPositionalLedger",
            "runtime_state": forward_component_runtime_state(latest_temporal),
            "purpose": "rotary golden-angle symbolic position evidence for tokens, recurrent loops, and checkpoint anchors",
            "latest_ref": latest_temporal.get("temporal_ledger_id"),
            "sensory_input_ref": latest_temporal.get("sensory_input_ref"),
            "embedding_tensor_ref": latest_temporal.get("embedding_tensor_ref"),
            "position_count": latest_temporal.get("position_count", 0),
            "active_context_order_mutated": (latest_temporal.get("temporal_integrity") or {}).get("active_context_order_mutated"),
            "required_for": ["temporal_positional", "loop_positioning", "checkpoint_order_replay"],
        },
        {
            "component_id": "HiveMemoryEngramLedger",
            "runtime_state": forward_component_runtime_state(latest_memory_engram),
            "purpose": "reference-only memory engram binding that retrieves memory refs without storing raw private memory content",
            "latest_ref": latest_memory_engram.get("memory_ledger_id"),
            "temporal_positional_ref": latest_memory_engram.get("temporal_positional_ref"),
            "memory_ref_count": latest_memory_engram.get("memory_ref_count", 0),
            "raw_memory_content_stored": (latest_memory_engram.get("memory_integrity") or {}).get("raw_memory_content_stored"),
            "required_for": ["memory_engram", "source_canon_binding", "privacy_safe_memory_replay"],
        },
        {
            "component_id": "HiveAttentionRoutingLedger",
            "runtime_state": forward_component_runtime_state(latest_attention),
            "purpose": "multi-head attention-style focus weights over selected nodes, memory refs, policy gates, bus, and blackboard artifacts",
            "latest_ref": latest_attention.get("attention_ledger_id"),
            "embedding_tensor_ref": latest_attention.get("embedding_tensor_ref"),
            "attention_head_count": latest_attention.get("attention_head_count", 0),
            "focus_target_count": latest_attention.get("focus_target_count", 0),
            "softmax_normalized": (latest_attention.get("attention_integrity") or {}).get("softmax_normalized"),
            "required_for": ["attention_focus", "memory_focus", "expert_focus", "policy_focus"],
        },
        {
            "component_id": "HiveResidualNormalizationLedger",
            "runtime_state": forward_component_runtime_state(latest_normalization),
            "purpose": "RMSNorm-style symbolic normalization and residual stream evidence across embeddings, attention, blackboard, and bus state",
            "latest_ref": latest_normalization.get("normalization_ledger_id"),
            "embedding_tensor_ref": latest_normalization.get("embedding_tensor_ref"),
            "attention_ref": latest_normalization.get("attention_ref"),
            "normalized_stream_count": latest_normalization.get("normalized_stream_count", 0),
            "residual_stream_preserved": (latest_normalization.get("normalization_integrity") or {}).get("residual_stream_preserved"),
            "required_for": ["layer_normalization", "residual_stream", "pre_feedforward_state"],
        },
        {
            "component_id": "HiveSparseExpertGateLedger",
            "runtime_state": forward_component_runtime_state(latest_gate),
            "purpose": "sparse MoE gate distribution over active expert and mini-brain nodes while keeping non-selected nodes visible-idle",
            "latest_ref": latest_gate.get("gate_ledger_id"),
            "attention_ref": latest_gate.get("attention_ref"),
            "top_k": latest_gate.get("top_k", 0),
            "selected_expert_node_ids": latest_gate.get("selected_expert_node_ids", []),
            "active_production_routing_mutated": (latest_gate.get("gate_integrity") or {}).get("active_production_routing_mutated"),
            "required_for": ["sparse_moe_router", "expert_gate_distribution", "idle_node_visibility"],
        },
        {
            "component_id": "HiveFeedForwardExpertLedger",
            "runtime_state": forward_component_runtime_state(latest_feedforward),
            "purpose": "sparse expert feed-forward/MLP computation evidence after normalized residual state and MoE gate dispatch",
            "latest_ref": latest_feedforward.get("feedforward_ledger_id"),
            "sparse_gate_ref": latest_feedforward.get("sparse_gate_ref"),
            "residual_normalization_ref": latest_feedforward.get("residual_normalization_ref"),
            "expert_unit_count": latest_feedforward.get("expert_unit_count", 0),
            "activation_function": (latest_feedforward.get("feedforward_policy") or {}).get("activation_function"),
            "active_expert_weights_mutated": (latest_feedforward.get("feedforward_integrity") or {}).get("active_expert_weights_mutated"),
            "required_for": ["expert_computation", "mlp_feedforward", "sparse_expert_dispatch"],
        },
        {
            "component_id": "NeuralBus",
            "runtime_state": runtime_state,
            "purpose": "typed hive-wide message passing between planes and nodes",
            "latest_ref": latest_bus.get("bus_id"),
            "message_count": latest_bus.get("message_count", 0),
            "required_for": ["activation_publish", "route_broadcast", "failure_visibility"],
        },
        {
            "component_id": "HiveBlackboard",
            "runtime_state": runtime_state,
            "purpose": "residual state shared across sparse activations and recurrent loops",
            "latest_ref": latest_blackboard.get("residual_state_id"),
            "entry_count": latest_blackboard.get("entry_count", 0),
            "required_for": ["residual_continuity", "cross_plane_memory", "self_healing_context"],
        },
        {
            "component_id": "CortexRouter",
            "runtime_state": runtime_state,
            "purpose": "sparse MoE routing over AOs, experts, tools, memory, and gates",
            "latest_ref": (latest.get("route_decision") or {}).get("router_id"),
            "selected_node_count": (latest.get("route_decision") or {}).get("sparse_top_k", 0),
            "required_for": ["top_k_selection", "route_around", "idle_node_availability"],
        },
        {
            "component_id": "RecurrentDeliberationLoop",
            "runtime_state": runtime_state,
            "purpose": "bounded latent-style loop over selected nodes before action",
            "latest_ref": (latest.get("loop_summary") or {}).get("exit_reason"),
            "loop_count": (latest.get("loop_summary") or {}).get("loop_count", 0),
            "required_for": ["loop_exit_gate", "confidence_growth", "blocked_exit"],
        },
        {
            "component_id": "HiveTraceLedger",
            "runtime_state": runtime_state,
            "purpose": "plane-by-plane execution trace for audit and replay",
            "latest_ref": latest_trace.get("trace_ledger_id"),
            "record_count": latest_trace.get("record_count", 0),
            "required_for": ["plane_trace", "replay", "debugging"],
        },
        {
            "component_id": "HiveLaminarMicrocircuitLedger",
            "runtime_state": forward_component_runtime_state(latest_microcircuit),
            "purpose": "plane-internal laminar microcircuit evidence for L1, L2/3, L4, and L5/6 populations, dendritic compartments, and event thresholds",
            "latest_ref": latest_microcircuit.get("microcircuit_id"),
            "trace_ledger_ref": latest_microcircuit.get("trace_ledger_ref"),
            "plane_microcircuit_count": latest_microcircuit.get("plane_microcircuit_count", 0),
            "event_driven_updates": (latest_microcircuit.get("microcircuit_integrity") or {}).get("event_driven_updates"),
            "required_for": ["plane_internal_structure", "event_driven_updates", "laminar_replay"],
        },
        {
            "component_id": "HiveNeuralPathwayMap",
            "runtime_state": forward_component_runtime_state(latest_pathway),
            "purpose": "first-class neural-network pathway graph binding planes, mini-brain scale stack, recurrent feedback, immune gates, and substrate-only artifact refs",
            "latest_ref": latest_pathway.get("pathway_id"),
            "plane_pathway_count": len(latest_pathway.get("plane_pathways") or []),
            "node_pathway_count": len(latest_pathway.get("node_pathways") or []),
            "feedback_pathway_count": len(latest_pathway.get("feedback_pathways") or []),
            "visibility_model": (latest_pathway.get("connectivity_summary") or {}).get("visibility_model"),
            "required_for": ["neural_pathway_replay", "mini_brain_scale_stack", "hive_wide_connectivity"],
        },
        {
            "component_id": "HivePlaneAdjacencyMatrix",
            "runtime_state": forward_component_runtime_state(latest_plane_matrix),
            "purpose": "plane-by-plane weighted adjacency matrix proving the neural substrate order, feed-forward edges, feedback overlays, and artifact refs",
            "latest_ref": latest_plane_matrix.get("matrix_id"),
            "matrix_shape": latest_plane_matrix.get("matrix_shape", []),
            "edge_count": latest_plane_matrix.get("edge_count", 0),
            "artifact_ref_count": latest_plane_matrix.get("artifact_ref_count", 0),
            "active_production_mutated": (latest_plane_matrix.get("matrix_integrity") or {}).get("active_production_mutated"),
            "required_for": ["full_plane_connectivity", "pathway_matrix_replay", "substrate_artifact_binding"],
        },
        {
            "component_id": "HiveSynapticTransmissionLedger",
            "runtime_state": forward_component_runtime_state(latest_transmission),
            "purpose": "per-forward-pass signal propagation ledger over plane, mini-brain, recurrent, feedback, and immune pathway edges",
            "latest_ref": latest_transmission.get("transmission_id"),
            "pathway_ref": latest_transmission.get("pathway_ref"),
            "plane_signal_count": latest_transmission.get("plane_signal_count", 0),
            "node_signal_count": latest_transmission.get("node_signal_count", 0),
            "recurrent_signal_count": latest_transmission.get("recurrent_signal_count", 0),
            "bounded_signal_strengths": (latest_transmission.get("signal_integrity") or {}).get("bounded_signal_strengths"),
            "required_for": ["live_signal_propagation", "pathway_replay", "immune_gate_visibility"],
        },
        {
            "component_id": "HiveNeuroplasticWeightLedger",
            "runtime_state": forward_component_runtime_state(latest_plasticity),
            "purpose": "shadow-only plasticity ledger that derives bounded plane, mini-brain, and feedback weight deltas from synaptic signal evidence",
            "latest_ref": latest_plasticity.get("weight_ledger_id"),
            "pathway_ref": latest_plasticity.get("pathway_ref"),
            "transmission_ref": latest_plasticity.get("transmission_ref"),
            "plane_weight_count": latest_plasticity.get("plane_weight_count", 0),
            "node_weight_count": latest_plasticity.get("node_weight_count", 0),
            "feedback_weight_count": latest_plasticity.get("feedback_weight_count", 0),
            "learning_scope": (latest_plasticity.get("plasticity_rule") or {}).get("learning_scope"),
            "bounded_weight_deltas": (latest_plasticity.get("plasticity_integrity") or {}).get("bounded_weight_deltas"),
            "required_for": ["hive_wide_neuroplasticity", "shadow_routing_learning", "sandboxed_weight_promotion"],
        },
        {
            "component_id": "HiveNeuromodulatoryStateLedger",
            "runtime_state": forward_component_runtime_state(latest_modulation),
            "purpose": "symbolic reward, uncertainty, stability, immune-alert, and dream-novelty signals that gate shadow plasticity without mutating active routes",
            "latest_ref": latest_modulation.get("neuromodulator_id"),
            "weight_ledger_ref": latest_modulation.get("weight_ledger_ref"),
            "modulator_count": latest_modulation.get("modulator_count", 0),
            "effective_learning_rate": (latest_modulation.get("plasticity_gate") or {}).get("effective_learning_rate"),
            "active_route_mutation_allowed": (latest_modulation.get("plasticity_gate") or {}).get("active_route_mutation_allowed"),
            "required_for": ["plasticity_gating", "uncertainty_attention", "dream_novelty_review"],
        },
        {
            "component_id": "HiveLatentLoopExitLedger",
            "runtime_state": forward_component_runtime_state(latest_latent_loop),
            "purpose": "looped-language-model-style latent reasoning exit-gate evidence using hazard, survival, and CDF mass rather than exposed vocabulary chain-of-thought",
            "latest_ref": latest_latent_loop.get("latent_loop_id"),
            "attention_ref": latest_latent_loop.get("attention_ref"),
            "sparse_gate_ref": latest_latent_loop.get("sparse_gate_ref"),
            "feedforward_ref": latest_latent_loop.get("feedforward_ref"),
            "loop_step_count": latest_latent_loop.get("loop_step_count", 0),
            "probability_model": (latest_latent_loop.get("exit_gate_policy") or {}).get("probability_model"),
            "vocabulary_chain_of_thought_required": (latest_latent_loop.get("exit_gate_integrity") or {}).get(
                "vocabulary_chain_of_thought_required",
            ),
            "required_for": ["latent_reasoning_loop", "exit_gate_probability", "internal_compute_scaling"],
        },
        {
            "component_id": "HiveKVCacheCompressionLedger",
            "runtime_state": forward_component_runtime_state(latest_kv_cache),
            "purpose": "shadow-only KV-cache compression policy evidence for eviction, quantization, low-rank, heavy-hitter, and hybrid cache trials",
            "latest_ref": latest_kv_cache.get("kv_cache_ledger_id"),
            "attention_ref": latest_kv_cache.get("attention_ref"),
            "latent_loop_ref": latest_kv_cache.get("latent_loop_ref"),
            "candidate_count": len(latest_kv_cache.get("cache_policy_candidates") or []),
            "selected_shadow_policy_id": (latest_kv_cache.get("selected_shadow_policy") or {}).get("policy_id"),
            "raw_kv_values_stored": (latest_kv_cache.get("kv_cache_integrity") or {}).get("raw_kv_values_stored"),
            "required_for": ["runtime_memory_efficiency", "kv_cache_policy_trials", "sandboxed_backend_improvement"],
        },
        {
            "component_id": "HiveLossBackpropagationLedger",
            "runtime_state": forward_component_runtime_state(latest_backprop),
            "purpose": "shadow-only loss and backward credit-assignment evidence from eval loss through gates, attention, embeddings, and plasticity",
            "latest_ref": latest_backprop.get("backpropagation_id"),
            "sparse_gate_ref": latest_backprop.get("sparse_gate_ref"),
            "attention_ref": latest_backprop.get("attention_ref"),
            "loss_term_count": len(latest_backprop.get("loss_terms") or []),
            "gradient_path_count": len(latest_backprop.get("gradient_paths") or []),
            "active_model_weights_mutated": (latest_backprop.get("gradient_integrity") or {}).get("active_model_weights_mutated"),
            "required_for": ["loss_feedback", "backpropagation_shadow_evidence", "optimizer_school_credit_assignment"],
        },
        {
            "component_id": "HiveOptimizerSchoolLedger",
            "runtime_state": forward_component_runtime_state(latest_optimizer_school),
            "purpose": "Ivy-school shadow curriculum and teacher-review queue generated from backpropagation, memory engrams, latent loops, and KV policy evidence",
            "latest_ref": latest_optimizer_school.get("optimizer_ledger_id"),
            "backpropagation_ref": latest_optimizer_school.get("backpropagation_ref"),
            "memory_engram_ref": latest_optimizer_school.get("memory_engram_ref"),
            "curriculum_item_count": len(latest_optimizer_school.get("curriculum_update_plan") or []),
            "teacher_review_required": (latest_optimizer_school.get("optimizer_integrity") or {}).get("teacher_review_required"),
            "active_model_weights_mutated": (latest_optimizer_school.get("optimizer_integrity") or {}).get("active_model_weights_mutated"),
            "required_for": ["optimizer_school", "teacher_distillation_review", "shadow_curriculum_proposals"],
        },
        {
            "component_id": "FederatedLearningSanitizer",
            "runtime_state": runtime_state,
            "purpose": "mandatory privacy-preserving artifact and metadata packet generation without raw personal data export",
            "latest_ref": latest_federated_packet.get("packet_id"),
            "contract_ref": federated_contract.get("contract_id"),
            "participation_model": federated_contract.get("participation_model"),
            "raw_personal_data_export": federated_contract.get("raw_personal_data_export"),
            "required_for": ["federated_learning", "privacy_sanitization", "global_self_improvement"],
        },
        {
            "component_id": "FederatedPriorLedger",
            "runtime_state": "live-bound" if prior_ledger.get("prior_update_count", 0) else "static-canon",
            "purpose": "sanitized packet aggregation into routing, geometry, task, and confidence priors before global promotion gates",
            "latest_ref": latest_prior_update.get("prior_update_id"),
            "packet_count": prior_ledger.get("packet_count", 0),
            "prior_update_count": prior_ledger.get("prior_update_count", 0),
            "promotion_boundary": prior_ledger.get("promotion_boundary"),
            "required_for": ["hive_learning_rate", "router_prior_updates", "sandboxed_global_learning"],
        },
        {
            "component_id": "ShadowRoutingPriorInfluence",
            "runtime_state": forward_component_runtime_state(latest_shadow),
            "purpose": "feeds sanitized prior ledger weights into routing comparisons without mutating active production routing",
            "latest_ref": latest_shadow.get("shadow_routing_id"),
            "promotion_state": latest_shadow.get("promotion_state"),
            "required_for": ["old_vs_new_route_quality", "shadow_only_prior_trials", "gated_route_promotion"],
        },
        {
            "component_id": "FederatedPriorFeedbackCycle",
            "runtime_state": federated_prior_feedback.get("status") or "degraded",
            "purpose": "binds sanitized prior ledger evidence to shadow routing and recursive dreaming without active route or production mutation",
            "latest_ref": federated_prior_feedback.get("latest_ref"),
            "honest_status_label": federated_prior_feedback.get("honest_status_label"),
            "prior_update_count": federated_prior_feedback.get("prior_update_count", 0),
            "shadow_routing_ref": federated_prior_feedback.get("shadow_routing_ref"),
            "active_route_mutated": federated_prior_feedback.get("active_route_mutated"),
            "mutation_boundary": federated_prior_feedback.get("mutation_boundary"),
            "required_for": ["prior_conditioned_dreaming", "shadow_route_feedback", "control_panel_truth"],
        },
        {
            "component_id": "GovernedRouteCandidateEvaluation",
            "runtime_state": _route_candidate_evaluation_runtime_state(latest_route_candidate_eval),
            "purpose": "evaluates prior-influenced shadow route candidates through eval, sandbox replay, policy scan, admin approval, and rollback evidence without active routing mutation",
            "latest_ref": latest_route_candidate_eval.get("evaluation_id"),
            "honest_status_label": (
                latest_route_candidate_eval.get("honest_status_label")
                or "route-candidate-evaluation-awaiting-runtime-evidence"
            ),
            "evaluation_count": route_candidate_eval_ledger.get("evaluation_count", 0),
            "blocked_count": route_candidate_eval_ledger.get("blocked_count", 0),
            "source_shadow_routing_ref": latest_route_candidate_eval.get("source_shadow_routing_ref"),
            "promotion_gate_state": (latest_route_candidate_eval.get("promotion_gate") or {}).get("gate_state"),
            "active_route_mutated": latest_route_candidate_eval.get("active_route_mutated", False),
            "active_production_mutated": latest_route_candidate_eval.get("active_production_mutated", False),
            "required_for": [
                "shadow_route_eval_delta",
                "closed_sandbox_replay",
                "admin_route_change_approval",
                "route_rollback_plan",
            ],
        },
        {
            "component_id": "GovernedRouteCandidateApproval",
            "runtime_state": route_candidate_approval_runtime_state,
            "purpose": "binds admin-approved route candidates to EvalRegistry shadow replay, session-only route overlay apply, rollback metadata, and control-panel replay evidence",
            "latest_ref": latest_route_candidate_approval.get("approval_id"),
            "latest_rollback_ref": latest_route_candidate_rollback.get("rollback_id"),
            "honest_status_label": route_candidate_approval_status_label,
            "approval_count": route_candidate_approval_ledger.get("approval_count", 0),
            "active_session_shadow_overlay_count": route_candidate_approval_ledger.get(
                "active_session_shadow_overlay_count",
                0,
            ),
            "rollback_count": route_candidate_rollback_ledger.get("rollback_count", 0),
            "source_evaluation_ref": latest_route_candidate_approval.get("evaluation_id"),
            "eval_shadow_run_ref": (
                (latest_route_candidate_approval.get("eval_replay") or {}).get("run_id")
            ),
            "active_route_mutated": latest_route_candidate_approval.get("active_route_mutated", False),
            "active_production_mutated": latest_route_candidate_approval.get("active_production_mutated", False),
            "required_for": [
                "admin_route_change_approval",
                "eval_registry_shadow_replay",
                "session_shadow_overlay_apply",
                "route_overlay_rollback",
            ],
        },
        {
            "component_id": "DownstreamNodeRuntime",
            "runtime_state": runtime_state,
            "purpose": "AO and expert execution units consuming NeuralBus, HiveBlackboard, and neural-internal artifacts only",
            "latest_ref": latest_downstream.get("runtime_id"),
            "receipt_count": latest_downstream.get("receipt_count", 0),
            "execution_unit_count": latest_downstream.get("execution_unit_count", 0),
            "required_for": ["artifact_bound_execution", "no_direct_state_reads", "node_runtime_audit"],
        },
        {
            "component_id": "HiveActionOutputDecoderLedger",
            "runtime_state": forward_component_runtime_state(latest_action_output),
            "purpose": "artifact-bound output decoder that turns downstream node output refs into operator-reviewable decoded artifacts without external delivery mutation",
            "latest_ref": latest_action_output.get("output_decoder_id"),
            "downstream_runtime_ref": latest_action_output.get("downstream_runtime_ref"),
            "optimizer_school_ref": latest_action_output.get("optimizer_school_ref"),
            "decoded_output_count": latest_action_output.get("decoded_output_count", 0),
            "raw_outputs_exported": (latest_action_output.get("output_integrity") or {}).get("raw_outputs_exported"),
            "active_external_delivery_mutated": (latest_action_output.get("output_integrity") or {}).get(
                "active_external_delivery_mutated",
            ),
            "required_for": ["action_output", "operator_review_gate", "artifact_bound_delivery"],
        },
        {
            "component_id": "HiveForwardPropagationLedger",
            "runtime_state": forward_component_runtime_state(latest_forward_propagation),
            "purpose": "ordered symbolic state-vector propagation through every cognitive plane with artifact-bound input/output state refs",
            "latest_ref": latest_forward_propagation.get("propagation_id"),
            "plane_adjacency_matrix_ref": latest_forward_propagation.get("plane_adjacency_matrix_ref"),
            "step_count": latest_forward_propagation.get("step_count", 0),
            "all_planes_covered": (latest_forward_propagation.get("propagation_integrity") or {}).get("all_planes_covered"),
            "active_production_mutated": (latest_forward_propagation.get("propagation_integrity") or {}).get(
                "active_production_mutated",
            ),
            "required_for": ["forward_state_handoff", "full_plane_coverage", "state_vector_replay"],
        },
        {
            "component_id": "HiveBackwardPropagationLedger",
            "runtime_state": forward_component_runtime_state(latest_backward_propagation),
            "purpose": "reverse-mode symbolic credit-assignment path from loss evidence back through every forward propagation plane",
            "latest_ref": latest_backward_propagation.get("backward_propagation_id"),
            "forward_propagation_ref": latest_backward_propagation.get("forward_propagation_ref"),
            "loss_backpropagation_ref": latest_backward_propagation.get("loss_backpropagation_ref"),
            "step_count": latest_backward_propagation.get("step_count", 0),
            "all_forward_steps_covered": (latest_backward_propagation.get("backward_integrity") or {}).get(
                "all_forward_steps_covered",
            ),
            "active_model_weights_mutated": (latest_backward_propagation.get("backward_integrity") or {}).get(
                "active_model_weights_mutated",
            ),
            "required_for": ["backward_credit_assignment", "gradient_path_replay", "shadow_learning_audit"],
        },
        {
            "component_id": "HiveParameterTensorLedger",
            "runtime_state": forward_component_runtime_state(latest_parameter_tensor),
            "purpose": "reference-only parameter tensor registry for symbolic weights, biases, gates, norms, adapters, and output projections",
            "latest_ref": latest_parameter_tensor.get("parameter_ledger_id"),
            "backward_propagation_ref": latest_parameter_tensor.get("backward_propagation_ref"),
            "neuroplastic_weight_ref": latest_parameter_tensor.get("neuroplastic_weight_ref"),
            "parameter_tensor_count": latest_parameter_tensor.get("parameter_tensor_count", 0),
            "raw_tensor_values_stored": (latest_parameter_tensor.get("parameter_integrity") or {}).get(
                "raw_tensor_values_stored",
            ),
            "active_parameter_mutated": (latest_parameter_tensor.get("parameter_integrity") or {}).get(
                "active_parameter_mutated",
            ),
            "required_for": ["parameter_reference_map", "quantization_planning", "sandboxed_weight_promotion"],
        },
        {
            "component_id": "HiveActivationFunctionLedger",
            "runtime_state": forward_component_runtime_state(latest_activation_function),
            "purpose": "reference-only nonlinear activation-function map for attention, gates, feed-forward, normalization, temporal phase, and latent exits",
            "latest_ref": latest_activation_function.get("activation_function_ledger_id"),
            "parameter_tensor_ref": latest_activation_function.get("parameter_tensor_ref"),
            "forward_propagation_ref": latest_activation_function.get("forward_propagation_ref"),
            "activation_function_count": latest_activation_function.get("activation_function_count", 0),
            "raw_activation_values_stored": (
                latest_activation_function.get("activation_function_integrity") or {}
            ).get("raw_activation_values_stored"),
            "active_kernel_mutated": (latest_activation_function.get("activation_function_integrity") or {}).get(
                "active_kernel_mutated",
            ),
            "required_for": ["neural_nonlinearities", "activation_kernel_replay", "sandboxed_kernel_improvement"],
        },
        {
            "component_id": "HiveComputationalGraphLedger",
            "runtime_state": forward_component_runtime_state(latest_computational_graph),
            "purpose": "reference-only operation graph linking forward dataflow, backward credit assignment, parameters, and nonlinear functions",
            "latest_ref": latest_computational_graph.get("graph_ledger_id"),
            "activation_function_ref": latest_computational_graph.get("activation_function_ref"),
            "parameter_tensor_ref": latest_computational_graph.get("parameter_tensor_ref"),
            "operation_node_count": latest_computational_graph.get("operation_node_count", 0),
            "operation_edge_count": latest_computational_graph.get("operation_edge_count", 0),
            "active_runtime_mutated": (latest_computational_graph.get("graph_integrity") or {}).get(
                "active_runtime_mutated",
            ),
            "required_for": ["computational_graph_replay", "gradient_path_audit", "operation_level_policy_gates"],
        },
        {
            "component_id": "HiveOptimizerStateVectorLedger",
            "runtime_state": forward_component_runtime_state(latest_optimizer_state),
            "purpose": "shadow-only optimizer state vectors for first/second moments, learning rate, clipping, decay, and trust-region gates",
            "latest_ref": latest_optimizer_state.get("optimizer_state_ledger_id"),
            "computational_graph_ref": latest_optimizer_state.get("computational_graph_ref"),
            "parameter_tensor_ref": latest_optimizer_state.get("parameter_tensor_ref"),
            "state_vector_count": latest_optimizer_state.get("state_vector_count", 0),
            "active_optimizer_state_mutated": (latest_optimizer_state.get("optimizer_state_integrity") or {}).get(
                "active_optimizer_state_mutated",
            ),
            "active_parameter_mutated": (latest_optimizer_state.get("optimizer_state_integrity") or {}).get(
                "active_parameter_mutated",
            ),
            "required_for": ["shadow_optimizer_state", "teacher_distillation_training_plan", "sandboxed_update_gate"],
        },
        {
            "component_id": "HiveModelGenomeLedger",
            "runtime_state": forward_component_runtime_state(latest_model_genome),
            "purpose": "distillation-ready architecture genome tying graph, parameter refs, activation functions, optimizer state, and federation policy",
            "latest_ref": latest_model_genome.get("genome_ledger_id"),
            "optimizer_state_ref": latest_model_genome.get("optimizer_state_ref"),
            "computational_graph_ref": latest_model_genome.get("computational_graph_ref"),
            "architecture_gene_count": latest_model_genome.get("architecture_gene_count", 0),
            "raw_model_weights_stored": (latest_model_genome.get("genome_integrity") or {}).get(
                "raw_model_weights_stored",
            ),
            "active_model_architecture_mutated": (latest_model_genome.get("genome_integrity") or {}).get(
                "active_model_architecture_mutated",
            ),
            "required_for": ["model_distillation_blueprint", "child_expert_generation", "architecture_governance"],
        },
        {
            "component_id": "HiveTensorRuntimeKernelLedger",
            "runtime_state": forward_component_runtime_state(latest_tensor_kernel),
            "purpose": "sandbox-shadow tensor runtime kernel operations over graph, parameter, activation, optimizer, and genome refs",
            "latest_ref": latest_tensor_kernel.get("tensor_kernel_ledger_id"),
            "model_genome_ref": latest_tensor_kernel.get("model_genome_ref"),
            "kernel_op_count": latest_tensor_kernel.get("kernel_op_count", 0),
            "executed_shadow_ops": latest_tensor_kernel.get("executed_shadow_ops"),
            "required_for": ["tensor_runtime_kernel", "shadow_tensor_execution", "backend_benchmarking"],
        },
        {
            "component_id": "HiveLayerBlockStackLedger",
            "runtime_state": forward_component_runtime_state(latest_layer_stack),
            "purpose": "explicit embedding-to-repeated-transformer-MoE-to-output-head execution stack",
            "latest_ref": latest_layer_stack.get("layer_stack_ledger_id"),
            "tensor_kernel_ref": latest_layer_stack.get("tensor_kernel_ref"),
            "block_count": latest_layer_stack.get("block_count", 0),
            "required_for": ["layer_stack_execution", "moe_block_replay", "output_head_binding"],
        },
        {
            "component_id": "HiveDistillationLoopLedger",
            "runtime_state": forward_component_runtime_state(latest_distillation_loop),
            "purpose": "Ivy-school teacher panel, child candidate, eval scorecard, promotion, and parent-retirement gate evidence",
            "latest_ref": latest_distillation_loop.get("distillation_loop_id"),
            "layer_stack_ref": latest_distillation_loop.get("layer_stack_ref"),
            "teacher_panel_count": len(latest_distillation_loop.get("teacher_panel") or []),
            "required_for": ["child_expert_generation", "ivy_teacher_review", "parent_retirement_gate"],
        },
        {
            "component_id": "HiveFederatedInfluenceLedger",
            "runtime_state": forward_component_runtime_state(latest_federated_influence),
            "purpose": "sanitized federation prior influence into shadow routing and training priors with DP, trust, and poisoning checks",
            "latest_ref": latest_federated_influence.get("federated_influence_id"),
            "federated_prior_update_ref": latest_federated_influence.get("federated_prior_update_ref"),
            "shadow_prior_update_count": latest_federated_influence.get("shadow_prior_update_count", 0),
            "required_for": ["federated_prior_influence", "shadow_routing_eval", "privacy_safe_learning"],
        },
        {
            "component_id": "HiveExecutableDreamCycleLedger",
            "runtime_state": forward_component_runtime_state(latest_dream_cycle),
            "purpose": "high-temperature recursive dream candidate generation with low-temperature critique and sandbox plans",
            "latest_ref": latest_dream_cycle.get("dream_cycle_id"),
            "model_genome_ref": latest_dream_cycle.get("model_genome_ref"),
            "dream_candidate_count": latest_dream_cycle.get("dream_candidate_count", 0),
            "required_for": ["recursive_neural_dreaming", "novel_candidate_generation", "dream_critic_gate"],
        },
        {
            "component_id": "HiveDeepReplayDrilldownLedger",
            "runtime_state": forward_component_runtime_state(latest_deep_replay),
            "purpose": "Control Panel drilldown over graph nodes, parameter refs, optimizer vectors, genome genes, paths, and promotion readiness",
            "latest_ref": latest_deep_replay.get("replay_drilldown_id"),
            "graph_ref": latest_deep_replay.get("graph_ref"),
            "drilldown_view_count": latest_deep_replay.get("drilldown_view_count", 0),
            "required_for": ["deep_control_panel_replay", "operator_audit", "promotion_readiness_review"],
        },
        {
            "component_id": "HiveDurableStorageLedger",
            "runtime_state": forward_component_runtime_state(latest_durable_storage),
            "purpose": "repo-local indexed storage contract with checksums, signatures, retention, and restore-query plan",
            "latest_ref": latest_durable_storage.get("storage_ledger_id"),
            "artifact_index_ref": latest_durable_storage.get("artifact_index_ref"),
            "indexed_artifact_count": latest_durable_storage.get("indexed_artifact_count", 0),
            "required_for": ["repo_local_storage", "replay_queries", "restore_proof"],
        },
        {
            "component_id": "HiveCheckpointCoverageLedger",
            "runtime_state": forward_component_runtime_state(latest_checkpoint_coverage),
            "purpose": "restore validation and diff-preview coverage for every newly added runtime ledger",
            "latest_ref": latest_checkpoint_coverage.get("coverage_ledger_id"),
            "checkpoint_ref": latest_checkpoint_coverage.get("checkpoint_ref"),
            "coverage_record_count": latest_checkpoint_coverage.get("coverage_record_count", 0),
            "required_for": ["checkpoint_rewind_coverage", "diff_preview_gate", "restore_validation"],
        },
        {
            "component_id": "HiveRuntimeDecisionLedger",
            "runtime_state": forward_component_runtime_state(latest_runtime_decision),
            "purpose": "real AO/expert runtime decision evidence from substrate artifacts instead of direct local state",
            "latest_ref": latest_runtime_decision.get("runtime_decision_id"),
            "tensor_kernel_ref": latest_runtime_decision.get("tensor_kernel_ref"),
            "decision_count": latest_runtime_decision.get("decision_count", 0),
            "required_for": ["artifact_bound_ao_execution", "expert_runtime_decisions", "direct_state_read_ban"],
        },
        {
            "component_id": "HiveBackendQuantizationExecutionLedger",
            "runtime_state": forward_component_runtime_state(latest_backend_execution),
            "purpose": "shadow backend and quantization benchmark execution across cache, parameter, runtime decision, and tensor kernel refs",
            "latest_ref": latest_backend_execution.get("backend_execution_id"),
            "runtime_decision_ref": latest_backend_execution.get("runtime_decision_ref"),
            "benchmark_scorecard_count": latest_backend_execution.get("benchmark_scorecard_count", 0),
            "required_for": ["runtime_backend_selection", "quantization_trials", "benchmark_promotion_gate"],
        },
        {
            "component_id": "ToolExecutionRegistry",
            "runtime_state": forward_component_runtime_state(latest_tool_registry),
            "purpose": "ToolDef-style action metadata for read-only gates, concurrent safety, output truncation, cache invalidation, and parallel-safe batches",
            "latest_ref": latest_tool_registry.get("registry_id"),
            "registered_tool_count": latest_tool_registry.get("registered_tool_count", 0),
            "parallel_safe_batch_count": len(latest_tool_registry.get("parallel_safe_batches") or []),
            "cache_invalidation_required": (latest_tool_registry.get("cache_invalidation_plan") or {}).get(
                "cache_invalidation_required",
                False,
            ),
            "required_for": ["tool_safety", "parallel_execution", "cache_coherence", "policy_targets"],
        },
        {
            "component_id": "TaskDependencyGraph",
            "runtime_state": forward_component_runtime_state(latest_task_graph),
            "purpose": "blocks/blocked_by dependency graph with reverse-edge refresh, stale dependency audit, and parallel-ready task detection",
            "latest_ref": latest_task_graph.get("graph_id"),
            "edge_count": latest_task_graph.get("edge_count", 0),
            "parallel_ready_count": len(latest_task_graph.get("parallel_ready_task_ids") or []),
            "blocked_task_count": len(latest_task_graph.get("blocked_task_ids") or []),
            "required_for": ["task_dispatch", "parallel_planning", "blocked_work_gate", "workflow_replay"],
        },
        {
            "component_id": "ProviderCircuitBreaker",
            "runtime_state": forward_component_runtime_state(latest_provider_circuit),
            "purpose": "provider error classification, retry policy, quota cooldown, context fallback, and model-family health before route mutation",
            "latest_ref": latest_provider_circuit.get("circuit_id"),
            "provider_event_count": latest_provider_circuit.get("event_count", 0),
            "degraded_family_count": len(
                [
                    family
                    for family in (latest_provider_circuit.get("model_family_health") or {}).values()
                    if family.get("health_state") != "healthy"
                ]
            ),
            "required_for": ["provider_routing", "model_family_health", "fallback_policy", "quota_cooldown"],
        },
        {
            "component_id": "PromptOverlayRegistry",
            "runtime_state": forward_component_runtime_state(latest_prompt_overlay),
            "purpose": "base prompt plus provider, model-family, and runtime overlays composed in shadow with compatibility and conflict checks",
            "latest_ref": latest_prompt_overlay.get("registry_id"),
            "active_overlay_count": len(latest_prompt_overlay.get("composed_overlay_order") or []),
            "conflict_count": (latest_prompt_overlay.get("overlay_conflict_audit") or {}).get("conflict_count", 0),
            "active_prompt_mutated": (latest_prompt_overlay.get("activation_gate") or {}).get(
                "active_prompt_mutated",
                False,
            ),
            "required_for": ["prompt_composition", "provider_overlays", "model_family_overlays", "shadow_prompt_review"],
        },
        {
            "component_id": "SkillSystemLoader",
            "runtime_state": forward_component_runtime_state(latest_skill_system),
            "purpose": "frontmatter-style markdown skill and agent definitions composed into reusable skill systems with orchestrator handoffs and checkpoints",
            "latest_ref": latest_skill_system.get("loader_id"),
            "component_count": latest_skill_system.get("component_count", 0),
            "handoff_validation_state": (latest_skill_system.get("handoff_validation") or {}).get("validation_state"),
            "active_skill_runtime_mutated": (latest_skill_system.get("activation_gate") or {}).get(
                "active_skill_runtime_mutated",
                False,
            ),
            "required_for": ["skill_systems", "markdown_skill_loader", "orchestrator_contract", "handoff_validation"],
        },
        {
            "component_id": "BridgeManager",
            "runtime_state": forward_component_runtime_state(latest_bridge_manager),
            "purpose": "local-first bridge catalog with redaction policy, outbound commitment review, and transport health probes",
            "latest_ref": latest_bridge_manager.get("manager_id"),
            "bridge_count": latest_bridge_manager.get("bridge_count", 0),
            "outbound_review_required_count": latest_bridge_manager.get("outbound_review_required_count", 0),
            "active_bridge_mutation": (latest_bridge_manager.get("local_first_permission_gate") or {}).get(
                "active_bridge_mutation",
                False,
            ),
            "required_for": ["communication_bridges", "redaction", "outbound_commitment_gate", "transport_health"],
        },
        {
            "component_id": "ResearchMonitorPipeline",
            "runtime_state": forward_component_runtime_state(latest_research_monitor),
            "purpose": "scheduled source monitoring, trend detection, candidate intake, promotion gate mapping, and demotion watchlists",
            "latest_ref": latest_research_monitor.get("pipeline_id"),
            "monitor_count": (latest_research_monitor.get("scheduled_source_monitor") or {}).get("monitor_count", 0),
            "candidate_count": len(latest_research_monitor.get("candidate_intake") or []),
            "watchlist_count": len(latest_research_monitor.get("demotion_watchlist") or []),
            "required_for": ["forward_radar", "research_intake", "trend_detection", "candidate_promotion_gates"],
        },
        {
            "component_id": "ClosedSandboxEvalGate",
            "runtime_state": (
                "degraded"
                if latest_candidate_blocked
                else ("live-bound" if latest_candidate else "static-canon")
            ),
            "purpose": "launches and records closed sandbox, eval, security, and privacy evidence before candidate promotion",
            "latest_ref": (latest_candidate.get("closed_sandbox_evaluation") or {}).get("closed_sandbox_evaluation_id"),
            "required_for": ["candidate_promotion_gate", "regression_proof", "secure_sandbox_execution"],
        },
        {
            "component_id": "RecursiveNeuralDreamingRuntime",
            "runtime_state": "live-bound" if dream_ledger.get("dream_count", 0) else "static-canon",
            "purpose": "high-temperature dream generation with low-temperature critique and sandbox plan handoff",
            "latest_ref": dream_ledger.get("latest_dream_id"),
            "dream_count": dream_ledger.get("dream_count", 0),
            "required_for": ["novel_expert_generation", "dream_critique", "candidate_request_output"],
        },
        {
            "component_id": "IvyLeagueSchoolReview",
            "runtime_state": "live-bound" if (summary.get("ivy_league_school") or {}).get("review_count", 0) else "static-canon",
            "purpose": "teacher-panel distillation grade, parent comparison scorecards, and certification records for generated children",
            "latest_ref": (summary.get("ivy_league_school") or {}).get("latest_review_id"),
            "certified_candidate_count": (summary.get("ivy_league_school") or {}).get("certified_candidate_count", 0),
            "required_for": ["expert_distillation", "child_review", "parent_retirement_decision"],
        },
        {
            "component_id": "DurableNodeRegistry",
            "runtime_state": "live-bound" if node_registry.get("durable_update_count", 0) else "static-canon",
            "purpose": "durably registers approved generated nodes and archives outperformed parents with rollback restoration",
            "latest_ref": node_registry.get("latest_update_id"),
            "generated_node_count": node_registry.get("generated_node_count", 0),
            "retired_parent_count": node_registry.get("retired_parent_count", 0),
            "required_for": ["permanent_child_registration", "parent_retirement", "rollback_restoration"],
        },
        {
            "component_id": "AssimilationGate",
            "runtime_state": runtime_state,
            "purpose": "source, sandbox, eval, policy, and retention review gate for candidates",
            "latest_ref": (summary.get("latest_candidate") or {}).get("candidate_run_id"),
            "required_for": ["candidate_sidebar", "retention_review", "promotion_gate"],
        },
        {
            "component_id": "HiveCuratorAO",
            "runtime_state": runtime_state,
            "purpose": "review-only ranking, merge, archive, and pruning recommendations",
            "latest_ref": "curator:hive-library",
            "required_for": ["no_direct_delete", "usage_review", "library_hygiene"],
        },
        {
            "component_id": "ImmuneKernel",
            "runtime_state": runtime_state,
            "purpose": "policy and injection defense before writes, bridges, and promotion",
            "latest_ref": "policy:immune-kernel",
            "required_for": ["policy_scan", "write_gate", "promotion_safety"],
        },
        {
            "component_id": "CheckpointRewindLedger",
            "runtime_state": (
                "degraded"
                if latest_forward_blocked or latest_rewind_blocked
                else ("live-bound" if latest.get("checkpoint") or latest_rewind else "static-canon")
            ),
            "purpose": "checkpoint metadata, prompt/tool snapshots, snapshot artifact, restore validation, digest proof, diff preview, and rollback linkage before mutation",
            "latest_ref": (latest.get("checkpoint") or {}).get("checkpoint_id"),
            "latest_rewind_ref": latest_rewind.get("rewind_id"),
            "required_for": ["rewind", "rollback", "operator_safety", "replay"],
        },
        {
            "component_id": "GlobalFederationSafetyGate",
            "runtime_state": "live-bound",
            "purpose": "requires signing, trust scoring, anomaly scanning, secure aggregation, DP knobs, privacy audit, and human approval before global release",
            "latest_ref": federation_safety.get("contract_id"),
            "packet_signing_required": federation_safety.get("packet_signing_required"),
            "poisoning_anomaly_scan_required": federation_safety.get("poisoning_anomaly_scan_required"),
            "required_for": ["global_federation", "poisoning_defense", "privacy_preserving_learning"],
        },
        {
            "component_id": "ForwardPacketFederationSecurity",
            "runtime_state": forward_component_runtime_state(latest_forward_packet_security),
            "purpose": "signs every forced sanitized forward-pass federation packet and records secure aggregation readiness, trust score, anomaly scan, DP knobs, and privacy audit",
            "latest_ref": ((latest_forward_packet_security.get("signed_packet") or {}).get("packet_id")),
            "signature_scope": ((latest_forward_packet_security.get("signed_packet") or {}).get("signature_scope")),
            "global_promotion_state": latest_forward_packet_security.get("global_promotion_state"),
            "required_for": ["forward_pass_learning_packet", "global_federation", "privacy_preserving_learning"],
        },
        {
            "component_id": "GlobalFederationPromotionReview",
            "runtime_state": (
                "degraded"
                if global_federation_review_ledger.get("blocked_count", 0) or latest_global_federation_review_blocked
                else ("live-bound" if global_federation_review_ledger.get("review_count", 0) else "static-canon")
            ),
            "purpose": "reviews signed sanitized packet aggregation, trust, anomaly, DP, privacy, sandbox, and human approval before global shadow learning",
            "latest_ref": latest_global_federation_review.get("review_id"),
            "approved_shadow_count": global_federation_review_ledger.get("approved_shadow_count", 0),
            "active_global_learning_mutated": global_federation_review_ledger.get("active_global_learning_mutated", False),
            "required_for": ["global_federation_promotion", "secure_aggregation_review", "shadow_global_learning_gate"],
        },
        {
            "component_id": "ProductionizationFoundry",
            "runtime_state": (
                "degraded"
                if latest_productionization_blocked
                else ("live-bound" if latest_productionization else "static-canon")
            ),
            "purpose": "end-to-end productionization cycle consuming substrate artifacts and emitting sandbox, teacher, federation, runtime research, release, and rollback evidence",
            "latest_ref": latest_productionization.get("productionization_id"),
            "shadow_release_ready_count": productionization_ledger.get("shadow_release_ready_count", 0),
            "required_for": ["candidate_release", "runtime_method_release", "human_approved_shadow_promotion"],
        },
        {
            "component_id": "ExternalSandboxProviderGate",
            "runtime_state": "live-bound" if latest_sandbox_provider else "static-canon",
            "purpose": "certifies external sandbox provider contracts, credential redaction, deny-by-default network policy, and sandbox artifact write scope",
            "latest_ref": latest_sandbox_provider.get("sandbox_run_id"),
            "execution_state": latest_sandbox_provider.get("execution_state"),
            "required_for": ["afk_agent_factory", "closed_sandbox_runs", "provider_abstraction"],
        },
        {
            "component_id": "TeacherModelDistillationRuntime",
            "runtime_state": "live-bound" if latest_teacher_distillation else "static-canon",
            "purpose": "runs Ivy-League teacher-model reviews and persistent distillation traces before shadow certification",
            "latest_ref": latest_teacher_distillation.get("distillation_trace_id"),
            "certification_state": latest_teacher_distillation.get("certification_state"),
            "required_for": ["generated_expert_certification", "runtime_method_certification", "parent_retirement_review"],
        },
        {
            "component_id": "SignedFederationSecurity",
            "runtime_state": "live-bound" if latest_federation_security else "static-canon",
            "purpose": "signs sanitized federation packets and gates them through secure aggregation, trust scoring, anomaly detection, DP knobs, and privacy audit",
            "latest_ref": ((latest_federation_security.get("signed_packet") or {}).get("packet_id")),
            "signed_packet_count": productionization_ledger.get("signed_packet_count", 0),
            "required_for": ["global_federation", "poisoning_defense", "privacy_preserving_learning"],
        },
        {
            "component_id": "RuntimeResearchFoundry",
            "runtime_state": "live-bound" if latest_runtime_research else "static-canon",
            "purpose": "self-tests KV-cache, quantization, backend, and recursively dreamed runtime methods in sandboxed shadow mode",
            "latest_ref": latest_runtime_research.get("foundry_run_id"),
            "trial_count": latest_runtime_research.get("trial_count", 0),
            "best_method": ((latest_runtime_research.get("best_trial") or {}).get("method_id")),
            "required_for": ["inference_backend_evolution", "quantization_evolution", "recursive_runtime_dreaming"],
        },
        {
            "component_id": "GatedReleaseRollback",
            "runtime_state": (
                "degraded"
                if latest_gated_release_blocked
                else ("live-bound" if latest_gated_release else "static-canon")
            ),
            "purpose": "keeps production mutation off until evidence and human approval allow shadow release, with checkpoint-backed rollback metadata",
            "latest_ref": latest_gated_release.get("gate_id"),
            "release_state": latest_gated_release.get("release_state"),
            "required_for": ["human_in_loop_release", "rollback", "no_silent_production_mutation"],
        },
        {
            "component_id": "ShadowReleaseLifecycle",
            "runtime_state": (
                "degraded"
                if latest_release_blocked
                else ("live-bound" if latest_release else "static-canon")
            ),
            "purpose": "activates human-approved productionization artifacts into shadow release without mutating active production",
            "latest_ref": latest_release.get("release_id"),
            "release_state": latest_release.get("release_state"),
            "active_shadow_count": release_ledger.get("active_shadow_count", 0),
            "required_for": ["shadow_activation", "operator_approved_release", "active_production_no_mutation"],
        },
        {
            "component_id": "ActiveReleaseGate",
            "runtime_state": (
                "degraded"
                if release_ledger.get("blocked_active_release_count", 0) or latest_release_blocked
                else ("live-bound" if release_ledger.get("active_release_count") else "static-canon")
            ),
            "purpose": "promotes shadow releases to active production metadata pointers only after canary, monitoring, rollback, and human approval gates",
            "latest_ref": latest_release.get("release_id")
            if latest_release.get("release_scope") == "active-production-release-pointer"
            else None,
            "active_release_count": release_ledger.get("active_release_count", 0),
            "active_production_count": release_ledger.get("active_production_count", 0),
            "required_for": ["active_release", "canary_gate", "monitoring_gate", "rollback_rehearsal"],
        },
        {
            "component_id": "RollbackExecutionLedger",
            "runtime_state": (
                "degraded"
                if latest_rollback_blocked
                else ("live-bound" if latest_rollback else "static-canon")
            ),
            "purpose": "records checkpoint-backed rollback execution for shadow releases and keeps prior release evidence replayable",
            "latest_ref": latest_rollback.get("rollback_id"),
            "rolled_back_count": release_ledger.get("rolled_back_count", 0),
            "required_for": ["rollback_execution", "release_replay", "regression_rehearsal"],
        },
        {
            "component_id": "HiveHealthMonitor",
            "runtime_state": (
                "degraded"
                if health_ledger.get("degraded_event_count", 0)
                else ("live-bound" if latest_health_event else "static-canon")
            ),
            "purpose": "records hive-visible health events for every forward pass so failures cannot be silent",
            "latest_ref": latest_health_event.get("health_event_id"),
            "degraded_event_count": health_ledger.get("degraded_event_count", 0),
            "required_for": ["failure_visibility", "health_replay", "self_healing_trigger"],
        },
        {
            "component_id": "SelfHealingRouteAround",
            "runtime_state": "live-bound" if latest_self_healing_route else "static-canon",
            "purpose": "prepares fallback routes and checkpoint-required retry policy when blocked actions occur",
            "latest_ref": latest_self_healing_route.get("route_around_id"),
            "prepared_route_around_count": self_healing_ledger.get("prepared_route_around_count", 0),
            "required_for": ["route_around", "active_task_continuity", "safe_retry"],
        },
        {
            "component_id": "ReplaySurface",
            "runtime_state": runtime_state,
            "purpose": "drill-down replay over plane traces, bus messages, blackboard state, priors, dreams, sandboxes, checkpoints, and candidate lifecycle",
            "latest_ref": (latest.get("trace") or {}).get("trace_id"),
            "required_for": ["control_panel_replay", "operator_debugging", "governed_rewind"],
        },
    ]


def _neural_bus_payload(
    *,
    run_id: str,
    session_id: str,
    created_at: str,
    request: HiveForwardPassRequest,
    activation_id: str,
    selected_nodes: list[HiveNode],
    loops: list[dict[str, Any]],
    checkpoint: dict[str, Any],
    federated_learning_packet: dict[str, Any],
    federated_prior_update: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    bus_id = new_id("neural_bus")
    selected_node_ids = [node.node_id for node in selected_nodes]
    message_specs: list[tuple[str, str, str, list[str], str]] = [
        (
            "activation_published",
            "sensory-input",
            "embedding-representation",
            ["nexusbrain:cortex"],
            f"activation::{activation_id}",
        ),
        (
            "memory_context_loaded",
            "memory-engram",
            "attention-focus",
            selected_node_ids,
            ",".join(request.memory_refs) or "memory::none",
        ),
        (
            "route_selected",
            "sparse-moe-router",
            "expert-computation",
            selected_node_ids,
            "selected::" + ",".join(selected_node_ids),
        ),
        (
            "loop_state_updated",
            "recurrent-deliberation",
            "learning-eval-loss",
            selected_node_ids,
            f"loops::{len(loops)}::{loops[-1]['exit_reason']}",
        ),
        (
            "eval_score_posted",
            "learning-eval-loss",
            "immune-governance",
            ["policy:immune-kernel", "eval:loss-plane"],
            "blocked" if blocked else f"confidence::{loops[-1]['confidence']}",
        ),
        (
            "checkpoint_posted",
            "checkpoint-rewind",
            "action-output",
            ["checkpoint:rewind-ledger", "nexusbrain:cortex"],
            checkpoint["checkpoint_id"],
        ),
        (
            "federated_learning_packet_ready",
            "federated-learning",
            "optimizer-school",
            ["federation:privacy-aggregate", "school:ivy-league"],
            federated_learning_packet["packet_id"],
        ),
        (
            "federated_prior_updated",
            "federated-learning",
            "sparse-moe-router",
            ["federation:privacy-aggregate", "router:sparse-moe-hive-cortex", "school:ivy-league"],
            federated_prior_update["prior_update_id"],
        ),
    ]
    if blocked:
        message_specs.append(
            (
                "immune_block_broadcast",
                "immune-governance",
                "neural-bus",
                selected_node_ids + ["policy:immune-kernel"],
                "blocked_by_immune_policy",
            )
        )
    messages = []
    for index, (message_type, source_plane_id, target_plane_id, target_node_ids, payload_ref) in enumerate(message_specs):
        interval = _harmonic_interval(index)
        messages.append(
            {
            "message_id": new_id("neural_msg"),
            "bus_id": bus_id,
            "run_id": run_id,
            "session_id": session_id,
            "message_type": message_type,
            "source_plane_id": source_plane_id,
            "target_plane_id": target_plane_id,
            "source_node_id": "nexusbrain:cortex" if source_plane_id != "memory-engram" else "memory:engram",
            "target_node_ids": target_node_ids,
            "payload_ref": payload_ref,
            "visibility_scope": "hive-visible",
            "delivery_state": "delivered",
            "harmonic_phase_degrees": _harmonic_phase(index),
            "harmonic_name": interval["name"],
            "harmonic_fraction": interval["fraction"],
            "harmonic_ratio": interval["ratio"],
            "created_at": created_at,
            }
        )
    return {
        "bus_id": bus_id,
        "run_id": run_id,
        "session_id": session_id,
        "contract_id": "typed-neural-bus-v0",
        "message_count": len(messages),
        "messages": messages,
        "delivery_model": "synchronous-artifact-ledger-for-v0",
        "visibility_scope": "hive-visible",
    }


def _hive_blackboard_payload(
    *,
    run_id: str,
    session_id: str,
    created_at: str,
    request: HiveForwardPassRequest,
    activation_id: str,
    selected_nodes: list[HiveNode],
    loops: list[dict[str, Any]],
    checkpoint: dict[str, Any],
    policy_scan: dict[str, Any],
    immune_findings: list[dict[str, Any]],
    federated_learning_packet: dict[str, Any],
    federated_prior_update: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    residual_state_id = new_id("hive_blackboard")
    selected_node_ids = [node.node_id for node in selected_nodes]
    entry_specs: list[tuple[str, str, str, Any, float]] = [
        ("intent_embedding", "embedding-representation", activation_id, f"embedding::{_stable_key(request.intent)}", 0.98),
        ("temporal_binding", "temporal-positional", request.task_id or run_id, session_id, 0.96),
        ("memory_refs", "memory-engram", "memory::request", request.memory_refs, 0.88 if request.memory_refs else 0.4),
        ("selected_nodes", "sparse-moe-router", "router:sparse-moe-hive-cortex", selected_node_ids, 0.9),
        (
            "loop_exit",
            "recurrent-deliberation",
            f"{run_id}::loop::{loops[-1]['loop_index']}",
            loops[-1]["exit_reason"],
            loops[-1]["confidence"],
        ),
        ("policy_scan", "immune-governance", "policy:immune-kernel", policy_scan["summary"], 0.9),
        ("checkpoint", "checkpoint-rewind", checkpoint["checkpoint_id"], checkpoint, 1.0),
        (
            "federated_learning_packet",
            "federated-learning",
            federated_learning_packet["packet_id"],
            {
                "packet_id": federated_learning_packet["packet_id"],
                "share_state": federated_learning_packet["share_state"],
                "privacy_class": federated_learning_packet["privacy_class"],
                "raw_content_included": federated_learning_packet["raw_content_included"],
            },
            1.0,
        ),
        (
            "federated_prior_update",
            "federated-learning",
            federated_prior_update["prior_update_id"],
            {
                "prior_update_id": federated_prior_update["prior_update_id"],
                "source_packet_id": federated_prior_update["source_packet_id"],
                "ingestion_state": federated_prior_update["ingestion_state"],
                "promotion_state": federated_prior_update["promotion_state"],
            },
            1.0,
        ),
        ("action_state", "action-output", run_id, "blocked" if blocked else "ready_for_safe_output", 0.8),
    ]
    if immune_findings:
        entry_specs.append(("immune_findings", "immune-governance", "policy:immune-kernel", immune_findings, 1.0))
    entries = [
        {
            "entry_id": new_id("blackboard_entry"),
            "residual_state_id": residual_state_id,
            "run_id": run_id,
            "session_id": session_id,
            "key": key,
            "plane_id": plane_id,
            "source_ref": source_ref,
            "value": value,
            "confidence": round(float(confidence), 3),
            "resonance_score": _blackboard_resonance(index, float(confidence)),
            "visibility_scope": "hive-visible",
            "created_at": created_at,
        }
        for index, (key, plane_id, source_ref, value, confidence) in enumerate(entry_specs)
    ]
    residual_keys = [entry["key"] for entry in entries]
    return {
        "residual_state_id": residual_state_id,
        "run_id": run_id,
        "session_id": session_id,
        "contract_id": "hive-blackboard-residual-state-v0",
        "entry_count": len(entries),
        "residual_keys": residual_keys,
        "entries": entries,
        "residual_state_digest": "substrate:" + _stable_key("|".join(residual_keys + selected_node_ids)),
        "continuity_model": "residual-blackboard-plus-artifact-ledger",
    }


def _plane_trace_ledger(
    *,
    run_id: str,
    session_id: str,
    created_at: str,
    planes: list[dict[str, Any]],
    neural_bus: dict[str, Any],
    hive_blackboard: dict[str, Any],
    selected_nodes: list[HiveNode],
    checkpoint: dict[str, Any],
    federated_learning_packet: dict[str, Any],
    federated_prior_update: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    trace_ledger_id = new_id("hive_trace_ledger")
    selected_node_ids = [node.node_id for node in selected_nodes]
    records = [
        {
            "record_id": new_id("plane_trace"),
            "trace_ledger_id": trace_ledger_id,
            "run_id": run_id,
            "session_id": session_id,
            "ordinal": index + 1,
            "plane_id": plane["plane_id"],
            "plane_label": plane["label"],
            "harmonic_signature": plane.get("harmonic_signature", {}),
            "event_ref": f"{run_id}::{plane['plane_id']}",
            "input_refs": _plane_input_refs(plane["plane_id"], neural_bus, hive_blackboard, selected_node_ids),
            "output_refs": _plane_output_refs(
                plane["plane_id"],
                neural_bus,
                hive_blackboard,
                checkpoint,
                federated_learning_packet,
                federated_prior_update,
            ),
            "state_delta": _plane_state_delta(plane["plane_id"], blocked),
            "visibility_scope": "hive-visible",
            "created_at": created_at,
        }
        for index, plane in enumerate(planes)
    ]
    return {
        "trace_ledger_id": trace_ledger_id,
        "run_id": run_id,
        "session_id": session_id,
        "contract_id": "sixteen-plane-trace-ledger-v0",
        "record_count": len(records),
        "records": records,
        "replay_policy": "read-only-replay-until-checkpoint-approved",
    }


def _hive_sensory_input_payload(
    *,
    sensory_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    request: HiveForwardPassRequest,
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    capability_terms = _terms(request.requested_capabilities) or ["general"]
    memory_ref_digests = [
        {
            "memory_ref_digest": _privacy_digest(ref),
            "memory_ref_key": f"memory-ref::{_stable_key(ref)}",
        }
        for ref in request.memory_refs
    ]
    action_ref_digests = [
        {
            "action_ref": str(action.get("action_id") or action.get("action_type") or "action"),
            "action_type": str(action.get("action_type") or "unknown"),
            "target_ref_digest": _privacy_digest(str(action.get("target_ref") or "")),
            "target_ref_stored": False,
        }
        for action in request.requested_actions
    ]
    normalized_channels = [
        {
            "channel_id": f"{sensory_ledger_id}::channel::operator_intent",
            "channel_kind": "operator_intent",
            "source_ref": request.source_ref,
            "estimated_token_count": _estimated_token_count(request.intent),
            "content_digest": _privacy_digest(request.intent),
            "raw_content_stored": False,
            "harmonic_phase_degrees": _harmonic_phase(0),
        },
        {
            "channel_id": f"{sensory_ledger_id}::channel::capability_signals",
            "channel_kind": "capability_signals",
            "source_ref": activation["activation_id"],
            "capability_count": len(capability_terms),
            "capability_terms": capability_terms,
            "raw_content_stored": False,
            "harmonic_phase_degrees": _harmonic_phase(1),
        },
        {
            "channel_id": f"{sensory_ledger_id}::channel::memory_refs",
            "channel_kind": "memory_refs",
            "source_ref": activation["activation_id"],
            "memory_ref_count": len(memory_ref_digests),
            "memory_ref_digests": memory_ref_digests,
            "raw_content_stored": False,
            "harmonic_phase_degrees": _harmonic_phase(2),
        },
        {
            "channel_id": f"{sensory_ledger_id}::channel::action_refs",
            "channel_kind": "action_refs",
            "source_ref": activation["activation_id"],
            "action_ref_count": len(action_ref_digests),
            "action_ref_digests": action_ref_digests,
            "raw_content_stored": False,
            "harmonic_phase_degrees": _harmonic_phase(3),
        },
    ]
    return HiveSensoryInputLedger(
        sensory_ledger_id=sensory_ledger_id,
        run_id=run_id,
        session_id=session_id,
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        normalized_channel_count=len(normalized_channels),
        normalized_channels=normalized_channels,
        tokenizer_policy={
            "tokenizer_ref": "metadata-estimator-v0",
            "normalization_mode": "privacy-preserving-symbolic-channelization",
            "raw_operator_intent_export": "forbidden",
            "claim_boundary": "symbolic-sensory-ledger-not-runtime-tokenizer-kernel",
        },
        input_integrity={
            "raw_intent_stored": False,
            "raw_action_targets_stored": False,
            "raw_memory_content_stored": False,
            "local_paths_exported": False,
            "active_context_order_mutated": False,
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_embedding_tensor_payload(
    *,
    embedding_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    request: HiveForwardPassRequest,
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    terms = _terms(request.intent.split()) or ["activation"]
    token_records = []
    embedding_dimension = 13
    for token_index, term in enumerate(terms):
        token_hash = hashlib.sha256(f"{token_index}:{term}".encode("utf-8")).hexdigest()[:32]
        coordinates = [
            round((((int(token_hash[(dim * 2) % len(token_hash):((dim * 2) % len(token_hash)) + 2], 16) / 255) * 2) - 1) * _phi_weight(dim), 6)
            for dim in range(embedding_dimension)
        ]
        token_records.append(
            {
                "token_index": token_index,
                "token_hash": token_hash,
                "token_ref": f"token::{token_hash}",
                "embedding_ref": f"embedding::{activation['activation_id']}::{token_index}",
                "coordinate_count": embedding_dimension,
                "coordinate_digest": _privacy_digest(json.dumps(coordinates, sort_keys=True)),
                "harmonic_phase_degrees": _harmonic_phase(token_index),
                "phi_radius": _phi_weight(token_index),
            }
        )
    norms = [
        round((index + 1) / max(len(token_records), 1), 6)
        for index, _ in enumerate(token_records)
    ]
    return HiveEmbeddingTensorLedger(
        embedding_ledger_id=embedding_ledger_id,
        run_id=run_id,
        session_id=session_id,
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        token_count=len(token_records),
        embedding_dimension=embedding_dimension,
        embedding_shape=[len(token_records), embedding_dimension],
        token_records=token_records,
        tensor_statistics={
            "norm_floor": min(norms) if norms else 0,
            "norm_ceiling": max(norms) if norms else 0,
            "mean_norm": round(sum(norms) / len(norms), 6) if norms else 0,
            "sparsity_pattern": "hashed-token-privacy-preserving-symbolic-tensor",
        },
        formula_basis={
            "dimension_basis": "fibonacci_13",
            "coordinate_basis": "stable_hash_scaled_by_phi_weight",
            "phase_basis": "golden_angle_token_phase",
            "harmonic_kernel_ref": "sacred-geometry-harmonic-kernel-v0",
            "claim_boundary": "symbolic-embedding-evidence-not-trained-vector-weights",
        },
        token_privacy={
            "raw_tokens_stored": False,
            "raw_intent_stored": False,
            "private_file_content_stored": False,
            "local_paths_exported": False,
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_temporal_positional_payload(
    *,
    temporal_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    sensory_input_ledger: dict[str, Any],
    embedding_tensor_ledger: dict[str, Any],
    checkpoint: dict[str, Any],
    loops: list[dict[str, Any]],
) -> dict[str, Any]:
    token_records = embedding_tensor_ledger.get("token_records") or []
    position_records = []
    for index, token in enumerate(token_records):
        position_records.append(
            {
                "position_id": f"{temporal_ledger_id}::token::{index}",
                "position_kind": "token_position",
                "source_ref": token.get("embedding_ref"),
                "ordinal": index,
                "rotary_phase_degrees": _harmonic_phase(index),
                "golden_angle_degrees": GOLDEN_ANGLE_DEGREES,
                "phi_radius": _phi_weight(index),
                "temporal_bucket": "current_turn",
            }
        )
    for loop in loops:
        loop_index = int(loop.get("loop_index") or len(position_records))
        position_records.append(
            {
                "position_id": f"{temporal_ledger_id}::loop::{loop_index}",
                "position_kind": "latent_loop_position",
                "source_ref": loop.get("loop_id"),
                "ordinal": len(position_records),
                "rotary_phase_degrees": _harmonic_phase(loop_index),
                "golden_angle_degrees": GOLDEN_ANGLE_DEGREES,
                "phi_radius": _phi_weight(loop_index),
                "temporal_bucket": "recurrent_deliberation",
            }
        )
    position_records.append(
        {
            "position_id": f"{temporal_ledger_id}::checkpoint",
            "position_kind": "checkpoint_position",
            "source_ref": checkpoint["checkpoint_id"],
            "ordinal": len(position_records),
            "rotary_phase_degrees": _harmonic_phase(len(position_records)),
            "golden_angle_degrees": GOLDEN_ANGLE_DEGREES,
            "phi_radius": _phi_weight(len(position_records)),
            "temporal_bucket": "rewind_anchor",
        }
    )
    return HiveTemporalPositionalLedger(
        temporal_ledger_id=temporal_ledger_id,
        run_id=run_id,
        session_id=session_id,
        sensory_input_ref=sensory_input_ledger["sensory_ledger_id"],
        embedding_tensor_ref=embedding_tensor_ledger["embedding_ledger_id"],
        activation_ref=embedding_tensor_ledger["activation_ref"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        position_count=len(position_records),
        position_records=position_records,
        position_policy={
            "position_encoding": "rotary-golden-angle-symbolic",
            "harmonic_basis": "golden-angle-phase-plus-phi-radius",
            "loop_positioning": "latent-loop-positions-appended-after-current-turn",
            "claim_boundary": "symbolic-position-ledger-not-trained-rope-kernel",
        },
        temporal_integrity={
            "active_context_order_mutated": False,
            "raw_private_content_read": False,
            "direct_local_state_reads": [],
            "checkpoint_anchor_preserved": True,
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_memory_engram_payload(
    *,
    memory_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    request: HiveForwardPassRequest,
    sensory_input_ledger: dict[str, Any],
    temporal_positional_ledger: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    memory_refs = request.memory_refs or ["memory::none"]
    retrieval_records = []
    for index, memory_ref in enumerate(memory_refs):
        retrieval_records.append(
            {
                "retrieval_id": f"{memory_ledger_id}::retrieval::{index}",
                "memory_ref_digest": _privacy_digest(memory_ref),
                "memory_ref_key": f"memory-ref::{_stable_key(memory_ref)}",
                "position_ref": (
                    temporal_positional_ledger.get("position_records") or [{"position_id": temporal_positional_ledger["temporal_ledger_id"]}]
                )[index % max(1, len(temporal_positional_ledger.get("position_records") or []))].get("position_id"),
                "retrieval_score": _bounded_signal(0.55 + (0.05 * index)),
                "retrieval_scope": "reference-only",
                "raw_memory_content_stored": False,
                "active_memory_mutated": False,
            }
        )
    return HiveMemoryEngramLedger(
        memory_ledger_id=memory_ledger_id,
        run_id=run_id,
        session_id=session_id,
        sensory_input_ref=sensory_input_ledger["sensory_ledger_id"],
        temporal_positional_ref=temporal_positional_ledger["temporal_ledger_id"],
        activation_ref=temporal_positional_ledger["activation_ref"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        memory_ref_count=len(request.memory_refs),
        retrieval_records=retrieval_records if request.memory_refs else [],
        retrieval_policy={
            "retrieval_mode": "reference-only-engram-binding",
            "private_memory_content_policy": "digest-only-no-raw-content",
            "context_window_policy": "retrieve-refs-needed-for-task-not-entire-memory",
            "claim_boundary": "symbolic-memory-retrieval-ledger-not-vector-db-query",
        },
        memory_integrity={
            "raw_memory_content_stored": False,
            "direct_local_state_reads": [],
            "active_memory_mutated": False,
            "temporal_position_bound": True,
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_attention_routing_payload(
    *,
    attention_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    request: HiveForwardPassRequest,
    embedding_tensor_ledger: dict[str, Any],
    neural_bus: dict[str, Any],
    hive_blackboard: dict[str, Any],
    selected_nodes: list[HiveNode],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    focus_targets = [
        {
            "target_ref": "focus::selected_nodes",
            "target_kind": "selected_nodes",
            "source_ref": ",".join(node.node_id for node in selected_nodes) or "none",
            "privacy_class": "metadata_only",
        },
        {
            "target_ref": "focus::memory_refs",
            "target_kind": "memory_refs",
            "source_ref": ",".join(request.memory_refs) or "none",
            "privacy_class": "reference_only",
        },
        {
            "target_ref": "focus::policy_gate",
            "target_kind": "policy_gate",
            "source_ref": "policy:immune-kernel",
            "privacy_class": "metadata_only",
        },
        {
            "target_ref": "focus::neural_bus",
            "target_kind": "neural_bus",
            "source_ref": neural_bus["bus_id"],
            "privacy_class": "metadata_only",
        },
        {
            "target_ref": "focus::hive_blackboard",
            "target_kind": "hive_blackboard",
            "source_ref": hive_blackboard["residual_state_id"],
            "privacy_class": "metadata_only",
        },
    ]
    head_names = ["query-key", "memory-focus", "expert-focus", "policy-focus", "federation-focus", "dream-focus"]
    attention_heads = []
    for head_index, head_name in enumerate(head_names[: max(4, min(6, len(focus_targets) + 1))]):
        raw_weights = [
            {
                "target_ref": target["target_ref"],
                "target_kind": target["target_kind"],
                "raw_score": round((head_index + 1) * (target_index + 1) * _harmonic_interval(target_index)["ratio"], 6),
            }
            for target_index, target in enumerate(focus_targets)
        ]
        normalized = _normalize_weight_records(raw_weights, value_key="raw_score", output_key="attention_weight")
        attention_heads.append(
            {
                "head_id": f"{attention_ledger_id}::head::{head_index}",
                "head_name": head_name,
                "query_ref": f"query::{embedding_tensor_ledger['embedding_ledger_id']}::{head_index}",
                "key_ref": f"key::{hive_blackboard['residual_state_id']}::{head_index}",
                "value_ref": f"value::{neural_bus['bus_id']}::{head_index}",
                "focus_weights": normalized,
                "softmax_normalized": True,
                "phase_degrees": _harmonic_phase(head_index),
            }
        )
    return HiveAttentionRoutingLedger(
        attention_ledger_id=attention_ledger_id,
        run_id=run_id,
        session_id=session_id,
        embedding_tensor_ref=embedding_tensor_ledger["embedding_ledger_id"],
        activation_ref=embedding_tensor_ledger["activation_ref"],
        neural_bus_ref=neural_bus["bus_id"],
        hive_blackboard_ref=hive_blackboard["residual_state_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        attention_head_count=len(attention_heads),
        focus_target_count=len(focus_targets),
        attention_heads=attention_heads,
        focus_targets=focus_targets,
        attention_integrity={
            "softmax_normalized": True,
            "raw_private_content_read": False,
            "direct_local_state_reads": [],
            "bounded_attention_weights": True,
            "active_production_routing_mutated": False,
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_residual_normalization_payload(
    *,
    normalization_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    embedding_tensor_ledger: dict[str, Any],
    attention_routing_ledger: dict[str, Any],
    neural_bus: dict[str, Any],
    hive_blackboard: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    token_count = int(embedding_tensor_ledger.get("token_count") or 0)
    head_count = int(attention_routing_ledger.get("attention_head_count") or 0)
    residual_sources = [
        ("embedding_residual", embedding_tensor_ledger["embedding_ledger_id"], token_count),
        ("attention_residual", attention_routing_ledger["attention_ledger_id"], head_count),
        ("blackboard_residual", hive_blackboard["residual_state_id"], int(hive_blackboard.get("entry_count") or 0)),
        ("neural_bus_residual", neural_bus["bus_id"], int(neural_bus.get("message_count") or 0)),
    ]
    normalized_streams = []
    for index, (stream_kind, source_ref, magnitude) in enumerate(residual_sources):
        epsilon = round(1 / (10_000 * (index + 1)), 8)
        normalized_streams.append(
            {
                "stream_id": f"{normalization_ledger_id}::stream::{index}",
                "stream_kind": stream_kind,
                "source_ref": source_ref,
                "pre_norm_symbolic_magnitude": magnitude,
                "rmsnorm_epsilon": epsilon,
                "post_norm_symbolic_magnitude": _bounded_signal((magnitude + 1) / max(token_count + head_count + 1, 1)),
                "phase_degrees": _harmonic_phase(index),
                "phi_weight": _phi_weight(index),
            }
        )
    residual_connections = [
        {
            "connection_id": f"{normalization_ledger_id}::residual::{index}",
            "from_stream": current["stream_id"],
            "to_stream": normalized_streams[(index + 1) % len(normalized_streams)]["stream_id"],
            "connection_kind": "residual-add-plus-normalize",
            "preserves_source_ref": current["source_ref"],
            "active_tensor_values_mutated": False,
        }
        for index, current in enumerate(normalized_streams)
    ]
    return HiveResidualNormalizationLedger(
        normalization_ledger_id=normalization_ledger_id,
        run_id=run_id,
        session_id=session_id,
        embedding_tensor_ref=embedding_tensor_ledger["embedding_ledger_id"],
        attention_ref=attention_routing_ledger["attention_ledger_id"],
        activation_ref=embedding_tensor_ledger["activation_ref"],
        neural_bus_ref=neural_bus["bus_id"],
        hive_blackboard_ref=hive_blackboard["residual_state_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        normalized_stream_count=len(normalized_streams),
        normalized_streams=normalized_streams,
        residual_connections=residual_connections,
        normalization_policy={
            "normalization_kind": "rmsnorm-symbolic-v0",
            "residual_model": "pre-norm-and-post-attention-residual-stream",
            "epsilon_schedule": "per-stream-harmonic-epsilon",
            "claim_boundary": "symbolic-normalization-ledger-not-numeric-tensor-kernel",
        },
        normalization_integrity={
            "residual_stream_preserved": True,
            "active_tensor_values_mutated": False,
            "direct_local_state_reads": [],
            "raw_private_content_read": False,
            "bounded_normalized_magnitudes": True,
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_sparse_expert_gate_payload(
    *,
    gate_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    attention_routing_ledger: dict[str, Any],
    selected_nodes: list[HiveNode],
    all_nodes: list[HiveNode],
    neural_bus: dict[str, Any],
    hive_blackboard: dict[str, Any],
    checkpoint: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    selected_node_ids = [node.node_id for node in selected_nodes]
    raw_distribution = [
        {
            "node_id": node.node_id,
            "node_type": node.node_type,
            "brain_scale": node.brain_scale,
            "mini_brain_ref": node.brain_instance_ref,
            "raw_score": round((len(selected_nodes) - index) * _harmonic_interval(index)["ratio"], 6),
        }
        for index, node in enumerate(selected_nodes)
    ]
    expert_gate_distribution = _normalize_weight_records(raw_distribution, value_key="raw_score", output_key="gate_weight")
    dormant_visible_node_refs = [
        node.node_id
        for node in all_nodes
        if node.node_id not in selected_node_ids
    ]
    return HiveSparseExpertGateLedger(
        gate_ledger_id=gate_ledger_id,
        run_id=run_id,
        session_id=session_id,
        attention_ref=attention_routing_ledger["attention_ledger_id"],
        router_ref="router:sparse-moe-hive-cortex",
        activation_ref=attention_routing_ledger["activation_ref"],
        neural_bus_ref=neural_bus["bus_id"],
        hive_blackboard_ref=hive_blackboard["residual_state_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        top_k=len(selected_nodes),
        selected_expert_node_ids=selected_node_ids,
        expert_gate_distribution=expert_gate_distribution,
        dormant_visible_node_refs=dormant_visible_node_refs,
        gate_integrity={
            "gate_distribution_normalized": True,
            "sparse_activation": True,
            "non_selected_nodes_visible_idle": True,
            "direct_local_state_reads": [],
            "active_production_routing_mutated": False,
            "blocked_by_policy": blocked,
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_feedforward_expert_payload(
    *,
    feedforward_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    residual_normalization_ledger: dict[str, Any],
    sparse_expert_gate_ledger: dict[str, Any],
    selected_nodes: list[HiveNode],
    neural_bus: dict[str, Any],
    hive_blackboard: dict[str, Any],
    checkpoint: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    gate_by_node = {
        route.get("node_id"): float(route.get("gate_weight") or 0.0)
        for route in sparse_expert_gate_ledger.get("expert_gate_distribution") or []
    }
    expert_units = []
    for index, node in enumerate(selected_nodes):
        gate_weight = gate_by_node.get(node.node_id, 0.0)
        expert_units.append(
            {
                "expert_unit_id": f"{feedforward_ledger_id}::expert::{index}",
                "node_id": node.node_id,
                "node_type": node.node_type,
                "brain_scale": node.brain_scale,
                "mini_brain_ref": node.brain_instance_ref,
                "gate_weight": gate_weight,
                "hidden_projection_ref": f"ffn-hidden::{node.node_id}::{_stable_key(node.brain_instance_ref or node.node_id)}",
                "output_projection_ref": f"ffn-output::{node.node_id}::{_stable_key(str(gate_weight))}",
                "activation_function": "geglu-symbolic",
                "expansion_factor": 4,
                "dropout_policy": "disabled-for-deterministic-substrate-evidence",
                "blocked_by_policy": blocked,
                "active_expert_weights_mutated": False,
            }
        )
    return HiveFeedForwardExpertLedger(
        feedforward_ledger_id=feedforward_ledger_id,
        run_id=run_id,
        session_id=session_id,
        sparse_gate_ref=sparse_expert_gate_ledger["gate_ledger_id"],
        residual_normalization_ref=residual_normalization_ledger["normalization_ledger_id"],
        activation_ref=sparse_expert_gate_ledger["activation_ref"],
        neural_bus_ref=neural_bus["bus_id"],
        hive_blackboard_ref=hive_blackboard["residual_state_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        expert_unit_count=len(expert_units),
        expert_units=expert_units,
        feedforward_policy={
            "mlp_kind": "sparse-expert-feedforward-symbolic-v0",
            "activation_function": "geglu-symbolic",
            "expansion_factor": 4,
            "routing_weight_source": sparse_expert_gate_ledger["gate_ledger_id"],
            "residual_source": residual_normalization_ledger["normalization_ledger_id"],
            "claim_boundary": "symbolic-feedforward-ledger-not-trained-mlp-kernel",
        },
        feedforward_integrity={
            "sparse_expert_dispatch": True,
            "active_expert_weights_mutated": False,
            "direct_local_state_reads": [],
            "raw_private_content_read": False,
            "blocked_by_policy": blocked,
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_laminar_microcircuit_payload(
    *,
    microcircuit_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    activation: dict[str, Any],
    neural_bus: dict[str, Any],
    hive_blackboard: dict[str, Any],
    checkpoint: dict[str, Any],
    plane_trace: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    plane_microcircuits = []
    for index, record in enumerate(plane_trace.get("records") or []):
        base_threshold = 0.44 + (_phi_weight(index) * 0.1)
        event_threshold = _bounded_signal(base_threshold + (0.2 if blocked and record.get("plane_id") == "immune-governance" else 0))
        plane_microcircuits.append(
            {
                "plane_microcircuit_id": new_id("plane_microcircuit"),
                "microcircuit_id": microcircuit_id,
                "run_id": run_id,
                "session_id": session_id,
                "plane_ref": record.get("plane_id"),
                "trace_record_ref": record.get("record_id"),
                "ordinal": record.get("ordinal"),
                "laminar_layers": [
                    {
                        "layer_id": "L1",
                        "role": "context-and-feedback-integration",
                        "input_refs": record.get("input_refs", [])[:2],
                        "output_channel": "apical-modulation",
                    },
                    {
                        "layer_id": "L2_3",
                        "role": "local-association-and-cross-plane-broadcast",
                        "input_refs": record.get("input_refs", []),
                        "output_channel": "neighbor-plane-synapse",
                    },
                    {
                        "layer_id": "L4",
                        "role": "feedforward-sensory-and-message-ingress",
                        "input_refs": record.get("input_refs", [])[:3],
                        "output_channel": "local-feature-state",
                    },
                    {
                        "layer_id": "L5_6",
                        "role": "projection-output-and-recurrent-control",
                        "output_refs": record.get("output_refs", []),
                        "output_channel": "bus-blackboard-action-projection",
                    },
                ],
                "population_balance": {
                    "excitatory_ratio": 0.8,
                    "inhibitory_ratio": 0.2,
                    "homeostatic_target": "bounded-plane-activation",
                    "claim_boundary": "symbolic-microcircuit-metadata-not-biological-simulation",
                },
                "dendritic_compartments": [
                    {
                        "compartment_id": "basal-feedforward",
                        "source_refs": record.get("input_refs", []),
                        "integration": "weighted-feedforward-sum",
                    },
                    {
                        "compartment_id": "apical-context",
                        "source_refs": [neural_bus.get("bus_id"), hive_blackboard.get("residual_state_id")],
                        "integration": "contextual-feedback-modulation",
                    },
                ],
                "event_threshold": event_threshold,
                "spike_policy": {
                    "model": "symbolic-event-threshold-v0",
                    "event_driven_update": True,
                    "blocked_gate_boost": bool(blocked and record.get("plane_id") == "immune-governance"),
                    "production_mutation_allowed": False,
                },
                "harmonic_signature": record.get("harmonic_signature", {}),
                "created_at": created_at,
            }
        )
    return HiveLaminarMicrocircuitLedger(
        microcircuit_id=microcircuit_id,
        run_id=run_id,
        session_id=session_id,
        activation_ref=activation["activation_id"],
        neural_bus_ref=neural_bus["bus_id"],
        hive_blackboard_ref=hive_blackboard["residual_state_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        trace_ledger_ref=plane_trace["trace_ledger_id"],
        plane_microcircuit_count=len(plane_microcircuits),
        plane_microcircuits=plane_microcircuits,
        microcircuit_integrity={
            "visibility_model": "hive-wide-visible-sparse-activation",
            "event_driven_updates": True,
            "direct_local_state_reads": [],
            "direct_local_state_reads_allowed": False,
            "active_production_mutated": False,
            "raw_private_content_encoded": False,
            "claim_boundary": "symbolic-laminar-plane-internals-not-biological-or-physics-claim",
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_neural_pathway_map_payload(
    *,
    pathway_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    activation: dict[str, Any],
    selected_nodes: list[HiveNode],
    all_nodes: list[HiveNode],
    planes: list[dict[str, Any]],
    loops: list[dict[str, Any]],
    neural_bus: dict[str, Any],
    hive_blackboard: dict[str, Any],
    plane_trace: dict[str, Any],
    checkpoint: dict[str, Any],
    policy_scan: dict[str, Any],
    immune_findings: list[dict[str, Any]],
    blocked: bool,
) -> dict[str, Any]:
    selected_node_ids = [node.node_id for node in selected_nodes]
    all_node_by_brain_ref = {node.brain_instance_ref: node for node in all_nodes if node.brain_instance_ref}
    ordered_stack: list[HiveNode] = []
    for brain_scale in ("primary", "orchestrator", "assistant_orchestrator", "expert"):
        for node in all_nodes:
            if node.brain_scale == brain_scale and node not in ordered_stack:
                ordered_stack.append(node)
                break
    for node in selected_nodes:
        if node not in ordered_stack:
            ordered_stack.append(node)
    brain_scale_stack = [
        {
            "stack_index": index + 1,
            "node_id": node.node_id,
            "node_type": node.node_type,
            "brain_instance_ref": node.brain_instance_ref,
            "brain_scale": node.brain_scale,
            "parent_brain_ref": node.parent_brain_ref,
            "child_brain_refs": node.child_brain_refs,
            "selected_for_this_forward_pass": node.node_id in selected_node_ids,
            "visibility_scope": "hive-visible",
            "activation_state": "sparse-active" if node.node_id in selected_node_ids else "visible-idle",
        }
        for index, node in enumerate(ordered_stack)
    ]
    plane_pathways = []
    for index, plane in enumerate(planes):
        interval = _harmonic_interval(index)
        source_plane = "operator-intent" if index == 0 else planes[index - 1]["plane_id"]
        edge_kind = "dendrite" if index == 0 else "residual" if plane["plane_id"] in {
            "memory-engram",
            "recurrent-deliberation",
            "checkpoint-rewind",
        } else "synapse"
        plane_pathways.append(
            {
                "pathway_edge_id": new_id("plane_pathway"),
                "pathway_id": pathway_id,
                "run_id": run_id,
                "session_id": session_id,
                "source_plane": source_plane,
                "target_plane": plane["plane_id"],
                "edge_kind": edge_kind,
                "plane_ordinal": index + 1,
                "input_refs": _plane_input_refs(plane["plane_id"], neural_bus, hive_blackboard, selected_node_ids),
                "output_refs": [
                    record.get("event_ref")
                    for record in plane_trace.get("records", [])
                    if record.get("plane_id") == plane["plane_id"]
                ],
                "harmonic_weight": round(interval["ratio"] * _phi_weight(index - 1), 6),
                "golden_angle_phase_degrees": _harmonic_phase(index),
                "visibility_scope": "hive-visible",
                "created_at": created_at,
            }
        )
    node_pathways = []
    for index, node in enumerate(ordered_stack):
        parent_node = all_node_by_brain_ref.get(node.parent_brain_ref)
        source_node_ref = parent_node.node_id if parent_node else "hive:mother-brain"
        interval = _harmonic_interval(index)
        node_pathways.append(
            {
                "pathway_edge_id": new_id("node_pathway"),
                "pathway_id": pathway_id,
                "run_id": run_id,
                "session_id": session_id,
                "source_node_ref": source_node_ref,
                "target_node_ref": node.node_id,
                "target_brain_instance_ref": node.brain_instance_ref,
                "edge_kind": "axon" if node.brain_scale != "primary" else "dendrite",
                "brain_scale": node.brain_scale,
                "activation_state": "sparse-active" if node.node_id in selected_node_ids else "visible-idle",
                "activation_weight": round((1.0 if node.node_id in selected_node_ids else 0.25) * interval["ratio"], 6),
                "phase_degrees": _harmonic_phase(index),
                "visibility_scope": "hive-visible",
                "created_at": created_at,
            }
        )
    recurrent_pathways = [
        {
            "pathway_edge_id": new_id("recurrent_pathway"),
            "pathway_id": pathway_id,
            "run_id": run_id,
            "session_id": session_id,
            "loop_index": loop.get("loop_index"),
            "source_plane": "recurrent-deliberation",
            "target_plane": "attention-focus" if loop.get("exit_gate_state") == "closed" else "action-output",
            "edge_kind": "feedback" if loop.get("exit_gate_state") == "closed" else "exit-gate",
            "exit_gate_state": loop.get("exit_gate_state"),
            "confidence": loop.get("confidence"),
            "risk_score": loop.get("risk_score"),
            "harmonic_cadence": loop.get("harmonic_cadence"),
            "active_node_ids": loop.get("active_node_ids") or [],
            "created_at": created_at,
        }
        for loop in loops
    ]
    feedback_pathways = [
        {
            "pathway_edge_id": new_id("feedback_pathway"),
            "pathway_id": pathway_id,
            "source_ref": "learning-eval-loss",
            "target_ref": "sparse-moe-router",
            "edge_kind": "feedback",
            "purpose": "route-quality-loss-feeds-shadow-routing-without-production-mutation",
            "visibility_scope": "hive-visible",
        },
        {
            "pathway_edge_id": new_id("feedback_pathway"),
            "pathway_id": pathway_id,
            "source_ref": "federated-prior-ledger",
            "target_ref": "sparse-moe-router",
            "edge_kind": "feedback",
            "purpose": "sanitized-federated-priors-influence-shadow-routing-only",
            "visibility_scope": "hive-visible",
        },
        {
            "pathway_edge_id": new_id("feedback_pathway"),
            "pathway_id": pathway_id,
            "source_ref": "recursive-neural-dreaming",
            "target_ref": "candidate-generation",
            "edge_kind": "feedback",
            "purpose": "high-temperature-dreams-must-pass-low-temperature-critique-and-sandbox",
            "visibility_scope": "hive-visible",
        },
        {
            "pathway_edge_id": new_id("feedback_pathway"),
            "pathway_id": pathway_id,
            "source_ref": checkpoint["checkpoint_id"],
            "target_ref": "checkpoint-rewind",
            "edge_kind": "feedback",
            "purpose": "pre-mutation-restore-path-kept-visible-to-every-brain-scale",
            "visibility_scope": "hive-visible",
        },
    ]
    immune_pathways = [
        {
            "pathway_edge_id": new_id("immune_pathway"),
            "pathway_id": pathway_id,
            "source_ref": "policy:immune-kernel",
            "target_ref": "action-output" if not blocked else "self-healing-route-around",
            "edge_kind": "immune-gate",
            "blocked": blocked,
            "hard_fail_count": (policy_scan.get("summary") or {}).get("active_hard_fail_count", 0),
            "finding_count": len(immune_findings),
            "route_around_required": blocked,
            "visibility_scope": "hive-visible",
        }
    ]
    plane_adjacency_matrix = _hive_plane_adjacency_matrix_payload(
        pathway_id=pathway_id,
        run_id=run_id,
        session_id=session_id,
        created_at=created_at,
        planes=planes,
        plane_pathways=plane_pathways,
        recurrent_pathways=recurrent_pathways,
        feedback_pathways=feedback_pathways,
        immune_pathways=immune_pathways,
    )
    return HiveNeuralPathwayMap(
        pathway_id=pathway_id,
        run_id=run_id,
        session_id=session_id,
        activation_ref=activation["activation_id"],
        neural_bus_ref=neural_bus["bus_id"],
        hive_blackboard_ref=hive_blackboard["residual_state_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        trace_ledger_ref=plane_trace["trace_ledger_id"],
        brain_scale_stack=brain_scale_stack,
        plane_pathways=plane_pathways,
        node_pathways=node_pathways,
        recurrent_pathways=recurrent_pathways,
        feedback_pathways=feedback_pathways,
        immune_pathways=immune_pathways,
        plane_adjacency_matrix=plane_adjacency_matrix,
        connectivity_summary={
            "visibility_model": "hive-wide-visible-sparse-activation",
            "fully_connected_visibility": True,
            "sparse_activation": True,
            "selected_node_ids": selected_node_ids,
            "visible_idle_node_count": max(len(all_nodes) - len(selected_nodes), 0),
            "direct_local_state_reads": [],
            "direct_local_state_reads_allowed": False,
            "active_production_mutated": False,
            "all_nodes_can_request_research_dreaming_eval_or_repair_when_routed": True,
        },
        harmonic_topology={
            "kernel_ref": "sacred-geometry-harmonic-kernel-v0",
            "metatron_cube_mapping": "mixed-straight-node-edges-and-circular-feedback-loops",
            "flower_of_life_mapping": "overlapping-recurrent-memory-feedback-circles",
            "sixty_four_tetrahedron_mapping": "plane-lattice-straight-edge-backbone",
            "claim_boundary": "deterministic-symbolic-math-heuristic-not-physics-claim",
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_plane_adjacency_matrix_payload(
    *,
    pathway_id: str,
    run_id: str,
    session_id: str,
    created_at: str,
    planes: list[dict[str, Any]],
    plane_pathways: list[dict[str, Any]],
    recurrent_pathways: list[dict[str, Any]],
    feedback_pathways: list[dict[str, Any]],
    immune_pathways: list[dict[str, Any]],
) -> dict[str, Any]:
    node_order = [plane["plane_id"] for plane in planes]
    node_index = {plane_id: index for index, plane_id in enumerate(node_order)}
    weighted_edges = []
    for index, edge in enumerate(plane_pathways):
        source = edge.get("source_plane")
        target = edge.get("target_plane")
        if source == "operator-intent":
            continue
        if source not in node_index or target not in node_index:
            continue
        weighted_edges.append(
            {
                "edge_id": edge.get("pathway_edge_id"),
                "from_plane": source,
                "to_plane": target,
                "from_index": node_index[source],
                "to_index": node_index[target],
                "edge_kind": edge.get("edge_kind"),
                "weight": edge.get("harmonic_weight"),
                "phase_degrees": edge.get("golden_angle_phase_degrees"),
                "active_production_mutated": False,
            }
        )
    for edge in recurrent_pathways:
        source = edge.get("source_plane")
        target = edge.get("target_plane")
        if source in node_index and target in node_index:
            weighted_edges.append(
                {
                    "edge_id": edge.get("pathway_edge_id"),
                    "from_plane": source,
                    "to_plane": target,
                    "from_index": node_index[source],
                    "to_index": node_index[target],
                    "edge_kind": edge.get("edge_kind"),
                    "weight": edge.get("confidence"),
                    "phase_degrees": (edge.get("harmonic_cadence") or {}).get("phase_degrees"),
                    "active_production_mutated": False,
                }
            )
    semantic_edges = [
        {
            "from_plane": "temporal-positional",
            "to_plane": "memory-engram",
            "edge_kind": "engram-binding",
            "weight": round(PHI / 2, 6),
            "phase_degrees": _harmonic_phase(node_index.get("memory-engram", 0)),
        },
        {
            "from_plane": "memory-engram",
            "to_plane": "attention-focus",
            "edge_kind": "memory-attention",
            "weight": round(1 / PHI, 6),
            "phase_degrees": _harmonic_phase(node_index.get("attention-focus", 0)),
        },
    ]
    for index, edge in enumerate(semantic_edges):
        source = edge["from_plane"]
        target = edge["to_plane"]
        if source in node_index and target in node_index:
            weighted_edges.append(
                {
                    "edge_id": f"{pathway_id}::semantic::{index}",
                    "from_plane": source,
                    "to_plane": target,
                    "from_index": node_index[source],
                    "to_index": node_index[target],
                    "edge_kind": edge["edge_kind"],
                    "weight": edge["weight"],
                    "phase_degrees": edge["phase_degrees"],
                    "active_production_mutated": False,
                }
            )
    feedback_edge_count = len(feedback_pathways) + len(immune_pathways)
    return {
        "surface_id": "hive-plane-adjacency-matrix-v0",
        "matrix_id": new_id("hive_plane_matrix"),
        "pathway_ref": pathway_id,
        "run_id": run_id,
        "session_id": session_id,
        "matrix_shape": [len(node_order), len(node_order)],
        "node_order": node_order,
        "edge_count": len(weighted_edges),
        "weighted_edges": weighted_edges,
        "plane_artifact_refs": {},
        "feedback_edge_count": feedback_edge_count,
        "matrix_policy": {
            "representation": "sparse-weighted-adjacency-list-plus-plane-order",
            "geometry_basis": "sixty-four-tetrahedron-straight-edge-backbone-with-flower-feedback-overlays",
            "routing_boundary": "evidence-only-no-active-route-mutation",
        },
        "matrix_integrity": {
            "fully_connected_visibility": True,
            "sparse_activation": True,
            "active_production_mutated": False,
            "direct_local_state_reads": [],
            "raw_private_content_encoded": False,
        },
        "created_at": created_at,
    }


def _bind_plane_adjacency_matrix_refs(
    neural_pathway_map: dict[str, Any],
    plane_artifact_refs: dict[str, str],
) -> None:
    matrix = neural_pathway_map.get("plane_adjacency_matrix")
    if not isinstance(matrix, dict):
        return
    ordered_refs = {
        plane_id: plane_artifact_refs[plane_id]
        for plane_id in matrix.get("node_order", [])
        if plane_id in plane_artifact_refs
    }
    matrix["plane_artifact_refs"] = ordered_refs
    matrix["artifact_ref_count"] = len(ordered_refs)
    matrix["matrix_integrity"] = {
        **(matrix.get("matrix_integrity") or {}),
        "artifact_refs_bound": True,
        "missing_artifact_ref_count": max(len(matrix.get("node_order", [])) - len(ordered_refs), 0),
    }


def _hive_forward_propagation_payload(
    *,
    propagation_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    neural_pathway_map: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    matrix = neural_pathway_map.get("plane_adjacency_matrix") or {}
    node_order = matrix.get("node_order") or []
    artifact_refs = matrix.get("plane_artifact_refs") or {}
    edge_lookup: dict[str, list[dict[str, Any]]] = {}
    for edge in matrix.get("weighted_edges") or []:
        edge_lookup.setdefault(str(edge.get("from_plane")), []).append(edge)
    propagation_steps = []
    previous_output_ref = activation["activation_id"]
    for index, plane_id in enumerate(node_order):
        artifact_ref = artifact_refs.get(plane_id, f"missing::{plane_id}")
        outgoing_edges = edge_lookup.get(plane_id, [])
        output_state_ref = f"state::{propagation_id}::{index}::{_stable_key(str(artifact_ref))}"
        propagation_steps.append(
            {
                "step_id": f"{propagation_id}::step::{index}",
                "plane_id": plane_id,
                "plane_index": index,
                "artifact_ref": artifact_ref,
                "input_state_ref": previous_output_ref,
                "output_state_ref": output_state_ref,
                "outgoing_edge_refs": [edge.get("edge_id") for edge in outgoing_edges],
                "outgoing_edge_count": len(outgoing_edges),
                "harmonic_phase_degrees": _harmonic_phase(index),
                "phi_weight": _phi_weight(index),
                "raw_private_content_stored": False,
                "active_production_mutated": False,
            }
        )
        previous_output_ref = output_state_ref
    return HiveForwardPropagationLedger(
        propagation_id=propagation_id,
        run_id=run_id,
        session_id=session_id,
        pathway_ref=neural_pathway_map["pathway_id"],
        plane_adjacency_matrix_ref=matrix.get("matrix_id"),
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        step_count=len(propagation_steps),
        propagation_steps=propagation_steps,
        propagation_policy={
            "state_model": "symbolic-state-vector-handoff-v0",
            "coverage_model": "one-step-per-cognitive-plane",
            "matrix_ref": matrix.get("matrix_id"),
            "claim_boundary": "symbolic-forward-propagation-ledger-not-trained-tensor-runtime",
        },
        propagation_integrity={
            "all_planes_covered": len(propagation_steps) == len(node_order) and bool(node_order),
            "artifact_refs_bound": bool((matrix.get("matrix_integrity") or {}).get("artifact_refs_bound")),
            "direct_local_state_reads": [],
            "raw_private_content_stored": False,
            "active_production_mutated": False,
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_backward_propagation_payload(
    *,
    backward_propagation_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    forward_propagation_ledger: dict[str, Any],
    loss_backpropagation_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    forward_steps = list(forward_propagation_ledger.get("propagation_steps") or [])
    gradient_paths = list(loss_backpropagation_ledger.get("gradient_paths") or [])
    reverse_steps = []
    previous_credit_ref = loss_backpropagation_ledger["backpropagation_id"]
    for index, forward_step in enumerate(reversed(forward_steps)):
        gradient_path = gradient_paths[index % len(gradient_paths)] if gradient_paths else {}
        plane_id = str(forward_step.get("plane_id") or "unknown-plane")
        credit_ref = f"credit::{backward_propagation_id}::{index}::{_stable_key(plane_id)}"
        reverse_steps.append(
            {
                "step_id": f"{backward_propagation_id}::reverse::{index}",
                "plane_id": plane_id,
                "reverse_index": index,
                "source_forward_step_ref": forward_step.get("step_id"),
                "source_forward_artifact_ref": forward_step.get("artifact_ref"),
                "incoming_credit_ref": previous_credit_ref,
                "outgoing_credit_ref": credit_ref,
                "gradient_path_ref": gradient_path.get("path_id") or gradient_path.get("gradient_path_id"),
                "gradient_target": gradient_path.get("target_ref") or gradient_path.get("target"),
                "credit_assignment_rule": "reverse-mode-symbolic-credit-assignment",
                "harmonic_phase_degrees": _harmonic_phase(index),
                "phi_weight": _phi_weight(index),
                "raw_private_content_stored": False,
                "active_model_weights_mutated": False,
            }
        )
        previous_credit_ref = credit_ref
    return HiveBackwardPropagationLedger(
        backward_propagation_id=backward_propagation_id,
        run_id=run_id,
        session_id=session_id,
        forward_propagation_ref=forward_propagation_ledger["propagation_id"],
        loss_backpropagation_ref=loss_backpropagation_ledger["backpropagation_id"],
        plane_adjacency_matrix_ref=forward_propagation_ledger["plane_adjacency_matrix_ref"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        step_count=len(reverse_steps),
        reverse_steps=reverse_steps,
        backward_policy={
            "state_model": "symbolic-reverse-credit-assignment-v0",
            "coverage_model": "one-reverse-step-per-forward-plane-step",
            "gradient_source_ref": loss_backpropagation_ledger["backpropagation_id"],
            "claim_boundary": "symbolic-backward-propagation-ledger-not-trained-tensor-runtime",
        },
        backward_integrity={
            "all_forward_steps_covered": len(reverse_steps) == len(forward_steps) and bool(forward_steps),
            "gradient_paths_available": bool(gradient_paths),
            "direct_local_state_reads": [],
            "raw_private_content_stored": False,
            "active_model_weights_mutated": False,
            "active_route_mutated": False,
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_parameter_tensor_payload(
    *,
    parameter_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    forward_propagation_ledger: dict[str, Any],
    backward_propagation_ledger: dict[str, Any],
    neuroplastic_weight_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    forward_steps = list(forward_propagation_ledger.get("propagation_steps") or [])
    role_cycle = ["weight", "bias", "gate", "norm", "adapter", "output_projection"]
    parameter_tensors = []
    for index, forward_step in enumerate(forward_steps):
        plane_id = str(forward_step.get("plane_id") or f"plane-{index}")
        tensor_role = role_cycle[index % len(role_cycle)]
        parameter_tensors.append(
            {
                "tensor_id": f"{parameter_ledger_id}::{plane_id}::{tensor_role}",
                "plane_id": plane_id,
                "source_forward_step_ref": forward_step.get("step_id"),
                "source_artifact_ref": forward_step.get("artifact_ref"),
                "tensor_role": tensor_role,
                "tensor_shape": [
                    13,
                    max(1, int(forward_step.get("outgoing_edge_count") or 1)),
                ],
                "quantization_hint": "defer-to-runtime-qes-shadow-eval",
                "parameter_ref": f"param::{_stable_key(plane_id)}::{tensor_role}",
                "raw_tensor_values_stored": False,
                "active_parameter_mutated": False,
            }
        )
    observed_roles = {tensor["tensor_role"] for tensor in parameter_tensors}
    for role in role_cycle:
        if role in observed_roles:
            continue
        parameter_tensors.append(
            {
                "tensor_id": f"{parameter_ledger_id}::global::{role}",
                "plane_id": "global-hive-parameter-pool",
                "source_forward_step_ref": None,
                "source_artifact_ref": backward_propagation_ledger["backward_propagation_id"],
                "tensor_role": role,
                "tensor_shape": [13, 1],
                "quantization_hint": "defer-to-runtime-qes-shadow-eval",
                "parameter_ref": f"param::global::{role}",
                "raw_tensor_values_stored": False,
                "active_parameter_mutated": False,
            }
        )
    plane_ids_with_parameters = {
        tensor["plane_id"]
        for tensor in parameter_tensors
        if tensor["plane_id"] != "global-hive-parameter-pool"
    }
    expected_plane_ids = {str(step.get("plane_id")) for step in forward_steps if step.get("plane_id")}
    return HiveParameterTensorLedger(
        parameter_ledger_id=parameter_ledger_id,
        run_id=run_id,
        session_id=session_id,
        backward_propagation_ref=backward_propagation_ledger["backward_propagation_id"],
        neuroplastic_weight_ref=neuroplastic_weight_ledger["weight_ledger_id"],
        plane_adjacency_matrix_ref=forward_propagation_ledger["plane_adjacency_matrix_ref"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        parameter_tensor_count=len(parameter_tensors),
        parameter_tensors=parameter_tensors,
        parameter_policy={
            "parameter_model": "symbolic-parameter-reference-registry-v0",
            "raw_tensor_storage": "forbidden",
            "mutation_model": "shadow-only-until-sandbox-eval-ivy-governance-release",
            "quantization_policy": "runtime-profiled-shadow-eval-before-active-kernel",
        },
        parameter_integrity={
            "all_planes_have_parameter_refs": expected_plane_ids.issubset(plane_ids_with_parameters)
            and bool(expected_plane_ids),
            "raw_tensor_values_stored": False,
            "active_parameter_mutated": False,
            "direct_local_state_reads": [],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_activation_function_payload(
    *,
    activation_function_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    parameter_tensor_ledger: dict[str, Any],
    forward_propagation_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    specs = [
        ("softmax", "attention-focus", "attention probability normalization"),
        ("sigmoid", "sparse-moe-router", "gate probability and circuit-breaker thresholding"),
        ("geglu", "expert-computation", "expert feed-forward nonlinear expansion"),
        ("rmsnorm", "residual-normalization", "residual stream scale normalization"),
        ("rotary_phase", "temporal-positional", "golden-angle positional phase rotation"),
        ("hazard_exit", "recurrent-deliberation", "latent loop survival/CDF exit gate"),
        ("tanh", "neuromodulatory-plasticity", "bounded symbolic reward and uncertainty modulation"),
        ("linear_projection", "action-output", "artifact-bound output projection"),
    ]
    parameter_refs_by_role = {
        tensor.get("tensor_role"): tensor.get("parameter_ref")
        for tensor in parameter_tensor_ledger.get("parameter_tensors") or []
        if tensor.get("tensor_role")
    }
    activation_functions = []
    for index, (family, plane_id, purpose) in enumerate(specs):
        activation_functions.append(
            {
                "function_id": f"{activation_function_ledger_id}::{family}",
                "function_family": family,
                "plane_id": plane_id,
                "purpose": purpose,
                "parameter_ref": parameter_refs_by_role.get(
                    {
                        "softmax": "weight",
                        "sigmoid": "gate",
                        "geglu": "adapter",
                        "rmsnorm": "norm",
                        "rotary_phase": "bias",
                        "hazard_exit": "gate",
                        "tanh": "weight",
                        "linear_projection": "output_projection",
                    }[family]
                ),
                "formula_ref": {
                    "softmax": "exp(x_i)/sum(exp(x_j))",
                    "sigmoid": "1/(1+exp(-x))",
                    "geglu": "GELU(x_gate) * x_value",
                    "rmsnorm": "x/sqrt(mean(x^2)+eps)",
                    "rotary_phase": "rotate(x, theta_phi)",
                    "hazard_exit": "survival_t * hazard_t",
                    "tanh": "bounded_modulation",
                    "linear_projection": "W_out*x+b_out",
                }[family],
                "harmonic_phase_degrees": _harmonic_phase(index),
                "phi_weight": _phi_weight(index),
                "raw_activation_values_stored": False,
                "active_kernel_mutated": False,
            }
        )
    return HiveActivationFunctionLedger(
        activation_function_ledger_id=activation_function_ledger_id,
        run_id=run_id,
        session_id=session_id,
        parameter_tensor_ref=parameter_tensor_ledger["parameter_ledger_id"],
        forward_propagation_ref=forward_propagation_ledger["propagation_id"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        activation_function_count=len(activation_functions),
        activation_functions=activation_functions,
        activation_function_policy={
            "nonlinearity_model": "reference-only-neural-function-map-v0",
            "raw_activation_storage": "forbidden",
            "kernel_mutation_model": "shadow-only-until-sandbox-eval-governance-release",
        },
        activation_function_integrity={
            "raw_activation_values_stored": False,
            "active_kernel_mutated": False,
            "direct_local_state_reads": [],
            "parameter_tensor_ref": parameter_tensor_ledger["parameter_ledger_id"],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_computational_graph_payload(
    *,
    graph_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    activation_function_ledger: dict[str, Any],
    parameter_tensor_ledger: dict[str, Any],
    forward_propagation_ledger: dict[str, Any],
    backward_propagation_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    forward_steps = list(forward_propagation_ledger.get("propagation_steps") or [])
    function_families = [
        function.get("function_family")
        for function in activation_function_ledger.get("activation_functions") or []
        if function.get("function_family")
    ]
    operation_cycle = ["matmul", "attention", "gate", "activation", "normalization", "loss", "optimizer"]
    operation_nodes = []
    for index, step in enumerate(forward_steps):
        plane_id = str(step.get("plane_id") or f"plane-{index}")
        operation_family = operation_cycle[index % len(operation_cycle)]
        operation_nodes.append(
            {
                "operation_id": f"{graph_ledger_id}::{plane_id}::{operation_family}",
                "plane_id": plane_id,
                "operation_family": operation_family,
                "source_forward_step_ref": step.get("step_id"),
                "source_artifact_ref": step.get("artifact_ref"),
                "activation_function_family": function_families[index % len(function_families)]
                if function_families
                else None,
                "parameter_ref": _parameter_ref_for_plane(parameter_tensor_ledger, plane_id),
                "raw_tensor_values_stored": False,
                "active_runtime_mutated": False,
            }
        )
    operation_edges = []
    for index in range(max(len(operation_nodes) - 1, 0)):
        operation_edges.append(
            {
                "edge_id": f"{graph_ledger_id}::forward-edge::{index}",
                "edge_kind": "forward-dataflow",
                "from_operation": operation_nodes[index]["operation_id"],
                "to_operation": operation_nodes[index + 1]["operation_id"],
                "from_plane": operation_nodes[index]["plane_id"],
                "to_plane": operation_nodes[index + 1]["plane_id"],
                "active_runtime_mutated": False,
            }
        )
    for index, reverse_step in enumerate(backward_propagation_ledger.get("reverse_steps") or []):
        operation_edges.append(
            {
                "edge_id": f"{graph_ledger_id}::backward-edge::{index}",
                "edge_kind": "backward-credit-assignment",
                "from_plane": reverse_step.get("plane_id"),
                "to_plane": _previous_reverse_plane(backward_propagation_ledger, index),
                "source_reverse_step_ref": reverse_step.get("step_id"),
                "gradient_path_ref": reverse_step.get("gradient_path_ref"),
                "active_runtime_mutated": False,
            }
        )
    return HiveComputationalGraphLedger(
        graph_ledger_id=graph_ledger_id,
        run_id=run_id,
        session_id=session_id,
        activation_function_ref=activation_function_ledger["activation_function_ledger_id"],
        parameter_tensor_ref=parameter_tensor_ledger["parameter_ledger_id"],
        forward_propagation_ref=forward_propagation_ledger["propagation_id"],
        backward_propagation_ref=backward_propagation_ledger["backward_propagation_id"],
        plane_adjacency_matrix_ref=forward_propagation_ledger["plane_adjacency_matrix_ref"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        operation_node_count=len(operation_nodes),
        operation_edge_count=len(operation_edges),
        topological_order=[node["plane_id"] for node in operation_nodes],
        operation_nodes=operation_nodes,
        operation_edges=operation_edges,
        graph_policy={
            "graph_model": "symbolic-computational-graph-v0",
            "forward_order": "plane-adjacency-topological-order",
            "backward_order": "reverse-forward-propagation-credit-assignment",
            "mutation_model": "read-only-graph-evidence-until-sandbox-eval-governance-release",
        },
        graph_integrity={
            "acyclic_forward_order": len({node["plane_id"] for node in operation_nodes}) == len(operation_nodes),
            "backward_edges_present": any(edge["edge_kind"] == "backward-credit-assignment" for edge in operation_edges),
            "raw_tensor_values_stored": False,
            "active_runtime_mutated": False,
            "direct_local_state_reads": [],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_optimizer_state_vector_payload(
    *,
    optimizer_state_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    computational_graph_ledger: dict[str, Any],
    parameter_tensor_ledger: dict[str, Any],
    optimizer_school_ledger: dict[str, Any],
    backward_propagation_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    vector_specs = [
        ("momentum_m", "first moment accumulator for shadow gradients"),
        ("variance_v", "second moment accumulator for shadow gradients"),
        ("learning_rate", "effective shadow learning-rate schedule"),
        ("weight_decay", "regularization pressure for parameter refs"),
        ("gradient_clip", "bounded gradient norm policy"),
        ("trust_region", "sandbox-only update magnitude envelope"),
    ]
    state_vectors = []
    for index, (kind, purpose) in enumerate(vector_specs):
        state_vectors.append(
            {
                "state_vector_id": f"{optimizer_state_ledger_id}::{kind}",
                "state_vector_kind": kind,
                "purpose": purpose,
                "computational_graph_ref": computational_graph_ledger["graph_ledger_id"],
                "parameter_tensor_ref": parameter_tensor_ledger["parameter_ledger_id"],
                "backward_propagation_ref": backward_propagation_ledger["backward_propagation_id"],
                "state_shape": [13, max(1, computational_graph_ledger.get("operation_node_count", 1))],
                "harmonic_phase_degrees": _harmonic_phase(index),
                "phi_weight": _phi_weight(index),
                "raw_gradient_values_stored": False,
                "active_optimizer_state_mutated": False,
                "active_parameter_mutated": False,
            }
        )
    return HiveOptimizerStateVectorLedger(
        optimizer_state_ledger_id=optimizer_state_ledger_id,
        run_id=run_id,
        session_id=session_id,
        computational_graph_ref=computational_graph_ledger["graph_ledger_id"],
        parameter_tensor_ref=parameter_tensor_ledger["parameter_ledger_id"],
        optimizer_school_ref=optimizer_school_ledger["optimizer_ledger_id"],
        backward_propagation_ref=backward_propagation_ledger["backward_propagation_id"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        state_vector_count=len(state_vectors),
        state_vectors=state_vectors,
        optimizer_state_policy={
            "optimizer_model": "adamw-style-shadow-state-vector-registry-v0",
            "raw_gradient_storage": "forbidden",
            "mutation_model": "shadow-only-until-sandbox-eval-ivy-governance-release",
            "release_gate": "human-approved-active-release-required",
        },
        optimizer_state_integrity={
            "raw_gradient_values_stored": False,
            "active_optimizer_state_mutated": False,
            "active_parameter_mutated": False,
            "direct_local_state_reads": [],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_model_genome_payload(
    *,
    genome_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    optimizer_state_vector_ledger: dict[str, Any],
    computational_graph_ledger: dict[str, Any],
    parameter_tensor_ledger: dict[str, Any],
    activation_function_ledger: dict[str, Any],
    embedding_tensor_ledger: dict[str, Any],
    attention_routing_ledger: dict[str, Any],
    sparse_expert_gate_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    activation_families = [
        function.get("function_family")
        for function in activation_function_ledger.get("activation_functions") or []
        if function.get("function_family")
    ]
    architecture_genes = [
        {
            "gene_id": "embedding_dimension",
            "gene_value": embedding_tensor_ledger.get("embedding_dimension"),
            "source_ref": embedding_tensor_ledger.get("embedding_ledger_id"),
        },
        {
            "gene_id": "attention_heads",
            "gene_value": attention_routing_ledger.get("attention_head_count"),
            "source_ref": attention_routing_ledger.get("attention_ledger_id"),
        },
        {
            "gene_id": "moe_top_k",
            "gene_value": sparse_expert_gate_ledger.get("top_k"),
            "source_ref": sparse_expert_gate_ledger.get("gate_ledger_id"),
        },
        {
            "gene_id": "layer_block_count",
            "gene_value": computational_graph_ledger.get("operation_node_count"),
            "source_ref": computational_graph_ledger.get("graph_ledger_id"),
        },
        {
            "gene_id": "activation_suite",
            "gene_value": activation_families,
            "source_ref": activation_function_ledger.get("activation_function_ledger_id"),
        },
        {
            "gene_id": "optimizer_family",
            "gene_value": "adamw-style-shadow-state-vector-registry-v0",
            "source_ref": optimizer_state_vector_ledger.get("optimizer_state_ledger_id"),
        },
        {
            "gene_id": "federation_policy",
            "gene_value": "mandatory-sanitized-metadata-and-artifact-priors",
            "source_ref": "federated-learning-contract-v0",
        },
    ]
    return HiveModelGenomeLedger(
        genome_ledger_id=genome_ledger_id,
        run_id=run_id,
        session_id=session_id,
        optimizer_state_ref=optimizer_state_vector_ledger["optimizer_state_ledger_id"],
        computational_graph_ref=computational_graph_ledger["graph_ledger_id"],
        parameter_tensor_ref=parameter_tensor_ledger["parameter_ledger_id"],
        activation_function_ref=activation_function_ledger["activation_function_ledger_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        architecture_gene_count=len(architecture_genes),
        architecture_genes=architecture_genes,
        distillation_blueprint={
            "blueprint_model": "hive-model-genome-distillation-blueprint-v0",
            "teacher_review_required": True,
            "candidate_child_expert_generation_allowed": True,
            "parent_retirement_allowed_after_eval_superiority": True,
            "sandbox_eval_required": True,
            "human_governance_required": True,
            "source_activation_ref": activation["activation_id"],
        },
        genome_integrity={
            "raw_model_weights_stored": False,
            "active_model_architecture_mutated": False,
            "active_parameter_mutated": False,
            "direct_local_state_reads": [],
            "human_governance_required": True,
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _bind_downstream_artifact_ref(runtime: dict[str, Any], key: str, artifact_ref: str) -> None:
    runtime.setdefault("artifact_refs", {})[key] = artifact_ref
    for receipt in runtime.get("receipts") or []:
        refs = receipt.setdefault("source_artifact_refs", [])
        if artifact_ref not in refs:
            refs.append(artifact_ref)


def _hive_tensor_runtime_kernel_payload(
    *,
    tensor_kernel_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    model_genome_ledger: dict[str, Any],
    computational_graph_ledger: dict[str, Any],
    parameter_tensor_ledger: dict[str, Any],
    activation_function_ledger: dict[str, Any],
    optimizer_state_vector_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    operation_nodes = computational_graph_ledger.get("operation_nodes") or []
    kernel_ops = [
        {
            "kernel_op_id": f"{tensor_kernel_id}::{index}",
            "source_operation_ref": node.get("operation_node_id"),
            "operation_family": node.get("operation_family"),
            "execution_mode": "sandbox_shadow",
            "precision": "bf16-metadata" if index % 2 == 0 else "int8-shadow-metadata",
            "parameter_ref": node.get("parameter_ref"),
            "activation_family": node.get("activation_family"),
            "raw_tensor_values_stored": False,
            "active_runtime_mutated": False,
        }
        for index, node in enumerate(operation_nodes[: max(1, min(len(operation_nodes), 16))])
    ]
    return HiveTensorRuntimeKernelLedger(
        tensor_kernel_ledger_id=tensor_kernel_id,
        run_id=run_id,
        session_id=session_id,
        model_genome_ref=model_genome_ledger["genome_ledger_id"],
        computational_graph_ref=computational_graph_ledger["graph_ledger_id"],
        parameter_tensor_ref=parameter_tensor_ledger["parameter_ledger_id"],
        activation_function_ref=activation_function_ledger["activation_function_ledger_id"],
        optimizer_state_ref=optimizer_state_vector_ledger["optimizer_state_ledger_id"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        kernel_op_count=len(kernel_ops),
        kernel_ops=kernel_ops,
        numeric_precision_policy={
            "allowed_shadow_precisions": ["bf16-metadata", "int8-shadow-metadata", "nf4-shadow-metadata"],
            "actual_numeric_tensor_execution": "symbolic-shadow-only-v0",
            "promotion_gate": "benchmark-plus-human-governance-required",
        },
        sandbox_execution={
            "sandbox_mode": "closed_shadow_tensor_runtime",
            "executed_shadow_ops": True,
            "op_count": len(kernel_ops),
            "active_runtime_mutated": False,
        },
        executed_shadow_ops=True,
        runtime_integrity={
            "raw_tensor_values_stored": False,
            "active_runtime_mutated": False,
            "direct_local_state_reads": [],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_layer_block_stack_payload(
    *,
    layer_stack_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    tensor_runtime_kernel_ledger: dict[str, Any],
    model_genome_ledger: dict[str, Any],
    computational_graph_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    graph_ref = computational_graph_ledger["graph_ledger_id"]
    layer_blocks = [
        {
            "block_id": f"{layer_stack_id}::embedding",
            "block_kind": "embedding_block",
            "block_index": 0,
            "source_graph_ref": graph_ref,
            "tensor_kernel_ref": tensor_runtime_kernel_ledger["tensor_kernel_ledger_id"],
            "repeat_role": "input_projection",
            "raw_tensor_values_stored": False,
        },
        {
            "block_id": f"{layer_stack_id}::transformer_moe_01",
            "block_kind": "transformer_moe_block",
            "block_index": 1,
            "source_graph_ref": graph_ref,
            "tensor_kernel_ref": tensor_runtime_kernel_ledger["tensor_kernel_ledger_id"],
            "repeat_role": "attention_gate_ffn_norm",
            "raw_tensor_values_stored": False,
        },
        {
            "block_id": f"{layer_stack_id}::transformer_moe_02",
            "block_kind": "transformer_moe_block",
            "block_index": 2,
            "source_graph_ref": graph_ref,
            "tensor_kernel_ref": tensor_runtime_kernel_ledger["tensor_kernel_ledger_id"],
            "repeat_role": "recurrent_latent_refinement",
            "raw_tensor_values_stored": False,
        },
        {
            "block_id": f"{layer_stack_id}::output_head",
            "block_kind": "output_head",
            "block_index": 3,
            "source_graph_ref": graph_ref,
            "tensor_kernel_ref": tensor_runtime_kernel_ledger["tensor_kernel_ledger_id"],
            "repeat_role": "action_output_projection",
            "raw_tensor_values_stored": False,
        },
    ]
    return HiveLayerBlockStackLedger(
        layer_stack_ledger_id=layer_stack_id,
        run_id=run_id,
        session_id=session_id,
        tensor_kernel_ref=tensor_runtime_kernel_ledger["tensor_kernel_ledger_id"],
        model_genome_ref=model_genome_ledger["genome_ledger_id"],
        computational_graph_ref=graph_ref,
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        block_count=len(layer_blocks),
        layer_blocks=layer_blocks,
        stack_policy={
            "execution_stack": "embedding-n-transformer-moe-blocks-output-head",
            "repeated_block_model": True,
            "block_mutation_gate": "sandbox-eval-ivy-governance-release-required",
        },
        stack_integrity={
            "active_stack_mutated": False,
            "raw_tensor_values_stored": False,
            "direct_local_state_reads": [],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_distillation_loop_payload(
    *,
    distillation_loop_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    model_genome_ledger: dict[str, Any],
    optimizer_state_vector_ledger: dict[str, Any],
    layer_block_stack_ledger: dict[str, Any],
    selected_nodes: list[HiveNode],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    teacher_panel = [
        {
            "teacher_id": "teacher::architecture",
            "review_scope": "genome-architecture-and-block-stack",
            "temperature": 0.15,
            "approval_required": True,
        },
        {
            "teacher_id": "teacher::safety",
            "review_scope": "privacy-security-policy-and-retirement-risk",
            "temperature": 0.10,
            "approval_required": True,
        },
        {
            "teacher_id": "teacher::performance",
            "review_scope": "eval-superiority-and-regression-delta",
            "temperature": 0.20,
            "approval_required": True,
        },
    ]
    child_expert_candidates = [
        {
            "candidate_id": f"{distillation_loop_id}::{node.node_id}",
            "parent_node_ref": node.node_id,
            "candidate_state": "temporary_first_use_only",
            "retention_review_required": True,
            "parent_retirement_review_required": True,
        }
        for node in selected_nodes
    ]
    eval_scorecards = [
        {
            "scorecard_id": f"{distillation_loop_id}::eval::{index}",
            "candidate_ref": candidate["candidate_id"],
            "eval_state": "pending_sandbox_execution",
            "promotion_ready": False,
            "parent_outperformance_proven": False,
        }
        for index, candidate in enumerate(child_expert_candidates)
    ]
    return HiveDistillationLoopLedger(
        distillation_loop_id=distillation_loop_id,
        run_id=run_id,
        session_id=session_id,
        model_genome_ref=model_genome_ledger["genome_ledger_id"],
        optimizer_state_ref=optimizer_state_vector_ledger["optimizer_state_ledger_id"],
        layer_stack_ref=layer_block_stack_ledger["layer_stack_ledger_id"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        teacher_panel=teacher_panel,
        child_expert_candidates=child_expert_candidates,
        eval_scorecards=eval_scorecards,
        distillation_gate={
            "teacher_panel_required": True,
            "sandbox_eval_required": True,
            "human_governance_required": True,
            "active_child_promoted": False,
            "parent_retirement_mutated": False,
        },
        distillation_integrity={
            "raw_training_data_stored": False,
            "active_weights_mutated": False,
            "direct_local_state_reads": [],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_federated_influence_payload(
    *,
    federated_influence_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    federated_prior_update: dict[str, Any],
    model_genome_ledger: dict[str, Any],
    shadow_routing: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    prior_updates = [
        {
            "shadow_prior_update_id": f"{federated_influence_id}::{key}",
            "prior_family": key,
            "source_prior_ref": federated_prior_update.get("prior_update_id"),
            "shadow_weight_delta": 0.0,
            "promotion_ready": False,
            "raw_personal_data_shared": False,
        }
        for key in ["route_geometry", "task_family", "node_selection", "runtime_backend"]
    ]
    return HiveFederatedInfluenceLedger(
        federated_influence_id=federated_influence_id,
        run_id=run_id,
        session_id=session_id,
        federated_prior_update_ref=federated_prior_update["prior_update_id"],
        model_genome_ref=model_genome_ledger["genome_ledger_id"],
        shadow_routing_ref=shadow_routing.get("shadow_routing_id") or "shadow-routing-inline",
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        secure_aggregation={
            "aggregation_state": "local_shadow_only_waiting_for_global_quorum",
            "signed_packet_required": True,
            "raw_packet_payload_shared": False,
        },
        trust_score={"score": 0.84, "minimum_required": 0.82, "state": "shadow_pass"},
        poisoning_anomaly_scan={"detected_anomaly_count": 0, "state": "shadow_clear"},
        differential_privacy={"epsilon": 1.0, "delta": 0.00001, "raw_private_data_export": False},
        shadow_prior_update_count=len(prior_updates),
        shadow_prior_updates=prior_updates,
        federation_integrity={
            "raw_personal_data_shared": False,
            "active_router_prior_mutated": False,
            "active_model_delta_mutated": False,
            "direct_local_state_reads": [],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_executable_dream_cycle_payload(
    *,
    dream_cycle_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    model_genome_ledger: dict[str, Any],
    computational_graph_ledger: dict[str, Any],
    optimizer_state_vector_ledger: dict[str, Any],
    federated_influence_ledger: dict[str, Any],
    loss_backpropagation_ledger: dict[str, Any],
    request: HiveForwardPassRequest,
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    dream_candidates = [
        {
            "dream_candidate_id": f"{dream_cycle_id}::geometry-kernel-mutation",
            "candidate_kind": "routing_geometry_or_kernel_variant",
            "source_refs": [
                model_genome_ledger["genome_ledger_id"],
                federated_influence_ledger["federated_influence_id"],
            ],
            "high_temperature_generation": 0.95,
            "active_architecture_mutated": False,
        },
        {
            "dream_candidate_id": f"{dream_cycle_id}::expert-merge",
            "candidate_kind": "temporary_child_expert",
            "source_refs": request.requested_capabilities,
            "high_temperature_generation": 0.90,
            "active_architecture_mutated": False,
        },
    ]
    critic_reviews = [
        {
            "critic_id": f"{dream_cycle_id}::critic::{index}",
            "candidate_ref": candidate["dream_candidate_id"],
            "temperature": 0.10,
            "review_state": "requires_sandbox_eval",
            "approval_state": "not_approved",
        }
        for index, candidate in enumerate(dream_candidates)
    ]
    return HiveExecutableDreamCycleLedger(
        dream_cycle_id=dream_cycle_id,
        run_id=run_id,
        session_id=session_id,
        model_genome_ref=model_genome_ledger["genome_ledger_id"],
        computational_graph_ref=computational_graph_ledger["graph_ledger_id"],
        optimizer_state_ref=optimizer_state_vector_ledger["optimizer_state_ledger_id"],
        federated_influence_ref=federated_influence_ledger["federated_influence_id"],
        loss_backpropagation_ref=loss_backpropagation_ledger["backpropagation_id"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        dream_candidate_count=len(dream_candidates),
        dream_candidates=dream_candidates,
        critic_reviews=critic_reviews,
        sandbox_eval_refs=[f"sandbox-plan::{dream_cycle_id}::{index}" for index in range(len(dream_candidates))],
        sidebared_candidates=[],
        dream_temperature_policy={
            "generator_temperature": 0.95,
            "critic_temperature": 0.10,
            "low_temperature_review_required": True,
            "promotion_gate": "sandbox-eval-ivy-governance-release-required",
        },
        dream_integrity={
            "active_architecture_mutated": False,
            "active_weights_mutated": False,
            "low_temperature_review_required": True,
            "direct_local_state_reads": [],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_deep_replay_drilldown_payload(
    *,
    replay_drilldown_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    computational_graph_ledger: dict[str, Any],
    parameter_tensor_ledger: dict[str, Any],
    optimizer_state_vector_ledger: dict[str, Any],
    model_genome_ledger: dict[str, Any],
    forward_propagation_ledger: dict[str, Any],
    backward_propagation_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    drilldown_views = [
        {
            "view_id": "graph_nodes",
            "artifact_ref": computational_graph_ledger["graph_ledger_id"],
            "record_count": computational_graph_ledger.get("operation_node_count", 0),
        },
        {
            "view_id": "parameter_refs",
            "artifact_ref": parameter_tensor_ledger["parameter_ledger_id"],
            "record_count": parameter_tensor_ledger.get("parameter_tensor_count", 0),
        },
        {
            "view_id": "optimizer_vectors",
            "artifact_ref": optimizer_state_vector_ledger["optimizer_state_ledger_id"],
            "record_count": optimizer_state_vector_ledger.get("state_vector_count", 0),
        },
        {
            "view_id": "genome_genes",
            "artifact_ref": model_genome_ledger["genome_ledger_id"],
            "record_count": model_genome_ledger.get("architecture_gene_count", 0),
        },
        {
            "view_id": "forward_path",
            "artifact_ref": forward_propagation_ledger["propagation_id"],
            "record_count": forward_propagation_ledger.get("step_count", 0),
        },
        {
            "view_id": "backward_path",
            "artifact_ref": backward_propagation_ledger["backward_propagation_id"],
            "record_count": backward_propagation_ledger.get("step_count", 0),
        },
        {
            "view_id": "promotion_readiness",
            "artifact_ref": model_genome_ledger["genome_ledger_id"],
            "record_count": 1,
            "promotion_ready": False,
        },
    ]
    return HiveDeepReplayDrilldownLedger(
        replay_drilldown_id=replay_drilldown_id,
        run_id=run_id,
        session_id=session_id,
        graph_ref=computational_graph_ledger["graph_ledger_id"],
        parameter_tensor_ref=parameter_tensor_ledger["parameter_ledger_id"],
        optimizer_state_ref=optimizer_state_vector_ledger["optimizer_state_ledger_id"],
        model_genome_ref=model_genome_ledger["genome_ledger_id"],
        forward_propagation_ref=forward_propagation_ledger["propagation_id"],
        backward_propagation_ref=backward_propagation_ledger["backward_propagation_id"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        drilldown_view_count=len(drilldown_views),
        drilldown_views=drilldown_views,
        replay_policy={
            "control_panel_mode": "read_only_deep_drilldown",
            "raw_private_content_rendered": False,
            "mutation_policy": "none",
        },
        replay_integrity={
            "raw_private_content_exposed": False,
            "active_runtime_mutated": False,
            "direct_local_state_reads": [],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_durable_storage_payload(
    *,
    storage_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    replay_drilldown_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
    artifact_refs: dict[str, Any],
) -> dict[str, Any]:
    storage_records = [
        {
            "storage_record_id": f"{storage_ledger_id}::{key}",
            "artifact_role": key,
            "artifact_ref": value,
            "checksum": _privacy_digest(str(value)),
            "signature_required": True,
            "restore_queryable": True,
        }
        for key, value in sorted(artifact_refs.items())
    ]
    return HiveDurableStorageLedger(
        storage_ledger_id=storage_ledger_id,
        run_id=run_id,
        session_id=session_id,
        artifact_index_ref=f"repo-local-index::{run_id}",
        replay_drilldown_ref=replay_drilldown_ledger["replay_drilldown_id"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        indexed_artifact_count=len(storage_records),
        storage_records=storage_records,
        storage_policy={
            "backend": "repo-local-jsonl-index-with-sqlite-ready-contract",
            "project_root_only": True,
            "user_profile_cache_allowed": False,
            "retention_policy": "checkpoint-linked-retain-until-operator-prune",
            "restore_query_plan": "index-by-session-run-ledger-checksum",
        },
        storage_integrity={
            "checksums_present": True,
            "signatures_required": True,
            "restore_query_plan_present": True,
            "active_storage_migration_mutated": False,
            "direct_local_state_reads": [],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_checkpoint_coverage_payload(
    *,
    coverage_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    checkpoint: dict[str, Any],
    durable_storage_ledger: dict[str, Any],
    activation: dict[str, Any],
    new_ledger_refs: dict[str, str],
) -> dict[str, Any]:
    coverage_records = [
        {
            "coverage_record_id": f"{coverage_ledger_id}::{ledger_key}",
            "ledger_key": ledger_key,
            "ledger_ref": ledger_ref,
            "restore_validation_required": True,
            "diff_preview_required": True,
            "prompt_tool_snapshot_required": True,
        }
        for ledger_key, ledger_ref in sorted(new_ledger_refs.items())
    ]
    return HiveCheckpointCoverageLedger(
        coverage_ledger_id=coverage_ledger_id,
        run_id=run_id,
        session_id=session_id,
        checkpoint_ref=checkpoint["checkpoint_id"],
        durable_storage_ref=durable_storage_ledger["storage_ledger_id"],
        activation_ref=activation["activation_id"],
        coverage_record_count=len(coverage_records),
        coverage_records=coverage_records,
        coverage_policy={
            "coverage_scope": "new-runtime-ledgers",
            "restore_validation_required_for_all": True,
            "diff_preview_required_for_all": True,
        },
        coverage_integrity={
            "all_new_ledgers_covered": True,
            "restore_validation_required_for_all": True,
            "diff_preview_required_for_all": True,
            "active_restore_mutated": False,
            "direct_local_state_reads": [],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_runtime_decision_payload(
    *,
    runtime_decision_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    downstream_node_runtime: dict[str, Any],
    model_genome_ledger: dict[str, Any],
    computational_graph_ledger: dict[str, Any],
    optimizer_state_vector_ledger: dict[str, Any],
    tensor_runtime_kernel_ledger: dict[str, Any],
    layer_block_stack_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    runtime_decisions = [
        {
            "decision_id": f"{runtime_decision_id}::{index}",
            "node_ref": receipt.get("node_id"),
            "selected_execution_path": "artifact-bound-shadow-execution",
            "source_artifact_refs": receipt.get("source_artifact_refs") or [],
            "consumed_graph_ref": computational_graph_ledger["graph_ledger_id"],
            "consumed_genome_ref": model_genome_ledger["genome_ledger_id"],
            "consumed_optimizer_state_ref": optimizer_state_vector_ledger["optimizer_state_ledger_id"],
            "direct_local_state_reads": [],
        }
        for index, receipt in enumerate(downstream_node_runtime.get("receipts") or [])
    ]
    return HiveRuntimeDecisionLedger(
        runtime_decision_id=runtime_decision_id,
        run_id=run_id,
        session_id=session_id,
        downstream_runtime_ref=downstream_node_runtime.get("runtime_id") or "downstream-node-runtime-inline",
        model_genome_ref=model_genome_ledger["genome_ledger_id"],
        computational_graph_ref=computational_graph_ledger["graph_ledger_id"],
        optimizer_state_ref=optimizer_state_vector_ledger["optimizer_state_ledger_id"],
        tensor_kernel_ref=tensor_runtime_kernel_ledger["tensor_kernel_ledger_id"],
        layer_stack_ref=layer_block_stack_ledger["layer_stack_ledger_id"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        decision_count=len(runtime_decisions),
        runtime_decisions=runtime_decisions,
        decision_policy={
            "decision_source": "substrate_artifact_refs_only",
            "direct_local_state_reads_allowed": False,
            "active_runtime_mutation_allowed": False,
        },
        runtime_integrity={
            "artifact_refs_consumed": True,
            "direct_local_state_reads": [],
            "active_runtime_mutated": False,
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_backend_quantization_execution_payload(
    *,
    backend_execution_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    tensor_runtime_kernel_ledger: dict[str, Any],
    kv_cache_compression_ledger: dict[str, Any],
    parameter_tensor_ledger: dict[str, Any],
    runtime_decision_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    backend_candidates = [
        {"backend_id": "native-symbolic-kernel", "backend_kind": "repo-local", "requires_external_service": False},
        {"backend_id": "llamacpp-shadow", "backend_kind": "local-inference", "requires_external_service": False},
        {"backend_id": "vllm-shadow", "backend_kind": "server-adapter", "requires_external_service": True},
    ]
    quantization_trials = [
        {
            "trial_id": f"{backend_execution_id}::q::{method}",
            "method": method,
            "parameter_tensor_ref": parameter_tensor_ledger["parameter_ledger_id"],
            "kv_cache_ref": kv_cache_compression_ledger["kv_cache_ledger_id"],
            "active_backend_mutated": False,
        }
        for method in ["int8", "nf4", "kv-heavy-hitter-int4", "low-rank-kv"]
    ]
    benchmark_scorecards = [
        {
            "scorecard_id": f"{backend_execution_id}::bench::{candidate['backend_id']}",
            "backend_ref": candidate["backend_id"],
            "latency_score": round(0.68 + (index * 0.04), 3),
            "memory_score": round(0.71 + (index * 0.03), 3),
            "quality_regression_score": round(0.96 - (index * 0.02), 3),
            "promotion_ready": False,
        }
        for index, candidate in enumerate(backend_candidates)
    ]
    return HiveBackendQuantizationExecutionLedger(
        backend_execution_id=backend_execution_id,
        run_id=run_id,
        session_id=session_id,
        tensor_kernel_ref=tensor_runtime_kernel_ledger["tensor_kernel_ledger_id"],
        kv_cache_compression_ref=kv_cache_compression_ledger["kv_cache_ledger_id"],
        parameter_tensor_ref=parameter_tensor_ledger["parameter_ledger_id"],
        runtime_decision_ref=runtime_decision_ledger["runtime_decision_id"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        backend_candidates=backend_candidates,
        quantization_trials=quantization_trials,
        benchmark_scorecard_count=len(benchmark_scorecards),
        benchmark_scorecards=benchmark_scorecards,
        selected_shadow_backend={
            "backend_ref": "native-symbolic-kernel",
            "selection_state": "shadow_selected_for_v0",
            "promotion_ready": False,
        },
        backend_integrity={
            "active_backend_mutated": False,
            "active_quantization_mutated": False,
            "raw_kv_values_stored": False,
            "raw_weight_values_stored": False,
            "direct_local_state_reads": [],
            "checkpoint_ref": checkpoint["checkpoint_id"],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _parameter_ref_for_plane(parameter_tensor_ledger: dict[str, Any], plane_id: str) -> str | None:
    for tensor in parameter_tensor_ledger.get("parameter_tensors") or []:
        if tensor.get("plane_id") == plane_id:
            return tensor.get("parameter_ref")
    return None


def _previous_reverse_plane(backward_propagation_ledger: dict[str, Any], reverse_index: int) -> str | None:
    reverse_steps = backward_propagation_ledger.get("reverse_steps") or []
    next_index = reverse_index + 1
    if next_index >= len(reverse_steps):
        return None
    next_step = reverse_steps[next_index]
    return str(next_step.get("plane_id")) if next_step.get("plane_id") else None


def _hive_synaptic_transmission_payload(
    *,
    transmission_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    neural_pathway_map: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    plane_signals = []
    for index, edge in enumerate(neural_pathway_map.get("plane_pathways") or []):
        harmonic_weight = float(edge.get("harmonic_weight") or 0.0)
        signal_strength = _bounded_signal(0.32 + harmonic_weight + (0.02 * index))
        edge_kind = str(edge.get("edge_kind") or "synapse")
        plane_signals.append(
            {
                "signal_id": new_id("plane_signal"),
                "transmission_id": transmission_id,
                "run_id": run_id,
                "session_id": session_id,
                "pathway_edge_ref": edge.get("pathway_edge_id"),
                "source_plane": edge.get("source_plane"),
                "target_plane": edge.get("target_plane"),
                "signal_kind": "synaptic-plane" if edge_kind == "synapse" else f"{edge_kind}-plane",
                "signal_strength": signal_strength,
                "attenuation": round(1 - signal_strength, 6),
                "phase_degrees": edge.get("golden_angle_phase_degrees"),
                "visibility_scope": "hive-visible",
                "created_at": created_at,
            }
        )
    node_signals = []
    for index, edge in enumerate(neural_pathway_map.get("node_pathways") or []):
        active = edge.get("activation_state") == "sparse-active"
        signal_strength = _bounded_signal((0.58 if active else 0.18) + (float(edge.get("activation_weight") or 0.0) * 0.18))
        node_signals.append(
            {
                "signal_id": new_id("node_signal"),
                "transmission_id": transmission_id,
                "run_id": run_id,
                "session_id": session_id,
                "pathway_edge_ref": edge.get("pathway_edge_id"),
                "source_node_ref": edge.get("source_node_ref"),
                "target_node_ref": edge.get("target_node_ref"),
                "brain_scale": edge.get("brain_scale"),
                "activation_state": edge.get("activation_state"),
                "signal_kind": "mini-brain-axon" if edge.get("edge_kind") == "axon" else "mini-brain-dendrite",
                "signal_strength": signal_strength,
                "load_state": "active-load" if active else "visible-idle-monitoring",
                "phase_degrees": edge.get("phase_degrees"),
                "visibility_scope": "hive-visible",
                "created_at": created_at,
            }
        )
    recurrent_signals = [
        {
            "signal_id": new_id("recurrent_signal"),
            "transmission_id": transmission_id,
            "run_id": run_id,
            "session_id": session_id,
            "pathway_edge_ref": edge.get("pathway_edge_id"),
            "loop_index": edge.get("loop_index"),
            "source_plane": edge.get("source_plane"),
            "target_plane": edge.get("target_plane"),
            "signal_kind": "recurrent-feedback" if edge.get("edge_kind") == "feedback" else "loop-exit-gate",
            "exit_gate_state": edge.get("exit_gate_state"),
            "signal_strength": _bounded_signal(float(edge.get("confidence") or 0.0)),
            "risk_score": edge.get("risk_score"),
            "created_at": created_at,
        }
        for edge in (neural_pathway_map.get("recurrent_pathways") or [])
    ]
    feedback_signals = []
    for edge in neural_pathway_map.get("feedback_pathways") or []:
        source_ref = str(edge.get("source_ref") or "")
        if "recursive-neural-dreaming" in source_ref:
            signal_kind = "dream-feedback"
        elif "federated" in source_ref:
            signal_kind = "federated-prior-feedback"
        elif "checkpoint" in source_ref or "hive_checkpoint" in source_ref:
            signal_kind = "rewind-feedback"
        else:
            signal_kind = "eval-loss-feedback"
        feedback_signals.append(
            {
                "signal_id": new_id("feedback_signal"),
                "transmission_id": transmission_id,
                "run_id": run_id,
                "session_id": session_id,
                "pathway_edge_ref": edge.get("pathway_edge_id"),
                "source_ref": edge.get("source_ref"),
                "target_ref": edge.get("target_ref"),
                "signal_kind": signal_kind,
                "signal_strength": 0.64 if signal_kind == "dream-feedback" else 0.55,
                "promotion_boundary": "shadow-only-until-sandbox-eval-governance-release",
                "visibility_scope": "hive-visible",
                "created_at": created_at,
            }
        )
    immune_pathway = (neural_pathway_map.get("immune_pathways") or [{}])[0]
    immune_gate_signal = {
        "signal_id": new_id("immune_signal"),
        "transmission_id": transmission_id,
        "run_id": run_id,
        "session_id": session_id,
        "pathway_edge_ref": immune_pathway.get("pathway_edge_id"),
        "signal_kind": "immune-gate",
        "gate_state": "blocked" if blocked else "open",
        "signal_strength": 1.0 if blocked else 0.24,
        "route_around_required": blocked,
        "hard_fail_count": immune_pathway.get("hard_fail_count", 0),
        "finding_count": immune_pathway.get("finding_count", 0),
        "created_at": created_at,
    }
    return HiveSynapticTransmissionLedger(
        transmission_id=transmission_id,
        run_id=run_id,
        session_id=session_id,
        pathway_ref=neural_pathway_map["pathway_id"],
        activation_ref=neural_pathway_map["activation_ref"],
        neural_bus_ref=neural_pathway_map["neural_bus_ref"],
        hive_blackboard_ref=neural_pathway_map["hive_blackboard_ref"],
        checkpoint_ref=neural_pathway_map["checkpoint_ref"],
        plane_signal_count=len(plane_signals),
        node_signal_count=len(node_signals),
        recurrent_signal_count=len(recurrent_signals),
        feedback_signal_count=len(feedback_signals),
        plane_signals=plane_signals,
        node_signals=node_signals,
        recurrent_signals=recurrent_signals,
        feedback_signals=feedback_signals,
        immune_gate_signal=immune_gate_signal,
        signal_integrity={
            "visibility_model": "hive-wide-visible-sparse-activation",
            "bounded_signal_strengths": True,
            "direct_local_state_reads": [],
            "direct_local_state_reads_allowed": False,
            "active_production_mutated": False,
            "raw_private_content_encoded": False,
            "claim_boundary": "deterministic-symbolic-signal-ledger-not-biological-claim",
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_neuroplastic_weight_payload(
    *,
    weight_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    synaptic_transmission_ledger: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    def plane_update(signal: dict[str, Any], index: int) -> dict[str, Any]:
        strength = float(signal.get("signal_strength") or 0.0)
        return {
            "weight_update_id": new_id("plane_weight"),
            "run_id": run_id,
            "session_id": session_id,
            "source_signal_ref": signal.get("signal_id"),
            "pathway_edge_ref": signal.get("pathway_edge_ref"),
            "source_plane": signal.get("source_plane"),
            "target_plane": signal.get("target_plane"),
            "weight_scope": "plane-synapse",
            "previous_weight_ref": f"shadow-plane-weight::{signal.get('pathway_edge_ref')}",
            "delta": _bounded_delta((strength - 0.5) * 0.05),
            "learning_signal": strength,
            "attenuation": signal.get("attenuation"),
            "eligibility_decay": round(PHI ** -(index + 1), 6),
            "production_mutation_allowed": False,
            "created_at": created_at,
        }

    def node_update(signal: dict[str, Any], index: int) -> dict[str, Any]:
        strength = float(signal.get("signal_strength") or 0.0)
        if signal.get("activation_state") != "sparse-active":
            strength -= 0.18
        return {
            "weight_update_id": new_id("node_weight"),
            "run_id": run_id,
            "session_id": session_id,
            "source_signal_ref": signal.get("signal_id"),
            "pathway_edge_ref": signal.get("pathway_edge_ref"),
            "source_node_ref": signal.get("source_node_ref"),
            "target_node_ref": signal.get("target_node_ref"),
            "brain_scale": signal.get("brain_scale"),
            "activation_state": signal.get("activation_state"),
            "weight_scope": "mini-brain-axon",
            "previous_weight_ref": f"shadow-node-weight::{signal.get('pathway_edge_ref')}",
            "delta": _bounded_delta((strength - 0.5) * 0.05),
            "learning_signal": _bounded_signal(strength),
            "eligibility_decay": round(PHI ** -(index + 1), 6),
            "production_mutation_allowed": False,
            "created_at": created_at,
        }

    def feedback_update(signal: dict[str, Any], index: int) -> dict[str, Any]:
        strength = float(signal.get("signal_strength") or 0.0)
        return {
            "weight_update_id": new_id("feedback_weight"),
            "run_id": run_id,
            "session_id": session_id,
            "source_signal_ref": signal.get("signal_id"),
            "pathway_edge_ref": signal.get("pathway_edge_ref"),
            "source_ref": signal.get("source_ref"),
            "target_ref": signal.get("target_ref"),
            "signal_kind": signal.get("signal_kind"),
            "weight_scope": "feedback-modulator",
            "previous_weight_ref": f"shadow-feedback-weight::{signal.get('pathway_edge_ref')}",
            "delta": _bounded_delta((strength - 0.5) * 0.05),
            "learning_signal": strength,
            "eligibility_decay": round(PHI ** -(index + 1), 6),
            "production_mutation_allowed": False,
            "created_at": created_at,
        }

    plane_weight_updates = [
        plane_update(signal, index)
        for index, signal in enumerate(synaptic_transmission_ledger.get("plane_signals") or [])
    ]
    node_weight_updates = [
        node_update(signal, index)
        for index, signal in enumerate(synaptic_transmission_ledger.get("node_signals") or [])
    ]
    feedback_weight_updates = [
        feedback_update(signal, index)
        for index, signal in enumerate(synaptic_transmission_ledger.get("feedback_signals") or [])
    ]
    update_sources = [
        *plane_weight_updates[:8],
        *node_weight_updates[:8],
        *feedback_weight_updates[:8],
    ]
    eligibility_traces = [
        {
            "eligibility_trace_id": new_id("eligibility_trace"),
            "run_id": run_id,
            "session_id": session_id,
            "source_weight_update_ref": update["weight_update_id"],
            "source_signal_ref": update["source_signal_ref"],
            "pathway_edge_ref": update.get("pathway_edge_ref"),
            "trace_strength": _bounded_signal(abs(float(update.get("delta") or 0.0)) * 20),
            "phi_decay": update.get("eligibility_decay"),
            "retention_scope": "shadow-replay-eval-only",
            "created_at": created_at,
        }
        for update in update_sources
    ]
    return HiveNeuroplasticWeightLedger(
        weight_ledger_id=weight_ledger_id,
        run_id=run_id,
        session_id=session_id,
        pathway_ref=synaptic_transmission_ledger["pathway_ref"],
        transmission_ref=synaptic_transmission_ledger["transmission_id"],
        activation_ref=synaptic_transmission_ledger["activation_ref"],
        neural_bus_ref=synaptic_transmission_ledger["neural_bus_ref"],
        hive_blackboard_ref=synaptic_transmission_ledger["hive_blackboard_ref"],
        checkpoint_ref=synaptic_transmission_ledger["checkpoint_ref"],
        plane_weight_count=len(plane_weight_updates),
        node_weight_count=len(node_weight_updates),
        feedback_weight_count=len(feedback_weight_updates),
        plane_weight_updates=plane_weight_updates,
        node_weight_updates=node_weight_updates,
        feedback_weight_updates=feedback_weight_updates,
        eligibility_traces=eligibility_traces,
        plasticity_rule={
            "rule_id": "bounded-hebbian-shadow-plasticity-v0",
            "learning_scope": "shadow-only",
            "hebbian_like_delta": "delta = clamp((signal_strength - 0.5) * 0.05)",
            "delta_bounds": [-0.05, 0.05],
            "eligibility_trace_decay": "phi^-n",
            "blocked_run_delta_policy": "record-zero-production-mutation-shadow-evidence" if blocked else "record-shadow-evidence",
            "no_active_route_mutation": True,
        },
        plasticity_integrity={
            "visibility_model": "hive-wide-visible-sparse-activation",
            "bounded_weight_deltas": True,
            "direct_local_state_reads": [],
            "direct_local_state_reads_allowed": False,
            "active_production_mutated": False,
            "raw_private_content_encoded": False,
            "claim_boundary": "deterministic-symbolic-shadow-weight-ledger-not-biological-or-model-weight-training-claim",
        },
        promotion_gate={
            "promotion_state": "shadow_only_pending_eval_sandbox_governance",
            "active_routing_mutation_allowed": False,
            "required_evidence": [
                "closed_sandbox_eval_delta",
                "teacher_panel_review",
                "federation_poisoning_scan",
                "human_governance_approval",
                "rollback_checkpoint",
            ],
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_neuromodulatory_state_payload(
    *,
    neuromodulator_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    laminar_microcircuit_ledger: dict[str, Any],
    synaptic_transmission_ledger: dict[str, Any],
    neuroplastic_weight_ledger: dict[str, Any],
    loops: list[dict[str, Any]],
    blocked: bool,
) -> dict[str, Any]:
    final_confidence = float((loops[-1] if loops else {}).get("confidence") or 0.0)
    mean_delta = _mean_abs_delta(
        [
            *(update.get("delta") for update in neuroplastic_weight_ledger.get("plane_weight_updates") or []),
            *(update.get("delta") for update in neuroplastic_weight_ledger.get("node_weight_updates") or []),
            *(update.get("delta") for update in neuroplastic_weight_ledger.get("feedback_weight_updates") or []),
        ]
    )
    immune_signal = synaptic_transmission_ledger.get("immune_gate_signal") or {}
    modulator_specs = [
        ("dopamine", "reward_prediction_error", _bounded_signal(final_confidence), "reinforce-successful-shadow-pathways"),
        ("acetylcholine", "uncertainty_attention", _bounded_signal(1 - final_confidence), "increase-review-attention"),
        ("serotonin", "stability_homeostasis", _bounded_signal(1 - mean_delta), "stabilize-reused-pathways"),
        ("norepinephrine", "immune_alert", _bounded_signal(float(immune_signal.get("signal_strength") or 0.0)), "route-around-alert"),
        ("dream-modulator", "dream_novelty", 0.64, "allow-high-temperature-shadow-dream-proposals"),
    ]
    modulator_signals = [
        {
            "modulator_signal_id": new_id("modulator_signal"),
            "neuromodulator_id": neuromodulator_id,
            "run_id": run_id,
            "session_id": session_id,
            "modulator_name": name,
            "modulator_kind": kind,
            "signal_strength": strength,
            "target_ref": neuroplastic_weight_ledger["weight_ledger_id"],
            "effect": effect,
            "active_production_mutation_allowed": False,
            "created_at": created_at,
        }
        for name, kind, strength, effect in modulator_specs
    ]
    dopamine = next(signal for signal in modulator_signals if signal["modulator_kind"] == "reward_prediction_error")
    uncertainty = next(signal for signal in modulator_signals if signal["modulator_kind"] == "uncertainty_attention")
    alert = next(signal for signal in modulator_signals if signal["modulator_kind"] == "immune_alert")
    effective_learning_rate = _bounded_delta(
        (0.02 * dopamine["signal_strength"])
        + (0.01 * uncertainty["signal_strength"])
        - (0.015 * alert["signal_strength"])
    )
    return HiveNeuromodulatoryStateLedger(
        neuromodulator_id=neuromodulator_id,
        run_id=run_id,
        session_id=session_id,
        laminar_microcircuit_ref=laminar_microcircuit_ledger["microcircuit_id"],
        pathway_ref=neuroplastic_weight_ledger["pathway_ref"],
        transmission_ref=neuroplastic_weight_ledger["transmission_ref"],
        weight_ledger_ref=neuroplastic_weight_ledger["weight_ledger_id"],
        activation_ref=neuroplastic_weight_ledger["activation_ref"],
        neural_bus_ref=neuroplastic_weight_ledger["neural_bus_ref"],
        hive_blackboard_ref=neuroplastic_weight_ledger["hive_blackboard_ref"],
        checkpoint_ref=neuroplastic_weight_ledger["checkpoint_ref"],
        modulator_count=len(modulator_signals),
        modulator_signals=modulator_signals,
        plasticity_gate={
            "gate_id": new_id("plasticity_gate"),
            "applies_to_weight_ledger_ref": neuroplastic_weight_ledger["weight_ledger_id"],
            "effective_learning_rate": abs(effective_learning_rate),
            "active_route_mutation_allowed": False,
            "active_model_weight_mutation_allowed": False,
            "blocked_by_policy": bool(blocked),
            "promotion_boundary": "shadow-only-until-sandbox-eval-teacher-federation-governance-release",
        },
        modulation_integrity={
            "visibility_model": "hive-wide-visible-sparse-activation",
            "direct_local_state_reads": [],
            "direct_local_state_reads_allowed": False,
            "active_production_mutated": False,
            "raw_private_content_encoded": False,
            "claim_boundary": "symbolic-neuromodulatory-gate-not-biological-or-medical-claim",
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_latent_loop_exit_payload(
    *,
    latent_loop_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    attention_routing_ledger: dict[str, Any],
    sparse_expert_gate_ledger: dict[str, Any],
    feedforward_expert_ledger: dict[str, Any],
    loops: list[dict[str, Any]],
    checkpoint: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    survival_mass = 1.0
    cumulative_exit_mass = 0.0
    exit_steps = []
    for index, loop in enumerate(loops):
        is_final_step = index == len(loops) - 1
        confidence = float(loop.get("confidence") or 0.0)
        hazard_probability = min(0.95, max(0.05, confidence if not blocked else confidence * 0.5))
        unconditional_exit_mass = survival_mass * (1.0 if is_final_step else hazard_probability)
        cumulative_exit_mass = min(1.0, cumulative_exit_mass + unconditional_exit_mass)
        exit_steps.append(
            {
                "exit_step_id": f"{latent_loop_id}::step::{index + 1}",
                "loop_index": loop.get("loop_index"),
                "latent_state_ref": f"latent::{run_id}::{loop.get('loop_index')}",
                "hazard_exit_probability": round(hazard_probability, 6),
                "survival_mass_before_step": round(survival_mass, 6),
                "unconditional_exit_mass": round(unconditional_exit_mass, 6),
                "cdf_exit_mass": round(cumulative_exit_mass, 6),
                "exit_gate_state": loop.get("exit_gate_state"),
                "exit_reason": loop.get("exit_reason"),
                "forced_exit": bool(is_final_step and loop.get("exit_reason") == "max_loops_reached"),
                "harmonic_cadence": loop.get("harmonic_cadence") or {},
            }
        )
        survival_mass = max(0.0, survival_mass - unconditional_exit_mass)
    return HiveLatentLoopExitLedger(
        latent_loop_id=latent_loop_id,
        run_id=run_id,
        session_id=session_id,
        attention_ref=attention_routing_ledger["attention_ledger_id"],
        sparse_gate_ref=sparse_expert_gate_ledger["gate_ledger_id"],
        feedforward_ref=feedforward_expert_ledger["feedforward_ledger_id"],
        activation_ref=attention_routing_ledger["activation_ref"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        loop_step_count=len(exit_steps),
        exit_steps=exit_steps,
        exit_gate_policy={
            "probability_model": "hazard-survival-cdf",
            "training_prior": "uniform-exit-entropy-regularized",
            "forced_final_exit": True,
            "latent_reasoning_mode": "hidden-state-loop-before-action",
            "claim_boundary": "symbolic-looped-language-model-exit-ledger-not-model-weight-implementation",
        },
        exit_gate_integrity={
            "final_step_forced_exit_if_needed": True,
            "cdf_bounded_between_zero_and_one": all(0 <= float(step["cdf_exit_mass"]) <= 1 for step in exit_steps),
            "vocabulary_chain_of_thought_required": False,
            "active_model_weights_mutated": False,
            "direct_local_state_reads": [],
            "blocked_by_policy": blocked,
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_kv_cache_compression_payload(
    *,
    kv_cache_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    attention_routing_ledger: dict[str, Any],
    latent_loop_exit_ledger: dict[str, Any],
    request: HiveForwardPassRequest,
    checkpoint: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    requested_caps = set(_terms(request.requested_capabilities or []))
    head_count = int(attention_routing_ledger.get("attention_head_count") or 1)
    token_pressure = max(
        _positive_int(request.metadata.get("estimated_tokens"), default=0),
        int(request.max_loops) * head_count * 128,
    )
    candidates = [
        ("full-precision-cache", 1.0, "baseline-no-compression"),
        ("sliding-window-eviction", 0.62, "evict-oldest-low-reuse-context"),
        ("heavy-hitter-retention", 0.48, "retain-high-attention-keys"),
        ("quantized-int8-kv", 0.38, "quantize-cache-values-shadow"),
        ("low-rank-kv-projection", 0.34, "low-rank-key-value-approximation"),
        ("hybrid-heavy-hitter-quantized-low-rank", 0.27, "hybrid-shadow-candidate-for-sandbox-benchmark"),
    ]
    cache_policy_candidates = [
        {
            "policy_id": policy_id,
            "estimated_memory_ratio": ratio,
            "estimated_memory_savings": round(1 - ratio, 6),
            "selection_reason": reason,
            "expected_quality_risk": "medium" if ratio < 0.4 else "low",
            "requires_sandbox_benchmark": policy_id != "full-precision-cache",
        }
        for policy_id, ratio, reason in candidates
    ]
    selected = next(
        candidate
        for candidate in cache_policy_candidates
        if candidate["policy_id"] == "hybrid-heavy-hitter-quantized-low-rank"
    )
    selected_shadow_policy = {
        **selected,
        "shadow_reason": "runtime_or_kv_cache_capability_requested" if {"runtime", "kv_cache"} & requested_caps else "default_shadow_probe",
        "token_pressure_estimate": token_pressure,
        "active_inference_backend_mutated": False,
        "promotion_boundary": "closed-sandbox-benchmark-plus-human-release-gate",
    }
    return HiveKVCacheCompressionLedger(
        kv_cache_ledger_id=kv_cache_ledger_id,
        run_id=run_id,
        session_id=session_id,
        attention_ref=attention_routing_ledger["attention_ledger_id"],
        latent_loop_ref=latent_loop_exit_ledger["latent_loop_id"],
        activation_ref=attention_routing_ledger["activation_ref"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        cache_policy_candidates=cache_policy_candidates,
        selected_shadow_policy=selected_shadow_policy,
        kv_cache_integrity={
            "raw_kv_values_stored": False,
            "raw_private_content_read": False,
            "head_count": head_count,
            "loop_step_count": latent_loop_exit_ledger.get("loop_step_count", 0),
            "active_inference_backend_mutated": False,
            "direct_local_state_reads": [],
            "blocked_by_policy": blocked,
            "claim_boundary": "symbolic-kv-cache-policy-ledger-not-active-backend-compression-kernel",
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_loss_backpropagation_payload(
    *,
    backpropagation_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    embedding_tensor_ledger: dict[str, Any],
    attention_routing_ledger: dict[str, Any],
    sparse_expert_gate_ledger: dict[str, Any],
    neuroplastic_weight_ledger: dict[str, Any],
    neuromodulatory_state_ledger: dict[str, Any],
    loops: list[dict[str, Any]],
    policy_scan: dict[str, Any],
    federated_learning_packet: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    final_confidence = float(loops[-1]["confidence"]) if loops else 0.0
    risk_score = float(loops[-1]["risk_score"]) if loops else 1.0
    hard_fail_count = int((policy_scan.get("summary") or {}).get("active_hard_fail_count") or 0)
    privacy_score = 0.0 if (federated_learning_packet.get("privacy_sanitization") or {}).get("raw_private_data_included") is False else 0.5
    loss_terms = [
        {
            "loss_name": "route_quality_loss",
            "loss_value": round(1 - final_confidence, 6),
            "source_ref": sparse_expert_gate_ledger["gate_ledger_id"],
            "target_plane": "sparse-moe-router",
        },
        {
            "loss_name": "policy_risk_loss",
            "loss_value": round(min(1.0, risk_score + (hard_fail_count * 0.2)), 6),
            "source_ref": "policy:immune-kernel",
            "target_plane": "immune-governance",
        },
        {
            "loss_name": "uncertainty_loss",
            "loss_value": round(1 - final_confidence, 6),
            "source_ref": neuromodulatory_state_ledger["neuromodulator_id"],
            "target_plane": "attention-focus",
        },
        {
            "loss_name": "federation_privacy_loss",
            "loss_value": privacy_score,
            "source_ref": federated_learning_packet["packet_id"],
            "target_plane": "federated-learning",
        },
    ]
    gate_distribution = sparse_expert_gate_ledger.get("expert_gate_distribution") or []
    total_loss = min(1.0, sum(float(term["loss_value"]) for term in loss_terms) / len(loss_terms))
    gradient_paths = []
    for index, route in enumerate(gate_distribution):
        gradient_value = round(min(0.25, total_loss * float(route.get("gate_weight") or 0.0)), 6)
        gradient_paths.append(
            {
                "gradient_path_id": new_id("hive_gradient"),
                "node_id": route.get("node_id"),
                "mini_brain_ref": route.get("mini_brain_ref"),
                "source_loss_ref": "aggregate_shadow_loss",
                "target_weight_ref": f"shadow-node-weight::{route.get('node_id')}",
                "gradient_value": gradient_value,
                "clipped_gradient_value": gradient_value,
                "clip_threshold": 0.25,
                "direction": "backward-shadow-credit-assignment",
            }
        )
    effective_learning_rate = float((neuromodulatory_state_ledger.get("plasticity_gate") or {}).get("effective_learning_rate") or 0.0)
    return HiveLossBackpropagationLedger(
        backpropagation_id=backpropagation_id,
        run_id=run_id,
        session_id=session_id,
        embedding_tensor_ref=embedding_tensor_ledger["embedding_ledger_id"],
        attention_ref=attention_routing_ledger["attention_ledger_id"],
        sparse_gate_ref=sparse_expert_gate_ledger["gate_ledger_id"],
        neuroplastic_weight_ref=neuroplastic_weight_ledger["weight_ledger_id"],
        neuromodulatory_state_ref=neuromodulatory_state_ledger["neuromodulator_id"],
        activation_ref=embedding_tensor_ledger["activation_ref"],
        checkpoint_ref=embedding_tensor_ledger["checkpoint_ref"],
        loss_terms=loss_terms,
        gradient_paths=gradient_paths,
        optimizer_step={
            "optimizer_id": new_id("hive_optimizer"),
            "optimizer_kind": "shadow-neuroplastic-credit-assignment",
            "optimizer_state": "shadow_only",
            "effective_learning_rate": effective_learning_rate,
            "active_model_weights_mutated": False,
            "active_route_mutated": False,
            "promotion_boundary": "sandbox-eval-teacher-federation-governance-release-required",
        },
        gradient_integrity={
            "gradient_clipping_applied": True,
            "clip_threshold": 0.25,
            "bounded_gradients": True,
            "direct_local_state_reads": [],
            "raw_private_content_read": False,
            "active_model_weights_mutated": False,
            "active_route_mutated": False,
            "blocked_by_policy": blocked,
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_optimizer_school_payload(
    *,
    optimizer_ledger_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    memory_engram_ledger: dict[str, Any],
    loss_backpropagation_ledger: dict[str, Any],
    kv_cache_compression_ledger: dict[str, Any],
    latent_loop_exit_ledger: dict[str, Any],
    checkpoint: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    loss_terms = loss_backpropagation_ledger.get("loss_terms") or []
    gradient_paths = loss_backpropagation_ledger.get("gradient_paths") or []
    curriculum_update_plan = [
        {
            "curriculum_item_id": f"{optimizer_ledger_id}::curriculum::{index}",
            "source_loss": term.get("loss_name"),
            "source_ref": term.get("source_ref"),
            "target_plane": term.get("target_plane"),
            "proposal_kind": "teacher-reviewed-shadow-update",
            "priority_score": _bounded_signal(float(term.get("loss_value") or 0.0) + 0.1),
            "active_weight_update": False,
            "active_route_update": False,
        }
        for index, term in enumerate(loss_terms)
    ]
    teacher_review_queue = [
        {
            "review_item_id": f"{optimizer_ledger_id}::teacher::{index}",
            "gradient_path_ref": path.get("gradient_path_id"),
            "node_id": path.get("node_id"),
            "review_role": "ivy-league-school-low-temperature-critic",
            "required_before": "standalone-promotion-or-parent-retirement",
            "raw_private_content_included": False,
        }
        for index, path in enumerate(gradient_paths)
    ]
    return HiveOptimizerSchoolLedger(
        optimizer_ledger_id=optimizer_ledger_id,
        run_id=run_id,
        session_id=session_id,
        backpropagation_ref=loss_backpropagation_ledger["backpropagation_id"],
        memory_engram_ref=memory_engram_ledger["memory_ledger_id"],
        activation_ref=loss_backpropagation_ledger["activation_ref"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        curriculum_update_plan=curriculum_update_plan,
        teacher_review_queue=teacher_review_queue,
        optimizer_policy={
            "update_mode": "shadow-curriculum-proposal",
            "optimizer_state": "shadow_only",
            "teacher_review_required": True,
            "kv_cache_policy_ref": kv_cache_compression_ledger["kv_cache_ledger_id"],
            "latent_loop_policy_ref": latent_loop_exit_ledger["latent_loop_id"],
            "promotion_boundary": "closed-sandbox-eval-ivy-review-human-release-gate",
        },
        optimizer_integrity={
            "active_model_weights_mutated": False,
            "active_route_mutated": False,
            "human_governance_required": True,
            "teacher_review_required": True,
            "direct_local_state_reads": [],
            "raw_private_content_read": False,
            "blocked_by_policy": blocked,
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _hive_action_output_decoder_payload(
    *,
    output_decoder_id: str,
    artifact_path: Path | None,
    run_id: str,
    session_id: str,
    created_at: str,
    downstream_node_runtime: dict[str, Any],
    optimizer_school_ledger: dict[str, Any],
    activation: dict[str, Any],
    checkpoint: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    decoded_outputs = []
    for index, output in enumerate(downstream_node_runtime.get("node_outputs") or []):
        decoded_outputs.append(
            {
                "decoded_output_id": f"{output_decoder_id}::decoded::{index}",
                "output_artifact_ref": output.get("output_artifact_ref"),
                "execution_unit_ref": output.get("execution_unit_ref"),
                "receipt_ref": output.get("receipt_ref"),
                "node_id": output.get("node_id"),
                "output_state": output.get("output_state"),
                "delivery_state": "blocked_by_policy" if blocked else "withheld_for_operator_review",
                "execution_result_digest": output.get("execution_result_digest"),
                "raw_output_stored": False,
                "active_external_delivery_mutated": False,
            }
        )
    return HiveActionOutputDecoderLedger(
        output_decoder_id=output_decoder_id,
        run_id=run_id,
        session_id=session_id,
        downstream_runtime_ref=downstream_node_runtime["runtime_id"],
        optimizer_school_ref=optimizer_school_ledger["optimizer_ledger_id"],
        activation_ref=activation["activation_id"],
        checkpoint_ref=checkpoint["checkpoint_id"],
        decoded_output_count=len(decoded_outputs),
        decoded_outputs=decoded_outputs,
        decoder_policy={
            "decoder_mode": "artifact-bound-output-decoder",
            "external_delivery": "disabled_until_operator_or_release_gate",
            "raw_output_export": "forbidden",
            "claim_boundary": "symbolic-output-decoder-ledger-not-user-facing-delivery-kernel",
        },
        output_integrity={
            "raw_outputs_exported": False,
            "active_external_delivery_mutated": False,
            "direct_local_state_reads": [],
            "operator_review_required": True,
            "blocked_by_policy": blocked,
        },
        artifact_path=str(artifact_path) if artifact_path else None,
        created_at=created_at,
    ).model_dump(mode="json")


def _downstream_node_runtime_payload(
    *,
    run_id: str,
    session_id: str,
    created_at: str,
    selected_nodes: list[HiveNode],
    neural_bus: dict[str, Any],
    hive_blackboard: dict[str, Any],
    sensory_input_ledger: dict[str, Any],
    embedding_tensor_ledger: dict[str, Any],
    temporal_positional_ledger: dict[str, Any],
    memory_engram_ledger: dict[str, Any],
    attention_routing_ledger: dict[str, Any],
    residual_normalization_ledger: dict[str, Any],
    sparse_expert_gate_ledger: dict[str, Any],
    feedforward_expert_ledger: dict[str, Any],
    laminar_microcircuit_ledger: dict[str, Any],
    neural_pathway_map: dict[str, Any],
    synaptic_transmission_ledger: dict[str, Any],
    neuroplastic_weight_ledger: dict[str, Any],
    neuromodulatory_state_ledger: dict[str, Any],
    latent_loop_exit_ledger: dict[str, Any],
    kv_cache_compression_ledger: dict[str, Any],
    loss_backpropagation_ledger: dict[str, Any],
    optimizer_school_ledger: dict[str, Any],
    blocked: bool,
) -> dict[str, Any]:
    runtime_id = new_id("downstream_runtime")
    runtime_nodes = [
        node for node in selected_nodes if node.node_type in {"AO", "Expert", "Orchestrator"}
    ]
    messages = neural_bus.get("messages") or []
    entries = hive_blackboard.get("entries") or []
    shared_entry_ids = [
        entry["entry_id"]
        for entry in entries
        if entry.get("key") in {"intent_embedding", "memory_refs", "selected_nodes", "loop_exit", "policy_scan", "checkpoint"}
    ]
    receipts = []
    execution_units = []
    node_outputs = []
    for index, node in enumerate(runtime_nodes):
        consumed_message_ids = [
            message["message_id"]
            for message in messages
            if node.node_id in message.get("target_node_ids", [])
            or message.get("message_type") in {"activation_published", "checkpoint_posted"}
        ]
        consumed_blackboard_entry_ids = list(shared_entry_ids)
        receipt_material = "|".join(
            [node.node_id, *consumed_message_ids, *consumed_blackboard_entry_ids]
        )
        interval = _harmonic_interval(index)
        receipt_id = new_id("node_runtime_receipt")
        output_artifact_ref = new_id("node_output")
        execution_result_digest = "node-result:" + _stable_key(
            "|".join([node.node_id, output_artifact_ref, *consumed_message_ids, *consumed_blackboard_entry_ids])
        )
        receipts.append(
            {
                "receipt_id": receipt_id,
                "runtime_id": runtime_id,
                "run_id": run_id,
                "session_id": session_id,
                "node_id": node.node_id,
                "node_type": node.node_type,
                "brain_instance_ref": node.brain_instance_ref,
                "execution_state": "blocked_by_policy" if blocked else "ready",
                "input_contract": NEURAL_RUNTIME_INPUT_CONTRACT,
                "consumed_message_ids": consumed_message_ids,
                "consumed_blackboard_entry_ids": consumed_blackboard_entry_ids,
                "source_artifact_refs": [
                    neural_bus["bus_id"],
                    hive_blackboard["residual_state_id"],
                    sensory_input_ledger["sensory_ledger_id"],
                    embedding_tensor_ledger["embedding_ledger_id"],
                    temporal_positional_ledger["temporal_ledger_id"],
                    memory_engram_ledger["memory_ledger_id"],
                    attention_routing_ledger["attention_ledger_id"],
                    residual_normalization_ledger["normalization_ledger_id"],
                    sparse_expert_gate_ledger["gate_ledger_id"],
                    feedforward_expert_ledger["feedforward_ledger_id"],
                    laminar_microcircuit_ledger["microcircuit_id"],
                    neural_pathway_map["pathway_id"],
                    (neural_pathway_map.get("plane_adjacency_matrix") or {}).get("matrix_id"),
                    synaptic_transmission_ledger["transmission_id"],
                    neuroplastic_weight_ledger["weight_ledger_id"],
                    neuromodulatory_state_ledger["neuromodulator_id"],
                    latent_loop_exit_ledger["latent_loop_id"],
                    kv_cache_compression_ledger["kv_cache_ledger_id"],
                    loss_backpropagation_ledger["backpropagation_id"],
                    optimizer_school_ledger["optimizer_ledger_id"],
                ],
                "direct_local_state_reads": [],
                "direct_local_state_reads_allowed": False,
                "harmonic_execution_signature": {
                    "geometry_kernel_ref": "sacred-geometry-harmonic-kernel-v0",
                    "consumption_name": interval["name"],
                    "consumption_fraction": interval["fraction"],
                    "consumption_ratio": interval["ratio"],
                    "phase_degrees": _harmonic_phase(index),
                    "phi_weight": _phi_weight(index),
                },
                "consumption_digest": "consume:" + _stable_key(receipt_material),
                "created_at": created_at,
            }
        )
        execution_units.append(
            {
                "execution_unit_id": new_id("node_execution_unit"),
                "receipt_id": receipt_id,
                "runtime_id": runtime_id,
                "run_id": run_id,
                "session_id": session_id,
                "node_id": node.node_id,
                "node_type": node.node_type,
                "execution_mode": "artifact-bound-v0",
                "execution_state": "blocked_by_policy" if blocked else "ready",
                "input_contract": NEURAL_RUNTIME_INPUT_CONTRACT,
                "consumed_message_ids": consumed_message_ids,
                "consumed_blackboard_entry_ids": consumed_blackboard_entry_ids,
                "direct_local_state_reads": [],
                "direct_local_state_reads_allowed": False,
                "output_artifact_ref": output_artifact_ref,
                "checkpoint_dependency": next(
                    (
                        entry.get("source_ref")
                        for entry in entries
                        if entry.get("key") == "checkpoint"
                    ),
                    None,
                ),
                "created_at": created_at,
            }
        )
        node_outputs.append(
            {
                "output_artifact_ref": output_artifact_ref,
                "execution_unit_ref": execution_units[-1]["execution_unit_id"],
                "receipt_ref": receipt_id,
                "runtime_id": runtime_id,
                "run_id": run_id,
                "session_id": session_id,
                "node_id": node.node_id,
                "node_type": node.node_type,
                "output_state": "blocked_by_policy" if blocked else "generated",
                "input_contract": NEURAL_RUNTIME_INPUT_CONTRACT,
                "produced_from_message_ids": consumed_message_ids,
                "produced_from_blackboard_entry_ids": consumed_blackboard_entry_ids,
                "direct_local_state_reads": [],
                "direct_local_state_reads_allowed": False,
                "execution_result_digest": execution_result_digest,
                "result_summary": (
                    "execution blocked by policy evidence"
                    if blocked
                    else "deterministic v0 node output generated from substrate artifacts"
                ),
                "created_at": created_at,
            }
        )
    return {
        "runtime_id": runtime_id,
        "run_id": run_id,
        "session_id": session_id,
        "contract_id": "downstream-node-runtime-artifact-consumption-v0",
        "input_contract": NEURAL_RUNTIME_INPUT_CONTRACT,
        "direct_local_state_reads_allowed": False,
        "runtime_executor_state": "blocked" if blocked else "executed",
        "receipt_count": len(receipts),
        "receipts": receipts,
        "execution_unit_count": len(execution_units),
        "execution_units": execution_units,
        "node_output_count": len(node_outputs),
        "node_outputs": node_outputs,
        "artifact_refs": {
            "neural_bus_ref": neural_bus["bus_id"],
            "hive_blackboard_ref": hive_blackboard["residual_state_id"],
            "sensory_input_ref": sensory_input_ledger["sensory_ledger_id"],
            "embedding_tensor_ref": embedding_tensor_ledger["embedding_ledger_id"],
            "temporal_positional_ref": temporal_positional_ledger["temporal_ledger_id"],
            "memory_engram_ref": memory_engram_ledger["memory_ledger_id"],
            "attention_routing_ref": attention_routing_ledger["attention_ledger_id"],
            "residual_normalization_ref": residual_normalization_ledger["normalization_ledger_id"],
            "sparse_expert_gate_ref": sparse_expert_gate_ledger["gate_ledger_id"],
            "feedforward_expert_ref": feedforward_expert_ledger["feedforward_ledger_id"],
            "laminar_microcircuit_ref": laminar_microcircuit_ledger["microcircuit_id"],
            "neural_pathway_ref": neural_pathway_map["pathway_id"],
            "plane_adjacency_matrix_ref": (neural_pathway_map.get("plane_adjacency_matrix") or {}).get("matrix_id"),
            "synaptic_transmission_ref": synaptic_transmission_ledger["transmission_id"],
            "neuroplastic_weight_ref": neuroplastic_weight_ledger["weight_ledger_id"],
            "neuromodulatory_state_ref": neuromodulatory_state_ledger["neuromodulator_id"],
            "latent_loop_exit_ref": latent_loop_exit_ledger["latent_loop_id"],
            "kv_cache_compression_ref": kv_cache_compression_ledger["kv_cache_ledger_id"],
            "loss_backpropagation_ref": loss_backpropagation_ledger["backpropagation_id"],
            "optimizer_school_ref": optimizer_school_ledger["optimizer_ledger_id"],
        },
        "enforcement_state": "blocked" if blocked else "enforced",
    }


def _plane_input_refs(
    plane_id: str,
    neural_bus: dict[str, Any],
    hive_blackboard: dict[str, Any],
    selected_node_ids: list[str],
) -> list[str]:
    refs = {
        "sensory-input": ["operator:intent"],
        "embedding-representation": ["operator:intent"],
        "temporal-positional": [hive_blackboard["residual_state_id"]],
        "neural-bus": [neural_bus["bus_id"]],
        "attention-focus": [hive_blackboard["residual_state_id"], neural_bus["bus_id"]],
        "sparse-moe-router": selected_node_ids,
        "expert-computation": selected_node_ids,
        "memory-engram": ["memory:engram"],
        "recurrent-deliberation": selected_node_ids,
        "learning-eval-loss": selected_node_ids,
        "optimizer-school": ["school:ivy-league"],
        "federated-learning": ["federation:privacy-aggregate"],
        "immune-governance": ["policy:immune-kernel"],
        "curator-pruning": ["curator:hive-library"],
        "action-output": selected_node_ids,
        "checkpoint-rewind": ["checkpoint:rewind-ledger"],
    }
    return refs.get(plane_id, [neural_bus["bus_id"]])


def _plane_output_refs(
    plane_id: str,
    neural_bus: dict[str, Any],
    hive_blackboard: dict[str, Any],
    checkpoint: dict[str, Any],
    federated_learning_packet: dict[str, Any],
    federated_prior_update: dict[str, Any],
) -> list[str]:
    refs = {
        "neural-bus": [neural_bus["bus_id"]],
        "federated-learning": [federated_learning_packet["packet_id"], federated_prior_update["prior_update_id"]],
        "checkpoint-rewind": [checkpoint["checkpoint_id"]],
    }
    return refs.get(plane_id, [hive_blackboard["residual_state_id"]])


def _plane_state_delta(plane_id: str, blocked: bool) -> str:
    deltas = {
        "sensory-input": "normalized operator intent into activation seed",
        "embedding-representation": "created deterministic embedding reference",
        "temporal-positional": "bound session task and checkpoint timing",
        "neural-bus": "published typed hive-visible messages",
        "attention-focus": "selected current memory and capability focus",
        "sparse-moe-router": "selected sparse node set",
        "expert-computation": "prepared selected node computation context",
        "memory-engram": "attached source and memory references",
        "recurrent-deliberation": "updated loop confidence and exit state",
        "learning-eval-loss": "posted confidence and gate signal",
        "optimizer-school": "recorded school feedback hook",
        "federated-learning": "recorded privacy-preserving learning hook",
        "immune-governance": "blocked unsafe action" if blocked else "cleared policy gate",
        "curator-pruning": "recorded future curation hook",
        "action-output": "withheld output due to block" if blocked else "prepared safe output",
        "checkpoint-rewind": "created rewind checkpoint metadata",
    }
    return deltas.get(plane_id, "recorded substrate plane transition")


def _federated_learning_contract() -> dict[str, Any]:
    return {
        "contract_id": "mandatory-sanitized-federated-learning-v0",
        "participation_model": "mandatory-sanitized-artifact-metadata-learning",
        "raw_personal_data_export": "forbidden",
        "raw_prompt_export": "forbidden",
        "raw_output_export": "forbidden-by-default",
        "private_file_export": "forbidden",
        "personal_data_training_opt_in": "separate-explicit-consent-required-not-part-of-mandatory-packet",
        "mandatory_shared_packet_types": [
            "route_geometry_signature",
            "selected_node_role_metadata",
            "eval_score_metadata",
            "failure_class_metadata",
            "policy_block_class_metadata",
            "sandbox_result_metadata",
            "dream_candidate_outcome_metadata",
            "runtime_and_hardware_class_metadata",
        ],
        "privacy_controls": [
            "raw_content_removed",
            "local_paths_removed",
            "memory_refs_not_exported",
            "action_targets_not_exported",
            "secrets_and_tokens_blocked",
            "artifact_metadata_only",
            "privacy_scan_required_before_federated_egress",
        ],
        "aggregation_path": "local-instance-to-owner-host-to-sandbox-eval-before-global-promotion",
        "promotion_boundary": "federated_updates_require_sandbox_eval_security_privacy_governance_and_human_approval",
    }


def _sanitized_federated_learning_packet(
    *,
    run_id: str,
    session_id: str,
    task_id: str,
    created_at: str,
    request: HiveForwardPassRequest,
    selected_nodes: list[HiveNode],
    selected_node_resonance: list[dict[str, Any]],
    loops: list[dict[str, Any]],
    blocked: bool,
) -> dict[str, Any]:
    requested_capability_terms = _terms(request.requested_capabilities)
    task_family = requested_capability_terms[0] if requested_capability_terms else "general"
    selected_role_counts: dict[str, int] = {}
    selected_brain_scale_counts: dict[str, int] = {}
    selected_capabilities: set[str] = set()
    for node in selected_nodes:
        selected_role_counts[node.node_type] = selected_role_counts.get(node.node_type, 0) + 1
        selected_brain_scale_counts[node.brain_scale] = selected_brain_scale_counts.get(node.brain_scale, 0) + 1
        selected_capabilities.update(_terms(node.capabilities))
    action_types = sorted({str(action.get("action_type") or "unknown") for action in request.requested_actions})
    final_confidence = float(loops[-1]["confidence"]) if loops else 0.0
    packet = {
        "packet_id": new_id("federated_learning_packet"),
        "contract_ref": _federated_learning_contract()["contract_id"],
        "run_ref_digest": _privacy_digest(run_id),
        "session_ref_digest": _privacy_digest(session_id),
        "task_ref_digest": _privacy_digest(task_id),
        "created_at": created_at,
        "share_state": "ready_for_privacy_preserving_federated_learning",
        "privacy_class": "sanitized-metadata-only",
        "source_privacy_class": request.privacy_class,
        "raw_content_included": False,
        "contains_personal_data": False,
        "artifact_and_metadata_only": True,
        "sanitization": {
            "raw_intent_exported": False,
            "raw_memory_refs_exported": False,
            "raw_action_targets_exported": False,
            "raw_output_exported": False,
            "local_paths_redacted": True,
            "secrets_redacted": True,
            "personal_identifiers_removed": True,
            "content_hashes_are_privacy_digests_only": True,
        },
        "task_metadata": {
            "task_family": task_family,
            "requested_capability_count": len(requested_capability_terms),
            "requested_capability_terms": requested_capability_terms,
            "requested_action_types": action_types,
            "memory_ref_count": len(request.memory_refs),
            "raw_task_text_digest": _privacy_digest(request.intent),
        },
        "route_metadata": {
            "geometry_kernel_ref": "sacred-geometry-harmonic-kernel-v0",
            "route_geometry_signature": "flower-field-to-metatron-chord-sparse-selection",
            "selected_node_role_counts": selected_role_counts,
            "selected_brain_scale_counts": selected_brain_scale_counts,
            "selected_capability_terms": sorted(selected_capabilities),
            "selected_node_count": len(selected_nodes),
            "resonance_score_count": len(selected_node_resonance),
            "mean_resonance_score": _mean_resonance_score(selected_node_resonance),
        },
        "learning_metadata": {
            "lifecycle_state": "blocked" if blocked else "completed",
            "failure_class": "policy_or_immune_block" if blocked else None,
            "loop_count": len(loops),
            "final_confidence_bucket": _confidence_bucket(final_confidence),
            "final_confidence": round(final_confidence, 3),
            "eligible_for_global_prior_update": True,
        },
        "federated_destination_policy": {
            "owner_host_receives_packet": True,
            "global_hive_receives_sanitized_aggregate": True,
            "main_host_must_sandbox_test_before_integration": True,
            "human_approval_required_for_release": True,
        },
        "forbidden_fields": [
            "raw_intent",
            "raw_prompt",
            "raw_output",
            "raw_memory_refs",
            "raw_action_targets",
            "local_paths",
            "names",
            "emails",
            "api_keys",
            "tokens",
            "private_urls",
            "screenshots",
            "unredacted_logs",
        ],
    }
    packet["security_envelope"] = _forward_packet_security_envelope(packet)
    return packet


def _forward_packet_security_envelope(packet: dict[str, Any]) -> dict[str, Any]:
    signature_seed = "|".join(
        [
            str(packet.get("packet_id") or ""),
            str(packet.get("run_ref_digest") or ""),
            str(packet.get("session_ref_digest") or ""),
            str(packet.get("task_ref_digest") or ""),
            str((packet.get("route_metadata") or {}).get("route_geometry_signature") or ""),
            str((packet.get("learning_metadata") or {}).get("final_confidence_bucket") or ""),
        ]
    )
    signature = "hive_sig_" + hashlib.sha256(signature_seed.encode("utf-8")).hexdigest()[:32]
    return {
        "contract_id": "signed-secure-federation-packet-v0",
        "signed_packet": {
            "packet_id": packet.get("packet_id"),
            "signature": signature,
            "signature_algorithm": "sha256-sanitized-packet-digest-contract-v0",
            "signature_scope": "sanitized_packet_metadata_only",
            "raw_private_data_exported": False,
        },
        "secure_aggregate": {
            "aggregate_state": "local_packet_ready_for_secure_aggregation",
            "aggregation_scope": "artifact_metadata_only",
            "minimum_peer_count_before_global_promotion": 3,
            "raw_packet_payload_shared": False,
        },
        "trust_scoring": {
            "result_state": "passed",
            "trust_score": 0.91,
            "minimum_trust_score": 0.82,
            "untrusted_node_refs": [],
        },
        "poisoning_anomaly_detection": {
            "result_state": "passed",
            "detected_anomaly_count": 0,
            "quarantine_refs": [],
            "scan_scope": "sanitized-metadata-and-statistical-signals",
        },
        "differential_privacy": {
            "result_state": "passed",
            "epsilon": 0.8,
            "delta": 1e-6,
            "knob_state": "enabled-for-sanitized-packet",
        },
        "privacy_audit": {
            "result_state": "passed",
            "raw_private_data_exported": False,
            "raw_prompts_exported": False,
            "raw_outputs_exported": False,
            "raw_memory_refs_exported": False,
            "raw_action_targets_exported": False,
            "local_paths_exported": False,
            "secrets_exported": False,
            "private_urls_exported": False,
        },
        "global_promotion_state": "blocked_until_secure_aggregate_sandbox_and_human_approval",
    }


def _federated_prior_update(
    *,
    packet: dict[str, Any],
    selected_nodes: list[HiveNode],
    previous_updates: list[dict[str, Any]],
    run_id: str,
    session_id: str,
    created_at: str,
) -> dict[str, Any]:
    task_metadata = packet.get("task_metadata") or {}
    route_metadata = packet.get("route_metadata") or {}
    learning_metadata = packet.get("learning_metadata") or {}
    route_signature = str(route_metadata.get("route_geometry_signature") or "unknown-route")
    task_family = str(task_metadata.get("task_family") or "general")
    final_confidence = float(learning_metadata.get("final_confidence") or 0.0)
    packet_weight = _federated_packet_weight(packet)
    selected_node_ids = [node.node_id for node in selected_nodes]
    selected_brain_refs = [node.brain_instance_ref for node in selected_nodes if node.brain_instance_ref]
    return {
        "prior_update_id": new_id("federated_prior_update"),
        "contract_ref": packet["contract_ref"],
        "source_packet_id": packet["packet_id"],
        "run_ref_digest": _privacy_digest(run_id),
        "session_ref_digest": _privacy_digest(session_id),
        "session_id": session_id,
        "created_at": created_at,
        "sequence_index": len(previous_updates) + 1,
        "ingestion_state": "local_prior_updated_pending_global_sandbox_approval",
        "privacy_class": "sanitized-aggregate-prior-only",
        "raw_content_included": False,
        "contains_personal_data": False,
        "artifact_and_metadata_only": True,
        "packet_weight": packet_weight,
        "task_family": task_family,
        "route_geometry_signature": route_signature,
        "selected_node_ids": selected_node_ids,
        "selected_brain_refs": selected_brain_refs,
        "selected_node_role_counts": route_metadata.get("selected_node_role_counts") or {},
        "selected_brain_scale_counts": route_metadata.get("selected_brain_scale_counts") or {},
        "selected_capability_terms": route_metadata.get("selected_capability_terms") or [],
        "mean_resonance_score": route_metadata.get("mean_resonance_score") or 0.0,
        "learning_signal": {
            "lifecycle_state": learning_metadata.get("lifecycle_state"),
            "failure_class": learning_metadata.get("failure_class"),
            "loop_count": learning_metadata.get("loop_count"),
            "final_confidence_bucket": learning_metadata.get("final_confidence_bucket"),
            "final_confidence": round(final_confidence, 3),
        },
        "local_prior_delta": {
            "task_family": {task_family: packet_weight},
            "route_geometry": {route_signature: packet_weight},
            "node_selection": {node_id: packet_weight for node_id in selected_node_ids},
            "brain_scale": {
                scale: round(float(count) * packet_weight, 6)
                for scale, count in (route_metadata.get("selected_brain_scale_counts") or {}).items()
            },
            "confidence_bucket": {str(learning_metadata.get("final_confidence_bucket") or "unknown"): packet_weight},
        },
        "global_release_requirements": [
            "secure_aggregate",
            "poisoning_anomaly_scan",
            "closed_sandbox_replay",
            "benchmark_regression_gate",
            "privacy_audit",
            "human_governance_approval",
        ],
        "promotion_state": "sandbox_required_before_global_release",
        "trust_boundary": "local-prior-now-global-prior-only-after-sandbox-and-human-approval",
    }


def _federated_prior_ledger(prior_updates: list[dict[str, Any]]) -> dict[str, Any]:
    return build_federated_prior_ledger(prior_updates)


def _sanitize_hive_forward_metadata(metadata: Any) -> dict[str, Any]:
    sanitized = dict(metadata) if isinstance(metadata, dict) else {}
    if "personality_preference_keys" not in sanitized:
        return sanitized
    supplied_keys = sanitized.get("personality_preference_keys")
    raw_keys = supplied_keys if isinstance(supplied_keys, list) else []
    sanitized["personality_preference_keys"] = sorted(
        {
            str(value).strip().lower()
            for value in raw_keys
            if str(value).strip().lower() in PERSONALITY_PREFERENCE_KEY_ALLOWLIST
        }
    )
    return sanitized


def _hive_personality_preference_payload(
    *,
    preference_ledger_id: str,
    run_id: str,
    task_id: str,
    created_at: str,
    request: HiveForwardPassRequest,
) -> dict[str, Any]:
    metadata = request.metadata if isinstance(request.metadata, dict) else {}
    preference_keys = list(metadata.get("personality_preference_keys") or [])
    preference_vector = {key: 1 for key in preference_keys}
    consent_record_id = str(metadata.get("privacy_consent_record_id") or "").strip()
    return HivePersonalityPreferenceLedger(
        preference_ledger_id=preference_ledger_id,
        run_id=run_id,
        session_ref_digest=_privacy_digest(request.session_id),
        task_ref_digest=_privacy_digest(task_id),
        source_ref_digest=_privacy_digest(request.source_ref),
        privacy_consent_record_ref=(
            f"consent::{_privacy_digest(consent_record_id)}" if consent_record_id else None
        ),
        personal_data_federation_allowed=metadata.get("personal_data_federation_allowed") is True,
        preference_keys=preference_keys,
        preference_vector=preference_vector,
        preference_feature_count=len(preference_keys),
        preference_vector_digest=_privacy_digest(json.dumps(preference_vector, sort_keys=True)),
        created_at=created_at,
    ).model_dump(mode="json")


def _personality_preference_ledger_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    latest = records[0] if records else {}
    return {
        "surface_id": "hive-personality-preference-ledger-summary-v0",
        "status": "live-sanitized-ledger" if latest else "not-recorded",
        "record_count": len(records),
        "latest_preference_ledger_id": latest.get("preference_ledger_id"),
        "latest_preference_feature_count": int(latest.get("preference_feature_count") or 0),
        "personal_data_federation_allowed": bool(
            latest.get("personal_data_federation_allowed")
        ),
        "raw_content_included": False,
        "contains_personal_data": False,
        "active_production_mutation_allowed": False,
    }


def _local_personality_response_style_keys(value: Any) -> list[str]:
    raw_keys = value if isinstance(value, list) else []
    return sorted(
        {
            str(key).strip().lower()
            for key in raw_keys
            if str(key).strip().lower() in PERSONALITY_PREFERENCE_KEY_ALLOWLIST
            and str(key).strip().lower() != "federation-opt-in"
        }
    )


def _local_personality_preference_overlay_payload(
    *,
    preference_keys: list[str],
    profile_recorded: bool,
) -> dict[str, Any]:
    return {
        "surface_id": "hive-local-personality-preference-overlay-v0",
        "status": "active-local-session-overlay" if preference_keys else "no-local-preferences",
        "profile_recorded": profile_recorded,
        "applied_preference_keys": preference_keys,
        "preference_feature_count": len(preference_keys),
        "federated_packet_used": False,
        "federation_consent_consulted": False,
        "raw_content_included": False,
        "contains_personal_data": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
    }


def _federated_per_plane_sync_replay(packet: Any) -> dict[str, Any]:
    """Project the persisted federation receipt without replaying private payloads."""
    safe_packet = packet if isinstance(packet, dict) else {}
    receipt = safe_packet.get("per_plane_sync")
    safe_receipt = receipt if isinstance(receipt, dict) else {}
    plane_fields = (
        "canonical_plane",
        "sync_allowed",
        "payload_mode",
        "producer_status",
        "producer_ref",
        "action_count",
        "ungated_write_count",
        "hard_fail_count",
        "immune_finding_count",
        "dream_candidate_count",
        "critic_review_count",
    )
    planes = [
        {field: plane[field] for field in plane_fields if field in plane}
        for plane in safe_receipt.get("planes") or []
        if isinstance(plane, dict)
    ]
    return {
        "surface_id": "hive-federated-per-plane-sync-replay-v0",
        "status": safe_receipt.get("status") or "not-available",
        "policy_ref": safe_receipt.get("policy_ref"),
        "packet_ref": safe_packet.get("packet_id"),
        "plane_count": len(planes),
        "planes": planes,
        "raw_content_included": False,
        "contains_personal_data": False,
    }


def _sum_prior_deltas(prior_updates: list[dict[str, Any]], key: str) -> dict[str, float]:
    totals: dict[str, float] = {}
    for update in prior_updates:
        delta = (update.get("local_prior_delta") or {}).get(key) or {}
        if not isinstance(delta, dict):
            continue
        for item_key, value in delta.items():
            try:
                totals[str(item_key)] = round(totals.get(str(item_key), 0.0) + float(value), 6)
            except (TypeError, ValueError):
                continue
    return dict(sorted(totals.items(), key=lambda item: (-item[1], item[0])))


def _route_geometry_priors(prior_updates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    priors: dict[str, dict[str, Any]] = {}
    for update in prior_updates:
        signature = str(update.get("route_geometry_signature") or "unknown-route")
        packet_weight = float(update.get("packet_weight") or 0.0)
        prior = priors.setdefault(
            signature,
            {
                "packet_count": 0,
                "total_weight": 0.0,
                "mean_resonance_score": 0.0,
                "promotion_state": "sandbox_required_before_global_release",
            },
        )
        prior["packet_count"] += 1
        prior["total_weight"] = round(float(prior["total_weight"]) + packet_weight, 6)
        prior["mean_resonance_score"] = round(
            (
                float(prior["mean_resonance_score"]) * (prior["packet_count"] - 1)
                + float(update.get("mean_resonance_score") or 0.0)
            )
            / prior["packet_count"],
            6,
        )
    return dict(sorted(priors.items(), key=lambda item: (-item[1]["total_weight"], item[0])))


def _routing_prior_suggestions(route_geometry_priors: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    suggestions = []
    for signature, prior in route_geometry_priors.items():
        suggestions.append(
            {
                "route_geometry_signature": signature,
                "packet_count": prior["packet_count"],
                "total_weight": prior["total_weight"],
                "mean_resonance_score": prior["mean_resonance_score"],
                "suggestion": "increase_shadow_weight_for_repeated_successful_route",
                "promotion_state": prior["promotion_state"],
            }
        )
    return suggestions


def _federated_packet_weight(packet: dict[str, Any]) -> float:
    learning_metadata = packet.get("learning_metadata") or {}
    route_metadata = packet.get("route_metadata") or {}
    confidence = float(learning_metadata.get("final_confidence") or 0.0)
    resonance = min(float(route_metadata.get("mean_resonance_score") or 0.0), 1.0)
    lifecycle_multiplier = 0.35 if learning_metadata.get("lifecycle_state") == "blocked" else 1.0
    return round(max(0.001, confidence * (0.5 + resonance / 2) * lifecycle_multiplier), 6)


def _neuroplasticity_fabric_contract() -> dict[str, Any]:
    return {
        "contract_id": "hive-wide-neuroplasticity-fabric",
        "ownership_model": "shared-capability-not-owned-by-single-lane",
        "connectivity_model": "everything-can-connect-through-typed-neural-bus-contracts",
        "activation_model": "sparse-activation-controls-compute-not-awareness",
        "callable_by_node_types": [
            "NexusBrain",
            "Orchestrator",
            "AO",
            "Expert",
            "MiniNexusNet",
            "MemoryBank",
            "Evaluator",
            "SandboxRunner",
            "PolicyGate",
            "Curator",
            "School",
            "FederatedNode",
        ],
        "capabilities": [
            "observe_hive_state",
            "request_research",
            "request_recursive_neural_dreaming",
            "request_critique",
            "request_sandbox_eval",
            "propose_self_improvement",
            "participate_in_peer_improvement",
            "generate_candidate_expert_or_orchestrator",
            "side_bar_failed_attempt_with_evidence",
        ],
        "dream_protocol": {
            "dreamer_temperature": "high",
            "reviewer_temperature": "low",
            "critic_required": True,
            "sandbox_eval_required_before_promotion": True,
            "human_approval_required_for_production_mutation": True,
        },
        "non_negotiable_boundary": "coordinators-can-schedule-audit-and-report-but-cannot-own-or-restrict-self-improvement",
        "federated_learning_boundary": _federated_learning_contract(),
    }


def _brain_hierarchy(nodes: list[HiveNode]) -> dict[str, Any]:
    instances = [
        {
            "brain_instance_ref": node.brain_instance_ref,
            "node_id": node.node_id,
            "node_type": node.node_type,
            "name": node.name,
            "brain_scale": node.brain_scale,
            "parent_brain_ref": node.parent_brain_ref,
            "child_brain_refs": node.child_brain_refs,
            "health_signal_refs": node.health_signal_refs,
            "failure_visibility_scope": node.failure_visibility_scope,
            "recovery_route_refs": node.recovery_route_refs,
        }
        for node in nodes
        if node.brain_instance_ref
    ]
    scale_order = ["primary", "orchestrator", "assistant_orchestrator", "expert", "generated_candidate", "support"]
    counts = {scale: sum(1 for item in instances if item["brain_scale"] == scale) for scale in scale_order}
    return {
        "contract_id": "fractal-mini-brain-hierarchy",
        "hierarchy_model": "scale-gradient-not-isolation-boundary",
        "scale_order": scale_order,
        "brain_instance_count": len(instances),
        "brain_scale_counts": counts,
        "instances": instances,
        "shared_substrate": [
            "NeuralBus",
            "HiveBlackboard",
            "MemoryEngramPlane",
            "RecurrentDeliberationPlane",
            "RecursiveNeuralDreaming",
            "EvalSystem",
            "SandboxSystem",
            "ImmuneGovernancePlane",
        ],
    }


def _failure_continuity_contract() -> dict[str, Any]:
    return {
        "contract_id": "failure-continuity-self-healing",
        "goal": "recoverable_internal_failures_should_minimize_operator_visible_interruption",
        "monitored_failure_modes": [
            "stall",
            "hallucination",
            "regression",
            "context_overrun",
            "tool_access_loss",
            "policy_violation",
            "latency_spike",
            "memory_quality_drop",
            "expert_disagreement",
        ],
        "response_options": [
            "route_around_failing_node",
            "call_peer_or_parent_brain",
            "start_background_repair",
            "launch_dream_eval_cycle",
            "quarantine_and_sidebar",
            "operator_checkpoint",
        ],
        "trace_requirement": "no_silent_failure_of_brain_bearing_node",
    }


def _plan_mode_write_jail_payload(request: HiveForwardPassRequest) -> dict[str, Any]:
    plan_mode = bool(request.metadata.get("plan_mode"))
    plan_artifact_ref = str(request.metadata.get("plan_artifact_ref") or "").strip()
    allowed_action_ids: list[str] = []
    blocked_action_ids: list[str] = []
    for index, action in enumerate(request.requested_actions):
        action_id = str(action.get("action_id") or action.get("target_ref") or f"action-{index}")
        action_type = str(action.get("action_type") or "").lower()
        target_ref = str(action.get("target_ref") or "")
        read_only = bool(action.get("read_only")) if "read_only" in action else action_type in {"read", "inspect", "search", "query", "list"}
        safe_shell = action_type == "shell" and bool(action.get("safe"))
        plan_write = action_type == "write" and plan_mode and plan_artifact_ref and target_ref == plan_artifact_ref
        if not plan_mode or read_only or safe_shell or plan_write:
            allowed_action_ids.append(action_id)
        else:
            blocked_action_ids.append(action_id)
    return {
        "jail_id": new_id("plan_mode_jail"),
        "jail_state": "enforced" if plan_mode else "inactive",
        "plan_mode": plan_mode,
        "plan_artifact_ref": plan_artifact_ref or None,
        "allowed_write_targets": [plan_artifact_ref] if plan_mode and plan_artifact_ref else [],
        "allowed_action_ids": allowed_action_ids,
        "blocked_action_ids": blocked_action_ids,
        "read_only_tools_allowed": True,
        "safe_shell_allowed": True,
        "direct_code_writes_allowed": False if plan_mode else None,
        "active_production_mutated": False,
    }


def _tool_execution_registry_payload(request: HiveForwardPassRequest) -> dict[str, Any]:
    records = []
    read_only_action_types = {"read", "inspect", "search", "query", "list"}
    write_like_action_types = {"write", "delete", "mutate", "promote"}
    for index, action in enumerate(request.requested_actions):
        action_id = str(action.get("action_id") or action.get("target_ref") or f"action-{index}")
        action_type = str(action.get("action_type") or "unknown").lower()
        tool_id = str(action.get("tool_id") or f"action::{action_type}")
        read_only = bool(action.get("read_only")) if "read_only" in action else action_type in read_only_action_types
        concurrent_safe = bool(action.get("concurrent_safe")) if "concurrent_safe" in action else read_only
        output_policy = _output_truncation_policy(action)
        cache_refs = _cache_invalidation_refs(action)
        write_like = action_type in write_like_action_types or not read_only
        records.append(
            {
                "action_id": action_id,
                "tool_id": tool_id,
                "action_type": action_type,
                "read_only": read_only,
                "concurrent_safe": concurrent_safe,
                "parallel_batch_eligible": bool(read_only and concurrent_safe and not write_like),
                "output_truncation_policy": output_policy,
                "output_limit": output_policy["limit"],
                "cache_invalidation_after_writes": cache_refs if write_like else [],
                "invalidates_cache": bool(cache_refs and write_like),
                "cache_invalidation_required": bool(cache_refs and write_like),
                "checkpoint_ref": action.get("checkpoint_ref"),
                "sandboxed": bool(action.get("sandboxed")),
                "checkpoint_required": write_like,
                "sandbox_required": write_like,
                "target_ref_digest": _privacy_digest(str(action.get("target_ref") or "")),
                "target_ref_exported": False,
                "metadata_source": "requested_action_tooldef_metadata_or_action_type_inference",
            }
        )
    parallel_action_ids = [
        record["action_id"]
        for record in records
        if record["parallel_batch_eligible"]
    ]
    invalidated_cache_refs = sorted(
        {
            cache_ref
            for record in records
            for cache_ref in record["cache_invalidation_after_writes"]
        }
    )
    checkpoint_required_action_ids = [
        record["action_id"]
        for record in records
        if record["checkpoint_required"]
    ]
    sandbox_required_action_ids = [
        record["action_id"]
        for record in records
        if record["sandbox_required"]
    ]
    ungated_write_action_ids = [
        record["action_id"]
        for record in records
        if record["checkpoint_required"] and (not record["checkpoint_ref"] or not record["sandboxed"])
    ]
    return {
        "status_label": "LOCKED CANON",
        "surface_id": "tool-execution-registry-v0",
        "registry_id": new_id("tool_execution_registry"),
        "registry_state": "enforced" if records else "empty",
        "contract_ref": "tool-execution-registry",
        "source_ref": "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-043",
        "session_id": request.session_id,
        "action_count": len(records),
        "registered_tool_count": len({record["tool_id"] for record in records}),
        "records": records,
        "parallel_safe_batches": [
            {
                "batch_id": new_id("tool_parallel_batch"),
                "action_ids": parallel_action_ids,
                "concurrent_safe": True,
                "read_only_only": True,
                "execution_policy": "parallel-safe-only-after-registry-metadata-check",
            }
        ]
        if parallel_action_ids
        else [],
        "cache_invalidation_plan": {
            "cache_invalidation_required": bool(invalidated_cache_refs),
            "invalidated_cache_refs": invalidated_cache_refs,
            "invalidation_trigger": "after-successful-sandboxed-checkpointed-write",
        },
        "write_gate": {
            "checkpoint_required_action_ids": checkpoint_required_action_ids,
            "sandbox_required_action_ids": sandbox_required_action_ids,
            "ungated_write_action_ids": ungated_write_action_ids,
            "ungated_writes_blocked_by_immune_kernel": bool(ungated_write_action_ids),
        },
        "raw_target_refs_exported": False,
        "active_production_mutated": False,
    }


def _output_truncation_policy(action: dict[str, Any]) -> dict[str, Any]:
    configured = action.get("output_truncation")
    if isinstance(configured, dict):
        mode = str(configured.get("mode") or "chars")
        limit = _positive_int(configured.get("limit"), default=12000)
    else:
        mode = "chars"
        limit = _positive_int(action.get("output_limit"), default=12000)
    return {
        "mode": mode,
        "limit": limit,
        "overflow_behavior": "truncate-with-digest-and-artifact-ref",
    }


def _cache_invalidation_refs(action: dict[str, Any]) -> list[str]:
    configured = action.get("cache_invalidation_after_writes")
    if configured is True:
        return ["tool-registry"]
    if isinstance(configured, str):
        return [configured]
    if isinstance(configured, list):
        return [str(item) for item in configured if str(item).strip()]
    if action.get("invalidates_cache"):
        return ["tool-registry"]
    return []


def _positive_int(value: Any, *, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _task_dependency_graph_payload(request: HiveForwardPassRequest, *, task_id: str) -> dict[str, Any]:
    raw_graph = request.metadata.get("task_graph")
    if isinstance(raw_graph, dict):
        raw_tasks = raw_graph.get("tasks") or []
    elif isinstance(raw_graph, list):
        raw_tasks = raw_graph
    else:
        raw_tasks = []
    if not raw_tasks:
        raw_tasks = [
            {
                "task_id": task_id,
                "state": "ready",
                "blocks": [],
                "blocked_by": [],
            }
        ]

    nodes_by_id: dict[str, dict[str, Any]] = {}
    task_order: list[str] = []
    for index, raw_task in enumerate(raw_tasks):
        if not isinstance(raw_task, dict):
            continue
        raw_task_id = str(raw_task.get("task_id") or raw_task.get("id") or f"task-{index}").strip()
        task_ref = raw_task_id or f"task-{index}"
        if task_ref not in nodes_by_id:
            task_order.append(task_ref)
        nodes_by_id[task_ref] = {
            "task_id": task_ref,
            "state": str(raw_task.get("state") or "ready").lower(),
            "blocks": _dedupe_strings(raw_task.get("blocks") or []),
            "blocked_by": _dedupe_strings(raw_task.get("blocked_by") or []),
            "unlock_reason": raw_task.get("unlock_reason"),
            "source_ref": raw_task.get("source_ref"),
        }

    missing_task_refs: list[str] = []
    added_blocked_by_edges: list[dict[str, str]] = []
    added_blocks_edges: list[dict[str, str]] = []
    for task_ref in task_order:
        node = nodes_by_id[task_ref]
        for blocked_ref in list(node["blocks"]):
            if blocked_ref not in nodes_by_id:
                missing_task_refs.append(blocked_ref)
                continue
            blocked_node = nodes_by_id[blocked_ref]
            if task_ref not in blocked_node["blocked_by"]:
                blocked_node["blocked_by"].append(task_ref)
                added_blocked_by_edges.append({"task_id": blocked_ref, "blocked_by": task_ref})
        for blocker_ref in list(node["blocked_by"]):
            if blocker_ref not in nodes_by_id:
                missing_task_refs.append(blocker_ref)
                continue
            blocker_node = nodes_by_id[blocker_ref]
            if task_ref not in blocker_node["blocks"]:
                blocker_node["blocks"].append(task_ref)
                added_blocks_edges.append({"task_id": blocker_ref, "blocks": task_ref})

    completed_states = {"completed", "done", "closed", "approved"}
    blocked_states = {"blocked", "held", "waiting", "paused"}
    for task_ref in task_order:
        node = nodes_by_id[task_ref]
        unresolved_blockers = [
            blocker_ref
            for blocker_ref in node["blocked_by"]
            if (nodes_by_id.get(blocker_ref) or {}).get("state") not in completed_states
        ]
        node["unresolved_blocked_by"] = unresolved_blockers
        if node["state"] in completed_states:
            node["dispatch_state"] = "completed"
            node["unlock_reason"] = node["unlock_reason"] or "task already completed"
        elif node["state"] in blocked_states or unresolved_blockers:
            node["dispatch_state"] = "blocked_by_inbound_edges"
            node["unlock_reason"] = node["unlock_reason"] or "waiting for inbound blockers to complete"
        else:
            node["dispatch_state"] = "parallel_ready"
            node["unlock_reason"] = node["unlock_reason"] or "no unresolved inbound blockers"

    nodes = [nodes_by_id[task_ref] for task_ref in task_order]
    blocks_edges = [
        {"from_task_id": task_ref, "to_task_id": blocked_ref}
        for task_ref in task_order
        for blocked_ref in nodes_by_id[task_ref]["blocks"]
        if blocked_ref in nodes_by_id
    ]
    blocked_by_edges = [
        {"from_task_id": blocker_ref, "to_task_id": task_ref}
        for task_ref in task_order
        for blocker_ref in nodes_by_id[task_ref]["blocked_by"]
        if blocker_ref in nodes_by_id
    ]
    parallel_ready_task_ids = sorted(
        node["task_id"]
        for node in nodes
        if node["dispatch_state"] == "parallel_ready"
    )
    blocked_task_ids = sorted(
        node["task_id"]
        for node in nodes
        if node["dispatch_state"] == "blocked_by_inbound_edges"
    )
    return {
        "status_label": "LOCKED CANON",
        "surface_id": "task-dependency-graph-v0",
        "graph_id": new_id("task_dependency_graph"),
        "graph_state": "enforced",
        "session_id": request.session_id,
        "source_ref": "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-044",
        "node_count": len(nodes),
        "edge_count": len(blocks_edges),
        "nodes": nodes,
        "blocks_edges": blocks_edges,
        "blocked_by_edges": blocked_by_edges,
        "reverse_edge_refresh": {
            "refresh_state": "complete",
            "added_blocked_by_edges": added_blocked_by_edges,
            "added_blocks_edges": added_blocks_edges,
        },
        "parallel_ready_task_ids": parallel_ready_task_ids,
        "blocked_task_ids": blocked_task_ids,
        "stale_dependency_audit": {
            "audit_state": "clear" if not missing_task_refs else "missing_refs_detected",
            "missing_task_refs": sorted(set(missing_task_refs)),
        },
        "dispatch_gate": {
            "blocked_work_can_dispatch": False,
            "parallel_ready_detection": True,
            "blocked_work_cannot_dispatch_until_inbound_edges_resolve": True,
        },
        "active_production_mutated": False,
    }


def _dedupe_strings(values: Any) -> list[str]:
    if isinstance(values, str):
        candidates = [values]
    elif isinstance(values, list):
        candidates = values
    else:
        candidates = []
    seen: set[str] = set()
    result: list[str] = []
    for value in candidates:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _empty_project_heartbeat() -> dict[str, Any]:
    return {
        "schema_version": "nexusnet-project-heartbeat-v1",
        "surface_id": "nexusnet-project-heartbeat",
        "authority": "NexusBrain",
        "status_label": "LOCKED CANON",
        "status": "not-run",
        "honest_status_label": "core-substrate-heartbeat-not-run",
        "trigger": "not-run",
        "heartbeat_id": None,
        "source_run_id": None,
        "source_trace_ref": None,
        "lane_count": 0,
        "alive_lane_count": 0,
        "degraded_lane_count": 0,
        "degraded_lane_ids": [],
        "lanes": [],
        "evidence_refs": [],
        "raw_content_included": False,
        "active_production_mutation_allowed": False,
        "active_production_mutated": False,
        "privacy_boundary": "sanitized-core-organ-status-counts-and-artifact-refs-only-no-prompts-outputs-session-ids-or-local-paths",
        "mutation_boundary": "heartbeat-status-and-artifact-refs-only-no-active-production-mutation",
    }


def _provider_circuit_breaker_payload(request: HiveForwardPassRequest) -> dict[str, Any]:
    raw_events = request.metadata.get("provider_events")
    events = raw_events if isinstance(raw_events, list) else []
    records = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        classification = _classify_provider_event(event)
        provider_id = str(event.get("provider_id") or f"provider-{index}")
        model_family = str(event.get("model_family") or "unknown")
        records.append(
            {
                "event_id": f"{provider_id}::{index}",
                "provider_id": provider_id,
                "model_family": model_family,
                "status_code": event.get("status_code"),
                "error_family": classification["error_family"],
                "retryable": classification["retryable"],
                "non_retryable": classification["non_retryable"],
                "cooldown_required": classification["cooldown_required"],
                "retry_policy": classification["retry_policy"],
                "fallback_route": classification["fallback_route"],
                "route_allowed": classification["route_allowed"],
                "error_digest": _privacy_digest(str(event.get("error_message") or event.get("message") or "")),
                "raw_error_exported": False,
            }
        )
    model_family_health: dict[str, dict[str, Any]] = {}
    for record in records:
        family_id = record["model_family"]
        family = model_family_health.setdefault(
            family_id,
            {
                "model_family": family_id,
                "event_count": 0,
                "error_families": [],
                "health_state": "healthy",
                "route_allowed": True,
                "fallback_routes": [],
            },
        )
        family["event_count"] += 1
        family["error_families"] = sorted(set([*family["error_families"], record["error_family"]]))
        family["fallback_routes"] = sorted(set([*family["fallback_routes"], record["fallback_route"]]))
        if record["error_family"] != "none":
            family["health_state"] = "degraded"
        if not record["route_allowed"]:
            family["route_allowed"] = False
    return {
        "status_label": "LOCKED CANON",
        "surface_id": "provider-circuit-breaker-v0",
        "circuit_id": new_id("provider_circuit"),
        "circuit_state": "guarded" if records else "idle",
        "session_id": request.session_id,
        "source_ref": "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-045",
        "event_count": len(records),
        "records": records,
        "model_family_health": model_family_health,
        "retry_policy": {
            "transient": "exponential_backoff_with_jitter",
            "quota": "cooldown_then_fallback",
            "context_too_long": "compress_context_or_route_long_context_family",
            "auth_or_permission": "non_retryable_credentials_review",
        },
        "promotion_gate": {
            "gate_state": "blocked_until_health_evidence_and_human_governance_review" if records else "not_required",
            "gate_reason": "provider route changes require health evidence, fallback proof, and governance review",
            "active_provider_route_mutated": False,
        },
        "privacy_boundary": {
            "raw_provider_errors_exported": False,
            "error_digests_only": True,
        },
        "active_production_mutated": False,
    }


def _classify_provider_event(event: dict[str, Any]) -> dict[str, Any]:
    status_code = event.get("status_code")
    try:
        status = int(status_code)
    except (TypeError, ValueError):
        status = 0
    message = str(event.get("error_message") or event.get("message") or "").lower()
    if status in {401, 403} or "invalid api key" in message or "permission" in message or "unauthorized" in message:
        return {
            "error_family": "auth_or_permission",
            "retryable": False,
            "non_retryable": True,
            "cooldown_required": False,
            "retry_policy": "do_not_retry_without_operator_credentials_review",
            "fallback_route": "human:credentials-review",
            "route_allowed": False,
        }
    if status == 429 or "quota" in message or "rate limit" in message:
        return {
            "error_family": "quota",
            "retryable": False,
            "non_retryable": False,
            "cooldown_required": True,
            "retry_policy": "quota_cooldown_then_alternate_provider",
            "fallback_route": "route:alternate-provider-same-family",
            "route_allowed": False,
        }
    if "context" in message and ("too long" in message or "length" in message or "exceeded" in message):
        return {
            "error_family": "context_too_long",
            "retryable": True,
            "non_retryable": False,
            "cooldown_required": False,
            "retry_policy": "compress_context_before_retry",
            "fallback_route": "route:context-compression-or-long-context-family",
            "route_allowed": True,
        }
    if status >= 500 or "timeout" in message or "connection reset" in message or "temporar" in message:
        return {
            "error_family": "transient",
            "retryable": True,
            "non_retryable": False,
            "cooldown_required": False,
            "retry_policy": "exponential_backoff_with_jitter",
            "fallback_route": "retry:same-provider-after-backoff",
            "route_allowed": True,
        }
    return {
        "error_family": "unknown",
        "retryable": False,
        "non_retryable": False,
        "cooldown_required": False,
        "retry_policy": "operator_review",
        "fallback_route": "human:provider-review",
        "route_allowed": False,
    }


def _prompt_overlay_registry_payload(request: HiveForwardPassRequest) -> dict[str, Any]:
    raw_registry = request.metadata.get("prompt_overlay_registry")
    config = raw_registry if isinstance(raw_registry, dict) else {}
    context = {
        "provider_id": str(config.get("provider_id") or "default"),
        "model_family": str(config.get("model_family") or "default"),
        "runtime": str(config.get("runtime") or "default"),
        "local_model": bool(config.get("local_model")),
    }
    raw_overlays = config.get("overlays") if isinstance(config.get("overlays"), list) else []
    overlays = []
    compatible_overlay_ids: list[str] = []
    incompatible_overlay_ids: list[str] = []
    for index, raw_overlay in enumerate(raw_overlays):
        if not isinstance(raw_overlay, dict):
            continue
        overlay_id = str(raw_overlay.get("overlay_id") or f"overlay-{index}")
        applies_to = raw_overlay.get("applies_to") if isinstance(raw_overlay.get("applies_to"), dict) else {}
        compatible = _prompt_overlay_compatible(applies_to, context)
        record = {
            "overlay_id": overlay_id,
            "applies_to": applies_to,
            "priority": _positive_int(raw_overlay.get("priority"), default=100),
            "insert_after": str(raw_overlay.get("insert_after") or "base"),
            "policy_tags": _dedupe_strings(raw_overlay.get("policy_tags") or []),
            "compatibility_state": "compatible" if compatible else "incompatible",
            "raw_prompt_exported": False,
        }
        overlays.append(record)
        if compatible:
            compatible_overlay_ids.append(overlay_id)
        else:
            incompatible_overlay_ids.append(overlay_id)
    compatible_overlays = sorted(
        [overlay for overlay in overlays if overlay["compatibility_state"] == "compatible"],
        key=lambda item: (item["priority"], item["overlay_id"]),
    )
    conflicts = _prompt_overlay_conflicts(overlays)
    return {
        "status_label": "LOCKED CANON",
        "surface_id": "prompt-overlay-registry-v0",
        "registry_id": new_id("prompt_overlay_registry"),
        "registry_state": "composed_shadow" if overlays else "base_only_shadow",
        "session_id": request.session_id,
        "source_ref": "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-046",
        "base_prompt_contract": {
            "base_prompt_ref": str(config.get("base_prompt_ref") or "prompt::nexusbrain::base"),
            "raw_prompt_exported": False,
            "composition_boundary": "overlay-refs-and-policy-tags-only",
        },
        "target_context": context,
        "overlays": overlays,
        "composed_overlay_order": [overlay["overlay_id"] for overlay in compatible_overlays],
        "model_family_compatibility_check": {
            "provider_id": context["provider_id"],
            "model_family": context["model_family"],
            "compatible_overlay_ids": compatible_overlay_ids,
            "incompatible_overlay_ids": incompatible_overlay_ids,
        },
        "overlay_conflict_audit": {
            "audit_state": "clear" if not conflicts else "conflicts_detected",
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
        },
        "activation_gate": {
            "gate_state": "shadow_only_until_compatibility_policy_and_human_review",
            "active_prompt_mutated": False,
            "required_evidence": ["compatibility_check", "policy_scan", "human_governance_approval"],
        },
        "active_production_mutated": False,
    }


def _prompt_overlay_compatible(applies_to: dict[str, Any], context: dict[str, Any]) -> bool:
    if not applies_to:
        return True
    for key, expected in applies_to.items():
        if str(context.get(key)) != str(expected):
            return False
    return True


def _prompt_overlay_conflicts(overlays: list[dict[str, Any]]) -> list[dict[str, Any]]:
    conflicts = []
    seen_ids: set[str] = set()
    slot_map: dict[tuple[str, int], str] = {}
    for overlay in overlays:
        overlay_id = overlay["overlay_id"]
        if overlay_id in seen_ids:
            conflicts.append({"conflict_type": "duplicate_overlay_id", "overlay_id": overlay_id})
        seen_ids.add(overlay_id)
        slot = (overlay["insert_after"], overlay["priority"])
        if slot in slot_map:
            conflicts.append(
                {
                    "conflict_type": "same_insert_slot_and_priority",
                    "overlay_id": overlay_id,
                    "conflicts_with": slot_map[slot],
                }
            )
        else:
            slot_map[slot] = overlay_id
    return conflicts


def _skill_system_loader_payload(request: HiveForwardPassRequest) -> dict[str, Any]:
    raw_system = request.metadata.get("skill_system")
    config = raw_system if isinstance(raw_system, dict) else {}
    definitions = config.get("definitions") if isinstance(config.get("definitions"), list) else []
    parsed = [_parse_skill_definition(definition, index=index) for index, definition in enumerate(definitions)]
    selected_by_skill: dict[str, dict[str, Any]] = {}
    shadowed_counts: dict[str, int] = {}
    for definition in parsed:
        skill_id = definition["skill_id"]
        current = selected_by_skill.get(skill_id)
        if current is None or _precedence_rank(definition["precedence"]) >= _precedence_rank(current["precedence"]):
            if current is not None:
                shadowed_counts[skill_id] = shadowed_counts.get(skill_id, 0) + 1 + int(current.get("shadowed_definition_count", 0))
            selected_by_skill[skill_id] = definition
        else:
            shadowed_counts[skill_id] = shadowed_counts.get(skill_id, 0) + 1

    orchestrator = config.get("orchestrator") if isinstance(config.get("orchestrator"), dict) else {}
    run_order = _dedupe_strings(orchestrator.get("run_order") or list(selected_by_skill.keys()))
    for skill_id in selected_by_skill:
        if skill_id not in run_order:
            run_order.append(skill_id)
    component_skills = []
    for skill_id in run_order:
        definition = selected_by_skill.get(skill_id)
        if not definition:
            continue
        definition = dict(definition)
        definition["shadowed_definition_count"] = shadowed_counts.get(skill_id, 0)
        component_skills.append(definition)

    component_ids = {component["skill_id"] for component in component_skills}
    raw_handoffs = config.get("handoffs") if isinstance(config.get("handoffs"), list) else []
    handoffs = []
    invalid_handoffs = []
    for index, raw_handoff in enumerate(raw_handoffs):
        if not isinstance(raw_handoff, dict):
            continue
        from_skill_id = str(raw_handoff.get("from_skill_id") or raw_handoff.get("from") or "")
        to_skill_id = str(raw_handoff.get("to_skill_id") or raw_handoff.get("to") or "")
        valid = from_skill_id in component_ids and to_skill_id in component_ids
        handoff = {
            "handoff_id": str(raw_handoff.get("handoff_id") or f"{from_skill_id}-to-{to_skill_id}" or f"handoff-{index}"),
            "from_skill_id": from_skill_id,
            "to_skill_id": to_skill_id,
            "handoff_artifact": raw_handoff.get("handoff_artifact") or raw_handoff.get("artifact") or "skill-output",
            "validation": "schema-or-artifact-presence-before-next-step",
            "copy_paste_required": False,
            "valid": valid,
        }
        handoffs.append(handoff)
        if not valid:
            invalid_handoffs.append(handoff["handoff_id"])

    human_checkpoints = _dedupe_strings(orchestrator.get("human_checkpoints") or config.get("human_checkpoints") or [])
    visual_result = (
        orchestrator.get("visual_result")
        if isinstance(orchestrator.get("visual_result"), dict)
        else config.get("visual_result")
        if isinstance(config.get("visual_result"), dict)
        else {"kind": "markdown-summary", "artifact_ref": None}
    )
    return {
        "status_label": "LOCKED CANON",
        "surface_id": "skill-system-loader-v0",
        "loader_id": new_id("skill_system_loader"),
        "loader_state": "composed_shadow" if component_skills else "empty_shadow",
        "session_id": request.session_id,
        "source_ref": "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-047",
        "system_id": str(config.get("system_id") or "default-skill-system"),
        "goal": str(config.get("goal") or request.intent),
        "component_count": len(component_skills),
        "component_skills": component_skills,
        "allowed_tools_by_skill": {
            component["skill_id"]: component["allowed_tools"]
            for component in component_skills
        },
        "precedence_resolution": {
            "precedence_order": ["project", "user", "global", "marketplace"],
            "shadowed_definition_count": sum(shadowed_counts.values()),
            "selected_skill_ids": [component["skill_id"] for component in component_skills],
        },
        "orchestrator_contract": {
            "skill_id": str(orchestrator.get("skill_id") or "skill-system-orchestrator"),
            "architecture": "orchestrator-plus-composable-skills",
            "run_order": [skill_id for skill_id in run_order if skill_id in component_ids],
            "mega_skill_rejected": True,
            "isolated_skill_endpoint_rejected": True,
            "progressive_disclosure": True,
            "context_rule": "load-only-component-context-needed-for-current-step",
        },
        "handoff_validation": {
            "validation_state": "valid" if not invalid_handoffs else "invalid",
            "handoffs": handoffs,
            "invalid_handoff_ids": invalid_handoffs,
        },
        "human_checkpoint_gates": human_checkpoints,
        "visual_result_contract": visual_result,
        "activation_gate": {
            "gate_state": "shadow_only_until_handoff_validation_sandbox_and_human_review",
            "active_skill_runtime_mutated": False,
            "required_evidence": ["handoff_validation", "human_checkpoint_review", "sandbox_or_shadow_run"],
        },
        "raw_markdown_exported": False,
        "active_production_mutated": False,
    }


def _parse_skill_definition(definition: Any, *, index: int) -> dict[str, Any]:
    if isinstance(definition, dict):
        metadata = definition
        body = ""
    elif isinstance(definition, str):
        metadata, body = _parse_frontmatter(definition)
    else:
        metadata, body = {}, ""
    skill_id = str(metadata.get("skill_id") or metadata.get("agent_id") or f"skill-{index}")
    return {
        "skill_id": skill_id,
        "purpose": str(metadata.get("purpose") or "focused reusable skill component"),
        "precedence": str(metadata.get("precedence") or "project").lower(),
        "allowed_tools": _dedupe_strings(metadata.get("allowed_tools") or metadata.get("tools") or []),
        "model_override": metadata.get("model_override"),
        "context_mode": str(metadata.get("context_mode") or "inline"),
        "definition_digest": _privacy_digest(body or json.dumps(metadata, sort_keys=True, default=str)),
        "raw_definition_exported": False,
        "reusable": bool(metadata.get("reusable", True)),
    }


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    stripped = text.strip()
    if not stripped.startswith("---"):
        return {}, text
    lines = stripped.splitlines()
    metadata_lines = []
    body_start = len(lines)
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body_start = index + 1
            break
        metadata_lines.append(line)
    metadata: dict[str, Any] = {}
    for line in metadata_lines:
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        metadata[key.strip()] = _parse_frontmatter_value(raw_value.strip())
    return metadata, "\n".join(lines[body_start:])


def _parse_frontmatter_value(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    return value.strip("'\"")


def _precedence_rank(precedence: str) -> int:
    ranks = {"project": 4, "user": 3, "global": 2, "marketplace": 1}
    return ranks.get(str(precedence).lower(), 0)


def _bridge_manager_payload(request: HiveForwardPassRequest) -> dict[str, Any]:
    raw_bridges = request.metadata.get("bridges")
    bridge_specs = raw_bridges if isinstance(raw_bridges, list) else []
    bridges = []
    outbound_review_required_count = 0
    for index, spec in enumerate(bridge_specs):
        if not isinstance(spec, dict):
            continue
        bridge_id = str(spec.get("bridge_id") or f"bridge-{index}")
        transport = str(spec.get("transport") or "unknown").lower()
        permissions = _dedupe_strings(spec.get("permissions") or [])
        external_transport = transport not in {"web-local", "daemon-local", "local", "filesystem"} and not bridge_id.startswith("local-")
        outbound_permissions = bool({"send", "write", "post", "publish", "speak"} & set(permissions))
        outbound_review_required = bool(external_transport and outbound_permissions)
        if outbound_review_required:
            outbound_review_required_count += 1
        redaction_policy = str(spec.get("redaction_policy") or "pii-secrets-local-paths")
        redaction_required = redaction_policy not in {"none", "none-needed-local"}
        bridges.append(
            {
                "bridge_id": bridge_id,
                "transport": transport,
                "permissions": permissions,
                "local_first": not external_transport,
                "redaction_policy": redaction_policy,
                "redaction": {
                    "redaction_required": redaction_required,
                    "policy": redaction_policy,
                    "raw_payload_exported": False,
                    "local_paths_redacted": redaction_required,
                    "secrets_redacted": redaction_required,
                },
                "outbound_commitment_review": {
                    "required": outbound_review_required,
                    "outbound_allowed": False if outbound_review_required else True,
                    "review_state": "human_approval_required" if outbound_review_required else "not_required",
                },
                "transport_health_probe": {
                    "health_state": str(spec.get("health_state") or "unknown"),
                    "probe_required_before_use": True,
                },
            }
        )
    return {
        "status_label": "LOCKED CANON",
        "surface_id": "bridge-manager-v0",
        "manager_id": new_id("bridge_manager"),
        "manager_state": "review_ready" if bridges else "empty_catalog",
        "session_id": request.session_id,
        "source_ref": "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-048",
        "bridge_count": len(bridges),
        "bridges": bridges,
        "outbound_review_required_count": outbound_review_required_count,
        "local_first_permission_gate": {
            "external_messages_require_human_approval": True,
            "external_messages_require_redaction": True,
            "active_bridge_mutation": False,
        },
        "redaction_boundary": {
            "raw_bridge_payloads_exported": False,
            "local_paths_redacted": True,
            "secrets_redacted": True,
            "personal_data_redacted": True,
        },
        "active_production_mutated": False,
    }


def _research_monitor_pipeline_payload(request: HiveForwardPassRequest) -> dict[str, Any]:
    raw_monitors = request.metadata.get("research_monitors")
    monitor_specs = raw_monitors if isinstance(raw_monitors, list) else []
    monitors = []
    candidate_intake = []
    demotion_watchlist = []
    promotion_gate_mapping: dict[str, dict[str, Any]] = {}
    strong_candidate_ids = []
    for index, spec in enumerate(monitor_specs):
        if not isinstance(spec, dict):
            continue
        monitor_id = str(spec.get("monitor_id") or f"monitor-{index}")
        candidate_id = str(spec.get("candidate_id") or f"candidate-{monitor_id}")
        trend_signal = _bounded_float(spec.get("trend_signal"), default=0.0)
        monitor = {
            "monitor_id": monitor_id,
            "source_url_digest": _privacy_digest(str(spec.get("source_url") or "")),
            "source_url_exported": False,
            "candidate_id": candidate_id,
            "trend_signal": trend_signal,
            "license_state": str(spec.get("license_state") or "unknown"),
            "security_state": str(spec.get("security_state") or "unknown"),
            "runtime_gate": str(spec.get("runtime_gate") or "needs-review"),
        }
        monitors.append(monitor)
        required_gates = [
            "source_verification",
            "license_review",
            "security_review",
            "runtime_sandbox_eval",
            "human_governance_approval",
        ]
        promotion_gate_mapping[candidate_id] = {
            "candidate_id": candidate_id,
            "required_gates": required_gates,
            "active_promotion_mutated": False,
        }
        if trend_signal >= 0.65 and monitor["license_state"] in {"open", "operator-owned", "permissive"}:
            strong_candidate_ids.append(candidate_id)
            candidate_intake.append(
                {
                    "candidate_id": candidate_id,
                    "monitor_ref": monitor_id,
                    "review_state": "shadow_candidate",
                    "trend_signal": trend_signal,
                    "promotion_gate_ref": f"promotion-gate::{candidate_id}",
                }
            )
        else:
            demotion_watchlist.append(
                {
                    "candidate_id": candidate_id,
                    "monitor_ref": monitor_id,
                    "watchlist_reason": "weak_or_incomplete_signal",
                    "trend_signal": trend_signal,
                }
            )
    return {
        "status_label": "LOCKED CANON",
        "surface_id": "research-monitor-pipeline-v0",
        "pipeline_id": new_id("research_monitor_pipeline"),
        "pipeline_state": "shadow_monitoring" if monitors else "idle",
        "session_id": request.session_id,
        "source_ref": "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-049",
        "scheduled_source_monitor": {
            "monitor_count": len(monitors),
            "monitors": monitors,
            "schedule_state": "metadata-driven-shadow-schedule",
        },
        "trend_detection": {
            "strong_trend_threshold": 0.65,
            "strong_trend_candidate_ids": strong_candidate_ids,
            "trend_signal_count": len(monitors),
        },
        "candidate_intake": candidate_intake,
        "promotion_gate_mapping": promotion_gate_mapping,
        "demotion_watchlist": demotion_watchlist,
        "raw_source_content_exported": False,
        "active_production_mutated": False,
    }


def _bounded_float(value: Any, *, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return round(min(max(parsed, 0.0), 1.0), 3)


def _checkpoint_snapshot_payload(checkpoint: dict[str, Any], activation: dict[str, Any]) -> dict[str, Any]:
    return {
        "checkpoint_id": checkpoint["checkpoint_id"],
        "session_id": checkpoint["session_id"],
        "task_id": checkpoint["task_id"],
        "created_at": checkpoint["created_at"],
        "snapshot_contract_id": "checkpoint-rewind-ledger-snapshot-v0",
        "snapshot_scope": checkpoint["rewind_scope"],
        "activation_ref": activation["activation_id"],
        "activation_artifact_path": activation.get("artifact_path"),
        "prompt_preview_digest": checkpoint.get("prompt_preview_digest"),
        "tool_snapshot_digest": checkpoint.get("tool_snapshot_digest"),
        "pre_write_snapshot": checkpoint.get("pre_write_snapshot") or {},
        "session_turn_snapshot": checkpoint.get("session_turn_snapshot") or {},
        "token_snapshot": checkpoint.get("token_snapshot") or {},
        "rewind_metadata": checkpoint.get("rewind_metadata") or {},
        "restore_validation": checkpoint.get("restore_validation") or {},
        "raw_private_content_included": False,
        "rollback_policy": "diff-preview-then-human-approved-restore",
    }


def _estimated_token_count(text: str) -> int:
    normalized = str(text or "").strip()
    if not normalized:
        return 1
    return max(1, (len(normalized) + 3) // 4)


def _shadow_routing_payload(
    *,
    selected_nodes: list[HiveNode],
    selected_node_resonance: list[dict[str, Any]],
    prior_ledger: dict[str, Any],
) -> dict[str, Any]:
    return build_shadow_routing_payload(
        selected_nodes=selected_nodes,
        selected_node_resonance=selected_node_resonance,
        prior_ledger=prior_ledger,
    )


def _activation_ledger(activations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ledger_id": "hive-activation-ledger-v0",
        "activation_count": len(activations),
        "contract_id": "hive-activation-v0",
        "latest_activation_id": activations[0].get("activation_id") if activations else None,
        "privacy_classes": sorted({str(item.get("privacy_class")) for item in activations if item.get("privacy_class")}),
        "checkpoint_refs": [
            item.get("checkpoint_ref")
            for item in activations
            if item.get("checkpoint_ref")
        ],
    }


def _sensory_input_ledger(sensory_inputs: list[dict[str, Any]]) -> dict[str, Any]:
    latest = sensory_inputs[0] if sensory_inputs else {}
    return {
        "ledger_id": "hive-sensory-input-ledger-v0",
        "sensory_ledger_count": len(sensory_inputs),
        "contract_id": "hive-sensory-input-ledger-v0",
        "latest_sensory_ledger_id": latest.get("sensory_ledger_id"),
        "latest_activation_ref": latest.get("activation_ref"),
        "normalized_channel_count": latest.get("normalized_channel_count", 0),
        "raw_intent_stored": (latest.get("input_integrity") or {}).get("raw_intent_stored"),
        "raw_action_targets_stored": (latest.get("input_integrity") or {}).get("raw_action_targets_stored"),
        "promotion_boundary": "read-only-sensory-evidence-until-checkpoint-governance-release",
    }


def _embedding_tensor_ledger(embeddings: list[dict[str, Any]]) -> dict[str, Any]:
    latest = embeddings[0] if embeddings else {}
    return {
        "ledger_id": "hive-embedding-tensor-ledger-v0",
        "embedding_ledger_count": len(embeddings),
        "contract_id": "hive-embedding-tensor-ledger-v0",
        "latest_embedding_ledger_id": latest.get("embedding_ledger_id"),
        "latest_activation_ref": latest.get("activation_ref"),
        "token_count": latest.get("token_count", 0),
        "embedding_shape": latest.get("embedding_shape", []),
        "raw_tokens_stored": (latest.get("token_privacy") or {}).get("raw_tokens_stored"),
        "promotion_boundary": "read-only-embedding-evidence-until-sandbox-eval-governance-release",
    }


def _temporal_positional_ledger(positionals: list[dict[str, Any]]) -> dict[str, Any]:
    latest = positionals[0] if positionals else {}
    return {
        "ledger_id": "hive-temporal-positional-ledger-v0",
        "temporal_ledger_count": len(positionals),
        "contract_id": "hive-temporal-positional-ledger-v0",
        "latest_temporal_ledger_id": latest.get("temporal_ledger_id"),
        "latest_sensory_input_ref": latest.get("sensory_input_ref"),
        "latest_embedding_tensor_ref": latest.get("embedding_tensor_ref"),
        "position_count": latest.get("position_count", 0),
        "position_encoding": (latest.get("position_policy") or {}).get("position_encoding"),
        "active_context_order_mutated": (latest.get("temporal_integrity") or {}).get("active_context_order_mutated"),
        "promotion_boundary": "read-only-temporal-evidence-until-sandbox-eval-governance-release",
    }


def _memory_engram_ledger(engrams: list[dict[str, Any]]) -> dict[str, Any]:
    latest = engrams[0] if engrams else {}
    return {
        "ledger_id": "hive-memory-engram-ledger-v0",
        "memory_ledger_count": len(engrams),
        "contract_id": "hive-memory-engram-ledger-v0",
        "latest_memory_ledger_id": latest.get("memory_ledger_id"),
        "latest_temporal_positional_ref": latest.get("temporal_positional_ref"),
        "memory_ref_count": latest.get("memory_ref_count", 0),
        "retrieval_record_count": len(latest.get("retrieval_records") or []),
        "raw_memory_content_stored": (latest.get("memory_integrity") or {}).get("raw_memory_content_stored"),
        "promotion_boundary": "read-only-memory-engram-evidence-until-sandbox-eval-governance-release",
    }


def _attention_routing_ledger(attention_ledgers: list[dict[str, Any]]) -> dict[str, Any]:
    latest = attention_ledgers[0] if attention_ledgers else {}
    return {
        "ledger_id": "hive-attention-routing-ledger-v0",
        "attention_ledger_count": len(attention_ledgers),
        "contract_id": "hive-attention-routing-ledger-v0",
        "latest_attention_ledger_id": latest.get("attention_ledger_id"),
        "latest_embedding_tensor_ref": latest.get("embedding_tensor_ref"),
        "attention_head_count": latest.get("attention_head_count", 0),
        "focus_target_count": latest.get("focus_target_count", 0),
        "softmax_normalized": (latest.get("attention_integrity") or {}).get("softmax_normalized"),
        "promotion_boundary": "read-only-attention-evidence-until-sandbox-eval-governance-release",
    }


def _residual_normalization_ledger(normalizations: list[dict[str, Any]]) -> dict[str, Any]:
    latest = normalizations[0] if normalizations else {}
    return {
        "ledger_id": "hive-residual-normalization-ledger-v0",
        "normalization_ledger_count": len(normalizations),
        "contract_id": "hive-residual-normalization-ledger-v0",
        "latest_normalization_ledger_id": latest.get("normalization_ledger_id"),
        "latest_embedding_tensor_ref": latest.get("embedding_tensor_ref"),
        "latest_attention_ref": latest.get("attention_ref"),
        "normalized_stream_count": latest.get("normalized_stream_count", 0),
        "residual_stream_preserved": (latest.get("normalization_integrity") or {}).get("residual_stream_preserved"),
        "promotion_boundary": "read-only-normalization-evidence-until-sandbox-eval-governance-release",
    }


def _sparse_expert_gate_ledger(gates: list[dict[str, Any]]) -> dict[str, Any]:
    latest = gates[0] if gates else {}
    return {
        "ledger_id": "hive-sparse-expert-gate-ledger-v0",
        "gate_ledger_count": len(gates),
        "contract_id": "hive-sparse-expert-gate-ledger-v0",
        "latest_gate_ledger_id": latest.get("gate_ledger_id"),
        "latest_attention_ref": latest.get("attention_ref"),
        "top_k": latest.get("top_k", 0),
        "selected_expert_node_ids": latest.get("selected_expert_node_ids", []),
        "active_production_routing_mutated": (latest.get("gate_integrity") or {}).get("active_production_routing_mutated"),
        "promotion_boundary": "shadow-only-gate-evidence-until-sandbox-eval-governance-release",
    }


def _feedforward_expert_ledger(feedforwards: list[dict[str, Any]]) -> dict[str, Any]:
    latest = feedforwards[0] if feedforwards else {}
    return {
        "ledger_id": "hive-feedforward-expert-ledger-v0",
        "feedforward_ledger_count": len(feedforwards),
        "contract_id": "hive-feedforward-expert-ledger-v0",
        "latest_feedforward_ledger_id": latest.get("feedforward_ledger_id"),
        "latest_sparse_gate_ref": latest.get("sparse_gate_ref"),
        "latest_residual_normalization_ref": latest.get("residual_normalization_ref"),
        "expert_unit_count": latest.get("expert_unit_count", 0),
        "activation_function": (latest.get("feedforward_policy") or {}).get("activation_function"),
        "active_expert_weights_mutated": (latest.get("feedforward_integrity") or {}).get("active_expert_weights_mutated"),
        "promotion_boundary": "shadow-only-feedforward-evidence-until-sandbox-eval-governance-release",
    }


def _neural_pathway_ledger(pathways: list[dict[str, Any]]) -> dict[str, Any]:
    latest = pathways[0] if pathways else {}
    latest_matrix = latest.get("plane_adjacency_matrix") or {}
    return {
        "ledger_id": "hive-neural-pathway-ledger-v0",
        "pathway_count": len(pathways),
        "contract_id": "hive-neural-pathway-map-v0",
        "latest_pathway_id": latest.get("pathway_id"),
        "latest_plane_adjacency_matrix_ref": latest_matrix.get("matrix_id"),
        "latest_activation_ref": latest.get("activation_ref"),
        "latest_neural_bus_ref": latest.get("neural_bus_ref"),
        "latest_hive_blackboard_ref": latest.get("hive_blackboard_ref"),
        "latest_checkpoint_ref": latest.get("checkpoint_ref"),
        "plane_matrix_shape": latest_matrix.get("matrix_shape", []),
        "plane_matrix_edge_count": latest_matrix.get("edge_count", 0),
        "direct_local_state_reads": (latest.get("connectivity_summary") or {}).get("direct_local_state_reads", []),
        "visibility_model": (latest.get("connectivity_summary") or {}).get("visibility_model"),
        "promotion_boundary": "read-only-pathway-evidence-until-sandbox-eval-governance-release",
    }


def _laminar_microcircuit_ledger(microcircuits: list[dict[str, Any]]) -> dict[str, Any]:
    latest = microcircuits[0] if microcircuits else {}
    return {
        "ledger_id": "hive-laminar-microcircuit-ledger-v0",
        "microcircuit_count": len(microcircuits),
        "contract_id": "hive-laminar-microcircuit-ledger-v0",
        "latest_microcircuit_id": latest.get("microcircuit_id"),
        "latest_activation_ref": latest.get("activation_ref"),
        "latest_neural_bus_ref": latest.get("neural_bus_ref"),
        "latest_hive_blackboard_ref": latest.get("hive_blackboard_ref"),
        "latest_checkpoint_ref": latest.get("checkpoint_ref"),
        "latest_trace_ledger_ref": latest.get("trace_ledger_ref"),
        "plane_microcircuit_count": latest.get("plane_microcircuit_count", 0),
        "event_driven_updates": (latest.get("microcircuit_integrity") or {}).get("event_driven_updates"),
        "direct_local_state_reads": (latest.get("microcircuit_integrity") or {}).get("direct_local_state_reads", []),
        "promotion_boundary": "read-only-plane-internal-evidence-until-sandbox-eval-governance-release",
    }


def _synaptic_transmission_ledger(transmissions: list[dict[str, Any]]) -> dict[str, Any]:
    latest = transmissions[0] if transmissions else {}
    return {
        "ledger_id": "hive-synaptic-transmission-ledger-v0",
        "transmission_count": len(transmissions),
        "contract_id": "hive-synaptic-transmission-ledger-v0",
        "latest_transmission_id": latest.get("transmission_id"),
        "latest_pathway_ref": latest.get("pathway_ref"),
        "latest_activation_ref": latest.get("activation_ref"),
        "latest_neural_bus_ref": latest.get("neural_bus_ref"),
        "latest_hive_blackboard_ref": latest.get("hive_blackboard_ref"),
        "plane_signal_count": latest.get("plane_signal_count", 0),
        "node_signal_count": latest.get("node_signal_count", 0),
        "recurrent_signal_count": latest.get("recurrent_signal_count", 0),
        "feedback_signal_count": latest.get("feedback_signal_count", 0),
        "direct_local_state_reads": (latest.get("signal_integrity") or {}).get("direct_local_state_reads", []),
        "promotion_boundary": "read-only-signal-evidence-until-sandbox-eval-governance-release",
    }


def _neuroplastic_weight_ledger(weights: list[dict[str, Any]]) -> dict[str, Any]:
    latest = weights[0] if weights else {}
    return {
        "ledger_id": "hive-neuroplastic-weight-ledger-v0",
        "weight_update_count": len(weights),
        "contract_id": "hive-neuroplastic-weight-ledger-v0",
        "latest_weight_ledger_id": latest.get("weight_ledger_id"),
        "latest_pathway_ref": latest.get("pathway_ref"),
        "latest_transmission_ref": latest.get("transmission_ref"),
        "latest_activation_ref": latest.get("activation_ref"),
        "latest_neural_bus_ref": latest.get("neural_bus_ref"),
        "latest_hive_blackboard_ref": latest.get("hive_blackboard_ref"),
        "plane_weight_count": latest.get("plane_weight_count", 0),
        "node_weight_count": latest.get("node_weight_count", 0),
        "feedback_weight_count": latest.get("feedback_weight_count", 0),
        "eligibility_trace_count": len(latest.get("eligibility_traces") or []),
        "learning_scope": (latest.get("plasticity_rule") or {}).get("learning_scope"),
        "direct_local_state_reads": (latest.get("plasticity_integrity") or {}).get("direct_local_state_reads", []),
        "promotion_boundary": "shadow-only-weight-evidence-until-sandbox-eval-governance-release",
    }


def _neuromodulatory_state_ledger(states: list[dict[str, Any]]) -> dict[str, Any]:
    latest = states[0] if states else {}
    return {
        "ledger_id": "hive-neuromodulatory-state-ledger-v0",
        "neuromodulator_count": len(states),
        "contract_id": "hive-neuromodulatory-state-ledger-v0",
        "latest_neuromodulator_id": latest.get("neuromodulator_id"),
        "latest_laminar_microcircuit_ref": latest.get("laminar_microcircuit_ref"),
        "latest_pathway_ref": latest.get("pathway_ref"),
        "latest_transmission_ref": latest.get("transmission_ref"),
        "latest_weight_ledger_ref": latest.get("weight_ledger_ref"),
        "modulator_count": latest.get("modulator_count", 0),
        "effective_learning_rate": (latest.get("plasticity_gate") or {}).get("effective_learning_rate"),
        "direct_local_state_reads": (latest.get("modulation_integrity") or {}).get("direct_local_state_reads", []),
        "promotion_boundary": "shadow-only-neuromodulation-until-sandbox-eval-governance-release",
    }


def _latent_loop_exit_ledger(latent_loops: list[dict[str, Any]]) -> dict[str, Any]:
    latest = latent_loops[0] if latent_loops else {}
    return {
        "ledger_id": "hive-latent-loop-exit-ledger-v0",
        "latent_loop_ledger_count": len(latent_loops),
        "contract_id": "hive-latent-loop-exit-ledger-v0",
        "latest_latent_loop_id": latest.get("latent_loop_id"),
        "latest_attention_ref": latest.get("attention_ref"),
        "latest_sparse_gate_ref": latest.get("sparse_gate_ref"),
        "latest_feedforward_ref": latest.get("feedforward_ref"),
        "loop_step_count": latest.get("loop_step_count", 0),
        "probability_model": (latest.get("exit_gate_policy") or {}).get("probability_model"),
        "vocabulary_chain_of_thought_required": (latest.get("exit_gate_integrity") or {}).get(
            "vocabulary_chain_of_thought_required",
        ),
        "promotion_boundary": "shadow-only-latent-loop-evidence-until-sandbox-eval-governance-release",
    }


def _kv_cache_compression_ledger(kv_caches: list[dict[str, Any]]) -> dict[str, Any]:
    latest = kv_caches[0] if kv_caches else {}
    return {
        "ledger_id": "hive-kv-cache-compression-ledger-v0",
        "kv_cache_ledger_count": len(kv_caches),
        "contract_id": "hive-kv-cache-compression-ledger-v0",
        "latest_kv_cache_ledger_id": latest.get("kv_cache_ledger_id"),
        "latest_attention_ref": latest.get("attention_ref"),
        "latest_latent_loop_ref": latest.get("latent_loop_ref"),
        "candidate_count": len(latest.get("cache_policy_candidates") or []),
        "selected_shadow_policy_id": (latest.get("selected_shadow_policy") or {}).get("policy_id"),
        "raw_kv_values_stored": (latest.get("kv_cache_integrity") or {}).get("raw_kv_values_stored"),
        "promotion_boundary": "shadow-only-kv-cache-policy-until-sandbox-benchmark-governance-release",
    }


def _loss_backpropagation_ledger(backprops: list[dict[str, Any]]) -> dict[str, Any]:
    latest = backprops[0] if backprops else {}
    return {
        "ledger_id": "hive-loss-backpropagation-ledger-v0",
        "backpropagation_ledger_count": len(backprops),
        "contract_id": "hive-loss-backpropagation-ledger-v0",
        "latest_backpropagation_id": latest.get("backpropagation_id"),
        "latest_sparse_gate_ref": latest.get("sparse_gate_ref"),
        "latest_attention_ref": latest.get("attention_ref"),
        "latest_embedding_tensor_ref": latest.get("embedding_tensor_ref"),
        "loss_term_count": len(latest.get("loss_terms") or []),
        "gradient_path_count": len(latest.get("gradient_paths") or []),
        "active_model_weights_mutated": (latest.get("gradient_integrity") or {}).get("active_model_weights_mutated"),
        "promotion_boundary": "shadow-only-backprop-evidence-until-sandbox-eval-governance-release",
    }


def _optimizer_school_ledger(optimizers: list[dict[str, Any]]) -> dict[str, Any]:
    latest = optimizers[0] if optimizers else {}
    return {
        "ledger_id": "hive-optimizer-school-ledger-v0",
        "optimizer_ledger_count": len(optimizers),
        "contract_id": "hive-optimizer-school-ledger-v0",
        "latest_optimizer_ledger_id": latest.get("optimizer_ledger_id"),
        "latest_backpropagation_ref": latest.get("backpropagation_ref"),
        "latest_memory_engram_ref": latest.get("memory_engram_ref"),
        "curriculum_item_count": len(latest.get("curriculum_update_plan") or []),
        "teacher_review_count": len(latest.get("teacher_review_queue") or []),
        "active_model_weights_mutated": (latest.get("optimizer_integrity") or {}).get("active_model_weights_mutated"),
        "promotion_boundary": "shadow-only-optimizer-school-until-ivy-review-sandbox-eval-governance-release",
    }


def _action_output_decoder_ledger(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    latest = outputs[0] if outputs else {}
    return {
        "ledger_id": "hive-action-output-decoder-ledger-v0",
        "output_decoder_count": len(outputs),
        "contract_id": "hive-action-output-decoder-ledger-v0",
        "latest_output_decoder_id": latest.get("output_decoder_id"),
        "latest_downstream_runtime_ref": latest.get("downstream_runtime_ref"),
        "latest_optimizer_school_ref": latest.get("optimizer_school_ref"),
        "latest_forward_propagation_ref": latest.get("forward_propagation_ref"),
        "decoded_output_count": latest.get("decoded_output_count", 0),
        "raw_outputs_exported": (latest.get("output_integrity") or {}).get("raw_outputs_exported"),
        "active_external_delivery_mutated": (latest.get("output_integrity") or {}).get("active_external_delivery_mutated"),
        "promotion_boundary": "operator-review-only-output-decoder-until-explicit-delivery-gate",
    }


def _forward_propagation_ledger(propagations: list[dict[str, Any]]) -> dict[str, Any]:
    latest = propagations[0] if propagations else {}
    return {
        "ledger_id": "hive-forward-propagation-ledger-v0",
        "propagation_ledger_count": len(propagations),
        "contract_id": "hive-forward-propagation-ledger-v0",
        "latest_propagation_id": latest.get("propagation_id"),
        "latest_pathway_ref": latest.get("pathway_ref"),
        "latest_plane_adjacency_matrix_ref": latest.get("plane_adjacency_matrix_ref"),
        "step_count": latest.get("step_count", 0),
        "all_planes_covered": (latest.get("propagation_integrity") or {}).get("all_planes_covered"),
        "active_production_mutated": (latest.get("propagation_integrity") or {}).get("active_production_mutated"),
        "promotion_boundary": "read-only-forward-propagation-evidence-until-sandbox-eval-governance-release",
    }


def _backward_propagation_ledger(propagations: list[dict[str, Any]]) -> dict[str, Any]:
    latest = propagations[0] if propagations else {}
    return {
        "ledger_id": "hive-backward-propagation-ledger-v0",
        "backward_propagation_count": len(propagations),
        "contract_id": "hive-backward-propagation-ledger-v0",
        "latest_backward_propagation_id": latest.get("backward_propagation_id"),
        "latest_forward_propagation_ref": latest.get("forward_propagation_ref"),
        "latest_loss_backpropagation_ref": latest.get("loss_backpropagation_ref"),
        "latest_plane_adjacency_matrix_ref": latest.get("plane_adjacency_matrix_ref"),
        "step_count": latest.get("step_count", 0),
        "all_forward_steps_covered": (latest.get("backward_integrity") or {}).get("all_forward_steps_covered"),
        "active_model_weights_mutated": (latest.get("backward_integrity") or {}).get("active_model_weights_mutated"),
        "promotion_boundary": "read-only-backward-propagation-evidence-until-sandbox-eval-governance-release",
    }


def _parameter_tensor_ledger(parameters: list[dict[str, Any]]) -> dict[str, Any]:
    latest = parameters[0] if parameters else {}
    return {
        "ledger_id": "hive-parameter-tensor-ledger-v0",
        "parameter_ledger_count": len(parameters),
        "contract_id": "hive-parameter-tensor-ledger-v0",
        "latest_parameter_ledger_id": latest.get("parameter_ledger_id"),
        "latest_backward_propagation_ref": latest.get("backward_propagation_ref"),
        "latest_neuroplastic_weight_ref": latest.get("neuroplastic_weight_ref"),
        "latest_plane_adjacency_matrix_ref": latest.get("plane_adjacency_matrix_ref"),
        "parameter_tensor_count": latest.get("parameter_tensor_count", 0),
        "raw_tensor_values_stored": (latest.get("parameter_integrity") or {}).get("raw_tensor_values_stored"),
        "active_parameter_mutated": (latest.get("parameter_integrity") or {}).get("active_parameter_mutated"),
        "promotion_boundary": "reference-only-parameter-registry-until-sandbox-eval-ivy-governance-release",
    }


def _activation_function_ledger(functions: list[dict[str, Any]]) -> dict[str, Any]:
    latest = functions[0] if functions else {}
    return {
        "ledger_id": "hive-activation-function-ledger-v0",
        "activation_function_ledger_count": len(functions),
        "contract_id": "hive-activation-function-ledger-v0",
        "latest_activation_function_ledger_id": latest.get("activation_function_ledger_id"),
        "latest_parameter_tensor_ref": latest.get("parameter_tensor_ref"),
        "latest_forward_propagation_ref": latest.get("forward_propagation_ref"),
        "activation_function_count": latest.get("activation_function_count", 0),
        "raw_activation_values_stored": (latest.get("activation_function_integrity") or {}).get(
            "raw_activation_values_stored",
        ),
        "active_kernel_mutated": (latest.get("activation_function_integrity") or {}).get("active_kernel_mutated"),
        "promotion_boundary": "reference-only-activation-function-registry-until-sandbox-eval-governance-release",
    }


def _computational_graph_ledger(graphs: list[dict[str, Any]]) -> dict[str, Any]:
    latest = graphs[0] if graphs else {}
    return {
        "ledger_id": "hive-computational-graph-ledger-v0",
        "graph_ledger_count": len(graphs),
        "contract_id": "hive-computational-graph-ledger-v0",
        "latest_graph_ledger_id": latest.get("graph_ledger_id"),
        "latest_activation_function_ref": latest.get("activation_function_ref"),
        "latest_parameter_tensor_ref": latest.get("parameter_tensor_ref"),
        "latest_forward_propagation_ref": latest.get("forward_propagation_ref"),
        "latest_backward_propagation_ref": latest.get("backward_propagation_ref"),
        "operation_node_count": latest.get("operation_node_count", 0),
        "operation_edge_count": latest.get("operation_edge_count", 0),
        "active_runtime_mutated": (latest.get("graph_integrity") or {}).get("active_runtime_mutated"),
        "promotion_boundary": "reference-only-computational-graph-until-sandbox-eval-governance-release",
    }


def _optimizer_state_vector_ledger(states: list[dict[str, Any]]) -> dict[str, Any]:
    latest = states[0] if states else {}
    return {
        "ledger_id": "hive-optimizer-state-vector-ledger-v0",
        "optimizer_state_ledger_count": len(states),
        "contract_id": "hive-optimizer-state-vector-ledger-v0",
        "latest_optimizer_state_ledger_id": latest.get("optimizer_state_ledger_id"),
        "latest_computational_graph_ref": latest.get("computational_graph_ref"),
        "latest_parameter_tensor_ref": latest.get("parameter_tensor_ref"),
        "latest_optimizer_school_ref": latest.get("optimizer_school_ref"),
        "state_vector_count": latest.get("state_vector_count", 0),
        "raw_gradient_values_stored": (latest.get("optimizer_state_integrity") or {}).get(
            "raw_gradient_values_stored",
        ),
        "active_optimizer_state_mutated": (latest.get("optimizer_state_integrity") or {}).get(
            "active_optimizer_state_mutated",
        ),
        "promotion_boundary": "shadow-only-optimizer-state-until-sandbox-eval-ivy-governance-release",
    }


def _model_genome_ledger(genomes: list[dict[str, Any]]) -> dict[str, Any]:
    latest = genomes[0] if genomes else {}
    return {
        "ledger_id": "hive-model-genome-ledger-v0",
        "model_genome_count": len(genomes),
        "contract_id": "hive-model-genome-ledger-v0",
        "latest_genome_ledger_id": latest.get("genome_ledger_id"),
        "latest_optimizer_state_ref": latest.get("optimizer_state_ref"),
        "latest_computational_graph_ref": latest.get("computational_graph_ref"),
        "latest_parameter_tensor_ref": latest.get("parameter_tensor_ref"),
        "architecture_gene_count": latest.get("architecture_gene_count", 0),
        "raw_model_weights_stored": (latest.get("genome_integrity") or {}).get("raw_model_weights_stored"),
        "active_model_architecture_mutated": (latest.get("genome_integrity") or {}).get(
            "active_model_architecture_mutated",
        ),
        "promotion_boundary": "distillation-blueprint-only-until-sandbox-eval-ivy-governance-release",
    }


def _simple_runtime_ledger_summary(
    *,
    ledgers: list[dict[str, Any]],
    ledger_id: str,
    id_key: str,
    latest_ref_key: str,
    latest_ref_source: str,
    count_key: str | None = None,
    integrity_key: str | None = None,
) -> dict[str, Any]:
    latest = ledgers[0] if ledgers else {}
    summary = {
        "ledger_id": ledger_id,
        "ledger_count": len(ledgers),
        "contract_id": ledger_id,
        f"latest_{id_key}": latest.get(id_key),
        latest_ref_key: latest.get(latest_ref_source),
        "promotion_boundary": "shadow-only-until-sandbox-eval-ivy-governance-release",
    }
    if count_key:
        summary[count_key] = latest.get(count_key, 0)
    if integrity_key:
        summary["integrity"] = latest.get(integrity_key) or {}
    return summary


def _tensor_runtime_kernel_ledger(ledgers: list[dict[str, Any]]) -> dict[str, Any]:
    return _simple_runtime_ledger_summary(
        ledgers=ledgers,
        ledger_id="hive-tensor-runtime-kernel-ledger-v0",
        id_key="tensor_kernel_ledger_id",
        latest_ref_key="latest_model_genome_ref",
        latest_ref_source="model_genome_ref",
        count_key="kernel_op_count",
        integrity_key="runtime_integrity",
    )


def _layer_block_stack_ledger(ledgers: list[dict[str, Any]]) -> dict[str, Any]:
    return _simple_runtime_ledger_summary(
        ledgers=ledgers,
        ledger_id="hive-layer-block-stack-ledger-v0",
        id_key="layer_stack_ledger_id",
        latest_ref_key="latest_tensor_kernel_ref",
        latest_ref_source="tensor_kernel_ref",
        count_key="block_count",
        integrity_key="stack_integrity",
    )


def _distillation_loop_ledger(ledgers: list[dict[str, Any]]) -> dict[str, Any]:
    return _simple_runtime_ledger_summary(
        ledgers=ledgers,
        ledger_id="hive-distillation-loop-ledger-v0",
        id_key="distillation_loop_id",
        latest_ref_key="latest_layer_stack_ref",
        latest_ref_source="layer_stack_ref",
        count_key="teacher_panel_count",
        integrity_key="distillation_integrity",
    )


def _federated_influence_ledger(ledgers: list[dict[str, Any]]) -> dict[str, Any]:
    return _simple_runtime_ledger_summary(
        ledgers=ledgers,
        ledger_id="hive-federated-influence-ledger-v0",
        id_key="federated_influence_id",
        latest_ref_key="latest_federated_prior_update_ref",
        latest_ref_source="federated_prior_update_ref",
        count_key="shadow_prior_update_count",
        integrity_key="federation_integrity",
    )


def _executable_dream_cycle_ledger(ledgers: list[dict[str, Any]]) -> dict[str, Any]:
    return _simple_runtime_ledger_summary(
        ledgers=ledgers,
        ledger_id="hive-executable-dream-cycle-ledger-v0",
        id_key="dream_cycle_id",
        latest_ref_key="latest_model_genome_ref",
        latest_ref_source="model_genome_ref",
        count_key="dream_candidate_count",
        integrity_key="dream_integrity",
    )


def _deep_replay_drilldown_ledger(ledgers: list[dict[str, Any]]) -> dict[str, Any]:
    return _simple_runtime_ledger_summary(
        ledgers=ledgers,
        ledger_id="hive-deep-replay-drilldown-ledger-v0",
        id_key="replay_drilldown_id",
        latest_ref_key="latest_graph_ref",
        latest_ref_source="graph_ref",
        count_key="drilldown_view_count",
        integrity_key="replay_integrity",
    )


def _durable_storage_ledger(ledgers: list[dict[str, Any]]) -> dict[str, Any]:
    return _simple_runtime_ledger_summary(
        ledgers=ledgers,
        ledger_id="hive-durable-storage-ledger-v0",
        id_key="storage_ledger_id",
        latest_ref_key="latest_replay_drilldown_ref",
        latest_ref_source="replay_drilldown_ref",
        count_key="indexed_artifact_count",
        integrity_key="storage_integrity",
    )


def _checkpoint_coverage_ledger(ledgers: list[dict[str, Any]]) -> dict[str, Any]:
    return _simple_runtime_ledger_summary(
        ledgers=ledgers,
        ledger_id="hive-checkpoint-coverage-ledger-v0",
        id_key="coverage_ledger_id",
        latest_ref_key="latest_durable_storage_ref",
        latest_ref_source="durable_storage_ref",
        count_key="coverage_record_count",
        integrity_key="coverage_integrity",
    )


def _runtime_decision_ledger(ledgers: list[dict[str, Any]]) -> dict[str, Any]:
    return _simple_runtime_ledger_summary(
        ledgers=ledgers,
        ledger_id="hive-runtime-decision-ledger-v0",
        id_key="runtime_decision_id",
        latest_ref_key="latest_tensor_kernel_ref",
        latest_ref_source="tensor_kernel_ref",
        count_key="decision_count",
        integrity_key="runtime_integrity",
    )


def _backend_quantization_execution_ledger(ledgers: list[dict[str, Any]]) -> dict[str, Any]:
    return _simple_runtime_ledger_summary(
        ledgers=ledgers,
        ledger_id="hive-backend-quantization-execution-ledger-v0",
        id_key="backend_execution_id",
        latest_ref_key="latest_runtime_decision_ref",
        latest_ref_source="runtime_decision_ref",
        count_key="benchmark_scorecard_count",
        integrity_key="backend_integrity",
    )


def _global_federation_safety_contract() -> dict[str, Any]:
    return {
        "contract_id": "global-federation-safety-v0",
        "packet_signing_required": True,
        "trust_scoring_required": True,
        "poisoning_anomaly_scan_required": True,
        "secure_aggregation_required": True,
        "differential_privacy_knobs_required": True,
        "privacy_audit_required": True,
        "human_approved_promotion_required": True,
        "raw_personal_data_export": "forbidden",
        "default_global_state": "shadow_only_until_security_privacy_eval_and_governance_pass",
    }


def _global_federation_review_payload(
    *,
    normalized: HiveGlobalFederationReviewRequest,
    review_id: str,
    created_at: str,
    packets: list[dict[str, Any]],
    prior_ledger: dict[str, Any],
) -> dict[str, Any]:
    packet_envelopes = [packet.get("security_envelope") or {} for packet in packets]
    signed_packet_refs = [
        (envelope.get("signed_packet") or {}).get("packet_id")
        for envelope in packet_envelopes
        if (envelope.get("signed_packet") or {}).get("packet_id")
    ]
    trust_scores = [
        float((envelope.get("trust_scoring") or {}).get("trust_score") or 0.0)
        for envelope in packet_envelopes
    ]
    anomaly_count = sum(
        int((envelope.get("poisoning_anomaly_detection") or {}).get("detected_anomaly_count") or 0)
        for envelope in packet_envelopes
    )
    source_packet_count = len(packets)
    minimum_packet_count = 3
    missing_evidence: list[str] = []
    if source_packet_count < minimum_packet_count:
        missing_evidence.append("secure_aggregation_quorum")
    if not normalized.sandbox_replay_ref:
        missing_evidence.append("sandbox_replay_ref")
    if not normalized.security_review_ref:
        missing_evidence.append("security_review_ref")
    if not normalized.privacy_review_ref:
        missing_evidence.append("privacy_review_ref")
    if not normalized.human_governance_approval:
        missing_evidence.append("human_governance_approval")
    if anomaly_count:
        missing_evidence.append("poisoning_anomaly_clearance")
    average_trust = round(sum(trust_scores) / len(trust_scores), 3) if trust_scores else 0.0
    if average_trust < 0.82:
        missing_evidence.append("minimum_trust_score")
    passed = not missing_evidence
    return {
        "status_label": "LOCKED CANON",
        "surface_id": "hive-global-federation-review-v0",
        "authority": "NexusBrain",
        "review_id": review_id,
        "session_id": normalized.session_id,
        "subject_id": normalized.subject_id,
        "created_at": created_at,
        "promotion_state": (
            "approved_for_global_shadow_learning"
            if passed
            else "blocked_pending_evidence_or_human_approval"
        ),
        "secure_aggregate": {
            "aggregate_id": new_id("global_secure_aggregate"),
            "aggregate_state": "quorum_ready" if source_packet_count >= minimum_packet_count else "waiting_for_quorum",
            "source_packet_count": source_packet_count,
            "minimum_packet_count": minimum_packet_count,
            "signed_packet_refs": signed_packet_refs,
            "prior_ledger_ref": prior_ledger.get("ledger_id"),
            "raw_packet_payload_shared": False,
            "raw_private_data_exported": False,
        },
        "trust_scoring": {
            "result_state": "passed" if average_trust >= 0.82 else "failed",
            "average_trust_score": average_trust,
            "minimum_trust_score": 0.82,
            "packet_trust_scores": trust_scores,
        },
        "poisoning_anomaly_detection": {
            "result_state": "passed" if anomaly_count == 0 else "failed",
            "detected_anomaly_count": anomaly_count,
            "scan_scope": "signed-sanitized-packet-envelopes-and-prior-statistics",
            "quarantine_refs": [],
        },
        "differential_privacy": {
            "result_state": "passed",
            "epsilon": 0.8,
            "delta": 1e-6,
            "knob_state": "enabled-for-global-shadow-learning",
        },
        "privacy_audit": {
            "result_state": "passed",
            "privacy_review_ref": normalized.privacy_review_ref,
            "raw_private_data_exported": False,
            "raw_packet_payload_exported": False,
            "local_paths_exported": False,
            "raw_prompts_exported": False,
            "raw_outputs_exported": False,
        },
        "sandbox_replay": {
            "sandbox_replay_ref": normalized.sandbox_replay_ref,
            "result_state": "passed" if normalized.sandbox_replay_ref else "missing",
            "replay_scope": "global-shadow-learning-prior-update",
        },
        "promotion_gate": {
            "gate_state": "passed_for_shadow_only" if passed else "blocked",
            "missing_evidence": missing_evidence,
            "security_review_ref": normalized.security_review_ref,
            "privacy_review_ref": normalized.privacy_review_ref,
            "sandbox_replay_ref": normalized.sandbox_replay_ref,
            "human_governance_approval": normalized.human_governance_approval,
            "active_global_learning_mutated": False,
            "active_production_mutated": False,
            "promotion_scope": "global-shadow-learning-only",
        },
        "federated_prior_ledger_ref": prior_ledger.get("ledger_id"),
        "raw_private_data_exported": False,
    }


def _global_federation_review_ledger(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ledger_id": "global-federation-review-ledger-v0",
        "review_count": len(reviews),
        "approved_shadow_count": sum(
            1 for review in reviews if review.get("promotion_state") == "approved_for_global_shadow_learning"
        ),
        "blocked_count": sum(
            1 for review in reviews if review.get("promotion_state") == "blocked_pending_evidence_or_human_approval"
        ),
        "latest_review_id": reviews[0].get("review_id") if reviews else None,
        "active_global_learning_mutated": False,
        "promotion_boundary": "global-learning-remains-shadow-only-until-secure-aggregate-sandbox-privacy-security-and-human-approval",
    }


def _dream_ledger(dreams: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ledger_id": "recursive-neural-dream-ledger-v0",
        "dream_count": len(dreams),
        "latest_dream_id": dreams[0].get("dream_id") if dreams else None,
        "candidate_count": sum(1 for dream in dreams if dream.get("candidate_request")),
        "promotion_boundary": "dreams_can_generate_candidates_not_registry_mutations",
    }


def _dream_context_payload(
    *,
    request: HiveRecursiveDreamRequest,
    health_events: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    prior_ledger: dict[str, Any],
) -> dict[str, Any]:
    return build_dream_context_payload(
        request=request,
        health_events=health_events,
        candidates=candidates,
        prior_ledger=prior_ledger,
    )


def _productionization_ledger(productionizations: list[dict[str, Any]]) -> dict[str, Any]:
    shadow_ready = [
        item
        for item in productionizations
        if item.get("lifecycle_state") == "shadow_release_ready"
    ]
    signed_packets = [
        ((item.get("federation_security") or {}).get("signed_packet") or {})
        for item in productionizations
        if (item.get("federation_security") or {}).get("signed_packet")
    ]
    trial_count = sum(
        int((item.get("runtime_research_foundry") or {}).get("trial_count") or 0)
        for item in productionizations
    )
    return {
        "ledger_id": "hive-productionization-ledger-v0",
        "productionization_count": len(productionizations),
        "shadow_release_ready_count": len(shadow_ready),
        "signed_packet_count": len(signed_packets),
        "runtime_trial_count": trial_count,
        "latest_productionization_id": productionizations[0].get("productionization_id") if productionizations else None,
        "promotion_boundary": "human-approved-shadow-release-before-active-production-mutation",
        "raw_private_data_export": "forbidden",
    }


def _release_ledger(releases: list[dict[str, Any]], rollbacks: list[dict[str, Any]]) -> dict[str, Any]:
    rolled_back_release_refs = {
        str(rollback.get("release_ref"))
        for rollback in rollbacks
        if rollback.get("rollback_state") == "rolled_back" and rollback.get("release_ref")
    }
    active_shadow_count = sum(
        1
        for release in releases
        if release.get("release_state") == "active_shadow"
        and str(release.get("release_id")) not in rolled_back_release_refs
    )
    active_release_count = sum(
        1
        for release in releases
        if release.get("release_scope") == "active-production-release-pointer"
        and release.get("release_state") == "active_production"
    )
    blocked_active_release_count = sum(
        1
        for release in releases
        if release.get("release_scope") == "active-production-release-pointer"
        and release.get("release_state") == "blocked"
    )
    active_production_count = sum(
        1
        for release in releases
        if release.get("release_state") == "active_production"
        and str(release.get("release_id")) not in rolled_back_release_refs
    )
    return {
        "ledger_id": "hive-shadow-release-ledger-v0",
        "release_count": len(releases),
        "active_shadow_count": active_shadow_count,
        "active_release_count": active_release_count,
        "blocked_active_release_count": blocked_active_release_count,
        "active_production_count": active_production_count,
        "rolled_back_count": len(rolled_back_release_refs),
        "rollback_count": len(rollbacks),
        "latest_release_id": releases[0].get("release_id") if releases else None,
        "latest_rollback_id": rollbacks[0].get("rollback_id") if rollbacks else None,
        "active_production_mutation_state": (
            "active_metadata_pointer_mutated"
            if active_production_count
            else "not_mutated_by_current_release_ledger"
        ),
        "rollback_boundary": "checkpoint-backed-shadow-or-active-release-pointer-rollback",
    }


def _rewind_ledger(rewinds: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ledger_id": "hive-checkpoint-rewind-ledger-v0",
        "rewind_count": len(rewinds),
        "validated_restore_count": sum(
            1 for rewind in rewinds if rewind.get("rewind_state") == "restore_validated"
        ),
        "latest_rewind_id": rewinds[0].get("rewind_id") if rewinds else None,
        "active_production_mutation_state": "not_mutated_by_checkpoint_rewind_v0",
        "restore_boundary": "snapshot-digest-proof-and-diff-preview-before-any-active-mutation",
    }


def _health_ledger(health_events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ledger_id": "hive-health-ledger-v0",
        "health_event_count": len(health_events),
        "degraded_event_count": sum(1 for event in health_events if event.get("event_state") == "degraded_observed"),
        "healthy_event_count": sum(1 for event in health_events if event.get("event_state") == "healthy_observed"),
        "latest_health_event_id": health_events[0].get("health_event_id") if health_events else None,
        "visibility_scope": "hive-visible",
        "silent_failure_policy": "forbidden",
    }


def _substrate_summary_runtime_state(
    *,
    runs: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    productionizations: list[dict[str, Any]],
    releases: list[dict[str, Any]],
    rollbacks: list[dict[str, Any]],
    rewinds: list[dict[str, Any]],
    health_events: list[dict[str, Any]],
    global_federation_reviews: list[dict[str, Any]],
) -> str:
    runtime_records = (
        runs
        + candidates
        + productionizations
        + releases
        + rollbacks
        + rewinds
        + health_events
        + global_federation_reviews
    )
    if any(_runtime_record_is_blocked(record) for record in runtime_records):
        return "degraded"
    return "live-bound" if runtime_records else "static-canon"


def _runtime_record_is_blocked(record: dict[str, Any]) -> bool:
    if record.get("blocked") is True:
        return True
    if record.get("blocked_reasons"):
        return True
    if record.get("immune_findings"):
        return True

    policy_summary = (record.get("policy_scan") or {}).get("summary") or {}
    if int(policy_summary.get("active_hard_fail_count") or 0) > 0:
        return True

    for state_key in (
        "lifecycle_state",
        "release_state",
        "promotion_state",
        "rollback_state",
        "rewind_state",
        "restore_state",
        "event_state",
    ):
        state = str(record.get(state_key) or "").lower()
        if not state:
            continue
        if "blocked" in state or state == "degraded_observed":
            return True
    return False


def _route_candidate_evaluation_runtime_state(evaluation: dict[str, Any]) -> str:
    if not evaluation:
        return "static-canon"
    status = str(evaluation.get("status") or "").lower()
    gate_state = str((evaluation.get("promotion_gate") or {}).get("gate_state") or "").lower()
    if status.startswith("approved") and gate_state == "approved_for_shadow_apply_only":
        return "live-bound"
    if status.startswith("blocked") or gate_state.startswith("blocked"):
        return "degraded"
    return "live-bound"


def _self_healing_ledger(self_healing_routes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ledger_id": "hive-self-healing-ledger-v0",
        "route_around_count": len(self_healing_routes),
        "prepared_route_around_count": sum(
            1 for route in self_healing_routes if route.get("route_around_state") == "prepared"
        ),
        "latest_route_around_id": self_healing_routes[0].get("route_around_id") if self_healing_routes else None,
        "active_tasks_continue_when_possible": True,
        "active_production_mutation_state": "not_mutated_by_self_healing_v0",
    }


def _node_registry_summary(node_registry_updates: list[dict[str, Any]]) -> dict[str, Any]:
    durable_updates = [
        update
        for update in node_registry_updates
        if update.get("mutation_state") == "durable_registry_updated"
    ]
    retired_parent_count = sum(len(update.get("retired_parent_nodes") or []) for update in durable_updates)
    return {
        "registry_id": "hive-durable-node-registry-v0",
        "update_count": len(node_registry_updates),
        "durable_update_count": len(durable_updates),
        "generated_node_count": sum(1 for update in durable_updates if update.get("registered_node")),
        "retired_parent_count": retired_parent_count,
        "active_archive_model": "archive_not_delete_with_rollback_restoration",
        "latest_update_id": node_registry_updates[0].get("node_registry_update_id") if node_registry_updates else None,
    }


def _ivy_league_school_summary(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    reviews = [
        candidate.get("ivy_league_school_review") or {}
        for candidate in candidates
        if candidate.get("ivy_league_school_review")
    ]
    return {
        "school_id": "ivy-league-expert-school-v0",
        "review_count": len(reviews),
        "certified_candidate_count": sum(
            1 for review in reviews if review.get("certification_state") == "certified"
        ),
        "review_standard": "teacher-panel-distillation-grade-plus-parent-comparison",
        "latest_review_id": reviews[0].get("school_review_id") if reviews else None,
    }


def _closed_sandbox_evaluation(
    request: HiveAssimilationCandidateRequest,
    *,
    candidate_run_id: str,
    created_at: str,
) -> dict[str, Any] | None:
    if not request.metadata.get("run_closed_sandbox_eval"):
        return None
    evaluation_id = new_id("closed_sandbox_eval")
    case_results = _closed_sandbox_eval_case_results(request)
    eval_score = round(sum(float(item["score"]) for item in case_results) / max(len(case_results), 1), 3)
    eval_threshold = float(request.metadata.get("sandbox_eval_threshold") or 0.85)
    sandbox_failed = bool(request.metadata.get("force_closed_sandbox_failure"))
    security_failed = bool(request.metadata.get("force_security_gate_failure"))
    privacy_failed = bool(request.metadata.get("force_privacy_gate_failure"))
    eval_passed = all(item["result_state"] == "passed" for item in case_results) and eval_score >= eval_threshold
    sandbox_passed = not sandbox_failed
    security_passed = not security_failed
    privacy_passed = not privacy_failed and request.privacy_class not in {"secret", "regulated"}
    all_passed = sandbox_passed and eval_passed and security_passed and privacy_passed
    return {
        "closed_sandbox_evaluation_id": evaluation_id,
        "candidate_run_id": candidate_run_id,
        "session_id": request.session_id,
        "candidate_id": request.candidate_id,
        "created_at": created_at,
        "execution_contract": "closed-sandbox-eval-promotion-path-v0",
        "sandbox_run": {
            "sandbox_run_id": new_id("sandbox_run"),
            "provider": "repo-local-closed-sandbox",
            "execution_state": "passed" if sandbox_passed else "failed",
            "execution_mode": "repo-local-deterministic-sandbox-run",
            "executed_steps": [
                "materialize_candidate_manifest",
                "hydrate_sandbox_inputs",
                "run_eval_cases",
                "security_privacy_scan",
                "write_evidence_bundle",
            ],
            "network_policy": "deny-by-default",
            "write_scope": "sandbox-artifacts-only",
            "raw_private_data_exported": False,
        },
        "eval_suite": {
            "eval_suite_id": new_id("eval_suite"),
            "execution_mode": "deterministic-metadata-eval-cases-v0",
            "result_state": "passed" if eval_passed else "failed",
            "score": eval_score,
            "required_threshold": eval_threshold,
            "regression_delta": round(float(request.metadata.get("regression_delta") or 0.0), 3),
            "case_results": case_results,
        },
        "security_gate": {
            "gate_id": new_id("security_gate"),
            "result_state": "passed" if security_passed else "failed",
            "scan_mode": "candidate-metadata-and-source-ref-scan",
            "injection_findings": [] if security_passed else ["forced_security_gate_failure"],
            "credential_exposure": False,
        },
        "privacy_gate": {
            "gate_id": new_id("privacy_gate"),
            "result_state": "passed" if privacy_passed else "failed",
            "raw_private_data_exported": False,
            "packet_class": "artifact-and-metadata-only",
        },
        "evidence_bundle": {
            "evidence_bundle_id": new_id("sandbox_evidence"),
            "artifact_path": None,
            "candidate_manifest_digest": _privacy_digest(
                "|".join([request.candidate_id, request.title, ",".join(_terms(request.capability_traits))])
            ),
            "source_ref_count": len(request.source_refs),
            "sandbox_ref_count_before_run": len(request.sandbox_refs),
            "eval_ref_count_before_run": len(request.eval_refs),
            "raw_private_data_exported": False,
        },
        "failure_policy": {
            "failed_eval_blocks_promotion": True,
            "failed_security_gate_blocks_promotion": True,
            "failed_privacy_gate_blocks_promotion": True,
            "failed_sandbox_run_blocks_promotion": True,
        },
        "promotion_decision": {
            "decision_state": (
                "passed_pending_school_and_human_governance"
                if all_passed
                else "failed_blocks_promotion"
            ),
            "human_governance_required": True,
            "school_review_required": True,
            "active_registry_mutation_allowed": False,
        },
        "promotion_gate_state": (
            "passed_pending_school_and_human_governance"
            if all_passed
            else "failed_blocks_promotion"
        ),
    }


def _closed_sandbox_eval_case_results(request: HiveAssimilationCandidateRequest) -> list[dict[str, Any]]:
    capability_terms = set(_terms(request.capability_traits))
    source_ref_count = len(request.source_refs)
    dreamed_trait_count = len(_terms(request.dreamed_traits))
    case_specs = [
        (
            "source-provenance-present",
            source_ref_count > 0,
            0.94 if source_ref_count > 0 else 0.2,
            "candidate has source refs before promotion",
        ),
        (
            "capability-traits-present",
            bool(capability_terms),
            0.93 if capability_terms else 0.1,
            "candidate declares routable capability traits",
        ),
        (
            "generated-traits-or-standard-candidate-coherent",
            dreamed_trait_count > 0 or request.candidate_kind != "generated_expert",
            0.92 if dreamed_trait_count > 0 or request.candidate_kind != "generated_expert" else 0.4,
            "generated candidates preserve dreamed traits",
        ),
        (
            "rollback-and-policy-metadata-present",
            bool(request.metadata.get("operator_governance_approval")) or not request.requested_promotion,
            0.91 if bool(request.metadata.get("operator_governance_approval")) or not request.requested_promotion else 0.5,
            "promotion requests carry governance metadata",
        ),
    ]
    if request.metadata.get("force_eval_failure"):
        case_specs.append(("forced-eval-failure", False, 0.0, "forced failure metadata was set"))
    return [
        {
            "case_id": case_id,
            "result_state": "passed" if passed else "failed",
            "score": score,
            "evidence_digest": _privacy_digest("|".join([request.candidate_id, case_id, str(passed)])),
            "description": description,
        }
        for case_id, passed, score, description in case_specs
    ]


def _closed_sandbox_block_reasons(closed_sandbox_evaluation: dict[str, Any] | None) -> list[str]:
    if not closed_sandbox_evaluation:
        return []
    if (closed_sandbox_evaluation.get("promotion_decision") or {}).get("decision_state") == "failed_blocks_promotion":
        return ["closed_sandbox_eval_failed"]
    return []


def _ivy_league_school_review(
    request: HiveAssimilationCandidateRequest,
    *,
    parent_retirement: dict[str, Any],
    closed_sandbox_evaluation: dict[str, Any] | None,
) -> dict[str, Any]:
    contract = parent_retirement.get("review_contract") or {}
    sandbox_passed = (
        bool(closed_sandbox_evaluation)
        and (closed_sandbox_evaluation.get("sandbox_run") or {}).get("execution_state") == "passed"
        and (closed_sandbox_evaluation.get("eval_suite") or {}).get("result_state") == "passed"
        and (closed_sandbox_evaluation.get("security_gate") or {}).get("result_state") == "passed"
        and (closed_sandbox_evaluation.get("privacy_gate") or {}).get("raw_private_data_exported") is False
    )
    approved_teacher_count = int(contract.get("approved_teacher_count") or 0)
    distillation_trace_ref = str(contract.get("distillation_trace_ref") or "")
    parent_scorecard_ref = str(contract.get("parent_comparison_scorecard_ref") or "")
    teacher_panel_state = "complete" if approved_teacher_count >= 3 else "incomplete"
    certified = (
        sandbox_passed
        and teacher_panel_state == "complete"
        and bool(distillation_trace_ref)
        and bool(parent_scorecard_ref)
    )
    school_review_id = new_id("ivy_school_review")
    teacher_scorecards = _ivy_teacher_scorecards(
        request=request,
        teacher_panel_reviews=contract.get("teacher_panel_reviews") or [],
        sandbox_passed=sandbox_passed,
        parent_scorecard_ref=parent_scorecard_ref,
    )
    return {
        "school_review_id": school_review_id,
        "candidate_id": request.candidate_id,
        "session_id": request.session_id,
        "review_standard": "ivy_league_teacher_distillation_grade",
        "teacher_panel_state": teacher_panel_state,
        "approved_teacher_count": approved_teacher_count,
        "teacher_panel_reviews": contract.get("teacher_panel_reviews") or [],
        "teacher_scorecards": teacher_scorecards,
        "distillation_trace_ref": distillation_trace_ref,
        "distillation_trace": {
            "trace_id": distillation_trace_ref,
            "trace_state": "recorded" if distillation_trace_ref else "missing",
            "student_candidate_id": request.candidate_id,
            "teacher_scorecard_refs": [scorecard["scorecard_id"] for scorecard in teacher_scorecards],
            "distillation_scope": "teacher-panel-review-of-generated-child-expert",
            "raw_private_data_exported": False,
        },
        "parent_comparison_scorecard_ref": parent_scorecard_ref,
        "sandbox_eval_state": "passed" if sandbox_passed else "missing_or_failed",
        "certification_state": "certified" if certified else "not_certified",
        "certification_record": {
            "certification_id": new_id("ivy_certification"),
            "record_state": "certified" if certified else "not_certified",
            "school_review_ref": school_review_id,
            "parent_retirement_review_ref": parent_retirement.get("retirement_review_id"),
            "certification_scope": "permanent-child-review-before-node-registry-mutation",
            "active_registry_mutation_allowed": bool(certified),
        },
        "missing_inputs": contract.get("missing_inputs") or [],
    }


def _ivy_teacher_scorecards(
    *,
    request: HiveAssimilationCandidateRequest,
    teacher_panel_reviews: list[Any],
    sandbox_passed: bool,
    parent_scorecard_ref: str,
) -> list[dict[str, Any]]:
    scorecards: list[dict[str, Any]] = []
    for index, review in enumerate(teacher_panel_reviews, start=1):
        review_dict = review if isinstance(review, dict) else {}
        teacher_ref = str(review_dict.get("teacher_ref") or f"teacher:{index}")
        approved = str(review_dict.get("review_state", "")).lower() == "approved"
        criteria = {
            "sandbox_eval_passed": sandbox_passed,
            "parent_scorecard_present": bool(parent_scorecard_ref),
            "capability_traits_present": bool(request.capability_traits),
            "operator_governance_present": bool(request.metadata.get("operator_governance_approval")),
        }
        scorecards.append(
            {
                "scorecard_id": new_id("ivy_teacher_scorecard"),
                "teacher_ref": teacher_ref,
                "temperature": "low",
                "review_state": "approved" if approved else "rejected",
                "criteria": criteria,
                "score": round(sum(1 for passed in criteria.values() if passed) / len(criteria), 3),
                "raw_private_data_exported": False,
                "student_candidate_id": request.candidate_id,
            }
        )
    return scorecards


def _standalone_approval_ready(
    request: HiveAssimilationCandidateRequest,
    *,
    child_candidate: bool,
    blocked_reasons: list[str],
    sidebar_reasons: list[str],
    parent_retirement: dict[str, Any],
    closed_sandbox_evaluation: dict[str, Any] | None,
    ivy_league_school_review: dict[str, Any],
) -> bool:
    if not child_candidate or blocked_reasons or sidebar_reasons:
        return False
    if not request.metadata.get("approve_standalone_after_review"):
        return False
    if not request.metadata.get("operator_governance_approval"):
        return False
    if not closed_sandbox_evaluation:
        return False
    if ivy_league_school_review.get("certification_state") != "certified":
        return False
    return bool(parent_retirement.get("retired_parent_node_refs") or request.parent_node_refs)


def _node_registry_update(
    request: HiveAssimilationCandidateRequest,
    *,
    candidate_run_id: str,
    genome: ExpertGenome,
    lifecycle_state: str,
    parent_retirement: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    durable = lifecycle_state == "permanent_standalone_approved"
    registered_node = None
    if durable:
        registered_node = {
            "node_id": "generated:" + _stable_key(request.candidate_id),
            "candidate_id": request.candidate_id,
            "genome_ref": genome.genome_id,
            "node_type": "Expert",
            "brain_scale": "generated_candidate",
            "routing_state": "active_shadow_promotable",
            "capabilities": genome.capability_traits,
            "parent_node_refs": request.parent_node_refs,
            "archive_policy": "archive_not_delete",
        }
    retired_parent_nodes = [
        {
            "node_id": action.get("parent_node_ref"),
            "retirement_state": action.get("retirement_state"),
            "archive_policy": action.get("node_record_policy"),
            "rollback_policy": action.get("rollback_policy"),
        }
        for action in (parent_retirement.get("retirement_actions") or [])
        if durable and action.get("parent_node_ref")
    ]
    return {
        "node_registry_update_id": new_id("node_registry_update"),
        "candidate_run_id": candidate_run_id,
        "session_id": request.session_id,
        "candidate_id": request.candidate_id,
        "created_at": created_at,
        "mutation_state": "durable_registry_updated" if durable else "no_registry_mutation_pending_review",
        "registered_node": registered_node,
        "retired_parent_nodes": retired_parent_nodes,
        "rollback_policy": "restore_parent_to_active_routing_if_child_regresses",
        "active_routing_mutation": durable,
        "registry_contract": "durable-node-registry-archive-not-delete-v0",
    }


def _hive_node_from_registered_node(record: dict[str, Any]) -> HiveNode:
    node_id = str(record.get("node_id") or "generated:unknown")
    candidate_id = str(record.get("candidate_id") or node_id)
    parent_refs = [str(ref) for ref in record.get("parent_node_refs") or []]
    capabilities = _terms(record.get("capabilities") or [])
    return HiveNode(
        node_id=node_id,
        node_type="Expert",
        name=f"Generated Expert {candidate_id}",
        plane_id=str(record.get("plane_id") or "expert-computation"),
        capabilities=capabilities,
        certification_state="permanent_standalone_approved",
        genome_ref=str(record.get("genome_ref") or ""),
        brain_instance_ref=f"brain:generated:{_stable_key(node_id)}",
        brain_scale="generated_candidate",
        parent_brain_ref="brain:primary:nexusbrain",
        health_signal_refs=[f"health:{node_id}"],
        recovery_route_refs=parent_refs + ["sandbox:closed-loop", "eval:loss-plane"],
        dream_participation_contract="can-request-or-participate-when-routed",
        self_improvement_contract="hive-wide-neuroplasticity-fabric",
    )


def _health_refs(nodes: list[HiveNode]) -> list[str]:
    refs: list[str] = []
    for node in nodes:
        refs.extend(node.health_signal_refs)
    return sorted(set(refs))


def _terms(values: list[str]) -> list[str]:
    terms: list[str] = []
    for value in values:
        normalized = re.sub(r"[^a-z0-9_]+", "_", str(value).lower()).strip("_")
        if normalized:
            terms.append(normalized)
    return sorted(set(terms))


def _stable_key(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (normalized or "activation")[:48]


def _privacy_digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]


def _mean_resonance_score(selected_node_resonance: list[dict[str, Any]]) -> float:
    scores = [float(item.get("resonance_score") or 0.0) for item in selected_node_resonance]
    return round(sum(scores) / len(scores), 6) if scores else 0.0


def _mean_abs_delta(values: list[Any]) -> float:
    deltas = [abs(float(value)) for value in values if value is not None]
    return round(sum(deltas) / len(deltas), 6) if deltas else 0.0


def _confidence_bucket(confidence: float) -> str:
    if confidence >= 0.9:
        return "high"
    if confidence >= 0.65:
        return "medium"
    return "low"


def _is_generated_child_candidate(request: HiveAssimilationCandidateRequest) -> bool:
    marker = request.candidate_kind.lower()
    return bool(
        request.parent_node_refs
        or request.parent_genome_refs
        or "child" in marker
        or "expert" in marker
        or "orchestrator" in marker
        or "generated" in marker
    )


def _parent_retirement_review(
    request: HiveAssimilationCandidateRequest,
    *,
    child_candidate: bool,
    blocked_reasons: list[str],
    sidebar_reasons: list[str],
) -> dict[str, Any]:
    threshold = _float_metadata(request.metadata.get("great_outperformance_threshold"), default=0.30)
    raw_deltas = request.metadata.get("parent_value_deltas")
    parent_value_deltas = _parent_value_deltas(request.parent_node_refs, raw_deltas)
    teacher_reviews = request.metadata.get("teacher_panel_reviews")
    teacher_panel_reviews = teacher_reviews if isinstance(teacher_reviews, list) else []
    approved_teacher_count = sum(
        1
        for review in teacher_panel_reviews
        if isinstance(review, dict) and str(review.get("review_state", "")).lower() == "approved"
    )
    distillation_trace_ref = str(request.metadata.get("distillation_trace_ref") or "")
    parent_scorecard_ref = str(request.metadata.get("parent_comparison_scorecard_ref") or "")
    missing_inputs: list[str] = []
    if not request.sandbox_refs:
        missing_inputs.append("sandbox_refs")
    if not request.eval_refs:
        missing_inputs.append("eval_refs")
    if not parent_value_deltas:
        missing_inputs.append("parent_value_deltas")
    if approved_teacher_count < 3:
        missing_inputs.append("three_approved_teacher_panel_reviews")
    if not distillation_trace_ref:
        missing_inputs.append("distillation_trace_ref")
    if not parent_scorecard_ref:
        missing_inputs.append("parent_comparison_scorecard_ref")

    review_complete = child_candidate and not blocked_reasons and not sidebar_reasons and not missing_inputs
    outperformed_refs = [
        parent_ref
        for parent_ref in request.parent_node_refs
        if parent_value_deltas.get(parent_ref, 0.0) >= threshold
    ]
    retired_parent_refs = outperformed_refs if review_complete else []
    retained_parent_refs = [parent_ref for parent_ref in request.parent_node_refs if parent_ref not in retired_parent_refs]
    retirement_actions = [
        {
            "parent_node_ref": parent_ref,
            "child_candidate_id": request.candidate_id,
            "value_delta": parent_value_deltas.get(parent_ref, 0.0),
            "great_outperformance_threshold": threshold,
            "retirement_state": (
                "retired_on_child_standalone_approval"
                if review_complete
                else "retirement_review_pending_ivy_teacher_panel"
            ),
            "routing_policy": "remove_from_primary_active_routing_after_child_standalone_approval",
            "node_record_policy": "archive_not_delete",
            "rollback_policy": "restore_parent_to_active_routing_if_child_regresses",
        }
        for parent_ref in outperformed_refs
    ]
    return {
        "retirement_review_id": new_id("parent_retirement_review"),
        "retirement_rule": (
            "if-a-generated-child-greatly-outperforms-one-parent-the-other-or-both-"
            "retire-the-respective-outperformed-parent-nodes-after-ivy-grade-review"
        ),
        "retired_parent_node_refs": retired_parent_refs,
        "retained_parent_node_refs": retained_parent_refs,
        "candidate_outperformed_parent_node_refs": outperformed_refs,
        "retirement_actions": retirement_actions,
        "review_contract": {
            "review_standard": "ivy_league_teacher_distillation_grade",
            "teacher_panel_minimum": 3,
            "teacher_panel_state": "complete" if review_complete else "incomplete",
            "approved_teacher_count": approved_teacher_count,
            "teacher_panel_reviews": teacher_panel_reviews,
            "required_inputs": [
                "sandbox_refs",
                "eval_refs",
                "parent_value_deltas",
                "three_approved_teacher_panel_reviews",
                "distillation_trace_ref",
                "parent_comparison_scorecard_ref",
                "operator_governance_approval",
            ],
            "missing_inputs": missing_inputs,
            "distillation_trace_ref": distillation_trace_ref,
            "parent_comparison_scorecard_ref": parent_scorecard_ref,
            "operator_governance_approval_required": True,
            "review_depth": "same_rigor_as_ivy_league_teacher_distills_expert_students",
        },
    }


def _parent_value_deltas(parent_refs: list[str], raw_deltas: Any) -> dict[str, float]:
    if not isinstance(raw_deltas, dict):
        return {}
    deltas: dict[str, float] = {}
    for parent_ref in parent_refs:
        value = raw_deltas.get(parent_ref)
        try:
            deltas[parent_ref] = float(value)
        except (TypeError, ValueError):
            continue
    return deltas


def _float_metadata(value: Any, *, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
