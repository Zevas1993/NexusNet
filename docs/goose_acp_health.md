# Goose ACP Health

## Scope
- ACP remains optional and provider-gated.
- This lane adds diagnostics, not a mandatory ACP runtime.

## Health Dimensions
- provider availability
- auth/config readiness
- endpoint configured state
- probe mode and probe status
- capability inventory
- tool compatibility
- subagent compatibility
- timeout pattern
- failure pattern
- protocol/version compatibility
- feature compatibility
- readiness checks and pass counts
- config-gap and recommended-action aggregation
- simulated compatibility fixtures and bundle-family compatibility
- bounded live-probe example inventory

## Inspection
- `GET /ops/brain/acp`
- `GET /ops/brain/acp/health`
- `GET /ops/brain/acp/providers/{provider_id}`
- `GET /ops/brain/acp/providers/compare`
- `POST /ops/brain/acp/compatibility`

## Boundaries
- Missing or disabled ACP providers degrade gracefully.
- ACP never becomes the identity or control plane of NexusNet.

## Operator Notes
- Compatibility checks stay read-only and report whether requested tool sets and subagent modes fit each ACP provider’s declared capabilities.
- Health summaries now distinguish disabled, misconfigured, version-mismatched, and ready-if-reachable ACP states.
- Provider detail now includes a bounded operator summary, recommended action, extension compatibility, and a sample compatibility drill-down without attempting live activation.
- ACP compatibility checks now accept requested extensions in addition to requested tools and subagent mode.
- ACP provider detail now also exposes readiness-check results, compatibility-fixture counts, and bundle-family compatibility for simulated provider diagnostics.
- ACP readiness now also distinguishes `simulated`, `live-probe-capable`, and `live-probe` posture without making ACP mandatory.
- If a real provider later appears, the same read-only health surface can report bounded probe status and failure patterns without introducing a separate ACP control plane.
- ACP provider compare now emits read-only diff output and a compare report artifact so operator review can compare remediation, compatibility, and probe posture between two providers.
- Provider detail and compare exports now also expose probe-readiness state, probe execution policy, bounded probe budgets, and explicit live-probe blockers so simulated readiness and future live readiness share the same contract.
- Health summaries now also aggregate provider-gated counts, blocked-probe counts, readiness-state counts, and blocker counts so closeout review can distinguish structurally ready diagnostics from real-provider readiness.
- Current repo config remains provider-gated:
  - `acp.enabled: false`
  - ACP providers are disabled
  - ACP provider endpoints are `null`
- Because of that config, bounded live probes are not active today; they only become relevant if a real ACP-capable provider is added to repo config.
