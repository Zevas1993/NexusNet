# Task Scope: 2026 Goose Gateway Coverage and Governance

## Accepted Baseline
- goose lane config and service registration
- recipe/runbook schema and baseline examples
- bounded subagent, delegation, and parallel lanes
- extension catalog baseline
- ACP bridge baseline
- permission, sandbox, persistent-instruction, and adversary-review baselines
- recipe/runbook execution history baseline
- scheduled recipe artifact persistence baseline
- wrapper, ops, and visualizer read-only Goose inspection
- current Goose docs, playbook, and task-scope artifacts

## This Task Touches
- broader gateway-only Goose flow trace linkage
- extension-bundle provenance, governance, and reporting
- richer ACP readiness, capability, and remediation diagnostics
- deeper adversary-review coverage for extension and inheritance risk families
- read-only wrapper, ops, and visualizer drill-down for Goose-derived gateway and bundle artifacts
- Goose gateway-coverage docs and validation

## Materialized In This Run
- gateway-only executions now persist through the shared Goose execution artifact schema and report lane
- extension bundles now produce governed provenance artifacts and detail reports
- ACP health now includes remediation-action aggregation and richer provider drill-down
- adversary review now explicitly classifies bundle-level permission escalation attempts
- wrapper and visualizer posture now expose gateway-history and bundle-governance drill-down fields

## Highest-Value Gaps At Start
- gateway-only Goose flows still lacked first-class persisted execution artifacts
- extension bundles were visible catalog entries but not yet governed artifacts with provenance and report drill-down
- ACP diagnostics were stronger than baseline but still thin on operator remediation and bundle-facing compatibility context
- adversary review still lacked explicit bundle-level permission escalation coverage

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
