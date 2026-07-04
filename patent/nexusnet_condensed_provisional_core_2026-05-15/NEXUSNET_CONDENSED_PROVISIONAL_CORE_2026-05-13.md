# Title

System and Method for Governed Sparse-Routed Artificial Intelligence Harness with Multi-Plane Memory and Checkpointed State Transitions

## Field

The disclosed subject matter relates to artificial intelligence orchestration, multi-agent and multi-model systems, governed tool use, sparse component routing, permissioned memory retrieval, policy-gated execution, evaluation-gated candidate promotion, trace recording, checkpointing, rollback where prior state and dependencies are preserved, and failure marking where restoration is not available.

## Background

Artificial intelligence systems may use a model, a retrieval store, a tool-calling layer, or multiple agents. However, many systems lack a single reviewable state path that defines what entered the system, what structured representation was created, what controller acted on it, what components were selected, what constraints governed execution, what state changed, and what terminal condition ended the operation.

Existing systems can blur several distinct behaviors. A user request, a tool action, a memory update, a route change, a prompt change, a model change, and a training candidate may all be processed through loosely related mechanisms. This makes it difficult to audit why an output was produced, why a component was selected, whether a memory item was permitted, whether a proposed improvement was safe, or how to reverse a harmful change.

Existing multi-agent systems can also over-broadcast tasks or delegate without a traceable selection rationale. Existing retrieval systems may treat source material, private context, policy rules, stale notes, evidence records, and speculative research as equivalent context. Existing self-improvement systems may allow a proposed change to become active without sufficient shadow testing, evaluation, checkpointing, or rollback evidence.

There is therefore a need for a governed artificial intelligence harness that converts raw inputs or proposed changes into typed activation records, sparsely routes governed components into a temporary operational circuit, retrieves memory from separated memory planes, applies policy and evaluation gates, records trace and checkpoint state, and terminates in a grouped disposition, including output disposition, evidence disposition, candidate disposition, or rollback disposition.

## Summary

In one embodiment, an artificial intelligence harness receives a raw input or proposed system change and creates a typed activation record. The typed activation record can include task type, intent, source identity, privacy class, risk class, required capabilities, memory requirements, policy labels, candidate-change status, trace identity, and allowed execution mode.

The harness includes a computer-implemented controller that receives the typed activation record. In some embodiments, the controller is referred to as a neural core, NexusNet, or NexusBrain. In each such embodiment, the controller remains a processor-executed control system that coordinates routing, memory permission, policy review, evaluation, output approval, candidate disposition, checkpointing, and rollback authority according to recorded state and gate results.

A routing service scores available operational components and selects a sparse active subset from the system architecture inventory. The selected subset forms a temporary operational circuit for the current activation.

The harness retrieves memory from separated memory planes rather than from one undifferentiated memory store. Retrieved memory items carry provenance, authority status, freshness, permission, privacy, confidence, contradiction, and allowed-use labels. A memory item may be usable for context, blocked from use, restricted to evidence, prevented from training use, quarantined, or treated as candidate-only.

Policy gates, memory-plane permissions, evaluator gates, artifact trust, protocol trust, candidate-state rules, checkpoint rules, and operator approval rules constrain execution. The same harness can process an ordinary user task and a proposed system change because both are represented as typed activations and both must pass through the same governed state path.

The operation ends in a terminal disposition. Terminal dispositions can be grouped as output dispositions, evidence dispositions, candidate dispositions, and rollback dispositions. The trace ledger and checkpoint ledger record the state path so the result is reviewable and, where prior state and dependencies have been preserved, restorable or revertible.

In some embodiments, candidate promotion and optional growth-component handling are performed using the same typed activation, sparse routing, governance, evaluation, trace, checkpoint, and terminal-disposition framework. When the activation concerns a proposed memory update, route update, tool update, expert update, training example, adapter, or model-component candidate, the harness processes that item as a candidate with shadow, sandbox, evaluation, promotion, and conditional rollback states.

## System Architecture

