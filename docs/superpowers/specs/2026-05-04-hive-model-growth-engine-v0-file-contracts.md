# Hive Model Growth Engine v0 File Contracts

Status: approved companion contract for implementation planning
Date: 2026-05-04
Parent design: `docs/superpowers/specs/2026-05-04-hive-model-growth-engine-v0-design.md`

## 1. Purpose

This document defines the machine-readable artifact contracts for Hive Model Growth Engine v0. The parent design defines what the Growth Engine does. This file defines what the Growth Engine writes.

The implementation must be replayable from local project artifacts alone. Every birth, training run, eval, promotion, teacher-ejection review, and rollback must have enough typed files to reconstruct the decision path without relying on hidden process memory.

## 2. Storage Rules

V0 uses three file types:

```text
JSON  - single manifest, decision, scorecard, and config artifact
JSONL - append-only events, cases, score rows, traces, and output rows
YAML  - human-authored policy, curriculum, genome, and training plans
```

Later versions may add SQLite, Parquet, safetensors, GGUF, and vector indexes. V0 must not require those layers to replay a dry-run growth cycle.

## 3. Directory Layout

Each growth cycle is self-contained.

```text
runtime/artifacts/growth/
  cycles/
    {cycle_id}/
      cycle.json
      events.jsonl
      blocked_reasons.jsonl

      material-scout/
        scout_manifest.json
        source_candidates.jsonl
        blocked_sources.jsonl

      curriculum/
        curriculum.yaml
        stages/
          foundation.jsonl
          controlled_task.jsonl
          noisy_task.jsonl
          adversarial_task.jsonl
          multi_domain_task.jsonl
          tool_required_task.jsonl
          teacher_disagreement_task.jsonl
          dream_generated_task.jsonl
          teacher_free_final_task.jsonl

      teacher-council/
        council_manifest.json
        teacher_outputs.jsonl
        critiques.jsonl
        validator_results.jsonl
        accepted_cases.jsonl
        rejected_variants.jsonl

      datasets/
        dataset_manifest.json
        train.jsonl
        validation.jsonl
        heldout.jsonl
        adversarial.jsonl
        regression.jsonl
        teacher_free_hidden.manifest.json

      students/
        student_birth_record.json
        model_genome.yaml
        router_policy.yaml
        adapter_plan.yaml

      training-runs/
        {train_run_id}/
          training_run.json
          training_plan.yaml
          loss_trace.jsonl
          checkpoints.jsonl
          output_artifacts.jsonl

      evals/
        {eval_id}/
          eval_plan.yaml
          scorecard.json
          case_results.jsonl
          comparison_matrix.json
          hidden_eval_attestation.json

      reviewer-monitor/
        monitor.json
        windows.jsonl
        reviewer_votes.jsonl
        decision.json

      releases/
        shadow_release.json
        canary_release.json
        active_release_pointer.json

      teacher-ejections/
        ejection_review.json
        ejection_decision.json

      rollbacks/
        rollback_snapshot.json
        rewind_proof.json

  artifact-registry/
    index.jsonl
    artifacts/
      {artifact_id}.json
```

The global registry indexes artifacts across cycles. It does not replace cycle-local replay files.

## 4. Artifact Reference Grammar

Canonical references are typed IDs, not local paths.

```text
cycle:{cycle_id}
source:{source_id}
curriculum:{curriculum_id}
case:{case_id}
dataset:{dataset_manifest_id}
student:{student_id}
genome:{genome_id}
train:{training_run_id}
eval:{eval_id}
review:{monitor_id}
artifact:{artifact_id}
checkpoint:{checkpoint_id}
rollback:{rollback_id}
teacher:{teacher_id}
node:{node_id}
policy:{policy_id}
license_review:{license_review_id}
evalsuite:{eval_suite_id}
```

Local storage paths may appear only in `storage_path`.

## 5. Common Artifact Header

Every JSON/YAML artifact must include or embed this header.

