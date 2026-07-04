# Nonprovisional Utility Specification Draft

## Title

Hive Mind Harness for Artificial Intelligence with Governed Sparse Routing

## Cross-Reference To Related Applications

[If filing after a provisional application, insert the provisional
application number and filing date here. Otherwise state: Not applicable.]

## Field

The disclosure relates to artificial intelligence systems, multi-agent
orchestration, machine-learning model routing, memory-augmented computing,
software safety systems, federated learning, and computer-implemented
training and evaluation harnesses.

## Background

Conventional AI applications commonly route a user prompt directly to a
hosted or local model, retrieve documents through a retrieval-augmented
generation pipeline, or invoke tools through an agent framework. Such
systems often treat memory, tool permissions, provider routing, model
selection, evaluation, autonomous coding, and user-interface status as
separate features. As a result, the systems can lack a unified decision
authority, can fail to record why a route was selected, can permit unsafe
tool use, can accumulate stale skills, and can treat self-improvement as an
ad hoc update rather than as a reversible, evaluated, and policy-gated
process.

Multi-agent systems can improve specialization, but many such systems
activate broad agent sets, depend on prompt-only conventions, or lack a
neural-network-like substrate for nodes, edges, activations, recurrent
loops, loss signals, and optimization. Mixture-of-experts model
architectures provide sparse expert activation at the model-weight level,
but do not by themselves govern external tools, memory, sandboxed updates,
provenance ledgers, visual operator controls, or privacy-preserving
deployment-level learning.

A need therefore exists for a computer-implemented AI harness that combines
a brain-first command path, sparse expert activation, explicit memory
planes, recurrent deliberation, sandboxed self-assimilation, trace-first
evaluation, checkpoint-based rollback, and federated learning boundaries in
a single governed architecture.

## Summary

In some embodiments, a computer-implemented neural network harness includes
a neural core service, a node registry, a neural bus, a cortex router,
assistant orchestrators, expert capsules, a multi-plane memory system, a
recurrent deliberation loop, an immune/governance kernel, a sandbox and
evaluation subsystem, a checkpoint/rewind ledger, and an action/output
subsystem. The harness receives an operator task or candidate capability,
converts it into a typed activation, retrieves relevant memory and
provenance, selects a sparse set of nodes, performs one or more internal
deliberation loops, evaluates confidence and risk, and permits an external
action only after required gates pass.

In some embodiments, candidate improvements are not directly installed.
Instead, a candidate is source-pinned, license-checked, privacy-classified,
converted into a capability genome, tested in a closed sandbox, compared
against baseline behavior, evaluated for security and regressions, and then
promoted, rejected, blocked, or side-barred with ledger evidence.

In some embodiments, the harness includes a federated learning plane that
exports only approved, redacted deltas, such as route-score summaries,
expert-performance scorecards, evaluation results, runtime-performance
summaries, and failure signatures. Raw private prompts, secrets, local file
contents, proprietary code, and unredacted transcripts are not exported
without explicit approval.

## Brief Description Of The Drawings

FIG. 1 illustrates an example brain-first neural network harness system.
FIG. 2 illustrates example neural-harness planes.
FIG. 3 illustrates an example task forward pass through the harness.
FIG. 4 illustrates an example sandboxed self-assimilation loop.
FIG. 5 illustrates an example skill-system and AFK sandbox agent factory.
FIG. 6 illustrates an example privacy-preserving federated learning flow.
FIG. 7 illustrates example trace, checkpoint, and rewind data structures.

## Detailed Description

### Definitions

A "neural core" refers to a computer service that remains the authority for
task routing, memory assembly, policy application, expert selection,
generation, critique, evaluation, and final output metadata.

A "hive node" refers to a typed harness component, including an assistant
orchestrator, expert capsule, Mini-NexusNet, skill, skill system, tool
adapter, model adapter, memory bank, evaluator, sandbox runner, policy gate,
curator, or training school component.

A "hive activation" refers to a typed representation of an input task,
candidate update, event, tool output, or federated signal. The activation
can include an intent, capability vector, risk vector, memory references,
provenance references, confidence, novelty, privacy class, and policy
labels.

A "skill system" refers to an orchestrated workflow made of multiple
focused reusable skills with typed handoffs, context limits, checkpoint
locations, and visible output artifacts.

### System Overview

Referring to FIG. 1, an operator input 102 enters a sensory/input plane 104.
A representation plane 106 converts the input into a hive activation. A
temporal lineage ledger 108 attaches session, dependency, prompt-preview,
candidate-strain, and checkpoint lineage. A neural bus 110 publishes the
activation to a cortex router 112 and a neural core 114. The cortex router
selects a sparse subset of assistant orchestrators 116, expert capsules
118, Mini-NexusNets 120, memory planes 122, sandbox/evaluation services 130,
and provider/tool adapters 144.

