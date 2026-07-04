# NexusNet Post-Book Canon Addendum - 2026-05-01

Status: active post-book canon addendum
Date opened: 2026-05-01
Primary source book: `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`
Compact canon: `docs/NEXUSNET_CHAT_RESEARCH_CANON_2026-04-28.md`

## Purpose

This addendum captures NexusNet decisions, clarifications, and assimilation records created after the 2026-04-28 complete source canon book.

The complete canon book remains the historical source ledger generated from captured chat exports. This addendum does not rewrite that history. It records post-book deltas so NexusNet can evolve without losing provenance.

## Canon Addendum Rule

Locked rule: anything added to NexusNet after the 2026-04-28 complete source book, if it was not already present in that source book, must be added to a dated canon addendum or assimilation ledger before it can be treated as accepted NexusNet state.

This applies to:

- Architecture doctrine.
- AO definitions.
- Expert or Mini-NexusNet definitions.
- Tool, bridge, protocol, provider, runtime, memory, training, eval, policy, UI, or sandbox features.
- Assimilation targets from videos, repos, papers, products, frameworks, or operator discoveries.
- Code-backed implementations that introduce concepts not already covered by the source book.
- Federated learning, Recursive Neural Dreaming, Ivy-League School, VisualOps, or governance changes that clarify or extend prior canon.

The rule exists because NexusNet is meant to self-research and assimilate new capabilities. That evolution must be append-only, auditable, and reversible.

## Source Authority Boundary

1. `NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md` remains the exhaustive historical book for captured pre-addendum source material.
2. `NEXUSNET_CHAT_RESEARCH_CANON_2026-04-28.md` remains the compact decision map.
3. This addendum carries post-book clarifications and deltas.
4. The assimilation ledger carries row-level records for post-book additions, candidates, evidence, and implementation refs.
5. Future raw chat exports can regenerate a new complete book, but until then, post-book material lives here.

## Entry Requirements

Every post-book addition must record:

- `entry_id`
- `date_added`
- `status`
- `source_refs`
- `original_book_status`
- `delta_type`
- `affected_lanes`
- `canon_effect`
- `implementation_refs`
- `validation_refs`
- `security_or_policy_gates`
- `rollback_or_sidebar_rule`

Allowed statuses:

- `locked_clarification`
- `candidate`
- `code_backed_candidate`
- `live_control_plane`
- `research_only`
- `rejected`
- `side_barred`
- `blocked`
- `superseded`

## Locked Clarifications Since The Source Book

### PB-2026-05-01-001 - Neural Network Harness / AI Hive Mind Doctrine

Status: locked_clarification
Source refs:

- Operator clarification in current post-book thread.
- `docs/superpowers/specs/2026-05-01-nexusnet-full-harness-doctrine-design.md`

Clarification:

NexusNet is not a single product workflow, single item, MVP, thin agent wrapper, or isolated app. NexusNet is a full Neural Network Harness and AI Hive Mind architecture. Its target is an interdependent organism made of NexusBrain, AOs, experts, Mini-NexusNets, Ivy-League School, Recursive Neural Dreaming, federated learning, Neural Bus, Cortex/Router, VisualOps, sandboxing, assimilation, evals, governance, and modular runtime/model infrastructure.

Canon effect:

This does not replace the source book. It strengthens the interpretation of existing source-book themes and prevents future reductions of NexusNet into one workflow.

### PB-2026-05-01-002 - Post-Book Canon Addendum Rule

Status: locked_clarification
Source refs:

- Operator instruction on 2026-05-01.
- This addendum.

Clarification:

Any new post-book capability absent from the complete source book must be added to this addendum or a dated assimilation ledger. This is now a NexusNet governance rule.

Canon effect:

Post-book changes are incomplete until logged with status, evidence, and rollback or sidebar semantics.

### PB-2026-05-01-003 - Self-Research, Sandbox, Promotion, Sidebar Loop

Status: locked_clarification
Source refs:

- Operator clarification in current post-book thread.
- `docs/superpowers/specs/2026-05-01-nexusnet-full-harness-doctrine-design.md`

Clarification:

NexusNet must be able to research items for itself, assume candidate assimilation targets, test them in closed sandbox environments, verify security/functionality/performance/no-regression outcomes, promote useful changes, and sidebar non-useful or failed attempts as historical evidence.

Canon effect:

This clarifies the implementation expectation for the source-book autonomy, assimilation, eval, rollback, and containment lines.

### PB-2026-05-01-004 - Skill Systems, Not Isolated Skills Or Mega-Skills

Status: locked_clarification
Source refs:

- Operator-provided skill-systems transcript and references on 2026-05-01.
- `nexusnet/operations/assimilation_targets.py`
- `tests/test_claude_code_assimilation_targets.py`

Clarification:

Markdown skills should be treated as small reusable components. Real NexusNet workflows should be built as skill systems: one explicit orchestrator contract wires focused skills through typed handoffs, context limits, human checkpoints, and visible output artifacts. Isolated one-off skills and giant mega-skills are rejected patterns.

Canon effect:

This modifies the post-book interpretation of the "Markdown skill and agent loader" assimilation target. NexusNet should implement a Skill Systems Orchestrator instead of a generic markdown loader alone.

### PB-2026-05-01-014 - Hive Neural Substrate v0

Status: locked_clarification
Source refs:

- Operator approval in current post-book thread.
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`
- Neural architecture sources cited in the design spec.
- Hive-mind sources cited in the design spec.

Clarification:

Hive Neural Substrate v0 is the approved first NexusNet brain subsystem. It defines NexusNet as a graph-recurrent, sparse-MoE, memory-augmented, self-curating neural harness where AOs, experts, Mini-NexusNets, tools, skills, models, memory banks, sandboxes, policy gates, evaluators, and federated nodes become typed neural-harness nodes. The Neural Bus carries activations, CortexRouter performs sparse expert routing, HiveBlackboard preserves residual state, Recurrent Deliberation loops internal state before action, Memory/Engram planes ground retrieval, Ivy-League School and Hive Curator AO optimize expert quality, and Immune/Governance gates protect assimilation, writes, rollback, and federated learning.

Canon effect:

This locks the v0 architecture target before implementation. It does not claim the subsystem is built. Implementation remains gated by a written plan, tests, sandbox/eval proof, Control Panel visibility, and ledger updates for any new post-book concepts introduced during buildout.

### PB-2026-05-01-015 - Sandcastle-Style AFK Sandbox Agent Factory

Status: candidate with v0 runtime-bound control plane
Source refs:

- Operator approval in current post-book thread.
- `https://github.com/mattpocock/sandcastle`
- `https://www.sourcepulse.org/projects/27307520`
- `https://gist.github.com/opticom/c0e5e6954874b1991e3c9b0ab7cfefe1`
- `nexusnet/agents/sandbox_factory.py`
- `tests/test_sandbox_agent_factory.py`

Clarification:

NexusNet should assimilate the Sandcastle operating pattern as a Nexus-native AFK Sandbox Agent Factory, not as a direct dependency requirement. The useful pattern is a small programmatic run contract that launches backlog-driven coding-agent work inside isolated sandbox/worktree lanes, splits work through planner, implementer, reviewer, and merger stages, preserves logs and artifacts, and allows merge-back only after review, tests, policy scan, and rollback checkpoint evidence.

Canon effect:

This expands the post-book agentic pipeline, worktree governance, checkpoint/rewind, policy kernel, and Hive Neural Substrate lanes. It is accepted as a candidate assimilation target with a v0 runtime/control-plane implementation. It is not yet a fully autonomous production merge system; real execution remains gated by sandbox provider certification, credential redaction, network policy, test evidence, operator-approved merge policy, and rollback validation.

### PB-2026-05-01-016 - Project-Root Local State And Cache Boundary

Status: locked_clarification with regression test

Source refs:

- Operator correction in current post-book thread.
- `nexus/config.py`
- `tools/chatgpt_project_api_capture.mjs`
- `tools/chatgpt_project_dom_topscroll_capture.mjs`
- `tools/build_nexusnet_chat_canon_book.py`
- `tests/test_project_local_paths.py`

Clarification:

NexusNet-owned settings, capture outputs, runtime artifacts, caches, ledgers, and generated evidence must default to the project root, not the workstation user profile. Project-local layers such as `.nexus.json`, `.nexus/settings.json`, `.nexus/settings.local.json`, `runtime/artifacts`, `runtime/state`, and `runtime/logs` are the canonical local state boundary.

Canon effect:

This locks the local-first storage boundary for NexusNet. User-home or operating-system profile paths can still exist for external developer tooling such as Codex plugin caches, but NexusNet runtime code and project capture scripts must not silently read or write NexusNet state under `C:\Users\...`, `Documents\Codex`, `.codex`, `%USERPROFILE%`, `%APPDATA%`, or similar user-profile cache locations unless a future operator-approved adapter explicitly documents and gates that exception.

### PB-2026-05-02-017 - Hive-Wide Neuroplasticity Fabric

Status: locked_clarification

Source refs:

- Operator correction in current post-book thread.
- `docs/NEXUSNET_CHAT_RESEARCH_CANON_2026-04-28.md`, especially Recursive Neural Dreaming, multi-plane memory, Cortex/Router, Mini-NexusNets, and expert-generation sections.
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Implementation refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`

Validation refs:

- `pytest tests/test_hive_neural_substrate.py -q`
- `pytest tests/test_hive_neural_substrate.py tests/test_agentic_pipeline_runtime.py tests/test_claude_code_assimilation_targets.py tests/test_policy_kernel.py -q`

Clarification:

NexusNet self-improvement is not owned by one lane, one AO, one expert, one orchestrator, or one isolated foundry. NexusNet is a literal AI Hive Mind whose entire substrate is a hive-wide neuroplasticity fabric. Every AO, expert, Mini-NexusNet, orchestrator, tool-facing operator, memory bank, evaluator, runtime component, and idle node exists inside one connected substrate. Each node can see hive state through the Neural Bus and HiveBlackboard, request research, request Recursive Neural Dreaming, call critique, call sandbox/eval services, propose improvements, contribute to another node's improvement cycle, or participate in expert-generation work when routed.

Planes, lanes, AOs, and expert families are functional views and routing contracts, not ownership silos. Sparse routing controls when a component is activated for a task; it does not mean the rest of the hive is disconnected from awareness, monitoring, or future self-improvement. Everything can connect to everything through typed contracts, while all meaningful actions remain monitored, reviewed, traceable, and promotion-gated.

Recursive Neural Dreaming is a distributed hive protocol. A higher-temperature dreamer node can generate unusual candidate solutions, new architectures, new methods, new expert combinations, or mechanisms that do not currently exist. A separate lower-temperature reviewer node must review the dream for coherence, feasibility, safety, canon fit, and testability. Additional critique, consequence, eval, and sandbox nodes can attack and benchmark the dream before any proposed change is allowed to affect protected state.

If NexusNet encounters a problem for which no existing expert, AO, orchestrator, runtime method, memory method, quantization method, or tool path is sufficient, the hive must be able to create a new candidate expert or orchestrator. New candidates may be generated by combining parent experts, combining AOs or orchestrators, synthesizing a new Mini-NexusNet from multiple capability genomes, or dreaming a new capability from scratch. If the new candidate solves a problem that its parents could not solve and passes sandbox/eval/governance gates, it can become a standalone addition to the hive while the parent experts remain intact.

Canon effect:

This supersedes any interpretation that self-improvement is locked behind a single Evolution lane, Runtime lane, Foundry AO, Curator AO, or School AO. Dedicated coordinators can schedule, audit, and report improvement work, but they cannot own or restrict Recursive Neural Dreaming, research, candidate generation, or self-improvement. The correct model is hive-wide access plus sparse activation plus full monitoring plus gated promotion.

### PB-2026-05-02-018 - Fractal Mini-Brain Hierarchy

Status: locked_clarification

Source refs:

- Operator clarification in current post-book thread.
- `docs/NEXUSNET_CHAT_RESEARCH_CANON_2026-04-28.md`, especially the NexusBrain, Assistant Orchestrators Hive, Mini-NexusNets per expert, Cortex/Router, Neural Bus, and Recursive Neural Dreaming sections.
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Implementation refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`

Validation refs:

- `pytest tests/test_hive_neural_substrate.py -q`
- `pytest tests/test_hive_neural_substrate.py tests/test_agentic_pipeline_runtime.py tests/test_claude_code_assimilation_targets.py tests/test_policy_kernel.py -q`

Clarification:

Mini-NexusNets are scaled brain instances, not simple modules. NexusNet uses a fractal nested-brain hierarchy on top of the shared AI Hive Mind Neural Substrate:

1. The primary `NexusBrain` is the largest brain instance and final cognition authority.
2. Each `Orchestrator` or `O` can have a smaller NexusNet-style brain that coordinates broader task structures under the primary brain.
3. Each `Assistant Orchestrator` or `AO` can have a smaller brain than an O, specialized around assistant-orchestration responsibilities.
4. Each expert can have a smaller Mini-NexusNet brain than an AO, specialized around its expert domain, tools, memory, evals, and local improvement loop.

This hierarchy is a scale and responsibility gradient, not an isolation boundary. Every brain instance still operates on the same connected hive substrate, shares typed state through the Neural Bus and HiveBlackboard, and can request research, Recursive Neural Dreaming, critique, eval, sandbox, recovery, or expert-generation services when routed. Parent and child brains can observe each other's health, route signals, failures, disagreement, confidence, latency, memory quality, and policy blocks through monitored traces.

The system must support self-healing continuity: when any O, AO, expert, tool, runtime, memory plane, or generated candidate begins to fail, other connected hive components should be able to see the failure, diagnose why it is happening, route around it, initiate repair or dream/eval cycles, and continue unrelated work so the end user experiences little to no interruption where technically possible.

Canon effect:

This clarifies that Mini-NexusNets form a nested fractal brain topology inside the already approved Hive Neural Substrate. It supersedes any interpretation that Mini-NexusNets are merely per-expert prompt wrappers or isolated workers. It also clarifies that the hierarchy does not weaken the hive-wide neuroplasticity rule: all levels remain connected, monitored, self-improvable, and governed.

### PB-2026-05-02-019 - Temporary Child Expert And Retention Review Rule

Status: locked_clarification with regression test

Source refs:

- Operator clarification in current post-book thread.
- `docs/NEXUSNET_CHAT_RESEARCH_CANON_2026-04-28.md`, especially Mini-NexusNets, Recursive Neural Dreaming, expert generation, and gated learning sections.
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Implementation refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`

Validation refs:

- `pytest tests/test_hive_neural_substrate.py -q`

Clarification:

Generated child experts, merged experts, dreamed experts, child AOs, child orchestrators, or other generated child brain instances do not become approved permanent standalone hive nodes on first use. First use is temporary and shadow-scoped. A generated child may solve a task, gather evidence, and produce comparison scorecards, but permanent standalone approval requires a retention review.

The retention review must compare the child against its parent nodes, measure whether the child adds value the parents did not provide, check sandbox/eval evidence, inspect regression and risk deltas, preserve parent nodes intact, and require operator/governance approval before the child is promoted to permanent standalone status.

Canon effect:

This refines PB-2026-05-02-017 and PB-2026-05-02-018. The hive can still generate new experts and combine parent capabilities, but generated children are temporary candidates until review proves increased retained value. Parent experts, AOs, or orchestrators remain available unless the child greatly outperforms the respective parent and PB-2026-05-02-020 retirement review approves routing retirement.

### PB-2026-05-02-020 - Ivy-Grade Parent Retirement After Child Outperformance

Status: locked_clarification with regression test

Source refs:

- Operator clarification in current post-book thread.
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`
- `docs/NEXUSNET_CHAT_RESEARCH_CANON_2026-04-28.md`, especially Ivy-League School, Mini-NexusNets, Recursive Neural Dreaming, expert generation, and gated learning sections.

