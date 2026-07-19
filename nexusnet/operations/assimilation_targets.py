from __future__ import annotations

from copy import deepcopy
import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from nexus.schemas import utcnow
from nexusnet.operations.skill_system_executor import SkillHandler, SkillSystemExecutor


SOURCE_REFS: list[dict[str, str]] = [
    {
        "source_id": "cheetahclaws-python",
        "label": "CheetahClaws Python reimplementation",
        "url": "https://github.com/SafeRL-Lab/cheetahclaws",
        "assimilation_boundary": "Apache Python source and architecture patterns only; raw leaked/decompiled archives stay research-only.",
    },
    {
        "source_id": "mattpocock-skills",
        "label": "Skills for real engineers",
        "url": "https://github.com/mattpocock/skills",
        "assimilation_boundary": "Small reusable agent skills, software fundamentals, and project workflow conventions.",
    },
    {
        "source_id": "openai-symphony",
        "label": "OpenAI Symphony orchestration spec",
        "url": "https://github.com/openai/symphony",
        "assimilation_boundary": "Issue/task orchestrator, workflow contract, isolated workspaces, retry/reconciliation, and DAG-style blocked work.",
    },
    {
        "source_id": "openai-harness-engineering",
        "label": "OpenAI harness engineering",
        "url": "https://openai.com/index/harness-engineering/",
        "assimilation_boundary": "Agent-legible repositories, progressive disclosure, local validation, observability, and guardrails.",
    },
    {
        "source_id": "skill-systems-video-transcript",
        "label": "Skill systems orchestration guidance",
        "url": "https://www.youtube.com/watch?v=FD53kEpLh9c",
        "assimilation_boundary": "Composable skills plus one orchestrator, explicit handoffs, human checkpoints, and visible outputs.",
    },
    {
        "source_id": "mattpocock-sandcastle",
        "label": "Matt Pocock Sandcastle",
        "url": "https://github.com/mattpocock/sandcastle",
        "assimilation_boundary": "Public MIT TypeScript sandbox-agent orchestration patterns only; NexusNet owns its native runtime, policies, and ledgers.",
    },
    {
        "source_id": "sandcastle-sourcepulse",
        "label": "Sandcastle SourcePulse project summary",
        "url": "https://www.sourcepulse.org/projects/27307520",
        "assimilation_boundary": "Secondary public summary for worktree, sandbox, merge-back, templates, and prompt orchestration traits.",
    },
    {
        "source_id": "sandcastle-devcontainer-gist",
        "label": "Sandcastle vs devcontainer comparison",
        "url": "https://gist.github.com/opticom/c0e5e6954874b1991e3c9b0ab7cfefe1",
        "assimilation_boundary": "Comparative AFK loop and headless sandbox operation notes; treat as corroborating implementation guidance.",
    },
]