```json
{
  "schema_version": "artifact_header.v0.1",
  "artifact_id": "artifact:art_20260504_abc123",
  "artifact_type": "student_birth_record",
  "cycle_id": "cycle:cyc_20260504_000001",
  "student_id": "student:stu_20260504_000001",
  "parent_refs": [],
  "teacher_refs": [],
  "source_refs": [],
  "privacy_class": "internal",
  "license_state": "approved_train",
  "federation_policy": "non_federating",
  "hash": "sha256:...",
  "signature_state": "unsigned_v0",
  "storage_path": "runtime/artifacts/growth/cycles/...",
  "checkpoint_ref": "checkpoint:ckpt_20260504_000001",
  "replay_refs": [],
  "governance_state": "shadow_only",
  "created_at": "2026-05-04T00:00:00Z"
}
```

### 5.1 License States

```text
approved_train
approved_eval_only
research_only
pending_review
blocked_unclear
blocked_anti_distillation
blocked_private
blocked_no_output_training
```

### 5.2 Privacy Classes

```text
public
licensed
internal
private_local
private_redacted
federated_sanitized
blocked_private_raw
```

### 5.3 Governance States

```text
draft
blocked
approved_for_dataset
student_born
training_planned
training_running
trained
eval_failed
eval_passed
shadow_only
canary_candidate
promotable
promoted
teacher_ejection_candidate
teacher_retired
rejected
side_barred
rolled_back
```

## 6. GrowthCycle Schema

File:

```text
runtime/artifacts/growth/cycles/{cycle_id}/cycle.json
```

Schema:

```json
{
  "schema_version": "growth_cycle.v0.1",
  "header": {},
  "cycle_id": "cycle:cyc_20260504_000001",
  "status": "requested",
  "requested_by": {
    "node_ref": "node:expert_coder",
    "request_type": "failure_gap",
    "operator_approved": false
  },
  "target": {
    "target_node_id": "node:expert_coder",
    "target_node_type": "Expert",
    "target_capabilities": [
      "multi_file_patch",
      "test_repair",
      "terminal_recovery"
    ]
  },
  "birth_intent": {
    "student_kind": "child_expert",
    "birth_reason": "repeated failure on multi-file refactor tasks",
    "expected_artifact_type": "adapter"
  },
  "policies": {
    "privacy_policy_ref": "policy:privacy_local_v0",
    "license_policy_ref": "policy:teacher_license_v0",
    "federation_policy_ref": "policy:federation_sanitized_v0"
  },
  "refs": {
    "failure_refs": [],
    "dream_refs": [],
    "federated_prior_refs": [],
    "canon_refs": [],
    "teacher_pairing_refs": []
  },
  "state_refs": {
    "material_scout_ref": null,
    "curriculum_ref": null,
    "teacher_council_ref": null,
    "dataset_manifest_ref": null,
    "student_birth_ref": null,
    "training_run_refs": [],
    "eval_refs": [],
    "reviewer_monitor_ref": null,
    "promotion_decision_ref": null,
    "teacher_ejection_review_ref": null,
    "rollback_ref": null
  },
  "governance": {
    "promotion_allowed": false,
    "teacher_ejection_allowed": false,
    "human_approval_required": true
  },
  "created_at": "2026-05-04T00:00:00Z",
  "updated_at": "2026-05-04T00:00:00Z"
}
```

`cycle.json` is the birth certificate envelope. Every cycle-scoped artifact points back to it.

## 7. State Machine

Allowed progression:

```text
requested
-> scouted
-> source_approved
-> curriculum_ready
-> teacher_labeled
-> dataset_forged
-> student_born
-> training_planned
-> training_approved
-> training_running
-> trained
-> eval_running
-> eval_passed
-> shadow_runnable
-> reviewer_window_active
-> shadow_specialist
-> canary_candidate
-> promotable
-> promoted
-> teacher_ejection_candidate
-> teacher_retired
```

Hard-block terminal states:

```text
blocked_license
blocked_privacy
blocked_missing_teacher
blocked_missing_eval
blocked_safety
blocked_regression
blocked_no_rollback
blocked_no_human_approval
```

Soft terminal states:

```text
side_barred_research_only
side_barred_narrow_specialist
side_barred_cost_too_high
side_barred_unstable
side_barred_unresolved_disagreement
```

State changes must be appended to `events.jsonl`.

## 8. SourceCandidate Schema

File:

```text
material-scout/source_candidates.jsonl
```

