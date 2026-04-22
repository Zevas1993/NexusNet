# Task Scope: 2026 Goose Real-Flow Expansion

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
- broader Goose real-flow trace linkage across recipe, runbook, subagent, gateway, and scheduled execution paths
- sustained scheduled-monitor and scheduled-recipe artifact persistence
- richer ACP health, compatibility, and provider detail diagnostics
- deeper adversary-review coverage for high-risk gateway, extension, and ACP inheritance paths
- wrapper, ops, and visualizer drill-down for Goose-derived artifacts
- Goose real-flow docs and validation

## Highest-Value Gaps At Start
- scheduled artifacts still leaned on summary snapshots more than explicit execution-linked persistence
- real Goose execution history did not consistently surface linked trace IDs, gateway decisions, approval chains, and report IDs across scheduled paths
- ACP provider detail was still thin for operator diagnostics and compatibility triage
- adversary review still lacked explicit coverage for extension or ACP privilege inheritance confusion

## Canon Preserved
- NexusNet remains brain-first
- Nexus remains the shell/platform/runtime surface
- Goose remains subordinate to Nexus and NexusNet
- ACP remains optional and provider-gated
- no second control plane
- no fail-open on high-risk review failure
- visualizer remains read-only

## Unrelated Dirty-Tree Risk
- Pre-existing tracked and untracked repo drift exists outside this task scope.
- Cache and temp permission noise is visible during status scans and is not part of this run.

## Outcome Snapshot
- Schedule-aware recipe, runbook, and subagent flows now emit execution-linked scheduled artifacts instead of relying only on summary-time snapshots.
- Goose history and scheduled artifacts now expose richer trace IDs, report IDs, execution IDs, gateway resolution IDs, and per-workflow latest artifact drill-down.
- ACP diagnostics now distinguish disabled, misconfigured, version-mismatched, and feature-incompatible states with operator summaries and extension compatibility checks.
- Adversary review now treats extension or ACP privilege inheritance confusion as an explicit bounded review family and preserves fail-closed or escalate behavior.