ASSIMILATION_TARGETS: list[dict[str, Any]] = [
    {
        "target_id": "tool-execution-registry",
        "label": "Tool Execution Registry",
        "state": "live-bound",
        "implementation_state": "runtime-executable",
        "source_ids": ["cheetahclaws-python", "openai-harness-engineering"],
        "implementation_refs": ["nexusnet/tools/assimilation/tool-execution-registry.md"],
        "implementation_source_refs": ["nexus/tools/registry.py"],
        "nexus_surface": "tool_execution_scorecard",
        "endpoint_refs": [
            "/ops/tools",
            "/ops/tools/filesystem.readonly",
            "/ops/tools/filesystem.write",
            "/ops/tools/batch",
            "/ops/brain/canon/tool-execution",
            "/ops/brain/canon/assimilation-targets",
        ],
        "assimilation_goal": "Promote ToolDef-style metadata into NexusNet tool surfaces so every tool exposes safety and scheduling traits.",
        "required_controls": [
            "read_only_metadata",
            "concurrent_safe_metadata",
            "output_truncation_policy",
            "cache_invalidation_after_writes",
            "parallel_safe_batches",
        ],
        "operator_contract": {
            "record_shape": ["tool_id", "read_only", "concurrent_safe", "output_limit", "invalidates_cache"],
            "safety_gate": "writes require sandbox and audit event",
            "control_panel_card": "Tool Execution",
        },
    },
    {
        "target_id": "checkpoint-rewind-ledger",
        "label": "Checkpoint / Rewind Ledger",
        "state": "live-bound",
        "implementation_state": "runtime-executable",
        "source_ids": ["cheetahclaws-python", "openai-harness-engineering"],
        "implementation_refs": ["nexusnet/operations/assimilation/checkpoint-rewind-ledger.md"],
        "implementation_source_refs": ["nexusnet/operations/checkpoint_rewind.py"],
        "nexus_surface": "blackbox_recorder",
        "endpoint_refs": ["/ops/brain/checkpoints", "/ops/brain/checkpoints/{checkpoint_id}/rewind"],
        "assimilation_goal": "Add reversible operator safety with pre-write snapshots, prompt previews, and turn-level rewind metadata.",
        "required_controls": [
            "pre_write_snapshot",
            "session_turn_snapshot",
            "token_snapshot",
            "prompt_preview",
            "rewind_metadata",
        ],
        "operator_contract": {
            "record_shape": ["checkpoint_id", "subject_ref", "snapshot_ref", "created_at", "restore_policy"],
            "safety_gate": "restore remains operator-approved until deterministic restore validation exists",
            "control_panel_card": "Black Box Recorder",
        },
    },
    {
        "target_id": "task-dependency-graph",
        "label": "Task Dependency Graph",
        "state": "live-bound",
        "implementation_state": "runtime-enforced",
        "source_ids": ["openai-symphony", "cheetahclaws-python"],
        "implementation_refs": ["nexusnet/agents/pipelines/assimilation/task-dependency-graph.md"],
        "implementation_source_refs": ["nexusnet/agents/pipelines/service.py"],
        "nexus_surface": "agentic_pipeline_scorecard",
        "endpoint_refs": [
            "/ops/brain/agentic-pipelines",
            "/ops/brain/agentic-pipelines/scheduled-runs",
            "/ops/brain/agentic-pipelines/runs/{run_id}/claim-ready",
            "/ops/brain/agentic-pipelines/runs/{run_id}/blocks/{block_id}/complete",
            "/ops/brain/canon/agentic-pipelines",
        ],
        "assimilation_goal": "Represent blocks, blocked_by edges, reverse-edge maintenance, and parallel-ready unlocked work.",
        "required_controls": [
            "blocks_edges",
            "blocked_by_edges",
            "reverse_edge_refresh",
            "parallel_ready_detection",
            "stale_dependency_audit",
        ],
        "operator_contract": {
            "record_shape": ["task_id", "blocks", "blocked_by", "state", "unlock_reason"],
            "safety_gate": "blocked work cannot dispatch until inbound blockers resolve",
            "control_panel_card": "Agentic Pipelines",
        },
    },
    {
        "target_id": "provider-circuit-error-classifier",
        "label": "Provider Circuit Breaker and Error Classifier",
        "state": "live-bound",
        "implementation_state": "runtime-executable",
        "source_ids": ["cheetahclaws-python", "openai-harness-engineering"],
        "implementation_refs": ["nexusnet/providers/assimilation/provider-circuit-error-classifier.md"],
        "implementation_source_refs": ["nexusnet/providers/model_providers.py"],
        "nexus_surface": "harness_provider_scorecard",
        "endpoint_refs": ["/ops/brain/harness-providers", "/ops/brain/harness-routing"],
        "assimilation_goal": "Classify provider errors and route around quota, context length, transient, and non-retryable failures.",
        "required_controls": [
            "retry_policy",
            "non_retryable_classifier",
            "context_too_long_fallback",
            "quota_cooldown",
            "model_family_health",
        ],
        "operator_contract": {
            "record_shape": ["provider_id", "error_family", "retryable", "cooldown_until", "fallback_route"],
            "safety_gate": "provider route changes require health evidence",
            "control_panel_card": "Harness Providers",
        },
    },
    {
        "target_id": "prompt-overlay-registry",
        "label": "Prompt Overlay Registry",
        "state": "live-bound",
        "implementation_state": "runtime-executable",
        "source_ids": ["cheetahclaws-python", "openai-harness-engineering"],
        "implementation_refs": ["nexusnet/agents/harnesses/assimilation/prompt-overlay-registry.md"],
        "implementation_source_refs": ["nexusnet/agents/harnesses/routing.py"],
        "nexus_surface": "harness_routing_scorecard",
        "endpoint_refs": ["/ops/brain/harness-routing", "/ops/brain/harness-routing/compose-prompt"],
        "assimilation_goal": "Compose a base NexusBrain prompt with provider and model-family overlays without duplicating whole prompts.",
        "required_controls": [
            "base_prompt_contract",
            "provider_overlay",
            "model_family_overlay",
            "local_model_overlay",
            "overlay_conflict_audit",
        ],
        "operator_contract": {
            "record_shape": ["overlay_id", "applies_to", "priority", "insert_after", "policy_tags"],
            "safety_gate": "overlay activation requires model-family compatibility check",
            "control_panel_card": "Harness Routing",
        },
    },
    {
        "target_id": "plan-mode-write-jail",
        "label": "Plan-Mode Write Jail",
        "state": "live-bound",
        "implementation_state": "runtime-enforced",
        "source_ids": ["cheetahclaws-python", "openai-symphony"],
        "implementation_refs": ["nexusnet/policy/assimilation/plan-mode-write-jail.md"],
        "implementation_source_refs": ["nexusnet/policy/kernel.py", "nexus/tools/registry.py", "nexus/api/app.py"],
        "nexus_surface": "policy_kernel_scorecard",
        "endpoint_refs": ["/ops/brain/policy/rules", "/ops/brain/policy/plan-write"],
        "assimilation_goal": "Make plan mode a first-class permission posture: read-only tools and safe shell are allowed, writes are jailed to plan artifacts.",
        "required_controls": [
            "plan_artifact_write_allowlist",
            "repo_write_block",
            "safe_shell_allowlist",
            "tool_read_only_gate",
            "plan_exit_review",
        ],
        "operator_contract": {
            "record_shape": ["mode_id", "allowed_writes", "blocked_writes", "safe_tools", "exit_gate"],
            "safety_gate": "implementation writes require explicit transition out of plan mode",
            "control_panel_card": "Policy Kernel",
        },
    },
    {
        "target_id": "skill-system-orchestrator",
        "label": "Skill Systems Orchestrator",
        "state": "live-bound",
        "implementation_state": "runtime-executable",
        "architecture": "orchestrator-plus-composable-skills",
        "source_ids": ["skill-systems-video-transcript", "mattpocock-skills", "openai-harness-engineering"],
        "implementation_refs": ["nexusnet/operations/assimilation/skill-system-orchestrator.md"],
        "implementation_source_refs": ["nexusnet/operations/skill_system_executor.py", "nexusnet/operations/assimilation_targets.py"],
        "nexus_surface": "assimilation_target_scorecard",
        "endpoint_refs": [
            "/ops/brain/skill-systems/compose",
            "/ops/brain/skill-systems/execute",
            "/ops/brain/skill-systems/runs/{run_id}/resume",
        ],
        "assimilation_goal": "Load markdown skills as small focused components, then wire them through one explicit orchestrator contract for real end-to-end workflows.",
        "required_controls": [
            "component_skill_manifest",
            "orchestrator_contract",
            "explicit_input_contracts",
            "handoff_validation",
            "human_checkpoint_gates",
            "visual_result_contract",
            "mega_skill_rejected",
            "isolated_skill_endpoint_rejected",
        ],
        "operator_contract": {
            "record_shape": ["system_id", "components", "handoff_map", "human_checkpoints", "visual_result"],
            "safety_gate": "skill systems run shadow-first until each handoff has validation evidence",
            "control_panel_card": "Assimilation Target Matrix",
        },
    },
    {
        "target_id": "bridge-manager",
        "label": "Bridge Manager",
        "state": "live-bound",
        "implementation_state": "runtime-executable",
        "source_ids": ["cheetahclaws-python", "openai-symphony"],
        "implementation_refs": ["nexusnet/computer_fabric/assimilation/bridge-manager.md"],
        "implementation_source_refs": ["nexusnet/computer_fabric/bridges.py", "nexusnet/computer_fabric/service.py"],
        "nexus_surface": "communication_integration_scorecard",
        "endpoint_refs": [
            "/ops/brain/bridges",
            "/ops/brain/bridges/commitments",
            "/ops/brain/bridges/commitments/{commitment_id}/approve",
            "/ops/brain/bridges/commitments/{commitment_id}/dispatch",
        ],
        "assimilation_goal": "Catalog Slack, Telegram, WeChat, web, and daemon bridges through local-first permission gates and redaction rules.",
        "required_controls": [
            "bridge_catalog",
            "local_first_permission_gate",
            "redaction_policy",
            "outbound_commitment_review",
            "transport_health_probe",
        ],
        "operator_contract": {
            "record_shape": ["bridge_id", "transport", "permissions", "redaction_policy", "health_state"],
            "safety_gate": "external messages require bridge-specific commitment policy",
            "control_panel_card": "Communication Integration",
        },
    },
    {
        "target_id": "research-monitor-pipeline",
        "label": "Research / Monitor Pipeline",
        "state": "live-bound",
        "implementation_state": "runtime-executable",
        "source_ids": ["openai-symphony", "openai-harness-engineering"],
        "implementation_refs": ["nexusnet/research/assimilation/research-monitor-pipeline.md"],
        "implementation_source_refs": ["nexusnet/research/monitor.py", "nexusnet/research/forward_radar.py"],
        "nexus_surface": "forward_radar_scorecard",
        "endpoint_refs": [
            "/ops/brain/research-monitors",
            "/ops/brain/research-monitors/sources",
            "/ops/brain/research-monitors/sources/{source_id}/poll",
            "/ops/brain/research-monitors/poll-due",
            "/ops/brain/forward-radar",
        ],
        "assimilation_goal": "Turn scheduled source monitoring into forward-radar candidates with trend detection, watchlists, and promotion gates.",
        "required_controls": [
            "scheduled_source_monitor",
            "trend_detection",
            "candidate_intake",
            "promotion_gate_mapping",
            "demotion_watchlist",
        ],
        "operator_contract": {
            "record_shape": ["monitor_id", "source_url", "candidate_id", "trend_signal", "review_state"],
            "safety_gate": "research candidates stay shadow-only until source/license/security/runtime gates pass",
            "control_panel_card": "Forward Radar Registry",
        },
    },
    {
        "target_id": "sandbox-agent-factory",
        "label": "Sandcastle-Style AFK Sandbox Agent Factory",
        "state": "live-bound",
        "implementation_state": "runtime-executable-local-and-container",
        "source_ids": ["mattpocock-sandcastle", "sandcastle-sourcepulse", "sandcastle-devcontainer-gist"],
        "implementation_refs": ["nexusnet/agents/assimilation/sandbox-agent-factory.md"],
        "implementation_source_refs": ["nexusnet/agents/sandbox_factory.py"],
        "nexus_surface": "sandbox_agent_factory_scorecard",
        "endpoint_refs": [
            "/ops/brain/sandbox-agent-factory",
            "/ops/brain/sandbox-agent-factory/runs",
            "/ops/brain/sandbox-agent-factory/runs/{run_id}/execute-local",
            "/ops/brain/sandbox-agent-factory/runs/{run_id}/execute-container",
            "/ops/brain/sandbox-agent-factory/runs/{run_id}/worktrees",
            "/ops/brain/sandbox-agent-factory/runs/{run_id}/merge-gates",
            "/ops/brain/canon/sandbox-agent-factory",
            "/ops/brain/canon/assimilation-targets",
        ],
        "assimilation_goal": "Turn Sandcastle-style AFK agent orchestration into a Nexus-native sandbox factory with worktree isolation, task pickup, review lanes, merge gates, and artifact ledgers.",
        "required_controls": [
            "worktree_per_agent",
            "sandbox_provider_abstraction",
            "backlog_label_filter",
            "planner_implementer_reviewer_merger_flow",
            "merge_back_policy_gate",
            "logs_and_artifacts_per_run",
            "permissioned_afk_execution",
        ],
        "operator_contract": {
            "record_shape": ["run_id", "backlog_ref", "task_ids", "sandbox_provider", "blocks", "required_checks", "policy_scan"],
            "safety_gate": "AFK agents stay in sandbox worktrees and cannot merge back without review, checks, policy scan, and rollback checkpoint",
            "control_panel_card": "Sandbox Agent Factory",
        },
    },
]


