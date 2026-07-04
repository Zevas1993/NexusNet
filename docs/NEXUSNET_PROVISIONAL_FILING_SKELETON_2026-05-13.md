# NexusNet Provisional Filing Skeleton - 2026-05-13

Status: drafting skeleton for patent-practitioner review.

This document is a non-code provisional filing skeleton derived from the NexusNet walkthrough. It is not legal advice, not a patentability opinion, and not a final claim set. It is written to give a patent drafter a mechanism-first description of the invention territory.

## Title

System and Method for Governed Sparse-Routed Artificial Intelligence Harness with Multi-Plane Memory and Reversible Self-Improvement

## Field

The disclosed subject matter relates to artificial intelligence orchestration, multi-agent and multi-model systems, governed tool use, memory routing, evaluation-gated self-modification, sparse operational routing, sandboxed candidate promotion, and reversible checkpointing for artificial intelligence systems.

## Background

Current artificial intelligence systems can generate outputs, call tools, retrieve external context, and use multiple models. However, many such systems treat model prompting, tool selection, memory retrieval, agent delegation, and self-improvement as loosely connected behaviors. The system often lacks a traceable state spine that shows what entered the system, what representation was created, what components were selected, what constraints applied, what evidence was used, what changed, and how to reverse a harmful change.

Existing systems also commonly blur memory types. Conversation history, source documents, retrieved snippets, policy rules, user preferences, experimental research, evaluation results, and system-change candidates may be placed into one context stream or one retrieval store. This makes it difficult to determine whether a memory item is authoritative, stale, private, speculative, license-restricted, or safe to use for training or modification.

Existing multi-agent systems can call several agents, but they often lack governed sparse routing. A task may be broadcast too broadly, routed by a static rule, or delegated without a reliable record of why a specific node was selected or rejected. This makes the system harder to audit, harder to reproduce, and harder to limit by cost, privacy, safety, or capability.

Existing self-improving or adaptive systems can propose prompt changes, memory updates, tool changes, routing changes, or model changes. However, they may lack a shadow-only candidate state, sandbox testing, evaluation gates, promotion gates, quarantine states, and rollback records. Without these controls, a proposed improvement can become an uncontrolled mutation.

Accordingly, there is a need for an artificial intelligence harness that converts inputs into typed activations, routes them through a sparse selected subset of governed components, retrieves memory from separated memory planes, applies policy and evaluation gates, records trace and checkpoint information, tests candidate changes in shadow or sandbox states, and permits rollback when a promoted change fails.

## Summary

In one embodiment, an input is received by an artificial intelligence harness and converted into a typed activation signal. The typed activation signal can include an intent label, task type, capability requirements, privacy class, risk class, source identifiers, memory requirements, policy labels, trace identifier, and candidate-change status.

A neural core, also referred to as NexusNet or NexusBrain, receives the typed activation and controls the task path. A router selects a sparse subset of operational components, including expert nodes, Assistant Orchestrators, memory planes, tools, evaluators, teacher models, runtime backends, sandbox services, and policy gates. The router can score candidate components using capability match, permission state, certification state, cost, latency, privacy scope, reliability history, memory access requirements, policy risk, and current quarantine state.

The selected components communicate through a typed bus and shared task state rather than through an untracked prompt exchange. The system retrieves memory from multiple separated memory planes, such as episodic memory, semantic memory, procedural memory, policy memory, evidence and trust memory, temporal lineage memory, dream or simulation memory, and candidate research memory. Retrieved memory items carry provenance, status, freshness, permission, and confidence labels.

Policy gates and evaluation gates govern execution. The system can determine whether the task is allowed to proceed, must be answered without tools, requires human approval, must remain in shadow mode, requires a sandbox, must use a teacher fallback, or must be blocked. Outputs are generated only through the governed path and are recorded in a trace ledger.

Candidate improvements are not immediately applied to protected state. A candidate improvement can be source-pinned, privacy-classified, license-classified, security-reviewed, and tested in shadow or sandbox mode. The candidate remains shadow-only unless required sandbox tests, replay tests, teacher review, policy checks, evaluation gates, and promotion gates pass. Checkpoint records preserve the prior state so that a promoted change can be rolled back if later failure conditions occur.

In further embodiments, the harness can use recursive dreaming, teacher review, expert councils, student birth records, and governed training candidates to grow new expert components. Over repeated governed cycles, promoted student experts, routing policies, adapters, memory encoders, or other components may be consolidated toward a native mixture-of-experts model lineage in which the NexusNet harness becomes the neural substrate of the resulting model.

## Detailed Description

### Overview Of The Mechanism Spine

The invention should be understood as a stateful governed harness, not as a single chatbot and not as a mere collection of agents. The mechanism spine is:

1. Receive an input or proposed system change.
2. Convert the input into a typed activation.
3. Attach trace identity, risk labels, privacy labels, and required capability labels.
4. Retrieve memory only from appropriate memory planes.
5. Score available operational nodes and select a sparse active subset.
6. Route typed signals over a bus to the selected subset.
7. Apply policy, artifact, protocol, memory, runtime, and operator gates.
8. Select tools, models, runtimes, evaluators, and sandboxes only when permitted.
9. Generate an output or candidate disposition through the neural core.
10. Record route, memory, gate, output, and checkpoint evidence in ledgers.
11. Keep candidate changes shadow-only until sandbox and promotion gates pass.
12. Permit rollback by restoring the prior checkpoint state when failure conditions are detected.

Each stage changes system state in a defined way. A patent reader should be able to follow the task from raw input, to activation, to selected circuit, to gated execution, to output or candidate status, to trace ledger, and to promotion or rollback.

### System 100: Governed Artificial Intelligence Harness

System 100 is a computer-implemented artificial intelligence harness. It coordinates models, expert nodes, Assistant Orchestrators, memory systems, tools, runtime backends, evaluators, sandboxes, policy gates, teacher systems, ledgers, and operator interfaces.

Input: user tasks, system events, tool results, runtime signals, memory updates, research candidates, error traces, dream outputs, teacher critiques, federation signals, or proposed system changes.

Output: user-facing responses, tool requests, document outputs, runtime decisions, memory candidates, training candidates, expert student records, promotion decisions, quarantine decisions, rollback decisions, or trace records.

Decision criteria: task type, risk class, privacy class, capability requirements, evidence sufficiency, policy result, memory provenance, component certification, sandbox result, evaluation score, teacher agreement, operator approval, and rollback availability.

State change: the harness creates or updates activation records, selected-node records, memory references, policy results, output records, candidate records, checkpoint records, and trace ledger entries.

### Input Interface 102

Input interface 102 receives data from a chat interface, application programming interface, command-line request, browser observation, file event, tool event, runtime monitor, research monitor, federation message, or operator action.

Input: raw text, structured request, file metadata, tool result, sensor observation, model output, evaluation result, or proposed update.

Output: normalized input record containing source, time, actor, declared purpose, input type, and initial privacy and risk labels.

Decision criteria: whether the input is user-supplied, system-supplied, remote-supplied, private, public, executable, sensitive, training-eligible, or blocked.

State change: a raw event becomes an input record with a trace identifier and initial classification.

### Activation Builder 110

Activation builder 110 converts the normalized input record into a typed activation signal. The typed activation is the first structured representation used by the harness.

Input: normalized input record, operator context, policy registry, available memory summaries, available capability registry, and trace identifier.

Output: typed activation containing intent, task type, risk vector, privacy class, required capabilities, memory needs, policy labels, cost constraints, latency constraints, source status, allowed execution mode, and candidate-change status.

Decision criteria: whether the input requests information, generation, tool use, memory update, system change, training data creation, expert birth, runtime change, policy change, or external sharing.

State change: unstructured input becomes a typed activation that can be routed, logged, replayed, and evaluated.

### Neural Core 120

Neural core 120 is the central authority. In NexusNet, this authority can be called NexusNet or NexusBrain. It does not merely call a model. It controls routing, memory use, policy review, deliberation, output approval, candidate disposition, and promotion authority.

Input: typed activation, router results, memory references, node outputs, policy results, evaluator results, teacher critiques, checkpoint status, sandbox results, and operator decisions.

Output: selected execution mode, approved active set, final output, candidate record, promotion decision, rollback decision, or request for more evidence.

Decision criteria: confidence, risk, memory sufficiency, expert disagreement, policy result, evaluation result, teacher agreement, privacy class, runtime reliability, checkpoint availability, and operator approval.

State change: the neural core updates the task state, decides whether to continue or stop recurrent deliberation, and authorizes only allowed output or candidate state transitions.

### Neural Bus 130

Neural bus 130 carries typed signals between the neural core, router, memory planes, hive nodes, tools, runtimes, evaluators, sandboxes, and ledgers.

Input: typed activations, memory requests, route requests, node calls, tool requests, policy requests, evaluation requests, sandbox requests, checkpoint requests, and output requests.

Output: typed messages containing sender identity, receiver identity, message type, payload summary, permission state, trace reference, and result status.

Decision criteria: whether sender and receiver are authorized, whether the message type is allowed, whether the payload crosses a privacy or permission boundary, and whether the message must be recorded for replay.

State change: hidden prompt-to-agent communication is replaced by traceable signal passing.

### Hive Node Registry 140

Hive node registry 140 stores operational components that can participate in a task. Nodes can include O-level orchestrators, Assistant Orchestrators, expert capsules, Mini-NexusNets, tool adapters, model adapters, runtime backends, evaluators, sandboxes, policy gates, teacher systems, memory services, and VisualOps surfaces.

Input: node definitions, capability records, permission records, memory scope records, teacher lineage records, certification records, quarantine records, runtime health, and scorecards.

Output: candidate node list for routing and node metadata for policy checks.

Decision criteria: node type, capability fit, permission scope, privacy scope, write scope, certification state, quarantine state, cost, latency, reliability, memory access, concurrency safety, teacher lineage, and evaluation coverage.

