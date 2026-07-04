# NexusNet Hive Model Growth Engine v0 Design

Status: approved architecture design, pending implementation plan
Date: 2026-05-04
Primary source book: `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`
Post-book addendum: `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
Teacher matrix: `docs/NEXUSNET_TEACHER_PAIRING_MATRIX_2026-05-04.md`
Substrate design: `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`
File contracts: `docs/superpowers/specs/2026-05-04-hive-model-growth-engine-v0-file-contracts.md`

## 1. Purpose

Hive Model Growth Engine v0 is the missing reproductive spine for NexusNet. The Hive Neural Substrate gives NexusNet a connected nervous system; the Growth Engine turns substrate evidence into actual child model artifacts that can be trained, evaluated, shadow-routed, promoted, retired, rolled back, and inspected.

The engine must let NexusNet grow from:

- teacher-guided expert traces,
- Recursive Neural Dreaming candidates,
- sanitized federated learning priors,
- failure traces,
- evaluator findings,
- user-approved project artifacts,
- license-cleared research material,
- runtime/backend performance evidence,
- and operator-approved curriculum material

into real student Experts, AOs, Os, router policies, adapters, quantized variants, and eventually a native NexusNet MoE lineage.

V0 is not allowed to silently mutate active production state. V0 creates the first complete growth loop:

```text
evidence -> training material -> teacher council labels -> dataset -> student birth
-> training run -> eval gauntlet -> shadow artifact -> reviewer decision
-> promotion candidate -> teacher ejection candidate only after repeated surpass proof
```

Implementation must be artifact-contract first. Every growth cycle, dataset split, teacher council output, student birth, training run, eval result, reviewer decision, promotion decision, teacher ejection review, and rollback proof must be written as replayable project-local artifacts before any future indexed database or real weight mutation is added.

## 2. Non-Negotiable Doctrine

### 2.1 Hive-Wide Access

The Growth Engine is not a lane silo. It is available to every routed node through the hive-wide neuroplastic substrate. Any Expert, AO, O, Mini-NexusNet, runtime component, dream cycle, evaluator, memory plane, or idle node can request a growth cycle when policy allows.

Coordinator nodes such as Dream Evolution O, TrainingAO, SelfTrainingAO, EvalsAO, GovernanceAO, and CuratorAO can schedule, audit, or review growth. They do not own growth exclusively.

### 2.2 License-Safe Teacher Sources

Training material, teacher outputs, labels, preference rankings, critiques, rubrics, synthetic examples, and distillation targets must come only from:

- open-source/open-weight sources whose license permits the intended training or derivative use,
- owned NexusNet data,
- human-authored material under assignment or explicit permission,
- deterministic validators and simulators,
- explicitly licensed teacher services that allow training/distillation/model improvement,
- public-domain or otherwise licensed datasets.

Sources with anti-distillation, anti-competitive-model, no-output-training, no-automated-extraction, or unclear rights are blocked from training use.

### 2.3 Private Data Boundary

Raw private prompts, raw outputs, private files, local paths, screenshots, secrets, personal identifiers, unredacted logs, and raw user-specific memory must not enter shared training or federation. Private local data may be used only when:

- the operator explicitly approves local-only training,
- the artifact is marked non-federating,
- no raw content leaves the machine,
- the generated artifact carries private-data lineage,
- and promotion remains local/private unless later sanitized and reviewed.

### 2.4 Student Promotion Is Not Teacher Ejection

Student promotion and teacher ejection are separate gates.

A student can become:

```text
candidate -> trained -> eval-passed -> shadow-runnable -> canary/promotable
```

without ejecting any teacher.

Teacher ejection is allowed only after repeated, independent, statistically meaningful surpass evidence proves the student consistently outperforms the relevant teacher or teacher council across held-out, adversarial, regression, domain, teacher-disagreement, and teacher-free evaluation windows.

No teacher is ejected because of one good run.

## 3. System Position

Hive Model Growth Engine v0 sits above the Hive Neural Substrate and below production routing.

```text
Hive Neural Substrate
  -> failure, trace, dream, federation, genome, optimizer, runtime ledgers
  -> Hive Model Growth Engine
      -> material scouting
      -> curriculum construction
      -> teacher council generation
      -> student birth
      -> sandboxed training
      -> eval gauntlet
      -> artifact registry
      -> reviewer/ejection gates
  -> Shadow Runtime
  -> Governance Release
  -> Active NexusNet routing pointer
