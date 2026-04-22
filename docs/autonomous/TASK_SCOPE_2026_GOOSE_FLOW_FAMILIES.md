# Task Scope: 2026 Goose Flow Families and Live-Probe Readiness

## Accepted Baseline
- goose lane config and service registration
- recipe and runbook schema plus baseline examples
- bounded subagent, delegation, and parallel lanes
- extension catalog and extension governance baseline
- versioned policy-set baseline and lifecycle/certification follow-on baseline
- recipe and runbook execution history baseline
- scheduled artifact persistence baseline
- ACP bridge baseline
- permission, sandbox, persistent-instruction, and adversary-review baselines
- wrapper, ops, and visualizer read-only Goose inspection baseline
- current Goose docs, playbook, and task-scope artifacts

## Current State At Start
- Goose gateway-linked recipe, runbook, subagent, scheduled, and direct gateway flows already persist execution artifacts, linked reports, extension provenance, policy lifecycle linkage, and certification linkage.
- Extension bundles already expose policy history, rollout state, certification artifacts, and read-only wrapper/visualizer inspection.
- ACP diagnostics already degrade gracefully, expose provider readiness summaries, compatibility fixtures, and provider detail views.
- Adversary review already fails closed or escalates on ambiguous binding, chained approval bypass, privilege confusion, and bundle escalation attempts with audit exports.

## This Task Touches
- broader live gateway-controlled Goose flow-family coverage and stored flow classification
- gateway, recipe, and runbook history summaries plus compare/export-ready read-only reports
- richer policy-set family handling and certification rollups across governed extension-bundle families
- ACP live-probe readiness shape, simulated-vs-live probe reporting, and compatibility operator detail
- read-only wrapper, ops, and visualizer compare/export usability for Goose-derived artifacts
- focused Goose docs and validation for the above

## Highest-Value Gaps At Start
- execution history persists linked artifacts but does not classify broader Goose flow families explicitly for operator comparison
- gateway, policy, certification, and adversary surfaces have detail endpoints but not first-class compare views for operators
- ACP readiness does not distinguish simulated readiness from live-probe-capable posture clearly enough for future real providers
- runtime posture surfaces report latest Goose artifacts but not family counts, compare refs, or export-oriented summaries for broader flow families

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
- Temp and cache permission noise remains visible during `git status` scans and is not part of this run.

## Planned High-Leverage Iterations
1. Persist explicit Goose flow-family classification across gateway, recipe, runbook, scheduled, delegation, approval-heavy, extension-only, and ACP-bridged execution paths.
2. Add read-only compare/export views for gateway executions, policy history, certification artifacts, and adversary review outcomes.
3. Expand ACP readiness to report simulated versus live-probe-capable posture without making ACP mandatory.
4. Surface new family counts, compare refs, and operator-facing summaries through wrapper and visualizer runtime posture.

## Materially Advanced In This Run
- gateway, recipe, and runbook execution artifacts now persist explicit `flow_families` and expose family counts plus latest-by-family summaries
- read-only compare endpoints now exist for recipe history, runbook history, gateway history, policy history, extension certification artifacts, and adversary reviews
- ACP readiness now distinguishes simulated posture from live-probe-capable and live-probe fields while preserving graceful degradation when providers are absent
- wrapper and visualizer runtime posture now surface Goose flow-family counts, compare refs, and ACP probe-mode summaries without introducing a second UI or control plane
