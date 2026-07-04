# NexusNet Model Routing Strategy

Status: live-control-plane implementation
Canon entry: PB-2026-05-03-053

## Route Contract

Every NexusNet inference decision carries:

- `trace_id`
- `agent_id`
- `privacy_class`
- `risk_level`
- task specificity
- complexity tier
- provider/model decision
- fallback chain
- cost ledger
- baseline cost comparison
- redacted trace metadata

## Routing Order

1. Privacy and safety policy
2. Explicit override
3. Header/config/policy route
4. Specificity route
5. Complexity route
6. Capability/provider selection
7. Fallback selection
8. Execution trace recording

This prevents a cheap cloud route from winning before NexusNet checks whether the request is local-only or high-risk.

## Tier Policy

- `simple`: cheapest capable local-first route.
- `standard`: cheapest route above a minimum quality floor, tool-capable preferred.
- `complex`: highest-quality route with cost as tiebreaker.
- `reasoning`: highest-quality reasoning-capable route, with validation and human gates when risk requires it.
- `default`: neutral fallback route for ambiguous or disabled complexity routing.

## Prompt Scoring Boundary

Complexity scoring excludes `system` and `developer` messages and only scores the recent task-relevant message window. This prevents NexusNet's own large brain prompt from inflating every request into the expensive tier.

## Manifest Adapter Boundary

The Manifest adapter is optional. It can emit OpenAI-compatible payloads for a self-hosted Manifest instance, parse `X-Manifest-*` headers, and record redacted trace metadata. It cannot bypass NexusNet privacy, governance, sandbox, or approval gates.

Required default:

```env
MANIFEST_TELEMETRY_DISABLED=1
```

## Ledger Rule

A model router without a cost ledger is incomplete. NexusNet records both:

- estimated selected-route cost
- estimated strong-baseline route cost

Prompt content is not exported into the ledger.
