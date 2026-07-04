# Workstream Observability Surface Spec

Status: P3 watchlist. Research-only product-surface comparison.

## Source Evidence

- Workstream paper: https://arxiv.org/abs/2604.17055
- Agent Observability Protocol: https://useaop.dev/
- OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Source status: primary paper page and official observability docs.

## Finding

Workstream frames agent use as part of the developer command center: pull requests, tasks, calendar, code review intelligence, AI-readiness scoring, and agent observability in one local-first surface. AOP and OpenTelemetry GenAI provide complementary trace conventions for agent/model/tool spans.

## NexusNet Assimilation Target

Use this as a Control Panel comparison target. NexusNet should expose what the agent is doing, why it is doing it, which model/tool/protocol it used, what it cost, whether it touched private data, and what gates are blocked.

## Proposed NexusNet Components

- `AgentActivityTimeline`: live and historical spans for thought, tool, model, retrieval, policy, and operator events.
- `AIReadinessChecklist`: repo/workspace readiness checks for agent action: tests, docs, AGENTS rules, sandbox, secrets, MCP config, and review gates.
- `CostAndLatencyLedger`: model/tool cost estimates and actuals.
- `LocalObservabilityExport`: optional export to AOP/OpenTelemetry-compatible events with redaction.

## Promotion Gates

- Keep observability local by default.
- Redact prompts, file contents, private paths, and secrets before any external export.
- Show blocked gates and next operator action rather than only success metrics.

## Risks

- Dashboards can become decorative if not tied to enforcement.
- Cost telemetry can be misleading without provider-specific pricing capture dates.
- Exported observability can leak sensitive user/workspace data.