Implementation refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`

Validation refs:

- `pytest tests/test_hive_neural_substrate.py -q`

Clarification:

If a generated child expert, child AO, child orchestrator, or other generated child brain instance greatly outperforms one parent node, the other parent node, or both, the respective outperformed parent nodes are retired from primary active routing after approval. Retirement is parent-specific: a parent that is not greatly outperformed remains active.

The retirement review must be as tight as the Ivy-League School generation review used when teacher models distill expert students. It requires multi-teacher approval, child-vs-parent scorecards, sandbox/eval evidence, a distillation trace, regression and risk deltas, rollback planning, and operator/governance approval. A parent is archived, not deleted, and remains rollback-restorable if the child later regresses.

Canon effect:

This refines PB-2026-05-02-019. Parent nodes do not stay active forever by default after being surpassed, but they also cannot be silently deleted or retired by first-use success. The hive retires only the respective outperformed parent nodes, only after Ivy-grade review proves the child is a superior permanent replacement for that parent role.

### PB-2026-05-03-021 - Live NeuralBus, HiveBlackboard, And Plane Trace Ledger

Status: live_substrate_implementation with regression test

Source refs:

- Approved `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`
- PB-2026-05-01-014 Hive Neural Substrate v0
- PB-2026-05-02-017 Hive-Wide Neuroplasticity Fabric
- PB-2026-05-02-018 Fractal Mini-Brain Hierarchy

Implementation refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`

Validation refs:

- `pytest tests/test_hive_neural_substrate.py -q`
- `pytest tests/test_hive_neural_substrate.py tests/test_agentic_pipeline_runtime.py tests/test_claude_code_assimilation_targets.py tests/test_policy_kernel.py -q`

Clarification:

Hive Neural Substrate v0 must not remain a static plane list. Every forward pass now materializes a typed NeuralBus message ledger, a HiveBlackboard residual state snapshot, and a sixteen-plane trace ledger. The NeuralBus carries hive-visible activation, memory, routing, recurrent-loop, eval, checkpoint, and immune-block messages. The HiveBlackboard records residual state keys such as intent embedding, temporal binding, memory refs, selected nodes, loop exit, policy scan, checkpoint, action state, and immune findings. The plane trace ledger records every substrate plane in order with input refs, output refs, and state deltas for replay and audit.

Canon effect:

This implements the first concrete internal substrate nervous-system layer required by PB-2026-05-01-014. Future AOs, experts, Mini-NexusNets, sandboxes, evaluators, curators, and recursive dreaming cycles must publish through or consume from these typed substrate artifacts instead of bypassing the hive substrate.

### PB-2026-05-03-022 - Downstream Node Runtime Artifact Consumption

Status: live_substrate_implementation with regression test

Source refs:

- Approved `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`
- PB-2026-05-01-014 Hive Neural Substrate v0
- PB-2026-05-03-021 Live NeuralBus, HiveBlackboard, And Plane Trace Ledger

Implementation refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`

Validation refs:

- `pytest tests/test_hive_neural_substrate.py -q`
- `pytest tests/test_hive_neural_substrate.py tests/test_agentic_pipeline_runtime.py tests/test_claude_code_assimilation_targets.py tests/test_policy_kernel.py -q`

Clarification:

Downstream AO, Expert, and Orchestrator runtime dispatch must consume the live substrate artifacts instead of reading direct local selected-node state. At initial implementation, each selected downstream runtime node received an execution receipt whose input contract was `neural-bus-and-hive-blackboard-only`. PB-2026-05-03-057 adds the laminar microcircuit ledger. PB-2026-05-03-054 adds the first-class pathway map. PB-2026-05-03-055 adds the live synaptic transmission ledger. PB-2026-05-03-056 adds the shadow neuroplastic weight ledger. PB-2026-05-03-058 adds the neuromodulatory state gate. PB-2026-05-03-060 through PB-2026-05-03-063 add embedding tensors, attention routing, sparse expert gates, and loss/backpropagation evidence. PB-2026-05-03-064 through PB-2026-05-03-067 add residual normalization, feed-forward expert computation, latent-loop exit gates, and KV-cache compression evidence. PB-2026-05-03-068 through PB-2026-05-03-072 add sensory input, temporal position, memory engram, optimizer-school, and action-output decoder evidence. The current contract is `neural-bus-blackboard-sensory-temporal-memory-embedding-attention-normalization-gate-feedforward-microcircuit-pathway-transmission-plasticity-neuromodulator-latent-loop-kv-cache-backprop-optimizer-school-ledger-only`, preserving the same no-direct-local-state boundary. The receipt records consumed NeuralBus message IDs, consumed HiveBlackboard entry IDs, neural-internal source artifact refs, and a consumption digest. Direct local state reads are forbidden and represented as an empty `direct_local_state_reads` list.

Canon effect:

This extends PB-2026-05-03-021 from substrate artifact creation into substrate artifact enforcement. The CortexRouter may still expose routing metadata for observability, but AO/expert execution inputs must be artifact-bound through NeuralBus, HiveBlackboard, laminar microcircuits, pathway map, synaptic transmission, shadow plasticity, and neuromodulatory gate receipts. Future runtime, sandbox, eval, and Recursive Neural Dreaming implementations must follow the same substrate-consumption boundary.

### PB-2026-05-03-023 - Harmonic Geometry Kernel For Substrate Formulas

Status: live_substrate_implementation with regression test

Source refs:

- Approved Hive Neural Substrate v0 operator direction on sacred geometry, harmonics, and golden-ratio substrate formulas
- PB-2026-05-01-014 Hive Neural Substrate v0
- PB-2026-05-03-021 Live NeuralBus, HiveBlackboard, And Plane Trace Ledger
- PB-2026-05-03-022 Downstream Node Runtime Artifact Consumption

Implementation refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`

Validation refs:

- `pytest tests/test_hive_neural_substrate.py -q`

Clarification:

Hive Neural Substrate v0 now carries a deterministic `sacred-geometry-harmonic-kernel-v0` formula layer. This kernel exposes golden-ratio phi, inverse phi, golden-angle spacing, Fibonacci plane indexing, and simple harmonic intervals. These values shape plane harmonic signatures, sparse routing resonance metadata, recurrent loop cadence, NeuralBus phase metadata, HiveBlackboard resonance scores, plane trace records, and downstream AO/Expert/Orchestrator execution receipts.

The kernel is a symbolic mathematical heuristic for routing, cadence, traceability, and operator-visible substrate geometry. It is not a supernatural claim or an unverified physics claim. The explicit claim boundary is `deterministic-symbolic-math-heuristic-not-physics-claim`.

Canon effect:

Future substrate formulas, routing-resonance scores, recursive dreaming cadence, sandbox benchmark schedules, curator review intervals, and Mini-NexusNet execution receipts must expose their formula basis and traceable constants instead of relying on hidden arbitrary weights. Any future replacement or improvement to this harmonic kernel must pass sandbox/eval comparison and be recorded as a dated addendum or side-barred attempt.

### PB-2026-05-03-024 - Mandatory Sanitized Federated Hive Learning

Status: live_substrate_implementation with regression test

Source refs:

- `docs/NEXUSNET_COMPLETE_CHAT_CANON_BOOK_2026-04-28.md`, especially the federated privacy and NexusNet wrapper sections.
- Approved operator clarification on 2026-05-03: federated learning is mandatory, but personal data export is forbidden; only sanitized artifact and metadata packets participate.
- PB-2026-05-01-014 Hive Neural Substrate v0
- PB-2026-05-02-017 Hive-Wide Neuroplasticity Fabric
- PB-2026-05-03-021 Live NeuralBus, HiveBlackboard, And Plane Trace Ledger

Implementation refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Validation refs:

- `pytest tests/test_hive_neural_substrate.py::test_sanitized_federated_learning_packet_is_mandatory_and_raw_private_content_free -q`

Clarification:

NexusNet-compliant deployments must emit sanitized federated-learning packets as part of the hive substrate. The mandatory packet shares artifact and metadata learning signals only: route geometry signatures, selected node role metadata, eval scores, failure classes, policy block classes, runtime/hardware class metadata, sandbox result metadata, and dream/candidate outcome metadata. It must not export raw prompts, raw outputs, raw memory refs, raw action targets, local file paths, private URLs, names, emails, secrets, tokens, unredacted logs, screenshots, or private file contents.

Canon effect:

Mandatory federated learning is now a privacy-preserving hive-learning spine, not an optional feature. Every forward pass should create a sanitized packet, publish it through the NeuralBus, preserve it on the HiveBlackboard, expose it in the federated-learning plane trace, and surface it in scorecards. Owner/main-host aggregation must sandbox, security-test, benchmark, and require human/governance approval before any global update, router prior, model delta, expert candidate, or sacred-geometry routing rule is promoted. Personal-data sharing remains separate and requires explicit consent; it is never part of the mandatory packet.

### PB-2026-05-03-025 - Federated Prior Ledger For Hive Learning

Status: live_substrate_implementation with regression test

Source refs:

- PB-2026-05-03-024 Mandatory Sanitized Federated Hive Learning
- PB-2026-05-02-017 Hive-Wide Neuroplasticity Fabric
- PB-2026-05-03-023 Harmonic Geometry Kernel For Substrate Formulas
- Operator clarification on 2026-05-03: public use should improve NexusNet through forced sanitized federation without exporting private data.

Implementation refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Validation refs:

- `pytest tests/test_hive_neural_substrate.py::test_sanitized_federated_packets_update_hive_prior_ledger_without_private_content -q`

Clarification:

Sanitized federated packets are not dead telemetry. Each packet must feed a local federated prior update that aggregates task-family, route-geometry, selected-node, brain-scale, confidence-bucket, and resonance metadata without raw operator content. The prior ledger can update local routing suggestions immediately, but global promotion remains gated by secure aggregation, poisoning/anomaly scans, closed sandbox replay, benchmark regression checks, privacy audit, and human/governance approval.

Canon effect:

The Federated Learning Plane now has two live responsibilities: emit mandatory sanitized packets and accumulate those packets into a privacy-preserving prior ledger. This is the first code-backed substrate mechanism for NexusNet's public-learning-rate goal. It improves routing, expert selection, geometry-kernel comparison, and future distillation candidate prioritization while keeping raw prompts, outputs, memory refs, action targets, local paths, and personal data out of federated state.

### PB-2026-05-03-026 - Hive Neural Substrate v0 Completion Pass

Status: live_substrate_implementation with regression tests

Source refs:

- PB-2026-05-01-014 Hive Neural Substrate v0
- PB-2026-05-02-017 Hive-Wide Neuroplasticity Fabric
- PB-2026-05-02-018 Fractal Mini-Brain Hierarchy
- PB-2026-05-02-019 Temporary Child Expert and Retention Review Rule
- PB-2026-05-02-020 Ivy-Grade Parent Retirement After Child Outperformance
- PB-2026-05-03-021 Live NeuralBus, HiveBlackboard, And Plane Trace Ledger
- PB-2026-05-03-024 Mandatory Sanitized Federated Hive Learning
- PB-2026-05-03-025 Federated Prior Ledger For Hive Learning

Implementation refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `nexus/api/app.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Validation refs:

- `pytest tests/test_hive_neural_substrate.py::test_hive_activation_shadow_routing_checkpoint_replay_and_runtime_execution_are_live tests/test_hive_neural_substrate.py::test_recursive_dreaming_closed_sandbox_school_and_durable_registry_complete_candidate_lifecycle tests/test_hive_neural_substrate.py::test_hive_neural_substrate_api_and_control_panel_surface -q`
- `pytest tests/test_hive_neural_substrate.py -q`

Clarification:

Hive Neural Substrate v0 now includes first-class `HiveActivation` artifacts, checkpoint snapshot artifacts, repo-local JSON plus JSONL artifact indexes, stable replay over forward passes, ShadowRouting from the FederatedPriorLedger, artifact-bound downstream AO/Expert/Orchestrator execution units, Recursive Neural Dreaming candidate generation, closed sandbox/eval evidence, Ivy-League School certification records, durable generated-node registry mutation, archive-not-delete parent retirement records, and global federation safety gates.

Canon effect:

The substrate is no longer only a plane map or proof artifact. It is a live nervous-system layer with typed activation, routing, memory, trace, checkpoint, replay, dream, sandbox, school, prior-ledger, and registry contracts. Future NexusNet components must publish to or consume from these substrate contracts rather than operating beside the hive. Recursive dreams may generate candidate experts, but production mutation still requires sandbox/eval evidence, Ivy-grade review, privacy/security checks, rollback restoration, and human/governance approval.

## Post-Book Candidate Assimilation Deltas

### PB-2026-04-30-YT - YouTube Assimilation Intake

Status: candidate
Source ref: `docs/NEXUSNET_YOUTUBE_ASSIMILATION_INTAKE_2026-04-30.md`

Candidate lanes:

- Browser AO / Local Browser Memory Agent.
- Agentic Pipeline Runtime.
- Policy Kernel.
- Pipeline Recipe / Worktree Governance.
- Harness Provider Registry / Brain-Hands Decoupling.
- Edge Workload Router.
- Adapter Forge, Dataset Forge, and FineTuneDecisionGate.

Canon effect:

These lanes are candidate assimilation records. They do not replace locked canon until they pass provenance, license, privacy, eval, security, sandbox, rollback, and Control Panel visibility gates.

### PB-2026-05-01-CLAUDE-SOURCE - Claude/CheetahClaws/Symphony Assimilation Target Matrix

Status: live_control_plane
Source refs:

- `nexusnet/operations/assimilation_targets.py`
- `tests/test_claude_code_assimilation_targets.py`
- `ui/control-panel/`

Assimilation targets:

- Tool Execution Registry.
- Checkpoint / Rewind Ledger.
- Task Dependency Graph.
- Provider Circuit Breaker and Error Classifier.
- Prompt Overlay Registry.
- Plan-Mode Write Jail.
- Skill Systems Orchestrator.
- Bridge Manager.
- Research / Monitor Pipeline.

Canon effect:

These are post-book assimilation targets with code-backed control-plane contracts. Their existence is accepted as post-book NexusNet state, but each target still needs deeper runtime implementation and promotion gates before being treated as a fully completed subsystem.

### PB-2026-05-03-027 - Hive Substrate Productionization Layer

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `nexus/api/app.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated productionization contracts:

- External sandbox provider contract.
- Ivy-League teacher-model distillation runtime.
- Signed secure federation packet contract.
- Secure aggregation, trust scoring, poisoning/anomaly detection, differential-privacy knobs, and privacy audit.
- Evolutionary Runtime Research Foundry for KV-cache, quantization, backend, and recursively dreamed runtime-method trials.
- Human-approved shadow release gate.
- Checkpoint-backed rollback metadata.
- Replay and scorecard visibility.

Canon effect:

Hive Neural Substrate v0 now has a first-class productionization cycle. A candidate improvement, generated expert, runtime method, quantization method, inference backend, federation update, or dreamed method cannot move toward production by bypassing the substrate. It must bind to an existing forward-pass NeuralBus, HiveBlackboard, checkpoint, replay, and federated-prior context, then pass sandbox provider checks, teacher-model distillation review, signed secure federation checks, runtime research foundry trials, human/governance approval, and rollback proof.