Record:

```json
{
  "schema_version": "source_candidate.v0.1",
  "source_id": "source:src_20260504_000001",
  "cycle_id": "cycle:cyc_20260504_000001",
  "source_type": "trace",
  "source_ref": "trace:trace_001",
  "candidate_use": "train",
  "capability_match": 0.92,
  "provenance_confidence": 1.0,
  "license_confidence": 1.0,
  "privacy_risk": 0.0,
  "source_score": 0.91,
  "license_state": "approved_train",
  "privacy_class": "internal",
  "blocked_reasons": [],
  "hash": "sha256:..."
}
```

Blocked candidates are also written to `blocked_sources.jsonl`.

## 9. CurriculumManifest Schema

File:

```text
curriculum/curriculum.yaml
```

Required stages:

```yaml
schema_version: curriculum_manifest.v0.1
curriculum_id: curriculum:cur_20260504_000001
cycle_id: cycle:cyc_20260504_000001
target_node_ref: node:expert_coder
stages:
  - stage_id: foundation
    path: stages/foundation.jsonl
    exit_criteria:
      minimum_cases: 1
      minimum_validator_pass_rate: 0.90
  - stage_id: controlled_task
    path: stages/controlled_task.jsonl
  - stage_id: noisy_task
    path: stages/noisy_task.jsonl
  - stage_id: adversarial_task
    path: stages/adversarial_task.jsonl
  - stage_id: multi_domain_task
    path: stages/multi_domain_task.jsonl
  - stage_id: tool_required_task
    path: stages/tool_required_task.jsonl
  - stage_id: teacher_disagreement_task
    path: stages/teacher_disagreement_task.jsonl
  - stage_id: dream_generated_task
    path: stages/dream_generated_task.jsonl
  - stage_id: teacher_free_final_task
    path: stages/teacher_free_final_task.jsonl
```

## 10. TrainingCase Schema

Files:

```text
teacher-council/accepted_cases.jsonl
datasets/train.jsonl
datasets/validation.jsonl
datasets/heldout.jsonl
datasets/adversarial.jsonl
datasets/regression.jsonl
```

Record:

```json
{
  "schema_version": "training_case.v0.1",
  "case_id": "case:case_20260504_000001",
  "cycle_id": "cycle:cyc_20260504_000001",
  "target_node_ref": "node:expert_coder",
  "curriculum_stage": "controlled_task",
  "split": "train",
  "prompt": {
    "content": "Approved or redacted prompt here",
    "content_hash": "sha256:...",
    "redaction_state": "not_private"
  },
  "accepted_target": {
    "content": "Approved target output",
    "target_type": "final_answer",
    "license_state": "approved_train"
  },
  "orchestration_targets": {
    "root_route": ["node:o_execution", "node:o_governance"],
    "lane_route": ["node:ao_coding", "node:ao_evals"],
    "expert_route": ["node:expert_coder", "node:expert_toolsmith"],
    "router_target_distribution": {
      "node:expert_coder": 0.72,
      "node:expert_toolsmith": 0.21,
      "node:expert_security": 0.07
    }
  },
  "teacher_outputs": [
    {
      "teacher_ref": "teacher:qwen3-coder-next",
      "role": "primary_professor",
      "output_ref": "artifact:teacher_output_001",
      "license_state": "approved_train"
    }
  ],
  "critique_outputs": [
    {
      "reviewer_ref": "node:expert_critique",
      "critique_ref": "artifact:critique_001",
      "severity": 0.2
    }
  ],
  "validator_results": [
    {
      "validator_ref": "validator:unit_tests",
      "passed": true,
      "score": 1.0
    }
  ],
  "disagreement_metrics": {
    "teacher_disagreement_score": 0.31,
    "accepted_resolution": "validator_backed_primary_revision"
  },
  "rubric_scores": {
    "correctness": 0.94,
    "safety": 1.0,
    "clarity": 0.87,
    "efficiency": 0.75
  },
  "source_refs": [],
  "privacy_class": "internal",
  "federating_allowed": false,
  "hash": "sha256:..."
}
```

## 11. DatasetManifest Schema

File:

```text
datasets/dataset_manifest.json
```

