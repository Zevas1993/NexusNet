# Event Sourced Agent Trace Log Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet run traces, memory, and Control Panel projections.

## Source Evidence

- EventStoreDB/Kurrent event streams docs: https://docs.kurrent.io/server/v24.10%20Preview%201/features/streams.html
- EventStoreDB/Kurrent projections docs: https://docs.kurrent.io/server/v22.10/projections
- CloudEvents specification: https://github.com/cloudevents/spec
- NATS JetStream docs: https://docs.nats.io/nats-concepts/jetstream
- Source status: official docs and open specifications.

## Finding

Event sourcing treats state changes as ordered events and builds read models through projections. For agents, this is deeper than logging: the event stream becomes the source of truth for plans, tool calls, policy decisions, memory writes, approvals, failures, and rollbacks.

## NexusNet Assimilation Target

Make NexusNet agent state replayable from append-only run events. Mutable summaries and dashboard views should become projections that can be rebuilt, audited, compared, and corrected without rewriting the original event stream.

## Proposed NexusNet Components

- `AgentEvent`: typed event with run id, sequence, actor, timestamp, privacy class, schema version, and content digest.
- `RunEventStream`: append-only stream per run, session, or workspace.
- `EventSchemaRegistry`: versioned schemas and migration rules for event payloads.
- `TraceProjection`: rebuildable views for Control Panel timelines, scorecards, memory lineage, and incident reports.
- `ProjectionRebuildCommand`: verifies that projections can be rebuilt from the event stream.

## Promotion Gates

- Append-only write path for authoritative agent events.
- Idempotency keys and optimistic concurrency checks for every event append.
- Privacy redaction strategy before events enter long-retention stores.
- Deterministic projection rebuild tests.
- Explicit retention rules for private, sensitive, and public-safe events.

## Risks

- Event logs can grow quickly and need compaction or archival policy.
- Bad privacy classification becomes durable unless preflight redaction is strong.
- Event schemas need discipline; otherwise projections become brittle.