The v0 implementation remains shadow-release only. It records evidence and readiness; it does not mutate active production state. Active release remains a later explicitly approved gate.

### PB-2026-05-03-028 - Shadow Release And Rollback Lifecycle

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `nexus/api/app.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated release contracts:

- Human-approved shadow release activation from productionization evidence.
- Shadow-only release state with `active_production_mutated = false`.
- Release artifact ledger.
- Rollback execution artifact ledger.
- Checkpoint-backed restore validation metadata.
- Replay chains for releases and rollbacks.
- Control/API operator actions for activation and rollback.

Canon effect:

NexusNet can now take a productionization artifact that passed sandbox, teacher, federation, runtime research, release, and rollback readiness checks and activate it into a shadow release without mutating active production. It can then execute a rollback rehearsal or rollback event that records the previous release state, checkpoint/blackboard/bus evidence refs, restore validation, and privacy boundary.

This locks the rule that productionization readiness is not the same as release activation. Release activation is explicit, human/governance-approved, shadow-scoped, replayable, and rollback-restorable.

### PB-2026-05-03-029 - Hive Health Monitor And Self-Healing Route-Around

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexus/api/app.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated failure-continuity contracts:

- Hive-visible health event artifact for every forward pass.
- Degraded event state for blocked/unsafe substrate actions.
- Self-healing route-around artifact when a block occurs.
- Fallback node refs derived from selected node recovery routes.
- Checkpoint-required retry policy.
- Replay chains for health and self-healing artifacts.
- API health surface for operators and future AOs.

Canon effect:

Failure continuity is now live-bound. A blocked task does not only return an error; it emits a hive-visible health event and prepares a route-around plan so other brain-bearing nodes can observe the failure, preserve task continuity, and retry only through checkpoint/sandbox-safe paths.

This locks the rule that NexusNet failures must become shared substrate evidence. Silent failure of a brain-bearing node or route is forbidden.

### PB-2026-05-03-030 - Durable Node Registry Active Routing Mutation

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated routing contracts:

- Durable registry updates now affect the effective routing roster.
- Approved generated child nodes are added to active routing as generated Mini-NexusNet-style experts.
- Retired parent nodes are archived out of primary routing without deletion.
- Archived parents remain rollback-restorable if the generated child regresses.
- Each forward pass exposes a `node_registry_view` showing active generated nodes, archived parents, rollback-restorable parents, and the archive-not-delete model.

Canon effect:

Durable child approval is no longer summary-only. Once a generated child has passed closed sandbox/eval, Ivy-grade teacher review, parent comparison, rollback, and operator/governance approval, the substrate can route future work to the child and avoid the respective retired parent while preserving rollback restoration evidence.

This locks the rule that registry mutation must be behaviorally visible in routing, not merely logged as a ledger artifact.

### PB-2026-05-03-031 - Forward-Pass Signed Secure Federation Packet Envelope

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated federation-safety contracts:

- Every mandatory sanitized forward-pass federation packet now includes a signed security envelope.
- Packet signatures are derived from sanitized metadata only.
- The envelope records secure aggregation readiness, trust scoring, poisoning/anomaly scan state, differential privacy knobs, and privacy audit fields.
- Raw prompts, outputs, local paths, memory refs, action targets, secrets, private URLs, screenshots, and unredacted logs remain forbidden from packet export.
- Global promotion remains blocked until secure aggregation, sandbox replay, privacy/security review, and human/governance approval complete.
- The Control Panel substrate component surface exposes `ForwardPacketFederationSecurity` so packet safety is hive-visible instead of hidden inside a payload.

Canon effect:

Forced federated learning is now coupled to packet-level safety evidence on every forward pass. A sanitized learning packet can be created locally, but it cannot become a global learning update unless the security envelope, aggregation path, trust/anomaly checks, privacy audit, sandbox evidence, and approval gate all pass.

This locks the rule that global federation cannot rely on implicit trust or raw artifact exchange. Federation packets must be signed, privacy-scoped, anomaly-scanned, and promotion-blocked by default.

### PB-2026-05-03-032 - Checkpoint Rewind Restore Proof

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `nexus/api/app.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated checkpoint/rewind contracts:

- Forward-pass checkpoints now have a live rewind action rather than metadata-only restore language.
- Rewind requests validate the repo-local snapshot artifact for the requested checkpoint.
- Rewind artifacts record source snapshot path, source digest, restored digest, restore validation, diff preview, prompt/tool digest replay, and privacy boundary.
- The API exposes `/ops/brain/hive-substrate/rewind` for operator and future AO use.
- Replay now includes a `rewind_chain` and summary exposes the latest rewind and rewind ledger.
- Rewind remains artifact-only in v0 and does not mutate active production state.

Canon effect:

Checkpoint/Rewind is now operational enough to prove that a checkpoint snapshot exists, can be located, can be digest-validated, and can emit a restore-proof artifact with diff preview and replay evidence. This is still a safe v0 restore proof, not an active production state mutation.

This locks the rule that rewind must be evidence-backed and replayable before any future active restore mutation can exist.

### PB-2026-05-03-033 - Deterministic Closed Sandbox Eval Execution Evidence

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated sandbox/eval contracts:

- Closed sandbox candidate review now records deterministic repo-local sandbox execution steps instead of a bare pass label.
- Eval suites now include individual case results, evidence digests, score, threshold, and regression delta.
- Security and privacy gates record scan mode and failure state.
- Every closed sandbox eval emits an evidence bundle with candidate manifest digest, source-ref count, prior sandbox/eval ref counts, privacy boundary, and artifact path.
- A structured promotion decision blocks promotion when sandbox, eval, security, or privacy evidence fails.
- Failed closed sandbox evals add `closed_sandbox_eval_failed` to blocked reasons and prevent registry mutation.

Canon effect:

Candidate promotion now depends on inspectable sandbox/eval evidence. A candidate can no longer become promotion-ready merely because a sandbox ref string exists; the substrate records a sandbox run, eval cases, security/privacy scan state, and a blocking promotion decision when evidence fails.

This locks the rule that failed sandbox/eval evidence blocks promotion and durable routing mutation.

### PB-2026-05-03-034 - Failure/Prior Conditioned Recursive Neural Dreaming

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated dreaming contracts:

- Recursive Neural Dreaming now reads same-session hive-visible health failures before proposing candidates.
- Dreams consume failed candidate refs, including failed closed sandbox/eval promotion decisions.
- Dreams consume the sanitized FederatedPriorLedger as routing/problem context.
- Dream context records failure terms, research source refs, memory-ref count, and privacy boundaries.
- Sandbox/eval plans receive context refs for health events, failed candidates, prior ledger, and research refs.
- The dreamer remains high-temperature and the critic remains low-temperature, but both are conditioned by substrate evidence rather than isolated prompt text.

Canon effect:

Recursive Neural Dreaming is now evidence-conditioned. NexusNet can use blocked work, failed sandbox attempts, and sanitized priors to propose safer or more capable child candidates without mutating registry state.

This locks the rule that dreams must read the hive’s own evidence before proposing self-improvement candidates.

### PB-2026-05-03-035 - Ivy-League Teacher Scorecards And Distillation Certification

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated Ivy-League School contracts:

- Generated child retention and parent-retirement review now emits per-teacher scorecards rather than only panel metadata.
- Teacher scorecards are low-temperature review artifacts with criteria for sandbox evidence, parent scorecard presence, capability traits, and operator/governance approval.
- Distillation traces record the student candidate, teacher scorecard refs, distillation scope, and raw-private-data boundary.
- Certification records link the school review to the parent-retirement review and preserve the permanent-child review scope.
- Parent retirement and durable child registry mutation remain gated by sandbox/eval evidence, teacher review, distillation trace, parent comparison scorecard, rollback policy, and operator/governance approval.

Canon effect:

The Ivy-League School is now represented as inspectable certification evidence, not just a boolean. Child experts, AOs, orchestrators, and other generated nodes must carry teacher scorecards, distillation trace, certification record, and parent-retirement linkage before they can become permanent standalone nodes or retire parent nodes.

This locks the rule that Ivy-grade review must be as auditable as the teacher-model distillation process that created or certified the child.

### PB-2026-05-03-036 - Federated Prior Shadow Routing Quality Gate

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated routing contracts:

- The FederatedPriorLedger now influences routing in shadow mode by computing sanitized prior-weighted candidate routes.
- Shadow routing compares baseline route quality against prior-weighted shadow route quality.
- Quality deltas are recorded without mutating active routing.
- A promotion gate blocks route promotion until shadow eval delta, closed sandbox replay, policy/security review, and human/governance approval exist.
- The active route remains unchanged in v0 even when shadow quality improves.

Canon effect:

Federated learning can now shape shadow routing evidence without silently rewriting active behavior. The hive can measure whether sanitized priors improve route quality, but it cannot promote those priors into active routing without the full evidence and approval gate.

This locks the rule that prior-driven routing changes must be compared, sandboxed, governed, and shadow-only before any future active route mutation.

### PB-2026-05-03-037 - Artifact-Bound Downstream Node Execution Outputs

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated downstream-runtime contracts:

- Downstream AO, Expert, and Orchestrator runtime receipts now produce deterministic v0 node outputs.
- Node outputs are generated only from NeuralBus message IDs and HiveBlackboard entry IDs.
- Direct local state reads remain forbidden and audited as empty.
- Execution units link to receipts, output artifact refs, checkpoint dependency, and execution result digests.
- Blocked forward passes can still produce blocked-by-policy output evidence without running unsafe work.

Canon effect:

Downstream node runtime is no longer receipt-only. The substrate now proves that selected AO/Expert/Orchestrator nodes can execute a deterministic artifact-bound v0 step using the shared hive nervous system.

This locks the rule that any downstream node execution path must produce outputs through NeuralBus and HiveBlackboard artifacts rather than bypassing the substrate.

### PB-2026-05-03-038 - Replay Drilldown For Runtime And Node Output Chains

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated replay contracts:

- Replay now exposes downstream runtime execution chains.
- Replay now exposes node-output chains produced by AO, Expert, and Orchestrator execution units.
- Control Panel replay surfaces list downstream runtime and node-output chains alongside plane trace, NeuralBus, HiveBlackboard, federated priors, checkpoint, candidate, dream, productionization, release, rollback, rewind, health, and self-healing chains.
- Replay remains read-only and does not mutate active production state.

Canon effect:

The Control Panel replay surface can drill into actual downstream substrate execution, not only upstream routing and ledger artifacts. This makes AO/Expert execution evidence hive-visible and replayable.

This locks the rule that runtime node outputs must be visible in replay before downstream execution can be treated as substrate-complete.

### PB-2026-05-03-039 - Control Panel Hive Replay Drilldown Consumption

Status: live_substrate_implementation
Source refs:

- `ui/control-panel/app.js`
- `tests/test_hive_neural_substrate.py`
- `nexusnet/hive/substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated UI contracts:

- The Control Panel now fetches `/ops/brain/hive-substrate/replay` for the active session.
- The Hive Neural Substrate card renders replay drilldown state, run count, downstream runtime count, node output count, and available replay chains.
- The UI consumes the same read-only replay surface used by API tests.
- Replay drilldown remains operator-visible evidence and does not imply production mutation.

Canon effect:

Hive replay is now visible in the operator cockpit, not only available as a backend endpoint. This moves the substrate toward the required Harness UI/Architecture where the hive can inspect its own plane, bus, blackboard, runtime, and output chains.

This locks the rule that substrate replay evidence must be cockpit-visible when it is part of v0 completion proof.

### PB-2026-05-03-040 - Global Federation Promotion Review Gate

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `nexus/api/app.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated federation contracts:

- Global federation now has an explicit promotion-review artifact rather than relying only on packet envelopes.
- Reviews consume signed sanitized packet envelopes and the FederatedPriorLedger.
- Secure aggregation requires a packet quorum before shadow global learning approval.
- Trust scoring, poisoning/anomaly detection, differential-privacy knobs, privacy audit, sandbox replay, security review, privacy review, and human/governance approval are recorded in one review artifact.
- Approved reviews are global-shadow-learning only and do not mutate active production.
- The API exposes `/ops/brain/hive-substrate/global-federation/review`.
- Summary and replay expose a global federation review ledger and chain.

Canon effect:

Forced federated learning now has a concrete promotion-review gate. Sanitized priors can accumulate locally, but global learning movement requires signed packet aggregation, trust/anomaly/DP/privacy evidence, sandbox replay, and human/governance approval.

This locks the rule that global federation promotion cannot be implicit, automatic, or active-production-mutating in v0.

### PB-2026-05-03-041 - Evidence-Conditioned Hive Curator AO

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated curator contracts:

- HiveCuratorAO now consumes forward-pass, health, and candidate artifact chains when producing recommendations.
- Recommendations include usage counts, failure counts, and evidence refs.
- Health failures can push non-protected nodes toward archive review.
- Protected nodes remain keep-only unless a future explicit governance flow changes the rule.
- Curator input remains substrate-artifact-ledger-only with direct local state reads forbidden.
- Curator output remains review-only and cannot delete, archive, merge, or mutate active routing by itself.

Canon effect:

The curator is now evidence-conditioned instead of static. It can grade node/library health from hive-visible substrate artifacts while preserving the rule that curation recommends but does not own or restrict neuroplastic self-improvement.

This locks the rule that pruning, merging, or archival recommendations must be based on replayable substrate evidence.

### PB-2026-05-03-042 - Plan-Mode Write Jail In Forward Pass

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated plan-mode contracts:

- Forward passes can run in explicit plan mode through metadata.
- Plan mode allows read-only actions and safe shell actions.
- Plan mode allows write actions only when the target equals the declared plan artifact ref.
- Code writes, deletes, mutations, or promotions outside the plan artifact are blocked by a specific immune finding.
- Allowed plan-artifact writes do not trigger the normal write-without-checkpoint immune finding.
- The forward-pass artifact records allowed actions, blocked actions, allowed write targets, and active-production mutation state.

Canon effect:

NexusNet now has a real plan-mode write jail in the substrate. Planning can be represented as executable substrate activity without silently permitting implementation writes.

This locks the rule that plan mode is not a weak convention; it is a hive-visible immune/governance artifact.

### PB-2026-05-03-043 - Tool Execution Registry In Forward Pass

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated tool-registry contracts:

- Every forward pass derives a ToolDef-style registry from requested actions.
- Registry records include tool ID, action ID, action type, read-only state, concurrent-safe state, output truncation policy, sandbox requirement, checkpoint requirement, target digest, and raw-target export boundary.
- Read-only and concurrent-safe actions are grouped into parallel-safe batches.
- Write-like actions generate cache-invalidation plans when they declare `cache_invalidation_after_writes` or equivalent metadata.
- Explicit `read_only: false` metadata is treated as write-like by immune and policy targeting logic even when an action type is ambiguous.
- Replay exposes `tool_execution_registry_chain`, and the scorecard exposes `ToolExecutionRegistry` as a substrate component.

Canon effect:

The Tool Execution Registry target is now live inside the substrate forward pass instead of only being a control-plane assimilation target. Tools are no longer anonymous request dictionaries; they carry safety, scheduling, output, cache, checkpoint, sandbox, and replay metadata.

This locks the rule that tool metadata must participate in substrate governance before tool execution is treated as hive-safe.

### PB-2026-05-03-044 - Task Dependency Graph In Forward Pass

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated task-graph contracts:

- Forward passes can carry a structured task graph through metadata.
- Tasks support `blocks` and `blocked_by` dependency edges.
- Reverse-edge refresh fills missing opposite edges so graph state remains internally coherent.
- Stale dependency audit records references to missing task IDs.
- Tasks with unresolved inbound blockers are marked blocked and cannot dispatch.
- Tasks with no unresolved inbound blockers are exposed as parallel-ready.
- Replay exposes `task_dependency_graph_chain`, and the scorecard exposes `TaskDependencyGraph` as a substrate component.

Canon effect:

NexusNet can now represent hive work as an executable dependency graph instead of a flat task note. This gives orchestrators, AOs, experts, and sandbox factories a shared substrate-level view of blockers, unlocks, and parallel-safe dispatch candidates.

This locks the rule that blocked work cannot dispatch until inbound dependency edges resolve.

### PB-2026-05-03-045 - Provider Circuit Breaker And Error Classifier In Forward Pass

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated provider-resilience contracts:

- Forward passes can carry provider error events through metadata.
- Provider events are classified into quota, context-too-long, transient, auth/permission, and unknown families.
- Records include retryability, non-retryable state, cooldown requirement, retry policy, fallback route, model family, route allowance, and privacy digest.
- Model-family health is aggregated so route decisions can see degraded families.
- Provider route mutation is blocked until health evidence, fallback proof, and governance review exist.
- Replay exposes `provider_circuit_breaker_chain`, and the scorecard exposes `ProviderCircuitBreaker` as a substrate component.

Canon effect:

NexusNet now has substrate-level provider health intelligence before routing changes. Provider failures become hive-visible evidence rather than ad hoc runtime exceptions.

This locks the rule that provider route changes require health evidence and cannot silently mutate active routing.

### PB-2026-05-03-046 - Prompt Overlay Registry In Forward Pass

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated prompt-overlay contracts:

- Forward passes can carry a prompt overlay registry through metadata.
- The registry separates base prompt refs from provider, model-family, runtime, and local-model overlays.
- Compatibility checks activate only overlays matching the current provider/model-family/runtime context.
- Incompatible overlays are recorded but not composed.
- Conflict audit records duplicate overlay IDs and same-slot priority conflicts.
- Composition is shadow-only and does not mutate the active base prompt.
- Replay exposes `prompt_overlay_registry_chain`, and the scorecard exposes `PromptOverlayRegistry` as a substrate component.

Canon effect:

NexusNet can now adapt prompt contracts by provider and model family without cloning or mutating the base NexusBrain prompt. Prompt changes are inspectable substrate artifacts with compatibility and conflict evidence.

This locks the rule that prompt overlays are shadow-reviewed before activation.

### PB-2026-05-03-047 - Skill System Loader In Forward Pass

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated skill-system contracts:

- Forward passes can carry a skill-system definition through metadata.
- Markdown/frontmatter skill definitions and dict skill definitions resolve into small reusable component skills.
- Project definitions override user/global/marketplace definitions for the same skill ID while preserving shadowed-definition evidence.
- Components record allowed tools, model overrides, context mode, reuse state, and privacy digests instead of raw markdown export.
- A single orchestrator contract records run order, progressive disclosure, anti-mega-skill policy, anti-isolated-endpoint policy, and context rules.
- Handoff validation records from/to skill IDs, handoff artifacts, validation state, and copy-paste-free transfer policy.
- Human checkpoints and visual result contracts are explicit.
- Replay exposes `skill_system_loader_chain`, and the scorecard exposes `SkillSystemLoader` as a substrate component.

Canon effect:

The Markdown skill/agent loader is now interpreted through NexusNet's skill-system architecture: focused reusable skills are components, and a single orchestrator wires their sequence, handoffs, checkpoints, and output surface.

This locks the rule that skills should compose into governed skill systems rather than grow into mega-skills or isolated one-off endpoints.

### PB-2026-05-03-048 - Bridge Manager In Forward Pass

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated bridge-manager contracts:

- Forward passes can carry a bridge catalog through metadata.
- Bridge records include bridge ID, transport, permissions, local-first state, redaction policy, outbound commitment review, and transport health probe state.
- External outbound permissions require human approval and redaction before messages can leave the hive.
- Raw bridge payloads are not exported into the substrate artifact.
- Local bridges can be read-only without outbound review, while external send/publish/speak/write permissions remain gated.
- Replay exposes `bridge_manager_chain`, and the scorecard exposes `BridgeManager` as a substrate component.

Canon effect:

NexusNet now represents communication bridges as governed substrate artifacts rather than direct side effects. Slack, web, daemon, and future bridge transports must pass local-first permissions, redaction, and outbound commitment checks.

This locks the rule that external bridge messages cannot leave NexusNet without bridge-specific commitment review.

### PB-2026-05-03-049 - Research Monitor Pipeline In Forward Pass

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated research-monitor contracts:

- Forward passes can carry research monitor entries through metadata.
- Scheduled source monitor state records monitor IDs, source URL digests, candidate IDs, trend signals, license state, security state, and runtime gate state.
- Strong trend signals become shadow candidate intake records only.
- Weak or incomplete signals move to a demotion watchlist.
- Each candidate receives a promotion-gate map requiring source verification, license review, security review, runtime sandbox eval, and human/governance approval.
- Raw source content is not exported into the substrate artifact.
- Replay exposes `research_monitor_pipeline_chain`, and the scorecard exposes `ResearchMonitorPipeline` as a substrate component.

Canon effect:

NexusNet now has a substrate-level forward radar: research signals become gated shadow candidates or watchlist entries, not automatic runtime changes.

This locks the rule that monitored research cannot promote without evidence gates.

### PB-2026-05-03-050 - Checkpoint Rewind Ledger Hardening

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated checkpoint contracts:

- Checkpoints now record explicit pre-write snapshot metadata.
- Checkpoints record session-turn snapshot metadata with run ref, task ID, session ID, and turn digest.
- Checkpoints record token snapshot metadata with estimated prompt/action token counts.
- Checkpoints record rewind metadata including operator-approved diff preview policy.
- Rewind restore validation confirms pre-write, session-turn, and token snapshots exist.
- Prompt/tool snapshot replay carries token snapshot metadata.

Canon effect:

The Checkpoint/Rewind Ledger now matches the post-book target more closely: restore proof has explicit snapshot categories instead of a single generic checkpoint metadata blob.

This locks the rule that rewind proof must include pre-write, session-turn, token, prompt, tool, and diff-preview evidence.

### PB-2026-05-03-051 - Control Panel Replay Chain Coverage

Status: live_substrate_implementation
Source refs:

- `ui/control-panel/app.js`
- `tests/test_hive_neural_substrate.py`
- `nexusnet/hive/substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated Control Panel contracts:

- The Hive Neural Substrate replay drilldown now counts tool registry chains.
- It counts task dependency graph chains.
- It counts provider circuit breaker chains.
- It counts prompt overlay registry chains.
- It counts skill-system loader chains.
- It counts bridge manager chains.
- It counts research monitor pipeline chains.
- Existing runtime and node-output counts remain visible.

Canon effect:

New substrate replay artifacts are cockpit-visible instead of hidden behind backend JSON. This keeps NexusNet's Harness UI aligned with the hive substrate.

This locks the rule that new substrate replay chains must be visible in the Control Panel when they are part of v0 completion proof.

### PB-2026-05-03-052 - Active Release Canary Gate

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `nexus/api/app.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated active-release contracts:

- A shadow release can now be promoted through an explicit active-release gate.
- Active release requires an existing active shadow release, operator approval ref, human/governance approval, canary eval refs, monitoring refs, and rollback rehearsal ref.
- Blocked active-release attempts are recorded as gate artifacts but do not count as active release pointers.
- Approved active release mutates only a repo-local release pointer metadata artifact.
- Code, model weights, prompts, runtime binaries, and private data are not mutated or exported by this gate.
- Rollback can restore the active production release pointer through the same rollback endpoint and records active-pointer restore scope.
- Replay exposes `active_release_chain`, and the Control Panel counts the active-release chain in the Hive Neural Substrate replay drilldown.

Canon effect:

NexusNet now has the missing step after shadow release: an evidence-bound active release pointer that is canary-gated, monitoring-armed, rollback-rehearsed, human-approved, and cockpit-visible.

This locks the rule that active production movement cannot be implicit. Even when release is approved, v0 mutates only release pointer metadata; real code, model, prompt, runtime, or binary mutation requires a separate signed release process with full rollback proof.

### PB-2026-05-03-053 - Manifest-Inspired Inference Economy Router

Status: live_control_plane
Source refs:

- `https://github.com/mnfst/manifest`
- `docs/manifest_assimilation.md`
- `docs/model_routing_strategy.md`
- `config/inference_routing.yaml`
- `nexusnet/runtime/inference_economy_router.py`
- `nexusnet/runtime/manifest_adapter.py`
- `nexus/api/app.py`
- `ui/control-panel/`
- `tests/runtime/test_inference_economy_router.py`
- `tests/runtime/test_manifest_adapter.py`

Assimilated Manifest-style contracts:

- NexusNet now has a native InferenceEconomyRouter beneath NexusBrain authority.
- Routing order is privacy/safety policy, explicit override, policy route, specificity, complexity, provider selection, fallback, trace recording.
- Complexity scoring excludes `system` and `developer` messages so NexusNet's own large brain prompt does not force expensive routing.
- Specificity routing covers coding, browsing, data analysis, image/video generation, social/email/calendar management, and trading.
- Tier assignment supports simple, standard, complex, reasoning, and default routes with capability thresholds instead of cheapest-only routing.
- Local providers include Ollama, LM Studio, and llama.cpp metadata paths.
- A ManifestAdapter can build OpenAI-compatible `manifest/auto` requests and parse `X-Manifest-*` routing headers.
- Manifest telemetry opt-out is required with `MANIFEST_TELEMETRY_DISABLED=1`.
- Cost ledgers compare selected-route cost against a strong-baseline route and never export raw prompt content.
- The API, blackbox scorecard refs, and Control Panel now expose the router.

Canon effect:

NexusNet can now make auditable, privacy-first inference economy decisions without making Manifest the brain. Manifest is treated as an optional local/self-hosted proxy adapter, while NexusNet's native router remains the canonical control layer.

This locks the rule that cost optimization cannot precede privacy, safety, governance, sandbox, eval, or human-approval gates.

### PB-2026-05-03-054 - First-Class Hive Neural Pathway Map

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated neural-pathway contracts:

- Every forward pass now emits a first-class `HiveNeuralPathwayMap` artifact.
- The pathway map binds activation, NeuralBus, HiveBlackboard, checkpoint, and plane-trace refs.
- The pathway map records the primary brain, orchestrator, AO, and expert mini-brain scale stack as hive-visible brain instances.
- Plane pathways explicitly model dendrite, synapse, residual, recurrent, feedback, and immune-gate edges.
- Node pathways record parent-to-child mini-brain links, sparse-active vs visible-idle state, activation weights, and harmonic phase metadata.
- Feedback pathways make eval/loss, federated priors, Recursive Neural Dreaming, and checkpoint/rewind visible as substrate feedback edges.
- Harmonic topology metadata maps the symbolic sacred-geometry kernel to mixed straight/circular pathways, Flower-of-Life-style feedback overlap, and 64-tetrahedron-style plane lattice edges.
- Downstream AO/Expert/Orchestrator runtime receipts now consume NeuralBus, HiveBlackboard, and the pathway map artifact, while still forbidding direct local state reads.
- Productionization, sandbox-provider receipts, shadow release, active release, and rollback evidence now carry the pathway map ref with NeuralBus and HiveBlackboard refs.
- Replay exposes `neural_pathway_chain`, the Control Panel counts neural pathway replay artifacts, and the scorecard exposes `HiveNeuralPathwayMap` as a substrate component.

Canon effect:

NexusNet's hive neural network pathways are no longer implicit inside route decisions and receipts. They are now an inspectable, replayable, repo-local artifact that shows how planes, mini-brains, feedback loops, immune gates, and harmonic substrate metadata connect during a forward pass.

This locks the rule that neural-pathway evidence must be generated with each forward pass before downstream execution is treated as substrate-complete. The pathway map is evidence and routing context only; it cannot mutate active production without sandbox/eval/governance/release approval.

### PB-2026-05-03-055 - Hive Synaptic Transmission Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated synaptic-transmission contracts:

- Every forward pass now emits a first-class `HiveSynapticTransmissionLedger` artifact after the pathway map is built.
- The transmission ledger binds pathway, activation, NeuralBus, HiveBlackboard, and checkpoint refs.
- Plane signals propagate across dendrite, synapse, residual, recurrent, and immune-gate pathway edges with bounded signal strengths.
- Node signals propagate through the mini-brain scale stack and distinguish sparse-active nodes from visible-idle monitoring nodes.
- Recurrent signals expose loop feedback and exit-gate state.
- Feedback signals expose eval/loss, federated-prior, Recursive Neural Dreaming, and checkpoint/rewind feedback paths.
- Immune gate signals expose open vs blocked gate state, hard-fail counts, findings, and route-around requirements.
- Downstream AO/Expert/Orchestrator runtime receipts now consume NeuralBus, HiveBlackboard, pathway map, and synaptic transmission refs.
- Productionization, sandbox-provider receipts, shadow release, active release, and rollback evidence now carry the synaptic transmission ref with the pathway map ref.
- Replay exposes `synaptic_transmission_chain`, the Control Panel counts signal replay artifacts, and the scorecard exposes `HiveSynapticTransmissionLedger` as a substrate component.

Canon effect:

NexusNet's pathway topology is now paired with live signal evidence. The substrate no longer only says which planes and mini-brains are connected; it records how activation signal propagates through those paths for a forward pass, including recurrent feedback and immune gating.

This locks the rule that pathway topology and signal transmission evidence must both exist before downstream execution, productionization, or release evidence can be considered substrate-complete. The signal ledger is read-only evidence; it cannot mutate active production without sandbox/eval/governance/release approval.

### PB-2026-05-03-056 - Hive Neuroplastic Weight Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated neuroplastic-weight contracts:

- Every forward pass now emits a first-class `HiveNeuroplasticWeightLedger` artifact after synaptic transmission.
- The weight ledger binds pathway, transmission, activation, NeuralBus, HiveBlackboard, and checkpoint refs.
- Plane, node, and feedback weight updates are derived from bounded synaptic signal evidence using a deterministic shadow-only Hebbian-style delta.
- Eligibility traces use phi-decay metadata so recurrent learning evidence can be replayed without mutating active routing or model weights.
- Plasticity integrity explicitly records empty direct local state reads, bounded deltas, no raw private content, and no active production mutation.
- Downstream AO/Expert/Orchestrator runtime receipts now consume NeuralBus, HiveBlackboard, pathway map, synaptic transmission, and neuroplastic weight refs.
- Productionization, sandbox-provider receipts, shadow release, active release, and rollback evidence now carry the neuroplastic weight ref with the pathway and synaptic refs.
- Replay exposes `neuroplastic_weight_chain`, the Control Panel counts weight replay artifacts, and the scorecard exposes `HiveNeuroplasticWeightLedger` as a substrate component.

Canon effect:

NexusNet now records the first live neuroplastic learning evidence layer. The substrate no longer only records pathway topology and signal propagation; it also derives bounded shadow weight deltas and eligibility traces that can later influence routing only after sandbox, eval, teacher review, federation safety, governance, and rollback gates pass.

This locks the rule that neuroplastic updates are evidence first and production changes later. A weight ledger can inform shadow routing and eval design, but it cannot mutate active production, active model weights, prompts, runtime binaries, or deployed routes without explicit gated release approval.