```

The engine must publish every meaningful event to NeuralBus-compatible artifacts and Control Panel surfaces so developers can inspect what happened, why it happened, what math was used, what data was used, which teachers participated, what was blocked, and what would roll back.

## 4. Core Components

### 4.1 TeacherMaterialScout

Purpose: find and rank candidate training sources for a target Expert, AO, O, router policy, runtime method, or Mini-NexusNet.

Inputs:

- `target_node_id`
- `target_node_type`: Expert, AO, O, Router, Runtime, Memory, Governance, Multimodal, other
- `target_capabilities`
- `teacher_pairing_refs`
- `failure_refs`
- `dream_refs`
- `federated_prior_refs`
- `canon_refs`
- `research_refs`
- `privacy_policy`
- `license_policy`

Outputs:

- source candidates,
- relevance score,
- capability match score,
- provenance refs,
- license state,
- privacy state,
- blocked reasons,
- recommended use: train, eval-only, research-only, sidebar, or reject.

The scout must write a cycle-scoped `scout_manifest.json`, `source_candidates.jsonl`, and `blocked_sources.jsonl`. Local filesystem paths are never canonical references; canonical references use the artifact-ref grammar defined in the file-contract spec.

Required scoring:

```text
source_score =
  0.35 * capability_match
+ 0.20 * provenance_confidence
+ 0.15 * license_confidence
+ 0.10 * recency_or_freshness
+ 0.10 * evaluator_relevance
+ 0.10 * failure_coverage
- privacy_risk_penalty
- contamination_penalty
```

### 4.2 CurriculumComposer

Purpose: convert approved sources and target capabilities into staged curriculum.

Required curriculum stages:

```text
foundation
controlled_task
noisy_task
adversarial_task
multi_domain_task
tool_required_task
teacher_disagreement_task
dream_generated_task
teacher_free_final_task
```

Each stage must expose:

- tasks,
- expected skills,
- source refs,
- teacher refs,
- validators,
- difficulty score,
- target metrics,
- exit criteria,
- data split assignment,
- privacy/federation policy.

Difficulty formula:

```text
difficulty =
  base_stage_weight
+ ambiguity_score
+ tool_use_score
+ adversarial_score
+ multi_domain_score
+ safety_risk_score
+ memory_dependency_score
```

### 4.3 TeacherCouncilDatasetBuilder

Purpose: make the selected teachers actively generate, label, critique, and refine training material.

For each task, the builder must collect:

- primary teacher output,
- secondary contrast teacher output,
- optional efficiency coach edits where permitted,
- skeptical examiner critique,
- validator outputs,
- disagreement notes,
- rubric scores,
- final accepted target,
- rejected target variants,
- license/provenance bundle,
- raw-private-data flag,
- federation eligibility flag.

Required output schema:

```text
TrainingCase
  case_id
  target_node_ref
  curriculum_stage
  prompt
  accepted_target
  teacher_outputs[]
  critique_outputs[]
  validator_results[]
  disagreement_metrics
  rubric_scores
  source_refs[]
  license_state
  privacy_class
  federating_allowed
  split
```

The builder must support multiple teacher-signal modes:

- `logit_distillation` when teacher logits or distributions are available,
- `sequence_distillation` when approved target text is available,
- `rubric_regression` when teachers provide scores,
- `preference_optimization` when chosen/rejected pairs are available,
- `contrastive_choice` when teachers disagree,
- `validator_grounded_task_loss` when deterministic validators provide ground truth,
- `router_supervision` when route targets are present,
- `safety_classifier_loss` when safety labels are present.

If a teacher is eval-only or research-only, its output can inform scorecards or critique but cannot become a training target.

### 4.4 DatasetForge

Purpose: turn accepted teacher/validator material into split-safe, license-safe, privacy-safe training and eval datasets.

DatasetForge sits between `TeacherCouncilDatasetBuilder` and `StudentBirthEngine`.

It must enforce:

- no hidden eval leakage into training,
- no private raw data in federated material,
- no blocked-license material in training,
- no teacher-free hidden eval visibility to teachers, students, curriculum builders, material scouts, or training runners,
- no duplicate case hashes across train and hidden eval,
- case hashes and source hashes are recorded.

Required splits:

```text
train
validation
heldout
adversarial
regression
teacher_free_hidden
```

The hidden split is sealed. Only EvalGauntlet may open it.

### 4.5 StudentBirthEngine

Purpose: create temporary student nodes from one or more parents.

Student kinds:

- `child_expert`
- `child_AO`
- `child_O`
- `router_policy_student`
- `runtime_method_student`
- `merged_parent_student`
- `dreamed_gap_student`

Each student starts as temporary and shadow-only.

Required record:

```text
StudentBirthRecord
  student_id
  student_kind
  parent_node_refs[]
  parent_artifact_refs[]
  target_capabilities[]
  genome_ref
  dataset_manifest_ref
  teacher_council_ref
  birth_reason
  first_use_policy = temporary_shadow_only
  promotion_state = not_promoted
  teacher_ejection_state = not_eligible
