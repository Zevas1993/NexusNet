# Task Scope: 2026 Goose Closeout and Pivot Prep

## Accepted Baseline
- goose lane config and service registration
- recipe and runbook schema plus baseline examples
- bounded subagent, delegation, and parallel lanes
- extension catalog and extension governance baseline
- versioned policy-set baseline
- flow-family classification baseline
- compare endpoint baseline
- visualizer compare control baseline
- lifecycle fixture baseline
- certification lineage baseline
- ACP compare/export readiness baseline
- permission, sandbox, persistent-instruction, and adversary-review baselines
- wrapper, ops, and visualizer read-only Goose inspection baseline
- current Goose docs, playbook, and task-scope artifacts

## Current State At Start
- Goose compare views already expose grouped read-only diff sections for gateway, policy, certification, adversary, and ACP comparisons.
- Certification artifacts already surface lineage anchors, restoration detection, historical certification artifact IDs, and operator compare/export reports.
- ACP diagnostics already distinguish simulated, blocked, and live-probe-capable readiness while remaining optional and provider-gated.
- Wrapper and visualizer surfaces already expose Goose-derived policy, certification, gateway, adversary, and ACP state read-only.

## This Task Touches
- explicit diff-category collapse and filter controls for large compare payloads
- deeper stored certification history across more governed bundle families
- provider-gated ACP closeout clarity and bounded probe readiness reporting
- final Goose compare/export/report usability polish
- Goose closeout reporting and pivot guidance

## Highest-Value Remaining Goose Gaps At Start
- compare grouping existed, but large payloads still needed explicit filter and collapse controls instead of passive grouping only
- certification history depth was still strongest on the currently active artifact chains rather than multiple stored historical artifacts across more families
- ACP readiness was structurally ready, but the provider-gated boundary needed cleaner operator-facing closeout language
- Goose lacked a final closeout report marking what is production-grade versus intentionally deferred

## Goose-Complete Vs Provider-Gated
- Production-grade now:
  - gateway-linked Goose flow families and execution artifacts
  - governed extension bundles, policy lifecycle history, rollout and rollback lineage
  - certification artifacts, lineage drill-down, and operator compare/export workflows
  - grouped visualizer compare UX and read-only wrapper/ops/visualizer inspection
  - adversary review compare/export coverage with fail-closed or escalate semantics
- Provider-gated:
  - bounded live ACP probe execution against a real reachable ACP provider
  - any ACP promotion work that depends on non-null endpoints, auth, or protocol negotiation
- Intentionally deferred:
  - any second UI or control plane
  - unconditional ACP activation
  - new Goose-derived families that do not solve an active operator problem

## Canon Preserved
- NexusNet remains brain-first and the neural-network upgrade path
- Nexus remains the shell, platform, and runtime surface
- Goose-derived patterns stay subordinate to Nexus and NexusNet
- ACP remains optional and provider-gated
- high-risk review remains fail-closed or escalate, never fail open
- wrapper and visualizer remain read-only inspection surfaces
- no second control plane or second UI system is introduced

## Known Unrelated Dirty-Tree Risk
- The repo still has substantial pre-existing tracked and untracked drift outside this task.
- Temp/cache permission-denied and long-path noise remains visible in `git status` and is unrelated to this run.

## Planned Closeout Iterations
1. Add explicit filter and collapse controls to the existing Goose compare UX without changing its read-only contract.
2. Extend stored certification and policy history depth across more bundle families so restoration, supersession, rollback, and held states are exercised by real fixtures.
3. Tighten ACP provider-gated reporting so the closeout clearly separates production-grade Goose work from future real-provider-triggered work.
4. Publish closeout docs and a pivot recommendation after broader validation.

## Outcome Snapshot
- Goose compare UX now supports category filters plus expand-all, collapse-all, and reset flows for large read-only diff payloads.
- Retrieval, filesystem, and ACP-governed bundle families now have deeper stored lifecycle and certification history rather than only current-artifact lineage inference.
- ACP closeout language now explicitly marks the lane as provider-gated because repo config still contains disabled providers with null endpoints.
- Goose is ready to pause as a bounded operator-governance lane unless a real ACP provider enters the repo or operator pain justifies reopening the lane.