### PB-2026-05-03-057 - Hive Laminar Microcircuit Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated laminar-microcircuit contracts:

- Every forward pass now emits a first-class `HiveLaminarMicrocircuitLedger` artifact after plane trace generation.
- The microcircuit ledger binds activation, NeuralBus, HiveBlackboard, checkpoint, and plane-trace refs.
- Each cognitive plane now has explicit L1, L2/3, L4, and L5/6 laminar layer metadata.
- Each plane records symbolic excitatory/inhibitory population balance, basal feedforward dendritic compartments, apical contextual dendritic compartments, and bounded event thresholds.
- The event-driven update policy is visible in replay while remaining symbolic metadata rather than a biological simulation claim.
- Downstream AO/Expert/Orchestrator runtime receipts now consume NeuralBus, HiveBlackboard, laminar microcircuit, pathway map, synaptic transmission, and neuroplastic weight refs.
- Productionization, sandbox-provider receipts, shadow release, active release, and rollback evidence now carry the laminar microcircuit ref with the other substrate refs.
- Replay exposes `laminar_microcircuit_chain`, the Control Panel counts microcircuit replay artifacts, and the scorecard exposes `HiveLaminarMicrocircuitLedger` as a substrate component.

Canon effect:

NexusNet's planes now contain explicit internal neural-network structure instead of being only top-level execution stages. This gives the hive substrate a first inspectable version of plane-internal laminar circuitry, dendritic-style integration, symbolic spike/event thresholds, and population-balance metadata.

This locks the rule that each plane must expose its internal microcircuit state as replayable evidence before downstream runtime execution can be called substrate-complete. The microcircuit ledger is read-only evidence and cannot mutate active production without sandbox/eval/governance/release approval.

### PB-2026-05-03-058 - Hive Neuromodulatory State Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_substrate.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated neuromodulatory-state contracts:

- Every forward pass now emits a first-class `HiveNeuromodulatoryStateLedger` artifact after shadow neuroplastic weight derivation.
- The neuromodulatory ledger binds laminar microcircuit, pathway, synaptic transmission, neuroplastic weight, activation, NeuralBus, HiveBlackboard, and checkpoint refs.
- The ledger records symbolic dopamine/reward-prediction-error, acetylcholine/uncertainty-attention, serotonin/stability-homeostasis, norepinephrine/immune-alert, and dream-novelty modulator signals.
- The plasticity gate computes a bounded effective shadow learning rate and explicitly blocks active route or model-weight mutation.
- Modulation integrity explicitly records empty direct local state reads, no raw private content, and no active production mutation.
- Downstream AO/Expert/Orchestrator runtime receipts now consume NeuralBus, HiveBlackboard, laminar microcircuit, pathway map, synaptic transmission, neuroplastic weight, and neuromodulatory state refs.
- Productionization, sandbox-provider receipts, shadow release, active release, and rollback evidence now carry the neuromodulatory state ref with the other substrate refs.
- Replay exposes `neuromodulatory_state_chain`, the Control Panel counts modulator/gate replay artifacts, and the scorecard exposes `HiveNeuromodulatoryStateLedger` as a substrate component.

Canon effect:

NexusNet's neuroplasticity now has a governing modulation layer rather than free-floating weight deltas. Reward, uncertainty, stability, immune alert, and dream novelty are visible as bounded symbolic signals that can shape shadow learning proposals without making production changes.

This locks the rule that plasticity requires a modulator gate before any learning evidence can be considered promotion-ready. Neuromodulatory state remains read-only evidence until sandbox/eval/teacher/federation/governance/release gates approve a change.

### PB-2026-05-03-059 - Nemotron Omni Multimodal Teacher Adapter

Status: live_control_plane
Source refs:

- `https://developer.nvidia.com/blog/nvidia-nemotron-3-nano-omni-powers-multimodal-agent-reasoning-in-a-single-efficient-open-model/`
- `https://huggingface.co/nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16`
- `docs/research/nvidia_nemotron_3_nano_omni_assimilation.md`
- `docs/decisions/ADR-optional-nemotron-omni-teacher.md`
- `nexusnet/teachers/adapters/nemotron_omni_adapter.py`
- `nexusnet/teachers/teacher_registry_v2026_live.yaml`
- `tests/test_nemotron_omni_teacher_adapter.py`

Assimilated Nemotron Omni contracts:

- NVIDIA Nemotron 3 Nano Omni is registered as an optional multimodal teacher/perception reference, not a NexusNet brain replacement.
- The live teacher registry now has an auxiliary `multimodal-professor` path that preserves the locked 19 live expert pairs.
- The adapter contract records the model as a 31B total parameter, about 3B active parameter per token, 256k-context multimodal MoE teacher reference with BF16, FP8, and NVFP4 variants.
- The adapter can build structured evidence packets for lesson packets, critique packets, multimodal summaries, benchmark observations, dream seeds, and foundry training candidates.
- Evidence is blocked by default until license status is approved, hardware profile is reviewed, and an operator approval ref exists.
- Raw multimodal inputs are not stored in the teacher evidence packet.

Canon effect:

NexusNet now has a concrete multimodal Ivy-class teacher seam for video, audio, image, text, documents, and GUI reasoning without altering the core brain path. Nemotron Omni can feed teacher/dream/foundry evidence into the Hive substrate, but it cannot replace the brain, mutate active routes, download weights, or run production inference without license, hardware, privacy, sandbox, benchmark, and human/governance approval.

### PB-2026-05-03-060 - Hive Embedding Tensor Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated embedding-tensor contracts:

- Every forward pass now emits a first-class `HiveEmbeddingTensorLedger` artifact after HiveActivation and before attention routing.
- The ledger binds activation, checkpoint, token records, embedding shape, symbolic tensor statistics, and harmonic formula basis.
- Token records store stable token hashes and coordinate digests, not raw tokens or raw intent.
- Embedding dimension is represented as Fibonacci-13 symbolic tensor metadata, with golden-angle phase and phi-radius per token.
- Replay exposes `embedding_tensor_chain`, the Control Panel counts embedding chains, and the scorecard exposes `HiveEmbeddingTensorLedger`.

Canon effect:

NexusNet now has an inspectable representation plane instead of only an activation ID and embedding ref. This remains symbolic replay evidence and does not claim trained model weights or expose raw private content.

### PB-2026-05-03-061 - Hive Attention Routing Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated attention-routing contracts:

- Every forward pass now emits a first-class `HiveAttentionRoutingLedger` artifact after embedding tensor generation.
- Multi-head attention-style metadata focuses over selected nodes, memory refs, policy gate, NeuralBus, and HiveBlackboard refs.
- Each attention head records query/key/value refs, normalized focus weights, and harmonic phase metadata.
- Raw private content is not read by the attention ledger.
- Replay exposes `attention_routing_chain`, the Control Panel counts attention chains, and the scorecard exposes `HiveAttentionRoutingLedger`.

Canon effect:

NexusNet now has a replayable attention/focus plane that explains what the hive is focusing on before sparse expert routing. Attention evidence remains read-only and cannot mutate active routing without sandbox/eval/governance/release approval.

### PB-2026-05-03-062 - Hive Sparse Expert Gate Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated sparse-expert-gate contracts:

- Every forward pass now emits a first-class `HiveSparseExpertGateLedger` artifact after attention routing.
- The gate ledger records top-k sparse expert/node selection, normalized gate distribution, Mini-NexusNet brain refs, and dormant visible-idle node refs.
- Non-selected nodes stay hive-visible for monitoring, dreaming, repair, and later routing.
- Active production routing is not mutated by gate evidence.
- Replay exposes `sparse_expert_gate_chain`, the Control Panel counts sparse-gate chains, and the scorecard exposes `HiveSparseExpertGateLedger`.

Canon effect:

NexusNet now has an explicit sparse-MoE gate plane rather than only a route decision. The gate records which mini-brains activated, which stayed visible-idle, and why the route stayed shadow-evidence until gated promotion.

### PB-2026-05-03-063 - Hive Loss Backpropagation Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated loss/backpropagation contracts:

- Every forward pass now emits a first-class `HiveLossBackpropagationLedger` artifact after neuromodulatory gating and before downstream runtime receipts.
- The ledger binds embedding tensor, attention routing, sparse gate, neuroplastic weights, neuromodulatory state, activation, and checkpoint refs.
- Loss terms include route-quality loss, policy-risk loss, uncertainty loss, and federation-privacy loss.
- Gradient paths provide clipped shadow credit assignment to selected mini-brain/expert routes.
- The optimizer step is shadow-only and cannot mutate active model weights or active routes.
- Replay exposes `loss_backpropagation_chain`, the Control Panel counts backprop chains, and the scorecard exposes `HiveLossBackpropagationLedger`.

Canon effect:

NexusNet now has a replayable backward pass evidence layer. This does not train production weights; it records loss, gradient, and optimizer metadata that can later inform sandbox/eval/teacher/federation/governance-approved promotion.

### PB-2026-05-03-064 - Hive Residual Normalization Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated residual-normalization contracts:

- Every forward pass now emits a first-class `HiveResidualNormalizationLedger` artifact after attention routing.
- The ledger binds embedding tensor, attention routing, NeuralBus, HiveBlackboard, activation, and checkpoint refs.
- Normalized streams include embedding residual, attention residual, blackboard residual, and neural-bus residual state.
- The policy records symbolic RMSNorm-style normalization with harmonic epsilon scheduling.
- Active tensor values are not mutated by the ledger.
- Replay exposes `residual_normalization_chain`, the Control Panel counts normalization chains, and the scorecard exposes `HiveResidualNormalizationLedger`.

Canon effect:

NexusNet now has a replayable residual stream and layer-normalization evidence surface. This turns the transformer normalization stage into an auditable substrate artifact instead of implicit metadata.

### PB-2026-05-03-065 - Hive FeedForward Expert Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated feed-forward expert contracts:

- Every forward pass now emits a first-class `HiveFeedForwardExpertLedger` artifact after sparse expert gating.
- The ledger binds sparse-gate distribution, residual-normalization state, NeuralBus, HiveBlackboard, activation, and checkpoint refs.
- Each selected Mini-NexusNet node receives a symbolic feed-forward expert unit with gate weight, hidden projection ref, output projection ref, GEGLU-style activation metadata, and 4x expansion metadata.
- Active expert weights are not mutated by feed-forward evidence.
- Replay exposes `feedforward_expert_chain`, the Control Panel counts feed-forward chains, and the scorecard exposes `HiveFeedForwardExpertLedger`.

Canon effect:

NexusNet now has explicit expert-computation evidence between sparse MoE gating and downstream AO/expert execution. This makes the expert MLP/FFN stage visible without claiming production weight training.

### PB-2026-05-03-066 - Hive Latent Loop Exit Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated latent-loop exit contracts:

- Every forward pass now emits a first-class `HiveLatentLoopExitLedger` artifact from recurrent deliberation loop evidence.
- The ledger binds attention routing, sparse gate, feed-forward expert, activation, and checkpoint refs.
- Exit steps record latent state refs, hazard exit probability, survival mass, unconditional exit mass, CDF exit mass, exit state, exit reason, forced-final-exit metadata, and harmonic cadence.
- The exit policy is hazard/survival/CDF based and mirrors looped-language-model style latent reasoning without requiring exposed vocabulary chain-of-thought.
- Replay exposes `latent_loop_exit_chain`, the Control Panel counts latent-loop chains, and the scorecard exposes `HiveLatentLoopExitLedger`.

Canon effect:

NexusNet now has a first-class latent reasoning loop and exit-gate ledger. This supports internal compute scaling evidence while preserving the boundary that production model weights and visible chain-of-thought are not mutated or required.

### PB-2026-05-03-067 - Hive KV Cache Compression Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated KV-cache compression contracts:

- Every forward pass now emits a first-class `HiveKVCacheCompressionLedger` artifact after latent-loop exit evidence.
- The ledger binds attention routing, latent-loop exit, activation, and checkpoint refs.
- Candidate policies include full precision, sliding-window eviction, heavy-hitter retention, quantized KV, low-rank KV projection, and a hybrid heavy-hitter/quantized/low-rank shadow policy.
- The selected policy is shadow-only and requires sandbox benchmarking before any backend mutation.
- Raw KV values and raw private content are not stored.
- Replay exposes `kv_cache_compression_chain`, the Control Panel counts KV-cache chains, and the scorecard exposes `HiveKVCacheCompressionLedger`.

Canon effect:

NexusNet now treats KV-cache optimization as a substrate-visible research and runtime evidence surface. It can compare compression candidates in shadow mode without silently mutating active inference backends.

### PB-2026-05-03-068 - Hive Sensory Input Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated sensory-input contracts:

- Every forward pass now emits a first-class `HiveSensoryInputLedger` artifact immediately after activation and checkpoint creation.
- The ledger normalizes operator intent, capability signals, memory refs, and action refs into privacy-safe symbolic channels.
- Raw intent, raw action targets, raw memory content, local paths, and private file content are not stored.
- The tokenizer policy is metadata-estimator based in v0 and explicitly marks the boundary as a symbolic evidence ledger, not a production tokenizer kernel.
- Replay exposes `sensory_input_chain`, the Control Panel counts sensory chains, and the scorecard exposes `HiveSensoryInputLedger`.

Canon effect:

NexusNet now has an auditable sensory/tokenization ingress plane before embedding. This completes the front edge of the hive substrate without leaking raw operator/private content into replay or federation.

### PB-2026-05-03-069 - Hive Temporal Positional Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated temporal-position contracts:

- Every forward pass now emits a first-class `HiveTemporalPositionalLedger` artifact after embedding tensor creation.
- The ledger binds sensory input, embedding tensor, activation, checkpoint, token positions, latent-loop positions, and checkpoint-anchor positions.
- Position records use rotary golden-angle symbolic metadata with phi-radius weights.
- Context order is not mutated by this evidence surface.
- Replay exposes `temporal_positional_chain`, the Control Panel counts position chains, and the scorecard exposes `HiveTemporalPositionalLedger`.

Canon effect:

NexusNet now has a replayable temporal/positional plane tying token order, recurrent loop order, and checkpoint order together before attention and memory binding.

### PB-2026-05-03-070 - Hive Memory Engram Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated memory-engram contracts:

- Every forward pass now emits a first-class `HiveMemoryEngramLedger` artifact after temporal position binding.
- The ledger binds memory refs to temporal positions using digest/key references only.
- Raw memory content is not stored, exported, or read into the evidence artifact.
- Retrieval mode is `reference-only-engram-binding`, preserving the source-canon/context memory boundary.
- Replay exposes `memory_engram_chain`, the Control Panel counts memory chains, and the scorecard exposes `HiveMemoryEngramLedger`.

Canon effect:

NexusNet now has a dedicated memory-engram plane that can bind source canon and prior context into the hive substrate without pulling entire private memory pools into every task.

### PB-2026-05-03-071 - Hive Optimizer School Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated optimizer-school contracts:

- Every forward pass now emits a first-class `HiveOptimizerSchoolLedger` artifact after loss/backpropagation and KV/latent-loop evidence.
- The ledger converts loss terms and gradient paths into shadow curriculum proposals and Ivy-school teacher review queue items.
- Active model weights, active routes, prompts, binaries, and provider settings are not mutated.
- Teacher review and human governance remain required before promotion.
- Replay exposes `optimizer_school_chain`, the Control Panel counts optimizer-school chains, and the scorecard exposes `HiveOptimizerSchoolLedger`.

Canon effect:

NexusNet now has an auditable optimizer-school bridge between shadow backpropagation evidence and Ivy-grade teacher/distillation review. Learning proposals exist, but production mutation remains sandbox/eval/governance gated.

