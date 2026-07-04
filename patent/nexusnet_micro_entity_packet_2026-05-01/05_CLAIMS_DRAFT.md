# Claims Draft

The following claims are a technical drafting starting point only. Have a
registered patent practitioner review and revise before filing if possible.

## Claim 1 - System

1. A computer-implemented artificial intelligence harness system comprising:
   one or more processors; memory storing instructions executable by the one
   or more processors; a neural core service configured to mediate task
   execution; a hive node registry storing typed records for a plurality of
   harness nodes including assistant orchestrators, expert capsules, memory
   banks, model adapters, tool adapters, evaluators, sandbox runners, and
   policy gates; a neural bus configured to carry typed hive activations
   between the harness nodes; a cortex router configured to select a sparse
   subset of the harness nodes for a task based on at least capability,
   confidence, risk, privacy, cost, latency, permission, and historical
   reliability scores; a multi-plane memory system configured to return
   memory items with provenance and status labels; a recurrent deliberation
   loop configured to update internal harness state through one or more
   routing, memory, expert, critique, and policy iterations before an
   external action is permitted; an immune governance kernel configured to
   block a route or candidate update that lacks a required permission,
   provenance, sandbox, evaluation, or checkpoint condition; a
   checkpoint/rewind ledger configured to store pre-action rollback
   metadata; and an action/output subsystem configured to emit an external
   output only after the neural core service determines that required gates
   have passed.

2. The system of claim 1, wherein the hive node registry stores, for each
   harness node, a node type, capabilities, allowed tools, write scope,
   privacy scope, concurrency safety, memory references, certification
   state, quarantine state, scorecard references, and a genome reference.

3. The system of claim 1, wherein the typed hive activation includes an
   intent, task vector, risk vector, capability vector, memory references,
   policy labels, confidence, novelty, privacy class, and trace references.

4. The system of claim 1, wherein the recurrent deliberation loop exits in
   response to at least one of a confidence threshold, a risk threshold, a
   policy-gate result, a disagreement-resolution result, a memory-sufficiency
   result, a maximum loop count, or an operator-checkpoint requirement.

5. The system of claim 1, wherein the multi-plane memory system separates at
   least source canon records, post-book addendum records, assimilation
   ledger records, trace records, expert genome records, evaluation records,
   sandbox artifacts, and federated aggregate lessons.

6. The system of claim 1, wherein the cortex router is configured to perform
   one or more of a direct expert route, debate route, quorum route,
   stop-signal route, contract-net auction route, emergency policy route, or
   federated aggregation route.

7. The system of claim 1, further comprising a VisualOps control panel
   configured to display brain path traces, selected nodes, rejected nodes,
   memory lookups, policy blocks, sandbox outcomes, evaluation scores,
   checkpoint references, and federation status.

8. The system of claim 1, further comprising a skill-system orchestrator
   configured to compose multiple focused skills into a workflow having
   typed handoffs, context limits, checkpoint locations, and output
   artifacts.

9. The system of claim 1, further comprising a sandbox agent factory
   configured to run planner, implementer, reviewer, and merger stages in
   isolated execution environments and to permit merge-back only after
   policy, test, review, and checkpoint requirements are satisfied.

10. The system of claim 1, wherein a candidate capability is promotable only
    after source identity pinning, license classification, privacy
    classification, sandbox testing, baseline comparison, evaluation, and
    immune-governance review.

11. The system of claim 1, wherein the checkpoint/rewind ledger stores at
    least pre-write file state, active prompt state, memory reference state,
    selected route state, sandbox artifact state, candidate genome state,
    and promotion decision state.

12. The system of claim 1, further comprising a federated learning plane
    configured to export approved, redacted deltas comprising one or more of
    route-score summaries, expert-performance scorecards, evaluation
    summaries, runtime-performance scorecards, or failure signatures while
    blocking export of raw private prompts, secrets, local file contents,
    proprietary code, and unredacted transcripts.

13. The system of claim 1, wherein the immune governance kernel includes a
    plan-mode write jail, a tool execution registry, provider circuit
    breakers, prompt overlay controls, redaction filters, license filters,
    quarantine states, and human checkpoint gates.

14. The system of claim 1, wherein the neural core service is configured to
    prevent user-interface actions, model providers, tool adapters, protocol
    adapters, or training jobs from bypassing brain-mediated routing and
    policy checks.

## Claim 15 - Method

15. A computer-implemented method comprising: receiving a task or candidate
    capability; generating a typed hive activation from the task or
    candidate capability; attaching temporal lineage and provenance to the
    typed hive activation; retrieving memory items from a multi-plane memory
    system, wherein each retrieved memory item includes a provenance label
    and a status label; selecting, by a cortex router, a sparse subset of
    harness nodes from a hive node registry; executing one or more recurrent
    deliberation loops including expert computation, memory lookup, critique,
    and policy evaluation; determining, by an immune governance kernel,
    whether required gates have passed; creating a checkpoint reference
    before an external write or promotion action; and emitting an output or
    candidate disposition through a neural core service.

16. The method of claim 15, further comprising rejecting or side-barring the
    candidate capability when sandbox or evaluation evidence fails a
    threshold.

17. The method of claim 15, further comprising updating route weights or
    expert scorecards based on test results, regression results, user
    correction, policy violations, latency, cost, confidence, or usefulness.

18. The method of claim 15, further comprising displaying, in a VisualOps
    interface, a trace of selected harness nodes, rejected harness nodes,
    memory operations, policy decisions, sandbox results, checkpoint
    references, and output metadata.

19. The method of claim 15, further comprising composing a workflow from a
    plurality of focused skills by an orchestrator skill that passes typed
    outputs from one skill as inputs to another skill.

20. The method of claim 15, further comprising receiving a federated update
    candidate, verifying redaction and consent metadata, and testing the
    federated update candidate in a sandbox before promotion.

21. The method of claim 15, wherein the sparse subset includes at least one
    assistant orchestrator and at least one expert capsule.

22. The method of claim 15, wherein the output comprises code, a document, a
    tool call, an application programming interface response, a visual state
    update, a training artifact, or a candidate assimilation report.

## Claim 23 - Computer-Readable Medium

23. One or more non-transitory computer-readable storage media storing
    instructions that, when executed by one or more processors, cause the
    one or more processors to perform operations comprising: maintaining a
    hive node registry of typed artificial-intelligence harness nodes;
    routing typed hive activations over a neural bus; selecting sparse
    harness nodes through a cortex router; retrieving provenance-labeled
    memory from a multi-plane memory system; performing recurrent
    deliberation before external action; enforcing immune-governance gates;
    recording checkpoint and rewind metadata; and emitting an output through
    a brain-mediated action subsystem.

24. The media of claim 23, wherein the operations further comprise
    classifying a candidate capability as promoted, rejected, blocked, or
    side-barred based on source, license, privacy, sandbox, evaluation,
    checkpoint, and policy evidence.

25. The media of claim 23, wherein the operations further comprise
    generating training records for a later mixture-of-experts artificial
    intelligence model from trace records, expert scorecards, evaluation
    results, dream simulation outputs, and federated aggregate lessons.