The system includes the following operational components.

1. Input interface.
2. Activation builder.
3. Computer-implemented controller.
4. Routing service, optionally called Cortex router.
5. Node registry.
6. Neural bus.
7. Shared task state.
8. Multi-plane memory system.
9. Policy and governance gates.
10. Evaluator gates.
11. Tool and runtime selection services.
12. Candidate improvement service.
13. Shadow and sandbox service.
14. Trace ledger.
15. Checkpoint and rollback ledger.
16. Output and action gate.
17. Operator review surface.

The node registry stores governed components that can be routed into an operational circuit, including expert nodes, memory access nodes, tool nodes, runtime nodes, evaluator nodes, policy nodes, candidate nodes, or growth-component nodes. In some embodiments, this registry is referred to as a Hive node registry when the registered components operate as coordinated routed components of the harness.

The input interface receives user tasks, system events, tool results, runtime signals, memory updates, research candidates, dream outputs, teacher critiques, federation signals, or proposed changes. The activation builder converts the input into a typed activation record. The computer-implemented controller controls the operation. The routing service selects a sparse active subset from the node registry. The neural bus carries typed messages between selected components. The shared task state records current activation status, memory references, selected nodes, rejections, policy findings, disagreements, and pending terminal conditions.

The multi-plane memory system supplies permissioned memory references. The policy and governance gates decide what is allowed. Evaluator gates provide evidence about whether outputs or candidates have enough support. Tool and runtime selection services select permitted execution resources. Candidate improvement, shadow, and sandbox services process proposed system changes without immediate mutation of protected state. The trace ledger records what happened. The checkpoint and rollback ledger records prior state, dependency state where available, restoration limits, and rollback information. The output and action gate controls anything leaving the internal harness. The operator review surface exposes route, memory, policy, evaluation, checkpoint, promotion, and rollback state.

## Operating State

The harness maintains operating state for each activation. The operating state can include:

1. Raw input record.
2. Typed activation record.
3. Task state.
4. Privacy and risk labels.
5. Candidate-change status.
6. Selected and rejected node records.
7. Memory reference records.
8. Policy gate records.
9. Evaluation records.
10. Runtime and tool decision records.
11. Output proposal records.
12. Candidate records.
13. Checkpoint records.
14. Rollback records.
15. Terminal disposition records.

The operating state allows the system or an operator to determine what entered, what structure was created, what operator acted, what constraints governed the operation, what changed, and why the operation ended.

## Engine And Controller

The controller is the primary computer-implemented decision service. It can be implemented as one or more processor-executed services that receive the typed activation record, maintain task state, call routing and gate functions, and determine whether to answer, route, retrieve memory, deliberate, call tools, call a runtime, request evaluation, create a candidate, require a sandbox, require approval, block the task, promote a candidate, mark a failure, or roll back a promoted change where rollback prerequisites are present.

Input to the controller can include the activation record, router scores, memory references, selected-node outputs, policy results, evaluator evidence records, teacher evidence records, sandbox results, checkpoint records, runtime records, and operator decisions.

Output from the controller can include an approved active set, allowed execution mode, memory request, tool request, runtime request, output approval, candidate disposition, escalation request, promotion decision, rollback decision, or stop condition.

Decision criteria can include risk, privacy, capability fit, evidence sufficiency, memory permission, node certification, policy result, checkpoint availability, rollback readiness, and operator approval. Confidence scores, evaluator results, and teacher agreement can be used as evidence inputs, but they are not final truth sources unless accepted by the controller and applicable governance gates.

## Typed Activation Record

The typed activation record is the structured representation created from raw input or a proposed system change.

The record can include:

1. Trace identifier.
2. Source identifier.
3. Actor type.
4. Task type.
5. Intent label.
6. Capability requirements.
7. Privacy class.
8. Risk class.
9. Memory requirements.
10. Tool requirements.
11. Runtime requirements.
12. Policy labels.
13. Candidate-change flag.
14. Protected-state impact.
15. Allowed execution mode.
16. Required gates.
17. Expected terminal conditions.

