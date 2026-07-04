# Protocol Trust Stack Spec

Status: P1 online assimilation target. Research-only until live protocol adapters are scoped.

## Source Evidence

- A2A latest specification: https://a2a-protocol.org/latest/specification/
- A2A and MCP relationship appendix: https://a2a-protocol.org/latest/specification/
- MCP latest specification: https://modelcontextprotocol.io/specification/2025-11-25
- AIP paper: https://arxiv.org/abs/2603.24775
- Agent Observability Protocol: https://useaop.dev/
- OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Source status: official specs/pages plus primary paper page.

## Finding

The agent protocol stack is splitting into distinct layers: MCP for tools/data/context, A2A for peer agent task coordination, identity/delegation layers such as AIP for verifiable authority, AOP/OpenTelemetry for traces, and commerce/payment protocols for special authority domains. Treating these as one generic "agent protocol" would blur trust boundaries.

## NexusNet Assimilation Target

Define protocol separation in NexusNet. A peer agent, a tool server, a browser operator, a model runtime, and an observability collector should each have different identity, consent, authority, and trace requirements.

## Proposed NexusNet Components

- `ProtocolBoundaryRegistry`: classifies connections as tool/context, peer-agent, UI operator, payment-like authority, telemetry, or model runtime.
- `AgentCardVerifier`: validates A2A agent cards, signatures when present, and public versus extended capability scope.
- `DelegationTokenLedger`: records identity, attenuated permissions, chain depth, expiration, and completion provenance.
- `TelemetrySchemaMapper`: maps NexusNet traces to AOP/OpenTelemetry-style spans without leaking private payloads.

## Promotion Gates

- Keep MCP, A2A, ACP/UI, telemetry, and payment-like authority separate.
- Never expose internal Hive Mind memory or local files through peer-agent discovery by default.
- Require signed or pinned identity before delegation receives tools or workspace authority.
- Make observability local-first unless the operator opts into export.

## Risks

- Protocol churn can invalidate adapters quickly.
- Identity papers may not become adopted standards.
- Too much protocol abstraction can distract from NexusNet-native safety gates.