State change: a task receives an inspectable set of eligible nodes rather than an unbounded collection of agents.

### Cortex Router 150

Cortex router 150 selects a sparse subset of operational nodes for the task. Sparse selection means the system activates only the components needed for the current task rather than broadcasting to every expert, every memory plane, every model, and every tool.

Input: typed activation, candidate node list, memory requirements, policy constraints, component scorecards, cost limits, latency limits, privacy labels, and risk labels.

Output: selected active set, rejected node list, route score records, routing rationale, fallback options, and escalation flags.

Decision criteria: capability match, confidence, risk, privacy compatibility, permission compatibility, memory access, runtime availability, cost, latency, certification, quarantine state, prior failure history, teacher fit, and required evaluation coverage.

State change: the system creates a temporary task circuit. The selected circuit may include the neural core, one or more orchestrators, selected Assistant Orchestrators, selected expert capsules, selected memory planes, selected tools, selected runtimes, selected evaluators, and selected gates.

### Sparse Routing As A Harness-Level Mixture

The sparse routing disclosed here is not limited to token routing inside a model. The harness routes operational components. An expert capsule, memory plane, runtime backend, evaluator, teacher, tool adapter, policy gate, sandbox, or visualization component can be selected or rejected for a task.

The router can therefore create a task-specific operational circuit. For a legal drafting task, the circuit may select a policy expert, source-evidence memory, procedural drafting memory, citation evaluator, and privacy gate. For a code-change task, the circuit may select a coder expert, security expert, test evaluator, sandbox, checkpoint gate, and rollback ledger. For a candidate training task, the circuit may select a SelfTrainingAO, teacher council, dream records, hidden evals, sandbox runner, promotion gate, and lineage ledger.

### HiveBlackboard 155

HiveBlackboard 155 is a shared task-state surface. It stores residual state across recurrent deliberation loops.

Input: activation state, selected nodes, memory references, expert outputs, disagreements, policy findings, runtime results, evaluator results, checkpoint references, and pending questions.

Output: current task state for the neural core and selected nodes.

Decision criteria: whether a state item is current, stale, disputed, policy-blocked, private, candidate-only, or ready for output.

State change: partial results, disagreements, missing evidence, and route changes become visible state rather than hidden context.

### Orchestrator Layer 160

The orchestrator layer includes O-level orchestrators and Assistant Orchestrators. O-level orchestrators coordinate broad task structures under the neural core. Assistant Orchestrators coordinate domain workflows, handoffs, evidence collection, and gate preparation.

Input: task activation, selected route, node outputs, memory references, policy requirements, and desired deliverable.

Output: decomposed workflow, handoff plan, evidence requirements, selected expert calls, review requests, and candidate disposition requests.

Decision criteria: task complexity, dependency order, required domains, required evidence, need for parallel work, permission boundaries, and gate requirements.

State change: a large task becomes an ordered or partially parallel workflow with traceable assignments and handoffs.

### Expert Capsule Layer 170

Expert capsules are specialist cognition units. Each expert has a domain boundary, permission scope, memory scope, teacher lineage, evaluation coverage, health history, and promotion or retirement state.

Input: expert-specific task slice, relevant memory references, permission scope, policy constraints, and expected output type.

Output: expert answer, critique, evidence request, disagreement record, confidence score, proposed tool request, proposed memory update, or candidate improvement.

Decision criteria: domain fit, evidence sufficiency, confidence, contradiction with other experts, policy risk, permission scope, and need for teacher review.

State change: the active task circuit gains specialized work products without giving any single expert final authority.

### Mini-NexusNet Units 175

A Mini-NexusNet is a nested specialist brain instance associated with an expert, child expert, or domain subsystem. It can have its own memory scope, teacher pairings, evaluation records, health history, and improvement loop while remaining subordinate to the neural core.

Input: domain task, domain memory, expert state, teacher feedback, eval results, and parent lineage.

Output: domain output, student candidate, route suggestion, training request, or retirement challenge against a parent path.

Decision criteria: domain performance, hidden eval results, teacher comparison, regression behavior, safety outcome, cost, latency, and rollback readiness.

State change: expert behavior can evolve through governed child and parent records rather than untracked prompt edits.

### Multi-Plane Memory System 180

Multi-plane memory system 180 separates different kinds of memory so that the harness can use each memory item according to its status and permission.

Input: memory request, activation labels, privacy class, source requirements, freshness requirements, evidence requirements, and allowed use mode.

Output: retrieved memory references, evidence snippets, source labels, confidence labels, contradiction labels, freshness labels, and use restrictions.

Decision criteria: memory plane, source provenance, freshness, authority status, privacy scope, license status, training eligibility, contradiction state, and relevance score.

State change: memory is not injected as undifferentiated context. It becomes a labeled set of references that can be accepted, rejected, cited, quarantined, or used only as candidate context.

### Memory Planes

The memory planes can include:

1. Episodic memory for events, sessions, traces, interactions, and prior outcomes.
2. Semantic memory for durable facts, concepts, definitions, and project doctrine.
3. Procedural memory for workflows, skills, task methods, and repeatable operations.
4. Policy memory for safety rules, permission rules, governance rules, license rules, and operator restrictions.
5. Evidence and trust memory for source provenance, scorecards, evaluation records, artifact trust, protocol trust, and confidence labels.
6. Temporal and lineage memory for when something was created, modified, superseded, contradicted, promoted, demoted, or rolled back.
7. Working memory for the current task state.
8. Dream and simulation memory for recursive dreaming outputs, rehearsal traces, adversarial cases, and curriculum seeds.
9. Candidate research memory for external ideas, models, papers, tools, and methods that are not yet adopted.
10. Federated lesson memory for approved redacted lessons from other deployments.

### Memory Operating System 185

Memory operating system 185 determines what kind of memory exists, where it lives, how fresh it is, how it can be used, whether it may influence outputs, and whether it may influence training or mutation.

Input: memory item, source record, permission record, use request, task activation, and policy state.

Output: allowed use mode, blocked use mode, required citation, required review, quarantine state, or forgetting recommendation.

Decision criteria: authority level, privacy class, source trust, age, contradiction, license status, training eligibility, user consent, and relationship to protected state.

State change: memory receives an explicit use status rather than becoming silent model context.

### Recurrent Deliberation Loop 190

Recurrent deliberation loop 190 lets the harness refine task state before external action.

Input: activation, selected active set, retrieved memory, expert outputs, disagreements, policy results, evaluator signals, and blackboard state.

Output: refined route, additional memory request, expert re-query, critique request, teacher review request, policy escalation, output approval, or stop condition.

Decision criteria: confidence threshold, risk threshold, unresolved disagreement, missing evidence, memory sufficiency, policy state, maximum loop count, cost limit, latency limit, and operator checkpoint requirement.

State change: the task state can improve through controlled loops without permitting unbounded recursive action.

### Immune Governance Kernel 200

Immune governance kernel 200 applies policy, safety, privacy, license, artifact trust, protocol trust, memory trust, runtime trust, and operator-approval rules.

Input: activation, selected route, proposed action, proposed tool use, proposed memory use, proposed output, proposed candidate change, artifact metadata, protocol metadata, and checkpoint status.

Output: allow, deny, clamp to safer mode, require sandbox, require teacher fallback, require human approval, require redaction, require checkpoint, quarantine, or block.

Decision criteria: policy match, prohibited action, privacy risk, write authority, external sharing, artifact provenance, unsafe serialization risk, protocol identity, source license, memory authority, checkpoint availability, and operator consent.

State change: proposed behavior and effective allowed behavior are separated. A proposed route may be reduced, blocked, or held until evidence exists.

### Tool And Runtime Selection 210

Tool and runtime selection 210 chooses models, providers, local runtimes, tools, adapters, or execution backends when the task requires them and governance permits them.

Input: activation, task requirements, selected route, available runtime registry, available tool registry, policy constraints, cost constraints, privacy constraints, hardware state, model passports, and reliability scorecards.

Output: selected tool, selected model, selected runtime, fallback runtime, no-tool decision, teacher fallback decision, or sandbox-only execution decision.

Decision criteria: capability fit, local versus remote privacy requirements, cost, latency, determinism, context length, quantization support, hardware fit, license, certification state, failure history, and required traceability.

State change: execution capability is bound to a task-specific permission and trace record.

### Output And Action Gate 220

Output and action gate 220 controls anything leaving the internal deliberation path.

Input: proposed answer, proposed tool call, proposed file operation, proposed memory update, proposed training record, proposed external message, proposed system change, or proposed candidate disposition.

Output: emitted answer, approved action request, redacted output, blocked output, review request, or candidate record.

Decision criteria: user intent, privacy state, policy state, confidence, citation sufficiency, tool permission, checkpoint status, and whether the output changes protected state.

State change: an internal result becomes either an external effect, a blocked effect, or a candidate-only record.

### Trace Ledger 230

Trace ledger 230 records the lifecycle of a task or candidate.

Input: input record, activation, memory references, route scores, selected nodes, rejected nodes, policy results, tool and runtime choices, expert outputs, evaluator results, checkpoint references, output record, and candidate disposition.

Output: replayable trace record, audit report, VisualOps state, promotion evidence, rollback evidence, or diagnostic record.

Decision criteria: which events are material, which events contain private data, which events must be redacted, which events support promotion, and which events support rollback.

State change: task execution becomes inspectable, replayable, and reviewable instead of transient.

### Checkpoint And Rewind Ledger 240

Checkpoint and rewind ledger 240 preserves the pre-change state when an action may alter protected memory, routing, policy, expert behavior, runtime configuration, release pointer, training state, or model component.

Input: proposed change, affected components, prior state, memory references, route state, policy state, candidate record, evaluation state, and release state.

Output: checkpoint record, rewind record, rollback pointer, restoration plan, rollback decision, or rollback completion record.

Decision criteria: whether the action is reversible, whether prior state is known, whether dependencies are captured, whether rollback has been tested, and whether failure conditions are defined.