Transformation: raw input becomes a typed activation. The typed activation can then be routed, checked, logged, replayed, evaluated, and resolved into a terminal disposition.

## Sparse Routing

The routing service converts the typed activation into a selected operational circuit. It does this by scoring available components in the node registry and selecting only the subset needed for the current activation.

Sparse means selecting fewer than all eligible components according to scored criteria, while recording selected and rejected components.

Candidate components are drawn from the system architecture inventory and can include any governed component that has declared capability, permission, and state records.

The selection operation can filter out disallowed candidates, rank the remaining candidates according to scoring criteria, select the highest-ranked candidates that satisfy required capability and gate-coverage needs, and then record selected and rejected reasons in the route ledger.

Scoring criteria can include:

1. Capability match.
2. Required permission.
3. Privacy compatibility.
4. Risk compatibility.
5. Memory access scope.
6. Certification state.
7. Quarantine state.
8. Cost.
9. Latency.
10. Reliability history.
11. Prior failure history.
12. Required evaluator coverage.
13. Checkpoint requirement.
14. Operator approval requirement.

Transformation: the typed activation becomes a selected operational circuit. The routing service also records rejected components and the reason each material component was selected or rejected. This distinguishes governed sparse routing from broad agent broadcast.

## Multi-Plane Memory

The memory system separates memory into planes so that memory can be retrieved according to its authority, permission, source, and allowed use.

Memory planes can include:

1. Episodic memory for prior events, sessions, traces, and outcomes.
2. Semantic memory for durable facts, concepts, and definitions.
3. Procedural memory for workflows and repeatable methods.
4. Policy memory for safety, permission, license, and governance rules.
5. Evidence and trust memory for provenance, evaluations, artifact trust, protocol trust, scorecards, and confidence records.
6. Temporal and lineage memory for supersession, ancestry, contradiction, promotion, demotion, and rollback history.
7. Working memory for the current activation.
8. Dream or simulation memory for bounded rehearsal, adversarial, curriculum, and training-candidate material.
9. Candidate research memory for unadopted external ideas or methods.
10. Federated lesson memory for accepted redacted lessons from other deployments.

Each retrieved memory reference can carry labels for provenance, status, freshness, permission, privacy, confidence, contradiction, license, training eligibility, and allowed use. A memory reference may be allowed for answer context, allowed only as evidence, restricted from training, blocked from use, marked stale, marked contradicted, quarantined, or kept candidate-only.

Transformation: the selected circuit receives labeled memory references, not raw unrestricted memory.

## Governance Gates

Governance gates constrain both ordinary outputs and proposed system changes. The gate layer can include policy gates, privacy gates, memory-permission gates, evaluator gates, artifact-trust gates, protocol-trust gates, runtime-trust gates, candidate-state gates, checkpoint gates, and operator-approval gates.

A gate can be rule-based, model-assisted, or hybrid. A rule-based gate applies deterministic conditions such as permission, privacy class, required checkpoint, allowed tool scope, or blocked action type. A model-assisted gate may request a classifier, evaluator, teacher, or scoring model to produce evidence about risk, support, contradiction, or quality. A hybrid gate combines deterministic rules with model-produced evidence, but the gate output remains a recorded control decision such as allow, deny, clamp, sandbox, escalate, quarantine, require more evidence, or require operator approval.

Evaluation sufficiency can be determined by thresholds, required evidence types, mandatory gates, absence of blocking policy results, required memory support, required replay or sandbox evidence, or operator approval. Evaluator evidence can support the decision, but the gate layer still records the control disposition.

A proposed behavior and an allowed behavior are separate. For example, the selected circuit may propose a tool action, memory update, route update, or candidate promotion. Governance may allow it, deny it, clamp it to a safer mode, require a sandbox, require teacher review, require human approval, require redaction, require checkpoint creation, quarantine it, or block it.

Decision criteria can include:

1. Whether the action changes protected state.
2. Whether memory use is permitted.
3. Whether the tool or protocol identity is trusted.
4. Whether the artifact has provenance.
5. Whether the candidate has source, license, privacy, and security review.
6. Whether evaluator evidence is sufficient as evidence rather than final truth.
7. Whether checkpoint records preserve the relevant prior state and dependencies.
8. Whether rollback, failure marking, or partial restoration is available.
9. Whether human approval is required.

Transformation: a proposed route, output, or candidate becomes an allowed action, a restricted action, a blocked action, or a candidate-only state.

## Trace, Checkpoint, And Rollback

The trace ledger records the lifecycle of an activation. It can record the raw input reference, typed activation, selected components, rejected components, memory references, policy results, evaluator evidence records, tool and runtime decisions, output proposal, candidate record, checkpoint record, and terminal disposition.

The checkpoint ledger records prior state before protected state changes. Protected state can include durable memory, routing policy, policy rules, tool permissions, expert behavior, model adapters, runtime settings, release pointers, training state, or model-component candidates. For changes that depend on external models, training processes, datasets, runtime state, or other mutable dependencies, the checkpoint record should identify which dependencies were preserved and which dependencies limit restoration.

A rollback or failure disposition can occur when failure conditions are detected after promotion or activation. Failure conditions can include evaluator failure, policy violation, regression, user correction, runtime failure, privacy failure, security finding, unsupported claim, teacher disagreement, or operator decision.

Transformation: a system change becomes reviewable and conditionally restorable. If a failure condition is met, the rollback ledger can restore a preserved prior state, revert a recorded setting, mark a candidate as failed, quarantine the changed state, or record that full restoration is unavailable because required prior state or dependencies were not preserved.

## Transformation Path

The core machine path is:

1. Raw input or proposed change enters the input interface.
2. The activation builder creates a typed activation record.
3. The controller reads the activation and requests memory, routing, and gate preparation.
4. The memory system retrieves labeled memory references from permitted memory planes.
5. The routing service scores components and creates a sparse selected circuit.
6. The neural bus carries typed messages among selected components.
7. The selected circuit produces a proposed output or candidate disposition.
8. Governance gates determine the allowed execution mode.
9. Evaluator gates determine whether evidence is sufficient.
10. The checkpoint ledger captures prior state when protected state may change.
11. The output and action gate emits, blocks, escalates, or records the result.
12. The trace ledger records the route, memory, gates, output, and terminal disposition.

This path is intentionally the same whether the activation began as a user question, a tool action request, a memory update request, a route change, a training candidate, or an optional model-component candidate.

## Terminal Conditions

The operation ends when the controller and gate layer produce a terminal disposition. Terminal dispositions can be grouped as follows:

1. Output disposition: approved, blocked, redacted, or escalated.
2. Evidence disposition: more evidence required, further evaluation required, teacher review required, operator review required, or memory support insufficient.
3. Candidate disposition: created, shadowed, sandboxed, canary-requested, promoted, rejected, quarantined, archived, retained, or retired.
4. Rollback disposition: restored, reverted where possible, marked failed, quarantined after failure, or recorded as not fully restorable because prior state or dependencies were not preserved.

A terminal disposition is recorded in the trace ledger. If protected state changed or may change, checkpoint or rollback records are also recorded.

## Example Operation

An operator asks the harness to answer a technical question and also asks whether the answer should become durable memory.

First, the input interface receives the raw request and creates a normalized input record. The activation builder creates a typed activation record with a technical-answer task type, a possible memory-update side effect, a privacy class, required technical capability, memory requirements, policy labels, and trace identity.

Second, the controller reads the activation and requests memory lookup. The memory system retrieves semantic memory, procedural memory, policy memory, and evidence/trust memory. It rejects private unrelated episodic memory and marks candidate research memory as non-authoritative.

Third, the routing service scores available components. It selects a technical expert, Memory Weaver, policy gate, evidence evaluator, output gate, trace ledger, and checkpoint service. It rejects unrelated vision, audio, and runtime-specialist components because they are not needed for the activation. The selected components form the operational circuit.

