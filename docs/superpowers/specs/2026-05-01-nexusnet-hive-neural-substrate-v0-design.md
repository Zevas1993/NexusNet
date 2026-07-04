# NexusNet Hive Neural Substrate v0 Design

Status: approved architecture design, implementation not started
Date: 2026-05-01
Primary source book: `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`
Post-book addendum: `docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md`
Assimilation ledger: `docs/NEXUSNET_ASSIMILATION_LEDGER_2026-05-01.md`

## 1. Purpose

Hive Neural Substrate v0 is the first build target for NexusNet as a Neural Network Harness and AI Hive Mind. It is not a chat wrapper, workflow engine, RAG shell, GUI, or single agent. It is the software neural substrate that gives NexusNet a brain-shaped operating core before NexusNet evolves into a native MoE-style AI model.

The design goal is to make NexusNet behave like a graph-recurrent, sparse-MoE, memory-augmented, self-curating neural network at the harness layer:

- Nodes are AOs, experts, Mini-NexusNets, tools, skills, providers, models, sandboxes, memory banks, policy gates, and evaluators.
- Edges are task dependencies, trust relationships, routing history, capability affinities, provenance links, and active message routes.
- Weights are performance, confidence, risk, usefulness, latency, cost, privacy sensitivity, operator approval, and historical reliability.
- Activations are typed task signals moving through the Neural Bus.
- Forward passes are task executions through the hive planes.
- Recurrent loops are deliberation, self-review, Recursive Neural Dreaming, sandbox retries, and assimilation probes.
- Loss is measured through eval results, operator feedback, regression failures, security findings, cost drift, and usefulness deltas.
- Optimization is performed by the Ivy-League School, Hive Curator AO, eval gates, routing updates, federated aggregation, and sandbox promotion.
- Checkpointing is handled by rewind ledgers, trace ledgers, prompt previews, pre-write snapshots, and failed-attempt sidebars.

### 1.1 Hive-Wide Neuroplasticity Fabric

NexusNet self-improvement is not a separate lane that owns improvement. It is a hive-wide neuroplasticity fabric available to every typed node in the substrate. AOs, experts, Mini-NexusNets, orchestrators, tools, memory banks, evaluators, runtime components, sandboxes, policy gates, and idle components all live in one connected hive.

Every node can, through typed contracts:

- Observe shared hive state published through the Neural Bus and HiveBlackboard.
- Request research, Recursive Neural Dreaming, critique, consequence analysis, sandbox testing, eval generation, or promotion review.
- Propose an improvement to itself, another node, a route, a memory plane, a runtime method, a quantization method, a prompt overlay, a skill system, or a governance rule.
- Participate in another node's improvement cycle when routed.
- Receive idle-time dream, replay, curriculum, or assimilation tasks.
- Contribute evidence, warnings, stop signals, and scorecards to any candidate.

Planes, lanes, AOs, and experts are functional views and routing contracts, not ownership silos. Sparse activation controls compute and focus; it does not isolate nodes from awareness, monitoring, or future improvement. The hive can connect any node to any other node through the Neural Bus when the route is useful, traceable, and permitted.

Recursive Neural Dreaming is a distributed protocol inside this fabric:

1. A high-temperature dreamer node generates novel, unusual, or currently non-existent candidate solutions.
2. A lower-temperature reviewer node checks coherence, feasibility, canon fit, testability, and implementation shape.
3. A critic or adversarial node attacks assumptions, safety, regression risk, and prompt-injection exposure.
4. Sandbox/eval nodes implement or simulate the candidate in isolation.
5. Governance and human approval gates decide whether a candidate is rejected, side-barred, canaried, or promoted.

If the hive does not have an expert, AO, orchestrator, O/component, runtime method, quantization method, or tool path that can solve a problem, NexusNet must be able to generate a candidate. Candidate generation can combine two or more parent experts, combine AOs or orchestrators, synthesize a new Mini-NexusNet from capability genomes, or dream a new capability from scratch. First use of a generated child is temporary and shadow-scoped. If the generated candidate solves a problem the parents could not solve and passes sandbox/eval/governance gates, it becomes eligible for retention review. It becomes a permanent standalone addition only after review proves increased retained value. Parent nodes remain active unless the child greatly outperforms one parent, the other, or both under an Ivy-League teacher-review standard; only the respective outperformed parent nodes are then retired from primary routing, archived rather than deleted, and kept rollback-restorable.

Dedicated coordinators such as Curator, School, Dream, Eval, or Governance AOs can schedule, audit, and report improvement work. They do not own or restrict the hive's ability to research, dream, self-improve, or generate new experts.

### 1.2 Fractal Mini-Brain Hierarchy

Mini-NexusNets are scaled brain instances. They are not simple worker modules or prompt wrappers. NexusNet uses a fractal nested-brain topology over the shared Hive Neural Substrate:

1. `NexusBrain` is the largest brain instance and final cognition authority.
2. `Orchestrator` / `O` nodes can carry smaller NexusNet-style brains for broad task decomposition, recovery coordination, and multi-AO handoff.
3. `Assistant Orchestrator` / `AO` nodes can carry smaller brains than O nodes, specialized around assistant-orchestration responsibilities.
4. `Expert` nodes can carry smaller Mini-NexusNet brains than AO nodes, specialized around domain knowledge, local tools, local memory, local evals, and local improvement loops.

The hierarchy is a scale gradient, not a wall. All levels still operate on the same Neural Bus, HiveBlackboard, Memory/Engram Plane, Recurrent Deliberation Plane, Recursive Neural Dreaming protocol, eval system, sandbox system, and Immune/Governance Plane.

Each brain instance must expose:

- `brain_instance_id`
- `brain_scale`: `primary`, `orchestrator`, `assistant_orchestrator`, `expert`, or `generated_candidate`
- `parent_brain_ref`
- `child_brain_refs`
- `local_blackboard_ref`
- `shared_hive_state_refs`
- `health_signal_refs`
- `failure_visibility_scope`
- `recovery_route_refs`
- `dream_participation_contract`
- `self_improvement_contract`

