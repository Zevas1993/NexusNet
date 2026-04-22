# Goose ACP Assimilation

## Scope
- Goose ACP bridge ideas are assimilated only as an optional provider lane.
- ACP remains subordinate to NexusNet routing, governance, SafetyAO, and EvalsAO.

## What Landed
- ACP provider catalog and bridge summary.
- Optional provider visibility with read-only availability state.
- No ACP dependency for default startup.

## Operationalization
- ACP health reporting now exposes provider readiness, auth/config state, timeout/failure patterns, and capability inventory.
- Wrapper and visualizer overlays now surface ACP ready-counts and status counts without making ACP mandatory.
- Read-only provider-detail and compatibility endpoints now let operators inspect whether a requested tool set or subagent mode fits declared ACP capabilities.
- ACP diagnostics now also expose version and feature compatibility so unsupported bridges can be diagnosed without attempting activation.
- ACP provider detail now also includes extension compatibility, operator summaries, and recommended actions for disabled, misconfigured, or version-mismatched providers.
- ACP health now also aggregates remediation-action counts so operator drill-down can separate absent providers from configuration work that is actually actionable.
- ACP readiness now also reports explicit readiness-check results, config-gap counts, recommended-action counts, compatibility-fixture counts, and bundle-family compatibility.
- ACP-facing extension certification now records privilege inheritance confusion explicitly so provider-gated bundles can stay in shadow-approved governance instead of widening privilege silently.
- ACP provider diagnostics now also distinguish simulated posture from live-probe-capable readiness and bounded live-probe examples, which keeps the lane ready for a future real provider without making ACP mandatory today.
- ACP provider compare now exposes remediation, compatibility, probe-mode, and bundle-family deltas plus exported compare artifacts, so a real provider can be assessed against a simulated baseline without changing control-plane posture.
- ACP operator detail and compare exports now also surface probe-readiness state, bounded probe budgets, and live-probe blockers so a future real provider can drop into the same read-only readiness contract.
- Closeout posture is now explicit: Goose ACP assimilation is operationally sufficient for diagnostics and compare/export today, and further ACP work should only reopen when a real provider endpoint is introduced or operator pain proves the simulated contract is insufficient.

## Boundaries
- ACP does not become the identity of NexusNet.
- ACP is not mandatory and does not replace existing runtime/provider baselines.

## Sources
- Goose docs: https://goose-docs.ai/
- Goose repository: https://github.com/aaif-goose/goose