VIDEO_SOURCE_REFS: list[dict[str, str]] = [
    {
        "source_id": "video-spec-frontier-small-model-training",
        "label": "Frontier small model training video spec",
        "url": "docs/assimilation/videos/2026-05-06/01-frontier-small-model-training-spec.md",
        "assimilation_boundary": "Edge model lifecycle and certification only.",
    },
    {
        "source_id": "fatihmakes-mark-xxxix",
        "label": "Mark XXXIX repository",
        "url": "https://github.com/FatihMakes/Mark-XXXIX",
        "assimilation_boundary": "Clean-room UX and tool-surface pattern only; CC BY-NC 4.0 blocks code import.",
    },
    {
        "source_id": "space-agent-video-spec",
        "label": "Space Agent self-updating surface spec",
        "url": "docs/assimilation/videos/2026-05-06/03-space-agent-self-updating-surface-spec.md",
        "assimilation_boundary": "Sandboxed generated surface candidates only.",
    },
    {
        "source_id": "agentic-rag-video-spec",
        "label": "Agentic RAG planner spec",
        "url": "docs/assimilation/videos/2026-05-06/04-agentic-rag-planner-spec.md",
        "assimilation_boundary": "Planner and claim ledger only; retrieved snippets are not authority.",
    },
    {
        "source_id": "gitnexus-video-spec",
        "label": "GitNexus codegraph gate spec",
        "url": "docs/assimilation/videos/2026-05-06/05-gitnexus-codegraph-gate-spec.md",
        "assimilation_boundary": "Graph evidence and stale-index blockers only.",
    },
    {
        "source_id": "synthetic-truth-video-spec",
        "label": "Synthetic truth guard spec",
        "url": "docs/assimilation/videos/2026-05-06/06-synthetic-truth-guard-spec.md",
        "assimilation_boundary": "Source-status and abstention governance.",
    },
    {
        "source_id": "black-box-interpretability-video-spec",
        "label": "Black box interpretability plane spec",
        "url": "docs/assimilation/videos/2026-05-06/07-black-box-interpretability-plane-spec.md",
        "assimilation_boundary": "Behavioral concept telemetry and open-model research records.",
    },
    {
        "source_id": "sakana-dgm",
        "label": "Sakana Darwin Godel Machine",
        "url": "https://sakana.ai/dgm/",
        "assimilation_boundary": "Shadow-only lineage and eval gates; no production self-rewrite.",
    },
    {
        "source_id": "deepmind-alphaevolve",
        "label": "Google DeepMind AlphaEvolve",
        "url": "https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/",
        "assimilation_boundary": "Verifier-first candidate search where objective scoring exists.",
    },
    {
        "source_id": "bytedance-ui-tars",
        "label": "ByteDance UI-TARS Desktop",
        "url": "https://github.com/bytedance/UI-TARS-desktop",
        "assimilation_boundary": "Operator event stream and permission split; no unscoped desktop authority.",
    },
    {
        "source_id": "karpathy-nanochat",
        "label": "Karpathy nanochat",
        "url": "https://github.com/karpathy/nanochat",
        "assimilation_boundary": "Reference patterns for explicit device precision, memory-bounded scale-down, and reproducible constrained-hardware experiments only; no runtime dependency or model-weight import.",
    },
    {
        "source_id": "justvugg-colibri",
        "label": "JustVugg Colibrì",
        "url": "https://github.com/JustVugg/colibri",
        "assimilation_boundary": "Independent architecture-intake, tier-planning, cache-telemetry, and evidence patterns only; no Colibrì source import, dependency, CLI, server, subprocess, or model-weight handling.",
    },
]