State change: a system change becomes reversible or is blocked until reversibility evidence exists.

### Candidate Improvement Engine 250

Candidate improvement engine 250 creates structured candidates from failures, user corrections, dream outputs, teacher critiques, runtime signals, benchmark results, research findings, or federation signals.

Input: source event, trace ledger references, source provenance, license labels, privacy labels, expected benefit, affected components, and risk labels.

Output: candidate record identifying type, source, rights, risk, affected capability, expected value, required tests, required gates, rollback plan, and allowed mode.

Decision criteria: source trust, license permission, privacy status, evidence strength, affected component risk, expected value, feasibility, and whether protected state would change.

State change: a vague improvement idea becomes a governed candidate with status.

Candidate types can include memory update candidates, route policy candidates, prompt policy candidates, tool candidates, runtime candidates, evaluator candidates, training data candidates, adapter candidates, expert candidates, Mini-NexusNet candidates, governance rule candidates, or model-component candidates.

### Shadow And Sandbox Service 260

Shadow and sandbox service 260 tests candidates without mutating protected production state.

Input: candidate record, sandbox environment, replay cases, hidden evals, teacher comparison requirements, policy checks, security checks, and rollback plan.

Output: sandbox result, shadow result, replay result, teacher comparison, evaluation score, failure signature, quarantine recommendation, promotion recommendation, or rejection recommendation.

Decision criteria: pass/fail result, regression behavior, safety result, privacy result, license result, artifact trust, teacher agreement, hidden eval performance, replay performance, cost, latency, and rollback readiness.

State change: the candidate remains shadow-only, becomes canary-requested, becomes promotion-ready, is rejected, is blocked, is archived, or is quarantined.

### Evaluation Gate 270

Evaluation gate 270 determines whether an output, candidate, student, route, memory change, tool change, runtime change, or model component has enough evidence to proceed.

Input: candidate record, tests, task-suite results, benchmark results, teacher critiques, expert critiques, replay results, hidden eval results, policy results, and operator requirements.

Output: pass, fail, partial pass, require more evidence, require teacher review, require human approval, quarantine, or promote request.

Decision criteria: score thresholds, regression thresholds, coverage requirements, confidence intervals, teacher agreement, safety failures, privacy failures, unsupported claims, and rollback availability.

State change: candidate status advances or is blocked based on evidence, not on self-assertion.

### Promotion Gate 280

Promotion gate 280 decides whether a candidate can affect active system behavior.

Input: candidate record, sandbox result, evaluation gate result, policy result, artifact trust result, protocol trust result, checkpoint record, rollback plan, teacher review, and operator approval.

Output: promoted, canary, shadow-only, side-barred, archived, rejected, blocked, or rolled back.

Decision criteria: all required gates passed, no blocking policy result, rollback available, operator approval present where required, no unresolved high-risk regression, and promotion scope bounded.

State change: a candidate may become active only after the gate changes its state from candidate to active or canary. Otherwise it remains non-authoritative.

### VisualOps Control Surface 290

VisualOps control surface 290 exposes the truthful state of routes, memory, gates, candidates, evals, sandboxes, checkpoints, rollbacks, runtime choices, federation, and promotion state to an operator.

Input: trace ledger records, route records, memory records, policy records, candidate records, sandbox records, eval records, checkpoint records, and runtime records.

Output: operator-visible route view, evidence view, blocked-state view, missing-evidence view, promotion view, rollback view, and audit export.

Decision criteria: what state is safe to show, what must be redacted, what requires operator approval, what is missing, what is blocked, and what can be rolled back.

State change: hidden automation state becomes reviewable operational evidence.

### Federation Boundary 300

Federation boundary 300 allows deployments to exchange approved redacted lessons without sharing raw private prompts, files, credentials, or protected local data.

Input: local trace summaries, failure signatures, scorecards, model or route performance summaries, approved lessons, privacy filters, opt-out rules, and remote lesson records.

Output: redacted deltas, sanitized lessons, accepted remote candidate signals, rejected remote signals, quarantine records, or local review requests.

Decision criteria: consent, opt-out status, privacy classification, source trust, secure aggregation availability, poisoning risk, local policy, and local acceptance gates.

State change: remote learning remains candidate influence until local governance accepts or rejects it.

### Recursive Dreaming Service 310

Recursive dreaming service 310 generates possible scenarios, training cases, adversarial cases, replay cases, curriculum seeds, or candidate solutions in a bounded state.

Input: failure traces, weak expert scorecards, teacher disagreement, memory gaps, runtime problems, policy friction, underrepresented tasks, and operator-approved dream objectives.

Output: dream agenda, dream trace, simulated case, adversarial case, curriculum seed, evaluation seed, training candidate, or blocked dream artifact.

Decision criteria: target gap, safety risk, novelty, evidence utility, source status, training eligibility, policy status, and whether output remains candidate-only.

State change: dream outputs become traceable candidate material and do not directly mutate production behavior.

### SelfTrainingAO And Growth Engine 320

