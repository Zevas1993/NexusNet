# LLM Gateway Budget Control Spec

Status: P2 online assimilation target. Research-only until NexusNet's actual provider, local runtime, and cost-control needs are mapped.

## Source Evidence

- LiteLLM docs: https://docs.litellm.ai/
- LiteLLM repository: https://github.com/BerriAI/litellm
- Langfuse docs: https://langfuse.com/docs
- Helicone docs: https://docs.helicone.ai/
- Source status: official docs and public repositories where available.

## Finding

LLM gateways and observability tools expose practical patterns for routing, budgets, fallbacks, rate limits, spend tracking, prompt/version observability, and provider abstraction. NexusNet should assimilate the control-plane ideas without making hosted gateways mandatory.

## NexusNet Assimilation Target

Create a model gateway policy layer for provider and local-runtime decisions. It should enforce budget ceilings, rate limits, route eligibility, fallback policy, privacy rules, and operator-visible cost estimates.

## Proposed NexusNet Components

- `ModelRouteBudget`: per-run, per-day, per-lane, and per-provider cost ceilings.
- `RouteEligibilityPolicy`: local-only, open-first, allowed hosted provider, privacy class, and fallback order.
- `CostTrace`: estimated tokens, actual tokens, cache savings, latency, provider, and spend.
- `RateLimitGate`: throttles or queues runs by lane, user, provider, and budget state.
- `GatewayAuditPanel`: shows why a route was selected, blocked, downgraded, or escalated.

## Promotion Gates

- Default to local/open-first routes where quality and hardware allow.
- Block hosted providers for private data unless explicitly permitted.
- Record cost and route decisions in traces.
- Keep hosted gateway dependencies optional for local-only commercial packaging.

## Risks

- Provider abstraction can hide model-specific behavior and policy differences.
- Hosted gateway logs may create privacy obligations.
- Cost controls are only useful if token accounting includes retries, tools, and cached context.