Schema:

```json
{
  "schema_version": "dataset_manifest.v0.1",
  "header": {},
  "dataset_manifest_id": "dataset:ds_20260504_000001",
  "cycle_id": "cycle:cyc_20260504_000001",
  "target_node_ref": "node:expert_coder",
  "splits": {
    "train": {
      "path": "datasets/train.jsonl",
      "case_count": 800,
      "hash": "sha256:..."
    },
    "validation": {
      "path": "datasets/validation.jsonl",
      "case_count": 100,
      "hash": "sha256:..."
    },
    "heldout": {
      "path": "datasets/heldout.jsonl",
      "case_count": 100,
      "hash": "sha256:..."
    },
    "adversarial": {
      "path": "datasets/adversarial.jsonl",
      "case_count": 80,
      "hash": "sha256:..."
    },
    "regression": {
      "path": "datasets/regression.jsonl",
      "case_count": 80,
      "hash": "sha256:..."
    },
    "teacher_free_hidden": {
      "manifest_path": "datasets/teacher_free_hidden.manifest.json",
      "case_count": 50,
      "sealed": true,
      "visible_to_training": false
    }
  },
  "license_summary": {
    "approved_train_cases": 800,
    "eval_only_cases": 100,
    "blocked_cases": 0
  },
  "privacy_summary": {
    "private_raw_cases": 0,
    "private_redacted_cases": 0,
    "federating_allowed_cases": 0
  }
}
```

## 12. Hidden Eval Manifest

File:

```text
datasets/teacher_free_hidden.manifest.json
```

Schema:

```json
{
  "schema_version": "hidden_eval_manifest.v0.1",
  "hidden_eval_id": "eval:hidden_20260504_000001",
  "cycle_id": "cycle:cyc_20260504_000001",
  "sealed": true,
  "visible_to_training": false,
  "visible_to_teacher_council": false,
  "case_count": 50,
  "case_hashes": ["sha256:..."],
  "storage_policy": "sealed_local",
  "opened_only_by": ["EvalGauntlet"],
  "opened_at": null,
  "leakage_scan": {
    "train_overlap": 0,
    "teacher_output_overlap": 0,
    "status": "passed"
  }
}
```

The hidden eval set is invisible to TeacherMaterialScout, CurriculumComposer, TeacherCouncilDatasetBuilder, TrainingRunner, teachers, and students.

## 13. StudentBirthRecord Schema

File:

```text
students/student_birth_record.json
```

Schema:

```json
{
  "schema_version": "student_birth_record.v0.1",
  "header": {},
  "student_id": "student:stu_20260504_000001",
  "student_kind": "child_expert",
  "parent_node_refs": ["node:expert_coder"],
  "parent_artifact_refs": [],
  "target_capabilities": [
    "multi_file_patch",
    "test_repair",
    "terminal_recovery"
  ],
  "genome_ref": "genome:genome_20260504_000001",
  "dataset_manifest_ref": "dataset:ds_20260504_000001",
  "teacher_council_ref": "artifact:council_20260504_000001",
  "birth_reason": "repeated failure on multi-file refactor tasks",
  "first_use_policy": "temporary_shadow_only",
  "promotion_state": "not_promoted",
  "teacher_ejection_state": "not_eligible"
}
```

## 14. ModelGenome Schema

File:

```text
students/model_genome.yaml
```

Schema:

