# Task Scope: 2026 Goose Compare UX and Lifecycle Fixtures

## Accepted Baseline
- goose lane config and service registration
- recipe and runbook schema plus baseline examples
- bounded subagent, delegation, and parallel lanes
- extension catalog and extension governance baseline
- versioned policy-set baseline
- flow-family classification baseline
- recipe and runbook execution history baseline
- scheduled artifact persistence baseline
- ACP bridge baseline
- ACP simulated-vs-live-probe readiness baseline
- permission, sandbox, persistent-instruction, and adversary-review baselines
- compare endpoint baseline
- wrapper, ops, and visualizer read-only Goose inspection baseline
- current Goose docs, playbook, and task-scope artifacts

## Current State At Start
- Goose gateway, recipe, runbook, scheduled, delegation, extension, and ACP-linked paths already persist execution artifacts with explicit `flow_families`.
- Read-only compare endpoints already exist for gateway history, recipe history, runbook history, policy history, certification artifacts, and adversary reviews.
- ACP readiness already distinguishes simulated posture from live-probe-capable posture and degrades gracefully when providers are absent.
- Wrapper, ops, and visualizer runtime posture already expose Goose compare refs and family counts.

## This Task Touches
- first-class visualizer and operator compare controls for existing Goose compare surfaces
- explicit multi-version policy lifecycle fixtures and certification lifecycle edge cases
- richer policy history and certification drill-down, lineage, and human-readable exports
- ACP readiness/probe compare support and bounded live-probe report shape
- Goose compare/export docs and focused validation

## Highest-Value Gaps At Start
- the visualizer exposes Goose compare refs but still lacks first-class Goose compare selectors and read-only operator controls
- compare cards still lean on generic scene/link chips and raw diff JSON instead of clearer human-readable Goose delta summaries
- policy-family lifecycle support exists, but explicit `rolled_back`, `superseded`, `held`, and restore-style fixture coverage is thin
- certification and provenance detail expose current state, but lineage, permission delta, and risk history drill-down are still shallow
- ACP has readiness and compatibility summaries but no first-class compare workflow for provider A vs B readiness/probe posture

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
1. Add explicit multi-version lifecycle fixtures and richer certification/policy lineage summaries with stable compare/export artifacts.
2. Add ACP readiness compare support and bounded live-probe report shape while preserving graceful absence semantics.
3. Add first-class Goose compare selectors and human-readable compare rendering to the visualizer without creating a second UI.
4. Validate targeted Goose compare, lifecycle, ACP, wrapper, and visualizer paths, then update docs and run log.

## Completed In This Run
- Added first-class visualizer Goose compare controls and human-readable compare-card summaries for gateway, policy, certification, adversary, and ACP provider comparisons.
- Added stable compare exports for gateway, policy lifecycle, certification, adversary review, and ACP provider compare workflows.
- Expanded lifecycle fixture coverage so `rolled_back`, `superseded`, and `held` states are explicit historical records, not schema-only possibilities.
- Expanded certification drill-down with stable lineage IDs, restoration detection, permission deltas, policy-lineage summaries, and compare exports.
- Preserved ACP graceful absence while adding provider-vs-provider compare/export support and keeping live probe posture bounded and optional.