The neural core 114 mediates all external effects. A HiveBlackboard 124
maintains residual working state across loops. A recurrent deliberation
loop 126 repeats routing, memory lookup, expert computation, critique, and
policy evaluation until an exit condition is satisfied. An immune/governance
plane 128 blocks unsafe routes, prompt-injection attempts, untrusted tools,
unapproved writes, unredacted federation, and candidate promotions lacking
evidence. A checkpoint/rewind ledger 132 records reversible state before
write actions. An action/output plane 134 emits approved code edits,
reports, tool calls, API responses, generated assets, or visual state. A
VisualOps control panel 136 renders traces and status.

### Neural-Harness Planes

Referring to FIG. 2, the harness includes multiple planes corresponding to
neural-network concepts. Nodes correspond to operational components, edges
correspond to trust, dependency, provenance, and routing relationships,
weights correspond to scores such as confidence, risk, usefulness, latency,
privacy, cost, approval, and reliability, and activations correspond to
typed task signals. A forward pass corresponds to a complete task execution.
Recurrent loops correspond to repeated internal deliberation before external
action. Loss corresponds to tests, regressions, policy violations, user
corrections, cost drift, latency drift, unsupported claims, and usefulness
deltas. Optimization is performed by a training school, curator, route
score updates, evaluation gates, and federated aggregation.

### Sparse Expert Routing

The cortex router 112 receives a focused activation set and scores candidate
nodes. The score can include capability fit, historical reliability,
confidence, privacy sensitivity, cost, latency, concurrency safety, tool
permissions, certification state, quarantine state, memory access, and
policy labels. The router selects only the nodes needed for a task, thereby
reducing unnecessary context loading and reducing unsafe broad activation.

Example route modes include direct expert route, debate route, quorum route,
stop-signal route, contract-net auction route, emergency policy route, and
federated aggregation route.

### Multi-Plane Memory And Engram Layer

The memory system 122 separates source canon, compact canon, post-book
addenda, assimilation ledger entries, project documents, trace ledgers,
skill registries, expert genome registries, evaluation histories, provider
scorecards, sandbox artifacts, and federated aggregate lessons. A retrieved
memory carries provenance, status, freshness, and permission labels. The
system can perform exact reference lookup, structured metadata lookup,
semantic retrieval, graph-neighborhood lookup, and later hashed engram-style
hot-memory lookup for frequent canon or workflow patterns.

### Recurrent Deliberation And Exit Gates

The recurrent deliberation loop 126 updates internal hive state before
external action. In each loop, the system may focus activations, route
sparse experts, retrieve memory, run critique, update the HiveBlackboard,
and evaluate risk and completeness. Exit gates can include confidence above
threshold, risk below threshold, required policy gates passed, expert
disagreement resolved, memory sufficient, maximum loops reached, operator
checkpoint required, or policy forced stop.

### Sandboxed Self-Assimilation

Referring to FIG. 4, a candidate capability can enter from operator prompt,
research monitor, repository, paper, video, product, or trace discovery.
The system pins source identity, reviews license and privacy class, extracts
traits into a capability genome, runs a closed sandbox test, executes
evaluations, applies immune/governance checks, writes a curator report, and
promotes, rejects, blocks, or side-bars the candidate. The candidate cannot
silently modify production memory, expert definitions, tools, prompts, or
runtime state.

### Skill Systems And AFK Sandbox Agent Factory

In some embodiments, focused skills are composed by an orchestrator into a
skill system. A skill system can include transcript extraction, research,
planning, implementation, review, packaging, scheduling, or bridge actions.
A sandbox agent factory can launch planner, implementer, reviewer, and
merger agents in isolated workspaces or containers. Merge-back is permitted
only after policy scan, test evidence, checkpoint reference, and operator
approval when required.

### Federated Learning Boundary

Referring to FIG. 6, each local NexusNet deployment can produce local
scorecards and deltas. A redaction and consent gate removes raw private
content, secrets, proprietary source code, and unapproved transcripts. An
aggregator receives approved summaries, computes aggregate lessons, and
returns signed update candidates. The receiving deployment treats returned
updates as candidates requiring sandbox and evaluation before promotion.

### VisualOps Control Panel

The VisualOps control panel 136 renders brain path traces, active assistant
orchestrators, expert capsules, route decisions, memory lookups, neural bus
traffic, sandbox outcomes, evaluation scores, policy blocks, checkpoint
references, federation state, and product readiness. Missing telemetry is
shown as unavailable rather than fabricated.

### Technical Effects

The described architecture can provide technical effects including reduced
uncontrolled tool execution, reduced unnecessary expert activation,
improved traceability of AI decisions, reversible autonomous update
attempts, privacy-preserving cross-deployment learning, improved isolation
of candidate capabilities, and improved operator visibility into AI system
state.

## Example Embodiments

1. A local-first desktop deployment uses local memory and project-root
   ledgers while routing selected tasks to hosted or local models.
2. A coding deployment uses the sandbox agent factory to implement backlog
   tasks in isolated branches and requires reviewer and policy-gate evidence
   before merge.
3. A research deployment monitors public sources, proposes candidate
   assimilations, and side-bars non-useful attempts as historical evidence.
4. An enterprise deployment disables raw federated exports and shares only
   approved route-score summaries.
5. A native-growth deployment uses traces, expert scorecards, dream outputs,
   and evaluation data as training material for later MoE-style model
   distillation.