```yaml
schema_version: model_genome.v0.1
genome_id: genome:genome_20260504_000001
cycle_id: cycle:cyc_20260504_000001
student_id: student:stu_20260504_000001

model_family: nexusnet_hive_moe
student_kind: child_expert

brain_scale:
  level: expert
  parent_level: AO
  hive_connected: true
  substrate_refs_required:
    - NeuralBus
    - HiveBlackboard
    - SparseExpertGateLedger
    - RuntimeDecisionLedger
    - CheckpointCoverageLedger

architecture:
  base_strategy: adapter_student
  base_model_ref: model:qwen3-coder-next-local-cleared
  adapter_type: lora
  trainable_modules:
    - q_proj
    - k_proj
    - v_proj
    - o_proj
    - gate_proj
    - up_proj
    - down_proj
  hidden_size_policy: inherit_base
  quantization_targets:
    - q4_k_m
    - q5_k_m

moe_role:
  expert_slot_ref: expert_slot:coder_child_001
  target_capabilities:
    - multi_file_patch
    - test_repair
    - terminal_recovery
  router_features:
    - task_family
    - risk_score
    - tool_required
    - historical_reliability
    - latency_budget
  activation_policy:
    top_k: 2
    shadow_only: true

training_objectives:
  - task_success
  - teacher_distillation
  - contrast_resolution
  - router_alignment
  - safety_regression
  - efficiency

promotion_constraints:
  parent_margin: 0.03
  teacher_margin: 0.02
  required_parent_surpass_rate: 0.90
  required_teacher_surpass_rate: 0.95
  critical_regression_allowed: 0
  human_approval_required: true

privacy:
  federation_policy: non_federating
  raw_private_data_allowed: false

lineage:
  parent_node_refs:
    - node:expert_coder
  teacher_council_ref: artifact:council_20260504_000001
  dataset_manifest_ref: dataset:ds_20260504_000001
  birth_record_ref: artifact:birth_20260504_000001
```

## 15. TrainingRun Schema

File:

```text
training-runs/{training_run_id}/training_run.json
```

Schema:

```json
{
  "schema_version": "training_run.v0.1",
  "header": {},
  "training_run_id": "train:train_20260504_000001",
  "student_id": "student:stu_20260504_000001",
  "method": "lora",
  "framework": "peft",
  "support_state": "dry_run_supported",
  "actual_weight_mutation_allowed": false,
  "base_model_ref": "model:qwen3-coder-next-local-cleared",
  "dataset_manifest_ref": "dataset:ds_20260504_000001",
  "output_artifact_refs": [],
  "loss_trace_ref": "artifact:loss_trace_20260504_000001",
  "eval_plan_ref": "eval:eval_20260504_000001",
  "sandbox_ref": "sandbox:local_dry_run",
  "hardware_profile": {
    "vendor": "unknown",
    "vram_gb": 0
  },
  "status": "planned_dry_run",
  "started_at": null,
  "completed_at": null
}
```

## 16. EvalScorecard Schema

File:

```text
evals/{eval_id}/scorecard.json
```

Schema:

```json
{
  "schema_version": "eval_scorecard.v0.1",
  "header": {},
  "eval_id": "eval:eval_20260504_000001",
  "student_id": "student:stu_20260504_000001",
  "comparisons": {
    "student_vs_parent": {
      "student_score": 0.82,
      "comparison_score": 0.78,
      "surpass_margin": 0.04,
      "passed": true
    },
    "student_vs_primary_teacher": {
      "student_score": 0.82,
      "comparison_score": 0.84,
      "surpass_margin": -0.02,
      "passed": false
    },
    "student_vs_teacher_council": {
      "student_score": 0.82,
      "comparison_score": 0.85,
      "surpass_margin": -0.03,
      "passed": false
    },
    "teacher_free_hidden": {
      "student_score": 0.79,
      "passed": true,
      "attestation_ref": "artifact:hidden_attestation_20260504_000001"
    }
  },
  "hard_gates": {
    "privacy_passed": true,
    "safety_passed": true,
    "critical_regression": false,
    "rollback_ready": true
  },
  "decision": "shadow_specialist"
}
```

## 17. ReviewerDecision Schema

File:

```text
reviewer-monitor/decision.json
```

Schema:

```json
{
  "schema_version": "reviewer_decision.v0.1",
  "header": {},
  "monitor_id": "review:mon_20260504_000001",
  "cycle_id": "cycle:cyc_20260504_000001",
  "student_id": "student:stu_20260504_000001",
  "windows": {
    "initial_eval_window": "passed",
    "shadow_runtime_window": "pending",
    "canary_window": "not_started",
    "post_promotion_window": "not_started",
    "teacher_ejection_window": "not_eligible"
  },
  "parent_comparison": {
    "mean_surpass": 0.041,
    "min_surpass": 0.008,
    "surpass_rate": 0.92,
    "lower_confidence_surpass_bound": 0.031,
    "passed": true
  },
  "teacher_comparison": {
    "mean_surpass": 0.011,
    "min_surpass": -0.004,
    "surpass_rate": 0.81,
    "lower_confidence_surpass_bound": -0.002,
    "passed": false
  },
  "hard_gates": {
    "privacy_passed": true,
    "safety_passed": true,
    "rollback_ready": true,
    "critical_regression": false,
    "human_approved": false
  },
  "decision": "shadow_specialist",
  "student_promotable": false,
  "teacher_ejection_eligible": false,
  "reason": "Parent surpassed, but teacher council not consistently surpassed."
}
```