```

The student birth record must be paired with a `model_genome.yaml` file. The birth record proves the student exists; the genome describes the repeatable model organism: brain scale, base strategy, adapter/training strategy, MoE role, router features, trainable modules, privacy/federation policy, promotion thresholds, and lineage.

### 4.6 TrainingRunner

Purpose: execute actual sandboxed training jobs after the planning gate passes.

V0 should support:

- LoRA,
- QLoRA,
- DPO,
- GRPO,
- router-policy training,
- tiny random-init proof-model training for architecture validation,
- adapter export,
- merged model export,
- GGUF export where supported,
- quantization candidate export.

Training is not executed by default. It requires an explicit operator run command, sandbox target, dataset manifest, approved license state, rollback artifact, and eval refs.

Every training method has a support state:

```text
declared_supported
planned
dry_run_supported
sandbox_supported
production_supported
```

V0 must start with `dry_run_supported` for the first child Expert cycle. The UI must not imply a method is production-supported when it only has a dry-run contract.

Required run contract:

```text
TrainingRun
  run_id
  student_id
  method
  framework
  base_model_ref
  dataset_manifest_ref
  output_artifact_refs[]
  loss_trace_ref
  eval_plan_ref
  sandbox_ref
  hardware_profile
  started_at
  completed_at
  status
```

### 4.7 EvalGauntlet

Purpose: prove the student is actually better before promotion or teacher ejection.

Required comparisons:

- student vs parent,
- student vs primary teacher,
- student vs secondary teacher,
- student vs teacher council consensus,
- student vs previous active NexusNet route,
- student vs baseline model,
- student under teacher-free hidden eval.

Required eval families:

- held-out domain tasks,
- adversarial tasks,
- regression tasks,
- privacy/redaction tasks,
- safety/policy tasks,
- latency/cost tasks,
- tool-use tasks where applicable,
- multimodal tasks where applicable,
- long-context tasks where applicable,
- dream-generated tasks,
- federated-prior stress tasks.

Hidden eval isolation is mandatory. The teacher-free hidden set must be invisible to TeacherMaterialScout, CurriculumComposer, TeacherCouncilDatasetBuilder, TrainingRunner, teachers, and students. EvalGauntlet records a leakage scan before hidden evaluation counts toward promotion or teacher ejection.

### 4.8 ReviewerCouncilMonitor

Purpose: monitor teacher/student pairings over time and decide whether a student is stable enough for promotion and whether teachers are eligible for ejection.

Reviewer roles:

- `primary_reviewer`: verifies domain correctness,
- `secondary_reviewer`: verifies contrast behavior,
- `critique_reviewer`: attacks assumptions and overfit,
- `safety_reviewer`: checks misuse and privacy,
- `regression_reviewer`: checks old skills remain intact,
- `runtime_reviewer`: checks latency, cost, memory, backend compatibility,
- `governance_reviewer`: verifies evidence completeness and approval rules.

Monitoring windows:

```text
initial_eval_window
shadow_runtime_window
canary_window
post_promotion_window
teacher_ejection_window
```

The monitor must calculate consistency, not just peak score.

```text
surpass_margin_i = student_score_i - comparison_score_i