### PB-2026-05-03-072 - Hive Action Output Decoder Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated action-output contracts:

- Every forward pass now emits a first-class `HiveActionOutputDecoderLedger` artifact after downstream AO/expert runtime execution.
- The ledger decodes downstream node output refs into operator-reviewable output artifacts using result digests only.
- Raw outputs are not exported by the decoder ledger.
- External delivery and active production mutation remain disabled unless an explicit operator/release gate approves them.
- Replay exposes `action_output_decoder_chain`, the Control Panel counts output decoder chains, and the scorecard exposes `HiveActionOutputDecoderLedger`.

Canon effect:

NexusNet now has a replayable action-output plane at the tail of the hive substrate. The forward pass can prove outputs were generated from substrate artifacts while keeping external delivery gated.

### PB-2026-05-03-073 - Hive Plane Adjacency Matrix

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated plane-matrix contracts:

- Every forward pass now embeds a first-class `hive-plane-adjacency-matrix-v0` object inside the neural pathway map.
- The matrix records the ordered sixteen-plane substrate shape, weighted plane edges, recurrent edges, semantic memory-attention edges, and feedback/immune overlay counts.
- Matrix refs are bound to the actual forward-pass artifacts for sensory input, embeddings, temporal positions, memory engrams, NeuralBus, attention, gates, expert computation, latent loops, loss/backpropagation, optimizer-school, action-output decoding, and checkpoint.
- Downstream AO/Expert/Orchestrator runtime receipts consume the matrix ID as a substrate artifact ref.
- The scorecard exposes `HivePlaneAdjacencyMatrix` and replay returns the matrix through `neural_pathway_chain`.

Canon effect:

NexusNet now has an explicit plane-to-plane neural connectivity matrix rather than only a list of pathway edges. This makes the substrate's full ordered neural network topology auditable while preserving the boundary that matrix evidence cannot mutate active production routing by itself.

### PB-2026-05-03-074 - Hive Forward Propagation Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated forward-propagation contracts:

- Every forward pass now emits a first-class `HiveForwardPropagationLedger` artifact.
- The ledger records one ordered state-vector handoff per substrate plane, starting at sensory input and ending at checkpoint/rewind.
- Each propagation step binds to the `hive-plane-adjacency-matrix-v0` refs instead of reading direct local state.
- The action-output decoder carries `forward_propagation_ref` so decoded outputs can be traced back through the substrate pathway.
- Replay exposes `forward_propagation_chain`, the Control Panel counts propagation chains, and the scorecard exposes `HiveForwardPropagationLedger`.
- Raw private content is not stored in propagation steps, and propagation evidence cannot mutate production state by itself.

Canon effect:

NexusNet now has an auditable forward-propagation trace across the full hive substrate. The neural network pathway is no longer only a topology map; it also records the ordered plane-to-plane state handoffs that AOs, experts, and replay surfaces must consume.

### PB-2026-05-03-075 - Hive Backward Propagation Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated backward-propagation contracts:

- Every forward pass now emits a first-class `HiveBackwardPropagationLedger` artifact after forward propagation and loss/backpropagation evidence exist.
- The ledger walks the forward-propagation steps in reverse, starting from checkpoint/rewind and ending at sensory input.
- Each reverse step binds to a source forward step, source artifact ref, loss/backpropagation ref, and symbolic gradient/credit-assignment metadata.
- Replay exposes `backward_propagation_chain`, the Control Panel counts reverse propagation chains, and the scorecard exposes `HiveBackwardPropagationLedger`.
- Reverse propagation is read-only shadow evidence. It stores no raw private content and cannot mutate model weights, routes, prompts, providers, files, or production runtime by itself.

Canon effect:

NexusNet now has both a forward state-flow pathway and a reverse credit-assignment pathway across the hive neural substrate. This closes the basic neural-network pathway loop while preserving the rule that actual weight or route mutation requires sandbox, eval, Ivy-school review, governance, and human approval.

### PB-2026-05-03-076 - Hive Parameter Tensor Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated parameter-tensor contracts:

- Every forward pass now emits a first-class `HiveParameterTensorLedger` artifact after forward propagation, backward propagation, and neuroplastic weight evidence exist.
- The ledger maps symbolic parameter refs for weights, biases, gates, norms, adapters, and output projections.
- Parameter tensor records bind to source forward steps and source substrate artifact refs.
- Raw tensor values are never stored, and active parameters cannot be mutated through this ledger.
- Downstream AO/expert runtime receipts consume the parameter tensor ledger as a substrate artifact ref.
- Replay exposes `parameter_tensor_chain`, the Control Panel counts parameter tensor chains, and the scorecard exposes `HiveParameterTensorLedger`.

Canon effect:

NexusNet now has a reference-only parameter plane for the hive neural network. This gives the substrate an auditable map of symbolic weights, biases, gates, norms, adapters, and output projections while preserving the rule that real parameter mutation requires sandbox, eval, Ivy-school review, governance, and human approval.

### PB-2026-05-03-077 - Hive Activation Function Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated activation-function contracts:

- Every forward pass now emits a first-class `HiveActivationFunctionLedger` artifact after parameter tensor refs exist.
- The ledger maps nonlinear function families for attention softmax, sigmoid gates, GEGLU expert computation, RMSNorm residual normalization, rotary/golden-angle phase, latent hazard exits, neuromodulatory bounding, and output projection.
- Function records bind to the parameter tensor ledger and forward propagation ledger.
- Raw activation values are never stored, and active kernel mutation is forbidden through this ledger.
- Downstream AO/expert runtime receipts consume the activation function ledger as a substrate artifact ref.
- Replay exposes `activation_function_chain`, the Control Panel counts activation function chains, and the scorecard exposes `HiveActivationFunctionLedger`.

Canon effect:

NexusNet now has an auditable nonlinear-function plane for the hive neural network. The substrate can prove which symbolic nonlinearities shaped a run without exposing private activation values or mutating active kernels.

### PB-2026-05-03-078 - Hive Computational Graph Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated computational-graph contracts:

- Every forward pass now emits a first-class `HiveComputationalGraphLedger` artifact after activation-function, parameter, forward-propagation, and backward-propagation evidence exist.
- The ledger records operation nodes and operation edges for forward dataflow and backward symbolic credit assignment.
- Operation nodes bind to source plane steps, source artifact refs, parameter refs, and activation-function families.
- Raw tensor values are never stored, and active runtime mutation is forbidden through this ledger.
- Downstream AO/expert runtime receipts consume the computational graph ledger as a substrate artifact ref.
- Replay exposes `computational_graph_chain`, the Control Panel counts computational graph chains, and the scorecard exposes `HiveComputationalGraphLedger`.

Canon effect:

NexusNet now has an auditable operation graph for the hive neural network. This connects topology, functions, parameters, forward flow, and reverse credit assignment into one replayable computational substrate without allowing direct production mutation.

### PB-2026-05-03-079 - Hive Optimizer State Vector Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated optimizer-state contracts:

- Every forward pass now emits a first-class `HiveOptimizerStateVectorLedger` artifact after the computational graph exists.
- The ledger records shadow optimizer vectors for first moment, second moment, learning rate, weight decay, gradient clipping, and trust region.
- Optimizer state vectors bind to the computational graph, parameter tensor ledger, optimizer-school ledger, and backward-propagation ledger.
- Raw gradient values are never stored, and active optimizer state or parameter mutation is forbidden through this ledger.
- Downstream AO/expert runtime receipts consume the optimizer state vector ledger as a substrate artifact ref.
- Replay exposes `optimizer_state_vector_chain`, the Control Panel counts optimizer-state chains, and the scorecard exposes `HiveOptimizerStateVectorLedger`.

Canon effect:

NexusNet now has explicit optimizer-state internals for shadow learning and future distillation planning. The substrate can reason about update mechanics without touching active parameters.

### PB-2026-05-03-080 - Hive Model Genome Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated model-genome contracts:

- Every forward pass now emits a first-class `HiveModelGenomeLedger` artifact after optimizer-state evidence exists.
- The ledger records distillation-ready architecture genes for embedding dimension, attention heads, MoE top-k, layer/block count, activation suite, optimizer family, and federation policy.
- The genome binds to optimizer state, computational graph, parameter tensors, activation functions, and checkpoint refs.
- Raw model weights are never stored, and active architecture mutation is forbidden through this ledger.
- The distillation blueprint requires teacher review, sandbox eval, governance, and human approval before child expert generation or parent retirement can become active.
- Downstream AO/expert runtime receipts consume the model genome ledger as a substrate artifact ref.
- Replay exposes `model_genome_chain`, the Control Panel counts model genome chains, and the scorecard exposes `HiveModelGenomeLedger`.

Canon effect:

NexusNet now has a distillation-ready architecture blueprint for the hive neural network. This gives future Ivy-school expert generation and recursive dreaming a governed genome artifact instead of relying on scattered runtime metadata.

### PB-2026-05-03-081 - Hive Tensor Runtime Kernel Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`
- `docs/superpowers/specs/2026-05-01-nexusnet-hive-neural-substrate-v0-design.md`

Assimilated tensor-runtime contracts:

- Every forward pass now emits a `HiveTensorRuntimeKernelLedger` after graph, genome, parameter, activation-function, and optimizer-state evidence exists.
- The ledger records sandbox-shadow tensor-like operations over graph operation refs without storing raw tensor values.
- Numeric precision metadata is represented for BF16, INT8, and NF4-style shadow execution policies.
- Active runtime mutation is forbidden until sandbox benchmarks, regression proof, governance, and human approval pass.

Canon effect:

NexusNet now has a first executable tensor-runtime contract for the neural substrate. It is still shadow/sandbox-only, but it converts the prior reference-only graph into runtime operation evidence.

### PB-2026-05-03-082 - Hive Layer Block Stack Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`

Assimilated layer-stack contracts:

- Every forward pass now emits a `HiveLayerBlockStackLedger`.
- The ledger models the repeated execution stack as embedding block, repeated transformer/MoE blocks, and output head.
- Blocks bind to tensor-kernel, graph, genome, activation, and checkpoint refs.

Canon effect:

NexusNet now has an explicit neural-network block stack rather than only a single forward-pass path.

### PB-2026-05-03-083 - Hive Distillation Loop Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `tests/test_hive_neural_network_internals.py`

Assimilated distillation contracts:

- Every forward pass now emits a `HiveDistillationLoopLedger`.
- The ledger records Ivy-school teacher panel requirements, temporary child expert candidates, eval scorecards, promotion gates, and parent-retirement gates.
- Active child promotion and parent retirement remain blocked until teacher review, sandbox/eval proof, governance, and human approval pass.

Canon effect:

NexusNet now has live distillation-loop evidence attached to every substrate run, preparing future student expert generation without silently mutating the hive.

### PB-2026-05-03-084 - Hive Federated Influence Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `tests/test_hive_neural_network_internals.py`

Assimilated federation-influence contracts:

- Every forward pass now emits a `HiveFederatedInfluenceLedger`.
- Sanitized federated prior updates feed shadow routing/training priors with secure aggregation, trust scoring, poisoning scan, and differential privacy metadata.
- Raw personal data is not shared and active router priors are not mutated.

Canon effect:

NexusNet now has a concrete influence loop from sanitized federated learning into shadow priors while keeping promotion governed.

### PB-2026-05-03-085 - Hive Executable Dream Cycle Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `tests/test_hive_neural_network_internals.py`

Assimilated dream-cycle contracts:

- Every forward pass now emits a `HiveExecutableDreamCycleLedger`.
- Dreams consume genome, graph, optimizer, loss, and federated-influence refs.
- High-temperature candidate generation is paired with low-temperature critic reviews and sandbox eval plans.
- Active architecture and weight mutation remain forbidden.

Canon effect:

Recursive Neural Dreaming is no longer just canon doctrine. It now has a live substrate artifact over the actual neural runtime evidence.

### PB-2026-05-03-086 - Hive Deep Replay Drilldown Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`

Assimilated replay contracts:

- Every forward pass now emits a `HiveDeepReplayDrilldownLedger`.
- Drilldowns cover graph nodes, parameter refs, optimizer vectors, genome genes, forward paths, backward paths, and promotion readiness.
- The Control Panel replay chain and scorecard expose the new replay surface.

Canon effect:

Operator replay now reaches inside neural-network internals instead of stopping at high-level forward-pass counts.

### PB-2026-05-03-087 - Hive Durable Storage Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_network_internals.py`

Assimilated storage contracts:

- Every forward pass now emits a `HiveDurableStorageLedger`.
- Storage records bind artifact roles to refs, checksums, signature requirements, restore-query state, and retention policy.
- Project-root-only storage is mandatory; user-profile cache storage is explicitly forbidden.

Canon effect:

The substrate now has indexed-storage evidence for replay and restore instead of only loose artifact files.

### PB-2026-05-03-088 - Hive Checkpoint Coverage Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `tests/test_hive_neural_network_internals.py`

Assimilated checkpoint contracts:

- Every forward pass now emits a `HiveCheckpointCoverageLedger`.
- The ledger requires restore validation, diff preview, and prompt/tool snapshot coverage for each new runtime ledger.
- Active restore remains blocked.

Canon effect:

Checkpoint/rewind coverage now follows the new runtime ledgers rather than only the older forward-pass artifacts.

### PB-2026-05-03-089 - Hive Runtime Decision Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `tests/test_hive_neural_network_internals.py`

Assimilated runtime-decision contracts:

- Every forward pass now emits a `HiveRuntimeDecisionLedger`.
- AO/expert decisions consume substrate artifact refs for graph, genome, optimizer, tensor kernel, and layer stack.
- Direct local state reads are recorded as forbidden and empty.

Canon effect:

Downstream AO/expert runtime behavior now has a decision artifact based on neural substrate evidence instead of receipts alone.

### PB-2026-05-03-090 - Hive Backend Quantization Execution Ledger

Status: live_substrate_implementation
Source refs:

- `nexusnet/hive/substrate.py`
- `nexusnet/hive/__init__.py`
- `ui/control-panel/app.js`
- `tests/test_hive_neural_network_internals.py`

Assimilated backend/quantization contracts:

- Every forward pass now emits a `HiveBackendQuantizationExecutionLedger`.
- The ledger records backend candidates, quantization trials, benchmark scorecards, and selected shadow backend metadata.
- Raw KV values and raw weights are not stored, and active backend mutation is forbidden.

Canon effect:

NexusNet now has a live shadow execution lane for runtime backend and quantization experiments that can later feed gated promotion.

### PB-2026-05-04-091 - Corrected Hierarchical Hive MoE Articulation

Status: locked_clarification
Source refs:

- Operator-selected external articulation in the current post-book thread.
- Operator correction that NexusNet must use open-source, open-weight, or otherwise distillation-approved teacher sources only.
- PB-2026-05-01-014 Hive Neural Substrate v0.
- PB-2026-05-02-017 Hive-Wide Neuroplasticity Fabric.
- PB-2026-05-02-018 Fractal Mini-Brain Hierarchy.
- PB-2026-05-02-019 Temporary Child Expert And Retention Review Rule.
- PB-2026-05-02-020 Ivy-Grade Parent Retirement After Child Outperformance.
- PB-2026-05-03-024 Mandatory Sanitized Federated Hive Learning.
- PB-2026-05-03-081 through PB-2026-05-03-090 runtime substrate ledgers.
- `https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html`
- `https://fe-static.deepseek.com/chat/transparency/deepseek-v3.2-model-card-0414-EN.pdf`
- `https://openai.com/policies/terms-of-use/`
- `https://support.claude.com/en/articles/12326764-can-i-use-my-outputs-to-train-an-ai-model`
- `https://ai.google.dev/gemini-api/terms`