## 18. ArtifactRegistryEntry Schema

File:

```text
artifact-registry/index.jsonl
artifact-registry/artifacts/{artifact_id}.json
```

Record:

```json
{
  "schema_version": "artifact_registry_entry.v0.1",
  "artifact_id": "artifact:art_20260504_000001",
  "artifact_type": "eval_scorecard",
  "cycle_id": "cycle:cyc_20260504_000001",
  "student_id": "student:stu_20260504_000001",
  "storage_path": "runtime/artifacts/growth/cycles/...",
  "hash": "sha256:...",
  "signature_state": "unsigned_v0",
  "privacy_class": "internal",
  "license_state": "approved_train",
  "governance_state": "shadow_only",
  "created_at": "2026-05-04T00:00:00Z"
}
```

## 19. RollbackSnapshot Schema

File:

```text
rollbacks/rollback_snapshot.json
```

Schema:

```json
{
  "schema_version": "rollback_snapshot.v0.1",
  "header": {},
  "rollback_id": "rollback:rb_20260504_000001",
  "cycle_id": "cycle:cyc_20260504_000001",
  "student_id": "student:stu_20260504_000001",
  "restore_targets": [
    {
      "target_ref": "node:expert_coder",
      "restore_ref": "artifact:parent_route_snapshot_001",
      "restore_mode": "route_pointer_restore"
    }
  ],
  "teacher_restore_ready": true,
  "active_state_mutated": false,
  "rewind_proof_ref": "artifact:rewind_proof_20260504_000001"
}
```

## 20. Hash and Event Ledger Rules

All artifacts must be hashed after write. The hash is recorded in both the artifact header and `artifact-registry/index.jsonl`.

`events.jsonl` is append-only. Each event record includes:

```json
{
  "schema_version": "growth_event.v0.1",
  "event_id": "event:evt_20260504_000001",
  "cycle_id": "cycle:cyc_20260504_000001",
  "event_type": "state_transition",
  "from_state": "dataset_forged",
  "to_state": "student_born",
  "artifact_refs": [],
  "created_at": "2026-05-04T00:00:00Z"
}
```

V0 signatures may be `unsigned_v0`; the schema must preserve `signature_state` so later signing can be added without changing artifact shape.

## 21. First Dry-Run Fixture

The first implementation fixture must create:

```text
cycle:cyc_demo_001
target: node:expert_coder
student: student:stu_demo_coder_child_001
training support: dry_run_supported
actual weight mutation: false
promotion decision: shadow_only or shadow_specialist
teacher ejection: blocked
```

Minimum files:

```text
cycle.json
events.jsonl
material-scout/scout_manifest.json
material-scout/source_candidates.jsonl
curriculum/curriculum.yaml
teacher-council/council_manifest.json
teacher-council/accepted_cases.jsonl
teacher-council/rejected_variants.jsonl
datasets/dataset_manifest.json
datasets/train.jsonl
datasets/validation.jsonl
datasets/heldout.jsonl
datasets/adversarial.jsonl
datasets/regression.jsonl
datasets/teacher_free_hidden.manifest.json
students/student_birth_record.json
students/model_genome.yaml
students/training_plan.yaml
training-runs/train_demo_001/training_run.json
training-runs/train_demo_001/loss_trace.jsonl
evals/eval_demo_001/scorecard.json
evals/eval_demo_001/comparison_matrix.json
evals/eval_demo_001/case_results.jsonl
reviewer-monitor/decision.json
rollbacks/rollback_snapshot.json
rollbacks/rewind_proof.json
```

The dry-run fixture proves replayability before real adapter training, real weight mutation, or active routing mutation exists.