mean_surpass = mean(surpass_margin_i)
min_surpass = min(surpass_margin_i)
surpass_rate = count(surpass_margin_i > required_margin) / n
regression_rate = failing_regression_cases / total_regression_cases
stability_score = 1 - stddev(surpass_margin_i)
```

Implementation uses a bounded form:

```text
stability_score = clamp(1 - normalized_stddev(surpass_margin_i), 0, 1)
```

Promotion and teacher ejection must also check:

```text
lower_confidence_surpass_bound >= required_margin
```

Promotion eligibility:

```text
student_promotable =
  mean_surpass_parent >= parent_margin
  AND surpass_rate_parent >= required_parent_surpass_rate
  AND regression_rate == 0
  AND privacy_passed
  AND safety_passed
  AND rollback_ready
  AND reviewer_quorum_passed
  AND human_approved
```

Teacher ejection eligibility:

```text
teacher_ejection_eligible =
  student_promotable
  AND mean_surpass_teacher >= teacher_margin
  AND min_surpass_teacher >= 0
  AND surpass_rate_teacher >= required_teacher_surpass_rate
  AND teacher_free_hidden_eval_passed
  AND post_shadow_stability_window_passed
  AND no_critical_regression
  AND independent_reviewer_quorum_passed
  AND rollback_restore_teacher_ready
  AND human_approved_for_teacher_ejection
```

Default thresholds:

```text
required_parent_surpass_rate = 0.90
required_teacher_surpass_rate = 0.95
parent_margin = 0.03
teacher_margin = 0.02
minimum_eval_windows = 3
minimum_cases_per_window = 50
critical_regression_allowed = 0
teacher_ejection_requires_manual_approval = true
```

If the student only beats the teacher in narrow conditions, the result is `shadow-specialist`, not teacher ejection.

### 4.9 ModelArtifactRegistry

Purpose: store every generated model artifact and make rollback possible.

Artifact types:

- dataset manifest,
- training case bundle,
- adapter,
- merged model,
- quantized model,
- router policy,
- evaluation report,
- teacher evidence bundle,
- student birth record,
- promotion decision,
- teacher ejection decision,
- rollback snapshot.

Every artifact needs:

```text
artifact_id
artifact_type
student_id
parent_refs[]
teacher_refs[]
source_refs[]
license_state
privacy_class
federation_policy
hash
signature_state
storage_path
created_at
rollback_ref
  promotion_state
```

### 4.10 GrowthControlPanel

Purpose: let developers see everything happen.

Required UI surfaces:

- active growth cycles,
- target Expert/AO/O being trained,
- teacher pairings,
- source scouting decisions,
- blocked source reasons,
- curriculum stages,
- teacher outputs and critique summaries,
- training math and loss curves,
- sandbox logs,
- eval gauntlet results,
- student vs parent vs teacher scorecards,
- reviewer monitor windows,
- promotion state,
- teacher ejection eligibility,
- artifact registry,
- rollback route,
- federation eligibility,
- privacy/license gates.

Raw private content must remain redacted by default.

## 5. Math Contracts

### 5.1 Total Training Loss

```text
L_total =
  alpha  * L_distill
+ beta   * L_contrast
+ gamma  * L_task
+ delta  * L_safety
+ eta    * L_router
+ theta  * L_regression
+ lambda * L_privacy
+ mu     * L_efficiency
+ rho    * L_preference
+ sigma  * L_rubric
```

Where:

- `L_distill` aligns the student with approved teacher distributions.
- `L_contrast` teaches disagreement handling between teachers.
- `L_task` optimizes ground-truth or validator-backed task success.
- `L_safety` penalizes unsafe or policy-violating outputs.
- `L_router` optimizes sparse route selection.
- `L_regression` penalizes damage to old capabilities.
- `L_privacy` penalizes leakage or federated privacy risk.
- `L_efficiency` penalizes unnecessary latency, memory, or cost.
- `L_preference` learns chosen/rejected teacher or validator preferences.
- `L_rubric` learns structured score targets when logits are unavailable.

### 5.2 Distillation Loss

```text
L_distill = KL(p_teacher || p_student)
```

This is used only when teacher probabilities or logits are available.

Fallback signal:

```text
L_distill_available =
  KL(p_teacher || p_student) when logits/distributions exist
  OR sequence_cross_entropy(accepted_target, student_output)
  OR 0 when teacher is eval-only/research-only