SelfTrainingAO and growth engine 320 turn approved traces, dream outputs, teacher labels, replay failures, and curriculum items into training candidates without permitting uncontrolled self-modification.

Input: approved evidence, teacher critiques, dream artifacts, candidate records, license labels, privacy labels, curriculum goals, student lineage, and evaluation requirements.

Output: training candidate, student birth record, expert child record, adapter candidate, route policy candidate, memory encoder candidate, or model-component candidate.

Decision criteria: source permission, training eligibility, teacher agreement, hidden eval coverage, safety result, regression result, parent comparison, rollback plan, and promotion scope.

State change: a developmental path is created from evidence to student candidate to sandbox result to promotion or retirement review.

### Teacher School And Teacher Council 330

Teacher school and teacher council 330 provide external or internal critique, labels, comparisons, and scoring for outputs and candidate students.

Input: candidate output, student behavior, parent behavior, teacher outputs, hidden eval cases, replay tasks, and scoring rubric.

Output: teacher labels, critique record, comparison score, disagreement record, curriculum recommendation, promotion recommendation, or retirement challenge.

Decision criteria: teacher reliability, source license, disagreement rate, task fit, benchmark result, hidden eval result, and regression behavior.

State change: teacher judgment becomes evidence and does not become final authority unless accepted through governance.

### Native Model Growth Substrate 340

Native model growth substrate 340 describes a long-term embodiment in which successful students, expert components, adapter policies, route policies, memory encoders, and model components are consolidated toward a native mixture-of-experts model lineage.

Input: promoted student records, teacher lineage, parent comparison records, hidden eval results, replay results, route records, memory records, and governance decisions.

Output: retained student, retired parent, consolidated expert component, native model component, MoE lineage record, or rejected consolidation.

Decision criteria: repeated surpass evidence, safety result, regression result, rollback plan, parent retirement evidence, teacher replacement evidence, and operator approval.

State change: the harness functions as a governed developmental substrate. In an end-state embodiment, the model born from this process carries NexusNet capabilities as part of its neural substrate, including sparse routing, memory governance, recursive dreaming, teacher lineage, evaluation gates, federation boundaries, VisualOps evidence, and rollback posture.

### Status Labels

A component, memory item, route, candidate, student, or artifact can carry one or more status labels. Useful status labels include raw, normalized, active, selected, rejected, blocked, quarantine, shadow-only, sandbox-only, canary-requested, active-requested, promoted, rolled back, archived, side-barred, demoted, retired, source-pinned, license-reviewed, privacy-reviewed, eval-passed, eval-failed, teacher-reviewed, operator-approved, and rollback-ready.

These labels prevent the system from treating unreviewed material as authoritative.

## Example Operation

This example follows one complete path from user task to possible improvement.

### Step 1: User Task

A user asks the system to prepare a technical explanation of a planned product feature and to identify whether the feature should update system memory.

Input state: raw user request.

Operator: input interface 102.

Output state: normalized input record with source, time, actor, task type, and initial privacy class.

### Step 2: Typed Activation

Activation builder 110 converts the request into a typed activation. The activation identifies the task as a technical explanation with a possible memory-update side effect.

Input state: normalized input record.

Operator: activation builder 110.

Output state: activation containing intent, capability requirements, memory requirements, privacy class, risk class, policy labels, and trace identifier.

### Step 3: Memory Plane Lookup

Neural core 120 requests memory from multi-plane memory system 180. The memory operating system permits semantic memory, procedural memory, policy memory, and evidence/trust memory. It blocks use of private unrelated episodic memory and marks candidate research as non-authoritative.

Input state: activation and memory request.

Operator: memory operating system 185.

Output state: labeled memory references with provenance, freshness, confidence, and use restrictions.

### Step 4: Sparse Node Selection

Cortex router 150 scores the hive node registry. It selects a technical expert, Memory Weaver, policy gate, evidence evaluator, and VisualOps surface. It rejects unrelated audio, vision, and runtime-specialist nodes because they are not needed.

Input state: activation, memory references, policy constraints, and node registry.

Operator: Cortex router 150.

Output state: selected active set, rejected node list, route score record, and routing rationale.

### Step 5: Policy Gate

Immune governance kernel 200 determines that answering the user is allowed, but directly updating durable memory is not allowed without candidate creation and review.

Input state: proposed answer path and possible memory-update path.

Operator: immune governance kernel 200.

Output state: answer path allowed, memory update clamped to candidate-only.

### Step 6: Tool Or Runtime Selection

Tool and runtime selection 210 determines that no external write tool is required. If model generation is needed, it chooses an allowed runtime based on privacy, cost, latency, certification, and traceability.

Input state: approved route and runtime requirements.

Operator: tool and runtime selection 210.

Output state: selected runtime or no-tool decision.

### Step 7: Output Generation

The selected expert and neural core generate the technical explanation. The evidence evaluator checks whether the explanation is supported by retrieved memory and whether unsupported claims should be removed.

Input state: selected active set, labeled memory, policy result, and runtime result.

Operator: neural core 120 with selected nodes.