Clarification:

The quoted hierarchical Hive MoE output is useful as an external articulation, but it is not accepted as NexusNet canon as written. The canonized version is a NexusNet-specific correction:

NexusNet is a governed hierarchical hive MoE neural harness built on a hive-wide connected substrate. Its root brain, O brains, AO brains, expert Mini-NexusNet brains, tool-facing workers, evaluators, memory planes, runtime kernels, and governance components are not isolated lane silos. Lanes are functional views and sparse-routing contracts only. Every node remains connected through the Neural Bus, HiveBlackboard, memory planes, replay ledgers, checkpoints, and governed policy contracts.

The corrected articulation must include mandatory sanitized federated learning. Production NexusNet deployments contribute only sanitized artifact metadata, performance signals, evaluation deltas, failure classes, routing priors, trust scores, and other privacy-filtered learning evidence. Raw prompts, raw outputs, private files, secrets, local paths, private screenshots, personal identifiers, and unredacted logs must not federate. Federated influence remains shadow-first until secure aggregation, poisoning checks, privacy review, sandbox/eval proof, governance review, checkpoint/rewind coverage, and human approval allow promotion.

Recursive Neural Dreaming as a universal protocol is available hive-wide. It is not locked behind one lane, one AO, one expert family, or one foundry component. Any routed node can request dreaming, research, critique, sandbox/eval, or candidate generation. Dreaming uses high-temperature candidate generation and lower-temperature independent review, then routes candidate changes through sandbox/eval/governance/checkpoint gates before any protected state can change.

The child-retention and parent-retirement rules remain mandatory. Newly generated child experts, child AOs, child orchestrators, or merged Mini-NexusNet brains are temporary on first use. Permanent retention requires Ivy-grade teacher review, parent comparison, sandbox/eval evidence, regression proof, rollback plan, and operator/governance approval. If a retained child greatly outperforms one parent, the other parent, or both, the respective parent-retirement decision must be made through the same Ivy-grade review and archive-not-delete rollback rule.

The articulation must also include runtime substrate ledgers and backend/quantization evidence. NexusNet's current substrate canon includes tensor-runtime, layer/block stack, distillation-loop, federated-influence, executable-dream-cycle, deep-replay, durable-storage, checkpoint-coverage, runtime-decision, and backend/quantization ledgers. Any future hierarchical Hive MoE description is incomplete if it ignores these ledgers, because they are the auditable internal nervous system for the neural substrate.

Licensing-safe teacher source rule:

NexusNet teacher councils, distillation targets, training datasets, synthetic examples, and model-output supervision must use open-source, open-weight, or otherwise distillation-approved sources only. Approved sources must have explicit rights for the intended use, including training, fine-tuning, distillation, derivative product development, or internal model improvement as applicable. Models with anti-distillation, anti-competitive-model, no-training-output, no-automated-extraction, or unclear rights are blocked from teacher-output training unless separate written permission or a reviewed license exception exists.

DeepSeek is the canonical example of a source family that can be considered for this lane only after the exact model/API channel and current license are verified. Current DeepSeek Open Platform terms state that inputs and outputs may be applied to training other models, including model distillation, and the current DeepSeek V3.2 model card states that open-source repository assets including model weights and code are licensed under MIT. That does not make every future DeepSeek route automatically approved; it means DeepSeek-style permissive or explicit distillation-approved licensing fits the intended NexusNet teacher-source rule after version-specific verification.

OpenAI, Anthropic, Gemini/Grounding, and other providers with restrictions against competitive model development, training on outputs, or training on grounded results are not valid NexusNet teacher-output sources for distilling NexusNet's own general-purpose model unless their current terms are changed or a written license allows it. They may still be used for non-training operator assistance, ordinary inference, research reading, comparison, or non-competitive tooling when permitted by their terms and by NexusNet policy.

Canon effect:

This canonizes the corrected articulation, not the raw quote. The accepted formal phrase is: governed hierarchical hive MoE neural harness with teacher-bootstrapped formation, hive-wide neuroplasticity, sparse routing, Recursive Neural Dreaming, mandatory sanitized federated learning, sandboxed promotion, checkpoint/rewind governance, child-retention, parent-retirement, runtime substrate ledgers, backend/quantization evidence, and licensing-safe teacher source controls.

Rollback or sidebar rule:

If a future source, repo, model card, or provider term contradicts the licensing-safe teacher source rule, that source must be blocked or side-barred for training/distillation use until reviewed. Existing derived artifacts from a disallowed source must be quarantined, provenance-marked, and excluded from training promotion.

### PB-2026-05-04-092 - Subsystem Teacher Pairing Matrix

Status: locked_clarification
Source refs:

- Operator request for a document covering teacher pairings per expert, per AO, and per O.
- `docs/NEXUSNET_TEACHER_PAIRING_MATRIX_2026-05-04.md`
- `nexusnet/teachers/teacher_registry_v2026_live.yaml`
- `nexusnet/teachers/expert_training_regimens.yaml`
- `nexusnet/teachers/teacher_routing_policy.yaml`
- `docs/teachers_historical_vs_live.md`
- `tests/test_teacher_pairing_matrix_document.py`

Clarification:

NexusNet now has a canon-facing Subsystem Teacher Pairing Matrix that documents O-level teacher pairings, AO-level teacher pairings, and expert-level teacher pairings in one place. The matrix preserves the hive-wide connected substrate rule: pairings are used for training, contrast, critique, routing, and promotion review, but they do not create isolated lane ownership or disconnect any node from the NeuralBus, HiveBlackboard, substrate ledgers, replay, checkpoint/rewind, Recursive Neural Dreaming, or sanitized federation.

Expert-level teacher pairings are registry-backed by the live v2026 teacher registry. AO-level and O-level pairings are canon-aligned v0 derived pairings based on the existing expert registry, source-book AO canon, and post-book substrate doctrine. They should remain readable documentation until a later runtime registry promotes them into structured machine-readable state with sandbox/eval evidence.

Canon effect:

Teacher formation now has a single cross-layer reference document for Root/O brains, AO brains, expert Mini-NexusNets, auxiliary teacher paths, dual-teacher contrast, Critique Expert arbitration, bounded LFM2 coaching, licensing-safe teacher source rules, temporary child retention, parent retirement, and archive-not-delete rollback.

Rollback or sidebar rule:

If a future runtime registry contradicts this document, the registry must cite a newer addendum/ledger entry, sandbox/eval evidence, and governance approval. Any teacher source that fails open-source, open-weight, or otherwise distillation-approved license review remains blocked from training and distillation regardless of where it appears in the pairing matrix.

### PB-2026-05-04-093 - Teacher Roster Current-Model Refresh

Status: code_backed_candidate
Source refs:

- Operator-provided current-model review of the teacher-pairing matrix.
- `docs/NEXUSNET_TEACHER_PAIRING_MATRIX_2026-05-04.md`
- `nexusnet/teachers/teacher_registry_v2026_live.yaml`
- `nexusnet/teachers/capability_cards.py`
- `nexusnet/teachers/teacher_benchmark_fleets.yaml`
- `tests/test_teacher_pairing_matrix_document.py`
- `tests/test_teacher_registry.py`
- `tests/test_teacher_routing.py`
- `tests/test_teacher_arbitration.py`
- `https://huggingface.co/moonshotai/Kimi-K2.6`
- `https://mistral.ai/news/mistral-small-4`
- `https://docs.mistral.ai/models/model-cards/mistral-medium-3-5-26-04`
- `https://api-docs.deepseek.com/news/news260424`
- `https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro`
- `https://github.com/QwenLM/Qwen3`
- `https://huggingface.co/Qwen/Qwen3-Coder-Next`
- `https://mistral.ai/news/devstral-2-vibe-cli`
- `https://huggingface.co/nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16`
- `https://huggingface.co/mistralai/Voxtral-Small-24B-2507`
- `https://github.com/openai/whisper`
- `https://owasp.org/www-project-top-10-for-large-language-model-applications/`
- `https://www.liquid.ai/blog/liquid-foundation-models-v2-our-second-series-of-generative-ai-models`

Clarification:

The teacher-pairing matrix structure remains accepted, but the live teacher roster is refreshed to current v0.1 source-backed candidates. Kimi K2.6 replaces the older Kimi research/vision/browser contrast slot. Mistral Small 4 replaces deprecated Magistral Small 1.2 as the default planning/strategy contrast. DeepSeek-V4-Pro becomes the high-stakes governance, analysis, and critique professor; DeepSeek-V4-Flash becomes the runtime/router/federation professor. DeepSeek-R1-Distill-Qwen-32B remains useful as compact/local contrast, not the default dean for every reasoning surface. DeepSeek-V2-Lite is retained as fallback-only.

The live coding stack keeps Qwen3-Coder-Next and Devstral 2, with Devstral Small 2 as the Apache-clean fallback and Mistral Medium 3.5 as a high-compute license-gated council candidate. Multimodal and audio rows remain strong with Nemotron Omni plus Qwen3-VL, and Voxtral Small plus Whisper-Large-V3, subject to license/hardware review where required.

Ambiguous teacher names are no longer live anchors. Code LLaMA-Secure is blocked until exact public model identity, license, and provenance are verified. Intent-BERT and LLaMA-Historian-tuned are treated as historical/internal placeholders, with live rows using NexusNet-owned or license-cleared `NexusNet-Intent-BERT-v0` and `NexusNet-Historian-v0`. RecurrentGemma-style memory training must use an owned or license-cleared derivative represented as `NexusNet-RecurrentMemory-v0`.

Security training must combine LLM teachers with deterministic validators and corpora, including CodeQL, Semgrep/OpenGrep, OWASP LLM Top 10, and unit/security tests. DreamerV3 and MuZero are algorithmic simulation professors, not ordinary chat-style LLM teachers. LFM2 remains a license-gated efficiency coach and cannot override correctness, safety, grounding, or high-risk review.

Canon effect:

The live v2026 teacher registry and pairing matrix now represent the current v0.1 roster. This is code-backed by tests and registry updates, but remains a current-model candidate layer rather than immutable final canon because model cards, licenses, and production suitability can change.

Rollback or sidebar rule:

If any refreshed model card, license, commercial term, or provider route fails the open-source/open-weight/distillation-approved rule, that teacher is blocked or side-barred from training/distillation immediately. Existing derived artifacts from a disallowed source must be provenance-marked, quarantined, and excluded from promotion.

### PB-2026-06-03-094 - Harness Contract And Agent Identity Preflight

Status: candidate

Entry metadata:

- entry_id: `PB-2026-06-03-094`
- date_added: `2026-06-03`
- source_refs:
  - Local video-watcher evidence for `YTDown_YouTube_YES-Harness-Self-optimization-w-9B-LLM-L_Media_aaViBfjnh78_001_1080p.mp4`
  - Local video-watcher evidence for `YTDown_YouTube_Unlock-Autonomous-AI-Agents-with-auth-md_Media_Dqp_b8GHLXU_001_1080p.mp4`
  - `https://arxiv.org/abs/2605.30621`
  - `https://github.com/workos/auth.md`
  - `docs/assimilation/videos/2026-06-03/01-harness-contract-agent-identity-preflight-spec.md`
- original_book_status: not present as a standalone target in the 2026-04-28 source book.
- delta_type: new video-derived assimilation target and implementation doctrine.
- affected_lanes: agent harnesses, agentic pipeline runtime, tool action harness, provider registry, identity and permission gates, self-improvement layer, Control Panel/canon scorecards.
- implementation_refs: proposed first under `nexusnet/agents/harnesses/contract.py`, with read-only integration into `nexusnet/agents/pipelines/service.py`, `nexusnet/tools/action_harness.py`, existing harness ledgers, and canon/control surfaces.
- validation_refs: future `tests/test_harness_contract_preflight.py`, `tests/test_agentic_pipeline_runtime.py`, `tests/test_tool_action_harness.py`, `tests/test_harness_improvement_ledger.py`, and any Control Panel/API scorecard tests added with the surface.
- security_or_policy_gates: no raw secrets, no raw private prompts/outputs, no direct model update, scoped identity only, sandbox/eval/provenance/security review before promotion.
- rollback_or_sidebar_rule: if activation, adherence, identity, scope, source, or privacy evidence fails, side-bar the target or keep it as review-only evidence; any generated artifacts from unsafe runs must be provenance-marked and excluded from protected-state promotion.

Clarification:

NexusNet should assimilate the combined YES Harness and auth.md lesson as a governed preflight and evidence ledger. Harness availability is not equivalent to harness benefit. A run can fail because the required skill, prompt, memory pack, tool policy, or eval context never loaded, or because the agent loaded the harness but ignored it. Long-running agents also need discoverable, scoped, auditable identity and credential delegation before they touch APIs, MCP servers, private tools, or high-risk actions.

The accepted target is a **Harness Contract And Agent Identity Preflight**. Before an agentic pipeline block, tool action, or harness-backed run is considered eligible to proceed, NexusNet should know which harness artifacts are required, which artifacts were actually loaded, whether the trajectory followed them, which identity or delegated account is acting, what scopes are available, whether the account is claimed or owner-bound, and whether raw secrets were kept out of the ledger.

Implementation doctrine:

Add this as an additive contract layer, not as a replacement pipeline. A future `HarnessContractLedger` should record required artifacts, activation evidence, adherence evidence, identity evidence, and an allow/block/review-required decision. The first implementation should be non-mutating: it can block unsafe or incomplete runs and create review-gated self-improvement candidates, but it must not update prompts, skills, routes, credentials, model weights, node registries, or production runtime state.

The preflight should consume the existing harness provider registry, harness model router, agentic pipeline runtime, tool action harness, permission service, sandbox service, artifact trust gates, and self-improvement queue. It should report metrics similar to skill-load rate, harness-adherence failure, and loaded-pass rate, plus identity-scope failures and raw-secret violations. Those metrics should become read-only canon/control-plane evidence before any active promotion behavior is considered.

Canon effect:

This adds a new video-derived assimilation target to the post-book canon: NexusNet agents must eventually prove both harness activation and harness adherence, and must carry scoped, auditable agent identity before governed tool/API work. The target strengthens existing self-improvement, harness-ledger, sandbox, permission, and policy gates. It does not authorize autonomous self-modification, direct fine-tuning, credential storage, or bypass of current review gates.

Rollback or sidebar rule:

If the target cannot be implemented without raw secret storage, unredacted private data, uncontrolled credential delegation, direct protected-state mutation, or bypass of existing sandbox/eval/governance gates, it remains side-barred as research evidence only. Any future implementation must be disabled or rolled back if contract evidence becomes unreliable, if source assumptions fail, or if identity/scope proof cannot be replayed.

### PB-2026-06-03-095 - Dedicated Memory Model Knowledge Lane

Status: candidate

Entry metadata:

- entry_id: `PB-2026-06-03-095`
- date_added: `2026-06-03`
- source_refs:
  - `https://arxiv.org/abs/2605.15156`
  - `https://www.marktechpost.com/2026/05/26/memo-a-modular-framework-for-training-a-dedicated-memory-model-on-new-knowledge-without-modifying-llm-parameters/`
  - `docs/assimilation/online/2026-06-03/01-memory-adapter-trace-voice-assimilation-spec.md`