```

For multi-teacher distillation:

```text
p_council =
  w_primary   * p_primary
+ w_secondary * p_secondary
+ w_critic    * p_critic_target
+ w_validator * p_validator_target

L_distill_council = KL(p_council || p_student)
```

### 5.3 Contrast Loss

```text
L_contrast =
  disagreement_severity
* student_failed_to_explain_choice
* rubric_weight
```

Implementation must use numeric factors in `[0, 1]`:

```text
L_contrast =
  disagreement_severity
* unresolved_choice_penalty
* rubric_weight
* validator_conflict_penalty
```

The student is rewarded for resolving teacher disagreement with source-grounded, validator-backed reasoning rather than blindly copying one teacher.

### 5.4 Router Objective

```text
route_score =
  quality_gain
- cost_penalty
- latency_penalty
- risk_penalty
- privacy_penalty
+ federation_prior
+ dream_novelty_bonus
+ historical_reliability
```

Sparse routing chooses:

```text
selected_experts = top_k(route_score)
```

subject to privacy, safety, capability, and budget constraints.

### 5.5 Teacher Ejection Score

```text
teacher_ejection_score =
  0.35 * mean_surpass_teacher
+ 0.20 * surpass_rate_teacher
+ 0.15 * teacher_free_eval_score
+ 0.10 * regression_cleanliness
+ 0.10 * runtime_stability
+ 0.10 * reviewer_confidence
```

Ejection is blocked if any hard gate fails, regardless of score.

Hard gates:

```text
privacy_passed
safety_passed
rollback_restore_teacher_ready
minimum_windows_met
no_critical_regression
human_approved_for_teacher_ejection
```

### 5.6 Federated Sanitized Prior

```text
global_prior =
  secure_aggregate(
    clip(
      sign(
        privacy_filter(local_delta)
      )
    )
  )
```

Federated packets may influence shadow routing or curriculum priorities. They must not directly mutate active production weights or reveal raw private data.

## 6. Runtime Flow

### 6.1 Growth Cycle

1. A node, evaluator, operator, dream, or federation prior requests growth.
2. Growth Engine normalizes the request into a `GrowthCycle`.
3. TeacherMaterialScout gathers sources.
4. License/privacy gates block contaminated or private sources.
5. CurriculumComposer creates staged tasks.
6. TeacherCouncilDatasetBuilder asks teachers to generate, contrast, critique, and label material.
7. DatasetForge stores approved training cases and eval splits.
8. StudentBirthEngine creates a temporary shadow student.
9. TrainingRunner executes a sandboxed training run only when explicitly approved.
10. EvalGauntlet compares student, parents, teachers, baselines, and teacher-free hidden evals.
11. ReviewerCouncilMonitor calculates consistency windows.
12. ModelArtifactRegistry stores artifacts and scorecards.
13. Governance decides: reject, sidebar, shadow, canary, promote, or teacher-ejection-candidate.
14. Control Panel exposes the full chain.

### 6.2 Teacher Ejection Flow

Teacher ejection requires a separate request after student promotion evidence exists.

```text
promoted student
  -> ejection review request
  -> reviewer monitor window replay
  -> teacher restore proof
  -> independent reviewer quorum
  -> human approval
  -> teacher archived from primary route
  -> teacher retained as rollback/restoration/provenance source
```

Teachers are archived, not deleted.

## 7. Data Storage

V0 begins with project-local JSON, JSONL, and YAML artifacts. Later versions can add SQLite, Parquet, safetensors, GGUF, and indexed query layers, but the first implementation must keep every cycle replayable from files alone.

Required directories:

```text
runtime/artifacts/growth/cycles/
runtime/artifacts/growth/material-scout/
runtime/artifacts/growth/curricula/
runtime/artifacts/growth/teacher-council/
runtime/artifacts/growth/students/
runtime/artifacts/growth/training-runs/
runtime/artifacts/growth/evals/
runtime/artifacts/growth/reviewer-monitor/
runtime/artifacts/growth/artifact-registry/
runtime/artifacts/growth/releases/
runtime/artifacts/growth/teacher-ejections/
runtime/artifacts/growth/rollbacks/
```

Cycle-centered storage is mandatory:

```text
runtime/artifacts/growth/cycles/{cycle_id}/
  cycle.json
  events.jsonl
  ...