Output state: proposed user output.

### Step 8: Output Gate

Output and action gate 220 confirms that the answer can be shown to the user, while the memory update must remain a candidate.

Input state: proposed user output and proposed memory update.

Operator: output and action gate 220.

Output state: emitted answer and memory-update candidate record.

### Step 9: Trace Ledger

Trace ledger 230 records the input, activation, memory references, selected nodes, rejected nodes, policy result, runtime choice, output, and candidate record.

Input state: all material events from the task.

Operator: trace ledger 230.

Output state: replayable trace and VisualOps evidence.

### Step 10: Sandbox Candidate

Candidate improvement engine 250 structures the memory update as a candidate. Shadow and sandbox service 260 tests whether adding the memory improves future retrieval without leaking private material or contradicting existing canon.

Input state: candidate memory update and trace references.

Operator: candidate improvement engine 250 and sandbox service 260.

Output state: sandbox result, eval result, and promotion recommendation.

### Step 11: Promotion Or Rollback

If the candidate passes policy, evidence, sandbox, evaluation, and operator gates, promotion gate 280 promotes it with a checkpoint record from checkpoint and rewind ledger 240. If later failure detection shows that the memory caused incorrect retrieval, the checkpoint record permits rollback.

Input state: candidate result, gate results, checkpoint record, and operator approval if required.

Operator: promotion gate 280 and checkpoint and rewind ledger 240.

Output state: promoted memory item, rejected candidate, quarantine record, or rollback record.

## Figures

The following drawing set should be prepared as plain black-and-white line drawings. The drawings should use simple rectangular boxes, circles only where functionally useful, solid black lines, arrowheads, and reference numerals. Do not use color, shading, grayscale fills, gradients, photographs, screenshots, decorative icons, cartoon elements, perspective effects, 3D shapes, or ornamental backgrounds. Text should be minimal and should identify functional components rather than marketing names.

### Figure 1: System Architecture

Purpose: show the governed harness as a complete system.

Black-and-white drawing layout:

1. Draw input interface 102 at the left.
2. Draw activation builder 110 after the input interface.
3. Draw neural core 120 centrally.
4. Draw neural bus 130 as a horizontal line or bus connected to the neural core.
5. Draw hive node registry 140 above or below the bus.
6. Draw Cortex router 150 connected to the registry and bus.
7. Draw memory planes 180 as a grouped stack connected to the neural core and router.
8. Draw hive nodes 160 and 170 as grouped boxes connected to the bus.
9. Draw immune governance kernel 200 between the selected nodes and external effects.
10. Draw tool and runtime selection 210 connected after governance.
11. Draw output and action gate 220 before final output 225.
12. Draw trace ledger 230 and checkpoint and rewind ledger 240 connected to each major stage.
13. Draw VisualOps control surface 290 connected to the ledgers.

Caption draft: Figure 1 illustrates a governed sparse-routed artificial intelligence harness in which an input is converted into a typed activation, routed by a neural core and router over a neural bus to selected memory planes and hive nodes, constrained by governance gates, executed by permitted tools or runtimes, emitted through an output gate, and recorded in trace and checkpoint ledgers.

### Figure 2: Sparse Routing Flow

Purpose: show how the router creates a sparse active set.

Black-and-white drawing layout:

1. Draw typed activation 112 entering route scorer 152.
2. Draw candidate node pool 142 as a larger box containing expert nodes, Assistant Orchestrators, memory planes, tools, runtimes, evaluators, and sandboxes.
3. Draw scoring and filtering block 154.
4. Draw decision criteria list 156 with capability, permission, privacy, risk, cost, latency, certification, quarantine, and reliability.
5. Draw selected node subset 158 as a small group of selected boxes.
6. Draw rejected node record 159 as a separate record.
7. Draw selected subset 158 connecting to neural bus 130.
8. Draw route ledger entry 232 receiving both selected and rejected records.

Caption draft: Figure 2 illustrates sparse routing in which a typed activation is scored against a candidate node pool, filtered by capability and governance criteria, reduced to a selected node subset, and recorded with selected and rejected node evidence.

### Figure 3: Memory Plane Diagram

Purpose: show separated memory authority and status.

Black-and-white drawing layout:

1. Draw memory operating system 185 at the center.
2. Draw separate memory plane boxes around it: episodic memory 181, semantic memory 182, procedural memory 183, policy memory 184, evidence and trust memory 186, temporal lineage memory 187, dream memory 188, and candidate research memory 189.
3. Draw memory request 114 entering memory operating system 185.
4. Draw provenance and status labeler 190 between the planes and output.
5. Draw labeled memory references 192 leaving the memory operating system.
6. Draw blocked or restricted memory record 194 as a separate output.

Caption draft: Figure 3 illustrates a multi-plane memory system in which a memory operating system retrieves from separated memory planes and outputs provenance-labeled memory references while blocking or restricting memory that lacks permission, freshness, authority, or trust status.

### Figure 4: Shadow Improvement Flow

Purpose: show that improvements are candidates before they can affect protected state.