VIDEO_ASSIMILATION_TARGETS: list[dict[str, Any]] = [
    {
        "target_id": "frontier-small-model-training",
        "label": "Frontier Small Model Training",
        "source_ids": ["video-spec-frontier-small-model-training"],
        "implementation_refs": ["nexusnet/runtime/assimilation/frontier-small-model-training.md"],
        "implementation_source_refs": ["nexusnet/runtime/model_passport.py"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/01-frontier-small-model-training-spec.md",
        "source_status": "secondary_verified",
        "promotion_state": "shadow_certification",
        "clean_room_required": False,
        "license_boundary": "source references only",
        "nexus_surfaces": ["model_passport", "eval_registry", "quantization_catalog"],
        "required_controls": ["model_passport", "device_matrix", "certified_task_labels", "blocked_task_labels"],
    },
    {
        "target_id": "jarvis-operator-shell",
        "label": "Jarvis Mark XXXIX Operator Shell",
        "source_ids": ["fatihmakes-mark-xxxix"],
        "implementation_refs": ["nexusnet/browser/assimilation/jarvis-operator-shell.md"],
        "implementation_source_refs": ["nexusnet/browser/profile_policy.py"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/02-jarvis-operator-shell-spec.md",
        "source_status": "primary_verified",
        "promotion_state": "governed_runtime",
        "clean_room_required": True,
        "license_boundary": "CC BY-NC 4.0 personal and non-commercial only",
        "nexus_surfaces": ["browser_profile_policy", "operator_events", "control_panel"],
        "required_controls": ["permission_envelope", "action_receipts", "profile_policy", "memory_consent"],
    },
    {
        "target_id": "space-self-updating-surface",
        "label": "Space Agent Self-Updating Surface",
        "source_ids": ["space-agent-video-spec"],
        "implementation_refs": ["nexusnet/core/assimilation/space-self-updating-surface.md"],
        "implementation_source_refs": ["nexusnet/core/autonomous_updates.py"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/03-space-agent-self-updating-surface-spec.md",
        "source_status": "secondary_verified",
        "promotion_state": "shadow_only",
        "clean_room_required": True,
        "license_boundary": "source references only",
        "nexus_surfaces": ["self_improvement_lineage", "sandbox_factory"],
        "required_controls": ["generated_artifact_schema", "sandbox_default", "rollback_plan", "review_queue"],
    },
    {
        "target_id": "agentic-rag-planner",
        "label": "Agentic RAG Planner",
        "source_ids": ["agentic-rag-video-spec"],
        "implementation_refs": ["nexusnet/retrieval/assimilation/agentic-rag-planner.md"],
        "implementation_source_refs": ["nexusnet/retrieval/planner.py"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/04-agentic-rag-planner-spec.md",
        "source_status": "secondary_verified",
        "promotion_state": "governed_runtime",
        "clean_room_required": False,
        "license_boundary": "source references only",
        "nexus_surfaces": ["retrieval_planner", "memory_quality_ledger"],
        "required_controls": ["retrieval_plan_schema", "claim_ledger", "critic_loop", "poisoning_controls"],
    },
    {
        "target_id": "gitnexus-codegraph-gate",
        "label": "GitNexus Codegraph Gate",
        "source_ids": ["gitnexus-video-spec"],
        "implementation_refs": ["nexusnet/operations/assimilation/gitnexus-codegraph-gate.md"],
        "implementation_source_refs": ["nexusnet/operations/codegraph_gate.py"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/05-gitnexus-codegraph-gate-spec.md",
        "source_status": "primary_verified",
        "promotion_state": "required_gate",
        "clean_room_required": False,
        "license_boundary": "tool evidence only",
        "nexus_surfaces": ["codegraph_gate", "agentic_pipelines"],
        "required_controls": ["impact_evidence", "stale_index_block", "detect_changes_evidence"],
    },
    {
        "target_id": "synthetic-truth-guard",
        "label": "Synthetic Truth Guard",
        "source_ids": ["synthetic-truth-video-spec"],
        "implementation_refs": ["nexusnet/memory/assimilation/synthetic-truth-guard.md"],
        "implementation_source_refs": ["nexusnet/memory/quality_ledger.py"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/06-synthetic-truth-guard-spec.md",
        "source_status": "secondary_verified",
        "promotion_state": "critical_governance",
        "clean_room_required": False,
        "license_boundary": "source references only",
        "nexus_surfaces": ["memory_quality_ledger", "knowledge_artifacts", "policy_kernel"],
        "required_controls": ["source_status_enum", "abstention_reward", "contradiction_workflow", "canon_gate"],
    },
    {
        "target_id": "black-box-interpretability-plane",
        "label": "Black Box Interpretability Plane",
        "source_ids": ["black-box-interpretability-video-spec"],
        "implementation_refs": ["nexusnet/telemetry/assimilation/black-box-interpretability-plane.md"],
        "implementation_source_refs": ["nexusnet/telemetry/concept_plane.py"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/07-black-box-interpretability-plane-spec.md",
        "source_status": "secondary_verified",
        "promotion_state": "governed_research_runtime",
        "clean_room_required": False,
        "license_boundary": "open-model research records only",
        "nexus_surfaces": ["concept_telemetry", "engram_index"],
        "required_controls": ["behavioral_proxy_label", "sae_experiment_record", "closed_model_boundary"],
    },
    {
        "target_id": "darwin-godel-machine-lineage",
        "label": "Darwin Godel Machine Lineage",
        "source_ids": ["sakana-dgm"],
        "implementation_refs": ["nexusnet/evolution/assimilation/darwin-godel-machine-lineage.md"],
        "implementation_source_refs": ["nexusnet/evolution/service.py"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/08-darwin-godel-machine-lineage-spec.md",
        "source_status": "primary_verified",
        "promotion_state": "shadow_only",
        "clean_room_required": True,
        "license_boundary": "source references and paper/code review only",
        "nexus_surfaces": ["self_improvement_lineage", "eval_registry"],
        "required_controls": ["lineage_artifact", "anti_cheat_receipts", "transfer_tests", "reward_hacking_probe"],
    },
    {
        "target_id": "alphaevolve-verifier-search",
        "label": "AlphaEvolve Verifier Search",
        "source_ids": ["deepmind-alphaevolve"],
        "implementation_refs": ["nexusnet/evals/assimilation/alphaevolve-verifier-search.md"],
        "implementation_source_refs": ["nexusnet/evals/verifier_search.py"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/09-alphaevolve-verifier-search-spec.md",
        "source_status": "primary_verified",
        "promotion_state": "shadow_optimizer",
        "clean_room_required": True,
        "license_boundary": "clean-room evaluator pattern only",
        "nexus_surfaces": ["verifier_search", "eval_registry"],
        "required_controls": ["objective_scorer", "candidate_database", "multi_objective_score", "human_review"],
    },
    {
        "target_id": "tars-computer-use-operator",
        "label": "TARS Computer-Use Operator",
        "source_ids": ["bytedance-ui-tars"],
        "implementation_refs": ["nexusnet/vision/assimilation/tars-computer-use-operator.md"],
        "implementation_source_refs": ["nexusnet/vision/computer_use.py"],
        "spec_ref": "docs/assimilation/videos/2026-05-06/10-tars-computer-use-operator-spec.md",
        "source_status": "primary_verified",
        "promotion_state": "governed_operator_runtime",
        "clean_room_required": True,
        "license_boundary": "source references only; no unscoped authority",
        "nexus_surfaces": ["operator_events", "multimodal_computer_use", "protocol_trust"],
        "required_controls": ["operator_split", "event_stream", "mcp_mount_registry", "stop_control"],
    },
    {
        "target_id": "nanochat-constrained-hardware-reference",
        "label": "nanochat Constrained-Hardware Reference",
        "source_ids": ["karpathy-nanochat"],
        "implementation_refs": ["nexusnet/runtime/evolutionary_inference/assimilation/nanochat-constrained-hardware-reference.md"],
        "implementation_source_refs": [
            "nexusnet/runtime/evolutionary_inference/hardware.py",
            "nexusnet/runtime/evolutionary_inference/synthesis.py",
            "nexusnet/runtime/evolutionary_inference/dream_lab.py",
        ],
        "spec_ref": "docs/assimilation/videos/2026-07-14/11-nanochat-constrained-hardware-reference-spec.md",
        "source_status": "primary_verified",
        "promotion_state": "shadow_certification",
        "clean_room_required": False,
        "license_boundary": "MIT source used as a reference for independently implemented hardware-adaptation patterns; no nanochat runtime dependency or model-weight import.",
        "nexus_surfaces": ["hardware_profile", "inference_evolution", "dream_lab"],
        "required_controls": [
            "device_aware_precision",
            "memory_budget_envelope",
            "reproducible_experiment_contract",
            "quality_and_throughput_evidence",
            "approval_gated_promotion",
        ],
    },
    {
        "target_id": "colibri-moe-architecture-intake",
        "label": "Colibrì MoE Architecture Intake",
        "source_ids": ["justvugg-colibri"],
        "implementation_refs": ["nexusnet/runtime/moe_residency/assimilation/colibri-moe-architecture-intake.md"],
        "implementation_source_refs": [
            "nexusnet/runtime/moe_residency/architecture.py",
            "nexusnet/runtime/evolutionary_inference/system.py",
        ],
        "spec_ref": "docs/third-party/COLIBRI_ASSIMILATION_NOTICE.md",
        "source_status": "primary_verified",
        "promotion_state": "shadow_certification",
        "clean_room_required": True,
        "license_boundary": "Apache-2.0 source used for independently implemented behavioral assimilation only; no Colibrì dependency, source import, provider, CLI, server, subprocess, or model-weight handling.",
        "nexus_surfaces": ["moe_residency", "inference_evolution"],
        "required_controls": [
            "explicit_architecture_descriptor",
            "header_only_tier_plan",
            "cpu_or_gpu_dense_placement",
            "bounded_expert_cache",
            "sanitized_live_residency_telemetry",
            "equivalence_gated_evolution_evidence",
        ],
    },
]


_RUNTIME_BINDINGS: dict[str, dict[str, str]] = {
    "tool-execution-registry": {"operational_endpoint": "/ops/brain/canon/tool-execution"},
    "checkpoint-rewind-ledger": {"operational_endpoint": "/ops/brain/checkpoints"},
    "task-dependency-graph": {"operational_endpoint": "/ops/brain/agentic-pipelines"},
    "provider-circuit-error-classifier": {"operational_endpoint": "/ops/brain/harness-providers"},
    "prompt-overlay-registry": {"operational_endpoint": "/ops/brain/harness-routing"},
    "plan-mode-write-jail": {"operational_endpoint": "/ops/brain/policy/rules"},
    "skill-system-orchestrator": {"operational_endpoint": "/ops/brain/canon/assimilation-targets"},
    "bridge-manager": {"operational_endpoint": "/ops/brain/bridges"},
    "research-monitor-pipeline": {"operational_endpoint": "/ops/brain/research-monitors"},
    "sandbox-agent-factory": {"operational_endpoint": "/ops/brain/sandbox-agent-factory"},
    "frontier-small-model-training": {"operational_endpoint": "/ops/brain/model-passports"},
    "jarvis-operator-shell": {"operational_endpoint": "/ops/brain/browser/profile-policy"},
    "space-self-updating-surface": {"operational_endpoint": "/ops/brain/autonomous-updates"},
    "agentic-rag-planner": {"operational_endpoint": "/ops/brain/retrieval/planner"},
    "gitnexus-codegraph-gate": {"operational_endpoint": "/ops/brain/codegraph-gate"},
    "synthetic-truth-guard": {"operational_endpoint": "/ops/brain/memory-quality"},
    "black-box-interpretability-plane": {"operational_endpoint": "/ops/brain/concept-telemetry"},
    "darwin-godel-machine-lineage": {"operational_endpoint": "/ops/brain/verifier-search"},
    "alphaevolve-verifier-search": {"operational_endpoint": "/ops/brain/verifier-search"},
    "tars-computer-use-operator": {"operational_endpoint": "/ops/brain/operator-events"},
    "nanochat-constrained-hardware-reference": {"operational_endpoint": "/ops/brain/inference-evolution"},
    "colibri-moe-architecture-intake": {"operational_endpoint": "/ops/brain/inference-evolution"},
}

_CANON_LEDGER_DATE = "2026-07-14"
_CANON_LEDGER_FIELDS = frozenset(
    {
        "entry_id",
        "date_added",
        "status",
        "source_refs",
        "original_book_status",
        "delta_type",
        "affected_lanes",
        "canon_effect",
        "implementation_refs",
        "validation_refs",
        "security_or_policy_gates",
        "rollback_or_sidebar_rule",
    }
)
_CANON_LEDGER_ALLOWED_STATUSES = {
    "locked_clarification",
    "candidate",
    "code_backed_candidate",
    "live_control_plane",
    "research_only",
    "rejected",
    "side_barred",
    "blocked",
    "superseded",
}
_CANON_LEDGER_TARGET_INPUTS = {
    "target_id",
    "source_ids",
    "implementation_refs",
    "required_controls",
}


def _runtime_binding(target_id: str) -> dict[str, str]:
    binding = _RUNTIME_BINDINGS.get(target_id)
    if binding is None:
        raise ValueError(f"missing runtime binding for assimilation target: {target_id}")
    endpoint = binding["operational_endpoint"]
    return {
        "operational_endpoint": endpoint,
        "evidence_endpoint": endpoint,
        "policy_endpoint": "/ops/brain/policy/rules",
        "verification_test": "tests/test_registered_assimilation_runtime_integration.py",
    }


def _canon_ledger_entry(target: dict[str, Any]) -> dict[str, Any]:
    missing_inputs = sorted(field for field in _CANON_LEDGER_TARGET_INPUTS if not target.get(field))
    if not target.get("nexus_surfaces") and not target.get("nexus_surface"):
        missing_inputs.append("nexus_surface_or_nexus_surfaces")
    if missing_inputs:
        raise ValueError(f"missing Canon ledger inputs: {', '.join(missing_inputs)}")
    binding = _runtime_binding(target["target_id"])
    lanes = list(target.get("nexus_surfaces") or [target["nexus_surface"]])
    ledger = {
        "entry_id": f"ASML-{target['target_id']}",
        "date_added": _CANON_LEDGER_DATE,
        "status": "live_control_plane",
        "source_refs": list(target["source_ids"]),
        "original_book_status": "not_accepted_as_this_named_target_in_2026-04-28_source_book",
        "delta_type": "clean_room_assimilation" if target.get("clean_room_required") else "governed_assimilation",
        "affected_lanes": lanes,
        "canon_effect": (
            "Registers a source-backed governed control-plane capability; "
            "it grants neither automatic production mutation nor automatic promotion."
        ),
        "implementation_refs": list(target["implementation_refs"]),
        "validation_refs": [
            binding["verification_test"],
            f"GET {binding['operational_endpoint']}",
        ],
        "security_or_policy_gates": [
            *target["required_controls"],
            f"policy_endpoint:{binding['policy_endpoint']}",
        ],
        "rollback_or_sidebar_rule": (
            "Automatic promotion is prohibited; retain the target in its governed or shadow "
            "promotion state and side-bar the capability when policy, security, regression, "
            "or validation evidence fails."
        ),
    }
    if set(ledger) != _CANON_LEDGER_FIELDS:
        raise ValueError(f"incomplete Canon ledger entry for assimilation target: {target['target_id']}")
    if ledger["status"] not in _CANON_LEDGER_ALLOWED_STATUSES:
        raise ValueError(f"invalid Canon ledger status for assimilation target: {target['target_id']}")
    if not all(ledger[field] for field in _CANON_LEDGER_FIELDS):
        raise ValueError(f"empty Canon ledger field for assimilation target: {target['target_id']}")
    return ledger


def _target_with_runtime_binding(target: dict[str, Any]) -> dict[str, Any]:
    bound = deepcopy(target)
    bound["runtime_binding"] = _runtime_binding(bound["target_id"])
    bound["canon_ledger"] = _canon_ledger_entry(bound)
    return bound


class SkillComponentSpec(BaseModel):
    skill_id: str
    purpose: str
    required_input: str | dict[str, Any] = "operator_input"
    output: str | dict[str, Any] = "skill_output"
    tools: list[str] = Field(default_factory=list)
    reusable: bool = True
    context_refs: list[str] = Field(default_factory=list)


class SkillCheckpointSpec(BaseModel):
    checkpoint_id: str
    after_skill_id: str
    approval_policy: str = "human-review"
    required: bool = True


class SkillSystemRequest(BaseModel):
    system_id: str
    goal: str
    trigger: dict[str, Any] = Field(default_factory=dict)
    components: list[SkillComponentSpec]
    human_checkpoints: list[SkillCheckpointSpec] = Field(default_factory=list)
    visual_result: dict[str, Any] = Field(default_factory=dict)
    schedule: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssimilationTargetRegistry:
    """Source-backed NexusNet control contracts for Claude-code-style harness targets."""

    def __init__(self, artifacts_dir: str | Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir else None
        self._latest_skill_system: dict[str, Any] | None = None
        self._skill_executor = SkillSystemExecutor(
            handlers={"context-passthrough": _context_passthrough_skill}
        )

    def register_skill_handler(self, skill_id: str, handler: SkillHandler) -> None:
        """Attach a local executable implementation to a declared reusable skill."""
        self._skill_executor.register(skill_id, handler)

    def execute_skill_system(
        self,
        payload: dict[str, Any] | SkillSystemRequest,
        *,
        initial_context: dict[str, Any],
    ) -> dict[str, Any]:
        request = payload if isinstance(payload, SkillSystemRequest) else SkillSystemRequest.model_validate(payload)
        return self._skill_executor.execute(
            system_id=request.system_id,
            components=request.components,
            initial_context=initial_context,
            human_checkpoints=request.human_checkpoints,
        )

    def resume_skill_system(
        self,
        run_id: str,
        *,
        approved_checkpoint_ids: list[str],
    ) -> dict[str, Any]:
        return self._skill_executor.resume(
            run_id,
            approved_checkpoint_ids=approved_checkpoint_ids,
        )

    def summary(self, session_id: str | None = None) -> dict[str, Any]:
        return self.scorecard(session_id=session_id)

    def target(self, target_id: str) -> dict[str, Any] | None:
        for target in ASSIMILATION_TARGETS:
            if target["target_id"] == target_id:
                return {
                    "status_label": "LOCKED CANON",
                    "target": _target_with_runtime_binding(target),
                    "source_refs": self._source_refs_for(target),
                    "control_plane_ref": "/ops/brain/canon/assimilation-targets",
                }
        return None

    def scorecard(self, session_id: str | None = None) -> dict[str, Any]:
        targets = [_target_with_runtime_binding(target) for target in ASSIMILATION_TARGETS]
        target_ids = [target["target_id"] for target in targets]
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "claude-code-assimilation-targets",
            "session_id": session_id,
            "runtime_state": "live-bound",
            "implementation_state": "control-plane-contracts-bound",
            "target_count": len(targets),
            "targets": targets,
            "coverage_summary": {
                "target_count": len(targets),
                "covered_target_ids": target_ids,
                "live_bound_count": sum(1 for target in targets if target.get("state") == "live-bound"),
                "skill_system_model": "orchestrator-plus-composable-skills",
                "clean_room_boundary": "Use public/open source implementations and source-backed patterns; do not depend on leaked or private code.",
            },
            "source_refs": deepcopy(SOURCE_REFS),
            "skill_system_rule": {
                "component_rule": "small-focused-reusable-skills",
                "orchestrator_rule": "one system orchestrator wires skills, handoffs, checkpoints, and visual outputs",
                "context_rule": "load exact step context only; keep bulky research in artifacts",
                "rejected_patterns": ["isolated_skill_endpoint", "mega_skill", "manual_copy_paste_handoff"],
            },
            "operator_actions": {
                "list_targets": {"method": "GET", "endpoint": "/ops/brain/assimilation-targets"},
                "target_detail": {"method": "GET", "endpoint": "/ops/brain/assimilation-targets/{target_id}"},
                "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/assimilation-targets"},
                "compose_skill_system": {"method": "POST", "endpoint": "/ops/brain/skill-systems/compose"},
                "execute_skill_system": {"method": "POST", "endpoint": "/ops/brain/skill-systems/execute"},
                "resume_skill_system": {
                    "method": "POST",
                    "endpoint": "/ops/brain/skill-systems/runs/{run_id}/resume",
                },
            },
            "latest_skill_system": deepcopy(self._latest_skill_system),
        }

    def video_scorecard(self, session_id: str | None = None) -> dict[str, Any]:
        targets = [_target_with_runtime_binding(target) for target in VIDEO_ASSIMILATION_TARGETS]
        return {
            "status_label": "LOCKED CANON",
            "surface_id": "video-assimilation-targets",
            "session_id": session_id,
            "runtime_state": "live-bound",
            "target_count": len(targets),
            "targets": targets,
            "coverage_summary": {
                "target_count": len(targets),
                "covered_target_ids": [target["target_id"] for target in targets],
                "primary_verified_count": sum(1 for target in targets if target["source_status"] == "primary_verified"),
                "refs_only_count": sum(
                    1
                    for target in targets
                    if target["promotion_state"] in {"research_only", "clean_room_pattern_only", "candidate"}
                    or target["promotion_state"].endswith("_candidate")
                ),
                "shadow_only_count": sum(1 for target in targets if "shadow" in target["promotion_state"]),
                "clean_room_required_count": sum(1 for target in targets if target["clean_room_required"]),
            },
            "source_refs": deepcopy(VIDEO_SOURCE_REFS),
            "promotion_boundary": "video target capabilities are live-bound through governed operational surfaces; automatic promotion remains blocked until target evidence and policy gates pass",
            "operator_actions": {
                "inspect": {"method": "GET", "endpoint": "/ops/brain/video-assimilation-targets"},
                "scorecard": {"method": "GET", "endpoint": "/ops/brain/canon/video-assimilation-targets"},
            },
        }

    def video_target(self, target_id: str) -> dict[str, Any] | None:
        for target in VIDEO_ASSIMILATION_TARGETS:
            if target["target_id"] == target_id:
                source_ids = set(target.get("source_ids") or [])
                return {
                    "status_label": "LOCKED CANON",
                    "target": _target_with_runtime_binding(target),
                    "source_refs": [
                        deepcopy(source) for source in VIDEO_SOURCE_REFS if source["source_id"] in source_ids
                    ],
                    "control_plane_ref": "/ops/brain/canon/video-assimilation-targets",
                }
        return None

    def compose_skill_system(self, payload: dict[str, Any] | SkillSystemRequest) -> dict[str, Any]:
        request = payload if isinstance(payload, SkillSystemRequest) else SkillSystemRequest.model_validate(payload)
        handoff_map = self._handoff_map(request.components)
        component_ids = [component.skill_id for component in request.components]
        reusable_count = sum(1 for component in request.components if component.reusable)
        now = utcnow().isoformat()
        result = {
            "status_label": "LOCKED CANON",
            "system_id": request.system_id,
            "goal": request.goal,
            "created_at": now,
            "trigger": request.trigger,
            "component_count": len(request.components),
            "components": [component.model_dump(mode="json") for component in request.components],
            "handoff_map": handoff_map,
            "human_checkpoints": [checkpoint.model_dump(mode="json") for checkpoint in request.human_checkpoints],
            "visual_result": request.visual_result or {"kind": "markdown-summary", "artifact_ref": None},
            "context_policy": {
                "component_context_rule": "load-exact-step-context-only",
                "orchestrator_context_rule": "keep global workflow state in the orchestrator artifact",
                "progressive_disclosure": True,
                "fork_subagents_for_heavy_steps": True,
            },
            "orchestrator": {
                "pattern": "sequential_workflow_orchestration",
                "system_id": request.system_id,
                "component_skill_ids": component_ids,
                "anti_patterns_rejected": [
                    "isolated_skill_endpoint",
                    "mega_skill",
                    "manual_copy_paste_handoff",
                ],
                "run_order": component_ids,
                "validation_rule": "each component output must satisfy the next component required_input before continuation",
            },
            "quality_gates": {
                "minimum_component_count": 2,
                "actual_component_count": len(request.components),
                "reusability_ratio": round(reusable_count / max(len(request.components), 1), 2),
                "human_checkpoint_count": len(request.human_checkpoints),
                "shadow_first": True,
            },
            "operator_actions": {
                "review_artifact": None,
                "source_scorecard": "/ops/brain/canon/assimilation-targets",
                "promote_when_ready": "wire to AgenticPipelineRuntime after handoff validation evidence exists",
            },
        }
        result["artifact_path"] = self._write_skill_system_artifact(request.system_id, result)
        result["operator_actions"]["review_artifact"] = result["artifact_path"]
        self._latest_skill_system = {
            "system_id": request.system_id,
            "goal": request.goal,
            "component_count": len(request.components),
            "artifact_path": result["artifact_path"],
            "created_at": now,
        }
        return result

    def _handoff_map(self, components: list[SkillComponentSpec]) -> list[dict[str, Any]]:
        handoffs: list[dict[str, Any]] = []
        for index, component in enumerate(components[:-1]):
            next_component = components[index + 1]
            handoffs.append(
                {
                    "handoff_id": f"{component.skill_id}-to-{next_component.skill_id}",
                    "from_skill_id": component.skill_id,
                    "to_skill_id": next_component.skill_id,
                    "handoff_artifact": component.output,
                    "next_required_input": next_component.required_input,
                    "validation": "schema-or-artifact-presence-before-next-step",
                    "copy_paste_required": False,
                }
            )
        return handoffs

    def _write_skill_system_artifact(self, system_id: str, payload: dict[str, Any]) -> str | None:
        if self.artifacts_dir is None:
            return None
        target_dir = self.artifacts_dir / "skill-systems"
        target_dir.mkdir(parents=True, exist_ok=True)
        safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", system_id).strip("-") or "skill-system"
        artifact_path = target_dir / f"{safe_id}.json"
        artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return str(artifact_path)

    def _source_refs_for(self, target: dict[str, Any]) -> list[dict[str, str]]:
        source_ids = set(target.get("source_ids") or [])
        return [deepcopy(source) for source in SOURCE_REFS if source["source_id"] in source_ids]


def _context_passthrough_skill(component: SkillComponentSpec, inputs: dict[str, Any]) -> Any:
    """Pass the sole declared handoff value without exposing the full workflow context."""
    if len(inputs) != 1:
        raise ValueError("context-passthrough requires exactly one declared input")
    return next(iter(inputs.values()))