```

The global registry indexes artifacts across cycles, but each cycle remains self-contained.

Every artifact must include:

- schema version,
- created timestamp,
- source refs,
- privacy class,
- license state,
- hash or digest,
- checkpoint ref,
- replay refs,
- governance state.

All artifacts use the common artifact header, typed artifact-ref grammar, state machine, enum values, and hash rules defined in the file-contract spec.

## 8. API Surface

Required routes:

```text
GET  /ops/brain/growth-engine
POST /ops/brain/growth-engine/cycles
POST /ops/brain/growth-engine/material-scout
POST /ops/brain/growth-engine/curriculum
POST /ops/brain/growth-engine/teacher-council
POST /ops/brain/growth-engine/students
POST /ops/brain/growth-engine/training-runs
POST /ops/brain/growth-engine/eval-gauntlet
POST /ops/brain/growth-engine/reviewer-monitor
POST /ops/brain/growth-engine/artifacts
POST /ops/brain/growth-engine/promotions
POST /ops/brain/growth-engine/teacher-ejection-reviews
GET  /ops/brain/canon/growth-engine
```

V0 implementation may combine some POST endpoints internally, but the domain model must keep these phases distinct.

## 9. Control Panel Requirements

The Control Panel must show:

- `growth_engine_scorecard`
- active cycle count,
- latest growth cycle,
- latest target node,
- latest teacher council,
- latest student,
- latest training run,
- latest eval gauntlet,
- reviewer monitor state,
- student promotion eligibility,
- teacher ejection eligibility,
- blocked source count,
- blocked training count,
- artifact registry count,
- rollback readiness.

Developer drilldowns must be able to replay:

- source scouting,
- curriculum tasks,
- teacher outputs,
- student birth lineage,
- training math,
- loss trace,
- eval scorecards,
- reviewer windows,
- promotion/ejection decisions,
- rollback proof.

## 10. Error Handling

Hard-block states:

- missing source provenance,
- blocked or unclear license,
- private data without local operator approval,
- missing teacher pairing,
- missing critique reviewer,
- missing eval refs,
- missing rollback artifact,
- failed privacy eval,
- failed safety eval,
- critical regression,
- failed reviewer quorum,
- missing human approval for promotion/ejection.

Soft-sidebar states:

- interesting dream candidate with weak eval,
- narrow specialist beats parent only on one family,
- source useful for research but not training,
- teacher disagreement unresolved,
- insufficient consistency window,
- runtime cost too high for active use.

## 11. Testing Strategy

V0 tests must prove:

1. A growth cycle can be created from a target Expert/AO/O request.
2. Source scouting blocks contaminated/private/unlicensed material.
3. Curriculum contains all required stages.
4. Teacher council output stores primary, secondary, critique, validator, and final target records.
5. Student birth creates temporary shadow-only students.
6. Training runner stays plan-only unless explicit run approval exists.
7. Training run artifacts can be registered after sandbox execution.
8. Eval gauntlet compares student against parent, teachers, and hidden teacher-free cases.
9. Reviewer monitor requires repeated consistency windows.
10. Student promotion does not imply teacher ejection.
11. Teacher ejection is blocked without repeated surpass evidence, rollback proof, reviewer quorum, and human approval.
12. Model artifacts are replayable and rollback-ready.
13. Control Panel and blackbox surfaces expose the growth engine.
14. Raw private content is redacted by default.

## 12. First Implementation Slice

The first implementation should not attempt the final native MoE all at once. It should prove one full shadow growth loop:

```text
target: one generated child Expert
method: adapter-style training run contract
training execution: sandbox stub or local dry-run first
eval: parent/teacher/student scorecards
promotion: shadow-only
teacher ejection: blocked until consistency windows pass
UI: visible in Control Panel
```

First slice support level:

```text
actual_weight_mutation_allowed = false
training_support_state = dry_run_supported
teacher_ejection_state = hard_blocked_until_consistency_windows_pass
```

Done means NexusNet can show a developer:

- why a child Expert was born,
- what teachers generated its material,
- what data and math were used,
- how it performed,
- why it is or is not promotable,
- why no teacher was ejected yet,
- and what exact evidence would be needed for ejection later.
