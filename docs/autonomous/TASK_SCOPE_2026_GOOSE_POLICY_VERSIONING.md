# Task Scope: 2026 Goose Gateway Breadth and Policy Versioning

## Accepted Baseline
- goose lane config and service registration
- recipe/runbook schema and baseline examples
- bounded subagent, delegation, and parallel lanes
- extension catalog baseline
- extension governance baseline
- ACP bridge baseline
- permission, sandbox, persistent-instruction, and adversary-review baselines
- recipe/runbook execution history baseline
- scheduled recipe artifact persistence baseline
- wrapper, ops, and visualizer read-only Goose inspection
- current Goose docs, playbook, and task-scope artifacts

## This Task Touches
- broader live gateway-controlled Goose flow linkage beyond the direct gateway endpoint
- versioned extension-bundle policy sets and bundle-family governance
- richer ACP readiness and provider compatibility diagnostics
- deeper Goose operator drill-down through read-only APIs, wrapper state, and visualizer posture
- Goose gateway/policy-versioning docs and validation

## Highest-Value Gaps At Start
- recipe, runbook, and subagent Goose flows still used gateway resolution transiently without persisting the gateway execution artifact itself
- extension governance still depended on static tool and permission maps instead of versioned policy-set artifacts
- ACP compatibility diagnostics still lacked stronger simulated compatibility fixtures and bundle-family alignment detail
- wrapper and visualizer Goose posture still surfaced extension governance state without explicit policy-set versioning

## Materially Advanced In This Run
- recipe, runbook, and subagent Goose flows now persist linked gateway execution artifacts, gateway report IDs, and gateway-produced artifact refs
- extension governance now exposes versioned policy-set IDs, versions, and bundle families through bundle detail, policy-set summary/detail endpoints, wrapper state, and visualizer posture
- ACP diagnostics now expose readiness checks, config-gap counts, recommended-action counts, and simulated compatibility fixtures for provider-gated operator review
- scheduled-monitor inspection now prefers the source execution report ID instead of accidentally surfacing a linked gateway report when both exist

## Canon Preserved
- NexusNet remains brain-first
- Nexus remains the shell/platform/runtime surface
- Goose remains subordinate to Nexus and NexusNet
- ACP remains optional and provider-gated
- no second control plane
- high-risk review remains fail-closed or escalate
- visualizer remains read-only

## Unrelated Dirty-Tree Risk
- Pre-existing tracked and untracked repo drift exists outside this task scope.
- Cache and temp permission noise is still visible during status scans and is not part of this run.
