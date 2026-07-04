# Agent UI Protocols Spec

Status: P3 watchlist. Research-only UI/protocol comparison; not a generated-UI implementation plan.

## Source Evidence

- AG-UI repository: https://github.com/ag-ui-protocol/ag-ui
- A2UI v0.9 specification: https://a2ui.org/specification/v0.9-a2ui/
- UCP overview/specification: https://ucp.dev/2026-04-08/specification/overview/
- Source status: public repository and protocol documentation pages.

## Finding

Agent UI protocols are emerging as a separate layer from tool protocols and peer-agent protocols. AG-UI focuses on event-based agent/user interaction for frontend applications. A2UI focuses on streaming JSON-defined UI surfaces, component updates, data-model updates, and validation errors. UCP shows a commerce-specific version/capability-negotiation pattern that is useful beyond commerce.

## NexusNet Assimilation Target

Use these as clean-room patterns for safe generated Control Panel surfaces. NexusNet should allow agents to propose structured UI states, dashboards, forms, and action previews without letting generated HTML, JavaScript, or hidden instructions cross into trusted UI authority.

## Proposed NexusNet Components

- `GeneratedSurfaceSchema`: whitelisted component catalog, root component requirement, stable IDs, and validation errors.
- `AgentUIEventStream`: agent events for status, tool calls, action previews, user approval, and UI state deltas.
- `CapabilityNegotiationRecord`: protocol/version/capability intersection before a generated surface can request actions.
- `UIDangerousActionGate`: generated UI can display high-impact actions, but execution requires a separate trusted operator approval.

## Promotion Gates

- Never execute generated HTML, JavaScript, or arbitrary component code.
- Require schema validation and a visible component catalog for every generated surface.
- Separate "agent suggested this button" from "trusted UI can execute this action."
- Keep UI telemetry local unless export is explicitly enabled.

## Risks

- UI protocols can blur display authority and action authority.
- Generated UI can mislead users even if it cannot execute code.
- Capability negotiation must be pinned and versioned, not inferred from agent claims.