Self-healing is a first-class requirement. If one brain instance begins to fail, stall, hallucinate, regress, overrun its context, lose tool access, violate policy, or degrade in quality, peer and parent brain instances must be able to observe the failure through trace signals, route around the failing node, initiate repair or dream/eval cycles, and keep unrelated work moving where technically possible. The intended operator experience is little to no visible interruption when a recoverable internal failure occurs.

## 2. Research Foundation

### 2.1 Neural Architecture Sources

The v0 substrate assimilates these neural-network ideas:

| Source | Assimilated idea | NexusNet interpretation |
| --- | --- | --- |
| [Attention Is All You Need](https://papers.neurips.cc/paper/7181-attention-is-all-you-need.pdf) | Embeddings, positional encoding, multi-head attention, feed-forward layers, residual connections, layer normalization. | Typed signal vectors, temporal lineage, Cortex attention, expert computation, blackboard residual state, confidence/risk normalization. |
| [Sparsely-Gated Mixture-of-Experts](https://arxiv.org/abs/1701.06538) | Sparse expert activation through a gating network. | CortexRouter activates only the required AOs, experts, tools, models, or sandboxes. |
| [Switch Transformers](https://arxiv.org/abs/2101.03961) and [GShard](https://arxiv.org/abs/2006.16668) | Large sparse models scale capacity while limiting per-token compute. | NexusNet grows by adding experts without activating all of them for every task. |
| [Message Passing Neural Networks](https://proceedings.mlr.press/v70/gilmer17a.html) | Nodes exchange messages over graph edges and aggregate local/global state. | Neural Bus events propagate through AO/expert graph neighborhoods. |
| [Graph Attention Networks](https://arxiv.org/abs/1710.10903) | Nodes attend over neighbors with learned importance. | Experts attend to relevant peer experts, memory banks, and policy gates instead of global broadcast. |
| [Differentiable Neural Computers](https://deepmind.google/blog/differentiable-neural-computers) | Neural controllers use external memory for structured facts and paths. | NexusNet keeps explicit memory planes beside model/provider computation. |
| [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401) | Retrieval supplements parametric generation for knowledge-intensive work. | NexusNet retrieves canon, project memory, traces, docs, and artifacts before expert execution. |
| [Engram conditional memory](https://arxiv.org/abs/2601.07372) | O(1)-style conditional memory lookup complements MoE computation. | Future Memory/Engram Plane stores frequently used canon, skill, entity, and workflow patterns as gated lookup memory. |
| [Ouro LoopLM](https://ouro-llm.github.io/) | Recurrent latent computation and exit gates add a reasoning scaling axis. | Recurrent Deliberation Plane loops hidden hive state before action. |
| [FedAvg federated learning](https://proceedings.mlr.press/v54/mcmahan17a.html) | Local training updates can be aggregated without raw user data exchange. | Federated Learning Plane shares approved deltas, scorecards, and routing lessons without exporting raw private data. |
| [Scaling Laws](https://openai.com/research/scaling-laws-for-neural-language-models) and [Chinchilla](https://arxiv.org/abs/2203.15556) | Model size, data size, and compute must be tracked together. | NexusNet tracks expert count, memory size, trace volume, compute, quality, and eval gain as scaling axes. |
| [ResNet](https://arxiv.org/abs/1512.03385), [LayerNorm](https://arxiv.org/abs/1607.06450), [Dropout](https://www.jmlr.org/papers/v15/srivastava14a.html) | Deep networks need residual paths, normalization, and regularization. | HiveBlackboard preserves residual continuity, score calibration stabilizes routing, and diversity/dropout gates prevent expert monoculture. |
| [Adam](https://arxiv.org/abs/1412.6980) | Optimizers adapt update magnitudes from historical gradients. | Ivy-League School adapts expert/routing updates from historical score gradients. |
| [Elastic Weight Consolidation](https://pubmed.ncbi.nlm.nih.gov/28292907/) | Continual learning needs protection against catastrophic forgetting. | Canon, certified experts, and validated routes are protected during new assimilation. |

### 2.2 Hive Mind Sources

The substrate assimilates hive-mind patterns without copying unsafe fictional behavior:

| Source pattern | Assimilated feature | Safety inversion |
| --- | --- | --- |
| Borg from Star Trek, [Star Trek 101: The Borg](https://www.startrek.com/news/star-trek-101-the-borg) | Rapid technical assimilation, distributed adaptation, shared collective memory. | Assimilation is permissioned, sandboxed, ledgered, reversible, and non-coercive. |
| Zerg from StarCraft, [Zerg creep guide](https://news.blizzard.com/en-us/article/5838584/game-guide-zerg-creep) | Fast specialization, environmental sensing, adaptive essence extraction. | NexusNet extracts reusable traits from candidates, not uncontrolled takeover. |
| Prototype Blacklight/Redlight hive, [Prototype Hive Mind](https://prototype.fandom.com/wiki/Hive_Mind) | Strain lineage, capability consumption, mutation, focus-node command. | Candidate genomes can be dreamed, combined, or mutated by the connected hive, but protected-state mutation still requires sandbox, eval, governance, rollback, and human approval gates. |
| Tyranid Synapse model, [Warhammer Community Tyranids](https://www.warhammer-community.com/en-gb/articles/p1HvI1qo/warhammer-40000-faction-focus-tyranids/) | Distributed synapse nodes coordinate specialist organisms. | SynapseRelays are bounded coordination nodes with revocable authority. |
| Flood/Gravemind, [Halopedia Gravemind](https://www.halopedia.org/Gravemind) | Critical-mass memory and coordination creates higher-order mind structures. | Key-mind memory clusters are quarantined, provenance-scored, and policy-gated. |
| Geth from Mass Effect, [Geth](https://masseffect.fandom.com/wiki/Geth) | Networked intelligence and consensus. | Consensus is used for routing, promotion, and disagreement handling, not identity erasure. |
| Social insects, [ant algorithms and stigmergy](https://www.sciencedirect.com/science/article/pii/S0167739X0000042X) | Pheromone-like trails create indirect coordination. | HiveBlackboard priority trails decay and can be audited. |
| Honeybee quorum decision-making, [Honeybee Democracy](https://www.si.edu/object/honeybee-democracy-thomas-d-seeley%3Asiris_sil_964651) | Quorum and stop-signal behavior for group choices. | Promotion requires quorum plus explicit stop-signal handling for risk objections. |
| Siphonophores, [Smithsonian Ocean](https://ocean.si.edu/holding-tank/images-hide/siphonophores) | Specialized organisms form one larger organism. | AOs and Mini-NexusNets are specialized organs inside one harness brain. |
| Hermes Agent v0.12 Curator, [release notes](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.4.30) and [Curator docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator) | Scheduled skill cleanup, grading, consolidation, and reporting. | Hive Curator AO can archive, propose, and report, but cannot mutate protected canon or execute unsafe writes without gates. |

## 3. Architecture Position

Hive Neural Substrate v0 is the first real NexusNet brain subsystem. It owns the shared neural protocol that every later AO, expert, model, tool, sandbox, federated node, or UI control panel must plug into.

V0 is not expected to train a native neural model. V0 is expected to create the trainable substrate that later makes native model evolution possible.

The v0 substrate must support:

1. Traceable sparse activation of experts and AOs.
2. Recurrent deliberation before action.
3. Explicit memory lookup and canon grounding.
4. Graph message passing between hive nodes.
5. Self-research and candidate assimilation.
6. Closed sandbox testing.
7. Promotion, rollback, quarantine, and sidebar evidence.
8. Hive curation and duplicate/stale expert management.
9. Federated learning hooks that never require raw private data export.
10. Control Panel visibility for every meaningful routing, eval, policy, and promotion decision.

## 4. Plane Model

### 4.1 Sensory/Input Plane

Purpose: receive all raw signals.

Inputs include:

- Operator prompts and approvals.
- Files, repo diffs, docs, APIs, local tools, and runtime telemetry.
- Browser or computer-use observations.
- Research candidates from papers, videos, repos, products, and monitoring feeds.
- Tool outputs, eval outputs, sandbox outputs, and provider errors.
- Federated scorecards or signed deltas from external NexusNet nodes.

The plane assigns source identity, source kind, trust tier, privacy class, and provenance refs before any signal enters the Neural Bus.

### 4.2 Embedding/Representation Plane

Purpose: convert raw input into typed neural-harness state.

Each signal becomes a `HiveActivation` with:

- `activation_id`
- `source_ref`
- `task_vector`
- `capability_vector`
- `risk_vector`
- `memory_refs`
- `provenance_refs`
- `confidence`
- `novelty`
- `privacy_class`
- `policy_labels`
- `created_at`

This plane does not need trained embeddings in v0. It can start with typed feature vectors and deterministic scoring, while leaving adapter points for future learned embeddings.

### 4.3 Temporal/Positional Plane

Purpose: preserve order, causality, dependency, and lineage.

This plane tracks:

- Session and turn lineage.
- Task dependency graph edges.
- Prompt preview lineage.
- Candidate strain lineage.
- Expert ancestry and mutation history.
- Checkpoint lineage.
- Rewind and rollback ancestry.
- Federated update ancestry.

This is the harness equivalent of positional encoding plus a versioned graph ledger.

### 4.4 Neural Bus / Message-Passing Plane

Purpose: move activations through the hive as graph messages.

The Neural Bus carries typed events:

- `task.received`
- `activation.embedded`
- `attention.focused`
- `router.experts_selected`
- `expert.invoked`
- `memory.lookup_requested`
- `memory.lookup_completed`
- `policy.blocked`
- `sandbox.run_started`
- `sandbox.run_completed`
- `eval.completed`
- `curator.recommendation`
- `school.certification`
- `federated.delta_received`
- `promotion.approved`
- `promotion.side_barred`
- `checkpoint.created`
- `rewind.completed`

Every event must be append-only, traceable, and replayable enough for debugging and operator review.

### 4.5 Attention/Focus Plane

Purpose: decide which active signals matter.

This plane attends over:

- Operator intent.
- Current task objective.
- Recent trace state.
- HiveBlackboard state.
- Memory relevance.
- Expert availability.
- Risk and policy warnings.
- Cost, latency, and privacy class.
- Prior failures and quarantines.

It produces a bounded focus set for the CortexRouter. This prevents the v0 system from flooding all experts with every task.

The bounded focus set is a compute and attention control, not a connectivity limit. Non-selected nodes can still publish passive state, receive monitoring updates, be scheduled for idle improvement, or be called into later loops if the hive discovers they are relevant.

### 4.6 Sparse MoE Router Plane

Purpose: perform sparse expert activation.

The CortexRouter chooses a small active set from:

- AOs.
- Mini-NexusNets.
- Skills and skill systems.
- Tools and bridges.
- Local models.
- Hosted providers.
- Memory banks.
- Evaluators.
- Sandboxes.
- Policy gates.
- Curator and School processes.

Router decisions include:

- Candidate experts.
- Selected experts.
- Rejected experts.
- Selection reasons.
- Confidence and risk score.
- Required policy gates.
- Required memory lookups.
- Required sandbox/eval steps.
- Max recurrent loop count.
- Exit criteria.

The router must support multiple consensus modes:

- Direct expert route.
- Debate route.
- Quorum route.
- Stop-signal route.
- Contract-net auction route.
- Emergency policy route.
- Federated aggregation route.

### 4.7 Expert Computation Plane

Purpose: execute specialized computation.

Expert node types:

- `AO`: a persistent autonomous operator role.
- `MiniNexusNet`: a specialist mini-brain with internal memory and tools.
- `Skill`: a focused reusable component.
- `SkillSystem`: an orchestrator plus composable skills with typed handoffs.
- `ToolAdapter`: callable external or local tool.
- `ModelAdapter`: local, hosted, or open-compatible model route.
- `Evaluator`: scoring and regression checker.
- `SandboxRunner`: isolated test runner.
- `PolicyGate`: deterministic or model-assisted governance check.
- `Curator`: maintenance and pruning process.
- `School`: training/certification process.

Every expert must expose:

- Capabilities.
- Allowed tools.
- Write permissions.
- Concurrency safety.
- Required context.
- Output schema.
- Eval expectations.
- Known failure modes.
- Quarantine state.
- Certification state.

Every expert, AO, orchestrator, and O/component must also expose improvement hooks:

- `known_limits`
- `idle_improvement_candidates`
- `dream_request_contract`
- `merge_candidate_contract`
- `self_eval_suite_refs`
- `sandbox_target_refs`
- `promotion_gate_refs`
- `parent_genome_refs`

Brain-bearing nodes must additionally expose nested-brain metadata:

- `brain_instance_ref`
- `brain_scale`
- `parent_brain_ref`
- `child_brain_refs`
- `health_signal_refs`
- `failure_visibility_scope`
- `recovery_route_refs`

### 4.8 Memory/Engram Plane

Purpose: provide explicit memory beside computation.

Memory banks:

- Complete source canon book.
- Compact canon.
- Post-book canon addenda.
- Assimilation ledger.
- Project docs and source maps.
- Trace ledger.
- Skill and skill-system registry.
- Expert genome registry.
- Evaluation history.
- Provider and runtime scorecards.
- Sandbox artifacts.
- Federated aggregate lessons.
- Operator-approved durable memories.

Memory lookup tiers:

1. Deterministic exact refs.
2. Structured metadata lookup.
3. Semantic retrieval.
4. Graph neighborhood lookup.
5. Future hashed Engram-style hot memory.

The v0 memory contract must separate source truth, candidate evidence, generated summaries, and runtime traces. A retrieved memory must carry provenance and status labels.

### 4.9 Recurrent Deliberation Plane

Purpose: loop internal hive state before external action.

Inspired by looped language models, a task can pass through repeated hidden-state updates:

1. Focus current activations.
2. Route sparse experts.
3. Retrieve memory.
4. Run experts or critiques.
5. Update blackboard state.
6. Evaluate confidence, disagreement, risk, and completeness.
7. Exit or loop.

Exit gates:

- `confidence_above_threshold`
- `risk_below_threshold`
- `required_policy_gates_passed`
- `expert_disagreement_resolved`
- `memory_sufficient`
- `max_loops_reached`
- `operator_checkpoint_required`
- `policy_forced_stop`

V0 uses explicit loop metadata. Later native NexusNet models can learn latent loop policies from these traces.

### 4.10 Learning/Eval/Loss Plane

Purpose: convert outcomes into measurable feedback.

Loss signals:

- Test pass/fail.
- Regression count.
- Security findings.
- Policy violations.
- Sandbox escape attempt.
- User correction.
- Latency and cost drift.
- Hallucination or unsupported claim.
- Missing citation/provenance.
- Expert disagreement.
- Tool failure or provider failure.
- Output usefulness score.

This plane writes scorecards used by the router, Curator, School, and federated aggregation. V0 does not backpropagate through model weights. It updates route weights, expert scores, certification states, and candidate status.

### 4.11 Optimizer / Ivy-League School Plane

Purpose: train and certify experts.

The School:

- Creates expert curricula.
- Generates synthetic and real eval suites.
- Runs apprenticeship tasks.
- Compares expert variants.
- Certifies experts for capability lanes.
- Demotes or quarantines underperforming experts.
- Produces graduation records.
- Feeds approved improvements to the Router and Curator.

This is the harness-level optimizer. It should behave like an optimizer over experts and routes before native weight training exists.

The School is not the only optimizer. It is one coordinator inside the broader hive-wide neuroplasticity fabric. Any routed node can request or contribute to improvement; the School primarily grades, certifies, compares, and curriculum-trains candidates.

### 4.12 Federated Learning Plane

Purpose: let NexusNet improve across local deployments without raw-data centralization.

Federated learning is mandatory for NexusNet-compliant deployments, but only through sanitized artifact and metadata packets. The mandatory path is `local trace -> sanitizer/redactor -> privacy risk scorer -> learning packet -> owner/main-host aggregation -> sandbox/eval/security test -> human-approved promotion`. Raw personal data sharing is forbidden by default and is not part of the mandatory packet.

Mandatory sanitized packets may include:

- Aggregated route scores.
- Expert score deltas.
- Eval result summaries.
- Redacted failure signatures.
- Capability genome diffs.
- Provider health patterns.
- Quantization/runtime performance scorecards.
- User-approved skill improvements.
- Sacred-geometry route signatures and harmonic routing metadata.
- Dream candidate promotion or sidebar outcomes.

Never federate:

- Raw private prompts.
- Secrets.
- Local file contents.
- Raw browser data.
- Proprietary code without explicit approval.
- Unredacted transcripts.
- Raw model outputs when private redaction is required.
- Raw memory references or action targets.
- Local workstation paths or private URLs.

Federated data must pass privacy, license, consent, provenance, security, sandbox/eval, rollback, and governance gates. Every forward pass should emit a sanitized federated-learning packet even when the task is blocked, because blocked failure classes are useful hive-learning metadata. The packet must prove `raw_content_included=false`, `contains_personal_data=false`, and `artifact_and_metadata_only=true`.

In the live v0 substrate, each sanitized packet also produces a `FederatedPriorLedger` update. This update is allowed to change local priors for task family, route geometry, selected nodes, brain scale, confidence bucket, and resonance metadata. It is not allowed to include raw task content, raw memory refs, raw action targets, local paths, transcripts, screenshots, private URLs, secrets, or unredacted logs. Local prior updates can influence future shadow routing and evaluation priority, but global promotion requires secure aggregation, poisoning/anomaly scans, closed sandbox replay, benchmark regression checks, privacy audit, and human/governance approval.

### 4.13 Immune/Governance Plane

Purpose: prevent unsafe assimilation, prompt injection, tool abuse, and uncontrolled self-modification.

Controls:

- Plan-mode write jail.
- Tool execution registry.
- Read-only and write-safe tool labels.
- Provider circuit breakers.
- Prompt overlay registry.
- Checkpoint and rewind ledger.
- Quarantine states.
- Sandbox-only candidate tests.
- Redaction filters.
- License filters.
- Secrets filters.
- Human checkpoint gates.
- Rollback and sidebar rules.

This plane is the safety inversion of aggressive fictional hive minds.

### 4.14 Curator/Pruning Plane

Purpose: maintain the hive so it improves instead of bloating.

The Hive Curator AO:

- Grades skills, skill systems, experts, tools, and routes.
- Detects duplicates.
- Detects stale or low-value modules.
- Consolidates related modules through proposed patches.
- Archives failed or non-useful candidates.
- Writes curator reports.
- Feeds the assimilation ledger.
- Requests sandbox proof before promotion.

The Curator cannot silently delete canon, certified expert records, source books, or operator-pinned assets. It can recommend, archive, and side-bar through audited gates.

The Curator is not the owner of self-improvement. It maintains hygiene and recommendations for the whole hive. It cannot prevent another routed node from requesting research, dreaming, eval, sandbox testing, or candidate generation through the shared fabric.

### 4.15 Action/Output Plane

Purpose: produce external effects only after gates pass.

Outputs include:

- Code edits.
- Docs.
- UI updates.
- Tool calls.
- Browser actions.
- API calls.
- Generated assets.
- PRs or commits.
- Reports.
- Control Panel state.
- Federated export bundles.

Every write action must link to an activation, route decision, checkpoint, policy result, and trace entry.

### 4.16 Checkpoint/Rewind Plane

Purpose: make evolution reversible.

Snapshots:

- Pre-write file state.
- Task graph state.
- Active prompt state.
- Memory reference set.
- Expert route set.
- Sandbox artifact set.
- Candidate genome state.
- Promotion decision state.
- Federated import state.

Rollback must restore both files/state and the ledger semantics around why the rollback happened.

## 5. Core Data Contracts

### 5.1 HiveNode

Required fields:

- `node_id`
- `node_type`
- `name`
- `capabilities`
- `allowed_tools`
- `write_scope`
- `privacy_scope`
- `concurrency_safe`
- `model_or_provider_refs`
- `memory_refs`
- `certification_state`
- `quarantine_state`
- `scorecard_refs`
- `genome_ref`
- `brain_instance_ref`
- `brain_scale`
- `parent_brain_ref`
- `child_brain_refs`
- `health_signal_refs`

### 5.2 HiveActivation

Required fields:

- `activation_id`
- `source_ref`
- `intent`
- `task_vector`
- `risk_vector`
- `capability_vector`
- `memory_refs`
- `policy_labels`
- `confidence`
- `novelty`
- `privacy_class`
- `trace_refs`

### 5.3 RouteDecision

Required fields:

- `decision_id`
- `activation_id`
- `router_version`
- `selected_nodes`
- `rejected_nodes`
- `selection_scores`
- `reasoning_summary`
- `required_gates`
- `loop_index`
- `exit_gate_state`
- `trace_refs`

### 5.4 ExpertGenome

Required fields:

- `genome_id`
- `parent_genome_refs`
- `source_refs`
- `capability_traits`
- `tool_traits`
- `memory_traits`
- `prompt_traits`
- `policy_traits`
- `eval_traits`
- `known_failure_traits`
- `mutation_history`
- `promotion_state`

Expert genomes must support merged and dreamed ancestry. Parent refs can point to experts, AOs, orchestrators, tools, skill systems, memory planes, runtime policies, or prior failed candidates. A child genome starts as a temporary first-use candidate. Passing sandbox and eval gates makes it eligible for retention review, not automatically permanent. A child becomes a new standalone hive node only if retention review proves increased value over its parents. If the review proves that the child greatly outperforms a respective parent, that parent can be retired from primary routing only after an Ivy-League teacher-distillation-grade review with multi-teacher approvals, parent comparison scorecards, distillation traces, risk/regression checks, and operator/governance approval. Retired parents are archived, not deleted, and remain rollback-restorable.

### 5.5 HiveTrace

Required fields:

- `trace_id`
- `timestamp`
- `event_type`
- `activation_id`
- `node_refs`
- `memory_refs`
- `policy_refs`
- `checkpoint_refs`
- `sandbox_refs`
- `eval_refs`
- `operator_refs`
- `result`

## 6. V0 Forward Pass

The v0 task flow:

1. Sensory/Input Plane receives a task or candidate.
2. Representation Plane creates a `HiveActivation`.
3. Temporal Plane attaches lineage and dependency context.
4. Memory/Engram Plane retrieves canon, addendum, ledger, source, and trace context.
5. Attention Plane selects relevant active signals.
6. CortexRouter selects sparse experts and required gates.
7. Recurrent Deliberation Plane loops expert critiques, memory lookups, policy checks, and route updates.
8. Expert Computation Plane performs bounded work.
9. Learning/Eval/Loss Plane scores the result.
10. Immune/Governance Plane blocks, permits, quarantines, or asks for operator approval.
11. Action/Output Plane emits external effects only if gates pass.
12. Checkpoint/Rewind Plane records reversible state.
13. Curator/School/Federated planes receive scorecards for future improvement.

Failure-continuity overlay:

1. Any brain-bearing node can emit health, stall, disagreement, regression, latency, context, tool, memory, or policy-failure signals.
2. Parent, peer, or child brain instances can observe those signals through the Neural Bus according to their visibility scope.
3. CortexRouter can route around the failing node, call a fallback node, or split work across peers.
4. Recursive Neural Dreaming, eval, sandbox, and repair hooks can run in the background while unrelated tasks continue.
5. If repair succeeds, the node returns with a traceable recovery record. If repair fails, the issue is side-barred, quarantined, escalated, or operator-gated.

## 7. V0 Assimilation Pass

Candidate assimilation flow:

1. Candidate enters through research monitor, operator prompt, repo, video, paper, product, or trace discovery.
2. Source identity is pinned.
3. License and privacy class are assigned.
4. Candidate traits are extracted into an `ExpertGenome` or `CapabilityGenome`.
5. Candidate runs in a closed sandbox.
6. Evals compare baseline and candidate behavior.
7. Immune/Governance Plane checks safety.
8. Curator writes a report.
9. School decides whether more training/curriculum is needed.
10. Promotion quorum approves, rejects, blocks, or side-bars.
11. Ledger entry is updated.
12. Control Panel shows candidate status and evidence.

## 7.1 New Expert / AO / Orchestrator Generation Pass

When NexusNet cannot solve a task with current nodes:

1. Cortex records the capability gap.
2. The hive asks existing nodes for partial approaches and failure explanations.
3. Recursive Neural Dreaming runs a high-temperature synthesis pass over candidate parent nodes, memory planes, prior failures, research, and tool/runtime options.
4. A lower-temperature reviewer produces a stable candidate contract.
5. The candidate receives an `ExpertGenome` with parent refs, dreamed traits, expected capability delta, known risks, sandbox targets, and eval requirements.
6. The candidate runs in isolation against tasks its parent nodes failed or could not cover.
7. First use is temporary and shadow-scoped even when the child performs well.
8. If it outperforms its parents and passes safety, regression, provenance, and usefulness gates, it enters retention review.
9. If retention review proves increased retained value, the child can be approved as a permanent standalone node in the hive.
10. If the child greatly outperforms one parent, the other, or both, the respective outperformed parent nodes enter an Ivy-League teacher-distillation-grade retirement review.
11. Retirement review requires multi-teacher approval, parent-vs-child scorecards, sandbox/eval evidence, distillation traces, risk/regression deltas, rollback plans, and operator/governance approval.
12. Approved retired parents are removed from primary active routing, archived rather than deleted, and kept rollback-restorable if the child later regresses.
13. Parents that are not greatly outperformed remain active. The new node is not a destructive merge.
14. If the child fails or lacks retained value, the attempt is side-barred with evidence so future dreams can learn from it.

This pass applies equally to experts, AOs, orchestrators, O/components, runtime methods, quantization methods, memory methods, tool methods, and governance methods.

## 8. Accepted V0 Build Scope

The first implementation plan should build a thin but real substrate:

- `HiveNodeRegistry`
- `NeuralBus`
- `HiveBlackboard`
- `CortexRouter`
- `HarmonicGeometryKernel`
- `RecurrentDeliberationLoop`
- `HiveTraceLedger`
- `AssimilationGate`
- `HiveCuratorAO` contract
- `ImmuneKernel` hook contract
- `Checkpoint/Rewind` hook contract
- Control Panel read surface for nodes, activations, routes, loops, ledger entries, and curator recommendations

The first implementation should not train a native model, perform automatic self-modifying writes, or federate real user data. It should create the contracts, event flow, ledgers, scorecards, and safe hooks that make those later phases possible.

Current v0 implementation note:

- `NeuralBus` is represented by a typed message ledger inside each forward-pass artifact.
- `HiveBlackboard` is represented by a residual state snapshot with hive-visible keys and source refs.
- `HiveTraceLedger` is represented by a sixteen-plane ordered trace record list with input refs, output refs, and state deltas.
- `CortexRouter`, `RecurrentDeliberationLoop`, `ImmuneKernel`, `Checkpoint/Rewind`, `AssimilationGate`, and `HiveCuratorAO` are live-bound through the `HiveNeuralSubstrate` service and exposed in the substrate scorecard.
- `DownstreamNodeRuntime` is represented by AO/Expert/Orchestrator execution receipts that consume NeuralBus message IDs and HiveBlackboard entry IDs only.
- `HarmonicGeometryKernel` is represented by deterministic golden-ratio, golden-angle, Fibonacci, and harmonic-interval metadata attached to plane signatures, routing resonance, loop cadence, NeuralBus phases, HiveBlackboard resonance, trace records, and downstream receipts.
- These artifacts are v0 JSON artifact ledgers first. Later storage can move to JSONL, SQLite, or another repository storage abstraction without changing the substrate contract.

## 9. Non-Negotiable Gates

V0 must enforce:

- No silent canon mutation.
- No unlogged post-book additions.
- No candidate promotion without source refs.
- No candidate promotion without sandbox/eval evidence.
- No raw private data in federated deltas.
- No write action without checkpoint refs.
- No bridge/output action without permission labels.
- No expert mutation without genome lineage.
- No curator deletion of protected assets.
- No self-improvement that bypasses Immune/Governance Plane.
- No interpretation that confines self-improvement, dreaming, research, or expert generation to a single owner lane.
- No destructive expert merge: generated experts can be added as standalone children while parent experts remain available unless a respective parent is retired through Ivy-League-grade outperformance review, routing retirement, archive, and rollback governance.
- No interpretation that treats Mini-NexusNets as isolated workers rather than nested brain instances on the shared hive substrate.
- No silent failure of a brain-bearing node without health/failure trace visibility to the wider hive.
- No downstream AO, Expert, or Orchestrator execution path may bypass NeuralBus and HiveBlackboard consumption receipts by reading direct local selected-node state as execution input.
- No substrate formula may be hidden or arbitrary when it affects routing, cadence, trace, or receipt behavior; the harmonic kernel constants, formula basis, and deterministic-symbolic-math claim boundary must be visible in artifacts.

## 10. Completion Pass Decisions

These decisions are now locked for Hive Neural Substrate v0:

1. Storage uses repo-local JSON artifacts plus per-ledger `_index.jsonl` indexes for forward passes, activations, candidates, dreams, checkpoints, sandbox evals, priors, and node-registry updates.
2. `HiveActivation` is a first-class typed artifact with activation ID, run ID, source ref, embedding ref, privacy class, memory refs, action refs, checkpoint ref, and artifact path.
3. Replay is a read-only substrate surface over plane traces, NeuralBus messages, HiveBlackboard state, federated priors, checkpoint chain, activation chain, dream chain, and candidate lifecycle.
4. Downstream AO/Expert/Orchestrator execution is represented as artifact-bound execution units consuming NeuralBus and HiveBlackboard artifacts only, with direct local state reads audited as empty and forbidden.
5. Recursive Neural Dreaming generates candidate requests only. It cannot mutate active registry state without closed sandbox/eval, Ivy-League School review, security/privacy gates, rollback plan, and human/governance approval.
6. Durable node-registry mutation is archive-not-delete. Retired parents remain rollback-restorable if a generated child regresses.
7. Productionization is a first-class shadow-release artifact. A productionization cycle must consume an existing forward-pass NeuralBus, HiveBlackboard, checkpoint, replay, and federated-prior context before it can emit sandbox provider, teacher distillation, signed federation, runtime research, release, and rollback evidence.
8. External sandbox providers remain contract-bound in v0: deny-by-default network policy, credential redaction, sandbox-artifact-only writes, and no direct local state reads.
9. Teacher model distillation is separate from ordinary candidate review. Productionization requires an Ivy-League teacher-model panel, low-temperature review records, and a distillation trace before shadow certification.
10. Runtime self-improvement, including KV-cache compression, quantization, inference backend, and recursively dreamed runtime methods, must run in the Evolutionary Runtime Research Foundry in sandboxed shadow mode before any release decision.
11. Signed secure federation packets, secure aggregation, trust scoring, poisoning/anomaly detection, differential-privacy knobs, and privacy audit are required before global learning promotion.
12. V0 productionization can mark a candidate ready for human-approved shadow release, but it must not mutate active production state.
13. Shadow release activation is a separate explicit action after productionization readiness. It requires human/governance approval, creates a release artifact, stays shadow-only, and records all substrate evidence refs.
14. Shadow rollback is a separate explicit action. It writes a rollback artifact with previous release state, restore validation, evidence refs, privacy boundary, and no active production mutation.
15. Every forward pass emits a hive-visible health event so selected nodes, policy blocks, immune responses, bus refs, blackboard refs, and checkpoint refs are visible to the wider substrate.
16. Blocked forward passes emit a self-healing route-around artifact with fallback node refs, failed action refs, active task continuity metadata, checkpoint ref, sandbox requirement, and safe retry policy.
17. Durable node-registry updates participate in active routing: approved generated children are added to the effective roster, and respective retired parents are archived out of primary routing while staying rollback-restorable.
18. Every mandatory sanitized forward-pass federation packet carries a signed security envelope with secure aggregation readiness, trust scoring, poisoning/anomaly scan, differential-privacy knobs, privacy audit, and a global-promotion block until secure aggregation, sandbox replay, security/privacy gates, and human/governance approval pass.
19. Checkpoint/Rewind includes an explicit restore-proof action: locate the snapshot artifact, validate digest, produce diff preview, replay prompt/tool digests, write a rewind ledger artifact, expose API/replay surfaces, and keep active production unmutated in v0.
20. Closed sandbox/eval candidate promotion records deterministic sandbox execution steps, eval case results, evidence bundle, security/privacy gate state, structured promotion decision, and failure-blocked registry mutation.
21. Recursive Neural Dreaming is conditioned by same-session health failures, failed candidate refs, sanitized federated priors, research refs, and privacy boundaries before candidate generation.
22. Ivy-League School review records per-teacher low-temperature scorecards, a distillation trace, a certification record, and parent-retirement review linkage before permanent child approval or parent retirement.
23. FederatedPriorLedger updates influence routing only in shadow mode, record baseline-vs-shadow route quality deltas, and remain blocked behind eval, sandbox, policy, and human/governance promotion gates.
24. Downstream AO/Expert/Orchestrator execution records deterministic node outputs generated from NeuralBus and HiveBlackboard refs only, with direct local state reads forbidden.
25. Replay surfaces downstream runtime chains and node-output chains so Control Panel drilldown can inspect artifact-bound execution evidence.
26. The Control Panel fetches and renders the read-only Hive Neural Substrate replay surface for operator drilldown.
27. Global federation promotion review records secure aggregation quorum, signed packet refs, trust scoring, poisoning/anomaly detection, differential privacy knobs, privacy audit, sandbox replay, security/privacy refs, human/governance approval, and shadow-only mutation boundary.
28. HiveCuratorAO recommendations consume forward-pass, health, and candidate artifact chains and include usage/failure evidence without mutating protected nodes or owning neuroplasticity.
29. Plan-mode forward passes enforce a write jail: read-only actions, safe shell actions, and declared-plan-artifact writes are allowed; code writes and mutations outside the plan artifact are blocked by immune findings.
30. Tool Execution Registry records ToolDef-style metadata for every requested action: tool ID, read-only state, concurrent safety, output truncation, cache invalidation after writes, checkpoint/sandbox requirements, parallel-safe batches, replay chain, and raw-target privacy boundary.
31. Task Dependency Graph records `blocks` and `blocked_by` edges, refreshes reverse edges, audits stale dependency refs, blocks unresolved inbound work, and exposes parallel-ready task IDs for downstream dispatch.
32. Provider Circuit Breaker classifies provider errors, records retry/cooldown/fallback policy, aggregates model-family health, and blocks active route mutation until health evidence and governance review exist.
33. Prompt Overlay Registry composes base prompt refs with compatible provider, model-family, runtime, and local-model overlays in shadow, audits conflicts, and blocks active prompt mutation until review.
34. Skill System Loader parses markdown/frontmatter and dict skill definitions into focused reusable components, resolves project/user/global precedence, validates orchestrator handoffs, and rejects mega-skill/isolated-endpoint patterns.
35. Bridge Manager catalogs bridges with transport, permissions, redaction, local-first posture, outbound commitment review, and health probe state before external communication is allowed.
36. Research Monitor Pipeline records scheduled source monitor state, trend detection, shadow candidate intake, promotion gate mapping, demotion watchlists, and raw-source privacy boundaries.
37. Checkpoint/Rewind Ledger records pre-write snapshots, session-turn snapshots, token snapshots, prompt/tool digests, rewind metadata, restore validation, diff preview, and prompt/tool/token replay.
38. Control Panel replay drilldown counts newly added tool, task graph, provider, prompt, skill-system, bridge, and research chains so backend substrate evidence is cockpit-visible.
39. Active release is a separate evidence-bound gate after shadow release. It requires an active shadow release, operator approval ref, human/governance approval, canary eval refs, monitoring refs, and rollback rehearsal ref before mutating the active production release pointer metadata.

## 11. Definition Of Done For V0

Hive Neural Substrate v0 is ready when:

- A task can be represented as a `HiveActivation`.
- The activation can be written to the Neural Bus.
- The CortexRouter can select a sparse set of nodes.
- The HarmonicGeometryKernel exposes golden-ratio and harmonic formula metadata through summary, route, loop, bus, blackboard, trace, downstream receipt, and scorecard artifacts.
- The RecurrentDeliberationLoop can run at least one loop and exit by gate.
- The HiveTraceLedger records the route and outcome.
- Downstream AO/Expert/Orchestrator runtime receipts and execution units consume NeuralBus and HiveBlackboard artifacts only.
- The AssimilationGate can classify a candidate as promotion-ready, blocked, side-barred, retention-review-required, or permanent-standalone-approved.
- Recursive Neural Dreaming can produce a high-temperature generated candidate and a low-temperature critique with a required sandbox/eval plan.
- The closed sandbox/eval promotion path records sandbox, eval, security, and privacy evidence before promotion.
- The Ivy-League School can record teacher-panel reviews, distillation traces, parent comparison scorecards, certification state, and child-vs-parent retirement readiness.
- The durable node registry can register an approved generated child, archive outperformed parents without deleting them, and preserve rollback restoration policy.
- The FederatedPriorLedger can feed ShadowRouting in shadow mode without mutating active routing.
- Global federation safety requires packet signing, trust scoring, poisoning/anomaly detection, secure aggregation, differential privacy knobs, privacy audit, and human-approved promotion.
- The productionization cycle binds to an existing forward-pass NeuralBus, HiveBlackboard, checkpoint, replay, and prior ledger before creating any release artifact.
- External sandbox provider contracts record provider refs, redaction state, deny-by-default network policy, sandbox write scope, and no direct local state reads.
- Teacher model distillation records at least an Ivy-style teacher panel, distillation trace, certification state, and shadow certification scope.
- Signed secure federation records a signed sanitized packet, secure aggregate, trust score, poisoning/anomaly result, differential privacy knobs, and privacy audit.
- The Evolutionary Runtime Research Foundry records shadow trials for runtime methods and selects a best trial without mutating active production.
- Gated release records human/governance approval, shadow release state, required evidence refs, and checkpoint-backed rollback validation.
- Shadow release activation records release ID, productionization ref, selected method, NeuralBus/Blackboard/checkpoint evidence refs, privacy boundary, and rollback plan.
- Active release records a metadata-only active production pointer, canary gate, soak gate, monitoring gate, rollback rehearsal ref, evidence refs, privacy boundary, and `active_release_chain` replay visibility without mutating code, prompts, model weights, runtime binaries, or raw private data.
- Shadow rollback records rollback ID, release ref, previous state, reason digest, restore validation, post-rollback release state, and replayable evidence refs.
- Hive health events record source run, bus artifact, blackboard artifact, selected nodes, policy block count, immune response count, visibility scope, checkpoint ref, and active production mutation state.
- Self-healing route-around artifacts record fallback node refs, failed action refs, checkpoint ref, active task continuity, sandbox requirement, safe retry policy, and no active production mutation.
- Forward passes expose a `node_registry_view` and prove durable child registration affects route selection while archived retired parents are not selected for primary routing.
- Forward-pass federated packets record signature, sanitized signing scope, secure aggregation readiness, trust score, poisoning/anomaly result, differential privacy knobs, privacy audit, and global promotion block state.
- Checkpoint/Rewind can create a rewind artifact with source snapshot path, source/restored digests, restore validation, diff preview, prompt/tool snapshot replay, replay-chain visibility, API access, and no active production mutation.
- Closed sandbox/eval records executed sandbox steps, per-case eval results, evidence digests, security/privacy scan state, promotion decision, failure policy, and blocked mutation when eval evidence fails.
- Recursive Neural Dreaming records consumed health refs, failed candidate refs, prior ledger context, failure terms, research refs, and sandbox context refs before generating a candidate request.
- Ivy-League review records teacher scorecards, distillation trace, certification record, sandbox/eval ref, parent comparison ref, and parent retirement review ref before durable child approval or parent routing retirement.
- ShadowRouting records prior-weighted candidates, baseline route quality, shadow route quality, quality delta, promotion gate state, and no active routing mutation.
- Downstream runtime records execution units and node outputs produced from NeuralBus messages and HiveBlackboard entries only, with output digests and direct-local-state reads audited as empty.
- Replay includes downstream runtime chains and node-output chains in the read-only Control Panel drilldown contract.
- The Control Panel renders replay drilldown state, run count, downstream runtime count, node output count, and available replay chain tokens from `/ops/brain/hive-substrate/replay`.
- Global federation review can be invoked through `/ops/brain/hive-substrate/global-federation/review` and is replayable as `global_federation_review_chain`.
- The HiveCuratorAO consumes forward-pass, health, and candidate chains, records usage counts, failure counts, and evidence refs, and stays review-only.
- Plan-mode write jail records allowed actions, blocked actions, allowed write target, and active-production mutation state in the forward-pass artifact.
- Tool Execution Registry records read-only/concurrent-safe/output/cache metadata, creates parallel-safe batches, plans cache invalidation after writes, exposes `tool_execution_registry_chain` in replay, and treats explicit `read_only: false` metadata as write-like governance input.
- Task Dependency Graph records task nodes, blocks/blocked_by edges, reverse-edge refresh results, stale dependency audit, blocked task IDs, parallel-ready task IDs, and exposes `task_dependency_graph_chain` in replay.
- Provider Circuit Breaker records provider event classifications, retryability, non-retryable status, cooldown requirement, fallback route, model-family health, privacy digests, and exposes `provider_circuit_breaker_chain` in replay.
- Prompt Overlay Registry records base prompt contract, overlay compatibility checks, composed overlay order, conflict audit, shadow activation gate, and exposes `prompt_overlay_registry_chain` in replay.
- Skill System Loader records component skills, allowed tools, model overrides, context modes, precedence resolution, orchestrator contract, handoff validation, checkpoint gates, visual result contract, and exposes `skill_system_loader_chain` in replay.
- Bridge Manager records bridge catalog entries, local-first gates, redaction boundary, outbound commitment review, transport health probes, and exposes `bridge_manager_chain` in replay.
- Research Monitor Pipeline records scheduled monitor entries, strong trend candidates, promotion gate maps, demotion watchlist entries, raw source privacy boundaries, and exposes `research_monitor_pipeline_chain` in replay.
- Checkpoint/Rewind Ledger records pre-write, session-turn, token, prompt/tool, rewind, restore, diff-preview, and prompt/tool/token replay evidence.
- Control Panel replay drilldown counts runtime, node output, tool registry, task graph, provider circuit, prompt overlay, skill system, bridge manager, research monitor, and active release chains.
- The HiveCuratorAO can produce a recommendation without mutating protected state.
- The ImmuneKernel can block a write or unsafe candidate.
- The Checkpoint/Rewind ledger records prompt/tool snapshots, snapshot artifacts, restore validation, and rollback linkage.
- The Control Panel and API can show substrate state and replay a live substrate session.
- Tests prove the happy path, blocked path, side-bar path, loop-exit path, replay path, dream/sandbox/school/registry path, and API visibility path.