Fourth, the selected circuit prepares a proposed answer and a proposed memory-update candidate. The policy gate allows the answer path but prevents direct durable memory mutation. The possible memory update is clamped to candidate-only status.

Fifth, the evaluator checks the proposed answer against the labeled memory references and produces an evidence input. The output and action gate emits the answer if the answer is supported and permitted by the controller and gates. The trace ledger records the input, activation, memory references, selected components, rejected components, policy results, evaluator evidence, and emitted answer.

Sixth, the candidate improvement service structures the memory update as a candidate record. The candidate record includes source, affected memory plane, privacy status, expected value, required evaluation, and rollback needs. The shadow and sandbox service tests the candidate against replay cases and contradiction checks.

Seventh, if the candidate passes required gates, the promotion gate can promote it to durable memory after checkpoint creation. If the candidate fails, it is rejected, archived, or quarantined. If the candidate is promoted and later causes retrieval errors, the checkpoint and rollback ledger restores the prior memory state only if the relevant prior state and dependencies were preserved. Otherwise, the ledger marks the candidate failed, quarantines the changed state, or records partial restoration.

The same path can handle other proposed changes. If the proposed change is a route policy, tool permission, expert update, training item, adapter, or optional model-component candidate, the typed activation still passes through sparse routing, memory permissions, governance gates, evaluation gates, trace recording, checkpointing, and terminal disposition.

## Protected-State Change Example

An operator or internal review process proposes changing a tool-permission rule so that a selected expert can use a file-writing tool during a future workflow.

First, the proposed permission change enters as a candidate activation rather than as an immediate configuration edit. The activation builder labels it as a protected-state change because it would alter tool authority.

Second, the controller requests the relevant policy memory, prior tool-use traces, failure history, route history, and current permission records. The routing service selects a policy gate, security reviewer, tool governance component, evaluator gate, checkpoint ledger, and operator review surface while leaving unrelated experts inactive.

Third, the gate layer applies hybrid review. Deterministic rules check whether the tool is in an allowed category, whether the proposed write scope is bounded, whether a checkpoint is required, and whether operator approval is mandatory. Model-assisted or evaluator evidence may score whether the proposed permission is overbroad, conflicts with prior failures, or lacks a clear workflow need.

Fourth, the candidate remains shadow-only unless the proposed permission passes policy, evaluator, security, checkpoint, and operator approval gates. If promoted, the checkpoint ledger records the prior permission state and any dependency assumptions. If later traces show unsafe writes or scope drift, the rollback disposition can restore the prior permission state where preserved, revert the setting where possible, quarantine the permission, or mark the candidate failed.

## Alternative Embodiments

### Candidate Promotion And Rollback

In one embodiment, the activation is a proposed system change rather than a user question. The harness creates a candidate record, holds the candidate in shadow-only or sandbox-only state, evaluates the candidate, records checkpoint state, and either promotes, rejects, archives, quarantines, marks failed, restores, or reverts the candidate where the necessary prior state and dependencies were preserved.

Candidate types can include memory updates, route policies, prompt policies, tool permissions, runtime choices, evaluator rules, training examples, adapters, expert nodes, Mini-NexusNets, governance rules, or optional model-component candidates.

### Optional Growth-Component Candidate Handling

In another embodiment, the candidate is a growth component. The harness may use approved traces, recursive dreaming outputs, teacher labels, replay failures, curriculum items, and evaluation evidence to create a student candidate. The student candidate can be a child expert, Mini-NexusNet, adapter, route policy, memory encoder, or optional model-component candidate.

The student candidate remains subject to the same governed path. It must be source-reviewed, privacy-reviewed, license-reviewed, sandbox-tested, evaluated, compared against teacher or parent evidence, checkpointed where state may change, and promoted only if required gates pass. A parent component may be retained, retired, marked failed, or restored to a prior preserved state based on evidence.

