# Task Scope: 2026 Goose Hardening

## Accepted Baseline
- goose lane config and service registration
- recipe/runbook schema and baseline examples
- bounded subagent, delegation, and parallel lanes
- extension catalog baseline
- ACP bridge baseline
- permission, sandbox, persistent-instruction, and adversary-review baselines
- recipe/runbook execution history baseline
- wrapper, ops, and visualizer read-only Goose inspection
- current Goose docs, playbook, and task-scope artifacts

## This Task Touches
- broader real-flow trace linkage for Goose recipe/runbook and subagent flows
- ACP health, version, and feature compatibility diagnostics
- adversary-review expansion for approval-bypass and privilege-confusion scenarios
- richer wrapper/ops/visualizer artifact drill-down and usability
- Goose hardening docs and validation

## Highest-Value Gaps At Start
- recipe and runbook history still relied too heavily on manual posting
- subagent traces were not carrying enough gateway or review provenance
- ACP diagnostics did not distinguish capability mismatch from version/config issues clearly enough
- adversary review lacked explicit coverage for chained approval bypass and recipe/subagent privilege confusion

## Canon Preserved
- NexusNet remains brain-first
- Nexus remains the shell/platform/runtime surface
- Goose remains subordinate to Nexus/NexusNet
- ACP remains optional and provider-gated
- no second control plane
- no fail-open on high-risk review failure
- visualizer remains read-only

## Unrelated Dirty-Tree Risk
- Pre-existing repo drift outside this task may still exist and is not part of this hardening pass.

## Outcome Snapshot
- Real Goose recipe and runbook flows now auto-link traces, gateway decisions, fallback chains, and adversary report IDs.
- ACP diagnostics now distinguish capability, version, and feature-compatibility states without making ACP mandatory.
- Adversary review now covers chained approval-bypass and privilege-confusion scenarios while preserving fail-closed or escalate semantics.