Black-and-white drawing layout:

1. Draw source event 252 at the left.
2. Draw candidate improvement engine 250.
3. Draw source pinning 253, privacy review 254, license review 255, and security review 256 as sequential gates.
4. Draw candidate record 257.
5. Draw shadow and sandbox service 260.
6. Draw evaluation gate 270.
7. Draw promotion gate 280.
8. Draw possible outcomes: rejected 281, blocked 282, archived 283, shadow-only 284, canary 285, promoted 286, and rolled back 287.
9. Draw checkpoint and rewind ledger 240 connected before promotion.
10. Draw trace ledger 230 connected to every stage.

Caption draft: Figure 4 illustrates a shadow improvement flow in which a proposed improvement is source-pinned, reviewed, structured as a candidate, tested in shadow or sandbox mode, evaluated, and either rejected, blocked, archived, retained as shadow-only, moved to canary, promoted, or rolled back.

### Figure 5: Checkpoint And Rewind Flow

Purpose: show reversible system change.

Black-and-white drawing layout:

1. Draw protected state before change 241.
2. Draw proposed promoted change 242.
3. Draw checkpoint creation 243 between the prior state and promoted change.
4. Draw active changed state 244.
5. Draw failure detector 245 receiving trace, eval, runtime, policy, or user-correction signals.
6. Draw rollback decision 246.
7. Draw restored prior state 247.
8. Draw rollback ledger entry 248.
9. Draw VisualOps surface 290 showing checkpoint, failure, rollback decision, and restored state.

Caption draft: Figure 5 illustrates checkpoint and rewind operation in which a prior protected state is captured before promotion, a changed state is monitored for failure conditions, and a rollback decision restores the prior state while recording the rollback in a ledger.

### Figure 6: Developmental Growth Substrate

Purpose: show the long-term artificial-womb embodiment without using decorative imagery.

Black-and-white drawing layout:

1. Draw approved evidence 321, dream artifacts 322, teacher labels 323, replay failures 324, and curriculum items 325 feeding SelfTrainingAO and growth engine 320.
2. Draw student birth record 326.
3. Draw child expert or Mini-NexusNet 327.
4. Draw teacher council 330 and hidden evals 331 connected to the child component.
5. Draw sandbox service 260 and promotion gate 280.
6. Draw retained student 332, retired parent 333, rejected student 334, and native MoE lineage 340 as possible outcomes.
7. Draw checkpoint and rewind ledger 240 connected to parent retirement and native lineage consolidation.

Caption draft: Figure 6 illustrates a governed developmental substrate in which approved evidence, dreams, teacher labels, replay failures, and curriculum items create student candidates that are tested, evaluated, retained, rejected, or consolidated toward a native mixture-of-experts model lineage.

## Additional Filing Notes

### Claimable Mechanism Themes

The strongest claimable themes are concrete mechanisms rather than broad results:

1. Typed activation creation from heterogeneous inputs.
2. Sparse operational routing over a node registry.
3. Separation of memory into permissioned memory planes.
4. Governance gates that can clamp proposed behavior to safer allowed behavior.
5. Trace ledgers that record selected nodes, rejected nodes, memory references, gates, outputs, and candidate status.
6. Shadow-only and sandbox-only candidate states before promotion.
7. Evaluation-gated promotion of memory, route, tool, expert, training, runtime, and model-component candidates.
8. Checkpoint and rewind records that permit rollback of promoted changes.
9. Operator-visible VisualOps state for route, memory, gate, sandbox, eval, promotion, and rollback evidence.
10. Developmental growth path from evidence and dreams to student candidates and possible native model consolidation.

### Terms To Use Carefully

The terms Hive Mind, artificial womb, Recursive Dreaming, student birth, and native model substrate are useful for understanding the invention, but filing language should tie them to technical mechanisms:

1. Hive Mind means a connected routed architecture of specialized governed nodes, not uncontrolled collective behavior.
2. Artificial womb means a governed developmental substrate for creating, testing, promoting, retiring, and consolidating child experts or native model components.
3. Recursive Dreaming means bounded generation of simulation, curriculum, replay, adversarial, or training candidates, not ungated production mutation.
4. Student birth means creation of a governed child expert, Mini-NexusNet, adapter, route policy, memory encoder, or model component with lineage and promotion records.
5. Native model substrate means a future embodiment in which promoted components consolidate into a model lineage carrying the harness capabilities.

### Matters For Patent Practitioner Review

A patent practitioner should review:

1. Whether the title should include Hive Mind, NexusNet, reversible self-improvement, or developmental model substrate.
2. Which components are currently implemented, scaffolded, planned, or future embodiments.
3. Which examples should be included in the provisional filing to support later claims.
4. Whether the native mixture-of-experts consolidation path should be included as an embodiment, a dependent claim direction, or a future continuation strategy.
5. Whether figure reference numerals and captions should be harmonized with any existing patent packet drawings.
6. Whether public disclosure, inventorship, ownership, assignments, open-source dependencies, and prior art have been reviewed before filing.

