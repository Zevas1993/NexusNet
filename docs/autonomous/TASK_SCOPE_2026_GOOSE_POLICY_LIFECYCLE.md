# Task Scope: 2026 Goose Policy Lifecycle and Certification

## Accepted Baseline
- goose lane config and service registration
- recipe and runbook schema plus baseline examples
- bounded subagent, delegation, and parallel lanes
- extension catalog and extension governance baseline
- versioned policy-set baseline
- ACP bridge baseline
- permission, sandbox, persistent-instruction, and adversary-review baselines
- recipe and runbook execution history baseline
- scheduled recipe artifact persistence baseline
- wrapper, ops, and visualizer read-only Goose inspection baseline
- current Goose docs, playbook, and task-scope artifacts

## Current State At Start
- Goose extension bundles already resolve through governed bundle metadata and versioned policy-set IDs.
- Gateway-controlled recipe, runbook, subagent, and direct gateway flows already persist execution artifacts and linked report IDs.
- ACP diagnostics already expose provider readiness, compatibility fixtures, and graceful absence handling.
- Adversary review already fails closed or escalates on ambiguous binding, chained approval bypass, privilege confusion, and bundle escalation attempts.

## This Task Touches
- policy-set lifecycle history, rollout state, rollback lineage, and read-only policy lifecycle reports
- extension-bundle certification artifacts, provenance enrichment, and privilege inheritance diagnostics
- broader gateway trace linkage for policy lifecycle and certification artifacts
- adversary-review audit exports and richer operator drill-down
- wrapper, ops, and visualizer read-only exposure of lifecycle, certification, and audit-export state
- Goose lifecycle/certification docs and focused validation

## Highest-Value Gaps At Start
- policy sets are versioned but still behave like static config snapshots instead of lifecycle-managed artifacts with lineage and rollout state
- extension bundles persist provenance but not distinct certification artifacts with certification status and privilege inheritance diagnostics
- gateway and wrapper surfaces expose policy-set IDs but not lifecycle artifact IDs, rollout status, or certification status
- adversary review exposes reports but not exportable operator audit artifacts

## Canon Preserved
- NexusNet remains brain-first and the neural-network upgrade path
- Nexus remains the shell, platform, and runtime surface
- Goose-derived patterns stay subordinate to Nexus and NexusNet
- ACP remains optional and provider-gated
- high-risk review remains fail-closed or escalate, never fail open
- wrapper and visualizer remain read-only inspection surfaces
- no second control plane or second UI system is introduced

## Known Unrelated Dirty-Tree Risk
- The repo has substantial pre-existing tracked and untracked drift outside this task scope.
- Temp and cache permission noise is visible during `git status` scans and is not part of this run.

## Materially Advanced In This Run
- policy sets are now inspectable lifecycle artifacts with status, lineage, rollout, rollback, and report linkage
- extension bundles now emit certification artifacts with certification state and privilege inheritance diagnostics
- gateway-linked extension provenance now carries lifecycle and certification linkage
- adversary reviews now emit audit exports for bounded operator review