### Recursive Dreaming And Training Candidates

In another embodiment, the harness generates bounded simulation, adversarial, replay, curriculum, or training-candidate material. Dream output is not production mutation. It is candidate material that receives provenance, safety labels, allowed-use labels, evaluation targets, and promotion status before it can influence memory, training, routing, or optional model-component candidates.

### Teacher Council Review

In another embodiment, one or more teacher systems evaluate an output, route, candidate, student, or parent-retirement request. Teacher outputs, teacher agreement, model confidence, and evaluator scores are evidence inputs, not final truth sources. The computer-implemented controller and governance gates decide whether the evidence is sufficient for a terminal disposition.

### Federation Boundary

In another embodiment, multiple deployments exchange redacted lessons, scorecards, failure signatures, or sanitized deltas. Remote lessons remain candidate influence until local policy, privacy, poisoning, consent, and acceptance gates approve them.

### Optional Later Model-Lineage Consolidation

In another embodiment, repeatedly promoted student components, route policies, adapters, memory encoders, and optional model-component candidates may be consolidated toward a later model lineage. The consolidation path uses the same governed harness path: every growth step begins as a typed activation, enters candidate state, passes through sparse routing, memory permission, governance, evaluation, checkpointing where applicable, and terminal disposition.

## Figures

### Figure 1: System Architecture

FIG. 1 illustrates a governed sparse-routed artificial intelligence harness including input interface 102, activation builder 110, computer-implemented controller 120, routing service 150, node registry 140, neural bus 130, multi-plane memory 180, governance gates 200, evaluator gates 270, tool and runtime selection 210, output and action gate 220, trace ledger 230, checkpoint and rollback ledger 240, and operator review surface 290. In operation, raw input is converted into a typed activation, routed to a selected operational circuit, constrained by memory, policy, and evaluation gates, emitted through an output gate, and recorded in trace and checkpoint ledgers.

### Figure 2: Sparse Routing

FIG. 2 illustrates a sparse routing flow in which typed activation 112 enters route scorer 152 and is compared against candidate component pool 142 containing eligible governed components from the system architecture inventory. Scoring and filtering stage 154 produces selected operational circuit 158 and rejected component record 159, and route ledger entry 232 records selected components, rejected components, and route reasons.

### Figure 3: Multi-Plane Memory

FIG. 3 illustrates permissioned multi-plane memory retrieval in which memory operating system 185 is connected to episodic memory 181, semantic memory 182, procedural memory 183, policy memory 184, evidence and trust memory 186, temporal lineage memory 187, dream memory 188, candidate research memory 189, and federated lesson memory 191. The separated memory planes produce labeled memory references 192 or blocked memory records 194 according to provenance, permission, status, and allowed use.

### Figure 4: Candidate Promotion And Rollback

FIG. 4 illustrates candidate promotion and rollback in which source event 252 is processed by candidate improvement service 250 to create candidate record 257. Shadow and sandbox service 260, evaluator gate 270, promotion gate 280, checkpoint ledger 240, and trace ledger 230 determine whether the candidate becomes promoted candidate 286, rejected candidate 281, quarantined candidate 282, restored candidate 287, or marked-failed candidate 288. A proposed system change remains candidate-only until sandbox, evaluation, governance, checkpoint, and promotion gates permit active use, with restoration or reversion available after failure detection when prior state and dependencies were preserved.

### Figure 5: Optional Growth-Component Candidate Handling

FIG. 5 illustrates optional growth-component candidate handling in which approved evidence 321, dream artifacts 322, teacher labels 323, replay failures 324, and curriculum items 325 are provided to growth service 320. Growth service 320 generates student candidate 326 for review by teacher council 330, hidden evaluator 331, sandbox service 260, and promotion gate 280. The resulting disposition may include retained student 332, retained parent 333, rejected student 334, or optional model-lineage candidate 340, and the growth-component candidate remains subject to the same governed candidate, evaluation, checkpoint, and terminal-disposition path.