- original_book_status: not present as a standalone target in the 2026-04-28 source book.
- delta_type: new paper-derived memory and knowledge assimilation target.
- affected_lanes: Knowledge Artifact Compiler, engram memory, retrieval planner, source provenance, evals, memory model training, Control Panel/canon evidence.
- implementation_refs: proposed design under the knowledge or memory subsystem before any training implementation; expected integration with `nexusnet/knowledge/`, `nexusnet/memory/engram_index.py`, and `nexusnet/retrieval/planner.py`.
- validation_refs: future memory-lane tests for source eligibility, reflection QA generation, bounded query protocol, KAC fallback, and shadow-only incremental updates.
- security_or_policy_gates: rights-cleared corpora only, no private/raw/unredacted data, no citation claims without source provenance, no protected-state mutation from memory-model output.
- rollback_or_sidebar_rule: if source rights, provenance, eval advantage, or privacy gates fail, keep the target as research evidence or side-bar the trained memory artifact.

Clarification:

NexusNet should assimilate MeMo as a dedicated memory-model lane, not as a replacement for retrieval, KAC, or source-to-claim provenance. The useful pattern is a frozen executive model that queries a smaller memory model trained on approved corpora. The lane is valuable where repeated retrieval is noisy, expensive, or weak at cross-document synthesis.

Implementation doctrine:

First add a design contract and tests. Eligible corpora must pass source digest, rights, freshness, and privacy filters. Reflection QA generation should preserve source refs and cover direct facts, consolidated multi-fact relationships, entity surfacing, and cross-document synthesis. At inference, the executive should use a bounded grounding, entity-identification, and support-seeking protocol. Memory-model answers remain secondary recall evidence unless linked back to KAC citations.

Canon effect:

This adds a candidate parametric-memory lane to NexusNet's knowledge stack while keeping KAC/RAG as the citation and fallback authority.

Rollback or sidebar rule:

Any memory model trained on unclear-rights, private, stale, or unsupported material must be quarantined and excluded from promotion. Any incremental merge that regresses accuracy or provenance must remain shadow-only.

### PB-2026-06-03-096 - Persistent Adapter State Fabric

Status: candidate

Entry metadata:

- entry_id: `PB-2026-06-03-096`
- date_added: `2026-06-03`
- source_refs:
  - `https://arxiv.org/abs/2606.02437`
  - `https://huggingface.co/papers/2606.02437`
  - `docs/assimilation/online/2026-06-03/01-memory-adapter-trace-voice-assimilation-spec.md`
- original_book_status: adapter and fine-tuning direction existed as themes; persistent adapter identity/provenance/residency fabric is post-book.
- delta_type: new PEFT-derived adapter lifecycle target.
- affected_lanes: AO/expert/Mini-NexusNet personalization, adapter forge, runtime routing, provider registry, teacher/foundry lanes, Control Panel replay, rollback.
- implementation_refs: proposed adapter passport and registry before any runtime adapter attachment.
- validation_refs: future adapter-passport, adapter-registry, shadow-routing, rollback, and leakage-prevention tests.
- security_or_policy_gates: source rights, base-model compatibility, privacy classification, eval deltas, residency, no raw weight logging, no policy override.
- rollback_or_sidebar_rule: incompatible, unproven, or unclear-rights adapters are blocked or side-barred; previous adapter selection must remain rollback-restorable.

Clarification:

NexusNet should treat PEFT adapters as governed persistent state modules for AOs, experts, Mini-NexusNets, operators, task families, tool habits, and memory-like updates. This is not permission for uncontrolled per-user fine-tuning. Every adapter needs identity, revision, source lineage, allowed base models, eval suite, route constraints, residency, and rollback metadata before use.

Implementation doctrine:

Add an adapter passport schema and registry first. The registry may enumerate candidate adapters without loading weights. Adapter routing stays shadow-only until compatibility, eval, privacy, rollback, and source-rights checks pass. Adapter evidence should appear in runtime decision ledgers and Control Panel replay, but raw adapter weights must not appear in logs, federated packets, or ordinary canon evidence.

Canon effect:

This adds a high-priority candidate substrate for persistent personalized model state across the hive while preserving governance and rollback.

Rollback or sidebar rule:

Any adapter that fails provenance, base compatibility, eval, privacy, or residency checks is blocked. If an approved adapter regresses behavior or violates policy, routing rolls back to the previous adapter or base model.

### PB-2026-06-03-097 - Trace-Optimized Secure Self-Evolving Agent Runtime

Status: candidate

Entry metadata:

- entry_id: `PB-2026-06-03-097`
- date_added: `2026-06-03`
- source_refs:
  - `https://youtu.be/NGfvTlU2T5E?si=4bz8lpPk7Ex3k7_L`
  - `https://developer.nvidia.com/blog/deploy-self-evolving-agents-for-faster-more-secure-research-with-a-hermes-agent-and-nvidia-nemoclaw/`
  - `docs/assimilation/online/2026-06-03/01-memory-adapter-trace-voice-assimilation-spec.md`
- original_book_status: secure agents, harnesses, skills, sandboxes, and self-improvement existed as themes; the trace-to-skill secure runtime pattern is post-book.
- delta_type: new video/blog-derived implementation doctrine extending `PB-2026-06-03-094`.
- affected_lanes: harness contract, self-improvement layer, sandbox/runtime policy, credential brokering, trace/eval observability, snapshot/restore, Control Panel.
- implementation_refs: proposed extension to future `HarnessContractLedger`, trace collector/analyzer, shadow optimizer, policy evidence, and snapshot/restore evidence.
- validation_refs: future tests for credential brokering, network allowlists, trace-to-skill review gates, snapshot redaction, restore proof, and Control Panel trace evidence.
- security_or_policy_gates: policy-as-code runtime enforcement, no raw secrets, no public/private data exfiltration, shadow-first self-improvement, redacted traces only.
- rollback_or_sidebar_rule: any runtime that relies on prompt-only security, stores raw credentials, or mutates learned state without review remains side-barred.

Clarification:

NexusNet should assimilate the Hermes/NemoClaw pattern as a secure self-evolving runtime made of model, harness, and policy-enforced runtime layers. The important target is not NVIDIA-specific dependency adoption; it is the pattern of learned skills and memories inside a sandbox where credentials are brokered outside the agent, network access is allowlisted, traces are exportable, and learned state survives rebuilds through redacted snapshots.

Implementation doctrine:

Extend `PB-2026-06-03-094` with runtime-policy evidence, trace refs, learned-state refs, and snapshot/restore refs. Trace analysis may propose skill, memory, prompt, or policy candidates, but those candidates are review-required and shadow-only. Public/private data mixing requires ETL mirrors, read-only boundaries, source labels, and exfiltration controls.

Canon effect:

This strengthens the existing harness contract by adding the secure runtime and trace-to-candidate improvement loop needed to make self-evolving agents auditable.

Rollback or sidebar rule:

If policy enforcement, credential brokering, trace redaction, or snapshot credential filtering cannot be proven, the target remains research-only. Learned skills or memories can be disabled or rolled back independently.

### PB-2026-06-03-098 - Dialogue Voice Scene Alignment Lane

Status: research_only

Entry metadata:

- entry_id: `PB-2026-06-03-098`
- date_added: `2026-06-03`
- source_refs:
  - `https://arxiv.org/abs/2605.30993`
  - `https://huggingface.co/papers/2605.30993`
  - `https://swanaigc.github.io/#/swanvoice`
  - `docs/assimilation/online/2026-06-03/01-memory-adapter-trace-voice-assimilation-spec.md`
- original_book_status: voice/audio/multimodal direction existed as broad themes; long-form multi-speaker dialogue scene alignment is post-book.
- delta_type: new audio and multimodal research target.
- affected_lanes: video/audio assimilation, transcript alignment, multi-agent replay, narration/presentation, Control Panel artifacts.
- implementation_refs: proposed audio-scene schema and forced-alignment evaluation lane only; no synthesis implementation approved.
- validation_refs: future tests for speaker consent refs, timestamp/speaker-turn preservation, synthetic-output evidence exclusion, and content-accuracy gates.
- security_or_policy_gates: voice consent, audio rights, watermark/provenance, content-accuracy review, no impersonation, no synthetic speech as factual evidence.
- rollback_or_sidebar_rule: remain research_only until consent, data/model availability, and content-accuracy gates are proven.

Clarification:

SwanVoice is useful for the audio/multimodal roadmap, but not as an unrestricted voice-cloning target. The accepted research target is dialogue-scene alignment: speaker turns, pause-aware alignment, long-form continuity, and optional narrated replay for multi-agent or operator artifacts.

Implementation doctrine:

First define an audio-scene schema with speaker ids, consent refs, turn ids, pause markers, alignment refs, style labels, and provenance. Generated speech is presentation output only and cannot satisfy evidence gates. The forced-alignment portion is more immediately useful than synthesis because it can improve video/audio assimilation and replay.

Canon effect:

This adds a low-priority research-only audio lane that may later support narration, simulation playback, and transcript alignment after safety and rights gates pass.

Rollback or sidebar rule:

Any unauthorized voice cloning, copyrighted/private audio training, undisclosed synthetic speech, or content-accuracy failure blocks promotion and side-bars the target.

### PB-2026-06-03-099 - Focal Coding Model Lane

Status: candidate

Entry metadata:

- entry_id: `PB-2026-06-03-099`
- date_added: `2026-06-03`
- source_refs:
  - `https://thenewstack.io/jetbrains-mellum2-open-source-coding-model/` (operator pointer; access returned HTTP 403 during this pass)
  - `https://blog.jetbrains.com/ai/2026/06/mellum2-goes-open-source-a-fast-model-for-ai-workflows/`
  - `https://huggingface.co/JetBrains/Mellum2-12B-A2.5B-Thinking`
  - `https://arxiv.org/abs/2605.31268`
  - `docs/assimilation/online/2026-06-03/02-focal-coding-and-hardware-router-assimilation-spec.md`
- original_book_status: coding assistants, local models, teacher rosters, provider routing, and edge workload routing existed as themes; a Mellum2-style focal coding route is post-book.
- delta_type: new open-weight coding-model assimilation target for local or low-cost coding subagents.
- affected_lanes: coding subagents, provider registry, local model routing, edge workload router, ToolActionHarness, evals, teacher/source-rights review, Control Panel evidence.
- implementation_refs: proposed model passport and shadow route before any production use; expected integration with provider registry, model route policy, edge workload routing, and coding-eval scorecards.
- validation_refs: future tests for license/card review, coding category routing, sandbox-only tool use, repo test pass/fail scoring, rollback to existing provider, and Control Panel route evidence.
- security_or_policy_gates: exact model card and license review, no teacher/distillation use without explicit rights, no autonomous writes outside existing ToolActionHarness gates, no production route without local benchmark and regression proof.
- rollback_or_sidebar_rule: if license, provenance, benchmark, hardware-fit, or sandbox evidence is insufficient, keep Mellum2 as a side-barred candidate or shadow-only route.

Clarification:

NexusNet should assimilate Mellum2 as a focal coding model lane, not as a replacement for NexusBrain, the governance layer, or existing high-capability teachers. The useful pattern is a specialized coding model that can serve local completion, patch drafting, test generation, narrow refactor proposals, code review triage, and harness update suggestions where hardware, latency, privacy, or cost make smaller routes valuable.

Implementation doctrine:

Add a model passport first. The passport must record model id, source refs, license/card status, parameter/active-parameter notes where verified, allowed tasks, blocked tasks, compatible runtimes, eval suites, hardware requirements, and rollback provider. Route Mellum2 only through shadow coding tasks until it beats or justifies its route against existing coding providers on NexusNet-owned fixtures. Proposed writes remain normal tool-action proposals and must pass the same sandbox, test, review, and governance gates as any other agent output.

Canon effect:

This adds a candidate model-route lane for specialized coding work and gives the Edge Workload Router a concrete open-weight coding model target to evaluate.

Rollback or sidebar rule:

Any Mellum2 route that fails license/provenance review, local benchmark proof, test regression checks, or write-gate compliance remains side-barred. Distillation or training use is blocked unless source rights explicitly permit it.

### PB-2026-06-03-100 - Hardware-Aware Local Model Fit Recommender

Status: candidate

Entry metadata:

- entry_id: `PB-2026-06-03-100`
- date_added: `2026-06-03`
- source_refs:
  - `F:/NexusNet/NexusNet/.codex-remote-attachments/019e8ca7-5bc8-7781-b1f5-227dab1adfd2/8432ce0e-4327-45d7-a426-767ec8291463/1-Photo-1.jpg`
  - `https://github.com/Pavelevich/llm-checker/blob/main/README.md`
  - `https://www.npmjs.com/package/llm-checker`
  - `docs/assimilation/online/2026-06-03/02-focal-coding-and-hardware-router-assimilation-spec.md`
- original_book_status: edge workload routing and hardware-aware runtime selection existed as themes; an external CLI-style local model recommender is post-book.
- delta_type: new hardware-fit and model-recommendation control-plane target.
- affected_lanes: Edge Workload Router, provider registry, model catalog, local backend/quantization evidence, operator Control Panel, privacy/redaction, package provenance review.
- implementation_refs: proposed NexusNet-owned hardware snapshot schema and model-fit scorecard before any external CLI adapter; optional read-only `llm-checker` adapter only after package, dependency, and license review.
- validation_refs: future tests for deterministic hardware fixtures, category-based ranked recommendations, low-memory blocking, redacted hardware evidence, package-review-required state, and no automatic downloads or installs.
- security_or_policy_gates: no automatic global npm install, no automatic model download, no raw serial numbers or user paths in shared evidence, no telemetry/federation of private hardware identifiers, explicit operator approval before external CLI execution.
- rollback_or_sidebar_rule: if package provenance, license, dependency, privacy, or recommendation correctness cannot be proven, keep `llm-checker` as an external reference only and implement the core recommender natively.

Clarification:

The screenshot points to `llm-checker` as a practical operator workflow: detect hardware, then recommend models by task category such as coding. NexusNet should assimilate the capability, not blindly depend on the npm package. The durable target is a hardware-aware model-fit recommender that can explain which local models, quantizations, and backends are viable for a specific machine and task.

Implementation doctrine:

Add a local hardware snapshot schema with CPU, RAM, GPU, VRAM, backend, OS, accelerator, and privacy-redaction fields. Add a model-fit scorecard that maps task categories to candidate models using memory budget, quantization fit, expected latency, privacy class, cost, license status, and current eval evidence. External `llm-checker` can be evaluated as an optional read-only adapter after package integrity, dependency, binary, license, and telemetry review. NexusNet must not use this lane to install packages, download models, mutate provider routes, or federate raw hardware identifiers without approval.

Canon effect:

This adds a concrete control-plane target for making local model selection explainable and hardware-aware, strengthening the existing Edge Workload Router and backend/quantization ledger.

Rollback or sidebar rule:

If hardware detection leaks private identifiers, recommendations are not reproducible, the npm package cannot pass provenance/license review, or the adapter attempts installs/downloads without approval, the external adapter is blocked and the native scorecard remains the only accepted target.

## Non-Promotion Rule

External claims do not become NexusNet canon just because they appear in a transcript, repo, video, paper, benchmark, or assistant recommendation.

They must pass:

- Source identity and URL pinning.
- Teacher-source rights and license review, including no anti-distillation or competitive-model restriction for training/distillation use.
- Privacy review where data is involved.
- Security and sandbox review.
- Eval and regression proof.
- Implementation or integration evidence where promoted.
- Addendum or ledger entry.

## Future Regeneration Rule

When updated raw chat exports become available, the complete book can be regenerated through `tools/build_nexusnet_chat_canon_book.py`. Until then, this addendum remains the canonical home for post-2026-04-28 deltas.

