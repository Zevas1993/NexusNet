# Agent Observability Standards Spec

Status: P1 online assimilation target. Research-only until mapped against NexusNet traces, Control Panel surfaces, and existing telemetry artifacts.

## Source Evidence

- OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OpenInference specification: https://arize-ai.github.io/openinference/spec/
- Phoenix repository: https://github.com/Arize-ai/phoenix
- AgentTrace paper: https://arxiv.org/abs/2602.10133
- AgentSight paper: https://arxiv.org/abs/2508.02736
- Source status: official specifications, public repository, and primary paper pages.

## Finding

Agent observability is moving beyond generic logs toward structured traces for model calls, agent spans, tool calls, retrieval, reasoning steps, exceptions, metrics, and sometimes system-level behavior. OpenTelemetry GenAI and OpenInference are the most useful standardization references, while AgentTrace and AgentSight show the need to connect semantic intent to runtime behavior.

## NexusNet Assimilation Target

Define a NexusNet trace schema that can export to standards without losing agent-specific state. The trace model should preserve goals, plan transitions, model routes, memory views, retrieval decisions, tool approvals, side effects, sandbox signals, and reviewer outcomes.

## Proposed NexusNet Components

- `NexusRunTrace`: root run ID, user goal, mode, authority level, model route, and privacy class.
- `AgentSpan`: planner, router, memory, retrieval, tool, shell, browser, code, reviewer, and verifier spans.
- `StateTransitionEvent`: what changed, why it changed, evidence used, and next node selected.
- `TraceExportAdapter`: OpenTelemetry and OpenInference compatible export with local redaction defaults.
- `IncidentReplayArtifact`: one failing run packaged for local debugging without leaking secrets.

## Promotion Gates

- Keep raw prompts, private docs, and secrets redacted by default in exported traces.
- Preserve enough local detail to debug state transitions even when exports are redacted.
- Align tool and model spans with OpenTelemetry where practical.
- Require trace review before enabling new high-authority lanes.

## Risks

- Observability can leak the same private data it is meant to protect.
- Standards are still changing, especially around agents and tools.
- Trace volume can become expensive without sampling, retention, and local compaction policy.
